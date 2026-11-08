"""Reproduce the R3 trace walkthrough: a misread photo check, its correction, and the next check's prior.

Run from the repo root (Phoenix optional, Ollama optional):
    .venv-phoenix\\Scripts\\phoenix.exe serve                       # separate venv, UI on :6006
    $env:STRIPCHECK_TRACING="1"; $env:STRIPCHECK_PLANNER="hybrid"
    .venv\\Scripts\\python.exe docs\\trace\\run_walkthrough.py [--serve 8103]

What is real: the rendered synthetic prop 03 is read by the local OCR, the server API runs the
check, the planner calls the local LLM (or falls back), the verifier gates the result, the
correction is written to a throwaway database and the JSONL/OTel traces are exported.
What is injected: the alert store holds only the synthetic prop-03 record (clearly marked
synthetic, example.invalid source), so no CDSCO row is copied into the repository.
The run uses a temporary data folder; the real database is never touched.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="stripcheck-trace-"))
os.environ["STRIPCHECK_DATA_DIR"] = str(TMP)
os.environ["STRIPCHECK_DB_PATH"] = str(TMP / "walkthrough.db")
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from core import config, db, llm, tracing  # noqa: E402
from core.props import demo_cases, render_demo  # noqa: E402
from core.supervisor import confusion_counts  # noqa: E402
from server.app import create_app  # noqa: E402

JSON = {"Accept": "application/json"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", type=int, default=0, help="keep the patched app running on this port for screenshots")
    args = parser.parse_args()
    case = next(c for c in demo_cases() if c["id"] == "03")
    alert = dict(case["alerts"][0], synthetic=False, flags=[], source_title="Walkthrough fixture record (prop 03, invented)",
                 source_url="https://example.invalid/stripcheck-walkthrough")
    db.batch_alerts = lambda *_a, **_k: [dict(alert)]
    db.check_coverage = lambda: {"real_alert_count": 1, "latest_month": "2026-09", "list_count": 1}
    image = render_demo("03")
    print("planner", config.PLANNER, "model", config.LLM_MODEL, "tracing", tracing.otel_enabled())
    if config.PLANNER in {"hybrid", "llm"}:
        print("warm model:", llm.warm(config.LLM_MODEL, config.OLLAMA_URL, timeout=90))
    app = create_app(db_path=TMP / "walkthrough.db")
    runs = []
    with TestClient(app) as client:
        for label in ("run1", "run2"):
            with image.open("rb") as handle:
                first = client.post("/api/checks", files={"image": ("03_misread.png", handle.read(), "image/png")}, headers=JSON).json()
            thread = first["thread_id"]
            if first.get("status") != "waiting":
                raise SystemExit(f"{label}: expected a question, got {json.dumps({k: first.get(k) for k in ('status', 'history', 'final')}, default=str)[-1500:]}")
            second = client.post(f"/api/checks/{thread}/resume", json={"choice": "LM2408B"}, headers=JSON).json()
            saved = db.get_document("checks", thread) or {}
            engine = (saved.get("context") or {}).get("_engine", {})
            runs.append({"run": label, "thread_id": thread, "session": engine.get("session"), "otel": engine.get("otel"),
                         "question": first.get("pending", {}).get("question"), "prior": first.get("pending", {}).get("prior"),
                         "label": (second.get("final") or {}).get("label"), "steps": second.get("history"),
                         "confusions_after": confusion_counts()})
            shutil.copy(TMP / "traces" / f"{thread}.jsonl", OUT / f"{label}_trace.jsonl")
            print(label, thread, runs[-1]["label"], runs[-1]["otel"])
    tracing.flush()
    (OUT / "walkthrough_runs.json").write_text(json.dumps(runs, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("wrote", OUT / "walkthrough_runs.json")
    if args.serve:
        import uvicorn
        print(f"serving patched app on http://127.0.0.1:{args.serve} (Ctrl+C to stop)")
        uvicorn.run(app, host="127.0.0.1", port=args.serve, log_level="warning")


if __name__ == "__main__":
    main()

"""Run StripCheck locally: python cli.py --help."""
import argparse
import importlib.util
import json
import platform
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from core import config, db


def output(value):
    print(json.dumps(value, indent=2, ensure_ascii=True, default=str))


def doctor(warm=False):
    db.init_db()
    packages = {name: importlib.util.find_spec(name) is not None for name in
                ("fastapi", "uvicorn", "PIL", "rapidfuzz", "qrcode", "rapidocr", "pytesseract", "zxingcpp", "Vision")}
    value = {"python": platform.python_version(), "packages": packages,
             "database": {"path": str(db.DB_PATH or config.DB_PATH), **db.stats()},
             "web_build": (config.ROOT / "web" / "dist" / "index.html").is_file(),
             "tesseract": bool(shutil.which("tesseract")), "ollama": {"up": False, "models": []},
             "phoenix": {"up": False}, "mode": "offline rules are available",
             "paper_toolchain": bool(shutil.which("latexmk"))}
    try:
        import requests
        result = requests.get(config.OLLAMA_URL.rstrip("/") + "/api/tags", timeout=1)
        result.raise_for_status()
        value["ollama"] = {"up": True, "models": [row.get("name") for row in result.json().get("models", [])]}
    except Exception:
        pass
    if warm:
        value["warm"] = "No model download is performed. OCR initializes on the first image check."
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a printed batch against locally stored CDSCO alert lists.")
    commands = parser.add_subparsers(dest="command", required=True)
    doc = commands.add_parser("doctor", help="Report installed capabilities and local data")
    doc.add_argument("--warm", action="store_true")
    serve = commands.add_parser("serve", help="Serve the website and API")
    serve.add_argument("--lan", action="store_true", help="Listen on the local Wi-Fi network")
    serve.add_argument("--port", type=int, default=8000)
    sync = commands.add_parser("sync", help="Refresh regulator snapshots and recheck saved packs")
    sync.add_argument("--offline", action="store_true")
    sync.add_argument("--full", action="store_true")
    ingest = commands.add_parser("ingest", help="Index local regulator snapshots")
    ingest.add_argument("path", nargs="?")
    ingest.add_argument("--no-llm", action="store_true")
    ingest.add_argument("--resume", help="Idempotently continue local snapshot ingestion")
    commands.add_parser("stats", help="Print statistics from the local database")
    commands.add_parser("recheck", help="Recheck the saved cabinet")
    props = commands.add_parser("props", help="Render clearly marked synthetic demo packs")
    props.add_argument("--demo", action="store_true")
    check = commands.add_parser("check", help="Check typed batch details or one/two pack photos")
    check.add_argument("images", nargs="*")
    check.add_argument("--text")
    for field in ("product", "brand", "mfg", "exp", "maker"):
        check.add_argument("--" + field, default="")
    check.add_argument("--planner", choices=("rules", "hybrid", "llm"), default="rules")
    check.add_argument("--vlm", action="store_true")
    check.add_argument("--lang", default="en")
    evaluate = commands.add_parser("eval", help="Run authored offline synthetic diagnostics")
    evaluate.add_argument("--quick", action="store_true")
    commands.add_parser("selftest", help="Exercise synthetic scenarios through the local API")
    args = parser.parse_args(argv)
    db.init_db()
    if args.command == "doctor":
        output(doctor(args.warm))
    elif args.command == "serve":
        if not 1 <= args.port <= 65535:
            parser.error("--port must be between 1 and 65535")
        import uvicorn
        from server.app import create_app
        if not (config.ROOT / "web" / "dist" / "index.html").is_file():
            print("Build the website first: npm --prefix web run build")
        application = create_app(lan=args.lan, port=args.port)
        print(f"StripCheck: http://127.0.0.1:{args.port}")
        if args.lan:
            from server.app import _local_ip
            print(f"Phone pairing: http://{_local_ip()}:{args.port} (same trusted Wi-Fi)")
        uvicorn.run(application, host="0.0.0.0" if args.lan else "127.0.0.1", port=args.port)
    elif args.command == "sync":
        from core.supervisor import sync_and_recheck
        report = sync_and_recheck(offline=args.offline, full=args.full)
        output(report)
        return int(report.get("status") == "error")
    elif args.command == "ingest":
        from core.ingest import ingest_file, ingest_snapshots
        if args.resume:
            print("Continuing idempotent snapshot ingestion; previously imported snapshots are retained.")
        output(ingest_file(Path(args.path)) if args.path else ingest_snapshots())
    elif args.command == "stats":
        output(db.stats())
    elif args.command == "recheck":
        from core.supervisor import recheck_cabinet
        output(recheck_cabinet())
    elif args.command == "props":
        from core.props import demo_cases, render_demo
        output({"synthetic": True, "images": [{"id": case["id"], "path": str(render_demo(case["id"]))} for case in demo_cases()]})
    elif args.command == "check":
        from core.investigator import investigate
        fields = {name: getattr(args, name) for name in ("product", "brand", "mfg", "exp", "maker")}
        if args.text:
            fields.update(batch=args.text, source="user", confirmed=True)
        elif args.images:
            if len(args.images) > 2:
                parser.error("Choose no more than two images")
            from core.pack_tools import read_pack
            for filename in args.images:
                reading = read_pack(Path(filename))
                for key, value in reading.get("fields", {}).items():
                    if value and not fields.get(key):
                        fields[key] = value
        else:
            parser.error("check needs --text BATCH or an image path")
        from core.supervisor import confusion_counts, remember_correction
        from core.tracing import record
        thread_id = "check-" + uuid.uuid4().hex
        created_at = datetime.now(timezone.utc).isoformat()
        snapshot = investigate(fields, db.all_alerts(), context={"lang": args.lang, "planner": args.planner,
            "real_alert_count": db.stats()["alerts"], "confusion_counts": confusion_counts()})
        for _ in range(3):
            if snapshot.get("status") != "waiting" or not sys.stdin.isatty():
                break
            pending = snapshot["pending"]
            print(pending["question"])
            answer = input("Printed value (or skip): ").strip()
            response = {"skip": True} if answer.lower() == "skip" else {"typed": answer, "choice": answer}
            previous = snapshot
            snapshot = investigate(snapshot["fields"], db.all_alerts(), context=snapshot.get("context"), answer=response)
            remember_correction(thread_id, previous, snapshot, response)
        snapshot.update(thread_id=thread_id, created_at=created_at, updated_at=datetime.now(timezone.utc).isoformat(), demo=False)
        db.save_document("checks", thread_id, snapshot)
        for step in snapshot.get("history", []):
            record(thread_id, "step", step)
        if snapshot.get("final"):
            record(thread_id, "final", snapshot["final"])
        if snapshot.get("pending"):
            record(thread_id, "interrupt", snapshot["pending"])
        output({key: value for key, value in snapshot.items() if key != "context"})
    elif args.command == "eval":
        from core.evaluate import run_quick
        report = run_quick()
        output(report)
        return int(bool(report["failed"]))
    elif args.command == "selftest":
        from fastapi.testclient import TestClient
        from core.props import demo_cases
        from server.app import create_app
        cases = []
        with TestClient(create_app()) as client:
            for case in demo_cases():
                result = client.post("/api/demo/checks", json={"case_id": case["id"]}, headers={"Accept": "application/json"})
                result.raise_for_status()
                snapshot = result.json()
                for answer in case.get("answers", [])[:3]:
                    if snapshot["status"] != "waiting":
                        break
                    result = client.post(f"/api/checks/{snapshot['thread_id']}/resume", json=answer, headers={"Accept": "application/json"})
                    result.raise_for_status()
                    snapshot = result.json()
                actual = (snapshot.get("final") or {}).get("label") or snapshot["status"]
                cases.append({"id": case["id"], "expected": case["expected"], "actual": actual, "passed": actual == case["expected"]})
        report = {"synthetic": True, "total": len(cases), "passed": sum(case["passed"] for case in cases), "cases": cases}
        output(report)
        return int(report["passed"] != report["total"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"StripCheck could not complete: {exc}", file=sys.stderr)
        raise SystemExit(1)

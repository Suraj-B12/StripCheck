"""Deterministic synthetic diagnostics, separate from a research evaluation."""
import time
from datetime import datetime, timezone

from core import db


def run_quick(callback=None) -> dict:
    from core.investigator import investigate
    from core.props import demo_cases
    rows = []
    started = time.perf_counter()
    for index, case in enumerate(demo_cases()):
        before = time.perf_counter()
        alerts = case.get("alerts", [])
        state = investigate(dict(case.get("fields", {})), alerts, context={"demo": True, "real_alert_count": 0})
        answers = case.get("answers", [])
        if isinstance(answers, dict):
            answers = [answers]
        for answer in answers[:3]:
            if state.get("status") != "waiting":
                break
            state = investigate(state["fields"], alerts, context=state.get("context"), answer=answer)
        final = state.get("final") or {}
        expected = case.get("expected")
        if isinstance(expected, dict):
            expected = expected.get("label")
        actual = final.get("label") or state.get("status", "unknown")
        passed = actual == expected or (expected == "waiting" and state.get("status") == "waiting")
        row = {"id": case["id"], "name": case.get("name", case.get("title", case["id"])),
               "expected": expected, "actual": actual, "passed": passed,
               "latency_ms": round((time.perf_counter() - before) * 1000, 2), "synthetic": True}
        rows.append(row)
        if callback:
            callback({"type": "step", "node": "diagnostic", "step": index + 1,
                      "message": f"Checked synthetic scenario {index + 1}.", "result": row})
    report = {"id": "quick", "available": True, "kind": "synthetic_diagnostic", "synthetic": True,
              "title": "Offline synthetic diagnostics", "created_at": datetime.now(timezone.utc).isoformat(),
              "notice": "These authored scenarios check application behavior. They do not measure performance on real medicines or establish research accuracy.",
              "total": len(rows), "passed": sum(row["passed"] for row in rows),
              "failed": sum(not row["passed"] for row in rows), "rows": rows, "cases": rows,
              "duration_ms": round((time.perf_counter() - started) * 1000, 2)}
    db.save_document("evaluation", "latest", report)
    return report


def latest() -> dict:
    return db.get_document("evaluation", "latest") or {"available": False, "kind": "synthetic_diagnostic", "rows": [], "notice": "Run the offline diagnostics to see results."}

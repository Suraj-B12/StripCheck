"""Re-check saved batches and persist deduplicated local notifications."""
import hashlib
from datetime import date, datetime, timezone

from core import db


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _notification(item: dict, kind: str, message: str, alert_id: str = "") -> tuple[dict, bool]:
    key = hashlib.sha256(f"{item['id']}:{kind}:{alert_id}".encode()).hexdigest()[:24]
    old = db.get_document("notifications", key)
    if old:
        return old, False
    value = {"id": key, "cabinet_id": item["id"], "kind": kind, "message": message,
             "batch": item.get("fields", {}).get("batch", ""), "label": item.get("label", ""),
             "alert_id": alert_id or None, "created_at": now(), "seen": False}
    created = db.insert_child_document("notifications", key, value, "cabinet", item["id"])
    return value, created


def _expiry_date(value: str) -> date | None:
    for pattern in ("%Y-%m", "%m/%Y", "%m-%Y", "%b %Y", "%Y-%m-%d", "%m/%y"):
        try:
            parsed = datetime.strptime(str(value), pattern)
            # The label's expiry month extends through the end of that month.
            next_month = date(parsed.year + (parsed.month == 12), parsed.month % 12 + 1, 1)
            from datetime import timedelta
            return next_month - timedelta(days=1)
        except ValueError:
            continue
    return None


def recheck_cabinet(callback=None) -> dict:
    from core.investigator import investigate
    alerts = db.all_alerts()
    items = db.list_documents("cabinet", limit=1000)
    report = {"checked": 0, "listed": 0, "needs_review": 0, "notifications": 0, "demo_skipped": 0}
    for item in items:
        if item.get("demo"):
            report["demo_skipped"] += 1
            continue
        snapshot = investigate(item.get("fields", {}), alerts, context={
            "cabinet": True, "batch_evidence": item.get("batch_evidence"),
            "real_alert_count": len(alerts),
        })
        final = snapshot.get("final") or {}
        report["checked"] += 1
        item["last_checked"] = now()
        item["final"] = final or item.get("final")
        item["needs_review"] = snapshot.get("status") == "waiting" or final.get("label") == "CANT_VERIFY"
        if not db.save_existing_document("cabinet", item["id"], item):
            continue
        if final.get("label") in ("FLAGGED", "SUSPECTED_FAKE"):
            report["listed"] += 1
            citations = final.get("citations") or []
            alert_id = str(citations[0].get("alert_id", citations[0].get("id", "listed"))) if citations and isinstance(citations[0], dict) else "listed"
            _, created = _notification(item, "listed", final.get("headline", "A saved batch appears on a loaded alert list."), alert_id)
            report["notifications"] += int(created)
        elif item["needs_review"]:
            report["needs_review"] += 1
        expiry = _expiry_date(item.get("fields", {}).get("exp", ""))
        if expiry and (expiry - date.today()).days <= 30:
            _, created = _notification(item, "expiry", f"Review the printed expiry date for {item.get('label') or 'your saved pack'}: {item['fields']['exp']}.", str(expiry))
            report["notifications"] += int(created)
        if callback:
            callback({"type": "step", "node": "cabinet", "message": f"Rechecked {report['checked']} saved batches."})
    return report


def sync_and_recheck(callback=None, offline=False, full=False) -> dict:
    from core.portal import sync
    report = sync(callback=callback, offline=offline, full=full)
    report["cabinet"] = recheck_cabinet(callback)
    return report


def confusion_counts() -> list[dict]:
    """Read bounded, local, explicitly confirmed character counts."""
    db.init_db()
    with db.connect() as con:
        return [dict(row) for row in con.execute("SELECT ocr_char,true_char,source,count FROM confusions WHERE source IN ('user','calibration') ORDER BY ocr_char,true_char LIMIT 1000")]


def remember_correction(thread_id: str, previous: dict | None, snapshot: dict, answer: dict | None) -> int:
    """Record only accepted human corrections to photo reads, once per answer."""
    from core.textutils import CONFUSABLE, batch_key
    if not previous or not answer or previous.get("demo") or snapshot.get("demo"):
        return 0
    fields = previous.get("fields", {})
    if fields.get("source") not in {"ocr", "ocr_enh", "carton", "vlm"} or answer.get("source", "user") != "user":
        return 0
    state = snapshot.get("context", {}).get("_engine", {})
    if state.get("provenance", {}).get("batch") != "user" or state.get("batch_evidence") not in {"user_confirmed", "user_typed"}:
        return 0
    before, after = batch_key(fields.get("batch")), batch_key(snapshot.get("fields", {}).get("batch"))
    if not before or len(before) != len(after):
        return 0
    count = 0
    db.init_db()
    with db.connect() as con:
        for position, (read, true) in enumerate(zip(before, after)):
            if read == true or true not in CONFUSABLE.get(read, ""):
                continue
            event_key = f"correction:{thread_id}:{state.get('asks', 0)}:{position}:{read}:{true}"
            inserted = con.execute("INSERT OR IGNORE INTO kv(key,value) VALUES(?,?)", (event_key, '"user_confirmed"'))
            if inserted.rowcount:
                con.execute("""INSERT INTO confusions(ocr_char,true_char,source,count) VALUES(?,?,'user',1)
                    ON CONFLICT(ocr_char,true_char,source) DO UPDATE SET count=count+1""", (read, true))
                count += 1
    return count

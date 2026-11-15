"""Autonomous monitor: a supervisor agent that syncs, rechecks the cabinet and notifies on its own."""
import json
import os
import socket
import sys
import threading
import time
import uuid
from datetime import date, datetime, timedelta, timezone

from core import config, db

AGENT = "supervisor"
MAX_BACKOFF_HOURS = 24
FIRST_RUN_DELAY = 30  # seconds after server start
KEEP_CYCLES = 200
_lock = threading.Lock()
_stop = threading.Event()
_thread = None


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def enabled() -> bool:
    """Off with STRIPCHECK_MONITOR=0 and always off under pytest."""
    return os.environ.get("STRIPCHECK_MONITOR", "1") != "0" and "pytest" not in sys.modules


def interval_hours() -> float:
    try:
        value = float(os.environ.get("STRIPCHECK_MONITOR_HOURS", "6"))
    except ValueError:
        return 6.0
    if value != value:
        return 6.0
    return min(MAX_BACKOFF_HOURS, max(0.01, value))


def next_delay_seconds(failures: int, hours: float | None = None) -> float:
    """Normal interval, doubled per consecutive failure, capped at 24 h."""
    hours = interval_hours() if hours is None else hours
    return min(MAX_BACKOFF_HOURS, hours * (2 ** max(0, min(int(failures), 10)))) * 3600


def _parse(stamp):
    try:
        value = datetime.fromisoformat(str(stamp))
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def sync_due(today: date | None = None, hours: float | None = None, at: datetime | None = None) -> tuple[bool, str]:
    """Due when nothing is stored, the last good sync is older than the interval, or the newest month is stale."""
    today = today or date.today()
    at = at or datetime.now(timezone.utc)
    hours = interval_hours() if hours is None else hours
    stats = db.stats()
    latest = stats.get("latest_month")
    if not stats.get("has_data") or not latest:
        return True, "no alert data stored"
    last = _parse(db.get_value("last_sync"))
    if last is None:
        return True, "no completed sync recorded"
    age = (at - last).total_seconds() / 3600
    if age >= hours:
        return True, f"last sync {age:.1f} h ago"
    previous = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    if str(latest) < previous:
        return True, f"newest stored month {latest} is older than {previous}"
    return False, f"up to date (newest month {latest}, synced {age:.1f} h ago)"


def _online() -> bool:
    """Cheap reachability probe of the portal host; never raises."""
    if config.OFFLINE:
        return False
    try:
        with socket.create_connection(("cdscoonline.gov.in", 443), timeout=3):
            return True
    except OSError:
        return False


def _labels() -> dict:
    return {i["id"]: (i.get("final") or {}).get("label") for i in db.list_documents("cabinet", limit=1000) if i.get("id")}


def _log(record):
    try:
        config.RUNS_DIR.mkdir(parents=True, exist_ok=True)
        with (config.RUNS_DIR / "monitor.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True, default=str) + "\n")
    except OSError:
        pass


def _save_cycle(cycle):
    state = db.get_value("monitor_state", {}) or {}
    failures = state.get("failures", 0) + 1 if cycle["errors"] else 0
    delay = next_delay_seconds(failures)
    db.set_value("monitor_state", {
        "failures": failures, "last_cycle": cycle, "last_run": cycle["finished_at"],
        "next_run": (datetime.now(timezone.utc) + timedelta(seconds=delay)).isoformat(timespec="seconds")})
    db.save_document("monitor_cycles", cycle["id"], cycle)
    for stale in db.list_documents("monitor_cycles", limit=1000)[KEEP_CYCLES:]:
        db.delete_document("monitor_cycles", stale.get("id"))


def run_cycle(trigger: str = "schedule", _held: bool = False) -> dict:
    """One bounded monitor cycle. Never raises; returns the cycle record."""
    if not _held and not _lock.acquire(blocking=False):
        return {"status": "busy", "message": "A monitor cycle is already running"}
    cycle = {"id": uuid.uuid4().hex[:12], "agent": AGENT, "trigger": trigger, "started_at": now(),
             "decision": "", "reason": "", "new_alerts": 0, "packs_rechecked": 0, "notifications": 0,
             "errors": [], "steps": [], "status": "running"}
    started = time.monotonic()

    def step(name, **info):
        cycle["steps"].append({"agent": AGENT, "step": name, "at": now(), **info})

    try:
        db.init_db()
        before_ids = {n.get("id") for n in db.list_documents("notifications", limit=1000)}
        before_labels = _labels()
        try:
            due, reason = sync_due()
            step("decide", due=due, reason=reason)
            cycle["decision"], cycle["reason"] = ("sync" if due else "skip_up_to_date"), reason
            if due:
                if not _online():
                    cycle["decision"], cycle["reason"] = "skip_offline", "portal not reachable; using stored snapshots"
                    step("online_check", online=False)
                else:
                    step("online_check", online=True)
                    from core import portal
                    report = portal.sync(callback=None, offline=False, full=False)
                    cycle["new_alerts"] = int(report.get("added", 0) or 0)
                    step("sync", status=report.get("status"), added=cycle["new_alerts"],
                         fetched=len(report.get("fetched") or []))
                    if report.get("status") == "busy":
                        cycle["decision"], cycle["reason"] = "skip_busy", "another sync is running"
                    for error in (report.get("errors") or [])[:10]:
                        cycle["errors"].append(f"sync: {error.get('source', '')} {error.get('error', error)}"[:300])
        except Exception as exc:
            cycle["errors"].append(f"sync: {type(exc).__name__}: {exc}"[:300])
            step("sync_failed", error=type(exc).__name__)
        try:
            from core import supervisor
            report = supervisor.recheck_cabinet()
            cycle["packs_rechecked"] = report.get("checked", 0)
            step("recheck", **{k: report.get(k, 0) for k in ("checked", "listed", "needs_review")})
            for item in db.list_documents("cabinet", limit=1000):
                old, new = before_labels.get(item.get("id")), (item.get("final") or {}).get("label")
                if item.get("demo") or not old or not new or old == new:
                    continue
                headline = (item.get("final") or {}).get("headline", "")
                supervisor._notification(item, "status_changed", f"{item.get('label') or 'Saved pack'}: {headline}", new)
                step("status_changed", pack=item.get("id"), was=old, now=new)
        except Exception as exc:
            cycle["errors"].append(f"recheck: {type(exc).__name__}: {exc}"[:300])
            step("recheck_failed", error=type(exc).__name__)
        cycle["notifications"] = len({n.get("id") for n in db.list_documents("notifications", limit=1000)} - before_ids)
    except Exception as exc:  # the database itself failed; still never crash the caller
        cycle["errors"].append(f"{type(exc).__name__}: {exc}"[:300])
    finally:
        cycle["finished_at"] = now()
        cycle["seconds"] = round(time.monotonic() - started, 2)
        cycle["status"] = "error" if cycle["errors"] else "ok"
        try:
            _save_cycle(cycle)
        except Exception:
            pass
        _log(cycle)
        if not _held:
            _lock.release()
    return cycle


def start_cycle_async(trigger: str = "manual", db_path=None) -> bool:
    """Run one cycle in a background thread; False when one is already running."""
    if not _lock.acquire(blocking=False):
        return False
    path = db_path or db.DB_PATH or config.DB_PATH

    def work():
        try:
            with db.using_database(path):
                run_cycle(trigger, _held=True)
        finally:
            _lock.release()
    threading.Thread(target=work, name="stripcheck-monitor-run", daemon=True).start()
    return True


def status() -> dict:
    state = db.get_value("monitor_state", {}) or {}
    return {"enabled": enabled(), "running": _lock.locked(), "interval_hours": interval_hours(),
            "failures": state.get("failures", 0), "last_run": state.get("last_run"),
            "next_run": state.get("next_run"), "last_cycle": state.get("last_cycle")}


def _loop(db_path):
    with db.using_database(db_path):
        wait = FIRST_RUN_DELAY
        due = _parse((db.get_value("monitor_state", {}) or {}).get("next_run"))
        if due:
            wait = max(FIRST_RUN_DELAY, (due - datetime.now(timezone.utc)).total_seconds())
        while not _stop.wait(min(wait, 3600)):
            due = _parse((db.get_value("monitor_state", {}) or {}).get("next_run"))
            remaining = (due - datetime.now(timezone.utc)).total_seconds() if due else 0
            if remaining > 1:
                wait = remaining
                continue
            run_cycle("schedule")
            wait = next_delay_seconds((db.get_value("monitor_state", {}) or {}).get("failures", 0))


def start(db_path=None) -> bool:
    """Start the single background thread; no-op when disabled or already running."""
    global _thread
    if not enabled() or (_thread and _thread.is_alive()):
        return False
    _stop.clear()
    _thread = threading.Thread(target=_loop, args=(db_path or db.DB_PATH or config.DB_PATH,), name="stripcheck-monitor", daemon=True)
    _thread.start()
    return True


def stop() -> None:
    _stop.set()

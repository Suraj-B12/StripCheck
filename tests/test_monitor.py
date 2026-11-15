"""Autonomous monitor agent: decisions, backoff, notifications and locking with the portal mocked."""
import threading
from datetime import date, datetime, timedelta, timezone

from fastapi.testclient import TestClient

from core import config, db, monitor


def _setup(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(db, "DB_PATH", None)
    db.init_db(tmp_path / "monitor.db")


def _alert_row(db_month):
    with db.connect() as con:
        con.execute("INSERT INTO alerts(row_hash,list_kind,list_month,entry_type,batch_key,batch_raw) VALUES('h1','nsq',?,'NSQ','B1','B1')", (db_month,))


def _fresh_data(months_ago=0, synced_hours_ago=1):
    today = date.today().replace(day=1)
    month = today
    for _ in range(months_ago):
        month = (month - timedelta(days=1)).replace(day=1)
    _alert_row(month.strftime("%Y-%m"))
    db.set_value("last_sync", (datetime.now(timezone.utc) - timedelta(hours=synced_hours_ago)).isoformat())


def _no_sync(monkeypatch):
    from core import portal
    def boom(**kwargs):
        raise AssertionError("sync must not run")
    monkeypatch.setattr(portal, "sync", boom)


def test_skips_sync_when_up_to_date(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    _fresh_data()
    _no_sync(monkeypatch)
    cycle = monitor.run_cycle("test")
    assert cycle["decision"] == "skip_up_to_date" and cycle["status"] == "ok"
    assert (config.RUNS_DIR / "monitor.jsonl").is_file()
    assert db.get_value("monitor_state")["failures"] == 0
    assert all(s["agent"] == "supervisor" for s in cycle["steps"])


def test_runs_sync_and_recheck_when_due(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    _fresh_data(months_ago=3, synced_hours_ago=48)
    from core import portal, investigator
    monkeypatch.setattr(monitor, "_online", lambda: True)
    monkeypatch.setattr(portal, "sync", lambda **kw: {"status": "complete", "added": 4, "fetched": [{}], "errors": []})
    db.save_document("cabinet", "p1", {"id": "p1", "label": "Pack", "fields": {"batch": "B9"}, "final": {"label": "NOT_LISTED"}})
    monkeypatch.setattr(investigator, "investigate", lambda f, a, context: {"status": "done", "final": {"label": "NOT_LISTED", "headline": "No matching alert found"}})
    cycle = monitor.run_cycle("test")
    assert cycle["decision"] == "sync" and cycle["new_alerts"] == 4 and cycle["packs_rechecked"] == 1
    assert cycle["notifications"] == 0 and cycle["status"] == "ok"


def test_offline_records_skip_without_exception(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    monkeypatch.setattr(monitor, "_online", lambda: False)
    _no_sync(monkeypatch)
    cycle = monitor.run_cycle("test")
    assert cycle["decision"] == "skip_offline" and cycle["errors"] == []
    assert db.list_documents("monitor_cycles")[0]["id"] == cycle["id"]


def test_sync_exception_is_caught_and_backs_off(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    from core import portal
    monkeypatch.setattr(monitor, "_online", lambda: True)
    def fail(**kwargs):
        raise RuntimeError("portal exploded")
    monkeypatch.setattr(portal, "sync", fail)
    first = monitor.run_cycle("test")
    assert first["status"] == "error" and db.get_value("monitor_state")["failures"] == 1
    monitor.run_cycle("test")
    assert db.get_value("monitor_state")["failures"] == 2
    monkeypatch.setattr(portal, "sync", lambda **kw: {"status": "complete", "added": 0, "fetched": [], "errors": []})
    monitor.run_cycle("test")
    assert db.get_value("monitor_state")["failures"] == 0


def test_notifications_only_on_status_change(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    _fresh_data()
    from core import investigator
    db.save_document("cabinet", "p1", {"id": "p1", "label": "Pack", "fields": {"batch": "B9"}, "final": {"label": "CANT_VERIFY"}})
    outcome = {"label": "CANT_VERIFY", "headline": "More evidence is needed"}
    monkeypatch.setattr(investigator, "investigate", lambda f, a, context: {"status": "done", "final": dict(outcome)})
    assert monitor.run_cycle("test")["notifications"] == 0
    outcome.update(label="NOT_LISTED", headline="No matching alert found")
    changed = monitor.run_cycle("test")
    assert changed["notifications"] == 1
    note = db.list_documents("notifications")[0]
    assert note["kind"] == "status_changed" and "No matching alert found" in note["message"]
    assert monitor.run_cycle("test")["notifications"] == 0


def test_schedule_and_backoff_math(monkeypatch):
    monkeypatch.setenv("STRIPCHECK_MONITOR_HOURS", "6")
    assert monitor.interval_hours() == 6
    assert monitor.next_delay_seconds(0) == 6 * 3600
    assert monitor.next_delay_seconds(1) == 12 * 3600
    assert monitor.next_delay_seconds(2) == 24 * 3600
    assert monitor.next_delay_seconds(9) == 24 * 3600
    monkeypatch.setenv("STRIPCHECK_MONITOR_HOURS", "nonsense")
    assert monitor.interval_hours() == 6
    monkeypatch.setenv("STRIPCHECK_MONITOR_HOURS", "1000")
    assert monitor.interval_hours() == 24


def test_sync_due_rules(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    assert monitor.sync_due()[0]
    _fresh_data()
    assert not monitor.sync_due()[0]
    assert monitor.sync_due(at=datetime.now(timezone.utc) + timedelta(hours=7))[0]
    assert monitor.sync_due(today=date.today() + timedelta(days=75))[0]


def test_lock_prevents_overlap(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    _fresh_data()
    assert monitor._lock.acquire(blocking=False)
    try:
        assert monitor.run_cycle("test")["status"] == "busy"
        assert monitor.start_cycle_async("test") is False
        client = TestClient(__import__("server.app", fromlist=["create_app"]).create_app(tmp_path / "monitor.db"))
        assert client.post("/api/monitor/run").status_code == 409
        assert client.get("/api/monitor").json()["running"] is True
    finally:
        monitor._lock.release()


def test_manual_run_endpoint_returns_immediately(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    _fresh_data()
    _no_sync(monkeypatch)
    from server.app import create_app
    client = TestClient(create_app(tmp_path / "monitor.db"))
    assert client.post("/api/monitor/run").status_code == 202
    for _ in range(100):
        if not monitor._lock.locked():
            break
        threading.Event().wait(0.05)
    body = client.get("/api/monitor").json()
    assert body["last_cycle"]["trigger"] == "manual" and body["next_run"]


def test_disabled_in_tests_and_by_env(tmp_path, monkeypatch):
    assert monitor.enabled() is False  # pytest is loaded
    assert monitor.start() is False
    from server.app import create_app
    with TestClient(create_app(tmp_path / "m.db", monitor=True)):
        assert monitor._thread is None or not monitor._thread.is_alive()

"""Synthetic local cabinet notification behavior."""
from core import config, db
from core.supervisor import recheck_cabinet


def test_cabinet_notifications_are_deduplicated_and_seen_state_survives(tmp_path, monkeypatch):
    from core import investigator
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", None)
    db.init_db(tmp_path / "supervisor.db")
    db.save_document("cabinet", "synthetic-pack", {"id": "synthetic-pack", "label": "Synthetic test pack", "fields": {"batch": "SYNTHETIC123"}, "batch_evidence": "user_confirmed"})
    def synthetic_investigation(fields, alerts, context):
        assert context["cabinet"] and context["batch_evidence"] == "user_confirmed"
        return {"status": "done", "final": {"label": "FLAGGED", "headline": "Synthetic listed batch", "citations": [{"id": "synthetic-alert"}]}}
    monkeypatch.setattr(investigator, "investigate", synthetic_investigation)
    first = recheck_cabinet()
    assert first["listed"] == 1 and first["notifications"] == 1
    notification = db.list_documents("notifications")[0]
    assert notification["batch"] == "SYNTHETIC123"
    notification["seen"] = True
    db.save_document("notifications", notification["id"], notification)
    second = recheck_cabinet()
    assert second["notifications"] == 0
    assert len(db.list_documents("notifications")) == 1
    assert db.list_documents("notifications")[0]["seen"]


def test_cabinet_abstention_requests_review_without_a_listed_notice(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", None)
    db.init_db(tmp_path / "supervisor.db")
    db.save_document("cabinet", "synthetic-pack", {"id": "synthetic-pack", "fields": {"batch": "SYNTHETIC123", "source": "user"}, "batch_evidence": "user_typed"})
    report = recheck_cabinet()
    assert report["checked"] == 1 and report["needs_review"] == 1
    assert report["listed"] == 0
    assert db.list_documents("notifications") == []


def test_correction_ledger_is_idempotent_and_rejects_nonhuman_reads(tmp_path, monkeypatch):
    from core.supervisor import remember_correction, confusion_counts
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", None)
    db.init_db(tmp_path / "learning.db")
    previous = {"fields": {"batch": "AB8", "source": "ocr"}}
    snapshot = {"fields": {"batch": "ABB"}, "context": {"_engine": {"asks": 1, "provenance": {"batch": "user"}, "batch_evidence": "user_confirmed"}}}
    assert remember_correction("synthetic-test", previous, snapshot, {"typed": "ABB"}) == 1
    assert remember_correction("synthetic-test", previous, snapshot, {"typed": "ABB"}) == 0
    assert remember_correction("synthetic-test-2", previous, snapshot, {"source": "carton"}) == 0
    assert remember_correction("synthetic-test-3", {**previous, "demo": True}, snapshot, {"typed": "ABB"}) == 0
    assert confusion_counts()[0]["count"] == 1

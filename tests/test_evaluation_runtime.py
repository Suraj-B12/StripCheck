"""Diagnostics are reproducible, isolated, and described as synthetic."""
from core import config, db
from core.evaluate import run_quick, latest


def test_synthetic_diagnostic_is_not_a_research_accuracy_claim(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", None)
    db.init_db(tmp_path / "evaluation.db")
    assert latest()["available"] is False
    first = run_quick()
    second = run_quick()
    assert first["synthetic"] and first["kind"] == "synthetic_diagnostic"
    assert first["failed"] == 0, first["rows"]
    assert first["total"] >= 5
    assert [(row["id"], row["actual"]) for row in first["rows"]] == [(row["id"], row["actual"]) for row in second["rows"]]
    assert "do not measure" in first["notice"]
    assert latest()["available"]
    assert db.stats()["alerts"] == 0

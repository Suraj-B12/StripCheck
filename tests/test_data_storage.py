"""Synthetic fixtures only: persistence, provenance and cleaning contracts."""
import hashlib
import json
from pathlib import Path
import pytest
from core import config, db
from core.ingest import clean_row, ingest_file, ingest_snapshots

@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(db, "DB_PATH", None)
    db.init_db()
    return tmp_path

def row(**overrides):
    return {"str_product_name": "Synthetic Lumera Tablets (Lumera)", "str_brand_name": "NA",
            "str_batch_no": "LX-240B", "str_manufactured_by": "Example Laboratories, Example City",
            "dt_manufacturing_date": "08/2024", "dt_expiry_date": "07/2027",
            "str_reporting_source": "CDSCO Labs", "str_reported_by_lab_or_state": "CDL, Kolkata",
            "str_nsq_result": "Synthetic dissolution result", "dt_reporting_month_year": "SEP-2026", **overrides}

def snapshot(folder, rows, month="2026-09"):
    path = folder / "raw" / "portal" / "nsq" / f"{month}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps({"aaData": rows}, ensure_ascii=False).encode("latin-1")
    path.write_bytes(raw)
    path.with_suffix(".meta.json").write_text(json.dumps({"url": "https://example.invalid/synthetic-fixture",
                "sha256": hashlib.sha256(raw).hexdigest(), "rows": len(rows), "fetched_at": "2026-10-27T00:00:00Z"}))
    return path

def test_schema_idempotent_and_documents(isolated):
    db.init_db(); db.init_db()
    with db.connect() as con:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"alerts", "sources", "quarantine", "checks", "cabinet", "documents", "confusions", "notifications"} <= tables
    db.save_document("cabinet", "one", {"label": "First"})
    db.save_document("cabinet", "one", {"label": "Updated"})
    assert db.get_document("cabinet", "one")["label"] == "Updated"
    assert len(db.list_documents("cabinet")) == 1
    assert db.delete_document("cabinet", "one") is True
    assert db.get_document("cabinet", "one") is None

def test_cleaning_rules():
    values, errors = clean_row(row(str_batch_no="(10)LX?240B; LZ-241C.", str_product_name="Synthetic Lumera Tablets (Lumera)"), "2026-09")
    assert not errors
    assert [value["batch_raw"] for value in values] == ["LX-240B", "LZ-241C"]
    assert values[0]["brand"] == "Lumera"
    assert values[0]["list_level"] == "central"
    assert values[0]["reported_by"] == "CDL Kolkata"
    assert "multi_batch_split" in values[0]["flags"]
    assert values[0]["mfg"] == "2024-08"

@pytest.mark.parametrize("batch", ["NM", "Not mentioned", "Up -to -01", "-"])
def test_placeholder_batches_quarantine(batch):
    assert "batch_placeholder" in clean_row(row(str_batch_no=batch), "2026-09")[1]

def test_no_split_on_slash_and_missing_maker():
    values, errors = clean_row(row(str_batch_no="CBC-0012/25", str_manufactured_by="NIL,NIL NIL"), "2026-09")
    assert len(values) == 1
    assert values[0]["batch_raw"] == "CBC-0012/25"
    assert "maker_missing" in errors
    values, errors = clean_row(row(str_manufactured_by="NIL,NIL NIL"), "2026-09", "spurious")
    assert not errors and values[0]["entry_type"] == "SPURIOUS"

def test_shorthand_multi_batch_is_not_invented():
    _, errors = clean_row(row(str_batch_no="SYN2408A&B"), "2026-09")
    assert "ambiguous_multi_batch" in errors

def test_short_batch_is_retained_and_date_shifts_are_quarantined():
    values, errors = clean_row(row(str_batch_no="A-1"), "2026-09")
    assert not errors
    assert values[0]["batch_key"] == "A1" and "batch_short" in values[0]["flags"]
    assert "batch_is_date" in clean_row(row(str_batch_no="08/2024"), "2026-09")[1]
    assert not clean_row(row(str_batch_no="SYN-03/24"), "2026-09")[1]
    assert not clean_row(row(str_batch_no="APRCT-2501"), "2026-09")[1]
    values, errors = clean_row(row(dt_manufacturing_date="08/2028", dt_expiry_date="07/2027"), "2026-09")
    assert not errors
    assert {"mfg_after_exp", "mfg_after_list_month"} <= set(values[0]["flags"])

def test_month_and_device_flags():
    values, _ = clean_row(row(str_product_name="Synthetic cotton gauze", dt_reporting_month_year="AUG-2026"), "2026-09")
    assert values[0]["list_month"] == "2026-09"
    assert {"month_mismatch", "non_drug"} <= set(values[0]["flags"])

def test_ingest_latin1_idempotent_provenance(isolated):
    path = snapshot(isolated, [row(str_product_name="Synthétique Lumera Tablets")])
    assert ingest_file(path)["added"] == 1
    assert ingest_file(path)["added"] == 0
    result = db.list_alerts(q="Lumera")
    assert result["total"] == 1
    detail = db.alert_detail(result["items"][0]["id"])
    assert detail["product"] == "Synthétique Lumera Tablets"
    assert detail["source_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert Path(detail["source_file"]).read_bytes() == path.read_bytes()
    assert detail["raw"]["str_batch_no"] == "LX-240B"
    assert detail["source_title"].startswith("Stored NSQ snapshot")

def test_revision_preserves_vanished_rows_and_bytes(isolated):
    path = snapshot(isolated, [row(), row(str_batch_no="OTHER123")])
    ingest_file(path)
    previous = db.all_alerts()
    path = snapshot(isolated, [row()])
    assert ingest_file(path)["added"] == 0
    assert len(db.all_alerts()) == 1
    removed = next(item for item in previous if item["batch_key"] == "OTHER123")
    assert db.alert_detail(removed["id"])["removed_at"]
    assert Path(removed["source_file"]).exists()
    # Publishers can revert to an earlier snapshot; previously removed rows must return.
    path = snapshot(isolated, [row(), row(str_batch_no="OTHER123")])
    ingest_file(path)
    assert len(db.all_alerts()) == 2

def test_invalid_rows_quarantined_and_bad_checksum_rejected(isolated):
    path = snapshot(isolated, [row(str_batch_no="NM")])
    assert ingest_file(path)["quarantined"] == 1
    assert db.stats()["total"] == 0
    assert "batch_placeholder" in db.list_documents("quarantine")[0]["reasons"]
    path.write_bytes(b'{"aaData":[]}')
    with pytest.raises(ValueError, match="checksum"):
        ingest_file(path)

def test_offline_uses_stored_sources(isolated):
    snapshot(isolated, [row()])
    assert ingest_snapshots()["added"] == 1
    assert ingest_snapshots()["added"] == 0

def test_parser_version_revalidates_cached_sources(isolated, monkeypatch):
    from core import ingest
    path = snapshot(isolated, [row()])
    ingest_file(path)
    original_id = db.all_alerts()[0]["id"]
    monkeypatch.setattr(ingest, "CLEANING_VERSION", "test-new-parser")
    result = ingest_file(path)
    assert result["added"] == 0 and result["unchanged"] is False
    assert db.all_alerts()[0]["id"] == original_id
    assert ingest_file(path)["unchanged"] is True

def test_empty_database_has_no_fabricated_data(isolated):
    assert not db.stats()["has_data"]
    assert db.list_alerts()["items"] == []

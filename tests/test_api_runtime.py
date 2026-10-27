"""Offline API tests using an isolated database and synthetic evidence."""
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from core import config, db
from server.app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "checks.db")
    monkeypatch.setattr(db, "DB_PATH", None)
    with TestClient(create_app(tmp_path / "checks.db")) as test_client:
        yield test_client


def events(response):
    result = []
    for chunk in response.text.split("\n\n"):
        if chunk.startswith("event: "):
            name, data = chunk.split("\n", 1)
            result.append((name[7:], json.loads(data[6:])))
    return result


def test_empty_database_is_honest_and_json_check_persists(client):
    assert client.get("/api/health").json()["db"]["alerts"] == 0
    response = client.post("/api/checks", json={"batch": "SYNTHETIC123"}, headers={"Accept": "application/json"})
    assert response.status_code == 200
    snapshot = response.json()
    assert snapshot["final"]["label"] == "CANT_VERIFY"
    assert snapshot["final"]["reason"] == "no_data"
    assert "context" not in snapshot
    assert client.get(f"/api/checks/{snapshot['thread_id']}").json()["final"] == snapshot["final"]
    assert client.get("/api/checks").json()["items"][0]["thread_id"] == snapshot["thread_id"]
    assert client.post(f"/api/checks/{snapshot['thread_id']}/resume", json={"skip": True}).status_code == 409


def test_all_sse_events_identify_thread_and_finish(client):
    response = client.post("/api/checks", json={"batch": "SYNTHETIC123"})
    assert response.headers["content-type"].startswith("text/event-stream")
    stream = events(response)
    assert stream[-1][0] == "done"
    assert {name for name, _ in stream} >= {"fields", "strip", "step", "final", "snapshot", "done"}
    identifiers = {data["thread_id"] for _, data in stream}
    assert len(identifiers) == 1
    trace = client.get(f"/api/traces/{identifiers.pop()}").json()
    assert trace["items"] and trace["backend"] == "local_jsonl"


def test_every_authored_demo_resumes_and_never_populates_real_index(client):
    from core.props import demo_cases
    public = client.get("/api/demo/cases").json()
    assert public["synthetic"]
    assert "alerts" not in public["items"][0]
    for case in demo_cases():
        response = client.post("/api/demo/checks", json={"case_id": case["id"]}, headers={"Accept": "application/json"})
        assert response.status_code == 200, response.text
        snapshot = response.json()
        assert snapshot["demo"]
        for answer in case["answers"]:
            if snapshot["status"] != "waiting":
                break
            response = client.post(f"/api/checks/{snapshot['thread_id']}/resume", json=answer, headers={"Accept": "application/json"})
            assert response.status_code == 200, response.text
            snapshot = response.json()
        assert snapshot["status"] == "done", case["id"]
        assert snapshot["final"]["label"] == case["expected"], (case["id"], snapshot)
    assert client.get("/api/stats").json()["alerts"] == 0


def test_cabinet_saves_durably_deletes_and_skips_demo_recheck(client):
    from core.props import demo_cases
    case = next(case for case in demo_cases() if case["expected"] == "NOT_LISTED")
    snapshot = client.post("/api/demo/checks", json={"case_id": case["id"]}, headers={"Accept": "application/json"}).json()
    for answer in case["answers"]:
        if snapshot["status"] == "waiting":
            snapshot = client.post(f"/api/checks/{snapshot['thread_id']}/resume", json=answer, headers={"Accept": "application/json"}).json()
    saved = client.post("/api/cabinet", json={"thread_id": snapshot["thread_id"], "label": "Synthetic pack"}).json()
    assert saved["demo"]
    assert client.post("/api/cabinet", json={"thread_id": snapshot["thread_id"]}).json()["id"] == saved["id"]
    assert len(client.get("/api/cabinet").json()["items"]) == 1
    assert client.post("/api/cabinet/recheck").json()["demo_skipped"] == 1
    assert client.delete(f"/api/cabinet/{saved['id']}").json()["deleted"]
    assert client.get("/api/cabinet").json()["items"] == []


def test_invalid_input_and_image_cannot_be_interpreted_as_evidence(client):
    assert client.post("/api/checks", json={"batch": ""}).status_code == 422
    assert client.post("/api/checks", json={"batch": ["BAD"]}).status_code == 422
    assert client.post("/api/checks", content="not json", headers={"Content-Type": "application/json"}).status_code == 400
    response = client.post("/api/checks", files={"images": ("photo.png", b"this is not an image", "image/png")})
    assert response.status_code == 422
    assert "error" in response.json()
    assert client.get("/api/checks").json()["items"] == []


def test_upload_reencodes_image_generated_filename_and_runs_local_reader(client, monkeypatch):
    from core import pack_tools
    seen = []
    def read_pack(path):
        seen.append(Path(path))
        return {"fields": {"batch": "SYNTHETIC999", "source": "ocr", "confirmed": False}, "warnings": ["Synthetic test reader"]}
    monkeypatch.setattr(pack_tools, "read_pack", read_pack)
    buffer = io.BytesIO()
    Image.new("RGB", (100, 100), "white").save(buffer, "PNG")
    response = client.post("/api/checks", files={"images": ("../../escape.png", buffer.getvalue(), "image/png")}, headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert seen[0].parent == config.DATA_DIR / "uploads"
    assert seen[0].name != "escape.png"
    assert response.json()["fields"]["source"] == "ocr"
    assert response.json()["warnings"] == ["Synthetic test reader"]


def test_upload_count_and_size_are_bounded(client):
    payload = io.BytesIO()
    Image.new("RGB", (1, 1), "white").save(payload, "PNG")
    files = [("images", (f"{i}.png", payload.getvalue(), "image/png")) for i in range(3)]
    assert client.post("/api/checks", files=files).status_code == 400
    too_big = b"x" * (15 * 1024 * 1024 + 1)
    assert client.post("/api/checks", files={"images": ("large.png", too_big, "image/png")}).status_code == 413


def test_sync_offline_and_pairing(client):
    report = client.post("/api/sync", json={"offline": True}, headers={"Accept": "application/json"}).json()
    assert report["offline"]
    assert report["added"] == 0
    assert report["cabinet"]["checked"] == 0
    assert client.get("/api/lan").json()["enabled"] is False
    assert client.get("/api/lan/qr.png").headers["content-type"] == "image/png"
    assert client.get("/api/does-not-exist").status_code == 404


def test_lan_pairing_requires_token_and_remembers_cookie(tmp_path, monkeypatch):
    monkeypatch.setenv("STRIPCHECK_LAN_TOKEN", "synthetic-test-pairing-key")
    monkeypatch.setattr(db, "DB_PATH", None)
    with TestClient(create_app(tmp_path / "lan.db", lan=True)) as client:
        assert client.get("/api/health").status_code == 401
        assert client.get("/api/health?k=wrong").status_code == 401
        response = client.get("/api/health?k=synthetic-test-pairing-key")
        assert response.status_code == 200
        assert "HttpOnly" in response.headers["set-cookie"]
        assert client.get("/api/health").status_code == 200


def test_pending_state_survives_app_recreation_and_invalid_answer(client):
    snapshot = client.post("/api/demo/checks", json={"case_id": "01"}, headers={"Accept": "application/json"}).json()
    assert snapshot["status"] == "waiting"
    thread_id = snapshot["thread_id"]
    with TestClient(create_app(db.DB_PATH)) as reopened:
        restored = reopened.get(f"/api/checks/{thread_id}").json()
        assert restored["pending"] == snapshot["pending"]
        invalid = reopened.post(f"/api/checks/{thread_id}/resume", json={"choice": "Yes"}, headers={"Accept": "application/json"}).json()
        assert invalid["status"] == "waiting"
        assert invalid["pending"]["error"]
        final = reopened.post(f"/api/checks/{thread_id}/resume", json={"typed": "LM2408B"}, headers={"Accept": "application/json"}).json()
        assert final["final"]["label"] == "FLAGGED"
        assert final["fields"]["confirmed"]


def test_diagnostics_api_sse_persists_report(client):
    response = client.post("/api/eval/quick", json={})
    stream = events(response)
    assert stream[-1][0] == "done"
    report = next(data for name, data in stream if name == "report")
    assert report["total"] == 11 and report["failed"] == 0
    assert client.get("/api/eval/latest").json()["rows"] == report["rows"]


def test_foreign_browser_origin_cannot_mutate_local_store(client):
    response = client.post("/api/checks", json={"batch": "SYNTHETIC"}, headers={"Origin": "https://unrelated.example"})
    assert response.status_code == 403
    response = client.post("/api/checks", json={"batch": "SYNTHETIC"}, headers={"Origin": "http://testserver", "Accept": "application/json"})
    assert response.status_code == 200


def test_sync_rejects_concurrent_run(client):
    client.app.state.sync_lock.acquire()
    try:
        response = client.post("/api/sync", json={"offline": True})
        assert response.status_code == 409
    finally:
        client.app.state.sync_lock.release()


def test_check_rejects_concurrent_resume(client):
    snapshot = client.post("/api/demo/checks", json={"case_id": "01"}, headers={"Accept": "application/json"}).json()
    thread_id = snapshot["thread_id"]
    client.app.state.busy_checks.add(thread_id)
    try:
        response = client.post(f"/api/checks/{thread_id}/resume", json={"typed": "LM2408B"})
        assert response.status_code == 409
    finally:
        client.app.state.busy_checks.discard(thread_id)


def test_nested_fields_and_boolean_options_validate_without_server_errors(client):
    assert client.post("/api/checks", json={"fields": []}).status_code == 422
    assert client.post("/api/checks", json={"fields": None}).status_code == 422
    assert client.post("/api/sync", json={"offline": "false"}).status_code == 422
    snapshot = client.post("/api/demo/checks", json={"case_id": "01"}, headers={"Accept": "application/json"}).json()
    url = f"/api/checks/{snapshot['thread_id']}/resume"
    assert client.post(url, json={"fields": []}).status_code == 422
    assert client.post(url, json={"skip": "false"}).status_code == 422


def test_coverage_scope_is_explicit_in_health_and_stats(client):
    health = client.get("/api/health").json()
    stats = client.get("/api/stats").json()
    assert health["coverage"]["scope"] == "loaded_lists_only"
    assert health["coverage"]["limited"]
    assert stats["coverage_warning"] == health["coverage_warning"]
    assert stats["coverage"]["month_count"] == 0


def test_heic_photo_is_decoded_locally(client, monkeypatch):
    pillow_heif = pytest.importorskip("pillow_heif")
    pillow_heif.register_heif_opener()
    from core import pack_tools
    monkeypatch.setattr(pack_tools, "read_pack", lambda path: {"fields": {"batch": "SYNTHETIC-HEIC", "source": "ocr"}, "warnings": []})
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), "white").save(buffer, "HEIF")
    response = client.post("/api/checks", files={"image": ("pack.heic", buffer.getvalue(), "image/heic")}, headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.json()["fields"]["batch"] == "SYNTHETIC-HEIC"


def test_real_photo_correction_is_learned_once_but_never_auto_confirms(client, monkeypatch):
    from core import pack_tools
    from core.props import demo_cases
    from core.supervisor import confusion_counts
    case = next(case for case in demo_cases() if case["id"] == "03")
    # This synthetic in-memory fixture models the shape of a loaded source record.
    # It never enters the real database or the demo namespace.
    alert = dict(case["alerts"][0], synthetic=False, flags=[], source_title="Unit-test source fixture", source_url="https://example.invalid/unit-test-source")
    monkeypatch.setattr(db, "batch_alerts", lambda *_args, **_kwargs: [alert])
    monkeypatch.setattr(db, "check_coverage", lambda: {"real_alert_count": 1, "latest_month": "2026-09", "list_count": 1})
    monkeypatch.setattr(pack_tools, "read_pack", lambda path: {"fields": case["fields"], "warnings": []})
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), "white").save(buffer, "PNG")
    def photo_check():
        return client.post("/api/checks", files={"image": ("test.png", buffer.getvalue(), "image/png")}, headers={"Accept": "application/json"}).json()
    snapshot = photo_check()
    assert snapshot["pending"]["kind"] == "confirm_char"
    thread_id = snapshot["thread_id"]
    result = client.post(f"/api/checks/{thread_id}/resume", json={"choice": "LM2408B"}, headers={"Accept": "application/json"}).json()
    assert result["final"]["label"] == "FLAGGED"
    assert confusion_counts() == [{"ocr_char": "8", "true_char": "B", "source": "user", "count": 1}]
    assert client.post(f"/api/checks/{thread_id}/resume", json={"choice": "LM2408B"}).status_code == 409
    next_check = photo_check()
    assert next_check["status"] == "waiting" and next_check["pending"]["kind"] == "confirm_char"
    assert any("Prior confirmed corrections: 8 to B: 1" in step["summary"] for step in next_check["history"])
    assert next_check["fields"]["batch"] == "LM24088"
    demo = client.post("/api/demo/checks", json={"case_id": "03"}, headers={"Accept": "application/json"}).json()
    client.post(f"/api/checks/{demo['thread_id']}/resume", json={"choice": "LM2408B"}, headers={"Accept": "application/json"})
    assert confusion_counts()[0]["count"] == 1

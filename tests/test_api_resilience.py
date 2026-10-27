"""Concurrency, persistence, migration, resource and upload-limit regressions."""
import asyncio
import io
import json
import sqlite3
import threading
import time
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from starlette.requests import Request

from core import config, db
import server.app as app_module
from server.app import create_app
from server.sse import stream_work


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", None)
    return create_app(tmp_path / "checks.db")


def test_db_transactions_close_connections_and_rollback(isolated):
    with db.connect() as con:
        con.execute("INSERT INTO kv VALUES('unit-test-close','value')")
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        con.execute("SELECT 1")
    with pytest.raises(RuntimeError):
        with db.connect() as failed:
            failed.execute("INSERT INTO kv VALUES('unit-test-rollback','value')")
            raise RuntimeError("Synthetic interruption")
    assert db.get_value("unit-test-rollback") is None


def test_warm_database_reads_do_not_write_or_run_schema(isolated, monkeypatch):
    statements = []
    original = sqlite3.connect
    def traced(*args, **kwargs):
        connection = original(*args, **kwargs)
        connection.set_trace_callback(statements.append)
        return connection
    monkeypatch.setattr(db.sqlite3, "connect", traced)
    for _ in range(20):
        assert db.get_document("checks", "missing") is None
    assert not any(sql.lstrip().startswith(("CREATE", "INSERT", "UPDATE")) for sql in statements)


def test_app_factories_keep_database_paths_isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", None)
    first = TestClient(create_app(tmp_path / "first.db"))
    second = TestClient(create_app(tmp_path / "second.db"))
    check = first.post("/api/checks", json={"batch": "SYNTHETIC123"}, headers={"Accept": "application/json"}).json()
    assert len(first.get("/api/checks").json()["items"]) == 1
    assert second.get("/api/checks").json()["items"] == []
    assert second.get(f"/api/checks/{check['thread_id']}").status_code == 404


def test_legacy_source_migration_preserves_ids_hashes_and_foreign_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", None)
    path = tmp_path / "legacy.db"
    legacy_schema = db.SCHEMA.replace("sha256 TEXT, title", "sha256 TEXT UNIQUE, title")
    with sqlite3.connect(path) as old:
        old.executescript(legacy_schema)
        old.execute("INSERT INTO sources(id,source_type,list_kind,list_month,sha256) VALUES(17,'portal_json','nsq','2026-08','same-bytes')")
        old.execute("INSERT INTO alerts(id,source_id,batch_key) VALUES(29,17,'SYNTHETIC')")
    db.init_db(path)
    with db.connect() as con:
        assert con.execute("SELECT source_id FROM alerts WHERE id=29").fetchone()[0] == 17
        assert con.execute("SELECT sha256 FROM sources WHERE id=17").fetchone()[0] == "same-bytes"
        con.execute("INSERT INTO sources(source_type,list_kind,list_month,sha256) VALUES('portal_json','nsq','2026-09','same-bytes')")
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []
        assert con.execute("SELECT value FROM kv WHERE key='schema_version'").fetchone()[0] == "3"


def test_indexed_batch_lookup_matches_exact_and_confusable_rows(isolated, monkeypatch):
    with db.connect() as con:
        con.executemany("INSERT INTO alerts(batch_key,batch_raw,product,entry_type,list_month,list_level) VALUES(?,?,?,?,?,?)", [
            ("AB8", "AB8", "Synthetic One", "NSQ", "2026-09", "central"),
            ("ABB", "ABB", "Synthetic Two", "NSQ", "2026-09", "state"),
            ("ZZZ", "ZZZ", "Synthetic Other", "NSQ", "2026-09", "central")])
    monkeypatch.setattr(db, "all_alerts", lambda: pytest.fail("Batch lookup must not read the full alert index"))
    client = TestClient(isolated)
    matches = client.get("/api/alerts?batch=AB8").json()["items"]
    assert [(r["batch_key"], r["match_type"]) for r in matches] == [("AB8", "exact"), ("ABB", "variant")]
    assert client.get("/api/alerts?batch=AB8&level=state").json()["total"] == 1
    assert client.get("/api/alerts?level=central").json()["total"] == 2


def test_image_decode_does_not_block_other_requests(isolated, monkeypatch):
    entered, release = threading.Event(), threading.Event()
    original = app_module._decode_upload
    def slow_decode(content, folder):
        entered.set()
        assert release.wait(3)
        return original(content, folder)
    monkeypatch.setattr(app_module, "_decode_upload", slow_decode)
    from core import pack_tools
    monkeypatch.setattr(pack_tools, "read_pack", lambda path: {"fields": {"batch": "SYNTHETIC", "source": "ocr"}, "warnings": []})
    picture = io.BytesIO()
    Image.new("RGB", (16, 16), "white").save(picture, "PNG")
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=isolated), base_url="http://testserver") as client:
            upload = asyncio.create_task(client.post("/api/checks", files={"image": ("test.png", picture.getvalue())}, headers={"Accept": "application/json"}))
            try:
                assert await asyncio.to_thread(entered.wait, 1)
                health = await asyncio.wait_for(client.get("/api/health"), timeout=.5)
                assert health.status_code == 200
            finally:
                release.set()
            assert (await upload).status_code == 200
    asyncio.run(run())


def test_chunked_oversized_multipart_is_stopped_before_full_spooling(isolated, monkeypatch):
    import starlette.formparsers as multipart
    files = []
    factory = multipart.SpooledTemporaryFile
    def track(*args, **kwargs):
        file = factory(*args, **kwargs)
        files.append(file)
        return file
    monkeypatch.setattr(multipart, "SpooledTemporaryFile", track)
    # A small test limit proves streaming enforcement without allocating 30 MB.
    monkeypatch.setattr(app_module, "MAX_IMAGE_BYTES", 1024)
    sent = 0
    async def run():
        nonlocal sent
        pieces = [b'--boundary\r\nContent-Disposition: form-data; name="image"; filename="x.png"\r\n\r\n'] + [b"x" * 8192] * 20
        async def receive():
            nonlocal sent
            sent += 1
            body = pieces.pop(0)
            return {"type": "http.request", "body": body, "more_body": bool(pieces)}
        request = Request({"type": "http", "method": "POST", "path": "/api/checks", "headers": [(b"content-type", b"multipart/form-data; boundary=boundary")], "app": isolated}, receive)
        with pytest.raises(app_module.HTTPException) as error:
            await app_module._read_images(request)
        assert error.value.status_code == 413
    asyncio.run(run())
    assert sent < 21
    assert files and all(file.closed for file in files)


def test_malformed_origin_token_and_method_return_structured_errors(isolated, monkeypatch):
    client = TestClient(isolated)
    assert client.post("/api/checks", json={"batch": "SYNTHETIC"}, headers={"Origin": "http://[broken"}).status_code == 403
    error = client.put("/api/health")
    assert error.status_code == 405 and error.json()["error"]["status"] == 405
    assert "allow" in error.headers
    monkeypatch.setenv("STRIPCHECK_LAN_TOKEN", "unit-test-token")
    isolated.state.lan = True
    assert client.get("/api/health?k=%E2%9C%93").status_code == 401


def test_failed_check_is_persisted_and_releases_running_lock(isolated, monkeypatch):
    from core import investigator
    monkeypatch.setattr(investigator, "investigate", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("Synthetic worker failure")))
    client = TestClient(isolated)
    response = client.post("/api/checks", json={"batch": "SYNTHETIC"}, headers={"Accept": "application/json"})
    assert response.status_code == 500
    assert client.get("/api/checks").json()["items"][0]["status"] == "error"
    assert isolated.state.busy_checks == set()


def test_sse_disconnect_keeps_worker_running_and_backlog_is_bounded():
    async def run():
        release, completed = threading.Event(), threading.Event()
        def work(emit):
            emit("step", {"summary": "Started"})
            assert release.wait(2)
            for index in range(2000):
                emit("step", {"step": index})
            completed.set()
            emit("done", {"status": "done"})
        response = stream_work("synthetic-disconnect", work)
        await anext(response.body_iterator)
        await response.body_iterator.aclose()
        release.set()
        assert await asyncio.to_thread(completed.wait, 2)
        def flood(emit):
            for index in range(2000):
                emit("step", {"step": index})
            emit("final", {"value": "complete"})
            emit("done", {"status": "done"})
        slow = stream_work("synthetic-backlog", flood)
        await asyncio.sleep(.1)
        frames = [item async for item in slow.body_iterator]
        assert len(frames) <= 256
        assert "event: done" in frames[-1]
        assert any("event: final" in frame for frame in frames)
    asyncio.run(run())


def test_indexed_check_has_coverage_and_requeries_a_changed_batch(isolated, monkeypatch):
    from core.props import demo_cases
    case = demo_cases()[0]
    row = case["alerts"][0]
    with db.connect() as con:
        con.execute("INSERT INTO sources(id,source_type,list_kind,list_month,sha256,url,title) VALUES(1,'portal_json','nsq','2026-09','fixture-hash','https://example.invalid/unit-test-source','Unit-test fixture')")
        con.execute("INSERT INTO alerts(id,source_id,batch_key,batch_raw,product,maker_name,mfg,exp,list_month,entry_type) VALUES(1,1,?,?,?,?,?,?,?,?)", (row["batch_key"],row["batch_raw"],row["product"],row["maker_name"],row["mfg"],row["exp"],row["list_month"],row["entry_type"]))
    monkeypatch.setattr(db, "all_alerts", lambda: pytest.fail("Checks must query bounded indexed candidates"))
    client = TestClient(isolated)
    headers = {"Accept": "application/json"}
    missing = client.post("/api/checks", json={"batch": "ZZ99999", "product": "Unlisted synthetic pack"}, headers=headers).json()
    assert missing["final"]["label"] == "NOT_LISTED"
    assert missing["final"]["latest_month"] == "2026-09"
    from core import pack_tools
    monkeypatch.setattr(pack_tools, "read_pack", lambda path: {"fields": dict(case["fields"], batch=""), "warnings": []})
    photo = io.BytesIO()
    Image.new("RGB", (16, 16), "white").save(photo, "PNG")
    unreadable = client.post("/api/checks", files={"image": ("test.png", photo.getvalue())}, headers=headers).json()
    assert unreadable["pending"]["kind"] == "type_batch"
    corrected = client.post(f"/api/checks/{unreadable['thread_id']}/resume", json={"typed": "LM2408B"}, headers=headers).json()
    assert corrected["final"]["label"] == "FLAGGED"


def test_concurrent_cabinet_save_does_not_duplicate_pack(isolated, monkeypatch):
    client = TestClient(isolated)
    snapshot = client.post("/api/demo/checks", json={"case_id": "02"}, headers={"Accept": "application/json"}).json()
    barrier = threading.Barrier(2)
    original = db.cabinet_for_check
    def simultaneous_lookup(thread_id):
        found = original(thread_id)
        barrier.wait(timeout=2)
        return found
    monkeypatch.setattr(db, "cabinet_for_check", simultaneous_lookup)
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=isolated), base_url="http://testserver") as session:
            first, second = await asyncio.gather(*[session.post("/api/cabinet", json={"thread_id": snapshot["thread_id"]}) for _ in range(2)])
            assert first.status_code == second.status_code == 200
            assert first.json()["id"] == second.json()["id"]
    asyncio.run(run())
    assert len(client.get("/api/cabinet").json()["items"]) == 1


def test_deleted_pack_cannot_be_recreated_by_stale_background_save(isolated):
    db.save_document("cabinet", "unit-test", {"id": "unit-test"})
    db.save_document("notifications", "unit-notice", {"id": "unit-notice", "cabinet_id": "unit-test"})
    assert db.delete_cabinet_item("unit-test")
    assert db.get_document("notifications", "unit-notice") is None
    assert not db.save_existing_document("cabinet", "unit-test", {"id": "unit-test", "final": {}})
    assert db.get_document("cabinet", "unit-test") is None


def test_delete_during_recheck_leaves_no_resurrected_pack_or_notification(isolated, monkeypatch):
    from core import investigator
    from core.supervisor import recheck_cabinet
    db.save_document("cabinet", "unit-test", {"id": "unit-test", "fields": {"batch": "SYNTHETIC"}, "batch_evidence": "user_typed"})
    def deleted_during_investigation(*args, **kwargs):
        db.delete_cabinet_item("unit-test")
        return {"status": "done", "final": {"label": "FLAGGED", "headline": "Synthetic fixture", "citations": [{"id": 1}]}}
    monkeypatch.setattr(investigator, "investigate", deleted_during_investigation)
    recheck_cabinet()
    assert db.get_document("cabinet", "unit-test") is None
    assert db.list_documents("notifications") == []
    assert not db.insert_child_document("notifications", "unit-notice", {"id": "unit-notice"}, "cabinet", "unit-test")

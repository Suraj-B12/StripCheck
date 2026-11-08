"""The token gate also protects a localhost-bound server exposed through a tunnel (STRIPCHECK_REQUIRE_TOKEN=1)."""
from fastapi.testclient import TestClient

from server.app import create_app


def test_tunnel_gate_requires_token(tmp_path, monkeypatch):
    monkeypatch.setenv("STRIPCHECK_LAN_TOKEN", "demo-token-123")
    monkeypatch.setenv("STRIPCHECK_REQUIRE_TOKEN", "1")
    client = TestClient(create_app(tmp_path / "gate.db"))
    assert client.get("/api/health").status_code == 401
    assert client.get("/api/health", params={"k": "wrong"}).status_code == 401
    assert client.get("/api/health", params={"k": "demo-token-123"}).status_code == 200
    assert client.get("/api/health", headers={"X-StripCheck-Key": "demo-token-123"}).status_code == 200


def test_no_gate_by_default(tmp_path, monkeypatch):
    monkeypatch.setenv("STRIPCHECK_LAN_TOKEN", "demo-token-123")
    monkeypatch.delenv("STRIPCHECK_REQUIRE_TOKEN", raising=False)
    client = TestClient(create_app(tmp_path / "open.db"))
    assert client.get("/api/health").status_code == 200


def test_typed_batch_rejects_non_batch_text(tmp_path, monkeypatch):
    monkeypatch.delenv("STRIPCHECK_REQUIRE_TOKEN", raising=False)
    client = TestClient(create_app(tmp_path / "batch.db"))
    for bad in ["कख<script>", "\U0001F48A", "---", "AB\x00C"]:
        response = client.post("/api/checks", json={"batch": bad})
        assert response.status_code == 422, bad
    assert client.post("/api/checks", json={"batch": "B.No. AB-12/34"}).status_code == 200

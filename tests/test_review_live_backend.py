"""Reviewer tests: backend correctness of live steps (no Ollama needed)."""
import pytest
from fastapi.testclient import TestClient

from core import config, db, llm
from server.app import create_app
from tests.test_live_thinking import sse


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setitem(llm._STATE, "down_until", 0.0)
    monkeypatch.delenv("STRIPCHECK_TRACING", raising=False)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "checks.db")
    monkeypatch.setattr(db, "DB_PATH", None)
    with TestClient(create_app(tmp_path / "checks.db")) as test_client:
        yield test_client


def test_persisted_trace_keeps_the_verifier_result_of_draft_verdict(client):
    """The live draft_verdict step is emitted before the verifier runs, and is the only one traced now."""
    stream = sse(client.post("/api/demo/checks", json={"case_id": "03", "planner": "rules"}))
    thread_id = next(data for name, data in stream if name == "snapshot")["snapshot"]["thread_id"]
    resumed = sse(client.post(f"/api/checks/{thread_id}/resume", json={"choice": "printed"}))
    final = next(data for name, data in resumed if name == "snapshot")["snapshot"]
    stored = [s for s in final["history"] if s["action"] == "draft_verdict"]
    assert stored and stored[-1].get("verifier")
    trace = client.get(f"/api/traces/{thread_id}").json()["items"]
    traced = [row for row in trace if row.get("event") == "step" and row.get("action") == "draft_verdict"]
    assert traced and traced[-1].get("verifier") == stored[-1]["verifier"]

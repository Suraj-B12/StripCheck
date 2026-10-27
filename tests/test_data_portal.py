"""Offline transport tests; no government endpoint is called by the test suite."""
import json
from core import config, db, portal

def test_portal_requests_are_paced_and_tls_verified(monkeypatch):
    clock = [10.0]
    calls = []
    class Response:
        def __enter__(self): return self
        def __exit__(self, *_): return None
        def read(self, _): return b'["2026"]'
    def urlopen(request, timeout):
        calls.append((clock[0], request.full_url, timeout))
        return Response()
    monkeypatch.setattr(portal.sys, "platform", "linux")
    monkeypatch.setattr(portal.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(portal.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds))
    monkeypatch.setattr(portal.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(portal, "_last_request", 0)
    portal._request("reportingYears", tab="nsq")
    portal._request("reportingYears", tab="spurious")
    assert calls[1][0] - calls[0][0] >= 1.5
    assert all(url.startswith("https://cdscoonline.gov.in/") for _, url, _ in calls)
    assert all(timeout <= 60 for _, _, timeout in calls)

def test_fast_sync_fetches_latest_three_published_months(monkeypatch):
    def request(endpoint, **params):
        value = ["2025", "2026"] if endpoint == "reportingYears" else ["Jan", "Mar", "Sep", "Aug"]
        return b"", value, "https://example.invalid"
    monkeypatch.setattr(portal, "_request", request)
    assert portal.discover_months("nsq") == [("2026-09", "SEP-2026"), ("2026-08", "AUG-2026"), ("2026-03", "MAR-2026")]

def test_unavailable_portal_retains_offline_data(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(db, "DB_PATH", None)
    db.init_db()
    def unavailable(*_, **__):
        raise RuntimeError("Synthetic network failure")
    monkeypatch.setattr(portal, "discover_months", unavailable)
    events = []
    result = portal.sync(events.append)
    assert result["status"] == "error"
    assert len(result["errors"]) == 2
    assert events[-1]["type"] == "complete"
    assert db.stats()["total"] == 0

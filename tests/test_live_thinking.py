"""Live planner thinking, live steps and the richer question payload (no Ollama needed)."""
import io
import json
import time

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from core import config, db, llm
from core.investigator import investigate
from core.props import demo_cases
from core.templates import BANNED
from server.app import _batch_crop, create_app

CASE = next(case for case in demo_cases() if case["id"] == "03")
DEMO = {"demo": True, "real_alert_count": 0}


@pytest.fixture(autouse=True)
def fresh_llm_state(monkeypatch):
    monkeypatch.setitem(llm._STATE, "down_until", 0.0)
    monkeypatch.delenv("STRIPCHECK_TRACING", raising=False)


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "checks.db")
    monkeypatch.setattr(db, "DB_PATH", None)
    with TestClient(create_app(tmp_path / "checks.db")) as test_client:
        yield test_client


def collector():
    seen = []
    return seen, lambda event, data: seen.append((event, data))


def thinking(seen, phase=None):
    return [data for event, data in seen if event == "thinking" and (phase is None or data["phase"] == phase)]


class FakeStream:
    """Ollama /api/chat NDJSON stream of the given content, in small chunks."""

    def __init__(self, content, size=4):
        chunks = [content[i:i + size] for i in range(0, len(content), size)]
        rows = [{"message": {"content": part}, "done": False} for part in chunks] + [{"message": {"content": ""}, "done": True}]
        self.lines = [json.dumps(row).encode("utf-8") + b"\n" for row in rows]

    def readline(self, limit=-1):
        return self.lines.pop(0) if self.lines else b""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def streaming_ollama(monkeypatch, thought_for):
    """Patch urlopen with a streaming fake; thought_for(allowed) gives the thought text."""
    requests = []

    def fake(request, timeout=None):
        body = json.loads(request.data)
        requests.append(body)
        allowed = body["format"]["properties"]["action"]["enum"]
        content = json.dumps({"thought": thought_for(allowed), "action": allowed[0]})
        return FakeStream(content)
    monkeypatch.setattr(llm, "urlopen", fake)
    return requests


def test_rules_mode_streams_steps_live_in_order_and_thinking_start_end():
    seen, observe = collector()
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="rules"), observer=observe)
    steps = [data for event, data in seen if event == "step"]
    assert [s["step"] for s in steps] == [s["step"] for s in snapshot["history"]]
    assert [s["action"] for s in steps] == [s["action"] for s in snapshot["history"]]
    blocks = thinking(seen)
    assert [(b["id"], b["phase"]) for b in blocks] == [("think-1", "start"), ("think-1", "end"), ("think-2", "start"), ("think-2", "end")]
    assert all(b["source"] == "rules" and b["context"] for b in blocks)
    assert blocks[1]["action"] == "search_variants" and "misread" in blocks[1]["text"] and blocks[1]["redacted"] is False
    assert blocks[0]["text"] == "" and isinstance(blocks[1]["ms"], int)
    # The thinking end arrives before the step that carries its decision.
    order = [(event, data.get("action") if event == "step" else data["phase"]) for event, data in seen]
    assert order.index(("thinking", "end")) < order.index(("step", "search_variants"))
    # The observer is never stored and the counter persists for resume.
    engine = snapshot["context"]["_engine"]
    assert "_observer" not in engine and engine["thinking_count"] == 2
    json.dumps(snapshot["context"])


def test_thinking_ids_continue_across_resume():
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="rules"))
    seen, observe = collector()
    resumed = investigate(snapshot["fields"], CASE["alerts"], context=snapshot["context"], answer={"choice": "printed"}, observer=observe)
    steps = [data for event, data in seen if event == "step"]
    assert steps[0]["action"] == "answer" and steps[0]["step"] == len(snapshot["history"]) + 1
    assert [s["step"] for s in steps] == [s["step"] for s in resumed["history"][len(snapshot["history"]):]]
    ids = {b["id"] for b in thinking(seen)}
    assert ids and all(int(i.split("-")[1]) > 2 for i in ids)


def test_observer_errors_never_break_a_check():
    def broken(event, data):
        raise RuntimeError("display failed")
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="rules"), observer=broken)
    plain = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="rules"))
    assert snapshot["status"] == plain["status"] == "waiting"
    assert snapshot["pending"]["kind"] == plain["pending"]["kind"]


def test_hybrid_streams_growing_deltas_and_ends_with_the_action(monkeypatch):
    monkeypatch.setattr(llm, "THROTTLE", 0)
    requests = streaming_ollama(monkeypatch, lambda allowed: "The 8 may be a scuffed \"B\"; try look-alike batches next." if "search_variants" in allowed else "Only the person holding the pack can confirm the character.")
    seen, observe = collector()
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="hybrid"), observer=observe)
    assert requests and all(body["stream"] is True for body in requests)
    first = [b for b in thinking(seen) if b["id"] == "think-1"]
    assert first[0]["phase"] == "start" and first[0]["source"] == "llm" and first[0]["model"]
    deltas = [b for b in first if b["phase"] == "delta"]
    assert len(deltas) > 1
    texts = [d["text"] for d in deltas]
    assert all(later.startswith(earlier) and len(later) > len(earlier) for earlier, later in zip(texts, texts[1:]))
    assert '"B"' in texts[-1] or texts[-1].startswith("The 8")
    end = first[-1]
    assert end["phase"] == "end" and end["source"] == "llm" and end["action"] == "search_variants"
    assert end["text"] == "The 8 may be a scuffed \"B\"; try look-alike batches next." and end["redacted"] is False
    assert snapshot["pending"]["kind"] == "confirm_char"
    final_ask = [b for b in thinking(seen, "end") if b["id"] == "think-2"][0]
    assert final_ask["action"] == "ask_user" and final_ask["source"] == "llm"


def test_deltas_are_throttled(monkeypatch):
    streaming_ollama(monkeypatch, lambda allowed: "A fairly long planner thought that arrives in many small chunks very quickly.")
    seen, observe = collector()
    investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="hybrid"), observer=observe)
    # All chunks arrive within 80 ms, so at most one delta per block is forwarded.
    for block_id in {b["id"] for b in thinking(seen)}:
        assert len([b for b in thinking(seen, "delta") if b["id"] == block_id]) <= 1


def test_banned_word_in_streamed_thought_is_redacted(monkeypatch):
    monkeypatch.setattr(llm, "THROTTLE", 0)
    streaming_ollama(monkeypatch, lambda allowed: "Looking at the print here, this batch seems safe so I will search look-alikes.")
    seen, observe = collector()
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="hybrid"), observer=observe)
    deltas = thinking(seen, "delta")
    assert deltas and not any(BANNED.search(d["text"]) for d in deltas)
    end = [b for b in thinking(seen, "end") if b["id"] == "think-1"][0]
    assert end["redacted"] is True and "withheld" in end["text"] and not BANNED.search(end["text"])
    assert "withheld" in [s for s in snapshot["history"] if s["action"] == "search_variants"][0]["thought"]


def test_ollama_down_ends_with_rules_fallback_quickly(monkeypatch):
    def refused(*args, **kwargs):
        raise ConnectionRefusedError("unit test: Ollama stopped")
    monkeypatch.setattr(llm, "urlopen", refused)
    seen, observe = collector()
    started = time.perf_counter()
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="hybrid"), observer=observe)
    assert time.perf_counter() - started < 2
    assert snapshot["pending"]["kind"] == "confirm_char"
    ends = thinking(seen, "end")
    assert ends and all(b["source"] == "rules(fallback)" and "model" not in b for b in ends)
    assert thinking(seen, "start")[0]["source"] == "llm" and not thinking(seen, "delta")


def test_streaming_respects_the_size_bound(monkeypatch):
    class Huge(FakeStream):
        def readline(self, limit=-1):
            return json.dumps({"message": {"content": "x" * 600_000}, "done": False}).encode("utf-8") + b"\n"
    monkeypatch.setattr(llm, "urlopen", lambda *args, **kwargs: Huge(""))
    assert llm.structured_call({"q": 1}, {"type": "object"}, model="m", on_text=lambda text: None) is None
    assert "invalid output" in llm._STATE["last_error"]


def test_partial_string_handles_escapes_and_incomplete_json():
    assert llm.partial_string('{"thought": "The \\"8\\" may\\nbe \\u00e9') == 'The "8" may\nbe é'
    assert llm.partial_string('{"thought": "ab\\u00') == "ab"
    assert llm.partial_string('{"thought": "ab\\') == "ab"
    assert llm.partial_string('{"tho') == ""
    assert llm.partial_string('{"action": "x", "thought": "done", "z": 1}') == "done"


def test_pending_has_reason_counter_and_crop_only_when_supplied():
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="rules"))
    pending = snapshot["pending"]
    assert pending["kind"] == "confirm_char" and pending["reason"] and not BANNED.search(pending["reason"])
    assert pending["asks_used"] == 1 and pending["asks_max"] == 2 and "crop" not in pending
    assert {"question", "options", "positions", "listed", "pack"} <= set(pending)
    with_crop = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="rules", batch_crop="/api/crops/abc123.png"))
    assert with_crop["pending"]["crop"] == "/api/crops/abc123.png"
    bad = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="rules", batch_crop="https://example.invalid/x.png"))
    assert "crop" not in bad["pending"]


def test_every_question_kind_has_a_reason():
    from core.templates import QUESTION_REASONS, question
    for kind in ("type_batch", "confirm_batch", "confirm_char", "box_photo"):
        assert question(kind, {"batch": "AB12"}, {"batch_key": "AB12"}, [1])["reason"] == QUESTION_REASONS[kind]
    assert question("confirm_field", {"batch": "AB12"}, {"date_diffs": [("exp", "2027-01", "2027-02")]})["reason"] == QUESTION_REASONS["confirm_field"]
    assert not any(BANNED.search(text) for text in QUESTION_REASONS.values())


def sse(response):
    result = []
    for chunk in response.text.split("\n\n"):
        if chunk.startswith("event: "):
            name, data = chunk.split("\n", 1)
            result.append((name[7:], json.loads(data[6:])))
    return result


def test_planner_is_validated_per_request(client):
    assert client.post("/api/checks", json={"batch": "SYNTHETIC1", "planner": "llm"}).status_code == 422
    assert client.post("/api/checks", json={"batch": "SYNTHETIC1", "planner": 3}).status_code == 422
    assert "planner" in client.post("/api/demo/checks", json={"case_id": "03", "planner": "bogus"}).json()["error"]["message"]
    picture = io.BytesIO()
    Image.new("RGB", (16, 16), "white").save(picture, "PNG")
    response = client.post("/api/checks", files={"image": ("t.png", picture.getvalue(), "image/png")}, data={"planner": "maybe"})
    assert response.status_code == 422
    assert client.post("/api/checks", json={"batch": "SYNTHETIC1", "planner": "rules"}, headers={"Accept": "application/json"}).status_code == 200


def test_sse_check_streams_live_steps_once_and_thinking(client):
    response = client.post("/api/demo/checks", json={"case_id": "03", "planner": "rules"})
    stream = sse(response)
    snapshot = next(data for name, data in stream if name == "snapshot")["snapshot"]
    steps = [data for name, data in stream if name == "step"]
    assert [s["step"] for s in steps] == [s["step"] for s in snapshot["history"]]
    names = [name for name, _ in stream]
    assert names.index("thinking") < names.index("snapshot") and names[-1] == "done"
    blocks = [data for name, data in stream if name == "thinking"]
    assert [(b["id"], b["phase"]) for b in blocks][:2] == [("think-1", "start"), ("think-1", "end")]
    interrupt = next(data for name, data in stream if name == "interrupt")
    assert interrupt["reason"] and interrupt["asks_used"] == 1 and interrupt["asks_max"] == 2
    assert snapshot["pending"]["reason"] == interrupt["reason"]
    thread_id = snapshot["thread_id"]
    stored = client.get(f"/api/checks/{thread_id}").json()
    trace = client.get(f"/api/traces/{thread_id}").json()["items"]
    traced = [row for row in trace if row["event"] == "thinking"]
    assert traced and all(row["phase"] == "end" for row in traced)
    # Resume keeps the planner and streams only the new steps, once.
    resumed = sse(client.post(f"/api/checks/{thread_id}/resume", json={"choice": "printed"}))
    new_steps = [data["step"] for name, data in resumed if name == "step"]
    final = next(data for name, data in resumed if name == "snapshot")["snapshot"]
    assert new_steps == [s["step"] for s in final["history"][len(stored["history"]):]]
    assert len(new_steps) == len(set(new_steps))
    assert all(int(data["id"].split("-")[1]) > 2 for name, data in resumed if name == "thinking")


def test_json_check_payload_and_health_has_llm_fields(client):
    snapshot = client.post("/api/demo/checks", json={"case_id": "03"}, headers={"Accept": "application/json"}).json()
    assert {"reason", "asks_used", "asks_max"} <= set(snapshot["pending"])
    ollama = client.get("/api/health").json()["ollama"]
    assert isinstance(ollama["llm_ok"], bool) and ollama["model"] == config.LLM_MODEL and "up" in ollama


def test_hybrid_request_is_kept_in_context_for_resume(client, monkeypatch):
    calls = []

    def fake(prompt, schema, **kwargs):
        calls.append(kwargs)
        return {"thought": "Try look-alikes first.", "action": prompt["allowed"][0]}
    monkeypatch.setattr(llm, "structured_call", fake)
    stream = sse(client.post("/api/demo/checks", json={"case_id": "03", "planner": "hybrid"}))
    assert calls and all("on_text" in kwargs for kwargs in calls)
    ends = [data for name, data in stream if name == "thinking" and data["phase"] == "end"]
    assert ends and all(b["source"] == "llm" for b in ends)
    thread_id = ends[0]["thread_id"]
    calls.clear()
    client.post(f"/api/checks/{thread_id}/resume", json={"choice": "printed"}, headers={"Accept": "application/json"})
    assert calls


def test_batch_crop_from_reader_box(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    photo = tmp_path / "pack.jpg"
    Image.new("RGB", (200, 120), "white").save(photo)
    reading = {"fields": {"batch_line": 1}, "lines": [{"box": [[0, 0], [50, 0], [50, 10], [0, 10]]}, {"box": [[10, 40], [150, 40], [150, 60], [10, 60]]}]}
    url = _batch_crop(photo, reading)
    assert url.startswith("/api/crops/") and (tmp_path / "crops" / url.split("/")[-1]).is_file()
    assert _batch_crop(photo, {"fields": {"batch_line": None}, "lines": []}) == ""
    assert _batch_crop(photo, {"fields": {"batch_line": 5}, "lines": reading["lines"]}) == ""


def test_photo_check_question_carries_the_batch_crop(client, monkeypatch):
    from core import pack_tools
    alert = dict(CASE["alerts"][0], synthetic=False, flags=[], source_title="Unit-test source fixture", source_url="https://example.invalid/unit-test-source")
    monkeypatch.setattr(db, "batch_alerts", lambda *_args, **_kwargs: [alert])
    monkeypatch.setattr(db, "check_coverage", lambda: {"real_alert_count": 1, "latest_month": "2026-09", "list_count": 1})
    fields = dict(CASE["fields"], batch_line=0)
    monkeypatch.setattr(pack_tools, "read_pack", lambda path: {"fields": fields, "lines": [{"box": [[2, 2], [60, 2], [60, 20], [2, 20]]}], "warnings": []})
    picture = io.BytesIO()
    Image.new("RGB", (64, 64), "white").save(picture, "PNG")
    snapshot = client.post("/api/checks", files={"image": ("t.png", picture.getvalue(), "image/png")}, headers={"Accept": "application/json"}).json()
    crop = snapshot["pending"]["crop"]
    assert crop.startswith("/api/crops/") and client.get(crop).status_code == 200


@pytest.mark.parametrize("thought, fragment", [
    ("Is pack ko abhi बंद करें aur pharmacist ko dikhayen.", "बंद"),
    ("This pack is fine to use, so no more questions.", "fine to"),
])
def test_live_deltas_hold_back_the_start_of_a_withheld_phrase(monkeypatch, thought, fragment):
    monkeypatch.setattr(llm, "THROTTLE", 0)
    streaming_ollama(monkeypatch, lambda allowed: thought)
    seen, observe = collector()
    investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="hybrid"), observer=observe)
    assert not [d["text"] for d in thinking(seen, "delta") if fragment in d["text"]]
    end = [b for b in thinking(seen, "end") if b["id"] == "think-1"][0]
    assert end["redacted"] is True and fragment not in end["text"]

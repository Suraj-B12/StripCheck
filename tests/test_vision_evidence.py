"""Vision fallback, confirm-reading question, request_photo and ReAct labels (mock Ollama, no network)."""
import io
import json

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from core import config, db, llm, verifier
from core.investigator import MAX_ASKS, MAX_STEPS, MAX_VISION_CALLS, investigate
from core.props import demo_cases
from core.templates import BANNED, NO, YES
from server.app import create_app

CASE = next(case for case in demo_cases() if case["id"] == "01")
LISTED = CASE["alerts"][0]["batch_raw"]  # LM2408B


@pytest.fixture(autouse=True)
def vision_on(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "VLM_MODEL", "qwen2.5vl:3b")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setitem(llm._STATE, "down_until", 0.0)
    monkeypatch.delenv("STRIPCHECK_TRACING", raising=False)


@pytest.fixture
def photo(tmp_path):
    path = tmp_path / "pack.png"
    Image.new("RGB", (2000, 900), "white").save(path)
    return str(path)


def fake_vision(batch=LISTED, confidence=0.7):
    calls = []

    def read(image_b64, **kwargs):
        calls.append({"image": image_b64, **kwargs})
        reading = llm.validate_vision({"batch": batch, "mfg": "", "exp": "", "confidence": confidence, "note": "clear"}) if batch is not None else None
        return {"reading": reading, "ms": 5.0, "error": "" if reading else "unreachable: URLError", "raw": None}
    return read, calls


def fields(batch="", source="ocr"):
    return dict(CASE["fields"], batch=batch, source=source, confirmed=False)


def context(photo, planner="rules", **extra):
    return {"demo": True, "real_alert_count": 0, "planner": planner, "vision_image": photo, **extra}


def resume(snapshot, answer, observer=None):
    return investigate(snapshot["fields"], CASE["alerts"], context=snapshot["context"], answer=answer, observer=observer)


def actions(snapshot):
    return [step["action"] for step in snapshot["history"]]


def test_vision_is_not_called_when_ocr_read_the_batch(monkeypatch, photo):
    read, calls = fake_vision()
    monkeypatch.setattr(llm, "vision_read", read)
    snapshot = investigate(fields(LISTED), CASE["alerts"], context=context(photo))
    assert calls == [] and "read_with_vision" not in actions(snapshot)
    assert snapshot["pending"]["kind"] == "confirm_batch"


def test_vision_reads_a_missing_batch_and_asks_to_confirm(monkeypatch, photo):
    read, calls = fake_vision()
    monkeypatch.setattr(llm, "vision_read", read)
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo))
    assert len(calls) == 1 and calls[0]["model"] == "qwen2.5vl:3b" and calls[0]["timeout"] == config.VLM_TIMEOUT
    # The whole photo was downscaled to at most 1280 px before it was sent.
    import base64
    sent = Image.open(io.BytesIO(base64.b64decode(calls[0]["image"])))
    assert max(sent.size) <= 1280
    pending = snapshot["pending"]
    assert pending["kind"] == "confirm_reading" and pending["reading"] == LISTED and pending["style"] == "yes_no"
    assert pending["question"] == "Is this the batch printed on your pack?" and pending["options"] == [YES, NO]
    assert pending["crop"].startswith("/api/crops/")
    step = next(s for s in snapshot["history"] if s["action"] == "read_with_vision")
    assert step["agent"] == "perception" and step["vision"]["status"] == "pending"
    assert snapshot["context"]["_engine"]["batch_evidence"] == "none"


def test_confirm_yes_continues_with_user_confirmed(monkeypatch, photo):
    monkeypatch.setattr(llm, "vision_read", fake_vision()[0])
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo))
    result = resume(snapshot, {"choice": "yes"})
    engine = result["context"]["_engine"]
    assert engine["batch_evidence"] == "user_confirmed" and engine["provenance"]["batch"] == "vlm"
    assert result["final"]["label"] == "FLAGGED" and result["fields"]["batch"] == LISTED
    assert engine["asks"] == 1


def test_confirm_no_asks_to_type_then_continues(monkeypatch, photo):
    monkeypatch.setattr(llm, "vision_read", fake_vision("LM2408D")[0])
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo))
    assert snapshot["pending"]["kind"] == "confirm_reading"
    typed = resume(snapshot, {"choice": NO})
    assert typed["pending"]["kind"] == "type_batch"
    done = resume(typed, {"typed": LISTED})
    assert done["context"]["_engine"]["batch_evidence"] == "user_typed"
    assert done["final"]["label"] == "FLAGGED"
    assert done["context"]["_engine"]["asks"] == MAX_ASKS


def test_vision_down_goes_to_type_batch_directly(monkeypatch, photo):
    read, calls = fake_vision(None)
    monkeypatch.setattr(llm, "vision_read", read)
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo))
    assert len(calls) == 1 and snapshot["pending"]["kind"] == "type_batch"
    assert next(s for s in snapshot["history"] if s["action"] == "read_with_vision")["vision"]["status"] == "failed"


def test_without_a_vision_model_the_old_type_batch_question_is_unchanged(monkeypatch, photo):
    monkeypatch.setattr(config, "VLM_MODEL", "")
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo))
    assert actions(snapshot) == ["extract_fields", "ask_user"] and snapshot["pending"]["kind"] == "type_batch"


def test_real_ollama_down_window_skips_vision(monkeypatch, photo):
    def refuse(*_args, **_kwargs):
        raise OSError("connection refused")
    monkeypatch.setattr(llm, "urlopen", refuse)
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo))
    assert snapshot["pending"]["kind"] == "type_batch"
    assert llm._STATE["down_until"] > 0
    assert llm.vision_read("abc", model="qwen2.5vl:3b")["error"].startswith("skipped")


def test_vision_reading_alone_never_yields_flagged(monkeypatch, photo):
    monkeypatch.setattr(llm, "vision_read", fake_vision()[0])
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo))
    skipped = resume(snapshot, {"skip": True})
    assert skipped["pending"]["kind"] == "type_batch"
    final = resume(skipped, {"skip": True})
    assert final["final"]["label"] == "CANT_VERIFY"
    # The verifier refuses a listed result when the batch evidence is a vision reading.
    top = {"status": "accept", "evidence": {"batch": "exact", "product": "match"}, "batch_key": LISTED, "entry_type": "NSQ", "id": 1}
    state = {"top": top, "batch_evidence": "vlm", "fields": {"batch": LISTED}, "provenance": {"batch": "vlm"}}
    assert any(v.startswith("R2") for v in verifier.check_rules({"label": "FLAGGED", "citations": [], "lang": "en"}, state))


def test_vision_output_validation():
    good = llm.validate_vision({"batch": "B.No.: LM2408B", "mfg": "08/2024", "exp": "07/2027", "confidence": 3, "note": "clear print"})
    assert good == {"batch": "LM2408B", "mfg": "08/2024", "exp": "07/2027", "confidence": 1.0, "note": "clear print"}
    for bad in ("", "AB", "X" * 26, "LM<script>", "batch number not visible ok", "--"):
        assert llm.validate_vision({"batch": bad, "confidence": 0.5}) is None or bad == "batch number not visible ok"
    assert llm.validate_vision({"batch": "LM 2408B", "confidence": "x", "note": "looks safe"}) == {"batch": "LM 2408B", "mfg": "", "exp": "", "confidence": 0.0, "note": ""}
    assert llm.validate_vision("LM2408B") is None
    assert llm.validate_vision({"batch": "ÄÖÜ123"}) is None


def test_vision_request_sends_base64_image_schema_and_temperature_zero(monkeypatch):
    seen = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, _n):
            return json.dumps({"message": {"content": json.dumps({"batch": "LM2408B", "mfg": "", "exp": "", "confidence": 0.9, "note": ""})}}).encode()

    def fake_urlopen(request, timeout):
        seen["body"], seen["timeout"], seen["url"] = json.loads(request.data), timeout, request.full_url
        return Response()
    monkeypatch.setattr(llm, "urlopen", fake_urlopen)
    result = llm.vision_read("aGVsbG8=", model="qwen2.5vl:3b", url="http://localhost:11434", timeout=30)
    body = seen["body"]
    assert result["reading"]["batch"] == "LM2408B"
    assert seen["url"] == "http://127.0.0.1:11434/api/chat" and seen["timeout"] == 30
    assert body["messages"][-1]["images"] == ["aGVsbG8="] and body["options"]["temperature"] == 0
    assert body["format"]["required"] == ["batch", "mfg", "exp", "confidence", "note"] and body["stream"] is False


def test_low_confidence_ocr_read_uses_vision_and_agreement_continues(monkeypatch, photo):
    read, calls = fake_vision(LISTED)
    monkeypatch.setattr(llm, "vision_read", read)
    snapshot = investigate(fields(LISTED), CASE["alerts"], context=context(photo, batch_low_confidence=True))
    assert len(calls) == 1
    # Agreement is not gate evidence: the usual confirmation gate still asks the person.
    assert snapshot["pending"]["kind"] == "confirm_batch"


def test_agent_requests_a_closer_photo_when_readers_disagree(monkeypatch, photo):
    monkeypatch.setattr(llm, "vision_read", fake_vision(LISTED)[0])
    offered = []

    def chat(messages, tools, **kwargs):
        names = [t["function"]["name"] for t in tools]
        offered.append(names)
        name = "request_photo" if "request_photo" in names else names[0]
        spec = next(t for t in tools if t["function"]["name"] == name)["function"]["parameters"]["properties"]
        args = {"thought": "One closer photo settles which reading is right."}
        if "kind" in spec:
            args["kind"] = spec["kind"]["enum"][0]
        return {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": name, "arguments": args}}]}
    monkeypatch.setattr(llm, "tool_chat", chat)
    ocr_misread = "LM24O8B"
    snapshot = investigate(fields(ocr_misread), CASE["alerts"], context=context(photo, planner="agent", batch_low_confidence=True))
    assert ["read_with_vision"] in offered or "read_with_vision" in actions(snapshot)
    pending = snapshot["pending"]
    assert pending["kind"] == "request_photo" and pending["photo_kind"] == "batch_zoom" and pending["style"] == "photo"
    assert "I can't take another photo" in pending["options"]
    # The uploaded close-up is read again (mocked read_pack output) and agrees with the vision reading.
    after = resume(snapshot, {"image": True, "fields": {"batch": LISTED, "product": "Lumera Tablets"}, "source": "carton"})
    engine = after["context"]["_engine"]
    assert engine["photos"] == 1 and engine["provenance"]["batch"] == "ocr" and engine["batch_evidence"] == "ocr"
    assert after["pending"]["kind"] == "confirm_batch"  # vision + OCR agreement is still not gate evidence
    final = resume(after, {"typed": LISTED})
    assert final["final"]["label"] == "FLAGGED"
    assert final["context"]["_engine"]["asks"] <= MAX_ASKS


def test_declining_the_photo_falls_back_to_typing(monkeypatch, photo):
    monkeypatch.setattr(llm, "vision_read", fake_vision(None)[0])
    monkeypatch.setattr(llm, "tool_chat", lambda messages, tools, **kw: {"role": "assistant", "content": "", "tool_calls": [{"function": {
        "name": "request_photo" if any(t["function"]["name"] == "request_photo" for t in tools) else tools[0]["function"]["name"],
        "arguments": {"thought": "A closer photo may help.", "kind": "batch_zoom"}}}]})
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo, planner="agent"))
    assert snapshot["pending"]["kind"] == "request_photo"
    declined = resume(snapshot, {"choice": "I can't take another photo"})
    assert declined["pending"]["kind"] == "type_batch"
    assert "request_photo" in declined["context"]["_engine"]["declined"]


def test_bounds_hold_when_the_agent_keeps_asking_for_evidence(monkeypatch, photo):
    read, calls = fake_vision(None)
    monkeypatch.setattr(llm, "vision_read", read)

    def chat(messages, tools, **kwargs):
        names = [t["function"]["name"] for t in tools]
        name = next((n for n in ("request_photo", "read_with_vision") if n in names), names[0])
        props = next(t for t in tools if t["function"]["name"] == name)["function"]["parameters"]["properties"]
        args = {"thought": "More evidence."}
        if "kind" in props:
            args["kind"] = props["kind"]["enum"][0]
        return {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": name, "arguments": args}}]}
    monkeypatch.setattr(llm, "tool_chat", chat)
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo, planner="agent"))
    for _ in range(6):
        if snapshot["status"] != "waiting":
            break
        kind = snapshot["pending"]["kind"]
        snapshot = resume(snapshot, {"image": True, "fields": {}, "source": "carton"} if kind == "request_photo" else {"skip": True})
    engine = snapshot["context"]["_engine"]
    assert snapshot["status"] == "done" and snapshot["final"]["label"] == "CANT_VERIFY"
    assert engine["asks"] <= MAX_ASKS and len(calls) <= MAX_VISION_CALLS and engine.get("photos", 0) <= 1
    assert len(snapshot["history"]) <= MAX_STEPS


def test_hybrid_mode_offers_vision_and_typing_without_a_model(monkeypatch, photo):
    monkeypatch.setattr(llm, "vision_read", fake_vision()[0])
    monkeypatch.setattr(config, "LLM_MODEL", "")
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo, planner="hybrid"))
    assert "read_with_vision" in actions(snapshot) and snapshot["pending"]["kind"] == "confirm_reading"


def test_react_fields_on_steps_and_thinking(monkeypatch, photo):
    monkeypatch.setattr(llm, "vision_read", fake_vision()[0])

    def chat(messages, tools, **kwargs):
        function = tools[0]["function"]
        args = {"thought": "Gathering the next piece of evidence."}
        if "kind" in function["parameters"]["properties"]:
            args["kind"] = function["parameters"]["properties"]["kind"]["enum"][0]
        return {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": function["name"], "arguments": args}}]}
    monkeypatch.setattr(llm, "tool_chat", chat)
    events = []
    snapshot = investigate(fields(""), CASE["alerts"], context=context(photo, planner="agent"), observer=lambda e, d: events.append((e, d)))
    snapshot = resume(snapshot, {"choice": "yes"}, observer=lambda e, d: events.append((e, d)))
    with_thought = [s for s in snapshot["history"] if s.get("thought")]
    assert with_thought and all(set(s["react"]) == {"thought", "action", "observation"} for s in with_thought)
    vision_step = next(s for s in snapshot["history"] if s["action"] == "read_with_vision")
    assert vision_step["react"]["action"]["tool"] == "read_with_vision" and LISTED in vision_step["react"]["observation"]
    ends = [d for e, d in events if e == "thinking" and d["phase"] == "end"]
    assert ends and all("react" in d and d["react"]["action"]["tool"] == d["action"] for d in ends)
    linked = {s.get("think_id") for s in snapshot["history"]} - {None}
    assert linked and linked <= {d["id"] for d in ends}
    for step in snapshot["history"]:
        assert not BANNED.search(json.dumps(step.get("react", {})))


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "checks.db")
    monkeypatch.setattr(db, "DB_PATH", None)
    with TestClient(create_app(tmp_path / "checks.db")) as test_client:
        yield test_client


def test_api_vision_confirm_and_request_photo_upload(client, monkeypatch):
    from core import pack_tools
    alert = dict(CASE["alerts"][0], synthetic=False, flags=[], source_title="Unit-test source fixture", source_url="https://example.invalid/unit-test-source")
    asked = []
    monkeypatch.setattr(db, "batch_alerts", lambda key, **_kw: asked.append(key) or ([alert] if key == "LM2408B" else []))
    monkeypatch.setattr(db, "check_coverage", lambda: {"real_alert_count": 1, "latest_month": "2026-09", "list_count": 1})
    monkeypatch.setattr(pack_tools, "read_pack", lambda path: {"fields": dict(CASE["fields"], batch="", source="none"), "warnings": [], "lines": []})
    monkeypatch.setattr(llm, "vision_read", fake_vision()[0])
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), "white").save(buffer, "PNG")
    headers = {"Accept": "application/json"}
    first = client.post("/api/checks", files={"image": ("p.png", buffer.getvalue(), "image/png")}, headers=headers).json()
    assert first["pending"]["kind"] == "confirm_reading"
    # The vision reading's alert rows are loaded on resume, so a yes can be checked against them.
    done = client.post(f"/api/checks/{first['thread_id']}/resume", json={"choice": "yes"}, headers=headers).json()
    assert "LM2408B" in asked and done["final"]["label"] == "FLAGGED"
    # request_photo answered by a multipart upload through the same resume endpoint.
    monkeypatch.setattr(llm, "vision_read", fake_vision(None)[0])
    monkeypatch.setattr(llm, "tool_chat", lambda messages, tools, **kw: {"role": "assistant", "content": "", "tool_calls": [{"function": {
        "name": "request_photo" if any(t["function"]["name"] == "request_photo" for t in tools) else tools[0]["function"]["name"],
        "arguments": {"thought": "A closer photo may help.", "kind": "batch_zoom"}}}]})
    second = client.post("/api/checks", files={"image": ("p.png", buffer.getvalue(), "image/png")}, data={"planner": "agent"}, headers=headers).json()
    assert second["pending"]["kind"] == "request_photo"
    monkeypatch.setattr(pack_tools, "read_pack", lambda path: {"fields": dict(CASE["fields"], batch="LM2408B", source="ocr"), "warnings": [], "lines": []})
    after = client.post(f"/api/checks/{second['thread_id']}/resume", files={"image": ("zoom.png", buffer.getvalue(), "image/png")}, headers=headers).json()
    assert after["fields"]["batch"] == "LM2408B" and after["pending"]["kind"] == "confirm_batch"
    health = client.get("/api/health").json()
    assert "vlm_ok" in json.dumps(health)

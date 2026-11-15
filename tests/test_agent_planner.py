"""Planner "agent": tool-calling loop, guard, bounds, self-correction and hand-offs (mock Ollama, no network)."""
import time

import pytest

from core import llm, verifier
from core.investigator import MAX_ASKS, MAX_STEPS, investigate
from core.props import demo_cases
from core.templates import BANNED

CASE = next(case for case in demo_cases() if case["id"] == "03")
DEMO = {"demo": True, "real_alert_count": 0, "planner": "agent"}


@pytest.fixture(autouse=True)
def fresh_llm_state(monkeypatch):
    monkeypatch.setitem(llm._STATE, "down_until", 0.0)
    monkeypatch.delenv("STRIPCHECK_TRACING", raising=False)


def run(context, answers=None, fields=None, observer=None):
    snapshot = investigate(fields or CASE["fields"], CASE["alerts"], context=context, observer=observer)
    for answer in (answers if answers is not None else CASE["answers"]):
        if snapshot["status"] != "waiting":
            break
        snapshot = investigate(snapshot["fields"], CASE["alerts"], context=snapshot["context"], answer=answer, observer=observer)
    return snapshot


def fake_chat(pick=None, thought="Checking the next piece of evidence."):
    """tool_chat stand-in: records the offered tools and calls pick(names) (default: the first)."""
    offered = []

    def chat(messages, tools, **kwargs):
        names = [tool["function"]["name"] for tool in tools]
        offered.append({"names": names, "tools": tools, "messages": messages, "kwargs": kwargs})
        choice = pick(names, tools) if pick else names[0]
        if choice is None:
            return {"role": "assistant", "content": "I am not sure."}
        name, args = choice if isinstance(choice, tuple) else (choice, None)
        if args is None:
            args = {"thought": thought}
            for tool in tools:
                if tool["function"]["name"] == name:
                    for key, spec in tool["function"]["parameters"]["properties"].items():
                        if "enum" in spec:
                            args[key] = spec["enum"][0]
        return {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": name, "arguments": args}}]}
    return chat, offered


def actions(snapshot):
    return [step["action"] for step in snapshot["history"]]


def test_tool_loop_chooses_every_tool_with_only_allowed_tools(monkeypatch):
    chat, offered = fake_chat()
    monkeypatch.setattr(llm, "tool_chat", chat)
    snapshot = run(DEMO)
    assert snapshot["final"]["label"] == "FLAGGED"
    sets = [call["names"] for call in offered]
    # Required searches are offered alone; the optional question offers a draft too.
    assert sets[:4] == [["search_exact"], ["search_variants"], ["grade"], ["ask_user", "draft_verdict"]]
    ask_tool = offered[3]["tools"][0]["function"]
    assert ask_tool["parameters"]["properties"]["kind"]["enum"] == ["confirm_char"]
    assert all("thought" in call["tools"][0]["function"]["parameters"]["required"] for call in offered)
    chosen = [s for s in snapshot["history"] if s["action"] in {"search_exact", "search_variants", "grade", "ask_user"}]
    assert chosen and all(s["source"] == "llm" for s in chosen)
    # ReAct: the observation of each tool is fed back on the next turn.
    second = offered[1]["messages"]
    assert second[-1]["role"] == "tool" and second[-1]["tool_name"] == "search_exact" and "exact_hits" in second[-1]["content"]
    assert len(snapshot["history"]) <= MAX_STEPS


def test_bad_calls_fall_back_to_the_rule_choice(monkeypatch):
    def pick(names, tools):
        if names == ["search_exact"]:
            return ("send_email", {"thought": "Email someone."})  # not offered
        if names == ["search_variants"]:
            return ("search_variants", "not-a-dict")  # malformed arguments
        if "ask_user" in names:
            return ("ask_user", {"thought": "Ask.", "kind": "type_batch"})  # kind outside the enum
        return names[0]
    chat, _ = fake_chat(pick)
    monkeypatch.setattr(llm, "tool_chat", chat)
    snapshot = run(DEMO)
    steps = {s["action"]: s for s in snapshot["history"] if s["action"] != "answer"}
    assert steps["search_exact"]["source"] == "rules(fallback)"
    assert steps["search_variants"]["source"] == "rules(fallback)"
    assert [s for s in snapshot["history"] if s["action"] == "ask_user"][0]["source"] == "rules(fallback)"
    assert snapshot["final"]["label"] == "FLAGGED"


def test_no_tool_calls_uses_the_json_schema_fallback(monkeypatch):
    chat, _ = fake_chat(lambda names, tools: None)
    monkeypatch.setattr(llm, "tool_chat", chat)
    schemas = []

    def structured(prompt, schema, **kwargs):
        schemas.append(schema)
        return {"thought": "Use the first allowed tool.", "tool": schema["properties"]["tool"]["enum"][0], "args": {}}
    monkeypatch.setattr(llm, "structured_call", structured)
    # ask_user omits its single-choice kind: the guard fills the only allowed value.
    snapshot = run(DEMO)
    assert schemas and schemas[0]["required"] == ["thought", "tool", "args"]
    exact = [s for s in snapshot["history"] if s["action"] == "search_exact"][0]
    assert exact["source"] == "llm" and exact["thought"] == "Use the first allowed tool."
    assert [s for s in snapshot["history"] if s["action"] == "ask_user"][0]["source"] == "llm"
    assert snapshot["final"]["label"] == "FLAGGED"


def test_model_cannot_skip_the_confirmation_gate(monkeypatch):
    # An OCR-read batch with an exact, corroborated entry: only ask_user(confirm_batch) is offered.
    fields = dict(CASE["fields"], batch=CASE["alerts"][0]["batch_raw"] if "batch_raw" in CASE["alerts"][0] else CASE["alerts"][0]["batch"], source="ocr")
    chat, offered = fake_chat(lambda names, tools: "draft_verdict" if "draft_verdict" in names else names[0])
    monkeypatch.setattr(llm, "tool_chat", chat)
    snapshot = investigate(fields, CASE["alerts"], context=dict(DEMO))
    if snapshot["status"] == "waiting" and snapshot["pending"]["kind"] == "confirm_batch":
        assert offered[-1]["names"] == ["ask_user"]
    assert snapshot["status"] == "waiting" or snapshot["final"]["label"] in {"CANT_VERIFY", "NOT_LISTED"}
    assert snapshot["final"] is None or snapshot["final"]["label"] not in {"FLAGGED", "SUSPECTED_FAKE"}


def test_bounds_hold_with_a_model_that_always_asks(monkeypatch):
    chat, offered = fake_chat(lambda names, tools: "ask_user" if "ask_user" in names else names[0])
    monkeypatch.setattr(llm, "tool_chat", chat)
    snapshot = run(DEMO, answers=[{"skip": True}] * 5)
    assert snapshot["status"] == "done"
    assert len(snapshot["history"]) <= MAX_STEPS
    assert snapshot["context"]["_engine"]["asks"] <= MAX_ASKS
    assert len(offered) <= 3 * MAX_STEPS


def test_self_correction_revises_once_then_stops(monkeypatch):
    original = verifier.check_rules
    seen = []

    def strict(verdict, state):
        found = original(verdict, state)
        if verdict.get("label") == "FLAGGED":
            found = found + ["R8: every used field needs grounded provenance"]
        seen.append(verdict.get("label"))
        return found
    monkeypatch.setattr(verifier, "check_rules", strict)
    answers = CASE["answers"] + [{"fields": {"product": CASE["fields"].get("product") or "Product"}, "source": "user"}]
    snapshot = run(dict(DEMO, planner="rules"), answers=answers)
    reflects = [s for s in snapshot["history"] if s["action"] == "reflect"]
    assert reflects[0]["decision"] == "ask_user" and reflects[0]["violations"] and reflects[0]["agent"] == "investigator"
    assert [r["decision"] for r in reflects[1:]] in ([], ["downgrade"])
    assert snapshot["status"] == "done" and snapshot["final"]["label"] == "CANT_VERIFY"
    assert snapshot["context"]["_engine"]["revisions"] == 1
    assert len(snapshot["history"]) <= MAX_STEPS


def test_a_used_revision_leaves_only_the_downgrade():
    from core.investigator import _revision_options
    state = {"revisions": 1, "batch_evidence": "ocr", "declined": []}
    assert _revision_options(state, ["R2: x"], "FLAGGED", {"id": 1}, True) == [("downgrade", None)]
    state["revisions"] = 0
    assert _revision_options(state, ["R2: x"], "FLAGGED", {"id": 1}, True)[0] == ("ask_user", "confirm_batch")
    assert _revision_options(state, ["R2: x"], "FLAGGED", {"id": 1}, False) == [("downgrade", None)]
    assert _revision_options(state, ["R3: x"], "FLAGGED", {"id": 1}, True) == [("downgrade", None)]


def test_unfixable_violation_downgrades_without_a_revision(monkeypatch):
    monkeypatch.setattr(verifier, "check_rules", lambda verdict, state: ["R3: alert type does not support this result"] if verdict.get("label") != "CANT_VERIFY" else [])
    snapshot = run(dict(DEMO, planner="rules"))
    reflect = [s for s in snapshot["history"] if s["action"] == "reflect"]
    assert len(reflect) == 1 and reflect[0]["decision"] == "downgrade" and reflect[0]["source"] == "rules"
    assert snapshot["final"]["label"] == "CANT_VERIFY"


def test_handoffs_and_agent_fields(monkeypatch):
    chat, _ = fake_chat()
    monkeypatch.setattr(llm, "tool_chat", chat)
    seen = []
    snapshot = run(DEMO, observer=lambda event, data: seen.append((event, data)))
    history = snapshot["history"]
    assert all(step.get("agent") in {"perception", "investigator", "verifier", "supervisor"} for step in history)
    assert history[0]["action"] == "extract_fields" and history[0]["agent"] == "perception"
    handoffs = [(s["from"], s["to"]) for s in history if s["action"] == "handoff"]
    assert ("perception", "investigator") in handoffs and ("investigator", "verifier") in handoffs
    thinking = [data for event, data in seen if event == "thinking"]
    assert thinking and all(data.get("agent") == "investigator" for data in thinking)
    assert all(not BANNED.search(data.get("text", "")) for data in thinking)
    messages = snapshot["context"]["_engine"]["messages"]
    assert messages[0]["from"] == "perception" and {"from", "to", "kind", "reason", "payload"} <= set(messages[0])


def test_rules_mode_keeps_step_counts_but_records_messages():
    snapshot = run(dict(DEMO, planner="rules"))
    assert len(snapshot["history"]) == 10 and "handoff" not in actions(snapshot)
    assert all("agent" in step for step in snapshot["history"])
    assert [m["to"] for m in snapshot["context"]["_engine"]["messages"]][:2] == ["investigator", "verifier"]


def test_banned_thought_is_withheld_in_agent_mode(monkeypatch):
    chat, _ = fake_chat(thought="This medicine is safe and genuine.")
    monkeypatch.setattr(llm, "tool_chat", chat)
    seen = []
    snapshot = run(DEMO, observer=lambda event, data: seen.append((event, data)))
    exact = [s for s in snapshot["history"] if s["action"] == "search_exact"][0]
    assert "withheld" in exact["thought"] and "safe" not in exact["thought"].lower()
    assert all("safe" not in data.get("text", "").lower() for event, data in seen if event == "thinking")


def test_ollama_down_completes_with_rules_fallback(monkeypatch):
    attempts = []

    def refused(*args, **kwargs):
        attempts.append(1)
        raise ConnectionRefusedError("unit test: Ollama stopped")
    monkeypatch.setattr(llm, "urlopen", refused)
    started = time.perf_counter()
    snapshot = run(DEMO)
    assert time.perf_counter() - started < 2
    assert snapshot["final"]["label"] == "FLAGGED"
    planned = [s for s in snapshot["history"] if s["action"] in {"search_exact", "search_variants", "grade", "ask_user"}]
    assert planned and all(s["source"] == "rules(fallback)" for s in planned)
    assert len(attempts) == 1


def test_server_and_evaluation_accept_the_agent_planner():
    from core.evaluate import ARM_PLANNERS, ARMS
    from server.app import _planner
    assert _planner("agent") == "agent" and _planner("rules") == "rules"
    assert "agent_llm" in ARMS and ARM_PLANNERS["agent_llm"] == "agent"

"""Hybrid planner, fallback, feedback-loop prior and optional OTel export (no Ollama or Phoenix needed)."""
import time

import pytest

from core import llm, tracing
from core.investigator import investigate
from core.props import demo_cases

CASE = next(case for case in demo_cases() if case["id"] == "03")
DEMO = {"demo": True, "real_alert_count": 0}


def real_context(**extra):
    # In-memory synthetic record shaped like a loaded source row; it never enters a database.
    return {"real_alert_count": 1, "latest_month": "2026-09", "list_count": 1, **extra}


def real_alerts():
    return [dict(CASE["alerts"][0], synthetic=False, flags=[], source_title="Unit-test source fixture", source_url="https://example.invalid/unit-test-source")]


@pytest.fixture(autouse=True)
def fresh_llm_state(monkeypatch):
    monkeypatch.setitem(llm._STATE, "down_until", 0.0)
    monkeypatch.delenv("STRIPCHECK_TRACING", raising=False)


def run(context, alerts=None, answers=None):
    alerts = alerts or CASE["alerts"]
    snapshot = investigate(CASE["fields"], alerts, context=context)
    for answer in (answers if answers is not None else CASE["answers"]):
        if snapshot["status"] != "waiting":
            break
        snapshot = investigate(snapshot["fields"], alerts, context=snapshot["context"], answer=answer)
    return snapshot


def by_action(snapshot, action):
    return [step for step in snapshot["history"] if step["action"] == action]


def fake_llm(responses):
    calls = []

    def call(prompt, schema, **kwargs):
        calls.append({"prompt": prompt, "schema": schema, "kwargs": kwargs})
        value = responses(prompt) if callable(responses) else responses
        return value
    return call, calls


def test_rules_mode_records_thought_and_source_without_extra_steps():
    snapshot = run(dict(DEMO, planner="rules"))
    assert snapshot["final"]["label"] == "FLAGGED"
    assert len(snapshot["history"]) == 10
    variants = by_action(snapshot, "search_variants")[0]
    assert variants["source"] == "rules" and "misread" in variants["thought"]
    assert by_action(snapshot, "draft_verdict")[0]["verifier"] == "approved"


def test_hybrid_calls_llm_at_branch_points_with_json_schema(monkeypatch):
    call, calls = fake_llm(lambda prompt: {"thought": "The 8 may be a scuffed B; try look-alikes." if "search_variants" in prompt["allowed"] else "Only the user can confirm the character.",
                                           "action": prompt["allowed"][0]})
    monkeypatch.setattr(llm, "structured_call", call)
    snapshot = run(dict(DEMO, planner="hybrid"))
    assert snapshot["final"]["label"] == "FLAGGED"
    assert len(calls) == 2
    first, second = calls
    assert first["schema"]["properties"]["action"]["enum"] == ["search_variants", "draft_verdict"]
    assert first["schema"]["required"] == ["thought", "action"]
    assert first["prompt"]["evidence"]["exact_hits"] == 0 and first["prompt"]["rule_suggestion"] == "search_variants"
    assert second["prompt"]["evidence"]["candidate_status"] == "needs_confirm_char"
    assert first["kwargs"]["timeout"] <= 90 and first["kwargs"]["model"]
    variants, ask = by_action(snapshot, "search_variants")[0], by_action(snapshot, "ask_user")[0]
    assert variants["source"] == "llm" and "scuffed B" in variants["thought"]
    assert ask["source"] == "llm"
    # The LLM thought stays in the trace; verdict text comes only from templates.
    final_text = " ".join(str(snapshot["final"].get(key, "")) for key in ("headline", "explanation", "advice"))
    assert "scuffed" not in final_text and "Only the user" not in final_text
    rules = run(dict(DEMO, planner="rules"))
    assert rules["final"]["label"] == snapshot["final"]["label"] and len(rules["history"]) == len(snapshot["history"])


def test_hybrid_with_ollama_off_falls_back_quickly(monkeypatch):
    attempts = []

    def refused(*args, **kwargs):
        attempts.append(1)
        raise ConnectionRefusedError("unit test: Ollama stopped")
    monkeypatch.setattr(llm, "urlopen", refused)
    started = time.perf_counter()
    snapshot = run(dict(DEMO, planner="hybrid"))
    assert time.perf_counter() - started < 2
    assert snapshot["final"]["label"] == "FLAGGED"
    assert by_action(snapshot, "search_variants")[0]["source"] == "rules(fallback)"
    assert by_action(snapshot, "ask_user")[0]["source"] == "rules(fallback)"
    # The circuit breaker stops repeat attempts after the first refusal.
    assert len(attempts) == 1


def test_invalid_or_disallowed_llm_action_falls_back(monkeypatch):
    call, _ = fake_llm({"thought": "Email the regulator.", "action": "send_email"})
    monkeypatch.setattr(llm, "structured_call", call)
    snapshot = run(dict(DEMO, planner="hybrid"))
    assert by_action(snapshot, "search_variants")[0]["source"] == "rules(fallback)"
    assert snapshot["final"]["label"] == "FLAGGED"


def test_banned_wording_in_thought_is_withheld(monkeypatch):
    call, _ = fake_llm(lambda prompt: {"thought": "This medicine is safe and genuine.", "action": prompt["allowed"][0]})
    monkeypatch.setattr(llm, "structured_call", call)
    snapshot = run(dict(DEMO, planner="hybrid"))
    thought = by_action(snapshot, "search_variants")[0]["thought"]
    assert "safe" not in thought.lower() and "withheld" in thought


def test_verifier_sends_back_a_premature_draft(monkeypatch):
    call, _ = fake_llm(lambda prompt: {"thought": "Nothing matched, give the result.", "action": "draft_verdict"} if "search_variants" in prompt["allowed"]
                       else {"thought": "Ask the user.", "action": "ask_user"})
    monkeypatch.setattr(llm, "structured_call", call)
    snapshot = run(dict(DEMO, planner="hybrid"))
    actions = [step["action"] for step in snapshot["history"]]
    assert actions[:6] == ["extract_fields", "search_exact", "plan", "verify", "search_variants", "grade"]
    assert by_action(snapshot, "search_variants")[0]["source"] == "rules(verifier)"
    assert snapshot["final"]["label"] == "FLAGGED" and len(snapshot["history"]) <= 16


def test_llm_may_abstain_but_never_flag_without_the_question(monkeypatch):
    call, _ = fake_llm(lambda prompt: {"thought": "Stop here.", "action": "draft_verdict"} if "ask_user" in prompt["allowed"] else {"thought": "Search.", "action": "search_variants"})
    monkeypatch.setattr(llm, "structured_call", call)
    snapshot = run(dict(DEMO, planner="hybrid"), answers=[])
    assert snapshot["status"] == "done" and snapshot["final"]["label"] == "CANT_VERIFY"
    assert by_action(snapshot, "draft_verdict")[0]["source"] == "llm"


def test_prior_shows_in_trace_and_question_but_never_skips_it():
    context = real_context(confusion_counts=[{"ocr_char": "8", "true_char": "B", "source": "user", "count": 1}])
    snapshot = investigate(CASE["fields"], real_alerts(), context=context)
    assert snapshot["status"] == "waiting" and snapshot["pending"]["kind"] == "confirm_char"
    variants = by_action(snapshot, "search_variants")[0]
    assert variants["prior"] == "8->B seen 1 time"
    assert "Prior confirmed corrections: 8 to B: 1" in variants["summary"]
    assert "read B as 8 once" in snapshot["pending"]["question"]
    assert snapshot["pending"]["prior"] == [{"read": "8", "true": "B", "count": 1}]
    assert by_action(snapshot, "ask_user")[0]["prior"] == "8->B seen 1 time"
    # Even a large prior does not change the printed batch or skip the question.
    strong = investigate(CASE["fields"], real_alerts(), context=real_context(confusion_counts=[{"ocr_char": "8", "true_char": "B", "source": "user", "count": 50}]))
    assert strong["status"] == "waiting" and strong["fields"]["batch"] == "LM24088"
    assert "50 times" in strong["pending"]["question"]


def test_demo_checks_never_use_the_prior():
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, confusion_counts=[{"ocr_char": "8", "true_char": "B", "source": "user", "count": 3}]))
    assert "prior" not in snapshot["pending"] and "earlier checks" not in snapshot["pending"]["question"].lower()


def test_otel_export_is_off_and_fast_when_phoenix_is_down(monkeypatch):
    assert tracing.export_check({"name": "x", "start_ns": 1, "end_ns": 2}) is None
    monkeypatch.setenv("STRIPCHECK_TRACING", "1")
    monkeypatch.setenv("STRIPCHECK_PHOENIX_URL", "http://127.0.0.1:9/v1/traces")
    monkeypatch.setitem(tracing._OTEL, "probe_at", 0.0)
    started = time.perf_counter()
    snapshot = run(dict(DEMO, planner="rules"))
    assert time.perf_counter() - started < 2
    assert snapshot["final"]["label"] == "FLAGGED" and "otel" not in snapshot["context"]["_engine"]
    assert "_marks" not in snapshot["context"]["_engine"] and "_call" not in snapshot["context"]["_engine"]


def test_export_never_raises_on_bad_segments(monkeypatch):
    monkeypatch.setattr(tracing, "_tracer", lambda: object())
    assert tracing.export_check({"name": "broken"}) is None
    assert tracing.export_check({}) is None


def test_otel_trace_is_nested_and_resume_joins_the_same_trace(monkeypatch):
    pytest.importorskip("opentelemetry.sdk")
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setenv("STRIPCHECK_TRACING", "1")
    monkeypatch.setattr(tracing, "_tracer", lambda: provider.get_tracer("test"))
    call, _ = fake_llm(lambda prompt: {"thought": "Try look-alikes.", "action": prompt["allowed"][0]})
    monkeypatch.setattr(llm, "structured_call", call)
    snapshot = run(dict(DEMO, planner="hybrid"))
    assert snapshot["final"]["label"] == "FLAGGED"
    spans = exporter.get_finished_spans()
    names = [span.name for span in spans]
    assert "check" in names and "check.resume" in names
    assert {"planner: search_variants", "search_variants", "planner_llm", "ask_user", "answer", "verifier"} <= set(names)
    assert len({span.context.trace_id for span in spans}) == 1
    root = next(span for span in spans if span.name == "check")
    resume = next(span for span in spans if span.name == "check.resume")
    assert resume.parent.span_id == root.context.span_id
    tool = next(span for span in spans if span.name == "search_variants" and span.attributes["openinference.span.kind"] == "TOOL")
    parent = next(span for span in spans if span.context.span_id == tool.parent.span_id)
    assert parent.name == "planner: search_variants" and parent.attributes["stripcheck.source"] == "llm"
    assert "LM2408B" in tool.attributes["output.value"]
    llm_span = next(span for span in spans if span.name == "planner_llm")
    assert llm_span.attributes["openinference.span.kind"] == "LLM" and "search_variants" in llm_span.attributes["input.value"]
    verifier = next(span for span in spans if span.name == "verifier")
    assert verifier.attributes["openinference.span.kind"] == "GUARDRAIL" and "approved" in verifier.attributes["output.value"]
    assert root.attributes["session.id"] == resume.attributes["session.id"]
    # Planner spans under the first root follow the step order in time.
    planners = sorted((span for span in spans if span.parent is not None and span.parent.span_id == root.context.span_id and span.name.startswith("planner:")), key=lambda span: span.start_time)
    assert [span.name for span in planners] == ["planner: extract_fields", "planner: search_exact", "planner: search_variants", "planner: grade", "planner: ask_user"]
    assert all(a.end_time <= b.start_time for a, b in zip(planners, planners[1:]))

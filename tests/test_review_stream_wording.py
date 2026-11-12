"""Reviewer tests: partial banned phrases must not reach live deltas (no Ollama needed)."""
import pytest

from core import llm
from core.investigator import investigate
from tests.test_live_thinking import CASE, DEMO, collector, streaming_ollama, thinking


@pytest.fixture(autouse=True)
def fresh_llm_state(monkeypatch):
    monkeypatch.setitem(llm._STATE, "down_until", 0.0)
    monkeypatch.setattr(llm, "THROTTLE", 0)


@pytest.mark.parametrize("thought, fragment", [
    ("If this batch is listed you should stop taking it right away.", "stop tak"),
    ("The print looks like a fake medicine from a counterfeit maker.", "fake medic"),
])
def test_partial_banned_phrase_never_streams(monkeypatch, thought, fragment):
    streaming_ollama(monkeypatch, lambda allowed: thought)
    seen, observe = collector()
    investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="hybrid"), observer=observe)
    leaked = [d["text"] for d in thinking(seen, "delta") if fragment in d["text"]]
    assert not leaked, leaked


def test_reassurance_wording_outside_banned_reaches_end_and_history(monkeypatch):
    """Documents the gap: model text implying the pack is fine is shown live and kept in history."""
    streaming_ollama(monkeypatch, lambda allowed: "No alert matches, so this pack is fine to use and harmless.")
    seen, observe = collector()
    snapshot = investigate(CASE["fields"], CASE["alerts"], context=dict(DEMO, planner="hybrid"), observer=observe)
    shown = [b["text"] for b in thinking(seen, "end")] + [s.get("thought", "") for s in snapshot["history"]]
    assert not any("fine to use" in text for text in shown), shown

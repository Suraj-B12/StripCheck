"""Offline, bounded investigation with JSON-serializable pause/resume state."""

from copy import deepcopy
from datetime import date
from pathlib import Path
import re
from time import perf_counter, perf_counter_ns, time_ns
import uuid

from core import config, llm, tracing
from core.matching import build_index, grade, search_exact, search_variants
from core.noisy import confirmation_positions, prior_counts
from core.templates import DECLINE_PHOTO, NO, YES, prior_note, question, render_verdict, thinking_context
from core.textutils import PLACEHOLDERS, batch_key, maker_name, parse_month_year
from core.verifier import GATE_EVIDENCE, verify_verdict

MAX_STEPS, MAX_ASKS, MAX_CANDIDATES = 16, 2, 20
MAX_VISION_CALLS, MAX_PHOTOS = 2, 1
FIELD_NAMES = ("batch", "product", "brand", "mfg", "exp", "maker")
SOURCES = {"user", "ocr", "qr", "ocr_enh", "carton", "vlm"}
_WALL0, _PERF0 = time_ns(), perf_counter_ns()


def _now_ns():
    """Wall-clock nanoseconds with perf_counter resolution (Windows time_ns is coarse)."""
    return _WALL0 + perf_counter_ns() - _PERF0


def _date(value):
    text = str(value or "").strip()
    if re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", text):
        return text
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        try:
            return date.fromisoformat(text).strftime("%Y-%m")
        except ValueError:
            return None
    return parse_month_year(text)


def _fields(raw):
    fields = {key: str(raw.get(key) or "").strip()[:500] for key in FIELD_NAMES}
    for key in ("maker", "mfg", "exp"):
        if fields[key].lower() in PLACEHOLDERS:
            fields[key] = ""
    # Keep every product line the reader saw: a brand line above the generic name must not hide it from grading.
    fields["product_text"] = str(raw.get("product_text") or "").strip()[:500]
    fields["product"] = fields["product"] or fields["product_text"]
    source = raw.get("source", "user")
    # read_pack reports "none" when the photo gave no batch; its other printed fields are still OCR text.
    source = "ocr" if source == "none" else source
    fields["source"] = source if source in SOURCES else "unknown"
    fields["confirmed"] = bool(raw.get("confirmed", False))
    return fields


def _rows(alerts, demo):
    rows = []
    for index, raw in enumerate(alerts):
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        flags = row.get("flags") or []
        if not isinstance(flags, (list, tuple, set, str)):
            flags = []
        synthetic = bool(row.get("synthetic")) or "synthetic" in flags or "synthetic" in str(row.get("source_title", "")).lower()
        if synthetic and not demo:
            continue
        row["batch_key"] = batch_key(row.get("batch_key") or row.get("batch_raw") or row.get("batch"))
        if not row["batch_key"]:
            continue
        if row.get("id") is None:
            row["id"] = index + 1
        row["product"] = str(row.get("product") or "")
        row["brand"] = str(row.get("brand") or "")
        row["maker_name"] = str(row.get("maker_name") or maker_name(row.get("maker_raw") or row.get("maker")))
        row["entry_type"] = str(row.get("entry_type") or "UNKNOWN").upper()
        row["mfg"], row["exp"] = _date(row.get("mfg")), _date(row.get("exp"))
        rows.append(row)
    return rows


TOOL_ACTIONS = {"extract_fields", "search_exact", "search_variants", "grade"}
RULE_THOUGHTS = {
    "search_variants": "No exact entry was found; the printed batch may hold a misread look-alike character, so search bounded alternatives.",
    "search_variants_after_hit": "An exact entry exists; look-alike alternatives are still checked so no listed batch is missed.",
    "confirm_char": "The closest entry differs only by look-alike character(s); only the person holding the pack can confirm which is printed.",
    "confirm_field": "A printed date disagrees with the entry; ask which date is printed before any result.",
    "box_photo": "The batch matches but the product, dates or maker are not corroborated; ask for more printed details.",
    "confirm_batch": "A corroborated entry matches, but the batch was read by a machine; a person must confirm it before a listed result.",
    "type_batch": "The batch number is missing or the readers disagree; ask the person to type it.",
    "draft_verdict": "The evidence is complete or no further question is allowed; draft the result for the verifier.",
    "search_exact": "Start with an exact search of the printed batch against the loaded alert records.",
    "grade": "Both searches ran; compare product, brand, dates and maker for every candidate.",
    "reflect_ask": "The verifier found a gap a person can close; ask one more question before any result.",
    "reflect_search": "The verifier found the search incomplete; run the missing search once.",
    "reflect": "The verifier sent the draft back; choose one revision or abstain.",
    "reflect_downgrade":"The verifier found a gap that no allowed step can close; abstain instead of guessing.",
    "read_with_vision": "The text reader could not read the batch clearly; read the batch line with the local vision model before asking the person to type.",
    "confirm_reading": "A vision reading is never used by itself; ask the person whether it is the printed batch.",
    "request_photo": "The readings are in doubt; one more photo of exactly the missing detail is the cheapest way to settle it.",
}
# Which agent owns each step. Agents are plain functions passing message dicts, not classes.
AGENTS = ("perception", "investigator", "verifier", "supervisor")
AGENT_OF = {"extract_fields": "perception", "read_pack": "perception", "read_with_vision": "perception", "verify": "verifier"}
MAX_MESSAGES = 24
# Tools the "agent" planner may call (offered per step only when the rules allow them).
TOOL_SPECS = {
    "search_exact": "Search the loaded alert records for the printed batch exactly.",
    "search_variants": "Search bounded look-alike alternatives of the printed batch (never changes the printed batch).",
    "grade": "Compare product, brand, dates and maker of every candidate with the pack.",
    "ask_user": "Ask the person holding the pack one question of the given kind.",
    "draft_verdict": "Draft the result from the evidence so far; the verifier checks it.",
    "downgrade": "Accept the verifier's result: abstain (cannot verify).",
    "read_with_vision": "Read the batch line from the photo with the local vision model; the reading is used only after the person confirms it.",
    "request_photo": "Ask the person for one more photo of exactly the missing evidence (the given kind); they may decline.",
}


def _log(state, action, summary, started=None, source="rules", thought=None, io=None, llm_meta=None, agent=None, observation=None, react_args=None, **extra):
    if len(state["history"]) >= MAX_STEPS:
        return
    entry = {"step": len(state["history"]) + 1, "action": action, "source": source, "summary": summary, "ms": round((perf_counter() - started) * 1000, 2) if started else 0,
             "agent": agent if agent in AGENTS else AGENT_OF.get(action, "investigator")}
    if thought:
        entry["thought"] = thought
        # ReAct labels: the reason, the tool call and a short summary of what it returned.
        entry["react"] = {"thought": thought, "action": {"tool": action, "args": dict(react_args or {})}, "observation": str(observation or summary)[:240]}
        if state.get("_last_think"):
            entry["think_id"] = state.pop("_last_think")
    entry.update({key: value for key, value in extra.items() if value is not None})
    state["history"].append(entry)
    state.setdefault("_marks", []).append({"i": len(state["history"]) - 1, "end_ns": _now_ns(), "io": io or {}, "llm": llm_meta})
    _emit(state, "step", dict(entry))


def _emit(state, event, data):
    """Send a live event to the caller's observer; display failures never affect the check."""
    observer = state.get("_observer")
    if observer is None:
        return
    try:
        observer(event, data)
    except Exception:
        pass


def _decide(state, mode, evidence, allowed, suggestion, thought_key):
    """Branch-point planner: the LLM in hybrid/llm mode, otherwise the rules.

    Emits one live "thinking" block (start, throttled deltas in hybrid mode, end).
    """
    number = int(state.get("thinking_count", 0)) + 1
    state["thinking_count"] = number
    model = state.get("llm_model") or config.LLM_MODEL
    asks_llm = mode in {"hybrid", "llm", "agent"} and len(allowed) >= 2 and suggestion in allowed and bool(model)
    block = {"id": f"think-{number}", "context": thinking_context(thought_key), "agent": "investigator"}
    start = dict(block, phase="start", source="llm" if asks_llm else "rules", text="")
    if asks_llm:
        start["model"] = model
    _emit(state, "thinking", start)
    extra = {}
    if asks_llm and state.get("_observer") is not None:
        extra["on_text"] = lambda text: _emit(state, "thinking", dict(block, phase="delta", source="llm", text=text, model=model, redacted=False))
    started = perf_counter()
    decision = llm.plan_decision(evidence, allowed, suggestion, RULE_THOUGHTS[thought_key], mode=mode,
                                 model=model, url=config.OLLAMA_URL, timeout=config.LLM_TIMEOUT, **extra)
    end = dict(block, phase="end", source=decision["source"], text=decision["thought"], action=decision["action"],
               ms=round((perf_counter() - started) * 1000), redacted=bool(decision.get("redacted")),
               react={"thought": decision["thought"], "action": {"tool": decision["action"], "args": {}}})
    if decision["source"] == "llm":
        end["model"] = model
    _emit(state, "thinking", end)
    state["_last_think"] = block["id"]
    state.setdefault("decisions", []).append({"step": len(state["history"]) + 1, "action": decision["action"], "source": decision["source"]})
    return decision


def _agent_decide(state, evidence, tools, rule_choice, thought_key, observations):
    """One tool-calling turn of the investigator agent ("agent" planner).

    `tools` are only the tools the rules allow now; an invalid call, timeout or
    error falls back to `rule_choice` (source "rules(fallback)"). Emits one thinking block.
    """
    number = int(state.get("thinking_count", 0)) + 1
    state["thinking_count"] = number
    model = state.get("llm_model") or config.LLM_MODEL
    rule_thought = RULE_THOUGHTS.get(thought_key, RULE_THOUGHTS["draft_verdict"])
    block = {"id": f"think-{number}", "context": thinking_context(thought_key), "agent": "investigator"}
    start = dict(block, phase="start", source="llm" if model else "rules", text="")
    if model:
        start["model"] = model
    _emit(state, "thinking", start)
    started = perf_counter()
    on_text = None
    if model and state.get("_observer") is not None:
        on_text = lambda text: _emit(state, "thinking", dict(block, phase="delta", source="llm", text=text, model=model, redacted=False))
    if model:
        decision = llm.agent_step(evidence, observations, tools, rule_choice, rule_thought, on_text=on_text,
                                  model=model, url=config.OLLAMA_URL, timeout=config.LLM_TIMEOUT)
    else:
        decision = {"action": rule_choice["tool"], "args": dict(rule_choice.get("args") or {}), "source": "rules", "thought": rule_thought, "llm": None, "redacted": False}
    end = dict(block, phase="end", source=decision["source"], text=decision["thought"], action=decision["action"],
               ms=round((perf_counter() - started) * 1000), redacted=bool(decision.get("redacted")),
               react={"thought": decision["thought"], "action": {"tool": decision["action"], "args": dict(decision.get("args") or {})}})
    if decision["source"] == "llm":
        end["model"] = model
    _emit(state, "thinking", end)
    state["_last_think"] = block["id"]
    state.setdefault("decisions", []).append({"step": len(state["history"]) + 1, "action": decision["action"], "source": decision["source"], "via": decision.get("via", "rules")})
    return decision


def _handoff(state, sender, receiver, kind, reason, payload=None):
    """Pass a message between agents; logged as a "handoff" step in the agent planner.

    Rules and hybrid planners keep their step counts: the message is kept in
    state["messages"] and in the trace only.
    """
    message = {"from": sender, "to": receiver, "kind": kind, "reason": reason, "payload": payload or {}}
    messages = state.setdefault("messages", [])
    if len(messages) < MAX_MESSAGES:
        messages.append(message)
    if state.get("planner") == "agent" and len(state["history"]) < MAX_STEPS - 1:
        _log(state, "handoff", f"{sender} -> {receiver}: {reason}", agent=sender, io={"output": message},
             **{"from": sender, "to": receiver, "reason": reason, "kind": kind})
    return message


def _prior_items(pairs, prior):
    return sorted({(read, true, prior.get((read, true), 0)) for read, true in pairs if prior.get((read, true), 0)})


def _prior_text(items):
    return "; ".join(f"{read}->{true} seen {count} time{'s' if count != 1 else ''}" for read, true, count in items[:6])


def _with_prior(pending, items):
    note = prior_note(items)
    if note:
        pending["question"] = f"{pending['question']} {note}"
        pending["prior"] = [{"read": read, "true": true, "count": count} for read, true, count in items]
    return pending


def _span_steps(state, history, marks):
    """Turn this call's history entries into agent-turn spans holding planner/tool/LLM spans.

    Consecutive steps of one agent form one AGENT span ("agent: investigator");
    hand-offs are their own spans ("handoff: perception -> investigator").
    """
    turns, previous_end = [], 0

    def add(agent, span):
        if turns and turns[-1]["attributes"]["stripcheck.agent"] == agent:
            turns[-1]["children"].append(span)
            turns[-1]["end_ns"] = max(turns[-1]["end_ns"], span["end_ns"])
        else:
            turns.append({"name": f"agent: {agent}", "kind": "AGENT", "start_ns": span["start_ns"], "end_ns": span["end_ns"],
                          "attributes": {"stripcheck.agent": agent}, "children": [span]})

    held = []  # the verifier turn follows the investigator -> verifier hand-off when there is one
    for mark in marks:
        entry = history[mark["i"]]
        if held and not (entry["action"] == "handoff" and entry.get("to") == "verifier"):
            add("verifier", held.pop())
        end = max(mark["end_ns"], previous_end)
        agent = entry.get("agent", "investigator")
        if entry["action"] == "handoff":
            add(agent, {"name": f"handoff: {entry.get('from')} -> {entry.get('to')}", "kind": "CHAIN", "start_ns": max(end - 1000, previous_end), "end_ns": end,
                        "input": {"from": entry.get("from"), "to": entry.get("to")}, "output": mark["io"].get("output"),
                        "attributes": {"stripcheck.step": entry["step"], "stripcheck.handoff.from": entry.get("from", ""), "stripcheck.handoff.to": entry.get("to", ""),
                                       "stripcheck.handoff.reason": entry.get("reason", "")}, "children": []})
            previous_end = end
            if held:
                add("verifier", dict(held.pop(), start_ns=end, end_ns=end + 1000))
                previous_end = end + 1000
            continue
        tool_start = max(end - int(float(entry.get("ms") or 0) * 1e6), previous_end)
        kind = "TOOL" if entry["action"] in TOOL_ACTIONS else "CHAIN"
        tool = {"name": entry["action"], "kind": kind, "start_ns": tool_start, "end_ns": end,
                "input": mark["io"].get("input"), "output": mark["io"].get("output", entry.get("summary")),
                "attributes": {"stripcheck.step": entry["step"], "stripcheck.summary": entry.get("summary", "")}, "children": []}
        verifier = None
        if entry["action"] == "draft_verdict" and entry.get("verifier"):
            verifier = {"name": "verifier", "kind": "GUARDRAIL", "start_ns": end, "end_ns": end + 1000,
                        "input": mark["io"].get("output"), "output": entry["verifier"], "attributes": {"stripcheck.agent": "verifier"}}
        children, start = [], tool_start
        meta = mark.get("llm")
        if meta:
            start = max(tool_start - int(float(meta.get("ms") or 0) * 1e6), previous_end)
            children.append({"name": "planner_llm", "kind": "LLM", "start_ns": start, "end_ns": tool_start,
                             "input": meta.get("prompt"), "output": meta.get("response") or meta.get("error"),
                             "attributes": {"llm.model_name": meta.get("model", ""), "llm.invocation_parameters": '{"temperature": 0}'}})
        children.append(tool)
        add(agent, {"name": f"planner: {entry['action']}", "kind": "CHAIN", "start_ns": start, "end_ns": end,
                    "input": {"step": entry["step"], "source": entry.get("source")},
                    "output": {"action": entry["action"], "thought": entry.get("thought", ""), "observation": (entry.get("react") or {}).get("observation", "")},
                    "attributes": {"stripcheck.source": entry.get("source", ""), "stripcheck.thought": entry.get("thought", ""), "stripcheck.prior": entry.get("prior", ""),
                                   "stripcheck.agent": agent},
                    "children": children})
        previous_end = end
        if verifier:
            held.append(verifier)
            previous_end = verifier["end_ns"]
    if held:
        add("verifier", held.pop())
    return turns


def _export(fields, state, pending, final):
    call, marks = state.pop("_call", None), state.pop("_marks", [])
    if not call or not tracing.otel_enabled():
        return
    resumed = bool(state.get("otel"))
    output = {"status": "waiting" if pending else "done", "label": (final or {}).get("label"), "question": (pending or {}).get("question"), "kind": (pending or {}).get("kind")}
    segment = {"name": "check.resume" if resumed else "check", "session": state.get("session"), "parent": state.get("otel"),
               "start_ns": call["start_ns"], "end_ns": _now_ns(),
               "input": {"fields": {k: fields.get(k) for k in FIELD_NAMES + ("source",)}, "answer": call.get("answer")}, "output": output,
               "attributes": {"stripcheck.planner": state.get("planner", "rules"), "stripcheck.batch_evidence": state.get("batch_evidence"), "stripcheck.asks": state.get("asks", 0), "stripcheck.steps": len(state["history"])},
               "steps": _span_steps(state, state["history"], marks)}
    ids = tracing.export_check(segment)
    if ids and not resumed:
        state["otel"] = ids


def _strip(fields, state, pending=None):
    key = batch_key(fields.get("batch"))
    positions = set((pending or {}).get("positions", []))
    confirmed = state.get("batch_evidence") in GATE_EVIDENCE
    return {"source": state.get("batch_evidence", "none"), "chars": [{"ch": char, "state": "uncertain" if i + 1 in positions else "confirmed" if confirmed else "read", "alts": [sub[2] for sub in (pending or {}).get("subs", []) if sub[0] == i]} for i, char in enumerate(key)]}


def _snapshot(fields, context, state, pending=None, final=None):
    state.pop("_observer", None)
    state.pop("_last_think", None)
    if pending and "asks_used" not in pending:
        pending["asks_used"], pending["asks_max"] = min(state["asks"] + 1, MAX_ASKS), MAX_ASKS
        crop = str(context.get("batch_crop") or "")
        if re.fullmatch(r"/api/crops/[A-Za-z0-9_-]{1,100}\.png", crop):
            pending["crop"] = crop
    try:
        _export(fields, state, pending, final)
    except Exception:
        state.pop("_call", None)
        state.pop("_marks", None)
    state["pending"] = pending
    context["_engine"] = state
    return {"fields": fields, "strip": _strip(fields, state, pending), "history": state["history"], "status": "waiting" if pending else "done", "pending": pending, "final": final, "context": context, "candidates": state.get("candidates", [])}


def _apply_answer(fields, state, answer):
    pending = state.get("pending")
    if not pending:
        return None
    kind = pending["kind"]
    choice = str(answer.get("choice", "")).strip()
    skip = bool(answer.get("skip")) or choice.lower() in {"cant_tell", "can't tell", "cannot tell", "skip", "decline", DECLINE_PHOTO.lower()}
    changes = {}
    old_key = batch_key(fields["batch"])
    if skip:
        state["declined"].append(kind)
        if kind == "confirm_field":
            state["conflict_ids"].append(pending.get("entry_id"))
        if kind == "confirm_reading" and state.get("vision"):
            state["vision"]["status"] = "rejected"
    elif kind == "confirm_reading":
        reading = str(pending.get("reading") or "")
        lowered = choice.lower()
        if answer.get("confirm") is True or lowered in {"yes", "y", YES.lower()}:
            changes["batch"] = reading
            state["batch_evidence"] = "user_confirmed"
            state["low_confidence"] = False
            if state.get("vision"):
                state["vision"]["status"] = "confirmed"
        elif answer.get("confirm") is False or lowered in {"no", "n", NO.lower()}:
            state["rejected_keys"].append(batch_key(reading))
            if state.get("vision"):
                state["vision"]["status"] = "rejected"
        else:
            return "Choose Yes or No."
    elif kind == "request_photo":
        supplied = answer.get("fields") if isinstance(answer.get("fields"), dict) else None
        if supplied is None and not answer.get("image"):
            return "Add the photo, or choose I can't take another photo."
        changes = _merge_photo(fields, state, supplied or {}, "carton" if pending.get("photo_kind") == "carton" else "ocr", old_key)
    elif kind in {"type_batch", "confirm_batch"}:
        typed = str(answer.get("typed") or answer.get("batch") or "").strip()
        chars = answer.get("chars")
        if not typed and isinstance(chars, dict) and kind == "confirm_batch":
            if any(not re.fullmatch(r"[A-Za-z0-9]", str(chars.get(str(i), chars.get(i, "")))) for i in pending["positions"]):
                return "Enter one letter or digit for every requested position."
            corrected = list(old_key)
            for position in pending["positions"]:
                corrected[position - 1] = str(chars.get(str(position), chars.get(position))).upper()
            typed = "".join(corrected)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 /-]{1,39}", typed) or len(batch_key(typed)) < 2:
            return "Type the printed batch number, or choose Can't tell."
        changes["batch"] = typed
        state["batch_evidence"] = "user_typed" if kind == "type_batch" else "user_confirmed"
        if old_key and batch_key(typed) != old_key:
            state["rejected_keys"].append(old_key)
    elif kind == "confirm_char":
        listed, pack = batch_key(pending["listed"]), batch_key(pending["pack"])
        selected = batch_key(str(answer.get("typed") or choice))
        listed_chars = "".join(listed[i - 1] for i in pending.get("positions", []) if i <= len(listed))
        pack_chars = "".join(pack[i - 1] for i in pending.get("positions", []) if i <= len(pack))
        if selected == listed or (listed_chars and selected == listed_chars) or choice.lower() == "listed":
            changes["batch"] = pending["listed"]
            state["batch_evidence"] = "user_confirmed"
            state["confirmed_keys"].append(listed)
            state["confirmed_substitutions"].extend(pending.get("subs", []))
        elif selected == pack or (pack_chars and selected == pack_chars) or choice.lower() in {"read", "pack", "printed"}:
            state["rejected_keys"].append(listed)
            state["batch_evidence"] = "user_confirmed"
        else:
            return "Choose the batch printed on the pack, or choose Can't tell."
    elif kind == "confirm_field":
        if choice == pending["listed"] or choice.lower() == "listed":
            changes[pending["field"]] = pending["listed"]
        elif choice == pending["pack"] or choice.lower() in {"pack", "printed", "read"}:
            state["conflict_ids"].append(pending.get("entry_id"))
        else:
            return "Choose one of the printed-date options, or choose Can't tell."
    else:
        supplied = answer.get("fields")
        if not isinstance(supplied, dict) or not any(str(supplied.get(k) or "").strip() for k in FIELD_NAMES):
            return "Add the details printed on the pack or carton, or choose Can't tell."
        changes = {key: str(supplied[key]).strip()[:500] for key in FIELD_NAMES if supplied.get(key)}
        answer_source = answer.get("source", "user")
        if answer_source not in SOURCES:
            return "The supplied detail source is not supported."
        if "batch" in changes:
            if answer_source != "user":
                if batch_key(changes["batch"]) == old_key:
                    state["batch_evidence"] = "dual_read"
                else:
                    state["batch_evidence"] = answer_source
                    state["reader_disagreement"] = bool(old_key)
            elif batch_key(changes["batch"]) != old_key and old_key:
                state["rejected_keys"].append(old_key)
            if answer_source == "user":
                state["batch_evidence"] = "user_typed"
    for key, value in changes.items():
        fields[key] = value
        if kind == "request_photo":
            state["provenance"][key] = "carton" if pending.get("photo_kind") == "carton" else "ocr"
        elif kind == "confirm_reading":
            state["provenance"][key] = "vlm"  # read by the vision model, confirmed by the person (batch_evidence user_confirmed)
        else:
            state["provenance"][key] = answer.get("source", "user") if kind == "box_photo" else "user"
    if changes:
        state["fields_version"] += 1
    if state["batch_evidence"] in GATE_EVIDENCE:
        fields["confirmed"] = True
        state["reader_disagreement"] = False
    else:
        fields["confirmed"] = False
    state["asks"] += 1
    _log(state, "answer", "Printed details updated by the user." if changes else "The user's answer was recorded.", source="user",
         io={"input": {k: answer.get(k) for k in ("choice", "typed", "skip", "chars", "source") if k in answer}, "output": {"changes": changes, "batch_evidence": state["batch_evidence"]}})
    state["pending"] = None
    return None


def _do_exact(state, index, batch, searched_count, demo, decision=None):
    """Tool: exact batch search."""
    decision = decision or {}
    started = perf_counter()
    exact = search_exact(index, batch, max_hits=MAX_CANDIDATES + 1)
    state["exact_searched"] = True
    _log(state, "search_exact", f"Checked the exact batch against {searched_count:,} {'synthetic' if demo else 'loaded'} records; {len(exact)} candidate(s).", started,
         source=decision.get("source", "rules"), thought=decision.get("thought"), llm_meta=decision.get("llm"),
         io={"input": {"batch_key": batch, "records": searched_count}, "output": [{"id": r.get("id"), "batch_key": r.get("batch_key"), "entry_type": r.get("entry_type")} for r in exact[:5]]})
    return exact


def _do_variants(state, index, batch, prior, known, decision):
    """Tool: bounded look-alike search; never changes the printed batch."""
    started = perf_counter()
    variants = search_variants(index, batch, prior=prior, max_subs=2, max_lookups=2000, max_hits=MAX_CANDIDATES + 1)
    state["variants_searched"] = True
    prior_suffix = ""
    used_priors = sorted({(read, true, prior.get((read, true), 0)) for candidate in variants for _, read, true in candidate.get("subs", []) if prior.get((read, true), 0)})
    if used_priors:
        prior_suffix = " Prior confirmed corrections: " + "; ".join(f"{read} to {true}: {count}" for read, true, count in used_priors[:6]) + ". Confirmation is still required."
    _log(state, "search_variants", f"Checked bounded character alternatives; {len(variants)} candidate(s). No printed character was changed." + prior_suffix, started,
         source=decision["source"], thought=decision["thought"], llm_meta=decision["llm"], prior=_prior_text(used_priors) or None,
         io={"input": {"batch_key": batch, "max_subs": 2, "prior": [f"{read}->{true} x{count}" for read, true, count in known[:6]]},
             "output": [{"id": r.get("id"), "batch_key": r.get("batch_key"), "subs": r.get("subs"), "entry_type": r.get("entry_type")} for r in variants[:5]]})
    return variants


def _do_grade(state, fields, exact, variants, decision=None):
    """Tool: record-linkage grading of every unique candidate."""
    decision = decision or {}
    unique = {}
    for row in exact + variants:
        if row["id"] not in unique:
            unique[row["id"]] = row
    state["truncated"] = len(unique) > MAX_CANDIDATES or len(exact) > MAX_CANDIDATES or len(variants) > MAX_CANDIDATES
    grading_fields = dict(fields, product_text=" ".join(dict.fromkeys(filter(None, (fields["product"], fields["brand"], fields.get("product_text", ""))))), mfg=_date(fields["mfg"]), exp=_date(fields["exp"]))
    candidates = []
    for row in list(unique.values())[:MAX_CANDIDATES]:
        if row["batch_key"] in state["confirmed_keys"]:
            row["how"] = "confirmed"
        candidate = grade(row, grading_fields)
        if row["batch_key"] in state["rejected_keys"]:
            candidate.update(status="reject", rejection="The user confirmed a different printed batch.")
        elif row["id"] in state["conflict_ids"]:
            candidate["status"] = "date_conflict"
        candidates.append(candidate)
    state["candidates"] = candidates
    _log(state, "grade", "Compared product, brand, dates and manufacturer for every candidate.",
         source=decision.get("source", "rules"), thought=decision.get("thought"), llm_meta=decision.get("llm"),
         io={"input": {k: grading_fields.get(k) for k in ("batch", "product", "brand", "mfg", "exp", "maker")},
             "output": [{"id": c.get("id"), "batch_key": c.get("batch_key"), "status": c.get("status"), "evidence": c.get("evidence")} for c in candidates[:5]]})
    return candidates


def _assess(state, candidates, can_ask, text_mode):
    """Rules: what the graded candidates allow next. Returns {top, reason, label, ask?, optional?}.

    `ask` is the question kind the rules allow; `optional` means a planner may draft instead
    (the batch confirmation gate is never optional).
    """
    conflicts = [c for c in candidates if c["status"] == "date_conflict"]
    pending_rows = [c for c in candidates if c["status"] in {"needs_confirm_char", "needs_confirm_field", "needs_more_evidence", "adjudicate"}]
    accepted = sorted([c for c in candidates if c["status"] == "accept"], key=lambda c: (c["entry_type"] != "SPURIOUS", c["confidence"] != "high"))
    if conflicts:
        return {"top": conflicts[0], "reason": "date_conflict", "label": "CANT_VERIFY"}
    if state["truncated"]:
        return {"top": None, "reason": "too many records share this batch; add clearer product details", "label": "CANT_VERIFY"}
    if pending_rows and (not accepted or any(c["status"] == "needs_confirm_field" for c in pending_rows)):
        top = next((candidate for candidate in pending_rows if candidate["status"] == "needs_confirm_field"), pending_rows[0])
        kind = {"needs_confirm_char": "confirm_char", "needs_confirm_field": "confirm_field", "needs_more_evidence": "box_photo", "adjudicate": "box_photo"}[top["status"]]
        reason = "the candidate needs more printed product, date or manufacturer evidence" if kind == "box_photo" else "the printed characters or dates could not be confirmed"
        allowed = can_ask and kind not in state["declined"] and (not text_mode or kind in {"confirm_field", "box_photo"})
        return {"top": top, "reason": reason, "label": "CANT_VERIFY", "ask": kind if allowed else None, "optional": True}
    if accepted:
        top = accepted[0]
        if state["batch_evidence"] not in GATE_EVIDENCE:
            allowed = can_ask and "confirm_batch" not in state["declined"]
            return {"top": top, "reason": "batch_gate", "label": "CANT_VERIFY", "ask": "confirm_batch" if allowed else None, "optional": False}
        return {"top": top, "reason": "", "label": "SUSPECTED_FAKE" if top["entry_type"] == "SPURIOUS" else "FLAGGED"}
    if pending_rows:
        return {"top": pending_rows[0], "reason": "the available details did not resolve every candidate", "label": "CANT_VERIFY"}
    return {"top": None, "reason": "", "label": "NOT_LISTED"}


def _ask(state, fields, context, kind, top, batch, prior, decision=None):
    """Tool: build the question and log the ask_user step."""
    if kind == "confirm_batch":
        positions = confirmation_positions(batch, prior)
        pending = question("confirm_batch", fields, top, positions)
        items = _prior_items({(batch[p - 1], true) for p in positions if p <= len(batch) for read, true in prior if read == batch[p - 1]}, prior)
        pending = _with_prior(pending, items)
        decision = decision or {"source": "rules", "thought": RULE_THOUGHTS["confirm_batch"], "llm": None}
        _log(state, "ask_user", "Confirm the printed batch before a listed result is shown.", source=decision["source"], thought=decision["thought"], llm_meta=decision.get("llm"),
             prior=_prior_text(items) or None, io={"input": {"candidate": (top or {}).get("batch_key")}, "output": pending})
        return pending
    top = top or {}
    pending = question(kind, fields, top, [sub[0] + 1 for sub in top.get("subs", [])])
    pending["subs"] = top.get("subs", [])
    items = _prior_items({(read, true) for _, read, true in top.get("subs", [])}, prior)
    pending = _with_prior(pending, items)
    decision = decision or {"source": "rules", "thought": RULE_THOUGHTS.get(kind, RULE_THOUGHTS["box_photo"]), "llm": None}
    _log(state, "ask_user", "A printed detail needs your confirmation.", source=decision["source"], thought=decision["thought"], llm_meta=decision.get("llm"),
         prior=_prior_text(items) or None, io={"input": {"candidate": top.get("batch_key"), "status": top.get("status")}, "output": pending})
    return pending


def _tool(name, kinds=None):
    tool = {"name": name, "description": TOOL_SPECS[name]}
    if kinds:
        tool["params"] = {"kind": {"type": "string", "enum": list(kinds), "description": "Question kind."}}
    return tool


def _agent_loop(state, fields, context, index, batch, searched_count, demo, prior, can_ask, text_mode):
    """Investigator agent, planner "agent": the model picks every tool (ReAct), bounded.

    The tools offered each turn come from the rules, so a required search or the
    confirmation gate can never be skipped. Returns {pending} or {top, reason, label, decision}.
    """
    exact = variants = candidates = None
    known = _prior_items({(read, true) for read, true in prior if read in batch}, prior)
    observations, assessed = list(state.get("observations", []))[-4:], {"top": None, "reason": "the check reached its bounded review limit", "label": "CANT_VERIFY"}
    for _ in range(MAX_STEPS):
        if len(state["history"]) >= MAX_STEPS - 2:
            return dict(assessed, label="CANT_VERIFY", reason="the check reached its bounded review limit", decision=None)
        if exact is None:
            tools, rule, key = [_tool("search_exact")], {"tool": "search_exact"}, "search_exact"
        elif variants is None:
            tools, rule, key = [_tool("search_variants")], {"tool": "search_variants"}, "search_variants" if not exact else "search_variants_after_hit"
        elif candidates is None:
            tools, rule, key = [_tool("grade")], {"tool": "grade"}, "grade"
        else:
            assessed = _assess(state, candidates, can_ask, text_mode)
            kind = assessed.get("ask")
            if kind and not assessed.get("optional"):
                tools, rule, key = [_tool("ask_user", [kind])], {"tool": "ask_user", "args": {"kind": kind}}, "confirm_batch"
            elif kind:
                tools, rule, key = [_tool("ask_user", [kind]), _tool("draft_verdict")], {"tool": "ask_user", "args": {"kind": kind}}, kind
                if kind == "box_photo" and _photo_ok(state, context):
                    tools.insert(1, _tool("request_photo", ["carton"]))
            else:
                tools, rule, key = [_tool("draft_verdict")], {"tool": "draft_verdict"}, "draft_verdict"
        top = assessed.get("top") if candidates is not None else None
        evidence = {"batch_read": batch, "batch_source": fields["source"], "batch_evidence": state["batch_evidence"], "records_searched": searched_count,
                    "exact_hits": None if exact is None else len(exact), "variant_hits": None if variants is None else len(variants),
                    "candidate_status": (top or {}).get("status"), "candidate_batch": (top or {}).get("batch_key"),
                    "substitutions": [f"pack {read} vs listed {true}" for _, read, true in (top or {}).get("subs", [])],
                    "questions_left": MAX_ASKS - state["asks"], "declined": list(state["declined"]),
                    "learned_reader_confusions": [f"{read}->{true} x{count}" for read, true, count in known[:6]],
                    "offered_tools": [tool["name"] for tool in tools]}
        decision = _agent_decide(state, evidence, tools, rule, key, observations)
        action = decision["action"]
        if action == "search_exact":
            exact = _do_exact(state, index, batch, searched_count, demo, decision)
            observation = {"exact_hits": len(exact), "batch_keys": [r.get("batch_key") for r in exact[:3]]}
        elif action == "search_variants":
            variants = _do_variants(state, index, batch, prior, known, decision)
            observation = {"variant_hits": len(variants), "batch_keys": [r.get("batch_key") for r in variants[:3]]}
        elif action == "grade":
            candidates = _do_grade(state, fields, exact, variants, decision)
            observation = {"candidates": [{"batch_key": c.get("batch_key"), "status": c.get("status"), "evidence": c.get("evidence")} for c in candidates[:3]]}
        elif action == "ask_user":
            return {"pending": _ask(state, fields, context, decision["args"].get("kind") or rule["args"]["kind"], assessed["top"], batch, prior, decision)}
        elif action == "request_photo":
            return {"pending": _ask_photo(state, fields, decision["args"].get("kind") or "carton", decision)}
        else:
            return dict(assessed, decision=decision)
        observations.append({"tool": action, "args": decision.get("args") or {}, "observation": observation})
        _remember(state, action, decision.get("args") or {}, observation)
    return dict(assessed, label="CANT_VERIFY", reason="the check reached its bounded review limit", decision=None)


def _merge_photo(fields, state, supplied, source, old_key):
    """Merge fields read from a requested photo; a vision reading never becomes gate evidence."""
    changes = {key: str(supplied[key]).strip()[:500] for key in FIELD_NAMES if key != "batch" and supplied.get(key) and not fields.get(key)}
    new_key = batch_key(supplied.get("batch"))
    vision = state.get("vision") or {}
    vision_key = batch_key(vision.get("batch")) if vision.get("status") == "pending" else ""
    state["photos"] = state.get("photos", 0) + 1
    if new_key and new_key not in state["rejected_keys"]:
        if old_key and new_key == old_key and state["provenance"].get("batch") not in {"vlm", None}:
            state["batch_evidence"] = "dual_read"  # two independent text reads of two photos agree (as for a carton photo)
            state["reader_disagreement"] = False
        else:
            changes["batch"] = str(supplied["batch"]).strip()[:40]
            state["batch_evidence"] = source
            state["reader_disagreement"] = bool(old_key and new_key != old_key and new_key != vision_key)
        if vision_key and new_key == vision_key:
            state["vision"] = dict(vision, status="agrees")
        elif vision:
            state["vision"] = None  # read the new photo again if doubt remains
    elif state.get("vision") and state["vision"].get("status") in {"failed", "rejected"}:
        state["vision"] = None
    return changes


def _crop_file(url):
    match = re.fullmatch(r"/api/crops/([A-Za-z0-9_-]{1,100})\.png", str(url or ""))
    return config.DATA_DIR / "crops" / f"{match[1]}.png" if match else None


def _vision_ready(state, context):
    image = str(context.get("vision_image") or "")
    return bool(config.VLM_MODEL) and bool(image) and Path(image).is_file() and state.get("vision_calls", 0) < MAX_VISION_CALLS and not context.get("cabinet")


def _do_vision(state, fields, context, decision):
    """Tool read_with_vision: the batch line (or the downscaled photo) to the local vision model."""
    from core.crops import vision_input
    started = perf_counter()
    state["vision_calls"] = state.get("vision_calls", 0) + 1
    display, crop_in = None, _crop_file(context.get("batch_crop"))
    used_crop = bool(crop_in and crop_in.is_file())
    try:
        image_b64, display = vision_input(context["vision_image"], crop_in if used_crop else None)
        result = llm.vision_read(image_b64, model=config.VLM_MODEL, url=config.OLLAMA_URL, timeout=config.VLM_TIMEOUT)
    except Exception as exc:
        result = {"reading": None, "ms": 0.0, "error": f"image unavailable: {type(exc).__name__}"}
    reading, ocr_key = result.get("reading"), batch_key(fields["batch"])
    if reading and batch_key(reading["batch"]) in state["rejected_keys"]:
        reading, result["error"] = None, "the reading matches a batch the person rejected"
    if reading:
        agrees = bool(ocr_key) and batch_key(reading["batch"]) == ocr_key and not state.get("reader_disagreement")
        status = "agrees" if agrees else "pending"
        summary = (f"The local vision model read the batch as {reading['batch']} (confidence {reading['confidence']:.2f}), "
                   + ("the same as the text reader." if agrees else "which a person must confirm before it is used."))
    else:
        status, summary = "failed", f"The local vision model gave no usable batch reading ({result.get('error') or 'no answer'})."
    crop = f"/api/crops/{Path(display).stem}.png" if display is not None and Path(display).parent == config.DATA_DIR / "crops" else ""
    state["vision"] = dict(reading or {}, status=status, ocr_batch=fields["batch"], crop=crop, model=config.VLM_MODEL)
    if crop and status == "pending":
        context["batch_crop"] = crop
    if status == "agrees":
        state["low_confidence"] = False
    observation = {"vision_batch": (reading or {}).get("batch", ""), "confidence": (reading or {}).get("confidence"), "status": status, "ocr_batch": fields["batch"]}
    _remember(state, "read_with_vision", {}, observation)
    meta = {"model": config.VLM_MODEL, "ms": result.get("ms", 0), "prompt": llm.VISION_PROMPT + " [image omitted]", "response": result.get("raw"), "error": result.get("error", "")}
    _log(state, "read_with_vision", summary, started, source=decision["source"], thought=decision["thought"], llm_meta=meta, agent="perception",
         observation=summary, react_args={"image": "batch line crop" if used_crop else "photo, max 1280 px"},
         io={"input": {"model": config.VLM_MODEL, "timeout": config.VLM_TIMEOUT}, "output": observation}, vision=observation)


def _remember(state, tool, args, observation):
    """Bounded ReAct observations shared by the perception phase and the agent loop."""
    items = state.setdefault("observations", [])
    items.append({"tool": tool, "args": args, "observation": observation})
    del items[:-8]


def _ask_photo(state, fields, photo_kind, decision):
    """Tool request_photo: ask for exactly the missing evidence; the person may decline."""
    pending = question("request_photo", fields, {"photo_kind": photo_kind})
    _log(state, "request_photo", f"Asked for one more photo ({photo_kind.replace('_', ' ')}).", source=decision["source"], thought=decision["thought"],
         llm_meta=decision.get("llm"), react_args={"kind": photo_kind}, observation="Waiting for the photo or a decline.", io={"output": pending})
    return pending


def _photo_ok(state, context):
    """One more photo can be asked for: a photo check, a question left, not asked or declined before."""
    return (bool(context.get("vision_image")) and state["asks"] < MAX_ASKS and state.get("photos", 0) < MAX_PHOTOS
            and "request_photo" not in state["declined"] and not context.get("cabinet"))


def _doubt(state, batch):
    """What is uncertain about the printed batch before any search ("" when nothing)."""
    if state["batch_evidence"] in GATE_EVIDENCE:
        return ""
    if not batch:
        return "missing"
    if state.get("reader_disagreement"):
        return "disagree"
    if state.get("low_confidence"):
        return "low"
    return ""


def _perception(state, fields, context, mode, can_ask):
    """Resolve doubt about the printed batch: vision, confirm the reading, one more photo, or typing.

    Rules decide which tools are allowed; a planner may pick among them. Returns
    ("go", None), ("pending", question) or ("abstain", reason). Bounded.
    """
    for _ in range(MAX_VISION_CALLS + 2):
        batch = batch_key(fields["batch"])
        doubt = _doubt(state, batch)
        if not doubt:
            return "go", None
        vision = state.get("vision") or {}
        status = vision.get("status")
        if doubt == "low" and status in {"agrees", "failed", "confirmed"}:
            return "go", None
        asks_left = MAX_ASKS - state["asks"] if can_ask else 0
        declined = state["declined"]
        options = []
        if not status and _vision_ready(state, context):
            options.append(("read_with_vision", None))
        confirm_ok = status == "pending" and asks_left >= 2 and "confirm_reading" not in declined
        if confirm_ok:
            options.append(("confirm_reading", None))
        if (doubt in {"missing", "disagree"} or status in {"rejected", "pending"}) and asks_left >= 1 and "type_batch" not in declined and not confirm_ok and not (not status and options):
            options.append(("type_batch", None))
        readers_differ = status == "pending" and bool(batch) and batch != batch_key(vision.get("batch"))
        if (readers_differ or (status == "failed" and doubt != "low")) and asks_left >= 2 and context.get("vision_image") \
                and state.get("photos", 0) < MAX_PHOTOS and "request_photo" not in declined:
            options.append(("request_photo", "batch_zoom"))
        if not options:
            if doubt == "low":
                return "go", None
            return "abstain", ("a readable batch number was not provided" if doubt == "missing" else "the images gave different batch readings that could not be resolved")
        names = [name for name, _ in options]
        key = names[0]
        rule = {"action": key, "source": "rules", "thought": RULE_THOUGHTS[key], "llm": None}
        evidence = {"batch_read": batch, "doubt": doubt, "batch_evidence": state["batch_evidence"], "vision_reading": vision.get("batch", ""),
                    "vision_status": status or "not run", "questions_left": asks_left, "declined": list(declined), "offered_tools": names}
        if len(options) < 2 or mode == "rules":
            decision = rule
        elif mode == "agent":
            tools, rule_call = [], {}
            for name, arg in options:
                if name == "read_with_vision":
                    tools.append(_tool("read_with_vision"))
                elif name == "request_photo":
                    tools.append(_tool("request_photo", [arg]))
                elif not any(t["name"] == "ask_user" for t in tools):
                    tools.append(_tool("ask_user", [n for n, _ in options if n in {"confirm_reading", "type_batch"}]))
            first = options[0]
            rule_call = {"tool": "ask_user", "args": {"kind": first[0]}} if first[0] in {"confirm_reading", "type_batch"} else {"tool": first[0], "args": {"kind": first[1]} if first[1] else {}}
            decision = _agent_decide(state, evidence, tools, rule_call, key, list(state.get("observations", [])))
            chosen = decision["action"]
            if chosen == "ask_user":
                chosen = decision.get("args", {}).get("kind") or rule_call.get("args", {}).get("kind")
            decision = dict(decision, action=chosen if chosen in names else key)
        else:
            decision = _decide(state, mode, evidence, names, key, key)
        action = decision["action"] if decision["action"] in names else key
        if action == "read_with_vision":
            _do_vision(state, fields, context, decision)
            continue
        if action == "request_photo":
            return "pending", _ask_photo(state, fields, dict(options)["request_photo"], decision)
        if action == "confirm_reading":
            pending = question("confirm_reading", fields, {"reading": vision.get("batch")})
            pending["ocr_batch"] = fields["batch"]
            _log(state, "ask_user", "Asked whether the vision reading is the printed batch.", source=decision["source"], thought=decision["thought"],
                 llm_meta=decision.get("llm"), react_args={"kind": "confirm_reading"}, observation="Waiting for Yes or No.", io={"output": pending})
            return "pending", pending
        pending = question("type_batch", fields)
        summary = ("The photos gave different batch readings. Enter the printed batch to resolve the difference." if doubt == "disagree" and status != "rejected"
                   else "The printed batch number is needed.")
        _log(state, "ask_user", summary, source=decision["source"], thought=decision["thought"],
             llm_meta=decision.get("llm"), react_args={"kind": "type_batch"}, io={"output": pending})
        return "pending", pending
    return "abstain", "the check reached its bounded review limit"


def _verifier_agent(fields, context, state, label, top, reason, batch, data_available):
    """Verifier agent: render the draft from templates and check every result rule."""
    verification_state = dict(context, **{key: state.get(key) for key in ("candidates", "asks", "provenance", "batch_evidence", "exact_searched", "variants_searched", "truncated")},
                              fields=fields, top=top, grounded_batch=bool(batch and state["provenance"].get("batch") in SOURCES), data_available=data_available, steps=len(state["history"]))
    draft = render_verdict(label, fields, top, context, reason, state["batch_evidence"])
    return verify_verdict(draft, verification_state)


def _revision_options(state, violations, label, top, can_ask):
    """Rules: which single revision could close the verifier's violations."""
    options = []
    if state.get("revisions", 0) < 1 and can_ask and top:
        kind = None
        if any(v.startswith("R2") for v in violations) and label in {"FLAGGED", "SUSPECTED_FAKE"}:
            kind = "confirm_batch" if state["batch_evidence"] not in GATE_EVIDENCE else "box_photo"
        elif any(v.startswith("R8") for v in violations):
            kind = "box_photo"
        if kind and kind not in state["declined"]:
            options.append(("ask_user", kind))
    options.append(("downgrade", None))
    return options


def _reflect(state, mode, fields, context, final, label, top, batch, prior):
    """Self-correction: one bounded revision after a verifier send-back; returns a question or None."""
    violations = list(final.get("verification") or [])
    _handoff(state, "verifier", "investigator", "send_back", f"The draft failed {len(violations)} result rule(s); revise once or abstain.", {"violations": violations})
    can_ask = state["asks"] < MAX_ASKS and len(state["history"]) < MAX_STEPS - 4 and not context.get("cabinet")
    options = _revision_options(state, violations, label, top, can_ask)
    names = [name for name, _ in options]
    kind = options[0][1]
    rule = {"action": names[0], "source": "rules", "thought": RULE_THOUGHTS["reflect_ask" if names[0] == "ask_user" else "reflect_downgrade"], "llm": None}
    evidence = {"draft_label": label, "violations": violations, "questions_left": MAX_ASKS - state["asks"], "revisions_left": 1 - state.get("revisions", 0), "options": names}
    if len(options) < 2:
        decision = rule
    elif mode == "agent":
        decision = _agent_decide(state, evidence, [_tool("ask_user", [kind]), _tool("downgrade")], {"tool": "ask_user", "args": {"kind": kind}}, "reflect", [])
    else:
        decision = _decide(state, mode, evidence, names, names[0], "reflect")
    action = decision["action"] if decision["action"] in names else names[-1]
    _log(state, "reflect", f"The verifier found {len(violations)} problem(s) in the draft; decision: {'ask one more question' if action == 'ask_user' else 'abstain'}.",
         source=decision["source"], thought=decision["thought"], llm_meta=decision.get("llm"), violations=violations, decision=action,
         io={"input": {"violations": violations, "options": names}, "output": {"decision": action}})
    if action == "ask_user":
        state["revisions"] = state.get("revisions", 0) + 1
        return _ask(state, fields, context, kind, top, batch, prior, decision)
    return None


def investigate(fields, alerts, context=None, answer=None, observer=None):
    """Run or resume a check. All external input is data.

    The only optional network call is the local Ollama planner at branch points
    (planner "hybrid"/"llm"); it is bounded and falls back to the rules.
    `observer(event, data)` receives live "step" and "thinking" events; it is never stored.
    """
    call_start = _now_ns()
    context = deepcopy(context or {})
    prior = prior_counts(context.get("confusion_counts", [])[:1000]) if not context.get("demo") else {}
    fields = _fields(fields or {})
    mode = str(context.get("planner") or config.PLANNER).strip().lower()
    mode = mode if mode in {"rules", "hybrid", "llm", "agent"} else "rules"
    state = context.get("_engine")
    if state:
        state["_call"], state["_marks"], state["_observer"] = {"start_ns": call_start, "answer": answer}, [], observer
    if not state:
        source = fields["source"]
        evidence = "user_typed" if source == "user" else "qr" if source == "qr" else "user_confirmed" if fields["confirmed"] else source
        if context.get("cabinet"):
            evidence = context.get("batch_evidence", evidence)
        state = {"history": [], "asks": 0, "fields_version": 1, "declined": [], "rejected_keys": [], "confirmed_keys": [], "confirmed_substitutions": [], "conflict_ids": [], "batch_evidence": evidence if fields["batch"] else "none", "provenance": {key: source for key in FIELD_NAMES if fields[key]}, "candidates": [], "pending": None}
        if context.get("reader_disagreement"):
            state["reader_disagreement"] = True
            state["batch_evidence"] = "none"
            fields["confirmed"] = False
        state["low_confidence"] = bool(context.get("batch_low_confidence")) and state["batch_evidence"] not in GATE_EVIDENCE
        state["session"] = str(context.get("thread_id") or uuid.uuid4().hex)
        state["_call"], state["_marks"], state["_observer"] = {"start_ns": call_start, "answer": None}, [], observer
        state["planner"] = mode
        if context.get("cabinet"):
            _handoff(state, "supervisor", "investigator", "recheck", "A saved pack is rechecked against the updated alert lists.", {"batch_evidence": state["batch_evidence"]})
        _log(state, "extract_fields", "Using the printed details supplied for this check.",
             io={"input": {"source": fields["source"], "confirmed": fields["confirmed"]}, "output": {k: fields[k] for k in FIELD_NAMES if fields[k]}})
        _handoff(state, "perception", "investigator", "fields", "The printed fields are ready with their provenance.",
                 {"fields": [k for k in FIELD_NAMES if fields[k]], "source": fields["source"]})
    state["planner"] = mode
    if context.get("llm_model"):
        state["llm_model"] = str(context["llm_model"])[:100]
    if state.get("pending"):
        if answer is None:
            return _snapshot(fields, context, state, state["pending"])
        error = _apply_answer(fields, state, answer)
        if error:
            pending = dict(state["pending"], error=error)
            return _snapshot(fields, context, state, pending)
        if context.get("reader_disagreement") and answer.get("source") == "carton":
            state["reader_disagreement"] = True
            state["batch_evidence"] = "none"
            fields["confirmed"] = False
        if answer.get("image") and state["batch_evidence"] not in GATE_EVIDENCE:
            state["low_confidence"] = bool(context.get("batch_low_confidence"))
    rows = _rows(alerts, bool(context.get("demo")))
    months = sorted({str(row.get("list_month")) for row in rows if row.get("list_month")})
    context.setdefault("latest_month", months[-1] if months else None)
    context.setdefault("list_count", len({(row.get("list_month"), row.get("source_url") or row.get("source_title"), row.get("entry_type")) for row in rows}))
    subset_coverage = bool(context.get("candidate_subset") and not context.get("demo")
                           and context.get("real_alert_count", 0) > 0 and context.get("latest_month") and context.get("list_count", 0) > 0)
    data_available = subset_coverage or bool(rows) and (bool(context.get("demo")) or context.get("real_alert_count", len(rows)) > 0)
    batch = batch_key(fields["batch"])
    reason, label, top, draft_decision = "", "CANT_VERIFY", None, None
    can_ask = state["asks"] < MAX_ASKS and len(state["history"]) < MAX_STEPS - 4 and not context.get("cabinet")
    text_mode = fields["source"] == "user" and context.get("mode", "text") == "text"
    step, value = _perception(state, fields, context, mode, can_ask) if data_available and not (batch and (len(batch) < 2 or len(fields["batch"]) > 40)) else ("go", None)
    if step == "pending":
        return _snapshot(fields, context, state, value)
    batch = batch_key(fields["batch"])
    if not data_available:
        reason = "no_data"
    elif step == "abstain":
        reason = value
    elif len(batch) < 2 or len(fields["batch"]) > 40:
        reason = "the printed batch number is incomplete or exceeds the supported length"
    elif any(fields[key] and _date(fields[key]) is None for key in ("mfg", "exp")):
        reason = "a printed date could not be read as a month and year; check the entered dates"
    elif len(state["history"]) >= MAX_STEPS - 3:
        reason = "the check reached its bounded review limit"
    else:
        index = build_index(rows)
        searched_count = context.get("real_alert_count", len(rows)) if subset_coverage else len(rows)
        demo = bool(context.get("demo"))
        known = []
        if mode == "agent":
            outcome_state = _agent_loop(state, fields, context, index, batch, searched_count, demo, prior, can_ask, text_mode)
            if outcome_state.get("pending"):
                return _snapshot(fields, context, state, outcome_state["pending"])
            top, reason, label, draft_decision = outcome_state["top"], outcome_state["reason"], outcome_state["label"], outcome_state.get("decision")
        else:
            exact = _do_exact(state, index, batch, searched_count, demo)
            known = _prior_items({(read, true) for read, true in prior if read in batch}, prior)
            if exact:
                decision = {"action": "search_variants", "source": "rules", "thought": RULE_THOUGHTS["search_variants_after_hit"], "llm": None}
            else:
                # Branch point (b): a search returned nothing.
                evidence = {"batch_read": batch, "batch_source": fields["source"], "exact_hits": 0, "records_searched": searched_count,
                            "learned_reader_confusions": [f"{read}->{true} x{count}" for read, true, count in known[:6]]}
                decision = _decide(state, mode, evidence, ["search_variants", "draft_verdict"], "search_variants", "search_variants")
            variant_source, variant_thought, variant_llm = decision["source"], decision["thought"], decision["llm"]
            if decision["action"] == "draft_verdict":
                # Branch point (d): the verifier sends the draft back once; NOT LISTED needs the variant search (R4).
                _log(state, "plan", "The planner proposed a result before the look-alike search.", source=decision["source"], thought=decision["thought"], llm_meta=decision["llm"], io={"output": {"action": "draft_verdict"}})
                _log(state, "verify", "The verifier sent the draft back: a not-listed result needs the bounded look-alike search first.", source="rules",
                     thought="Rule R4: exact and variant searches must both run before a NOT LISTED result.", io={"output": {"violations": ["R4: a complete, grounded search is required"]}})
                variant_source, variant_thought, variant_llm = "rules(verifier)", "Re-planned after the verifier send-back: search bounded look-alike alternatives.", None
            variants = _do_variants(state, index, batch, prior, known, {"source": variant_source, "thought": variant_thought, "llm": variant_llm})
            candidates = _do_grade(state, fields, exact, variants)
            assessed = _assess(state, candidates, can_ask, text_mode)
            top, reason, label = assessed["top"], assessed["reason"], assessed["label"]
            kind = assessed.get("ask")
            if assessed.get("optional"):
                decision = {"action": "draft_verdict", "source": "rules", "thought": RULE_THOUGHTS["draft_verdict"], "llm": None}
                if kind:
                    # Branch point (c): grading left a candidate that needs a person or more evidence.
                    evidence = {"batch_read": batch, "batch_source": fields["source"], "candidate_status": top["status"], "candidate_batch": top.get("batch_key"),
                                "substitutions": [f"pack {read} vs listed {true}" for _, read, true in top.get("subs", [])],
                                "evidence": top.get("evidence"), "questions_left": MAX_ASKS - state["asks"],
                                "learned_reader_confusions": [f"{read}->{true} x{count}" for read, true, count in _prior_items({(r, t) for _, r, t in top.get("subs", [])}, prior)]}
                    allowed = ["ask_user", "draft_verdict"] + (["request_photo"] if kind == "box_photo" and _photo_ok(state, context) else [])
                    decision = _decide(state, mode, evidence, allowed, "ask_user", kind)
                if decision["action"] == "request_photo":
                    return _snapshot(fields, context, state, _ask_photo(state, fields, "carton", decision))
                if decision["action"] == "ask_user":
                    return _snapshot(fields, context, state, _ask(state, fields, context, kind, top, batch, prior, decision))
                draft_decision = decision
            elif kind:
                return _snapshot(fields, context, state, _ask(state, fields, context, kind, top, batch, prior))
    outcome = ("A corroborated entry matches the confirmed batch; draft the listed result with its citation." if label in {"FLAGGED", "SUSPECTED_FAKE"}
               else "No candidate survived exact and look-alike search and grading; draft a result limited to the lists loaded." if label == "NOT_LISTED"
               else f"The evidence stays incomplete ({reason or 'unresolved'}); abstain instead of guessing.")
    decision = draft_decision or {"source": "rules", "thought": outcome, "llm": None}
    _log(state, "draft_verdict", "Prepared the evidence-based result and checked the result rules.", source=decision["source"], thought=decision["thought"], llm_meta=decision["llm"])
    draft_index = len(state["history"]) - 1 if state["history"] and state["history"][-1]["action"] == "draft_verdict" else None
    draft_mark = state["_marks"][-1] if draft_index is not None and state.get("_marks") and state["_marks"][-1]["i"] == draft_index else None
    _handoff(state, "investigator", "verifier", "draft", "The draft result is ready for the result rules.", {"label": label, "reason": reason})
    final = _verifier_agent(fields, context, state, label, top, reason, batch, data_available)
    if draft_index is not None:
        verdict = final.get("verification") or "approved"
        state["history"][draft_index]["verifier"] = verdict
        if draft_mark is not None:
            draft_mark["io"] = {"input": {"label": label, "reason": reason, "top": (top or {}).get("id")}, "output": {"label": final.get("label"), "headline": final.get("headline"), "citations": final.get("citations"), "verifier": verdict}}
    if final.get("verification"):
        # Self-correction: the verifier sends the draft back once with its violations.
        pending = _reflect(state, mode, fields, context, final, label, top, batch, prior)
        if pending:
            return _snapshot(fields, context, state, pending)
    return _snapshot(fields, context, state, final=final)

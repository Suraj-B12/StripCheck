"""Offline, bounded investigation with JSON-serializable pause/resume state."""

from copy import deepcopy
from datetime import date
import re
from time import perf_counter, perf_counter_ns, time_ns
import uuid

from core import config, llm, tracing
from core.matching import build_index, grade, search_exact, search_variants
from core.noisy import confirmation_positions, prior_counts
from core.templates import prior_note, question, render_verdict
from core.textutils import PLACEHOLDERS, batch_key, maker_name, parse_month_year
from core.verifier import GATE_EVIDENCE, verify_verdict

MAX_STEPS, MAX_ASKS, MAX_CANDIDATES = 16, 2, 20
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
    fields["product"] = fields["product"] or str(raw.get("product_text") or "")[:500]
    fields["source"] = raw.get("source", "user") if raw.get("source", "user") in SOURCES else "unknown"
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
}


def _log(state, action, summary, started=None, source="rules", thought=None, io=None, llm_meta=None, **extra):
    if len(state["history"]) >= MAX_STEPS:
        return
    entry = {"step": len(state["history"]) + 1, "action": action, "source": source, "summary": summary, "ms": round((perf_counter() - started) * 1000, 2) if started else 0}
    if thought:
        entry["thought"] = thought
    entry.update({key: value for key, value in extra.items() if value is not None})
    state["history"].append(entry)
    state.setdefault("_marks", []).append({"i": len(state["history"]) - 1, "end_ns": _now_ns(), "io": io or {}, "llm": llm_meta})


def _decide(state, mode, evidence, allowed, suggestion, thought_key):
    """Branch-point planner: the LLM in hybrid/llm mode, otherwise the rules."""
    decision = llm.plan_decision(evidence, allowed, suggestion, RULE_THOUGHTS[thought_key], mode=mode,
                                 model=state.get("llm_model") or config.LLM_MODEL, url=config.OLLAMA_URL, timeout=config.LLM_TIMEOUT)
    state.setdefault("decisions", []).append({"step": len(state["history"]) + 1, "action": decision["action"], "source": decision["source"]})
    return decision


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
    """Turn this call's history entries into nested planner/tool/LLM spans."""
    steps, previous_end = [], 0
    for mark in marks:
        entry = history[mark["i"]]
        end = max(mark["end_ns"], previous_end)
        tool_start = max(end - int(float(entry.get("ms") or 0) * 1e6), previous_end)
        kind = "TOOL" if entry["action"] in TOOL_ACTIONS else "CHAIN"
        tool = {"name": entry["action"], "kind": kind, "start_ns": tool_start, "end_ns": end,
                "input": mark["io"].get("input"), "output": mark["io"].get("output", entry.get("summary")),
                "attributes": {"stripcheck.step": entry["step"], "stripcheck.summary": entry.get("summary", "")}, "children": []}
        if entry["action"] == "draft_verdict" and entry.get("verifier"):
            tool["children"].append({"name": "verifier", "kind": "GUARDRAIL", "start_ns": tool_start, "end_ns": end,
                                     "input": mark["io"].get("output"), "output": entry["verifier"]})
        children, start = [], tool_start
        meta = mark.get("llm")
        if meta:
            start = max(tool_start - int(float(meta.get("ms") or 0) * 1e6), previous_end)
            children.append({"name": "planner_llm", "kind": "LLM", "start_ns": start, "end_ns": tool_start,
                             "input": meta.get("prompt"), "output": meta.get("response") or meta.get("error"),
                             "attributes": {"llm.model_name": meta.get("model", ""), "llm.invocation_parameters": '{"temperature": 0}'}})
        children.append(tool)
        steps.append({"name": f"planner: {entry['action']}", "kind": "CHAIN", "start_ns": start, "end_ns": end,
                      "input": {"step": entry["step"], "source": entry.get("source")},
                      "output": {"action": entry["action"], "thought": entry.get("thought", "")},
                      "attributes": {"stripcheck.source": entry.get("source", ""), "stripcheck.thought": entry.get("thought", ""), "stripcheck.prior": entry.get("prior", "")},
                      "children": children})
        previous_end = end
    return steps


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
    skip = bool(answer.get("skip")) or choice.lower() in {"cant_tell", "can't tell", "cannot tell", "skip"}
    changes = {}
    old_key = batch_key(fields["batch"])
    if skip:
        state["declined"].append(kind)
        if kind == "confirm_field":
            state["conflict_ids"].append(pending.get("entry_id"))
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


def investigate(fields, alerts, context=None, answer=None):
    """Run or resume a check. All external input is data.

    The only optional network call is the local Ollama planner at branch points
    (planner "hybrid"/"llm"); it is bounded and falls back to the rules.
    """
    call_start = _now_ns()
    context = deepcopy(context or {})
    prior = prior_counts(context.get("confusion_counts", [])[:1000]) if not context.get("demo") else {}
    fields = _fields(fields or {})
    mode = str(context.get("planner") or config.PLANNER).strip().lower()
    mode = mode if mode in {"rules", "hybrid", "llm"} else "rules"
    state = context.get("_engine")
    if state:
        state["_call"], state["_marks"] = {"start_ns": call_start, "answer": answer}, []
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
        state["session"] = str(context.get("thread_id") or uuid.uuid4().hex)
        state["_call"], state["_marks"] = {"start_ns": call_start, "answer": None}, []
        _log(state, "extract_fields", "Using the printed details supplied for this check.",
             io={"input": {"source": fields["source"], "confirmed": fields["confirmed"]}, "output": {k: fields[k] for k in FIELD_NAMES if fields[k]}})
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
    if not data_available:
        reason = "no_data"
    elif not batch:
        if can_ask and "type_batch" not in state["declined"]:
            pending = question("type_batch", fields)
            _log(state, "ask_user", "The printed batch number is needed.", thought=RULE_THOUGHTS["type_batch"], io={"output": pending})
            return _snapshot(fields, context, state, pending)
        reason = "a readable batch number was not provided"
    elif len(batch) < 2 or len(fields["batch"]) > 40:
        reason = "the printed batch number is incomplete or exceeds the supported length"
    elif state.get("reader_disagreement"):
        if can_ask and "type_batch" not in state["declined"]:
            pending = question("type_batch", fields)
            _log(state, "ask_user", "The photos gave different batch readings. Enter the printed batch to resolve the difference.", thought=RULE_THOUGHTS["type_batch"], io={"output": pending})
            return _snapshot(fields, context, state, pending)
        reason = "the images gave different batch readings that could not be resolved"
    elif any(fields[key] and _date(fields[key]) is None for key in ("mfg", "exp")):
        reason = "a printed date could not be read as a month and year; check the entered dates"
    elif len(state["history"]) >= MAX_STEPS - 3:
        reason = "the check reached its bounded review limit"
    else:
        started = perf_counter()
        index = build_index(rows)
        exact = search_exact(index, batch, max_hits=MAX_CANDIDATES + 1)
        state["exact_searched"] = True
        searched_count = context.get("real_alert_count", len(rows)) if subset_coverage else len(rows)
        _log(state, "search_exact", f"Checked the exact batch against {searched_count:,} {'synthetic' if context.get('demo') else 'loaded'} records; {len(exact)} candidate(s).", started,
             io={"input": {"batch_key": batch, "records": searched_count}, "output": [{"id": r.get("id"), "batch_key": r.get("batch_key"), "entry_type": r.get("entry_type")} for r in exact[:5]]})
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
        started = perf_counter()
        variants = search_variants(index, batch, prior=prior, max_subs=2, max_lookups=2000, max_hits=MAX_CANDIDATES + 1)
        state["variants_searched"] = True
        prior_suffix = ""
        used_priors = sorted({(read, true, prior.get((read, true), 0)) for candidate in variants for _, read, true in candidate.get("subs", []) if prior.get((read, true), 0)})
        if used_priors:
            prior_suffix = " Prior confirmed corrections: " + "; ".join(f"{read} to {true}: {count}" for read, true, count in used_priors[:6]) + ". Confirmation is still required."
        _log(state, "search_variants", f"Checked bounded character alternatives; {len(variants)} candidate(s). No printed character was changed." + prior_suffix, started,
             source=variant_source, thought=variant_thought, llm_meta=variant_llm, prior=_prior_text(used_priors) or None,
             io={"input": {"batch_key": batch, "max_subs": 2, "prior": [f"{read}->{true} x{count}" for read, true, count in known[:6]]},
                 "output": [{"id": r.get("id"), "batch_key": r.get("batch_key"), "subs": r.get("subs"), "entry_type": r.get("entry_type")} for r in variants[:5]]})
        unique = {}
        for row in exact + variants:
            if row["id"] not in unique:
                unique[row["id"]] = row
        state["truncated"] = len(unique) > MAX_CANDIDATES or len(exact) > MAX_CANDIDATES or len(variants) > MAX_CANDIDATES
        grading_fields = dict(fields, product_text=f"{fields['product']} {fields['brand']}", mfg=_date(fields["mfg"]), exp=_date(fields["exp"]))
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
             io={"input": {k: grading_fields.get(k) for k in ("batch", "product", "brand", "mfg", "exp", "maker")},
                 "output": [{"id": c.get("id"), "batch_key": c.get("batch_key"), "status": c.get("status"), "evidence": c.get("evidence")} for c in candidates[:5]]})
        conflicts = [c for c in candidates if c["status"] == "date_conflict"]
        pending_rows = [c for c in candidates if c["status"] in {"needs_confirm_char", "needs_confirm_field", "needs_more_evidence", "adjudicate"}]
        accepted = sorted([c for c in candidates if c["status"] == "accept"], key=lambda c: (c["entry_type"] != "SPURIOUS", c["confidence"] != "high"))
        if conflicts:
            top, reason = conflicts[0], "date_conflict"
        elif state["truncated"]:
            reason = "too many records share this batch; add clearer product details"
        elif pending_rows and (not accepted or any(c["status"] == "needs_confirm_field" for c in pending_rows)):
            top = next((candidate for candidate in pending_rows if candidate["status"] == "needs_confirm_field"), pending_rows[0])
            kind = {"needs_confirm_char": "confirm_char", "needs_confirm_field": "confirm_field", "needs_more_evidence": "box_photo", "adjudicate": "box_photo"}[top["status"]]
            decision = {"action": "draft_verdict", "source": "rules", "thought": RULE_THOUGHTS["draft_verdict"], "llm": None}
            if can_ask and kind not in state["declined"] and (not text_mode or kind in {"confirm_field", "box_photo"}):
                # Branch point (c): grading left a candidate that needs a person or more evidence.
                evidence = {"batch_read": batch, "batch_source": fields["source"], "candidate_status": top["status"], "candidate_batch": top.get("batch_key"),
                            "substitutions": [f"pack {read} vs listed {true}" for _, read, true in top.get("subs", [])],
                            "evidence": top.get("evidence"), "questions_left": MAX_ASKS - state["asks"],
                            "learned_reader_confusions": [f"{read}->{true} x{count}" for read, true, count in _prior_items({(r, t) for _, r, t in top.get("subs", [])}, prior)]}
                decision = _decide(state, mode, evidence, ["ask_user", "draft_verdict"], "ask_user", kind)
            if decision["action"] == "ask_user":
                pending = question(kind, fields, top, [sub[0] + 1 for sub in top.get("subs", [])])
                pending["subs"] = top.get("subs", [])
                items = _prior_items({(read, true) for _, read, true in top.get("subs", [])}, prior)
                pending = _with_prior(pending, items)
                _log(state, "ask_user", "A printed detail needs your confirmation.", source=decision["source"], thought=decision["thought"], llm_meta=decision["llm"],
                     prior=_prior_text(items) or None, io={"input": {"candidate": top.get("batch_key"), "status": top["status"]}, "output": pending})
                return _snapshot(fields, context, state, pending)
            reason = "the candidate needs more printed product, date or manufacturer evidence" if kind == "box_photo" else "the printed characters or dates could not be confirmed"
            draft_decision = decision
        elif accepted:
            top = accepted[0]
            if state["batch_evidence"] not in GATE_EVIDENCE:
                if can_ask and "confirm_batch" not in state["declined"]:
                    positions = confirmation_positions(batch, prior)
                    pending = question("confirm_batch", fields, top, positions)
                    items = _prior_items({(batch[p - 1], true) for p in positions if p <= len(batch) for read, true in prior if read == batch[p - 1]}, prior)
                    pending = _with_prior(pending, items)
                    _log(state, "ask_user", "Confirm the printed batch before a listed result is shown.", thought=RULE_THOUGHTS["confirm_batch"],
                         prior=_prior_text(items) or None, io={"input": {"candidate": top.get("batch_key")}, "output": pending})
                    return _snapshot(fields, context, state, pending)
                reason = "batch_gate"
            else:
                label = "SUSPECTED_FAKE" if top["entry_type"] == "SPURIOUS" else "FLAGGED"
        elif pending_rows:
            top, reason = pending_rows[0], "the available details did not resolve every candidate"
        else:
            label = "NOT_LISTED"
    outcome = ("A corroborated entry matches the confirmed batch; draft the listed result with its citation." if label in {"FLAGGED", "SUSPECTED_FAKE"}
               else "No candidate survived exact and look-alike search and grading; draft a result limited to the lists loaded." if label == "NOT_LISTED"
               else f"The evidence stays incomplete ({reason or 'unresolved'}); abstain instead of guessing.")
    decision = draft_decision or {"source": "rules", "thought": outcome, "llm": None}
    _log(state, "draft_verdict", "Prepared the evidence-based result and checked the result rules.", source=decision["source"], thought=decision["thought"], llm_meta=decision["llm"])
    logged = bool(state["history"]) and state["history"][-1]["action"] == "draft_verdict"
    verification_state = dict(context, **{key: state.get(key) for key in ("candidates", "asks", "provenance", "batch_evidence", "exact_searched", "variants_searched", "truncated")}, fields=fields, top=top, grounded_batch=bool(batch and state["provenance"].get("batch") in SOURCES), data_available=data_available, steps=len(state["history"]))
    draft = render_verdict(label, fields, top, context, reason, state["batch_evidence"])
    final = verify_verdict(draft, verification_state)
    if logged and state.get("_marks") and state["_marks"][-1]["i"] == len(state["history"]) - 1:
        verdict = final.get("verification") or "approved"
        state["history"][-1]["verifier"] = verdict
        state["_marks"][-1]["io"] = {"input": {"label": label, "reason": reason, "top": (top or {}).get("id")}, "output": {"label": final.get("label"), "headline": final.get("headline"), "citations": final.get("citations"), "verifier": verdict}}
    return _snapshot(fields, context, state, final=final)

"""Offline, bounded investigation with JSON-serializable pause/resume state."""

from copy import deepcopy
from datetime import date
import re
from time import perf_counter

from core.matching import build_index, grade, search_exact, search_variants
from core.noisy import confirmation_positions, prior_counts
from core.templates import question, render_verdict
from core.textutils import PLACEHOLDERS, batch_key, maker_name, parse_month_year
from core.verifier import GATE_EVIDENCE, verify_verdict

MAX_STEPS, MAX_ASKS, MAX_CANDIDATES = 16, 2, 20
FIELD_NAMES = ("batch", "product", "brand", "mfg", "exp", "maker")
SOURCES = {"user", "ocr", "qr", "ocr_enh", "carton", "vlm"}


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


def _log(state, action, summary, started=None):
    if len(state["history"]) >= MAX_STEPS:
        return
    state["history"].append({"step": len(state["history"]) + 1, "action": action, "source": "rules", "summary": summary, "ms": round((perf_counter() - started) * 1000, 2) if started else 0})


def _strip(fields, state, pending=None):
    key = batch_key(fields.get("batch"))
    positions = set((pending or {}).get("positions", []))
    confirmed = state.get("batch_evidence") in GATE_EVIDENCE
    return {"source": state.get("batch_evidence", "none"), "chars": [{"ch": char, "state": "uncertain" if i + 1 in positions else "confirmed" if confirmed else "read", "alts": [sub[2] for sub in (pending or {}).get("subs", []) if sub[0] == i]} for i, char in enumerate(key)]}


def _snapshot(fields, context, state, pending=None, final=None):
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
    _log(state, "answer", "Printed details updated by the user." if changes else "The user's answer was recorded.")
    state["pending"] = None
    return None


def investigate(fields, alerts, context=None, answer=None):
    """Run or resume a check. All external input is data; no network calls occur."""
    context = deepcopy(context or {})
    prior = prior_counts(context.get("confusion_counts", [])[:1000]) if not context.get("demo") else {}
    fields = _fields(fields or {})
    state = context.get("_engine")
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
        _log(state, "extract_fields", "Using the printed details supplied for this check.")
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
    reason, label, top = "", "CANT_VERIFY", None
    can_ask = state["asks"] < MAX_ASKS and len(state["history"]) < MAX_STEPS - 4 and not context.get("cabinet")
    text_mode = fields["source"] == "user" and context.get("mode", "text") == "text"
    if not data_available:
        reason = "no_data"
    elif not batch:
        if can_ask and "type_batch" not in state["declined"]:
            pending = question("type_batch", fields)
            _log(state, "ask_user", "The printed batch number is needed.")
            return _snapshot(fields, context, state, pending)
        reason = "a readable batch number was not provided"
    elif len(batch) < 2 or len(fields["batch"]) > 40:
        reason = "the printed batch number is incomplete or exceeds the supported length"
    elif state.get("reader_disagreement"):
        if can_ask and "type_batch" not in state["declined"]:
            pending = question("type_batch", fields)
            _log(state, "ask_user", "The photos gave different batch readings. Enter the printed batch to resolve the difference.")
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
        _log(state, "search_exact", f"Checked the exact batch against {searched_count:,} {'synthetic' if context.get('demo') else 'loaded'} records; {len(exact)} candidate(s).", started)
        started = perf_counter()
        variants = search_variants(index, batch, prior=prior, max_subs=2, max_lookups=2000, max_hits=MAX_CANDIDATES + 1)
        state["variants_searched"] = True
        prior_note = ""
        used_priors = sorted({(read, true, prior.get((read, true), 0)) for candidate in variants for _, read, true in candidate.get("subs", []) if prior.get((read, true), 0)})
        if used_priors:
            prior_note = " Prior confirmed corrections: " + "; ".join(f"{read} to {true}: {count}" for read, true, count in used_priors[:6]) + ". Confirmation is still required."
        _log(state, "search_variants", f"Checked bounded character alternatives; {len(variants)} candidate(s). No printed character was changed." + prior_note, started)
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
        _log(state, "grade", "Compared product, brand, dates and manufacturer for every candidate.")
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
            if can_ask and kind not in state["declined"] and (not text_mode or kind in {"confirm_field", "box_photo"}):
                pending = question(kind, fields, top, [sub[0] + 1 for sub in top.get("subs", [])])
                pending["subs"] = top.get("subs", [])
                _log(state, "ask_user", "A printed detail needs your confirmation.")
                return _snapshot(fields, context, state, pending)
            reason = "the candidate needs more printed product, date or manufacturer evidence" if kind == "box_photo" else "the printed characters or dates could not be confirmed"
        elif accepted:
            top = accepted[0]
            if state["batch_evidence"] not in GATE_EVIDENCE:
                if can_ask and "confirm_batch" not in state["declined"]:
                    pending = question("confirm_batch", fields, top, confirmation_positions(batch, prior))
                    _log(state, "ask_user", "Confirm the printed batch before a listed result is shown.")
                    return _snapshot(fields, context, state, pending)
                reason = "batch_gate"
            else:
                label = "SUSPECTED_FAKE" if top["entry_type"] == "SPURIOUS" else "FLAGGED"
        elif pending_rows:
            top, reason = pending_rows[0], "the available details did not resolve every candidate"
        else:
            label = "NOT_LISTED"
    _log(state, "draft_verdict", "Prepared the evidence-based result and checked the result rules.")
    verification_state = dict(context, **{key: state.get(key) for key in ("candidates", "asks", "provenance", "batch_evidence", "exact_searched", "variants_searched", "truncated")}, fields=fields, top=top, grounded_batch=bool(batch and state["provenance"].get("batch") in SOURCES), data_available=data_available, steps=len(state["history"]))
    final = render_verdict(label, fields, top, context, reason, state["batch_evidence"])
    final = verify_verdict(final, verification_state)
    return _snapshot(fields, context, state, final=final)

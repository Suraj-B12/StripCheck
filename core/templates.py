"""All result and question copy. Models never author these messages."""

import re
from urllib.parse import urlsplit

LABELS = {"FLAGGED", "SUSPECTED_FAKE", "NOT_LISTED", "CANT_VERIFY"}
BANNED = re.compile(r"\bsafe\b|\bgenuine\b|\bauthentic\b|\bfake medicine\b|\bstop (?:taking|using)\b|सुरक्षित|असली|बंद करें", re.I)
# Model thoughts only: reassurance or advice about the medicine (treated like a BANNED hit).
REASSURE = re.compile(r"\b(?:fine|ok(?:ay)?|harmless|fit|good) (?:to|for) (?:use|take|taking|consume|eat)\b|\bharmless\b|\bno (?:risk|problem|danger)\b|\bnothing to worry\b|\bnot (?:dangerous|harmful)\b", re.I)
# Trailing words that may start a BANNED or REASSURE phrase: held back from live text until the next word arrives.
HOLD_TAIL = re.compile(r"(?:\s*\b(?:stop|fake|fine|ok|okay|fit|good|no|nothing|not)\b(?:\s+(?:to|for))?|\s*बंद)\s*$", re.I)
ADVICE = "Show this pack to your pharmacist. Do not stop any prescribed medicine without medical advice."


def clean_text(value):
    return BANNED.sub("[word omitted]", str(value or "").strip())[:1000]


def month_name(value):
    months = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
    match = re.fullmatch(r"(\d{4})-(\d{2})", str(value or ""))
    if match and 1 <= int(match[2]) <= 12:
        return f"{months[int(match[2]) - 1]} {match[1]}"
    return clean_text(value) or "unknown"


def citation(entry, demo=False):
    url = str(entry.get("source_url") or "")
    if urlsplit(url).scheme not in {"http", "https"}:
        url = ""
    title = clean_text(entry.get("source_title")) or ("Synthetic demonstration fixture" if demo else "Stored CDSCO alert")
    month = entry.get("list_month", "")
    row = entry.get("row_no", "")
    result = clean_text(entry.get("result"))
    return {
        "id": entry.get("id"), "title": title, "source_title": title,
        "url": url, "source_url": url, "list_month": month,
        "row_no": row, "page": entry.get("page"), "result": result,
        "entry_type": entry.get("entry_type"),
        "source_sha256": entry.get("source_sha256", ""), "synthetic": bool(demo),
        "text": f"{title} · {month_name(month)} · row {row or 'not specified'}" + (f" · reported: {result}" if result else ""),
    }


def render_verdict(label, fields, entry=None, context=None, reason="", batch_evidence="none"):
    context, entry = context or {}, entry or {}
    label = label if label in LABELS else "CANT_VERIFY"
    demo = bool(context.get("demo"))
    month = month_name(entry.get("list_month") or context.get("latest_month"))
    citations = [citation(entry, demo)] if entry else []
    advice = ADVICE
    if label == "FLAGGED":
        headline = "This batch is on an alert list"
        if demo:
            explanation = "This batch matches a synthetic demonstration alert for a failed quality test. This is an example result, not a check against real CDSCO records."
        else:
            result = clean_text(entry.get("result")) or "see the cited record"
            reporter = clean_text(entry.get("reported_by")) or "the cited reporting laboratory"
            level = clean_text(entry.get("source_level"))
            explanation = f"This batch appears on CDSCO's {month} {level + ' ' if level else ''}list of drugs found Not of Standard Quality (failed test: {result}; reported by {reporter})."
    elif label == "SUSPECTED_FAKE":
        headline = "This batch is listed as purported spurious"
        if demo:
            explanation = "This batch matches a synthetic demonstration entry marked purported spurious. This is an example result, not a check against real CDSCO records."
        else:
            firm_reply = str(entry.get("firm_reply", entry.get("str_firm_reply", ""))).lower()
            under_investigation = "under investigation" in str(entry.get("maker_name", "")).lower()
            denial = bool(re.search(r"(?:did not|not|never)\s+(?:manufacture|make|manufactured)", firm_reply))
            detail = "the manufacturer named on the label says it did not make this batch" if under_investigation or denial else "the testing laboratory declared the sample spurious"
            explanation = f"This batch matches an entry CDSCO lists as purported spurious in its {month} alert ({detail})."
    elif label == "NOT_LISTED":
        headline = "No matching alert found"
        count = context.get("list_count", 0)
        if demo:
            explanation = "No matching batch was found in the synthetic demonstration records. This example does not check a real pack against CDSCO's records."
        else:
            explanation = f"No match on the CDSCO lists loaded ({count} lists, latest {month_name(context.get('latest_month'))}). This does not certify the medicine; CDSCO tests only sampled batches."
        advice = "Check the printed details and the list date. If you have concerns about this pack, ask your pharmacist."
    else:
        headline = "More evidence is needed"
        if reason == "no_data":
            headline = "Alert data has not been loaded"
            explanation = "StripCheck has no real CDSCO alert records available for this check. Import or sync the official lists, then check this pack again."
        elif reason == "batch_gate" and entry:
            if demo:
                explanation = f"Possible demonstration match: if your batch reads {clean_text(entry.get('batch_raw') or entry.get('batch_key'))}, it matches a synthetic alert. The printed batch could not be confirmed."
            else:
                explanation = f"Possible match: if your batch reads {clean_text(entry.get('batch_raw') or entry.get('batch_key'))}, it is on CDSCO's {month} list. We could not confirm the batch, so ask your pharmacist to check it."
        elif reason == "date_conflict" and entry:
            differences = entry.get("date_diffs", [])
            detail = "; ".join(f"{key}: list {listed}, pack {pack}" for key, listed, pack in differences)
            explanation = f"StripCheck could not verify this pack: the alert for batch {clean_text(entry.get('batch_key'))} has different dates ({clean_text(detail)}). Ask your pharmacist to check the printed dates and batch against the cited alert."
        elif entry.get("evidence", {}).get("batch") in {"exact", "confirmed"}:
            record = "A synthetic demonstration record" if demo else "A stored alert record"
            explanation = f"{record} shares batch {clean_text(entry.get('batch_raw') or entry.get('batch_key'))}, but the printed details do not establish that it applies to this pack. Check the product name, manufacturer and printed dates against the cited record."
        else:
            explanation = f"StripCheck could not verify this pack: {clean_text(reason) or 'the available details do not establish a matching record'}. Ask your pharmacist to check the batch number against CDSCO's alerts."
        advice = "Ask your pharmacist to check the batch number and printed details. Do not stop any prescribed medicine without medical advice."
    if demo:
        headline = "Demo · " + headline
    return {
        "label": label, "headline": headline, "explanation": explanation, "advice": advice,
        "confidence": entry.get("confidence", "limited") if label in {"FLAGGED", "SUSPECTED_FAKE"} else "limited",
        "citations": citations, "evidence": entry.get("evidence", {}),
        "batch_evidence": batch_evidence, "lang": "en", "latest_month": context.get("latest_month"),
        "demo": demo, "reason": reason, "batch": fields.get("batch", ""),
    }


THINKING_CONTEXT = {
    "search_variants": "Exact search found nothing. Deciding what to check next.",
    "confirm_char": "The closest entry differs only by look-alike characters. Deciding whether to ask you.",
    "confirm_field": "A printed date differs from the closest entry. Deciding whether to ask you.",
    "box_photo": "The batch matches, but other printed details are not corroborated. Deciding whether to ask you.",
    "search_exact": "Starting the investigation. Choosing the first search.",
    "search_variants_after_hit": "Exact search is done. Choosing the next search.",
    "grade": "Both searches are done. Choosing how to compare the candidates.",
    "confirm_batch": "A listed entry matches. Deciding how to confirm the printed batch.",
    "draft_verdict": "The evidence is gathered. Deciding whether to draft the result.",
    "reflect": "The verifier found problems with the draft. Deciding how to revise it once.",
    "read_with_vision": "The photo text reader could not read the batch clearly. Deciding how to read it.",
    "confirm_reading": "A vision model read the batch. Deciding how to confirm the reading with you.",
    "request_photo": "The printed details are still in doubt. Deciding whether one more photo would settle it.",
}
QUESTION_REASONS = {
    "type_batch": "I need the batch number exactly as printed, because alert entries are matched by batch.",
    "confirm_batch": "A listed entry matches this batch, and a machine reading has to be confirmed by a person before a listed result is shown.",
    "confirm_char": "The closest listed batch differs only by characters that photos often confuse, and only you can see which one is printed.",
    "confirm_field": "A printed date differs from the alert entry, so the entry may belong to a different pack.",
    "box_photo": "A batch number alone does not show that an alert entry applies to this pack, so more printed details are needed.",
    "confirm_reading": "The photo text reader could not read the batch clearly, so a local vision model read it, and a model reading is used only after you confirm it.",
    "request_photo": "One more photo is the quickest way to settle the doubt about the printed details.",
}
PHOTO_KINDS = {
    "batch_zoom": "Take a close-up photo of the batch line (B.No.) so it fills the frame, without glare.",
    "second_angle": "Take another photo of the pack from a different angle so the light does not hide the print.",
    "carton": "Take a photo of the carton side that shows the product name and the manufacturer.",
}
ANSWER_STYLES = {"type_batch": "text", "confirm_batch": "chars", "confirm_char": "choice2", "confirm_field": "choice2",
                 "confirm_reading": "yes_no", "request_photo": "photo", "box_photo": "fields"}
YES, NO, DECLINE_PHOTO = "Yes, that's the batch", "No, it's different", "I can't take another photo"


def thinking_context(key):
    """Short context line for a planner decision; never model text."""
    return THINKING_CONTEXT.get(key, "Deciding the next step.")


def question_reason(kind):
    """One sentence saying why the agent is asking."""
    return QUESTION_REASONS.get(kind, QUESTION_REASONS["box_photo"])


def prior_note(items):
    """Question suffix for learned reader confusions; it never replaces the question."""
    parts = []
    for read, true, count in list(items)[:3]:
        times = "once" if int(count) == 1 else f"{int(count)} times"
        parts.append(f"{clean_text(true)} as {clean_text(read)} {times}")
    if not parts:
        return ""
    return "Earlier checks on this computer confirmed that the photo reader read " + "; ".join(parts) + ". Please still check the printed character yourself."


def question(kind, fields, entry=None, positions=None):
    entry, positions = entry or {}, positions or []
    batch = fields.get("batch", "")
    base = {"kind": kind, "batch": batch, "entry_id": entry.get("id"), "options": [], "reason": question_reason(kind), "style": ANSWER_STYLES.get(kind, "fields")}
    if kind == "confirm_reading":
        reading = clean_text(entry.get("reading"))[:40]
        base.update(question="Is this the batch printed on your pack?", reading=reading, options=[YES, NO])
    elif kind == "request_photo":
        photo = entry.get("photo_kind") if entry.get("photo_kind") in PHOTO_KINDS else "batch_zoom"
        base.update(question="Can you take one more photo?", photo_kind=photo, photo_hint=PHOTO_KINDS[photo], options=[DECLINE_PHOTO])
    elif kind == "type_batch":
        base.update(question="Read the batch number printed on your pack and type it here.", options=["Can't tell"])
    elif kind == "confirm_batch":
        where = " and ".join(str(i) for i in positions)
        base.update(question=f"Before we show this result, look at the printed batch. Type the characters at positions {where}, or type the whole batch.", positions=positions, options=["Type the whole batch", "Can't tell"])
    elif kind == "confirm_char":
        listed = entry.get("batch_raw") or entry.get("batch_key", "")
        base.update(question=f"One or more characters may be unclear. Which batch is printed on your pack: {batch} or {listed}?", positions=positions, options=[listed, batch, "Can't tell"], listed=listed, pack=batch)
    elif kind == "confirm_field":
        name, listed, pack = entry["date_diffs"][0]
        human = "expiry" if name == "exp" else "manufacturing"
        base.update(question=f"Your pack's {human} date reads {pack}; the alert lists {listed}. Which is printed?", field=name, pack=pack, listed=listed, options=[listed, pack, "Can't tell"])
    else:
        prompt = "A batch number alone cannot establish a match. Add the product name and the manufacturer or printed dates from the pack or carton."
        if entry.get("evidence", {}).get("batch") in {"exact", "confirmed"}:
            prompt = f"A record shares batch {clean_text(entry.get('batch_raw') or entry.get('batch_key'))}. To check whether it applies to this pack, add the product name and manufacturer or printed dates exactly as shown on the pack or carton. Review any details already entered."
        base.update(question=prompt, options=["Add printed details", "Can't tell"], fields=["product", "brand", "maker", "mfg", "exp"])
    return base

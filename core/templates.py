"""All result and question copy. Models never author these messages."""

import re
from urllib.parse import urlsplit

LABELS = {"FLAGGED", "SUSPECTED_FAKE", "NOT_LISTED", "CANT_VERIFY"}
BANNED = re.compile(r"\bsafe\b|\bgenuine\b|\bauthentic\b|\bfake medicine\b|\bstop (?:taking|using)\b|सुरक्षित|असली|बंद करें", re.I)
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


def question(kind, fields, entry=None, positions=None):
    entry, positions = entry or {}, positions or []
    batch = fields.get("batch", "")
    base = {"kind": kind, "batch": batch, "entry_id": entry.get("id"), "options": []}
    if kind == "type_batch":
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
        base.update(question="A batch number alone cannot establish a match. Add the product name and the manufacturer or printed dates from the pack or carton.", options=["Add printed details", "Can't tell"], fields=["product", "brand", "maker", "mfg", "exp"])
    return base

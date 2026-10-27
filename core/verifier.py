"""Independent deterministic final-result gate."""

from core.templates import BANNED, LABELS, render_verdict
from core.textutils import batch_key

GATE_EVIDENCE = {"qr", "dual_read", "user_typed", "user_confirmed"}
PENDING = {"needs_confirm_char", "needs_confirm_field", "needs_more_evidence", "adjudicate", "date_conflict"}


def check_rules(verdict, state):
    violations = []
    label = verdict.get("label")
    candidates = state.get("candidates", [])
    entry = state.get("top") or {}
    evidence = entry.get("evidence", {})
    if label not in LABELS:
        violations.append("R1: unknown result label")
    if label in {"FLAGGED", "SUSPECTED_FAKE"}:
        if (entry.get("status") != "accept" or evidence.get("batch") not in {"exact", "confirmed"}
                or state.get("batch_evidence") not in GATE_EVIDENCE
                or evidence.get("product") != "match" or "mismatch" in evidence.values()
                or not batch_key(state.get("fields", {}).get("batch"))
                or batch_key(state.get("fields", {}).get("batch")) != batch_key(entry.get("batch_key") or entry.get("batch_raw"))):
            violations.append("R2: corroborated, confirmed batch evidence is required")
        if (label == "SUSPECTED_FAKE") != (entry.get("entry_type") == "SPURIOUS") or entry.get("entry_type") not in {"SPURIOUS", "NSQ", "MISBRANDED", "ADULTERATED"}:
            violations.append("R3: alert type does not support this result")
        citations = verdict.get("citations", [])
        if not citations or not any(c.get("id") == entry.get("id") and (c.get("source_url") or c.get("source_sha256") or (c.get("synthetic") and state.get("demo"))) for c in citations):
            violations.append("R5: a traceable source citation is required")
    if label == "NOT_LISTED":
        if (not state.get("grounded_batch") or not state.get("exact_searched") or not state.get("variants_searched")
                or any(c.get("status") in PENDING | {"accept"} for c in candidates)
                or not state.get("data_available") or state.get("truncated")):
            violations.append("R4: a complete, grounded search is required")
        if not state.get("demo") and (not verdict.get("latest_month") or "lists loaded" not in verdict.get("explanation", "")):
            violations.append("R9: list coverage and freshness are required")
    texts = [verdict.get(k, "") for k in ("headline", "explanation", "advice")]
    if any(BANNED.search(str(text)) for text in texts):
        violations.append("R5: unsupported assurance or medicine instruction")
    if state.get("steps", 0) > 16 or state.get("asks", 0) > 2:
        violations.append("R6: bounded workflow exceeded")
    if label != "CANT_VERIFY" and any(c.get("status") in {"date_conflict", "needs_confirm_field"} for c in candidates):
        violations.append("R7: unresolved printed-date conflict")
    provenance = state.get("provenance", {})
    if label != "CANT_VERIFY" and any(value and provenance.get(key) not in {"user", "ocr", "qr", "ocr_enh", "carton", "vlm"} for key, value in state.get("fields", {}).items() if key in {"batch", "product", "brand", "maker", "mfg", "exp"}):
        violations.append("R8: every used field needs grounded provenance")
    if verdict.get("lang") != "en":
        violations.append("R10: reviewed translation unavailable")
    return violations


def verify_verdict(verdict, state):
    violations = check_rules(verdict, state)
    if not violations:
        return verdict
    reason = "batch_gate" if all(item.startswith("R2") for item in violations) else "the available evidence did not pass the verification checks"
    result = render_verdict("CANT_VERIFY", state.get("fields", {}), state.get("top"), state, reason, state.get("batch_evidence", "none"))
    result["verification"] = violations
    return result

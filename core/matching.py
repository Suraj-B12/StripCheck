import math
from rapidfuzz import fuzz
from core.textutils import batch_key, confusion_variants, product_coverage, maker_name

BRAND_MATCH, BRAND_MISMATCH, DATE_ASK_MAX_DIGITS = 0.8, 0.5, 1
NOISY_ALPHA, MAX_VARIANT_LOOKUPS = 1.0, 2000

def build_index(rows):
    idx = {}
    for r in rows:
        idx.setdefault(r["batch_key"], []).append(r)
    return idx

def search_exact(index, key, max_hits=None):
    rows = index.get(key, [])
    if max_hits is not None:
        rows = rows[:max(0, max_hits)]
    return [dict(r, how="exact", subs=[]) for r in rows]

def noisy_score(subs, prior, alpha=NOISY_ALPHA):
    """Log-odds that each read char o was really t: sum log((n[o,t]+a)/(n[o,o]+a)). 0 with no counts."""
    return sum(math.log((prior.get((o, t), 0) + alpha) / (prior.get((o, o), 0) + alpha)) for _, o, t in subs)

def search_variants(index, key, prior=None, max_subs=2, max_lookups=MAX_VARIANT_LOOKUPS, max_hits=None):
    prior = prior or {}
    hits = []
    if max_hits is not None and max_hits <= 0:
        return hits
    for n, (v, subs) in enumerate(confusion_variants(key, max_subs)):
        if n >= max_lookups: break
        for r in index.get(v, []):
            hits.append(dict(r, how="variant", subs=subs, score=noisy_score(subs, prior)))
            if max_hits is not None and len(hits) >= max_hits:
                break
        if max_hits is not None and len(hits) >= max_hits:
            break
    hits.sort(key=lambda h: (len(h["subs"]), -h["score"], (0, h["id"]) if isinstance(h.get("id"), (int, float)) else (1, str(h.get("id") or ""))))
    return hits

def brand_evidence(entry_brand, f):
    b = (entry_brand or "").strip()
    if not b or b.upper() in ("NA", "N/A", "NIL", "-"): return "n/a"
    cov = product_coverage(b, f"{f.get('product_text', '')} {f.get('brand') or ''}")
    if cov is None: return "unknown"
    if cov >= BRAND_MATCH: return "match"
    if f.get("brand") and cov < BRAND_MISMATCH: return "mismatch"
    return "unknown"

def _digit_diff(a, b):
    return sum(1 for x, y in zip(a, b) if x != y) if len(a) == len(b) else 99

def grade(entry, f):
    ev = {"batch": entry["how"]}
    cov = product_coverage(entry["product"], f.get("product_text", ""))
    ev["product"] = "unknown" if cov is None else "match" if cov >= 0.8 else "partial" if cov >= 0.5 else "mismatch"
    ev["brand"] = brand_evidence(entry.get("brand"), f)
    pairs = [(k, entry.get(k), f.get(k)) for k in ("mfg", "exp") if entry.get(k) and f.get(k)]
    diffs = [(k, a, b) for k, a, b in pairs if a != b]
    ev["dates"] = "unknown" if not pairs else "mismatch" if diffs else "match"
    if entry["entry_type"] == "SPURIOUS":
        ev["maker"] = "n/a"
    elif not f.get("maker"):
        ev["maker"] = "unknown"
    else:
        ev["maker"] = "match" if fuzz.token_set_ratio(entry["maker_name"].lower(), maker_name(f["maker"]).lower()) >= 85 else "mismatch"
    entry_has_dates = bool(entry.get("mfg") or entry.get("exp"))
    conf = "high"
    if "mismatch" in (ev["product"], ev["maker"], ev["brand"]):
        st = "reject"                                    # batch collision or a different product: never flag
    elif ev["dates"] == "mismatch":
        if ev["product"] == "match" and ev["batch"] in ("exact", "confirmed"):
            small = all(_digit_diff(a, b) <= DATE_ASK_MAX_DIGITS for _, a, b in diffs)
            st = "needs_confirm_field" if small else "date_conflict"
        else:
            st = "reject"                                # v1.1 behaviour
    elif ev["product"] == "partial" and not (ev["dates"] == "match" and ev["maker"] == "match"):
        st = "adjudicate"
    elif ev["batch"] not in ("exact", "confirmed", "auto_corrected"):
        st = "needs_confirm_char"
    elif ev["product"] == "unknown":
        st = "needs_more_evidence"
    elif entry["entry_type"] == "SPURIOUS":
        if ev["dates"] == "match": st = "accept"
        elif not entry_has_dates: st, conf = "accept", "medium"
        else: st = "needs_more_evidence"
    elif ev["dates"] == "match" or ev["maker"] == "match":
        st = "accept"
        if not (ev["dates"] == "match" and ev["maker"] == "match"): conf = "medium"
    else:
        st = "needs_more_evidence"
    return dict(entry, evidence=ev, status=st, confidence=conf, date_diffs=diffs)

def decide(graded, read_ok):
    acc = [g for g in graded if g["status"] == "accept"]
    if acc:
        top = sorted(acc, key=lambda g: (g["entry_type"] != "SPURIOUS", g["confidence"] != "high"))[0]
        return ("SUSPECTED_FAKE" if top["entry_type"] == "SPURIOUS" else "FLAGGED"), top
    pending = [g for g in graded if g["status"] in ("needs_confirm_char", "needs_confirm_field", "needs_more_evidence", "adjudicate")]
    if pending:
        return "ASK", pending[0]
    conflict = [g for g in graded if g["status"] == "date_conflict"]
    if conflict:
        return "CANT_VERIFY", conflict[0]
    return ("NOT_LISTED" if read_ok else "CANT_VERIFY"), None

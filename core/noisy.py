"""Bounded character-confusion helpers; a prior never authorizes a correction."""

from core.textutils import CONFUSABLE
from core.matching import noisy_score, search_variants


def prior_counts(rows):
    """Combine stored calibration and user counts without changing the alphabet."""
    result = {}
    for row in rows:
        read = str(row.get("read_char", row.get("ocr_char", row.get("read", "")))).upper()
        true = str(row.get("true_char", row.get("true", ""))).upper()
        if len(read) == len(true) == 1 and (read == true or true in CONFUSABLE.get(read, "")):
            result[(read, true)] = result.get((read, true), 0) + max(0, int(row.get("count", 0)))
    return result


def confirmation_positions(key, prior=None):
    """Return up to two 1-based positions, with the most ambiguous first."""
    prior = prior or {}
    ranked = sorted(
        (i for i, char in enumerate(key) if char in CONFUSABLE),
        key=lambda i: (-sum(prior.get((key[i], alt), 0) for alt in CONFUSABLE[key[i]]), i),
    )
    return [i + 1 for i in (ranked[:2] if ranked else list(range(max(0, len(key) - 2), len(key))))]


def rank_variants(index, key, prior=None, limit=20):
    return search_variants(index, key, prior=prior, max_subs=2, max_lookups=2000)[:max(0, min(limit, 20))]

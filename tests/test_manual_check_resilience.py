"""Synthetic regressions for manual checks; no stored official records included."""

from copy import deepcopy

import pytest

from core.investigator import investigate
from core.matching import grade


@pytest.fixture
def row():
    return {"id": "synthetic-manual", "product": "Examplezolid Tablets 600mg", "brand": "Examplebrand",
            "batch_raw": "SYN261185", "batch_key": "SYN261185", "mfg": "2026-05", "exp": "2028-04",
            "maker_name": "Fictional Manufacturing", "entry_type": "NSQ", "list_month": "2026-08",
            "source_title": "Synthetic manual-check regression", "source_url": "", "synthetic": True,
            "result": "Synthetic dissolution finding", "row_no": 1}


def run(row, **fields):
    return investigate({"batch": row["batch_raw"], "source": "user", "confirmed": True, **fields},
                       [row], {"demo": True, "mode": "text"})


def resume(snapshot, row, answer):
    return investigate(snapshot["fields"], [row], snapshot["context"], answer)


@pytest.mark.parametrize("stale", [
    {"maker": "Example Laboratories", "mfg": "2024-08", "exp": "2027-07"},
    {"maker": "Example Laboratories"},
    {"mfg": "2024-08", "exp": "2027-07"},
])
def test_exact_batch_with_missing_product_and_conflicting_details_asks(row, stale):
    result = run(row, **stale)
    assert result["status"] == "waiting" and result["final"] is None
    assert result["pending"]["kind"] == "box_photo"
    assert "A record shares batch SYN261185" in result["pending"]["question"]
    assert result["candidates"][0]["status"] == "needs_more_evidence"
    after = resume(result, row, {"skip": True})
    assert after["final"]["label"] == "CANT_VERIFY"
    assert after["final"]["citations"][0]["id"] == row["id"]
    assert "shares batch SYN261185" in after["final"]["explanation"]


def test_clean_manual_batch_asks_and_printed_followup_can_verify(row):
    result = run(row)
    assert result["pending"]["kind"] == "box_photo"
    assert set(result["pending"]["fields"]) >= {"product", "maker", "mfg", "exp"}
    result = resume(result, row, {"fields": {"product": row["product"], "maker": row["maker_name"]}})
    assert result["status"] == "done" and result["final"]["label"] == "FLAGGED"
    assert result["final"]["batch_evidence"] == "user_typed"


def test_corrected_printed_details_replace_conflicts_without_inference(row):
    result = run(row, maker="Example Laboratories", mfg="2024-08", exp="2027-07")
    result = resume(result, row, {"fields": {"product": row["product"], "maker": row["maker_name"],
                                           "mfg": row["mfg"], "exp": row["exp"]}})
    assert result["final"]["label"] == "FLAGGED"
    assert result["fields"]["maker"] == row["maker_name"]


@pytest.mark.parametrize("product", ["Examplezolid Tablets 600mg", "Examplezolid"])
def test_matching_or_partial_product_and_conflicting_maker_remain_incomplete(row, product):
    result = run(row, product=product, maker="Different Fictional Manufacturer")
    assert result["pending"]["kind"] == "box_photo"
    result = resume(result, row, {"skip": True})
    assert result["final"]["label"] == "CANT_VERIFY"


@pytest.mark.parametrize("details", [
    {"product": "Entirelydifferent Capsules"},
    {"product": "Examplezolid Tablets 600mg", "brand": "Unrelatedbrand"},
])
def test_independent_product_or_brand_collision_still_rejected(row, details):
    result = run(row, maker="Unrelated Company", **details)
    assert result["final"]["label"] == "NOT_LISTED"


def test_unresolved_details_stop_within_question_budget(row):
    result = run(row)
    for _ in range(2):
        result = resume(result, row, {"fields": {"maker": "Different Fictional Manufacturer"}})
    assert result["final"]["label"] == "CANT_VERIFY"
    assert result["context"]["_engine"]["asks"] == 2
    assert len(result["history"]) <= 16


def test_typed_nearby_batch_is_not_replaced_or_implicitly_confirmed(row):
    changed = deepcopy(row)
    changed["batch_raw"] = changed["batch_key"] = "SYN26B185"
    result = investigate({"batch": "SYN268185", "product": row["product"], "maker": row["maker_name"], "source": "user"},
                         [changed], {"demo": True, "mode": "text"})
    assert result["fields"]["batch"] == "SYN268185"
    assert result["status"] == "done" and result["final"]["label"] == "CANT_VERIFY"


def test_confirmed_batch_with_unknown_product_ignores_no_conflicts(row):
    candidate = grade(dict(row, how="confirmed", subs=[]), {"maker": "Different Fictional Manufacturer", "exp": "2027-07"})
    assert candidate["status"] == "needs_more_evidence"
    assert candidate["evidence"]["maker"] == candidate["evidence"]["dates"] == "mismatch"

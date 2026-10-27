"""Crash, resource-bound and false-alarm regressions using synthetic fixtures."""

from copy import deepcopy
import random

import pytest

from core.investigator import investigate
from core.matching import build_index, grade, search_exact, search_variants
from core.props import demo_cases
from core.templates import render_verdict
from core.verifier import check_rules


def fixture():
    case = demo_cases()[0]
    return deepcopy(case["fields"]), deepcopy(case["alerts"][0])


def check(fields, rows, context=None):
    return investigate(fields, rows, {"demo": True, **(context or {})})


def test_oversized_batch_is_never_silently_truncated_to_a_hit():
    fields, row = fixture()
    row["batch_key"] = row["batch_raw"] = "X" * 40
    fields.update(batch="X" * 40 + "Y", source="user")
    result = check(fields, [row])
    assert result["fields"]["batch"] == fields["batch"]
    assert result["final"]["label"] == "CANT_VERIFY"
    assert "supported length" in result["final"]["reason"]


def test_invalid_printed_date_is_not_discarded_to_gain_acceptance():
    fields, row = fixture()
    fields.update(exp="not a date", source="user")
    result = check(fields, [row])
    assert result["final"]["label"] == "CANT_VERIFY"
    assert "printed date" in result["final"]["reason"]


def test_iso_full_dates_compare_correctly():
    fields, row = fixture()
    fields.update(mfg="2024-08-22", exp="2027-07-31", source="user")
    result = check(fields, [row])
    assert result["final"]["label"] == "FLAGGED"


def test_invalid_iso_calendar_day_abstains():
    fields, row = fixture()
    fields.update(exp="2027-02-31", source="user")
    assert check(fields, [row])["final"]["label"] == "CANT_VERIFY"


def test_placeholder_maker_is_missing_evidence_not_a_contradiction():
    fields, row = fixture()
    fields.update(maker="N/A", source="user")
    assert check(fields, [row])["final"]["label"] == "FLAGGED"


def test_initial_conflicting_readers_require_typing_even_for_qr():
    fields, row = fixture()
    fields.update(source="qr", confirmed=True)
    result = check(fields, [row], {"reader_disagreement": True, "reader_batches": ["LM2408B", "LM2408R"]})
    assert result["pending"]["kind"] == "type_batch"
    assert result["strip"]["source"] == "none" and not result["fields"]["confirmed"]
    result = investigate(result["fields"], [row], result["context"], {"typed": "LM2408R"})
    assert result["final"]["label"] == "NOT_LISTED"


def test_initial_conflicting_readers_decline_abstains():
    fields, row = fixture()
    result = check(fields, [row], {"reader_disagreement": True})
    result = investigate(result["fields"], [row], result["context"], {"skip": True})
    assert result["final"]["label"] == "CANT_VERIFY"


def test_conflicting_carton_photos_cannot_claim_dual_read_agreement():
    fields, row = fixture()
    fields.update(mfg="", exp="", maker="")
    result = check(fields, [row])
    assert result["pending"]["kind"] == "box_photo"
    context = dict(result["context"], reader_disagreement=True, reader_batches=[fields["batch"], "LM2408R"])
    result = investigate(result["fields"], [row], context, {"source": "carton", "fields": {"batch": fields["batch"], "maker": "Example Laboratories"}})
    assert result["pending"]["kind"] == "type_batch"
    assert result["context"]["_engine"]["batch_evidence"] == "none"
    result = investigate(result["fields"], [row], result["context"], {"typed": fields["batch"]})
    assert result["final"]["label"] == "FLAGGED"


def test_nullable_and_invalid_alert_rows_do_not_crash():
    fields, row = fixture()
    row.update(maker_name=None, flags=None, product=None, brand=None)
    result = check(fields, [None, "invalid", row])
    assert result["status"] in {"waiting", "done"}
    assert not result.get("final") or result["final"]["label"] != "FLAGGED"


def test_malformed_flag_metadata_does_not_crash():
    fields, row = fixture()
    row["flags"] = 42
    assert check(dict(fields, source="user"), [row])["final"]["label"] == "FLAGGED"


@pytest.mark.parametrize("entry_type", [None, "", "UNKNOWN"])
def test_missing_or_unknown_source_alert_type_cannot_alarm(entry_type):
    fields, row = fixture()
    row["entry_type"] = entry_type
    result = check(dict(fields, source="user"), [row])
    assert result["final"]["label"] == "CANT_VERIFY"
    assert any(rule.startswith("R3") for rule in result["final"]["verification"])


def test_search_hit_materialization_is_bounded_and_truncation_abstains():
    fields, row = fixture()
    rows = [dict(row, id=i) for i in range(50_000)]
    index = build_index(rows)
    assert len(search_exact(index, fields["batch"], max_hits=21)) == 21
    assert len(search_variants(index, "LM24088", max_hits=21)) == 21
    result = check(dict(fields, source="user"), rows)
    assert result["context"]["_engine"]["truncated"]
    assert len(result["candidates"]) <= 20
    assert result["final"]["label"] == "CANT_VERIFY"


def test_variant_sort_handles_mixed_ids_deterministically():
    rows = [{"id": 7, "batch_key": "B8"}, {"id": "fixture", "batch_key": "B8"}, {"id": None, "batch_key": "B8"}]
    result = search_variants(build_index(rows), "BB")
    assert [item["id"] for item in result] == [7, None, "fixture"]


def test_indexed_subset_zero_hits_uses_explicit_server_coverage():
    fields, _ = fixture()
    fields["source"] = "user"
    result = investigate(fields, [], {"candidate_subset": True, "real_alert_count": 5000, "latest_month": "2026-09", "list_count": 12})
    assert result["final"]["label"] == "NOT_LISTED"
    assert "12 lists" in result["final"]["explanation"]
    assert any("5,000 loaded records" in item["summary"] for item in result["history"])


def test_incomplete_subset_coverage_cannot_claim_not_listed():
    fields, _ = fixture()
    result = investigate(fields, [], {"candidate_subset": True, "real_alert_count": 5000})
    assert result["final"]["label"] == "CANT_VERIFY"


def test_missing_batch_with_indexed_coverage_can_ask_for_input():
    fields, _ = fixture()
    fields["batch"] = ""
    result = investigate(fields, [], {"candidate_subset": True, "real_alert_count": 5000, "latest_month": "2026-09", "list_count": 12})
    assert result["pending"]["kind"] == "type_batch"


def verifier_fixture():
    fields, row = fixture()
    fields["source"] = "user"
    entry = grade(dict(row, how="exact", subs=[]), dict(fields, product_text=fields["product"]))
    state = {"fields": fields, "top": entry, "candidates": [entry], "batch_evidence": "user_typed", "demo": True,
             "provenance": {key: "user" for key in fields}, "asks": 0, "steps": 5}
    verdict = render_verdict("FLAGGED", fields, entry, state, batch_evidence="user_typed")
    return verdict, state


def test_verifier_rejects_stale_candidate_for_another_batch():
    verdict, state = verifier_fixture()
    assert check_rules(verdict, state) == []
    state["fields"]["batch"] = "LM2408R"
    assert any(rule.startswith("R2") for rule in check_rules(verdict, state))


def test_verifier_requires_citation_for_the_accepted_record():
    verdict, state = verifier_fixture()
    verdict["citations"][0]["id"] = "unrelated"
    assert any(rule.startswith("R5") for rule in check_rules(verdict, state))


def test_verifier_blocks_unknown_alert_type():
    verdict, state = verifier_fixture()
    state["top"]["entry_type"] = "UNKNOWN"
    assert any(rule.startswith("R3") for rule in check_rules(verdict, state))


def test_verifier_blocks_unresolved_date_question_anywhere():
    verdict, state = verifier_fixture()
    state["candidates"].append({"status": "needs_confirm_field"})
    assert any(rule.startswith("R7") for rule in check_rules(verdict, state))


def test_seeded_distinct_nonconfusable_batches_never_alarm():
    fields, row = fixture()
    randomizer = random.Random(417)
    for _ in range(100):
        fields.update(batch="HX" + "".join(randomizer.choice("XYUV") for _ in range(8)), source="user")
        result = check(fields, [row])
        assert result["final"]["label"] == "NOT_LISTED"
        assert len(result["history"]) <= 16


@pytest.mark.parametrize("case", demo_cases(), ids=lambda case: case["id"])
def test_all_demo_paths_stay_within_question_and_step_budgets(case):
    result = check(case["fields"], case["alerts"])
    for answer in case["answers"]:
        if result["status"] == "waiting":
            result = investigate(result["fields"], case["alerts"], result["context"], answer)
    assert result["final"]["label"] == case["expected"]
    assert result["context"]["_engine"]["asks"] <= 2
    assert len(result["history"]) <= 16

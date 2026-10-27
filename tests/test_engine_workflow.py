"""Synthetic fixtures, invented products and batch identifiers. No CDSCO data."""

import json
from copy import deepcopy
import pytest

from core.investigator import investigate
from core.templates import BANNED, render_verdict
from core.verifier import check_rules


@pytest.fixture
def alert():
    return {"id": 1, "product": "Examplezol Tablets", "brand": "Examplebrand", "batch_raw": "EXB2401", "batch_key": "EXB2401", "mfg": "2024-01", "exp": "2027-12", "maker_name": "Example Laboratories", "entry_type": "NSQ", "result": "Synthetic dissolution finding", "list_month": "2026-09", "source_title": "Synthetic demonstration fixture", "source_url": "", "row_no": 1, "synthetic": True}


@pytest.fixture
def fields():
    return {"batch": "EXB2401", "product": "Examplezol Tablets", "brand": "Examplebrand", "mfg": "2024-01", "exp": "2027-12", "maker": "Example Laboratories", "source": "ocr", "confirmed": False}


def run(fields, alert, **context):
    return investigate(fields, [alert], context={"demo": True, "latest_month": "2026-09", **context})


def resume(snapshot, alert, answer):
    return investigate(snapshot["fields"], [alert], context=json.loads(json.dumps(snapshot["context"])), answer=answer)


def test_flag_requires_printed_batch_confirmation(fields, alert):
    result = run(fields, alert)
    assert result["status"] == "waiting" and result["pending"]["kind"] == "confirm_batch"
    result = resume(result, alert, {"typed": fields["batch"]})
    assert result["final"]["label"] == "FLAGGED"
    assert result["final"]["batch_evidence"] == "user_confirmed"
    assert result["final"]["citations"][0]["synthetic"]
    assert "synthetic" in result["final"]["explanation"]
    assert len(result["history"]) <= 16 and result["context"]["_engine"]["asks"] == 1


def test_confirmation_no_bare_yes(fields, alert):
    result = run(fields, alert)
    after = resume(result, alert, {"choice": "yes"})
    assert after["status"] == "waiting" and after["pending"]["error"]
    assert after["final"] is None


def test_confirmation_chars_do_not_ignore_correction(fields, alert):
    result = run(fields, alert)
    chars = {str(position): fields["batch"][position - 1] for position in result["pending"]["positions"]}
    first = str(result["pending"]["positions"][0])
    chars[first] = "9"
    result = resume(result, alert, {"chars": chars})
    assert result["fields"]["batch"] != fields["batch"]
    assert result["status"] == "done" and result["final"]["label"] == "NOT_LISTED"
    assert alert["batch_key"] in result["context"]["_engine"]["rejected_keys"]


def test_sibling_correction_rejects_previous_read(fields, alert):
    result = run(fields, alert)
    result = resume(result, alert, {"typed": "EX82401"})
    assert result["final"]["label"] == "NOT_LISTED"
    assert result["context"]["_engine"]["asks"] == 1


def test_declined_batch_is_possible_match(fields, alert):
    result = resume(run(fields, alert), alert, {"skip": True})
    assert result["final"]["label"] == "CANT_VERIFY"
    assert "Possible demonstration match" in result["final"]["explanation"]


def test_variant_never_silently_corrected(fields, alert):
    fields["batch"] = "EX82401"
    result = run(fields, alert)
    assert result["pending"]["kind"] == "confirm_char" and result["fields"]["batch"] == "EX82401"
    result = resume(result, alert, {"choice": "EXB2401"})
    assert result["final"]["label"] == "FLAGGED" and result["fields"]["batch"] == "EXB2401"


def test_variant_decline_remains_unresolved(fields, alert):
    fields["batch"] = "EX82401"
    result = resume(run(fields, alert), alert, {"choice": "Can't tell"})
    assert result["final"]["label"] == "CANT_VERIFY"


def test_user_typed_batch_passes_gate(fields, alert):
    fields["source"] = "user"
    assert run(fields, alert)["final"]["label"] == "FLAGGED"


def test_no_real_data_never_reports_not_listed(fields, alert):
    assert investigate(fields, [], {})["final"]["reason"] == "no_data"
    assert investigate(fields, [alert], {"demo": False})["final"]["reason"] == "no_data"


def test_batch_collision_rejected(fields, alert):
    fields.update(product="Entirelydifferent Tablets", brand="Otherbrand", maker="Other Company")
    assert run(fields, alert)["final"]["label"] == "NOT_LISTED"


def test_one_digit_date_is_asked_and_printed_conflict_abstains(fields, alert):
    fields["exp"] = "2027-10"
    result = run(fields, alert)
    assert result["pending"]["kind"] == "confirm_field"
    result = resume(result, alert, {"choice": "2027-10"})
    assert result["final"]["label"] == "CANT_VERIFY" and result["final"]["reason"] == "date_conflict"


def test_corrected_date_regrades_then_confirms_batch(fields, alert):
    fields["exp"] = "2027-10"
    result = resume(run(fields, alert), alert, {"choice": "2027-12"})
    assert result["pending"]["kind"] == "confirm_batch"
    result = resume(result, alert, {"typed": fields["batch"]})
    assert result["final"]["label"] == "FLAGGED"
    assert result["context"]["_engine"]["asks"] == 2 and len(result["history"]) <= 16


def test_far_date_conflict_abstains_without_question(fields, alert):
    fields["exp"] = "2028-03"
    assert run(fields, alert)["final"]["reason"] == "date_conflict"


def test_missing_corroboration_asks_for_printed_details(fields, alert):
    fields.update(mfg="", exp="", maker="")
    result = run(fields, alert)
    assert result["pending"]["kind"] == "box_photo"
    result = resume(result, alert, {"fields": {"maker": "Example Laboratories"}})
    assert result["pending"]["kind"] == "confirm_batch"
    result = resume(result, alert, {"typed": fields["batch"]})
    assert result["final"]["label"] == "FLAGGED"


def test_unreadable_batch_can_be_typed(fields, alert):
    fields["batch"] = ""
    result = run(fields, alert)
    assert result["pending"]["kind"] == "type_batch"
    result = resume(result, alert, {"typed": "EXB2401"})
    assert result["final"]["label"] == "FLAGGED"


def test_carton_provenance_and_independent_batch_agreement(fields, alert):
    fields.update(mfg="", exp="", maker="")
    result = resume(run(fields, alert), alert, {"source": "carton", "fields": {"batch": fields["batch"], "maker": "Example Laboratories"}})
    assert result["final"]["label"] == "FLAGGED"
    assert result["final"]["batch_evidence"] == "dual_read"
    assert result["context"]["_engine"]["provenance"]["maker"] == "carton"


def test_carton_different_batch_requires_explicit_resolution(fields, alert):
    fields.update(mfg="", exp="", maker="")
    result = resume(run(fields, alert), alert, {"source": "carton", "fields": {"batch": "EX82401", "maker": "Example Laboratories"}})
    assert result["pending"]["kind"] == "type_batch"
    assert not result["fields"]["confirmed"]
    result = resume(result, alert, {"skip": True})
    assert result["final"]["label"] == "CANT_VERIFY"


def test_spurious_uses_evidence_specific_wording(fields, alert):
    fields["source"] = "user"
    alert.update(entry_type="SPURIOUS", synthetic=False, source_url="https://example.invalid/synthetic-test", source_title="Test fixture citation")
    result = investigate(fields, [alert], {"latest_month": "2026-09"})
    assert result["final"]["label"] == "SUSPECTED_FAKE"
    assert "testing laboratory" in result["final"]["explanation"]
    alert["maker_name"] = "Under Investigation"
    result = investigate(fields, [alert], {"latest_month": "2026-09"})
    assert "manufacturer named" in result["final"]["explanation"]


def test_untraceable_real_alert_cannot_flag(fields, alert):
    fields["source"] = "user"
    alert.update(synthetic=False, source_title="Missing provenance fixture")
    result = investigate(fields, [alert], {"latest_month": "2026-09"})
    assert result["final"]["label"] == "CANT_VERIFY"
    assert any(item.startswith("R5") for item in result["final"]["verification"])


def test_cabinet_without_trusted_batch_abstains(fields, alert):
    result = run(fields, alert, cabinet=True, batch_evidence="ocr")
    assert result["status"] == "done" and result["final"]["reason"] == "batch_gate"
    assert run(fields, alert, cabinet=True, batch_evidence="user_confirmed")["final"]["label"] == "FLAGGED"


def test_input_not_mutated_and_context_json_serializable(fields, alert):
    original = deepcopy(fields), deepcopy(alert)
    result = run(fields, alert)
    json.dumps(result)
    assert (fields, alert) == original


@pytest.mark.parametrize("label", ["FLAGGED", "SUSPECTED_FAKE", "NOT_LISTED", "CANT_VERIFY"])
def test_all_templates_filter_unsafe_dynamic_text(label, fields, alert):
    alert["result"] = "authentic genuine fake medicine"
    result = render_verdict(label, fields, alert, {"latest_month": "2026-09"})
    for key in ("headline", "explanation", "advice"):
        assert not BANNED.search(result[key])


def test_model_output_invalid_action_falls_back(monkeypatch):
    import core.llm as llm
    monkeypatch.setattr(llm, "structured_call", lambda *args, **kwargs: {"action": "send_email"})
    assert llm.choose_action({}, ["search_exact"], "search_exact") == ("search_exact", "rules(fallback)")
    assert llm.structured_call is not None


def test_model_off_by_default_and_nonlocal_rejected():
    from core.llm import structured_call
    assert structured_call("test", {}) is None
    assert structured_call("test", {}, model="example", url="https://example.invalid") is None

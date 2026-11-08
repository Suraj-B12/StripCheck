"""Regressions found by the R4 evaluation and the guide review. Synthetic fixtures only, no CDSCO data."""

import json

from core.investigator import investigate
from core.noisy import confirmation_positions

ALERT = {"id": 1, "product": "Examplezol Tablets IP 500 mg", "brand": "", "batch_raw": "EXB2401", "batch_key": "EXB2401",
         "mfg": "2024-01", "exp": "2027-12", "maker_name": "Example Laboratories", "entry_type": "NSQ",
         "result": "Synthetic dissolution finding", "list_month": "2026-09", "source_title": "Synthetic fixture",
         "source_url": "", "row_no": 1, "synthetic": True}


def _run(fields, answer=None, snapshot=None):
    if snapshot:
        return investigate(snapshot["fields"], [ALERT], context=json.loads(json.dumps(snapshot["context"])), answer=answer)
    return investigate(fields, [ALERT], context={"demo": True, "latest_month": "2026-09"})


def test_brand_line_does_not_hide_generic_name():
    # OCR took the brand line as the product; the generic name is only in product_text.
    fields = {"batch": "EXB2401", "product": "BRANDOZOL", "product_text": "BRANDOZOL Examplezol Tablets IP 500 mg",
              "brand": "", "mfg": "2024-01", "exp": "2027-12", "maker": "Example Laboratories", "source": "ocr", "confirmed": False}
    result = _run(fields)
    assert result["status"] == "waiting" and result["pending"]["kind"] == "confirm_batch"
    result = _run(None, {"typed": "EXB2401"}, result)
    assert result["final"]["label"] == "FLAGGED"


def test_every_lookalike_position_is_asked():
    # B, 2, 4, 0 and 1 are all look-alikes; a misread could sit at any of them.
    positions = confirmation_positions("EXB2401")
    assert sorted(positions) == [3, 4, 5, 6, 7]
    assert confirmation_positions("XYW") == [2, 3]

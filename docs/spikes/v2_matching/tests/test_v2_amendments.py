# Spec v2 Appendix A3 tests (as written in the spec) plus extra edge cases found while designing.
from core.textutils import find_batch, parse_month_year, product_coverage
from core.matching import build_index, search_exact, search_variants, grade, decide

def test_v2_textutils():
    assert find_batch(["Calamine Lotion IP", "B.No. CL2401"]) == ("CL2401", 1)
    assert find_batch(["Batchwise QC passed", "Batch No: X1234"]) == ("X1234", 1)
    assert find_batch(["BatchNo.AB1234"]) == ("AB1234", 0)
    assert find_batch(["B.No.", "SP240165", "Mfg. 06/2024"]) == ("SP240165", 1)
    assert find_batch(["B.No.", "Mfg. 06/2024"]) == (None, None)
    assert parse_month_year("01/07/24") == "2024-07"
    assert parse_month_year("Apr—2026") == "2026-04"

def test_v2_matching():
    e = dict(id=9, product="Paracetamol Tablets IP 650 mg", brand="Dolo-650", batch_key="DL2401",
             mfg="2025-01", exp="2027-12", maker_name="Micro Labs Ltd", entry_type="NSQ", how="exact", subs=[])
    other_brand = dict(product_text="Calpol 650 Paracetamol Tablets IP", brand="Calpol 650", mfg="2025-01", exp="2027-12", maker="GSK")
    assert grade(e, other_brand)["status"] == "reject"
    one_digit = dict(product_text="Dolo-650 Paracetamol Tablets IP", brand="Dolo-650", mfg="2025-01", exp="2027-10", maker="Micro Labs Ltd")
    assert grade(e, one_digit)["status"] == "needs_confirm_field"
    far = dict(one_digit, exp="2028-03")
    g = grade(e, far)
    assert g["status"] == "date_conflict" and decide([g], read_ok=True)[0] == "CANT_VERIFY"
    idx = build_index([dict(id=1, batch_key="BBT2305"), dict(id=2, batch_key="B8T2305")])
    assert [h["id"] for h in search_variants(idx, "B3T2305")][:2] == [1, 2]
    assert [h["id"] for h in search_variants(idx, "B3T2305", prior={("3", "8"): 5})][:2] == [2, 1]

# ---- extra edge cases -------------------------------------------------------------------------

def test_brand_only_in_product_brackets_still_matches():
    # older portal rows: brand embedded in the product name, brand field empty -> brand n/a, product decides
    e = dict(id=1, product="Levetiracetam Tablets IP (Levipil 500)", brand="", batch_key="SIE1003A", mfg="2023-04",
             exp="2025-03", maker_name="Sun Pharma Laboratories Ltd", entry_type="NSQ", how="exact", subs=[])
    f = dict(product_text="LEVIPIL 500 Levetiracetam Tablets IP 500 mg", brand="LEVIPIL 500", mfg="2023-04", exp="2025-03",
             maker="Sun Pharma Laboratories Ltd.")
    assert grade(e, f)["status"] == "accept"

def test_brand_unknown_when_pack_brand_not_detected():
    e = dict(id=1, product="Alprazolam Tablets IP 0.5 mg", brand="Alzomac-0.5 Tablets", batch_key="60098", mfg="2026-02",
             exp="2028-01", maker_name="Uniza Lifecare Pvt. Ltd", entry_type="NSQ", how="exact", subs=[])
    f = dict(product_text="Alprazolam Tablets IP 0.5 mg", brand=None, mfg="2026-02", exp="2028-01", maker="Uniza Lifecare Pvt. Ltd.")
    g = grade(e, f)
    assert g["evidence"]["brand"] == "unknown" and g["status"] == "accept"

def test_variant_with_date_mismatch_is_rejected_like_v11():
    # a sibling batch with different dates is a different batch, not a conflict to ask about
    e = dict(id=4, product="Paracetamol Tablets IP 650 mg (Demo-650)", batch_key="BBT2305", mfg="2025-01", exp="2027-12",
             maker_name="Demo Remedies Pvt Ltd", entry_type="NSQ", how="variant", subs=[(1, "3", "B")])
    f = dict(product_text="DEMO-650 Paracetamol Tablets IP 650 mg", mfg="2025-02", exp="2027-12", maker="Demo Remedies Pvt. Ltd.")
    assert grade(e, f)["status"] == "reject"

def test_variant_lookup_cap():
    hits = search_variants({}, "B3T2305O0S5", max_lookups=10)
    assert hits == []

def test_dates_ddmmyy_does_not_break_mm_yyyy():
    assert parse_month_year("06/2024") == "2024-06"
    assert parse_month_year("1.2.24") == "2024-02"
    assert parse_month_year("05/27") == "2027-05"

# v1.1 Appendix A3 tests, copied verbatim; they must keep passing after the v2 amendments.
from core.textutils import *
from core.textutils import batch_key
from core.matching import build_index, search_exact, search_variants, grade, decide

def test_dates():
    cases = {"06/2024":"2024-06","6-2024":"2024-06","Jun-24":"2024-06","JUN 2024":"2024-06","June, 2024":"2024-06",
             "Apr--2026":"2026-04","Oct/2023":"2023-10","01/07/2024":"2024-07","JUN.26":"2026-06","09-2026":"2026-09",
             "Mfg. 06/2024":"2024-06","Exp.05/2026":"2026-05","NM":None,"N/A":None,"Not Mentioned":None,"":None,
             "Feb-2026":"2026-02","Mar-28":"2028-03","05/27":"2027-05"}
    for k, v in cases.items():
        assert parse_month_year(k) == v, k

def test_headers_legacy_state_portal():
    legacy = ['S.No', 'Product/Drug Name', 'Batch No.', 'Manufacturin\ng Date', 'Expiry\nDate', 'Manufactured By', 'NSQ Result', 'Reported by\nCDSCO\nLaboratory']
    portal = ["S.No", "Name of Product", "Batch No", "Manufacturing Dates", "Manufacturer Details", "Reporting Source", "Reporting by Lab/State", "Reporting Month & Year", "Remarks"]
    assert map_headers(legacy) == {0:'sno',1:'product',2:'batch',3:'mfg',4:'exp',5:'maker',6:'result',7:'reported_by'}
    assert map_headers(portal) == {0:'sno',1:'product',2:'batch',3:'mfg',4:'maker',5:'source_level',6:'reported_by',7:'list_month',8:'result'}
    assert split_portal_dates("Manufacturing Date: Oct-2024Expiry Date: Mar-2027") == ("2024-10", "2027-03")

def test_makers_types_batches_qr():
    assert maker_name("M/s. Shangrila Industries (P) Ltd., (Pharma Division) Mining Rangpo East Sikkim-737132") == "Shangrila Industries (P) Ltd"
    assert maker_name("Manufacturer Name: Under InvestigationManufactured By: Under Investigation") == "Under Investigation"
    assert maker_name("M/s.Hygeia Labs, Baddi Mkt By : Alkem Labs Ltd") == "Hygeia Labs"
    assert entry_type("SPURIOUS") == "SPURIOUS" and entry_type("Dissolution") == "NSQ" and entry_type("Misbranded") == "MISBRANDED"
    assert entry_type("", "NSQ Remark: The product is purported to be spurious") == "SPURIOUS"
    assert find_batch(["PANTOSHANG-40", "B.No. SP240165"]) == ("SP240165", 1)
    assert find_batch(["Lot: AD-204 Exp 04/2026"]) == ("AD-204", 0)
    assert parse_qr_payload("(01)08901234567890(10)SP240165(11)240601(17)260531") == {"gtin":"08901234567890","batch":"SP240165","mfg":"2024-06","exp":"2026-05"}
    assert parse_qr_payload("Brand: Dolo 650\nBatch No: DOBS3975\nMfg: 03/2025\nExp: 02/2028") == {"batch":"DOBS3975","mfg":"2025-03","exp":"2028-02"}
    assert any(v == "BBT2305" for v, _ in confusion_variants("B3T2305"))
    assert product_coverage("Telapp MT 25 (Telmisartan & Metoprolol Succinate (ER) Tablets)", "Telma 40 Telmisartan Tablets IP 40 mg") < 0.5

def test_pack_labels():
    assert find_dates(["Mfg. 06/2024    Exp. 05/2026"]) == ("2024-06", "2026-05")
    assert find_dates(["Mfg.06/2024 Exp.05/2026"]) == ("2024-06", "2026-05")
    assert find_dates(["MFD. 06/2024", "EXP. 05/2026"]) == ("2024-06", "2026-05")
    assert find_dates(["Mfd. by: Shangrila Industries (P) Ltd.,", "Mfg. Date: Jun-2024", "Exp. Date: May-2026"]) == ("2024-06", "2026-05")
    assert find_dates(["MFG.DT. 11/24 EXP.DT. 10/26"]) == ("2024-11", "2026-10")
    assert find_dates(["Manufacturing Date: 01/07/2024", "Expiry Date: 30/06/2026"]) == ("2024-07", "2026-06")
    assert find_dates(["Use before JUN.26"]) == (None, "2026-06")
    assert find_dates(["Mfd. by: Demo Remedies Pvt. Ltd."]) == (None, None)
    assert find_party(["Mfd. by: Shangrila Industries (P) Ltd.,", "Rangpo"], MAKER_RE) == "Shangrila Industries (P) Ltd"
    assert find_party(["Mkt. by: Alkem Laboratories Ltd."], MKT_RE) == "Alkem Laboratories Ltd"

E = [
 dict(id=1, product="Pantoprazole GastroResistant Tablets IP (Pantoshang-40)", batch_key="SP240165", mfg="2024-06", exp="2026-05", maker_name="Shangrila Industries (P) Ltd", entry_type="NSQ"),
 dict(id=2, product="Telapp MT 25 (Telmisartan & Metoprolol Succinate (ER) Tablets)", batch_key="T24H459A", mfg="2024-08", exp="2026-07", maker_name="Bajaj Formulation", entry_type="NSQ"),
 dict(id=3, product="Cefixime Dispersible Tablets IP", batch_key="TC2439", mfg="2024-10", exp="2027-03", maker_name="Under Investigation", entry_type="SPURIOUS"),
 dict(id=4, product="Paracetamol Tablets IP 650 mg (Demo-650)", batch_key="BBT2305", mfg="2025-01", exp="2027-12", maker_name="Demo Remedies Pvt Ltd", entry_type="NSQ"),
 dict(id=5, product="Gentamicin Injection I.P. 30 ml", batch_key="GJ2309", mfg=None, exp=None, maker_name="Under Investigation", entry_type="SPURIOUS"),
]
IDX = build_index(E)

def run(f):
    k = batch_key(f["batch"]); c = search_exact(IDX, k)
    if not any(grade(x, f)["status"] == "accept" for x in c): c += search_variants(IDX, k)
    return decide([grade(x, f) for x in c], read_ok=True)[0]

def test_scenarios():
    assert run(dict(batch="SP240165", product_text="PANTOSHANG-40 Pantoprazole Gastro-Resistant Tablets IP", mfg="2024-06", exp="2026-05", maker="Shangrila Industries (P) Ltd.")) == "FLAGGED"
    assert run(dict(batch="B3T2305", product_text="DEMO-650 Paracetamol Tablets IP 650 mg", mfg="2025-01", exp="2027-12", maker="Demo Remedies Pvt. Ltd.")) == "ASK"
    assert run(dict(batch="T24H459A", product_text="Telma 40 Telmisartan Tablets IP 40 mg", mfg="2024-03", exp="2027-02", maker="Glenmark Pharmaceuticals Ltd.")) == "NOT_LISTED"
    assert run(dict(batch="TC2439", product_text="Cefixime Dispersible Tablets IP 200 mg", mfg="2024-10", exp="2027-03", maker="")) == "SUSPECTED_FAKE"
    assert run(dict(batch="GJ-2309", product_text="Gentamicin Injection IP 30 ml", mfg="2024-02", exp="2026-01", maker="")) == "SUSPECTED_FAKE"
    assert run(dict(batch="SP240165", product_text="PANTOSHANG-40 Pantoprazole Gastro-Resistant Tablets IP", mfg=None, exp=None, maker="")) == "ASK"
    assert run(dict(batch="DOBS3975", product_text="Dolo 650 Paracetamol Tablets IP", mfg="2025-03", exp="2028-02", maker="Micro Labs Ltd")) == "NOT_LISTED"

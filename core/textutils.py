import re, itertools
from rapidfuzz import fuzz

MONTHS = {m: i for i, m in enumerate(["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"], 1)}
PLACEHOLDERS = {"", "-", "--", "na", "n/a", "nm", "not mentioned", "notmentioned", "nil", "none"}

def parse_month_year(s):
    """'06/2024','6-2024','Jun-24','JUN 2024','June, 2024','Apr--2026','Oct/2023','01/07/2024','JUN.26' -> 'YYYY-MM' or None."""
    if s is None: return None
    t = str(s).strip().lower().replace("–", "-").replace("—", "-")          # v2: em dash too
    if t in PLACEHOLDERS: return None
    m = re.search(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b", t)          # DD/MM/YYYY
    if m and 1 <= int(m.group(2)) <= 12: return f"{m.group(3)}-{int(m.group(2)):02d}"
    m = re.search(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2})\b", t)          # v2: DD/MM/YY
    if m and 1 <= int(m.group(1)) <= 31 and 1 <= int(m.group(2)) <= 12: return f"20{m.group(3)}-{int(m.group(2)):02d}"
    m = re.search(r"\b(\d{1,2})\s*[/\-.]\s*(\d{4}|\d{2})\b", t)               # MM/YYYY or MM/YY
    if m and 1 <= int(m.group(1)) <= 12:
        y = m.group(2); y = "20" + y if len(y) == 2 else y
        return f"{y}-{int(m.group(1)):02d}"
    m = re.search(r"\b([a-z]{3})[a-z]*\.?\s*[,/\-.]*\s*'?(\d{4}|\d{2})\b", t)  # Mon-YY / Month YYYY / JUN.26
    if m and m.group(1) in MONTHS:
        y = m.group(2); y = "20" + y if len(y) == 2 else y
        return f"{y}-{MONTHS[m.group(1)]:02d}"
    return None

def batch_key(s):
    return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())

def squash(s): return re.sub(r"[^a-z]", "", str(s or "").lower())

HEADER_SYNONYMS = {
    "sno": ["sno", "slno", "srno", "serialno"],
    "product": ["productdrugname", "nameofproduct", "nameofthedrug", "nameofdrugs", "productname", "drugname", "product"],
    "batch": ["batchno", "batchnumber", "batch", "lotno"],
    "mfg": ["manufacturingdate", "mfgdate", "dateofmanufacture", "manufacturingdates"],
    "exp": ["expirydate", "expdate", "dateofexpiry"],
    "maker": ["manufacturedby", "manufacturerdetails", "nameofmanufacturer", "manufacturer"],
    "result": ["nsqresult", "reasonfornsq", "result", "remarks", "testresult"],
    "reported_by": ["reportedbycdscolaboratory", "reportedbystatelaboratory", "reportingbylabstate", "reportedby", "drawnby", "laboratory"],
    "source_level": ["reportingsource"],
    "list_month": ["reportingmonthyear", "reportingmonth"],
}
def map_headers(cells):
    out = {}
    for i, c in enumerate(cells):
        sq = squash(c)
        for field, syns in HEADER_SYNONYMS.items():
            if field in out.values(): continue
            if sq in syns or any(sq.startswith(x) for x in syns if len(x) >= 5):
                out[i] = field; break
    return out

def split_portal_dates(s):
    m1 = re.search(r"manufacturing\s*date\s*:?\s*([A-Za-z0-9/\-. ]+?)(?=expiry|$)", s, re.I)
    m2 = re.search(r"expiry\s*date\s*:?\s*([A-Za-z0-9/\-. ]+)", s, re.I)
    return (parse_month_year(m1.group(1)) if m1 else None, parse_month_year(m2.group(1)) if m2 else None)

def maker_name(raw):
    t = re.sub(r"\s+", " ", str(raw or "")).strip()
    if "under investigation" in t.lower(): return "Under Investigation"
    m = re.search(r"manufactured\s*by\s*:\s*(.+)$", t, re.I) or re.search(r"manufacturer\s*name\s*:\s*(.+)$", t, re.I)
    if m: t = m.group(1)
    t = re.split(r"\b(?:mkt\.?\s*by|marketed\s*by|manufa?c?tu?red\s*for)\b", t, flags=re.I)[0]
    t = re.sub(r"^m\s*/\s*s\.?\s*", "", t, flags=re.I)
    return t.split(",")[0].strip(" .;:")

def entry_type(result, remarks="", maker="", list_kind=""):
    blob = f"{result} {remarks} {list_kind}".lower()
    if "spurious" in blob or "under investigation" in str(maker).lower(): return "SPURIOUS"
    if "misbrand" in blob: return "MISBRANDED"
    if "adulterat" in blob: return "ADULTERATED"
    return "NSQ"

# v2: labels must not match inside words ("Lotion", "Batchwise")
BATCH_RE = re.compile(r"(?:\bB\.?\s?No\b\.?|\bBatch(?=\W|No|Number|$)(?:\s*No\.?|\s*Number)?|\bLot(?=\W|No|$)(?:\s*No\.?)?|\bBN\b|\bB\.N\.)\s*[:.\-]?\s*([A-Z0-9][A-Z0-9\-/]{2,19})", re.I)
# v2: label and value on separate OCR lines
LABEL_ONLY_RE = re.compile(r"^\s*(?:B\.?\s?No\b\.?|Batch(?:\s*No\.?|\s*Number)?|Lot(?:\s*No\.?)?|BN|B\.N\.)\s*[:.\-]?\s*$", re.I)
NEXT_TOKEN_RE = re.compile(r"^\s*(?=[A-Z0-9\-/]*\d)([A-Z0-9][A-Z0-9\-/]{2,19})\b", re.I)
def find_batch(lines):
    for i, ln in enumerate(lines):
        m = BATCH_RE.search(ln)
        if m: return m.group(1).rstrip("-/"), i
        if LABEL_ONLY_RE.match(ln) and i + 1 < len(lines):
            m2 = NEXT_TOKEN_RE.match(lines[i + 1])
            if m2: return m2.group(1).rstrip("-/"), i + 1
    return None, None

CONFUSABLE = {"0": "OQDC", "O": "0QDC", "Q": "O0", "D": "0O", "C": "0O", "1": "IL7T", "I": "1L", "L": "1I", "T": "17",
              "7": "1T", "2": "Z", "Z": "2", "3": "8B", "8": "B3", "B": "83", "4": "A", "A": "4", "5": "S", "S": "5",
              "6": "G", "G": "6", "9": "G"}
def confusion_variants(key, max_subs=2):
    pos = [i for i, c in enumerate(key) if c in CONFUSABLE]
    for n in range(1, max_subs + 1):
        for idx in itertools.combinations(pos, n):
            for repl in itertools.product(*[CONFUSABLE[key[i]] for i in idx]):
                v = list(key)
                for i, r in zip(idx, repl): v[i] = r
                yield "".join(v), [(i, key[i], r) for i, r in zip(idx, repl)]

STOP = set("tablets tablet tab tabs capsules capsule cap caps injection inj ip bp usp mg ml mcg gm g w v and the of for "
           "syrup suspension oral solution sterile film coated gastro resistant gastroresistant prolonged release "
           "er sr xr dr dispersible each contains vial ampoule "
           "extended modified controlled delayed immediate sustained".split())       # v2: release descriptors
def name_tokens(s):
    s = re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower().replace("-", " "))
    return [t for t in s.split() if t not in STOP and not t.isdigit() and len(t) > 1]
def product_coverage(entry_product, pack_text):
    e, p = name_tokens(entry_product), name_tokens(pack_text)
    if not e or not p: return None
    hit = sum(1 for t in e if max(fuzz.ratio(t, q) for q in p) >= 85)
    return hit / len(e)

GS1_AI = {"01": "gtin", "10": "batch", "11": "mfg", "17": "exp", "21": "serial"}
def parse_qr_payload(txt):
    out = {}
    if not txt: return out
    for ai, val in re.findall(r"\((\d{2})\)([^()]+)", txt):
        if ai in GS1_AI: out[GS1_AI[ai]] = val.strip()
    if not out and re.match(r"^\]?(?:d2|Q3)?01\d{14}", txt):
        rest = re.sub(r"^\](?:d2|Q3)", "", txt)
        while rest:
            ai = rest[:2]
            if ai in ("01",): out["gtin"], rest = rest[2:16], rest[16:]
            elif ai in ("11", "17"): out[GS1_AI[ai]], rest = rest[2:8], rest[8:]
            elif ai in ("10", "21"):
                val, _, rest = rest[2:].partition("\x1d"); out[GS1_AI[ai]] = val
            else: break
    for k in ("mfg", "exp"):
        v = out.get(k)
        if v and re.fullmatch(r"\d{6}", v): out[k] = f"20{v[:2]}-{v[2:4]}"
    if "batch" not in out:
        m = re.search(r"(?:batch\s*(?:no\.?|number)?|b\.?\s?no\.?|lot\s*(?:no\.?)?)\s*[:#.\-]?\s*([A-Z0-9][A-Z0-9\-/]{2,19})", txt, re.I)
        if m: out["batch"] = m.group(1)
        for k, pat in (("mfg", r"(?:mfg|mfd|manufactur\w*)\s*(?:date|dt)?\s*[:.\-]?\s*([A-Za-z0-9/\-. ]{4,12})"),
                       ("exp", r"(?:exp\w*)\s*(?:date|dt)?\s*[:.\-]?\s*([A-Za-z0-9/\-. ]{4,12})")):
            m = re.search(pat, txt, re.I)
            if m and parse_month_year(m.group(1)): out[k] = parse_month_year(m.group(1))
    return out

DATE_TXT = r"([A-Za-z]{3,9}\.?[\s\-/.,']*\d{2,4}|\d{1,2}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{4}|\d{1,2}\s*[/\-.]\s*\d{2,4})"
MFG_RE = re.compile(r"\b(?:Mfg|Mfd|MFD|Manufacturing|Mfg\.?\s*Date|Date\s*of\s*Mfg)\b\.?\s*(?:Date|Dt)?\.?\s*[:\-]?\s*(?!by\b)" + DATE_TXT, re.I)
EXP_RE = re.compile(r"\b(?:Exp|Expiry|Use\s*before|Best\s*before)\b\.?\s*(?:Date|Dt)?\.?\s*[:\-]?\s*" + DATE_TXT, re.I)
MAKER_RE = re.compile(r"\b(?:Mfd\.?\s*by|Mfg\.?\s*by|Manufactured\s*by)\s*[:\-]?\s*(.+)", re.I)
MKT_RE = re.compile(r"\b(?:Mkt\.?\s*by|Marketed\s*by)\s*[:\-]?\s*(.+)", re.I)

def find_dates(lines):
    text = " | ".join(lines)
    m1, m2 = MFG_RE.search(text), EXP_RE.search(text)
    return (parse_month_year(m1.group(1)) if m1 else None, parse_month_year(m2.group(1)) if m2 else None)

def find_party(lines, rx):
    for ln in lines:
        m = rx.search(ln)
        if m: return m.group(1).strip(" ,.;:")
    return None

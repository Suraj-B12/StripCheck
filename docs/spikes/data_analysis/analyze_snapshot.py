"""Exploratory statistics on the CDSCO SUGAM snapshot (design + paper numbers). Not project code."""
import json, re, sys, pathlib, statistics, itertools
from collections import Counter, defaultdict

SNAP = pathlib.Path(sys.argv[1])

MONTHS = {m: i for i, m in enumerate(["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"], 1)}
PLACEHOLDERS = {"", "-", "--", "na", "n/a", "nm", "not mentioned", "notmentioned", "nil", "none"}

def parse_month_year(s):
    if s is None: return None
    t = str(s).strip().lower().replace("–", "-")
    if t in PLACEHOLDERS: return None
    m = re.search(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b", t)
    if m and 1 <= int(m.group(2)) <= 12: return f"{m.group(3)}-{int(m.group(2)):02d}"
    m = re.search(r"\b(\d{1,2})\s*[/\-.]\s*(\d{4}|\d{2})\b", t)
    if m and 1 <= int(m.group(1)) <= 12:
        y = m.group(2); y = "20" + y if len(y) == 2 else y
        return f"{y}-{int(m.group(1)):02d}"
    m = re.search(r"\b([a-z]{3})[a-z]*\.?\s*[,/\-.]*\s*'?(\d{4}|\d{2})\b", t)
    if m and m.group(1) in MONTHS:
        y = m.group(2); y = "20" + y if len(y) == 2 else y
        return f"{y}-{MONTHS[m.group(1)]:02d}"
    return None

def batch_key(s): return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())

CONFUSABLE = {"0": "OQDC", "O": "0QDC", "Q": "O0", "D": "0O", "C": "0O", "1": "IL7T", "I": "1L", "L": "1I", "T": "17",
              "7": "1T", "2": "Z", "Z": "2", "3": "8B", "8": "B3", "B": "83", "4": "A", "A": "4", "5": "S", "S": "5",
              "6": "G", "G": "6", "9": "G"}
def variants1(key):
    for i, c in enumerate(key):
        for r in CONFUSABLE.get(c, ""):
            yield key[:i] + r + key[i+1:]

STOP = set("tablets tablet tab tabs capsules capsule cap caps injection inj ip bp usp mg ml mcg gm g w v and the of for "
           "syrup suspension oral solution sterile film coated gastro resistant gastroresistant prolonged release "
           "er sr xr dr dispersible each contains vial ampoule".split())
def name_tokens(s):
    s = re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower().replace("-", " "))
    return [t for t in s.split() if t not in STOP and not t.isdigit() and len(t) > 1]

def ym_index(ym):
    y, m = ym.split("-"); return int(y) * 12 + int(m) - 1

rows = []
for f in sorted(SNAP.glob("*.json")):
    tab, y, mon = f.stem.split("_")
    data = json.loads(f.read_bytes().decode("latin-1")).get("aaData", [])
    for r in data:
        rep = f"{y}-{MONTHS[mon.lower()]:02d}"
        product = r.get("str_product_name") or r.get("product_name_from_dtl") or ""
        result = (r.get("str_nsq_result") or "") + " " + (r.get("str_nsq_remarks") or "")
        rows.append({
            "tab": tab, "report": rep, "product": product.strip(), "brand": (r.get("str_brand_name") or "").strip(),
            "batch_raw": r.get("str_batch_no") or "", "key": batch_key(r.get("str_batch_no")),
            "mfg": parse_month_year(r.get("dt_manufacturing_date")), "exp": parse_month_year(r.get("dt_expiry_date")),
            "mfg_raw": r.get("dt_manufacturing_date"), "exp_raw": r.get("dt_expiry_date"),
            "maker": (r.get("str_manufactured_by") or "").strip(), "result": result.strip(),
            "source": (r.get("str_reporting_source") or "").strip(), "lab": (r.get("str_reported_by_lab_or_state") or "").strip(),
            "spurious": tab == "spurious" or "spurious" in result.lower(),
        })

print(f"TOTAL rows: {len(rows)}  (nsq tab {sum(r['tab']=='nsq' for r in rows)}, spurious tab {sum(r['tab']=='spurious' for r in rows)})")
months = Counter(r["report"] for r in rows if r["tab"] == "nsq")
print(f"NSQ months covered: {len(months)}  first {min(months)}  last {max(months)}")
by_year = Counter(r["report"][:4] for r in rows if r["tab"] == "nsq")
print("NSQ rows by year:", dict(sorted(by_year.items())))
mc = sorted(months.values())
print(f"rows/month: min {mc[0]} median {statistics.median(mc)} max {mc[-1]}")
print("spurious-tab rows by month:", dict(sorted(Counter(r['report'] for r in rows if r['tab']=='spurious').items())))
print("rows mentioning spurious (any tab):", sum(r["spurious"] for r in rows))
src = Counter(re.sub(r"s$", "", r["source"].lower()) for r in rows)
print("reporting source variants:", src.most_common(8))
print("brand present share (nsq):", round(sum(1 for r in rows if r['tab']=='nsq' and r['brand'].lower() not in ('', 'na', 'nil', '-'))/max(1,sum(r['tab']=='nsq' for r in rows)), 3))

# batch keys
keys = [r["key"] for r in rows]
lens = Counter(len(k) for k in keys)
print("batch key length dist:", dict(sorted(lens.items())))
print("empty/placeholder batch share:", round(sum(1 for r in rows if not r['key'] or r['batch_raw'].strip().lower() in PLACEHOLDERS)/len(rows), 4))
print("short keys (<4) share:", round(sum(1 for k in keys if 0 < len(k) < 4)/len(keys), 4))
print("weird batch examples:", [r["batch_raw"] for r in rows if re.search(r"[^A-Za-z0-9\-/ .]", r["batch_raw"])][:12])

# exact collisions: same key, different product token sets
idx = defaultdict(list)
for r in rows:
    if r["key"]: idx[r["key"]].append(r)
multi = {k: v for k, v in idx.items() if len(v) > 1}
def prod_sig(r): return frozenset(name_tokens(r["product"]))
coll = {k: v for k, v in multi.items() if len({prod_sig(r) for r in v}) > 1 and not any(prod_sig(a) & prod_sig(b) for a, b in itertools.combinations(v, 2))}
same_prod_repeat = {k: v for k, v in multi.items() if len({prod_sig(r) for r in v}) == 1}
print(f"distinct keys: {len(idx)}  keys listed >1 time: {len(multi)}  same-product repeats: {len(same_prod_repeat)}  disjoint-product collisions: {len(coll)}")
print("collision examples:", [(k, [x['product'][:40] for x in v][:3]) for k, v in list(coll.items())[:6]])

# confusable neighbours (1 substitution) inside the index
with_nb = 0; nb_same_maker = 0; examples = []
mk = lambda r: re.sub(r"[^a-z]", "", r["maker"].lower())[:18]
for k, v in idx.items():
    nbs = [n for n in set(variants1(k)) if n in idx and n != k]
    if nbs:
        with_nb += 1
        if any(mk(a) == mk(b) and mk(a) for a in v for n in nbs for b in idx[n]):
            nb_same_maker += 1
            if len(examples) < 8: examples.append((k, nbs[:3], v[0]["product"][:30]))
print(f"keys with a 1-confusable-substitution neighbour in index: {with_nb} ({with_nb/len(idx):.2%}); same maker: {nb_same_maker} ({nb_same_maker/len(idx):.2%})")
print("sibling examples:", examples)

# lag and remaining shelf life
lag = [ym_index(r["report"]) - ym_index(r["mfg"]) for r in rows if r["mfg"]]
rem = [ym_index(r["exp"]) - ym_index(r["report"]) for r in rows if r["exp"]]
q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
print(f"lag mfg->alert months: n={len(lag)} median {statistics.median(lag)} IQR {q(lag,.25)}-{q(lag,.75)}  p90 {q(lag,.9)}  negative(mfg after alert) {sum(1 for x in lag if x < 0)}")
print(f"remaining shelf life at alert months: n={len(rem)} median {statistics.median(rem)} IQR {q(rem,.25)}-{q(rem,.75)}; share >=12 months left {sum(1 for x in rem if x >= 12)/len(rem):.2%}; already expired {sum(1 for x in rem if x < 0)/len(rem):.2%}")
print("date parse failure share (mfg/exp):", round(sum(1 for r in rows if not r['mfg'])/len(rows), 4), round(sum(1 for r in rows if not r['exp'])/len(rows), 4))
print("mfg after exp:", sum(1 for r in rows if r['mfg'] and r['exp'] and r['mfg'] > r['exp']))
print("unparsed date examples:", list({r['mfg_raw'] for r in rows if not r['mfg']})[:15])

# failure categories
CATS = [("dissolution", "dissolution"), ("assay/content", r"assay|content"), ("description", "description"), ("identification", "identification"),
        ("disintegration", "disintegration"), ("sterility", "sterility"), ("particulate", "particulate"), ("BET/endotoxin", r"\bbet\b|endotoxin"),
        ("microbial", "microb"), ("uniformity", "uniformity"), ("pH", r"\bph\b"), ("labelling/misbranded", r"label|misbrand"), ("weight", "weight")]
cc = Counter()
for r in rows:
    t = r["result"].lower()
    for name, pat in CATS:
        if re.search(pat, t): cc[name] += 1
print("failure categories (multi-label):", cc.most_common())
print("top labs/states:", Counter(r["lab"] for r in rows).most_common(10))

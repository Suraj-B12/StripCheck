"""Move the 25 Oct 2026 design-phase portal snapshot into the spec v2 layout and write preliminary paper macros.

Usage: python import_snapshot.py <snapshot_dir> <repo_root> [--no-stats]
Writes data/raw/portal/{nsq,spurious}/YYYY-MM.json (+ .meta.json) and, unless --no-stats is given,
paper/generated/stats.tex (owned by the Integrator; the Builder always passes --no-stats).
M1's `cli.py sync` / `cli.py stats` replace both with database-backed versions.
"""
import hashlib, json, pathlib, re, shutil, statistics, sys, itertools
from collections import Counter, defaultdict

SNAP, ROOT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
BASE = "https://cdscoonline.gov.in/CDSCO"
MON = {m: i for i, m in enumerate(["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"], 1)}

# ---- 1. copy into data/raw/portal/{tab}/YYYY-MM.json with metadata ----------------------------
rows = []
for f in sorted(SNAP.glob("*.json")):
    tab, y, mon = f.stem.split("_")
    ym = f"{y}-{MON[mon]:02d}"
    raw = f.read_bytes()
    dest = ROOT / "data" / "raw" / "portal" / tab / f"{ym}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(f, dest)
    data = json.loads(raw.decode("latin-1")).get("aaData", [])
    endpoint = "filteredNsqDrugTable" if tab == "nsq" else "filteredSpuriousDrugTable"
    meta = {"url": f"{BASE}/{endpoint}?month={mon}-{y}&source=All&tab={tab}", "fetched_at": "2026-10-25",
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "rows": len(data), "encoding": "latin-1",
            "note": "design-phase snapshot (1.5 s between requests)"}
    dest.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    for r in data:
        rows.append((tab, ym, r))

# ---- 2. statistics (same definitions as analyze_snapshot.py) --------------------------------
MONTHS = {m.lower(): i for m, i in MON.items()}
PLACEHOLDERS = {"", "-", "--", "na", "n/a", "nm", "not mentioned", "notmentioned", "nil", "none"}
def parse_month_year(s):
    if s is None: return None
    t = str(s).strip().lower().replace("–", "-")
    if t in PLACEHOLDERS: return None
    m = re.search(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b", t)
    if m and 1 <= int(m.group(2)) <= 12: return f"{m.group(3)}-{int(m.group(2)):02d}"
    m = re.search(r"\b(\d{1,2})\s*[/\-.]\s*(\d{4}|\d{2})\b", t)
    if m and 1 <= int(m.group(1)) <= 12:
        yy = m.group(2); yy = "20" + yy if len(yy) == 2 else yy
        return f"{yy}-{int(m.group(1)):02d}"
    m = re.search(r"\b([a-z]{3})[a-z]*\.?\s*[,/\-.]*\s*'?(\d{4}|\d{2})\b", t)
    if m and m.group(1) in MONTHS:
        yy = m.group(2); yy = "20" + yy if len(yy) == 2 else yy
        return f"{yy}-{MONTHS[m.group(1)]:02d}"
    return None
def batch_key(s): return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())
CONFUSABLE = {"0": "OQDC", "O": "0QDC", "Q": "O0", "D": "0O", "C": "0O", "1": "IL7T", "I": "1L", "L": "1I", "T": "17",
              "7": "1T", "2": "Z", "Z": "2", "3": "8B", "8": "B3", "B": "83", "4": "A", "A": "4", "5": "S", "S": "5",
              "6": "G", "G": "6", "9": "G"}
STOP = set("tablets tablet tab tabs capsules capsule cap caps injection inj ip bp usp mg ml mcg gm g w v and the of for "
           "syrup suspension oral solution sterile film coated gastro resistant gastroresistant prolonged release "
           "er sr xr dr dispersible each contains vial ampoule".split())
def name_tokens(s):
    s = re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower().replace("-", " "))
    return [t for t in s.split() if t not in STOP and not t.isdigit() and len(t) > 1]
def ym_index(ym): yy, mm = ym.split("-"); return int(yy) * 12 + int(mm) - 1

recs = []
for tab, ym, r in rows:
    product = r.get("str_product_name") or r.get("product_name_from_dtl") or ""
    recs.append({"tab": tab, "report": ym, "key": batch_key(r.get("str_batch_no")), "product": product,
                 "brand": (r.get("str_brand_name") or "").strip(), "maker": r.get("str_manufactured_by") or "",
                 "mfg": parse_month_year(r.get("dt_manufacturing_date")), "exp": parse_month_year(r.get("dt_expiry_date")),
                 "source": (r.get("str_reporting_source") or "").lower(),
                 "spurious": tab == "spurious" or "spurious" in f"{r.get('str_nsq_result')} {r.get('str_nsq_remarks')}".lower()})
nsq = [x for x in recs if x["tab"] == "nsq"]
months = Counter(x["report"] for x in nsq)
by_year = Counter(x["report"][:4] for x in nsq)
idx = defaultdict(list)
for x in recs:
    if x["key"]: idx[x["key"]].append(x)
sig = lambda x: frozenset(name_tokens(x["product"]))
multi = {k: v for k, v in idx.items() if len(v) > 1}
coll = {k for k, v in multi.items() if len({sig(x) for x in v}) > 1 and not any(sig(a) & sig(b) for a, b in itertools.combinations(v, 2))}
mk = lambda x: re.sub(r"[^a-z]", "", x["maker"].lower())[:18]
def variants1(k):
    for i, c in enumerate(k):
        for rr in CONFUSABLE.get(c, ""): yield k[:i] + rr + k[i + 1:]
nb = sib = 0
for k, v in idx.items():
    ns = [n for n in set(variants1(k)) if n in idx and n != k]
    if ns:
        nb += 1
        if any(mk(a) and mk(a) == mk(b) for a in v for n in ns for b in idx[n]): sib += 1
lag = [ym_index(x["report"]) - ym_index(x["mfg"]) for x in recs if x["mfg"]]
rem = [ym_index(x["exp"]) - ym_index(x["report"]) for x in recs if x["exp"]]
q = lambda xs, p: sorted(xs)[int(p * (len(xs) - 1))]
fmt = lambda n: f"{n:,}".replace(",", "{,}")
pct = lambda a, b: f"{100 * a / b:.1f}"

macros = {
    "SnapshotDate": "25 October 2026",
    "NumAlertRows": fmt(len(recs)), "NumNsqRows": fmt(len(nsq)), "NumSpuriousTabRows": fmt(len(recs) - len(nsq)),
    "NumMonths": str(len(months)), "FirstMonth": "January 2019", "LastMonth": "September 2026",
    "RowsPerMonthMin": str(min(months.values())), "RowsPerMonthMedian": f"{statistics.median(months.values()):g}",
    "RowsPerMonthMax": str(max(months.values())),
    "RowsYearFirst": fmt(by_year["2019"]), "RowsYearTwentyFour": fmt(by_year["2024"]), "RowsYearTwentyFive": fmt(by_year["2025"]),
    "RowsYearTwentySix": fmt(by_year["2026"]),
    "RowsStateLabs": fmt(sum(1 for x in recs if "state" in x["source"])), "RowsCentralLabs": fmt(sum(1 for x in recs if "cdsco" in x["source"])),
    "BrandPresentPct": pct(sum(1 for x in nsq if x["brand"].lower() not in ("", "na", "nil", "-")), len(nsq)),
    "SpuriousMentions": fmt(sum(x["spurious"] for x in recs)),
    "DistinctKeys": fmt(len(idx)), "RepeatedKeys": fmt(len(multi)), "CollisionKeys": fmt(len(coll)),
    "ShortKeyPct": pct(sum(1 for x in recs if 0 < len(x["key"]) < 4), len(recs)),
    "NeighbourKeys": fmt(nb), "NeighbourKeysPct": f"{100 * nb / len(idx):.2f}",
    "SiblingKeys": fmt(sib), "SiblingKeysPct": f"{100 * sib / len(idx):.2f}",
    "LagMedian": f"{statistics.median(lag):g}", "LagQOne": str(q(lag, .25)), "LagQThree": str(q(lag, .75)), "LagPNinety": str(q(lag, .9)),
    "ShelfMedian": f"{statistics.median(rem):g}", "ShelfQOne": str(q(rem, .25)), "ShelfQThree": str(q(rem, .75)),
    "ShelfTwelvePlusPct": pct(sum(1 for d in rem if d >= 12), len(rem)), "ExpiredAtAlertPct": pct(sum(1 for d in rem if d < 0), len(rem)),
    "MissingDatePct": pct(sum(1 for x in recs if not x["mfg"]), len(recs)),
}
if "--no-stats" in sys.argv:
    print(f"copied {len(set((t, m) for t, m, _ in rows))} monthly files, {len(recs)} rows; stats.tex not written (--no-stats)")
    raise SystemExit(0)
out = ROOT / "paper" / "generated" / "stats.tex"
out.parent.mkdir(parents=True, exist_ok=True)
lines = ["% GENERATED FILE. Do not edit by hand.",
         "% Source: design-phase snapshot of the CDSCO SUGAM portal (docs/spikes/data_analysis/import_snapshot.py).",
         "% Replaced in M1 by `python cli.py stats`, which reads the ingested database."]
lines += [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in macros.items()]
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"copied {len(set((t, m) for t, m, _ in rows))} monthly files, {len(recs)} rows; wrote {out}")
for k, v in macros.items(): print(f"  {k} = {v}")

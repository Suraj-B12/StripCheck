"""One-off polite snapshot of the CDSCO SUGAM NSQ/spurious JSON endpoints for design analysis (not project code)."""
import json, sys, time, pathlib, urllib.request, urllib.parse

BASE = "https://cdscoonline.gov.in/CDSCO"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) StripCheck-research/0.1 (college project; polite snapshot)"
OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)


def get(path, **params):
    url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            time.sleep(1.5)
            return raw
        except Exception as e:  # noqa: BLE001
            print(f"  retry {attempt + 1} {url}: {type(e).__name__} {e}")
            time.sleep(5)
    return None


for tab in ("nsq", "spurious"):
    years = json.loads(get("reportingYears", tab=tab).decode("latin-1"))
    for y in years:
        months = json.loads(get("publicReportingMonths", year=y, tab=tab).decode("latin-1"))
        for m in months:
            key = f"{m.upper()}-{y}"
            dest = OUT / f"{tab}_{y}_{m.upper()}.json"
            if dest.exists():
                continue
            endpoint = "filteredNsqDrugTable" if tab == "nsq" else "filteredSpuriousDrugTable"
            raw = get(endpoint, month=key, source="All", tab=tab)
            if raw is None:
                print(f"FAILED {tab} {key}")
                continue
            dest.write_bytes(raw)
            try:
                n = len(json.loads(raw.decode("latin-1")).get("aaData", []))
            except Exception:  # noqa: BLE001
                n = -1
            print(f"{tab} {key}: {n} rows, {len(raw)} bytes")
print("done")

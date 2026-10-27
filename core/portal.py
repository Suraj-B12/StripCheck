"""Polite public CDSCO sync, immutable snapshots, and offline re-import."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from core import config, db
from core.ingest import ingest_snapshots, atomic_write, archive_snapshot, _snapshot_rows

MONTHS = {name: number for number, name in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split(), 1)}
_request_lock = threading.Lock()
_sync_lock = threading.Lock()
_last_request = 0.0

def _request(endpoint, **params):
    """Every attempted request is paced; TLS stays enabled and failures are bounded."""
    global _last_request
    url = f"{config.PORTAL_URL}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    error = None
    for attempt in range(3):
        with _request_lock:
            pause = max(0, config.SYNC_DELAY - (time.monotonic() - _last_request))
            if pause:
                time.sleep(pause)
            _last_request = time.monotonic()
            try:
                if sys.platform == "darwin" and shutil.which("curl"):
                    # Apple's curl uses the system trust store; verification remains on.
                    # This also supports managed Macs whose enterprise root is in Keychain.
                    result = subprocess.run([shutil.which("curl"), "--fail", "--silent", "--show-error", "--location",
                                             "--proto", "=https", "--proto-redir", "=https",
                                             "--max-time", str(config.NETWORK_TIMEOUT), "--max-filesize", "16777216",
                                             "--user-agent", "StripCheck/2.0 (academic project)", "--header", "Accept: application/json", url],
                                            capture_output=True, timeout=config.NETWORK_TIMEOUT + 3, check=True)
                    raw = result.stdout
                else:
                    request = urllib.request.Request(url, headers={"User-Agent": "StripCheck/2.0 (academic project)", "Accept": "application/json"})
                    with urllib.request.urlopen(request, timeout=config.NETWORK_TIMEOUT) as response:
                        raw = response.read(16 * 1024 * 1024 + 1)
                if len(raw) > 16 * 1024 * 1024:
                    raise ValueError("Portal response exceeds the 16 MB limit")
                value = json.loads(raw.decode("latin-1"))
                return raw, value, url
            except (OSError, ValueError, urllib.error.URLError, subprocess.SubprocessError) as exc:
                error = exc
        if attempt < 2:
            time.sleep(attempt + 1)
    raise RuntimeError(f"CDSCO source unavailable: {type(error).__name__}: {error}")

def discover_months(tab, full=False):
    _, years, _ = _request("reportingYears", tab=tab)
    if not isinstance(years, list):
        raise ValueError("CDSCO returned an unexpected years response")
    years = sorted({str(year) for year in years if re.fullmatch(r"(?:19|20)\d{2}", str(year))}, reverse=True)[:20]
    found = set()
    for year in years:
        _, months, _ = _request("publicReportingMonths", year=year, tab=tab)
        if not isinstance(months, list):
            raise ValueError("CDSCO returned an unexpected months response")
        for month in months:
            mon = str(month).strip().upper()[:3]
            if mon in MONTHS:
                found.add((f"{year}-{MONTHS[mon]:02d}", f"{mon}-{year}"))
        if not full and len(found) >= 3:
            break
    found = sorted(found, reverse=True)
    return found[:240] if full else found[:3]

def fetch_month(tab, month, request_month):
    if tab not in {"nsq", "spurious"} or not re.fullmatch(r"(?:19|20)\d{2}-(?:0[1-9]|1[0-2])", month):
        raise ValueError("Choose a valid portal kind and YYYY-MM month")
    expected_month = f"{next(name for name, number in MONTHS.items() if number == int(month[5:]))}-{month[:4]}"
    if request_month != expected_month:
        raise ValueError("Requested portal month does not match the stored source month")
    endpoint = "filteredNsqDrugTable" if tab == "nsq" else "filteredSpuriousDrugTable"
    raw, value, url = _request(endpoint, month=request_month, source="All", tab=tab)
    if not isinstance(value, dict) or not isinstance(value.get("aaData"), list):
        raise ValueError("CDSCO returned an unexpected alert response; existing data retained")
    rows = _snapshot_rows(raw)
    folder = config.DATA_DIR / "raw" / "portal" / tab
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / f"{month}.json"
    digest = hashlib.sha256(raw).hexdigest()
    unchanged = dest.exists() and dest.stat().st_size == len(raw) and hashlib.sha256(dest.read_bytes()).hexdigest() == digest
    # Content-addressed originals survive future revisions of the same month.
    archive_snapshot(raw, digest)
    atomic_write(dest, raw)
    metadata = {"url": url, "fetched_at": db.now(), "sha256": digest,
                "bytes": len(raw), "rows": len(rows), "encoding": "latin-1", "month": month, "kind": tab}
    atomic_write(dest.with_suffix(".meta.json"), json.dumps(metadata, indent=2).encode("utf-8"))
    return {"month": month, "kind": tab, "rows": metadata["rows"], "unchanged": unchanged, "sha256": digest}

def sync(callback=None, offline=False, full=False):
    """Fetch latest three published months per tab (full=True: history), then ingest.

    callback receives {type,message,...}; report has fetched, sources, added,
    quarantined, errors, offline, status, started_at, finished_at and stats.
    Network failures preserve cached records and still attempt offline ingestion.
    """
    if not _sync_lock.acquire(blocking=False):
        return {"status": "busy", "message": "A sync is already running", "added": 0, "errors": []}
    started = db.now()
    fetched, errors = [], []
    offline = bool(offline or config.OFFLINE)
    def emit(typ, message, **extra):
        if callback:
            callback({"type": typ, "message": message, **extra})
    try:
        db.init_db()
        emit("started", "Reading stored snapshots" if offline else "Connecting to the CDSCO public portal")
        if not offline:
            for tab in ("nsq", "spurious"):
                try:
                    months = discover_months(tab, full=full)
                    for month, request_month in months:
                        emit("fetching", f"Downloading {tab.upper()} {month}", month=month, kind=tab)
                        fetched.append(fetch_month(tab, month, request_month))
                except (OSError, RuntimeError, ValueError) as exc:
                    errors.append({"source": tab, "error": str(exc)})
                    emit("warning", f"{tab.upper()} source could not be refreshed; stored snapshots remain available")
        report = ingest_snapshots(callback)
        errors.extend(report.pop("errors", []))
        finished = db.now()
        status = "partial" if errors and db.stats()["has_data"] else "error" if errors else "complete"
        result = {**report, "fetched": fetched, "errors": errors, "offline": offline,
                  "status": status, "started_at": started, "finished_at": finished}
        if fetched and not errors:
            db.set_value("last_sync", finished)
        db.set_value("last_sync_attempt", finished)
        db.set_value("last_sync_report", result)
        result["stats"] = db.stats()
        emit("complete", f"Sync finished: {result['added']} new alert rows", added=result["added"], status=status)
        return result
    finally:
        _sync_lock.release()

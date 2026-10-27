"""Validate stored portal snapshots and retain their exact source provenance."""
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from core import config, db
from core.textutils import batch_key, entry_type, maker_name, parse_month_year

PLACEHOLDERS = {"", "na", "nm", "nil", "none", "notmentioned", "notavailable", "notapplicable", "notspecified", "notprovided", "notstated", "upto01"}
CLEANING_VERSION = "2.4"
MAX_SNAPSHOT_BYTES = 16 * 1024 * 1024
MAX_SNAPSHOT_ROWS = 100000

def atomic_write(path, content):
    """Replace a complete file on the same filesystem; never leave partial JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

def archive_snapshot(raw, digest):
    archive = config.DATA_DIR / "raw" / "archive" / f"{digest}.json"
    # Re-create a damaged content-addressed copy from the verified original.
    if not archive.exists() or archive.stat().st_size != len(raw) or hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
        atomic_write(archive, raw)
    return archive

def _snapshot_rows(raw, encoding="latin-1"):
    if len(raw) > MAX_SNAPSHOT_BYTES:
        raise ValueError("Snapshot exceeds the 16 MB import limit")
    if encoding not in {"latin-1", "iso-8859-1", "utf-8", "utf-8-sig"}:
        raise ValueError("Unsupported snapshot encoding")
    try:
        value = json.loads(raw.decode("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else encoding))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ValueError("Snapshot is not valid JSON in its declared encoding") from exc
    if isinstance(value, dict):
        if "aaData" not in value and "data" not in value:
            raise ValueError("Snapshot has no alert row list; existing alerts were retained")
        rows = value.get("aaData", value.get("data"))
    else:
        rows = value
    if not isinstance(rows, list):
        raise ValueError("The stored snapshot does not contain an alert row list")
    if len(rows) > MAX_SNAPSHOT_ROWS:
        raise ValueError("Snapshot exceeds the 100,000-row import limit; it was not truncated")
    return rows

def _text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def _descriptive(value, flags):
    """Repair only reversible UTF-8/Latin-1 mojibake in descriptive fields.

    Snapshot bytes and raw_json remain unchanged. Batch/date identifiers never
    pass through this function, and the repair is visible in the row's flags.
    """
    text = _text(value)
    if any(marker in text for marker in ("\u00c2", "\u00c3", "\u00e2", "\u00f0", "\u00ef", "\u00e0")):
        try:
            repaired = text.encode("latin-1").decode("utf-8")
            if repaired != text and repaired.encode("utf-8").decode("latin-1") == text:
                if "encoding_repaired" not in flags:
                    flags.append("encoding_repaired")
                return repaired
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return text

def _empty(value):
    cleaned = re.sub(r"[^a-z0-9]", "", _text(value).lower())
    return cleaned in PLACEHOLDERS or (bool(cleaned) and re.fullmatch(r"(?:nil|na)+", cleaned) is not None)

def _date(value):
    raw = _text(value)
    if re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", raw):
        return raw
    if re.match(r"\d{4}-(?:0[1-9]|1[0-2])-\d{2}", raw):
        return raw[:7]
    return parse_month_year(raw)

def _batch_is_date(value):
    """A date-like substring in a genuine identifier (e.g. SYN-03/24) is not a shifted date cell."""
    raw = _text(value)
    numeric = r"(?:\d{1,2}[/.\-]\d{2,4}|\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}|\d{4}-\d{2}(?:-\d{2})?)"
    named = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[\s/.,'\-]+\d{2,4}"
    if not re.fullmatch(f"(?:{numeric}|{named})", raw, re.I):
        return False
    date = _date(raw)
    return bool(date and 1900 <= int(date[:4]) <= 2100)

def clean_row(raw, month, kind="nsq"):
    """Return a list of cleaned rows (multi-batch cells expand) and validation reasons."""
    flags, reasons = [], []
    if any(isinstance(value, (dict, list)) for value in raw.values()):
        return [], ["unsupported_field_shape"]
    product = _descriptive(raw.get("str_product_name") or raw.get("product_name_from_dtl") or raw.get("product"), flags)
    brand = _descriptive(raw.get("str_brand_name") or raw.get("brand"), flags).strip("() ")
    tail = re.search(r"\((?:Brand\s*Name\s*:\s*)?([^()]+)\)\s*$", product, re.I)
    if _empty(brand):
        brand = ""
        if tail and re.search(r"[A-Za-z]", tail.group(1)) and not re.search(r"\b(?:mg|ml|mcg|w/w|w/v|tablets?|capsules?|IP|BP|USP)\b", tail.group(1), re.I):
            brand = tail.group(1).strip()
    product = re.sub(r"\s*\(Brand\s*Name\s*:[^()]+\)\s*$", "", product, flags=re.I)
    maker = _descriptive(raw.get("str_manufactured_by") or raw.get("str_manufacturer_name") or raw.get("maker") or raw.get("maker_name"), flags)
    if _empty(maker):
        maker = ""
        flags.append("maker_missing")
    batch = _text(raw.get("str_batch_no") or raw.get("batch_raw") or raw.get("batch"))
    batch = re.sub(r"^\s*\(10\)\s*", "", batch)
    batch = re.sub(r"(?<=[A-Za-z0-9])\?(?=[A-Za-z0-9])", "-", batch).rstrip(".,;: ")
    parts = re.split(r"\s*(?:[,;&]|\band\b)\s*", batch, flags=re.I)
    if len(parts) > 1 and all(len(batch_key(p)) >= 3 for p in parts):
        flags.append("multi_batch_split")
    else:
        if len(parts) > 1:
            reasons.append("ambiguous_multi_batch")
        parts = [batch]
    result = _descriptive(raw.get("str_nsq_result") or raw.get("result"), flags)
    remarks = _descriptive(raw.get("str_nsq_remarks") or raw.get("remarks"), flags)
    typ = "SPURIOUS" if kind.lower() == "spurious" or str(raw.get("num_spurious_flag")) == "1" else entry_type(result, remarks, maker, kind)
    level = _text(raw.get("str_reporting_source") or raw.get("list_level")).lower()
    level = "central" if "cdsco" in level or "cdl" in level else "state" if "state" in level else "unknown"
    lab = _descriptive(raw.get("str_reported_by_lab_or_state") or raw.get("reported_by"), flags)
    lab = re.sub(r"\s*,\s*", " ", lab)
    report_month = _date(raw.get("dt_reporting_month_year"))
    if report_month and report_month != month:
        flags.append("month_mismatch")
    if re.search(r"\b(shampoo|serum|syringe|gauze|cotton)\b", product, re.I):
        flags.append("non_drug")
    if not product or _empty(product):
        reasons.append("product_missing")
    if not maker and typ != "SPURIOUS":
        reasons.append("maker_missing")
    if any(_empty(p) or len(batch_key(p)) < 2 or re.search(r"\b(?:not\s+mentioned|up\s*-?to)\b", p, re.I) for p in parts):
        reasons.append("batch_placeholder")
    if any(_batch_is_date(part) for part in parts):
        reasons.append("batch_is_date")
    raw_mfg = raw.get("dt_manufacturing_date") or raw.get("mfg")
    raw_exp = raw.get("dt_expiry_date") or raw.get("exp")
    mfg, exp = _date(raw_mfg), _date(raw_exp)
    if not mfg or not exp:
        flags.append("date_missing")
    if any(value and not _empty(value) and not _date(value) for value in (raw_mfg, raw_exp)):
        flags.append("date_unparsed")
    if mfg and exp and mfg > exp:
        flags.append("mfg_after_exp")
    if mfg and mfg > month:
        flags.append("mfg_after_list_month")
    if mfg and exp:
        months_apart = (int(exp[:4])-int(mfg[:4]))*12 + int(exp[5:7])-int(mfg[5:7])
        if months_apart > 120:
            flags.append("shelf_life_gt_10y")
    output = []
    for part in parts:
        output.append({"product": product, "brand": brand, "batch_raw": part.strip(), "batch_key": batch_key(part),
                       "mfg": mfg, "exp": exp,
                       "maker_raw": maker, "maker_name": maker_name(maker), "marketer": _descriptive(raw.get("marketer"), flags),
                       "result": result, "remarks": remarks, "firm_reply": _descriptive(raw.get("str_firm_reply"), flags),
                       "reported_by": lab, "list_month": month, "list_kind": kind.lower(), "list_level": level,
                       "entry_type": typ, "flags": flags[:] + (["batch_short"] if len(batch_key(part)) < 4 else []), "status": "valid"})
    return output, reasons

def portal_json(path, encoding="latin-1"):
    path = Path(path)
    if path.stat().st_size > MAX_SNAPSHOT_BYTES:
        raise ValueError("Snapshot exceeds the 16 MB import limit")
    for index, raw in enumerate(_snapshot_rows(path.read_bytes(), encoding), 1):
        yield {"page": 1, "row_no": index, "fields": raw, "raw_text": json.dumps(raw, ensure_ascii=False)}

def ingest_file(path, *, month=None, kind=None, metadata=None):
    """Import one stored JSON source atomically; repeated identical input adds zero rows."""
    db.init_db()
    path = Path(path)
    if path.stat().st_size > MAX_SNAPSHOT_BYTES:
        raise ValueError("Snapshot exceeds the 16 MB import limit")
    raw_bytes = path.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    meta_path = path.with_suffix(".meta.json")
    if meta_path.exists() and meta_path.stat().st_size > 256 * 1024:
        raise ValueError("Snapshot metadata exceeds the 256 KB limit")
    try:
        meta = metadata if metadata is not None else (json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {})
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ValueError("Snapshot metadata is not valid JSON") from exc
    if not isinstance(meta, dict):
        raise ValueError("Snapshot metadata must be an object")
    if meta.get("sha256") and meta["sha256"] != digest:
        raise ValueError(f"Snapshot checksum mismatch: {path.name}")
    month = month or path.stem
    kind = (kind or path.parent.name).lower()
    if not re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", month):
        raise ValueError("Source month must be YYYY-MM")
    if kind not in {"nsq", "spurious"}:
        raise ValueError("Source kind must be nsq or spurious")
    source_url = str(meta.get("url") or "")
    official_source = urlsplit(source_url).scheme == "https" and urlsplit(source_url).hostname == "cdscoonline.gov.in"
    source_title = f"CDSCO {kind.upper()} portal · {month}" if official_source else f"Stored {kind.upper()} snapshot · {month}"
    encoding = meta.get("encoding", "latin-1")
    if not isinstance(encoding, str):
        raise ValueError("Snapshot encoding must be a supported encoding name")
    encoding = encoding.lower()
    rows = _snapshot_rows(raw_bytes, encoding)
    archive = archive_snapshot(raw_bytes, digest)
    fetched_at = str(meta.get("fetched_at") or db.now())[:100]
    expected = meta.get("rows", len(rows))
    if not isinstance(expected, int) or isinstance(expected, bool) or not 0 <= expected <= MAX_SNAPSHOT_ROWS:
        raise ValueError("Snapshot expected row count must be an integer within the import limit")
    stamp = db.now()
    with db.connect() as con:
        con.execute("BEGIN IMMEDIATE")
        previous = con.execute("SELECT id,superseded_by FROM sources WHERE source_type='portal' AND list_kind=? AND list_month=? AND sha256=?", (kind, month, digest)).fetchone()
        parser_version = con.execute("SELECT value FROM kv WHERE key=?", (f"ingest_version:{previous['id']}",)).fetchone() if previous else None
        if previous and previous["superseded_by"] is None and parser_version and parser_version[0] == CLEANING_VERSION:
            return {"source_id": previous[0], "file": path.name, "added": 0, "quarantined": 0, "unchanged": True}
        existing_hashes = {row[0] for row in con.execute("SELECT row_hash FROM alerts WHERE list_kind=? AND list_month=?", (kind, month))}
        old_sources = [r[0] for r in con.execute("SELECT id FROM sources WHERE source_type='portal' AND list_kind=? AND list_month=? AND superseded_by IS NULL", (kind, month))]
        if previous:
            old_sources = [id for id in old_sources if id != previous["id"]]
        if previous:
            source_id = previous["id"]
            con.execute("UPDATE sources SET superseded_by=NULL,ingested_at=?,fetched_at=? WHERE id=?", (stamp, fetched_at, source_id))
            con.execute("DELETE FROM quarantine WHERE source_id=?", (source_id,))
        else:
            cur = con.execute("""INSERT INTO sources(source_type,file_name,url,sha256,title,list_kind,list_level,list_month,
              strategy,rows_found,rows_expected,fetched_at,ingested_at) VALUES('portal',?,?,?,?,?,'mixed',?,'portal_json',?,?,?,?)""",
              (str(archive), source_url, digest, source_title, kind, month,
               len(rows), expected, fetched_at, stamp))
            source_id = cur.lastrowid
        added = valid = flagged = quarantined = 0
        hashes = []
        for row_no, raw in enumerate(rows, 1):
            raw_text = json.dumps(raw, ensure_ascii=False)
            if not isinstance(raw, dict):
                cleaned, reasons = [], ["unknown_row_format"]
            else:
                cleaned, reasons = clean_row(raw, month, kind)
            if reasons:
                con.execute("INSERT INTO quarantine(source_id,page,row_no,raw_json,reasons,created_at) VALUES(?,?,?,?,?,?)",
                            (source_id, 1, row_no, raw_text, json.dumps(reasons + ["no_llm"]), stamp))
                quarantined += 1
                continue
            for item in cleaned:
                canonical = json.dumps({"raw": raw, "source_type": "portal", "list_month": month,
                                        "list_kind": kind, "batch": item["batch_key"]}, sort_keys=True, ensure_ascii=False)
                row_hash = hashlib.sha1(canonical.encode("utf-8")).hexdigest()
                hashes.append(row_hash)
                if row_hash in existing_hashes:
                    updates = dict(item, last_seen=stamp, source_id=source_id)
                    updates["flags"] = json.dumps(updates["flags"])
                    con.execute("UPDATE alerts SET " + ",".join(f"{key}=?" for key in updates) + ",removed_at=NULL WHERE row_hash=?",
                                list(updates.values()) + [row_hash])
                else:
                    data = dict(item, source_id=source_id, row_hash=row_hash, page=1, row_no=row_no,
                                raw_json=raw_text, first_seen=stamp, last_seen=stamp)
                    data["flags"] = json.dumps(data["flags"])
                    columns = list(data)
                    con.execute(f"INSERT INTO alerts({','.join(columns)}) VALUES({','.join('?' for _ in columns)})", list(data.values()))
                    added += 1
                    existing_hashes.add(row_hash)
                valid += 1
                flagged += bool(item["flags"])
        con.execute("CREATE TEMP TABLE seen_import_hashes(row_hash TEXT PRIMARY KEY)")
        con.executemany("INSERT OR IGNORE INTO seen_import_hashes(row_hash) VALUES(?)", ((value,) for value in hashes))
        con.execute("UPDATE alerts SET removed_at=? WHERE source_id=? AND NOT EXISTS (SELECT 1 FROM seen_import_hashes seen WHERE seen.row_hash=alerts.row_hash)", (stamp, source_id))
        if old_sources:
            slots = ",".join("?" for _ in old_sources)
            con.execute(f"UPDATE alerts SET removed_at=? WHERE source_id IN ({slots}) AND removed_at IS NULL", [stamp] + old_sources)
            con.execute(f"UPDATE sources SET superseded_by=? WHERE id IN ({slots})", [source_id] + old_sources)
        con.execute("UPDATE sources SET rows_valid=?,rows_flagged=?,rows_quarantined=? WHERE id=?", (valid, flagged, quarantined, source_id))
        con.execute("INSERT OR REPLACE INTO kv(key,value) VALUES(?,?)", (f"ingest_version:{source_id}", CLEANING_VERSION))
    return {"source_id": source_id, "file": path.name, "month": month, "kind": kind,
            "found": len(rows), "valid": valid, "added": added, "quarantined": quarantined, "unchanged": False}

def ingest_snapshots(callback=None):
    reports, errors = [], []
    for path in sorted((config.DATA_DIR / "raw" / "portal").glob("*/*.json"))[:1000]:
        if path.name.endswith(".meta.json"):
            continue
        try:
            report = ingest_file(path)
            reports.append(report)
            if callback:
                callback({"type": "source", "message": f"Indexed {path.parent.name.upper()} {path.stem}", **report})
        except (OSError, ValueError, TypeError) as exc:
            errors.append({"file": path.name, "error": str(exc)})
    return {"sources": reports, "added": sum(r["added"] for r in reports),
            "quarantined": sum(r["quarantined"] for r in reports), "errors": errors}

def pdf_lines(path):
    """Extract grounded table cells; no reconstruction or invented missing cells."""
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        for page_no, page in enumerate(pdf.pages[:250], 1):
            for table in page.extract_tables():
                for row_no, cells in enumerate(table[:10000], 1):
                    yield {"page": page_no, "row_no": row_no, "cells": cells,
                           "raw_text": " | ".join(str(cell or "") for cell in cells)}

def pdf_text_chunks(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        for page_no, page in enumerate(pdf.pages[:60], 1):
            yield {"page": page_no, "row_no": 1, "raw_text": page.extract_text() or ""}

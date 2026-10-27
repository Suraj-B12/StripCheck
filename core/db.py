"""SQLite provenance records and durable application documents."""
import json
import math
import sqlite3
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from core import config

DB_PATH = None
_CONTEXT_PATH = ContextVar("stripcheck_db_path", default=None)
_INITIALIZED = {}
_INIT_LOCK = threading.RLock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources(
 id INTEGER PRIMARY KEY, source_type TEXT, file_name TEXT, url TEXT, sha256 TEXT, title TEXT,
 list_kind TEXT, list_level TEXT, list_month TEXT, strategy TEXT,
 rows_found INT DEFAULT 0, rows_valid INT DEFAULT 0, rows_flagged INT DEFAULT 0,
 rows_repaired INT DEFAULT 0, rows_quarantined INT DEFAULT 0, rows_expected INT,
 fetched_at TEXT, ingested_at TEXT, superseded_by INT);
CREATE TABLE IF NOT EXISTS alerts(
 id INTEGER PRIMARY KEY, source_id INT REFERENCES sources(id), row_hash TEXT UNIQUE,
 list_kind TEXT, list_level TEXT, list_month TEXT, page INT, row_no INT, bbox TEXT,
 product TEXT, brand TEXT, batch_raw TEXT, batch_key TEXT, mfg TEXT, exp TEXT,
 maker_raw TEXT, maker_name TEXT, marketer TEXT, result TEXT, remarks TEXT, firm_reply TEXT, reported_by TEXT,
 entry_type TEXT, flags TEXT, status TEXT, raw_json TEXT,
 first_seen TEXT, last_seen TEXT, removed_at TEXT, linked_alert_id INT);
CREATE INDEX IF NOT EXISTS idx_alerts_batch ON alerts(batch_key);
CREATE INDEX IF NOT EXISTS idx_alerts_month ON alerts(list_month);
CREATE INDEX IF NOT EXISTS idx_alerts_active_batch ON alerts(batch_key) WHERE removed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_alerts_active_month ON alerts(list_month DESC,id DESC) WHERE removed_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_sources_identity ON sources(source_type,list_kind,list_month,sha256);
CREATE TABLE IF NOT EXISTS quarantine(id INTEGER PRIMARY KEY, source_id INT, page INT, row_no INT,
 raw_json TEXT, reasons TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, kind TEXT, thread_id TEXT, started_at TEXT,
 finished_at TEXT, status TEXT, report_json TEXT);
CREATE TABLE IF NOT EXISTS checks(id INTEGER PRIMARY KEY, thread_id TEXT UNIQUE, mode TEXT, image_paths TEXT,
 verdict TEXT, confidence TEXT, entry_ids TEXT, batch_evidence TEXT, asks INT, steps INT, seconds REAL,
 planner_mode TEXT, model TEXT, lang TEXT, created_at TEXT, final_json TEXT);
CREATE TABLE IF NOT EXISTS cabinet(id INTEGER PRIMARY KEY, label TEXT, product_text TEXT, brand TEXT,
 batch_key TEXT, batch_display TEXT, batch_evidence TEXT, mfg TEXT, exp TEXT, maker TEXT, check_thread_id TEXT,
 added_at TEXT, last_verdict TEXT, last_checked_at TEXT, last_alert_ids TEXT);
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, cabinet_id INT, alert_id INT, kind TEXT,
 message TEXT, created_at TEXT, seen INT DEFAULT 0, UNIQUE(cabinet_id, alert_id, kind));
CREATE TABLE IF NOT EXISTS confusions(ocr_char TEXT, true_char TEXT, source TEXT, count INT,
 PRIMARY KEY(ocr_char, true_char, source));
CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS documents(collection TEXT NOT NULL, id TEXT NOT NULL, value TEXT NOT NULL,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(collection,id));
CREATE INDEX IF NOT EXISTS idx_documents_updated ON documents(collection,updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_cabinet_check ON documents(json_extract(value,'$.thread_id')) WHERE collection='cabinet';
CREATE INDEX IF NOT EXISTS idx_notification_cabinet ON documents(json_extract(value,'$.cabinet_id')) WHERE collection='notifications';
"""

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _target(path=None):
    return Path(path or _CONTEXT_PATH.get() or DB_PATH or config.DB_PATH).expanduser().resolve()


@contextmanager
def using_database(path):
    """Keep each app's database bound to its request and background workers."""
    token = _CONTEXT_PATH.set(Path(path))
    try:
        yield
    finally:
        _CONTEXT_PATH.reset(token)


@contextmanager
def connect(path=None):
    """Commit/roll back a short transaction and always close its connection."""
    target = _target(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(target), timeout=15, check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=15000")
        with con:
            yield con
    finally:
        con.close()


def _migrate_source_identity(con):
    """Replace legacy hash-only uniqueness without changing source IDs or hashes."""
    legacy = False
    for index in con.execute("PRAGMA index_list(sources)").fetchall():
        escaped = index[1].replace('"', '""')
        columns = [row[2] for row in con.execute(f'PRAGMA index_info("{escaped}")')]
        if index[2] and columns == ["sha256"]:
            legacy = True
    if not legacy:
        return
    con.commit()
    con.execute("PRAGMA foreign_keys=OFF")
    try:
        con.execute("BEGIN IMMEDIATE")
        table_sql = SCHEMA.split(";", 1)[0].replace("IF NOT EXISTS sources", "sources_migrating")
        con.execute(table_sql)
        columns = [row[1] for row in con.execute("PRAGMA table_info(sources)")]
        names = ",".join('"' + name.replace('"', '""') + '"' for name in columns)
        con.execute(f"INSERT INTO sources_migrating({names}) SELECT {names} FROM sources")
        con.execute("DROP TABLE sources")
        con.execute("ALTER TABLE sources_migrating RENAME TO sources")
        con.execute("CREATE UNIQUE INDEX idx_sources_identity ON sources(source_type,list_kind,list_month,sha256)")
        if con.execute("PRAGMA foreign_key_check").fetchone():
            raise sqlite3.IntegrityError("Source migration would break a stored source reference")
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.execute("PRAGMA foreign_keys=ON")


def init_db(path=None):
    global DB_PATH
    if path is not None:
        DB_PATH = Path(path)
    target = _target(path)
    with _INIT_LOCK:
        try:
            info = target.stat()
            identity = (info.st_dev, info.st_ino)
        except FileNotFoundError:
            identity = None
        if identity is not None and _INITIALIZED.get(target) == identity:
            return target
        with connect(target) as con:
            con.execute("PRAGMA journal_mode=WAL")
            con.executescript(SCHEMA)
            _migrate_source_identity(con)
            con.execute("INSERT INTO kv(key,value) VALUES('schema_version','3') ON CONFLICT(key) DO UPDATE SET value=excluded.value WHERE value<>excluded.value")
        info = target.stat()
        _INITIALIZED[target] = (info.st_dev, info.st_ino)
    return target

def configure(path):
    return init_db(path)

def _json(value, default):
    try:
        return json.loads(value) if value else default
    except (ValueError, TypeError):
        return default

def _alert(row):
    if row is None:
        return None
    value = dict(row)
    value["flags"] = _json(value.get("flags"), [])
    value["batch"] = value.get("batch_raw", "")
    value["maker"] = value.get("maker_name", "")
    value["month"] = value.get("list_month", "")
    value["kind"] = value.get("entry_type", "NSQ")
    value["source_url"] = value.get("source_url") or ""
    value["source_title"] = value.get("source_title") or "Stored source snapshot"
    return value

ALERT_SELECT = """SELECT a.*, s.url AS source_url,s.title AS source_title,s.sha256 AS source_sha256,
 s.fetched_at AS source_fetched_at,s.file_name AS source_file FROM alerts a
 LEFT JOIN sources s ON s.id=a.source_id"""

def list_alerts(q="", month="", kind="", page=1, size=30, level=""):
    init_db()
    page, size = max(1, int(page)), max(1, min(200, int(size)))
    where, args = ["a.removed_at IS NULL"], []
    if q.strip():
        where.append("(a.product LIKE ? OR a.brand LIKE ? OR a.batch_key LIKE ? OR a.batch_raw LIKE ? OR a.maker_name LIKE ?)")
        term = f"%{q.strip()}%"
        args.extend([term] * 5)
    if month:
        where.append("a.list_month=?")
        args.append(month)
    if level:
        where.append("a.list_level=?")
        args.append(level)
    if kind:
        where.append("(upper(a.entry_type)=? OR upper(a.list_kind)=?)")
        args.extend([kind.upper()] * 2)
    clause = " WHERE " + " AND ".join(where)
    with connect() as con:
        total = con.execute("SELECT COUNT(*) FROM alerts a" + clause, args).fetchone()[0]
        rows = con.execute(ALERT_SELECT + clause + " ORDER BY a.list_month DESC,a.id DESC LIMIT ? OFFSET ?",
                           args + [size, (page - 1) * size]).fetchall()
    return {"items": [_alert(r) for r in rows], "total": total, "page": page,
            "pages": max(1, math.ceil(total / size)), "size": size}

def alert_detail(id):
    init_db()
    with connect() as con:
        row = con.execute(ALERT_SELECT + " WHERE a.id=?", (id,)).fetchone()
    value = _alert(row)
    if value:
        value["raw"] = _json(value.get("raw_json"), {})
    return value

def all_alerts():
    init_db()
    with connect() as con:
        return [_alert(row) for row in con.execute(ALERT_SELECT + " WHERE a.removed_at IS NULL ORDER BY a.id")]

def stats():
    init_db()
    with connect() as con:
        total = con.execute("SELECT COUNT(*) FROM alerts WHERE removed_at IS NULL").fetchone()[0]
        groups = con.execute("SELECT list_month,COUNT(*) n FROM alerts WHERE removed_at IS NULL GROUP BY list_month ORDER BY list_month DESC").fetchall()
        kinds = {r[0]: r[1] for r in con.execute("SELECT entry_type,COUNT(*) FROM alerts WHERE removed_at IS NULL GROUP BY entry_type")}
        source_count = con.execute("SELECT COUNT(*) FROM sources WHERE superseded_by IS NULL").fetchone()[0]
        quarantined = con.execute("SELECT COUNT(*) FROM quarantine q JOIN sources s ON s.id=q.source_id WHERE s.superseded_by IS NULL").fetchone()[0]
        last = con.execute("SELECT value FROM kv WHERE key='last_sync'").fetchone()
        checked = con.execute("SELECT COUNT(*) FROM documents WHERE collection='checks'").fetchone()[0]
    months = [r[0] for r in groups]
    return {"total": total, "alerts": total, "total_alerts": total, "nsq": kinds.get("NSQ", 0),
            "spurious": kinds.get("SPURIOUS", 0), "sources": source_count, "quarantine": quarantined,
            "months": months, "month_count": len(months), "latest_month": months[0] if months else None,
            "earliest_month": months[-1] if months else None, "by_month": [{"month": r[0], "count": r[1]} for r in groups],
            "by_kind": kinds, "last_sync": _json(last[0], last[0]) if last else None,
            "checks": checked, "has_data": bool(total)}

def save_document(collection, id, value):
    init_db()
    doc = dict(value)
    doc.setdefault("id", str(id))
    stamp = now()
    with connect() as con:
        con.execute("""INSERT INTO documents(collection,id,value,created_at,updated_at) VALUES(?,?,?,?,?)
        ON CONFLICT(collection,id) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                    (str(collection), str(id), json.dumps(doc, ensure_ascii=False, default=str), stamp, stamp))
    return doc

def get_document(collection, id):
    init_db()
    with connect() as con:
        row = con.execute("SELECT value FROM documents WHERE collection=? AND id=?", (collection, str(id))).fetchone()
    return _json(row[0], None) if row else None

def list_documents(collection, limit=100):
    init_db()
    limit = max(1, min(1000, int(limit)))
    with connect() as con:
        if collection in {"sources", "quarantine"}:
            return [dict(r) for r in con.execute(f"SELECT * FROM {collection} ORDER BY id DESC LIMIT ?", (limit,))]
        rows = con.execute("SELECT value FROM documents WHERE collection=? ORDER BY updated_at DESC,rowid DESC LIMIT ?", (collection, limit)).fetchall()
    return [_json(r[0], {}) for r in rows]

def delete_document(collection, id):
    init_db()
    with connect() as con:
        result = con.execute("DELETE FROM documents WHERE collection=? AND id=?", (collection, str(id)))
    return result.rowcount > 0

def set_value(key, value):
    init_db()
    with connect() as con:
        con.execute("INSERT OR REPLACE INTO kv(key,value) VALUES(?,?)", (key, json.dumps(value)))

def get_value(key, default=None):
    init_db()
    with connect() as con:
        row = con.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
    return _json(row[0], default) if row else default


def batch_alerts(batch, *, q="", month="", kind="", level="", limit=None):
    """Fetch only exact/confusable batch keys through SQLite's active-batch index."""
    from itertools import islice
    from core.textutils import batch_key, confusion_variants
    key = batch_key(batch)
    keys = list(dict.fromkeys([key] + [variant for variant, _ in islice(confusion_variants(key, 2), 2000)]))
    init_db()
    rows = []
    with connect() as con:
        for offset in range(0, len(keys), 400):
            chunk = keys[offset:offset + 400]
            where = ["a.removed_at IS NULL", "a.batch_key IN (" + ",".join("?" for _ in chunk) + ")"]
            args = list(chunk)
            if q.strip():
                where.append("(a.product LIKE ? OR a.brand LIKE ? OR a.batch_raw LIKE ? OR a.maker_name LIKE ?)")
                args.extend([f"%{q.strip()}%"] * 4)
            for column, value in (("list_month", month), ("list_level", level)):
                if value:
                    where.append(f"a.{column}=?")
                    args.append(value)
            if kind:
                where.append("(upper(a.entry_type)=? OR upper(a.list_kind)=?)")
                args.extend([kind.upper()] * 2)
            query = ALERT_SELECT + " WHERE " + " AND ".join(where)
            if limit is not None:
                remaining = max(0, int(limit) - len(rows))
                if not remaining:
                    break
                query += " LIMIT ?"
                args.append(remaining)
            rows.extend(_alert(row) for row in con.execute(query, args))
    return rows


def check_coverage():
    """Minimal coverage metadata for indexed investigation, without loading rows."""
    init_db()
    with connect() as con:
        row = con.execute("""SELECT COUNT(*) AS real_alert_count, MAX(list_month) AS latest_month,
            COUNT(DISTINCT COALESCE(source_id,'') || ':' || COALESCE(list_month,'') || ':' || COALESCE(entry_type,'')) AS list_count
            FROM alerts WHERE removed_at IS NULL""").fetchone()
    return dict(row)


def cabinet_for_check(thread_id):
    init_db()
    with connect() as con:
        row = con.execute("SELECT value FROM documents WHERE collection='cabinet' AND json_extract(value,'$.thread_id')=? ORDER BY updated_at DESC LIMIT 1", (thread_id,)).fetchone()
    return _json(row[0], None) if row else None


def delete_cabinet_item(item_id):
    """Delete the pack and all of its local notifications in one transaction."""
    init_db()
    with connect() as con:
        deleted = con.execute("DELETE FROM documents WHERE collection='cabinet' AND id=?", (str(item_id),)).rowcount
        con.execute("DELETE FROM documents WHERE collection='notifications' AND json_extract(value,'$.cabinet_id')=?", (str(item_id),))
    return bool(deleted)


def save_existing_document(collection, id, value):
    """A background recheck must never recreate a pack removed in the meantime."""
    init_db()
    with connect() as con:
        result = con.execute("UPDATE documents SET value=?,updated_at=? WHERE collection=? AND id=?",
            (json.dumps(value, ensure_ascii=False, default=str), now(), collection, str(id)))
    return bool(result.rowcount)


def insert_child_document(collection, id, value, parent_collection, parent_id):
    """Insert once, only while the parent still exists in the same transaction."""
    init_db()
    stamp = now()
    with connect() as con:
        result = con.execute("""INSERT OR IGNORE INTO documents(collection,id,value,created_at,updated_at)
            SELECT ?,?,?,?,? WHERE EXISTS(SELECT 1 FROM documents WHERE collection=? AND id=?)""",
            (collection,str(id),json.dumps(value,ensure_ascii=False,default=str),stamp,stamp,parent_collection,str(parent_id)))
    return bool(result.rowcount)

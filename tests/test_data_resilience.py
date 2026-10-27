"""Synthetic adversarial imports retain provenance and never erase valid data on errors."""
from contextlib import contextmanager
import hashlib
import json
import sqlite3
import pytest
from core import config, db, ingest, portal


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(config, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(config, 'DB_PATH', tmp_path / 'test.db')
    monkeypatch.setattr(db, 'DB_PATH', None)
    db.init_db()
    return tmp_path


def row(batch='SYN2408B', **extra):
    return {'str_product_name': 'Synthetic Tablets', 'str_batch_no': batch,
            'str_manufactured_by': 'Synthetic Laboratories', **extra}


def source(folder, value, month='2026-09', kind='nsq', encoding='latin-1'):
    path = folder / 'raw' / 'portal' / kind / f'{month}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=False).encode(encoding))
    return path


def test_same_bytes_have_distinct_month_and_kind_provenance(isolated):
    first = source(isolated, {'aaData': [row()]})
    second = source(isolated, {'aaData': [row()]}, month='2026-08')
    third = source(isolated, {'aaData': [row()]}, kind='spurious')
    ids = {ingest.ingest_file(path)['source_id'] for path in (first, second, third)}
    assert len(ids) == 3 and db.stats()['total'] == 3
    assert len({item['source_sha256'] for item in db.all_alerts()}) == 1
    for month in ('2026-09', '2026-08'):
        ingest.ingest_file(source(isolated, {'aaData': []}, month=month))
    assert db.stats()['total'] == 1
    assert db.all_alerts()[0]['list_kind'] == 'spurious'


@pytest.mark.parametrize('value', [{}, {'error': 'Temporarily unavailable'}, {'aaData': None}, None])
def test_invalid_response_does_not_supersede_existing_alerts(isolated, value):
    path = source(isolated, {'aaData': [row()]})
    ingest.ingest_file(path)
    source(isolated, value)
    with pytest.raises(ValueError):
        ingest.ingest_file(path)
    assert db.stats()['total'] == 1
    assert len(db.list_documents('sources')) == 1


@pytest.mark.parametrize('metadata', [[], {'encoding': 1}, {'encoding': 'unknown'}, {'rows': False}, {'rows': -1}])
def test_malformed_metadata_is_rejected_without_partial_import(isolated, metadata):
    path = source(isolated, {'aaData': [row()]})
    with pytest.raises(ValueError):
        ingest.ingest_file(path, metadata=metadata)
    assert db.stats()['total'] == 0


def test_import_limits_do_not_silently_truncate(isolated, monkeypatch):
    path = source(isolated, {'aaData': [row(), row('SYN2409B')]})
    monkeypatch.setattr(ingest, 'MAX_SNAPSHOT_ROWS', 1)
    with pytest.raises(ValueError, match='not truncated'):
        ingest.ingest_file(path)
    monkeypatch.setattr(ingest, 'MAX_SNAPSHOT_BYTES', 20)
    with pytest.raises(ValueError, match='16 MB'):
        ingest.ingest_file(path)
    assert db.stats()['total'] == 0


def test_import_works_with_low_sqlite_parameter_limit(isolated, monkeypatch):
    original = db.connect
    @contextmanager
    def limited(*args, **kwargs):
        with original(*args, **kwargs) as con:
            con.setlimit(sqlite3.SQLITE_LIMIT_VARIABLE_NUMBER, 100)
            yield con
    monkeypatch.setattr(db, 'connect', limited)
    path = source(isolated, {'aaData': [row(f'SYN{i:06d}') for i in range(300)]})
    assert ingest.ingest_file(path)['added'] == 300
    assert db.stats()['total'] == 300


def test_failed_import_rolls_back_and_retry_succeeds(isolated, monkeypatch):
    path = source(isolated, {'aaData': [row(), row('SYN2409B')]})
    original = ingest.clean_row
    calls = 0
    def interrupted(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError('synthetic interruption')
        return original(*args, **kwargs)
    monkeypatch.setattr(ingest, 'clean_row', interrupted)
    with pytest.raises(RuntimeError):
        ingest.ingest_file(path)
    assert db.stats()['total'] == 0 and not db.list_documents('sources')
    monkeypatch.setattr(ingest, 'clean_row', original)
    assert ingest.ingest_file(path)['added'] == 2


def test_utf8_bom_and_declared_charset_remain_grounded(isolated):
    name = 'Synthetic Café दवा Tablets'
    for month, encoding, metadata in [('2026-09', 'utf-8-sig', {}), ('2026-08', 'utf-8', {'encoding': 'utf-8'})]:
        path = source(isolated, {'aaData': [row(str_product_name=name)]}, month=month, encoding=encoding)
        ingest.ingest_file(path, metadata=metadata)
    assert all(item['product'] == name for item in db.all_alerts())


def test_corrupted_archive_is_repaired_from_verified_snapshot(isolated):
    path = source(isolated, {'aaData': [row()]})
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    archive = isolated / 'raw' / 'archive' / f'{digest}.json'
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b'corrupted')
    ingest.ingest_file(path)
    assert archive.read_bytes() == path.read_bytes()
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest


def test_structured_row_fields_are_quarantined(isolated):
    path = source(isolated, {'aaData': [row(str_batch_no={'value': 'SYN2408B'})]})
    assert ingest.ingest_file(path)['quarantined'] == 1
    assert 'unsupported_field_shape' in db.list_documents('quarantine')[0]['reasons']
    assert db.stats()['total'] == 0


def test_fetch_rejects_mislabelled_month_before_network(monkeypatch):
    monkeypatch.setattr(portal, '_request', lambda *args, **kwargs: pytest.fail('must not request'))
    for args in [('nsq', '../2026-09', 'SEP-2026'), ('nsq', '2026-09', 'AUG-2026'), ('../nsq', '2026-09', 'SEP-2026')]:
        with pytest.raises(ValueError):
            portal.fetch_month(*args)


def test_discovery_deduplicates_months_and_invalid_years(monkeypatch):
    def request(endpoint, **params):
        value = ['2026', 'x', '9999999999999999'] if endpoint == 'reportingYears' else ['SEP', 'SEP', 'AUG', 'JUL']
        return b'', value, ''
    monkeypatch.setattr(portal, '_request', request)
    assert portal.discover_months('nsq') == [('2026-09', 'SEP-2026'), ('2026-08', 'AUG-2026'), ('2026-07', 'JUL-2026')]


def test_descriptive_mojibake_repair_preserves_raw_evidence_and_batch(isolated):
    name = 'Synthetic Brand – 225'
    mojibake = name.encode('utf-8').decode('latin-1')
    path = source(isolated, {'aaData': [row(str_brand_name=mojibake)]})
    original_bytes = path.read_bytes()
    ingest.ingest_file(path)
    alert = db.all_alerts()[0]
    detail = db.alert_detail(alert['id'])
    assert alert['brand'] == name
    assert alert['batch_raw'] == 'SYN2408B' and alert['batch_key'] == 'SYN2408B'
    assert 'encoding_repaired' in alert['flags']
    assert detail['raw']['str_brand_name'] == mojibake
    assert path.read_bytes() == original_bytes
    assert detail['source_sha256'] == hashlib.sha256(original_bytes).hexdigest()
    cleaned, _ = ingest.clean_row(row(str_product_name='Synthetic Café Tablets'), '2026-09')
    assert cleaned[0]['product'] == 'Synthetic Café Tablets'
    assert 'encoding_repaired' not in cleaned[0]['flags']

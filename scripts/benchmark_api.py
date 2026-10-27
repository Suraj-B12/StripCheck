"""Repeatable local API benchmark against an isolated synthetic 20,000-row DB.

Run: .venv/bin/python scripts/benchmark_api.py
No real source rows, photos or application records are read or modified.
"""
import json, statistics, tempfile, time, sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory() as folder:
    os.environ['STRIPCHECK_DATA_DIR'] = folder
    os.environ['STRIPCHECK_DB_PATH'] = str(Path(folder) / 'bench.db')
    os.environ['STRIPCHECK_RUNS_DIR'] = str(Path(folder) / 'runs')
    from core import db
    from server.app import create_app
    from fastapi.testclient import TestClient
    path = Path(folder)/'bench.db'
    db.init_db(path)
    with db.connect() as con:
        con.executemany("INSERT INTO alerts(batch_key,batch_raw,product,entry_type,list_month) VALUES(?,?,?,?,?)", [(f'TEST{i:07}',f'TEST{i:07}','Synthetic benchmark item','NSQ','2026-09') for i in range(20000)])
    client = TestClient(create_app(path))
    def measure(fn,n):
        times=[]
        for _ in range(n):
            start=time.perf_counter();fn();times.append((time.perf_counter()-start)*1000)
        return round(statistics.median(times),3)
    measures={'rows':20000,'stats_median_ms':measure(db.stats,30),'exact_batch_http_median_ms':measure(lambda:client.get('/api/alerts?batch=TEST0001234'),10)}
    counter=[]
    original=db.sqlite3.connect
    def connect(*args,**kwargs):
        result=original(*args,**kwargs);result.set_trace_callback(counter.append);return result
    db.sqlite3.connect=connect
    for _ in range(20):db.get_document('checks','absent')
    measures['schema_ddl_for_20_reads']=sum(s.lstrip().startswith('CREATE TABLE') for s in counter)
    measures['schema_writes_for_20_reads']=sum('schema_version' in s and s.lstrip().startswith('INSERT') for s in counter)
    db.sqlite3.connect=original
    print(json.dumps(measures, indent=2))

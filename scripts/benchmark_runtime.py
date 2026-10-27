"""Repeatable synthetic-data benchmark; never touches the user's live database.

Run: .venv/bin/python scripts/benchmark_runtime.py --rows 10000 --queries 50
Results are timings from this machine, not accuracy or production capacity claims.
"""
import argparse
import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path


def measure(call, repeats=1):
    elapsed = []
    for _ in range(repeats):
        start = time.perf_counter()
        call()
        elapsed.append((time.perf_counter() - start) * 1000)
    return {"median_ms": round(statistics.median(elapsed), 3), "max_ms": round(max(elapsed), 3), "runs": repeats}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--queries", type=int, default=50)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 100 <= args.rows <= 25000 or not 1 <= args.queries <= 200:
        parser.error("Choose 100–25000 rows and 1–200 queries")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    with tempfile.TemporaryDirectory(prefix="stripcheck-benchmark-") as folder:
        temporary = Path(folder)
        os.environ["STRIPCHECK_DATA_DIR"] = str(temporary)
        os.environ["STRIPCHECK_DB_PATH"] = str(temporary / "benchmark.db")
        from core import db
        from core.ingest import ingest_file
        from core.matching import build_index, search_exact, search_variants
        path = temporary / "raw" / "portal" / "nsq" / "2026-09.json"
        path.parent.mkdir(parents=True)
        rows = [{"str_product_name": f"Synthetic Product {i % 100} Tablets", "str_batch_no": f"SYN{i:08d}X",
                 "str_manufactured_by": "Synthetic Example Laboratories", "dt_manufacturing_date": "08/2024",
                 "dt_expiry_date": "07/2027", "str_nsq_result": "Synthetic benchmark fixture"}
                for i in range(args.rows)]
        path.write_bytes(json.dumps({"aaData": rows}).encode("latin-1"))
        results = {"synthetic": True, "rows": args.rows, "python": sys.version.split()[0],
                   "snapshot_bytes": path.stat().st_size}
        results["initial_ingest"] = measure(lambda: ingest_file(path))
        results["unchanged_ingest"] = measure(lambda: ingest_file(path), 3)
        results["materialize_all_alerts"] = measure(db.all_alerts, 3)
        alerts = db.all_alerts()
        results["build_memory_index"] = measure(lambda: build_index(alerts), 3)
        index = build_index(alerts)
        key = f"SYN{args.rows // 2:08d}X"
        results["exact_memory_lookup"] = measure(lambda: search_exact(index, key), args.queries)
        results["bounded_variants"] = measure(lambda: search_variants(index, key), min(args.queries, 10))
        results["alert_search_page"] = measure(lambda: db.list_alerts(q=key, size=30), args.queries)
        results["statistics"] = measure(db.stats, args.queries)
        results["stored_rows"] = db.stats()["total"]
        assert results["stored_rows"] == args.rows
        payload = json.dumps(results, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload + "\n", encoding="utf-8")
        print(payload)


if __name__ == "__main__":
    main()

"""Reproducible index statistics; never writes into the research paper implicitly."""
import json
from collections import Counter
from pathlib import Path
from core import db

def statistics():
    result = db.stats()
    rows = db.all_alerts()
    batches = Counter(row["batch_key"] for row in rows)
    result.update({"distinct_batches": len(batches), "repeated_batches": sum(n > 1 for n in batches.values()),
                   "missing_manufacturer": sum(not row.get("maker_name") for row in rows),
                   "missing_dates": sum(not row.get("mfg") or not row.get("exp") for row in rows),
                   "non_drug": sum("non_drug" in row.get("flags", []) for row in rows)})
    return result

def write_stats(path):
    result = statistics()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

stats = statistics

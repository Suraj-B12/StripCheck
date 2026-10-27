"""Local, best-effort JSONL tracing. No remote service is required."""
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

_LOCK = threading.Lock()


def _folder() -> Path:
    from core import config
    return Path(config.DATA_DIR) / "traces"


def _valid(thread_id: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_-]{1,100}", thread_id))


def record(thread_id: str, event: str, data: dict | None = None) -> None:
    if not _valid(thread_id):
        return
    try:
        row = {"at": datetime.now(timezone.utc).isoformat(), "thread_id": thread_id,
               "event": event, "model": None, "tokens_in": 0, "tokens_out": 0,
               "fallback": False, **(data or {})}
        with _LOCK:
            folder = _folder()
            folder.mkdir(parents=True, exist_ok=True)
            with (folder / f"{thread_id}.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    except (OSError, TypeError, ValueError):
        pass


def read_trace(thread_id: str) -> list[dict]:
    if not _valid(thread_id):
        return []
    try:
        path = _folder() / f"{thread_id}.jsonl"
        if not path.is_file():
            return []
        rows = []
        with path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle):
                if index >= 2000:
                    break
                try:
                    rows.append(json.loads(line))
                except (ValueError, TypeError):
                    continue
        return rows
    except OSError:
        return []

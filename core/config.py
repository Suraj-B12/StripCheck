"""Local, environment-configurable paths and bounded runtime settings."""
import os
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

DATA_DIR = Path(os.environ.get("STRIPCHECK_DATA_DIR", str(ROOT / "data"))).expanduser()
DB_PATH = Path(os.environ.get("STRIPCHECK_DB_PATH", str(DATA_DIR / "stripcheck.db"))).expanduser()
RUNS_DIR = Path(os.environ.get("STRIPCHECK_RUNS_DIR", str(ROOT / "runs"))).expanduser()
UPLOAD_DIR = DATA_DIR / "uploads"
RAW_DIR = DATA_DIR / "raw"
PORTAL_URL = "https://cdscoonline.gov.in/CDSCO"

def _bounded_number(name, default, minimum, maximum, integer=False):
    try:
        value = float(os.environ.get(name, str(default)))
        if not math.isfinite(value):
            value = default
    except ValueError:
        value = default
    value = min(maximum, max(minimum, value))
    return int(value) if integer else value

SYNC_DELAY = _bounded_number("STRIPCHECK_SYNC_DELAY", 1.5, 1.5, 60)
NETWORK_TIMEOUT = _bounded_number("STRIPCHECK_NETWORK_TIMEOUT", 20, 3, 60, integer=True)
LLM_MODEL = os.environ.get("STRIPCHECK_LLM_MODEL", "qwen2.5:3b")
VLM_MODEL = os.environ.get("STRIPCHECK_VLM_MODEL", "")
OLLAMA_URL = os.environ.get("STRIPCHECK_OLLAMA_URL", "http://localhost:11434")
LLM_TIMEOUT = _bounded_number("STRIPCHECK_LLM_TIMEOUT", 15, 1, 90, integer=True)
VLM_TIMEOUT = _bounded_number("STRIPCHECK_VLM_TIMEOUT", 30, 1, 60, integer=True)
PLANNER = os.environ.get("STRIPCHECK_PLANNER", "rules")
LANG = os.environ.get("STRIPCHECK_LANG", "en")
OFFLINE = os.environ.get("STRIPCHECK_OFFLINE", "0") == "1"
MAX_STEPS, MAX_ASKS, MAX_REREADS, MAX_REVISIONS = 16, 2, 1, 1
MAX_VARIANT_SUBS, MAX_CANDIDATES, MAX_VARIANT_LOOKUPS = 2, 20, 2000
PRODUCT_MATCH, PRODUCT_PARTIAL, MAKER_MATCH = .8, .5, 85
BRAND_MATCH, BRAND_MISMATCH, DATE_ASK_MAX_DIGITS = .8, .5, 1
OCR_LOW_SCORE, NOISY_ALPHA, CONFIRM_BATCH_REQUIRED = .8, 1.0, True
INGEST_MIN_VALID_RATE, INGEST_MAX_LLM_REPAIRS, INGEST_MAX_TEXT_CHUNKS = .8, 25, 60
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_IMAGE_PIXELS = 24_000_000

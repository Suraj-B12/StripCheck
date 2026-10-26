# StripCheck — Build Spec for Claude Code

*Agentic AI (26CD7PEAAI) mini-project · Review 2 demo build → Review 3 prototype · written 22 Oct 2026 · v1.1*

*v1.1 changes: product-only hits are never graded, which closes a crash path when the batch is unreadable (§9.1–9.3, §9.5–9.6); one question confirms a 2-substitution variant, and a confirmed character also corrects the stored batch (§9.4, §9.6); the learned prior orders variants but never skips the question (§10, A2 notes); a cap on candidates per search (§5); ingest completeness (§7.7); median latency, parsing and safety metrics (§13, §15, §16 M7); placeholder tabs until M7/M8 (§14). If Claude Code already started on v1.0, replace the file and tell it: "The spec is now v1.1. Read its v1.1 changes line and apply those changes to anything already built."*

> **Paste this into Claude Code, opened in the project folder:**
>
> Read `StripCheck_Build_Spec.md` completely before writing any code. Then implement it milestone by milestone in the order given in §16, starting with M0. After each milestone, run its tests and its demo command, fix whatever fails, and give me a 3-line status (what's done / the demo command / anything I must do by hand). Use the verified code in Appendix A and the verified patterns in Appendix B as written. Target: Windows 11, conda env `stripcheck` (Python 3.11), Ollama running locally. Stop after M6 and tell me; M7–M10 only if I say so.

---

## 0. Ground rules for the implementer

1. **Platform.** Windows 11 laptop, PowerShell, conda env `stripcheck` with Python 3.11. Use `pathlib` for every path, `encoding="utf-8"` for every file, and keep console output ASCII (`->`, not `→`). Put `PYTHONUTF8=1` in `.env`.
2. **Code style (the owner's standing preference).** Minimal, flat, procedural. Plain functions; `TypedDict`/Pydantic only for data shapes. No class hierarchies, no factories, no plugin registries, no dependency-injection layers. One module per concern (§4). Short docstrings.
3. **Never break the demo.** Every LLM call, network call and tracing call has a timeout and a fallback (§9.5). The app must still run with **Ollama off** (planner falls back to rules) and with **Phoenix off** (the JSONL step log is still written and shown in the UI).
4. **Bound every loop** (§9.5). No paid APIs. No network access in the check path.
5. **Safety language is a hard requirement** (§9.8). Never output "safe", never tell anyone to stop a medicine, and flag only the listed batch, never a brand.
6. **No invented data.** Every alert row comes from a file in `data/raw/`. Every pack field must be grounded in QR or OCR text, or typed by the user (§8.4).
7. **Tests** (`pytest -q`) must pass without Ollama or Phoenix running. Mock LLM paths or mark them `@pytest.mark.llm` and skip by default.
8. If an API here doesn't match the installed library version, read the installed package's source or docs and adapt minimally. Record the change under "Deviations" in `README.md`.
9. Cite external code, data and models in `README.md` (course policy §8.1): CDSCO alert lists, RapidOCR/PP-OCR models, LangGraph, Arize Phoenix, Ollama, the Qwen model and its license.

---

## 1. What we are building

**The one decision:** *"Is this exact medicine pack from a batch that CDSCO has flagged?"*

**The verdicts:**

| Label | Meaning | User-facing action |
|---|---|---|
| `FLAGGED` | Batch matches an entry on a CDSCO list of drugs found Not of Standard Quality (also misbranded or adulterated) | Show your pharmacist |
| `SUSPECTED_FAKE` | Batch matches an entry CDSCO lists as spurious ("purported to be spurious", maker "Under Investigation") | Show your pharmacist |
| `NOT_LISTED` | No surviving match on the lists loaded, as of the latest month | Not a certification of safety |
| `CANT_VERIFY` | Evidence too weak after bounded retries and asks; the agent abstains | Ask your pharmacist to check the batch |

**Components:**

- **Ingest agent.** Turns CDSCO alert files (PDF now; HTML/CSV from the new portal in M9) into a validated alert index in SQLite. It repairs bad rows with a grounded LLM call or quarantines them with reasons. Checkpointed and resumable.
- **Investigator agent.** Reads a pack photo (QR → OCR → enhanced re-read), extracts fields, and retrieves candidate entries (exact batch → OCR-confusion variants → product fallback). It grades each candidate field by field, asks the user when evidence is missing, and drafts a cited verdict. Plan → act → observe loop with an LLM planner and a rule fallback.
- **Verifier agent (critic).** Checks the draft against hard rules plus an optional LLM critique. It approves, sends the draft back once, or downgrades to `CANT_VERIFY`.
- **Supervisor.** Routes background work. After every ingest it runs the cabinet re-check (memory).
- **Observability:** Arize Phoenix (OpenTelemetry) plus a JSONL step log. **UI:** Streamlit. **LLM:** local Ollama (`qwen2.5:3b` by default).

---

## 2. Verified facts about the data — design around these, don't re-research

Checked on 22 Oct 2026 against CDSCO's site, CDSCO PDFs and press copies of the 2026 alerts.

**Legacy monthly PDFs (up to the June 2025 lists, posted 18 Jul 2025):** machine-readable text, one table per list.
- Column headers, verbatim, central list: `S.No | Product/Drug Name | Batch No. | Manufacturing Date | Expiry Date | Manufactured By | NSQ Result | Reported by CDSCO Laboratory`. State lists end with `Reported by State Laboratory`.
- Headings, verbatim: `A. NOT OF STANDARD QUALITY (NSQ) ALERT FOR THE MONTH OF MARCH-2025 (CDSCO/Central Laboratories)` and `B. NOT OF STANDARD QUALITY ALERT FOR THE MONTH OF JUNE– 2025 (STATE LABORATORIES)`. Note the en dash.
- Every data row starts with `1.`, `2.`, … in the S.No column.
- **Header cells break words across lines**, e.g. `Manufacturin\ng Date`. Match headers on *squashed* text (lowercase letters only), as in `map_headers` in Appendix A1.
- **Date formats seen:** `09/2024`, `Apr-24`, `Feb-2026`, `05/2027`, `Oct/2023`, `Apr--2026`, `01/07/2024`, `09-2026`. **Placeholders:** `NM`, `N/A`, `Not Mentioned`.
- **Known data errors:** manufacturing date after expiry; manufacturing date later than the alert month. Flag these rows, keep them.
- **Spurious entries** appear as NSQ Result `SPURIOUS`, or as a remark "purported to be spurious", usually with maker "Under Investigation". There are also separate PDFs titled "List of spurious Drugs for the month of …".
- **Manufacturer cell:** `M/s. Name, address…`, sometimes followed by `Mkt By : …` or `Manufactured for : …`.
- **Last column:** a lab (`CDL, Kolkata`, `RDTL, Guwahati`, `CDTL-Mumbai`) or a state (`Karnataka`).
- **Sizes:** Jan-2025 central list 52 rows, Mar-2025 central 70, Jun-2025 state 130.

**New portal (from 28 Aug 2025).** A CDSCO notice dated 28 Aug 2025 moved NSQ alerts to a new page (Notifications → NSQ Alerts, `/opencms/opencms/en/Notifications/nsq-drugs/`). A plain fetch of that page returns only the site header, so its table appears to load via JavaScript.
- Columns, as reproduced in press copies of the May 2026 alert: `S.No | Name of Product | Batch No | Manufacturing Dates | Manufacturer Details | Reporting Source | Reporting by Lab/State | Reporting Month & Year | Remarks`.
- Typical cell values: `Manufacturing Date: Oct-2024Expiry Date: Mar-2027`, `Manufacturer Name: Under InvestigationManufactured By: Under Investigation`, `CDSCO Labs`, `MAY-2026`, `NSQ Remark: … Firm Reply: …`.
- To ingest it, save the page from a browser, or copy the table into Excel and save as CSV. The adapter comes in M9; `map_headers` already understands these headers.

**QR codes.** Mandatory only on Schedule H2 brands: the top 300 brands since 1 Aug 2023, extending to vaccines, antimicrobials, NDPS and anti-cancer drugs in 2027–28. The payload is not standardised. It may be a GS1 element string (`(01)` GTIN, `(10)` batch, `(11)` mfg YYMMDD, `(17)` exp YYMMDD), labelled text, or just a URL.

**OCR observation (our own test, RapidOCR 3.10):** a scuffed `B` was read as `3` with confidence **1.0**, and enhancing and re-reading gave the same wrong answer. **OCR confidence cannot detect confident misreads.** The agent catches them by checking the reading against the alert index (confusion-aware variant search) and asking the user to confirm the one character. This is the central agentic behaviour, so keep it.

**Real files to ingest.** The user saves these into `data\raw\`; `cli.py fetch` also tries them:

```
https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/NSQ%20Alert%20For%20The%20Month%20of%20March-2025.pdf
https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/STATE%20NSQ%20%20June%20-2025.pdf
https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/STATE%20NSQ%20MAY-2025.pdf
https://medicaldialogues.in/pdf_upload/nsq-alert-for-the-month-of-january-2025-277058.pdf
https://medicaldialogues.in/pdf_upload/nsq-alert-for-the-month-of-feb-2025-280934.pdf
https://medicaldialogues.in/pdf_upload/state-nsq-alert-for-the-month-of-january-2025-276688.pdf
```

---

## 3. Stack and environment (versions verified Oct 2026)

`requirements.txt`:

```
# Python 3.11 (conda env "stripcheck"). Phoenix and Streamlit need >= 3.11.
langgraph>=1.2,<2
langgraph-checkpoint-sqlite>=3.1,<4
langchain-ollama>=1.1,<2
pydantic>=2.10,<3
rapidocr>=3.10,<4                  # PP-OCR det/rec/cls models ship inside the wheel; pulls opencv-python-headless
onnxruntime>=1.20                  # rapidocr does NOT install an inference engine itself
pdfplumber>=0.11,<0.12
rapidfuzz>=3.10,<4
qrcode[pil]>=8.0
pillow>=10
numpy
pandas
lxml
beautifulsoup4
openpyxl
requests
python-dotenv
streamlit>=1.50,<2
arize-phoenix>=20,<21              # local trace UI: `phoenix serve` -> http://localhost:6006
arize-phoenix-otel>=0.17,<1
openinference-instrumentation-langchain>=0.1.79,<0.2
pytest
```

- **Do not** add `opencv-python` (the non-headless build). Two `cv2` builds in one environment conflict, and `rapidocr` already pulls the headless one.
- **Install:**

  ```
  conda activate stripcheck
  pip install -r requirements.txt
  ```

- **LLM.**
  - Pull the default model with `ollama pull qwen2.5:3b` (about 1.9 GB). It runs on CPU and gives sub-10-second structured answers.
  - If the laptop has an NVIDIA GPU with 8 GB or more, `qwen2.5:7b` is better. Set it in `.env`.
  - Check with `ollama list`. On Windows the Ollama tray app runs the server at `http://localhost:11434`.

---

## 4. Repository layout

```
stripcheck/                      <- project root: open this folder for the demo
  app.py                         Streamlit UI (streamlit run app.py)
  cli.py                         argparse CLI: doctor | fetch | ingest | props | check | recheck | eval
  requirements.txt  .env.example  README.md  CLAUDE.md
  .streamlit/config.toml         [server] fileWatcherType = "none"   (keeps the UI fast with big data folders)
  core/
    __init__.py
    config.py        paths, model names, thresholds, flags (reads .env with python-dotenv)
    db.py            sqlite3 schema + small query helpers (no ORM), WAL mode
    textutils.py     Appendix A1, verbatim (verified)
    matching.py      Appendix A2, verbatim (verified)
    llm.py           ChatOllama structured calls: timeout + fallback (Appendix B7)
    tracing.py       Phoenix register + JSONL step log (Appendix B3)
    pack_tools.py    QR, OCR, enhance, field extraction + LangChain @tool wrappers
    alert_tools.py   search/grade @tool wrappers over matching.py, loads the index from SQLite
    ingest.py        discovery, classification, table extraction strategies, validation, repair, commit
    ingest_agent.py  LangGraph Ingest agent
    investigator.py  LangGraph Investigator agent + planner
    verifier.py      hard rules + optional LLM critique
    supervisor.py    LangGraph supervisor: ingest -> recheck cabinet -> report
    props.py         demo props + golden set generator
    evaluate.py      metrics + A/B arms
  data/raw/  data/props/  data/eval/  data/photos/  data/uploads/
  data/stripcheck.db  data/checkpoints.db
  runs/              JSONL step logs, eval results
  tests/
```

`CLAUDE.md` should hold short conventions for future sessions: the ground rules in §0, the commands in §15, and "keep Appendix A code verbatim unless a test proves it wrong".

---

## 5. Configuration (`core/config.py` and `.env`)

`.env.example`:

```
STRIPCHECK_LLM_MODEL=qwen2.5:3b
STRIPCHECK_OLLAMA_URL=http://localhost:11434
STRIPCHECK_PLANNER=hybrid          # hybrid | llm | rules
STRIPCHECK_TRACING=1
STRIPCHECK_PHOENIX_URL=http://localhost:6006
STRIPCHECK_LLM_TIMEOUT=90
PYTHONUTF8=1
```

Constants in `config.py`. Tune on the dev set only, never on the eval set:

```
PRODUCT_MATCH = 0.8      # share of the entry's name tokens found on the pack
PRODUCT_PARTIAL = 0.5
MAKER_MATCH = 85         # rapidfuzz token_set_ratio
OCR_LOW_SCORE = 0.90
MAX_STEPS = 12           # planner iterations per check
MAX_ASKS = 2             # human questions per check
MAX_REREADS = 1          # enhanced OCR passes per image
MAX_REVISIONS = 1        # verifier send-backs
MAX_VARIANT_SUBS = 2     # OCR-confusion substitutions per variant
MAX_CANDIDATES = 20      # entries kept per search, best first
INGEST_MIN_VALID_RATE = 0.8
INGEST_MAX_LLM_REPAIRS = 25   # per file
INGEST_MAX_TEXT_CHUNKS = 60   # per file, strategy B
```

`KNOWN_SOURCES` is the list of `(url, filename)` pairs from §2.

---

## 6. Database (`core/db.py`, SQLite, `PRAGMA journal_mode=WAL`)

```sql
CREATE TABLE IF NOT EXISTS sources(
  id INTEGER PRIMARY KEY, file_name TEXT, sha256 TEXT UNIQUE, url TEXT, title TEXT,
  list_kind TEXT,            -- nsq | spurious
  list_level TEXT,           -- central | state | unknown
  list_month TEXT,           -- YYYY-MM or NULL
  strategy TEXT,             -- lines | text_chunks | html | csv
  rows_found INT, rows_valid INT, rows_flagged INT, rows_repaired INT, rows_quarantined INT,
  ingested_at TEXT);
CREATE TABLE IF NOT EXISTS alerts(
  id INTEGER PRIMARY KEY, source_id INT REFERENCES sources(id),
  list_kind TEXT, list_level TEXT, list_month TEXT, page INT, row_no INT,
  product TEXT, batch_raw TEXT, batch_key TEXT, mfg TEXT, exp TEXT,
  maker_raw TEXT, maker_name TEXT, marketer TEXT, result TEXT, reported_by TEXT,
  entry_type TEXT,           -- NSQ | SPURIOUS | MISBRANDED | ADULTERATED
  flags TEXT,                -- JSON list, e.g. ["mfg_after_exp"]
  status TEXT,               -- valid | flagged | repaired
  raw_json TEXT,
  UNIQUE(source_id, row_no));
CREATE INDEX IF NOT EXISTS idx_alerts_batch ON alerts(batch_key);
CREATE TABLE IF NOT EXISTS quarantine(id INTEGER PRIMARY KEY, source_id INT, page INT, row_no INT, raw_json TEXT, reasons TEXT);
CREATE TABLE IF NOT EXISTS checks(id INTEGER PRIMARY KEY, thread_id TEXT, image_paths TEXT, verdict TEXT, confidence TEXT,
  entry_id INT, asks INT, steps INT, seconds REAL, planner_mode TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS cabinet(id INTEGER PRIMARY KEY, label TEXT, product_text TEXT, batch_key TEXT, mfg TEXT, exp TEXT,
  maker TEXT, added_at TEXT, last_verdict TEXT, last_checked_at TEXT);
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, cabinet_id INT, alert_id INT, message TEXT, created_at TEXT, seen INT DEFAULT 0);
CREATE TABLE IF NOT EXISTS corrections(ocr_char TEXT, true_char TEXT, count INT, PRIMARY KEY(ocr_char, true_char));
```

The same batch may legitimately appear in several lists or months. Keep every row; cite all of them.

---

## 7. Ingest agent (M1)

### 7.1 Sources
- Ingest `data/raw/*.pdf` (M1) and `*.html`, `*.htm`, `*.csv`, `*.xlsx` (M9).
- `cli.py fetch` downloads `KNOWN_SOURCES` with `requests`: browser-like User-Agent, 30-second timeout, TLS verification on (never disable it). It skips files already present and prints failures. The user downloads by hand if the server refuses.
- Skip a file whose `sha256` is already in `sources`, so ingest is idempotent.

### 7.2 Classify (`classify_source`)
- Work from the first-page text, or for HTML the title.
- `list_level`:
  - `state` if the text matches `STATE\s+LAB` or the filename contains `STATE`;
  - `central` if it matches `CDSCO|Central`;
  - otherwise `unknown`.
- `list_kind`: `spurious` if "spurious" appears in the title or filename; otherwise `nsq`.
- `list_month`: match the regex `MONTH\s+OF\s+([A-Za-z]+)\W*(\d{4})` and normalise with `parse_month_year`. If that fails, try the filename. If that fails, ask the LLM (`SourceMeta` schema), accepting only a month that appears in the text or filename. Otherwise set NULL and flag rows `no_list_month`.

### 7.3 Extract table rows
- **Strategy A `lines` (primary).** For each page, for each `page.extract_tables()` result (Appendix B6):
  - **Header row:** the first row where `map_headers(row)` maps at least 5 fields, including `batch` and `product`. Carry the header across pages and tables, because continuation tables have none.
  - **Data row:** the S.No cell matches `^\s*\d{1,4}\.?\s*$`.
  - **Continuation:** a row with an empty S.No cell but text elsewhere continues the previous row (it was split at a page break). Append its cell text to the previous row with a space.
  - Join each cell's internal newlines with a single space.
- **Strategy B `text_chunks` (fallback).** Use it when A yields 0 rows or a valid rate below `INGEST_MIN_VALID_RATE`.
  - Concatenate `page.extract_text()` across pages.
  - Split into row chunks at the regex `(?m)^\s*(\d{1,4})\.\s+`.
  - Send each chunk to the LLM with the `AlertRow` schema, grounded per §7.6.
  - Cap at `INGEST_MAX_TEXT_CHUNKS` per file. Keep whichever strategy gives more valid rows.

### 7.4 Map headers
- Use synonyms first (`map_headers`, Appendix A1).
- If a header maps fewer than 5 fields, or misses `batch` or `product`, call the LLM (`HeaderMap` schema, Appendix C) with the header cells and the first 2 data rows.
- Validate the proposed mapping on the first 5 rows (§7.5 validators). Accept it if at least 4 of 5 rows are valid; otherwise go to strategy B.
- **Why this matters (say it in the demo):** CDSCO changed its columns in Aug 2025. A fixed script breaks; this agent notices the unknown layout, proposes a mapping, tests it on sample rows, and only then commits.

### 7.5 Normalise and validate (`normalize_row`, `validate_row`)

**Normalise:**
- `product`: collapse whitespace.
- `batch_raw`: collapse whitespace; `batch_key = batch_key(batch_raw)`.
- `mfg` and `exp`: `parse_month_year`. For the portal's combined `mfg` cell with no `exp` column, use `split_portal_dates`.
- `maker_name = maker_name(maker_raw)`. `marketer` is the text after `Mkt By` / `Marketed by` / `Manufactured for`.
- `result`: the NSQ Result cell. For the portal, the text after `NSQ Remark:` up to `Firm Reply`.
- `entry_type = entry_type(result, remarks, maker_raw, list_kind)`.

**Errors** (row unusable as-is; sends it to repair):
- `product` empty.
- `batch_key` empty, shorter than 2 characters, or a placeholder.
- `batch_raw` parses as a date (column shift).
- maker empty and not SPURIOUS.

**Flags** (keep the row, mark it): `date_unparsed`, `date_missing`, `mfg_after_exp`, `mfg_after_list_month`, `shelf_life_gt_10y`, `batch_short` (under 4 characters, so collision-prone).

### 7.6 Repair and quarantine
- For rows with errors, call the LLM (`AlertRow` schema) with the header names and the raw cells, then re-normalise and re-validate.
- **Grounding guard:** `batch_key(llm.batch)` must be a substring of `batch_key(raw row text)`, and at least half of the product tokens must appear in the raw text. Otherwise reject the repair.
- Allow at most `INGEST_MAX_LLM_REPAIRS` per file. The remainder are quarantined with the reason `repair_budget_exhausted`.
- With `--no-llm`, or with Ollama down, quarantine directly with the reason `no_llm`.

### 7.7 Commit and report
- One transaction per file: the `sources` row, then `alerts` and `quarantine`.
- Print an ASCII report table. Per file: strategy, found, valid, flagged, repaired, quarantined, expected, completeness, top 3 reasons. Then totals.
- **expected** = the rows the file numbers itself: the sum of the highest S.No in each numbered section (numbering can restart at 1 inside a file; skip S.No cells that don't parse). **completeness** = found ÷ expected, or "n/a" when the file has no S.No column. This is an R4 metric (§13).
- Return the report as a dict for the UI.

### 7.8 Graph (`ingest_agent.py`)
- **State:** `files`, `i`, `meta`, `rows`, `report`, `strategy`.
- **Nodes:** `discover` → `classify` → `extract_lines` → `map_validate`.
- **Routing after `map_validate`:** if the valid rate is below threshold and strategy B hasn't run, go to `extract_text_chunks` and then back to `map_validate`. Otherwise go to `repair` → `commit` → `next_file`.
- **Routing after `next_file`:** if more files remain, back to `classify`; otherwise `report` → END.
- **Checkpointer:** `SqliteSaver` on `data/checkpoints.db`, `thread_id = "ingest-<timestamp>"`.
- **Durable:** after a crash, `python cli.py ingest --resume <thread_id>` calls `graph.invoke(None, config)`, which resumes at the failed node (verified, Appendix B2).
- **Test hook:** env `STRIPCHECK_CRASH_AT=<filename>` raises in `extract_lines` for that file, for the resume test.

---

## 8. Pack tools (M2), `core/pack_tools.py`

All tools are plain functions plus LangChain `@tool` wrappers. Nodes invoke the wrappers with `config` so that spans nest (Appendix B3). Outputs must be small and JSON-serialisable.

### 8.1 `decode_qr(image_path)`
- `cv2.QRCodeDetector().detectAndDecode(img)`; if that gives nothing, retry on the 2× upscaled grayscale image.
- Returns `{"found": bool, "raw": str|None, "fields": parse_qr_payload(raw)}`.
- A URL-only payload has `fields == {}`; record it and continue with OCR.

### 8.2 `ocr_read(image_path, enhanced=False)`
- Use a module-level `RapidOCR()` (create once). `res = ENGINE(img)` → `res.txts`, `res.scores`, `res.boxes`.
- Silence its logger with `logging.getLogger("RapidOCR").setLevel(logging.ERROR)`.
- Returns `{"lines": [...], "scores": [...], "pass": "raw"|"enhanced"}`, with lines in reading order (top-to-bottom by box y, then x).

### 8.3 `enhance(image)`
Grayscale → 2× INTER_CUBIC upscale → CLAHE (clipLimit 2.0, tiles 8×8) → 3×3 sharpen kernel (Appendix B5). Helps with blur and glare. **It does not fix confident misreads** (§2), so don't claim it does.

### 8.4 `extract_fields(ocr_lines, qr_fields, mode)`
1. **Regex pass** (all tested, Appendix A1):
   - `find_batch(lines)`.
   - `find_dates(lines)`. It handles labels like `MFD. 06/2024` (a *date*) without confusing them with `Mfd. by:` (the *manufacturer*).
   - `find_party(lines, MAKER_RE)` for the manufacturer and `find_party(lines, MKT_RE)` for the marketer.
   - `product_text` = the top 3 OCR lines that contain no label (B.No/Mfg/Exp/Mfd/Mkt/DEMO) joined.
2. **QR fields override** OCR fields when present (`batch_source="qr"`).
3. If the batch or product is still missing and `mode != "rules"`, call the LLM with the `PackFields` schema (Appendix C).
4. **Grounding guard (hallucination check):** every non-null value must appear in the OCR/QR text (`rapidfuzz.fuzz.partial_ratio(squashed value, squashed text) >= 90`). Otherwise set it to null and log `grounding_rejected`.
5. Returns `{"brand","generic","product_text","batch","batch_source","batch_line_score","mfg","exp","maker","marketer"}`.

---

## 9. Investigator and Verifier (M3, M4)

### 9.1 State (`TypedDict`, `total=False`)

```python
class CheckState(TypedDict, total=False):
    images: list[str]                 # [pack photo, optional box photo]
    planner_mode: str                 # hybrid | llm | rules
    qr: dict                          # {"tried": bool, "found": bool, "raw": str|None, "fields": dict}
    ocr: list                         # [{"image", "pass", "lines", "scores"}]
    fields: dict                      # see §8.4
    batch_confirmed: bool
    searched: list                    # subset of ["exact", "variants", "product"]
    candidates: list                  # alert rows + how/subs
    product_hits: list                # search_by_product results: context only, never graded or flagged
    graded: list                      # matching.grade() outputs
    need: dict                        # current open question for the user, if any
    asks: int
    rereads: int
    steps: int
    revisions: int
    declined: list                    # kinds of asks the user skipped
    answers: Annotated[list, operator.add]
    history: Annotated[list, operator.add]   # {"step","source":"llm"|"rules","thought","action"}
    next_action: str
    draft: dict                       # {"label","entry_ids","confidence","citation","explanation","reason"}
    critique: dict
    final: dict
```

### 9.2 Actions (each is a graph node that returns to `planner`)

| Action | Allowed when | Does |
|---|---|---|
| `read_qr` | QR not tried on the latest image | `decode_qr` |
| `read_text` | no OCR yet for the latest image | `ocr_read` |
| `reread_enhanced` | OCR done, `rereads < MAX_REREADS`, and the batch is missing or its line score is below `OCR_LOW_SCORE` | enhanced OCR, merge lines |
| `extract_fields` | new QR/OCR evidence not yet extracted | §8.4 |
| `search_exact` | batch present, "exact" not searched | `matching.search_exact` |
| `search_variants` | batch present, "variants" not searched, nothing accepted | `matching.search_variants(prior=corrections)` |
| `search_by_product` | batch missing after rereads and asks, product present | entries with `product_coverage >= 0.8` and no date mismatch, best coverage first, saved to `product_hits`, **not** `candidates`, so they are never graded. They can only lead to a `box_photo` ask or `CANT_VERIFY`, never a flag |
| `grade` | ungraded candidates | `matching.grade`; status `adjudicate` → LLM `ProductJudgement` (not in rules mode) |
| `ask_user` | `asks < MAX_ASKS` and an open need not in `declined` | `interrupt()` (§9.6) |
| `draft_verdict` | always allowed; forced when `steps >= MAX_STEPS` | `matching.decide` + templates (§9.8) |

### 9.3 Planner (`planner` node)

**`rule_next(state)` is a deterministic priority list.** It returns `(action, reason)`:

1. QR not tried → `read_qr`
2. latest image not OCR'd → `read_text`
3. new evidence not extracted → `extract_fields`
4. batch missing and `rereads < MAX_REREADS` → `reread_enhanced`
5. batch missing and a `type_batch` ask is allowed → `ask_user` (type_batch)
6. batch missing → `search_by_product` if not searched; else, if `product_hits` is non-empty and a `box_photo` ask is allowed → `ask_user` (box_photo, batch-missing wording, §9.6); else `draft_verdict` (`CANT_VERIFY`; the reason says how many list entries name this product)
7. "exact" not searched → `search_exact`
8. ungraded candidates → `grade`
9. nothing accepted and "variants" not searched → `search_variants`
10. ungraded candidates → `grade`
11. pending candidate and an ask is allowed. The ask kind depends on the candidate's status:
    - `needs_confirm_char` → `confirm_char`;
    - `needs_more_evidence` → `box_photo`;
    - `adjudicate` (rules mode only) → `box_photo`.
12. otherwise → `draft_verdict`

**Modes (`STRIPCHECK_PLANNER`):**
- **`rules`:** always `rule_next`.
- **`hybrid` (default):** use the LLM only at *branch points*, otherwise `rule_next`. The branch points are:
  - (a) after `extract_fields`, when `batch_source == "ocr"` and the batch line score is below `OCR_LOW_SCORE`;
  - (b) after a search that returned 0 candidates;
  - (c) after `grade`, when any status is `adjudicate`, `needs_more_evidence` or `needs_confirm_char`;
  - (d) when the verifier sent the draft back.
- **`llm`:** the LLM at every step.

**LLM call:** the `PlannerDecision` schema (Appendix C) gets a compact evidence summary, the `allowed` actions and the rule suggestion. **Guard:** if the action isn't in `allowed`, or the call fails or times out, use `rule_next` and record `source="rules(fallback)"`. Every decision is appended to `history` as `{step, source, thought, action}`. This *is* the visible ReAct trace, so render it in the UI.

### 9.4 Retrieval and grading
Use `core/matching.py` (Appendix A2) verbatim. Its rules, which tests prove on 7 scenarios:

- **Hard mismatch → reject.** A product, date or maker mismatch rejects the candidate. This is a batch collision, and rejecting it is what prevents false alarms.
- **Spurious entries** skip the maker check (maker is "Under Investigation"). They need product match plus a date match, unless the entry has no dates (then confidence is `medium`).
- **NSQ entries** need product match plus a date match or a maker match.
- **Variant (non-exact) batch → `needs_confirm_char`.** A human confirms the substituted character, or both characters for a 2-substitution variant, in one question (§9.6).
- **Partial product match** without full date and maker corroboration → `adjudicate` (LLM decides).
- If several candidates are accepted, `SUSPECTED_FAKE` outranks `FLAGGED`. Cite all accepted entries.

### 9.5 Bounds and fallbacks
- **Planner and asks:** `MAX_STEPS=12` planner iterations, `MAX_ASKS=2`, `MAX_REREADS=1`, `MAX_REVISIONS=1`.
- **Variant search:** at most 2 substitutions per variant, roughly 100–250 index lookups, in-memory.
- **Candidates:** each search keeps at most `MAX_CANDIDATES` entries, best first (variants: fewest substitutions, then the learned prior; product hits: highest coverage).
- **Every LLM call:** timeout `STRIPCHECK_LLM_TIMEOUT`, wrapped in try/except; on failure use the rules path.
- **Tracing** failures never raise.

### 9.6 Human-in-the-loop (`ask_user` node, LangGraph `interrupt`)

**Payloads:**

| `kind` | question (template) | options | resume value |
|---|---|---|---|
| `confirm_char` | "The strip reads 'B3T2305'. CDSCO lists 'BBT2305' (product, Mar 2025). Look at character 2: is it 'B' or '3'?" | `[list_char, ocr_char, "Can't tell"]` | `{"choice": "B"}` |
| `box_photo` | "This batch matches a CDSCO entry, but the strip doesn't show the manufacturer or dates. Upload a photo of the carton, or skip." | `["Upload", "Skip"]` | `{"image_path": "..."}` or `{"skip": true}` |
| `type_batch` | "I can't read the batch number. Type it exactly as printed after 'B.No.', or skip." | `["Type", "Skip"]` | `{"typed": "..."}` or `{"skip": true}` |

With the batch missing (§9.3 step 6), `box_photo` uses this wording instead: "I can't read the batch number, and {n} CDSCO list entries name this product. Upload a photo of the carton, where the batch is often printed more clearly, or skip."

For a 2-substitution variant, `confirm_char` names both positions in one question: "Look at characters 2 and 6: do they read 'B' and '0', or '3' and 'O'?" The options are the listed pair, the OCR pair and "Can't tell", and one answer settles both. Positions are 1-based on the batch as the question shows it (the match key: letters and digits only).

**Handling the answer:**
- **`confirm_char`:**
  - If the user picks the listed character(s), the batch is confirmed. Set the candidate's `how="confirmed"`, set `fields["batch"]` to the listed batch with `batch_confirmed=True` (so a saved cabinet item stores the corrected batch), re-grade, and increment `corrections(ocr_char, true_char)` for each substitution.
  - If the user picks the OCR character(s), reject the candidate with the reason "user confirmed the printed character".
  - "Can't tell" leaves the candidate unresolved, which leads to `CANT_VERIFY` unless something else is accepted.
- **`box_photo`:** append the image, reset `rereads` to 0 (the re-read bound is per image), run QR/OCR/extract on it, fill only *missing* fields, then re-grade. If the carton supplies a missing batch, the normal search path (§9.3 step 7 onward) takes over.
- **`type_batch`:** set the batch with `batch_source="user"`, mark it confirmed, and clear `searched`.
- **`skip`:** add the kind to `declined`. Every answer increments `asks`.

**LangGraph gotcha.** On resume the node re-runs from its first line. Put **no side effects before `interrupt()`**. Build the payload deterministically, and do any DB writes (corrections) only *after* `interrupt()` returns.

### 9.7 Verifier (`verify` node, the critic agent)

**Hard rules (all modes):**
- **R1.** The label is one of the 4 verdicts.
- **R2.** `FLAGGED` / `SUSPECTED_FAKE` need:
  - a cited entry with status `accept`;
  - batch evidence that is `exact` or `confirmed`;
  - product evidence that is `match` or LLM-adjudicated "yes";
  - no mismatch anywhere.
- **R3.** `SUSPECTED_FAKE` needs entry type `SPURIOUS`; `FLAGGED` needs `NSQ`, `MISBRANDED` or `ADULTERATED`.
- **R4.** `NOT_LISTED` needs all of:
  - a grounded batch;
  - "exact" **and** "variants" searched;
  - no pending or accepted candidate.
- **R5.** The explanation carries the citation for flags, and no banned phrase (§9.8).
- **R6.** All counters are within bounds.

**On violation:**
- If `revisions < MAX_REVISIONS`, send the draft back to `planner` with `critique` (for example "NOT_LISTED but variants not searched" → `search_variants`).
- Otherwise downgrade to `CANT_VERIFY` with reason `verifier: <rule>`.

**LLM critique (hybrid/llm, only after the hard rules pass):** the `Critique` schema. If it doesn't approve, drop the LLM rationale and keep the template text. Approve once.

### 9.8 Verdict templates and safety

Explanations are **templates** filled from the evidence. The LLM may add a one-sentence rationale, and the verifier filters it.

- **FLAGGED:** "This batch appears on CDSCO's {Mon YYYY} {central/state} list of drugs found Not of Standard Quality (failed test: {result}; reported by {reported_by}). Show this pack to your pharmacist. Do not stop any prescribed medicine without medical advice."
- **SUSPECTED_FAKE:** "This batch matches an entry CDSCO lists as purported spurious in its {Mon YYYY} alert (the manufacturer named on the label says it did not make this batch). Show this pack to your pharmacist. Do not stop any prescribed medicine without medical advice."
- **NOT_LISTED:** "No match on the CDSCO lists loaded ({n} lists, latest {Mon YYYY}). This does not certify the medicine; CDSCO tests only sampled batches."
- **CANT_VERIFY:** "StripCheck could not verify this pack: {reason}. Ask your pharmacist to check the batch number against CDSCO's alerts."
- **Citation line:** `{level} NSQ alert {Mon YYYY} · row {row_no}, page {page} · {reported_by} · failed: {result} · file {file_name}`.
- **Banned phrases** (regex, case-insensitive, applied to any LLM text): `\bis safe\b`, `\bsafe to (use|take|consume)\b`, `\bstop (taking|using)\b`, `\bgenuine\b`, `\bauthentic\b`, `\bfake medicine\b`.

### 9.9 Graph wiring (`investigator.py`)
- `START → planner`.
- `planner` → conditional edge on `next_action` to one of: `read_qr`, `read_text`, `reread_enhanced`, `extract_fields`, `search_exact`, `search_variants`, `search_by_product`, `grade`, `ask_user`, `draft_verdict`.
- Every tool node → `planner`. `draft_verdict` → `verify`.
- `verify` → `planner` (revise) or `finish`. `finish` → END.
- **Compile once** with `SqliteSaver(sqlite3.connect("data/checkpoints.db", check_same_thread=False))`. In Streamlit, cache it with `@st.cache_resource`.
- **Threads:** one thread per check, `thread_id = "check-" + uuid4().hex[:8]`.
- **`finish`** writes the `checks` row and the last JSONL line, and returns `final`.
- **Nodes** have signature `(state, config)` and call tools as `tool.invoke(args, config=config)` so spans nest.

---

## 10. Supervisor, memory and feedback loop (M8)

- **`supervisor.py` (LangGraph):** `route` → `ingest_agent` (invoke the ingest graph with `config`, nested in the trace) → `recheck_cabinet` → `report`.
- **Recheck:** for each cabinet item, run `search_exact` + `search_variants` + `grade` on the stored fields, with no images and no asks. Any `accept` creates a `notifications` row ("A batch in your cabinet now appears on the {month} list").
- **Cabinet (long-term memory).** After a check, "Save to cabinet" stores the fields and the verdict. The UI shows notifications.
- **Corrections (feedback loop).** Every substitution a user confirms increments `corrections` (§9.6). On later checks:
  - `search_variants` orders variants by the learned counts;
  - the trace records the prior it used, for example "prior: 3→B seen twice";
  - the `confirm_char` question mentions it: "OCR has misread B as 3 twice before."
  - This gives the visible "one feedback loop" that R3 asks for.
  - **The prior never skips the question.** Two batches of one product from the same maker and month can differ by a single confusable character (sequential numbering), so only a person looking at the pack can confirm it. Never set `how="auto_corrected"`.

---

## 11. Observability (M5)

- **`tracing.init_tracing()`:** call it once at CLI or app start (Appendix B3):
  - Use `register(project_name="stripcheck", endpoint=f"{PHOENIX_URL}/v1/traces", auto_instrument=True, batch=True, verbose=False)`.
  - Wrap it in try/except. If Phoenix is down, print one line and continue.
- **Nested spans.** Nodes take `(state, config)` and invoke `@tool` wrappers and `ChatOllama` with `config`. That makes spans nest: graph → node → TOOL and LLM spans with inputs and outputs (verified).
- **JSONL step log:** `runs/<thread_id>.jsonl`, one line per planner decision and per tool result: `{ts, step, node, action, source, thought, summary, ms}`. The UI timeline reads this when Phoenix is off.
- **CLI:** call `tracer_provider.force_flush()` before exit.
- **Phoenix UI:** `http://localhost:6006`, project `stripcheck`.

---

## 12. Demo props and golden set (M2, M7), `core/props.py`

### 12.1 `render_pack(fields, out_path, *, qr=False, damage=None, glare=False, marketer_only=False, seed=0)`
- **Canvas:** a 1200×750 RGB carton.
- **Lines, in order:**
  - brand (large, bold);
  - generic name;
  - strength;
  - `B.No. {batch}`;
  - `Mfg. {MM/YYYY}    Exp. {MM/YYYY}`;
  - `Mfd. by: {maker}`. With `marketer_only`, print `Mkt. by: {marketer}` instead and leave out the dates line;
  - an optional QR (GS1 string `(01)…(10){batch}(11)YYMMDD(17)YYMMDD`) at the right;
  - the footer `DEMO PROP - NOT A MEDICINE`.
- **Fonts:** `arialbd.ttf` / `arial.ttf` (Windows), then `DejaVuSans*.ttf`, then the PIL default.
- **`damage={"index": i, "seed": s}`:** erase 3 small foil-coloured rectangles over the left stroke of character `i` of the batch. In our test this turned `B` into `3`.
- **`glare`:** Gaussian blur 2.2 plus a soft white ellipse over part of the text.

### 12.2 `calibrate_misread(fields, index)`
- For each confusable position and seeds 0–59: render with `damage`, OCR it and extract the batch.
- Accept the first image where:
  - the read differs from the truth;
  - `batch_key(read)` is one of `confusion_variants(truth)` with exactly 1 substitution;
  - the read is **not** itself in the index.
- Save it. If nothing qualifies, log it, use the glare variant instead, and note it in the manifest. This keeps the demo deterministic on *this* laptop.

### 12.3 Demo set (`python cli.py props --demo`)
Pick real rows from the DB and write these props plus `data/props/manifest.json`:

| File | Built from | Expected verdict |
|---|---|---|
| `01_flagged_clean.jpg` | NSQ row with parsed mfg/exp, real maker, batch_key length ≥ 5 | FLAGGED |
| `02_flagged_qr.jpg` | same row, with QR | FLAGGED (QR path) |
| `03_misread.jpg` | NSQ row whose batch has a confusable char, `calibrate_misread` | FLAGGED after one `confirm_char` |
| `04_suspected_fake.jpg` | SPURIOUS row (prefer one with dates) | SUSPECTED_FAKE |
| `05_marketer_only.jpg` | NSQ row, `marketer_only=True` | ask `box_photo` → FLAGGED with box (use `01`), else CANT_VERIFY |
| `06_trap_collision.jpg` | batch of NSQ row A + product, maker and dates of a different row B, chosen so that `product_coverage(A.product, B.product) < 0.5` and B's maker differs | NOT_LISTED (a lookup script false-alarms) |
| `07_genuine.jpg` | invented batch (2 letters + 6 digits) not in the index, nor any 1-substitution variant | NOT_LISTED |

The manifest stores `[{file, truth, entry_id, scenario, notes}]`.

### 12.4 Golden set (`python cli.py props --eval --n 60 --seed 7`)
- **Scenario mix:** 35% flagged (a mix of clean, glare, misread and qr), 15% suspected fake, 20% traps, 30% genuine.
- Output goes to `data/eval/` with a manifest. Deterministic for a given seed.
- **Dev set:** seed 1, for tuning. **Eval set:** seed 7, report only.
- Add real phone photos of the team's own strips to `data/photos/` with a manifest. These are genuine negatives (NOT_LISTED unless actually listed).

---

## 13. Evaluation and A/B (M7), `core/evaluate.py`

**Arms:**
- **`baseline`** (the "lookup script"): QR → OCR → regex batch → exact lookup. Any hit gives FLAGGED or SUSPECTED_FAKE by entry type; no hit gives NOT_LISTED. No corroboration, no variants, no asks.
- **`agent_rules`:** the graph with `planner=rules`.
- **`agent_hybrid`:** the graph with `planner=hybrid` (needs Ollama).

**HITL policy:**
- **`--hitl oracle`:** a simulated user answers from the manifest truth. `confirm_char` gets the true character(s) at the asked position(s), `box_photo` gets the clean prop of the same row if it exists (else skip), `type_batch` gets the true batch.
- **`--hitl none`:** every ask is skipped.
- Report both.

**Metrics:**

| Metric | Definition |
|---|---|
| hit recall | correct label among truth ∈ {FLAGGED, SUSPECTED_FAKE} |
| type accuracy | correct label among the flagged positives |
| false-alarm rate | predicted FLAGGED or SUSPECTED_FAKE among truth NOT_LISTED |
| trap false-alarm rate | the same, on traps only |
| abstention rate | share of CANT_VERIFY |
| asks per pack | mean asks |
| steps, latency | mean steps; median, mean and p95 seconds per check |
| safety | verdict texts with a banned phrase (§9.8), plus FLAGGED or SUSPECTED_FAKE verdicts without a citation line. Must be 0 |
| parsing accuracy | field-level accuracy on a 50-row hand-checked sample (`parsecheck`, below) |
| completeness | found ÷ expected rows per file, from the ingest report (§7.7) |

**Parsing hand-check:** `python cli.py parsecheck --sample 50` writes `runs/parse_sample.csv` with a fixed seed: file, page, row and every parsed field, each followed by an empty `<field>_ok` column. The team marks each field Y or N against the PDF. `python cli.py parsecheck --score runs/parse_sample.csv` prints the accuracy overall and per field.

**Output:** `runs/eval_<ts>.json` and `.md`, plus a table printed to the console. No thresholds may be tuned on seed 7.

**A/B decision rule (registered at R2):** adopt the agent if its trap false-alarm rate is at least 50% (relative) lower than the baseline's and its hit recall is no more than 5 points lower. Report whatever happens.

---

## 14. Streamlit UI (M6), `app.py`

**At M6,** the Cabinet and Evaluation tabs show a one-line placeholder ("Built in M8" / "Built in M7"), and "Run ingest" calls the ingest agent directly. M7 and M8 fill those tabs in and switch "Run ingest" to the supervisor. "Save to cabinet" works from M6, since it only writes a `cabinet` row.

**Sidebar:**
- **Health:** Ollama via `GET {url}/api/tags` (is the model present?), Phoenix via `GET {url}`, and DB row/list counts with the latest list month.
- **Planner-mode radio:** hybrid / llm / rules.
- A link to Phoenix.
- The advisory notice: "Advisory only. Not medical advice. Show your pharmacist."

**Tabs:**
1. **Check a pack**
   - Inputs: `st.file_uploader` (jpg/jpeg/png/webp, at most 15 MB), `st.camera_input`, or a "Demo props" selectbox from the manifest.
   - "Run check" saves the image to `data/uploads/`, starts a thread and streams the graph (Appendix B4).
   - **Live timeline** (`st.status`): one row per `history` entry, e.g. `Step 4 · planner (llm): "No exact match; OCR may have misread" -> search_variants`, followed by the tool's result summary.
   - **On interrupt:** show the question and widgets for its kind (option buttons, a text input, or an uploader). Submit resumes with `Command(resume=...)`.
   - **Verdict card:** coloured by label, with the label, the explanation and the confidence.
   - **Citation table:** month, level, row, page, lab/state, failed test, file.
   - **Evidence table:** batch, product, dates and maker, each with match / mismatch / unknown.
   - "Save to cabinet".
   - Expanders: OCR lines, QR payload, evidence ledger JSON.
2. **Alert lists:** the sources table (per-file counts), the quarantine table with reasons, a fuzzy batch/product search, and a "Run ingest" button that runs the supervisor and shows the report.
3. **Cabinet:** saved items, notifications, and "Re-check now".
4. **Evaluation:** the latest eval table, and "Run quick eval" (`baseline` and `agent_rules`, n=20).

---

## 15. CLI, `cli.py` (argparse)

```
python cli.py doctor [--warm]                    # Python, packages, Ollama + model, Phoenix, DB counts, data/raw files; --warm loads the model
python cli.py fetch                              # try KNOWN_SOURCES -> data/raw (skips existing)
python cli.py ingest [--no-llm] [--resume THREAD_ID]
python cli.py props --demo | --eval --n 60 --seed 7
python cli.py check IMAGE [--planner rules|hybrid|llm]   # prints the step timeline; prompts in the terminal on interrupts
python cli.py recheck
python cli.py eval --arms baseline,agent_rules[,agent_hybrid] --hitl oracle|none [--limit N]
python cli.py parsecheck --sample 50 | --score runs/parse_sample.csv   # parsing hand-check sheet, then its accuracy
```

---

## 16. Build order: milestones and definition of done

The time estimates are for Claude Code.

| # | Milestone | Done when |
|---|---|---|
| **M0** (15 min) | Scaffold, `requirements.txt`, `config.py`, `db.py`, `doctor`, `CLAUDE.md`, `.streamlit/config.toml`, plus `pytest.ini` with `[pytest]`, `pythonpath = .`, `markers = llm: needs Ollama` and `addopts = -m "not llm"` (so `import core` works and LLM tests skip by default) | `python cli.py doctor` prints every check; `pytest -q` runs |
| **M1** (60 min) | `textutils.py` (A1) + tests (A3); `ingest.py`; `ingest_agent.py` with checkpointer; `cli.py ingest` | The real PDFs in `data/raw` ingest; the report shows per-file counts; a second run adds 0 rows; the crash-and-resume test passes |
| **M2** (45 min) | `pack_tools.py`, `props.py` (`--demo`) | 7 demo props plus manifest; OCR finds the batch on clean props; the misread prop is calibrated (or the fallback is logged) |
| **M3** (75 min) | `matching.py` (A2) + tests; `alert_tools.py`; `investigator.py` (rules planner); `verifier.py`; `cli.py check` with terminal prompts | All 7 props give the expected verdicts with `--planner rules`; graph tests replay scripted answers |
| **M4** (45 min) | `llm.py`; hybrid/llm planner; LLM field extraction; product adjudication; verifier critique; ingest repair and header mapping | Hybrid gives the same verdicts on the props; with Ollama stopped it falls back, logs `rules(fallback)` and still finishes |
| **M5** (20 min) | `tracing.py` + JSONL | With `phoenix serve` running, `check data/props/03_misread.jpg` shows a nested trace in project `stripcheck` (graph → planner/tool nodes → TOOL/LLM spans) |
| **M6** (60 min) | `app.py` | Every demo prop runs from the UI, including the HITL ask; the health panel and the Alert lists tab work |
| — | **Review 2 cut line: M0–M6 is the demo.** | |
| M7 (45 min) | `evaluate.py` + `props --eval` + `parsecheck` + Evaluation tab | `cli.py eval --arms baseline,agent_rules --hitl oracle` prints the metrics table; `cli.py parsecheck --sample 50` writes the hand-check sheet |
| M8 (45 min) | supervisor + cabinet + notifications + corrections feedback loop | Ingesting a new list notifies a saved batch; a confirmed `3→B` appears as a prior in the next trace |
| M9 (30 min) | HTML/CSV/XLSX adapters for the 2026 portal | A saved portal page or CSV ingests through the same validators |
| M10 | README (setup, run, results, citations, deviations), repo hygiene, screenshots for R3 | Fresh-clone instructions work |

**Tests to write.** None of them need Ollama.
- `tests/test_textutils.py` and `tests/test_matching.py` (Appendix A3).
- `tests/test_ingest.py`: build a small ruled PDF with ReportLab containing the §2 header (including the `Manufacturin\ng Date` break) and 6 rows, including one `SPURIOUS`, one `NM` date and one column-shifted row. Assert the counts and the quarantine.
- `tests/test_investigator.py`: run the graph on the demo props with planner `rules` and scripted resume answers; assert the verdicts.
- `tests/test_resume.py`: crash mid-ingest via `STRIPCHECK_CRASH_AT`, then resume.

Add `reportlab` to a `requirements-dev.txt` for the test fixture.

---

## 17. Demo runbook for Review 2 ("run it from your project folder")

**Pre-flight, 30 minutes before your turn:**
1. Open 3 terminals in the project folder and run `conda activate stripcheck` in each.
2. **Terminal 1:** `phoenix serve`. Wait for "Phoenix is up and running".
3. **Terminal 2:** `python cli.py doctor --warm`. Everything should be OK and the model should be loaded. Ollama's `keep_alive` is 30 minutes, so warm it again if you wait longer.
4. **Terminal 3:** `streamlit run app.py`. Keep browser tabs open on `localhost:8501` and `localhost:6006`.
5. Run every demo prop once, then refresh the page.
6. Plug in the charger, disable sleep, and close heavy apps (DaVinci Resolve, browsers with many tabs). No internet is needed.

**Script, about 4 minutes:**
1. **(30 s) Real data.** Open the Alert lists tab: real CDSCO lists, the row counts, the quarantine with reasons. Mention: "CDSCO changed its format in Aug 2025; our ingest agent validates a new layout before trusting it."
2. **(40 s)** `01_flagged_clean` → FLAGGED with the citation; walk the evidence table.
3. **(60 s)** `03_misread`. Show:
   - OCR read `B3T…` with confidence about 1.0;
   - exact search finds nothing;
   - the agent suspects a misread and searches confusion variants;
   - it finds `BBT…`, and product, dates and maker all match;
   - it asks one question; you answer; FLAGGED.

   Then open the Phoenix trace.
4. **(30 s)** `06_trap_collision` → NOT_LISTED: "Same batch number as a CDSCO entry, but a different product and maker, so it's rejected. A lookup script would raise a false alarm here."
5. **(30 s)** `04_suspected_fake` → SUSPECTED_FAKE.
6. **(20 s)** Switch the planner to `rules`; it still runs. Point out the bounded loops and the fallbacks.
7. **(20 s)** What's next for R3/R4: the evaluation and A/B test, cabinet re-checks, the new-portal adapter.

**Fallbacks:**
- **UI breaks:** `python cli.py check data\props\03_misread.jpg`.
- **Phoenix down:** the UI timeline from JSONL.
- **LLM slow:** `rules` mode.
- **DB problem:** re-run `python cli.py ingest --no-llm`, which takes about a minute.

---

## 18. Troubleshooting (Windows)

- **`conda activate` fails in PowerShell:** run `conda init powershell`, then reopen the terminal, or use Anaconda Prompt.
- **`UnicodeEncodeError` in the console:** set `$env:PYTHONUTF8=1` (it's also in `.env`), and keep CLI output ASCII.
- **CDSCO download fails (SSL error, 403 or timeout):** save the file from a browser into `data\raw`. Never set `verify=False`.
- **Ollama not answering:** start the tray app or run `ollama serve`. `ollama ps` shows the loaded model. The first call is slow while the model loads.
- **Port 6006 busy:** `$env:PHOENIX_PORT="6007"; phoenix serve`, and set `STRIPCHECK_PHOENIX_URL=http://localhost:6007`.
- **`ImportError: DLL load failed` for cv2:** `pip uninstall -y opencv-python`, then `pip install --force-reinstall opencv-python-headless`.
- **"database is locked":** use WAL mode, short transactions, one connection per thread, and `check_same_thread=False` for the checkpointer.
- **RapidOCR log spam:** `logging.getLogger("RapidOCR").setLevel(logging.ERROR)`.

---

## Appendix A — Verified code (use verbatim)

### A1. `core/textutils.py` (tested: 19 date formats, legacy/state/portal header layouts, makers, entry types, batch labels, QR payloads)

```python
import re, itertools
from rapidfuzz import fuzz

MONTHS = {m: i for i, m in enumerate(["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"], 1)}
PLACEHOLDERS = {"", "-", "--", "na", "n/a", "nm", "not mentioned", "notmentioned", "nil", "none"}

def parse_month_year(s):
    """'06/2024','6-2024','Jun-24','JUN 2024','June, 2024','Apr--2026','Oct/2023','01/07/2024','JUN.26' -> 'YYYY-MM' or None."""
    if s is None: return None
    t = str(s).strip().lower().replace("–", "-")
    if t in PLACEHOLDERS: return None
    m = re.search(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b", t)          # DD/MM/YYYY
    if m and 1 <= int(m.group(2)) <= 12: return f"{m.group(3)}-{int(m.group(2)):02d}"
    m = re.search(r"\b(\d{1,2})\s*[/\-.]\s*(\d{4}|\d{2})\b", t)               # MM/YYYY or MM/YY
    if m and 1 <= int(m.group(1)) <= 12:
        y = m.group(2); y = "20" + y if len(y) == 2 else y
        return f"{y}-{int(m.group(1)):02d}"
    m = re.search(r"\b([a-z]{3})[a-z]*\.?\s*[,/\-.]*\s*'?(\d{4}|\d{2})\b", t)  # Mon-YY / Month YYYY / JUN.26
    if m and m.group(1) in MONTHS:
        y = m.group(2); y = "20" + y if len(y) == 2 else y
        return f"{y}-{MONTHS[m.group(1)]:02d}"
    return None

def batch_key(s):
    return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())

def squash(s): return re.sub(r"[^a-z]", "", str(s or "").lower())

# canonical field <- header synonyms (squashed); covers legacy PDFs (2024-25) and the 2026 NSQ portal table
HEADER_SYNONYMS = {
    "sno": ["sno", "slno", "srno", "serialno"],
    "product": ["productdrugname", "nameofproduct", "nameofthedrug", "nameofdrugs", "productname", "drugname", "product"],
    "batch": ["batchno", "batchnumber", "batch", "lotno"],
    "mfg": ["manufacturingdate", "mfgdate", "dateofmanufacture", "manufacturingdates"],
    "exp": ["expirydate", "expdate", "dateofexpiry"],
    "maker": ["manufacturedby", "manufacturerdetails", "nameofmanufacturer", "manufacturer"],
    "result": ["nsqresult", "reasonfornsq", "result", "remarks", "testresult"],
    "reported_by": ["reportedbycdscolaboratory", "reportedbystatelaboratory", "reportingbylabstate", "reportedby", "drawnby", "laboratory"],
    "source_level": ["reportingsource"],
    "list_month": ["reportingmonthyear", "reportingmonth"],
}
def map_headers(cells):
    """Return {column_index: canonical_field}. Exact synonym match first, then prefix match. Unmapped columns are left out."""
    out = {}
    for i, c in enumerate(cells):
        sq = squash(c)
        for field, syns in HEADER_SYNONYMS.items():
            if field in out.values(): continue
            if sq in syns or any(sq.startswith(x) for x in syns if len(x) >= 5):
                out[i] = field; break
    return out

def split_portal_dates(s):
    """2026 portal cell: 'Manufacturing Date: Oct-2024Expiry Date: Mar-2027' -> ('2024-10','2027-03')."""
    m1 = re.search(r"manufacturing\s*date\s*:?\s*([A-Za-z0-9/\-. ]+?)(?=expiry|$)", s, re.I)
    m2 = re.search(r"expiry\s*date\s*:?\s*([A-Za-z0-9/\-. ]+)", s, re.I)
    return (parse_month_year(m1.group(1)) if m1 else None, parse_month_year(m2.group(1)) if m2 else None)

def maker_name(raw):
    """'M/s. Shangrila Industries (P) Ltd., (Pharma Division) Mining Rangpo' -> 'Shangrila Industries (P) Ltd'.
    2026 portal: 'Manufacturer Name: XManufactured By: Y' -> Y. Any 'under investigation' -> 'Under Investigation'."""
    t = re.sub(r"\s+", " ", str(raw or "")).strip()
    if "under investigation" in t.lower(): return "Under Investigation"
    m = re.search(r"manufactured\s*by\s*:\s*(.+)$", t, re.I) or re.search(r"manufacturer\s*name\s*:\s*(.+)$", t, re.I)
    if m: t = m.group(1)
    t = re.split(r"\b(?:mkt\.?\s*by|marketed\s*by|manufa?c?tu?red\s*for)\b", t, flags=re.I)[0]
    t = re.sub(r"^m\s*/\s*s\.?\s*", "", t, flags=re.I)
    return t.split(",")[0].strip(" .;:")

def entry_type(result, remarks="", maker="", list_kind=""):
    blob = f"{result} {remarks} {list_kind}".lower()
    if "spurious" in blob or "under investigation" in str(maker).lower(): return "SPURIOUS"
    if "misbrand" in blob: return "MISBRANDED"
    if "adulterat" in blob: return "ADULTERATED"
    return "NSQ"

BATCH_RE = re.compile(r"(?:\bB\.?\s?No\b\.?|\bBatch(?:\s*No\.?|\s*Number)?|\bLot(?:\s*No\.?)?|\bBN\b|\bB\.N\.)\s*[:.\-]?\s*([A-Z0-9][A-Z0-9\-/]{2,19})", re.I)
def find_batch(lines):
    for i, ln in enumerate(lines):
        m = BATCH_RE.search(ln)
        if m: return m.group(1).rstrip("-/"), i
    return None, None

# Characters OCR confuses on foil strips. '3'<->'B' was observed in our own test: a scuffed 'B' read as '3' at confidence 1.0.
CONFUSABLE = {"0": "OQDC", "O": "0QDC", "Q": "O0", "D": "0O", "C": "0O", "1": "IL7T", "I": "1L", "L": "1I", "T": "17",
              "7": "1T", "2": "Z", "Z": "2", "3": "8B", "8": "B3", "B": "83", "4": "A", "A": "4", "5": "S", "S": "5",
              "6": "G", "G": "6", "9": "G"}
def confusion_variants(key, max_subs=2):
    """All batch keys reachable by <= max_subs OCR-confusable substitutions, with the substitutions made."""
    pos = [i for i, c in enumerate(key) if c in CONFUSABLE]
    for n in range(1, max_subs + 1):
        for idx in itertools.combinations(pos, n):
            for repl in itertools.product(*[CONFUSABLE[key[i]] for i in idx]):
                v = list(key)
                for i, r in zip(idx, repl): v[i] = r
                yield "".join(v), [(i, key[i], r) for i, r in zip(idx, repl)]

STOP = set("tablets tablet tab tabs capsules capsule cap caps injection inj ip bp usp mg ml mcg gm g w v and the of for "
           "syrup suspension oral solution sterile film coated gastro resistant gastroresistant prolonged release "
           "er sr xr dr dispersible each contains vial ampoule".split())
def name_tokens(s):
    s = re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower().replace("-", " "))
    return [t for t in s.split() if t not in STOP and not t.isdigit() and len(t) > 1]
def product_coverage(entry_product, pack_text):
    """Share of the entry's name tokens found (fuzzy >= 85) on the pack. The pack may carry extra words (brand, strength)."""
    e, p = name_tokens(entry_product), name_tokens(pack_text)
    if not e or not p: return None
    hit = sum(1 for t in e if max(fuzz.ratio(t, q) for q in p) >= 85)
    return hit / len(e)

GS1_AI = {"01": "gtin", "10": "batch", "11": "mfg", "17": "exp", "21": "serial"}
def parse_qr_payload(txt):
    """GS1 '(01)..(10)..(17)YYMMDD', raw GS1 with FNC1/GS separators, or 'key: value' text. Returns dict (may be empty)."""
    out = {}
    if not txt: return out
    for ai, val in re.findall(r"\((\d{2})\)([^()]+)", txt):
        if ai in GS1_AI: out[GS1_AI[ai]] = val.strip()
    if not out and re.match(r"^\]?(?:d2|Q3)?01\d{14}", txt):
        rest = re.sub(r"^\](?:d2|Q3)", "", txt)
        while rest:
            ai = rest[:2]
            if ai in ("01",): out["gtin"], rest = rest[2:16], rest[16:]
            elif ai in ("11", "17"): out[GS1_AI[ai]], rest = rest[2:8], rest[8:]
            elif ai in ("10", "21"):
                val, _, rest = rest[2:].partition("\x1d"); out[GS1_AI[ai]] = val
            else: break
    for k in ("mfg", "exp"):
        v = out.get(k)
        if v and re.fullmatch(r"\d{6}", v): out[k] = f"20{v[:2]}-{v[2:4]}"
    if "batch" not in out:
        m = re.search(r"(?:batch\s*(?:no\.?|number)?|b\.?\s?no\.?|lot\s*(?:no\.?)?)\s*[:#.\-]?\s*([A-Z0-9][A-Z0-9\-/]{2,19})", txt, re.I)
        if m: out["batch"] = m.group(1)
        for k, pat in (("mfg", r"(?:mfg|mfd|manufactur\w*)\s*(?:date|dt)?\s*[:.\-]?\s*([A-Za-z0-9/\-. ]{4,12})"),
                       ("exp", r"(?:exp\w*)\s*(?:date|dt)?\s*[:.\-]?\s*([A-Za-z0-9/\-. ]{4,12})")):
            m = re.search(pat, txt, re.I)
            if m and parse_month_year(m.group(1)): out[k] = parse_month_year(m.group(1))
    return out

# ---- pack-side label parsing (tested on 8 label layouts; 'Mfd. by' is never read as a date) ----
DATE_TXT = r"([A-Za-z]{3,9}\.?[\s\-/.,']*\d{2,4}|\d{1,2}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{4}|\d{1,2}\s*[/\-.]\s*\d{2,4})"
MFG_RE = re.compile(r"\b(?:Mfg|Mfd|MFD|Manufacturing|Mfg\.?\s*Date|Date\s*of\s*Mfg)\b\.?\s*(?:Date|Dt)?\.?\s*[:\-]?\s*(?!by\b)" + DATE_TXT, re.I)
EXP_RE = re.compile(r"\b(?:Exp|Expiry|Use\s*before|Best\s*before)\b\.?\s*(?:Date|Dt)?\.?\s*[:\-]?\s*" + DATE_TXT, re.I)
MAKER_RE = re.compile(r"\b(?:Mfd\.?\s*by|Mfg\.?\s*by|Manufactured\s*by)\s*[:\-]?\s*(.+)", re.I)
MKT_RE = re.compile(r"\b(?:Mkt\.?\s*by|Marketed\s*by)\s*[:\-]?\s*(.+)", re.I)

def find_dates(lines):
    """Label-anchored dates. 'Mfg. 06/2024 Exp.05/2026' on one line -> ('2024-06', '2026-05')."""
    text = " | ".join(lines)
    m1, m2 = MFG_RE.search(text), EXP_RE.search(text)
    return (parse_month_year(m1.group(1)) if m1 else None, parse_month_year(m2.group(1)) if m2 else None)

def find_party(lines, rx):
    """find_party(lines, MAKER_RE) -> manufacturer text; find_party(lines, MKT_RE) -> marketer text."""
    for ln in lines:
        m = rx.search(ln)
        if m: return m.group(1).strip(" ,.;:")
    return None
```

### A2. `core/matching.py` (tested: 7 scenarios, all pass)

```python
from rapidfuzz import fuzz
from core.textutils import batch_key, confusion_variants, product_coverage, maker_name

def build_index(rows):
    """rows: dicts from the alerts table. Returns {batch_key: [row, ...]}."""
    idx = {}
    for r in rows:
        idx.setdefault(r["batch_key"], []).append(r)
    return idx

def search_exact(index, key):
    return [dict(r, how="exact", subs=[]) for r in index.get(key, [])]

def search_variants(index, key, prior=None, max_subs=2):
    """OCR-confusion variants of key that exist in the index. prior: {(ocr_char, true_char): count} learned from users."""
    prior = prior or {}
    hits = []
    for v, subs in confusion_variants(key, max_subs):
        for r in index.get(v, []):
            hits.append(dict(r, how="variant", subs=subs))
    hits.sort(key=lambda h: (len(h["subs"]), -sum(prior.get((o, t), 0) for _, o, t in h["subs"])))
    return hits

def grade(entry, f):
    """entry: alert row (+how, subs). f: pack fields {product_text, mfg, exp, maker}. Returns entry + evidence + status + confidence."""
    ev = {"batch": entry["how"]}
    cov = product_coverage(entry["product"], f.get("product_text", ""))
    ev["product"] = "unknown" if cov is None else "match" if cov >= 0.8 else "partial" if cov >= 0.5 else "mismatch"
    pairs = [(entry.get(k), f.get(k)) for k in ("mfg", "exp") if entry.get(k) and f.get(k)]
    ev["dates"] = "unknown" if not pairs else "match" if all(a == b for a, b in pairs) else "mismatch"
    if entry["entry_type"] == "SPURIOUS":
        ev["maker"] = "n/a"
    elif not f.get("maker"):
        ev["maker"] = "unknown"
    else:
        ev["maker"] = "match" if fuzz.token_set_ratio(entry["maker_name"].lower(), maker_name(f["maker"]).lower()) >= 85 else "mismatch"
    entry_has_dates = bool(entry.get("mfg") or entry.get("exp"))
    conf = "high"
    if "mismatch" in (ev["product"], ev["dates"], ev["maker"]):
        st = "reject"                                    # batch collision or a different product: never flag
    elif ev["product"] == "partial" and not (ev["dates"] == "match" and ev["maker"] == "match"):
        st = "adjudicate"                                # LLM decides same/different product (rules mode: ask for more evidence)
    elif ev["batch"] not in ("exact", "confirmed", "auto_corrected"):
        st = "needs_confirm_char"                        # human confirms the substituted character
    elif ev["product"] == "unknown":
        st = "needs_more_evidence"
    elif entry["entry_type"] == "SPURIOUS":
        if ev["dates"] == "match": st = "accept"
        elif not entry_has_dates: st, conf = "accept", "medium"   # CDSCO entry gives no dates to compare
        else: st = "needs_more_evidence"
    elif ev["dates"] == "match" or ev["maker"] == "match":
        st = "accept"
        if not (ev["dates"] == "match" and ev["maker"] == "match"): conf = "medium"
    else:
        st = "needs_more_evidence"                       # e.g. strip shows only the marketer and no dates
    return dict(entry, evidence=ev, status=st, confidence=conf)

def decide(graded, read_ok):
    """Returns (label, top_entry). label in FLAGGED | SUSPECTED_FAKE | NOT_LISTED | CANT_VERIFY | ASK."""
    acc = [g for g in graded if g["status"] == "accept"]
    if acc:
        top = sorted(acc, key=lambda g: (g["entry_type"] != "SPURIOUS", g["confidence"] != "high"))[0]
        return ("SUSPECTED_FAKE" if top["entry_type"] == "SPURIOUS" else "FLAGGED"), top
    pending = [g for g in graded if g["status"] in ("needs_confirm_char", "needs_more_evidence", "adjudicate")]
    if pending:
        return "ASK", pending[0]
    return ("NOT_LISTED" if read_ok else "CANT_VERIFY"), None
```

Notes:
- After a `confirm_char` answer where the user picks the listed character, set the candidate's `how` to `"confirmed"` and re-grade. This was tested: the misread candidate then grades `accept`.
- `"auto_corrected"` is never set (§10: the learned prior orders variants but never skips the question). Leave the tuple as it is.
- In `decide`, `ASK` means "the planner should ask". If no asks remain, or the user declined, the planner drafts `CANT_VERIFY`, giving the pending candidate as the reason.

### A3. Tests to include

`tests/test_textutils.py`:

```python
from core.textutils import *

def test_dates():
    cases = {"06/2024":"2024-06","6-2024":"2024-06","Jun-24":"2024-06","JUN 2024":"2024-06","June, 2024":"2024-06",
             "Apr--2026":"2026-04","Oct/2023":"2023-10","01/07/2024":"2024-07","JUN.26":"2026-06","09-2026":"2026-09",
             "Mfg. 06/2024":"2024-06","Exp.05/2026":"2026-05","NM":None,"N/A":None,"Not Mentioned":None,"":None,
             "Feb-2026":"2026-02","Mar-28":"2028-03","05/27":"2027-05"}
    for k, v in cases.items():
        assert parse_month_year(k) == v, k

def test_headers_legacy_state_portal():
    legacy = ['S.No', 'Product/Drug Name', 'Batch No.', 'Manufacturin\ng Date', 'Expiry\nDate', 'Manufactured By', 'NSQ Result', 'Reported by\nCDSCO\nLaboratory']
    portal = ["S.No", "Name of Product", "Batch No", "Manufacturing Dates", "Manufacturer Details", "Reporting Source", "Reporting by Lab/State", "Reporting Month & Year", "Remarks"]
    assert map_headers(legacy) == {0:'sno',1:'product',2:'batch',3:'mfg',4:'exp',5:'maker',6:'result',7:'reported_by'}
    assert map_headers(portal) == {0:'sno',1:'product',2:'batch',3:'mfg',4:'maker',5:'source_level',6:'reported_by',7:'list_month',8:'result'}
    assert split_portal_dates("Manufacturing Date: Oct-2024Expiry Date: Mar-2027") == ("2024-10", "2027-03")

def test_makers_types_batches_qr():
    assert maker_name("M/s. Shangrila Industries (P) Ltd., (Pharma Division) Mining Rangpo East Sikkim-737132") == "Shangrila Industries (P) Ltd"
    assert maker_name("Manufacturer Name: Under InvestigationManufactured By: Under Investigation") == "Under Investigation"
    assert maker_name("M/s.Hygeia Labs, Baddi Mkt By : Alkem Labs Ltd") == "Hygeia Labs"
    assert entry_type("SPURIOUS") == "SPURIOUS" and entry_type("Dissolution") == "NSQ" and entry_type("Misbranded") == "MISBRANDED"
    assert entry_type("", "NSQ Remark: The product is purported to be spurious") == "SPURIOUS"
    assert find_batch(["PANTOSHANG-40", "B.No. SP240165"]) == ("SP240165", 1)
    assert find_batch(["Lot: AD-204 Exp 04/2026"]) == ("AD-204", 0)
    assert parse_qr_payload("(01)08901234567890(10)SP240165(11)240601(17)260531") == {"gtin":"08901234567890","batch":"SP240165","mfg":"2024-06","exp":"2026-05"}
    assert parse_qr_payload("Brand: Dolo 650\nBatch No: DOBS3975\nMfg: 03/2025\nExp: 02/2028") == {"batch":"DOBS3975","mfg":"2025-03","exp":"2028-02"}
    assert any(v == "BBT2305" for v, _ in confusion_variants("B3T2305"))
    assert product_coverage("Telapp MT 25 (Telmisartan & Metoprolol Succinate (ER) Tablets)", "Telma 40 Telmisartan Tablets IP 40 mg") < 0.5

def test_pack_labels():
    assert find_dates(["Mfg. 06/2024    Exp. 05/2026"]) == ("2024-06", "2026-05")
    assert find_dates(["Mfg.06/2024 Exp.05/2026"]) == ("2024-06", "2026-05")
    assert find_dates(["MFD. 06/2024", "EXP. 05/2026"]) == ("2024-06", "2026-05")
    assert find_dates(["Mfd. by: Shangrila Industries (P) Ltd.,", "Mfg. Date: Jun-2024", "Exp. Date: May-2026"]) == ("2024-06", "2026-05")
    assert find_dates(["MFG.DT. 11/24 EXP.DT. 10/26"]) == ("2024-11", "2026-10")
    assert find_dates(["Manufacturing Date: 01/07/2024", "Expiry Date: 30/06/2026"]) == ("2024-07", "2026-06")
    assert find_dates(["Use before JUN.26"]) == (None, "2026-06")
    assert find_dates(["Mfd. by: Demo Remedies Pvt. Ltd."]) == (None, None)
    assert find_party(["Mfd. by: Shangrila Industries (P) Ltd.,", "Rangpo"], MAKER_RE) == "Shangrila Industries (P) Ltd"
    assert find_party(["Mkt. by: Alkem Laboratories Ltd."], MKT_RE) == "Alkem Laboratories Ltd"
```

`tests/test_matching.py` covers the 7 scenarios (expected: FLAGGED, ASK, NOT_LISTED, SUSPECTED_FAKE, SUSPECTED_FAKE, ASK, NOT_LISTED):

```python
from core.textutils import batch_key
from core.matching import build_index, search_exact, search_variants, grade, decide

E = [
 dict(id=1, product="Pantoprazole GastroResistant Tablets IP (Pantoshang-40)", batch_key="SP240165", mfg="2024-06", exp="2026-05", maker_name="Shangrila Industries (P) Ltd", entry_type="NSQ"),
 dict(id=2, product="Telapp MT 25 (Telmisartan & Metoprolol Succinate (ER) Tablets)", batch_key="T24H459A", mfg="2024-08", exp="2026-07", maker_name="Bajaj Formulation", entry_type="NSQ"),
 dict(id=3, product="Cefixime Dispersible Tablets IP", batch_key="TC2439", mfg="2024-10", exp="2027-03", maker_name="Under Investigation", entry_type="SPURIOUS"),
 dict(id=4, product="Paracetamol Tablets IP 650 mg (Demo-650)", batch_key="BBT2305", mfg="2025-01", exp="2027-12", maker_name="Demo Remedies Pvt Ltd", entry_type="NSQ"),
 dict(id=5, product="Gentamicin Injection I.P. 30 ml", batch_key="GJ2309", mfg=None, exp=None, maker_name="Under Investigation", entry_type="SPURIOUS"),
]
IDX = build_index(E)

def run(f):
    k = batch_key(f["batch"]); c = search_exact(IDX, k)
    if not any(grade(x, f)["status"] == "accept" for x in c): c += search_variants(IDX, k)
    return decide([grade(x, f) for x in c], read_ok=True)[0]

def test_scenarios():
    assert run(dict(batch="SP240165", product_text="PANTOSHANG-40 Pantoprazole Gastro-Resistant Tablets IP", mfg="2024-06", exp="2026-05", maker="Shangrila Industries (P) Ltd.")) == "FLAGGED"
    assert run(dict(batch="B3T2305", product_text="DEMO-650 Paracetamol Tablets IP 650 mg", mfg="2025-01", exp="2027-12", maker="Demo Remedies Pvt. Ltd.")) == "ASK"
    assert run(dict(batch="T24H459A", product_text="Telma 40 Telmisartan Tablets IP 40 mg", mfg="2024-03", exp="2027-02", maker="Glenmark Pharmaceuticals Ltd.")) == "NOT_LISTED"
    assert run(dict(batch="TC2439", product_text="Cefixime Dispersible Tablets IP 200 mg", mfg="2024-10", exp="2027-03", maker="")) == "SUSPECTED_FAKE"
    assert run(dict(batch="GJ-2309", product_text="Gentamicin Injection IP 30 ml", mfg="2024-02", exp="2026-01", maker="")) == "SUSPECTED_FAKE"
    assert run(dict(batch="SP240165", product_text="PANTOSHANG-40 Pantoprazole Gastro-Resistant Tablets IP", mfg=None, exp=None, maker="")) == "ASK"
    assert run(dict(batch="DOBS3975", product_text="Dolo 650 Paracetamol Tablets IP", mfg="2025-03", exp="2028-02", maker="Micro Labs Ltd")) == "NOT_LISTED"
```

---

## Appendix B — Verified patterns (run on langgraph 1.2.16, langgraph-checkpoint-sqlite 3.1.2, arize-phoenix 20.24.0, arize-phoenix-otel 0.17.2, openinference-instrumentation-langchain 0.1.79, rapidocr 3.10.0, OpenCV 5.0)

### B1. Stream, interrupt and resume across processes

```python
import sqlite3, operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.sqlite import SqliteSaver

def ask(state):
    ans = interrupt({"kind": "confirm_char", "question": "Is character 2 'B' or '3'?", "options": ["B", "3", "Can't tell"]})
    return {"answers": [ans]}                      # side effects only AFTER interrupt() returns

app = graph.compile(checkpointer=SqliteSaver(sqlite3.connect("data/checkpoints.db", check_same_thread=False)))
cfg = {"configurable": {"thread_id": "check-1a2b3c4d"}}
for chunk in app.stream({"images": [path]}, cfg, stream_mode="updates"):
    # node updates arrive as {"node_name": {...}}; an interrupt arrives as
    # {"__interrupt__": (Interrupt(value={...}, id="..."),)}
    ...
state = app.get_state(cfg)          # state.next == ("ask_user",), state.interrupts[0].value == the payload
for chunk in app.stream(Command(resume={"choice": "B"}), cfg, stream_mode="updates"):   # works from a NEW process too
    ...
```

### B2. Durable resume after a crash

```python
try:
    app.invoke({"files": files, "i": 0}, cfg)
except Exception:
    pass                                  # state saved up to the last completed node; get_state(cfg).next == ("failed_node",)
app.invoke(None, cfg)                     # later, any process: re-runs the failed node and continues to END
```

### B3. Phoenix tracing with properly nested tool spans

```python
# core/tracing.py
from phoenix.otel import register
TP = register(project_name="stripcheck", endpoint="http://localhost:6006/v1/traces",
              auto_instrument=True, batch=True, verbose=False)   # wrap in try/except; None if Phoenix is down

# tools: LangChain @tool, invoked INSIDE nodes WITH config -> nested TOOL spans
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

@tool
def ocr_read_tool(image_path: str, enhanced: bool = False) -> dict:
    """Read text lines from a pack image with OCR."""
    return ocr_read(image_path, enhanced)

def read_text(state: CheckState, config: RunnableConfig):
    r = ocr_read_tool.invoke({"image_path": state["images"][-1]}, config=config)
    return {"ocr": state.get("ocr", []) + [r]}

app.invoke(inp, {"run_name": "investigator", "configurable": {"thread_id": tid}})
# Verified span tree in Phoenix: investigator (CHAIN) -> read_text (CHAIN) -> ocr_read_tool (TOOL, input/output captured)
# Calling plain decorated functions WITHOUT config produced root-level spans (not nested) -> always pass config.
```

### B4. Streamlit HITL loop

This is a pattern; the stream semantics are verified in B1.

```python
import streamlit as st
from langgraph.types import Command

@st.cache_resource
def get_graph():
    return build_investigator()            # compiled with SqliteSaver(check_same_thread=False)

def run(inp):
    g = get_graph(); cfg = {"configurable": {"thread_id": st.session_state.tid}, "run_name": "investigator"}
    st.session_state.pending = None
    with st.status("Agent working...", expanded=True) as box:
        for chunk in g.stream(inp, cfg, stream_mode="updates"):
            if "__interrupt__" in chunk:
                st.session_state.pending = chunk["__interrupt__"][0].value
            else:
                for node, upd in chunk.items():
                    for h in (upd or {}).get("history", []):
                        box.write(f"Step {h['step']} - planner ({h['source']}): {h['thought']} -> {h['action']}")
    st.session_state.final = g.get_state(cfg).values.get("final")

if st.button("Run check"):
    st.session_state.tid = "check-" + uuid.uuid4().hex[:8]
    run({"images": [saved_path], "planner_mode": mode})
if st.session_state.get("pending"):
    p = st.session_state.pending
    st.warning(p["question"])
    # render widgets by p["kind"]; on submit:
    # run(Command(resume={"choice": choice}))  /  {"image_path": ...}  /  {"typed": ...}  /  {"skip": True}
```

### B5. QR, OCR and enhancement

```python
import cv2, numpy as np, logging
from rapidocr import RapidOCR
logging.getLogger("RapidOCR").setLevel(logging.ERROR)
ENGINE = RapidOCR()                                   # models are bundled in the wheel; about 1 s per pack image on CPU

res = ENGINE(image_path_or_bgr_array)                 # res.txts (tuple[str]), res.scores (tuple[float]), res.boxes
val, pts, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(path))   # '' when not found (blurred QR fails -> fall back to OCR)

def enhance(bgr):
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    g = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(g)
    g = cv2.filter2D(g, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
```

### B6. pdfplumber strategy A (`lines`)

Verified on a ruled replica of the CDSCO table, including the `Manufacturin\ng Date` header break.

```python
import pdfplumber, re
from core.textutils import map_headers
SNO = re.compile(r"^\s*\d{1,4}\.?\s*$")

def extract_lines(pdf_path):
    rows, header = [], None
    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            for table in page.extract_tables():
                for r in table:
                    cells = [re.sub(r"\s+", " ", c or "").strip() for c in r]
                    m = map_headers(r)
                    if len(m) >= 5 and "batch" in m.values() and "product" in m.values():
                        header = m; continue
                    if not header: continue
                    if SNO.match(cells[0] if cells else ""):
                        rows.append({"page": pno, "row_no": int(re.sub(r"\D", "", cells[0])),
                                     **{f: cells[i] for i, f in header.items() if i < len(cells)}})
                    elif rows and cells and not cells[0] and any(cells[1:]):   # empty S.No = continuation of a row split across pages
                        for i, f in header.items():                             # (rows like "NOTE: ..." have text in S.No and are skipped)
                            if i < len(cells) and cells[i]:
                                rows[-1][f] = (rows[-1].get(f, "") + " " + cells[i]).strip()
    return rows
# On an UNRULED table extract_tables() returns nothing and pdfplumber's "text" strategy gives a scrambled grid
# -> that's why strategy B (row chunks + grounded LLM) exists.
```

### B7. LLM call with schema, timeout and fallback (`core/llm.py`)

```python
from langchain_ollama import ChatOllama
from core import config

def structured(schema, system, user, run_config=None):
    """Returns a schema instance, or None on any failure (Ollama down, timeout, invalid output)."""
    try:
        llm = ChatOllama(model=config.LLM_MODEL, base_url=config.OLLAMA_URL, temperature=0, num_ctx=4096,
                         keep_alive="30m", client_kwargs={"timeout": config.LLM_TIMEOUT})
        return llm.with_structured_output(schema, method="json_schema").invoke(
            [("system", system), ("human", user)], config=run_config)
    except Exception as e:                      # httpx.ConnectError when Ollama is off (verified)
        print(f"[llm] fallback: {type(e).__name__}")
        return None
```

---

## Appendix C — LLM schemas and prompts (Pydantic, `method="json_schema"`)

Keep the prompts short; a 3B model follows short, explicit instructions best. Pass the user content as compact JSON.

```python
from typing import Literal
from pydantic import BaseModel, Field

ACTIONS = Literal["read_qr", "read_text", "reread_enhanced", "extract_fields", "search_exact", "search_variants",
                  "search_by_product", "grade", "ask_user", "draft_verdict"]

class PlannerDecision(BaseModel):
    thought: str = Field(description="one short sentence: what is uncertain and why this action helps")
    action: ACTIONS
# system: "You plan the next step of an agent that checks whether a medicine pack's batch is on CDSCO alert lists.
#  Choose exactly one action from `allowed`. Prefer the cheapest action that resolves the biggest uncertainty.
#  Never choose draft_verdict before a search unless the batch is unreadable. Asking the user is limited; use it
#  only when evidence is missing from the photo. `rule_suggestion` is a safe default."
# user: {"evidence": {...compact...}, "allowed": [...], "rule_suggestion": "...", "critique": {...}|null}

class PackFields(BaseModel):
    brand: str | None; generic_name: str | None; strength: str | None
    batch: str | None; mfg: str | None; exp: str | None
    manufacturer: str | None; marketer: str | None
# system: "Extract fields from OCR lines of an Indian medicine pack. Copy values exactly as printed. Never guess;
#  use null when absent. 'Mfd.' followed by a date is the manufacturing date; 'Mfd. by' is the manufacturer.
#  'Mkt. by' / 'Marketed by' is the marketer."
# user: {"lines": [[i, text, score], ...]}

class ProductJudgement(BaseModel):
    same_product: Literal["yes", "no", "unsure"]
    reason: str
# system: "Decide if a CDSCO alert entry and a medicine pack name the same product (same active ingredients and
#  dosage form; a brand in brackets must match the pack's brand if the pack shows one). Answer unsure if unclear."
# user: {"entry_product": "...", "pack": {"brand": ..., "generic": ..., "strength": ...}}

class HeaderMap(BaseModel):
    mapping: dict[str, Literal["sno", "product", "batch", "mfg", "exp", "maker", "result", "reported_by",
                               "source_level", "list_month", "ignore"]]
# system: "Map each column header of a drug-alert table to a canonical field. Use 'ignore' if none fits."
# user: {"headers": [...], "sample_rows": [[...], [...]]}

class AlertRow(BaseModel):
    product: str | None; batch: str | None; mfg: str | None; exp: str | None
    maker: str | None; result: str | None; reported_by: str | None
# system: "Split this row of a CDSCO drug-alert table into fields. Copy text exactly; never invent values; null if absent."
# user: {"headers": [...], "raw": "..."}            -> grounding guard in §7.6 is mandatory

class SourceMeta(BaseModel):
    list_kind: Literal["nsq", "spurious"]; list_level: Literal["central", "state", "unknown"]; list_month: str | None
# user: {"filename": "...", "first_page_text": "...first 800 chars..."}

class Critique(BaseModel):
    approve: bool
    problems: list[str]
# system: "Check an agent's verdict text against its evidence. Disapprove if the text claims anything the evidence
#  does not show, calls a medicine safe or genuine, or tells anyone to stop a medicine."
# user: {"verdict": {...}, "evidence": {...}}
```

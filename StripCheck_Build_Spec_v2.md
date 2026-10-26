# StripCheck — Build Spec v2.0

*Agentic AI (26CD7PEAAI) mini-project · design phase output, 25 Oct 2026 · supersedes v1.1 for scope, architecture and build order. The verified code in v1.1 Appendices A–C stays the base; §A of this file lists the only amendments, each with a test.*

**Read order for implementers (human or agent):** this file → `docs/design/ui_direction.md` → `StripCheck_Build_Spec.md` (v1.1) Appendices A–C → `research_notes/StripCheck engineering scan/*.md` → `CLAUDE.md`.

---

## 0. What changed from v1.1, and why

| # | Change | Why (evidence) |
|---|---|---|
| C1 | **Primary data source is CDSCO's SUGAM portal JSON** (Jan 2019 → Sep 2026, 93 NSQ months + spurious feed), not hand-saved PDFs | Found in the browser on 25 Oct 2026: `cdscoonline.gov.in/CDSCO/filteredNsqDrugTable?month=…&source=All&tab=nsq` is a plain GET returning clean JSON, including a separate **brand** field. A polite snapshot pulled every month with no failures (research_notes/…/cdsco_data_sources.md). v1.1 assumed the post-Aug-2025 data needed a manual browser save and would have stopped at June 2025. |
| C2 | Legacy PDFs become a **secondary** source: provenance crops + an automatic parsing-accuracy check against the JSON for overlapping months | Gives the ingest agent's PDF skills a measurable job instead of being the only data path. |
| C3 | **Streamlit replaced by FastAPI + a custom React UI** streamed over SSE, usable from a phone on the LAN | Streamlit's rerun model fights streaming + HITL, and the owner asked for a UI that does not look generated. Design system in `docs/design/ui_direction.md`. |
| C4 | **Batch-confirmation gate before any alarm** (`confirm_batch`): FLAGGED/SUSPECTED_FAKE needs the batch to come from QR, the user, or two agreeing independent reads | Closes a false-alarm path v1.1 missed: a confident OCR misread that lands *exactly* on a listed sibling batch (same product, maker and month, one confusable character apart) passes every corroboration check as an "exact" hit. v1.1 only asked humans about *variant* hits. |
| C5 | **Brand corroboration** and **date-conflict handling** in grading | The portal now gives a brand field; a brand mismatch is strong collision evidence. A single date typo or misread no longer silently rejects a true match: one-digit differences are asked, larger ones become CANT_VERIFY with the reason, never NOT_LISTED. |
| C6 | **Noisy-channel variant ranking** from a confusion matrix learned from calibration renders + user confirmations (Dirichlet-smoothed) | Replaces the ad-hoc count sort with a defensible model; the prior still never skips the question (v1.1 §10 kept). |
| C7 | Optional **second reader**: a small local vision-language model via Ollama, used only for agreement, never as sole evidence for an alarm | An independent model family is the only automatic way to catch confident OCR misreads. GPU available (RTX 4050, 6 GB). |
| C8 | **Character crops** in every human question (the real pixels of the doubted glyph) | People answer "is it B or 3?" far better when they see the exact glyph the camera saw. |
| C9 | **Text mode** (type a batch, no photo), **bill scan** (pharmacy invoice → several checks), **multilingual verdict templates** (English, Hindi, one regional language), **read aloud** | Pharmacist and accessibility use; Indian bills print batch numbers per line item. |
| C10 | **Evaluation v2**: sibling traps, date-conflict cases, a degradation ladder, print-and-capture photos, ablations, LLM model benchmark, paired statistics, cross-source ingest accuracy | Turns the demo into a paper-grade evaluation. |
| C11 | **Paper is a build artefact**: `paper/` (IEEE LaTeX) with numbers generated from the DB (`paper/generated/stats.tex`) and updated at every milestone | Owner requirement: keep the research paper in step with the work. |
| C12 | **Resumable, incrementally-saved agent work** and git commits per milestone | A usage-limit cut-off on 25 Oct 2026 lost 13 of 14 research agents' work; never again. |
| C13 | Optional **MCP server** exposing read-only `lookup_batch` / `search_alerts` | Lets other agents (e.g. Claude Desktop) use StripCheck's index; a natural Agentic-AI extension. |

Everything in v1.1 not contradicted here still applies (ground rules §0, safety §9.8, bounds §9.5, LangGraph gotchas §9.6, troubleshooting §18).

---

## 1. Ground rules (v1.1 §0, plus)

1. Windows 11, PowerShell, conda env `stripcheck`. `pathlib` everywhere, `encoding="utf-8"` for our files (CDSCO JSON is **latin-1**, decode it explicitly), ASCII console output, `PYTHONUTF8=1`.
2. Code style: minimal, flat, procedural Python; `TypedDict`/Pydantic only for data shapes; one module per concern. Frontend: function components, no state-management library unless needed, CSS variables from the design tokens, no UI kit.
3. Never break the demo: every LLM/VLM/network/tracing call has a timeout and a fallback. The app runs with Ollama off, Phoenix off and **no internet** (the check path never touches the network; sync is a separate, explicit action).
4. Bound every loop. No paid APIs.
5. Safety language is a hard requirement (v1.1 §9.8 + §10.9 here). No green for NOT_LISTED.
6. No invented data. Every alert row traces to a stored raw snapshot (`data/raw/…` + sha256). Every pack field is grounded in QR/OCR/VLM text that is itself confirmed, or typed by the user.
7. Tests (`pytest -q`, `npm test`) pass without Ollama, Phoenix or internet. LLM tests are `@pytest.mark.llm` and skipped by default; network tests are `@pytest.mark.net`.
8. **Save work incrementally.** Agents write files early and often, keep a status checklist, resume from what is on disk, and commit at the end of every module (`git` is initialised in M0). Never hold a large amount of unsaved work.
9. **Update the paper** (`paper/`) and `docs/research_log.md` at the end of every milestone (§17).
10. Cite external code, data and models in `README.md` and the paper (CDSCO, RapidOCR/PP-OCR, LangGraph, Phoenix, Ollama and each model's licence).
11. CDSCO copyright policy requires acknowledgement and forbids reproduction without permission: keep raw snapshots local (`data/` is git-ignored), cite the source on every verdict, and publish only derived statistics in the paper.

---

## 2. The decision and the verdicts (v1.1 §1, unchanged labels)

*"Is this exact medicine pack from a batch that CDSCO has flagged?"* Labels: `FLAGGED`, `SUSPECTED_FAKE`, `NOT_LISTED`, `CANT_VERIFY`. User-facing headlines and colours: `docs/design/ui_direction.md` §4.4. The meaning of `NOT_LISTED` is exactly "no surviving match on the lists loaded, as of {latest month}", never a statement about quality.

---

## 3. Data (replaces v1.1 §2 "Real files to ingest", §7.1)

### 3.1 Sources, in priority order

| Source | What | How | Provenance shown to users |
|---|---|---|---|
| `portal` (primary) | NSQ Jan 2019 → latest; spurious 2025 → latest | JSON endpoints below | "CDSCO NSQ portal · {MON-YYYY} · {lab/state}" + link to the viewer |
| `pdf` (secondary) | CDSCO monthly PDFs Jan 2024 → Jul 2025 (central, state, spurious, revised) | `cli.py fetch --pdfs` from the URL table in `research_notes/StripCheck engineering scan/cdsco_data_sources.md` (CDSCO direct, TheHealthMaster mirror as fallback, marked secondary) | rendered crop of the actual table row |
| `state` (optional, M9) | Maharashtra FDA NSQ table (HTML, ~200 rows, no month column) | `cli.py fetch --state mh` | "Maharashtra FDA NSQ list · scraped {date}" |
| `file` (manual) | any `.html/.csv/.xlsx/.pdf` the user drops in `data/raw/manual/` | same validators | file name |

### 3.2 Portal endpoints (verified 25 Oct 2026, no auth, TLS valid, `charset=ISO-8859-1`)

```
GET https://cdscoonline.gov.in/CDSCO/reportingYears?tab=nsq|spurious                 -> ["2019",...]
GET https://cdscoonline.gov.in/CDSCO/publicReportingMonths?year=2025&tab=nsq           -> ["Jan",...]
GET https://cdscoonline.gov.in/CDSCO/filteredNsqDrugTable?month=AUG-2025&source=All&tab=nsq
GET https://cdscoonline.gov.in/CDSCO/filteredSpuriousDrugTable?month=SEP-2026&source=All&tab=spurious
GET https://cdscoonline.gov.in/CDSCO/publicNsqDrugTable          (latest month only)
GET https://cdscoonline.gov.in/CDSCO/viewPublicSpuriousDrugData  (latest month only)
```
Responses: `{"aaData":[{...}]}`. Field lists: research notes, "Browser investigation". Month keys are `<MON>-<YYYY>` built from the month list (`Jan` → `JAN-2025`).

### 3.3 Sync policy (`core/portal.py`)
- One request at a time, **≥ 1.5 s apart**, `User-Agent: StripCheck/2.0 (academic project)`, timeout 60 s, 3 retries with backoff, TLS verification always on.
- Store each response verbatim: `data/raw/portal/{tab}/{YYYY-MM}.json` plus `{YYYY-MM}.meta.json` (`url, fetched_at, sha256, bytes, rows`).
- First sync fetches everything (~110 requests, ~3 min). Later syncs fetch months not yet stored plus the **latest 3 months** (CDSCO shows "Pending States", so rows arrive late). `--full` refetches all.
- Unchanged sha256 → skip. Changed → the ingest agent diffs by `row_hash` (sha1 of the canonical raw row): new rows inserted with `first_seen`, missing rows get `removed_at` (never deleted).
- `--offline` ingests only from stored snapshots: the demo laptop never needs the internet after the first sync.

### 3.4 Field mapping (portal → canonical)
| canonical | NSQ tab | spurious tab |
|---|---|---|
| product | `str_product_name` (strip a trailing "(Brand Name : …)") | `product_name_from_dtl` |
| brand | `str_brand_name` unless `NA/NIL/-`; else the bracketed tail of the product name if it looks like a brand | `str_brand_name` (strip brackets) |
| batch_raw | `str_batch_no` | `str_batch_no` |
| mfg / exp | `dt_manufacturing_date` / `dt_expiry_date` via `parse_month_year` | same |
| maker_raw | `str_manufactured_by` (placeholder `NIL,NIL NIL` → empty) | `str_manufactured_by`, `str_manufacturer_name` |
| result | `str_nsq_result` | `str_nsq_result` |
| remarks / firm_reply | — | `str_nsq_remarks` / `str_firm_reply` |
| reported_by | `str_reported_by_lab_or_state` | same |
| list_level | `str_reporting_source` normalised: contains "cdsco"/"cdl" → central, "state" → state | same |
| list_month | from the request month (trust the request, cross-check `dt_reporting_month_year`, flag mismatches) | same |
| entry_type | `entry_type(result, remarks, maker, list_kind)`; spurious tab or `num_spurious_flag=1` → `SPURIOUS` | |

Unknown keys appearing later (schema drift) go through the LLM `HeaderMap` path (v1.1 §7.4), validated on 5 sample rows before use. This is the portal version of the "CDSCO changed its columns" demo moment.

### 3.5 Data facts to quote (refreshed by `cli.py stats` into `paper/generated/stats.tex`; do not hard-code)
Rows per month 2025-26 range ~94–330; reporting-source and lab spellings vary; brand is "NA" in older months; placeholder makers and odd batch strings exist (`Up -to -01`, `CBC-0012/25`, `155`); some rows lack dates. Section 15.6 lists the statistics the paper needs (collision rate, confusable-neighbour density, alert lag, remaining shelf life at alert).

---

## 4. Architecture

```
                 ┌──────────────────────── Supervisor (LangGraph) ───────────────────────┐
  CLI / API ───► │ route ─► Ingest agent ─► diff ─► Cabinet re-check ─► notify ─► report │
                 └───────────────────────────────────────────────────────────────────────┘
                                │ writes                         ▲ reads
                                ▼                                │
   SQLite (WAL): sources · alerts · quarantine · runs · checks · cabinet · notifications · confusions
                                ▲                                ▲
  Phone / laptop UI ── SSE ──► FastAPI ──► Investigator agent (LangGraph, SqliteSaver threads)
                                             perception: QR → OCR → enhance → [VLM]
                                             retrieval: exact → noisy-channel variants → product hits
                                             grading: blocked record linkage (batch block; product,
                                                      brand, dates, maker comparisons)
                                             HITL: interrupt() → confirm_char / confirm_batch /
                                                   confirm_field / box_photo / type_batch
                                             └─► Verifier agent (hard rules R1–R10 + optional LLM critique)
  Ollama (local LLM + optional VLM) · RapidOCR (ONNX) · Phoenix (optional OTel) · JSONL step logs
```

Agents and their single responsibilities:
- **Ingest agent**: turns any source into validated alert rows; repairs or quarantines; never invents.
- **Investigator**: perceives a pack, retrieves candidates, grades them, asks the person when evidence is missing, drafts a templated verdict.
- **Verifier (critic)**: blocks any draft that breaks a hard rule; may send back once; otherwise downgrades to `CANT_VERIFY`.
- **Supervisor**: background orchestration with memory (sync → re-check cabinet → notify; expiry reminders).

### 4.1 Repository layout
```
AgenticAI StripCheck/            <- repo root (git)
  StripCheck_Build_Spec.md       v1.1 (kept for its verified appendices)
  StripCheck_Build_Spec_v2.md    this file
  CLAUDE.md  AGENTS.md  README.md  requirements.txt  requirements-dev.txt  .env.example  pytest.ini  .gitignore  .gitattributes
  docs/COLLABORATION.md  docs/BUILD_GUIDE.md  docs/BUILD_STATUS.md  docs/HANDOFF.md  docs/decisions.md   (two-machine workflow, D15)
  cli.py                         doctor | sync | fetch | ingest | stats | props | check | serve | recheck | eval | bench | parsecheck | selftest | mcp
  core/
    config.py  db.py  textutils.py  matching.py  noisy.py      (noisy-channel confusion model)
    llm.py  vlm.py  tracing.py
    portal.py                    SUGAM fetch + snapshot cache
    ingest.py  ingest_agent.py   adapters (portal/pdf/html/csv/xlsx), validate, repair, diff, commit
    pack_tools.py  crops.py      QR/OCR/enhance/extract, character boxes and crops
    alert_tools.py  investigator.py  verifier.py  supervisor.py
    templates.py                 verdict templates (en/hi/+1), banned-phrase filter
    props.py  degrade.py  evaluate.py  bench.py  analysis.py
  server/
    app.py                       FastAPI app factory, static files, CORS off
    routes_checks.py  routes_alerts.py  routes_cabinet.py  routes_eval.py  routes_system.py
    sse.py                       graph-stream -> SSE bridge
  web/                           Vite + React + TypeScript (see ui_direction.md)
    src/{app,components,screens,lib,styles}/  public/  package.json  vite.config.ts
  mcp_server.py                  optional (M9)
  data/   raw/{portal,pdf,state,manual}/  props/  eval/  photos/  uploads/  stripcheck.db  checkpoints.db
  runs/                          JSONL step logs, eval outputs
  paper/                         IEEE LaTeX: main.tex, sections/, figures/, generated/, references.bib
  docs/  design/  research_log.md  decisions.md
  research_notes/  reports/      literature survey (deep-research output)
  tests/
```

---

## 5. Stack and environment

Machine (checked 25 Oct 2026): Windows 11, Ryzen AI 9 HX 370 (12C/24T), 31 GB RAM, **RTX 4050 Laptop 6 GB**, Ollama 0.17.7 running (only `mistral:latest` pulled so far), Anaconda (no `stripcheck` env yet), Node 24.11.1, Git, TeX Live 2025 with `latexmk` and `IEEEtran`.

- **Python**: conda env `stripcheck`, Python 3.11 (v1.1's verified version) unless the tech scan (`research_notes/StripCheck engineering scan/tech_stack_oct2026.md`) finds a blocker; it may recommend 3.12.
- **Python packages**: v1.1 §3 list **minus** `streamlit`, **plus** `fastapi`, `uvicorn[standard]`, `sse-starlette`, `python-multipart`, `zxing-cpp`, `matplotlib`, `scipy`, `statsmodels`; dev: `pytest`, `hypothesis`, `reportlab`, `httpx`; optional: `mcp`. Exact pins are taken from the tech scan in M0 and written to `requirements.txt`; deviations from v1.1's verified pins are recorded in `README.md` → "Deviations".
- **Frontend**: Vite + React + TypeScript; `@fontsource` packages for Archivo, Atkinson Hyperlegible Next and Mono, Noto Sans Devanagari and Kannada; `@phosphor-icons/react`. No UI kit, no CSS framework, no CDN.
- **Models** (pull in M0; the default is chosen by the M4 benchmark, not by taste):
  - LLM candidates: `qwen2.5:3b` (v1.1 baseline) and the 2–3 strongest ≤8B instruct models from the tech scan that fit 6 GB VRAM with an 8k context. Reasoning ("thinking") variants are called with thinking off for structured output.
  - VLM candidate (optional second reader): the best ≤4B vision model from the tech scan that fits next to OCR on the GPU.
- **Paper**: `latexmk -pdf paper/main.tex` (TeX Live 2025).

### 5.1 Pinned stack (from the tech scan of 26 Oct 2026; `research_notes/StripCheck engineering scan/tech_stack_oct2026.md`)

**Python 3.12** (not 3.11): numpy 2.5 and scipy 1.18 ship no cp311 wheels, and the laptop's default 3.10 is unsupported by several packages. Create `conda create -n stripcheck python=3.12`, then `pip install --dry-run -r requirements.txt` before anything else (the pins were checked against PyPI metadata, not a resolver).

```
langgraph>=1.2.16,<2                 # 1.2.16-1.2.17 fix several interrupt/resume bugs
langgraph-checkpoint-sqlite>=3.1.2,<4
langchain-core>=1.7,<2
langchain-ollama>=1.1,<2
ollama>=0.6.3,<1
pydantic>=2.12,<3
rapidocr>=3.10,<4                    # defaults to PP-OCRv6 since 3.9: set Det/Rec ocr_version explicitly
onnxruntime>=1.31,<2                 # CPU build for OCR; the GPU stays with Ollama
opencv-python-headless>=4.14,<5      # pip would otherwise pick 5.0 (unverified with rapidocr)
pdfplumber>=0.11.10,<0.12
pypdfium2>=5.14,<6
rapidfuzz>=3.14,<4
qrcode[pil]>=8.2,<9
zxing-cpp>=3.1,<4
pillow>=12.3,<14
numpy>=2.5,<3
pandas>=3.1,<4
requests>=2.34,<3
python-dotenv>=1.2.4,<2
arize-phoenix-otel>=0.17.2,<1
openinference-instrumentation-langchain>=0.1.80,<0.2
fastapi>=0.135,<1                    # native SSE in fastapi.sse; sse-starlette is not needed
uvicorn[standard]>=0.54,<1
python-multipart>=0.0.32,<1
matplotlib>=3.11,<4
scipy>=1.18.1,<2
statsmodels>=0.15,<0.16
```
`requirements-dev.txt`: `pytest>=9.1,<10`, `hypothesis>=6.170,<7`, `reportlab>=5.1,<6`, `httpx>=0.28.1,<0.29`. Optional: `mcp>=2.3,<3` (v2 renamed FastMCP: `from mcp.server.mcpserver import MCPServer`). **Phoenix server in its own venv** (`pip install "arize-phoenix>=20.26.1,<21"`, `phoenix serve`): it pins many exact dependencies and releases almost daily. Fresh major versions (pillow 13, pandas 3, zxing-cpp 3, reportlab 5) are allowed but M0 runs the full test suite against them before going further; if one breaks, cap it below the major and record the deviation.

**Implementation notes from the scan.** `get_stream_writer` comes from `langgraph.config`; `interrupt(..., response_schema=Model)` (LangGraph ≥ 1.2.12) validates resume values, which suits our ask payloads. `SqliteSaver` is synchronous and lock-serialised: the server runs graphs in worker threads and one process owns `data/checkpoints.db` (switch to `AsyncSqliteSaver` only if the server goes fully async). RapidOCR's `engine(img, return_word_box=True)` returns word boxes for the character-crop step; Devanagari recognisers exist in PP-OCRv5/v4, not v6, and no Kannada recogniser exists.

**Ollama.** The laptop runs 0.17.7; the current release is 0.40.x. 0.17.7 can run `qwen2.5:3b`, `qwen3:4b`, `granite4:3b` (Apache 2.0), `phi4-mini`, `ministral-3:3b` (Apache 2.0) and the vision models `qwen3-vl:4b`, `qwen2.5vl:3b`, `gemma3:4b`. Newer candidates (`qwen3.5:4b`, `gemma4:e2b`, the 0.9B OCR model `glm-ocr`) need an upgrade, which is the owner's call. Structured output has regressed across Ollama releases, so: validate every reply with Pydantic and retry once; never send `tools` and `format` in the same request; prefer non-thinking models or set `think` explicitly; temperature 0; `OLLAMA_CONTEXT_LENGTH=8192`; record the Ollama version in every experiment. The M4 benchmark chooses among the candidates that run; nothing is chosen by reputation.

**Frontend** (Node 24.11.1 is installed, which satisfies every package below): `react` and `react-dom` 19.3.1, `react-router` 8.5.0, `vite` 8.3.5, `@vitejs/plugin-react` 6.1.2, `vitest` 5.0.5, `@types/react` and `@types/react-dom` 19.3.0, `@fontsource/{archivo,atkinson-hyperlegible-next,atkinson-hyperlegible-mono,noto-sans-devanagari,noto-sans-kannada}` 5.3.0, `@phosphor-icons/react` (pin in M0). `typescript` 7.0.2 is a new major: use it if `vite build` and `vitest` pass in M0, otherwise fall back to the latest 5.x. Commit `package-lock.json`.

---

## 6. Configuration additions (`.env.example`, `core/config.py`)

```
STRIPCHECK_LLM_MODEL=qwen2.5:3b          # replaced by the M4 benchmark winner
STRIPCHECK_VLM_MODEL=                    # empty = second reader off
STRIPCHECK_OLLAMA_URL=http://localhost:11434
STRIPCHECK_PLANNER=hybrid                # hybrid | llm | rules
STRIPCHECK_LLM_TIMEOUT=90
STRIPCHECK_VLM_TIMEOUT=60
STRIPCHECK_TRACING=1
STRIPCHECK_PHOENIX_URL=http://localhost:6006
STRIPCHECK_LANG=en                       # en | hi | kn (verdict templates)
STRIPCHECK_LAN=0                         # 1 = serve on 0.0.0.0 so a phone on the same Wi-Fi can open the app
STRIPCHECK_LAN_TOKEN=                    # optional pairing token required in the URL when LAN is on
STRIPCHECK_SYNC_DELAY=1.5                # seconds between portal requests (never below 1.0)
STRIPCHECK_OFFLINE=0                     # 1 = ingest only from stored snapshots
STRIPCHECK_UPLOAD_RETENTION_DAYS=30
PYTHONUTF8=1
```

New constants (tune on the dev set only):
```
CONFIRM_BATCH_REQUIRED = True   # the C4 gate; ablation arm turns it off
BRAND_MATCH = 0.8               # share of entry brand tokens found on the pack
BRAND_MISMATCH = 0.5            # below this, with a detected pack brand -> mismatch
DATE_ASK_MAX_DIGITS = 1         # date differences of one digit are asked, more is a conflict
STALE_DAYS = 45                 # freshness chip turns amber
SYNC_RECENT_MONTHS = 3
NOISY_ALPHA = 1.0               # Dirichlet smoothing for the confusion model
MAX_VARIANT_LOOKUPS = 2000      # hard cap on variant keys generated per read
```
**`MAX_STEPS` rises from 12 to 16.** Tracing the demo scenarios through the v2 planner showed that the unreadable-pack path (QR, OCR, extract, enhanced re-read, extract, typed batch, exact search, grade, carton photo, its QR, OCR and extract, regrade, draft) needs 14 planner steps, so 12 would force a premature `CANT_VERIFY`. Every planner decision counts as a step, including the decision to draft. Other v1.1 constants (MAX_ASKS 2, MAX_REREADS 1, MAX_REVISIONS 1, MAX_VARIANT_SUBS 2, MAX_CANDIDATES 20, thresholds) are unchanged.

Step and question budgets per demo prop (rules planner, truthful answers, no VLM), which `tests/test_investigator.py` asserts: 01 → 7 steps, 1 ask · 02 → 6, 0 · 03 → 9, 1 · 04 → 7, 1 · 05 → 11, 1 · 06 → 7, 0 · 07 → 6, 0 · 08 → 9, 1 · 09 → 9, 2 (listed date) or 7, 1 (printed date) · 10 → 7, 0 · 11 → 14, 2. (06 and 10 assume the variant search finds no further entries; each extra variant hit adds one grade step.)

---

## 7. Database v2 (`core/db.py`, SQLite WAL, one connection per thread)

```sql
CREATE TABLE IF NOT EXISTS sources(
  id INTEGER PRIMARY KEY, source_type TEXT,          -- portal | pdf | html | csv | xlsx | state
  file_name TEXT, url TEXT, sha256 TEXT UNIQUE, title TEXT,
  list_kind TEXT, list_level TEXT, list_month TEXT,  -- list_level may be 'mixed' for portal months
  strategy TEXT, rows_found INT, rows_valid INT, rows_flagged INT, rows_repaired INT, rows_quarantined INT,
  rows_expected INT, fetched_at TEXT, ingested_at TEXT, superseded_by INT);
CREATE TABLE IF NOT EXISTS alerts(
  id INTEGER PRIMARY KEY, source_id INT REFERENCES sources(id), row_hash TEXT UNIQUE,
  list_kind TEXT, list_level TEXT, list_month TEXT, page INT, row_no INT, bbox TEXT,
  product TEXT, brand TEXT, batch_raw TEXT, batch_key TEXT, mfg TEXT, exp TEXT,
  maker_raw TEXT, maker_name TEXT, marketer TEXT, result TEXT, remarks TEXT, firm_reply TEXT, reported_by TEXT,
  entry_type TEXT, flags TEXT, status TEXT, raw_json TEXT,
  first_seen TEXT, last_seen TEXT, removed_at TEXT, linked_alert_id INT);
CREATE INDEX IF NOT EXISTS idx_alerts_batch ON alerts(batch_key);
CREATE INDEX IF NOT EXISTS idx_alerts_month ON alerts(list_month);
CREATE TABLE IF NOT EXISTS quarantine(id INTEGER PRIMARY KEY, source_id INT, page INT, row_no INT, raw_json TEXT, reasons TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, kind TEXT, thread_id TEXT, started_at TEXT, finished_at TEXT, status TEXT, report_json TEXT);
CREATE TABLE IF NOT EXISTS checks(id INTEGER PRIMARY KEY, thread_id TEXT UNIQUE, mode TEXT, image_paths TEXT, verdict TEXT,
  confidence TEXT, entry_ids TEXT, batch_evidence TEXT, asks INT, steps INT, seconds REAL, planner_mode TEXT, model TEXT,
  lang TEXT, created_at TEXT, final_json TEXT);
CREATE TABLE IF NOT EXISTS cabinet(id INTEGER PRIMARY KEY, label TEXT, product_text TEXT, brand TEXT, batch_key TEXT,
  batch_display TEXT, batch_evidence TEXT, mfg TEXT, exp TEXT, maker TEXT, check_thread_id TEXT, added_at TEXT,
  last_verdict TEXT, last_checked_at TEXT, last_alert_ids TEXT);
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY, cabinet_id INT, alert_id INT, kind TEXT,  -- listed | expiry
  message TEXT, created_at TEXT, seen INT DEFAULT 0, UNIQUE(cabinet_id, alert_id, kind));
CREATE TABLE IF NOT EXISTS confusions(ocr_char TEXT, true_char TEXT, source TEXT, count INT,   -- source: user | calibration
  PRIMARY KEY(ocr_char, true_char, source));
CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, value TEXT);   -- sync state, last sync time, schema version
```
`row_hash` = sha1 of the canonical JSON of the raw row plus `source_type` and `list_month`; it makes ingest idempotent across reruns. The same batch on several lists stays as several rows, and every one is cited (v1.1 §6).

---

## 8. Ingest agent v2 (M1) — `core/ingest.py`, `core/ingest_agent.py`, `core/portal.py`

### 8.1 Graph
`discover → classify → extract → map_validate → (extract_text_chunks → map_validate)? → repair → diff_commit → next_file → … → link_sources → report → END`, checkpointed with `SqliteSaver` (`thread_id = "ingest-<timestamp>"`), resumable with `cli.py ingest --resume <thread>` (v1.1 §7.8, B2). `STRIPCHECK_CRASH_AT=<name>` raises inside `extract` for the resume test.

- `discover`: portal snapshots in `data/raw/portal/**` (new or changed sha256), then PDFs, state and manual files.
- `classify`: portal → kind/level/month from the request and the rows; PDFs/files → v1.1 §7.2 (regex → filename → `SourceMeta` LLM, accepted only if the month appears in the text).
- `extract`: one adapter per type (`portal_json`, `pdf_lines` = v1.1 strategy A, `pdf_text_chunks` = strategy B, `html_table`, `csv`, `xlsx`). Every adapter yields raw rows `{page, row_no, cells/fields, raw_text}`.
- `map_validate`: v1.1 §7.4–7.5 plus the cleaning rules below. Unknown portal keys or headers → `HeaderMap` LLM proposal, accepted only if ≥ 4 of 5 sample rows validate.
- `repair`: v1.1 §7.6 grounded LLM repair, capped per file; else quarantine with a reason.
- `diff_commit`: one transaction per source: upsert by `row_hash`, set `first_seen/last_seen`, mark vanished rows `removed_at`, write quarantine, update `sources`.
- `link_sources`: link PDF rows to portal rows of the same month (`batch_key` equal and `product_coverage ≥ 0.8`) via `linked_alert_id`; emit the cross-source agreement table (field-level agreement rates), which is the automatic PDF-parsing accuracy measure.
- `report`: v1.1 §7.7 ASCII table + dict for the UI, per source: strategy, found, valid, flagged, repaired, quarantined, expected, completeness, top-3 reasons.

### 8.2 Cleaning rules added from the 25 Oct 2026 data analysis
1. **Multi-batch cells**: split `batch_raw` on `,` `;` `&` and the word `and` when every part has ≥ 3 alphanumerics (`PFB-701, OPCP-195` → two rows sharing the other fields, `flags += ["multi_batch_split"]`). Never split on `/` or `-` (they occur inside real batch numbers such as `CBC-0012/25`).
2. Strip trailing punctuation and a leading GS1 application identifier (`(10)CITW-31` → `CITW-31`).
3. `?` between alphanumerics is a dash lost in the latin-1 encoding: display it as `-`. (`batch_key` already drops it.)
4. Batch cells made of words (`Up -to -01`, `NM`, `Not mentioned`) → error `batch_placeholder` (repair or quarantine).
5. Brand: use the brand field unless it is `NA/NIL/-`; otherwise take a trailing bracketed name from the product if it contains letters and is not a dosage phrase (`Levetiracetam Tablets IP (Levipil 500)` → brand `Levipil 500`).
6. Maker placeholders (`NIL`, `NIL,NIL NIL`, `-`) → empty maker, flag `maker_missing` (still an error for non-spurious rows, as in v1.1).
7. Normalise reporting source (`CDSCO lab`/`CDSCO Labs`/`CDL` → central; `State lab`/`State Lab` → state) and lab names (collapse `CDL, Kolkata` and `CDL Kolkata`).
8. Flag `month_mismatch` when `dt_reporting_month_year` differs from the request month; keep the request month.
9. Flag `non_drug` for obvious cosmetics/devices (shampoo, serum, syringe, gauze, cotton) — kept and searchable, reported separately in statistics.

### 8.3 Portal fetch (`core/portal.py`)
Section 3.3 rules. `cli.py sync` = fetch (unless `--offline`) + supervisor (ingest → re-check cabinet → notify). Unit tests use recorded fixtures in `tests/fixtures/portal/` (a few real rows, latin-1 bytes), never the network.

---

## 9. Perception v2 (M2) — `core/pack_tools.py`, `core/crops.py`, `core/vlm.py`

- `decode_qr(path)`: `zxingcpp.read_barcodes` (QR, DataMatrix, GS1) on the image, then on a 2× grayscale upscale; OpenCV `QRCodeDetector` as a fallback. Returns `{found, raw, format, fields: parse_qr_payload(raw)}`.
- `ocr_read(path, enhanced=False)`: module-level RapidOCR engine (PP-OCRv5 English/Latin recognition if the installed RapidOCR ships it; otherwise its default). Lines in reading order with `box`, `score`, and word boxes when the API provides them.
- `enhance(bgr)`: v1.1 B5, unchanged. It helps blur and glare; it does not fix confident misreads (v1.1 §2).
- `extract_fields(ocr_lines, qr_fields, mode)`: v1.1 §8.4 plus the A1 amendments (§A), plus `brand` (largest-font line without a label, from box heights) and `strength`. Every field carries provenance: `{value, source: qr|ocr|ocr_enh|vlm|user|carton, image, line, score}`.
- `crops.py`:
  - `batch_line_crop(image, line_box)` → PNG.
  - `char_boxes(line_box, line_text, batch_span, word_boxes=None)`: use word/character boxes if RapidOCR returns them; otherwise split the batch token's horizontal extent in proportion to character advance widths (monospace assumption), then snap each boundary to the nearest column-projection minimum within ±30% of a character width.
  - `glyph_crops(...)` → one PNG per character with 25% padding. Crops are saved under `data/uploads/<thread_id>/crops/` and served by id, never by path.
- `vlm.py` (optional second reader): `read_pack_vlm(path)` sends the image (long side ≤ 1024 px) to `STRIPCHECK_VLM_MODEL` with the `PackFieldsVLM` schema (§E), temperature 0, timeout `STRIPCHECK_VLM_TIMEOUT`; returns `None` on any failure. Its values are *reads*, never facts: they can create agreement (`dual_read`) or an alternate key to search, and never alone justify an alarm.

---

## 10. Investigator and verifier v2 (M3, M4)

### 10.1 State additions (to v1.1 §9.1)
```python
    mode: str                 # photo | text
    reads: list               # [{"source": "qr|ocr|ocr_enh|vlm|carton|user", "batch": str, "key": str,
                              #   "image": int, "line": int|None, "score": float|None}]
    batch_evidence: str       # qr | dual_read | user_typed | user_confirmed | ocr | vlm | carton | none
    vlm_tried: list           # image indexes the VLM has read
    conflicts: list           # [{"entry_id", "field": "mfg|exp", "pack": "YYYY-MM", "entry": "YYYY-MM", "digits": int}]
    crops: dict               # {"batch_line": crop_id, "chars": [crop_id, ...]} for the current batch read
    lang: str                 # en | hi | kn
```

### 10.2 Actions (v1.1 §9.2, plus)
| Action | Allowed when | Does |
|---|---|---|
| `read_vlm` | VLM configured, latest image not read by it | `read_pack_vlm`; adds a `reads` entry; if its key equals an OCR/QR key → `batch_evidence = dual_read` |
| `ask_user` (new kinds) | see §10.4 | `confirm_batch`, `confirm_field` |

`search_exact` / `search_variants` run for **every distinct read key** (OCR and VLM can disagree); candidates are de-duplicated by alert id, keeping the strongest `how`.

### 10.3 Rule planner v2 (`rule_next`, deterministic priority list)
1. `mode == "text"` skips perception: fields come from the request, `batch_evidence = user_typed`.
2. QR not tried on the latest image → `read_qr`.
3. Latest image not OCR'd → `read_text`.
4. New evidence not extracted → `extract_fields`.
5. Batch missing and `rereads < MAX_REREADS` → `reread_enhanced`.
6. Batch missing, VLM configured and not tried on this image → `read_vlm`.
7. Batch missing and a `type_batch` ask is allowed → `ask_user(type_batch)`.
8. Batch missing → `search_by_product` if not searched; else `box_photo` ask if product hits exist and an ask is allowed; else `draft_verdict` (`CANT_VERIFY`, reason names how many entries list this product). (v1.1 step 6.)
9. Batch read only by OCR, VLM configured and not tried on this image → `read_vlm`.
10. "exact" not searched for every read key → `search_exact`.
11. Ungraded candidates → `grade`.
12. Nothing accepted and "variants" not searched → `search_variants`.
13. Ungraded candidates → `grade`.
14. A pending candidate and an ask allowed → ask by status: `needs_confirm_char` → `confirm_char`; `needs_confirm_field` → `confirm_field`; `needs_more_evidence` → `box_photo`; `adjudicate` (rules mode) → `box_photo`.
15. An accepted candidate, `CONFIRM_BATCH_REQUIRED`, `batch_evidence` not in {`qr`, `dual_read`, `user_typed`, `user_confirmed`}, an ask allowed and `confirm_batch` not declined → `ask_user(confirm_batch)`.
16. Otherwise → `draft_verdict`.

Hybrid branch points (v1.1 §9.3 a–d) are unchanged, plus (e) after `read_vlm` when the VLM and OCR keys disagree. The LLM may only pick from `allowed`; anything else falls back to `rule_next` with `source="rules(fallback)"`.

### 10.4 Human-in-the-loop v2 (v1.1 §9.6, plus)
Payloads are built deterministically, carry crop ids, and nothing has side effects before `interrupt()` returns.

| kind | question (template) | options | resume | effect |
|---|---|---|---|---|
| `confirm_char` | v1.1 wording; adds "OCR has misread {o} as {t} {n} times before." when the learned prior applies | listed char(s), read char(s), "Can't tell" | `{"choice": ...}` | listed → candidate `how="confirmed"`, `fields.batch` = listed batch, `batch_evidence="user_confirmed"`, `confusions(user)` += 1 per substitution; read → reject candidate ("you confirmed the printed character"); can't tell → unresolved |
| `confirm_batch` | "Before we show this result, look at the batch on your strip. Type its {k}th and {m}th characters." + batch-line crop. The positions are the two the confusion model rates most likely to be misread (for a key with no confusable character: the last two). A bare "Yes" button is not offered, because people habituate to yes/no confirmations and tap without looking (theme T15). | two one-character inputs, "Type the whole batch instead", "Can't tell" | `{"chars": {"4": "2", "7": "B"}}` / `{"typed": "..."}` / `{"choice": "cant_tell"}` | chars equal the read → `user_confirmed`; chars differ → the corrected key replaces the read (the read is rejected as below), searches cleared, regrade; typed → behaves like `type_batch`; can't tell → `declined += ["confirm_batch"]`. The usability study measures whether this catches planted misreads better than a yes/no button. |
| `confirm_field` | "Your strip's {expiry/manufacturing} date reads {pack}; CDSCO lists {entry}. Which is printed?" + crop of the date line | pack value, listed value, "Can't tell" | `{"choice": ...}` | listed → field updated (`source="user"`), regrade; pack → conflict stands (`date_conflict`); can't tell → conflict stands |
| `box_photo`, `type_batch` | v1.1 | v1.1 | v1.1 | v1.1; a carton read whose batch key equals the strip's key sets `batch_evidence = dual_read` |

Every answer increments `asks` (MAX_ASKS = 2). Worked budgets: misread prop = 1 ask (confirm_char also confirms the batch); clean OCR flag = 1 ask (confirm_batch), 0 with VLM agreement or QR; marketer-only = box_photo (1) + confirm_batch only if the carton's batch read differs (2).

Answer-handling rules found by tracing the scenarios:
- **"No, let me fix it" rejects the read.** When `confirm_batch` returns a typed batch `T` that differs from the read key `R`, every candidate whose key equals `R` is rejected with the reason "you said the strip does not read {R}". Without this, the sibling trap would re-find `R` as a variant of `T` and ask a redundant character question.
- **Reader disagreement becomes a character question.** If the OCR and VLM keys differ and a candidate matches one of them, the agent asks `confirm_char` for the differing positions (options: the candidate's characters, the other reader's characters, "Can't tell").
- **Fields have a version.** Any change to the fields (a new image, an answer, a typed batch) increments `fields_version`; a candidate counts as graded only for the version it was graded against, so new evidence always triggers a regrade.
- **The drafter applies the batch gate itself.** If the top accepted candidate lacks gate-passing batch evidence and `confirm_batch` can no longer be asked (budget spent or declined), `draft_verdict` writes the "possible match" `CANT_VERIFY` directly (§10.7). The verifier's R2 stays as a safety net, so the normal path never needs a send-back for this.

### 10.5 Grading v2 (`matching.grade`, amended in §A2)
Field evidence: `batch` (exact | variant | confirmed), `product` (match | partial | mismatch | unknown), **`brand`** (match | mismatch | unknown | n/a), `dates` (match | mismatch | unknown), `maker` (match | mismatch | unknown | n/a).
- `brand`: n/a if the entry has no brand. Coverage of the entry's brand tokens on the pack text ≥ `BRAND_MATCH` → match. Mismatch only when the pack has a **detected brand** (field `brand`) and coverage < `BRAND_MISMATCH`; otherwise unknown.
- Status order:
  1. `product`, `maker` or `brand` mismatch → `reject` (collision; never flag).
  2. `dates` mismatch with everything else not mismatching → if every differing date differs in ≤ `DATE_ASK_MAX_DIGITS` digit → `needs_confirm_field`; else `date_conflict`.
  3. Then the v1.1 order (adjudicate → needs_confirm_char → needs_more_evidence → spurious rules → accept rules).
- `decide()` adds: `date_conflict` (and nothing accepted or pending) → `CANT_VERIFY` with the reason "CDSCO lists batch {b} of this product from the same maker with different dates ({entry}) than your pack ({pack})"; `needs_confirm_field` counts as pending (`ASK`).
- All 7 v1.1 scenarios keep their expected outcomes (A3 test unchanged and still required).

### 10.6 Noisy-channel variant ranking (`core/noisy.py`)
- Channel model `P(read = r | true = t)` per character from counts `n[r,t]` (sum of `calibration` and `user` sources) with Dirichlet smoothing α = `NOISY_ALPHA` over the candidate set `CONFUSABLE[r] ∪ {r}`. The structural `CONFUSABLE` table bounds the search; counts only reorder.
- Score of a variant = Σ log P(r_i | t_i) over substituted positions + Σ log P(t_j | t_j) over the rest. Order: fewer substitutions first, then higher score, then alert id (deterministic).
- `calibration` counts come from `cli.py props --calibrate`: render random batch keys with the damage/glare/blur generators, OCR them, align (equal length → position-wise; else Levenshtein alignment), and count substitutions. The resulting confusion matrix is a paper figure.
- The trace logs the prior used ("prior: 3→B seen 2× (user), 11× (calibration)"). The prior never skips the question and `how="auto_corrected"` is never set (v1.1 §10 stands).

### 10.7 Verifier v2 (hard rules; v1.1 §9.7 amended)
- **R1** label is one of the four.
- **R2** `FLAGGED`/`SUSPECTED_FAKE` need: a cited entry with status `accept`; batch evidence `exact` or `confirmed` on that entry **and** `batch_evidence` in {`qr`, `dual_read`, `user_typed`, `user_confirmed`} when `CONFIRM_BATCH_REQUIRED`; product `match` or LLM-adjudicated "yes"; brand not `mismatch`; no mismatch or unresolved conflict anywhere.
- **R3** entry type consistent with the label (v1.1).
- **R4** `NOT_LISTED` needs a grounded batch, exact **and** variants searched for every read key, no pending, accepted or conflicted candidate.
- **R5** flags carry the citation line; no banned phrase in any text (v1.1 list, applied to every language's LLM text).
- **R6** counters within bounds.
- **R7** an unresolved `date_conflict` forbids both flags and `NOT_LISTED` → `CANT_VERIFY` with the conflict as the reason.
- **R8** every field used in grading has provenance; no field may come only from an LLM extraction that failed grounding.
- **R9** `NOT_LISTED` text states the lists loaded and the latest month (data freshness).
- **R10** the template exists for `lang`; otherwise English, with the UI's language toggle still offering the translation.

On violation: send back once with a critique naming the rule and the action that fixes it; otherwise downgrade to `CANT_VERIFY` with `reason = "verifier: <rule>"`. A downgrade caused only by R2's batch gate uses the honest wording "Possible match: if your batch reads {b}, it is on CDSCO's {month} list. We could not confirm the batch, so ask your pharmacist to check it."

### 10.8 Text mode and bill scan
- **Text mode** (`mode="text"`): the request gives `batch` (+ optional product, brand, dates, maker). Same graph from step 10; asks limited to `confirm_field`.
- **Bill scan** (M9): OCR the invoice → `BillItems` LLM extraction (§E) of `{product, batch, exp}` rows with the grounding guard → one confirmation screen listing all read batches with edit-in-place (one ask) → each row runs in text mode as a sub-check (`thread_id = <bill>-<n>`) → a results table. Bound: 12 items per bill.

### 10.9 Templates and safety (`core/templates.py`)
- v1.1 §9.8 templates verbatim for English; Hindi and the regional language are hand-written translations reviewed by a native speaker on the team (the translator signs off in `docs/decisions.md`).
- `SUSPECTED_FAKE` has two wordings, because the portal data show two kinds of spurious entry: (a) the maker is "Under Investigation" or `str_firm_reply` says the labelled maker did not make the batch → v1.1 wording with "(the manufacturer named on the label says it did not make this batch)"; (b) the NSQ result says "hence spurious" with a named maker (e.g. Sep 2026, Buprenorphine Injection, batch BUP324004) → "(the testing laboratory declared the sample spurious)". Never use wording (a) without the firm-reply or under-investigation evidence. The LLM never writes user-facing verdict text; it may add one English rationale line in developer views only, filtered by the banned-phrase regex.
- Banned phrases (v1.1) apply in every language; add Hindi equivalents of "safe", "genuine" and "stop taking" (e.g. सुरक्षित, असली, बंद करें) to the filter for LLM text.
- Untrusted text: OCR/VLM output and alert text are data. They go into LLM prompts only inside JSON fields; prompts say so; the LLM cannot trigger actions outside `allowed`, and no LLM output reaches the user unfiltered. This is the agent's prompt-injection defence and is discussed in the paper.

---

## 11. Supervisor, memory and feedback (M8; v1.1 §10 amended)

- `supervisor.py` graph: `route → sync_or_ingest → recheck_cabinet → notify → report`.
- **Sync schedule**: on demand (button / `cli.py sync`); optionally a background poll once a day from the 15th to the 30th of each month (CDSCO lists have appeared on the 19th–24th of the next month).
- **Re-check**: for each cabinet item, text-mode search + grade on the stored fields (no asks). An `accept` creates a `listed` notification; wording depends on the stored `batch_evidence` ("A batch matching the one you saved (SP240165) appears on CDSCO's Sep 2026 list").
- **Expiry reminders**: an `expiry` notification 30 days before the stored expiry month.
- **Feedback loop**: confirmed substitutions update `confusions(user)`; the next check's variant ranking and question wording show the prior (§10.6). This is the visible learning loop.

---

## 12. Observability (v1.1 §11, plus)

JSONL step lines add `model`, `tokens_in`, `tokens_out` (Ollama `prompt_eval_count`/`eval_count`), `fallback` (bool) and `crop_ids`. `GET /api/traces/{thread_id}` serves the JSONL; the UI's Traces screen renders it when Phoenix is off. Tracing failures never raise.

---

## 13. API (FastAPI, `server/`) and streaming

Bind `127.0.0.1:8000` by default; `--lan` binds `0.0.0.0` and, if `STRIPCHECK_LAN_TOKEN` is set, requires `?k=<token>` once (then a cookie). Same-origin only (no CORS). Uploads: ≤ 2 images per request, ≤ 15 MB each, decoded with Pillow before saving (rejects non-images), saved under generated names. Crops and files are served by id, never by path.

```
GET  /api/health                         ollama {up, models, llm_ok, vlm_ok}, phoenix {up}, db {alerts, sources, months, latest_month, last_sync}, lan_url
POST /api/checks                         multipart images[] + planner + lang, or JSON {mode:"text", batch, product?, brand?, mfg?, exp?, maker?}
                                         -> text/event-stream until an interrupt or the final verdict
POST /api/checks/{tid}/resume            JSON {choice} | {typed} | {skip:true}, or multipart image (box_photo) -> text/event-stream
GET  /api/checks/{tid}                   snapshot {status: running|waiting|done, pending, fields, strip, history, final}
GET  /api/checks?limit=50                recent checks
GET  /api/crops/{crop_id}.png
GET  /api/alerts?q=&batch=&month=&kind=&level=&page=&size=   batch search is confusion-aware (labels "1 character differs")
GET  /api/alerts/{id}                    row + source + provenance;  GET /api/alerts/{id}/source.png (PDF rows)
GET  /api/sources   GET /api/quarantine   GET /api/stats
POST /api/sync                           -> text/event-stream of supervisor progress; 409 if a sync is running
GET  /api/cabinet   POST /api/cabinet {thread_id}   DELETE /api/cabinet/{id}   POST /api/cabinet/recheck
GET  /api/notifications                  POST /api/notifications/{id}/seen
GET  /api/eval/latest                    POST /api/eval/quick -> text/event-stream
GET  /api/traces/{tid}
GET  /api/lan    GET /api/lan/qr.png
```

**SSE bridge (`server/sse.py`).** The compiled graph runs in a worker thread (`run_in_threadpool`) with `stream_mode=["updates", "custom"]`; nodes publish UI-relevant state with `get_stream_writer()` (`fields`, `strip`, `candidates`). The bridge converts chunks to SSE events (Appendix D) through a thread-safe queue, sends a heartbeat comment every 15 s, and ends with `final` or `interrupt` followed by `done`. Streams use `POST` + `fetch` readers (EventSource cannot send bodies). If the browser disconnects, the graph still runs to its next interrupt or end; state lives in the checkpointer, so reloading the page and calling `GET /api/checks/{tid}` restores the question or the verdict. One run per `thread_id` at a time (a lock map); one sync at a time.

---

## 14. UI build notes (M6)

Design: `docs/design/ui_direction.md` (authoritative) and the clickable prototype `docs/design/prototype/index.html` (Check screen in all five states with real Sep 2026 data; open with `preview_start design-prototype` or any static server; `?state=flagged|fake|notlisted|cantverify&theme=light|dark`). The React components must match the prototype's tokens, strip, timeline, ask card and verdict slip. Lessons already learned from it: never use `display: revert` to toggle states (it resets author layout); give SVG `<use>` of a symbol explicit `width`/`height`; text on `--pen` uses `--on-pen`; grid tracks that hold long mono strings need `minmax(0, 1fr)`. Build notes:
- `web/src/lib/api.ts`: typed client + SSE parser (`fetch` + `ReadableStream`, handles partial chunks and heartbeats); unit-tested with Vitest.
- `web/src/components/`: `BatchStrip`, `StepTimeline`, `AskCard`, `VerdictSlip`, `EvidenceChips`, `FreshnessChip`, `PhonePair`, `DataTable`.
- Routes: `/` Check · `/lists` · `/cabinet` · `/eval` · `/traces/:tid?`.
- Tokens live in `web/src/styles/tokens.css`; a Vitest test checks WCAG contrast for every text/background token pair in both themes.
- `vite build` output goes to `web/dist`, served by FastAPI at `/`. `cli.py serve` prints the build command if `web/dist` is missing.
- M6 is "done" only after a scripted run through the built-in browser: each demo prop, every ask kind, phone-width layout, keyboard-only path.

---

## 15. Props, datasets and evaluation v2 (M2, M7)

### 15.1 Rendering (`core/props.py`, `core/degrade.py`)
`render_pack` (v1.1 §12.1) gains: a `brand` line; `foil=True` (silver gradient with a specular band, for strip-like props); `emboss=True` (raised-text shading on the batch line); `strokes={"index": i, "add": "left_bar"}`, the inverse of `damage`, which turns `3` into something OCR reads as `B` (used for sibling traps). `degrade.py` applies one corruption at a time with severity 0–3: Gaussian blur, motion blur, JPEG quality, rotation, perspective, glare, low light (gamma), sensor noise.

### 15.2 Calibration
- `calibrate_misread` (v1.1 §12.2) unchanged.
- `calibrate_sibling(entry)`: pick a listed key `K` with a position where a one-substitution variant `K'` is **not** in the index; render a genuine pack printed with `K'`, then add strokes until OCR reads exactly `K`. Accept the first seed that works; otherwise log and skip.
- `props --calibrate`: the confusion-matrix calibration of §10.6 (≥ 2,000 rendered keys), stored as `confusions(source="calibration")`, plotted for the paper.

### 15.3 Demo set (`props --demo`, from real DB rows)
| File | Built from | Expected |
|---|---|---|
| 01_flagged_clean | NSQ row with dates, maker, key length ≥ 5 | FLAGGED after one `confirm_batch` (no ask with QR or VLM agreement) |
| 02_flagged_qr | same row + GS1 QR | FLAGGED, no ask |
| 03_misread | calibrated one-character misread | FLAGGED after one `confirm_char` |
| 04_suspected_fake | spurious row (prefer one with dates) | SUSPECTED_FAKE after `confirm_batch` |
| 05_marketer_only | NSQ row, marketer only | `box_photo` (use 01) → FLAGGED; skip → CANT_VERIFY |
| 06_trap_collision | batch of row A + product/maker/dates of row B (coverage < 0.5, maker differs) | NOT_LISTED (a lookup script false-alarms) |
| 07_genuine | invented key not in the index nor one substitution away | NOT_LISTED |
| 08_sibling_trap | `calibrate_sibling` | `confirm_batch` → "No" + typed true key → NOT_LISTED; with the gate off → FLAGGED (false alarm) |
| 09_date_conflict | listed row printed with one expiry digit changed | `confirm_field`: listed value → FLAGGED; printed value → CANT_VERIFY |
| 10_brand_trap | listed batch + same generic + a different brand and maker | NOT_LISTED |
| 11_unreadable | 01 with severity-3 blur | `type_batch`; typed → proceeds; skipped → CANT_VERIFY |

### 15.4 Golden set v2 (`props --eval --n 200 --seed 7`; dev seed 1)
Mix: flagged 30% (clean, qr, glare, misread-1, misread-2), suspected fake 10%, traps 15% (product, brand), sibling traps 10%, date conflicts 5%, genuine 25%, unreadable 5%. Ladder set (`props --ladder`): 30 base packs (half listed, half genuine) × 8 corruptions × severities 0–3.

### 15.5 Real-world sets (team tasks, with manifests)
- **Print-and-capture**: print 20 props, photograph each with 2 phones under 2 lights → 80 images.
- **Real strips**: ≥ 30 photos of the team's own medicines. Truth = manual lookup of the typed batch; expected NOT_LISTED unless actually listed (a real hit is a case study).

### 15.6 Dataset statistics for the paper (`core/analysis.py`, `cli.py stats`)
Totals by year/month/level/kind; batch-key length distribution; exact collisions across unrelated products; confusable-neighbour density (overall and same maker); alert lag (reporting month − manufacturing month) and remaining shelf life at alert; failure categories; data-quality flags; completeness per source; PDF↔portal agreement. Outputs `paper/generated/stats.tex` (LaTeX macros such as `\NumAlerts`) and `paper/figures/*.pdf`. Never hand-copy numbers into the paper.

### 15.7 Arms, ablations, HITL
Arms: `baseline` (v1.1 lookup script), `agent_rules`, `agent_hybrid@<model>` for each LLM candidate, `agent_llm@<best>`. Ablations of `agent_rules`: `-variants`, `-corroboration` (accept on batch match alone), `-verifier`, `-confirm_gate`, `+vlm`. HITL policies: `oracle` (v1.1 §13, extended: `confirm_batch` answers "yes" if the read is the truth, else types the truth; `confirm_field` picks the printed truth) and `none`.

### 15.8 Metrics (v1.1 §13, plus)
Sibling-trap and brand-trap false-alarm rates; date-conflict handling accuracy; asks per pack by scenario; risk–coverage curve (error among answered checks vs share answered); per-node latency; LLM schema-validity and fallback rates; VLM agreement rate and double-misread rate (both readers wrong in the same way).

Added after the literature survey (`reports/StripCheck literature survey.md` §7 and §9):
- **Predictive value at realistic base rates.** Test sets are about 30% listed by design, but almost every strip a person photographs is unlisted. Report the positive predictive value of FLAGGED and the false-reassurance rate of NOT_LISTED at assumed prevalences of 1% and 0.1%, computed from the measured hit recall and false-alarm rates with their intervals. A small false-alarm rate can otherwise produce more false than true alarms.
- **OCR confidence calibration on batch codes.** A reliability diagram and expected calibration error for RapidOCR line scores on batch-code crops (no published calibration study covers short identifiers).
- **Blocking recall.** Pair completeness of the variant search (share of misread packs whose true entry is among the candidates), reported separately from verdict accuracy.
- **Durable measurements as contributions.** The annotated strip images (synthetic, captured and real tiers), the batch-code confusion table, the calibration curve, the collision rate and the manufacture-to-listing lag are released as results in their own right; tool-level novelty is perishable.

### 15.9 Statistics
Wilson 95% intervals for every rate; exact McNemar test for paired comparisons on identical items; bootstrap (10,000 resamples) for median latency; Holm correction across the ablation family; effect sizes reported alongside p-values.

### 15.10 Preregistered decision rules (frozen in `docs/decisions.md` before the seed-7 run)
- **R-A** (v1.1): adopt the agent if its trap false-alarm rate is ≥ 50% (relative) lower than the baseline's and its hit recall is ≤ 5 points lower.
- **R-B**: keep the confirm gate if the sibling-trap false-alarm rate drops ≥ 50% (relative) vs `-confirm_gate`, with oracle hit recall within 2 points.
- **R-C**: default to the hybrid planner only if accuracy is not significantly lower than rules (McNemar, α = 0.05) and median latency is ≤ 2× rules.
Report whatever happens.

### 15.11 LLM benchmark (`cli.py bench`)
Per model: JSON-schema validity; p50/p95 latency; agreement with `rule_next` on 100 recorded branch-point states; product-adjudication accuracy on 200 labelled pairs generated from the DB (positives: an entry's product vs pack-style rewrites of it; negatives: real collision groups and same-generic/different-brand pairs); field-extraction accuracy on 50 OCR line sets from props. The winner becomes `STRIPCHECK_LLM_MODEL`, recorded in `docs/decisions.md`.

### 15.12 Ingest evaluation
Parsing hand-check (`parsecheck`, 50 PDF rows); automatic PDF↔portal agreement for every overlapping month (field-level); completeness per source; quarantine reasons.

### 15.13 Usability study (optional, M10)
8–12 participants; tasks: check a flagged prop, answer a character question, save to cabinet, read a NOT_LISTED result and explain what it means. Measures: task success, time, SUS, and a comprehension question on NOT_LISTED ("does this mean the medicine is safe?"). Consent form; no personal data stored.

---

## 16. CLI v2 (`cli.py`, argparse)

```
python cli.py doctor [--warm]                         # Python, packages, Ollama + models, GPU, Phoenix, DB, web build, paper toolchain
python cli.py sync [--offline] [--full]               # portal snapshots -> supervisor (ingest -> re-check -> notify)
python cli.py fetch --pdfs | --state mh               # secondary sources
python cli.py ingest [--no-llm] [--resume THREAD_ID]
python cli.py stats                                   # paper/generated/stats.tex + figures
python cli.py props --demo | --eval --n 200 --seed 7 | --ladder | --calibrate
python cli.py check IMAGE [IMAGE] [--planner rules|hybrid|llm] [--vlm] [--lang hi]
python cli.py check --text BATCH [--product P] [--brand B] [--mfg M] [--exp E] [--maker K]
python cli.py serve [--lan] [--port 8000]
python cli.py recheck
python cli.py eval --arms baseline,agent_rules[,...] --hitl oracle|none [--set golden|ladder|captured|real] [--limit N]
python cli.py bench --models m1,m2,...
python cli.py parsecheck --sample 50 | --score runs/parse_sample.csv
python cli.py selftest                                # offline end-to-end: fixtures -> props -> every demo prop through the API -> expected verdicts
python cli.py mcp                                     # optional read-only MCP server (stdio)
```

---

## 17. Milestones v2 (build order for the coding phase)

Every milestone ends with: tests green (`pytest -q`, and `npm test` from M6), `cli.py selftest` green from M3, a git commit, a `docs/research_log.md` entry, and its paper hook done. Nothing is "done" on a claim; it is done when the command in the table passes.

| # | Milestone | Done when | Paper hook |
|---|---|---|---|
| **M0** | git init (+ `.gitignore`: `data/`, `runs/`, `*.db`, `node_modules/`, `web/dist/`, `.env`), conda env, pins from the tech scan, `config.py`, `db.py` v2, `pytest.ini` (`llm`, `net` markers, both skipped by default), `cli.py doctor`, web scaffold with tokens and fonts, FastAPI skeleton (`/api/health`, static files), paper build | `doctor` all checks print; `pytest -q` passes; `npm run build` passes; `serve` shows the app shell; `latexmk` builds `paper/main.pdf` | implementation-stack table |
| **M1** | Data: `portal.py`, adapters, cleaning rules, validators, repair, quarantine, diff/upsert, ingest graph with checkpoint/resume, PDF path, cross-source linking, `analysis.py` + `stats` | sync from stored snapshots loads every month; a second run adds 0 rows; crash-and-resume test passes; PDF months ingest; agreement table printed; `stats` writes macros and figures | §III Data |
| **M2** | Perception + props: `pack_tools` v2, `crops.py`, `vlm.py`, `props.py`/`degrade.py`, calibration | 11 demo props + manifest; OCR finds the batch on clean props; misread and sibling props calibrated (or fallback logged); crops render; confusion matrix saved | perception + confusion-matrix figure |
| **M3** | Reasoning in rules mode: `matching.py` v2 (§A), `noisy.py`, `alert_tools.py`, `investigator.py`, `verifier.py`, `templates.py`, text mode, `cli.py check` with terminal prompts | all 11 demo props give the expected verdicts with scripted answers; unit, graph and verifier tests pass; `selftest` passes | method: planner, grading, HITL, verifier |
| **M4** | LLM layer: `llm.py`, hybrid/llm planner, field extraction, adjudication, critique, ingest LLM paths, `bench` | hybrid gives the same verdicts on the demo props; with Ollama stopped it logs `rules(fallback)` and still finishes; benchmark table produced; default model chosen | model benchmark |
| **M5** | Observability | `check data/props/03_misread.jpg` with Phoenix running shows a nested trace; JSONL timeline served by the API | observability |
| **M6** | API + UI (§13, §14, `ui_direction.md`) | every demo prop runs from the UI, including every ask kind; phone over LAN verified; contrast test passes; scripted browser run passes | UI + screenshots |
| — | **Review 2 cut line: M0–M6 is the demo** | | |
| **M7** | Evaluation (§15) + Evaluation screen | eval tables and figures for every arm, ablation and set; preregistered rules evaluated and reported | results |
| **M8** | Supervisor, cabinet, notifications, expiry reminders, learning loop | a new month in the fixtures notifies a saved batch; a confirmed `3→B` appears as a prior in the next trace | memory + case study |
| **M9** | Extras: bill scan, Hindi + regional templates, read aloud, MCP server, Maharashtra source | each has a test and a demo path | extensions |
| **M10** | Paper and release: README (setup, run, results, citations, deviations), screenshots, demo runbook, fresh-clone test | `paper/main.pdf` complete; fresh clone → `doctor` → `selftest` passes | final paper |

**How the coding phase runs each milestone (ultracode):** (1) a planning agent turns the milestone's spec sections and the current code into `docs/milestones/M<k>_plan.md` (tasks, files, tests); (2) implementation agents work on disjoint modules in parallel (worktrees only when files overlap), saving and committing per module; (3) a verification stage runs the tests and adversarial reviewers (correctness, safety language, spec compliance, Windows/encoding, performance) whose confirmed findings are fixed in a loop until green; (4) a documentation stage updates the paper, the research log and the README, then commits.

---

## 18. Demo runbook v2 (Review 2)

Pre-flight (30 min before): `conda activate stripcheck`; `python cli.py doctor --warm`; `python cli.py sync --offline` (data already synced earlier); optional `phoenix serve`; `python cli.py serve --lan`; open the app on the laptop and on a phone (QR in the header); run every demo prop once; plug in the charger, disable sleep.

Script (about 5 minutes):
1. **Real data (40 s).** Alert lists: every CDSCO list from Jan 2019 to Sep 2026, the counts, quarantine with reasons, "CDSCO moved its lists to a portal in Aug 2025; our ingest agent reads it directly and validates any new layout before trusting it."
2. **01 flagged (40 s).** The confirm-batch tap, the verdict slip, the citation and source.
3. **03 misread (60 s).** OCR reads `B3T…` at confidence ~1.0; exact search empty; the agent suspects a misread; the strip flicks through alternatives; one question with the real glyph crop; FLAGGED; the trace.
4. **08 sibling trap (40 s).** "Real lists contain sibling batches one character apart, like R21119 and R21719. A confident misread can land exactly on a listed sibling. Our agent never raises an alarm on an unconfirmed read."
5. **06 trap collision (20 s)** and **04 suspected fake (20 s)**.
6. **Phone (40 s).** Scan a real strip from someone in the room: NOT_LISTED, with the freshness line and "this does not certify the medicine".
7. **Resilience (20 s).** Stop Ollama: the planner falls back to rules and still answers.

Fallbacks: UI breaks → `python cli.py check data\props\03_misread.jpg`; Phoenix down → the Traces screen; LLM slow → rules mode; DB problem → `python cli.py sync --offline`.

---

## 19. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The portal endpoint changes or blocks scripts | stored snapshots + `--offline`; PDF fallback for 2024-25; schema-drift mapping via `HeaderMap`; polite request rate |
| OCR is weak on real foil strips | enhanced re-read, carton photo ask, typed batch, optional VLM reader; report real-photo results honestly |
| Small-LLM structured output fails | JSON schema + validation + rules fallback; the benchmark picks the model |
| GPU memory contention (OCR + LLM + VLM) | OCR on CPU; LLM and VLM on GPU, called sequentially; `keep_alive` tuned |
| Usage limits during the build | incremental saving, resumable workflows, commits per module |
| CDSCO copyright | local index only, citation on every verdict, derived statistics only in the paper, not an official service |
| Over-trust by users | no green, no "safe", explicit freshness and limits, pharmacist referral, abstention |
| Schedule | Review 2 cut line at M6; M7+ only after the demo works |

---

## 20. Paper plan (`paper/`)

IEEE conference format (`IEEEtran`). Sections and the milestone that fills each: I Introduction (now) · II Related work (literature survey, now) · III Data: CDSCO alerts (M1) · IV System design (now as design, finalised M3–M6) · V Evaluation methodology (now, frozen before M7) · VI Results (M7–M8) · VII Discussion: limitations, ethics, safety, threats to validity (M7–M10) · VIII Conclusion. Numbers come from `paper/generated/*.tex`; figures from scripts in `core/analysis.py` and `core/evaluate.py`; references only from verified `.bib` files in `research_notes/` merged into `paper/references.bib`.

---

## Appendix A — Amendments to v1.1 verified code (each with its test)

### A1 `core/textutils.py`
1. **`BATCH_RE`**: stop matching inside words (v1.1 read "Lotion" as label "Lot" + batch "ion", and "Batchwise" similarly):
```python
BATCH_RE = re.compile(r"(?:\bB\.?\s?No\b\.?|\bBatch(?=\W|No|Number|$)(?:\s*No\.?|\s*Number)?|\bLot(?=\W|No|$)(?:\s*No\.?)?|\bBN\b|\bB\.N\.)\s*[:.\-]?\s*([A-Z0-9][A-Z0-9\-/]{2,19})", re.I)
```
2. **Label and value on separate OCR lines**:
```python
LABEL_ONLY_RE = re.compile(r"^\s*(?:B\.?\s?No\b\.?|Batch(?:\s*No\.?|\s*Number)?|Lot(?:\s*No\.?)?|BN|B\.N\.)\s*[:.\-]?\s*$", re.I)
NEXT_TOKEN_RE = re.compile(r"^\s*(?=[A-Z0-9\-/]*\d)([A-Z0-9][A-Z0-9\-/]{2,19})\b", re.I)   # must contain a digit
def find_batch(lines):
    for i, ln in enumerate(lines):
        m = BATCH_RE.search(ln)
        if m: return m.group(1).rstrip("-/"), i
        if LABEL_ONLY_RE.match(ln) and i + 1 < len(lines):
            m2 = NEXT_TOKEN_RE.match(lines[i + 1])
            if m2: return m2.group(1).rstrip("-/"), i + 1
    return None, None
```
3. **`parse_month_year`**: also replace the em dash, and read `DD/MM/YY` (v1.1 turned `01/07/24` into `2007-01`). Insert after the `DD/MM/YYYY` rule:
```python
    m = re.search(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2})\b", t)          # DD/MM/YY
    if m and 1 <= int(m.group(1)) <= 31 and 1 <= int(m.group(2)) <= 12: return f"20{m.group(3)}-{int(m.group(2)):02d}"
```
4. **`STOP`**: add `extended modified controlled delayed immediate sustained` (release descriptors that packs abbreviate).

### A2 `core/matching.py`
1. `search_variants(index, key, prior=None, max_subs=2, max_lookups=2000)`: cap generated keys at `max_lookups`; rank by `(len(subs), -noisy.score(subs, prior), id)` where `noisy.score` = Σ over substitutions of `log((n[o,t] + α) / (n[o,o] + α))` (the log-odds that the read character `o` was really `t`). With no counts every score is 0 and ties fall back to id, so v1.1 behaviour is kept.
2. `grade(entry, f)`: add `ev["brand"] = brand_evidence(entry.get("brand"), f)`, which returns `n/a` (entry has no brand), `match` (coverage ≥ `BRAND_MATCH`), `mismatch` (pack has a detected brand and coverage < `BRAND_MISMATCH`), or `unknown` (also when the entry brand has no name tokens). Status order: (i) product, maker or brand mismatch → `reject`; (ii) dates mismatch while product is `match` **and the batch is `exact` or `confirmed`** → `needs_confirm_field` if every differing date differs in at most `DATE_ASK_MAX_DIGITS` digit, else `date_conflict`; (iii) any other dates mismatch → `reject` (v1.1; a variant sibling with different dates is a different batch); (iv) the v1.1 order. Return `date_diffs` with the entry.
3. `decide(graded, read_ok)`: `needs_confirm_field` counts as pending (`ASK`); if nothing is accepted or pending and some candidate is `date_conflict` → `("CANT_VERIFY", that candidate)`.

### A3 Tests added (the v1.1 tests stay and must still pass)
```python
def test_v2_textutils():
    assert find_batch(["Calamine Lotion IP", "B.No. CL2401"]) == ("CL2401", 1)
    assert find_batch(["Batchwise QC passed", "Batch No: X1234"]) == ("X1234", 1)
    assert find_batch(["BatchNo.AB1234"]) == ("AB1234", 0)
    assert find_batch(["B.No.", "SP240165", "Mfg. 06/2024"]) == ("SP240165", 1)
    assert find_batch(["B.No.", "Mfg. 06/2024"]) == (None, None)
    assert parse_month_year("01/07/24") == "2024-07"
    assert parse_month_year("Apr—2026") == "2026-04"

def test_v2_matching():
    e = dict(id=9, product="Paracetamol Tablets IP 650 mg", brand="Dolo-650", batch_key="DL2401",
             mfg="2025-01", exp="2027-12", maker_name="Micro Labs Ltd", entry_type="NSQ", how="exact", subs=[])
    other_brand = dict(product_text="Calpol 650 Paracetamol Tablets IP", brand="Calpol 650", mfg="2025-01", exp="2027-12", maker="GSK")
    assert grade(e, other_brand)["status"] == "reject"
    one_digit = dict(product_text="Dolo-650 Paracetamol Tablets IP", brand="Dolo-650", mfg="2025-01", exp="2027-10", maker="Micro Labs Ltd")
    assert grade(e, one_digit)["status"] == "needs_confirm_field"
    far = dict(one_digit, exp="2028-03")
    g = grade(e, far)
    assert g["status"] == "date_conflict" and decide([g], read_ok=True)[0] == "CANT_VERIFY"
    idx = build_index([dict(id=1, batch_key="BBT2305"), dict(id=2, batch_key="B8T2305")])
    assert [h["id"] for h in search_variants(idx, "B3T2305")][:2] == [1, 2]
    assert [h["id"] for h in search_variants(idx, "B3T2305", prior={("3", "8"): 5})][:2] == [2, 1]
```
Graph-level tests (M3): `08_sibling_trap` → `NOT_LISTED` with the gate and `FLAGGED` without it; `09_date_conflict` both answers; R2 downgrade wording when `confirm_batch` is declined.

**Verified 25 Oct 2026** (Python 3.11.9, rapidfuzz 3.14.6): the amended modules and tests are in `docs/spikes/v2_matching/`; `pytest -q` → 12 passed (v1.1 A3 tests verbatim, including all 7 matching scenarios, plus the tests above and five more edge cases). M3 starts from that code.

---

## Appendix D — SSE events (`data:` is JSON; every event carries `thread_id`)

```
event: step        {"step":5,"node":"planner","action":"search_variants","source":"llm","thought":"the 3 may be a scuffed B","summary":"1 entry: BBT2305","ms":812}
event: fields      {"batch":{"value":"B3T2305","source":"ocr","score":0.99,"image":0,"line":3},"product_text":{...},"mfg":{...},"exp":{...},"maker":{...},"brand":{...}}
event: strip       {"chars":[{"ch":"B","state":"read","alts":[]},{"ch":"3","state":"confusable","alts":["8","B"]},...],"source":"ocr","ask_index":null}
event: candidates  [{"id":412,"batch_key":"BBT2305","how":"variant","status":"needs_confirm_char","evidence":{...}}]
event: interrupt   {"kind":"confirm_char","question":"...","options":["B","3","Can't tell"],"positions":[2],"crop_ids":["c_9f2a..."],"prior":"OCR has misread B as 3 twice before."}
event: final       {"label":"FLAGGED","headline":"On a CDSCO list of failed samples","explanation":"...","confidence":"high","citations":[...],"evidence":{...},"batch_evidence":"user_confirmed","lang":"en"}
event: error       {"message":"Ollama timed out; using rules","recoverable":true}
event: done        {}
```

## Appendix E — New LLM/VLM schemas (Pydantic, `method="json_schema"`)

```python
class PackFieldsVLM(BaseModel):
    batch: str | None; batch_legible: bool
    mfg: str | None; exp: str | None
    brand: str | None; generic_name: str | None; manufacturer: str | None
# system: "You read printed text on a photo of a medicine strip or carton. Copy characters exactly as printed;
#  never correct, complete or guess them. If any character of the batch number is unclear, set batch_legible
#  to false. Use null when a field is not visible."

class BillItem(BaseModel):
    product: str; batch: str | None; exp: str | None
class BillItems(BaseModel):
    items: list[BillItem]
# system: "Extract the medicine line items from the OCR lines of an Indian pharmacy bill. Copy text exactly.
#  One item per medicine. Never invent a batch number; use null if it is not printed."
# Grounding guard (v1.1 §8.4) applies to every value.
```


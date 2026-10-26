# Build guide for the Builder (and the Builder's coding agent)

*Version 1.0 · 27 October 2026. Read `docs/COLLABORATION.md` first: it holds the rules. This file holds the procedures.*

---

## 0. What you are building, in one paragraph

StripCheck is an offline agent that reads a photo of a medicine strip or carton, extracts the batch number and other printed fields, and decides whether that exact batch appears on CDSCO's monthly lists of drugs that failed quality tests (NSQ) or were declared spurious. It answers FLAGGED, SUSPECTED_FAKE, NOT_LISTED or CANT_VERIFY, always cites its source, asks the person a question when one character is in doubt or before any alarm, and never calls a medicine safe. Python backend (LangGraph agents, RapidOCR, SQLite, FastAPI) and a React web UI usable from a phone on the same Wi-Fi. A small local language model (Ollama) helps at a few decision points, but **everything must also work without it**, which is how you will build and test on your PC.

The complete design is `StripCheck_Build_Spec_v2.md`. This guide tells you how to turn it into code on your machine and hand it over.

---

## 1. Documents and what each is for

| Read | Why |
|---|---|
| `CLAUDE.md` / `AGENTS.md` | Conventions every session follows (style, safety, saving work, gotchas). Claude Code loads `CLAUDE.md` automatically. |
| `docs/COLLABORATION.md` | The rules: roles, `main`-only git protocol, claiming, ownership, pre-push checklist, conflicts. |
| `docs/BUILD_STATUS.md` | Which milestone is claimed, built or done. Update it when you claim and when you finish. |
| `docs/HANDOFF.md` | Messages between the two machines, newest first. Read before every session. |
| `StripCheck_Build_Spec_v2.md` | **The contract.** §0 lists what changed from v1.1; §3 data; §4 architecture and repo layout; §5 stack and pins; §6 config; §7 database; §8 ingest; §9 perception; §10 investigator, HITL, grading, verifier, templates; §11 memory; §13 API; §14 UI; §15 evaluation; §16 CLI; §17 milestones; Appendices A, D, E. |
| `StripCheck_Build_Spec.md` (v1.1, frozen) | Verified reference code and patterns: Appendix A (textutils, matching), Appendix B (LangGraph streaming/interrupt/resume, crash resume, Phoenix spans, Streamlit-era HITL loop, OCR/QR, pdfplumber, LLM call), Appendix C (Pydantic schemas and prompts). v2 overrides it where they differ. |
| `docs/spikes/v2_matching/` | `textutils.py` and `matching.py` with the v2 amendments applied, plus tests (12 passing). Copy them into `core/` and `tests/` in M3 (or M1 for textutils). |
| `docs/design/ui_direction.md` + `docs/design/prototype/index.html` | The UI design system and a clickable prototype of the Check screen in all five states. The React UI must match it. |
| `research_notes/StripCheck engineering scan/` | Facts behind the data and stack decisions (portal endpoints, library versions, model shortlist). |
| `paper/`, `reports/`, `research_notes/StripCheck literature survey/` | The research paper and literature survey. Integrator-owned; read for context only. |

---

## 2. Install the prerequisites (once)

**Windows 11 (primary target).**
1. Git for Windows (2.45+), with Git Credential Manager (default).
2. Python **3.12** (64-bit), either Miniconda/Anaconda or the python.org installer.
3. Node.js **24 LTS** (or at least 22.12), from nodejs.org.
4. Optional: Ollama (https://ollama.com) if you want to try the LLM paths; not required for building.
5. Optional: TeX Live, only if you want to build the paper (you do not need to).

**macOS / Linux.** Same versions; use `python3.12 -m venv .venv` and `source .venv/bin/activate`. All code uses `pathlib`; if anything assumes Windows paths, that is a bug to fix.

---

## 3. Get the repository and the environment

```
git clone https://github.com/Suraj-B12/StripCheck.git
cd StripCheck

# Option A: conda (the Integrator laptop uses this)
conda create -n stripcheck python=3.12 -y
conda activate stripcheck

# Option B: venv
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux

python -m pip install --upgrade pip
pip install --dry-run -r requirements.txt     # M0 step 1: check the pins resolve; fix and record any conflict
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env                          # cp on macOS/Linux; then edit if needed
```
The `web/` folder appears in M0; after that: `npm --prefix web ci` (or `npm --prefix web install` the first time).

**PowerShell note:** if `npm` scripts are blocked, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once (or use the `npm.cmd` shim).

---

## 4. Getting the data (needed from M1)

CDSCO data is never committed (copyright policy). Fetch it once on your machine; it takes about three minutes because requests are spaced 1.5 s apart.

```
python docs/spikes/data_analysis/snapshot_cdsco.py data/_snapshot
python docs/spikes/data_analysis/import_snapshot.py data/_snapshot . --no-stats
```
This writes `data/raw/portal/{nsq,spurious}/YYYY-MM.json` plus `.meta.json` files, the same layout `cli.py sync --offline` reads. **Always pass `--no-stats`**: without it the script rewrites `paper/generated/stats.tex`, which belongs to the Integrator. Once M1 exists, `python cli.py sync` replaces these scripts.

Tests must not depend on this data: they use small synthetic fixtures in `tests/fixtures/`.

---

## 5. The build plan (M0 to M6, in order)

General rules for every milestone:
- Claim it in `docs/BUILD_STATUS.md` and push the claim first.
- Implement exactly what spec v2 §17 lists for the milestone and the sections it points to.
- Write the tests named here; mark Ollama tests `@pytest.mark.llm` and internet tests `@pytest.mark.net`.
- Commit and push after each module whose tests pass.
- "Built" means: every test without those markers passes on your PC, and the offline parts of the "Done when" commands pass. Paste the command output summary into HANDOFF.

### M0 · Foundation
- **Spec:** §4.1 (layout), §5 and §5.1 (stack and pins), §6 (config), §7 (database), §13 (only `/api/health`), §14 (web scaffold), §16 (`doctor`, `serve`).
- **Create:** `pytest.ini` (`pythonpath = .`, markers `llm` and `net`, `addopts = -m "not llm and not net"`); `core/__init__.py`; `core/config.py` (reads `.env` with python-dotenv; constants from v1.1 §5 and v2 §6, including `MAX_STEPS = 16`); `core/db.py` (schema v2, WAL, `connect()` helper, `init_db()`); `cli.py` (argparse with every subcommand from §16; `doctor` and `serve` implemented, others print "not implemented yet (M<k>)"); `server/__init__.py`, `server/app.py` (FastAPI app factory, `GET /api/health`, serves `web/dist` at `/` when it exists); `web/` (Vite + React + TypeScript; `src/styles/tokens.css` from `ui_direction.md` §3; fonts from `@fontsource`; an app shell with the left rail, top bar and freshness chip from the prototype); `requirements-dev.txt` if changed; README "Setup" section.
- **Tests:** config loads defaults without `.env`; `init_db()` creates every table and is idempotent; `/api/health` returns 200 with Ollama absent (status "down", not an error).
- **Done when (built):** `python cli.py doctor` prints every check (Ollama/Phoenix may be "not running"); `python -m pytest -q` green; `npm --prefix web run build` passes; `python cli.py serve` shows the shell at http://127.0.0.1:8000.

### M1 · Data
- **Spec:** §3 (sources, endpoints, sync policy, field mapping), §8 (ingest graph, cleaning rules §8.2, portal fetch §8.3), §7, §15.6 (statistics), v1.1 §7 (ingest details) and Appendix B2/B6.
- **Create:** `core/textutils.py` (copy from `docs/spikes/v2_matching/core/textutils.py`), `core/portal.py`, `core/ingest.py` (adapters: `portal_json`, `pdf_lines`, `pdf_text_chunks`; HTML/CSV/XLSX may be stubs until M9), `core/ingest_agent.py` (LangGraph + SqliteSaver, resumable, `STRIPCHECK_CRASH_AT`), `core/analysis.py` (statistics to `paper/generated/stats.tex` and `paper/figures/`; the Builder runs it only to test, and does not commit its outputs), CLI `sync`, `ingest`, `stats`, `fetch --pdfs`.
- **Tests:** latin-1 fixture decoding; every cleaning rule in §8.2 (multi-batch split, GS1 prefix, `?` dash, brand from brackets, placeholder makers, source and lab normalisation, month mismatch flag); idempotent re-ingest adds 0 rows; crash-and-resume; a ReportLab-generated PDF table (v1.1 §16) parsed by `pdf_lines`; repair without Ollama quarantines with reason `no_llm`.
- **Done when (built):** `python cli.py sync --offline` loads every stored month; a second run adds 0 rows; the resume test passes; `python cli.py stats` runs (outputs not committed by the Builder).

### M2 · Perception and props
- **Spec:** §9, §15.1 to §15.3, v1.1 §8 and §12, Appendix B5.
- **Create:** `core/pack_tools.py` (zxing-cpp QR/DataMatrix with OpenCV fallback; RapidOCR with `ocr_version` pinned; enhance; `extract_fields` with provenance), `core/crops.py`, `core/vlm.py` (returns `None` when Ollama or the model is missing), `core/props.py`, `core/degrade.py`, CLI `props`.
- **Tests:** QR payload parsing; OCR reads the batch on a rendered clean prop (marked slow if needed); character boxes and crops are produced; `vlm.read_pack_vlm` returns `None` without Ollama; degradations are deterministic per seed.
- **Done when (built):** `python cli.py props --demo` writes the 11 demo props and the manifest from your local database; OCR reads the batch on the clean props; misread and sibling calibration succeed or log their fallback; `python cli.py props --calibrate` stores a confusion table.

### M3 · Reasoning (rules mode)
- **Spec:** §10 (all of it, including the answer-handling rules, step/question budgets and verifier R1 to R10), §11 (only the `confusions` table use), Appendix A, v1.1 §9.
- **Create:** `core/matching.py` (copy from the spike), `core/noisy.py`, `core/alert_tools.py`, `core/investigator.py`, `core/verifier.py`, `core/templates.py` (English templates now; Hindi and the regional language in M9), text mode, CLI `check` (terminal prompts) and `selftest`.
- **Tests:** the spike tests; graph tests that run all 11 demo props with scripted answers and assert verdicts **and** the step/question budgets in spec §6; verifier rule tests; banned-phrase tests on every template.
- **Done when (built):** all 11 demo props give the expected verdicts with `--planner rules`; `python cli.py selftest` passes.

### M4 · LLM layer
- **Spec:** §5.1 (Ollama notes), §10.3 (hybrid branch points), §15.11, v1.1 §9.3 and Appendices B7 and C, v2 Appendix E.
- **Create:** `core/llm.py` (structured output with Pydantic validation, one retry, timeout, fallback returning `None`; never send `tools` and `format` together), the hybrid and llm planners, product adjudication, extraction fallback, verifier critique, ingest repair and header mapping, CLI `bench`.
- **Tests:** everything with the LLM **mocked** (no Ollama needed): fallback to rules on timeout, invalid JSON and disallowed action; `llm`-marked integration tests for the Integrator.
- **Done when (built):** mocked tests pass; with Ollama stopped, `python cli.py check <prop> --planner hybrid` finishes and the log shows `rules(fallback)`. (The Integrator runs the real models and the benchmark.)

### M5 · Observability
- **Spec:** §12, v1.1 §11 and Appendix B3.
- **Create:** `core/tracing.py` (Phoenix `register` wrapped in try/except; JSONL step log always), `GET /api/traces/{tid}`.
- **Tests:** JSONL lines are written and parse; tracing failure never raises.
- **Done when (built):** a check writes `runs/<thread>.jsonl`; the trace endpoint returns it.

### M6 · API and UI
- **Spec:** §13 (every endpoint, SSE bridge), §14, `docs/design/ui_direction.md`, the prototype, Appendix D (SSE events).
- **Create:** `server/routes_*.py`, `server/sse.py`, and the React screens and components listed in §14 (`BatchStrip`, `StepTimeline`, `AskCard`, `VerdictSlip`, `EvidenceChips`, `FreshnessChip`, `PhonePair`, `DataTable`), phone pairing.
- **Tests:** FastAPI TestClient tests for checks, resume and SSE event order; Vitest tests for the SSE parser, strip state mapping and the WCAG contrast of every token pair.
- **Done when (built):** every demo prop runs from the UI in rules mode, including each question kind; `npm --prefix web test` and `npm --prefix web run build` pass; `python -m pytest -q` green; screenshots of the five verdict states committed to `docs/img/`.

After M6 the Builder stops unless the HANDOFF asks for more (M7 to M10 are mostly Integrator work: evaluation, supervisor tuning, extras, paper).

---

## 6. Kickoff prompts for your coding agent (copy and paste)

**First session (Claude Code or any coding agent, opened in the repository folder):**
```
You are the Builder agent for StripCheck. Before writing any code:
1. Run `git pull --rebase`.
2. Read, in this order: CLAUDE.md (or AGENTS.md), docs/COLLABORATION.md, docs/BUILD_GUIDE.md, docs/BUILD_STATUS.md, the newest entries in docs/HANDOFF.md, StripCheck_Build_Spec_v2.md and docs/design/ui_direction.md. Skim StripCheck_Build_Spec.md (v1.1) Appendices A to C: they are verified reference code.
3. Claim the first milestone whose state is "not started" in docs/BUILD_STATUS.md (normally M0). Commit only that change as "status: claim M0 (builder)" and push it at once.
4. Implement that milestone exactly as StripCheck_Build_Spec_v2.md §17 and the sections it references describe, and as docs/BUILD_GUIDE.md §5 lists for it. Keep code minimal, flat and procedural.
5. Save incrementally: after each module whose tests pass, run the pre-push checklist in docs/COLLABORATION.md §6, commit with the message format in §4, and push.
6. Every test that needs neither Ollama nor the internet must pass on this machine. Mark Ollama tests @pytest.mark.llm and internet tests @pytest.mark.net.
7. When the milestone's "Done when (built)" checks pass, set its row to "built" in docs/BUILD_STATUS.md and add a docs/HANDOFF.md entry with the exact commands you ran and their results, the files you created, what you could not verify, and ACTION items for the Integrator. Commit and push.
8. Stop and report. Do not start the next milestone unless asked.
Never force-push, never commit anything under data/, never weaken a safety rule, and ask me before installing system software or downloading anything large.
```

**Continuing session:**
```
Continue as the StripCheck Builder. Run `git pull --rebase`, read docs/BUILD_STATUS.md and the newest docs/HANDOFF.md entries (the Integrator may have pushed fixes, questions or ACTION items), then resume the builder's "in progress" milestone from what is already committed. Follow CLAUDE.md and docs/COLLABORATION.md. Commit and push after each module.
```

**With Claude Code's multi-agent mode (ultracode), for one milestone:**
```
ultracode: as the StripCheck Builder, implement milestone M<k>. Follow the first-session prompt rules above. Plan the milestone into modules, implement disjoint modules in parallel (worktrees only when files overlap), make every agent save and commit incrementally, run the full test suite in a final verification stage with adversarial review for spec compliance and safety language, then update docs/BUILD_STATUS.md and docs/HANDOFF.md and push to main.
```

---

## 7. Everyday commands

```
python -m pytest -q                       # offline tests (default markers exclude llm and net)
python -m pytest -q -m llm                # Integrator: tests that need Ollama
python cli.py doctor
python cli.py sync --offline              # from M1
python cli.py props --demo                # from M2
python cli.py check data/props/03_misread.jpg --planner rules   # from M3
python cli.py selftest                    # from M3
python cli.py serve                       # from M0; UI from M6 at http://127.0.0.1:8000
npm --prefix web run dev                  # UI development server (proxy /api to :8000)
npm --prefix web test
npm --prefix web run build
```

---

## 8. Troubleshooting

- **`UnicodeDecodeError` on portal JSON:** the portal serves ISO-8859-1; decode bytes with `latin-1`. Console output stays ASCII; set `PYTHONUTF8=1`.
- **`ImportError: DLL load failed` for cv2:** `pip uninstall -y opencv-python opencv-python-headless` then `pip install "opencv-python-headless>=4.14,<5"`. Never install both builds.
- **RapidOCR picks unexpected models:** set `Det.ocr_version` and `Rec.ocr_version` explicitly (spec §5.1); the default changed to PP-OCRv6 in RapidOCR 3.9.
- **`database is locked`:** WAL mode, short transactions, one connection per thread, `check_same_thread=False` only for the checkpointer.
- **LangGraph resume oddities:** nodes re-run from the top on resume; nothing with side effects may run before `interrupt()` returns (v1.1 §9.6). LangGraph ≥ 1.2.16 is required.
- **pip resolver conflict on a fresh major version** (pillow 13, pandas 3, zxing-cpp 3, reportlab 5): cap below the major, record it in `docs/decisions.md` and README "Deviations".
- **Port 8000 busy:** `python cli.py serve --port 8010`.
- **`conda` not found in PowerShell:** run `conda init powershell` once and reopen the terminal, or use the Anaconda Prompt.

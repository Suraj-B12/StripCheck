# StripCheck research and build log

Newest entries first. Every milestone and every research run adds an entry: what was done, where the outputs are, what is unfinished, and how to resume.

## 2026-10-27 · Repository and two-machine workflow

- Published the project to https://github.com/Suraj-B12/StripCheck (`main` only). A collaborator (Builder) implements milestones on his PC and pushes; this laptop (Integrator) runs Ollama, real data, evaluation and the paper.
- Added `docs/COLLABORATION.md` (rules), `docs/BUILD_GUIDE.md` (setup, data, per-milestone plan, kickoff prompts), `docs/BUILD_STATUS.md` (milestone board), `docs/HANDOFF.md` (message log), `docs/decisions.md` (D1 to D15 plus pending P1 to P4), `AGENTS.md`, a collaboration section in `CLAUDE.md`, `.gitignore` (data, databases, builds, secrets excluded), `.gitattributes`, proposed `requirements*.txt` and `.env.example`.
- `docs/spikes/data_analysis/import_snapshot.py` gained `--no-stats` so the Builder can load data without touching `paper/generated/stats.tex`.

## 2026-10-26 · Synthesis report complete

- `reports/StripCheck literature survey.md`: 18,811 words, 10 sections, a summary table of key works, a gap table (G1 to G10, limits L1 to L3), 324 distinct citations, all present in `paper/references.bib`. Sections 1 to 6 map onto the thesis literature-survey chapter; §10 gives condensing and citation notes.
- Changes it prompted: predictive value at realistic base rates (1% and 0.1%), OCR confidence calibration on batch codes, and blocking recall of the variant search added to spec v2 §15.8 and paper §V; durable measurements (strip dataset, confusion table, calibration, collision rate, lag) framed as contributions.

## 2026-10-26 · Literature survey integrated; ready for M0

- Run 3 finished: all 12 literature themes researched and citation-verified (350 verified BibTeX entries across themes); the tech-stack scan is complete. Only the synthesis report (`reports/StripCheck literature survey.md`, for the thesis chapter) was cut off by the usage limit and was relaunched on the same run ID (`wf_f1defe68-0ca`).
- `paper/tools/merge_bib.py` merged the theme bibliographies into `paper/references.bib`: 338 unique entries (15 cross-theme duplicates merged), plus Holm (1979) verified through OpenAlex. A `\nocite{*}` BibTeX test compiled all entries with 0 warnings and 0 errors.
- Paper: Related Work written (8 subsections, 79 verified keys); every `\citeneeded` placeholder replaced (`paper/tools/check_cites.py`: 92 keys cited, 0 missing, 0 placeholders); builds to 9 pages with no undefined references.
- Framing correction from the survey: Nazar, SafeDose, RecallOps India and Blacklisted already offer typed or photo lookup, look-alike guards, abstention, corroboration or re-checks. The paper now positions StripCheck on what we did not find elsewhere (character questions to the user, full field corroboration on photographed consumer packs, offline operation, verifier agent, second reader) and on the data analysis and the evaluation.
- Spec v2 §5.1: verified pins (Python 3.12; RapidOCR OCR version pinned explicitly; OpenCV < 5; FastAPI native SSE; LangGraph ≥ 1.2.16; MCP 2.x API; Phoenix in its own venv; Ollama model shortlist and the 0.17.7 → 0.40.x upgrade question).
- Brief rebuilt with all 350 verified references listed per theme (`docs/prompts/brief/`), page republished.

## 2026-10-26 · Resumed; external survey brief

- Resumed run 3 (`wf_f1defe68-0ca`) from its saved state.
- Wrote a brief for a friend's research model: `docs/prompts/literature_survey_brief.template.md` → `build_brief.py` fills each theme card with our verified references (320 at build time) → `literature_survey_brief.md`, plus paste-ready files in `docs/prompts/brief/`. 15 themes: our 12 plus three new ones found while designing (T13 agent_security: prompt injection through text printed on packs; T14 receipts_kie: for bill scan; T15 warning_habituation: people tap "yes" without looking).
- `docs/prompts/check_external_survey.py` validates returned files (header, 11 sections, source fields, key format, BibTeX match, DOI/URL) and separates new sources for verification; tested on a planted-error sample (all errors caught).
- Shareable copy-button page: `docs/prompts/brief_page.html`, published privately at https://claude.ai/artifact/HTTGaW8JLaf9PzV3grL6xk (rebuild with `build_brief.py` then `build_brief_page.py`, republish the same file).
- Design change from T15: `confirm_batch` now asks for the two characters most likely to be misread instead of offering a yes/no button (spec v2 §10.4).

## 2026-10-25 · PAUSED at the owner's request (resume here)

Run 3 of the literature survey (`wf_f1defe68-0ca`) was stopped deliberately. Every agent had been saving incrementally, so nothing finished was lost.

| Theme | Research | Citation check | Verified .bib entries |
|---|---|---|---|
| sf_medicines_india | complete | complete | 49 |
| traceability_authentication | complete | complete | 20 |
| screening_tech_and_apps | complete | complete | 26 |
| packaging_ocr | complete | complete | 31 |
| ocr_postcorrection_alpr | complete | complete | 24 |
| record_linkage | complete | complete | 18 |
| llm_agents | complete | complete | 35 |
| document_extraction | complete | complete | 34 |
| abstention_hitl_safety | complete | partial | 19 so far |
| evaluation_methodology | complete | partial (log started, .bib empty) | 0 so far |
| india_user_context | complete | not started | none |
| recall_monitoring | in progress (~5,600 words saved) | not started | none |
| tech_stack_oct2026 (engineering) | in progress (~3,300 words saved) | n/a | n/a |
| Synthesis report (`reports/StripCheck literature survey.md`) | not started | | |

**To resume:** `Workflow({scriptPath: "docs/workflows/stripcheck_lit_v3.js", resumeFromRunId: "wf_f1defe68-0ca"})`. Agents that finished replay from cache; unfinished ones restart and continue from their own files (status checklists, `## Verification log`, partial `.bib`). The report writer runs once at least 11 themes are verified.

**After the survey finishes (remaining design-phase work):** merge the verified `.bib` files into `paper/references.bib`; write `paper/sections/02_related_work.tex` from the report and replace every `\citeneeded{}` in the introduction and system sections with verified keys; take dependency pins and the model shortlist from `tech_stack_oct2026.md` into spec v2 §5; then tell the owner it is time to start coding (M0).

**Open questions for the owner:** team names and institution for the paper; the regional language besides Hindi (Kannada assumed) and a native-speaker reviewer; whether coding agents may commit after each module; OK to pull about 10-15 GB of Ollama models.

## 2026-10-25 · Design phase (thinking before coding)

**Status:** paused (see above).

### Literature survey (deep-research workflow)
- Run 1 (`wf_dcd55f76-a0d`) was cut off by the session usage limit after about 2.2M tokens. Agents saved only at the end, so 13 of 14 lost their work. Only `research_notes/StripCheck engineering scan/cdsco_data_sources.md` survived.
- Run 2 (`wf_51b32e59-c9a`, launched 25 Oct 2026) re-runs 12 literature themes + the tech-stack scan with mandatory incremental saving (status checklist, append after every 2-3 sources, resume from the existing file) and a rolling window of 6 agents.
- Run 2 also hit the usage limit (~1.7M subagent tokens), but incremental saving worked: research finished for 5 themes, verification finished for 2 (`ocr_postcorrection_alpr`, `record_linkage`), and `sf_medicines_india` was saved mid-way.
- Run 3 (`wf_f1defe68-0ca`, `docs/workflows/stripcheck_lit_v3.js`) does only the remaining work: research for 7 themes (one resumed), verification for 10, then the synthesis report. Research and verification agents run on Sonnet to fit the usage window; the report writer runs on the session model.
- **Resume if interrupted:** `Workflow({scriptPath: "docs/workflows/stripcheck_lit_v3.js", resumeFromRunId: "wf_f1defe68-0ca"})`. Completed agents replay from cache; unfinished agents continue from their own files on disk. All three scripts (v1, v2, v3) are kept in `docs/workflows/` as a record of the survey method.
- Outputs: `research_notes/StripCheck literature survey/<theme>.md` + `<theme>.bib` (verified references only), `reports/StripCheck literature survey.md` (synthesis).

### Data source discovery
- CDSCO's NSQ alerts moved to `cdscoonline.gov.in` (SUGAM). The viewer's own JavaScript calls plain JSON endpoints (`filteredNsqDrugTable?month=MON-YYYY&source=All&tab=nsq`, `filteredSpuriousDrugTable`, `reportingYears`, `publicReportingMonths`). No cookie is needed; responses are latin-1.
- A polite snapshot (1.5 s between requests) fetched all 93 NSQ months (Jan 2019 → Sep 2026) and the 2025-26 spurious months: 108 files, 3.7 MB, zero failures. Details: `research_notes/StripCheck engineering scan/cdsco_data_sources.md` ("Browser investigation").
- Consequence: the portal JSON becomes the primary ingest source (spec v2 §3); PDFs become secondary.

### Design outputs
- `StripCheck_Build_Spec_v2.md`: complete v2 build spec (portal-first data, FastAPI + React UI, confirm-batch gate, brand and date-conflict grading, noisy-channel ranking, optional VLM reader, evaluation v2, milestones M0 to M10, Appendix A code amendments).
- `docs/spikes/v2_matching/`: the Appendix A amendments as runnable code; `pytest -q` → 12 passed (v1.1 tests verbatim + v2 tests).
- Scenario tracing of the v2 planner found four logic gaps, now fixed in the spec: MAX_STEPS 12 → 16; typed corrections reject the read key; reader disagreement becomes a character question; drafter applies the batch gate; fields carry a version so new evidence forces a regrade. Step/question budgets for all 11 demo props are recorded for the M3 tests.
- `docs/design/ui_direction.md` + `docs/design/prototype/index.html`: design system and a clickable Check-screen prototype (five states, light/dark, phone layout verified at 375 px with no horizontal scroll). Fixed while critiquing: `display: revert` state toggling, SVG crop sizing, dark-mode ring specificity, accent-button contrast, timeline badge wrapping.
- `paper/`: IEEE LaTeX draft that compiles (5 pages): abstract, introduction, data, system design and evaluation method written; related work waits for the verified survey; results after M7. Numbers come from `paper/generated/stats.tex`, produced by `docs/spikes/data_analysis/import_snapshot.py`.
- `data/raw/portal/`: the snapshot in the spec layout (186 files incl. metadata; git-ignored).
- `CLAUDE.md`: conventions for every coding session.

### Snapshot statistics (preliminary, regenerated in M1)
7,005 rows over 93 months; 63.5% of flagged batches still have at least 12 months of shelf life when the alert appears (median lag 10 months); 36 batch keys shared by unrelated products; 58 same-maker confusable sibling pairs (e.g. R21119/R21719).

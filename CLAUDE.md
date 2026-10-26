# StripCheck: conventions for Claude Code sessions

Agentic AI college project (course 26CD7PEAAI). StripCheck checks whether a medicine pack's batch is on CDSCO's NSQ/spurious alert lists: perception (QR, OCR, optional VLM) → confusion-aware retrieval → record-linkage grading → human questions → verifier → templated verdict.

## Read first
1. `docs/COLLABORATION.md`: the two-machine rules (roles, `main`-only git protocol, claiming, ownership, pre-push checklist). **Binding for every agent.**
2. `docs/BUILD_STATUS.md` and the newest entries of `docs/HANDOFF.md`: what is claimed, built, done, and any messages or ACTION items.
3. `docs/BUILD_GUIDE.md`: setup, getting the data, per-milestone build plan, kickoff prompts, troubleshooting.
4. `StripCheck_Build_Spec_v2.md`: authoritative scope, architecture, milestones (M0 to M10).
5. `docs/design/ui_direction.md` + `docs/design/prototype/index.html`: authoritative UI design system and prototype.
6. `StripCheck_Build_Spec.md` (v1.1, frozen): verified appendices A to C (code, LangGraph/Phoenix/OCR patterns, LLM schemas).
7. `docs/spikes/`: verified reference code (v2 matching amendments, 12 tests passing) and the data-analysis scripts.
8. `research_notes/`, `reports/`, `paper/`: literature survey, engineering scans and the paper (Integrator-owned).
9. `docs/research_log.md` and `docs/decisions.md`: history, run IDs, decisions and spec deviations.

## Collaboration (two machines, one `main` branch)
- **Builder** (collaborator's PC, usually no Ollama/GPU/data) implements milestones and pushes; **Integrator** (Suraj's laptop: GPU, Ollama, CDSCO data) runs the backend agents, LLM tests, evaluation and paper, and pushes adjustments. Details: `docs/COLLABORATION.md` §1.
- Every session starts with `git pull --rebase`, then reads `docs/BUILD_STATUS.md` and `docs/HANDOFF.md`. Claim work in BUILD_STATUS (commit + push the claim) before starting.
- Commit after each module whose tests pass (`<scope>: <what> (<test summary>)`), `git pull --rebase` and re-test before `git push`. Never force-push, amend pushed commits, or rewrite history; no branches.
- Finished module, milestone, stop or blocker → a `docs/HANDOFF.md` entry (newest first) with commands run and results.
- Spec changes need a `docs/decisions.md` entry in the same commit. `StripCheck_Build_Spec.md` (v1.1) is frozen.

## Ground rules
- Windows 11, PowerShell, conda env `stripcheck`. `pathlib` for paths, `encoding="utf-8"` for our files; CDSCO portal JSON is **latin-1**. Console output ASCII only. `PYTHONUTF8=1` in `.env`.
- Python style: minimal, flat, procedural. Plain functions; `TypedDict`/Pydantic only for data shapes; no class hierarchies, factories or DI layers; one module per concern; short docstrings.
- Frontend: Vite + React + TypeScript, function components, CSS variables from `web/src/styles/tokens.css`, no UI kit, no CSS framework, no CDN; fonts from `@fontsource`.
- Never break the demo: every LLM, VLM, network and tracing call has a timeout and a fallback. A check must complete with Ollama off, Phoenix off and no internet.
- Bound every loop. No paid APIs. Never disable TLS verification. Portal requests at least 1.5 s apart.
- Safety language is a hard requirement: never "safe", "genuine", "authentic", "fake medicine", "stop taking"; flag only the listed batch, never a brand; user-facing verdict text only from `core/templates.py`; no green for NOT_LISTED.
- No invented data: every alert row traces to a stored raw snapshot; every pack field is grounded in QR/OCR/VLM text or typed by the user.
- Keep v1.1 Appendix A code verbatim except the amendments in spec v2 Appendix A (already verified in `docs/spikes/v2_matching`).
- Record deviations from the specs in `README.md` → "Deviations" and decisions in `docs/decisions.md`.

## Saving work (mandatory, usage limits can end a session at any moment)
- Create output files early, append after every small unit of work, keep a status checklist at the top of long documents, and on start resume from whatever is already on disk.
- Commit after each module whose tests pass. Never hold a large amount of unsaved work in memory.
- Run large fan-outs in batches; keep workflow stages idempotent; record every run ID and its resume command in `docs/research_log.md`.

## Tests
- `pytest -q` must pass without Ollama, Phoenix or internet. Markers: `llm` (needs Ollama) and `net` (needs internet) are skipped by default.
- `npm test` (Vitest) for the web client from M6. `python cli.py selftest` (offline end to end) from M3.
- Do not mark a milestone done until its "Done when" command in spec v2 §17 passes.

## Paper and logs (every milestone)
- Update the relevant `paper/sections/*.tex` (plan in spec v2 §20). Numbers come only from `paper/generated/*.tex` (written by `cli.py stats` and `cli.py eval`), figures only from scripts. References only from verified `.bib` files.
- Prose rules for the paper (humanizer): no "not X but Y" contrasts, no dashes as clause connectors, no forced triads, no inflated words (crucial, pivotal, robust as praise, landscape, showcase, delve), plain verbs (is, has), sentence-case headings.
- Build the paper: `cd paper; latexmk main.tex` (config in `paper/latexmkrc`, output in `paper/build/`).
- Add a `docs/research_log.md` entry per milestone: what was done, outputs, open items, how to resume.

## Commands (spec v2 §16)
```
python cli.py doctor [--warm]
python cli.py sync [--offline] [--full]
python cli.py ingest [--no-llm] [--resume THREAD_ID]
python cli.py stats
python cli.py props --demo | --eval --n 200 --seed 7 | --ladder | --calibrate
python cli.py check IMAGE [--planner rules|hybrid|llm] [--vlm] | check --text BATCH
python cli.py serve [--lan]
python cli.py eval --arms ... --hitl oracle|none
python cli.py bench --models ...
python cli.py selftest
```

## Gotchas
- LangGraph `interrupt()`: a node re-runs from its first line on resume, so no side effects before `interrupt()` returns.
- `SqliteSaver(sqlite3.connect(path, check_same_thread=False))`; SQLite in WAL mode; one connection per thread.
- RapidOCR logs a lot: `logging.getLogger("RapidOCR").setLevel(logging.ERROR)`.
- Never install `opencv-python` next to `opencv-python-headless`.
- Portal snapshots live in `data/raw/portal/{nsq,spurious}/YYYY-MM.json` with `.meta.json`; `data/` is git-ignored (CDSCO copyright: keep data local, cite the source, publish only derived statistics).
- The Read tool cannot open PDFs on this machine ("password-protected" error even for our own files); render pages with `rungs -sDEVICE=png16m` (TeX Live Ghostscript) or use pdfplumber.

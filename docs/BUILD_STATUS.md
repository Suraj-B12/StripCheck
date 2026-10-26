# Build status

*Update this file when you claim, finish or stop work (`docs/COLLABORATION.md` §3). Commit a claim on its own and push it at once. History and messages go in `docs/HANDOFF.md`.*

States: `not started` · `in progress` · `built` (Builder: offline checks pass) · `done` (Integrator: full "Done when" passes on the laptop) · `blocked`.

## Milestones (spec v2 §17)

| # | Milestone | State | Owner | Claimed | Last update | Evidence (command → result) |
|---|---|---|---|---|---|---|
| M0 | Foundation: env, config, db, doctor, FastAPI skeleton, web scaffold, paper build | not started | Builder | | | |
| M1 | Data: portal sync, ingest agent, cleaning, resume, stats | not started | Builder | | | |
| M2 | Perception and props: QR, OCR, crops, VLM reader, demo props, calibration | not started | Builder | | | |
| M3 | Reasoning in rules mode: matching, noisy channel, investigator, verifier, templates, CLI check, selftest | not started | Builder | | | |
| M4 | LLM layer: Ollama structured calls, hybrid planner, adjudication, benchmark | not started | Builder (mocked) → Integrator (real models) | | | |
| M5 | Observability: Phoenix tracing, JSONL, trace API | not started | Builder → Integrator | | | |
| M6 | API and UI: endpoints, SSE, React screens, phone pairing | not started | Builder | | | |
| — | **Review 2 cut line: M0 to M6 is the demo** | | | | | |
| M7 | Evaluation: golden set, ladder, arms, ablations, statistics, figures | not started | Integrator | | | |
| M8 | Supervisor, cabinet, notifications, learning loop | not started | Builder → Integrator | | | |
| M9 | Extras: bill scan, Hindi and regional templates, read aloud, MCP server | not started | Builder | | | |
| M10 | Paper and release | not started | Integrator | | | |

## Current module checklist

*The owner of the `in progress` milestone keeps this list current (one line per module: `[ ]` to do, `[x]` committed and pushed with tests green).*

- (none yet)

## Design phase (finished 27 Oct 2026, Integrator)

- [x] Spec v2 (`StripCheck_Build_Spec_v2.md`), UI direction and prototype (`docs/design/`)
- [x] Verified matching amendments (`docs/spikes/v2_matching`, 12 tests)
- [x] Literature survey (12 themes, 350 verified references; `reports/StripCheck literature survey.md`)
- [x] Paper draft (`paper/`, 9 pages, builds with no undefined references)
- [x] Collaboration rules, build guide, agent instructions

## Machine capabilities

| Capability | Builder PC | Integrator laptop |
|---|---|---|
| Python 3.12, Node ≥ 22.12, Git | required | yes (Node 24.11) |
| CDSCO data | fetched locally from M1 | yes |
| Ollama + models, GPU | optional | yes (Ollama 0.17.7, RTX 4050 6 GB) |
| TeX Live | not needed | yes (2025) |
| Phoenix | optional | yes (separate venv) |

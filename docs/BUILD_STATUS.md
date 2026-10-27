# Build status

*Update this file when you claim, finish or stop work (`docs/COLLABORATION.md` §3). Commit a claim on its own and push it at once. History and messages go in `docs/HANDOFF.md`.*

States: `not started` · `in progress` · `built` (Builder: offline checks pass) · `done` (Integrator: full "Done when" passes on the laptop) · `blocked`.

## Reviewed publication · 2026-10-27

The user authorized publishing the reviewed implementation to `main`. Final local verification: **184 Python tests, 43 web tests, 14 compiled Swift checks, 11/11 synthetic scenarios**, clean web build/lint, live native API integration and more than twenty verification areas in [`RELEASE_CHECKS.md`](RELEASE_CHECKS.md). Implementation commit `691e3da` is published; both hosted jobs passed, including **nine XCTest cases and the full unsigned iOS simulator build**. Device interaction/signing/research requirements remain separate. Local preview: **http://127.0.0.1:8765**. Data was backed up before the offline parser refresh; source and alert identities were preserved. The newest handoff entry records the final review-page fix and publication evidence.

## Historical local implementation session · 2026-10-27

This section preserves the earlier local-delivery record. Its test counts and publication statements describe that point in time; the reviewed publication above and newest handoff entry are current.

Builder: Codex on collaborator macOS. The requested local website/API is implemented and verified; the native SwiftUI client source and its compiled API contract checks are delivered. A full iOS simulator/device build remains unverified because this machine has no full Xcode/iOS SDK. The user requested the application work in one session, replacing the per-milestone stop. The original research milestone states below remain unchanged: this local delivery is not a claim that every research milestone is complete. Decisions D16–D18 describe the implementation boundaries.

The checked items in this local section mean implemented and verified to the extent stated, not committed or pushed.

- [x] SQLite persistence; official portal sync and offline imports; actual local Apple Vision OCR; deterministic matching, confirmation and verifier; API, SSE, resume, history and cabinet.
- [x] Apple-inspired responsive web interface; readable typography; browser checks for confirmation, verdict, cabinet save, real alert search and diagnostics.
- [x] Native SwiftUI client source for camera/photos, typed checks, confirmation, alerts, cabinet and activity; compiled API model/client checks and live local API round-trip.
- [x] macOS desktop/phone launchers, Windows launcher, fresh-clone setup and documented deviations. The launchers are provided; physical-phone access has not been tested.
- [ ] Native simulator/device build, camera permissions, VoiceOver interaction and signing, requiring full Xcode/iOS SDK and any necessary device/account authorization.
- [ ] Remaining research architecture/evaluation and reviewed extras: LangGraph checkpointing, production Phoenix integration, model benchmarking/calibration, the full M7 experiment programme and M9 extras. No research accuracy results are fabricated.

### Recorded verification

| Check | Result |
|---|---|
| `.venv/bin/python -m pytest -q` | **88 passed**; one upstream Starlette TestClient/httpx deprecation warning |
| `.venv/bin/python cli.py selftest` | **11/11** isolated synthetic scenarios passed |
| `npm --prefix web test` | **22 passed**, including streaming and theme-contrast checks |
| `npm --prefix web run build` | Passed; approximately **281 KB JavaScript / 41 KB CSS** production output |
| `npm --prefix web run lint` | Oxlint: **0 warnings** |
| Native `StripCheckVerify` executable | **8 compiled contract checks passed** |
| Native URLSession integration | Local check → confirmation/resume → verdict → cabinet save/read/delete round-trip passed |
| Native source/project validation | SwiftUI syntax and project/plist validation passed; full iOS compilation unverified |
| In-app browser review | Confirmation/result/save-cabinet, real alert search and diagnostics **11/11** verified; responsive previews at **319 px and 770 px** reviewed |
| Historical official data | **6,923 active alerts**, **108 source snapshots**, **93 months** from January 2019 through September 2026; **72 quarantined source rows** |
| Data provenance/idempotence | All 108 archived checksums and official source hostnames verified; no synthetic live alerts; repeated offline import adds **0** rows |

The current website is running at **http://127.0.0.1:8765**, listening on localhost only. Final browser passes also verified the no-match, batch collision, missing-product, ambiguous-character and mismatched-date paths. The delivery archive contains source plus `web/dist`, excluding local data, credentials and installed dependencies; see the final packaging entry in `docs/HANDOFF.md`.

Automatic approval review rejected the attempted LAN launch because binding to other network interfaces would expose local photos and checks without the required authorization. **No LAN access was enabled, and no physical-phone connection was tested.** No GitHub push, public deployment, signing/account operation or App Store publication was performed. Integrator-owned research and paper files were preserved.

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

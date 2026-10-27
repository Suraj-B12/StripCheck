# Release verification · 27 October 2026

The user requested an efficiency and crash review, at least ten checks, local hosting and a push to the original repository. Three independent code reviews covered the API/database, ingestion/image reading, and matching/native app; a fourth review checked the browser changes. The list below records distinct verification areas rather than repeating the same test to inflate a count.

## Latest follow-up: Pages showcase and manual checks

The follow-up passes **196 Python tests** (including 12 new incomplete-manual-evidence regressions) and **75 web tests across seven files**. The web suite covers demo-to-manual field isolation, all eleven public guided paths with no network calls, project-subpath navigation, bounded storage and malformed persisted state. Lint, local and Pages production builds, deterministic synthetic fixture comparison and the seven-file static artifact audit pass. Local JavaScript is **264.86 KB** plus **24.38 KB** loaded for secondary pages; Pages uses **256.23 KB**, **23.51 KB** for secondary pages and **62.45 KB** for its lazy fixture adapter. CSS is **42.30 KB**. No dependency was added.

Actual browser checks verified that a fresh `TG261185` query finds two candidates and asks for printed identity details. The public preview completes a guided check, saves the example, survives a Cabinet hash-route refresh and displays all eleven recorded scenario outcomes. Existing Activity results remain historical snapshots.

The Pages workflow publishes only the separately audited static directory. Publishing awaits the owner's one-time Pages setting; neither the configured public URL nor a successful deployment is claimed before that happens. See [the setup instructions](GITHUB_PAGES.md).

## Earlier publication checks

| # | Verification area | Evidence |
|---|---|---|
| 1 | Full offline Python regression suite | **184 passed**, no skips, including real Apple Vision OCR/QR; one upstream Starlette/httpx deprecation warning |
| 2 | Deterministic end-to-end outcomes | CLI selftest **11/11** synthetic scenarios |
| 3 | Ingestion and source identity | Malformed responses, empty revisions, cross-month hash collisions, rollback and SQLite parameter limits covered in the passing suite |
| 4 | Image and OCR failure paths | Corrupt/large images, deadline exhaustion, malformed OCR, barcode disagreements and crop bounds covered |
| 5 | Matching and verdict verification | Oversized batch input, candidate limits, two-photo disagreement, missing/unknown alert types and confirmation covered |
| 6 | API/database concurrency | **14 new resilience checks** include isolated DB paths, connection closure, upload responsiveness, saved-pack deduplication and delete/recheck races |
| 7 | Streaming recovery | Disconnected clients, failed workers, queue limits, interrupted streams and resource cleanup covered |
| 8 | Browser regression suite | **43 tests passed** across four files, including readable review records and malformed-source fallbacks |
| 9 | Browser component races | Delayed restoration cannot overwrite typing; old Cabinet/Activity responses cannot replace the latest selection or reopen a closed dialog |
| 10 | Browser request resilience | Timeouts, cancellation, response-size limits, disabled/full storage, UTF-8 fragments and incomplete streams covered |
| 11 | Readable light/dark themes | **18 contrast assertions** meet the tested AA token pairs |
| 12 | TypeScript and production build | Build passed; initial JavaScript **264.33 KB**, secondary page chunk **24.36 KB**, CSS **40.84 KB** |
| 13 | Web lint | Passed with **0 warnings** |
| 14 | npm dependency advisory scan | **0 known vulnerabilities** reported for the final lockfile |
| 15 | Python dependency compatibility | `pip check`: no broken requirements |
| 16 | Native compiled contract/resilience checks | **14 passed**; URL policy, redirects, errors, cancellation and bounded photo handling included |
| 17 | Native live API round-trip | Health, demo definitions, confirmation/resume, verdict, cabinet save/read/delete, activity and alerts passed against the updated localhost server |
| 18 | Native source/project checks | SwiftUI syntax parse, project, Info.plist and privacy-manifest validation passed |
| 19 | Browser interaction | Actual confirmation/result, lazy library load, filtered search, rapid Sources/Needs review switching and readable source-review explanations verified |
| 20 | Performance comparison | Indexed batch HTTP search on 20,000 synthetic rows: **137.421 ms before; 2.911–3.728 ms after** across review/final runs; twenty DB reads now perform zero schema writes |
| 21 | Live data migration/provenance | Backup created; integrity and foreign-key checks passed; every prior alert ID/source ID/batch key and source hash preserved; **108** snapshot hashes/official hostnames checked; **6,923** active alerts remain |
| 22 | Launch/source checks | macOS launcher syntax, Python compilation and Git whitespace checks passed |
| 23 | Hosted build and native XCTest | [Both jobs passed for `691e3da`](https://github.com/Suraj-B12/StripCheck/actions/runs/40449407179): nine XCTest cases, 14 Swift executable checks and the full unsigned iOS simulator build; Linux Python suite passed 182 tests and skipped two Apple Vision tests covered by the 184-test local macOS run |

The web first-load bundle was approximately 280.79 KB before review. Secondary pages now load on demand, completed streamed checks avoid a redundant result request, and search no longer refreshes database-wide statistics on each keystroke. Indexed SQL retrieves bounded candidate rows. Image processing shares decoded images, bounds worker time and downsamples native previews off the main actor.

Reproduce the timing measurements with `python scripts/benchmark_api.py` and `python scripts/benchmark_runtime.py`. These use isolated synthetic databases. Timings are local measurements, not a production capacity or medicine-classification accuracy claim.

## Packaging and Git checks

The clean archive passed its SHA-256 manifest/integrity check and an extracted-copy smoke test: empty database, all five website routes, every generated asset, no-data abstention and all eleven synthetic workflows. Git's staged whitespace and release-content scans passed before the implementation commit. No source snapshots, uploaded photos, databases, installed dependencies or build output are committed.

## Release boundaries

The local website is served at `http://127.0.0.1:8765`. Phone LAN access is not enabled. The existing full historical index stays local; a fresh clone must fetch its own official records.

The local Mac has only Command Line Tools. Hosted verification completed the full simulator SDK build with Xcode 16.4/iOS 18.5 and nine XCTest cases; the compiler emitted an App Intents metadata notice because the app does not depend on that framework. Simulator interaction, physical camera/Local Network prompts, device testing, VoiceOver, signing and App Store publication still require release validation. Remaining research/model/evaluation features are documented in the root README.

No finite test suite proves the absence of every bug. The reported checks cover the identified failure paths and preserve the distinction between software verification and the original research validation.

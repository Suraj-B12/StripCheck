# Handoff log

*Newest entry first. Add an entry for every push that finishes a module or milestone, stops mid-way, needs a decision or reports a blocker. Never edit the other side's entries; reply with a new entry.*

**Entry format**
```
## YYYY-MM-DD · <Builder | Integrator> · <milestone or topic> · <built | done | stopped | blocked | question | info>
- Changed: <modules and files>
- Ran: <exact commands and results, e.g. `python -m pytest -q` -> 41 passed, 3 deselected>
- Not verified: <what you could not check and why>
- Notes: <deviations (with decisions.md id), surprises, choices made where the spec was silent>
- ACTION (<owner>): <what the other side or a human must do>
- Next: <what comes next>
```

---

## 2026-10-27 · Builder · Efficiency and resilience review · built

- User authorization: publish the finished application to the original `main` after at least ten review checks. D19 records the updated publication scope. Write permission was verified before preparing the push.
- Changed: indexed bounded candidate retrieval; closed SQLite transactions, per-app DB scope and source-schema v3 migration preserving IDs; atomic source imports and parser v2.4 descriptive encoding repair; shared image decoding and bounded workers; saved-pack deduplication and delete/recheck races; browser timeouts, cancellation, stale-response guards, optional storage and component regression tests; lazy secondary pages; native redirect/cancellation/Keychain/image defenses; pinned GitHub CI and repeatable benchmarks/package script.
- Ran: full isolated `.venv/bin/python -m pytest -q` with native recognition access → **184 passed**, no skips, one upstream Starlette/httpx deprecation warning. `cli.py selftest` → **11/11**. Web tests → **39 passed**; TypeScript/production build passed; lint → **0 warnings**. npm audit → **0 known vulnerabilities**; pip check → no broken requirements.
- Ran: native `StripCheckVerify` → **14 compiled checks passed** plus live URLSession check/confirmation/resume/cabinet/activity/alerts against the restarted localhost server. SwiftUI syntax, project, Info.plist and privacy manifest validations passed; the partial local Apple toolchain emits linker search-path warnings but builds the API verification executable successfully.
- Measured: synthetic 20,000-row batch-search HTTP median **137.421 ms before**, **2.911–3.728 ms after**; no schema writes for repeated reads. Initial web JavaScript **280.79 KB → 264.33 KB**. These are local synthetic timings, not clinical accuracy or production capacity measurements.
- Data: backed up the local DB, refreshed stored snapshots offline, confirmed integrity/foreign keys, all prior alert/source identities and hashes unchanged, and verified **108** archived snapshot hashes/official hostnames. **6,923** active alerts remain. No raw source data is part of the Git update.
- Packaging: rebuilt source-plus-web archive, verified its manifest and extraction; clean-copy startup, five website routes, all assets, no-data handling and eleven isolated demos passed.
- Local hosting: **http://127.0.0.1:8765** is running the reviewed build. LAN remains disabled.
- Release validation: more than twenty checked areas are recorded in `docs/RELEASE_CHECKS.md`. Full Xcode SDK/XCTest validation is configured in GitHub Actions and must be reported from its actual run. Physical device/camera/Local Network prompts, VoiceOver, signing and remaining research features remain unverified.
- Publication: source-only commits will be pushed to `main` after the final staged-file audit and required pull/retest. Hosted CI results and final commit are reported with the delivery.

---

## 2026-10-27 · Builder · Packaged local delivery · built

- Delivered: `../StripCheck-Web-iOS.zip` contains the complete repository source, generated Xcode project, reproducibility files, screenshots and prebuilt `web/dist` website. It excludes Git internals, installed dependencies, native build caches, credentials, local alert snapshots, databases, uploaded photos and check logs. A SHA-256 file manifest is included in the archive.
- Final browser pass: date disagreement correctly produced an incomplete result, with both dates shown; the page returned to an empty new check. The inspected browser console contained no errors. `docs/img/website-preview.png` and `docs/img/website-check.png` show the actual running website.
- Final web checks: production build passed, **22 tests passed**, lint produced **0 warnings**. Backend **88 tests**, **11 synthetic diagnostic cases**, and **8 compiled Swift checks** plus live API integration passed as recorded below.
- Packaging verification: archive integrity, file hashes, exclusion rules, required app files and an extracted fresh-data API/static-site smoke check were verified before delivery.
- Remaining release work: full iOS SDK build and physical/simulator testing; signing and distribution; the outstanding research extensions documented in README. No production deployment or App Store release is claimed.

---

## 2026-10-27 · Builder · Local application implementation · built

This entry records the verified local website/API and native-client source delivery. It does not mark the original research milestones complete or claim a full iOS build.

- Changed: `core/` data, perception, matching, bounded investigation/verifier, persistence, traces, diagnostics and cabinet recheck modules; `server/` FastAPI routes and streaming; `cli.py`; the React/TypeScript website under `web/`; tests; runtime dependencies; `ios/` SwiftUI client, Xcode project, standalone API package and verification executable; macOS launchers, Windows launcher and README setup/deviations. Local runtime data and build output remain outside Git. Integrator-owned paper and research files were not edited.
- Ran: `.venv/bin/python -m pytest -q` → **88 passed**, with one upstream Starlette TestClient/httpx deprecation warning. The data/perception subset includes actual local Apple Vision extraction from synthetic images. `.venv/bin/python cli.py selftest` → **11/11 synthetic scenarios passed**.
- Ran: `npm --prefix web test` → **22 passed**, including streaming and theme-contrast checks; `npm --prefix web run build` → passed, approximately **281 KB JS / 41 KB CSS**; `npm --prefix web run lint` → **0 warnings**.
- Ran: native `StripCheckVerify` → **8 compiled contract checks passed**. A live URLSession round-trip against the local API passed check creation, batch confirmation/resume, verdict retrieval and temporary cabinet save/read/delete. SwiftUI syntax and project/plist validation passed. These results exercise the native API client; they do not substitute for an iOS simulator/device build.
- Browser evidence: the in-app browser exercised confirmation, result rendering, cabinet save, real alert search and diagnostics **11/11**; responsive layouts were reviewed at **319 px and 770 px**. Final passes also exercised no-match, batch collision, missing-product, ambiguous-character and mismatched-date outcomes. Screenshots are saved in `docs/img/`; no broader browser/device certification is claimed.
- Data: public CDSCO history was fetched with verified HTTPS, at least 1.5 seconds between requests, and bounded retries. The final local index contains **6,923 active alerts from 108 snapshots across 93 months, January 2019–September 2026**, with **72 quarantined source rows**. Every archived snapshot's SHA-256 and official source hostname was checked; zero provenance problems or synthetic live alerts were found. A repeated offline import adds **0** rows. Ten identity round-trips using stored real source values matched their expected NSQ/spurious outcomes; this validates retrieval wiring, not clinical accuracy.
- Data review fixes: preserve two-character batch codes with a caution flag; recognize whole-cell date-shaped batch errors without rejecting date-like substrings inside valid identifiers; quarantine ambiguous shorthand such as a shared prefix with `A&B` rather than inventing expanded batch numbers. Retain source bytes, rejected rows and removed revisions; parser-version tracking allows improved validation of cached snapshots. Missing official metadata produces a `Stored ... snapshot` title rather than an invented regulator attribution.
- Runtime: the current server is **http://127.0.0.1:8765**, localhost only. To restart that preview after stopping it, use `.venv/bin/python cli.py serve --port 8765`. Standard launchers use port 8000 by default; the macOS launchers accept `STRIPCHECK_PORT`, and the Windows launcher accepts `-Port`.
- Not verified: full Xcode/iOS SDK compilation, simulator/device installation, physical camera permission flows, VoiceOver interaction and signing. Only Command Line Tools are installed; the package's compiled verification executable passed, while full iOS/XCTest execution requires Xcode. Windows launcher execution and a physical-phone LAN connection have not been exercised.
- Notes: D16–D18 record the requested visual direction and local delivery scope. The runtime uses deterministic bounded state transitions and SQLite documents; it does not claim the research LangGraph/Phoenix architecture, measured model/calibration performance, the full M7 evaluation, or M9 extras such as reviewed regional translations and additional ingestion interfaces. Official portal JSON is the supported end-to-end data route. Synthetic diagnostics are software regression checks, not medicine-classification accuracy measurements.
- Delivery: a source-plus-`web/dist` archive is recorded in the final packaging entry, excluding data, credentials and installed dependencies. No GitHub push, public deployment, account/signing operation or App Store publication has occurred.
- ACTION (Integrator or authorized device owner): use full Xcode/iOS SDK to build and test the native client on simulator/device, then verify camera, Local Network, VoiceOver and signing flows. Continue the outstanding research work only with real measurements and reviewed translations.
- Next: complete the full Xcode/device release validation and the documented research extensions before claiming those milestones.

Automatic approval review rejected the attempted LAN launch because exposing local photos and checks on other network interfaces was not authorized. **No LAN server was started.** The phone launcher and pairing implementation are provided, but this handoff does not claim a tested physical-phone connection.

---

## 2026-10-27 · Integrator · Design phase and repository setup · info
- Changed: first push of the repository. Specs v1.1 (frozen) and v2; `CLAUDE.md`, `AGENTS.md`; `docs/COLLABORATION.md`, `docs/BUILD_GUIDE.md`, `docs/BUILD_STATUS.md`, `docs/decisions.md`; UI direction and clickable prototype (`docs/design/`); verified spikes (`docs/spikes/`); literature survey (`research_notes/`, `reports/`); paper draft (`paper/`); external-survey brief (`docs/prompts/`); proposed `requirements.txt`, `requirements-dev.txt`, `.env.example`.
- Ran: `docs/spikes/v2_matching`: `python -m pytest -q` -> 12 passed. Paper: `latexmk` -> 9 pages, 0 undefined references. BibTeX `\nocite{*}` over all 338 entries -> 0 warnings, 0 errors.
- Not verified: the `requirements.txt` pins were checked against PyPI metadata only, not resolved by pip (M0 step 1 is `pip install --dry-run -r requirements.txt`). No application code exists yet.
- Notes: CDSCO data is not in the repository (copyright policy); fetch it with `docs/BUILD_GUIDE.md` §4 when M1 needs it, always with `--no-stats`.
- ACTION (Builder): start M0 with the first-session kickoff prompt in `docs/BUILD_GUIDE.md` §6.
- ACTION (Integrator): decide the Ollama upgrade (0.17.7 -> 0.40.x), the regional language besides Hindi and its reviewer, and the team names for the paper; record them in `docs/decisions.md`.
- Next: M0 (Builder).

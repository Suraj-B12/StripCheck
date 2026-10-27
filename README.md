# StripCheck

## Public presentation

A GitHub Pages build is provided for sharing the interface and eleven fictional guided examples. It does not check real medicines or upload photos. [Deployment and preview instructions](docs/GITHUB_PAGES.md) explain the one-time Pages setting and public-site boundaries; the local application below remains the real checking workflow.

## Reviewed build

The efficiency and crash review passed **184 Python tests, 43 web tests, 14 compiled Swift checks** and all **11 synthetic scenarios**. See [the verification record](docs/RELEASE_CHECKS.md) for more than twenty checked areas, measurements and release limits. GitHub Actions checks the Python API, website and unsigned iOS simulator build on pushes to `main`.

## Run the local app

The repository now includes a working React website and local Python API: photo and typed-batch checks, human confirmation, cited alert records, a searchable alert library, saved packs, rechecks, local history, diagnostic demos and phone pairing. The interface uses large system typography and restrained glass surfaces. **Demo records are explicitly synthetic and are never added to the live alert index.**

On this configured Mac, double-click **`Start StripCheck.command`** to open the website. Keep its Terminal window open; press **Control-C** to stop. To use a phone on the same trusted Wi-Fi, stop the desktop server and open **`Start for phone.command`**. That launcher creates a temporary pairing token; use the pairing screen's QR code or link on the phone.

### First setup on a fresh clone

Prerequisites: **Python 3.12 or later** and **Node.js 22.12 or later**. This local build has also been exercised on Python 3.14. No account, API key or downloaded language model is required.

macOS / Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
npm --prefix web ci
npm --prefix web run build
python cli.py sync --full
python cli.py serve
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
npm.cmd --prefix web ci
npm.cmd --prefix web run build
.\.venv\Scripts\python.exe cli.py sync --full
.\.venv\Scripts\python.exe cli.py serve
```

Open **http://127.0.0.1:8000**. For later Windows launches, run `./start-stripcheck.ps1`; add `-Lan` for token-protected phone pairing. Use `python cli.py serve --port 8001` if another app uses port 8000. The macOS launchers also accept the `STRIPCHECK_PORT` environment variable.

### Native iOS app

Open [`ios/StripCheck.xcodeproj`](ios/StripCheck.xcodeproj) in full Xcode, choose the StripCheck scheme and an iPhone simulator, and run. The native SwiftUI client connects to the same running local API. Follow [`ios/README.md`](ios/README.md) for server address, device signing and pairing setup.

The compiled Swift API verification and live server round-trips pass. [GitHub verification](https://github.com/Suraj-B12/StripCheck/actions/runs/40449407179) also passed all nine XCTest cases and built the complete application for the iOS simulator with Xcode 16.4 and the iOS 18.5 SDK. Simulator interaction, physical camera, Local Network permission, VoiceOver, signing and App Store release checks remain required.

### Reproduce the verified dependencies

`web/package-lock.json` pins the web dependency graph. `requirements.lock.txt` records the Python versions exercised on this Mac; apply it with `pip install -r requirements.txt -r requirements-dev.txt -c requirements.lock.txt`. Other platforms or Python versions may require a separately resolved lock.

### Data and image reading

- `python cli.py sync --full` downloads all published months discovered from the official CDSCO portal. The first historical import can take several minutes because requests are spaced at least 1.5 seconds apart. `python cli.py sync` refreshes the newest three published months. Both keep exact source bytes, checksums and links.
- `python cli.py sync --offline` rebuilds from stored snapshots without a network connection. Repeating an unchanged import adds no duplicate rows. Rejected source rows remain visible in quarantine; the application reports the loaded coverage.
- Photo reading on macOS uses **Apple Vision locally**. JPEG, PNG, WebP and HEIC are supported when the installed Pillow plugins can decode them. Existing Tesseract or bundled RapidOCR readers can be used on other platforms. If no reader is available, enter the printed fields; a failed read never creates invented pack details. Run `python cli.py doctor` to inspect installed capabilities.
- An alarm requires the printed batch to be confirmed. A missing match describes only the lists loaded on this computer. Show concerning or incomplete results, together with the pack, to a pharmacist.
- Photos, snapshots, SQLite data and logs stay in ignored `data/` and `runs/` directories. Source material and pack photos are not included in Git. To choose other local storage, set `STRIPCHECK_DATA_DIR`, `STRIPCHECK_DB_PATH` and optionally `STRIPCHECK_RUNS_DIR` before starting the server.

### Development and checks

```sh
python -m pytest -q
python cli.py selftest
python cli.py eval --quick
npm --prefix web run build
```

For live web development, run `python cli.py serve` and `npm --prefix web run dev` in separate terminals. API documentation is available at `/api/docs` on the local server. The original project background and research plan follow below; current implementation boundaries are listed under **Deviations**.

---

**Is this exact medicine pack from a batch that India's drug regulator has flagged?**

StripCheck is an offline agent for checking a photographed medicine strip or carton against the monthly lists of drug samples that CDSCO (Central Drugs Standard Control Organisation) declares Not of Standard Quality (NSQ) or spurious. It reads the pack (QR code, OCR, optionally a small local vision model), searches the alert index while allowing for the characters OCR confuses (B/3/8, 0/O, 1/7...), corroborates product, brand, dates and maker the way record linkage does, asks the person when a character is in doubt or before any alarm, and passes every draft verdict through a rule-based verifier that can abstain.

Verdicts: **FLAGGED** (on an NSQ list) · **SUSPECTED_FAKE** (listed as purportedly spurious) · **NOT_LISTED** (no match on the lists loaded; this does not certify the medicine) · **CANT_VERIFY** (the agent abstains). Matched alerts cite their source records. A no-match result states the loaded coverage; an incomplete check explains the missing evidence. Results direct the person to a pharmacist.

> Advisory only, not medical advice. StripCheck is a student project (Agentic AI, course 26CD7PEAAI) and not a CDSCO service. It never says a medicine is safe or genuine and never tells anyone to stop a medicine.

## Status

| Phase | State |
|---|---|
| Design, data discovery, literature survey, paper draft | done (Oct 2026) |
| Local website, API and deterministic batch-check workflow | implemented; see current verification evidence in `docs/BUILD_STATUS.md` |
| Evaluation, extras, paper results (M7 to M10) | later |

## Working on this repository

Two machines build StripCheck on one `main` branch. **Read these before changing anything:**

1. [`docs/COLLABORATION.md`](docs/COLLABORATION.md): roles, git protocol, claiming work, ownership, pre-push checklist.
2. [`docs/BUILD_GUIDE.md`](docs/BUILD_GUIDE.md): setup, getting the data, per-milestone build plan, kickoff prompts for coding agents.
3. [`docs/BUILD_STATUS.md`](docs/BUILD_STATUS.md) and [`docs/HANDOFF.md`](docs/HANDOFF.md): current state and messages.
4. [`CLAUDE.md`](CLAUDE.md) / [`AGENTS.md`](AGENTS.md): conventions for AI coding agents.

## Repository map

| Path | What it is |
|---|---|
| `StripCheck_Build_Spec_v2.md` | The build specification (authoritative): data, architecture, agents, API, UI, evaluation, milestones |
| `StripCheck_Build_Spec.md` | Spec v1.1 (frozen): verified reference code and patterns in Appendices A to C |
| `docs/design/` | UI design system (`ui_direction.md`) and a clickable prototype of the Check screen (`prototype/index.html`) |
| `docs/spikes/` | Verified reference code (matching amendments with tests) and the data snapshot/analysis scripts |
| `docs/decisions.md` | Decision log and spec deviations |
| `docs/research_log.md` | History of the design phase, research runs and how to resume them |
| `research_notes/`, `reports/` | Literature survey (12 themes, 350 verified references) and engineering scans |
| `paper/` | IEEE-format research paper (LaTeX) with generated numbers |
| `docs/prompts/` | Brief for running the literature survey on another research model, with an intake checker |
| `core/`, `server/`, `web/`, `tests/`, `cli.py` | Application code (created from M0 onward) |

## Original research environment

```
conda create -n stripcheck python=3.12 -y && conda activate stripcheck
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
python cli.py doctor
python -m pytest -q
```
Data: CDSCO alert data is not stored in this repository. Each machine fetches it (see `docs/BUILD_GUIDE.md` §4).

## Data and acknowledgements

Alert data: Central Drugs Standard Control Organisation, Government of India ([public NSQ portal](https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug)). The data is fetched and kept locally, cited on matching verdicts, and only derived statistics are published. The current macOS OCR reader is Apple Vision; existing Tesseract and bundled RapidOCR readers are optional fallbacks. The research design additionally describes LangGraph, Ollama and Phoenix; see the implementation boundaries below.

## Deviations

Deviations of the code from `StripCheck_Build_Spec_v2.md` are listed here, each with its `docs/decisions.md` id.

- **D16:** The requested large-type, Apple-inspired responsive interface supersedes the earlier visual prototype for this local release. The original research design remains available for comparison. The native iOS client is maintained separately under `ios/`.
- **D17/D19:** The initial delivery was local. The user subsequently authorized source publication to the original `main` branch after review. External deployment, App Store publication and signing are separate. Integrator-owned paper and research files remain unchanged.
- **D18:** The runnable engine uses explicit, bounded deterministic transitions and durable SQLite documents. It does not claim LangGraph checkpointing, production Phoenix integration, or measured research-model performance. Optional local Ollama structured-call helpers fail back without blocking rules-mode checks. No VLM, language model or OCR model is downloaded automatically.
- **D18:** On macOS, bounded Apple Vision OCR and barcode reading provide real image extraction. Tesseract and already-installed RapidOCR weights are fallbacks. Character crops use proportional character boundaries; they are visual evidence aids, not calibrated segmentation measurements. Local verification on macOS must run with access to the OS recognition service.
- **D18:** The official JSON portal is the supported end-to-end ingestion route. Grounded PDF table/text extraction helpers exist, but a complete PDF repair pipeline, state-source feeds and CSV/HTML/XLSX schema repair remain research extensions. A normal refresh covers the most recent three published months; `--full` imports historical coverage. On managed Macs, the native HTTPS client uses the system certificate store with verification enabled.
- **D18:** The built-in diagnostic cases are eleven authored synthetic scenarios with expected answers. Their results are software checks, not clinical accuracy, a calibrated medicine classifier, or the preregistered M7 research evaluation. Regional-language review, optional model benchmarking and paper results remain Integrator work.
- **D20:** The public GitHub Pages build replays authored synthetic examples because Pages cannot host the Python API. It uses separate build output and hash navigation and publishes no local runtime data.
- **D21:** Manual editing after a demo clears inherited fictional fields. An exact batch with missing or conflicting supporting details stays incomplete and asks for printed evidence; independent product/brand collisions still reject, and acceptance thresholds are unchanged.

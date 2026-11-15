# StripCheck

## Public presentation

[Open the public demo](https://vsxye.github.io/StripCheck/) to explore the interface and eleven fictional guided examples. It does not check real medicines or upload photos; the local application below provides the real checking workflow. The showcase is hosted in a separate artifact repository. See [hosting and preview instructions](docs/GITHUB_PAGES.md).

## Reviewed build

The efficiency and crash review passed **184 Python tests, 43 web tests, 14 compiled Swift checks** and all **11 synthetic scenarios**. See [the verification record](docs/RELEASE_CHECKS.md) for more than twenty checked areas, measurements and release limits. GitHub Actions checks the Python API, website and unsigned iOS simulator build on pushes to `main`.

## Run the local app

The repository now includes a working React website and local Python API: photo and typed-batch checks, human confirmation, cited alert records, a searchable alert library, saved packs, rechecks, local history, diagnostic demos and phone pairing. The interface uses large system typography and restrained glass surfaces. **Demo records are explicitly synthetic and are never added to the live alert index.**

On this configured Mac, double-click **`Start StripCheck.command`** to open the website. Keep its Terminal window open; press **Control-C** to stop. To use a phone on the same trusted Wi-Fi, stop the desktop server and open **`Start for phone.command`**. That launcher creates a temporary pairing token; use the pairing screen's QR code or link on the phone.

### First setup on a fresh clone

Prerequisites: **Python 3.12 or later** and **Node.js 22.12 or later**. This local build has also been exercised on Python 3.14. No account, API key or language model is required for the default rules mode. The local models below are optional extras.

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

### Agent mode, vision model and monitor (optional, local)

These need [Ollama](https://ollama.com) running on the same computer. Without it everything still works in the default rules mode.

```powershell
ollama pull qwen2.5:3b      # the planner model (agent and hybrid modes)
ollama pull qwen2.5vl:3b    # the vision model (reads a batch the OCR cannot read)
python cli.py check data/samples/pack_types/misread_FLAGGED.png --planner agent
python cli.py serve
```

- **Agent mode.** In the web app, choose **Agent** in the planner control (it is greyed out until Ollama and the model are found). From the command line use `--planner agent`, or set `STRIPCHECK_PLANNER=agent` for every check. The local model picks the next tool at every step; the rules decide which tools it may pick, so a required search or the confirmation question can never be skipped. If the model is off, slow or answers badly, the rule choice is used and the step says `rules(fallback)`. The default stays `rules`.
- **Vision model.** `qwen2.5vl:3b` is the default (`STRIPCHECK_VLM_MODEL`; `STRIPCHECK_VLM_TIMEOUT`, default 30 s). It is used only when OCR and QR cannot read the batch, and only for photo checks. What it reads is shown to the person as a yes/no question and is never trusted alone. On a laptop without a GPU it takes 2 to 6 seconds per crop, so run one check before a demo to load it.
- **Monitor.** `python cli.py serve` also starts a background monitor (every 6 hours by default, `STRIPCHECK_MONITOR_HOURS`). It decides whether a sync is due, checks the connection, syncs, re-checks saved packs and notifies when a status changes. Failures back off up to 24 hours and never affect a check. Turn it off with `STRIPCHECK_MONITOR=0`. Run one cycle with `python cli.py monitor --once`, read its state at `GET /api/monitor`, and start a cycle with `POST /api/monitor/run`.

### Native iOS app

Open [`ios/StripCheck.xcodeproj`](ios/StripCheck.xcodeproj) in full Xcode, choose the StripCheck scheme and an iPhone simulator, and run. The native SwiftUI client connects to the same running local API. Follow [`ios/README.md`](ios/README.md) for server address, device signing and pairing setup.

The compiled Swift API verification and live server round-trips pass. [GitHub verification](https://github.com/Suraj-B12/StripCheck/actions/runs/40449407179) also passed all nine XCTest cases and built the complete application for the iOS simulator with Xcode 16.4 and the iOS 18.5 SDK. Simulator interaction, physical camera, Local Network permission, VoiceOver, signing and App Store release checks remain required.

### Reproduce the verified dependencies

`web/package-lock.json` pins the web dependency graph. `requirements.lock.txt` records the Python versions exercised on this Mac; apply it with `pip install -r requirements.txt -r requirements-dev.txt -c requirements.lock.txt`. Other platforms or Python versions may require a separately resolved lock.

### Data and image reading

- `python cli.py sync --full` downloads all published months discovered from the official CDSCO portal. The first historical import can take several minutes because requests are spaced at least 1.5 seconds apart. `python cli.py sync` refreshes the newest three published months. Both keep exact source bytes, checksums and links.
- `python cli.py sync --offline` rebuilds from stored snapshots without a network connection. Repeating an unchanged import adds no duplicate rows. Rejected source rows remain visible in quarantine; the application reports the loaded coverage.
- Photo reading on macOS uses **Apple Vision locally**. JPEG, PNG, WebP and HEIC are supported when the installed Pillow plugins can decode them. On Windows and Linux it uses **RapidOCR 3.10** (PP-OCR weights from the pinned package, ONNX Runtime on CPU, about 0.3 s per image once warm) and **zxing-cpp** for QR codes; both install from `requirements.txt`. If no reader is available, enter the printed fields; a failed read never creates invented pack details. Run `python cli.py doctor` to inspect installed capabilities.
- An alarm requires the printed batch to be confirmed. A missing match describes only the lists loaded on this computer. Show concerning or incomplete results, together with the pack, to a pharmacist.
- Photos, snapshots, SQLite data and logs stay in ignored `data/` and `runs/` directories. Source material and pack photos are not included in Git. To choose other local storage, set `STRIPCHECK_DATA_DIR`, `STRIPCHECK_DB_PATH` and optionally `STRIPCHECK_RUNS_DIR` before starting the server.

### Live phone demo (Cloudflare quick tunnel, Windows)

Step-by-step script for a review: [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md). On Windows, double-click `Start StripCheck Demo.cmd` (it also starts Ollama and loads the model when they are installed).

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-demo-tunnel.ps1
```

The script starts the server on localhost, opens a temporary `trycloudflare.com` tunnel and prints a phone link with a one-time token (`/?k=...`) plus a QR code. Requests without the token get 401. Press Ctrl-C to stop both. Needs `cloudflared` installed; no account is required.

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
| Windows OCR, hybrid planner, Phoenix tracing, tunnel demo | done (Nov 2026) |
| R4 evaluation (seed 7, n=60), report and slides | done; see `docs/results/eval_seed7.md`, `paper/`, `docs/guide/index.html` |
| Agentic upgrade: tool-calling agent, self-check, hand-offs, vision fallback, monitor | built (Nov 2026); 289 Python and 117 web tests pass; four-arm seed-7 evaluation done (D27 to D29) |

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
- **D23:** Windows reads photos with RapidOCR and zxing-cpp; the tunnel demo uses the token gate on localhost (`STRIPCHECK_REQUIRE_TOKEN=1`); the hybrid planner calls the local model at two branch points with a rules fallback; Phoenix export is optional.
- **D24:** The R4 evaluation uses 60 rendered cartons from real alert rows. Misreads are printed on the carton, so OCR noise is simulated, not measured, and no real strip photos are included.
- **D25:** Fixes from the evaluation: full product text kept for grading, R2 aligned with partial-match grading, every look-alike position asked at confirmation. All arms were rerun after the fixes.
- **D26:** The rule planner stays the default. The hybrid planner matched it on all 60 packs but had a much longer tail latency, so it is an option.
- **D27:** A third planner mode, `agent`, lets the local model pick the next tool at every step (a thought, an action and an observation, repeated). The rules list the tools allowed at each step, so the model cannot skip a search or the confirmation question; a bad or late model answer uses the rule choice (`rules(fallback)`). After the verifier rejects a draft, one self-check lets the planner revise once. Perception, investigator, verifier and supervisor are explicit agents that pass hand-off messages. Bounds are unchanged.
- **D28:** `core/monitor.py` is an autonomous monitor started by `cli.py serve` (every 6 hours; `STRIPCHECK_MONITOR=0` turns it off). It decides if a sync is due, syncs with the existing spacing and TLS rules, re-checks saved packs and notifies on changes. `GET /api/monitor`, `POST /api/monitor/run`, `cli.py monitor --once`.
- **D29:** When OCR and QR cannot read the batch, the agent may use a local vision model (`qwen2.5vl:3b`). Its reading is shown with the photo crop as a yes/no question; only after "No" is the person asked to type. A vision reading is never gate evidence until the person confirms it. The agent can also ask for one more photo (`request_photo`). On the CPU-only laptop the model takes 2 to 6 seconds per crop, and in a live test it misread one digit with high stated confidence, which the confirmation step and the look-alike search caught.

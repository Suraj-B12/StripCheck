# StripCheck

**Is this exact medicine pack from a batch that India's drug regulator has flagged?**

StripCheck is an offline agent for checking a photographed medicine strip or carton against the monthly lists of drug samples that CDSCO (Central Drugs Standard Control Organisation) declares Not of Standard Quality (NSQ) or spurious. It reads the pack (QR code, OCR, optionally a small local vision model), searches the alert index while allowing for the characters OCR confuses (B/3/8, 0/O, 1/7...), corroborates product, brand, dates and maker the way record linkage does, asks the person when a character is in doubt or before any alarm, and passes every draft verdict through a rule-based verifier that can abstain.

Verdicts: **FLAGGED** (on an NSQ list) · **SUSPECTED_FAKE** (listed as purportedly spurious) · **NOT_LISTED** (no match on the lists loaded; this does not certify the medicine) · **CANT_VERIFY** (the agent abstains). Every verdict cites its source and tells the person to show the pack to a pharmacist.

> Advisory only, not medical advice. StripCheck is a student project (Agentic AI, course 26CD7PEAAI) and not a CDSCO service. It never says a medicine is safe or genuine and never tells anyone to stop a medicine.

## Status

| Phase | State |
|---|---|
| Design, data discovery, literature survey, paper draft | done (Oct 2026) |
| Implementation M0 to M6 (the demo) | next; see `docs/BUILD_STATUS.md` |
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

## Quick start (after M0)

```
conda create -n stripcheck python=3.12 -y && conda activate stripcheck
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
python cli.py doctor
python -m pytest -q
```
Data: CDSCO alert data is not stored in this repository. Each machine fetches it (see `docs/BUILD_GUIDE.md` §4).

## Data and acknowledgements

Alert data: Central Drugs Standard Control Organisation, Government of India (NSQ alerts, https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug). The data is fetched and kept locally, cited on every verdict, and only derived statistics are published. OCR models: PaddleOCR PP-OCR via RapidOCR. Agents: LangGraph. Local models: Ollama (model licences listed in the paper and `docs/decisions.md` once chosen). Tracing: Arize Phoenix / OpenTelemetry.

## Deviations

Deviations of the code from `StripCheck_Build_Spec_v2.md` are listed here, each with its `docs/decisions.md` id.

- (none yet)

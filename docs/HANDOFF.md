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

## 2026-10-27 · Integrator · Design phase and repository setup · info
- Changed: first push of the repository. Specs v1.1 (frozen) and v2; `CLAUDE.md`, `AGENTS.md`; `docs/COLLABORATION.md`, `docs/BUILD_GUIDE.md`, `docs/BUILD_STATUS.md`, `docs/decisions.md`; UI direction and clickable prototype (`docs/design/`); verified spikes (`docs/spikes/`); literature survey (`research_notes/`, `reports/`); paper draft (`paper/`); external-survey brief (`docs/prompts/`); proposed `requirements.txt`, `requirements-dev.txt`, `.env.example`.
- Ran: `docs/spikes/v2_matching`: `python -m pytest -q` -> 12 passed. Paper: `latexmk` -> 9 pages, 0 undefined references. BibTeX `\nocite{*}` over all 338 entries -> 0 warnings, 0 errors.
- Not verified: the `requirements.txt` pins were checked against PyPI metadata only, not resolved by pip (M0 step 1 is `pip install --dry-run -r requirements.txt`). No application code exists yet.
- Notes: CDSCO data is not in the repository (copyright policy); fetch it with `docs/BUILD_GUIDE.md` §4 when M1 needs it, always with `--no-stats`.
- ACTION (Builder): start M0 with the first-session kickoff prompt in `docs/BUILD_GUIDE.md` §6.
- ACTION (Integrator): decide the Ollama upgrade (0.17.7 -> 0.40.x), the regional language besides Hindi and its reviewer, and the team names for the paper; record them in `docs/decisions.md`.
- Next: M0 (Builder).

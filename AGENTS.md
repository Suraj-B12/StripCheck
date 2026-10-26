# AGENTS.md: instructions for AI coding agents working on StripCheck

This repository is built by two machines that share one `main` branch. If you are an AI coding agent (Claude Code, Codex, Cursor, Copilot or any other), these instructions apply to you. Claude Code also loads `CLAUDE.md`, which contains the same rules plus project conventions; read it too.

## Start of every session
1. `git pull --rebase`.
2. Read `CLAUDE.md`, `docs/COLLABORATION.md` (binding rules), `docs/BUILD_GUIDE.md` (procedures), `docs/BUILD_STATUS.md` (who is doing what) and the newest entries of `docs/HANDOFF.md` (messages, ACTION items, blockers).
3. Identify your role: on the collaborator's PC you are the **Builder**; on Suraj's laptop you are the **Integrator** (`docs/COLLABORATION.md` §1). If unsure, ask the human.
4. Claim exactly one milestone or task in `docs/BUILD_STATUS.md`; commit and push the claim before writing code.

## While working
- Implement exactly what `StripCheck_Build_Spec_v2.md` says (milestones in §17; the sections each milestone references). The UI follows `docs/design/ui_direction.md` and `docs/design/prototype/index.html`. `StripCheck_Build_Spec.md` (v1.1) is frozen verified reference code; v2 overrides it where they differ.
- Python: minimal, flat, procedural; plain functions; `TypedDict`/Pydantic only for data shapes; one module per concern; `pathlib`; UTF-8 for our files, latin-1 for CDSCO portal JSON; ASCII console output.
- Everything must run with Ollama off, Phoenix off and no internet. Every model, network and tracing call has a timeout and a fallback. Bound every loop.
- Tests: `python -m pytest -q` (Ollama tests marked `llm`, internet tests marked `net`, both skipped by default). From M6 also `npm --prefix web test` and `npm --prefix web run build`.
- Save incrementally: create files early; after each module whose tests pass, commit (`<scope>: <what> (<test summary>)`), `git pull --rebase`, re-run the tests, `git push`.

## Hard rules
- Only `main`. Never force-push, amend or rebase pushed commits, delete others' work, or create branches.
- Never commit `data/`, `runs/`, databases, `.env`, `node_modules/`, `web/dist/`, `paper/build/`, photos of real medicines, or files over 5 MB.
- Safety language: user-facing text never says "safe", "genuine", "authentic", "fake medicine" or "stop taking"; verdict text only from `core/templates.py`; NOT_LISTED is never green; flag only the listed batch, never a brand.
- No invented data: alert rows come from stored CDSCO snapshots; pack fields come from QR/OCR/VLM text or the user. Test fixtures are synthetic and marked as such.
- Never disable TLS verification; portal requests at least 1.5 s apart; no paid or cloud APIs.
- Do not edit Integrator-owned paths (`paper/`, `research_notes/`, `reports/`, `docs/research_log.md`, `docs/workflows/`, `docs/prompts/`, `docs/spikes/`) unless you are the Integrator.
- Spec changes require a `docs/decisions.md` entry in the same commit.
- Ask the human before installing system software, downloading large files (for example Ollama models), or using any account or credential.

## End of a milestone or session
- Update `docs/BUILD_STATUS.md` (state, date, test summary).
- Append a `docs/HANDOFF.md` entry (format in that file): what changed, commands run with results, what is unverified, ACTION items.
- Commit and push. Report to the human and stop unless told to continue.

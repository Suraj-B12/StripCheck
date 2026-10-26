# Collaboration rules (two machines, one `main` branch)

*Version 1.0 · 27 October 2026. These rules bind every person and every AI agent that commits to this repository. If a rule and a convenience disagree, follow the rule and write down the problem in `docs/HANDOFF.md`.*

Repository: https://github.com/Suraj-B12/StripCheck

---

## 1. Roles

| Role | Who | Machine | Does | Does not |
|---|---|---|---|---|
| **Builder** | the collaborator (and his coding agent) | his PC (no GPU, Ollama or CDSCO data assumed) | Implements milestones M0 to M6 (and later ones when asked) exactly as `StripCheck_Build_Spec_v2.md` §17 describes; writes tests; makes every test that does not need Ollama or the internet pass; pushes to `main`. | Change the specs silently; commit data; tune evaluation thresholds; edit the paper. |
| **Integrator** | Suraj, with Claude Code on the main laptop | Windows laptop with RTX 4050 GPU, Ollama models and the full CDSCO data | Pulls the Builder's work, runs the parts that need Ollama, the GPU and real data (LLM tests, model benchmark, evaluation, demo), fixes integration issues, runs the backend agents, updates the paper and the research log, and pushes adjustments. | Rewrite the Builder's work without leaving a note; push untested changes. |

Both roles may fix bugs anywhere. Ownership (§5) decides who edits a file by default, not who is allowed to.

---

## 2. One branch: `main`

- All work goes to `main`. There are no feature branches and no pull requests. History is append-only.
- **Never** run `git push --force`, `git push -f`, `git rebase` on commits that are already pushed, `git reset --hard origin/...` over someone else's work, or `git commit --amend` on a pushed commit.
- `git pull --rebase` is the only way to bring in remote work before you push (it rebases **your unpushed** commits on top of `main`).
- Tag finished milestones: `git tag m0-done && git push origin m0-done` (Integrator tags after confirming; the Builder may tag his side as `m0-built`).

### 2.1 The loop for every work session

```
git pull --rebase                    # 1. start from the latest main
# 2. read docs/BUILD_STATUS.md and docs/HANDOFF.md (newest entry first)
# 3. claim the milestone or task in docs/BUILD_STATUS.md, commit "status: claim M1 (builder)", push at once
# 4. work in small units; after each module whose tests pass:
python -m pytest -q
git add <the files of that module>
git commit -m "M1: portal adapter and fixtures (pytest: 41 passed)"
# 5. push at least after every finished module and before you stop for the day:
git pull --rebase && python -m pytest -q && git push
# 6. when the milestone is done: update docs/BUILD_STATUS.md, append to docs/HANDOFF.md, commit, push
```

Pushing small and often is part of the safety model: a session (human or agent) can end at any moment, and unpushed work is invisible to the other machine.

---

## 3. Claiming work (`docs/BUILD_STATUS.md`)

- Before starting a milestone or task, set its row to `in progress`, with your role and the date, commit only that change (`status: claim M2 (builder)`) and push immediately. Pull first; if someone else claimed it, pick another.
- One milestone in progress per role at a time. Milestones go in order (M0 → M6 first); a later milestone may start only when the earlier one is at least `built`.
- States: `not started` → `in progress` → `built` (Builder: all tests that need no Ollama/internet pass, the offline parts of "Done when" pass) → `done` (Integrator: the full "Done when" command passes on the laptop, including LLM parts) → tagged.
- If you stop in the middle, leave the row `in progress`, add a "Stopped at" note in `docs/HANDOFF.md` with what is finished and what is next, and push.

---

## 4. Commits

- **Message format:** `<scope>: <what changed> (<test summary>)`. Scopes: `M0`...`M10` for milestone work, `fix`, `test`, `docs`, `spec`, `status`, `paper`, `data-tools`, `chore`. Examples: `M3: verifier rules R1-R10 (pytest: 88 passed)`, `fix: latin-1 decoding of portal JSON (pytest: 52 passed)`.
- One commit per finished module or fix. A commit must leave `python -m pytest -q` green on the committer's machine. Work in progress that is not green stays uncommitted or goes to a clearly marked `wip:` commit that is followed by a fix before any push (never push a red `main`).
- Commits written by an AI agent end with a trailer naming the agent, for example `Co-Authored-By: Claude <noreply@anthropic.com>` or the equivalent for the agent used.
- Stage files by name; review `git status` before every commit. Never `git add` anything under `data/`, `runs/`, `.env`, `node_modules/`, `web/dist/` or `paper/build/` (they are ignored; do not force-add them).

---

## 5. Who edits what (default ownership)

| Path | Default owner | Rule for the other role |
|---|---|---|
| `core/`, `server/`, `web/`, `cli.py`, `tests/`, `requirements*.txt`, `web/package*.json`, `.env.example`, `pytest.ini`, `README.md` (setup sections) | Builder | Integrator edits for fixes and integration; each edit gets a `docs/HANDOFF.md` line so the Builder pulls knowingly |
| `paper/`, `research_notes/`, `reports/`, `docs/research_log.md`, `docs/workflows/`, `docs/prompts/`, `docs/spikes/` | Integrator | Builder does not edit (read-only reference) |
| `StripCheck_Build_Spec_v2.md`, `docs/design/`, `CLAUDE.md`, `AGENTS.md`, `docs/COLLABORATION.md`, `docs/BUILD_GUIDE.md` | shared | change only with a `spec:` or `docs:` commit **and** an entry in `docs/decisions.md` (what, why, date, who); never silently |
| `docs/BUILD_STATUS.md`, `docs/HANDOFF.md`, `docs/decisions.md` | shared, append-mostly | edit your own rows/entries; append, do not rewrite others' entries |
| `StripCheck_Build_Spec.md` (v1.1) | frozen | never edit; it is the verified reference for Appendices A to C |

**Spec changes.** The spec is the contract. If the code needs to differ from it (a library changed, a better design appears), write the deviation in `docs/decisions.md` and in `README.md` → "Deviations", then change the spec text in the same commit. Implementation details the spec leaves open need no decision entry.

---

## 6. Before every push (checklist)

1. `git pull --rebase` succeeded (resolve conflicts per §7).
2. `python -m pytest -q` is green **after** the pull. From M6 also `npm --prefix web test` and `npm --prefix web run build`.
3. `git status` shows no data, secrets, databases, images of real packs, build output or editor junk.
4. No file over 5 MB is added. Screenshots for docs go in `docs/img/` as compressed PNG or WebP.
5. `docs/BUILD_STATUS.md` reflects reality; a `docs/HANDOFF.md` entry exists for any finished module, milestone, stop or breaking change.
6. Then `git push`. If the push is rejected because `main` moved, go back to step 1. Never force.

---

## 7. Conflicts and a broken `main`

- **During `git pull --rebase`:** open each conflicted file, keep both sides' intent, run the tests, `git add` the file, `git rebase --continue`. If the conflict is in a file the other role owns, prefer their version and re-apply your change on top. If you cannot resolve it with confidence: `git rebase --abort`, then `git pull --no-rebase` (creates a merge commit, which is allowed), resolve there, and describe what you did in `docs/HANDOFF.md`.
- **Generated files** (`package-lock.json`, `paper/generated/*.tex`): take the incoming version, then regenerate (`npm install`, `python cli.py stats`) and commit the result.
- **If `main` is red after a pull** (tests fail): the person who notices fixes forward with a `fix:` commit if the fix is small and obvious; otherwise writes a `BLOCKER` entry in `docs/HANDOFF.md` naming the failing test and the commit, and pushes only that note. Never revert someone else's commit without a HANDOFF entry explaining why; prefer `git revert <sha>` (a new commit) over any history rewrite.

---

## 8. Data, privacy and safety rules (non-negotiable)

- **No CDSCO data in git.** Snapshots, the alert database, props rendered from real rows and evaluation images stay in ignored folders. Each machine fetches its own copy politely (BUILD_GUIDE "Getting the data"). Test fixtures are synthetic (invented product names and batches, marked as such) or a handful of rows at most.
- **Never** disable TLS verification, scrape faster than one request per 1.5 s, or add paid or cloud APIs.
- **Safety language** (spec v1.1 §9.8, v2 §10.9): user-facing text never says "safe", "genuine", "authentic", "fake medicine" or "stop taking"; verdict text comes only from `core/templates.py`; NOT_LISTED is never green. A failing banned-phrase test blocks any push.
- **No secrets.** Nothing in this project needs an API key. `.env` is local; only `.env.example` is committed.
- **Photos of real medicines** taken by the team stay out of git (they can show names and addresses); share them privately if needed.

---

## 9. Machine differences

| Capability | Builder PC | Integrator laptop |
|---|---|---|
| Python 3.12, Node ≥ 22.12, Git | required | yes (Node 24) |
| CDSCO data | fetched locally when needed (M1+) | yes |
| Ollama + models, GPU | optional | yes (RTX 4050, 6 GB) |
| TeX Live | not needed | yes |
| Phoenix | optional | yes (separate venv) |

Code must work on the Builder PC with Ollama absent: the rule planner, OCR, retrieval, grading, verifier, API and UI all run without a language model, and LLM paths fall back (spec v2 §1.3). Tests that need Ollama carry `@pytest.mark.llm`; tests that need the internet carry `@pytest.mark.net`; both are skipped by default and run on the Integrator laptop with `python -m pytest -q -m "llm or net"`.

---

## 10. Communication

- **`docs/HANDOFF.md`** is the message board: newest entry first, one entry per push that finishes something, stops mid-way, needs a decision or reports a blocker. Format in the file.
- **`docs/decisions.md`** records decisions and spec deviations (numbered, dated, never deleted; superseded entries say so).
- **GitHub Issues** may be used for bugs found during integration (label `integration`, `bug`, `question`); link the issue in the HANDOFF entry.
- Anything a person must do by hand (install a model, approve a download, answer a design question) is written as `ACTION (owner): ...` in HANDOFF.

---

## 11. Rules for AI coding agents (both machines)

1. Read `CLAUDE.md` (or `AGENTS.md`), this file, `docs/BUILD_GUIDE.md` and `docs/BUILD_STATUS.md` before doing anything else, then the newest `docs/HANDOFF.md` entries.
2. Work only on the claimed milestone; follow `StripCheck_Build_Spec_v2.md` and `docs/design/ui_direction.md` exactly; where they are silent, choose the simplest option and note it in HANDOFF.
3. Save incrementally: create files early, commit after each module whose tests pass, push after each module, keep a status checklist in `docs/BUILD_STATUS.md`. On start, resume from what is already on disk and in `main`.
4. Run the tests yourself; never report a milestone as built without pasting the passing command output into the HANDOFF entry.
5. Do not install software system-wide, change git configuration, delete files outside the repository, or push anything other than `main`. Ask the human for anything that needs an account, a password, a paid service or a large download.
6. When unsure whether a change alters the spec, stop and write a question in HANDOFF instead of guessing.

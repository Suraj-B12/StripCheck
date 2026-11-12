# Final push (8 to 12 Nov 2026): status checklist

*Resume point if a session ends: read this file first, then `git log`. Every line is updated when its work lands on disk; commits follow each finished workstream.*

Source plan: `C:\Users\suraj\Downloads\StripCheck_Project_Plan.md` (Parts 6 to 8). R1 and R2 are done. Final submission is due Thu 12 Nov 2026: report PDF, slides PDF, repository with README, tag `v1.0`.

## Workstreams

| ID | Workstream | Owner | State | Output |
|---|---|---|---|---|
| A | Windows photo OCR (RapidOCR + zxing on Windows), props render and read correctly | agent A | **done** (11/11 demo packs read correctly, ~0.3 s warm) | `core/pack_tools.py`, `requirements.txt`, tests |
| B | R4 evaluation: golden set from real alerts (seed 1 dev, seed 7 eval), arms baseline / agent_rules / agent_hybrid x HITL oracle / none, metrics and per-scenario tables, `runs/eval_*.md`, `docs/results/` | agent B | **done** (e283407; rerun all arms after investigator fixes) | `core/evaluate.py`, `core/props.py`, `cli.py eval` |
| C | Observability and LLM: optional Phoenix/OpenTelemetry spans, hybrid planner with qwen2.5:3b, feedback-loop prior visible in trace and question | agent C | **done** (fd976f9) | `core/tracing.py`, `core/llm.py` |
| D | LaTeX report (IEEE, 8 to 12 pages) per plan Part 7.7, numbers from generated files | agent D | **done** (3e71c05) | `paper/` |
| E | Visual guide: how StripCheck works, design choices, scraping, parsing, agent thinking, failsafes | agent E | **done** (commit 25e86db; update LLM/eval sections after B,C land) | `docs/guide/index.html` |
| F | Mobile live demo over a Cloudflare quick tunnel | lead | **done** (commit 1563ef6; verified 401 without token, 200 with link, over the public tunnel) | `scripts/start-demo-tunnel.ps1`, README |
| G | Slides (beamer) per plan Part 7.6 | agent D | **done** (3e71c05) | `paper/slides/` |
| H | Full test sweep, malformed-input checks, fresh-clone run on Windows | lead | **done** | test logs |

## Log
- 2026-11-08: plan read; repo surveyed (194 Python, 75 web tests pass on Windows); gaps listed above.
- 2026-11-08: A done (Windows OCR); tunnel gate test fixed; cli check handles EOF on stdin.
- 2026-11-08: E done (docs/guide). Team names sent to D: 1BM23CD008 Aryanraj S Singh, 1BM23CD050 Richik Chaudhuri, 1BM23CD061 Suraj B (lead), 1BM23CD062 Sushanth Deo. No real photos: synthetic packs only.
- RESUME: B (eval), C (tracing/LLM), D (paper+slides) were still running uncommitted; check docs/final/{B,C,D}_status.md, run pytest, commit their files. cli.py EOFError fix is uncommitted (goes with B's cli.py). Then: fix confirmation-position gap in core/investigator.py (ask positions where nearest listed batch differs; see docs/final/E_status.md), update guide LLM/eval sections, fix \Sepackage typo in paper/main.tex if D did not, H sweep, tag v1.0.
- NEXT after C lands: fix investigator brand-line product_text bug + grade()/R2 partial-match disagreement + confirmation-position gap; rerun eval (3 commands in docs/final/B_status.md); rebuild paper; update guide; README Deviations (simulated misreads).
- 2026-11-08 16:30: C committed (fd976f9). Investigator fixes e8d70e4 (D25); eval rerun 6b69280 (oracle hit recall 1.00, all predictions held, adopt). README + D23-D25 13f0828. Batch-text validation 3e1c69f. Selftest 11/11, web build+lint clean, malformed probes OK.
- IN FLIGHT: agent F updating paper/slides/guide for run 2 + run-1 disclosure (docs/final/F_status.md); fresh-clone test in scratchpad/fresh. THEN: commit F, rebuild PDFs, restart tunnel, BUILD_STATUS/HANDOFF/research_log entries, tag v1.0.
- 2026-11-08: H fresh-clone check on Windows (Python 3.12, README steps): pytest 225 passed / 3 skipped, selftest 11/11, web 75 passed + build; RapidOCR and zxing available. (Python 3.10 is unsupported per README: sqlite setlimit needs 3.11+.)
- 2026-11-08 16:45: submission PDFs in docs/submission (3b87ec9); tunnel restarted on final code; tagged v1.0. Contribution table confirmed by the team lead. Nothing remaining.
- 2026-11-12: live thinking + question UX workflow wf_474e3743-e76 (contract docs/final/live_thinking_contract.md; status docs/final/G_*_status.md). Resume: Workflow({scriptPath: <session>/workflows/scripts/live-thinking-and-questions-wf_474e3743-e76.js, resumeFromRunId: 'wf_474e3743-e76'}).
- 2026-11-12: AAT report workflow wf_2f7d1645-32a -> paper/report/ (template: Downloads/AAI_AAT_Report.zip; status paper/report/STATUS.md). Resume: Workflow({scriptPath: <session>/workflows/scripts/aat-report-wf_2f7d1645-32a.js, resumeFromRunId: 'wf_2f7d1645-32a'}). Team No. NOT required: remove the TeamNo line from the title page after the workflow ends (user, 2026-11-12).
- 2026-11-12 SAVE POINT. In flight, uncommitted on disk on purpose (reviewers' failing tests until the fixer runs): live-thinking code in core/llm.py, core/investigator.py, core/templates.py, server/app.py, server/sse.py, web/src/** (Thinking.tsx, Ask.tsx, lib/thinking.ts, lib/ask.ts), tests/test_live_thinking.py + review tests. Resume: re-invoke workflow wf_474e3743-e76 (script path above) with resumeFromRunId; then run pytest + npm test/tsc/lint/build, commit.
- Report draft in paper/report/ (committed as WIP); resume workflow wf_2f7d1645-32a. After it ends: remove the Team No. line from the title page; build; copy PDF to docs/submission/.
- Then: restart site with Ollama (qwen2.5:3b) + tunnel; image prompt is in data/samples/realistic_pack_prompt.md.
- 2026-11-13: live thinking + question UI committed (4e15613), verified over the tunnel and in the browser (thinking streams, question card, answer -> result, no console errors). Ollama started from %LOCALAPPDATA%\Programs\Ollama\ollama serve; model warmed. Report workflow resumed (wjfble803).

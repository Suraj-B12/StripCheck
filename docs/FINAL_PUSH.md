# Final push (8 to 12 Nov 2026): status checklist

*Resume point if a session ends: read this file first, then `git log`. Every line is updated when its work lands on disk; commits follow each finished workstream.*

Source plan: `C:\Users\suraj\Downloads\StripCheck_Project_Plan.md` (Parts 6 to 8). R1 and R2 are done. Final submission is due Thu 12 Nov 2026: report PDF, slides PDF, repository with README, tag `v1.0`.

## Workstreams

| ID | Workstream | Owner | State | Output |
|---|---|---|---|---|
| A | Windows photo OCR (RapidOCR + zxing on Windows), props render and read correctly | agent A | **done** (11/11 demo packs read correctly, ~0.3 s warm) | `core/pack_tools.py`, `requirements.txt`, tests |
| B | R4 evaluation: golden set from real alerts (seed 1 dev, seed 7 eval), arms baseline / agent_rules / agent_hybrid x HITL oracle / none, metrics and per-scenario tables, `runs/eval_*.md`, `docs/results/` | agent B | **done** (e283407; rerun all arms after investigator fixes) | `core/evaluate.py`, `core/props.py`, `cli.py eval` |
| C | Observability and LLM: optional Phoenix/OpenTelemetry spans, hybrid planner with qwen2.5:3b, feedback-loop prior visible in trace and question | agent C | todo | `core/tracing.py`, `core/llm.py` |
| D | LaTeX report (IEEE, 8 to 12 pages) per plan Part 7.7, numbers from generated files | agent D | **done** (3e71c05) | `paper/` |
| E | Visual guide: how StripCheck works, design choices, scraping, parsing, agent thinking, failsafes | agent E | **done** (commit 25e86db; update LLM/eval sections after B,C land) | `docs/guide/index.html` |
| F | Mobile live demo over a Cloudflare quick tunnel | lead | **done** (commit 1563ef6; verified 401 without token, 200 with link, over the public tunnel) | `scripts/start-demo-tunnel.ps1`, README |
| G | Slides (beamer) per plan Part 7.6 | agent D | **done** (3e71c05) | `paper/slides/` |
| H | Full test sweep, malformed-input checks, fresh-clone run on Windows | lead | todo | test logs |

## Log
- 2026-11-08: plan read; repo surveyed (194 Python, 75 web tests pass on Windows); gaps listed above.
- 2026-11-08: A done (Windows OCR); tunnel gate test fixed; cli check handles EOF on stdin.
- 2026-11-08: E done (docs/guide). Team names sent to D: 1BM23CD008 Aryanraj S Singh, 1BM23CD050 Richik Chaudhuri, 1BM23CD061 Suraj B (lead), 1BM23CD062 Sushanth Deo. No real photos: synthetic packs only.
- RESUME: B (eval), C (tracing/LLM), D (paper+slides) were still running uncommitted; check docs/final/{B,C,D}_status.md, run pytest, commit their files. cli.py EOFError fix is uncommitted (goes with B's cli.py). Then: fix confirmation-position gap in core/investigator.py (ask positions where nearest listed batch differs; see docs/final/E_status.md), update guide LLM/eval sections, fix \Sepackage typo in paper/main.tex if D did not, H sweep, tag v1.0.
- NEXT after C lands: fix investigator brand-line product_text bug + grade()/R2 partial-match disagreement + confirmation-position gap; rerun eval (3 commands in docs/final/B_status.md); rebuild paper; update guide; README Deviations (simulated misreads).

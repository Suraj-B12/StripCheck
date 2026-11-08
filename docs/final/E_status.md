# Agent E status: visual guide (docs/guide/index.html)

- [x] Read code and docs (core/*, server/app.py, cli.py, spec v2 0,3,4,8-11,15, data note, ui_direction, README deviations)
- [x] Sections 1-15 written (eval results placeholder: div id="eval-results", comment AGENT-B-RESULTS, for agent B)
- [x] Rendered with headless Edge: desktop 1280 light + dark, phone 390 (via iframe harness; headless Edge minimum viewport is 518). Overflows fixed.

Output: docs/guide/index.html (single self-contained file, inline CSS/SVG, no JS, Google Fonts optional with system fallback, prefers-color-scheme dark).

Code facts that differ from the plan/spec (the guide states these in amber "Design vs build" boxes and in the viva answers):
- Runnable engine is deterministic rules (D18): no LangGraph, no Phoenix; every trace step has source "rules". core/llm.py choose_action exists with rules fallback but is not called on the check path. cli.py `--planner` is accepted and stored, not used by investigate().
- Ingest is deterministic validate/quarantine (extra reason "no_llm"); no LLM header mapping or repair.
- Verifier has no send-back: any violation downgrades to CANT_VERIFY. MAX_STEPS is 16 (plan said 12); LLM timeout 15 s (plan said 90 s).
- Product-name search when no batch is readable (spec 10.3 step 8) is not in the build; it asks type_batch.
- Evaluation implemented = 11 synthetic diagnostics (eval --quick); research A/B arms are plan only.

Finding (code, not fixed; noted in guide section 9 and viva Q17):
- noisy.confirmation_positions with no learned counts asks the first two confusable positions by index. If OCR reads an unlisted sibling as a listed key with the misread elsewhere (e.g. 4th char), typing only those two positions confirms the misread. "Type the whole batch" avoids it. Candidate fix: also ask positions where a variant/sibling candidate differs.

Not committed (per instructions).

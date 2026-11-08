# Agent C status: observability, LLM planner, feedback loop

- [x] 1. Hybrid planner calls the LLM at branch points (JSON schema), trace records thought/action/source, clean fallback. Live with qwen2.5:3b: both branch points `source=llm`, same verdicts and step counts as rules.
- [x] 2. Optional OTel/Phoenix export (one trace per check incl. resume), never raises; Phoenix 21.0.0 in `.venv-phoenix`, `phoenix serve` running on http://127.0.0.1:6006 (left running).
- [x] 3. Feedback loop: confirmed 8->B stored; next check shows `prior: 8->B seen 1 time` in trace and in question; question never skipped.
- [x] 4. `docs/trace/` walkthrough (README.md), 2 Phoenix screenshots, Phoenix span export, JSONL logs, reproducible script.
- [x] 5. `tests/test_agentic_observability.py` (12 pass); full `pytest -q`: 223 passed, 2 skipped.

## Log
- 2026-11-08: read files. Finding: `context["planner"]` was ignored; investigator was rules-only; `llm.choose_action` unused; no OTel.
- 2026-11-08: `core/llm.py` `plan_decision` (schema {thought, action enum}, 30 s circuit breaker on connection errors, banned-wording filter on thoughts), `warm()`. `core/investigator.py`: branch points (b) empty exact search and (c) pending candidate call the planner in hybrid/llm mode; (d) verifier send-back once when the LLM drafts before the variant search. Steps carry `source`; decision steps a `thought`; `answer` steps are `source: user`; `draft_verdict` carries `verifier`. Step counts unchanged. Planner mode from `context["planner"]`, else `STRIPCHECK_PLANNER` (default rules). Public signatures and return shapes unchanged (only extra keys).
- 2026-11-08: `core/tracing.py` `export_check` (OTel SDK, OTLP/HTTP to `STRIPCHECK_PHOENIX_URL`, default http://127.0.0.1:6006/v1/traces; on only with STRIPCHECK_TRACING=1; 0.25 s cached TCP probe; batch processor). Spans: `check` (AGENT) -> `planner: <action>` (CHAIN) -> `planner_llm` (LLM) + tool span (TOOL/CHAIN) -> `verifier` (GUARDRAIL). Resume segment `check.resume` is a child of the first root.
- 2026-11-08: `core/templates.py` `prior_note()` added (question text stays in templates). `.gitignore` gets `.venv-phoenix/` (already committed by someone else). `requirements-observability.txt` added.
- 2026-11-08: Span timestamps use a perf_counter-based clock (Windows `time_ns` is coarse and reordered spans in Phoenix); spans clamped to step order; test added.
- 2026-11-08: Live runs: Phoenix trace a29478b5... (run 1, 25 spans) and 734e15c1... (run 2, prior). Ollama unreachable: hybrid check finishes in ~2 s with `rules(fallback)`, FLAGGED.
- Open: the web StepTimeline (`web/src/components/Shared.tsx`, not mine) shows action/summary/source but not `thought`/`prior`; headless Edge could not render a third screenshot (run 2) reliably; `cli.py check` records history in JSONL but does not set STRIPCHECK_TRACING itself.

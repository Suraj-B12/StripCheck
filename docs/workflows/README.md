# Research workflow scripts (record of method)

These are the multi-agent workflow scripts that produced the literature survey in `research_notes/StripCheck literature survey/` and `reports/StripCheck literature survey.md` (Claude Code Workflow tool, 25 to 26 Oct 2026). They are kept as a record of the survey method for the thesis.

- `stripcheck_lit_v1.js`: first run (14 researchers, verification, synthesis); cut off by a usage limit before agents saved.
- `stripcheck_lit_v2.js`: re-run with mandatory incremental saving and a rolling window of six agents.
- `stripcheck_lit_v3.js`: finished the remaining themes on Sonnet, verified all twelve, and wrote the synthesis report.

They contain absolute paths of the Integrator laptop (notes folder and the deep-research skill) and only run there. Run history and resume commands: `docs/research_log.md`.

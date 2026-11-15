# K: agentic core upgrade (status checklist)

- [x] Read rules, contract, investigator, llm, verifier, templates, tracing, evaluate, tests
- [x] llm.py: native tool-call step (tool_chat, agent_step) + JSON-schema fallback + shared wording guard (_forwarder/_guarded)
- [x] investigator.py: planner "agent" tool loop (_agent_loop; tools offered from rules; guard; ReAct observations)
- [x] investigator.py: self-correction (_reflect, _revision_options; at most one revision, then CANT_VERIFY)
- [x] investigator.py: agent field on steps/thinking, _handoff messages (steps in agent mode), agent-turn spans
- [x] server/app.py PLANNERS + perception agent field; cli check --planner agent; evaluate arm agent_llm (not run)
- [x] contract doc additive section 2a
- [x] tests/test_agent_planner.py (13 tests, mock Ollama); one deliberate update in test_agentic_observability (span nesting)
- [x] pytest 272 passed / 2 skipped; npm test 104 passed; selftest exit 0
- [x] 3 live checks in agent mode (qwen2.5:3b): demo 03 FLAGGED 6.9 s; misread_FLAGGED.png CANT_VERIFY 6.1 s (model drafted instead of the optional question); QX7781 NOT_LISTED 2.3 s

Notes: not committed. Not touched: core/supervisor.py, core/monitor.py, server lifespan, cli serve flags.
Open: qwen2.5:3b usually omits the 'thought' argument (thought then reads "(The model gave no reason.) <rule thought>"); web UI does not yet render handoff/reflect specially; README Deviations / decisions.md entry not written.

# G backend status: live thinking + question payload

Contract: docs/final/live_thinking_contract.md. Not committed (lead commits).

## Checklist
- [x] core/llm.py: structured_call(on_text=...) streaming path, partial thought extraction, 80 ms throttle; plan_decision(on_text=...) with BANNED stop + redacted flag
- [x] core/templates.py: thinking_context(key), question_reason(kind), reason in question()
- [x] core/investigator.py: investigate(observer=), live step emit, thinking start/delta/end, thinking_count persisted, asks_used/asks_max/crop on pending
- [x] server/sse.py: queue 2048
- [x] server/app.py: observer -> SSE, record only thinking end, skip live steps in _snapshot_events, planner validation (JSON, multipart, demo), health llm_ok/model, batch crop
- [x] tests/test_live_thinking.py (17 tests)
- [x] full suite: 243 passed, 2 skipped
- [x] live Ollama hybrid run (demo 03, qwen2.5:3b): think-1 9 deltas over 1.3 s -> search_variants; think-2 12 deltas over 1.6 s -> ask_user; interrupt confirm_char 1/2 with reason

## Notes
- core/llm.py local_url(): "localhost" -> 127.0.0.1 for Ollama requests (Windows IPv6 attempt cost ~1 s per call; health probe went 1.0 s -> 0.04 s).
- tests/test_api_resilience.py backlog test updated for queue bound 2048 (flood 5000, waits for producer before reading).
- Health probe cached 5 s, timeout 0.4 s.
- Known limits: the live draft_verdict step lacks "verifier" (added after logging; the snapshot has it). A retried stream (invalid JSON on try 1) restarts deltas from "" (full-text frames keep the client consistent). The stream deadline is checked per NDJSON line, so one stalled read can last up to the socket timeout.
- Health also returns planner: {default, choices}.

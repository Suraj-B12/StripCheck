# W: web client for agentic events

Contract: docs/final/live_thinking_contract.md section 2a. Owner: web/src only. No commits.

## Checklist
- [x] Agent badges (lib/agents.ts, components/AgentBadge.tsx; steps and thinking blocks)
- [x] Hand-off connector rows with slide-in (off under reduced motion)
- [x] Self-check rows (R1-R10 in plain words, decision)
- [x] Planner segmented control Rules / Hybrid / Agent, disabled without llm_ok, localStorage, default Agent
- [x] Legacy payloads and PUBLIC_DEMO unchanged (no badge without agent; no planner field in demo)
- [x] Tests: components/Agents.test.tsx, screens/CheckScreenLive.test.tsx (111 pass)
- [x] npm test, tsc, lint (0 warnings), build green

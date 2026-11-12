# G: web client for live thinking + conversational questions

Contract: docs/final/live_thinking_contract.md. Owner: web/src only. No commits.

## Checklist
- [x] api.ts types (Step.thought/prior, Health.ollama.llm_ok/model, pending fields, planner on submit)
- [x] Thinking.tsx (ThinkingPanel + reducer + rebuild from history)
- [x] Ask.tsx (conversational question card: avatar, typing, OTP, choice cards, shake, tick)
- [x] CheckScreen wiring (thinking events, planner switch, ask card)
- [x] CSS (animations, reduced motion, 320 px)
- [x] Tests (Thinking, OTP, choice cards, planner payload)
- [x] npm test / tsc / lint / build green

## Log
- api.ts types and components/Thinking.tsx written (applyThinking, blocksFromHistory, ThinkingPanel).
- components/Ask.tsx written (AskConversation, CharBoxes, ChoiceCards, AnsweredThread).
- helpers moved to lib/thinking.ts and lib/ask.ts; CheckScreen wired (thinking/strip events, planner switch, AskConversation, AnsweredThread). Next: CSS.
- CSS appended to app.css (thinking, switch, conversation, OTP, choice cards, keyframes, 480px, reduced motion). Next: tests.
- Tests added: components/Thinking.test.tsx, components/Ask.test.tsx, screens/CheckScreenLive.test.tsx. 97 tests pass, tsc and lint clean. Next: build + browser check.
- Final: npm test 97/97 (was 76), tsc clean, oxlint 0 warnings, vite build OK. Visual check against a scratch mock of the contract (port 8765, not shipped): live streaming, collapse, OTP, answered thread, final; 320 px no horizontal scroll; dark theme OK.
- Planner payload: sent only when /api/health returned an `ollama` object (hybrid if llm_ok and switch on, else rules); omitted when health is unknown so the server default applies (keeps the existing exact-payload tests). Not sent in PUBLIC_DEMO.
- DONE. Not committed (lead commits).

# Live thinking and conversational questions: shared contract (2026-11-12)

Backend and frontend are built in parallel against this file. Change it only by agreement (the lead edits it).

## 1. Planner selection per check
- `POST /api/checks` JSON body may include `"planner": "rules" | "hybrid"`; multipart form may include a `planner` field. Anything else -> 422 with a plain message. Missing -> server default (`config.PLANNER`).
- The choice is stored in the check context, so `/resume` keeps it. Demo checks accept it too.
- `GET /api/health` -> `ollama: {up, models, llm_ok, model, ...}` must include `llm_ok: bool` and `model: str` (the configured `STRIPCHECK_LLM_MODEL`). The web enables the "Local AI reasoning" switch only when `llm_ok` is true.

## 2. Live events (SSE), in addition to the existing ones
Steps are now emitted **live** while the investigator runs (not only after it returns). The final `snapshot` event is still sent and remains the source of truth; the client replaces its history with the snapshot's.

`step` (existing shape) - every `_log` entry as it happens: `{step, action, source, summary, ms, thought?, prior?, ...}`. Never re-emitted afterwards.

`thinking` - one block per branch-point decision:
```
{ "id": "think-<n>",                     // unique within the check (n = decision counter, continues across resume)
  "phase": "start" | "delta" | "end",
  "context": "Exact search found nothing. Deciding what to check next.",   // short, from templates/RULE text, never model text
  "source": "llm" | "rules" | "rules(fallback)",   // on start: "llm" when the model is being asked, else "rules"
  "text": "<full thought text so far>",  // FULL accumulated text every time (robust to dropped frames); "" on start
  "model": "qwen2.5:3b",                 // when source is llm
  "action": "search_variants",           // on end: the chosen action
  "ms": 1840,                             // on end: wall time of the decision
  "redacted": false }                     // on end/delta: true when the wording rules withheld model text
```
- Rules mode: emit `start` then `end` immediately with the rule thought (`source: "rules"`).
- Hybrid mode: `start` (`source: "llm"`), throttled `delta`s (at most one per 80 ms, full text), then `end` with the cleaned final thought and chosen action. If the model fails or times out: `end` with `source: "rules(fallback)"` and the rule thought.
- Every delta is checked against `core.templates.BANNED`; on a hit the server sends `end` with `redacted: true` and the withheld-rationale text, and sends no more deltas for that block.
- Model text is shown as reasoning only. It never enters verdict text (unchanged rule).

## 3. Question payload (`interrupt` / `snapshot.pending`) additions
- `reason`: one plain sentence from `core/templates.py` saying why the agent is asking (per kind). Safety wording rules apply.
- `asks_used` and `asks_max`: integers (question number and the bound, 2).
- `crop`: optional `"/api/crops/<id>.png"` URL of the batch line from the uploaded photo, when the reader has a box for it. Omitted otherwise.
- `confirm_batch` already has `positions` (1-based). The client may answer with `{"chars": {"<pos>": "<char>", ...}}` (supported by the investigator) or `{"typed": "<whole batch>"}`.
- `confirm_char` has `listed` and `pack` strings and `positions` where they differ.

## 4. UI behaviour (web)
- Thinking panel: while a block streams, a shimmering "Thinking" label with a pulsing orb, the context line, and the text streaming in with a blinking caret. On `end` it collapses to "Thought for 1.8 s" (+ model name, or "Rule-based", or "Local model unavailable, used the rules") with the chosen action as a chip; click to expand. One small note: "Shown for transparency. Results come only from the rules and the verifier."
- After reload (no live events) the panel is rebuilt from `history` steps that carry `thought`.
- Questions read as a short conversation with the agent: avatar, typing indicator (~600 ms) before the question appears, "why I'm asking" line, question counter, the photo crop when present, OTP-style boxes for the look-alike positions (others shown fixed), choice cards that highlight differing characters, shake on a rejected answer, a confirmation tick and "Checking again" after answering.
- `prefers-reduced-motion: reduce` disables every animation (content still appears). Keyboard and screen-reader friendly (`aria-live="polite"` for new questions and thinking end).
- Colours only from `web/src/styles/tokens.css` variables; no green for NOT_LISTED; no UI kit.

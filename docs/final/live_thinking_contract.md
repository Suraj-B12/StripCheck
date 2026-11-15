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

## 2a. Agent planner, self-correction and hand-offs (2026-11-15, additive only)
Old clients keep working: every field below is optional and every existing field keeps its meaning.
- Planner choice may also be `"agent"` (POST body/form and `cli.py check --planner agent`). The investigator agent then picks every tool by Ollama native tool calling; the tools offered per step come from the rules. Rules and hybrid behave as before.
- `step.agent`: `"perception" | "investigator" | "verifier" | "supervisor"`, the agent that owns the step. Missing on old records: treat as `"investigator"`.
- `thinking.agent`: the agent making the decision (always `"investigator"` today). Agent-mode blocks follow the same start/delta/end rules, full text, BANNED/REASSURE/HOLD_TAIL guard; a fallback still ends with `source: "rules(fallback)"`.
- New step actions:
  - `handoff`: `{from, to, kind, reason}` (kind `fields | draft | send_back | recheck`). Logged as steps only in the agent planner; rules/hybrid keep their step counts and keep hand-offs in the engine state and the trace.
  - `reflect`: after the verifier rejects a draft: `{violations: [...], decision: "ask_user" | "downgrade"}`. At most one revision per check; after it the result is CANT_VERIFY as before.
- New thinking `context` keys come only from `core/templates.py` (e.g. reflect: "The verifier found problems with the draft. Deciding how to revise it once.").
- Clients that do not know an action may show it as a plain step with its `summary`.

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

## 2b. Vision fallback, evidence requests and ReAct labels (2026-11-15, additive only)
Old clients keep working: every field below is optional.
- New tool step `read_with_vision` (`agent: "perception"`): the batch-line crop (or the photo downscaled to 1280 px) goes to the local vision model (`STRIPCHECK_VLM_MODEL`, default `qwen2.5vl:3b`; timeout `STRIPCHECK_VLM_TIMEOUT`, default 30 s). Extra field `vision: {vision_batch, confidence, status, ocr_batch}` with status `pending | agrees | failed`. It runs only when the batch is missing, the readers disagree, or the batch line has very low OCR confidence, and only for photo checks. A vision reading is never gate evidence (R2 unchanged).
- New question kind `confirm_reading`: `{kind, question: "Is this the batch printed on your pack?", reading, ocr_batch, options: ["Yes, that's the batch", "No, it's different"], style: "yes_no", crop?}`. Answer `{"choice": "yes" | "no"}` (or the option text, or `{"confirm": true|false}`). Yes: `batch_evidence = user_confirmed`, batch provenance `vlm`. No: the next question is `type_batch`.
- New tool step and question kind `request_photo`: `{kind: "request_photo", photo_kind: "batch_zoom" | "second_angle" | "carton", photo_hint, options: ["I can't take another photo"], style: "photo"}`. Answer: multipart upload to `/api/checks/{id}/resume` (field `image`), or `{"choice": "I can't take another photo"}` / `{"skip": true}` to decline. Counts toward `asks_max`; at most one per check.
- Every question payload has `style`: `text | chars | choice2 | yes_no | photo | fields`.
- ReAct labels: every step with a `thought` has `react: {thought, action: {tool, args}, observation}` (observation is a short summary of the tool result) and, when a thinking block chose it, `think_id` (the block `id`). Every thinking `end` has `react: {thought, action: {tool, args}}`; the client attaches the observation from the step whose `think_id` matches.
- `GET /api/health` -> `ollama.vlm_ok` (vision model installed) and `ollama.vlm_model`.

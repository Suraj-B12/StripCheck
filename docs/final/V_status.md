# V: vision fallback, evidence gathering, ReAct labels, answer styles (status checklist)

- [x] Read rules, contract, K_status, investigator, llm, pack_tools, crops, verifier, templates, server, web
- [x] config VLM default qwen2.5vl:3b; llm.vision_read + validate_vision; crops.vision_input
- [x] templates: confirm_reading + request_photo questions/reasons/contexts
- [x] investigator: perception-doubt phase (read_with_vision, confirm_reading, request_photo, type_batch), answers, react fields
- [x] server: vision_image/batch_low_confidence context, resume candidate batches incl. reading, multipart request_photo
- [x] contract doc section 2b
- [x] web: Ask answer styles, request_photo button, Thinking Thought/Action/Observation rows
- [x] tests python (tests/test_vision_evidence.py, 17; tests/conftest.py turns VLM off by default)
- [x] web tests (src/components/AnswerStyles.test.tsx, 6)
- [x] pytest 289 passed / npm test 117 passed / tsc / lint / build / selftest ok: / tsc / lint / build / selftest
- [x] live test with qwen2.5vl:3b (agent planner, TestClient, data/samples/pack_types/unreadable_test.png)


## Design
- Perception-doubt phase in core/investigator.py (`_perception`) runs before any search when the batch is missing, the readers disagree, or the batch line has very low OCR confidence (server: score < 0.5). Rules list the allowed tools (read_with_vision, ask_user confirm_reading/type_batch, request_photo batch_zoom); rules mode takes the first, hybrid asks the planner, agent uses tool calling. Bounded: 2 vision calls, 1 photo, MAX_ASKS 2.
- `llm.vision_read` (Ollama /api/chat, base64 image, JSON schema, temperature 0, STRIPCHECK_VLM_TIMEOUT) + `llm.validate_vision` (charset, length 3-25, label prefix stripped, wording guard on note). Connection errors set the shared down-window; a timeout does not.
- `crops.vision_input`: batch-line crop (upscaled to 448 px wide) or the photo downscaled to 1280 px; server crops the "Batch No" label line plus the space to its right when the value was unreadable.
- confirm_reading: yes -> user_confirmed, provenance vlm; no/skip -> type_batch. Asked only when 2 asks remain, else type_batch directly. The server loads alert rows for the pending vision reading on resume.
- request_photo: multipart resume; fields merge with provenance (ocr, or carton for kind carton); OCR + vision agreement is never gate evidence; decline -> typing or CANT_VERIFY. Agent loop also offers request_photo(carton) beside box_photo.
- ReAct: `react` on steps with a thought, `think_id` link, `react` on thinking end; web shows Thought / Action / Observation rows.
- tests/conftest.py sets config.VLM_MODEL = "" for every test (so a local Ollama is never reached); vision tests turn it on.

## Live (qwen2.5vl:3b on CPU, size_vram 0; qwen2.5:3b planner)
- unreadable_test.png = glare_FLAGGED.png with the batch value blurred/low-contrast/noised; OCR reads only "Batch No".
- Vision (crop) read AYA2107 (true AYA2101) conf 0.95 in 5.6 s cold / 2.0 s warm. Whole photo at 1280 px timed out at 60 s on CPU.
- Yes path: confirm_reading -> yes -> confirm_char AYA2107 vs AYA-2101 -> AYA-2101 -> FLAGGED (user_confirmed). Skipping confirm_char -> CANT_VERIFY.
- No path: confirm_reading -> no -> type_batch -> AYA2101 -> FLAGGED (user_typed).

Open: whole-photo vision too slow on this laptop (CPU only); vision confidence is not calibrated (0.95 on a wrong digit); README Deviations / decisions.md entry not written; not committed.

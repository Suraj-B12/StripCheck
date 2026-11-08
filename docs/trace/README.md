# Trace walkthrough: a misread batch, one question, and the learned prior

This folder holds the R3 trace walkthrough. It covers one misread check traced in Phoenix, and a second check where the correction confirmed in the first one shows up as a prior in the trace and in the question.

| File | What it is |
|---|---|
| `run_walkthrough.py` | Reproduces both runs (instructions in its docstring) |
| `01_phoenix_trace_list.png` | Phoenix project `stripcheck` with the traces |
| `02_phoenix_run1_misread_trace.png` | Run 1 trace: root span, planner steps, LLM and tool spans |
| `phoenix_spans_run1.json` | All 25 spans of run 1 as returned by the Phoenix REST API (`/v1/projects/stripcheck/spans`) |
| `run1_trace.jsonl`, `run2_trace.jsonl` | The app's own JSONL step log (written whether or not Phoenix runs) |
| `walkthrough_runs.json` | Summary of both runs: step trace with thought/source/prior, question, label, learned counts |

## Setup used (8 Nov 2026)

- Ollama 0.17.7 with `qwen2.5:3b`, `STRIPCHECK_PLANNER=hybrid`, `STRIPCHECK_LLM_TIMEOUT=30`.
- Phoenix 21.0.0 in its own venv (`.venv-phoenix`), `phoenix serve` on http://127.0.0.1:6006; app venv has only the OTel SDK and OTLP/HTTP exporter (`requirements-observability.txt`); `STRIPCHECK_TRACING=1`.
- Input: the rendered synthetic prop `03` photo. The local OCR (RapidOCR on Windows) reads the batch `LM24088`; the printed batch is `LM2408B`.
- The alert store holds one invented record (prop 03, `example.invalid` source) so that no CDSCO row is copied into the repository. The check runs through the real server API (`POST /api/checks`, then `/resume`) with a throwaway database. The run is not marked as a demo, so the correction is learned.

## The five steps (run 1)

**1. Root span and step timeline.** Screenshot `02`. The trace root `check` (AGENT) holds one `planner: <action>` span per step. Each planner span has the tool span (`TOOL` for extract/search/grade) and, at branch points, a `planner_llm` span (LLM). The resumed half of the check (`check.resume`) is a child of the same root, so the question and the answer appear in one trace. Total 25 spans, 8.8 s, almost all of it the two LLM calls.

**2. The planner's decision after the empty exact search.** `search_exact` returns 0 candidates. This is branch point (b), so the planner asks the LLM, with a JSON schema that allows only `search_variants` or `draft_verdict`:

```
input:  {"evidence": {"batch_read": "LM24088", "batch_source": "ocr", "exact_hits": 0, "records_searched": 1,
         "learned_reader_confusions": []}, "allowed": ["search_variants", "draft_verdict"], "rule_suggestion": "search_variants"}
output: {"thought": "The batch read is unique and not found in the records, suggesting it may be a variant or a new batch.",
         "action": "search_variants"}
```

The step trace records `action=search_variants, source=llm` and the thought. If Ollama is off, the same step shows `source=rules(fallback)` with the rule thought. If the LLM had picked `draft_verdict`, the verifier would send the draft back once (R4: a not-listed result needs the variant search).

**3. The `search_variants` tool span.** Input `{"batch_key": "LM24088", "max_subs": 2, "prior": []}`. Output: one candidate `LM2408B`, substitution `[6, "8", "B"]` (position 7, read 8, listed B), entry type NSQ. Grading marks it `needs_confirm_char`. That is branch point (c), where the LLM picks `ask_user` over `draft_verdict` (thought: "...requiring user confirmation to proceed").

**4. The `ask_user` interrupt and the resumed answer.** The `ask_user` span output is the question payload: "Which batch is printed on your pack: LM24088 or LM2408B?" with options `LM2408B`, `LM24088`, `Can't tell`. The check pauses (`status: waiting`). The resume span `answer` has input `{"choice": "LM2408B", "source": "user"}` and output `{"changes": {"batch": "LM2408B"}, "batch_evidence": "user_confirmed"}`. The server stores the correction (JSONL event `learning`: "Stored 1 explicitly confirmed character correction(s)..."), and `confusions(8->B, user)` becomes 1.

**5. The verifier approves, and the final verdict.** After the answer, the search repeats on the confirmed batch: an exact hit, grade `accept`. `draft_verdict` has a `verifier` (GUARDRAIL) child whose input is the template draft (label FLAGGED, headline, citation id 10001 with its source URL) and whose output is `approved`. The final label is FLAGGED with the citation. All verdict text comes from `core/templates.py`; the LLM's thoughts appear only in the trace.

## The feedback loop (run 2)

The same photo is checked again. From `walkthrough_runs.json` and `run2_trace.jsonl`:

- `search_variants` step: `prior: "8->B seen 1 time"`, summary "... Prior confirmed corrections: 8 to B: 1. Confirmation is still required."; the LLM's planner input now lists `learned_reader_confusions: ["8->B x1"]` and its thought reads "To account for potential reader confusion, it is important to check for variations of the batch number."
- The question still appears (the prior never skips it), and it now ends with: "Earlier checks on this computer confirmed that the photo reader read B as 8 once. Please still check the printed character yourself." The interrupt payload carries `prior: [{"read": "8", "true": "B", "count": 1}]`.
- After the answer, the label is FLAGGED and the count becomes 2.

Demo checks (`/api/demo/...`) never read or write the prior, so the public demo stays deterministic.

## Things we saw

- The 3B model's thoughts are short and on topic. They are not always exact: in run 1 it swapped the pack and listed batch in its ask thought. This is acceptable because the thought only explains the choice. The action is restricted to the allowed enum, and every result still passes the deterministic verifier.
- A cold model load took about 38 s for a 7B model (longer than the per-call timeout). `llm.warm()` preloads the model, and the walkthrough script calls it. Without the warm-up, the first decision falls back to rules, and a 30 s circuit breaker keeps the rest of the check from waiting again.
- With Ollama unreachable, a hybrid check finished in about 2 s with `rules(fallback)` at both branch points and the same FLAGGED result. With Phoenix stopped, a 0.25 s TCP probe (cached for 15 s) skips span creation entirely.

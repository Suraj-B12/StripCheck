# Agent B status: R4 evaluation (M7)

- [x] Read CLAUDE.md, FINAL_PUSH, plan R4/eval sections, spec v2 section 15, core modules
- [x] core/golden.py: golden-set manifest from real DB rows (seed 1 dev, seed 7 eval)
- [x] core/props.py: render_pack + degrade for eval cartons (banner DEMO PROP - NOT A MEDICINE)
- [x] core/evaluate.py: arms, HITL policies, metrics, Wilson, McNemar, decision rule, predictions, md/json/LaTeX (diagnostics `run_quick` kept)
- [x] cli.py: `props --eval --n --seed`, `eval --arms --hitl --seed --n`, `eval --quick` keeps diagnostics
- [x] tests/test_evaluation_golden.py (6 tests, fixture rows, fake perception, < 2 s)
- [x] Dev run seed 1 (sanity only, rules arms)
- [x] Final run seed 7, rules arms (baseline, agent_rules x oracle, none): runs/eval_20261108_112606.md
- [x] Final run seed 7, agent_hybrid x oracle, none on the full 60 items (qwen2.5:3b live): runs/eval_20261108_113941.md (4 min wall)
- [x] paper/generated/results.tex + results_tables.tex, docs/results/eval_seed7.md (rewritten on every seed-7 run; compile-checked with IEEEtran)
- [x] Full pytest: 223 passed, 2 skipped (16:05); tests/test_evaluation_golden.py 6 passed

## Commands
```
.venv\Scripts\python.exe cli.py props --eval --n 60 --seed 7
.venv\Scripts\python.exe cli.py eval --arms baseline,agent_rules --hitl oracle,none --seed 7
.venv\Scripts\python.exe cli.py eval --arms agent_hybrid --hitl oracle,none --seed 7
```
Results merge into `runs/eval_seed7_latest.json`; each call writes `runs/eval_<ts>.json/.md`; seed 7 also writes
`docs/results/eval_seed7.md`, `paper/generated/results.tex`, `paper/generated/results_tables.tex`.

## Notes
- OCR (RapidOCR PP-OCRv6-small) reads the eval cartons on Windows: seed 1 batch read equal to rendered text on 56/60, median about 1 s per image. Perception runs once per image and is cached in `data/eval/seed<N>/perception.json` (key: image hash + pack_tools.py hash), shared by all arms.
- Misread and sibling items simulate the OCR error by rendering the misread string (spec's stroke calibration not implemented); the manifest keeps the printed truth for the oracle. Deviation to record in README.
- Agent C wired the hybrid planner into the investigator (sources: llm, rules(fallback), rules, user). The eval counts llm and fallback steps per arm.

## Requests to other owners (found on the dev set, seed 1; nothing tuned on seed 7)
1. **investigator.py (grading drops the OCR product text).** `_fields()` keeps only `product` and `brand`; grading then uses `product_text = product + brand`. When the carton prints a brand line above the generic name, `extract_fields` picks the brand as `product`, so the generic name never reaches `grade()` and the listed row is rejected as a product mismatch (false negative: NOT_LISTED) or graded partial. 7 of 8 agent_rules errors on seed 1 (oracle) are brand cartons. Suggested fix: keep `raw["product_text"]` in `_fields` and grade on `f"{product} {brand} {product_text}"`.
2. **matching.grade vs verifier R2 inconsistency.** `grade()` accepts a candidate with product "partial" when dates and maker match, but verifier R2 requires product "match", so the result becomes CANT_VERIFY (batch_gate) after the user already confirmed the batch (a wasted question). Seen on s1_003, s1_013, s1_018.

## Seed 7 rules results (2026-11-08 11:26, before hybrid)
- Perception: RapidOCR on all 60, batch read equal to rendered text 60/60, QR decoded on 8/8 QR cartons, median 1.33 s.
- Oracle: baseline hit recall 32/40, collision FAR 8/8, sibling FAR 4/4; agent_rules hit recall 33/40, FAR 0/20, 0.55 questions per pack, 0 safety violations. McNemar p = 0.011 (18 vs 5 discordant). Decision rule: adopt.
- None (questions skipped): agent_rules hit recall 5/40, abstention 31/60, FAR 0/20.
- All 7 agent_rules oracle errors are NOT_LISTED on listed cartons that print a brand line (request 1 below). 7 of the 15 positive brand cartons fail.

## Seed 7 hybrid results (2026-11-08 11:39, full set, no subset)
- Ollama up, qwen2.5:3b present. Planner steps: oracle 27 llm / 0 fallback; none 30 llm / 0 fallback.
- Verdicts identical to agent_rules on 60/60 items in both HITL settings (prediction "hybrid matches rules" held; "beats rules on partial product matches" not evaluable: no partial-product items).
- Latency (perception + reasoning) oracle median 1.51 s, mean 3.52 s, p95 9.64 s (rules: 1.44 / 1.48 / 1.89).
- Code check at 16:01: investigator.py, llm.py, pack_tools.py, matching.py and verifier.py unchanged since before the seed-7 runs, so all arms ran on the same code. Requests 1 and 2 are still open; if fixed, rerun every arm (both commands above) and say so in the report.
- Final combined report: docs/results/eval_seed7.md; macros paper/generated/results.tex (\ResBase*, \ResRules*, \ResHybrid* for Oracle/Skip).

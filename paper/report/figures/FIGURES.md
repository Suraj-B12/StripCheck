# Report figures (data figures only)

Status: [x] all 8 figures generated, rendered at 150 dpi and inspected; [x] numbers cross-checked against `paper/generated/results.tex` and `docs/results/eval_seed7.md`.

Regenerate (from the repository root, read-only on all sources):

    .venv\Scripts\python.exe paper\report\tools\make_figures.py

Every PDF is a vector file exactly 6.0 in wide (432 pt), CMU Serif (Computer Modern) text, 10 pt ticks, 11 pt axis labels, Okabe-Ito colours (baseline #7F7F7F, agent rules #0072B2, agent hybrid #E69F00, extra #009E73). Include each one at its natural size so the type stays at 10 to 11 pt:

    \includegraphics{figures/fig_headline_seed7.pdf}      % or width=0.96\textwidth (6.0 in of 6.25 in)

A CSV beside each PDF holds every plotted number. Error bars are Wilson 95% intervals, recomputed by the script and asserted equal (to 1e-3) to the intervals stored in the run JSON. Hatching always marks the comparison condition (no human answers, run 1, seed 1, 95th percentile); solid fill is the main condition. A bar of height 0 is drawn as a short coloured stroke on the axis so the arm stays identifiable.

Wording note: the scenario called `genuine` in the data is labelled "Not listed" in the figures (safety-language rule). In captions say "not-listed control packs", never "genuine".

---

## Figure 1. `fig_alerts_per_year.pdf` (+ `.csv`)

Shows: number of alerts in the indexed database per year of the alert list month, 2019 to 2026; the 2026 bar is hatched because the year is partial (last list month 2026-09).

Numbers: 2019: 399; 2020: 315; 2021: 337; 2022: 568; 2023: 624; 2024: 869; 2025: 1,914 (1,882 NSQ + 32 spurious); 2026 (Jan to Sep): 1,897 (1,881 NSQ + 16 spurious). Total 6,923.

Source: local SQLite DB `data/stripcheck.db` (core.config.DB_PATH), opened read-only, `SELECT list_kind, list_month ... FROM alerts WHERE removed_at IS NULL` (the same filter as `db.all_alerts()`, so the total equals the 6,923 alerts the evaluation used). The DB holds 6,953 rows in all; 30 are marked removed. Note: `paper/generated/stats.tex` gives different yearly counts (e.g. 1,898 for 2025, 1,890 for 2026) because it describes the 25 October design-phase snapshot (7,005 rows), not the indexed DB; do not mix the two in one sentence.

Suggested caption: Alerts in the local index by year of the CDSCO list month (n = 6,923 indexed alerts). The 2026 bar covers January to September only.

## Figure 2. `fig_alert_timing.pdf` (+ `.csv`)

Shows: two histograms (3-month bins). Left: months from the manufacturing month to the alert list month. Right: months of shelf life left (expiry month minus list month) at the list month; the vertical line at 0 separates already-expired batches. Dashed line = median.

Numbers: rows with a parseable YYYY-MM date: 6,839 of 6,923 for each measure (84 excluded, no parseable date). Lag: median 10 months, quartiles 6 and 15, range -21 to 56; 16 rows with negative lag (manufacture after the list month, data-entry errors) are counted in the median but fall outside the plotted 0 to 60 range. Shelf life left: median 14 months, quartiles 9 and 18, range -23 to 117; 3 rows below -12 and 1 row at or above 60 fall outside the plotted range; 40 of 6,839 are below 0 (already expired when listed; 0.6%). Quartiles use the same index rule as `docs/spikes/data_analysis/import_snapshot.py`; the medians and quartiles match `stats.tex` (LagMedian 10, LagQOne 6, LagQThree 15, ShelfMedian 14, ShelfQOne 9, ShelfQThree 18). Bin counts are in the CSV.

Source: same DB query as Figure 1 (list_month, mfg, exp).

Suggested caption: Timing of alerts in the local index (n = 6,839 alerts with parseable dates). Left: months from manufacture to the alert list month (median 10). Right: shelf life left when the alert was listed (median 14 months); bars left of zero are batches already expired.

## Figure 3. `fig_headline_seed7.pdf` (+ `.csv`)

Shows: hit recall and false-alarm rate (all not-listed packs, collision packs) for the three arms, seed 7, HITL = oracle, with Wilson 95% intervals and k/n labels.

Numbers (k/n, Wilson 95%):
- Hit recall: baseline 32/40 (0.65 to 0.90); agent rules 40/40 (0.91 to 1.00); agent hybrid 40/40 (0.91 to 1.00).
- False-alarm rate, all not-listed: baseline 12/20 (0.39 to 0.78); rules 0/20 (0.00 to 0.16); hybrid 0/20 (0.00 to 0.16).
- False-alarm rate, collisions: baseline 8/8 (0.68 to 1.00); rules 0/8 (0.00 to 0.32); hybrid 0/8 (0.00 to 0.32).

Source: `runs/eval_seed7_latest.json` (results.oracle.*.summary), run 2. Cross-checked: `paper/generated/results.tex` (\ResBaseOracleHitRecallK 32/40, \ResRulesOracleFARK 0/20, \ResBaseOracleFARCollisionK 8/8, ...) and `docs/results/eval_seed7.md` Table A.

Suggested caption: Headline results on the evaluation set (seed 7, n = 60, a person answers every question). Bars show proportions with Wilson 95% intervals; labels give k/n. Listed packs n = 40; not-listed packs n = 20, of which 8 are collisions.

## Figure 4. `fig_scenarios_seed7.pdf` (+ `.csv`)

Shows: correct verdicts per scenario, one panel per arm, seed 7, HITL = oracle. Counts out of n.

Numbers (baseline / rules / hybrid): clean 8/8, 8/8, 8/8; glare 8/8, 8/8, 8/8; QR code 8/8, 8/8, 8/8; misread 0/8, 8/8, 8/8; spurious 8/8, 8/8, 8/8; not listed (data name `genuine`) 8/8, 8/8, 8/8; collision 0/8, 8/8, 8/8; sibling 0/4, 4/4, 4/4. Totals 40/60, 60/60, 60/60.

Source: `runs/eval_seed7_latest.json` (summary.by_scenario); matches `docs/results/eval_seed7.md` Table C (oracle).

Suggested caption: Correct verdicts per scenario on seed 7 with a person answering (n = 8 per scenario, 4 for siblings). The baseline fails exactly on misreads, collisions and siblings.

## Figure 5. `fig_hitl_seed7.pdf` (+ `.csv`)

Shows: agent (rules) on seed 7 with the person answering (oracle, solid) and with no answers (none, hatched): hit recall, abstention rate, false-alarm rate on not-listed packs.

Numbers (k/n, Wilson 95%): hit recall oracle 40/40 (0.91 to 1.00), none 8/40 (0.10 to 0.35); abstention oracle 0/60 (0.00 to 0.06), none 36/60 (0.47 to 0.71); false-alarm rate oracle 0/20 (0.00 to 0.16), none 0/20 (0.00 to 0.16).

Source: `runs/eval_seed7_latest.json` (results.oracle.agent_rules, results.none.agent_rules); matches results.tex \ResRulesOracle*K and \ResRulesSkip*K, and eval_seed7.md Tables A and B. Agent hybrid has identical counts under both policies.

Suggested caption: Effect of the human answer for the agent (rules), seed 7. Without answers the agent abstains (CANT_VERIFY) on 36 of 60 packs instead of guessing, so hit recall falls while the false-alarm rate stays at zero.

## Figure 6. `fig_latency_seed7.pdf` (+ `.csv`)

Shows: per-pack time in seconds, seed 7, HITL = oracle. Left: end-to-end time (shared perception plus the arm's reasoning). Right: reasoning time only. Solid = median, hatched = 95th percentile.

Numbers (median / p95, s): end to end: baseline 1.33 / 1.82; rules 1.39 / 1.86; hybrid 1.51 / 8.96. Reasoning only: baseline 0.000 / 0.000 (a single lookup, no reasoning step); rules 0.061 / 0.103; hybrid 0.099 / 7.672. Unrounded values in the CSV (e.g. hybrid p95 8.955, 7.6723).

Source: `runs/eval_seed7_latest.json` (summary.latency_s, summary.reasoning_s); matches results.tex (\ResHybridOracleLatPNinetyFive 8.96, \ResRulesOracleReasonMedian 0.061) and eval_seed7.md Table A. Hardware: the Integrator laptop; perception median 1.332 s per image.

Suggested caption: Time per pack on seed 7 (n = 60). The rules agent adds about 0.06 s of reasoning to the 1.3 s perception step; the hybrid planner's local LLM calls set its 95th percentile (9.0 s end to end).

## Figure 7. `fig_run1_run2.pdf` (+ `.csv`)

Shows: agent (rules), seed 7, HITL = oracle, before (run 1, commit e283407, hatched) and after the three fixes (run 2, solid). Left: hit recall, hit recall on clean + QR packs, overall accuracy with Wilson 95% intervals. Right: correct verdicts per scenario.

Numbers: hit recall 33/40 (0.68 to 0.91) to 40/40 (0.91 to 1.00); clean + QR 12/16 (0.51 to 0.90) to 16/16 (0.81 to 1.00); accuracy 53/60 (0.78 to 0.94) to 60/60 (0.94 to 1.00). Per scenario run 1 to run 2: clean 7/8 to 8/8; glare 7/8 to 8/8; QR code 5/8 to 8/8; misread 6/8 to 8/8; spurious 8/8 to 8/8; not listed 8/8 to 8/8; collision 8/8 to 8/8; sibling 4/4 to 4/4.

Source: run 1 parsed by the script from `git show e283407:docs/results/eval_seed7.md` (Tables A and C, oracle); the values agree with `paper/run1_results.tex` (\RunOneRulesOracleHitRecallK 33/40, CleanQRK 12/16, AccuracyK 53/60, CleanK 7/8, MisreadK 6/8). Run 2 from `runs/eval_seed7_latest.json`. Both runs use the same golden set (60/60 batch reads exact, same perception median 1.332 s).

Suggested caption: Agent (rules) on seed 7 before (run 1) and after the three fixes (run 2), with a person answering. Run 1 is reported in full; the fixes were made after it and the same set was run again, so run 2 is no longer a blind test.

## Figure 8. `fig_seeds.pdf` (+ `.csv`)

Shows: headline metrics per arm on the development set (seed 1, dotted hatch) and the evaluation set (seed 7, solid), HITL = oracle, Wilson 95% intervals and k/n labels. Four panels: hit recall, overall accuracy, false-alarm rate on not-listed packs, false-alarm rate on collisions.

Numbers (seed 1 / seed 7):
- Hit recall: baseline 31/40 / 32/40; rules 40/40 / 40/40; hybrid 40/40 / 40/40.
- Overall accuracy: baseline 39/60 / 40/60; rules 60/60 / 60/60; hybrid 60/60 / 60/60.
- False-alarm rate, not-listed: baseline 12/20 / 12/20; rules 0/20 / 0/20; hybrid 0/20 / 0/20.
- False-alarm rate, collisions: baseline 8/8 / 8/8; rules 0/8 / 0/8; hybrid 0/8 / 0/8.

Seed 1 also (not plotted, from `paper/report/data/eval_seed1.md`): HITL = none, rules and hybrid hit recall 7/40, abstention 37/60, accuracy 23/60, false-alarm rate 0/20; baseline unchanged (31/40). Baseline per scenario on seed 1: misread 1/8, QR 7/8, spurious 7/8 (seed 7: 0/8, 8/8, 8/8). Perception on seed 1 read the batch exactly on 56/60 images (seed 7: 60/60), median 1.111 s per image. Questions per pack, rules oracle: 0.63 (seed 7: 0.60). Hybrid on seed 1: 31 LLM steps, 0 fallbacks (oracle).

Source: seed 1 run made for this report on 2026-11-12 in the clean clone (scratchpad `fresh`, commit e5aa2d7, same core code as the seed-7 run 2) with qwen2.5:3b; commands `cli.py props --eval --n 60 --seed 1`, `cli.py eval --arms baseline,agent_rules --hitl oracle,none --seed 1`, `cli.py eval --arms agent_hybrid --hitl oracle,none --seed 1` (hybrid finished in about 5 minutes). Copied to `paper/report/data/eval_seed1.md` (report), `eval_seed1.json` (merged store), `eval_seed1_run.log`. The golden-set manifest hash is 12a483272b8585ef, identical to the earlier seed-1 store in `runs/eval_seed1_latest.json`, and the alert count is 6,923. Seed 7 from `runs/eval_seed7_latest.json`.

Deviation from the task instructions: the run used a scratch copy of `data/stripcheck.db` (STRIPCHECK_DATA_DIR and STRIPCHECK_DB_PATH pointed to `scratchpad/seed1data`) instead of the main DB, because `run_research` writes an `evaluation/research_latest` document into the DB and `props --eval` writes images under DATA_DIR/eval; pointing at the main data would have replaced the seed-7 summary the app shows. The alert rows are byte-identical (file copy). `paper/generated/*` and `docs/results/*` timestamps were checked before and after: unchanged.

Caveat for the text: the generated seed-1 markdown says "Thresholds were not tuned on this seed"; that sentence is boilerplate printed for every seed. Per FACTS.md (section 11), seed 1 is the development set on which thresholds were tuned, so seed 1 results are not an independent test.

Suggested caption: Headline metrics on the development set (seed 1) and the evaluation set (seed 7), a person answering, n = 60 each. Labels give k/n; whiskers are Wilson 95% intervals. The agent arms give the same counts on both sets; the baseline differs by one pack.

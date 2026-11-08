# StripCheck evaluation, seed 7 (n = 60)

Created 2026-11-08T10:49:33.970962+00:00. The golden set renders 60 cartons from real CDSCO alert rows (local database: 6923 alerts). Every image carries the banner DEMO PROP - NOT A MEDICINE. Misread and sibling items simulate an OCR error by rendering the misread string; the oracle answers from the printed truth. Thresholds were not tuned on this seed.

Scenario mix: clean 8, glare 8, misread 8, qr 8, spurious 8, collision 8, genuine 8, sibling 4.

Perception (shared by all arms, read once per image): engines {'RapidOCR PP-OCRv6-small': 60}, errors 0, batch read equal to the rendered text on 60/60 images, median 1.332 s per image. Latency per pack is perception time plus the arm's own reasoning time.

Ollama at the hybrid run: up=True, model qwen2.5:3b present=True.

## Table A: headline metrics, HITL = oracle

Rates as value (k/n; Wilson 95% interval).

| Metric | Baseline (lookup) | Agent (rules) | Agent (hybrid) |
|---|---|---|---|
| Hit recall | 0.80 (32/40; 0.65-0.90) | 1.00 (40/40; 0.91-1.00) | 1.00 (40/40; 0.91-1.00) |
| Hit recall (clean + QR) | 1.00 (16/16; 0.81-1.00) | 1.00 (16/16; 0.81-1.00) | 1.00 (16/16; 0.81-1.00) |
| Type accuracy | 1.00 (32/32; 0.89-1.00) | 1.00 (40/40; 0.91-1.00) | 1.00 (40/40; 0.91-1.00) |
| False-alarm rate (all NOT_LISTED) | 0.60 (12/20; 0.39-0.78) | 0.00 (0/20; 0.00-0.16) | 0.00 (0/20; 0.00-0.16) |
| False-alarm rate (collisions) | 1.00 (8/8; 0.68-1.00) | 0.00 (0/8; 0.00-0.32) | 0.00 (0/8; 0.00-0.32) |
| False-alarm rate (siblings) | 1.00 (4/4; 0.51-1.00) | 0.00 (0/4; 0.00-0.49) | 0.00 (0/4; 0.00-0.49) |
| Abstention rate | 0.00 (0/60; 0.00-0.06) | 0.00 (0/60; 0.00-0.06) | 0.00 (0/60; 0.00-0.06) |
| Overall accuracy | 0.67 (40/60; 0.54-0.77) | 1.00 (60/60; 0.94-1.00) | 1.00 (60/60; 0.94-1.00) |
| Questions per pack | 0.00 | 0.60 | 0.60 |
| Steps per pack | 1.0 | 8.0 | 8.0 |
| Latency median / mean / p95 (s) | 1.33 / 1.36 / 1.82 | 1.39 / 1.43 / 1.86 | 1.51 / 3.28 / 8.96 |
| Reasoning only, median / p95 (s) | 0.000 / 0.000 | 0.061 / 0.103 | 0.099 / 7.672 |
| Safety violations | 0 | 0 | 0 |
| LLM steps / fallback steps | 0 / 0 | 0 / 0 | 28 / 0 |

## Table B: headline metrics, HITL = none

Rates as value (k/n; Wilson 95% interval).

| Metric | Baseline (lookup) | Agent (rules) | Agent (hybrid) |
|---|---|---|---|
| Hit recall | 0.80 (32/40; 0.65-0.90) | 0.20 (8/40; 0.10-0.35) | 0.20 (8/40; 0.10-0.35) |
| Hit recall (clean + QR) | 1.00 (16/16; 0.81-1.00) | 0.50 (8/16; 0.28-0.72) | 0.50 (8/16; 0.28-0.72) |
| Type accuracy | 1.00 (32/32; 0.89-1.00) | 1.00 (8/8; 0.68-1.00) | 1.00 (8/8; 0.68-1.00) |
| False-alarm rate (all NOT_LISTED) | 0.60 (12/20; 0.39-0.78) | 0.00 (0/20; 0.00-0.16) | 0.00 (0/20; 0.00-0.16) |
| False-alarm rate (collisions) | 1.00 (8/8; 0.68-1.00) | 0.00 (0/8; 0.00-0.32) | 0.00 (0/8; 0.00-0.32) |
| False-alarm rate (siblings) | 1.00 (4/4; 0.51-1.00) | 0.00 (0/4; 0.00-0.49) | 0.00 (0/4; 0.00-0.49) |
| Abstention rate | 0.00 (0/60; 0.00-0.06) | 0.60 (36/60; 0.47-0.71) | 0.60 (36/60; 0.47-0.71) |
| Overall accuracy | 0.67 (40/60; 0.54-0.77) | 0.40 (24/60; 0.29-0.53) | 0.40 (24/60; 0.29-0.53) |
| Questions per pack | 0.00 | 0.60 | 0.60 |
| Steps per pack | 1.0 | 8.0 | 8.0 |
| Latency median / mean / p95 (s) | 1.33 / 1.36 / 1.82 | 1.41 / 1.45 / 1.87 | 1.51 / 3.44 / 12.64 |
| Reasoning only, median / p95 (s) | 0.000 / 0.000 | 0.095 / 0.131 | 0.099 / 11.352 |
| Safety violations | 0 | 0 | 0 |
| LLM steps / fallback steps | 0 / 0 | 0 / 0 | 32 / 0 |

## Table C: correct verdicts per scenario (k/n), HITL = oracle

| Scenario | Baseline (lookup) | Agent (rules) | Agent (hybrid) |
|---|---|---|---|
| clean | 8/8 | 8/8 | 8/8 |
| glare | 8/8 | 8/8 | 8/8 |
| misread | 0/8 | 8/8 | 8/8 |
| qr | 8/8 | 8/8 | 8/8 |
| spurious | 8/8 | 8/8 | 8/8 |
| collision | 0/8 | 8/8 | 8/8 |
| genuine | 8/8 | 8/8 | 8/8 |
| sibling | 0/4 | 4/4 | 4/4 |

## Table C: correct verdicts per scenario (k/n), HITL = none

| Scenario | Baseline (lookup) | Agent (rules) | Agent (hybrid) |
|---|---|---|---|
| clean | 8/8 | 0/8 | 0/8 |
| glare | 8/8 | 0/8 | 0/8 |
| misread | 0/8 | 0/8 | 0/8 |
| qr | 8/8 | 8/8 | 8/8 |
| spurious | 8/8 | 0/8 | 0/8 |
| collision | 0/8 | 8/8 | 8/8 |
| genuine | 8/8 | 8/8 | 8/8 |
| sibling | 0/4 | 0/4 | 0/4 |

## Paired comparison and decision rule

Exact McNemar test on per-item correctness against the baseline. Decision rule (registered at R2): adopt the agent if its collision false-alarm rate is at least 50% lower (relative) than the baseline's and its hit recall is no more than 5 points lower.

| Arm | HITL | Agent-only correct | Baseline-only correct | McNemar p | Decision | Detail |
|---|---|---|---|---|---|---|
| Agent (rules) | oracle | 20 | 0 | 2e-06 | adopt | collision FAR 0.00 vs 1.00 (100% lower); hit recall 1.00 vs 0.80 (20.0 points higher) |
| Agent (hybrid) | oracle | 20 | 0 | 2e-06 | adopt | collision FAR 0.00 vs 1.00 (100% lower); hit recall 1.00 vs 0.80 (20.0 points higher) |
| Agent (rules) | none | 8 | 24 | 0.007 | do not adopt | collision FAR 0.00 vs 1.00 (100% lower); hit recall 0.20 vs 0.80 (60.0 points lower) |
| Agent (hybrid) | none | 8 | 24 | 0.007 | do not adopt | collision FAR 0.00 vs 1.00 (100% lower); hit recall 0.20 vs 0.80 (60.0 points lower) |

## Registered predictions (HITL = oracle)

| Prediction | Outcome | Counts |
|---|---|---|
| Clean packs: all arms tie | held | baseline 8/8; agent_rules 8/8; agent_hybrid 8/8 |
| Collisions: baseline false-alarms on every one; agent at most 10% | held | baseline 8/8, agent_rules 0/8 |
| Misreads: baseline misses every flag; agent with oracle recovers at least 80% at no more than 1 question per pack | held | baseline detected 0/8; agent_rules correct 8/8 at 1.0 questions per pack |
| Hybrid matches rules on verdicts | held | 60/60 identical labels |
| Hybrid beats rules on partial product matches | not evaluable | no item produced a partial product match |

## Every incorrect verdict

| HITL | Arm | Item | Truth | Verdict | Read batch | Printed batch | Asks | Questions | Reason |
|---|---|---|---|---|---|---|---|---|---|
| oracle | baseline | s7_017_misread | FLAGGED | NOT_LISTED | M2P2502 | MZP2502 | 0 | - |  |
| oracle | baseline | s7_018_misread | FLAGGED | NOT_LISTED | UF26T4082F | UF2674082F | 0 | - |  |
| oracle | baseline | s7_019_misread | FLAGGED | NOT_LISTED | T2L544 | T21544 | 0 | - |  |
| oracle | baseline | s7_020_misread | FLAGGED | NOT_LISTED | N260O742 | N2600742 | 0 | - |  |
| oracle | baseline | s7_021_misread | FLAGGED | NOT_LISTED | UCCGL07 | UCCGL01 | 0 | - |  |
| oracle | baseline | s7_022_misread | FLAGGED | NOT_LISTED | V2300882 | V2300382 | 0 | - |  |
| oracle | baseline | s7_023_misread | FLAGGED | NOT_LISTED | LO92402 | L092402 | 0 | - |  |
| oracle | baseline | s7_024_misread | FLAGGED | NOT_LISTED | 4S6366 | AS6366 | 0 | - |  |
| oracle | baseline | s7_041_collision | NOT_LISTED | FLAGGED | TG241031C | TG241031C | 0 | - |  |
| oracle | baseline | s7_042_collision | NOT_LISTED | FLAGGED | DVT197270 | DVT197270 | 0 | - |  |
| oracle | baseline | s7_043_collision | NOT_LISTED | FLAGGED | HP404 | HP404 | 0 | - |  |
| oracle | baseline | s7_044_collision | NOT_LISTED | FLAGGED | TAH231704 | TAH231704 | 0 | - |  |
| oracle | baseline | s7_045_collision | NOT_LISTED | FLAGGED | AGWT25032 | AGWT25032 | 0 | - |  |
| oracle | baseline | s7_046_collision | NOT_LISTED | FLAGGED | IW0225 | IW0225 | 0 | - |  |
| oracle | baseline | s7_047_collision | NOT_LISTED | FLAGGED | T2603386 | T2603386 | 0 | - |  |
| oracle | baseline | s7_048_collision | NOT_LISTED | FLAGGED | UT260046 | UT260046 | 0 | - |  |
| oracle | baseline | s7_057_sibling | NOT_LISTED | FLAGGED | GLL19018 | 6LL19018 | 0 | - |  |
| oracle | baseline | s7_058_sibling | NOT_LISTED | FLAGGED | T18839 | TL8839 | 0 | - |  |
| oracle | baseline | s7_059_sibling | NOT_LISTED | FLAGGED | TLMT703 | TLMT708 | 0 | - |  |
| oracle | baseline | s7_060_sibling | NOT_LISTED | FLAGGED | TS7463 | 1S7463 | 0 | - |  |
| none | baseline | s7_017_misread | FLAGGED | NOT_LISTED | M2P2502 | MZP2502 | 0 | - |  |
| none | baseline | s7_018_misread | FLAGGED | NOT_LISTED | UF26T4082F | UF2674082F | 0 | - |  |
| none | baseline | s7_019_misread | FLAGGED | NOT_LISTED | T2L544 | T21544 | 0 | - |  |
| none | baseline | s7_020_misread | FLAGGED | NOT_LISTED | N260O742 | N2600742 | 0 | - |  |
| none | baseline | s7_021_misread | FLAGGED | NOT_LISTED | UCCGL07 | UCCGL01 | 0 | - |  |
| none | baseline | s7_022_misread | FLAGGED | NOT_LISTED | V2300882 | V2300382 | 0 | - |  |
| none | baseline | s7_023_misread | FLAGGED | NOT_LISTED | LO92402 | L092402 | 0 | - |  |
| none | baseline | s7_024_misread | FLAGGED | NOT_LISTED | 4S6366 | AS6366 | 0 | - |  |
| none | baseline | s7_041_collision | NOT_LISTED | FLAGGED | TG241031C | TG241031C | 0 | - |  |
| none | baseline | s7_042_collision | NOT_LISTED | FLAGGED | DVT197270 | DVT197270 | 0 | - |  |
| none | baseline | s7_043_collision | NOT_LISTED | FLAGGED | HP404 | HP404 | 0 | - |  |
| none | baseline | s7_044_collision | NOT_LISTED | FLAGGED | TAH231704 | TAH231704 | 0 | - |  |
| none | baseline | s7_045_collision | NOT_LISTED | FLAGGED | AGWT25032 | AGWT25032 | 0 | - |  |
| none | baseline | s7_046_collision | NOT_LISTED | FLAGGED | IW0225 | IW0225 | 0 | - |  |
| none | baseline | s7_047_collision | NOT_LISTED | FLAGGED | T2603386 | T2603386 | 0 | - |  |
| none | baseline | s7_048_collision | NOT_LISTED | FLAGGED | UT260046 | UT260046 | 0 | - |  |
| none | baseline | s7_057_sibling | NOT_LISTED | FLAGGED | GLL19018 | 6LL19018 | 0 | - |  |
| none | baseline | s7_058_sibling | NOT_LISTED | FLAGGED | T18839 | TL8839 | 0 | - |  |
| none | baseline | s7_059_sibling | NOT_LISTED | FLAGGED | TLMT703 | TLMT708 | 0 | - |  |
| none | baseline | s7_060_sibling | NOT_LISTED | FLAGGED | TS7463 | 1S7463 | 0 | - |  |
| none | agent_rules | s7_001_clean | FLAGGED | CANT_VERIFY | AGWT25037 | AGWT25037 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_002_clean | FLAGGED | CANT_VERIFY | RH896 | RH896 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_003_clean | FLAGGED | CANT_VERIFY | 45PSA138 | 45PSA138 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_004_clean | FLAGGED | CANT_VERIFY | CTZ19001 | CTZ19001 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_005_clean | FLAGGED | CANT_VERIFY | MYRTAB971 | MYRTAB971 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_006_clean | FLAGGED | CANT_VERIFY | PF8B101 | PF8B101 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_007_clean | FLAGGED | CANT_VERIFY | THE26003AL | THE26003AL | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_008_clean | FLAGGED | CANT_VERIFY | MVT534 | MVT534 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_009_glare | FLAGGED | CANT_VERIFY | AYA2101 | AYA2101 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_010_glare | FLAGGED | CANT_VERIFY | QT1572 | QT1572 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_011_glare | FLAGGED | CANT_VERIFY | NON09 | NON09 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_012_glare | FLAGGED | CANT_VERIFY | W25010 | W25010 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_013_glare | FLAGGED | CANT_VERIFY | TA24665 | TA24665 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_014_glare | FLAGGED | CANT_VERIFY | BL23015 | BL23015 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_015_glare | FLAGGED | CANT_VERIFY | T087J44 | T087J44 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_016_glare | FLAGGED | CANT_VERIFY | GM20173 | GM20173 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_017_misread | FLAGGED | CANT_VERIFY | M2P2502 | MZP2502 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_018_misread | FLAGGED | CANT_VERIFY | UF26T4082F | UF2674082F | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_019_misread | FLAGGED | CANT_VERIFY | T2L544 | T21544 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_020_misread | FLAGGED | CANT_VERIFY | N260O742 | N2600742 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_021_misread | FLAGGED | CANT_VERIFY | UCCGL07 | UCCGL01 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_022_misread | FLAGGED | CANT_VERIFY | V2300882 | V2300382 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_023_misread | FLAGGED | CANT_VERIFY | LO92402 | L092402 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_024_misread | FLAGGED | CANT_VERIFY | 4S6366 | AS6366 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_033_spurious | SUSPECTED_FAKE | CANT_VERIFY | AGI23216 | AGI23216 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_034_spurious | SUSPECTED_FAKE | CANT_VERIFY | BPF251519 | BPF251519 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_035_spurious | SUSPECTED_FAKE | CANT_VERIFY | 18240626 | 18240626 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_036_spurious | SUSPECTED_FAKE | CANT_VERIFY | SIF2676A | SIF2676A | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_037_spurious | SUSPECTED_FAKE | CANT_VERIFY | SIE0116A | SIE0116A | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_038_spurious | SUSPECTED_FAKE | CANT_VERIFY | MNT27015 | MNT27015 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_039_spurious | SUSPECTED_FAKE | CANT_VERIFY | SC05856 | SC05856 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_040_spurious | SUSPECTED_FAKE | CANT_VERIFY | 23440679 | 23440679 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_057_sibling | NOT_LISTED | CANT_VERIFY | GLL19018 | 6LL19018 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_058_sibling | NOT_LISTED | CANT_VERIFY | T18839 | TL8839 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_059_sibling | NOT_LISTED | CANT_VERIFY | TLMT703 | TLMT708 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_060_sibling | NOT_LISTED | CANT_VERIFY | TS7463 | 1S7463 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_001_clean | FLAGGED | CANT_VERIFY | AGWT25037 | AGWT25037 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_002_clean | FLAGGED | CANT_VERIFY | RH896 | RH896 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_003_clean | FLAGGED | CANT_VERIFY | 45PSA138 | 45PSA138 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_004_clean | FLAGGED | CANT_VERIFY | CTZ19001 | CTZ19001 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_005_clean | FLAGGED | CANT_VERIFY | MYRTAB971 | MYRTAB971 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_006_clean | FLAGGED | CANT_VERIFY | PF8B101 | PF8B101 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_007_clean | FLAGGED | CANT_VERIFY | THE26003AL | THE26003AL | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_008_clean | FLAGGED | CANT_VERIFY | MVT534 | MVT534 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_009_glare | FLAGGED | CANT_VERIFY | AYA2101 | AYA2101 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_010_glare | FLAGGED | CANT_VERIFY | QT1572 | QT1572 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_011_glare | FLAGGED | CANT_VERIFY | NON09 | NON09 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_012_glare | FLAGGED | CANT_VERIFY | W25010 | W25010 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_013_glare | FLAGGED | CANT_VERIFY | TA24665 | TA24665 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_014_glare | FLAGGED | CANT_VERIFY | BL23015 | BL23015 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_015_glare | FLAGGED | CANT_VERIFY | T087J44 | T087J44 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_016_glare | FLAGGED | CANT_VERIFY | GM20173 | GM20173 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_017_misread | FLAGGED | CANT_VERIFY | M2P2502 | MZP2502 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_018_misread | FLAGGED | CANT_VERIFY | UF26T4082F | UF2674082F | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_019_misread | FLAGGED | CANT_VERIFY | T2L544 | T21544 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_020_misread | FLAGGED | CANT_VERIFY | N260O742 | N2600742 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_021_misread | FLAGGED | CANT_VERIFY | UCCGL07 | UCCGL01 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_022_misread | FLAGGED | CANT_VERIFY | V2300882 | V2300382 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_023_misread | FLAGGED | CANT_VERIFY | LO92402 | L092402 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_024_misread | FLAGGED | CANT_VERIFY | 4S6366 | AS6366 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_033_spurious | SUSPECTED_FAKE | CANT_VERIFY | AGI23216 | AGI23216 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_034_spurious | SUSPECTED_FAKE | CANT_VERIFY | BPF251519 | BPF251519 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_035_spurious | SUSPECTED_FAKE | CANT_VERIFY | 18240626 | 18240626 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_036_spurious | SUSPECTED_FAKE | CANT_VERIFY | SIF2676A | SIF2676A | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_037_spurious | SUSPECTED_FAKE | CANT_VERIFY | SIE0116A | SIE0116A | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_038_spurious | SUSPECTED_FAKE | CANT_VERIFY | MNT27015 | MNT27015 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_039_spurious | SUSPECTED_FAKE | CANT_VERIFY | SC05856 | SC05856 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_040_spurious | SUSPECTED_FAKE | CANT_VERIFY | 23440679 | 23440679 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_057_sibling | NOT_LISTED | CANT_VERIFY | GLL19018 | 6LL19018 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_058_sibling | NOT_LISTED | CANT_VERIFY | T18839 | TL8839 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_059_sibling | NOT_LISTED | CANT_VERIFY | TLMT703 | TLMT708 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_060_sibling | NOT_LISTED | CANT_VERIFY | TS7463 | 1S7463 | 1 | confirm_batch | batch_gate |


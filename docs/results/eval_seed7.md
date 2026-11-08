# StripCheck evaluation, seed 7 (n = 60)

Created 2026-11-08T06:09:41.143312+00:00. The golden set renders 60 cartons from real CDSCO alert rows (local database: 6923 alerts). Every image carries the banner DEMO PROP - NOT A MEDICINE. Misread and sibling items simulate an OCR error by rendering the misread string; the oracle answers from the printed truth. Thresholds were not tuned on this seed.

Scenario mix: clean 8, glare 8, misread 8, qr 8, spurious 8, collision 8, genuine 8, sibling 4.

Perception (shared by all arms, read once per image): engines {'RapidOCR PP-OCRv6-small': 60}, errors 0, batch read equal to the rendered text on 60/60 images, median 1.332 s per image. Latency per pack is perception time plus the arm's own reasoning time.

Ollama at the hybrid run: up=True, model qwen2.5:3b present=True.

## Table A: headline metrics, HITL = oracle

Rates as value (k/n; Wilson 95% interval).

| Metric | Baseline (lookup) | Agent (rules) | Agent (hybrid) |
|---|---|---|---|
| Hit recall | 0.80 (32/40; 0.65-0.90) | 0.82 (33/40; 0.68-0.91) | 0.82 (33/40; 0.68-0.91) |
| Hit recall (clean + QR) | 1.00 (16/16; 0.81-1.00) | 0.75 (12/16; 0.51-0.90) | 0.75 (12/16; 0.51-0.90) |
| Type accuracy | 1.00 (32/32; 0.89-1.00) | 1.00 (33/33; 0.90-1.00) | 1.00 (33/33; 0.90-1.00) |
| False-alarm rate (all NOT_LISTED) | 0.60 (12/20; 0.39-0.78) | 0.00 (0/20; 0.00-0.16) | 0.00 (0/20; 0.00-0.16) |
| False-alarm rate (collisions) | 1.00 (8/8; 0.68-1.00) | 0.00 (0/8; 0.00-0.32) | 0.00 (0/8; 0.00-0.32) |
| False-alarm rate (siblings) | 1.00 (4/4; 0.51-1.00) | 0.00 (0/4; 0.00-0.49) | 0.00 (0/4; 0.00-0.49) |
| Abstention rate | 0.00 (0/60; 0.00-0.06) | 0.00 (0/60; 0.00-0.06) | 0.00 (0/60; 0.00-0.06) |
| Overall accuracy | 0.67 (40/60; 0.54-0.77) | 0.88 (53/60; 0.78-0.94) | 0.88 (53/60; 0.78-0.94) |
| Questions per pack | 0.00 | 0.55 | 0.55 |
| Steps per pack | 1.0 | 7.8 | 7.8 |
| Latency median / mean / p95 (s) | 1.33 / 1.36 / 1.82 | 1.44 / 1.48 / 1.89 | 1.51 / 3.52 / 9.64 |
| Reasoning only, median / p95 (s) | 0.000 / 0.000 | 0.125 / 0.208 | 0.097 / 8.269 |
| Safety violations | 0 | 0 | 0 |
| LLM steps / fallback steps | 0 / 0 | 0 / 0 | 27 / 0 |

## Table B: headline metrics, HITL = none

Rates as value (k/n; Wilson 95% interval).

| Metric | Baseline (lookup) | Agent (rules) | Agent (hybrid) |
|---|---|---|---|
| Hit recall | 0.80 (32/40; 0.65-0.90) | 0.12 (5/40; 0.05-0.26) | 0.12 (5/40; 0.05-0.26) |
| Hit recall (clean + QR) | 1.00 (16/16; 0.81-1.00) | 0.31 (5/16; 0.14-0.56) | 0.31 (5/16; 0.14-0.56) |
| Type accuracy | 1.00 (32/32; 0.89-1.00) | 1.00 (5/5; 0.57-1.00) | 1.00 (5/5; 0.57-1.00) |
| False-alarm rate (all NOT_LISTED) | 0.60 (12/20; 0.39-0.78) | 0.00 (0/20; 0.00-0.16) | 0.00 (0/20; 0.00-0.16) |
| False-alarm rate (collisions) | 1.00 (8/8; 0.68-1.00) | 0.00 (0/8; 0.00-0.32) | 0.00 (0/8; 0.00-0.32) |
| False-alarm rate (siblings) | 1.00 (4/4; 0.51-1.00) | 0.00 (0/4; 0.00-0.49) | 0.00 (0/4; 0.00-0.49) |
| Abstention rate | 0.00 (0/60; 0.00-0.06) | 0.52 (31/60; 0.39-0.64) | 0.52 (31/60; 0.39-0.64) |
| Overall accuracy | 0.67 (40/60; 0.54-0.77) | 0.37 (22/60; 0.26-0.49) | 0.37 (22/60; 0.26-0.49) |
| Questions per pack | 0.00 | 0.52 | 0.52 |
| Steps per pack | 1.0 | 7.6 | 7.6 |
| Latency median / mean / p95 (s) | 1.33 / 1.36 / 1.82 | 1.45 / 1.49 / 1.91 | 1.52 / 3.32 / 12.78 |
| Reasoning only, median / p95 (s) | 0.000 / 0.000 | 0.132 / 0.190 | 0.115 / 11.363 |
| Safety violations | 0 | 0 | 0 |
| LLM steps / fallback steps | 0 / 0 | 0 / 0 | 30 / 0 |

## Table C: correct verdicts per scenario (k/n), HITL = oracle

| Scenario | Baseline (lookup) | Agent (rules) | Agent (hybrid) |
|---|---|---|---|
| clean | 8/8 | 7/8 | 7/8 |
| glare | 8/8 | 7/8 | 7/8 |
| misread | 0/8 | 6/8 | 6/8 |
| qr | 8/8 | 5/8 | 5/8 |
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
| qr | 8/8 | 5/8 | 5/8 |
| spurious | 8/8 | 0/8 | 0/8 |
| collision | 0/8 | 8/8 | 8/8 |
| genuine | 8/8 | 8/8 | 8/8 |
| sibling | 0/4 | 1/4 | 1/4 |

## Paired comparison and decision rule

Exact McNemar test on per-item correctness against the baseline. Decision rule (registered at R2): adopt the agent if its collision false-alarm rate is at least 50% lower (relative) than the baseline's and its hit recall is no more than 5 points lower.

| Arm | HITL | Agent-only correct | Baseline-only correct | McNemar p | Decision | Detail |
|---|---|---|---|---|---|---|
| Agent (rules) | oracle | 18 | 5 | 0.010622 | adopt | collision FAR 0.00 vs 1.00 (100% lower); hit recall 0.82 vs 0.80 (2.5 points higher) |
| Agent (hybrid) | oracle | 18 | 5 | 0.010622 | adopt | collision FAR 0.00 vs 1.00 (100% lower); hit recall 0.82 vs 0.80 (2.5 points higher) |
| Agent (rules) | none | 9 | 27 | 0.003933 | do not adopt | collision FAR 0.00 vs 1.00 (100% lower); hit recall 0.12 vs 0.80 (67.5 points lower) |
| Agent (hybrid) | none | 9 | 27 | 0.003933 | do not adopt | collision FAR 0.00 vs 1.00 (100% lower); hit recall 0.12 vs 0.80 (67.5 points lower) |

## Registered predictions (HITL = oracle)

| Prediction | Outcome | Counts |
|---|---|---|
| Clean packs: all arms tie | did not hold | baseline 8/8; agent_rules 7/8; agent_hybrid 7/8 |
| Collisions: baseline false-alarms on every one; agent at most 10% | held | baseline 8/8, agent_rules 0/8 |
| Misreads: baseline misses every flag; agent with oracle recovers at least 80% at no more than 1 question per pack | did not hold | baseline detected 0/8; agent_rules correct 6/8 at 0.75 questions per pack |
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
| oracle | agent_rules | s7_005_clean | FLAGGED | NOT_LISTED | MYRTAB971 | MYRTAB971 | 0 | - |  |
| oracle | agent_rules | s7_015_glare | FLAGGED | NOT_LISTED | T087J44 | T087J44 | 0 | - |  |
| oracle | agent_rules | s7_022_misread | FLAGGED | NOT_LISTED | V2300882 | V2300382 | 0 | - |  |
| oracle | agent_rules | s7_023_misread | FLAGGED | NOT_LISTED | LO92402 | L092402 | 0 | - |  |
| oracle | agent_rules | s7_027_qr | FLAGGED | NOT_LISTED | MBC111 | MBC111 | 0 | - |  |
| oracle | agent_rules | s7_028_qr | FLAGGED | NOT_LISTED | GF292 | GF292 | 0 | - |  |
| oracle | agent_rules | s7_030_qr | FLAGGED | NOT_LISTED | TG251919B | TG251919B | 0 | - |  |
| oracle | agent_hybrid | s7_005_clean | FLAGGED | NOT_LISTED | MYRTAB971 | MYRTAB971 | 0 | - |  |
| oracle | agent_hybrid | s7_015_glare | FLAGGED | NOT_LISTED | T087J44 | T087J44 | 0 | - |  |
| oracle | agent_hybrid | s7_022_misread | FLAGGED | NOT_LISTED | V2300882 | V2300382 | 0 | - |  |
| oracle | agent_hybrid | s7_023_misread | FLAGGED | NOT_LISTED | LO92402 | L092402 | 0 | - |  |
| oracle | agent_hybrid | s7_027_qr | FLAGGED | NOT_LISTED | MBC111 | MBC111 | 0 | - |  |
| oracle | agent_hybrid | s7_028_qr | FLAGGED | NOT_LISTED | GF292 | GF292 | 0 | - |  |
| oracle | agent_hybrid | s7_030_qr | FLAGGED | NOT_LISTED | TG251919B | TG251919B | 0 | - |  |
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
| none | agent_rules | s7_005_clean | FLAGGED | NOT_LISTED | MYRTAB971 | MYRTAB971 | 0 | - |  |
| none | agent_rules | s7_006_clean | FLAGGED | CANT_VERIFY | PF8B101 | PF8B101 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_007_clean | FLAGGED | CANT_VERIFY | THE26003AL | THE26003AL | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_008_clean | FLAGGED | CANT_VERIFY | MVT534 | MVT534 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_009_glare | FLAGGED | CANT_VERIFY | AYA2101 | AYA2101 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_010_glare | FLAGGED | CANT_VERIFY | QT1572 | QT1572 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_011_glare | FLAGGED | CANT_VERIFY | NON09 | NON09 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_012_glare | FLAGGED | CANT_VERIFY | W25010 | W25010 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_013_glare | FLAGGED | CANT_VERIFY | TA24665 | TA24665 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_014_glare | FLAGGED | CANT_VERIFY | BL23015 | BL23015 | 1 | box_photo | the candidate needs more printed product, date or manufacturer evidenc |
| none | agent_rules | s7_015_glare | FLAGGED | NOT_LISTED | T087J44 | T087J44 | 0 | - |  |
| none | agent_rules | s7_016_glare | FLAGGED | CANT_VERIFY | GM20173 | GM20173 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_017_misread | FLAGGED | CANT_VERIFY | M2P2502 | MZP2502 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_018_misread | FLAGGED | CANT_VERIFY | UF26T4082F | UF2674082F | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_019_misread | FLAGGED | CANT_VERIFY | T2L544 | T21544 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_020_misread | FLAGGED | CANT_VERIFY | N260O742 | N2600742 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_021_misread | FLAGGED | CANT_VERIFY | UCCGL07 | UCCGL01 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_022_misread | FLAGGED | NOT_LISTED | V2300882 | V2300382 | 0 | - |  |
| none | agent_rules | s7_023_misread | FLAGGED | NOT_LISTED | LO92402 | L092402 | 0 | - |  |
| none | agent_rules | s7_024_misread | FLAGGED | CANT_VERIFY | 4S6366 | AS6366 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_rules | s7_027_qr | FLAGGED | NOT_LISTED | MBC111 | MBC111 | 0 | - |  |
| none | agent_rules | s7_028_qr | FLAGGED | NOT_LISTED | GF292 | GF292 | 0 | - |  |
| none | agent_rules | s7_030_qr | FLAGGED | NOT_LISTED | TG251919B | TG251919B | 0 | - |  |
| none | agent_rules | s7_033_spurious | SUSPECTED_FAKE | CANT_VERIFY | AGI23216 | AGI23216 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_034_spurious | SUSPECTED_FAKE | CANT_VERIFY | BPF251519 | BPF251519 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_035_spurious | SUSPECTED_FAKE | CANT_VERIFY | 18240626 | 18240626 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_036_spurious | SUSPECTED_FAKE | CANT_VERIFY | SIF2676A | SIF2676A | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_037_spurious | SUSPECTED_FAKE | CANT_VERIFY | SIE0116A | SIE0116A | 1 | box_photo | the candidate needs more printed product, date or manufacturer evidenc |
| none | agent_rules | s7_038_spurious | SUSPECTED_FAKE | CANT_VERIFY | MNT27015 | MNT27015 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_039_spurious | SUSPECTED_FAKE | CANT_VERIFY | SC05856 | SC05856 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_040_spurious | SUSPECTED_FAKE | CANT_VERIFY | 23440679 | 23440679 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_058_sibling | NOT_LISTED | CANT_VERIFY | T18839 | TL8839 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_059_sibling | NOT_LISTED | CANT_VERIFY | TLMT703 | TLMT708 | 1 | confirm_batch | batch_gate |
| none | agent_rules | s7_060_sibling | NOT_LISTED | CANT_VERIFY | TS7463 | 1S7463 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_001_clean | FLAGGED | CANT_VERIFY | AGWT25037 | AGWT25037 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_002_clean | FLAGGED | CANT_VERIFY | RH896 | RH896 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_003_clean | FLAGGED | CANT_VERIFY | 45PSA138 | 45PSA138 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_004_clean | FLAGGED | CANT_VERIFY | CTZ19001 | CTZ19001 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_005_clean | FLAGGED | NOT_LISTED | MYRTAB971 | MYRTAB971 | 0 | - |  |
| none | agent_hybrid | s7_006_clean | FLAGGED | CANT_VERIFY | PF8B101 | PF8B101 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_007_clean | FLAGGED | CANT_VERIFY | THE26003AL | THE26003AL | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_008_clean | FLAGGED | CANT_VERIFY | MVT534 | MVT534 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_009_glare | FLAGGED | CANT_VERIFY | AYA2101 | AYA2101 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_010_glare | FLAGGED | CANT_VERIFY | QT1572 | QT1572 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_011_glare | FLAGGED | CANT_VERIFY | NON09 | NON09 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_012_glare | FLAGGED | CANT_VERIFY | W25010 | W25010 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_013_glare | FLAGGED | CANT_VERIFY | TA24665 | TA24665 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_014_glare | FLAGGED | CANT_VERIFY | BL23015 | BL23015 | 1 | box_photo | the candidate needs more printed product, date or manufacturer evidenc |
| none | agent_hybrid | s7_015_glare | FLAGGED | NOT_LISTED | T087J44 | T087J44 | 0 | - |  |
| none | agent_hybrid | s7_016_glare | FLAGGED | CANT_VERIFY | GM20173 | GM20173 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_017_misread | FLAGGED | CANT_VERIFY | M2P2502 | MZP2502 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_018_misread | FLAGGED | CANT_VERIFY | UF26T4082F | UF2674082F | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_019_misread | FLAGGED | CANT_VERIFY | T2L544 | T21544 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_020_misread | FLAGGED | CANT_VERIFY | N260O742 | N2600742 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_021_misread | FLAGGED | CANT_VERIFY | UCCGL07 | UCCGL01 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_022_misread | FLAGGED | NOT_LISTED | V2300882 | V2300382 | 0 | - |  |
| none | agent_hybrid | s7_023_misread | FLAGGED | NOT_LISTED | LO92402 | L092402 | 0 | - |  |
| none | agent_hybrid | s7_024_misread | FLAGGED | CANT_VERIFY | 4S6366 | AS6366 | 1 | confirm_char | the printed characters or dates could not be confirmed |
| none | agent_hybrid | s7_027_qr | FLAGGED | NOT_LISTED | MBC111 | MBC111 | 0 | - |  |
| none | agent_hybrid | s7_028_qr | FLAGGED | NOT_LISTED | GF292 | GF292 | 0 | - |  |
| none | agent_hybrid | s7_030_qr | FLAGGED | NOT_LISTED | TG251919B | TG251919B | 0 | - |  |
| none | agent_hybrid | s7_033_spurious | SUSPECTED_FAKE | CANT_VERIFY | AGI23216 | AGI23216 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_034_spurious | SUSPECTED_FAKE | CANT_VERIFY | BPF251519 | BPF251519 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_035_spurious | SUSPECTED_FAKE | CANT_VERIFY | 18240626 | 18240626 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_036_spurious | SUSPECTED_FAKE | CANT_VERIFY | SIF2676A | SIF2676A | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_037_spurious | SUSPECTED_FAKE | CANT_VERIFY | SIE0116A | SIE0116A | 1 | box_photo | the candidate needs more printed product, date or manufacturer evidenc |
| none | agent_hybrid | s7_038_spurious | SUSPECTED_FAKE | CANT_VERIFY | MNT27015 | MNT27015 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_039_spurious | SUSPECTED_FAKE | CANT_VERIFY | SC05856 | SC05856 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_040_spurious | SUSPECTED_FAKE | CANT_VERIFY | 23440679 | 23440679 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_058_sibling | NOT_LISTED | CANT_VERIFY | T18839 | TL8839 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_059_sibling | NOT_LISTED | CANT_VERIFY | TLMT703 | TLMT708 | 1 | confirm_batch | batch_gate |
| none | agent_hybrid | s7_060_sibling | NOT_LISTED | CANT_VERIFY | TS7463 | 1S7463 | 1 | confirm_batch | batch_gate |


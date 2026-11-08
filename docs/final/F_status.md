# Agent F status: final numbers in report, slides, guide (run 2 + run-1 disclosure)

- [x] Read results (run 1 e283407, run 2 current), D25, C_status
- [x] Paper: abstract, 06_evaluation, 07_experiment, 08_limitations, 09_conclusion, deviations table, run-1 disclosure
- [x] Paper build (0 undefined refs, 8-12 pages), PNG check
- [x] Slides update + build
- [x] Guide: amber boxes, viva answers, eval-results box
- [x] Guide structure check (HTML, phone width)

## Notes
- Paper: run-1 values hand-typed only in paper/run1_results.tex (from e283407). R-C computed in main.tex (\ifRCholds) from generated macros: holds. New subsection 'A first run and three fixes' (sec:runs) + Table tab:runs. Deviations row for D25. Author line split (was overfull 115pt). Build: 12 pages, 0 undefined, 0 BibTeX warnings; only overfull is the generated predictions table (5.8pt).
- Lesson: backslashes in bash heredocs get mangled in this tool; use Write/Edit tools or scripts written with Write.
- Slides: results slide now 4 arms (lookup, rules, hybrid, rules-skipped) with p95; outcome text R-A, R-C, predictions, run-1 line; new backup "run 1, the three fixes and run 2"; per-scenario backup split in two frames (3 arms overlapped); deviations + R2 backup updated; observability row mentions OTel/Phoenix. Build: 20 pages, 0 undefined; overfull vbox on title (pre-existing), results (11.7pt, renders fine), concepts (1.2pt).
- Guide: arch figure boxes (Ollama hybrid, Phoenix optional), D18 amber box, sec 8 planner card, sec 9 table/figure/fixed-gap box, verifier caption + R2 + failsafes, sec 12 cards/figure/R-B not run, eval-results box filled (run 2 tables A/B, decisions, predictions, run-1 disclosure), sec 13 row, viva Q2/8/9/10/15/16/17, glossary, footer.
- Guide check: HTML parser balanced, 0 script tags, one id="eval-results". Phone 375 px (headless Edge iframe harness): page scrollWidth <= 375 after adding `.grid2>*,.grid3>*,.grid4>*{min-width:0}` (pre-existing overflow from the section 3 <pre> card); wide tables scroll inside their own box as before.

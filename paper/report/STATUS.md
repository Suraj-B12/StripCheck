# Report status checklist (paper/report)

Build: `cd paper/report; latexmk main.tex` -> `paper/report/build/main.pdf` (latexmkrc sets out_dir=build, bibtex_fudge=0).

## Skeleton (agent: skeleton) -- DONE
- [x] directories created (chapters/, figures/, tools/)
- [x] main.tex: template preamble lines 1-146 verbatim; only the project block and \guidancefalse changed
- [x] StripCheck additions block after the preamble: bibname=References + TOC entry via \apptocmd, \input ../generated/stats, ../generated/results (\res{} helper), ../run1_results, verdict label macros, \todo, \graphicspath{figures/}
- [x] title page + certificate verbatim from the template (names/USNs via macros); template has no declaration/acknowledgement pages
- [x] abstract -> chapters/ch00_abstract.tex; abbreviations -> chapters/ch00_abbreviations.tex
- [x] chapters ch01..ch10 placeholders with the template's exact section titles and labels sec:<key>-<slug>
- [x] appendices appA_contribution (app:contrib), appB_setup (app:run), appC_traces (app:traces), appD_prompts (app:prompts)
- [x] logo.png copied
- [x] latexmkrc + first compile OK (exit 0, 24 pages, no undefined refs)
- [x] GUIDANCE.md extracted (tools/extract_guidance.py)
- NOTE: \TeamNo is TEAMNO (main.tex, line marked ">>> TEAM NUMBER")
- NOTE: ch01 has a SKELETON-ONLY \nocite{cdsco2026portal}; delete it once chapters cite sources
- NOTE: template certificate paragraph gives a 7pt overfull hbox with our names (template text, left as is)
- NOTE: appendix headings render "CHAPTER A" because the template's chapter title format is kept verbatim

## FACTS.md (agent: facts) -- DONE
- [x] paper/report/FACTS.md written (21 sections: data, requirements, architecture, loop and bounds, verifier R1-R10, tools, memory, HITL kinds, safety, observability, eval design, run-1 and run-2 results, deviations, limitations, contributions, versions, commands, verbatim prompts, in-progress work, discrepancies, cite keys)
- [x] every number names its source; uncertain items marked UNVERIFIED
- NOTE: FACTS.md section 20 lists paper claims that the code does not support (JSONL token counts, trace event names) -- writers must use the corrected wording
- NOTE: live thinking / conversational questions (docs/final/live_thinking_contract.md) are uncommitted; describe only if the lead confirms (FACTS.md section 19)

## Figures (agent: figures) -- DONE
- [x] tools/make_figures.py (matplotlib, vector PDF 6.0 in wide, CMU Serif, Type 3 fonts, CSV beside each PDF)
- [x] fig_alerts_per_year, fig_alert_timing (local DB, read-only)
- [x] fig_headline_seed7, fig_scenarios_seed7, fig_hitl_seed7, fig_latency_seed7 (runs/eval_seed7_latest.json)
- [x] fig_run1_run2 (git show e283407:docs/results/eval_seed7.md vs run 2)
- [x] seed-1 eval run in the clean clone on a scratch DB copy (paper/generated unchanged); data/eval_seed1.md + .json + run log; fig_seeds
- [x] every PDF rendered at 150 dpi and inspected
- [x] figures/FIGURES.md (numbers, sources, captions); FACTS.md section 22
- NOTE: include figures at natural size (6.0 in) or width=0.96\textwidth; label "Not listed" = data scenario `genuine`

## Front matter, Ch1, Ch10 (agent: intro-conclusion) -- IN PROGRESS
- [ ] chapters/ch00_abstract.tex (one paragraph, 200-300 words, keywords)
- [ ] chapters/ch00_abbreviations.tex
- [ ] chapters/ch01_introduction.tex (4-6 pages)
- [ ] chapters/ch10_conclusion.tex (1-2 pages)
- [ ] compile + page range

## Chapters 7 and 8 (agent: ch07-ch08) -- IN PROGRESS
- [ ] figures/fig_phoenix_trace.png (cropped from docs/trace/02_phoenix_run1_misread_trace.png by tools/crop_trace.py) with TikZ callouts
- [ ] chapters/ch07_evaluation.tex
- [ ] chapters/ch08_experimentation.tex
- [ ] full latexmk build, page range noted here

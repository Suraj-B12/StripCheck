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

## Front matter, Ch1, Ch10 (agent: intro-conclusion) -- DONE
- [x] chapters/ch00_abstract.tex (one paragraph, about 295 words, 6 keywords, \res macros, no cites)
- [x] chapters/ch00_abbreviations.tex (38 entries; CI = Continuous Integration as used in ch03/ch06; added GS1, HTTP, ISO, PDF, SDK, TCP, UTC)
- [x] chapters/ch01_introduction.tex (fig:intro-alerts-per-year uses fig_alerts_per_year.pdf; tab:intro-verdicts, tab:intro-capabilities)
- [x] chapters/ch10_conclusion.tex (tab:concl-objectives revisits objectives 1-6; 5 future-work items tied to ch09 limitations)
- [x] compile (private outdir, exit 0, 99 pages): abstract p. iii, abbreviations p. xii, Ch1 pp. 1-6, Ch10 pp. 60-61
- NOTE: only undefined ref in the build is tab:design-bounds (ch03 -> ch04, owned by ch03-ch04 agent)
- NOTE: build/ was being written by another agent at the same time (corrupt aux); compile in a separate -outdir when agents run in parallel

## Chapters 7 and 8 (agent: ch07-ch08) -- DONE
- [x] figures/fig_phoenix_trace.png (cropped from docs/trace/02_phoenix_run1_misread_trace.png by tools/crop_trace.py) with TikZ callouts
- [x] chapters/ch07_evaluation.tex (tracing + Phoenix fig, eval set table, metrics, baselines, results table from \res macros, 3 figures, error table)
- [x] chapters/ch08_experimentation.tex (H1/R-A, H2/R-C, setup table, seed 1 vs seed 7, run 1 vs run 2 + D25 disclosure, predictions table, decision D26)
- [x] full latexmk build OK (exit 0, 98 pages; built with -outdir in scratchpad because concurrent builds in build/ corrupted the .aux). Ch7 = pages 41-48, Ch8 = pages 49-53 (arabic numbering). No overfull boxes in ch07/ch08. Only unresolved ref in the whole report: tab:design-bounds (ch04, other agent).
- NOTE: all figures in ch07/ch08 at 0.8\linewidth. Ch7 is about 7.3 pages, over the 4-6 page aim, mostly the full-page results table (tab:eval-results); trim the HITL=none latency/LLM rows if the page budget is enforced.
- NOTE: hand-typed numbers (reasoning p95 0.103 s, Phoenix span times, all seed-1 values) are sourced in FACTS.md sections 22-23.

## Ch09 + appendices A-D (agent: limitations-appendices) -- DONE
- [x] ch09_limitations.tex (limitations, failure-mode/guardrail risk table, ethics)
- [x] appA_contribution.tex (from paper/sections/10_contributions.tex)
- [x] appB_setup.tex (README commands; no keys)
- [x] appC_traces.tex (run1, run2 JSONL; no-HITL eval record; Phoenix PNGs copied to figures/fig_phoenix_*.png)
- [x] appD_prompts.tex (verbatim prompts from core/llm.py HEAD; no LLM judge, scoring against manifest labels)
- [x] compile + page range: full build exit 0, 97 pages (built in a scratch out_dir to avoid clashing with parallel builds in build/). Ch9 = printed pp. 54-58 (5 pp., over the 2-3 page budget because of the 12 pt template and the 14-row risk table, now a top float in footnotesize); App. A 72, B 73-76, C 77-82, D 83-85.
- NOTE: no overfull boxes left in ch09/appA-D; remaining undefined ref tab:design-bounds is in ch03 (owned by ch03-ch04 agent, table to be added in ch04)
- NOTE: Phoenix screenshots in figures/fig_phoenix_trace_list.png and fig_phoenix_run1_trace.png are byte-identical copies of docs/trace/01_*.png and 02_*.png

## Chapters 5 and 6 (agent: ch05-ch06) -- DONE
- [x] figures/fig_ui_check.png in place (used as fig:ui-check). Phoenix figure is owned by ch07; ch05 points to sec:eval-tracing-and-monitoring and app:traces
- [x] chapters/ch05_concepts.tex (tab:concepts matrix; evidence per concept with real trace excerpts lst:trace-run1, lst:branch-b, lst:trace-run2; bonus concepts)
- [x] chapters/ch06_implementation.tex (tab:stack versions, portal sync + Latin-1 JSON parsing + tab:ingest, alg:loop, tab:tools, OCR on Windows/macOS, eq:channel noisy-channel ranking, grading, lst:prompt, tab:bounds, tab:verifier, templates, API + clients + fig:ui-check, tab:modules)
- [x] facts checked against HEAD code and a read-only DB query; FACTS.md section 25 (snapshot count corrected to 93 NSQ + 15 spurious current + 3 superseded)
- [x] compiled with latexmk -outdir=build_ch0506 (separate dir to avoid racing; exit 0; no errors, no overfull boxes or undefined refs in ch05/ch06). Pages: Chapter 5 = printed 21-25 (about 4.5 pages), Chapter 6 = printed 26-34 (9 pages, over the 5-7 budget because of 6 tables, the algorithm and the figure; candidates to cut if needed: tab:ingest, fig:ui-check, lst:prompt since Appendix D has it)
- NOTE: floats in ch05/ch06 use [htbp] (with [H] they left half-empty pages)
- NOTE: the Bash tool halves backslashes in heredocs/inline scripts on this machine ("\b" became a backspace, "\f" a form feed); use the Edit tool or bytes([92]) in scripts when writing LaTeX
- NOTE: build_ch0506/ is a scratch build dir that can be deleted

## Chapter 2 literature (agent: ch02) -- DONE
- [x] chapters/ch02_literature.tex written (4 template sections; 6 themed subsections; tab:lit-themes, tab:lit-compare)
- [x] every \cite key (79) checked against ../references.bib; facts in FACTS.md section 24
- [x] whole report compiled with latexmk (separate -outdir build_ch02, since removed, to avoid racing other agents; exit 0, 98+ pages); Chapter 2 = printed pages 7-12 (about 5.3 pages)
- NOTE: a concurrent compile left build/main.aux corrupted ("Extra }" at l.576); delete build/main.aux before the next normal build if it recurs
- NOTE: ch07_evaluation.tex line 18 reads "begingroupsloppy" (lost backslashes; earlier it held a U+0008 char); owner ch07 agent

## Ch03 requirements + Ch04 design (agent: ch03-ch04) -- DONE
- [x] ch03_requirements.tex (stakeholders, FR1-FR10 with tests, NFR1-NFR9, data sources table, hardware/software paragraph pointing to tab:stack, feasibility)
- [x] ch04_design.tex: TikZ architecture (fig:arch, two lanes), TikZ decision flow (fig:design-flow: decisions, branch points (b)/(c), send-back, verifier gate, bounds box), component subsections, tab:design-patterns, tab:design-state, tab:design-bounds, tab:design-dataflow (walkthrough LM24088 -> LM2408B, invented record)
- [x] compiled (latexmk, private outdir), pages rendered to PNG at 110 dpi and inspected; no overfull boxes or undefined refs from ch03/ch04
- [x] FACTS.md section 26 (facts first used by ch03/ch04)
- Pages (build of 2026-11-13): Ch3 pp. 13-17 (5 pages, budget 3-4); Ch4 pp. 18-26 (9 pages, budget 5-7; the architecture figure takes a float page of its own)
- NOTE: floats in ch03/ch04 use [!htbp] (not [H]) to avoid half-empty pages; tables locally allow line breaks after underscores in \texttt
- NOTE: the shared build/ dir had a corrupt main.aux from a concurrent compile ("Missing \begin{document}"); delete build/main.aux if latexmk fails there

## Assemble and build (agent: assemble-build) -- DONE
- [x] include order checked (ch00 abstract/abbrev, ch01-ch10, references, appA-D); bibtex 0 warnings; all graphics found; 0 undefined refs/cites; latexmk exit 0 in build/ (stale corrupt build/main.aux deleted first) and in a scratch outdir
- [x] fixes: xurl (2 long WHO/Seattle URLs in refs), emergencystretch 2em (certificate line), short captions for tab:ingest and tab:eval-results (List of Tables overflow), abbreviations tabular -> longtable (overfull vbox 26.6 pt)
- [x] measured: 98 PDF pages total (14 front matter i-xiv, 84 arabic). Body Ch1 p.1 to Ch10 p.60 = 60 pages, 10 over the 50 cap. Per chapter vs template max: Ch1 6/6, Ch2 6/6, Ch3 5/4 (+1), Ch4 9/7 (+2), Ch5 5/4 (+1), Ch6 9/7 (+2), Ch7 8/6 (+2), Ch8 5/4 (+1), Ch9 5/3 (+2), Ch10 2/2
- [x] overfull boxes > 5 pt: none left (one 1.2 pt in ch03 line 95 table cell "Distributor")
- NOTE: title page still shows TEAMNO (\TeamNo in main.tex line 46) -- needs the real team number
- NOTE: figures/fig_alert_timing.pdf and fig_headline_seed7.pdf are not used by any chapter
- NOTE: OMS/cmtt font substitution for a \{ inside \texttt in ch04 line 109 (brace drawn from cmsy; cosmetic)

## Reviewer findings pass (agent: review-fixes) -- DONE
- [x] numbers: CPU/GPU device claims, held-out wording, seed-1 lookup explanation, batch strings policy, two machines OS, pairing token, ch07 number-source sentence
- [x] figures: UI screenshot, Phoenix crops, data plots at natural size, quarantine note, TikZ label gaps, root-span durations, fig8.2 labels, appC listings, fig1.1 grid, Distributor column, cmtt brace
- [x] prose: ch09 alarm claim, CDSCO policy cite, sibling-frequency claims, ch1/ch2 duplication, repeated sentences, LLM-Modulo wording, future work 'most', SFAKE note, appD opener, commit pinning
- [x] page budget: main body <= 50 pages
- [x] rebuild + render changed figure pages
- [x] (resumed 13 Nov 09:15) found number/figure/prose fixes already applied in sources by the earlier pass; rebuild gave 0 errors but main body 63 pp (Ch1 p1 to Ch10 end p63)
- [x] moved 10 floats to new Appendix E (chapters/appE_supplement.tex, app:supp): tab:req-stakeholders, tab:design-state, tab:design-bounds, tab:tools, fig:ui-check, tab:eval-mix, fig:eval-hitl, fig:eval-latency, fig:exp-seeds, tab:lim-risks; backup of chapters before the move in scratchpad/chapters_backup_review
- [x] update in-text refs to say Appendix E; trim prose per chapter; rebuild to <= 50 pp
- [x] in-text refs updated (each moved float is cited as "in Appendix E"); prose trimmed in Ch1, 2, 3, 4, 5, 6, 7, 8, 9 (duplicates removed, cross-references instead); tab:exp-setup also moved to App. E with its content in the Ch8 text
- [x] Fig 4.1 'image' label moved off 'images, answer' (pos=0.72); App. E floats pinned with [H]
- [x] FACTS.md section 27 (Ollama log: GPU in the seed-1 run; seed-7 device not recorded)
- [x] build: latexmk exit 0, 0 errors, 0 undefined refs/cites, 0 overfull boxes, bibtex 0 warnings. Main body Ch1 p.1 to Ch10 end p.49 = 49 pages (Ch1 1-5, Ch2 6-10, Ch3 11-15, Ch4 16-23, Ch5 24-27, Ch6 28-34, Ch7 35-40, Ch8 41-44, Ch9 45-47, Ch10 48-49); References p.50; App. A 61, B 62, C 67, D 74, E 77
- NOTE: the title page no longer prints a team number (\TeamNo is defined in main.tex but unused); add it to the title block if the course lead assigns one

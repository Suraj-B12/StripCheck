Status: COMPLETE

Checklist:
- [x] Q1 Reject option and selective prediction (Chow 1970; El-Yaniv and Wiener 2010; Geifman and El-Yaniv 2017; Wen et al. 2025 TACL)
- [x] Q2 Learning to defer and human-AI teams (Madras 2018; Mozannar and Sontag 2020; Bansal 2021; automation bias)
- [x] Q3 Hallucination, grounding, attribution, guardrails
- [x] Q4 Risk communication in consumer health tools (false reassurance, "not found", colour semantics)
- [x] Q5 Governance (WHO, ICMR, DPDP Act/Rules, MDR 2017 SaMD status)

# Abstention, Human-in-the-Loop and Safety for StripCheck (notes; today = 25 Oct 2026)

## Q1 Reject option and selective prediction

### Takeaway
Abstention has a 55-year theoretical pedigree (Chow 1970 onward) framed as a risk-coverage trade-off: a system may refuse some inputs to reduce error on those it answers. Modern deep-learning (Geifman and El-Yaniv 2017) and LLM (Wen et al. 2025) work treats abstention as a first-class output, which directly legitimises StripCheck's CANT_VERIFY verdict.

### Cited Findings
- Chow 1970 is the origin of the "reject option" / error-reject trade-off. Only bibliographic metadata was confirmed (Crossref record: C. Chow, "On optimum recognition error and reject tradeoff", IEEE Trans. Information Theory 16(1):41-46, 1970, DOI 10.1109/TIT.1970.1054406). The IEEE page did not render, so the abstract/rule was NOT read; the claim that the optimal rule rejects when the posterior is too low is background knowledge and must be verified before citing it with specifics. Relevance: StripCheck's CANT_VERIFY is a reject option whose "cost" is a missed counterfeit versus a false alarm. — [Crossref record](https://api.crossref.org/works/10.1109/TIT.1970.1054406)
- El-Yaniv and Wiener 2010 (JMLR 11(53):1605-1641) study selective classification (classification with a reject option) and formalise the risk-coverage (RC) trade-off: coverage = fraction of inputs answered; the aim is to characterise and achieve optimal or near-optimal RC trade-offs for noise-free models. The abstract does not state specific theorems. Relevance: gives the evaluation vocabulary StripCheck should report (coverage = share of strips receiving a verdict other than CANT_VERIFY; selective risk = error among answered strips). — [JMLR page](https://jmlr.org/papers/v11/el-yaniv10a.html)
- Geifman and El-Yaniv 2017 (NeurIPS 2017; arXiv:1705.08500, submitted 23 May 2017) give a method that builds a selective classifier from a trained deep network so a user-specified risk level is met with high probability; it thresholds the max-softmax "softmax response". Headline: 2% top-5 ImageNet error guaranteed with probability 99.9% at almost 60% coverage. (Softmax-response detail comes from search-result text, not the opened arXiv abstract; NeurIPS page range 4878-4887 also from search text, unverified.) Relevance: shows a principled way to set an abstention threshold against a target error; StripCheck's OCR/VLM confidence and corroboration-field agreement could be calibrated the same way. — [arXiv abstract](https://arxiv.org/abs/1705.08500)
- Wen et al. 2025 (TACL 13:529-556, DOI 10.1162/tacl_a_00754) survey abstention in LLMs, defined as "the refusal of large language models (LLMs) to provide an answer", as a means to reduce hallucination and improve safety. They organise work through three lenses: the query, the model, and human values; and flag open questions on abstention as a meta-capability and context-specific tuning. Relevance: positions StripCheck's rule-based verifier (query-level: unreadable image; model-level: low confidence/disagreement; values-level: safety of health advice) in the current taxonomy. — [ACL Anthology](https://aclanthology.org/2025.tacl-1.26)

- Cocchieri, Ragazzi, Tagliavini and Moro, "LLMs (Almost) Never Abstain Under Medical Uncertainty", Proc. 64th Annual Meeting of the ACL (Vol. 1 Long Papers), San Diego, July 2026, pp.29573-29613, DOI 10.18653/v1/2026.acl-long.1365: MedQAbstain converts medical MCQA sets into abstention tests (gold answer removed, "I abstain" option added) and finds "state-of-the-art LLMs systematically overcommit", rarely abstaining even when the question is hidden. Abstract gives no figures; PDF not read. Relevance: the most recent evidence that LLM self-abstention is unreliable, supporting StripCheck's design in which abstention is enforced by a deterministic verifier and rule fallback, not left to the small local LLM. — [ACL Anthology](https://aclanthology.org/2026.acl-long.1365/)
- Search-snippet only (not opened, do not cite without verification): "Do Large Language Models Know When Not to Answer in Medical QA?" (UncertaiNLP workshop 2025, conformal prediction + abstention); SelectLLM (NeurIPS 2025, selective-prediction-aware fine-tuning).

### Inferences
- StripCheck's CANT_VERIFY is a selective-prediction reject option; its paper should report a risk-coverage curve over test strips (inference, not in sources).
- Because the verdict set is asymmetric (a false NOT_LISTED is far costlier than a false CANT_VERIFY), a cost-sensitive Chow-style threshold, set conservatively, is the right framing (inference).

### Gaps
- Chow 1970 content not read (IEEE page empty). El-Yaniv and Wiener's specific theorems not read (abstract only). No source yet on abstention calibrated for OCR pipelines specifically.

## Q2 Learning to defer and human-AI teams

### Takeaway
Learning-to-defer extends rejection to account for a human downstream, while human-factors research shows people over-rely on automated advice, and AI explanations can raise acceptance regardless of correctness. This supports StripCheck's ask-the-human-when-a-character-is-in-doubt step but warns that the human step must be designed against automation bias.

### Cited Findings
- Madras, Pitassi and Zemel (NeurIPS 2018; arXiv:1711.06664, rev. 7 Sep 2018) define "learning to defer", extending rejection learning to account for how the downstream decision-maker behaves, including biased or inconsistent humans; they claim deferral can make systems more accurate and less biased. No numbers in the abstract. Relevance: motivates a human-in-the-loop that is modelled, not just bolted on. — [arXiv abstract](https://arxiv.org/abs/1711.06664)
- Mozannar and Sontag (ICML 2020; arXiv:2006.01862) learn jointly a classifier and a rejector from samples of the expert's decisions, via reduction to cost-sensitive learning with a consistent surrogate loss generalising cross-entropy. Relevance: formal basis for deciding when StripCheck should ask the user to read a doubtful character versus decide itself. — [arXiv abstract](https://arxiv.org/abs/2006.01862)
- Bansal et al. (CHI 2021; arXiv:2006.14779) found AI help produced complementary team gains, but explanations did not increase them and increased acceptance of AI recommendations "regardless of its correctness". Relevance: challenges showing rich rationale to users; StripCheck's cited, templated verdict should be paired with a prompt to compare against the physical strip. — [arXiv abstract](https://arxiv.org/abs/2006.14779)
- Parasuraman and Manzey (Human Factors 52(3):381-410, 2010, DOI 10.1177/0018720810376055): automation bias produces omission and commission errors when decision aids are imperfect, affects novices and experts, and is not prevented by training or instructions. Relevance: a consumer reading "NOT_LISTED" may omit own checks; justifies design (not warnings alone) to counter reliance. — [TU Berlin DepositOnce record](https://depositonce.tu-berlin.de/items/0c787d91-6021-480b-a333-009e0d1d0092/full)
- Goddard, Roudsari and Wyatt (JAMIA 19(1):121-127, 2012, DOI 10.1136/amiajnl-2011-000089, PMID 21685142): systematic review of automation bias in clinical decision support; of 13,821 retrieved papers 74 met inclusion. Mediators: user factors, trust/confidence, workload/time pressure. Mitigators: training, accountability, design such as screen placement, updated confidence levels, and giving information rather than recommendations. (Figures from a fetch-tool summary of the Europe PMC record; abstract not reproduced verbatim.) Relevance: directly supports StripCheck presenting evidence (matched fields, source list, date) rather than an imperative recommendation. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%22automation%20bias%22%20AND%20AUTH:%22Goddard%20K%22%20AND%20PUB_YEAR:2012&format=json&resultType=core)

- Buçinca, Malaya and Gajos, "To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-assisted Decision-making", Proc. ACM Hum.-Comput. Interact. 5(CSCW1), pp.1-21, 2021, DOI 10.1145/3449287 (arXiv submission 19 Feb 2021): N=199 experiment; three cognitive forcing designs "significantly reduced overreliance" relative to simple explainable-AI approaches, but the most effective designs were rated least favourably, and benefits were larger for people with higher Need for Cognition. Relevance: a forced step (e.g. user must confirm the printed batch characters before the lookup) is evidence-backed against rubber-stamping, at a usability cost StripCheck should measure. — [arXiv abstract](https://arxiv.org/abs/2102.09692); [Crossref record](https://api.crossref.org/works/10.1145/3449287)

### Inferences
- Asking only when a character is genuinely in doubt (rather than always) balances Madras/Mozannar deferral against alert fatigue; automation-bias literature argues for presenting the user's own photo crop beside the reading (inference).

### Gaps
- No human-subjects evidence on consumers confirming OCR characters; the effect of confirmation prompts on rubber-stamping is an open question for StripCheck's own user study.

## Q3 Hallucination, grounding, attribution, guardrails

### Takeaway
Surveys establish that neural generation hallucinates and that retrieval alone does not remove it; attribution benchmarks show that even strong LLMs fail to fully support their statements with citations (about half the time on ELI5). StripCheck's template-based verdicts, where every sentence is filled from verified fields and database rows with a citation, plus a rule-based verifier and banned phrases, are a deterministic form of grounded, attributable generation and of output guardrails.

### Cited Findings
- Ji et al., "Survey of Hallucination in Natural Language Generation", ACM Computing Surveys 55(12):1-38, 2023, DOI 10.1145/3571730: neural generation is "prone to hallucinate unintended text", degrading performance and failing user expectations; survey covers metrics, mitigation, task-specific progress (summarisation, dialogue, QA, data-to-text, MT, vision-language) and LLMs. (Author list taken from Crossref record, 10 authors; the arXiv listing names more, so the arXiv preprint and the published version differ.) Relevance: motivates keeping the LLM out of the verdict text. — [Crossref record](https://api.crossref.org/works/10.1145/3571730); [arXiv abstract](https://arxiv.org/abs/2202.03629)
- Huang et al., "A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions", ACM Trans. Inf. Syst. 43(2), 2025 (online 24 Jan 2025; pp. 1-55), DOI 10.1145/3703155: LLMs produce "plausible yet nonfactual content"; the survey gives a taxonomy, detection methods and benchmarks, and discusses limitations of retrieval-augmented LLMs in addressing hallucination; open directions include hallucination in large vision-language models. Relevance: the optional VLM second reader in StripCheck is a hallucination risk for reading digits; its output should be a cross-check, never a sole source. — [Crossref record](https://api.crossref.org/works/10.1145/3703155); [arXiv abstract](https://arxiv.org/abs/2311.05232)
- Gao et al., ALCE, EMNLP 2023 (arXiv:2305.14627): first benchmark for automatic evaluation of LLM citations; on ELI5, even the best models lack complete citation support "50% of the time". Relevance: empirical argument that free-form LLM answers with citations are not trustworthy enough for a safety verdict; supports template + deterministic citation. — [arXiv abstract](https://arxiv.org/abs/2305.14627)
- Rashkin et al., "Measuring Attribution in Natural Language Generation Models" (arXiv:2112.12870, v1 23 Dec 2021, v2 2 Aug 2022): defines Attributable to Identified Sources (AIS), a human-evaluation framework with a two-stage annotation pipeline, validated on conversational QA, summarisation and table-to-text (4 datasets). Relevance: StripCheck verdict sentences can be evaluated by an AIS-style check: is every claim attributable to a named CDSCO list row? — [arXiv abstract](https://arxiv.org/abs/2112.12870)
- Rebedea et al., NeMo Guardrails, EMNLP 2023 demo track (arXiv:2310.10501): open-source toolkit of user-defined, interpretable "rails" at runtime (topic avoidance, predefined dialogue paths, language style), independent of the underlying LLM. Relevance: StripCheck's critic/verifier with banned phrases ("safe", "genuine", "stop taking") is an output rail of this kind, implemented as hard rules rather than a learned classifier. — [arXiv abstract](https://arxiv.org/abs/2310.10501)
- Inan et al., Llama Guard (arXiv:2312.06674, 7 Dec 2023): Llama2-7b instruction-tuned safeguard for prompt and response classification against a customisable taxonomy; reported to match or exceed moderation tools on OpenAI Moderation Evaluation and ToxicChat. Relevance: a learned alternative to StripCheck's deterministic guard; it targets content-moderation harms, not medical over-reassurance, so it would not by itself catch "this is safe". — [arXiv abstract](https://arxiv.org/abs/2312.06674)

### Inferences
- StripCheck's design sits at the deterministic end of the guardrail spectrum (rules and templates), trading fluency for auditability; the paper should state that a learned guard (Llama Guard) is complementary but unverified for this harm (inference).
- Banned-phrase lists are lexical and can be evaded by paraphrase; templates make the guarantee structural, because the LLM never writes the final sentence (inference).

### Gaps
- No peer-reviewed evaluation found of guardrails specifically for medicine-authenticity advice. Recent (2025-2026) hallucination-in-health-LLM evidence not yet gathered in this run.

## Q4 Risk communication in consumer health tools

### Takeaway
Evidence shows consumer tools over- and under-triage (symptom checkers) and that a bare "negative" is often misread as "no risk": adding an explicit residual-risk sentence raised correct understanding from 54% to 89% in one experiment. This supports StripCheck wording "not found on the lists we checked" and refusing a green "safe" signal.

### Cited Findings
- Semigran, Linder, Gidengil and Mehrotra, "Evaluation of symptom checkers for self diagnosis and triage: audit study", BMJ 351:h3480, July 2015, DOI 10.1136/bmj.h3480: 23 free symptom checkers tested on 45 vignettes; correct diagnosis listed first in 34% (95% CI 31-37%, n=770), within top 20 in 58%; appropriate triage advice in 57% (95% CI 52-61%, n=532), 80% for emergent, 55% for non-emergent, 33% for self-care cases; per-checker triage accuracy 33%-78%; triage tended to be overly cautious. Relevance: classic evidence that consumer-facing automated health tools are error-prone and skew conservative, motivating explicit evaluation and an abstain option. Note it concerns symptom triage, not product authenticity. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%22Evaluation%20of%20symptom%20checkers%20for%20self%20diagnosis%20and%20triage%22%20AND%20PUB_YEAR:2015&format=json&resultType=core)
- Batteux et al., "Impact of residual risk messaging to reduce false reassurance following test-negative results from asymptomatic coronavirus (SARS-CoV-2) testing: an online experimental study of a hypothetical test", BMJ Open 12(3):e056533, 2022, DOI 10.1136/bmjopen-2021-056533: 1,200 UK adults, 8 message conditions. Correct understanding of "most likely not infectious" was 54.3% with the bare "Your coronavirus test result is negative", 71.1% with the NHS wording, 88.7% when "But there is still a chance you may be infectious" was added (AOR 3.25 vs NHS, 95% CI 1.64-6.42), 90.7% with an infographic added. Behavioural intentions were unchanged (mean about 6.4/7). Relevance: the closest direct evidence that a negative/not-found result needs an explicit residual-risk sentence; supports NOT_LISTED text such as "not found on the lists checked; this does not confirm the medicine is genuine". Caveat: hypothetical COVID test, UK, online sample. — [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8927897)
- Search-derived (news/trade summaries, not opened primary papers; treat as weak): traffic-light food-label studies show green labels raise perceived healthiness; one summary says people need extra information to interpret what colours refer to. None found tested whether green is read as "safe" in a health-risk sense. — [Queen Mary news item](https://www.qmul.ac.uk/sbbs/news/items/people-choose-healthy-and-sustainable-lunches-if-given-the-green-light.html) (news; page not opened, from search snippet only)

### Inferences
- The residual-risk experiment suggests NOT_LISTED should always carry a "what this does not mean" sentence and a neutral (non-green) style; colour decision is supported by reasoning and weak food-label evidence only (inference).
- Because absence from a list reflects only CDSCO sampling (a small share of batches), "not listed" is a statement about coverage of a source, not the product (inference; sampling-share figure belongs to another notes file).

### Gaps
- No peer-reviewed study found directly testing colour semantics of green for medicine/safety results; no study of "not found" wording for authenticity checkers. Screening-result communication literature (e.g. cervical screening "low risk not no risk") was only seen via search summary and not opened.

## Q5 Governance relevant to India

### Takeaway
Indian and WHO guidance stress human oversight, avoidance of exaggerating or underplaying risk, and accountability; CDSCO's October 2025 draft guidance defines SaMD by a "medical purpose" (diagnosis, prevention, monitoring, prediction, treatment of disease), which a batch-lookup advisory does not obviously meet but could if its wording drifts into clinical advice.

### Cited Findings
- ICMR, "Ethical Guidelines for Application of Artificial Intelligence in Biomedical Research and Healthcare" (DHR-ICMR AI Cell, 2023, ISBN 978-93-5811-343-3; PDF read in full text via pdftotext): ten principles (autonomy; safety and risk minimisation; trustworthiness; data privacy; accountability and liability; optimisation of data quality; accessibility, equity and inclusiveness; collaboration; non-discrimination and fairness; validity). Text states AI "should neither exaggerate nor underestimate the seriousness of the clinical condition", that output should match the user's understanding, and that human oversight and manual override "must be made compulsory" for AI capable of severe or bodily injury; HITL places humans in a supervisory role and helps share accountability. Relevance: supports StripCheck's HITL confirmation, abstention and refusal to over-/under-state; note the guidance targets biomedical research and clinical AI, so applicability to a consumer student tool is by analogy (inference). Page/section numbers: Section 1.1 Autonomy (p.11), 1.2 Safety (pp.12-16), 1.5 Accountability (p.21). — [ICMR PDF](https://www.icmr.gov.in/icmrobject/custom_data/pdf/Ethical-guidelines/Ethical_Guidelines_AI_Healthcare_2023.pdf)
- WHO, "Ethics and governance of artificial intelligence for health", 28 June 2021, ISBN 9789240029200 (the full PDF could not be downloaded, HTTP 403; principles taken from the WHO news release of the same date): six principles: protecting human autonomy (people keep control of medical decisions); promoting human well-being, safety and the public interest (safety, accuracy and effectiveness for defined uses, with quality control); ensuring transparency, explainability and intelligibility; fostering responsibility and accountability; ensuring inclusiveness and equity; promoting AI that is responsive and sustainable (continual, open evaluation in real use). Relevance: "defined uses" and "continual evaluation" support StripCheck's narrow scope and its stated limitation that NOT_LISTED is not authenticity. — [WHO news release, 28 Jun 2021](https://www.who.int/news/item/28-06-2021-who-issues-first-global-report-on-ai-in-health-and-six-guiding-principles-for-its-design-and-use); [WHO publication page](https://www.who.int/publications/i/item/9789240029200)
- WHO, news release 18 Jan 2024 "WHO releases AI ethics and governance guidance for large multi-modal models": more than 40 recommendations; risks named include false, inaccurate, biased or incomplete statements that could harm health decisions, and "automation bias" where clinicians and patients overlook errors or hand difficult decisions to the model; recommends regulators approve health LMMs and independent post-release audits. The WHO publication page for the guidance (98 pp, ISBN 978-92-4-008475-9) shows a publication date of 25 March 2025, which differs from the Jan 2024 release; whether this is a later edition/re-issue was not resolved. — [WHO news release](https://www.who.int/news/item/18-01-2024-who-releases-ai-ethics-and-governance-guidance-for-large-multi-modal-models); [WHO publication page](https://www.who.int/publications/i/item/9789240084759)
- CDSCO Notice F.No.MED-16028/2/2024-eOffice dated 21 Oct 2025, "Draft Guidance Document on ... Medical Device Software under MDR, 2017" (scanned PDF; read by local OCR of all 76 pages, so quotations may contain OCR errors): states medical device software is regulated under the Medical Devices Rules 2017; comments invited within 30 days of publication via a Google Form. Defines SaMD as software intended to perform one or more "medical purposes" without being part of a hardware device; defines medical purposes as including "diagnosis, prevention, monitoring, mitigation, prediction, treatment, etc., of any disease or pathological condition"; states "Not all software used within healthcare is qualified as a medical device"; intended-use statements are to specify medical purpose, disease/condition, users (including non-clinical users), environment (e.g. home use) and contraindications; the guidance has a risk-based classification section (4.4) and covers AI/ML-based software and mobile apps. Relevance: a tool that only reports whether a printed batch appears on a regulator's NSQ/spurious list does not obviously diagnose, monitor or treat disease, so SaMD status is doubtful; advising users to stop or continue a medicine would move it toward a medical purpose, which supports the banned phrase "stop taking". — [CDSCO draft PDF](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Draft%20guidance%20document%20on%20Medical%20Device%20Software%2021%2010%202025.pdf)
- Secondary (law-firm commentary, not primary): Nishith Desai Associates summarise the same draft (issued 21 Oct 2025; four-tier Class A-D classification; SaMD classified by significance of information and healthcare situation). A Mondaq article dated 5 Aug 2026 reports CDSCO has published the guidance in final form and that general wellness software is excluded; the final guidance itself was NOT opened and its issue date is not stated in the article. — [Nishith Desai](https://nishithdesai.com/research-and-articles/hotline/pharma-healthcare-update/the-next-frontier-in-medtech-regulation-dissecting-cdscos-draft-guidance-on-medical-device-software-15465); [Mondaq, 5 Aug 2026](https://www.mondaq.com/india/healthcare/1826286/cdsco-publishes-guidance-on-medical-device-software-under-mdr-2017)
- Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023, assent 11 Aug 2023; Gazette of India Extraordinary, Part II Sec 1, No. 25, MeitY-hosted copy read in full text): s.2(i) "Data Fiduciary" is any person who alone or with others determines the purpose and means of processing; s.3(a) applies to processing of digital personal data within India (collected digitally, or digitised later); s.3(c)(i) excludes personal data processed by an individual for any personal or domestic purpose; s.8(5) requires a Data Fiduciary to protect personal data in its possession or control with reasonable security safeguards. Relevance: a local, offline StripCheck that never transmits photos or saved batches leaves the developer arguably not determining purpose and means of any processing of others' data (an individual running it for own use falls under s.3(c)(i)); if distributed to the public and any data reached the developer, fiduciary duties would arise. This is the author's reading, not legal advice, and needs checking with counsel before the thesis asserts it. — [Gazette copy of the Act](https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf)
- DPDP Rules, 2025 (secondary; law-firm article opened, primary Gazette text not opened): notified by MeitY on 13 Nov 2025; Phase I (immediate, 13 Nov 2025) institutional provisions incl. the Data Protection Board; Phase II (13 Nov 2026, one year) consent-manager registration; Phase III (13 May 2027, 18 months) substantive framework: notice and consent, fiduciary obligations, children's data, data principal rights, exemptions, cross-border transfer. As of today (25 Oct 2026) the substantive obligations are therefore not yet in force. A different search snippet reported 14 Nov 2025 and G.S.R. 846(E); these were not confirmed in the opened article. — [AZB Partners via Mondaq](https://www.mondaq.com/india/privacy-protection/1708314/update-indias-digital-personal-data-protection-framework-comes-into-effect)

### Inferences
- SaMD status: on the draft's own definition (medical purpose = diagnosis, prevention, monitoring, mitigation, prediction, treatment of disease), a tool that only matches a printed batch against regulator-published NSQ/spurious lists and states the match is probably not SaMD, but this is the author's reading of a draft, not a CDSCO determination. The risk rises if outputs advise on taking/stopping medicines or claim authenticity; the banned phrases and the "not listed is not safe/genuine" wording keep the tool on the informational side. A formal query to CDSCO would be needed for certainty.
- Privacy: running fully offline with no developer-side data collection is the strongest practical position under the DPDP Act; if a future version adds cloud OCR/LLM calls, telemetry or accounts, the developer would likely become a Data Fiduciary once the 13 May 2027 phase begins (inference; verify with counsel).
- The thesis can cite ICMR 2023 and WHO 2021/2024 as ethical frameworks (human oversight, not overstating risk, defined-use validation), noting they are guidance, not binding on a student prototype.

### Gaps
- Not opened: the final CDSCO medical device software guidance (a 5 Aug 2026 law-firm article says it exists; issue date unknown), the DPDP Rules 2025 Gazette text (G.S.R. number unconfirmed), the full WHO 2021 and 2024/2025 PDFs (403/page overview only), the text of Medical Devices Rules 2017 definition of "medical device" (only the draft guidance's paraphrase was read). WHO LMM guidance date discrepancy (18 Jan 2024 release vs 25 Mar 2025 on publication page) unresolved. No Indian case law or CDSCO statement on consumer medicine-verification apps found.

## Final takeaways for the Related Work section
- Abstention is theoretically grounded (Chow 1970; El-Yaniv and Wiener 2010; Geifman and El-Yaniv 2017) and is now recognised as a safety mechanism for LLMs (Wen et al. 2025); but LLMs themselves rarely abstain (Cocchieri et al., ACL 2026), so StripCheck's rule-enforced CANT_VERIFY is the defensible design.
- Human deferral helps only if designed against over-reliance: automation bias is robust (Parasuraman and Manzey 2010; Goddard et al. 2012), explanations can raise acceptance regardless of correctness (Bansal et al. 2021), cognitive forcing functions help (Buçinca et al. 2021).
- Free-form LLM text is poorly attributable (Gao et al. 2023: about half of ELI5 answers lack full citation support); template-based, source-cited verdicts and hard-rule guardrails (cf. NeMo Guardrails, Llama Guard) are a defensible alternative; learned guards are unverified for medical over-reassurance.
- Risk communication: bare negatives are misread (54% vs 89% correct understanding with a residual-risk sentence, Batteux et al. 2022, COVID context); the evidence on colour semantics for green is weak and indirect, so the no-green choice rests on reasoning plus this analogy and should be flagged as a design rationale, ideally tested in a small user study.
- Governance (as of 25 Oct 2026): ICMR 2023 and WHO 2021/2024 give ethics frameworks; CDSCO's MDR-2017 software guidance (draft 21 Oct 2025, reportedly finalised by Aug 2026) defines SaMD by medical purpose; DPDP Act 2023 is in force in part, with substantive obligations from 13 May 2027.

## BibTeX

@article{chow1970reject,
  author  = {Chow, C. K.},
  title   = {On optimum recognition error and reject tradeoff},
  journal = {IEEE Transactions on Information Theory},
  volume  = {16},
  number  = {1},
  pages   = {41--46},
  year    = {1970},
  doi     = {10.1109/TIT.1970.1054406}
}

@article{elyaniv2010noisefree,
  author  = {El-Yaniv, Ran and Wiener, Yair},
  title   = {On the Foundations of Noise-free Selective Classification},
  journal = {Journal of Machine Learning Research},
  volume  = {11},
  number  = {53},
  pages   = {1605--1641},
  year    = {2010},
  url     = {https://jmlr.org/papers/v11/el-yaniv10a.html}
}

@inproceedings{geifman2017selective,
  author    = {Geifman, Yonatan and El-Yaniv, Ran},
  title     = {Selective Classification for Deep Neural Networks},
  booktitle = {Advances in Neural Information Processing Systems 30 (NeurIPS 2017)},
  year      = {2017},
  note      = {arXiv:1705.08500; page range 4878--4887 unverified},
  url       = {https://arxiv.org/abs/1705.08500}
}

@article{wen2025abstention,
  author  = {Wen, Bingbing and Yao, Jihan and Feng, Shangbin and Xu, Chenjun and Tsvetkov, Yulia and Howe, Bill and Wang, Lucy Lu},
  title   = {Know Your Limits: A Survey of Abstention in Large Language Models},
  journal = {Transactions of the Association for Computational Linguistics},
  volume  = {13},
  pages   = {529--556},
  year    = {2025},
  doi     = {10.1162/tacl_a_00754}
}

@inproceedings{madras2018defer,
  author    = {Madras, David and Pitassi, Toniann and Zemel, Richard},
  title     = {Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer},
  booktitle = {Advances in Neural Information Processing Systems 31 (NeurIPS 2018)},
  year      = {2018},
  note      = {arXiv:1711.06664},
  url       = {https://arxiv.org/abs/1711.06664}
}

@inproceedings{mozannar2020defer,
  author    = {Mozannar, Hussein and Sontag, David},
  title     = {Consistent Estimators for Learning to Defer to an Expert},
  booktitle = {Proceedings of the 37th International Conference on Machine Learning (ICML 2020)},
  year      = {2020},
  note      = {arXiv:2006.01862},
  url       = {https://arxiv.org/abs/2006.01862}
}

@inproceedings{bansal2021whole,
  author    = {Bansal, Gagan and Wu, Tongshuang and Zhou, Joyce and Fok, Raymond and Nushi, Besmira and Kamar, Ece and Ribeiro, Marco Tulio and Weld, Daniel S.},
  title     = {Does the Whole Exceed its Parts? The Effect of {AI} Explanations on Complementary Team Performance},
  booktitle = {Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems},
  year      = {2021},
  note      = {arXiv:2006.14779; ACM DOI and page numbers not verified},
  url       = {https://arxiv.org/abs/2006.14779}
}

@article{parasuraman2010complacency,
  author  = {Parasuraman, Raja and Manzey, Dietrich H.},
  title   = {Complacency and Bias in Human Use of Automation: An Attentional Integration},
  journal = {Human Factors},
  volume  = {52},
  number  = {3},
  pages   = {381--410},
  year    = {2010},
  doi     = {10.1177/0018720810376055}
}

@article{goddard2012automation,
  author  = {Goddard, Kate and Roudsari, Abdul and Wyatt, Jeremy C.},
  title   = {Automation bias: a systematic review of frequency, effect mediators, and mitigators},
  journal = {Journal of the American Medical Informatics Association},
  volume  = {19},
  number  = {1},
  pages   = {121--127},
  year    = {2012},
  doi     = {10.1136/amiajnl-2011-000089}
}

@inproceedings{gao2023alce,
  author    = {Gao, Tianyu and Yen, Howard and Yu, Jiatong and Chen, Danqi},
  title     = {Enabling Large Language Models to Generate Text with Citations},
  booktitle = {Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year      = {2023},
  note      = {arXiv:2305.14627; ACL Anthology pages not verified},
  url       = {https://arxiv.org/abs/2305.14627}
}

@misc{rashkin2021ais,
  author = {Rashkin, Hannah and Nikolaev, Vitaly and Lamm, Matthew and Aroyo, Lora and Collins, Michael and Das, Dipanjan and Petrov, Slav and Tomar, Gaurav Singh and Turc, Iulia and Reitter, David},
  title  = {Measuring Attribution in Natural Language Generation Models},
  year   = {2021},
  note   = {arXiv:2112.12870 (v2 Aug 2022); preprint as opened. Journal version (Computational Linguistics 2023) not verified in this run},
  url    = {https://arxiv.org/abs/2112.12870}
}

@misc{inan2023llamaguard,
  author = {Inan, Hakan and Upasani, Kartikeya and Chi, Jianfeng and Rungta, Rashi and Iyer, Krithika and Mao, Yuning and Tontchev, Michael and Hu, Qing and Fuller, Brian and Testuggine, Davide and Khabsa, Madian},
  title  = {Llama Guard: {LLM}-based Input-Output Safeguard for Human-{AI} Conversations},
  year   = {2023},
  note   = {arXiv:2312.06674, submitted 7 Dec 2023},
  url    = {https://arxiv.org/abs/2312.06674}
}

@inproceedings{rebedea2023nemo,
  author    = {Rebedea, Traian and Dinu, Razvan and Sreedhar, Makesh and Parisien, Christopher and Cohen, Jonathan},
  title     = {{NeMo} Guardrails: A Toolkit for Controllable and Safe {LLM} Applications with Programmable Rails},
  booktitle = {Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing: System Demonstrations (EMNLP 2023)},
  year      = {2023},
  note      = {arXiv:2310.10501},
  url       = {https://arxiv.org/abs/2310.10501}
}

@article{ji2023hallucination,
  author  = {Ji, Ziwei and Lee, Nayeon and Frieske, Rita and Yu, Tiezheng and Su, Dan and Xu, Yan and Ishii, Etsuko and Bang, Ye Jin and Madotto, Andrea and Fung, Pascale},
  title   = {Survey of Hallucination in Natural Language Generation},
  journal = {ACM Computing Surveys},
  volume  = {55},
  number  = {12},
  pages   = {1--38},
  year    = {2023},
  doi     = {10.1145/3571730},
  note    = {Author list as in Crossref record}
}

@article{huang2025hallucination,
  author  = {Huang, Lei and Yu, Weijiang and Ma, Weitao and Zhong, Weihong and Feng, Zhangyin and Wang, Haotian and Chen, Qianglong and Peng, Weihua and Feng, Xiaocheng and Qin, Bing and Liu, Ting},
  title   = {A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions},
  journal = {ACM Transactions on Information Systems},
  volume  = {43},
  number  = {2},
  pages   = {1--55},
  year    = {2025},
  doi     = {10.1145/3703155}
}

@article{bucinca2021trust,
  author  = {Bu{\c{c}}inca, Zana and Malaya, Maja Barbara and Gajos, Krzysztof Z.},
  title   = {To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on {AI} in {AI}-assisted Decision-making},
  journal = {Proceedings of the ACM on Human-Computer Interaction},
  volume  = {5},
  number  = {CSCW1},
  pages   = {1--21},
  year    = {2021},
  doi     = {10.1145/3449287}
}

@inproceedings{cocchieri2026abstain,
  author    = {Cocchieri, Alessio and Ragazzi, Luca and Tagliavini, Giuseppe and Moro, Gianluca},
  title     = {{LLMs} (Almost) Never Abstain Under Medical Uncertainty},
  booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  address   = {San Diego, California},
  publisher = {Association for Computational Linguistics},
  pages     = {29573--29613},
  year      = {2026},
  doi       = {10.18653/v1/2026.acl-long.1365}
}

@article{semigran2015symptom,
  author  = {Semigran, Hannah L. and Linder, Jeffrey A. and Gidengil, Courtney and Mehrotra, Ateev},
  title   = {Evaluation of symptom checkers for self diagnosis and triage: audit study},
  journal = {BMJ},
  volume  = {351},
  pages   = {h3480},
  year    = {2015},
  doi     = {10.1136/bmj.h3480}
}

@article{batteux2022residual,
  author  = {Batteux, E. and Bonfield, S. and Jones, L. F. and Carter, H. and Gold, N. and Amlot, R. and Marteau, T. and Weston, D.},
  title   = {Impact of residual risk messaging to reduce false reassurance following test-negative results from asymptomatic coronavirus ({SARS-CoV-2}) testing: an online experimental study of a hypothetical test},
  journal = {BMJ Open},
  volume  = {12},
  number  = {3},
  pages   = {e056533},
  year    = {2022},
  doi     = {10.1136/bmjopen-2021-056533},
  note    = {Given names not verified; initials as listed in the PMC record}
}

@techreport{who2021ethics,
  author      = {{World Health Organization}},
  title       = {Ethics and governance of artificial intelligence for health: {WHO} guidance},
  institution = {World Health Organization},
  address     = {Geneva},
  year        = {2021},
  isbn        = {9789240029200},
  url         = {https://www.who.int/publications/i/item/9789240029200},
  note        = {Published 28 June 2021. Accessed 25 Oct 2026}
}

@techreport{who2024lmm,
  author      = {{World Health Organization}},
  title       = {Ethics and governance of artificial intelligence for health: Guidance on large multi-modal models},
  institution = {World Health Organization},
  address     = {Geneva},
  year        = {2024},
  isbn        = {9789240084759},
  url         = {https://www.who.int/publications/i/item/9789240084759},
  note        = {Release announced 18 Jan 2024; publication page shows 25 Mar 2025 (discrepancy unresolved). ISBN as printed on the page: 978-92-4-008475-9. Accessed 25 Oct 2026}
}

@techreport{icmr2023ai,
  author      = {{DHR-ICMR Artificial Intelligence Cell}},
  title       = {Ethical Guidelines for Application of Artificial Intelligence in Biomedical Research and Healthcare},
  institution = {Indian Council of Medical Research},
  address     = {New Delhi},
  year        = {2023},
  isbn        = {978-93-5811-343-3},
  url         = {https://www.icmr.gov.in/icmrobject/custom_data/pdf/Ethical-guidelines/Ethical_Guidelines_AI_Healthcare_2023.pdf},
  note        = {Accessed 25 Oct 2026}
}

@misc{cdsco2025softwaredraft,
  author = {{Central Drugs Standard Control Organisation}},
  title  = {Draft Guidance Document on Medical Device Software under {MDR}, 2017},
  year   = {2025},
  note   = {Notice F.No.MED-16028/2/2024-eOffice dated 21 Oct 2025. Scanned PDF read by OCR. Accessed 25 Oct 2026},
  url    = {https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Draft%20guidance%20document%20on%20Medical%20Device%20Software%2021%2010%202025.pdf}
}

@misc{india2023dpdp,
  author = {{Government of India}},
  title  = {The Digital Personal Data Protection Act, 2023 (No. 22 of 2023)},
  year   = {2023},
  note   = {Gazette of India Extraordinary, Part II Sec. 1, No. 25, 11 Aug 2023. Accessed 25 Oct 2026},
  url    = {https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf}
}

@misc{azb2025dpdprules,
  author = {{AZB \& Partners}},
  title  = {Update: India's Digital Personal Data Protection Framework Comes into Effect (law-firm commentary on DPDP Rules 2025)},
  year   = {2025},
  note   = {Secondary source via Mondaq; Rules notified 13 Nov 2025. Accessed 25 Oct 2026},
  url    = {https://www.mondaq.com/india/privacy-protection/1708314/update-indias-digital-personal-data-protection-framework-comes-into-effect}
}


## Verification log
- chow1970reject: VERIFIED via Crossref (title, author, IEEE Trans. Inf. Theory 16(1):41-46, 1970, DOI). Content claim about the optimal rejection rule remains unread background knowledge [UNVERIFIED as to content].
- elyaniv2010noisefree: VERIFIED via JMLR page metadata (11(53):1605-1641, 2010; title and authors). Note: the notes' prose says the abstract states no theorems; not re-checked beyond metadata.
- geifman2017selective: CORRECTED. Title/authors/date and abstract numbers (2% top-5 ImageNet error, probability 99.9%, almost 60% coverage) verified on arXiv. NeurIPS 2017 vol. 30 verified on papers.nips.cc, but the page range 4878-4887 was NOT confirmed and was removed from the .bib; BibTeX url now points to the NeurIPS proceedings page. The "softmax response" detail is not in the arXiv abstract (unverified).
- madras2018defer: CORRECTED. Title, authors and abstract claims verified (arXiv, papers.nips.cc, NeurIPS vol. 31). Note: the NeurIPS record lists the second author as "Toni Pitassi"; arXiv gives Toniann; kept arXiv spelling. The earlier BibTeX url now points to the proceedings page.
- mozannar2020defer: CORRECTED. Verified on arXiv and PMLR (vol. 119, pp. 7076-7087, ICML 2020); added the PMLR volume and pages to the .bib.
- bansal2021whole: CORRECTED. Verified on arXiv and Crossref; the previously "unverified" ACM DOI is 10.1145/3411764.3445717, pp. 1-16 (CHI 2021). Quoted claim ("regardless of its correctness") confirmed in the abstract.
- parasuraman2010complacency: VERIFIED via Crossref and Europe PMC abstract (omission/commission errors, naive and expert participants, not prevented by training or instructions all confirmed).
- goddard2012automation: VERIFIED via Crossref and Europe PMC abstract (13,821 retrieved, 74 included; mediators and mitigators as stated).
- bucinca2021trust: VERIFIED via Crossref (DOI 10.1145/3449287, PACM HCI 5 CSCW1, pp. 1-21) and arXiv abstract (N=199; forcing reduced overreliance; least favourable ratings; Need for Cognition). Crossref lists the title without the subtitle; the full title from arXiv is used.
- semigran2015symptom: VERIFIED via Crossref and Europe PMC abstract; all quoted figures (34%, 58%, 57%, 80/55/33%, 33-78%, risk averse) match.
- batteux2022residual: CORRECTED. Verified via Crossref and Europe PMC abstract. Figures confirmed (54% vs 71% vs 89% vs 91%; AOR 3.25; 1200 adults; behaviour M=6.4). Author given names were "not verified" in the notes; Crossref gives full names (Eleonore Batteux et al.), now used in the .bib. The 8 message conditions are consistent with the abstract (4 x 2 design).
- wen2025abstention: VERIFIED via Crossref, ACL Anthology metadata (TACL 13:529-556, 2025, DOI) and arXiv abstract (three perspectives: query, model, human values; meta-capability and context-specific optimisation).
- cocchieri2026abstain: VERIFIED via Crossref and ACL Anthology (ACL 2026 Long, pp. 29573-29613, DOI; abstract quote "state-of-the-art LLMs systematically overcommit, rarely abstaining even when the question itself is hidden" confirmed). Anthology date field is July 2026.
- gao2023alce: CORRECTED. Verified on arXiv (abstract: "even the best models lack complete citation support 50% of the time" on ELI5) and Crossref; the notes' "ACL Anthology pages not verified" resolved: DOI 10.18653/v1/2023.emnlp-main.398, pp. 6465-6488.
- rashkin2023ais: CORRECTED. arXiv:2112.12870 confirmed, but it was published as Computational Linguistics 49(4):777-840, 2023, DOI 10.1162/coli_a_00486 (Crossref); the BibTeX is now @article and the key changed from rashkin2021ais to rashkin2023ais. (Crossref also holds a separate early-access record 10.1162/coli_a_00490; the issue version is cited.) Abstract details (AIS, two-stage annotation, three tasks/four datasets) confirmed; the v1/v2 dates were not rechecked.
- rebedea2023nemo: CORRECTED. Verified on arXiv and Crossref; EMNLP 2023 System Demonstrations, pp. 431-445, DOI 10.18653/v1/2023.emnlp-demo.40 added.
- inan2023llamaguard: VERIFIED on arXiv (authors, 7 Dec 2023, Llama2-7b, OpenAI Moderation Evaluation and ToxicChat claims). Preprint only; no peer-reviewed venue found in this check.
- ji2023hallucination: VERIFIED via Crossref (ACM Comput. Surv. 55(12):1-38, DOI 10.1145/3571730; 10 authors) and arXiv abstract (quoted "prone to hallucinate unintended text").
- huang2025hallucination: VERIFIED via Crossref (ACM TOIS 43(2), online 24 Jan 2025, DOI 10.1145/3703155; 11 authors) and arXiv abstract ("plausible yet nonfactual content", RAG limitations, vision-language directions).
- who2021ethics: VERIFIED on the WHO publication page (title, 28 June 2021, ISBN 9789240029200, 150 pp) and the WHO news release (six principles as listed in the notes).
- who2024lmm: VERIFIED with unresolved discrepancy. Publication page: title, ISBN 978-92-4-008475-9, 98 pp, dated 25 March 2025. News release dated 18 Jan 2024 confirmed (over 40 recommendations; automation bias; false, inaccurate, biased or incomplete statements). Kept year 2024 with a note in the .bib.
- icmr2023ai: VERIFIED from the full PDF text (ISBN 978-93-5811-343-3; principle xii text "neither exaggerate nor underestimate", "Human-in-the-loop", oversight and manual override "must be made compulsory" confirmed; principle list in the index matches). Notes' page numbers (11, 12-16, 21) not rechecked.
- cdsco2025softwaredraft: VERIFIED from the 76-page PDF text layer (medical purposes definition, "Not all software used within healthcare is qualified as a medical device", section 4.4 risk-based classification, mobile apps and AI/ML software, Google Form for comments). Date 21 Oct 2025 (file name; search coverage says 30-day comment window). The notice number F.No.MED-16028/2/2024-eOffice was NOT found in the text layer [UNVERIFIED]; it is omitted from the .bib.
- india2023dpdp: VERIFIED from the Gazette PDF text (Act 22 of 2023, 11 Aug 2023, Part II Sec 1 No. 25; s.2(i) Data Fiduciary; s.3(c)(i) personal or domestic purpose exclusion; s.8(5) reasonable security safeguards). The legal reading of applicability to StripCheck is the researcher's inference, not a verified source claim.
- azb2025dpdprules: VERIFIED via the opened Mondaq page (AZB & Partners; Rules notified 13 Nov 2025; phases 13 Nov 2025, 13 Nov 2026, 13 May 2027; no G.S.R. number in article). The alternative 14 Nov 2025 / G.S.R. 846(E) remains UNVERIFIED and should not be cited. Secondary source only.
- Nishith Desai Associates hotline article on the CDSCO draft: UNVERIFIED (not opened in this check); omitted from .bib.
- Mondaq 5 Aug 2026 article claiming the CDSCO guidance was finalised: UNVERIFIED (not opened; a search found a CDSCO document reported by Biospectrum dated 27 Jul 2026 on application submission, unclear whether it is the final version). The claim "CDSCO reportedly finalised the guidance by Aug 2026" [UNVERIFIED]. Omitted from .bib.
- Queen Mary traffic-light news item and food-label colour claims: UNVERIFIED (search snippet only) [UNVERIFIED]; omitted from .bib.
- "Do Large Language Models Know When Not to Answer in Medical QA?" and SelectLLM (snippet-only items): UNVERIFIED; omitted from .bib.
Verification: COMPLETE

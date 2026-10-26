export const meta = {
  name: 'stripcheck-literature-survey',
  description: 'StripCheck literature survey + engineering scan: 14 researchers, per-theme citation verification, synthesized survey report',
  whenToUse: 'Research phase of the StripCheck college project',
  phases: [
    { title: 'Research', detail: '12 literature themes + 2 engineering investigations, in parallel' },
    { title: 'Verify', detail: 'one citation checker per literature theme: confirm every reference, fix bibliography, write BibTeX' },
    { title: 'Synthesize', detail: 'report writer turns verified notes into the literature survey report' },
  ],
}

const BASE = 'C:\\Users\\suraj\\Desktop\\Misc\\AgenticAI StripCheck'
const NOTES = BASE + '\\research_notes\\StripCheck literature survey'
const ENG = BASE + '\\research_notes\\StripCheck engineering scan'
const SKILL = 'C:\\Users\\suraj\\AppData\\Local\\Claude-Data\\claude_pzs8sxrjxfjjc\\local-agent-mode-sessions\\skills-plugin\\cf6bea7f-42dc-48e9-a8f0-6aad7949619b\\7ab2ee43-b226-4fc5-9191-183b461c7107\\skills\\deep-research'

const CONTEXT = 'Project context (use it only to judge relevance; do not research the project itself): StripCheck is a final-year Agentic-AI college project in India. A user photographs a medicine strip or carton; a local, offline LangGraph agent reads it (QR code, then OCR with RapidOCR/PP-OCR, then an enhanced re-read; optionally a small local vision-language model as an independent second reader), extracts batch number, product name, manufacturing/expiry dates and manufacturer, and checks whether that exact batch appears on the monthly lists that CDSCO (India\'s Central Drugs Standard Control Organisation) publishes of drug samples found Not of Standard Quality (NSQ) or spurious. Retrieval is an exact batch lookup plus an OCR-confusion-aware variant search (B<->3, 0<->O, 1<->7, 5<->S ...), followed by field-by-field corroboration (product, dates, maker) that rejects batch-number collisions, a human-in-the-loop question when a character is in doubt, and a verifier/critic agent that enforces hard rules before any verdict (FLAGGED / SUSPECTED_FAKE / NOT_LISTED / CANT_VERIFY, i.e. the agent can abstain). An ingest agent parses CDSCO PDF/HTML alert tables into a validated SQLite index with LLM-assisted repair and quarantine of bad rows. A small local LLM (Ollama) acts as planner and adjudicator with a deterministic rule fallback. A "medicine cabinet" memory re-checks saved batches whenever new alert lists arrive. Everything runs on a Windows laptop with no paid APIs. The research feeds the Related Work section of an IEEE-style paper and a later university thesis.'

const LIT_CONSTRAINTS = [
  'Today is 25 October 2026. Cover the classic/seminal works AND the most recent work (2023 to Oct 2026). Give the date of every time-sensitive fact.',
  'Academic rigor: this feeds a research paper and a university thesis. Cite only sources you actually opened. Give full bibliographic details (authors, title, venue, year, volume/pages if any, DOI or stable URL).',
  'Prefer peer-reviewed papers, official reports (WHO, CDSCO, Gazette of India, regulators) and primary documentation. Use news only for recent events, and label it as news.',
  'For every source write 2-3 lines: what it found or claims (with numbers where available) and its relevance to StripCheck (which design choice it supports, challenges or motivates).',
  'Aim for roughly 12-20 strong sources for this theme; quality over quantity.',
  'End the notes with a BibTeX block holding one entry per academic or official source, with lowercase ASCII citation keys of the form authorYEARword (e.g. yao2023react). Web pages use @misc with url and note = {Accessed 25 Oct 2026}.',
  'Never fabricate a citation, author, number, URL or DOI. If you cannot confirm a detail, say so explicitly.',
]

const ENG_CONSTRAINTS = [
  'Today is 25 October 2026. Report exact versions, dates and URLs as seen on official sources, and cite the URL for every fact.',
  'This is an engineering investigation, not a literature review: be concrete and practical. Do not install anything, run code, or modify any file other than your notes file.',
  'Never guess a version number, URL or endpoint; if you cannot confirm it, say so.',
]

const THEMES = [
  { key: 'sf_medicines_india', kind: 'lit',
    topic: 'the burden of substandard and falsified (SF) medicines globally and in India, and India\'s legal and regulatory framework and alert system for Not-of-Standard-Quality (NSQ) and spurious drugs',
    objective: 'A dense, well-cited account of definitions, measured prevalence, harms, the CDSCO monthly NSQ/spurious alert system and recall rules, and recent incidents, usable as the motivation and background of the paper.',
    questions: [
      'How do WHO (World Health Assembly 2017 SF definitions) and Indian law define substandard, falsified, spurious, adulterated, misbranded and NSQ? (Drugs and Cosmetics Act 1940, Sections 16, 17, 17A, 17B; penalties in Section 27; the 2008 amendment)',
      'What prevalence of SF medicines has been measured globally (WHO Global Surveillance and Monitoring System report 2017, the "1 in 10" estimate; Ozawa et al. 2018 JAMA Network Open meta-analysis; later meta-analyses 2019-2026) and in India (CDSCO National Drug Survey 2014-16: NSQ about 3.16%, spurious about 0.0245%, verify the exact figures; other Indian quality studies), and what are the health and economic harms (treatment failure, antimicrobial resistance, deaths)?',
      'How does CDSCO\'s monthly NSQ/spurious drug alert system work: since when it has been published, central vs state laboratories, typical monthly counts in 2024-2026, the move of alerts from monthly PDFs to a new NSQ portal page in August 2025, and the CDSCO "Guidelines on Recall and Rapid Alert System for Drugs" (2012)?',
      'Which recent incidents involve substandard drugs made in or sold in India (Gambia and Uzbekistan cough syrups 2022, Cameroon 2023, the Madhya Pradesh "Coldrif" diethylene-glycol deaths of 2025, any 2026 incidents), and what regulatory responses followed (revised Schedule M GMP and its deadlines, mandatory testing of cough-syrup exports, others)?',
      'Is there evidence on how many consumers or pharmacists know about NSQ alerts, and on the time lag between manufacture, sampling, test result and alert publication?',
    ],
    sources: [
      'WHO GSMS report (2017), WHO fact sheets and WHA documents (who.int)',
      'CDSCO website (cdsco.gov.in), PIB press releases (pib.gov.in), Gazette of India notifications, Lok Sabha / Rajya Sabha answers',
      'Peer-reviewed literature via PubMed / Google Scholar (BMJ Global Health, Lancet, JAMA Network Open, PLOS ONE, AJTMH, Journal of Pharmaceutical Policy and Practice)',
      'Reputable news (Reuters, The Hindu, Indian Express) only for 2022-2026 incidents',
    ],
  },
  { key: 'traceability_authentication', kind: 'lit',
    topic: 'pharmaceutical supply-chain authentication and traceability systems (serialization, QR/DataMatrix codes, track-and-trace, mobile authentication services) worldwide and in India, and their limitations',
    objective: 'Explain what existing authentication/traceability systems can and cannot establish, with the key analytic point that they authenticate provenance but do not test quality: a genuine but substandard batch from a licensed maker carries valid codes, so only a lab-result alert list can flag it.',
    questions: [
      'India: the Schedule H2 QR code mandate (G.S.R. 823(E), November 2022; effective 1 August 2023; top 300 brands; which data must be encoded), QR codes on APIs (2023), export track-and-trace (iVEDA / DAVA), and any 2024-2026 moves toward universal track-and-trace or a central verification database. What does a consumer actually get when scanning an H2 QR code?',
      'EU Falsified Medicines Directive 2011/62/EU and Delegated Regulation (EU) 2016/161 (unique identifier, anti-tampering device, EMVS); US DSCSA (2013, the November 2023 interoperability requirement and the exemptions/stabilisation periods through 2025-2026); GS1 standards (GTIN, application identifiers (01)(10)(11)(17)(21), GS1 DataMatrix).',
      'Mobile authentication services (Sproxil, mPedigree, Nigeria\'s NAFDAC MAS, PharmaSecure in India): evidence on uptake and effectiveness, and known weaknesses (code cloning or reuse).',
      'Blockchain-based drug traceability (MediLedger pilots, academic proposals): maturity and evidence of real-world effect.',
      'Which sources explicitly discuss that serialization/authentication cannot detect substandard (as opposed to falsified) medicines?',
    ],
    sources: [
      'Gazette of India / CDSCO notifications; EUR-Lex; FDA DSCSA pages; GS1 General Specifications',
      'WHO "Policy paper on traceability of medical products" (2021) and WHO GSMS material',
      'Peer-reviewed evaluations (BMJ Global Health, Journal of Pharmaceutical Policy and Practice, IEEE Access, Health Policy and Planning)',
    ],
  },
  { key: 'screening_tech_and_apps', kind: 'lit',
    topic: 'technologies and services used to screen medicine quality or verify medicines in the field and by consumers, including image-based AI methods and existing consumer apps',
    objective: 'Position StripCheck (an information-based check of a pack\'s batch against official lab-failure lists) against field screening devices, image-based AI for counterfeit detection, and consumer verification/recall-check apps worldwide and in India.',
    questions: [
      'Which field-screening technologies exist (handheld Raman / NIR spectrometers, the GPHF Minilab, paper analytical devices, the FDA CD-3, smartphone-based spectroscopy or colorimetry), and what do systematic reviews conclude about cost, sensitivity, skill needed and usability (Kovacs et al. 2014 PLOS ONE; Vickers et al. 2018 BMJ Global Health; reviews from 2020-2026)?',
      'Which image-based or deep-learning approaches detect counterfeit medicines or packaging (print defects, pill images, smartphone apps), and how well do they perform?',
      'Which consumer-facing verification or recall-check apps and services exist worldwide and in India (e.g., GS1 India Smart Consumer / DataKart, H2 QR scanning, any app or website that checks a batch against CDSCO NSQ alerts, pharmacy-chain tools, FDA recall search, other national recall lookups)? What exactly do they check (authenticity, quality, or recall status)? Are any of them agentic or LLM-based?',
      'What gaps remain that an offline, explainable batch-versus-alert-list checker could fill?',
    ],
    sources: [
      'Systematic reviews on PubMed / Google Scholar',
      'IEEE Xplore and ACM Digital Library for image-based detection',
      'Official app pages and store listings for apps (cite as web sources with access date)',
    ],
  },
  { key: 'packaging_ocr', kind: 'lit',
    topic: 'text recognition on pharmaceutical and product packaging, especially batch/lot numbers and expiry dates printed on blister foil and cartons, plus the current OCR model landscape and how reliable OCR confidence scores are',
    objective: 'Background on reading batch/expiry codes from packs, the PP-OCR family that RapidOCR packages, vision-language-model OCR that could serve as an independent second reader, and evidence that OCR systems produce confident misreads that confidence scores and image enhancement do not catch.',
    questions: [
      'Which methods and datasets exist for recognising expiry dates and lot/batch codes on packages (e.g., Seker and Ahn 2022, "A generalized framework for recognition of expiration dates on product packages using fully convolutional networks", and its ExpDate dataset; dot-matrix, inkjet and embossed code recognition; industrial OCR/OCV for lot codes), and what accuracy do they report? What makes foil blister strips hard (reflection, embossing, curvature, glare)?',
      'What has been built and evaluated for reading medication labels for visually impaired users or for medication-safety checks?',
      'Lightweight OCR: PP-OCR (Du et al. 2020), PP-OCRv2/v3/v4, PP-OCRv5 and the PaddleOCR 3.0 technical report (2025); RapidOCR; scene-text recognition surveys (Long, He and Yao 2021 IJCV; Chen et al. 2021 ACM Computing Surveys); TrOCR (Li et al., AAAI 2023).',
      'Vision-language models used for OCR (GOT-OCR 2.0, Qwen2.5-VL technical report 2025, Qwen3-VL, olmOCR, PaddleOCR-VL, DeepSeek-OCR, newer ones up to Oct 2026), especially small (8B or less) models that run locally, and evidence on their hallucination behaviour on short alphanumeric codes.',
      'How reliable are confidence scores of OCR and deep networks (Guo et al. 2017 ICML calibration; overconfident errors in text recognition; uncertainty estimation for OCR)? Does contrast enhancement (CLAHE: Pizer et al. 1987; Zuiderveld 1994) fix misreads or only help with blur/glare?',
    ],
    sources: [
      'arXiv; CVPR / ICCV / ECCV / ICDAR proceedings; Expert Systems with Applications; Pattern Recognition; IJDAR',
      'Official model technical reports and repositories',
    ],
  },
  { key: 'ocr_postcorrection_alpr', kind: 'lit',
    topic: 'OCR error correction with noisy-channel models and confusion matrices, matching noisy reads against a closed vocabulary, and the closest real-world analogue: automatic licence-plate recognition (ALPR) hotlist matching with confusable characters and human verification',
    objective: 'Give StripCheck\'s confusion-aware variant search and human confirmation a principled grounding (noisy channel / weighted edit distance over a closed lexicon) and a real-world precedent (ALPR hotlist hits that must be visually verified because misreads cause false alarms).',
    questions: [
      'Noisy-channel spelling and OCR correction: Kernighan, Church and Gale (1990); Brill and Moore (2000); Kolak and Resnik (2002, 2005); character confusion matrices; weighted edit distance (Levenshtein 1966; Wagner and Fischer 1974); lexicon-constrained recognition.',
      'Surveys and competitions: Nguyen et al. 2021 "Survey of Post-OCR Processing Approaches" (ACM Computing Surveys); ICDAR post-OCR competitions (Chiron et al. 2017; Rigaud et al. 2019); recent LLM-based post-OCR correction (2023-2026) and its hallucination risk.',
      'ALPR: how systems handle confusable characters (0/O/D/Q, 1/I/7, 8/B, 5/S, 2/Z), syntax-based correction, hotlist matching; documented false-positive incidents caused by misreads (e.g., wrongful stops) and policies that require officers to visually verify a hit before acting (police guidance, ACLU/EFF reports, court cases, academic studies). Include ALPR surveys (e.g., Du et al. 2013 IEEE TCSVT; Laroca et al.).',
      'Learning confusion priors from user feedback, human-in-the-loop correction and active learning for OCR.',
    ],
    sources: [
      'ACL Anthology, ACM DL, IEEE Xplore',
      'Policy documents, court records and civil-liberties reports for ALPR verification practice',
    ],
  },
  { key: 'record_linkage', kind: 'lit',
    topic: 'record linkage / entity resolution theory and practice as a framework for deciding whether a medicine pack and an alert-list entry refer to the same batch, including blocking, field-wise agreement, clerical review and LLM-based entity matching',
    objective: 'Frame StripCheck\'s matching as blocked record linkage (batch key as the blocking key; product, dates and maker as comparison fields; Fellegi-Sunter match / possible-match / non-match zones, with the possible-match zone sent to a human like clerical review).',
    questions: [
      'Fellegi and Sunter 1969 (match / possible match / non-match; m- and u-probabilities); Newcombe et al. 1959; Winkler (Jaro-Winkler 1990; EM estimation); Christen 2012 "Data Matching"; Elmagarmid, Ipeirotis and Verykios 2007 (TKDE).',
      'Blocking and indexing surveys (Christen 2012 TKDE; Papadakis et al. 2020 ACM Computing Surveys).',
      'Clerical review and human-in-the-loop entity resolution (CrowdER, Wang et al. 2012 VLDB; active-learning ER).',
      'String similarity for names (Levenshtein, Jaro-Winkler, token-based measures; Cohen, Ravikumar and Fienberg 2003 comparison).',
      'LLM-based entity matching (Narayan et al. 2022 VLDB "Can Foundation Models Wrangle Your Data?"; Peeters, Steiner and Bizer 2023/2025 "Entity Matching using Large Language Models"), and matching of drug names (brand vs generic, drug-name normalisation such as RxNorm, Indian brand-name variability).',
    ],
    sources: [
      'JASA, VLDB, SIGMOD, TKDE, ACM Computing Surveys, EDBT; books',
    ],
  },
  { key: 'llm_agents', kind: 'lit',
    topic: 'LLM-based agent architectures relevant to a bounded, tool-using, verifier-checked agent running on small local models',
    objective: 'Cover reasoning-and-acting loops, planning, critics and external verifiers, the limits of self-correction, multi-agent supervision, human-in-the-loop interrupts, structured output, small language models for agents, observability and evaluation practice, so the paper can justify a hybrid rules+LLM planner with a hard-rule verifier.',
    questions: [
      'ReAct (Yao et al., ICLR 2023), MRKL (Karpas et al. 2022), Toolformer (Schick et al. 2023), Reflexion (Shinn et al. 2023), Self-Refine (Madaan et al. 2023), CRITIC (Gou et al., ICLR 2024).',
      'Limits of self-correction and the case for external verifiers: Huang et al. (ICLR 2024) "Large Language Models Cannot Self-Correct Reasoning Yet"; Kambhampati et al. (ICML 2024) "LLMs Can\'t Plan, But Can Help Planning in LLM-Modulo Frameworks".',
      'Multi-agent and hierarchical/supervisor patterns (AutoGen, MetaGPT, CAMEL), agent surveys (Wang et al. 2024 Frontiers of Computer Science; Xi et al.), Anthropic "Building effective agents" (Dec 2024), LangGraph documentation on durable execution, checkpointing and interrupts, and human-in-the-loop agent designs.',
      'Small language models for agents (Belcak et al. 2025 "Small Language Models are the Future of Agentic AI"); structured output and constrained decoding (Willard and Louf 2023; Tam et al. 2024 "Let Me Speak Freely?"; Geng et al. 2025 JSONSchemaBench; XGrammar).',
      'Agent evaluation practice (Kapoor et al. 2024 "AI Agents That Matter"; tau-bench; AgentBench), agent observability (OpenTelemetry GenAI semantic conventions, OpenInference), and 2025-2026 work on reliable agents in high-stakes domains such as healthcare.',
    ],
    sources: [
      'arXiv; NeurIPS / ICLR / ICML / ACL proceedings',
      'Official framework documentation (LangGraph, OpenTelemetry)',
    ],
  },
  { key: 'abstention_hitl_safety', kind: 'lit',
    topic: 'abstention and selective prediction, human-AI collaboration, grounding and hallucination control, safety guardrails, risk communication for consumer health tools, and AI-in-health governance relevant to India',
    objective: 'Support StripCheck\'s CANT_VERIFY abstention, its human confirmation step, its template-based cited verdicts with banned phrases ("safe", "genuine", "stop taking"), and its local/offline privacy stance.',
    questions: [
      'Reject option and selective prediction: Chow 1970; El-Yaniv and Wiener 2010; Geifman and El-Yaniv 2017 (NeurIPS); abstention in LLMs (Wen et al. 2025 TACL "Know Your Limits").',
      'Learning to defer and human-AI teams: Madras et al. 2018; Mozannar and Sontag 2020; Bansal et al. 2021 (CHI); automation bias and complacency (Parasuraman and Manzey 2010; Goddard et al. 2012 JAMIA).',
      'Hallucination and grounding: Ji et al. 2023 (ACM Computing Surveys); Huang et al. survey; attributed generation with citations (Gao et al. 2023 ALCE; Rashkin et al. AIS); guardrails (NeMo Guardrails; Llama Guard).',
      'Risk communication in consumer health tools: false reassurance, how to phrase "not found" results, evidence from symptom-checker evaluations (Semigran et al. 2015 BMJ) and screening-result communication.',
      'Governance: WHO "Ethics and governance of AI for health" (2021) and its 2024 guidance on large multi-modal models; ICMR "Ethical Guidelines for Application of AI in Biomedical Research and Healthcare" (2023); India\'s Digital Personal Data Protection Act 2023 and its 2025 Rules; whether a consumer advisory tool would count as software as a medical device under India\'s Medical Devices Rules 2017.',
    ],
    sources: [
      'NeurIPS / ICML / CHI / JAMIA / BMJ',
      'WHO, ICMR, MeitY and CDSCO publications',
    ],
  },
  { key: 'document_extraction', kind: 'lit',
    topic: 'extraction of tables from PDFs and web pages, schema matching and schema drift, data validation, and LLM-assisted repair, as background for an ingest agent that turns government alert PDFs/HTML into a validated database',
    objective: 'Background for StripCheck\'s ingest agent: rule-based table extraction with an LLM fallback, header mapping as schema matching (CDSCO changed its columns in August 2025), validation, grounded repair and quarantine.',
    questions: [
      'Rule-based PDF table tools (pdfplumber, Camelot, Tabula) and comparative evaluations of PDF table extraction.',
      'Deep table structure recognition and document understanding: TableNet (2019); Table Transformer / PubTables-1M (Smock et al., CVPR 2022); DocLayNet (2022); TableFormer (2022); LayoutLM v1-v3; Donut (2022); Nougat (2023); Docling technical report (2024); newer 2025-2026 systems.',
      'LLM-based structured extraction with JSON schemas, and grounding checks against hallucinated values.',
      'Schema matching (Rahm and Bernstein 2001, VLDB Journal) and LLM-based schema matching (2024-2026); schema/layout drift detection.',
      'Data validation for pipelines (Breck et al. 2019 MLSys; Schelter et al. 2018 VLDB "Deequ"; Great Expectations), quarantine / dead-letter patterns; prior work extracting drug recall or alert data from regulator documents (FDA enforcement reports, openFDA, any CDSCO scraping work).',
    ],
    sources: [
      'CVPR / ICDAR / KDD / VLDB / MLSys papers, arXiv',
      'Official tool documentation',
    ],
  },
  { key: 'evaluation_methodology', kind: 'lit',
    topic: 'evaluation methodology for a perception-plus-agent system tested on synthetic and real images',
    objective: 'Justify StripCheck\'s evaluation: a synthetic golden set of rendered packs with controlled damage, print-and-capture and real photos, an A/B comparison against a lookup-script baseline with a preregistered decision rule, ablations, robustness curves, paired tests and confidence intervals, abstention metrics, and a usability study.',
    questions: [
      'Synthetic text-image data (Jaderberg et al. 2014 MJSynth; Gupta et al. 2016 SynthText) and the synthetic-to-real gap; print-and-capture and physical-world testing.',
      'Corruption robustness benchmarks (Hendrycks and Dietterich 2019, ImageNet-C) and OCR-specific robustness benchmarks under blur, glare, perspective and compression.',
      'Paired comparison of classifiers (McNemar 1947; Edwards 1948; Dietterich 1998 Neural Computation), confidence intervals for proportions (Wilson 1927; Agresti and Coull 1998; Brown, Cai and DasGupta 2001), bootstrap (Efron and Tibshirani 1993).',
      'Evaluating abstaining systems (risk-coverage curves, AURC), ablation-study practice, preregistration (Nosek et al. 2018 PNAS) and its use in ML, agent-evaluation pitfalls and cost/latency reporting (Kapoor et al. 2024).',
      'Usability and app-quality measurement: SUS (Brooke 1996; Bangor, Kortum and Miller 2008/2009; Lewis 2018), MARS for mHealth apps (Stoyanov et al. 2015).',
    ],
    sources: [
      'Statistics journals, ML venues (NeurIPS, ICLR, CVPR), HCI venues (CHI, IJHCI)',
    ],
  },
  { key: 'recall_monitoring', kind: 'lit',
    topic: 'how drug recalls and quality alerts reach, or fail to reach, consumers and pharmacists, and digital tools for continuous monitoring of a person\'s medicines',
    objective: 'Motivate StripCheck\'s "medicine cabinet" that re-checks saved batches whenever a new alert list is ingested, and its explicit statement of data freshness (latest list month loaded).',
    questions: [
      'Recall effectiveness and consumer awareness: FDA recall process and effectiveness checks; studies on patient awareness and response to drug recalls (e.g., valsartan 2018, ranitidine 2019-2020); how recall information reaches patients.',
      'Notification channels (pharmacy-level notification, SMS, apps, EHR alerts) and their evidence; analogues such as vehicle recall lookup by VIN (NHTSA) and food recall apps.',
      'India: the CDSCO "Guidelines on Recall and Rapid Alert System for Drugs" (2012) and evidence on implementation; the reach of NSQ alerts; the Pharmacovigilance Programme of India (PvPI); WHO Medical Product Alerts and the GSMS rapid alert system.',
      'openFDA enforcement/recall data as an example of machine-readable alert data; medication-management apps and evidence on engagement and retention (JMIR mHealth and uHealth).',
      'Any published estimate of the lag between manufacture, sampling, test result and alert publication, and how much of a batch is already sold or consumed by the time an alert appears.',
    ],
    sources: [
      'FDA, NHTSA, WHO and CDSCO documents',
      'Peer-reviewed literature (JAMA, BMJ, Drug Safety, Pharmacoepidemiology and Drug Safety, JMIR mHealth and uHealth)',
    ],
  },
  { key: 'india_user_context', kind: 'lit',
    topic: 'the Indian user context for a phone-based medicine-checking tool: medicine buying and use, trust in chemists, self-medication, smartphone and internet penetration, health and digital literacy, language diversity, accessibility and digital-health infrastructure',
    objective: 'Ground the paper\'s motivation and UI decisions (phone-first, plain language, multilingual verdicts, pharmacist referral) in evidence about Indian users.',
    questions: [
      'Prevalence of self-medication and over-the-counter purchase in India (meta-analyses), the role and number of retail chemists, generic vs branded use, Jan Aushadhi.',
      'Smartphone and internet penetration and the share of Indic-language internet users (TRAI, IAMAI-Kantar reports 2024-2026); health literacy studies in India.',
      'What people do when they suspect a bad medicine; trust in pharmacists; reporting channels (PvPI ADR reporting app).',
      'Digital-health infrastructure and rules relevant to a consumer health app: ABDM, e-pharmacy regulation status, accessibility guidelines (WCAG 2.2; India\'s GIGW 3.0).',
      'Design evidence for health alerts and information for low-literacy or multilingual users (plain language, icons, colour, voice).',
    ],
    sources: [
      'TRAI, IAMAI, NFHS-5, MoHFW, WHO SEARO publications',
      'Peer-reviewed literature (BMJ Open, PLOS ONE, Indian Journal of Pharmacology, JMIR)',
      'W3C WCAG 2.2 and GIGW 3.0',
    ],
  },
  { key: 'cdsco_data_sources', kind: 'eng',
    topic: 'every obtainable source of CDSCO NSQ / spurious drug alert data (legacy monthly PDFs up to mid-2025, the NSQ portal page used since August 2025, press mirrors of the monthly lists, state drug-controller lists, open datasets) as of October 2026',
    objective: 'A concrete, URL-level inventory that lets StripCheck ingest as many real alert lists as possible, including the August 2025 to October 2026 months, with formats and counts.',
    questions: [
      'List the exact URLs of CDSCO monthly NSQ alert PDFs (central-lab and state-lab lists) and any separate spurious-drug lists from January 2024 to the last month published as PDF (around June/July 2025). Known pattern: https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/<file>.pdf, listed on the CDSCO Drug Alerts page. For each: month, central/state, nsq/spurious, URL, and whether it is reachable.',
      'For the NSQ portal page (https://cdsco.gov.in/opencms/opencms/en/Notifications/nsq-drugs/ or similar, from 28 Aug 2025): read its raw HTML via WebFetch and report any script URLs, JSP/JSON endpoints, export/download links or per-month files you can see. (Another investigator inspects the live JavaScript in a browser; you focus on what the HTML and search engines reveal.)',
      'Press mirrors of the monthly lists from August 2025 to October 2026 (medicaldialogues.in pdf_upload files, pharmabiz, expresspharma, etc.): for each month, the URL of a full list (PDF or HTML table) if one exists, and the counts reported (e.g., "CDSCO flags N samples as NSQ and M as spurious in <month>").',
      'State drug-controller sources that publish NSQ/spurious batch lists (e.g., Kerala Drugs Control Department, Karnataka, Maharashtra FDA, Telangana DCA, Tamil Nadu, Himachal Pradesh): URL, format, update frequency.',
      'Open datasets or GitHub scrapers of CDSCO alerts (data.gov.in, Kaggle, GitHub), and the CDSCO website\'s terms of use / copyright policy for reusing this data.',
    ],
    sources: [
      'cdsco.gov.in pages and PDFs; pib.gov.in press releases',
      'medicaldialogues.in, pharmabiz.com, expresspharma.in, financialexpress / economic times health coverage',
      'State drug-controller websites; data.gov.in; GitHub; Kaggle',
    ],
    constraints: [
      'Do not use any browser tool. WebFetch and WebSearch only. Reading PDFs through WebFetch is fine; do not download files to disk.',
      'Put the complete URL inventory in your notes file as tables, in addition to the structured output.',
    ],
  },
  { key: 'tech_stack_oct2026', kind: 'eng',
    topic: 'the current (October 2026) versions, Python support and breaking changes of the libraries StripCheck plans to use, plus the best small local LLMs and vision-language models available in Ollama for a laptop with an NVIDIA RTX 4050 (6 GB VRAM) and 31 GB RAM',
    objective: 'A verified, pin-ready dependency picture and model shortlist so the build does not fail on API drift. The original spec pinned: langgraph>=1.2,<2; langgraph-checkpoint-sqlite>=3.1,<4; langchain-ollama>=1.1,<2; pydantic>=2.10; rapidocr>=3.10,<4; onnxruntime>=1.20; pdfplumber>=0.11,<0.12; rapidfuzz>=3.10; qrcode[pil]>=8.0; streamlit>=1.50; arize-phoenix>=20,<21; arize-phoenix-otel>=0.17,<1; openinference-instrumentation-langchain>=0.1.79,<0.2; Python 3.11; default LLM qwen2.5:3b.',
    questions: [
      'For each package (langgraph, langgraph-checkpoint-sqlite, langchain-core, langchain-ollama, ollama (python client), pydantic, rapidocr, onnxruntime, onnxruntime-gpu, onnxruntime-directml, opencv-python-headless, pdfplumber, pypdfium2, rapidfuzz, qrcode, zxing-cpp, pillow, numpy, pandas, httpx, requests, python-dotenv, arize-phoenix, arize-phoenix-otel, openinference-instrumentation-langchain, fastapi, uvicorn, sse-starlette, python-multipart, mcp, reportlab, pytest, matplotlib, scipy, statsmodels, streamlit): latest version and release date on PyPI (use https://pypi.org/pypi/<name>/json), requires_python, Windows wheels for Python 3.11 and 3.12, and any breaking change relative to the pins above. Recommend Python 3.11 or 3.12 for this stack, with reasons.',
      'LangGraph 1.x: current API for interrupt() and Command(resume=...), stream modes (updates, values, custom, messages; get_stream_writer), durability modes, SqliteSaver import path and constructor, checkpointer behaviour across processes, and anything deprecated since 1.0.',
      'RapidOCR 3.x (docs at rapidai.github.io/RapidOCRDocs and the GitHub repo): does it ship PP-OCRv5 models and which are default; how to select models/languages; does it expose per-word or per-character boxes (return_word_box / return_single_char_box) for English text; GPU options on Windows (onnxruntime-gpu CUDA, DirectML, OpenVINO, torch engines); typical CPU latency.',
      'Ollama (current version, structured outputs with JSON schema, the think parameter for reasoning models, keep_alive): list the best small instruct LLMs (about 8B parameters or less) for reliable JSON-schema output and tool calling available in the Ollama library in Oct 2026 (e.g., qwen3 / qwen3-2507 / newer Qwen, gemma3 / gemma3n / newer Gemma, phi4-mini, llama3.2, granite4, ministral, smollm3, others), with tag, download size, whether it fits 6 GB VRAM with an 8k context, licence, and any known structured-output issues. Same for small vision-language models usable as an OCR second reader (qwen2.5vl, qwen3-vl, gemma3 vision, minicpm-v, granite vision, moondream, others).',
      'Phoenix (arize-phoenix) current version, the "phoenix serve" CLI, phoenix.otel.register parameters, Python support; FastAPI server-sent events (sse-starlette vs any native support); the Python MCP SDK (FastMCP) current API; and for the frontend, the current stable versions of react, react-dom, vite, @vitejs/plugin-react, typescript, react-router and @fontsource packages on the npm registry (https://registry.npmjs.org/<name>/latest).',
    ],
    sources: [
      'pypi.org JSON API, registry.npmjs.org, ollama.com/library and ollama.com/blog, GitHub release pages, official documentation sites',
    ],
    constraints: [
      'Put a proposed requirements.txt (with pins) and a proposed package.json dependency block in your notes file.',
    ],
  },
]

const E1_SCHEMA = {
  type: 'object',
  properties: {
    legacy_pdfs: { type: 'array', items: { type: 'object', properties: {
      month: { type: 'string' }, level: { type: 'string' }, kind: { type: 'string' }, url: { type: 'string' }, reachable: { type: 'string' }, notes: { type: 'string' } },
      required: ['month', 'level', 'kind', 'url'] } },
    portal: { type: 'object', properties: {
      url: { type: 'string' }, how_data_loads: { type: 'string' }, endpoints_found: { type: 'array', items: { type: 'string' } },
      downloadable_files: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } } },
    mirrors: { type: 'array', items: { type: 'object', properties: {
      month: { type: 'string' }, url: { type: 'string' }, format: { type: 'string' }, count_reported: { type: 'string' } }, required: ['url'] } },
    state_sources: { type: 'array', items: { type: 'object', properties: {
      state: { type: 'string' }, url: { type: 'string' }, format: { type: 'string' }, notes: { type: 'string' } }, required: ['state', 'url'] } },
    monthly_counts: { type: 'array', items: { type: 'object', properties: {
      month: { type: 'string' }, nsq: { type: 'string' }, spurious: { type: 'string' }, source_url: { type: 'string' } }, required: ['month'] } },
    open_datasets: { type: 'array', items: { type: 'string' } },
    terms_of_use: { type: 'string' },
    recommendations: { type: 'array', items: { type: 'string' } },
  },
  required: ['legacy_pdfs', 'portal', 'mirrors', 'state_sources', 'recommendations'],
}

const MODEL_ITEM = { type: 'object', properties: {
  ollama_tag: { type: 'string' }, params: { type: 'string' }, size_gb: { type: 'string' }, fits_6gb_vram: { type: 'string' },
  structured_output: { type: 'string' }, license: { type: 'string' }, released: { type: 'string' }, notes: { type: 'string' } },
  required: ['ollama_tag'] }

const E2_SCHEMA = {
  type: 'object',
  properties: {
    python_version: { type: 'string' },
    packages: { type: 'array', items: { type: 'object', properties: {
      name: { type: 'string' }, latest: { type: 'string' }, released: { type: 'string' }, requires_python: { type: 'string' },
      recommended_pin: { type: 'string' }, notes: { type: 'string' } }, required: ['name', 'latest', 'recommended_pin'] } },
    llm_models: { type: 'array', items: MODEL_ITEM },
    vlm_models: { type: 'array', items: MODEL_ITEM },
    ollama_version: { type: 'string' },
    ocr_findings: { type: 'array', items: { type: 'string' } },
    langgraph_findings: { type: 'array', items: { type: 'string' } },
    frontend_stack: { type: 'array', items: { type: 'object', properties: {
      name: { type: 'string' }, version: { type: 'string' }, notes: { type: 'string' } }, required: ['name', 'version'] } },
    risks: { type: 'array', items: { type: 'string' } },
    recommendations: { type: 'array', items: { type: 'string' } },
  },
  required: ['python_version', 'packages', 'llm_models', 'vlm_models', 'recommendations'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    theme: { type: 'string' },
    sources_checked: { type: 'integer' },
    verified: { type: 'integer' },
    corrected: { type: 'integer' },
    unverified: { type: 'integer' },
    unverified_items: { type: 'array', items: { type: 'string' } },
    notable_corrections: { type: 'array', items: { type: 'string' } },
    bib_path: { type: 'string' },
    strongest_findings: { type: 'array', items: { type: 'string' },
      description: 'Up to 8 one-line findings most useful for the paper, each ending with its citation key in brackets' },
  },
  required: ['theme', 'sources_checked', 'verified', 'corrected', 'unverified', 'bib_path', 'strongest_findings'],
}

function bullets(list) { return (list || []).map(x => '- ' + x).join('\n') }

function researchPrompt(t) {
  const dir = t.kind === 'lit' ? NOTES : ENG
  const cons = (t.kind === 'lit' ? LIT_CONSTRAINTS : ENG_CONSTRAINTS).concat(t.constraints || [])
  return 'Research ' + t.topic + '.\n\n' +
    'Objective: ' + t.objective + '\n\n' +
    'Key questions:\n' + bullets(t.questions) + '\n\n' +
    'Suggested sources:\n' + bullets(t.sources) + '\n\n' +
    'Constraints:\n' + bullets(cons) + '\n\n' +
    CONTEXT + '\n\n' +
    'Save your output notes to ' + dir + '\\' + t.key + '.md\n\n' +
    '**As a first step, you must read ' + SKILL + '\\references\\researcher.md for instructions on how to conduct research.**'
}

function verifyPrompt(t) {
  const notes = NOTES + '\\' + t.key + '.md'
  const bib = NOTES + '\\' + t.key + '.bib'
  return 'You are the citation verifier for one theme of an academic literature survey (theme: ' + t.key + '). The notes at ' + notes + ' were written by another researcher. Every reference in them will be cited in a research paper and a university thesis, so a fabricated or garbled reference is a serious failure.\n\n' +
    'For EVERY academic or official source in the notes:\n' +
    '1. Papers and books: confirm title, authors, year, venue and DOI using Crossref (https://api.crossref.org/works?query.bibliographic=<url-encoded title>&rows=3, or https://api.crossref.org/works/<doi>), arXiv (https://export.arxiv.org/api/query?search_query=ti:%22<title>%22), Semantic Scholar (https://api.semanticscholar.org/graph/v1/paper/search?query=<title>&fields=title,year,authors,venue,externalIds), DBLP or the publisher page.\n' +
    '2. Reports, laws, regulations and web pages: open the URL and confirm it exists and says what the notes claim.\n' +
    '3. Spot-check every specific number, date or strong claim attributed to a source (percentages, counts, dates). Correct it or flag it.\n\n' +
    'Then:\n' +
    '- Write ' + bib + ' containing BibTeX entries ONLY for sources you VERIFIED or CORRECTED, with accurate fields and a doi or url. Use @misc with url and note = {Accessed 25 Oct 2026} for web sources. Keep the researcher\'s citation keys (lowercase ASCII authorYEARword) unless they are malformed or duplicated.\n' +
    '- Append to the notes file a section "## Verification log" with one line per source: VERIFIED, CORRECTED (say what changed) or UNVERIFIED (say why). Mark claims in the notes that rest only on unverified sources with [UNVERIFIED]. Do not otherwise rewrite the researcher\'s notes.\n' +
    '- Never invent bibliographic data. If a source cannot be found, mark it UNVERIFIED and leave it out of the .bib file.\n\n' +
    'Return the structured summary, including up to 8 one-line findings that are most useful for the paper, each ending with its citation key in brackets.'
}

const REPORT_QUESTION = 'What do the scientific literature and current practice (up to October 2026) say about the problem StripCheck addresses and the techniques it uses: (1) the burden of substandard and falsified medicines and India\'s NSQ/spurious alert and recall system; (2) existing approaches to verifying medicines (traceability and authentication, field quality screening, consumer apps) and why none of them answers "is this exact batch on a regulator\'s list of failed samples?"; (3) the component techniques: OCR of packaging and its confident misreads, noisy-channel / confusion-aware post-correction and ALPR-style hotlist matching, record linkage with clerical review, LLM agent architectures with external verifiers and human-in-the-loop, abstention plus safety and risk communication, and document/table extraction with validation; (4) recall notification and continuous monitoring; (5) the Indian user context; and (6) evaluation methodology; and which research gaps does StripCheck fill? The report must be organised so it can be condensed into the Related Work section of an IEEE paper and expanded into a thesis literature-survey chapter. Include a summary table of the key works (authors, year, venue, method or contribution, key finding, limitation, relevance to StripCheck). Cite only sources that the "Verification log" sections in the notes mark as VERIFIED or CORRECTED, use the citation keys from the .bib files in the notes folder, and never cite anything marked UNVERIFIED.'

phase('Research')
log('Launching 14 researchers (12 literature themes, 2 engineering investigations)')

const results = await pipeline(
  THEMES,
  (t) => agent(researchPrompt(t), {
    label: 'research:' + t.key,
    phase: 'Research',
    agentType: 'general-purpose',
    schema: t.key === 'cdsco_data_sources' ? E1_SCHEMA : t.key === 'tech_stack_oct2026' ? E2_SCHEMA : undefined,
  }),
  (res, t) => {
    if (res == null) { log('research failed: ' + t.key); return null }
    if (t.kind !== 'lit') return { key: t.key, kind: 'eng', data: res }
    return agent(verifyPrompt(t), { label: 'verify:' + t.key, phase: 'Verify', schema: VERIFY_SCHEMA, effort: 'high' })
      .then(v => ({ key: t.key, kind: 'lit', verification: v }))
  },
)

const lit = results.filter(r => r && r.kind === 'lit')
const eng = results.filter(r => r && r.kind === 'eng')
log(lit.length + '/12 literature themes researched and verified; ' + eng.length + '/2 engineering scans done')

phase('Synthesize')
const report = await agent(
  'Read the notes in ' + NOTES + '\\ and synthesize into a research report that answers: ' + REPORT_QUESTION + '\n\n' +
  'Earlier research in this conversation to build on: none\n\n' +
  'Save your final report to this exact path: ' + BASE + '\\reports\\StripCheck literature survey.md\n\n' +
  '**As a first step, you must read ' + SKILL + '\\references\\report-writer.md for instructions on how to write your research report.**',
  { label: 'write-report', phase: 'Synthesize', agentType: 'general-purpose' },
)

return { lit, eng, report }

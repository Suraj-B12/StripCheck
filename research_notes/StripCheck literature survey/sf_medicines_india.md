Status: COMPLETE

# Substandard and falsified (SF) medicines: global and Indian burden; India's NSQ/spurious legal and alert framework

Checklist:
- [x] Q1 Definitions (WHO WHA 2017 SF; Indian law: D&C Act 1940 ss.16, 17, 17A, 17B, 27; 2008 amendment)
- [x] Q2 Prevalence and harms (WHO GSMS 2017; Ozawa 2018; later meta-analyses; CDSCO National Drug Survey 2014-16; other Indian studies)
- [x] Q3 CDSCO monthly NSQ/spurious alert system, counts 2024-2026, Aug 2025 online portal, 2012 Recall and Rapid Alert guidelines
- [x] Q4 Recent incidents (Gambia, Uzbekistan 2022; Cameroon 2023; MP Coldrif 2025; 2026) and regulatory responses
- [x] Q5 Awareness of NSQ alerts; lag between manufacture, sampling, test result and alert

## Q1 Definitions: WHO and Indian law

### Cited Findings (WHO)
- WHO working definitions approved by the 70th World Health Assembly (WHA70, May 2017), which also adopted "Substandard and Falsified (SF) medical products" as the official term (replacing "SSFFC"). Substandard ("out of specification") = "authorized medical products that fail to meet either their quality standards or specifications, or both"; Unregistered/unlicensed = "Medical products that have not undergone evaluation and/or approval by the National or Regional Regulatory Authority" for the market where marketed/distributed; Falsified = "Medical products that deliberately/fraudulently misrepresent their identity, composition or source." — [WHO, Definitions of SF medical products](https://www.who.int/teams/regulation-prequalification/incidents-and-SF/background/definitions) (Accessed 25 Oct 2026).
  - Source note: WHO definitions page, opened. Relevance to StripCheck: the WHO split maps onto CDSCO's NSQ (~substandard) vs spurious (~falsified) labels, and justifies StripCheck's two separate positive verdicts (FLAGGED for NSQ batches vs SUSPECTED_FAKE for spurious/identity-mismatch cases).
- WHO fact sheet (dated 3 Dec 2024) restates: substandard products "do not meet quality standards and specifications, often due to poor manufacturing practices or inadequate quality control"; falsified products "deliberately misrepresent their identity, composition or source"; repeats the 2017 estimate that 1 in 10 medicines in LMICs failed quality tests and that countries spend an estimated US$30.5 billion/year on SF products. — [WHO fact sheet: Substandard and falsified medical products, 3 Dec 2024](https://www.who.int/news-room/fact-sheets/detail/substandard-and-falsified-medical-products).
  - Relevance: authoritative, current headline numbers for the paper's opening paragraph.

### Cited Findings (Indian law)
- Drugs and Cosmetics Act 1940, Section 17B ("Spurious drugs"; inserted in its present form by Act 68 of 1982, which substituted ss.17, 17A, 17B, per CourtBook annotation, not independently verified): a drug "shall be deemed to be spurious" (a) "if it is manufactured under a name which belongs to another drug"; (b) if it is an imitation of, a substitute for, or resembles another drug "in a manner likely to deceive", or bears another drug's name unless plainly marked to reveal its true character; (c) if the label/container names a purported manufacturer "which individual or company is fictitious or does not exist"; (d) "if it has been substituted wholly or in part by another drug or substance"; (e) "if it purports to be the product of a manufacturer of whom it is not truly a product." — [AdvocateKhoj bare act, s.17B](https://www.advocatekhoj.com/library/bareacts/drugsandcosmetics/17b.php); amendment history per [CourtBook s.17B](https://courtbook.in/drugs-and-cosmetics-act-1940/section-17B) (search snippet only).
  - Relevance: clauses (c) and (e) make "spurious" fundamentally an identity/manufacturer misrepresentation; this directly motivates StripCheck's field-by-field corroboration of manufacturer and brand (a strip whose batch matches an alert entry but whose printed manufacturer differs, or a spurious-listed batch whose label claims a genuine maker, is the SUSPECTED_FAKE case). It also explains why CDSCO spurious entries often carry a note that the "actual manufacturer" disowned the batch.
- Section 17A ("Adulterated drugs"): deemed adulterated if (a) it consists wholly/partly of "filthy, putrid or decomposed substance"; (b) prepared/packed/stored under insanitary conditions; (c) container of poisonous/deleterious substance; (d) contains a non-prescribed colour for colouring only; (e) "contains any harmful or toxic substance which may render it injurious to health"; (f) "any substance has been mixed therewith so as to reduce its quality or strength." — [AdvocateKhoj bare act, s.17A](https://www.advocatekhoj.com/library/bareacts/drugsandcosmetics/17a.php).
  - Relevance: diethylene-glycol (DEG) contaminated syrups (Q4) are legally "adulterated" (s.17A(e)) as well as NSQ; CDSCO alert lists may label such batches as adulterated/spurious, so StripCheck's ingest schema must keep the regulator's category string rather than collapse it to a binary.
- Section 27 (penalties), pre-2008 text (as still reproduced on AdvocateKhoj): (a) adulterated (17A) or spurious (17B) or NSQ drug likely to cause death or grievous hurt: 5 years to life + fine >= Rs 10,000; (b) other adulterated or unlicensed sale: 1-3 years + fine >= Rs 5,000; (c) other spurious: 3-5 years + fine >= Rs 5,000; (d) any other contravention of Chapter IV (this is where ordinary NSQ falls): 1-2 years and fine. — [AdvocateKhoj bare act, s.27](https://www.advocatekhoj.com/library/bareacts/drugsandcosmetics/27.php). NOTE: this page shows the unamended text; use the 2008 Amendment Act below for current penalties.
- Drugs and Cosmetics (Amendment) Act 2008 (Act No. 26 of 2008, assented 5 Dec 2008): s.27(a) raised to "not less than ten years but which may extend to imprisonment for life" and fine "not less than ten lakh rupees or three times value of the drugs confiscated, which-ever is more", with fine paid as compensation to the victim or, on death, to relatives; s.27(b) 3-5 years + fine >= Rs 1 lakh or 3x value; s.27(c) (spurious) 7 years to life + fine >= Rs 3 lakh or 3x value; s.27(d) fine >= Rs 20,000. Inserted s.32B (compounding of minor offences), s.36AB (Special Courts for adulterated/spurious drug offences), s.36AC (such offences cognizable; bail only if Public Prosecutor heard and court satisfied of reasonable grounds of innocence, i.e. effectively non-bailable); s.32 amended to let "a recognised consumer association" and "the person aggrieved" institute prosecution. — [The Drugs and Cosmetics (Amendment) Act, 2008, No. 26 of 2008 (PRS India copy)](https://prsindia.org/files/bills_acts/acts_parliament/2008/the-drugs-and-cosmetics-(amendment)-act,-2008.pdf); also on [CDSCO site](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/acts_rules/DC_ACT_AMENDMENT_2008_file.pdf) (not opened).
  - Relevance: the severity gap between spurious (cognizable, 7 years to life) and ordinary NSQ (s.27(d), often administrative action) justifies StripCheck reporting the regulator's category separately and treating a spurious match with stricter evidence rules (verifier must confirm manufacturer/brand corroboration), since a false SUSPECTED_FAKE accusation is weighty.
- "NSQ" is not a single statutory section: a drug is "not of standard quality" if it fails the standards in the Second Schedule (s.16, Act; not opened, see Gaps). CDSCO's "Regulatory guidelines for taking action on samples of drugs declared spurious or not of standard quality in the light of enhanced penalties under the D&C (Amendment) Act, 2008" (Doc. No. CDSCO/ENFORCEMENT/NSQGUIDELINE/001, Version 00; undated in text) classifies Government Analyst reports into Category A (spurious and adulterated; spurious drugs "manufactured concealing the true identity of the product and made to resemble another drug, especially some popular brand"; "may or may not contain the active ingredients"; "usually manufactured by unlicensed anti-social elements but sometimes licensed manufacturers"), Category B (grossly substandard by licensed makers: e.g. assay <70% for thermolabile products, failing disintegration/dissolution, fungus in liquids, sterility/pyrogen/endotoxin failure in parenterals, vaccine potency failure) and Category C (minor defects: broken/chipped tablets, discolouration, weight variation, labelling errors). Prosecution is for spurious/adulterated (with s.36AC) and grossly substandard with intent/negligence; minor NSQ via administrative measures (suspension/cancellation, compounding). Clause 12 asks State Drug Control Organizations to "create a rapid alert system" for spurious/adulterated drug information. Annexure A reproduces 1993 Drugs Consultative Committee NSQ defect guidelines. — [CDSCO, Regulatory guidelines on taking action on NSQ drugs](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadReportsFiles/Regulatory%20guidlines%20on%20taking%20action%20on%20NSQ%20drugs.pdf).
  - Relevance: shows that NSQ ranges from trivial (labelling, chipped tablets) to dangerous (sterility, assay failure); the CDSCO monthly list's "reason for failure" column therefore matters, and StripCheck should surface the failure reason to the user rather than a bare flag. Note also that India's NSQ category conflates WHO "substandard" with some labelling defects.
- Section 16 ("Standards of quality"): (1) for a drug, "standard quality" means the drug complies with the standard set out in the Second Schedule (pharmacopoeial or prescribed standards); (2) the Central Government may amend the Second Schedule after consulting the Drugs Technical Advisory Board with at least three months' notice in the Official Gazette. Hence "Not of Standard Quality" (NSQ) = failing the s.16/Second Schedule standard as declared by a Government Analyst. — [AdvocateKhoj bare act, s.16](https://www.advocatekhoj.com/library/bareacts/drugsandcosmetics/16.php).
- Section 17 ("Misbranded drugs"): deemed misbranded if (a) coloured, coated, powdered or polished to conceal damage or "made to appear of better or greater therapeutic value" than it is; (b) not labelled in the prescribed manner; (c) its label/container/accompanying material bears a statement, design or device that "makes any false claim for the drug" or is "false or misleading in any particular." — [AdvocateKhoj bare act, s.17](https://www.advocatekhoj.com/library/bareacts/drugsandcosmetics/17.php).
  - Relevance: label content itself is a regulated object (s.17(b),(c)); StripCheck's reading of the label (batch, dates, manufacturer) operates on exactly the information the law requires to be truthful, and label inconsistencies are themselves a legal signal, not just an OCR nuisance.

### Takeaway (Q1)
WHO (WHA70, 2017) uses three categories: substandard (authorized but out of specification), unregistered/unlicensed, and falsified (deliberate misrepresentation of identity, composition or source). Indian law uses four overlapping statutory categories under the Drugs and Cosmetics Act 1940: NSQ (fails s.16/Second Schedule standards, roughly WHO "substandard"), misbranded (s.17), adulterated (s.17A) and spurious (s.17B, roughly WHO "falsified": misrepresented name, maker or substitution). The 2008 Amendment (Act 26 of 2008) made spurious/adulterated offences cognizable and effectively non-bailable, with up to life imprisonment, while ordinary NSQ is mostly handled administratively under CDSCO's Category A/B/C guidelines.

### Inferences (Q1)
- The NSQ vs spurious split in CDSCO alerts maps cleanly onto StripCheck's FLAGGED vs SUSPECTED_FAKE verdicts; a spurious entry usually means the named manufacturer disowned the batch, so identity corroboration (manufacturer, brand) is the critical evidence.
- Because NSQ covers both trivial and dangerous defects, the agent should show the regulator's stated reason for failure rather than imply all flagged batches are equally dangerous.

### Gaps (Q1)
- Second Schedule contents not opened. India Code (official) version of the consolidated Act not opened; amendment-history footnotes (Act 68 of 1982) rely on a CourtBook search snippet.
- Whether the Jan Vishwas (Amendment of Provisions) Act 2023 changed any D&C Act s.27(d)/compounding provisions was not checked.

## Q2 Prevalence and harms

### Cited Findings (global)
- WHO (28 Nov 2017) released two reports: (1) the first report of the WHO Global Surveillance and Monitoring System (GSMS, launched July 2013; data to 30 June 2017) and (2) "A study on the public health and socioeconomic impact of substandard and falsified medical products" (WHO with the Member State Mechanism). Estimated failure rate 10.5% of medical products in LMICs ("1 in 10"), based on >100 published quality surveys, 88 LMICs, ~48,000 samples (only 178 samples from high-income countries). Modelled harms: 72,000-169,000 child pneumonia deaths/yr from SF antibiotics (University of Edinburgh model); 116,000 (64,000-158,000) additional malaria deaths/yr in sub-Saharan Africa from SF antimalarials (LSHTM model), costing US$38.5m (21.4-52.4m)/yr in extra care. GSMS had received 1,500 reports since 2013: African Region 42%, Americas 21%, European 21%, Western Pacific 8%, Eastern Mediterranean 6%, South-East Asia Region only 2%. Antimalarials and antibiotics most reported; products split almost evenly between generic and patented. WHO cautions estimates are "just an indication" given lack of accurate data. — [WHO news release, 28 Nov 2017](https://www.who.int/news/item/28-11-2017-1-in-10-medical-products-in-developinG-countries-is-substandard-or-falsified).
  - Relevance: seminal "1 in 10" motivation; the 2% SEARO share of GSMS reports (India is in SEARO) signals under-reporting in the region, motivating citizen-side checking tools. Note: I opened the WHO press release, not the full 2017 report PDFs; report figures above are as stated in the release.
- Ozawa et al. (2018), JAMA Netw Open 1(4):e181662: systematic review of 265 studies (400,647 samples); meta-analysis of 96 studies (67,839 samples) in LMICs. Pooled SF prevalence 13.6% (95% CI 11.0-16.3%); Africa 18.7% (12.9-24.5%), Asia 13.7% (8.2-19.1%); antimalarials 19.1% (15.0-23.3%), antibiotics 12.4% (7.1-17.7%). Eight economic estimates (mostly market-size) ranged US$10-200 billion/yr (median US$31.25 billion), mostly without disclosed methods. — [Ozawa et al. 2018, JAMA Network Open](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2696509), DOI 10.1001/jamanetworkopen.2018.1662.
  - Relevance: the most-cited peer-reviewed prevalence figure; supports the claim that SF medicines are common enough in Asia (~1 in 7 samples) that a batch-level check by the end user is worthwhile.
- McManus D, Naughton BD (2020), BMJ Glob Health 5(8):e002393, DOI 10.1136/bmjgh-2020-002393: systematic review of 33 SF sampling studies 2013-2018; median SF prevalence 25% (IQR 7.7-34%) vs 28.5% in a 2013 review; study quality improving but definitive prevalence cannot be drawn due to variable sample sizes, designs and missing context. — [PubMed 32859648](https://pubmed.ncbi.nlm.nih.gov/32859648/) (abstract opened).
  - Relevance: prevalence estimates are design-dependent and fragile; supports framing StripCheck around the official alert list (a verifiable signal) rather than any probabilistic "risk score".
- Ozawa S, Chen H-H, Lee Y-F, Higgins CR, Yemeke TT (2022), Am J Trop Med Hyg 106(6):1778-1790, DOI 10.4269/ajtmh.21-1123: 130 studies, 95,520 samples in LMICs; pooled SF prevalence 12.4% (95% CI 10.2-14.6%) for essential medicines; of failed samples, 25.9% had <80% of stated API, 13.8% <50% API (likely falsified, about 1 in 7 failures), 12.5% no/incorrect API; <50%-API share higher in Asia (23.4%) than Africa (11.4%); about six in seven failures appear substandard rather than falsified. — [PMC9209904](https://pmc.ncbi.nlm.nih.gov/articles/PMC9209904/).
  - Relevance: most poor-quality medicine is substandard (manufacturing/QC failure), which no packaging inspection can detect; only lab testing reveals it, and the public result of that testing is the NSQ list. This is the core argument for StripCheck's list-lookup design over visual counterfeit detection.
- Tabernero P, Newton PN (2023), BMJ Glob Health 8(7):e012039, DOI 10.1136/bmjgh-2023-012039: anti-TB medicines, 65 publications, 7,682 samples from 22 countries; 15.2% failed at least one quality test (14.1% in quality surveys); authors call for rapid, affordable portable screening devices for pharmacy inspectors. — [PubMed 37433693](https://pubmed.ncbi.nlm.nih.gov/37433693/) (abstract opened).
  - Relevance: India has the world's largest TB burden; SF anti-TB drugs drive resistance, so batch-level checking matters for chronic-therapy patients (supports the medicine-cabinet re-check).
- Rusatira JC, Novoa MD, Uwimana JB, Persaud C, Pal E, Khan A, Michtalik H, Padayachee N, Lumpkin M, Preston C, Ahmed S (2026), PLOS Glob Public Health 6(9):e0006326 (published 2 Sep 2026), DOI 10.1371/journal.pgph.0006326: PRISMA 2020/PROSPERO review of studies 2010-2025, 123 studies, 34 African countries, 36,069 samples of MNCH medicines and antimalarials; pooled failure 17.9% (95% CI 13.6-22.7); substandard 12.8% vs falsified 1.2%; highest failure for corticosteroids (65.0%), uterotonics (43.9%), hematinics (34.7%); antimalarials, antihypertensives, antibiotics 15-20%; mystery-client purchasing was a significant predictor of heterogeneity. — [PubMed 42685013](https://pubmed.ncbi.nlm.nih.gov/42685013/) (abstract opened).
  - Relevance: the most recent (2026) meta-analysis; confirms the substandard-dominates-falsified pattern (about 10:1), consistent with India's NSQ >> spurious ratio. Africa-only, so cite for global context, not India.

### Cited Findings (India: National Drug Survey 2014-16)
- National Drug Survey 2014-16 (conducted by National Institute of Biologicals, Noida, for MoHFW/CDSCO): 224 drug molecules and selected FDCs; samples tested at seven central and three state drug-testing laboratories [UNVERIFIED: lab counts not found in opened sources]. Overall 3.16% of drugs found NSQ, as stated in a Rajya Sabha written reply reported on 7 Aug 2017. — [Medical Dialogues (news), 7 Aug 2017](https://business.medicaldialogues.in/minister-admits-that-3-16-percent-of-drugs-in-india-not-of-standard-quality).
- Parliamentary reply reported 25 Jun 2019: survey drew 47,012 samples from government and private sources; 17.8% came from government sources, where NSQ was 10.02% and spurious 0.059%. States/UTs were asked to legally sample batches declared NSQ. — [Medical Dialogues (news), 25 Jun 2019](https://business.medicaldialogues.in/more-than-10-percent-of-drug-samples-from-government-sources-not-of-standard-quality).
- OPENED (news, 23 Feb 2017, The News Minute, citing the Health Ministry): NIB Noida survey, 47,012 samples tested (the same article also says 47,954 drawn; the 942 difference is unexplained), 1,850 NSQ and 13 spurious, stated as "3.16 per cent" NSQ and "0.0245 per cent" spurious. This CONFIRMS the figures 3.16% and 0.0245% as the ministry's published headline numbers. DISCREPANCY: raw counts do not reproduce the percentages (1,850/47,012 = 3.94%; 13/47,012 = 0.028%), so the headline rates are probably weighted/adjusted estimates (my inference; methodology not verified because the primary MoHFW report chapters at mohfw.gov.in returned HTTP 403). Cite the percentages as "as reported by the Ministry", not as raw ratios. — [The News Minute (news), 23 Feb 2017](https://www.thenewsminute.com/amp/story/news/1850-drugs-sold-india-not-standard-quality-health-ministry-57646).
- Search-snippet only (not opened): a Rajya Sabha reply of 7 Feb 2023 (PQ 259) gave retail-outlet rates of 3% NSQ and 0.023% spurious. Recommend citing "about 3% NSQ (3.16%) and well under 0.1% spurious (0.0245% overall; 0.023% retail; 0.059% government sources)" with the parliamentary/ministry sources.
- Other Indian quality studies (search-snippet summaries from news/aggregators only; NOT opened or verified, do not cite as primary): pilot pharmacy-level studies reporting 12% (Delhi) and 5% (Chennai) substandard samples; a Delhi wholesale-trader sampling study at 7%; single-drug studies of diclofenac (15.62%, n=32) and amoxicillin (13.04%, n=46); a journal letter (JKIMSU 2016) stating Indian prevalence estimates range from 0.04% to 34%. Source for the summary: search results incl. [IndiaSpend](https://www.indiaspend.com/n-838516) and [Medical Dialogues](https://medicaldialogues.in/1-in-7-indian-drugs-revealed-as-sub-standard). Wide dispersion of estimates (0.04%-34%) is itself the finding; primary papers still need to be located.
  - Relevance: in India the measured problem is overwhelmingly NSQ (substandard) rather than spurious, so a tool keyed to the official NSQ list addresses the larger share of measured risk; but the low base rate also means most scans will be NOT_LISTED, so StripCheck must word that verdict carefully (not "safe") and avoid false positives from batch-number collisions.

### Takeaway (Q2)
Globally about 1 in 10 (WHO 2017, 10.5%) to 12-14% (Ozawa 2018: 13.6%; Ozawa 2022: 12.4%) of sampled medicines in LMICs are SF, with most failures substandard rather than falsified (about 6:1 to 10:1); estimates are design-dependent (McManus 2020 median 25%). India's official survey (NIB, 2014-16) reported ~3.16% NSQ and ~0.0245% spurious, with ~10% NSQ in government-sourced samples; later annual regulator-targeted testing gives ~2.7-3.2% NSQ. Harm estimates are model-based (WHO/Edinburgh/LSHTM) and empirical harm data are scarce (Pal 2025).

### Inferences (Q2)
- India's official figures are far below global LMIC pooled rates (about 3% vs 12-14%); possible reasons (sampling frame, lab capacity, definitions, under-detection) are not resolved by the sources; the paper should not claim India's true rate equals either.
- Because substandard dominates, a regulator-list lookup (which captures lab-detected chemical failures) is more relevant to the measured burden than visual counterfeit detection.

### Gaps (Q2)
- Full GSMS 2017 report PDFs not opened (only the WHO release). Primary MoHFW National Drug Survey report not opened (403); methodology of weighting unverified. No primary peer-reviewed Indian pharmacy-level prevalence paper was opened. No Indian-specific economic-burden figure found; Ozawa 2018 global economic range (US$10-200 billion, median 31.25) and WHO's US$30.5 billion are market-size style estimates.

## Q3 CDSCO NSQ/spurious alert system and recall rules

### Cited Findings (monthly alert mechanics and counts; mostly news, labelled)
- Monthly counts as reported by news agencies from health-ministry/CDSCO statements (NEWS; search-result summaries, individual articles NOT opened unless marked): Feb 2025: 47 central + 56 state NSQ ([The Week/PTI, 28 Mar 2025](https://www.theweek.in/wire-updates/national/2025/03/28/del114-health-drugs-quality.html)); Apr 2025: 60 central + 136 state, 1 spurious (Bihar) ([The Week/PTI, 20 May 2025](https://www.theweek.in/wire-updates/national/2025/05/20/des100-health-drugs-quality.html)); Sep 2025: 52 central + 60 state, 1 spurious (Chhattisgarh) ([Dinamalar](https://www.dinamalar.com/news/kalvimalar-news-en/central-drugs-laboratories-find-52-drug-samples-34not-of-standard-quality34-in-september-alert/57724)); Oct 2025: 211 (63 central + 148 state), spurious 3 Bihar + 2 Delhi ([IANS, 21 Nov 2025](https://ianslive.in/cdsco-labs-flag-211-drug-samples-as-not-of-standard-quality-in-october--20251121110525)); Nov 2025: 205 (64 central + 141 state), 2 spurious from Ghaziabad made by unauthorised makers using another company's brand ([IANS, 19 Dec 2025](https://ianslive.in/cdsco-labs-flag-205-drug-samples-as-not-of-standard-quality-in-november--20251219160347)); Dec 2025: 167 (74 central + 93 state), spurious: 4 from North Zone Ghaziabad + 1 each FDA Ahmedabad, Bihar, Maharashtra; ministry states the NSQ/spurious list "is put up on the CDSCO portal on a monthly basis as part of routine regulatory surveillance" ([Deccan Herald/PTI](https://www.deccanherald.com/india/167-drug-samples-flagged-as-not-of-standard-quality-in-december-2025-health-ministry-3870598); [DT Next](https://www.dtnext.in/lifestyle/wellbeing/cdsco-labs-flag167drug-samples-as-not-of-standard-quality-indecember)).
  - Caveat: these totals are from news summaries; check against the CDSCO/SUGAM JSON that StripCheck already ingests (the project's own data is a better primary source for monthly counts).
- OPENED: July 2026 alert (published by ETV Bharat 21 Aug 2026): 40 central-lab NSQ + 240 state-lab NSQ, 1 spurious (Bihar; unauthorised entity using another company's brand name); headline "280" while components sum to 281 (unexplained). Described as "routine monthly surveillance" done "in collaboration with state regulators"; NSQ failures (dissolution, assay, uniformity, etc.) are "batch-specific" and do not necessarily reflect on the company's other products. Ministry context: over the past five years, more than 950 enforcement actions and 3,599 criminal prosecution cases against makers/distributors/sellers of spurious and adulterated drugs. — [ETV Bharat (news), 21 Aug 2026](https://www.etvbharat.com/en/bharat/cdsco-flags-280-drug-samples-as-nsq-or-spurious-in-july-enn26082107816).
  - Relevance: confirms (i) the alert is batch-specific, which justifies StripCheck's exact batch lookup as the primary key, and (ii) the monthly lag (July samples published ~21 Aug), which motivates the medicine-cabinet re-check when new lists arrive. State labs now contribute the majority of entries (240/280), so ingesting both the central and state lists is essential.
- Aug 2025 dedicated NSQ link: a secondary write-up (Corpseed, 1 Sep 2025, by Parul Bohral) reports that CDSCO launched a dedicated link for NSQ drug alerts to improve transparency and give stakeholders quick access; the opened page did not give the notice date, the URL or search fields. A search-result summary of the same item stated a notice dated 28 Aug 2025 and search by product name, manufacturing details and NSQ result, but I could not confirm these from the opened text. — [Corpseed (commercial news), 1 Sep 2025](https://www.corpseed.com/news/cdsco-launches-dedicated-link-for-nsq-drug-alerts). Treat the 28 Aug 2025 date as UNVERIFIED pending CDSCO's own notice.
- PRIMARY (opened, scanned PDF read as image): CDSCO (Enforcement and Intelligence cell) NOTICE dated 28 Aug 2025, signed by Dr Rajeev Singh Raghuvanshi, Drugs Controller General (India), "Availability of Not of Standard Quality (NSQ) Alert on New Link in CDSCO Website": "The NSQ alerts are published on a monthly basis by CDSCO and are made available on the CDSCO website"; NSQ alerts "can now be accessed via a new dedicated link"; "details like Name of product, manufacturing details, NSQ results etc., are easily searchable"; new link https://cdsco.gov.in/opencms/opencms/en/Notifications/nsq-drugs/ . — [CDSCO Notice, 28 Aug 2025 (PDF)](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/aret%20all%20Stakeholders.pdf). This supersedes the UNVERIFIED caveat on the Corpseed item above: the 28 Aug 2025 date is now confirmed from the primary notice.
  - Relevance: the authoritative citation for the move from monthly PDFs to a searchable online NSQ listing; the structured, searchable source is what makes automated ingestion (StripCheck's ingest agent and SUGAM JSON) feasible, while the legacy PDFs (2019 to mid-2025) still require PDF/HTML parsing and row repair/quarantine.
- PRIMARY (opened): CDSCO "Latest Alerts" page (accessed 25 Oct 2026) lists, as separate monthly PDFs, "CDSCO NSQ Alert", "State NSQ Alert" and "List of spurious Drugs" for each month, plus a "Drug Alert" list (e.g. "Revise list drug alert May-2025"). Release dates show the publication lag: lists for June 2025 (CDSCO NSQ, State NSQ, spurious) were released 18 Jul 2025; spurious list for May 2025 released 20 Jun 2025; revised May 2025 drug alert released 18 Jul 2025. The page also carries ad hoc alerts (e.g. 21 Aug 2025 theft-in-transit alert for Novo Nordisk products). After Jun 2025 no monthly NSQ PDFs appear on this page (consistent with the move to the new link). — [CDSCO Latest Alerts](https://cdsco.gov.in/opencms/opencms/en/Latest-Alerts).
  - Relevance: documents (a) three parallel lists (central NSQ, state NSQ, spurious) that StripCheck's ingest must merge with provenance, (b) the existence of "revised" lists (so ingested rows must be versioned and re-checked), and (c) a roughly 3-7 week lag from month-end to publication, which supports the cabinet re-check design.

### Cited Findings (recall and rapid alert rules; PRIMARY, opened)
- CDSCO "Guidelines on Recall and Rapid Alert System for Drugs (Including Biologicals & Vaccines)", Document No. CDSCO/RRAS, Ver. 00. Original effective date 23 Nov 2012 (the copy on the CDSCO site is labelled "Version: 2017" with "Effective Date: 23/11/2012"); a revised "Version: 2024" has effective date 18 Jul 2024. Both texts (compared by grep) keep the same timelines. Key content (2024 text):
  - Background: the Act and Rules reference recalls (Schedule M; licence conditions Rules 74(j) and 78(i)) but "effective and uniform recall procedure, with time lines at every level of supply chain is required and at present auditing and accountability is not in place", observed where drugs were declared NSQ by a Government Analyst, after serious adverse effects/deaths, banned drugs (s.26A), or voluntary withdrawals.
  - Classification: Class I = "reasonable probability that the use of, or exposure to, a defective product will cause serious adverse health consequences or death" (plus s.26A-banned drugs and products whose licence is suspended/cancelled); Class II = temporary adverse consequences or remote probability of serious harm; Class III = not likely to cause adverse health consequences. For NSQ drugs, the 39th Drugs Consultative Committee categories A, B, C map to Class I, II, III.
  - Level of recall: Class I to wholesale, retail AND consumer level, with "public announcements ... using print/electronic media aids viz. Newspapers, Television, Radio etc."; Class II to wholesale and retail; Class III to wholesale only.
  - Timelines: "within 24 hours up to a maximum of 72 hours for Class I recall, for class II recall up to a maximum of 10 days and for Class III recall up to a maximum of 30 days"; for Class I, stop sale/distribution within 24 hours and physical recall completed within 72 hours.
  - Procedure (annexed SOP QMS-GNL-010): when a Government Analyst declares a sample NSQ in Form 13, the lab forwards it to the Drugs Inspector, who informs the State Licensing Authority (SLA) where the manufacturer is located; the SLA orders stop-sale and recall (Annexure I/II) and logs it; for Class I the SLA communicates "through fastest mode ... mass media through newspapers, TV and in the departmental web portal" and "It is preferred that information's are given by SMS or through website to the public and the regulatory mechanism shall try to reach that level"; Drugs Inspector freezes stock.
  — [CDSCO RRAS Guidelines, Version 2024, effective 18 Jul 2024 (PDF)](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/Guidelinerapid24.pdf); [CDSCO RRAS Guidelines, labelled Version 2017, effective 23 Nov 2012 (PDF)](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/4GuidelineRecalRapidAlert.pdf).
  - Relevance: the guideline's own aspiration that the public be reached "by SMS or through website" is exactly the consumer-level gap StripCheck targets. Importantly, only Class I recalls reach the consumer level; Class II/III NSQ batches are recalled only from wholesale/retail, so units already in households are never actively reached. That is the strongest regulatory argument for a consumer-side batch check and for the medicine-cabinet re-check. The monthly NSQ list is a public disclosure, but is not itself a consumer recall notice.

### Cited Findings (annual national testing totals)
- Lok Sabha reply by Union Health Minister J. P. Nadda (to Dr Mohammad Jawed; reported 18 Dec 2025): samples tested / declared NSQ / declared spurious-or-adulterated, by financial year: 2020-21: 84,874 / 2,652 / 263; 2021-22: 88,844 / 2,545 / 379; 2022-23: 96,713 / 3,053 / 424; 2023-24: 1,06,150 / 2,988 / 282; 2024-25: 1,16,323 / 3,104 / 245. Lists of NSQ/spurious/adulterated drugs from Central Drugs Testing Laboratories are "regularly uploaded" to the CDSCO website under "Drug Alerts". Risk-based inspections of manufacturing and testing firms (CDSCO with states) since Dec 2022: >960 premises inspected, >860 actions (show-cause notices, stop-production orders, suspensions, cancellations, warning letters). SSDRS scheme: Rs 756 crore released to states/UTs; 17 new state drug-testing labs built and 24 upgraded. — [Medical Dialogues (news, by Susmita Roy), 18 Dec 2025](https://medicaldialogues.in/news/industry/pharma/over-14300-drug-samples-fail-quality-tests-in-five-years-minister-160877).
  - Derived (my arithmetic): NSQ rate among tested samples = 3.1% (2020-21), 2.9% (2021-22), 3.2% (2022-23), 2.8% (2023-24), 2.7% (2024-25); spurious/adulterated 0.21-0.44%. These are rates among regulator-targeted (not random) samples, so not population prevalence. Five-year totals: 14,342 NSQ and 1,593 spurious/adulterated.
  - Search-snippet only (not opened): prosecutions launched 663 (2022-23), 604 (2023-24), 961 (2024-25) [UNVERIFIED: Deccan Herald/PTI 22 Jul 2025 says 604 prosecutions in 2024-25] ([Rajya Sabha PQ, 17 Dec 2024](https://rsdebate.nic.in/bitstream/123456789/752644/1/PQ_266_17122024_U2491_p259_p261.pdf); [Deccan Herald](https://www.deccanherald.com/india/3104-drugs-found-to-be-not-of-standard-quality-between-april-24-and-march-25-govt-3642541), 403 on fetch). Indiamedtoday gives 96,173 for 2022-23 (likely typo for 96,713).
  - Relevance: roughly 3,000 NSQ and 250-450 spurious batches per year means the lookup table grows by a few thousand rows/year; small enough for a local SQLite index on a laptop (supports the offline design), but large enough that OCR-confusion batch collisions across products are plausible (supports field-by-field corroboration).

### Takeaway (Q3)
CDSCO publishes three parallel monthly lists (central-lab NSQ, state-lab NSQ, spurious), historically as PDFs on its Latest Alerts page about 3-7 weeks after month end, and since a 28 Aug 2025 notice via a searchable NSQ link. Monthly volumes in 2025-26 were roughly 160-280 NSQ entries (state labs now the majority) plus 1-5 spurious; annual national totals are about 3,000 NSQ and 250-450 spurious/adulterated batches. The 2012 (revised 2024) Recall and Rapid Alert guidelines reach the consumer level only for Class I.

### Inferences (Q3)
- Lists are a public disclosure, not a consumer recall notice; Class II/III units already at home are never actively reached, which is the regulatory gap a consumer-side batch check fills.
- Revised lists and a month-level lag mean a saved batch can become flagged weeks later; the cabinet re-check is justified.

### Gaps (Q3)
- Start date of the monthly NSQ alert practice not established in my sources (CDSCO pages open here show 2025 lists; StripCheck's data begins Jan 2019). Monthly counts are from news summaries, not CDSCO totals. SUGAM portal JSON not examined here. The search-summary figure of a Rajya Sabha reply is unopened.

## Q4 Recent incidents and regulatory responses

### Cited Findings (incidents)
- The Gambia, 2022 (PRIMARY): WHO Medical Product Alert N°6/2022, 5 Oct 2022: four substandard (contaminated) paediatric syrups (Promethazine Oral Solution, Kofexmalin Baby Cough Syrup, Makoff Baby Cough Syrup, Magrip N Cold Syrup), stated manufacturer Maiden Pharmaceuticals Ltd (Haryana, India), identified in The Gambia (reported to WHO Sep 2022), with "unacceptable amounts" of diethylene glycol (DEG) and ethylene glycol (EG); possible spread via informal markets; manufacturer "has not provided guarantees to WHO on the safety and quality". The alert page itself gives no death count. — [WHO Medical Product Alert N°6/2022, 5 Oct 2022](https://www.who.int/news/item/05-10-2022-medical-product-alert-n-6-2022-substandard-(contaminated)-paediatric-medicines).
  - NEWS (opened, Tribune India/Reuters-sourced, 21 Dec 2022): Gambian parliamentary health committee report tabled 20 Dec 2022 cites "at least 70" child deaths from acute kidney injury (an embedded tweet in the same page says 66; figures conflict across outlets) and urged legal action against Maiden; India told WHO that tests on samples of the same batches met specification; Maiden's MD Naresh Kumar Goyal denied wrongdoing; Maiden's production licence was suspended. — [Tribune India (news), 21 Dec 2022](https://www.tribuneindia.com/news/nation/gambia-lawmakers-say-india-based-drug-maker-maiden-to-blame-for-child-kidney-injury-deaths-462921).
  - Relevance: export-side failure. Shows that a batch made in India can harm abroad and that WHO alerts list product + batch + maker; a batch-level lookup is the right granularity. Note WHO labels these "substandard (contaminated)" even though Indian law would class DEG adulteration under s.17A.
- Madhya Pradesh "Coldrif", 2025 (PRIMARY): WHO Medical Product Alert N°5/2025, 13 Oct 2025: DEG found in "at least three" oral liquid medicines, specific batches of COLDRIF, Respifresh TR and ReLife (manufacturers Sresan Pharmaceutical, Rednex Pharmaceuticals, Shape Pharma; batch numbers only in annex PDF, not opened). WHO identified localized clusters of acute illness and child fatalities in India on 30 Sep 2025; CDSCO informed WHO on 8 Oct 2025. State authorities halted production at implicated sites, suspended product authorizations and initiated recalls; CDSCO told WHO none were exported and there was no evidence of illegal export; WHO still advised targeted surveillance of informal supply chains. — [WHO Medical Product Alert N°5/2025, 13 Oct 2025](https://www.who.int/news/item/13-10-2025-medical-product-alert-n-5-2025--substandard-(contaminated)-oral-liquid-medicines).
  - News/secondary (search summaries, NOT opened): DEG levels reported as Coldrif 48.6% w/v, Respifresh TR 1.34%, ReLife 0.61% (limit 0.1%); child death toll reported between 20 and 23+, mainly Chhindwara district, MP ([Tribune India](https://www.tribuneindia.com/news/world/who-issues-alert-over-3-adultrated-cough-syrups-manufactured-in-india-cautions-use-globally); [Scroll](https://scroll.in/latest/1087658/who-warns-against-three-contaminated-indian-cough-syrups-after-deaths-of-22-children)). Final verified death count not established here (see Gaps). NEWS (opened): PTI report of 15 Oct 2025 quoting Chhindwara Additional Collector Dhirendra Singh: toll "24" children, mostly under five, with suspected kidney failure; two more under treatment; at least three Rajasthan deaths reported separately (unclear whether counted) ([Tribune India/PTI, 15 Oct 2025](https://www.tribuneindia.com/news/madhya-pradesh/mp-coldrif-cough-syrup-fatality-count-reaches-24-after-2-more-children-die)). Later counts (search summary only, not opened) reach 25 but include a non-Coldrif death. Use "at least 24 children (official figure as of 15 Oct 2025)".
  - Relevance: the first major domestic DEG tragedy of the period; shows that harm can occur before any monthly NSQ listing exists (the alert followed the deaths), so StripCheck must state that NOT_LISTED is not a safety guarantee and must re-check saved batches when later lists or ad hoc alerts arrive.
- Uzbekistan (and Cambodia), 2022-23 (PRIMARY): WHO Medical Product Alert N°1/2023, 11 Jan 2023: AMBRONOL syrup and DOK-1 Max syrup, stated manufacturer Marion Biotech Pvt Ltd (Uttar Pradesh, India); Uzbekistan's national QC labs found unacceptable DEG and/or EG; reported to WHO 22 Dec 2022 (Uzbekistan); the page (later updated) adds a report from Cambodia on 3 Apr 2023; no guarantees from the manufacturer; possible distribution in other countries of the region and via informal markets. The WHO page does not state a death count. — [WHO Medical Product Alert N°1/2023, 11 Jan 2023](https://www.who.int/news/item/11-01-2023-medical-product-alert-n-1-2023-substandard-%28contaminated%29-liquid-dosage-medicines).
  - News (search summary, not opened): 18 child deaths in Uzbekistan linked to DOK-1 Max; Indian authorities suspended Marion Biotech's licence and stopped production [UNVERIFIED: not in the Down To Earth page] ([Down To Earth](https://www.downtoearth.org.in/health/who-alert-on-sub-standard-cough-syrups-made-by-noida-firm-87086)).
- Cameroon, 2023 (PRIMARY): WHO Medical Product Alert N°5/2023, 19 Jul 2023: NATURCOLD syrup (paracetamol + phenylephrine + chlorpheniramine), DEG up to 28.6% vs limit of not more than 0.10%; detected in Cameroon, reported to WHO 13 Mar 2023; packaging names "FRAKEN INTERNATIONAL (England)" but the UK MHRA "has confirmed that no such manufacturer exists in the UK"; origin still under enquiry. The WHO alert does NOT name an Indian manufacturer. — [WHO Medical Product Alert N°5/2023, 19 Jul 2023](https://www.who.int/news/item/19-07-2023-medical-product-alert-n-5-2023--substandard-(contaminated)-syrup-medicines).
  - News (search summary, not opened): Indian regulators reportedly ordered Riemann Labs (Indore [UNVERIFIED detail]; spelled "Reimann" by the outlet) to stop production as the alleged maker; Cameroon investigated six child deaths ([Health Policy Watch](https://healthpolicy-watch.news/made-in-india-another-cough-syrup-caught-by-the-who-for-contamination/)). Treat the India link as REPORTED, not confirmed by WHO.
  - Relevance: Naturcold is simultaneously substandard (contaminated) and falsified-like (fictitious marketer), mirroring Indian s.17B(c) "fictitious or does not exist". This is the scenario where StripCheck's manufacturer-field corroboration matters most: a fictitious maker never appears in any licence database or alert entry, so the agent should abstain (CANT_VERIFY) or flag inconsistency rather than return NOT_LISTED as if reassuring.
- Coldrif follow-up (NEWS, opened): CDSCO letter of 7 Oct 2025 to all States/UTs, signed by DCG(I) Dr Rajeev Singh Raghuvanshi, after the Chhindwara (MP) child deaths: inspections of facilities whose drugs had earlier been declared NSQ found "manufacturers are not testing each batch of excipients, inactive and active pharmaceutical ingredients"; reiterates that rules require testing of every raw-material and finished-product batch with records, and asks states to enforce via inspections and to ensure vendor qualification and sourcing of excipients from approved vendors. About 20 children under five reportedly died in MP; Tamil Nadu sealed the plant. — [Tribune India (news), 9 Oct 2025](https://www.tribuneindia.com/news/india/cough-syrup-deaths-drug-regulator-flags-lapses-in-testing-raw-material).
- (NEWS, opened) Sresan Pharma owner Ranganathan Govindan arrested in Chennai by MP police on the night of 8-9 Oct 2025; Tamil Nadu drug authorities found 46-48% DEG (limit 0.1%); TN Drugs Control issued stop-production order, froze syrup stocks and suspended the licence; the Kancheepuram facility lacked valid GMP certification and held unbilled DEG containers; at least nine states banned Coldrif; at least 20 child deaths, mostly Chhindwara, some in Rajasthan; charges include drug adulteration and culpable homicide not amounting to murder. — [Tribune India (news), 9 Oct 2025](https://www.tribuneindia.com/news/india/owner-of-pharma-firm-behind-toxic-coldrif-cough-syrup-arrested-in-chennai/amp).
  - Search-summary only (not opened): Union Health Ministry advisory of 3 Oct 2025 said cough and cold medicines should not be prescribed to children under two; an MP probe found non-pharmaceutical-grade propylene glycol untested for DEG/EG; the ministry initially said Chhindwara samples showed no DEG/EG before TN tests found it ([WION](https://www.wionews.com/india-news/cough-syrup-deaths-states-ban-coldrif-after-diethylene-glycol-presence-confirmed-beyond-permissible-limits-1759597609077)). Conflicting early reports; the 46-48% TN finding and WHO alert are the reliable anchors.

### Cited Findings (regulatory responses)
- Mandatory pre-export testing of cough syrups (NEWS, opened): DGFT notification (number not given in article) made cough-syrup exports permissible only after export samples are tested and a Certificate of Analysis (CoA) is produced, "with effect from June 1, 2023"; CoA from Indian Pharmacopoeia Commission, RDTL Chandigarh, CDL Kolkata, CDTL Chennai/Hyderabad/Mumbai, RDTL Guwahati, or NABL-accredited state drug-testing labs. Article links it to the deaths of 66 children in The Gambia and 18 in Uzbekistan. — [Outlook India (news), 23 May 2023](https://outlookindia.com/national/cough-syrups-to-undergo-testing-before-export-from-june-1-news-288654). DGFT notification text itself NOT opened.
- Revised Schedule M (GMP): notified 28 Dec 2023 (the G.S.R. number 922(E) is widely cited but I did not open the Gazette to confirm it); manufacturers with turnover > Rs 250 crore given 6 months (effective 28/29 Jun 2024; PIB sources differ by a day); turnover <= Rs 250 crore given 12 months; in Feb 2025 MoHFW conditionally extended the MSME deadline to 31 Dec 2025 for firms applying in Form 'A' with an upgrade plan to the Central Licence Approving Authority (application deadline 11 May [2025]). — PIB release PRID 2102291 ([PIB, Feb 2025](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2102291); HTTP 403 when fetched, facts from search snippet) and [Lexplosion (legal-compliance news), 14 Feb 2025](https://lexplosion.in/health-ministry-extends-schedule-m-compliance-deadline-for-small-and-medium-manufacturers-with-turnover-below-rs-250-crores-to-31st-december-2025/) (opened).
- Schedule M status (search-summary only, not opened; commercial/compliance-vendor sources conflict): the revised Schedule M is repeatedly cited as G.S.R. 922(E) dated 28 Dec 2023 (consistent across several search results; Gazette not opened); one source says it came into force 5 Jan 2024; MSME deadline sources give 31 Dec 2025 vs 1 Jan 2026; a vendor dashboard claims the DCGI directed states on 7 Nov 2025 to act strictly against non-compliant units and that no further extension was granted. UNVERIFIED; check CDSCO notices before citing 2026 status.
- Jan Vishwas (Amendment of Provisions) Act 2023: reported (search summaries of law-firm and press pieces, not opened) to have amended the D&C Act, notified 28 Mar 2024 to take effect 31 Dec 2024, with the Bill stage making s.27(d) compoundable on payment of Rs 20,000; enacted scope NOT confirmed. A Cyril Amarchand blog snippet lists compoundable provisions as s.13(1)(b), s.28 and s.28A and bars compounding of repeat offences, which does not mention s.27(d), so the final Act may differ from the Bill. UNVERIFIED; treat as an open item.
- Risk-based inspections of manufacturing/testing firms by CDSCO + states since Dec 2022 (>960 premises, >860 actions) and SSDRS lab strengthening (17 new, 24 upgraded labs) — see Q3 annual-totals entry ([Medical Dialogues, 18 Dec 2025](https://medicaldialogues.in/news/industry/pharma/over-14300-drug-samples-fail-quality-tests-in-five-years-minister-160877)).
  - Relevance: all responses are supply-side (GMP, export CoA, raw-material testing, inspections). None gives the patient a way to check a pack already at home, which is the gap StripCheck fills; StripCheck complements, not replaces, these controls.
- QR/barcode authentication mandates (PRIMARY, opened): CDSCO FAQ (dated 21 Jul 2023) on G.S.R. 823(E) of 17 Nov 2022 (Drugs Rules 1945 amended; new Schedule H2 listing the top 300 brands of formulations): manufacturers must print/affix a Bar Code or QR Code with (i) unique product identification code, (ii) proper/generic name, brand name, (iv) manufacturer name and address, (v) batch number, (vi) date of manufacture, (vii) date of expiry, (viii) manufacturing licence number; in force 1 Aug 2023 for any batch of a Schedule H2 brand made on or after that date; on the primary label or, if space is inadequate, the secondary label; UPIC decided by the manufacturer's own SOP; voluntary for other brands. — [CDSCO FAQs on QR code, 21 Jul 2023 (PDF)](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Final%20FAQs%20on%20QR%20code%2021.07.2023.pdf).
- CDSCO "Guidance for Identification and Verification of Spurious Drugs" (undated 2-page PDF, opened): restates s.17B; notes G.S.R. 20(E) of 18 Jan 2022 requiring a QR code at each packaging level on every API (bulk drug) manufactured or imported, effective 1 Jan 2023 (UPIC, batch no., mfg and exp. dates), and G.S.R. 823(E) for top-300 brands effective 1 Aug 2023; gives a 3-step consumer process: check label for code, "Scan the Bar Code/Quick Response Code with the Mobile Phone", read the returned information "for product authenticity/genuineness". — [CDSCO, Guidance for Identification and Verification of Spurious Drugs (PDF)](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/Guidance-for-Identification-and-Verification-of-Spurious-Drugs.pdf).
  - Relevance: STRONG design support. The regulator itself prescribes phone-based scanning as the consumer authenticity check, and the QR payload contains exactly StripCheck's target fields (batch, mfg/exp dates, manufacturer), which justifies StripCheck's QR-first pipeline with OCR fallback (most of the market beyond 300 brands has no mandated code). Limitation: the UPIC is manufacturer-defined with no central verification registry named in these documents, so a scanned QR proves only what the label claims; cross-checking against the CDSCO NSQ/spurious lists adds an independent regulator signal.
  - UNVERIFIED (single secondary blog source in search summary, not opened): G.S.R. 506(E) of 22 Jun 2026 reportedly extends the QR mandate to all vaccines, antimicrobials, anticancer and NDPS drugs, effective 1 Jul 2027 (antimicrobials 1 Jul 2028) ([Zelthy blog](https://www.zelthy.com/blog/schedule-h2-expanded-drug-categories)). Must be checked in the Gazette before citing.

### Cited Findings (2026 incidents; NEWS)
- Feb 2026, near Patna, Bihar: Delhi Police (Crime Branch, NDPS Act FIR) busted a clandestine unlicensed factory; seized ~1.19 lakh spurious zinc tablets, 42,000 fake azithromycin tablets, 27 kg paracetamol powder, 13 kg tramadol powder (valued > Rs 5 crore), 500 g alprazolam; nine arrested; described as the third such bust in Bihar within days. — [The Morning Voice (news), 24 Feb 2026](https://www.tmv.in/article/delhi-police-bust-fake-drug-factory-near-patna-nine-arrested-drugs-worth-5-crore-seized-date=2026-02-24).
- Jul 2026, Dehradun, Uttarakhand: joint UP FSDA + Ghaziabad Crime Branch raid on a factory producing fakes bearing the names of Cipla, Lupin, Dr Reddy's, Elder, Micro Labs, Mankind, Intas, Abbott, Sun Pharma, Aristo, Macleods and Zydus; seizure estimated Rs 5-7 crore; traced from earlier raids in Lucknow and Ghaziabad; no arrests reported at publication. — [ETV Bharat (news), 23 Jul 2026](https://www.etvbharat.com/en/state/fake-medicines-worth-rs-5-7-crore-seized-from-dehradun-factory-enn26072302950).
- No 2026 mass-casualty contaminated-medicine incident involving Indian products was found in my searches (searched to 25 Oct 2026); this is a negative finding from limited searching, not proof of absence.
  - Relevance: 2026 fakes copy well-known brands (exactly the Schedule H2 QR-code brands), so a fake may carry a copied or fabricated QR code; StripCheck should therefore not treat a successful QR decode as proof of authenticity and should corroborate QR content against OCR of the printed text and the alert lists.

### Takeaway (Q4)
Indian-made oral liquids contaminated with diethylene glycol caused child deaths in The Gambia (2022; 66-70 deaths reported, conflicting), Uzbekistan (2022; 18 reported, news) and Madhya Pradesh (2025; at least 24 reported by 15 Oct 2025; WHO Alert 5/2025). Cameroon 2023 (Naturcold) is WHO-documented but its Indian origin is only reported by news. Responses were supply-side: export CoA testing from 1 Jun 2023, revised Schedule M (28 Dec 2023, MSME deadline extended to end 2025), raw-material testing enforcement (CDSCO letter 7 Oct 2025), inspections, and QR/barcode mandates (top-300 brands from 1 Aug 2023). 2026 events found are counterfeit-factory busts, not mass-casualty poisonings.

### Inferences (Q4)
- Harm preceded listing in each case, so NOT_LISTED must never be phrased as safe. Fakes of top brands are exactly the Schedule H2 QR brands, so a decoded QR is not proof of authenticity.

### Gaps (Q4)
- Gazette texts (Schedule M, DGFT export notification, Jan Vishwas Act, G.S.R. 506(E) of 2026) not opened. Final Coldrif death count and legal outcomes unknown. Riemann Labs/Cameroon India link is news-only. No death count in WHO alerts themselves.

## Q5 Awareness and alert lag

### Cited Findings (awareness)
- Pal E, Merchant L, Koffi AK, Mehta R, Rusatira JC, Kubiak L, Michtalik HJ, Caubel P, Ahmed S (2025), J Pharm Policy Pract 18(1):2550369 (published 12 Sep 2025), DOI 10.1080/20523211.2025.2550369: scoping review of 78 peer-reviewed studies (past 15 years); health and economic harm data are "predominantly based on statistical models, and empirical data are grossly lacking"; "Knowledge of risks, identification of SFM, and reporting to regulatory authorities are substantially low among healthcare providers and general public"; interventions are predominantly supply-side, with "a noticeable deficiency" in provider- and consumer-focused interventions; recommends "digital health interventions" and public-awareness campaigns. — [PubMed 40958951](https://pubmed.ncbi.nlm.nih.gov/40958951/) (abstract opened).
  - Relevance: the most direct literature support for StripCheck's premise: a consumer-facing digital tool addresses a documented demand-side gap.
- Falah MM, Daar E, Zahra D, Dillon MJ (2025), BMJ Glob Health 10(5):e018189 (24 May 2025), DOI 10.1136/bmjgh-2024-018189: Jordan, Jan-Jun 2023, 209 public + 136 healthcare professionals (convenience sample); only 24% of public and 35% of professionals familiar with SF medicines; of those aware, only 8% (public) and 25% (professionals) correctly identified SF medicines; 17% of public and 26% of professionals reported experiences with SF medicines; 81% of the public and all professionals who encountered SF medicines did not report them, citing lack of awareness of reporting mechanisms. — [PubMed 40412817](https://pubmed.ncbi.nlm.nih.gov/40412817/) (abstract opened).
  - Relevance: non-Indian but recent quantitative evidence that consumers and pharmacists cannot reliably identify SF medicines by inspection; supports automating the check against official lists. Use as an analogue, labelled as Jordan.
- India-specific: I found NO peer-reviewed study that measures Indian consumers' or pharmacists' awareness of CDSCO NSQ/spurious monthly alerts specifically (PubMed E-utilities searches on awareness/knowledge + substandard/spurious/falsified/counterfeit + pharmacist/consumer/public, run 25 Oct 2026, plus a web search). Nearest Indian items (search summaries only, NOT opened): a Bangalore email survey of 122 community pharmacists in which 50.81% believed online pharmacies could be a source of counterfeit/substandard medicines ([IMSEAR record](https://imsear.searo.who.int/items/2bca5708-02a4-4d26-94a5-ba6a259ce939)); an older Liberty Institute/International Policy Network report in which 92% of interviewed pharmacists said they had been offered substandard or spurious drugs at cheaper prices ([SecuringIndustry summary](https://www.securingindustry.com/pharmaceuticals/survey-measures-substandard-medicines-from-indian-traders/s40/a487)). Neither verified.
- Thakur N (2023), Med Anthropol Theory 10(3):1-21, DOI 10.17157/mat.10.3.7279: ethnography with Indian traders and officials arguing that in Indian pharma trade quality or fake-ness is produced in a drug's paperwork rather than its chemical composition, reflecting a regulatory shift from "drug safety" to "drug security". — [PubMed 38660628](https://pubmed.ncbi.nlm.nih.gov/38660628/) (abstract opened).
  - Relevance: a critical counterpoint for the Discussion: label/paper-based verification (which StripCheck does) checks documentary identity, not chemistry; StripCheck can only say whether the regulator has already tested and flagged the batch.

### Cited Findings (lag between manufacture, sampling, test result and alert)
- Structural lag evidence (PRIMARY): the CDSCO Latest Alerts page shows month-M lists released around the 18th-20th of month M+1 (e.g. June 2025 lists released 18 Jul 2025; May 2025 spurious list released 20 Jun 2025) ([CDSCO Latest Alerts](https://cdsco.gov.in/opencms/opencms/en/Latest-Alerts)); news shows the same ~3-week lag in 2025-26 (e.g. July 2026 alert reported 21 Aug 2026) ([ETV Bharat, 21 Aug 2026](https://www.etvbharat.com/en/bharat/cdsco-flags-280-drug-samples-as-nsq-or-spurious-in-july-enn26082107816)). Note: "month M" is the month the test result was reported/compiled, not the month of manufacture or sampling.
- The recall guideline's process chain (PRIMARY): Government Analyst Form 13 report -> Drugs Inspector -> State Licensing Authority -> stop-sale/recall order to manufacturer -> recall within 24-72 h (Class I), 10 days (II) or 30 days (III) ([CDSCO RRAS Guidelines 2024](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/Guidelinerapid24.pdf)). The guideline sets no deadline for the analyst's test itself or for publication on the monthly list.
- Fryze I, Naughton BD (2025), BMJ Open 15(10):e103672 (27 Oct 2025), DOI 10.1136/bmjopen-2025-103672: systematic review of 13 papers using official recall databases of 23 countries (2010-2024); substandard medicines had significantly higher recall rates than falsified; leading reasons were contamination, out-of-specification results, stability and packaging; "India was identified as a common source of SF medicines in Zambia, Sri Lanka, Brazil and Nepal"; calls for harmonised, standardised recall notifications. — [PubMed 41145244](https://pubmed.ncbi.nlm.nih.gov/41145244/) (abstract opened).
  - Relevance: supports the need for a standardised, machine-readable alert schema (StripCheck's validated SQLite index with field normalisation) and confirms Indian-made products feature in other countries' recalls.
- I found NO published quantitative study of the lag from manufacture -> sampling -> Government Analyst result -> CDSCO list publication for Indian NSQ alerts. StripCheck's own SUGAM dataset (Jan 2019 - Sep 2026; manufacturing date, expiry date and reporting month per row) could measure the manufacture-to-alert lag directly, which would be an original contribution (my inference; not a cited finding).

### Takeaway (Q5)
Demand-side evidence is thin: a 2025 scoping review (78 studies) finds low public/provider knowledge of SF risk and few consumer-focused interventions; a Jordan survey shows 24% public familiarity. No India-specific study of awareness of CDSCO NSQ alerts, and no published study of the manufacture-to-alert lag, was found. Structural lag from CDSCO's own page is roughly 3-7 weeks after the result month; manufacture-to-alert lag is unmeasured.

### Inferences (Q5)
- Measuring manufacture-to-alert lag from StripCheck's SUGAM dataset (mfg date versus reporting month) would be an original contribution.

### Gaps (Q5)
- Indian pharmacist awareness items are unverified search summaries. Lag from sampling to Government Analyst report is undocumented in sources opened.

## BibTeX

```bibtex
@misc{who2017definitions,
  author = {{World Health Organization}},
  title = {Definitions of Substandard and Falsified (SF) Medical Products},
  howpublished = {WHO Regulation and Prequalification, Incidents and SF},
  year = {2017},
  url = {https://www.who.int/teams/regulation-prequalification/incidents-and-SF/background/definitions},
  note = {Definitions approved by the 70th World Health Assembly, May 2017. Accessed 25 Oct 2026}
}

@misc{who2024factsheet,
  author = {{World Health Organization}},
  title = {Substandard and Falsified Medical Products (Fact Sheet)},
  year = {2024},
  month = dec,
  url = {https://www.who.int/news-room/fact-sheets/detail/substandard-and-falsified-medical-products},
  note = {Dated 3 Dec 2024. Accessed 25 Oct 2026}
}

@misc{who2017oneinten,
  author = {{World Health Organization}},
  title = {1 in 10 Medical Products in Developing Countries Is Substandard or Falsified},
  howpublished = {WHO News Release},
  year = {2017},
  month = nov,
  url = {https://www.who.int/news/item/28-11-2017-1-in-10-medical-products-in-developinG-countries-is-substandard-or-falsified},
  note = {28 Nov 2017; accompanies the WHO GSMS report and the public-health and socioeconomic impact study. Accessed 25 Oct 2026}
}

@article{ozawa2018prevalence,
  author = {Ozawa, Sachiko and Evans, Daniel R. and Bessias, Sophia and Haynie, Deson G. and Yemeke, Tatenda T. and Laing, Sarah K. and Herrington, James E.},
  title = {Prevalence and Estimated Economic Burden of Substandard and Falsified Medicines in Low- and Middle-Income Countries: A Systematic Review and Meta-analysis},
  journal = {JAMA Network Open},
  year = {2018},
  volume = {1},
  number = {4},
  pages = {e181662},
  doi = {10.1001/jamanetworkopen.2018.1662}
}

@misc{dcact1940s17b,
  author = {{Government of India}},
  title = {The Drugs and Cosmetics Act, 1940: Sections 16, 17, 17A, 17B and 27 (bare act text)},
  howpublished = {AdvocateKhoj bare acts library},
  year = {1940},
  url = {https://www.advocatekhoj.com/library/bareacts/drugsandcosmetics/17b.php},
  note = {Sections 16, 17, 17A, 27 at sibling URLs (16.php, 17.php, 17a.php, 27.php); s.27 shown in pre-2008 form. Accessed 25 Oct 2026}
}

@misc{goi2008dcamendment,
  author = {{Government of India}},
  title = {The Drugs and Cosmetics (Amendment) Act, 2008 (No. 26 of 2008)},
  howpublished = {Gazette of India; copy hosted by PRS Legislative Research},
  year = {2008},
  month = dec,
  url = {https://prsindia.org/files/bills_acts/acts_parliament/2008/the-drugs-and-cosmetics-(amendment)-act,-2008.pdf},
  note = {Assented 5 Dec 2008. Accessed 25 Oct 2026}
}

@misc{cdsco2008nsqguidelines,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Regulatory Guidelines for Taking Action on Samples of Drugs Declared Spurious or Not of Standard Quality in the Light of Enhanced Penalties under the Drugs and Cosmetics (Amendment) Act, 2008},
  howpublished = {CDSCO, Document No. CDSCO/ENFORCEMENT/NSQGUIDELINE/001, Version 00},
  year = {n.d.},
  url = {https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadReportsFiles/Regulatory%20guidlines%20on%20taking%20action%20on%20NSQ%20drugs.pdf},
  note = {Publication year not stated in the document. Accessed 25 Oct 2026}
}

@misc{medicaldialogues2017nds,
  author = {{Medical Dialogues}},
  title = {3.16 Percent of Drugs in India Not of Standard Quality, Admits Ministry},
  howpublished = {Medical Dialogues (news)},
  year = {2017},
  month = aug,
  url = {https://business.medicaldialogues.in/minister-admits-that-3-16-percent-of-drugs-in-india-not-of-standard-quality},
  note = {7 Aug 2017; reports Rajya Sabha written reply on National Drug Survey 2014-16. Accessed 25 Oct 2026}
}

@misc{singhania2019nds,
  author = {Singhania, Meghna A.},
  title = {More than 10 Percent of Drug Samples from Government Sources Not of Standard Quality},
  howpublished = {Medical Dialogues (news)},
  year = {2019},
  month = jun,
  url = {https://business.medicaldialogues.in/more-than-10-percent-of-drug-samples-from-government-sources-not-of-standard-quality},
  note = {25 Jun 2019; reports parliamentary reply on National Drug Survey 2014-16. Accessed 25 Oct 2026}
}

@misc{cdsco2025nsqlink,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Notice: Availability of Not of Standard Quality ({NSQ}) Alert on New Link in {CDSCO} Website},
  howpublished = {CDSCO Enforcement and Intelligence Cell, signed by R. S. Raghuvanshi, DCG(I)},
  year = {2025},
  month = aug,
  url = {https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/aret%20all%20Stakeholders.pdf},
  note = {Dated 28 Aug 2025; new link https://cdsco.gov.in/opencms/opencms/en/Notifications/nsq-drugs/. Accessed 25 Oct 2026}
}

@misc{cdsco2026latestalerts,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Latest Alerts},
  howpublished = {CDSCO website},
  year = {2026},
  url = {https://cdsco.gov.in/opencms/opencms/en/Latest-Alerts},
  note = {Monthly CDSCO NSQ, State NSQ and spurious lists with release dates. Accessed 25 Oct 2026}
}

@misc{etvbharat2026july,
  author = {{ETV Bharat}},
  title = {{CDSCO} Flags 280 Drug Samples as {NSQ} or Spurious in July},
  howpublished = {ETV Bharat (news)},
  year = {2026},
  month = aug,
  url = {https://www.etvbharat.com/en/bharat/cdsco-flags-280-drug-samples-as-nsq-or-spurious-in-july-enn26082107816},
  note = {21 Aug 2026. Accessed 25 Oct 2026}
}

@misc{bohral2025nsqlink,
  author = {Bohral, Parul},
  title = {{CDSCO} Launches Dedicated Link for {NSQ} Drug Alerts},
  howpublished = {Corpseed (news)},
  year = {2025},
  month = sep,
  url = {https://www.corpseed.com/news/cdsco-launches-dedicated-link-for-nsq-drug-alerts},
  note = {1 Sep 2025; secondary to cdsco2025nsqlink. Accessed 25 Oct 2026}
}

@misc{cdsco2012recall,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Guidelines on Recall and Rapid Alert System for Drugs (Including Biologicals \& Vaccines)},
  howpublished = {CDSCO, Document No. CDSCO/RRAS, Ver. 00 (copy labelled Version 2017)},
  year = {2012},
  month = nov,
  url = {https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/4GuidelineRecalRapidAlert.pdf},
  note = {Effective 23 Nov 2012. Accessed 25 Oct 2026}
}

@misc{cdsco2024recall,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Guidelines on Recall and Rapid Alert System for Drugs (Including Biologicals \& Vaccines), Version 2024},
  howpublished = {CDSCO, Document No. CDSCO/RRAS, Ver. 00},
  year = {2024},
  month = jul,
  url = {https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/Guidelinerapid24.pdf},
  note = {Effective 18 Jul 2024. Accessed 25 Oct 2026}
}

@misc{roy2025fiveyears,
  author = {Roy, Susmita},
  title = {Over 14,300 Drug Samples Fail Quality Tests in Five Years: Minister},
  howpublished = {Medical Dialogues (news)},
  year = {2025},
  month = dec,
  url = {https://medicaldialogues.in/news/industry/pharma/over-14300-drug-samples-fail-quality-tests-in-five-years-minister-160877},
  note = {18 Dec 2025; reports Lok Sabha reply by Health Minister J. P. Nadda. Accessed 25 Oct 2026}
}

@misc{who2022alert6,
  author = {{World Health Organization}},
  title = {Medical Product Alert N{\textdegree}6/2022: Substandard (Contaminated) Paediatric Medicines},
  year = {2022},
  month = oct,
  url = {https://www.who.int/news/item/05-10-2022-medical-product-alert-n-6-2022-substandard-(contaminated)-paediatric-medicines},
  note = {5 Oct 2022 (The Gambia; Maiden Pharmaceuticals). Accessed 25 Oct 2026}
}

@misc{who2025alert5,
  author = {{World Health Organization}},
  title = {Medical Product Alert N{\textdegree}5/2025: Substandard (Contaminated) Oral Liquid Medicines},
  year = {2025},
  month = oct,
  url = {https://www.who.int/news/item/13-10-2025-medical-product-alert-n-5-2025--substandard-(contaminated)-oral-liquid-medicines},
  note = {13 Oct 2025 (Coldrif, Respifresh TR, ReLife; India). Accessed 25 Oct 2026}
}

@misc{who2023alert1,
  author = {{World Health Organization}},
  title = {Medical Product Alert N{\textdegree}1/2023: Substandard (Contaminated) Liquid Dosage Medicines},
  year = {2023},
  month = jan,
  url = {https://www.who.int/news/item/11-01-2023-medical-product-alert-n-1-2023-substandard-%28contaminated%29-liquid-dosage-medicines},
  note = {11 Jan 2023 (Uzbekistan, Cambodia; Marion Biotech). Accessed 25 Oct 2026}
}

@misc{who2023alert5,
  author = {{World Health Organization}},
  title = {Medical Product Alert N{\textdegree}5/2023: Substandard (Contaminated) Syrup Medicines},
  year = {2023},
  month = jul,
  url = {https://www.who.int/news/item/19-07-2023-medical-product-alert-n-5-2023--substandard-(contaminated)-syrup-medicines},
  note = {19 Jul 2023 (Cameroon; Naturcold). Accessed 25 Oct 2026}
}

@misc{thakur2025coldrifletter,
  author = {Thakur, Aksheev},
  title = {Cough Syrup Deaths: Drug Regulator Flags Lapses in Testing Raw Material},
  howpublished = {The Tribune (news)},
  year = {2025},
  month = oct,
  url = {https://www.tribuneindia.com/news/india/cough-syrup-deaths-drug-regulator-flags-lapses-in-testing-raw-material},
  note = {9 Oct 2025. Accessed 25 Oct 2026}
}

@misc{tribune2025sresanarrest,
  author = {{The Tribune}},
  title = {Owner of Pharma Firm behind Toxic Coldrif Cough Syrup Arrested in Chennai},
  howpublished = {The Tribune (news)},
  year = {2025},
  month = oct,
  url = {https://www.tribuneindia.com/news/india/owner-of-pharma-firm-behind-toxic-coldrif-cough-syrup-arrested-in-chennai/amp},
  note = {9 Oct 2025. Accessed 25 Oct 2026}
}

@misc{outlook2023coughsyrupexport,
  author = {{Outlook News Desk}},
  title = {Cough Syrups to Undergo Testing before Export from June 1},
  howpublished = {Outlook India (news)},
  year = {2023},
  month = may,
  url = {https://outlookindia.com/national/cough-syrups-to-undergo-testing-before-export-from-june-1-news-288654},
  note = {23 May 2023. Accessed 25 Oct 2026}
}

@misc{pib2025schedulem,
  author = {{Press Information Bureau, Ministry of Health and Family Welfare}},
  title = {Conditional Extension of Timeline to Small and Medium Pharmaceutical Manufacturers for Compliance with Revised Schedule {M} Notification},
  year = {2025},
  month = feb,
  url = {https://www.pib.gov.in/PressReleasePage.aspx?PRID=2102291},
  note = {Page returned HTTP 403 to automated fetch; content verified only via search snippet. Accessed 25 Oct 2026}
}

@misc{lexplosion2025schedulem,
  author = {{Lexplosion}},
  title = {Health Ministry Extends Schedule {M} Compliance Deadline for Small and Medium Manufacturers with Turnover below Rs 250 Crores to 31st December 2025},
  year = {2025},
  month = feb,
  url = {https://lexplosion.in/health-ministry-extends-schedule-m-compliance-deadline-for-small-and-medium-manufacturers-with-turnover-below-rs-250-crores-to-31st-december-2025/},
  note = {14 Feb 2025. Accessed 25 Oct 2026}
}

@misc{cdsco2023qrfaq,
  author = {{Central Drugs Standard Control Organisation}},
  title = {{FAQs} on Implementation of {GSR} 823({E}) Dated 17th November, 2022 with Respect to Bar Code or {QR} Code on Top 300 Brands},
  year = {2023},
  month = jul,
  url = {https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Final%20FAQs%20on%20QR%20code%2021.07.2023.pdf},
  note = {Dated 21 Jul 2023. Accessed 25 Oct 2026}
}

@misc{cdscospuriousguidance,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Guidance for Identification and Verification of Spurious Drugs},
  year = {n.d.},
  url = {https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/Guidance-for-Identification-and-Verification-of-Spurious-Drugs.pdf},
  note = {Undated; refers to rules effective 1 Aug 2023, so issued no earlier than 2023. Accessed 25 Oct 2026}
}

@misc{tmv2026patna,
  author = {{The Morning Voice}},
  title = {Delhi Police Bust Fake Drug Factory near Patna, Nine Arrested, Drugs Worth Rs 5 Crore Seized},
  howpublished = {The Morning Voice (news)},
  year = {2026},
  month = feb,
  url = {https://www.tmv.in/article/delhi-police-bust-fake-drug-factory-near-patna-nine-arrested-drugs-worth-5-crore-seized-date=2026-02-24},
  note = {24 Feb 2026. Accessed 25 Oct 2026}
}

@misc{etvbharat2026dehradun,
  author = {{ETV Bharat}},
  title = {Fake Medicines Worth over Rs 5 Crore Seized from Factory in Uttarakhand's Dehradun},
  howpublished = {ETV Bharat (news)},
  year = {2026},
  month = jul,
  url = {https://www.etvbharat.com/en/state/fake-medicines-worth-rs-5-7-crore-seized-from-dehradun-factory-enn26072302950},
  note = {23 Jul 2026. Accessed 25 Oct 2026}
}

@article{mcmanus2020systematic,
  author = {McManus, D. and Naughton, B. D.},
  title = {A Systematic Review of Substandard, Falsified, Unlicensed and Unregistered Medicine Sampling Studies: A Focus on Context, Prevalence, and Quality},
  journal = {BMJ Global Health},
  year = {2020},
  volume = {5},
  number = {8},
  pages = {e002393},
  doi = {10.1136/bmjgh-2020-002393}
}

@article{ozawa2022characterizing,
  author = {Ozawa, Sachiko and Chen, Hui-Han and Lee, Yi-Fang and Higgins, Colleen R. and Yemeke, Tatenda T.},
  title = {Characterizing Medicine Quality by Active Pharmaceutical Ingredient Levels: A Systematic Review and Meta-Analysis across Low- and Middle-Income Countries},
  journal = {American Journal of Tropical Medicine and Hygiene},
  year = {2022},
  volume = {106},
  number = {6},
  pages = {1778--1790},
  doi = {10.4269/ajtmh.21-1123}
}

@article{tabernero2023estimating,
  author = {Tabernero, P. and Newton, P. N.},
  title = {Estimating the Prevalence of Poor-Quality Anti-{TB} Medicines: A Neglected Risk for Global {TB} Control and Resistance},
  journal = {BMJ Global Health},
  year = {2023},
  volume = {8},
  number = {7},
  pages = {e012039},
  doi = {10.1136/bmjgh-2023-012039}
}

@article{rusatira2026nearly,
  author = {Rusatira, J. C. and Novoa, M. D. and Uwimana, J. B. and Persaud, C. and Pal, E. and Khan, A. and Michtalik, H. and Padayachee, N. and Lumpkin, M. and Preston, C. and Ahmed, S.},
  title = {Nearly One in Five Essential Medicines Fail Quality Standards in {Africa}: A Systematic Review and Meta-Analysis of {MNCH} Medicines and Antimalarials},
  journal = {PLOS Global Public Health},
  year = {2026},
  volume = {6},
  number = {9},
  pages = {e0006326},
  doi = {10.1371/journal.pgph.0006326},
  note = {Author given names given as initials, as listed in PubMed}
}

@article{pal2025assessing,
  author = {Pal, E. and Merchant, L. and Koffi, A. K. and Mehta, R. and Rusatira, J. C. and Kubiak, L. and Michtalik, H. J. and Caubel, P. and Ahmed, S.},
  title = {Assessing Knowledge, Attitudes, and Practices and Demand-Side Interventions for Combating Substandard and Falsified Medicines: A Scoping Review},
  journal = {Journal of Pharmaceutical Policy and Practice},
  year = {2025},
  volume = {18},
  number = {1},
  pages = {2550369},
  doi = {10.1080/20523211.2025.2550369}
}

@article{falah2025prevalence,
  author = {Falah, M. M. and Daar, E. and Zahra, D. and Dillon, M. J.},
  title = {Prevalence, Experience and Awareness of Substandard and Falsified Medicines among the Public and Healthcare Professionals in {Jordan}},
  journal = {BMJ Global Health},
  year = {2025},
  volume = {10},
  number = {5},
  pages = {e018189},
  doi = {10.1136/bmjgh-2024-018189}
}

@article{thakur2023substandard,
  author = {Thakur, N.},
  title = {Sub-standard or Sub-legal? Distribution, Pharma Dossiers, and Fake-talk in {India}},
  journal = {Medicine Anthropology Theory},
  year = {2023},
  volume = {10},
  number = {3},
  pages = {1--21},
  doi = {10.17157/mat.10.3.7279}
}

@article{fryze2025substandard,
  author = {Fryze, I. and Naughton, B. D.},
  title = {Substandard and Falsified Medicine Recalls in the Legitimate Supply Chain: A Systematic Review of Evidence},
  journal = {BMJ Open},
  year = {2025},
  volume = {15},
  number = {10},
  pages = {e103672},
  doi = {10.1136/bmjopen-2025-103672}
}

@misc{tnm2017nds,
  author = {{The News Minute}},
  title = {1,850 Drugs Sold in {India} Not of Standard Quality: Health Ministry},
  howpublished = {The News Minute (news)},
  year = {2017},
  month = feb,
  url = {https://www.thenewsminute.com/amp/story/news/1850-drugs-sold-india-not-standard-quality-health-ministry-57646},
  note = {23 Feb 2017; National Drug Survey 2014-16 headline figures (47,012 samples; 3.16\% NSQ; 0.0245\% spurious). Accessed 25 Oct 2026}
}

@misc{tribune2022gambia,
  author = {{The Tribune}},
  title = {Gambia Lawmakers Say India-based Drug Maker Maiden to Blame for Child Kidney Injury Deaths},
  howpublished = {The Tribune (news)},
  year = {2022},
  month = dec,
  url = {https://www.tribuneindia.com/news/nation/gambia-lawmakers-say-india-based-drug-maker-maiden-to-blame-for-child-kidney-injury-deaths-462921},
  note = {21 Dec 2022. Accessed 25 Oct 2026}
}

@misc{tribune2025coldriftoll,
  author = {{The Tribune (PTI)}},
  title = {{MP}: Coldrif Cough Syrup Fatality Count Reaches 24 after 2 More Children Die},
  howpublished = {The Tribune (news)},
  year = {2025},
  month = oct,
  url = {https://www.tribuneindia.com/news/madhya-pradesh/mp-coldrif-cough-syrup-fatality-count-reaches-24-after-2-more-children-die},
  note = {15 Oct 2025. Accessed 25 Oct 2026}
}
```

## Verification log

Verifier run 25 Oct 2026 (Crossref for DOIs; direct page/PDF fetch for web sources).

- who2017definitions: VERIFIED. Page open; definitions text and WHA70 (29 May 2017) adoption of "SF" term replacing SSFFC confirmed.
- who2024factsheet: VERIFIED. Dated 3 December 2024; "1 in 10", US$ 30.5 billion and substandard/falsified wording confirmed.
- who2017oneinten: VERIFIED. 10.5%, 88 LMICs, 48 000 samples, 178 high-income samples, 72 000-169 000 pneumonia deaths, 116 000 (64 000-158 000) malaria deaths, US$ 38.5m, 1500 reports, regional shares (42/21/21/8/6/2%), GSMS launched July 2013 all confirmed in release text.
- dcact1940s17b (D&C Act ss.16, 17, 17A, 17B, 27 on AdvocateKhoj): VERIFIED. All five pages open; clause text for 17B (a-e), 17A, 17, 16 (Second Schedule, 3 months' notice) matches. s.27 page shows the old text (5 yr-life, Rs 10,000 etc.) as the notes say. CourtBook annotation "Subs. by Act 68 of 1982, s.13 (w.e.f. 1-2-1983)" now opened and confirmed (the earlier "search snippet only" caveat no longer applies). Caveat: AdvocateKhoj is a private legal database, not India Code; cite the Act itself and use AdvocateKhoj only as access URL.
- goi2008dcamendment (Act 26 of 2008): VERIFIED. PDF text: assented 5 Dec 2008; s.27(a) not less than 10 years to life and fine not less than Rs 10 lakh or 3x value; s.27(b) 3-5 years, Rs 1 lakh or 3x; s.27(c) not less than 7 years to life, Rs 3 lakh or 3x; s.27(d) fine not less than Rs 20,000; new ss.32B, 36AB, 36AC (cognizable; bail conditions) and s.32 consumer-association amendment all present.
- cdsco2008nsqguidelines: VERIFIED. PDF open; Category A/B/C defects, "usually manufactured by unlicensed anti-social elements", assay below 70% for thermolabile products, clause 12 State rapid alert system all present. No date in document (year n.d. retained).
- khatun2017nds (notes key medicaldialogues2017nds; RENAMED, byline Ruby Khatun added): CORRECTED. Page confirms 3.16% NSQ in National Drug Survey 2014-16 and the Rajya Sabha written reply (7 Aug 2017). The page does NOT mention 224 molecules, NIB Noida or "seven central and three state laboratories"; 224 molecules and NIB are in tnm2017nds; "seven central and three state drug-testing laboratories" is [UNVERIFIED] (found in neither opened source).
- singhania2019nds: VERIFIED. 47012 samples, 17.8% from government sources, NSQ 10.02% and spurious 0.059% (estimated, government sources) confirmed; byline Meghna A Singhania, 25 Jun 2019. The sentence about States asked to sample NSQ batches was not re-checked.
- tnm2017nds: VERIFIED. 47,012 samples tested, 1,850 NSQ, 13 spurious, 3.16% and 0.0245% as ministry-stated percentages; same page also says 47,954 samples drawn from 654 districts (so the 942 gap is in the source) and 224 drug molecules in 15 therapeutic categories of NLEM 2011; NIB Noida. The researcher's note that raw counts do not reproduce the percentages is arithmetically correct (1,850/47,012 = 3.94%).
- cdsco2025nsqlink: VERIFIED. Scanned PDF read visually: CDSCO Enforcement and Intelligence cell notice dated 28 Aug 2025, signed Dr Rajeev Singh Raghuvanshi DCG(I), new link .../Notifications/nsq-drugs/ and "easily searchable" wording as quoted.
- cdsco2026latestalerts: VERIFIED. Page open (HTTP 200); lists "CDSCO NSQ Alert", "STATE NSQ ALERT" and "List of spurious Drugs" for June 2025 all dated 2025-Jul-18; May 2025 spurious list 2025-Jun-20; "Revise list drug alert May-2025" 2025-Jul-18; 21 Aug 2025 corrigendum item present (the Novo Nordisk theft alert was not individually checked).
- etvbharat2026july: VERIFIED. Published 21 Aug 2026; 40 central + 240 state NSQ and 1 spurious (Bihar, unauthorised entity using another company's brand); headline 280 vs components 281 mismatch is real in source; "batch-specific" wording and ">950 enforcement actions and 3,599 criminal prosecution cases over five years" confirmed.
- bohral2025nsqlink: VERIFIED. Corpseed page, byline Parul Bohral, dated 2025-09-01 (page metadata); commercial secondary source, superseded by cdsco2025nsqlink.
- cdsco2012recall: VERIFIED. PDF open: "Effective Date: 23/11/2012" and "VERSION: 2017" label as the notes say.
- cdsco2024recall: VERIFIED. PDF open: "Effective Date: 18/07/2024"; Class I 24-72 h, Class II up to 10 days, Class III up to 30 days confirmed. Class definitions, SOP and SMS/website passages not individually re-read.
- roy2025fiveyears (Medical Dialogues, Lok Sabha reply): VERIFIED. Table of samples tested / NSQ / spurious-adulterated for 2020-21 to 2024-25 matches the notes exactly; derived totals 14,342 NSQ and 1,593 spurious/adulterated are arithmetically correct; >960 premises, >860 actions, Rs 756 crore, 17 new and 24 upgraded labs confirmed; byline Susmita Roy, 18 Dec 2025. Minister is J. P. Nadda per the notes; the questioner name (Dr Mohammad Jawed) was not re-checked.
- who2022alert6: VERIFIED. N°6/2022, 5 Oct 2022; four products and Maiden Pharmaceuticals Limited (Haryana); DEG and EG; "reported to WHO in September 2022"; no guarantees from manufacturer; informal markets; no death count on page.
- who2025alert5: VERIFIED. N°5/2025, 13 Oct 2025; COLDRIF, Respifresh TR, ReLife; Sresan Pharmaceutical, Rednex Pharmaceuticals, Shape Pharma; 30 Sep 2025 WHO information; reported 8 Oct 2025; none exported per CDSCO. Batch numbers in annex not opened.
- who2023alert1: VERIFIED. N°1/2023, 11 Jan 2023; AMBRONOL and DOK-1 Max, Marion Biotech Pvt Ltd (Uttar Pradesh); Uzbekistan reported 22 Dec 2022, Cambodia reported 3 Apr 2023; no guarantees; informal markets.
- who2023alert5: VERIFIED. N°5/2023, 19 Jul 2023; NATURCOLD, DEG up to 28.6% vs limit 0.10%; FRAKEN INTERNATIONAL (England), MHRA says no such manufacturer; reported 13 Mar 2023; no Indian manufacturer named.
- thakur2025coldrifletter: VERIFIED. Aksheev Thakur, Tribune News Service, 9 Oct 2025; CDSCO letter of 7 Oct to all states; "not testing each batch of excipients..." quote confirmed; "20 children" as stated in the article.
- tribune2025sresanarrest (byline corrected to Tribune Web Desk): CORRECTED (author field only). Content confirmed: Ranganathan Govindan arrested in Chennai by MP police, 46-48% DEG, culpable homicide not amounting to murder, at least nine states, at least 20 deaths; dated 9 Oct 2025.
- outlook2023coughsyrupexport: VERIFIED. 23 May 2023; CoA before export from 1 June; lab list as stated; "66 and 18 children in Gambia and Uzbekistan, respectively" described as "allegedly linked". The DGFT notification itself is not opened (remains a gap).
- pib2025schedulem: CORRECTED. The notes say the page returned HTTP 403; it opened for this verifier. PIB release posted 12 Feb 2025 (Ministry of Health and Family Welfare); revised Schedule M notified 28 Dec 2023; 6 months for turnover above Rs 250 crore, 12 months for Rs 250 crore or less; extension to 31 Dec 2025 conditional on Form A application within 3 months from 11 Feb 2025. The page text does NOT give "G.S.R. 922(E)"; that number stays [UNVERIFIED].
- lexplosion2025schedulem: VERIFIED. Page open; 31 Dec 2025 extension and Form A deadline "11th May" confirmed (secondary reproduction of the MoHFW release).
- cdsco2023qrfaq: VERIFIED (date caveat). PDF text confirms G.S.R. 823(E) of 17 Nov 2022, particulars list, Schedule H2 top 300 brands, in force 1 Aug 2023, batches made on or after that date, secondary label if space is short, UPIC set by manufacturer's SOP, voluntary for other brands. The PDF has no printed date; "21 Jul 2023" comes from the file name only.
- cdscospuriousguidance: VERIFIED. PDF text matches: s.17B restated, G.S.R. 20(E) of 18.01.2022 (API QR, effective 01.01.2023), G.S.R. 823(E), three-step scan process flow. Undated.
- akshitha2026patna (notes key tmv2026patna; RENAMED, byline Yekkirala Akshitha added): VERIFIED. 24 Feb 2026; 1.19 lakh spurious zinc tablets, 42,000 fake azithromycin, 27 kg paracetamol powder, 13 kg tramadol powder valued over Rs 5 crore, 500 g alprazolam; nine arrested; "third such bust in Bihar within days"; investigation began with an NDPS Act FIR at Crime Branch, New Delhi.
- etvbharat2026dehradun: VERIFIED. 23 Jul 2026; named companies list (Cipla through Zydus) matches. The "Rs 5-7 crore" figure is in the URL slug and headline per notes; joint UP FSDA / Ghaziabad Crime Branch not re-read in full.
- ozawa2018prevalence: VERIFIED via Crossref and PubMed 30646106. Authors, JAMA Netw Open 1(4):e181662, 10 Aug 2018. Abstract confirms 265 studies, 96 studies / 67,839 samples, 13.6% (11.0-16.3), Africa 18.7%, Asia 13.7%, antimalarials 19.1%, antibiotics 12.4%, eight economic estimates $10-200 billion. Not confirmable from the abstract: "median US$31.25 billion" and "400,647 samples"; check full text before citing those two numbers.
- mcmanus2020systematic: VERIFIED via Crossref and PubMed 32859648. Authors given as Dominic McManus and Bernard David Naughton; 33 studies, median 25% (7.7-34%) vs 28.5% in 2013; "definitive conclusions ... cannot be drawn" confirmed.
- ozawa2022characterizing: VERIFIED via Crossref and PubMed 35895431. 130 studies, 95,520 samples, 12.4% (10.2-14.6), 25.9% of failed <80% API, 13.8% <50% API, 12.5% 0% API, six of seven likely substandard. Not confirmable from abstract: Asia 23.4% vs Africa 11.4% for <50% API. Also note abstract says 1.8% of all samples had <50% API.
- tabernero2023estimating: VERIFIED via Crossref and PubMed 37433693. 65 publications, 7,682 samples, 22 countries, 15.2% failed at least one test, 14.1% in quality surveys. The abstract itself says data are "not generalisable" to the global TB supply; do not cite 15.2% as global prevalence. The notes' "calls for portable screening devices" is not visible in the abstract text retrieved (may be in full text).
- rusatira2026nearly: VERIFIED via Crossref and PubMed 42685013. Published 2 Sep 2026; 123 studies, 34 countries, 36,069 samples, 17.9% (13.6-22.7), substandard 12.8%, falsified 1.2%, corticosteroids 65.0%, uterotonics 43.9%, hematinics 34.7%, mystery-client predictor confirmed. Full given names added.
- pal2025assessing: VERIFIED via Crossref and PubMed 40958951. 78 studies, quotes on "grossly lacking" empirical data, low knowledge, deficiency of consumer-focused interventions, digital health interventions confirmed; 12 Sep 2025.
- falah2025prevalence: VERIFIED via Crossref and PubMed 40412817. 209 public, 136 professionals, Jan-Jun 2023, 24%/35% familiar, 8%/25% correctly identified, 17%/26% experience, 81% of public did not report. Full given names added; Crossref title is wrapped in stray quote characters (publisher metadata artefact).
- thakur2023substandard: CORRECTED. Author is Nishpriha Thakur (notes had initial only); journal name is "Medicine Anthropology Theory" (notes text abbreviated it as "Med Anthropol Theory"; bib already correct); published 27 Sep 2023; claim about paperwork vs chemical composition confirmed from abstract.
- fryze2025substandard: VERIFIED via Crossref and PubMed 41145244. 13 papers, 23 countries, 2010-2024, quote that India was a common source of SF medicines in Zambia, Sri Lanka, Brazil and Nepal confirmed; Crossref issued date Oct 2025 (notes say 27 Oct 2025; day not checked).
- reuters2022gambia (notes key tribune2022gambia; RENAMED, Reuters credit): VERIFIED. Dakar, 20 Dec 2022, page updated 21 Dec 2022; "at least 70" children in text, embedded tweet says "at least 66"; Goyal did not respond; production licence suspended. The notes' remark that India told WHO tested samples met specification was not re-read.
- tribune2025coldriftoll: VERIFIED. PTI, 15 Oct 2025, toll 24 children mostly under five, Additional Collector Dhirendra Singh. The Rajasthan sentence was not found by grep (not re-read in full).
- pti2025feb / pti2025apr (The Week, PTI, notes listed without keys): VERIFIED via WebFetch (direct fetch gave Access Denied). Feb 2025: 47 central + 56 state NSQ (report 28 Mar 2025); Apr 2025: 60 central + 136 state, 1 spurious Bihar (20 May 2025).
- dinamalar2025sep: VERIFIED. 52 central, 60 state, 1 spurious from Chhattisgarh (unauthorised manufacturer using another company's brand); "displayed monthly" wording confirmed.
- ians2025oct: VERIFIED. 211 = 63 central + 148 state; spurious 3 Bihar + 2 Delhi; 21 Nov 2025.
- ians2025nov: VERIFIED. 205 = 64 central + 141 state; 2 spurious from North Zone Ghaziabad; 19 Dec 2025 (URL date; page not re-read for the day).
- dtnext2025dec and Deccan Herald/PTI December item: VERIFIED. 167 = 74 central + 93 state (DT Next text); spurious 4 North Zone Ghaziabad + 1 each FDA Ahmedabad, Bihar, Maharashtra (Deccan Herald, 22 Jan 2026); "monthly basis" wording in DT Next.
- scroll2025coldrif: VERIFIED. Coldrif 48.6%, ReLife 0.616%, Respifresh TR 1.34% DEG (limit 0.1%); headline says 22 children. Notes quote ReLife as 0.61%; source says 0.616%.
- banerji2023marion (Down To Earth): VERIFIED for 18 child deaths in Uzbekistan and the Marion Biotech alert (12 Jan 2023, Nandita Banerji). The notes' claim that "Indian authorities suspended Marion Biotech's licence and stopped production" was NOT found in this page: [UNVERIFIED] as attributed to Down To Earth.
- healthpolicywatch2023naturcold: VERIFIED in part. Page says Reimann Labs "allegedly" made Naturcold and was ordered to shut down by Indian regulators. The notes' "Indore" and "six child deaths" details were NOT found on the page: [UNVERIFIED]. The page also states WHO reported at least 66 children died in The Gambia.
- Tribune, "WHO issues alert over 3 adulterated cough syrups" (tribuneindia.com/news/world/...): UNVERIFIED for the notes' specifics. Page opens but the DEG percentages and the death toll were not found in it; not added to bib. DEG figures are covered by scroll2025coldrif.
- Deccan Herald, "3,104 drugs found to be NSQ between April 24 and March 25" (22 Jul 2025): CORRECTED claim. Page confirms 3,104 NSQ in 2024-25 but states 604 prosecutions were launched in 2024-25; the notes' "663 (2022-23), 604 (2023-24), 961 (2024-25)" attribution conflicts with this. Prosecution-by-year figures are [UNVERIFIED]; not added to bib. Rajya Sabha PQ 266 of 17 Dec 2024 (rsdebate.nic.in): UNVERIFIED (file fetched is damaged/unreadable). Indiamedtoday 96,173 typo claim: not checked, and roy2025fiveyears confirms 96,713.
- WION Coldrif article (wionews.com): UNVERIFIED. HTTP 403 to automated fetch; the 3 Oct 2025 advisory and propylene-glycol claims stay [UNVERIFIED].
- IndiaSpend (indiaspend.com/n-838516) and Medical Dialogues "1 in 7 Indian drugs" (2016): UNVERIFIED for the 12% Delhi / 5% Chennai / 7% / diclofenac 15.62% / amoxicillin 13.04% / 0.04%-34% claims. Both pages open; the Medical Dialogues piece (16 Feb 2016) says substandard medicines "could be three times more prevalent than the government says, two new studies show" but the specific percentages were not found; IndiaSpend text mentions "11 of the remaining 24,136 drugs (0.04" in a different context. Not added to bib; primary papers still needed.
- IMSEAR record (Bangalore pharmacist survey, 50.81%) and SecuringIndustry (92% of pharmacists): UNVERIFIED. Both hosts unreachable (connection failure) from this environment; the claims stay [UNVERIFIED].
- zelthy blog on G.S.R. 506(E) / Schedule H2 expansion: UNVERIFIED as law. Page opens (published 21 Jul 2026, updated 11 Sep 2026, vendor blog) and says G.S.R. 506(E) of 22 Jun 2026, compliance 1 Jul 2027, antimicrobials 1 Jul 2028, consistent with the notes, but it is a single commercial source; Gazette not checked, so the claim remains [UNVERIFIED]. Not added to bib.
- Not checkable from any opened source (claims remain [UNVERIFIED]): Jan Vishwas (Amendment of Provisions) Act 2023 scope and s.27(d) compounding; DGFT notification number and text; G.S.R. 922(E) number for Schedule M; Rajya Sabha reply of 7 Feb 2023 (PQ 259) retail figures 3% NSQ / 0.023% spurious; Coldrif final death count and legal outcomes; PIB/Schedule M vendor-dashboard claims of 7 Nov 2025.
- who2017definitions, who2024factsheet, who2017oneinten: see the three lines above (all VERIFIED).

Verification: COMPLETE

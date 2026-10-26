Status: COMPLETE

Checklist:
- [x] Q1 Recall effectiveness and consumer awareness (FDA process, effectiveness checks, valsartan 2018, ranitidine 2019-2020)
- [x] Q2 Notification channels (pharmacy, SMS, apps, EHR) and analogues (NHTSA VIN lookup, food recall apps)
- [x] Q3 India: CDSCO 2012 recall guidelines, NSQ alert reach, PvPI, WHO alerts/GSMS, Telangana DCA SMS alerts
- [x] Q4 openFDA recall data as precedent; medication-management apps and engagement evidence
- [x] Q5 Lag between manufacture, sampling, result, alert; share of batch sold/consumed before alert

# Drug recall and quality-alert monitoring (notes for StripCheck "medicine cabinet" and data-freshness statement)

Conventions. All pages and APIs accessed 25-26 Oct 2026. "Abstract only" means the full text was not opened (abstract read via the Europe PMC REST API). BibTeX keys are given in square brackets and listed in the BibTeX section. Items marked NEWS are news reports, used only for recent events. Where a figure could not be verified it says UNVERIFIED and should not be cited. This file was finished after an interrupted run; earlier findings were kept and condensed to fit the length limit.

## Q1 Recall effectiveness and consumer awareness

### Takeaway
Regulators audit recalls at the trade level (consignees), not at the level of the patient who holds the product, and the few patient-facing studies (2021-2026) show poor understanding of recalls and an unsolved last-mile problem: EHR and pharmacy systems do not know which lot a patient holds. The valsartan/ranitidine literature shows that recalls change behaviour and sometimes cause harm through disruption, which argues for precise batch-level messaging.

### Cited Findings
- FDA recall strategy and effectiveness checks: 21 CFR 7.42 lists as strategy factors how easy the product is to identify, how obvious the defect is to consumers, and "Degree to which the product remains unused in the market-place" (as printed). Recall depth is consumer, retail or wholesale level. Effectiveness checks (levels A 100% of consignees, B more than 10% and less than 100%, C 10%, D 2%, E none) verify that consignees (firms) were notified and acted, by visits, calls or letters. Public warning is reserved for serious hazards when other means seem inadequate. Text version dated 1 Oct 2026. — [eCFR 21 CFR 7.42](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-7/subpart-C/section-7.42) [fda2026cfr742]. Relevance: primary basis for saying recall effectiveness is audited per consignee, not per patient; supports StripCheck's patient-side re-check as filling an unmeasured stage.
- Closest published analogue of the medicine cabinet: Gadgil et al. built a nightly job at a large urban academic medical centre that polled the FDA recall API, matched new recalls to patients' EHR medication lists and sent a patient-portal message; 9 patients gave qualitative feedback (convenience sample). It worked technically, but the EHR prescription cannot be traced to the lot a community pharmacy dispensed, so the authors conclude automated recall notification cannot be deployed clinically without a prescription-to-dispensed-lot audit trail (JMIRx Med 2026, abstract only). — [doi:10.2196/68345](https://doi.org/10.2196/68345) [gadgil2026automating]. Relevance: names the exact gap StripCheck fills: the patient's own strip supplies the lot/batch number; nightly re-check against a machine-readable feed is the same architecture.
- Dutch focus groups of patients who had experienced a recall: little knowledge of recall procedures, recalls confused with shortages, difficulty judging risk, unclear communication, some reduced trust or use of the medicine; preference for pharmacist-led, personalised communication proportionate to urgency (Int J Clin Pharm 2026, abstract only; qualitative, no prevalence). — [doi:10.1007/s11096-025-02082-z](https://doi.org/10.1007/s11096-025-02082-z) [annema2026patient]. Relevance: supports plain-language verdicts that separate "this batch is listed" from "shortage", and advice to consult the pharmacist/prescriber rather than stop treatment.
- Valsartan 2018, Ontario: among 55,461 patients on recalled generic valsartan, 73.8% moved to another ARB and 8.8% to non-recalled valsartan within a month [UNVERIFIED: search summary only]; 10.7% had not filled an alternative at 3 months [UNVERIFIED]; hypertension ED visits rose in the first month from 0.11% to 0.17% (+55%, p = 0.02). NUMBERS FROM THE ACC conference-coverage article (NEWS-type secondary report of the AHA 2019 presentation); the Circulation research letter itself (141(5):411-413) shows no abstract in Europe PMC and was not opened. — [ACC coverage, 14 Nov 2019](https://www.acc.org/latest-in-cardiology/articles/2019/11/14/13/36/sat-715am-population-impact-generic-valsartan-recall-aha-2019); letter: [doi:10.1161/circulationaha.119.044494](https://doi.org/10.1161/circulationaha.119.044494) [jackevicius2020valsartan]. Relevance: a recall of a chronic medicine moves large populations fast and a tail is left without therapy; wording must not induce abrupt stopping.
- Valsartan 2018, US claims data: in 87,130 adherent heart-failure patients no difference in 6-month hospitalisation/ED/urgent care (HR 1.00, 95% CI 0.96-1.03) (Pharmacoepidemiol Drug Saf 2024, abstract only) — [doi:10.1002/pds.5777](https://doi.org/10.1002/pds.5777) [devine2024valsartan]; in 76,934 valsartan vs 509,472 non-recalled ARB/ACE-I hypertension patients the valsartan group had higher risk of all-cause hospital/ED/urgent care (HR 1.02) and composite cardiac events (HR 1.22), linked by the authors to recall-related shortages (J Am Heart Assoc 2024;13(1):e032266, abstract summary only) — [doi:10.1161/JAHA.123.032266](https://doi.org/10.1161/JAHA.123.032266) [devine2024arb]. Relevance: harm, where it appears, is attributed to disruption and shortage, not to continued use; supports exact-batch matching over blanket warnings (inference).
- Mailed recall letters: 300 US veterans who received recalled valsartan and were mailed a recall letter on 12 Mar 2019 showed no change in systolic BP (137.2 to 135.8 mmHg, p = 0.125) or control (28% to 27%); 33 valsartan medication changes, of which 11 were documented as recall-related (Ther Adv Drug Saf 2021, abstract only; single centre, no control group). — [doi:10.1177/20420986211016173](https://doi.org/10.1177/20420986211016173) [morizio2021veterans]. Relevance: an example of pharmacy-level patient notification done by post; only a minority of changes were attributable to the letter, so even direct notification yields partial response.
- Canadian national dispensing 2015-2019: valsartan dispensing fell 57.8% (362,231 prescriptions in June 2018 to 152,892 in September 2018) while non-valsartan ARBs rose 14.6% (CMAJ Open 2021, abstract only). — [doi:10.9778/cmajo.20200232](https://doi.org/10.9778/cmajo.20200232) [fenna2021valsartan]. Relevance: supply-side (pharmacy) action changes dispensing quickly; says nothing about patient awareness.
- Ranitidine: Korean interrupted time series after the ranitidine withdrawal (HIRA data Jan 2016-May 2023): immediate drop in H2RA use (about 1,041.7 DDD per 100,000 inhabitants) and jump in PPI use (about 235.2), then rising trends (J Prev Med Public Health 2025;58(1):21-30, abstract summary) — [doi:10.3961/jpmph.24.357](https://doi.org/10.3961/jpmph.24.357) [choi2025ranitidine]. Indian professionals: a questionnaire of 198 physicians and 113 pharmacists around Chennai on the FDA ranitidine recall (Future J Pharm Sci 2021) — [doi:10.1186/s43094-021-00267-7](https://doi.org/10.1186/s43094-021-00267-7) [begam2021ranitidine]; full text NOT opened and a secondhand awareness figure (74%) is UNVERIFIED, do not cite numbers.
- Systematic review of 13 papers on substandard/falsified (SF) recalls from regulators in 23 countries: substandard recalled significantly more than falsified; main causes contamination, out-of-specification, stability and packaging; India named as a common source in Zambia, Sri Lanka, Brazil, Nepal; nitrosamine recalls in all regions in 2018; recall notification data not harmonised (BMJ Open 2025, abstract only). — [doi:10.1136/bmjopen-2025-103672](https://doi.org/10.1136/bmjopen-2025-103672) [fryze2025substandard]. Relevance: supports ingesting heterogeneous regulator tables into one validated schema.
- Caution on regulator data quality (FOOD, not drugs): an HHS OIG audit of 30 voluntary food recalls (of 1,557 reported 1 Oct 2012-4 May 2015) found weaknesses in initiation, monitoring and the Recall Enterprise System data (report A-01-16-01502, 22 Dec 2017). — [OIG](https://oig.hhs.gov/oas/reports/region1/11601502.asp) [hhsoig2017foodrecall]. Relevance: analogy only; regulator recall datasets have documented quality problems.

### Inferences
- Consumers learn of recalls mostly through intermediaries (pharmacy, prescriber); any tool that gives the patient a self-service, batch-level check removes the dependence on those intermediaries.
- Because the response to recalls includes avoidable harm from disruption, a verdict of FLAGGED should carry action-proportionate language (contact pharmacist/prescriber; do not stop a chronic medicine abruptly).

### Gaps
- No peer-reviewed measurement found of the share of patients who learn of or act on a consumer-level drug recall.
- No FDA drug effectiveness-check results (audit-check outcomes) were located.
- The Jackevicius Circulation letter and the Begam ranitidine paper were not read in full.

## Q2 Notification channels and analogues

### Takeaway
Even with legally mandated mail notification and a free VIN lookup, about a third of recalled US vehicles were still unrepaired 15 months after a remedy became available; repeated multichannel outreach worked better than a single notice, and the VIN lookup regime carries an explicit minimum refresh interval and visible "last updated" date. Drug recall channels are pharmacy-level or postal; patient-facing push is rare and technically blocked by missing lot data.

### Cited Findings
- GAO-24-106356 (Jan 2024): owners are notified by First-Class Mail by law; NHTSA reported in 2021 that 69% of passenger vehicles recalled in 2018 were remedied 15 months after a remedy became available (report footnote 4); Takata manufacturers reached almost 80% with at least monthly outreach by certified mail, postcards, email, phone and social media in several languages; barriers: owner awareness, perceived risk, convenience, parts, vehicle age and stale registration contact data; NHTSA's 2019 focus groups had 5 groups and 189 participants; GAO-18-127 found owners prefer at least one electronic notification in addition to mail. — [GAO-24-106356](https://www.gao.gov/products/gao-24-106356) [gao2024vehicle]. Relevance (vehicle analogy): supports repeated re-checking and push channels; the VIN registry ties a unit to an owner, which medicines lack; StripCheck's saved batches are a voluntary, owner-held equivalent.
- NHTSA VIN lookup: manufacturers with at least 25,000 light vehicles (or 5,000 motorcycles) per year must provide a VIN-searchable recall lookup, "updated at least once every seven (7) calendar days", with the date of the last update shown on the search and results pages; recall completion data cover campaigns of the previous fifteen calendar years at minimum (text from the eCFR API for 49 CFR 573.15 version 1 Oct 2026, read 26 Oct 2026). Introduced by the 2013 rule (Federal Register 2013-19785, 20 Aug 2013; abstract seen only). — [eCFR 49 CFR 573.15](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-573/section-573.15) [ecfr2026vin]. Relevance: a regulator-mandated refresh floor and a visible "last updated" stamp are the direct precedent for StripCheck's explicit statement of data freshness.
- Pharmacy and EHR channels: see Gadgil 2026 (EHR/portal push, blocked by lot traceability) and Morizio 2021 (postal letters from a pharmacy/health system) in Q1. The Dutch study recommends pharmacist-led personalised communication [annema2026patient].
- Indian pharmacy-level push: Telangana DCA bulk SMS (NEWS, Medical Dialogues, 11 Mar 2026) and Karnataka's portal (NEWS, Medical Dialogues/PTI, 17 May 2026) are described in Q3; both reach trade, not patients.
- Rwanda FDA "Safety alerts" web page (Feb 2019-Feb 2023): Class I = 33.0% of recalls, antibiotics 35.8%, contamination 26.4%, India the top manufacturing country (29.2%) (BMC Public Health 2024, abstract only). — [doi:10.1186/s12889-024-19245-8](https://doi.org/10.1186/s12889-024-19245-8) [bahizi2024rwanda]. Relevance: a regulator web page is the de facto public alert channel in many LMICs, so a scraper/ingest layer is realistic.

### Inferences
- Push channels matter more than a pull website: StripCheck's cabinet turns a pull-only government list into a push notification for the one person who holds the batch.
- Food recall apps were not studied here (see Gaps); the vehicle case is the documented analogue.

### Gaps
- No peer-reviewed evaluation of SMS or app-based consumer drug-recall alerts was found; no food-recall-app evaluation was opened. The 2013 NHTSA rule full text was not opened.

## Q3 India: CDSCO recall system, NSQ alert reach, PvPI, WHO alerts, state portals

### Takeaway
India's recall guideline is manufacturer- and trade-centred: consumer-level recall with public announcement exists only for Class I, and a patient holding a Class II/III NSQ batch is by design outside the notification perimeter. Newer state systems (Telangana SMS, Karnataka portal) push to pharmacies and stockists, not patients; no effectiveness data exist for any of them.

### Cited Findings
- CDSCO "Guidelines on Recall and Rapid Alert System for Drugs", effective 23 Nov 2012 (CDSCO-hosted copy labelled Version 2017, bundled with SOP QA-GNL-021, 1 Aug 2015). Section 2 says an effective uniform recall procedure is required and that "at present auditing and accountability is not in place" (paraphrase). NSQ drugs are subject to statutory recall; Classes I/II/III follow the DCC categories A/B/C. Consumer-level recall with print/electronic public announcement only for Class I. Timelines: Class I decision within 24 h (max 72 h), stop sale 24 h, recall complete 72 h; Class II up to 10 days; Class III up to 30 days; recall communication to the chain within 24 h by fastest mode (email, phone, fax, SMS). SOP clauses 5.4-5.7: the State Licensing Authority informs the public for Class I via mass media and the web portal; Drugs Inspectors assess effectiveness. The Recall Log records batch, mfg/exp dates, quantity produced, distributed, unsold and returned. Notice templates carry product, batch, mfg date, expiry and manufacturer, the fields StripCheck extracts. — [CDSCO PDF](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/4GuidelineRecalRapidAlert.pdf) [cdsco2012recall]. Relevance: defines the NSQ recall regime and the structural gap the cabinet fills.
- Current version: "VERSION: 2024", Doc. CDSCO/RRAS Ver. 00, effective 18 Jul 2024, 25 pages; classes, levels and timelines unchanged; SOP QMS-GNL-010 clause 5.4: for Class I "it is preferred that information's are given by SMS or through website to the public and the regulatory mechanism shall try to reach that level" (wording as printed). — [CDSCO PDF 2024](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/Guidelinerapid24.pdf) [cdsco2024recall]. Relevance: public SMS/web is an aspiration for Class I only, with no mechanism or metric.
- NEWS, Medical Dialogues, 7 Oct 2019 (updated 16 Aug 2021): the DCC set up a sub-committee on NSQ recall; short-term steps (state nodal officers, WhatsApp groups), medium-term (drug-control websites for NSQ reports, a mobile app), long-term (portal linking regulators, labs and supply chain). Whether the app/portal was built is NOT established. — [Medical Dialogues](https://business.medicaldialogues.in/cdsco-committee-to-draft-new-guidelines-for-effective-recall-of-substandard-drugs) [medicaldialogues2019cdscorecall].
- NEWS, Daily Pioneer/PTI, 22 Sep 2026: CDSCO's August 2026 alert lists 220 NSQ samples (29 Central Drugs Laboratories, 191 State Drug Testing Laboratories) and 1 spurious sample (Delhi); published about three weeks after month end; officials state the failure applies only to the batch tested. — [Daily Pioneer](https://dailypioneer.com/news/220-drug-samples-fail-quality-tests-august) [pioneer2026august]. Relevance: dated publication-lag datum and the official batch-specific framing that verdict wording should mirror.
- NEWS, Medical Dialogues, 25 Sep 2026 (Susmita Roy): in the August 2026 state-lab table each row gives product, batch, manufacturing date, expiry, manufacturer, failure result, reporting lab/state and reporting month-year (AUG-2026), without test dates; failure types include assay, dissolution, identification, sterility and endotoxin; four entries described as spurious; one azithromycin 500 mg batch manufactured Oct-2024, expiring Sep-2026, listed AUG-2026; one rosuvastatin row shows expiry (Jun-2025) before manufacture (Jul-2025), an inconsistent published record. — [Medical Dialogues](https://medicaldialogues.in/news/industry/pharma/cdsco/state-drug-alert-azithromycin-cefixime-among-191-drug-samples-flagged-by-cdsco-for-quality-failures-in-august-180004) [medicaldialogues2026august]. Relevance: fields available for corroboration; evidence that source tables contain errors (motivates validation and quarantine); the list gives only a reporting month, justifying "list as of month" wording.
- NEWS, Medical Dialogues, 11 Mar 2026 (Parthika Patel): Telangana Drugs Control Administration launched a bulk SMS system that notifies retail pharmacies and wholesalers when the Drugs Control Laboratory, Hyderabad, declares a sample NSQ, instructing them to stop sale and withdraw stock; no recipient counts, response times or effectiveness data; the claim that few states have such a platform (attributed to The Hindu) is unverified. — [Medical Dialogues](https://medicaldialogues.in/news/industry/pharma/telangana-dca-introduces-sms-alert-system-to-warn-pharmacies-about-substandard-medicines-166301) [medicaldialogues2026telangana]. Relevance: 2026 precedent of push alerts to the pharmacy level only; issued per lab result and earlier than CDSCO's monthly lists, hence StripCheck must state the list month.
- NEWS, Medical Dialogues/PTI, 17 May 2026 (Susmita Roy): Karnataka's Food Safety and Drug Administration department built a real-time portal; officials upload a declared-NSQ batch, the portal is linked to wholesaler/stockist databases, messages go to them and to retailers, and stock is frozen automatically; about 15,000 stockists/wholesalers now on the system, about 45,000 retailers/pharmacists planned next; medicines worth Rs 1.85 crore were recalled in 2025-26; the minister said that under the earlier process substandard medicines could still reach the public; no statement on notifying patients. A reported reduction of the withdrawal timeline from 30 to 3 days appeared only in a search summary and is UNVERIFIED. — [Medical Dialogues](https://medicaldialogues.in/news/industry/pharma/karnataka-launches-real-time-portal-to-freeze-nsq-drugs-track-ndps-medicine-sales-170872) [medicaldialogues2026karnataka]. Relevance: a second state-level, trade-side system; reinforces that the consumer end is uncovered.
- PvPI: the National Coordination Centre (Indian Pharmacopoeia Commission) receives almost 100,000 ADR case reports a year through 250 ADR Monitoring Centres, collated 250,787 reports Jul 2011-Jun 2017 and issued 56 drug safety alerts between Mar 2016 and Jun 2017; these alerts concern unlisted adverse reactions to be reported by health professionals, not batch quality (Perspect Clin Res 2018;9(1):51-55, abstract). — [doi:10.4103/picr.picr_29_17](https://doi.org/10.4103/picr.picr_29_17) [thota2018pvpi]. Relevance: PvPI is a separate channel (ADR signals, aimed at professionals); it does not supply batch-level NSQ data, so it is out of scope for StripCheck's matching. The IPC alerts page returned HTTP 500 in both attempts; current alert counts are not verified.
- WHO GSMS (launched 2013): trained focal points in national regulators submit rapid alert forms; WHO contacts the focal point within 72 h (24 h if adverse reactions); a public Medical Product Alert is considered for significant public-health threat, wide geographic risk, or when steps to inform health professionals/consumers have not been taken; the pages give no alert counts or report-to-alert times (WHO pages read 25 Oct 2026; per-page dates absent). WHO's activity report covering Aug 2017-Dec 2021 records 877 incidents with an average annual increase of 36.3% (from a search-result snippet; report not opened). — [WHO GSMS](https://www.who.int/who-global-surveillance-and-monitoring-system) [who2026gsms]. Relevance: alerts are rare and aimed at regulators and professionals; a stated limitation is that StripCheck does not cover WHO alerts.
- Lancet Regional Health Southeast Asia editorial (Dec 2025): in Oct 2025 WHO issued an alert for three substandard oral liquid medicines made in India (DEG/EG contamination linked to the deaths of 20 children); since 2022 WHO has issued seven alerts on contaminated liquid oral medicines, almost all made in India, linked to over 300 deaths; calls for transparency and "a robust drug recall mechanism"; gives no NSQ counts. — [doi:10.1016/j.lansea.2025.100705](https://doi.org/10.1016/j.lansea.2025.100705) [lancet2025tiny]. Relevance: recent framing of weak enforcement and recall mechanisms in India (motivation, not method).

### Inferences
- Alert reach in India ends at the trade for Class II/III and, with state SMS/portal systems, for Class I too; no document found measures patient reach.
- Three timestamps coexist (state SMS, CDSCO monthly list, WHO alert), none machine-linked to the patient's pack; the cabinet should record the ingest date of each list and show it.

### Gaps
- No evaluation of Telangana's SMS or Karnataka's portal; no PvPI quality-alert source; the WHO and PvPI pages lack counts; CDSCO's "dedicated link for NSQ alerts" (reported 1 Sep 2025 by a low-quality commercial site, no original source) is UNVERIFIED. No evidence found on the proportion of Indian consumers who see NSQ lists.

## Q4 openFDA recall data and medication-management apps

### Takeaway
openFDA is the machine-readable precedent for CDSCO's SUGAM JSON, and its own disclaimers (weekly refresh, not for public alerts, recalls can be expanded to more lots) map directly onto StripCheck's freshness statement. Medication apps focus on adherence, lose many users, and are not documented to check recall data, so a passive, photograph-once cabinet is both novel and engagement-realistic.

### Cited Findings
- openFDA Drug Enforcement API: data from FDA's Recall Enterprise System, 2004 to present, updated weekly; disclaimers: do not use for public alerts or to track a recall's lifecycle, status is not updated after classification, recalls may be corrected later (e.g. expanded to more lots), do not rely on it for medical decisions; fields include recall_initiation_date, report_date, classification, status, code_info, distribution_pattern, product_quantity (field descriptions not shown, so lot content of code_info not confirmed). — [openFDA](https://open.fda.gov/apis/drug/enforcement/) [openfda2026enforcement]. Relevance: explicit weekly refresh and "not a basis for medical decisions" wording StripCheck can emulate; recall expansion justifies re-checking saved batches.
- FDA enforcement data are widely mined: 13,248 drug recalls 2015-2024 (class associated with cause, Cramer's V 0.550; no exposure denominators) (Ther Innov Regul Sci 2026, abstract) — [doi:10.1007/s43441-026-01016-9](https://doi.org/10.1007/s43441-026-01016-9) [bekele2026recallclass]; seven opioids 2002-2025: 286 recalls, more than 350 million units, unit counts missing for 34 events (11.9%), no production denominators (Pharmacoepidemiol Drug Saf 2026;35(3):e70341, abstract) — [doi:10.1002/pds.70341](https://doi.org/10.1002/pds.70341) [nunes2026opioid]; nitrosamine recalls Jul 2018-Mar 2025, ARBs and metformin most recalled (Ther Innov Regul Sci 2026;60(2):519-533, abstract) — [doi:10.1007/s43441-025-00891-y](https://doi.org/10.1007/s43441-025-00891-y) [yerram2026nitrosamine]. Relevance: recall lists keep growing for years and public data lack distribution/consumption figures; StripCheck should say what the lists do not contain.
- Medicine Quality Monitoring Globe (open web system for substandard/falsified news in five languages): 11,000 distinct incidents Jul 2018-Dec 2024; English classifier precision 37%, recall 90%, F1 52%, so curators review before publication (PLOS Digit Health 2026;5(9):e0001648, abstract). — [doi:10.1371/journal.pdig.0001648](https://doi.org/10.1371/journal.pdig.0001648) [freifeld2026globe]. Relevance: monitoring precedent coupling automated filtering with human curation because automated precision is low; parallels LLM-assisted ingest with quarantine.
- Free adherence apps: 80 screened, 9 included; tracking history the most common output (8/9) and most desired (mean 5.29/7); users wanted professional help interpreting data (JMIR mHealth Uhealth 2025;13:e68919, abstract) — [doi:10.2196/68919](https://doi.org/10.2196/68919) [messner2025adherence]. Relevance: adherence apps do not appear to include recall/batch checks (the abstract does not mention any); supports a history view in the cabinet.
- Engagement: pooled dropout in app-based chronic-disease interventions 43% (95% CI 29-57) across 17 studies, I2 above 99% (J Med Internet Res 2020;22(9):e20283, abstract; JMIR, not JMIR mHealth and uHealth). — [doi:10.2196/20283](https://doi.org/10.2196/20283) [meyerowitzkatz2020dropout]. Relevance: do not rely on daily engagement; make re-checks passive.

### Inferences
- A cabinet whose value does not depend on the user re-opening the app (background re-check on ingest) matches the engagement evidence.

### Gaps
- No JMIR mHealth and uHealth study of recall-alert apps was found; no evidence on engagement with batch-level recall features specifically.

## Q5 Time lags and share of batch consumed before alert

### Takeaway
No published estimate exists of the fraction of a batch sold or consumed before an alert. The component delays are evidenced only piecemeal: Nepal's recall data (many months from manufacture to recall), Indian court findings (sampling-to-report of 6 to 20 months against a 60-day rule), and about three weeks from month end to CDSCO's monthly list.

### Cited Findings
- Nepal, 50 substandard-drug recalls posted 17 Apr 2023-14 May 2025: 34% were recalled after 15 months on the market and 26% within the first 5 months (the abstract's wording of the 15-month category is ambiguous); causes included non-compliance with Indian Pharmacopoeia 2022 (40%) and assay failure (34%) (Ther Adv Drug Saf 2025;16:20420986251398725, abstract only). — [doi:10.1177/20420986251398725](https://doi.org/10.1177/20420986251398725) [barma2025recall]. Relevance: the only quantitative manufacture-to-recall lag found; much of a batch is likely consumed before recall; "NOT_LISTED" can only mean "not listed as of the list date".
- Bombay High Court (Nagpur Bench), Ashwani v. State of Maharashtra, 2026:BHC-NAG:945, judgment dated 17 Jan 2026 (per LiveLaw excerpt): sample sent to the Government Analyst 14 Jul 2022; extension sought only on 1 Nov 2022, after the 60-day limit in Rule 45 of the Drugs and Cosmetics Rules, 1945; NSQ report 18 Jan 2023 (about six months); prosecution quashed; court asked for more laboratories and online monitoring. Secondary reports only (judgment not opened; the reports differ on naming of parties). — [Verdictum](https://www.verdictum.in/court-updates/high-courts/bombay-high-court/ashwani-v-state-of-maharashtra-2026bhc-nag945-rule-45-drug-testing-delayed-erring-officials-1605430) [verdictum2026ashwani]; [LiveLaw](https://www.livelaw.in/amp/high-court/bombay-high-court/bombay-hc-drugs-cosmetics-rules-sample-testing-60-days-web-host-reports-strict-action-erring-officers-520565).
- Karnataka High Court, M/s Zim Laboratories Ltd v. Union of India, Crl.P. 8341/2018, order of 30 Aug 2024 (NEWS, LiveLaw): the analyst took more than a year (another report of the same case, from a search result, calls it a 20-month delay; not verified); samples tested after shelf life expiry; the court noted the drug may stay in circulation and directed the DCGI to build an online system so samples are tested within 60 days with reports visible online in real time. Judgment not opened; whether the system was built is unverified. — [LiveLaw](https://www.livelaw.in/amp/high-court/karnataka-high-court/karnataka-high-court-orders-dcgi-implement-online-system-expedited-drug-testing-and-reporting-drugs-and-cosmetics-act-268613) [livelaw2024zim]. Relevance: judicial acknowledgement that testing delay lets suspect batches stay in circulation; supports "not yet reported" wording.
- CDSCO guideline clocks (24-72 h Class I etc.) start "from the receipt of information", that is after the analyst's report, and exclude manufacture-to-sampling and testing time [cdsco2024recall]. The August 2026 list was published about three weeks after month end and one listed batch was manufactured 22 months before being listed [pioneer2026august; medicaldialogues2026august] (single data points, not a distribution).
- Official recall logs record quantity produced, distributed, unsold and returned (CDSCO SOP), and 21 CFR 7.42 asks "how much product remains unused", but no public figure of these quantities was found [cdsco2012recall; fda2026cfr742].

### Inferences
- Patient exposure delay = market residence before sampling (unobserved) + sampling-to-report (statutory 60 days, exceeded in the cited cases) + report-to-monthly-list (about 3 weeks) + list-to-patient (no consumer channel for Class II/III). With 24-36 month shelf lives, many listed batches are probably already dispensed (inference, unverified).
- This justifies (a) repeat checking when each new list is ingested, (b) displaying the list month and ingest date, (c) never presenting NOT_LISTED as "safe".

### Gaps
- No published Indian estimate of sampling-to-report time or of the share of a batch consumed before alert; no US equivalent. Court reports are secondary and anecdotal.

## BibTeX

@misc{cdsco2012recall,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Guidelines on Recall and Rapid Alert System for Drugs (Including Biologicals and Vaccines), Document No. CDSCO/RRAS Ver. 00, effective 23 November 2012; with SOP QA-GNL-021 Rev. 01 (effective 1 August 2015)},
  year = {2012},
  howpublished = {Directorate General of Health Services, Ministry of Health and Family Welfare, Government of India},
  url = {https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/4GuidelineRecalRapidAlert.pdf},
  note = {Accessed 25 Oct 2026. Hosted copy labelled Version 2017.}
}

@misc{cdsco2024recall,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Guidelines on Recall and Rapid Alert System for Drugs, Version 2024, Document No. CDSCO/RRAS Ver. 00, effective 18 July 2024; with SOP QMS-GNL-010},
  year = {2024},
  howpublished = {Directorate General of Health Services, Ministry of Health and Family Welfare, Government of India},
  url = {https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/biologicals/Guidelinerapid24.pdf},
  note = {Accessed 25 Oct 2026}
}

@misc{fda2026cfr742,
  author = {{U.S. Food and Drug Administration}},
  title = {21 {CFR} 7.42: Recall strategy},
  year = {2026},
  howpublished = {Electronic Code of Federal Regulations},
  url = {https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-7/subpart-C/section-7.42},
  note = {Text version dated 1 Oct 2026. Accessed 25 Oct 2026}
}

@misc{ecfr2026vin,
  author = {{National Highway Traffic Safety Administration}},
  title = {49 {CFR} 573.15: Public availability of recall information (VIN-based recall lookup)},
  year = {2026},
  howpublished = {Electronic Code of Federal Regulations},
  url = {https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-573/section-573.15},
  note = {Text version dated 1 Oct 2026, read via the eCFR API 26 Oct 2026. Section number is as requested from the API; verify against the printed code before citing}
}

@techreport{gao2024vehicle,
  author = {{U.S. Government Accountability Office}},
  title = {Vehicle Safety: Opportunities to Improve Repair Rates for Recalled Vehicles},
  institution = {U.S. Government Accountability Office},
  number = {GAO-24-106356},
  year = {2024},
  month = jan,
  url = {https://www.gao.gov/products/gao-24-106356},
  note = {Accessed 25 Oct 2026}
}

@misc{openfda2026enforcement,
  author = {{U.S. Food and Drug Administration}},
  title = {openFDA: Drug Enforcement Reports API},
  year = {2026},
  url = {https://open.fda.gov/apis/drug/enforcement/},
  note = {Accessed 25 Oct 2026}
}

@misc{who2026gsms,
  author = {{World Health Organization}},
  title = {WHO Global Surveillance and Monitoring System for substandard and falsified medical products},
  year = {2026},
  url = {https://www.who.int/who-global-surveillance-and-monitoring-system},
  note = {Accessed 25 Oct 2026. URL taken from a search result; the page text was read from WHO GSMS pages in an earlier session of this task, re-check before final submission}
}

@article{gadgil2026automating,
  author = {Gadgil, M. and Pavlakos, R. and Carini, S. and Turner, B. and Elder, I. and Hess, W. and Houle, L. and Huff, L. and Johanson, E. and Ramos-Izquierdo, C. and Liang, D. and Ogonowski, P. and Phipps, J. and Peryea, T. and Sim, I.},
  title = {Automating Individualized Notification of Drug Recalls to Patients: Complex Challenges and Qualitative Evaluation},
  journal = {JMIRx Med},
  year = {2026},
  volume = {7},
  pages = {e68345},
  doi = {10.2196/68345},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 41529108}
}

@article{annema2026patient,
  author = {Annema, P. A. and Venrooij, L. M. W. N. and Bouvy, M. L. and van Marum, R. J. and Derijks, H. J.},
  title = {Patient perspectives on drug recalls in the Netherlands: a qualitative study},
  journal = {International Journal of Clinical Pharmacy},
  year = {2026},
  volume = {48},
  number = {3},
  pages = {864--873},
  doi = {10.1007/s11096-025-02082-z},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 41533231}
}

@article{devine2024valsartan,
  author = {Devine, J. W. and Tadrous, M. and Hernandez, I. and Mukhopadhyay, N. and Rothenberger, S. D. and Callaway Kim, K. and Gellad, W. F. and Suda, K. J.},
  title = {Effects of the valsartan recall on heart failure patients: A nationwide analysis},
  journal = {Pharmacoepidemiology and Drug Safety},
  year = {2024},
  volume = {33},
  number = {4},
  pages = {e5777},
  doi = {10.1002/pds.5777},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 38511239}
}

@article{devine2024arb,
  author = {Devine, J. W. and Tadrous, M. and Hernandez, I. and Callaway Kim, K. and Rothenberger, S. D. and Mukhopadhyay, N. and Gellad, W. F. and Suda, K. J.},
  title = {A Retrospective Cohort Study of the 2018 Angiotensin Receptor Blocker Recalls and Subsequent Drug Shortages in Patients With Hypertension},
  journal = {Journal of the American Heart Association},
  year = {2024},
  volume = {13},
  number = {1},
  pages = {e032266},
  doi = {10.1161/JAHA.123.032266},
  note = {Abstract summary via Europe PMC, 26 Oct 2026; PMID 38156554}
}

@article{jackevicius2020valsartan,
  author = {Jackevicius, C. A. and Krumholz, H. M. and Chong, A. and Koh, M. and Ozaki, A. F. and Austin, P. C. and Udell, J. A. and Ko, D. T.},
  title = {Population Impact of Generic Valsartan Recall},
  journal = {Circulation},
  year = {2020},
  volume = {141},
  number = {5},
  pages = {411--413},
  doi = {10.1161/circulationaha.119.044494},
  note = {Research letter; not opened. Numbers cited in these notes come from ACC conference coverage (acc.org, 14 Nov 2019, AHA 2019 presentation); verify against the letter. Accessed 26 Oct 2026; PMID 31707798}
}

@article{morizio2021veterans,
  author = {Morizio, P. L. and Britnell, S. R. and Ottman, A. A.},
  title = {Impact of national valsartan recalls on Veterans' outcomes},
  journal = {Therapeutic Advances in Drug Safety},
  year = {2021},
  volume = {12},
  pages = {20420986211016173},
  doi = {10.1177/20420986211016173},
  note = {Abstract summary via Europe PMC, 26 Oct 2026; PMID 34249328}
}

@article{fenna2021valsartan,
  author = {Fenna, J. and Chu, C. and Hassan, R. and Gomes, T. and Tadrous, M.},
  title = {Extent of a valsartan drug shortage and its effect on antihypertensive drug use in the Canadian population: a national cross-sectional study},
  journal = {CMAJ Open},
  year = {2021},
  volume = {9},
  number = {4},
  pages = {E1128--E1133},
  doi = {10.9778/cmajo.20200232},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 34876414}
}

@article{choi2025ranitidine,
  author = {Choi, J. P. and Kim, S. and Park, J. S. and Kim, M. S. and Choi, N. K. and Shin, C. M. and Lee, J.},
  title = {Utilization of Acid Suppressants After Withdrawal of Ranitidine in Korea: An Interrupted Time Series Analysis},
  journal = {Journal of Preventive Medicine and Public Health},
  year = {2025},
  volume = {58},
  number = {1},
  pages = {21--30},
  doi = {10.3961/jpmph.24.357},
  note = {Abstract summary via Europe PMC, 26 Oct 2026; PMID 39788691}
}

@misc{begam2021ranitidine,
  author = {Begam, Rukaiah Fatma and others},
  title = {Awareness about {FDA} announcement on voluntary recall of ranitidine among physicians and pharmacists in and around Chennai, India: a cross-sectional study},
  howpublished = {Future Journal of Pharmaceutical Sciences, vol. 7},
  year = {2021},
  doi = {10.1186/s43094-021-00267-7},
  note = {Bibliographic data from Crossref only; full text not opened; full author list and article number unconfirmed. Accessed 25 Oct 2026}
}

@article{fryze2025substandard,
  author = {Fryze, I. and Naughton, B. D.},
  title = {Substandard and falsified medicine recalls in the legitimate supply chain: a systematic review of evidence},
  journal = {BMJ Open},
  year = {2025},
  volume = {15},
  number = {10},
  pages = {e103672},
  doi = {10.1136/bmjopen-2025-103672},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 41145244}
}

@article{barma2025recall,
  author = {Barma, S. and Pathak, N. and Dhungana, S. and Jha, P. K. and Shrestha, S.},
  title = {Drug recall, its frequencies and conclusion: a retrospective secondary analysis involving 2-year publicly available data from Nepal},
  journal = {Therapeutic Advances in Drug Safety},
  year = {2025},
  volume = {16},
  pages = {20420986251398725},
  doi = {10.1177/20420986251398725},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 41362372}
}

@article{nunes2026opioid,
  author = {Nunes, J. C. and Costa, G. P. A. and De Aquino, J. P.},
  title = {Characteristics of United States Food and Drug Administration Drug Recalls Involving Opioid Medications, 2002--2025},
  journal = {Pharmacoepidemiology and Drug Safety},
  year = {2026},
  volume = {35},
  number = {3},
  pages = {e70341},
  doi = {10.1002/pds.70341},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 41725568}
}

@article{bekele2026recallclass,
  author = {Bekele, L. K. and Badar, M. A. and Kluse, C. J.},
  title = {Association Between {FDA} Drug Recall Classification and Product-Related Characteristics},
  journal = {Therapeutic Innovation \& Regulatory Science},
  year = {2026},
  doi = {10.1007/s43441-026-01016-9},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; volume and pages not confirmed}
}

@article{yerram2026nitrosamine,
  author = {Yerram, S. and Muhammad Nizam, V. P. and Srivastava, S. and Nanduri, S.},
  title = {Nitrosamine Contamination in Pharmaceuticals: A Retrospective Regulatory Analysis of {USFDA} Recalls and Risk Mitigation Strategies (2018--2025)},
  journal = {Therapeutic Innovation \& Regulatory Science},
  year = {2026},
  volume = {60},
  number = {2},
  pages = {519--533},
  doi = {10.1007/s43441-025-00891-y},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 41247449}
}

@article{bahizi2024rwanda,
  author = {Bahizi, M. and Nyirimigabo, E. and Ntirenganya, L. and Umuhoza, M. I. and Habyalimana, V. and Bikorimana, G. and Ukwishaka, J.},
  title = {A four-year assessment of the characteristics of {Rwandan FDA} drug recalls},
  journal = {BMC Public Health},
  year = {2024},
  volume = {24},
  pages = {1784},
  doi = {10.1186/s12889-024-19245-8},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 38965502}
}

@article{freifeld2026globe,
  author = {Freifeld, C. C. and Van Assche, K. and Olliaro, A. and Battain, M. and Kitignavong, I. and Vidhamaly, V. and Boupha, P. and Boutsamay, K. and Thi Do, N. and Bellingham, K. and Pimxayvong, V. and Olinh, T. and Rosado Olmo, A. and Xu, J. and Jiang, S. and Soult, A. and Insal, S. and Gu{\'e}rin, P. J. and Newton, P. N. and Caillet, C.},
  title = {The Medicine Quality Monitoring Globe: A public health intelligence system for collecting and curating reports of substandard and falsified medical products from publicly available Internet news media},
  journal = {PLOS Digital Health},
  year = {2026},
  volume = {5},
  number = {9},
  pages = {e0001648},
  doi = {10.1371/journal.pdig.0001648},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 42743126}
}

@article{messner2025adherence,
  author = {Messner, K. and Sutter, V. and Allemann, S. and Arnet, I.},
  title = {Exploring the Fit Between the Outputs of Freely Available Medication Adherence Apps and Users' Needs: Mixed Methods Study},
  journal = {JMIR mHealth and uHealth},
  year = {2025},
  volume = {13},
  pages = {e68919},
  doi = {10.2196/68919},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 41401443}
}

@article{meyerowitzkatz2020dropout,
  author = {Meyerowitz-Katz, G. and Ravi, S. and Arnolda, L. and Feng, X. and Maberly, G. and Astell-Burt, T.},
  title = {Rates of Attrition and Dropout in App-Based Interventions for Chronic Disease: Systematic Review and Meta-Analysis},
  journal = {Journal of Medical Internet Research},
  year = {2020},
  volume = {22},
  number = {9},
  pages = {e20283},
  doi = {10.2196/20283},
  note = {Abstract accessed via Europe PMC, 25 Oct 2026; PMID 32990635}
}

@article{thota2018pvpi,
  author = {Thota, P. and Thota, A. and Medhi, B. and Sidhu, S. and Kumar, P. and Selvan, V. K. and Singh, G. N.},
  title = {Drug safety alerts of pharmacovigilance programme of {India}: A scope for targeted spontaneous reporting in {India}},
  journal = {Perspectives in Clinical Research},
  year = {2018},
  volume = {9},
  number = {1},
  pages = {51--55},
  doi = {10.4103/picr.picr_29_17},
  note = {Abstract accessed via Europe PMC, 26 Oct 2026; PMID 29430420}
}

@article{lancet2025tiny,
  author = {{The Lancet Regional Health -- Southeast Asia}},
  title = {Tiny lives, big failures: {India's} drug regulation crisis},
  journal = {The Lancet Regional Health -- Southeast Asia},
  year = {2025},
  volume = {43},
  pages = {100705},
  doi = {10.1016/j.lansea.2025.100705},
  note = {Editorial, Dec 2025; PMC12766585. Accessed 25 Oct 2026. Author attribution not recorded}
}

@misc{hhsoig2017foodrecall,
  author = {{HHS Office of Inspector General}},
  title = {The Food and Drug Administration's Food-Recall Process Did Not Always Ensure the Safety of the Nation's Food Supply, Report A-01-16-01502},
  year = {2017},
  url = {https://oig.hhs.gov/oas/reports/region1/11601502.asp},
  note = {Issued 22 Dec 2017. Accessed 25 Oct 2026}
}

@misc{medicaldialogues2019cdscorecall,
  author = {{Medical Dialogues}},
  title = {{CDSCO} committee to draft new guidelines for effective recall of substandard drugs},
  howpublished = {Medical Dialogues (news)},
  year = {2019},
  url = {https://business.medicaldialogues.in/cdsco-committee-to-draft-new-guidelines-for-effective-recall-of-substandard-drugs},
  note = {News report, 7 Oct 2019, updated 16 Aug 2021. Accessed 25 Oct 2026}
}

@misc{pioneer2026august,
  author = {{Press Trust of India}},
  title = {220 drug samples fail quality tests in August},
  howpublished = {The Daily Pioneer (news)},
  year = {2026},
  url = {https://dailypioneer.com/news/220-drug-samples-fail-quality-tests-august},
  note = {News report, 22 Sep 2026. Accessed 25 Oct 2026}
}

@misc{medicaldialogues2026august,
  author = {Roy, Susmita},
  title = {State drug alert: Azithromycin, Cefixime among 191 drug samples flagged by {CDSCO} for quality failures in {August}},
  howpublished = {Medical Dialogues (news)},
  year = {2026},
  url = {https://medicaldialogues.in/news/industry/pharma/cdsco/state-drug-alert-azithromycin-cefixime-among-191-drug-samples-flagged-by-cdsco-for-quality-failures-in-august-180004},
  note = {News report, 25 Sep 2026. Accessed 25 Oct 2026}
}

@misc{medicaldialogues2026telangana,
  author = {Patel, Parthika},
  title = {Telangana {DCA} introduces {SMS} alert system to warn pharmacies about substandard medicines},
  howpublished = {Medical Dialogues (news)},
  year = {2026},
  url = {https://medicaldialogues.in/news/industry/pharma/telangana-dca-introduces-sms-alert-system-to-warn-pharmacies-about-substandard-medicines-166301},
  note = {Published 11 Mar 2026. News report. Accessed 25 Oct 2026}
}

@misc{medicaldialogues2026karnataka,
  author = {Roy, Susmita},
  title = {Karnataka launches real-time portal to freeze {NSQ} drugs, track {NDPS} medicine sales},
  howpublished = {Medical Dialogues (news), source PTI},
  year = {2026},
  url = {https://medicaldialogues.in/news/industry/pharma/karnataka-launches-real-time-portal-to-freeze-nsq-drugs-track-ndps-medicine-sales-170872},
  note = {Published 17 May 2026. News report. Accessed 26 Oct 2026}
}

@misc{verdictum2026ashwani,
  author = {{Verdictum}},
  title = {Ashwani v. State of Maharashtra, 2026:BHC-NAG:945: Rule 45 drug testing delayed, erring officials},
  howpublished = {Verdictum (legal news); Bombay High Court, Nagpur Bench},
  year = {2026},
  url = {https://www.verdictum.in/court-updates/high-courts/bombay-high-court/ashwani-v-state-of-maharashtra-2026bhc-nag945-rule-45-drug-testing-delayed-erring-officials-1605430},
  note = {Legal news report; judgment dated 17 Jan 2026 per LiveLaw excerpt; judgment text not opened. Accessed 26 Oct 2026}
}

@misc{livelaw2024zim,
  author = {{LiveLaw}},
  title = {Karnataka High Court orders {DCGI} to implement online system for expedited drug testing and reporting ({M/s Zim Laboratories Ltd v. Union of India}, Crl.P. 8341/2018)},
  howpublished = {LiveLaw (legal news)},
  year = {2024},
  url = {https://www.livelaw.in/amp/high-court/karnataka-high-court/karnataka-high-court-orders-dcgi-implement-online-system-expedited-drug-testing-and-reporting-drugs-and-cosmetics-act-268613},
  note = {News report, Sep 2024 on an order of about 30 Aug 2024; judgment not opened. Accessed 26 Oct 2026}
}

@misc{livelaw2026ashwani,
  author = {Vaishya, Saksham},
  title = {Drugs \& Cosmetics Rules | 60-Day Sample Testing Mandatory; Web-Host Reports: {Bombay HC} Orders Strict Action Against Erring Officers},
  howpublished = {LiveLaw (legal news); Bombay High Court, Nagpur Bench},
  year = {2026},
  url = {https://www.livelaw.in/amp/high-court/bombay-high-court/bombay-hc-drugs-cosmetics-rules-sample-testing-60-days-web-host-reports-strict-action-erring-officers-520565},
  note = {News report dated 24 Jan 2026 on Ashwani \& Ors. v. State of Maharashtra, Crl. WP 967 of 2024; judgment not opened. Accessed 26 Oct 2026}
}

@misc{acc2019valsartan,
  author = {{American College of Cardiology}},
  title = {Study Examines Effect of Valsartan Recall},
  howpublished = {ACC Latest in Cardiology (AHA 2019 conference coverage)},
  year = {2019},
  url = {https://www.acc.org/latest-in-cardiology/articles/2019/11/14/13/36/sat-715am-population-impact-generic-valsartan-recall-aha-2019},
  note = {Dated 14 Nov 2019 from the URL. Page itself blocked on 26 Oct 2026; title seen in search results and figures cross-checked in MDedge coverage (mdedge.com/cardiology/article/212447). Accessed 26 Oct 2026}
}

## Verification log

Verified 26 Oct 2026 by a second pass (Crossref, Europe PMC abstracts, publisher and regulator pages, GAO PDF text). The BibTeX section above is the researcher's original; use recall_monitoring.bib, which contains the verified and corrected entries.

- fda2026cfr742: CORRECTED. eCFR text for 21 CFR 7.42 (version 1 Oct 2026) confirmed: effectiveness-check levels A-E, depth of recall, public warning. The notes' quotation was wrong; the printed factor is "Degree to which the product remains unused in the market-place". Fixed in the notes.
- ecfr2026vin: CORRECTED. 49 CFR 573.15 confirmed (25,000 light vehicles / 5,000 motorcycles; updated at least every 7 calendar days with last-update date shown; 15 calendar years). Title corrected to "Public availability of motor vehicle recall information"; the "verify section number" caveat is resolved.
- gao2024vehicle: VERIFIED. GAO-24-106356 (9 Jan 2024): 69 percent remedied 15 months after remedy available (2021 NHTSA report, footnote 4); Takata manufacturers almost 80 percent with at least monthly outreach by certified mail, postcards, email, phone, social media; NHTSA 2019 research with five focus groups and 189 participants; First-Class Mail requirement. The attribution "GAO-18-127 found owners prefer at least one electronic notification" was not found in this report and is UNVERIFIED.
- openfda2026enforcement: VERIFIED (page read). Weekly updates, 2004 to present, RES source, disclaimers on public alerts and lifecycle tracking, status not updated after classification, recalls may be expanded to more lots, "Do not rely on openFDA to make decisions regarding medical care". The listed field names (recall_initiation_date etc.) were not re-checked.
- cdsco2012recall: CORRECTED. PDF text confirms effective 23/11/2012, "auditing and accountability is not in place", timelines (24-72 h, 10 d, 30 d), Class I public announcements via print/electronic media, SOP QA-GNL-021 Rev. 01 effective 01.08.2015, SOP 5.4-5.5, Recall Log, fastest-mode communication incl. SMS. The claim that the hosted copy is "labelled Version 2017" was NOT found in the PDF text and is dropped.
- cdsco2024recall: VERIFIED. "VERSION: 2024", effective 18/07/2024, 25 pages; SOP wording "It is preferred that information's are given by SMS or through website to the public" confirmed.
- who2026gsms: VERIFIED. 72 h contact, 24 h for adverse reactions, Medical Product Alert criteria, 2013 launch confirmed on the page. The "877 incidents, 36.3% annual increase" figure came from a search snippet and is UNVERIFIED.
- hhsoig2017foodrecall: VERIFIED. Report A-01-16-01502, issued 22 Dec 2017; 30 recalls sampled from 1,557 reported 1 Oct 2012 to 4 May 2015.
- gadgil2026automating: VERIFIED. Crossref and abstract match (15 authors, JMIRx Med 7, e68345; nightly scan, 9 patients, lot-traceability conclusion).
- annema2026patient: CORRECTED. Metadata and abstract match; second author's name corrected to Nahar-van Venrooij, L. M. W.
- jackevicius2020valsartan: CORRECTED. Bibliographic data verified (Circulation 141(5):411-413, 2020). Letter not opened. 55,461 patients and ED visits 0.11% to 0.17% (P = .02) confirmed in MDedge conference coverage; 73.8%/8.8% seen only in a search summary and 10.7% at 3 months not found: marked [UNVERIFIED] in Q1.
- acc2019valsartan: CORRECTED. ACC page title is "Study Examines Effect of Valsartan Recall"; the page is blocked to scripted access, so figures were cross-checked in MDedge (mdedge.com/cardiology/article/212447). New key added (the notes cited the URL without a key).
- devine2024valsartan: VERIFIED. 87,130 adherent patients, HR 1.00 (0.96-1.03) for all-cause hospitalisation/ED/UC; cardiac events HR 1.04.
- devine2024arb: VERIFIED. 76,934 vs 509,472; HR 1.02 (1.00-1.04) and 1.22 (1.15-1.29). The abstract attributes effects to the recall and shortage; the notes' inference that harm stems from disruption rather than continued use is the researcher's inference, not a finding [UNVERIFIED as a causal claim].
- morizio2021veterans: VERIFIED. 300 patients, letter mailed 12 Mar 2019, SBP 137.2 vs 135.8 (p = 0.125), control 28% vs 27%, 33 changes, 11 recall-related.
- fenna2021valsartan: VERIFIED. 57.8% fall (362,231 to 152,892), non-valsartan ARBs +14.6%; CMAJ Open 9(4):E1128-E1133.
- choi2025ranitidine: VERIFIED. HIRA Jan 2016 to May 2023; H2RA -1041.7, PPI +235.2 DDD per 100,000 per day; JPMPH 58(1):21-30.
- begam2021ranitidine: CORRECTED. Authors are Begam, Ravikumar, Velmurugan; article number 112 (Future J Pharm Sci 7). Full text read: 198 physicians and 113 pharmacists confirmed; awareness is 75% in the abstract and 74% (230/311) in the results, so the earlier "74% UNVERIFIED" is now verified with that caveat.
- fryze2025substandard: VERIFIED. 13 papers, 23 countries, India named for Zambia, Sri Lanka, Brazil, Nepal; nitrosamines recalled in all regions in 2018; BMJ Open 15(10):e103672.
- bahizi2024rwanda: VERIFIED. 33.0% Class I, antibiotics 35.8%, contamination 26.4%, India 29.2%, Feb 2019-Feb 2023; BMC Public Health 24:1784.
- thota2018pvpi: VERIFIED. About 100,000 case reports a year, 250 AMCs, 250,787 ICSRs Jul 2011-Jun 2017, 56 alerts Mar 2016-Jun 2017; Perspect Clin Res 9(1):51-55.
- lancet2025tiny: VERIFIED. Editorial (PMC12766585): October 2025 WHO alert, 20 child deaths, seven alerts since 2022, over 300 deaths, "robust drug recall mechanism". Corporate authorship, no named authors.
- bekele2026recallclass: VERIFIED. 13,248 recalls 2015-2024; Cramer's V 0.550 for cause confirmed; online 11 Jul 2026, volume and pages unassigned.
- nunes2026opioid: VERIFIED. 286 recalls, over 350 million units, unit counts missing for 34 events (11.9%); PDS 35(3):e70341.
- yerram2026nitrosamine: VERIFIED. Jul 2018-Mar 2025, ARBs and metformin most recalled; TIRS 60(2):519-533.
- freifeld2026globe: VERIFIED. 11,000 incidents Jul 2018-Dec 2024; precision 37%, recall 90%, F1 52%; five languages; curators review.
- messner2025adherence: VERIFIED. 80 screened, 9 included, tracking history 8/9, mean desire 5.29.
- meyerowitzkatz2020dropout: VERIFIED. 17 studies, pooled dropout 43% (29-57), I2 above 99%; J Med Internet Res 22(9):e20283.
- barma2025recall: VERIFIED. 50 recalls, 17 Apr 2023-14 May 2025, 34% recalled after 15 months and 26% within the first 5 months, IP-2022 non-compliance 40%, assay failure 34%.
- medicaldialogues2019cdscorecall: CORRECTED. Published 2019-10-07, updated 16 Aug 2021, author Farhat Nasim; short/medium/long-term content (nodal officers, WhatsApp, websites, mobile app, portal) confirmed.
- pioneer2026august: VERIFIED. PTI, 22 Sep 2026; 29 CDL and 191 SDL NSQ samples; one spurious sample from Delhi; batch-specific statement confirmed.
- medicaldialogues2026august: VERIFIED. Susmita Roy, 25 Sep 2026; four spurious entries; azithromycin batch 2408001232 mfg Oct-2024, exp Sep-2026, AUG-2026; rosuvastatin IT04501 mfg Jul-2025, exp Jun-2025.
- medicaldialogues2026telangana: VERIFIED. Parthika Patel, 11 Mar 2026; bulk SMS to pharmacies and wholesalers on NSQ declaration by the Hyderabad lab; the "few states" claim is attributed on the page to The Hindu and was not independently checked.
- medicaldialogues2026karnataka: VERIFIED. Susmita Roy, 17 May 2026, source PTI; about 15,000 stockists/wholesalers, about 45,000 retailers planned, Rs 1.85 crore recalled in 2025-26, minister's remark that substandard medicines could still reach the public. The 30-to-3-day claim was not on the page and stays UNVERIFIED.
- verdictum2026ashwani: CORRECTED. Real headline is "Delay Beyond 60 Days in Drug Sample Testing Vitiates Prosecution: Bombay High Court Quashes Case Under Drugs and Cosmetics Act" (Agatha Shukla, 25 Jan 2026); neutral citation 2026:BHC-NAG:945, 60-day rule, additional laboratories and online monitoring confirmed. The notes' title was reconstructed from the URL slug. Judgment date 17 Jan 2026 not confirmed [UNVERIFIED].
- livelaw2026ashwani: CORRECTED. LiveLaw (Saksham Vaishya, 24 Jan 2026): petitioners are directors of M/s Oscar Remedies Pvt Ltd (Ashwani Lamba and others), Crl WP 967/2024; sample drawn 12 Jul 2022, forwarded 14 Jul 2022, extension sought 1 Nov 2022, NSQ report 18 Jan 2023; compliance listed 4 May 2026. New key added (the notes cited this URL without a key).
- livelaw2024zim: CORRECTED. Real headline is "Karnataka High Court Directs Creation Of Online System For Expeditious Testing Of Drug Samples By Govt Analyst, Uploading Of Reports" (4 Sep 2024; 2024 LiveLaw (Kar) 393; Justice N S Sanjay Gowda). "More than a year" and tests after shelf-life expiry confirmed; the notes' "30 Aug 2024" order date and the "20-month" figure are not confirmed [UNVERIFIED].
- Not checked, so UNVERIFIED and absent from the .bib: the 2013 NHTSA rule (Federal Register 2013-19785) and the WHO activity report (877 incidents).

Verification: COMPLETE

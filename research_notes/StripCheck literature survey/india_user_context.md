Status: COMPLETE

# Indian user context for a phone-based medicine-checking tool (StripCheck)

Overall takeaways (for Related Work / motivation; today = 25 Oct 2026)
- Buying medicines without a prescription from a neighbourhood chemist is normal in India (meta-analysis pooled ~54% self-medication, very heterogeneous), so the point of sale is the natural moment for a batch check; the chemist acts as advisor, so the abstain verdict should refer the user to the pharmacist.
- Phone access is wide but uneven: 886 M active internet users in 2024, 55% rural, 98% use Indic-language content (IAMAI-KANTAR, via news); NFHS-6 reportedly has 64.3% of women 15-49 ever using the internet (secondary source). Implication: multilingual, voice-capable, low-typing UI and shared-device privacy.
- Health literacy is low in the few Indian community studies (11.7% adequate in rural Hooghly; small local samples, no national figure found). Classic HCI evidence (Medhi 2011) says text UIs fail low-literacy users while graphics plus local-language audio work: verdicts need icon + short plain sentence + audio, never colour or icon alone.
- No opened study measures what Indian consumers do on suspecting a fake medicine; the only formal channel found is PvPI (adverse reactions: helpline 1800-180-3024, form, app), with a Nov 2025 push for QR displays at pharmacies. This is a stated research gap.
- Regulatory context: e-pharmacy rules are still a 2018 draft (GSR 817(E)) as of mid-2026 and chemists struck on 20 May 2026; DPDP Rules phased to ~May 2027; WCAG 2.2 (Dec 2024) and GIGW 3.0 are the accessibility yardsticks. A local, offline, read-only alert checker sits outside both e-pharmacy and ABDM.
- Source-quality warning: many 2025-26 figures come from news or secondary analyses (labelled); primary IAMAI, NFHS-6 and TRAI documents were not opened.

Checklist
- [x] Q1 Self-medication / OTC prevalence, retail chemists, generic vs branded, Jan Aushadhi
- [x] Q2 Smartphone / internet penetration, Indic-language users, health literacy
- [x] Q3 Behaviour on suspecting a bad medicine, trust in pharmacists, PvPI reporting
- [x] Q4 Digital-health infrastructure and rules: ABDM, e-pharmacy status, WCAG 2.2, GIGW 3.0
- [x] Q5 Design evidence for health alerts for low-literacy / multilingual users

## Q1 Self-medication, OTC purchase, retail chemists, generics, Jan Aushadhi
- [PEER-REVIEWED] Rashid et al. 2020 (Curr Clin Pharmacol 15(2):90-101, doi 10.2174/1574884714666191122103953): meta-analysis of 17 Indian cross-sectional studies (n=10,248; studies 2000-2016; PubMed + Cochrane only). Pooled self-medication prevalence 53.57% (95% CI 36.92-70.21), I2=100%, study range 8.3%-92%. Source of medicine: familiarity 30.45%, pharmacist advice 30.10% (11 studies), other 11.98%. Indications: headache 41.5%, cough/cold 40.5%, fever 39.9%. Drug classes: NSAIDs 45.9%. Reasons: minor ailment 42.5%, economic 30.9%. Egger test significant (p=0.013) = possible publication bias; samples often students/narrow groups. Relevance: self-purchase from the chemist is mainstream, so the point of purchase is where a batch check is most useful; the very high heterogeneity means cite the 54% as indicative only. URL https://pmc.ncbi.nlm.nih.gov/articles/PMC7579319
- [PEER-REVIEWED] Chandran & Manickavasagam 2022 (J Family Med Prim Care 11(9):5516-5520, doi 10.4103/jfmpc.jfmpc_2157_21): interviews with pharmacists of 15 stand-alone pharmacies (Chennai + a tier-2 TN city). On average 38% of daily sales (range 28-75%) were without prescription; all 15 admitted selling prescription drugs over the counter; 7/15 sold antibiotics without prescription; 60% said customers describe symptoms, 40% ask by brand name. Self-report, n=15 (authors note likely under-reporting). Cites Pune simulated-client studies (94% of 263 pharmacies dispensed antibiotics in 2013). Relevance: buying without a prescription is routine, the chemist is the de facto advisor, and buyers often name brands, so the product-name/brand corroboration step in StripCheck matches how people actually ask. URL https://pmc.ncbi.nlm.nih.gov/articles/PMC9731000
- [SEARCH-SNIPPET ONLY, not opened] Other Indian meta-analyses exist (pregnant women pooled 19.3%, Chaudhary et al. 2024, Pharmacoepidemiol Drug Saf; paediatric antibiotic self-medication 19.8%): not opened, do not cite until verified.
- [NEWS, trade-body claim] AIOCD (trade body) says it represents about 12.4 lakh chemists and distributors (ETV Bharat, 13 May 2026); 8.5 lakh was cited by AIOCD in 2020 (search snippet only). Not an independent count; a Pharmacy Council of India / state licensing figure was not found. ETV Bharat https://www.etvbharat.com/en/health/pharmacies-across-india-shut-may-20-epharmacy-concerns-enn26051305103
- [NEWS/IANS quoting Ministry of Chemicals and Fertilisers, 17 Jun 2026] Jan Aushadhi Kendras: about 84 in 2014 to more than 19,200 in 2026 (UP 4,042; Kerala 1,791; Karnataka 1,665; TN 1,591); ministry claims >Rs 40,000 crore citizen savings. A search snippet (not opened) gives 20,149 as of 30 Jun 2026 and a target of 25,000 by Mar 2027. Relevance: a parallel generic channel with its own packaging, so StripCheck must handle generic-name labels, not only brands. https://ianslive.in/jan-aushadhi-kendras-grow-to-over-19200-from-just-84-in-2014-govt--20260617182223
- [PEER-REVIEWED] Rathi & Biyani 2021, "Knowledge, attitude, and perception of Indian population about generic versus branded medicines: a web-based study", Asian J Pharm Clin Res 14(2), doi 10.22159/ajpcr.2021v14i2.40088 (pages not confirmed; full text opened). Online convenience sample n=537 (internet users, so biased). 78.6% had heard of generics; 54.8% preferred to buy generics but 74.3% had never asked a doctor for generics; only 22.1% thought doctors preferred generics, 37.7% thought chemists preferred to sell generics; 44.9% did not know the type of drugs on their own prescription. Relevance: many users cannot name what they take and the chemist's choice dominates, so StripCheck should read generic and brand names and not assume the user knows the composition. https://journals.innovareacademics.in/index.php/ajpcr/article/download/40088/24378
- [Search snippets only] BMJ Global Health 2018 (Aivalli et al., Karnataka, supplement) reportedly found generic and branded products of comparable tested quality but perceptions favouring branded; page returned HTTP 403, so not cited. A Mysuru Jan Aushadhi perception study (IJCMPH) also unopened.

### Takeaway
Self-purchase from chemists is mainstream and prescription-free sales are routine; Jan Aushadhi (about 19,200 to 20,100 outlets in mid-2026, a government claim) adds a generic-name channel. This motivates a point-of-purchase check that handles both brand and generic labels.
### Inferences
- Because buyers often ask by brand or symptom and cannot name their drug, corroborating product, brand and maker (not only batch) matches real labelling variety.
### Gaps
- No opened source on the generic-vs-branded share of volume, nor an independent chemist count (12.4 lakh is a trade-body claim; one 2026 article says over 8 lakh struck).

## Q2 Smartphone and internet penetration, Indic-language users, health literacy
- [NEWS (PTI via The Week), 16 Jan 2025, reporting IAMAI-KANTAR "Internet in India Report 2024"] 886 million active internet users in 2024 (+8% y/y), projected >900 million in 2025; 488 million rural users = 55%; 98% access Indic-language content; ~57% of urban users prefer regional languages; 47% of users are women; women ~58% of shared-device users in rural India. Primary PDF not opened. Relevance: strongly motivates multilingual output and a phone-first UI; shared devices raise a privacy point for the medicine cabinet. https://www.theweek.in/wire-updates/business/2025/01/16/dcm51-biz-iamai-internet-usage-report.html
- [TRAI, search snippets only, PR No. 104/2026; PDF >10MB could not be fetched] End-June 2026 total telephone subscribers 1,348.08 million; broadband 1,087.50 million incl. M2M / 1,001.50 million excl. M2M; end-July 2026 broadband 1,094.48 million incl. M2M (news reprints). Note broadband subscriptions are connections, not unique people or smartphones. Official PR: https://www.trai.gov.in/sites/default/files/2026-07/PR_No104of2026_0.pdf (not opened).

- [NEWS/secondary analysis, Dataful (Factly), Ananya Matta, 3 Jul 2026, of NFHS-5 (2019-21) vs NFHS-6 (2023-24 per search snippet; fieldwork dates not stated in opened article)] Women 15-49 who have ever used the internet: 33.3% (NFHS-5) to 64.3% (NFHS-6); own a mobile phone 54% to 63.6%; urban internet use 51.8% to 77.3%; rural 24.6% to 58.6% (article contains a conflicting rural figure, verify against NFHS dataset); mobile ownership urban 77.6%, rural 57.4% (NFHS-6). Relevance: even in the newest data roughly a third of women have never used the internet and rural/urban gaps persist, so a design that assumes confident smartphone use is risky; offline/local operation and simple flows help. Primary NFHS-6 report (MoHFW/IIPS) not opened. https://insights.dataful.in/articles/womens-internet-use-nearly-doubles-but-access-gaps-remain
- [Health literacy: search snippets only, not opened] No national-prevalence study of health literacy in India was found; an MDPI IJERPH 2021 paper (ijerph-18-00495) reportedly says no population-level HL measurement existed in India; a 2026 Gujarat TB-patient study reports 67.1% limited HL (clinical sample). Treat as a gap unless opened later.

- [PEER-REVIEWED, community study] Reshma, Chandrasekhar, Paul, Das 2024, "A Cross-Sectional Study on Health Literacy and its associated factors among Adults of a Rural Area of Hooghly District, West Bengal", Journal of Health Literacy 9(3):95-105, doi 10.22038/jhl.2024.79591.1566. HLS-EU-Q47, adults 18-64 in Singur, two-stage random sample, fieldwork Oct 2020 to Nov 2022: only 11.7% adequate HL, 88.3% problematic/inadequate (inadequate 61.6%); HL linked to age, schooling, employment, family decision-making; adequate in the healthcare domain but inadequate in other domains. One district; not national. Relevance: design for a user who struggles with technical text (plain language, short verdicts). (A Bangalore outpatient HLS-EU-Q16 study, n=200, 65.5% limited HL, was seen only as a search snippet: not cited.) https://literacy.mums.ac.ir/article_24818_412184db862d936baa451b633c1d155a.pdf
- [NEWS snippet only, ETV Bharat 30 May 2026] Corroborates NFHS-6 headline numbers (64.3% vs 33.3% women ever used internet; 63.6% own phone; 6.79 lakh households, 715 districts).

### Takeaway
Phones and Indic-language content dominate Indian internet use and growth, but women, rural and low-schooling users remain less connected, and measured health literacy is low in the few Indian community studies.
### Inferences
- A phone-first, Indic-language, voice-supported, low-typing design is justified, but claims about national health literacy must be avoided (no national measure found).
### Gaps
- IAMAI-KANTAR and NFHS-6 primary reports and the TRAI PDF were not opened; smartphone-specific penetration (as opposed to broadband connections or any phone) was not found in an opened source.

## Q3 Behaviour on suspecting a bad medicine, trust in pharmacists, reporting channels
- [OFFICIAL, IPC (Indian Pharmacopoeia Commission) PvPI FAQ page, last updated 31 Oct 2018 per page] Consumers/patients can report suspected adverse drug reactions via a separate "Medicines Side Effect Reporting Form (for consumers)" sent to the nearest ADR Monitoring Centre or the National Coordinating Centre, via the toll-free helpline 1800-180-3024 (Mon-Fri 9:00-17:30, voicemail otherwise), or via the "ADR PvPI" Android app. Note: these channels are for adverse reactions, not for reporting a suspected fake/NSQ batch to CDSCO; no consumer channel for suspected-spurious reports was confirmed in opened sources. Page date old: confirm current details. https://www.ipc.gov.in/PvPI/faq.html
- [NEWS (Outlook India Healthcare Spotlight), 24 Nov 2025] DCGI (Dr Rajeev Singh Raghuvanshi) circular to State/UT regulators, after the 16th PvPI Working Group Meeting, asks that a PvPI ADR-reporting QR code and the toll-free helpline 1800 180 3024 be prominently displayed at every retail and wholesale pharmacy to raise patient participation (under-reporting called a long-standing problem; no figures given). IPC's ADRMS platform was unveiled by the Health Minister on 19 Aug 2024. Relevance: a pharmacist-point reporting route exists, so StripCheck's "refer to pharmacist / report" step can point users to the PvPI helpline/QR for reactions. https://www.outlookindia.com/amp/story/healthcare-spotlight/dcgi-asks-states-to-mandate-display-of-pvpi-qr-code-at-all-pharmacies
- [Search snippet, IPC site, page failed to open (HTTP 500)] IPC announced a multilingual IVRS for the helpline in 10 languages plus English; date not confirmed. Cite only after verifying.
- [Gap, important] No opened survey found of what Indian consumers actually do when they suspect a bad or fake medicine, nor a survey of consumer trust in pharmacists. Searches returned prevalence/regulatory material only. State this as a research gap in the paper (supports a user study as future work). Pharmacy-side behaviour is documented in Chandran 2022 (see Q1).
- [Search snippet only] CDSCO national survey (2014-16) reported NSQ 3.16% and spurious 0.0245% (government sources NSQ 10.02%); not opened here, covered by other researchers' theme (SF medicines in India).

- [NEWS on industry survey, South First, 25 Aug 2026, reporting ASPA-CRISIL "State of Counterfeiting in India 2025"] Online poll of 1,639 consumers in nine cities (only Hyderabad, Chennai, Bengaluru named): 33% met a counterfeit healthcare product in the past year (Hyderabad 46%, Chennai 39%, Bengaluru 33%); 52% check authenticity before buying (62% across all categories); 60% trust their own ability to spot a fake; for healthcare, 66% check packaging quality, 48% look for a hologram, 40% check a QR code; counterfeits were met at local retail outlets (63%) and online aggregators (60%). The article does not say what people do after finding a fake. Industry-sponsored online urban sample: indicative only. Relevance: consumers rely on eyeballing packaging and QR/hologram checks are a known habit, which supports a camera-based check with QR read first. https://thesouthfirst.com/health/a-fake-medicine-can-look-genuine-survey-finds-one-in-three-consumers-met-a-counterfeit-healthcare-product/

### Takeaway
The only formal consumer channel found is PvPI (adverse reactions) and the Nov 2025 pharmacy QR/helpline push; consumers mostly self-inspect packaging. No opened study documents what Indians do after suspecting a bad medicine or how much they trust chemists.
### Inferences
- StripCheck's CANT_VERIFY / ask-the-pharmacist outcome plus a pointer to the PvPI helpline bridges self-inspection and formal reporting; frame this as a design assumption, not an evidence-based finding.
### Gaps
- No peer-reviewed trust-in-pharmacist or suspected-fake-behaviour survey for India was found; a CDSCO consumer complaint route was not confirmed.

## Q4 Digital-health infrastructure and rules (ABDM, e-pharmacy, WCAG 2.2, GIGW 3.0)
- [OFFICIAL, W3C Recommendation] WCAG 2.2, W3C Recommendation, 12 Dec 2024 (editors Campbell, Adams, Bradley Montgomery, Cooper, Kirkpatrick). Adds 9 success criteria (2.4.11 Focus Not Obscured Min AA; 2.4.12 Enhanced AAA; 2.4.13 Focus Appearance AAA; 2.5.7 Dragging Movements AA; 2.5.8 Target Size (Minimum) AA; 3.2.6 Consistent Help A; 3.3.7 Redundant Entry A; 3.3.8 Accessible Authentication Min AA; 3.3.9 Enhanced AAA); removes 4.1.1 Parsing. Normative text for each criterion was not read in the opened portion. Relevance: concrete, testable targets for a camera/OCR app: large touch targets (2.5.8), no redundant re-entry of batch/product fields after the HITL question (3.3.7), no dragging-only crop gesture (2.5.7), consistent help (3.2.6). https://www.w3.org/TR/WCAG22/
- [OFFICIAL, NIC / MeitY, guidelines.india.gov.in, page "Last Updated 23.10.2026"] GIGW 3.0 = Guidelines for Indian Government Websites and Apps; applies to central/state/district/local government websites and apps; accessibility is one of four pillars (with quality, security, lifecycle); draws on Rights of Persons with Disabilities Act 2016 and WCAG 2.1; certification via STQC. The opened page did not state a conformance level or release year; secondary sources (Digit.in, IMPRI, a vendor blog, snippets only) say WCAG 2.1 AA and 88 mandatory checkpoints: treat as unverified. Relevance: StripCheck is not a government app so GIGW is not binding; cite it as the Indian accessibility benchmark and WCAG 2.2 as the stricter, newer one. https://guidelines.india.gov.in/scope-and-objective/
- [OFFICIAL via PIB-based explainer (Drishti IAS, 8 Jul 2026)] ABDM launched 2021 (September 2021 per FAQ); ABHA = 14-digit health ID, records shared only with consent; >93 crore ABHA accounts and >104 crore health records linked (as of ~8 Jul 2026); NHA is the implementing agency; Scan and Share QR OPD registration. Search snippets (not opened) give 95.99 crore ABHA at 31 Jul 2026 and ~97.8 crore at 1 Sep 2026; numbers differ by cut-off date, so quote the date with every figure. Relevance: ABDM focuses on clinical records and facility registries; it has no drug-batch authenticity layer, so StripCheck sits outside it; an optional future ABHA link is not needed for a local, offline design. https://www.drishtiias.com/daily-updates/daily-news-analysis/ayushman-bharat-health-accounts-abha
- [PEER-REVIEW STATUS UNCERTAIN: new open-access journal, internal inconsistencies noted; use cautiously] Kumar & Hussain 2026 (Int J Pharmaceutical Sciences 4(6):1264-1277, doi 10.5281/zenodo.20552346; published 5 Jun 2026): says the 2018 draft e-pharmacy rules GSR 817(E) (28 Aug 2018) were never notified as binding regulation ("neither enforced nor withdrawn"); GSR 220(E) (26 Mar 2020 per its reference list) relaxed rules for doorstep delivery during COVID; Rule 65 of the Drugs and Cosmetics Rules 1945 is contested for digital prescriptions; Delhi HC (Zaheer Ahmed v Union of India) asked the Centre to expedite rules; strike of 20 May 2026 by AIOCD (article says "over 800,000 chemists", which conflicts with AIOCD's 12.4 lakh membership claim in the news). Relevance: e-pharmacy remains in a regulatory grey zone as of mid-2026, so a consumer tool that only reads public alert lists and does not sell or dispense medicines avoids that regime. https://www.ijpsjournal.com/article/evolving-regulatory-framework-for-e-pharmciesin-india-challenges-legal-concern
- [NEWS (ETV Bharat, 13 May 2026)] AIOCD called a one-day nationwide shutdown on 20 May 2026 against GSR 817(E) and GSR 220(E); it argues online sales weaken Rule 65 safeguards, enable fake prescriptions and antimicrobial misuse; no government response reported in that article. (see Q1 link)
- [Search snippets only, not opened] DPDP Rules 2025 notified 13 Nov 2025, phased: board provisions immediate, consent-manager provisions after 1 year, core notice/consent/security duties after 18 months (about 13 May 2027). Relevance: a local-only app that keeps the medicine cabinet on the device limits personal-data exposure; verify against the Gazette text before citing. Sources seen: Deccan Herald / The Week (PTI) 14 Nov 2025.
- [Gap] Not found/opened: official Gazette text of current e-pharmacy rules (none finalised per Kumar & Hussain), any CDSCO/regulatory guidance that specifically addresses consumer apps that check drug alerts, and the primary ABDM dashboard (abdm.gov.in returned only a title).


### Takeaway
As of mid-2026 e-pharmacy remains an unfinalised 2018 draft with chemist protests; ABDM is large (about 93 to 98 crore ABHAs, dated figures) but record-centred; WCAG 2.2 plus GIGW 3.0 give concrete accessibility targets.
### Inferences
- A read-only offline alert checker avoids the e-pharmacy and ABDM regimes; WCAG 2.2 criteria 2.5.7, 2.5.8, 3.2.6, 3.3.7 map to concrete UI tests.
### Gaps
- GIGW 3.0 conformance level and release year, DPDP treatment of health data, and the primary ABDM dashboard were not confirmed from opened primary sources.

## Q5 Design evidence for health alerts for low-literacy and multilingual users
- [PEER-REVIEWED, classic] Medhi (Thies), Patnaik, Brunskill, Gautama, Thies, Toyama 2011, "Designing Mobile Interfaces for Novice and Low-Literacy Users", ACM TOCHI 18(1), Article 2, 28 pp., April 2011, doi 10.1145/1959022.1959024 (full text opened). Ethnography with 90 low-literacy subjects (India, Kenya, Philippines, South Africa) + two quantitative studies with >70 subjects in India. Text interfaces (forms, SMS, USSD) unusable for first-time low-literacy users and error-prone for literate novices; in a health data-entry task a live operator was up to 10x more accurate than text; in mobile banking the graphical interface had the highest task completion, spoken dialog was faster for those who understood it. Eight recommendations: graphical cues; voice annotation; local-language support in text AND audio; minimise hierarchy; avoid non-numeric text input; avoid scrolling menus; minimise soft-key mappings; integrate human mediators. Relevance: supports pictorial verdict states + spoken verdict in the user's language, minimal typing (camera input, HITL question answered by tapping a candidate), and a human referral (pharmacist) for the abstain case. Caveat: 2011 study, feature-phone era, banking/health-data-entry tasks, not alert comprehension. https://doi.org/10.1145/1959022.1959024
- [PEER-REVIEWED, classic; abstract page opened only] Medhi Thies, Sagar, Toyama 2007, "Text-free User Interfaces for Illiterate and Semi-literate Users", Information Technologies and International Development 4(1):37-50 (page numbers 37-50 confirmed on page; volume/issue from an IDEAS listing URL snippet; DOI not found). Ethnographic design with illiterate domestic workers in three Bangalore slums; semi-abstract graphics + voice feedback + a consistent help feature; text-free designs strongly preferred over text UIs. Relevance: supports icons/colour plus audio for verdicts and an always-visible help control (cf. WCAG 3.2.6 Consistent Help). https://www.microsoft.com/en-us/research/?p=160568
- [PEER-REVIEWED, 2023, non-India but low-literacy medicine pictograms] Dowse, Okeyo, Sikhondze, Khumalo 2023, "Pharmaceutical indication pictograms for low literacy viewers: Health literacy and comprehension", Health SA Gesondheid 28, a2192, doi 10.4102/hsag.v28i0.2192. 90 isiXhosa-speaking adults (max 12 years schooling) in primary care clinics (Makhanda, South Africa); 10 locally developed pictograms; mean comprehension 7.9/10, 8/10 pictograms met the 66.7% correct (ISO) criterion; only 15.6% had adequate health literacy; comprehension rose with health literacy (p=0.002) and education, fell with age. Relevance: pictograms help but must be locally tested; 2 of 10 failed, so StripCheck icons (flagged, suspected fake, not listed, can't verify) need comprehension testing and a text/voice backup, and should not be used alone. Evidence is South African, not Indian. https://hsag.co.za/index.php/hsag/article/view/2192
- [PEER-REVIEWED, 2024 systematic review] Thomas, Jenkins, George 2024, "A systematic review and qualitative evidence synthesis of factors affecting mHealth adoption in India", Oxford Open Digital Health 2, oqae046, doi 10.1093/oodh/oqae046 (published 19 Nov 2024). 22 studies synthesised (from 250 records). Barriers: lack of local-language systems and non-technical wording; low literacy and digital skills (typing, IVR, reading); rural women often without own phones, husbands control access, tariff rise moved women onto husbands' phones; affordability; poor networks; privacy (device alarms revealing condition). Recommends human-centred design, training/support, incremental change, mHealth as complement to health workers not replacement. Relevance: directly supports local-language output, minimal typing, a privacy-aware medicine cabinet on shared phones, and pharmacist referral as complementary human step. Only first 100k characters of the page read. https://academic.oup.com/oodh/article/7904826
- [Gap] No opened Indian study on colour semantics (red/amber/green) or on voice-verdict comprehension for medicine alerts specifically; do not claim any. Colour should never be the only cue (WCAG 1.4.1 use of colour: standard criterion, not re-read here).


### Takeaway
Evidence (mostly 2007-2011 HCI-for-development plus a 2023 pictogram study and a 2024 India mHealth review) favours graphics with local-language audio, minimal typing and human back-up over text-only alerts.
### Inferences
- Verdict screen: icon + one plain sentence in the chosen language + play-audio button + ask-your-pharmacist step; test icons with users (Dowse: 2 of 10 pictograms failed).
### Gaps
- No Indian evidence specifically on colour-coded or spoken medicine-alert verdicts; icon-only labels are not supported (a Qatar label study by Kheir and Dowse was seen only in a snippet).

## BibTeX

@article{rashid2020selfmed,
  author = {Rashid, Mohammad and Chhabra, Mayuri and Kashyap, Arti and Undela, Krishna and Gudi, Sai Krishna},
  title = {Prevalence and Predictors of Self-Medication Practices in {India}: A Systematic Literature Review and Meta-Analysis},
  journal = {Current Clinical Pharmacology},
  year = {2020},
  volume = {15},
  number = {2},
  pages = {90--101},
  doi = {10.2174/1574884714666191122103953},
  note = {PMCID PMC7579319. Full author given names unverified (initials only in opened page).}
}

@article{chandran2022antibiotics,
  author = {Chandran, Deena Sangeetha and Manickavasagam, Prema Prathicksha},
  title = {Sale of antibiotics without prescription in stand-alone pharmacies in {Tamil Nadu}},
  journal = {Journal of Family Medicine and Primary Care},
  year = {2022},
  volume = {11},
  number = {9},
  pages = {5516--5520},
  doi = {10.4103/jfmpc.jfmpc_2157_21}
}

@misc{iamai2025internet,
  author = {{IAMAI and KANTAR}},
  title = {Internet in {India} Report 2024 (as reported by PTI in The Week, news)},
  year = {2025},
  url = {https://www.theweek.in/wire-updates/business/2025/01/16/dcm51-biz-iamai-internet-usage-report.html},
  note = {News report of the study, 16 Jan 2025; primary PDF not opened. Accessed 25 Oct 2026}
}

@misc{trai2026pr104,
  author = {{Telecom Regulatory Authority of India}},
  title = {Press Release No. 104/2026: Highlights of Telecom Subscription Data at the end of June 2026},
  year = {2026},
  url = {https://www.trai.gov.in/sites/default/files/2026-07/PR_No104of2026_0.pdf},
  note = {Figures taken from search snippets; PDF not opened. Accessed 25 Oct 2026}
}

@misc{ians2026janaushadhi,
  author = {{IANS}},
  title = {Jan Aushadhi Kendras grow to over 19,200 from just 84 in 2014: Govt (news)},
  year = {2026},
  url = {https://ianslive.in/jan-aushadhi-kendras-grow-to-over-19200-from-just-84-in-2014-govt--20260617182223},
  note = {News, 17 Jun 2026. Accessed 25 Oct 2026}
}

@misc{etv2026pharmacystrike,
  author = {{ETV Bharat}},
  title = {12 Lakh Pharmacies Across India To Shut On May 20 Over E-Pharmacy Concerns (news)},
  year = {2026},
  url = {https://www.etvbharat.com/en/health/pharmacies-across-india-shut-may-20-epharmacy-concerns-enn26051305103},
  note = {News, 13 May 2026. Accessed 25 Oct 2026}
}

@misc{dataful2026womeninternet,
  author = {Matta, Ananya},
  title = {Women's Internet Use Nearly Doubles, but Access Gaps Remain},
  howpublished = {Dataful (Factly); secondary analysis of NFHS-5 and NFHS-6},
  year = {2026},
  url = {https://insights.dataful.in/articles/womens-internet-use-nearly-doubles-but-access-gaps-remain},
  note = {Published 3 Jul 2026; secondary analysis, primary NFHS-6 report not opened. Accessed 25 Oct 2026}
}

@misc{ipc2018pvpifaq,
  author = {{Indian Pharmacopoeia Commission}},
  title = {{PvPI} -- Frequently Asked Questions},
  year = {2018},
  url = {https://www.ipc.gov.in/PvPI/faq.html},
  note = {Page last updated 31 Oct 2018 as shown on page. Accessed 25 Oct 2026}
}

@misc{outlook2025pvpiqr,
  author = {{Outlook India Healthcare Spotlight}},
  title = {{DCGI} asks states to mandate display of {PvPI} {QR} code at all pharmacies (news)},
  year = {2025},
  url = {https://www.outlookindia.com/amp/story/healthcare-spotlight/dcgi-asks-states-to-mandate-display-of-pvpi-qr-code-at-all-pharmacies},
  note = {News, 24 Nov 2025. Accessed 25 Oct 2026}
}

@misc{w3c2024wcag22,
  author = {Campbell, Alastair and Adams, Chuck and Bradley Montgomery, Rachael and Cooper, Michael and Kirkpatrick, Andrew},
  title = {Web Content Accessibility Guidelines ({WCAG}) 2.2},
  howpublished = {W3C Recommendation},
  year = {2024},
  url = {https://www.w3.org/TR/WCAG22/},
  note = {Published 12 December 2024. Accessed 25 Oct 2026}
}

@misc{nic2026gigw3,
  author = {{National Informatics Centre}},
  title = {Guidelines for {Indian} Government Websites and Apps ({GIGW} 3.0): Scope and Objective},
  year = {2026},
  url = {https://guidelines.india.gov.in/scope-and-objective/},
  note = {Page shows Last Updated 23.10.2026; release year of GIGW 3.0 not stated on opened page. Accessed 25 Oct 2026}
}

@misc{drishti2026abha,
  author = {{Drishti IAS}},
  title = {Ayushman Bharat Health Accounts ({ABHA}) (explainer based on PIB)},
  year = {2026},
  url = {https://www.drishtiias.com/daily-updates/daily-news-analysis/ayushman-bharat-health-accounts-abha},
  note = {News/explainer, 8 Jul 2026. Accessed 25 Oct 2026}
}

@article{kumar2026epharmacy,
  author = {Kumar, Abhishek and Hussain, Kashif},
  title = {Evolving Regulatory Framework for E-Pharmacies in {India}: Challenges \& Legal Concern},
  journal = {International Journal of Pharmaceutical Sciences},
  year = {2026},
  volume = {4},
  number = {6},
  pages = {1264--1277},
  doi = {10.5281/zenodo.20552346},
  note = {Published 5 Jun 2026; new open-access journal, treat with caution}
}

@article{medhi2011mobile,
  author = {Medhi, Indrani and Patnaik, Somani and Brunskill, Emma and Gautama, S. N. Nagasena and Thies, William and Toyama, Kentaro},
  title = {Designing Mobile Interfaces for Novice and Low-Literacy Users},
  journal = {ACM Transactions on Computer-Human Interaction},
  year = {2011},
  volume = {18},
  number = {1},
  pages = {2:1--2:28},
  doi = {10.1145/1959022.1959024}
}

@article{medhi2007textfree,
  author = {Medhi, Indrani and Sagar, Aman and Toyama, Kentaro},
  title = {Text-free User Interfaces for Illiterate and Semi-literate Users},
  journal = {Information Technologies and International Development},
  year = {2007},
  volume = {4},
  number = {1},
  pages = {37--50},
  url = {https://www.microsoft.com/en-us/research/?p=160568},
  note = {Volume/issue taken from a search-result URL; DOI not found. Accessed 25 Oct 2026}
}

@article{dowse2023pictograms,
  author = {Dowse, Ros and Okeyo, Sam and Sikhondze, Simise and Khumalo, Nosihle},
  title = {Pharmaceutical indication pictograms for low literacy viewers: Health literacy and comprehension},
  journal = {Health SA Gesondheid},
  year = {2023},
  volume = {28},
  pages = {a2192},
  doi = {10.4102/hsag.v28i0.2192}
}

@article{thomas2024mhealth,
  author = {Thomas, Verghese and Jenkins, Judy and George, Jomin},
  title = {A systematic review and qualitative evidence synthesis of factors affecting {mHealth} adoption in {India}},
  journal = {Oxford Open Digital Health},
  year = {2024},
  volume = {2},
  pages = {oqae046},
  doi = {10.1093/oodh/oqae046}
}

@article{rathi2021generic,
  author = {Rathi, Heena and Biyani, Mohit},
  title = {Knowledge, attitude, and perception of {Indian} population about generic versus branded medicines: A web-based study},
  journal = {Asian Journal of Pharmaceutical and Clinical Research},
  year = {2021},
  volume = {14},
  number = {2},
  doi = {10.22159/ajpcr.2021v14i2.40088},
  note = {Page numbers not confirmed}
}

@article{reshma2024healthliteracy,
  author = {Reshma, A. S. and Chandrasekhar, Taklikar and Paul, Bobby and Arpita, Das},
  title = {A Cross-Sectional Study on Health Literacy and its associated factors among Adults of a Rural Area of {Hooghly} District, {West Bengal}},
  journal = {Journal of Health Literacy},
  year = {2024},
  volume = {9},
  number = {3},
  pages = {95--105},
  doi = {10.22038/jhl.2024.79591.1566},
  note = {Author name order/given names as printed on the first page; may be reversed for some authors}
}

@misc{southfirst2026counterfeit,
  author = {{South First}},
  title = {A fake medicine can look genuine: survey finds one in three consumers met a counterfeit healthcare product (news on ASPA-CRISIL report)},
  year = {2026},
  url = {https://thesouthfirst.com/health/a-fake-medicine-can-look-genuine-survey-finds-one-in-three-consumers-met-a-counterfeit-healthcare-product/},
  note = {News, 25 Aug 2026; industry survey, primary report not opened. Accessed 25 Oct 2026}
}


## Verification log
- rashid2020selfmed: VERIFIED via Crossref (title, 5 authors, Curr Clin Pharmacol 15(2):90-101, doi match). Given names now confirmed: Muhammed Rashid, Manik Chhabra, Ananth Kashyap, Krishna Undela, Sai K. Gudi. Pooled 53.57% and subgroup figures not re-checked against full text.
- chandran2022antibiotics: VERIFIED via Crossref (title, authors, JFMPC 11(9):5516-5520, Sept 2022, doi match).
- rathi2021generic: CORRECTED. Correct DOI is 10.22159/ajpcr.2021.v14i2.40088 (notes omitted a dot after "ajpcr"); pages 95-98; published 7 Feb 2021 (Crossref + journal page). Survey percentages not re-checked.
- medhi2011mobile: VERIFIED via Crossref (title, 6 authors, ACM TOCHI 18(1), Apr 2011, doi match; article number 2). Specific claims (10x operator accuracy, eight recommendations) not re-checked; the notes say they came from full text.
- medhi2007textfree: CORRECTED. DOI found: 10.1162/itid.2007.4.1.37 (Crossref: Inf. Technol. Int. Dev. 4(1):37-50, Oct 2007); title is "Text-Free User Interfaces for Illiterate and Semiliterate Users" and the first author is Indrani Medhi (the notes' "Medhi Thies" is her later name). An earlier ICTD 2006 conference version exists (doi 10.1109/ictd.2006.301841, pp. 72-82); cite the journal version.
- dowse2023pictograms: VERIFIED (Crossref + journal page). Abstract confirms n=90, mean 7.9/10, 8/10 pictograms met 66.7% ISO criterion, 15.6% adequate HL, HL association p=0.002, negative with age, positive with education. Setting is Makhanda, South Africa as stated.
- thomas2024mhealth: VERIFIED via Crossref (title, authors, Oxford Open Digit Health 2, oqae046, online 19 Nov 2024). Abstract supports human-centred design and digital-literacy disparities; the detailed barrier list (22 studies, women's phone access) not re-checked.
- reshma2024healthliteracy: CORRECTED. Author order/names: A. S. Reshma, Chandrasekhar Taklikar (surname Taklikar), Bobby Paul, Arpita Das; the bib in the notes wrongly treated "Taklikar" as a given name and "Arpita" as a surname. Journal page lists issue 3.4 (Jul-Sep 2024 combined issue), pp. 95-105, doi match. 11.7% adequate / 88.3% problematic-inadequate, HLS-EU-Q47, Oct 2020-Nov 2022 confirmed.
- kumar2026epharmacy: VERIFIED (Zenodo record + publisher page): Abhishek Kumar, Kashif Hussain, Int J Pharm Sci 4(6):1264-1277, 5 Jun 2026. Page confirms GSR 817(E) "never formally notified... neither enforced nor withdrawn", Zaheer Ahmed v Union of India (2018) direction to expedite rules, Rule 65, 20 May 2026 strike. Note: the article itself says "over 800,000" chemists, as the notes flag; the publisher's printed title has the typo "E-Pharmciesin" (corrected in bib). Journal is new; low-prestige source.
- ians2026janaushadhi: VERIFIED (page opened). IANS, 17 Jun 2026: 84 Kendras in 2014 to "more than 19,200" in 2026; UP 4,042, Kerala 1,791, Karnataka 1,665, TN 1,591; ministry claims savings of more than Rs 40,000 crore. Attributed to Ministry of Chemicals and Fertilisers. The unopened 20,149 / 25,000-target snippet stays unverified and should not be cited.
- etv2026pharmacystrike: VERIFIED (page opened). ETV Bharat English Team, 13 May 2026: AIOCD "represents 12.4 lakh chemists and drug distributors"; at least 12 lakh shops to close 20 May 2026; AIOCD demands withdrawal of GSR 220(E) (Mar 2020) and GSR 817(E). The 8.5 lakh (2020) AIOCD figure is [UNVERIFIED] (snippet only). Trade-body claim, not an independent count.
- ipc2018pvpifaq: VERIFIED (page opened). Helpline 1800-180-3024, Mon-Fri 9:00AM-5:30PM with voice-message fallback, "ADR PvPI" Android app, patients/consumers may report ADRs; page footer "Last updated: 31/10/2018". Current details not confirmed. The IVRS-in-10-languages claim remains [UNVERIFIED].
- w3c2024wcag22: VERIFIED (page opened): W3C Recommendation 12 Dec 2024; editors Alastair Campbell, Chuck Adams, Rachael Bradley Montgomery, Michael Cooper, Andrew Kirkpatrick. The list of the nine new success criteria and 4.1.1 removal is standard W3C knowledge and was not re-read in this pass.
- nic2026gigw3: CORRECTED/PARTLY VERIFIED. Page opened ("Last Updated: 23.10.2026"; applies to government websites and apps at any level; STQC certification). The page itself states the guidelines are based on ISO 23026, WCAG 2.1, the RPwD Act 2016 and the IT Act 2000, so "draws on WCAG 2.1" is confirmed from the primary page. The "four pillars" wording and the "AA / 88 checkpoints" claims were not found on the page: [UNVERIFIED].
- outlook2025pvpiqr: VERIFIED (page opened). Archana Jyoti, updated 24 Nov 2025: DCGI Dr Rajeev Singh Raghuvanshi directed State/UT regulators to display the PvPI QR code and helpline 1800 180 3024 at all pharmacies, following the 16th PvPI Working Group meeting; under-reporting called long-standing. The ADRMS launch date of 19 Aug 2024 was not checked here: [UNVERIFIED].
- dataful2026womeninternet: CORRECTED (detail). Page opened (Ananya Matta, 3 Jul 2026): women ever used internet 33.3% to 64.3%; mobile ownership 54% to 63.6%; urban internet 51.8% to 77.3%; rural internet 24.6% to 58.6%; urban mobile ownership 61.8% to 77.6%, rural 36.9% to 57.4% (so notes' "rural 57.4%" is the NFHS-6 ownership value, correct). The article contradicts itself on rural internet use (also states "33.% to 63.3%"), so cite only the 58.6% figure with a caveat or the national 64.3%. Secondary source; NFHS-6 primary report not opened.
- southfirst2026counterfeit: CORRECTED (detail). Page opened (Sumit Jha, 25 Aug 2026): ASPA-CRISIL State of Counterfeiting in India 2025; 1,639 consumers online in nine cities; 33% met counterfeit healthcare product; 52% check authenticity (62% across categories); 60% trust own ability; healthcare cues 66% packaging quality, 48% hologram, 40% QR; 63% local retail, 60% online aggregators (among those who met a counterfeit). Hyderabad 46%, Chennai 39%, Bengaluru 33% are described as city-level counterfeit exposure; the article says "overall" (35% across all categories), so these city figures are likely all-category, NOT healthcare-specific as the notes imply.
- trai2026pr104: VERIFIED (PDF opened, 13.8 MB, dated 28 Jul 2026): total telephone subscribers 1348.08 M; broadband incl. M2M 1087.50 M; excl. M2M 1001.50 M at end-June 2026. The end-July 1,094.48 M figure was not verified here: [UNVERIFIED].
- iamai2025internet: VERIFIED as a news report (PTI via The Week, 16 Jan 2025): 886 M users in 2024 (+8%), 488 M rural = 55%, 98% Indic-language content, 47% women, ~58% of rural shared-device users women. Primary IAMAI-KANTAR PDF not opened; the 57% urban regional-language preference and >900 M 2025 projection were not re-checked: [UNVERIFIED].
- drishti2026abha: PARTLY VERIFIED (page opened, PIB-based explainer): "over 104 crore health records" linked with "more than 93 crore ABHA", ABHA is a 14-digit identifier under ABDM. Launch month (Sept 2021), consent-only sharing, NHA role and Scan and Share not re-checked: [UNVERIFIED]; snippet figures (95.99 crore, 97.8 crore) remain [UNVERIFIED]. Secondary source; prefer a PIB/ABDM primary page.
- Other items in the notes that were snippet-only and remain [UNVERIFIED]: DPDP Rules 2025 phasing; Chaudhary et al. 2024 pregnancy self-medication meta-analysis; Aivalli et al. BMJ Global Health 2018; MDPI IJERPH 2021 health-literacy claim; Gujarat TB study 67.1%; Bangalore HLS-EU-Q16 65.5%; CDSCO 2014-16 survey NSQ 3.16% / spurious 0.0245%; Kheir and Dowse Qatar label study. Rashid 2020 detail: the notes label familiarity 30.45% and pharmacist advice 30.10% as "source of medicine"; the paper reports them as reasons/sources of information for self-medication (minor ailments 42.46% and economic concerns ~30.8% as reasons, headache 41.53%).
Verification: COMPLETE

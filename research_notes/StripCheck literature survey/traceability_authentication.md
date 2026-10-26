Status: COMPLETE

# Pharmaceutical supply-chain authentication and traceability (worldwide and India): what it can and cannot establish

Checklist:
- [x] Q1 India: Schedule H2 QR mandate (G.S.R. 823(E)), API QR codes, export track-and-trace (iVEDA/DAVA), 2024-2026 moves; consumer scan experience
- [x] Q2 EU FMD / Delegated Reg. 2016/161 / EMVS; US DSCSA; GS1 standards
- [x] Q3 Mobile authentication services (Sproxil, mPedigree, NAFDAC MAS, PharmaSecure): uptake, effectiveness, weaknesses
- [x] Q4 Blockchain-based drug traceability: maturity and real-world evidence
- [x] Q5 Sources explicitly saying serialization/authentication cannot detect substandard medicines

## Q1 India: Schedule H2 QR code mandate, API QR codes, export track-and-trace, 2024-2026 moves, consumer scan

### Takeaway
India's domestic regime (as of Oct 2026) is a batch-level, manufacturer-defined bar/QR code on 300 Schedule H2 brands (G.S.R. 823(E), 17 Nov 2022; in force 1 Aug 2023) plus QR codes on APIs (G.S.R. 20(E), 18 Jan 2022; in force 1 Jan 2023), extended by G.S.R. 506(E) (22 Jun 2026) to all vaccines, anticancer and NDPS drugs from 1 Jul 2027 and antimicrobials from 1 Jul 2028. There is no unit-level serial, no national verification database and no regulator-side check: a consumer scan only displays what the manufacturer (or a counterfeiter) encoded. Unit-level GS1 serialization with parent-child aggregation (iVEDA, formerly DAVA) applies only to exports, and its deadlines slipped repeatedly to 1 Feb 2025.

### Cited Findings
- **CDSCO (2023), "FAQs on implementation of GSR 823(E) dated 17th November, 2022 with respect to Bar Code or QR Code on Top 300 Brands"** (2 pp., dated 21.07.2023). Q1: Schedule H2 brands must print/affix a Bar Code or QR code containing (i) unique product identification code, (ii) proper and generic name, brand name, (iv) name and address of manufacturer, (v) batch number, (vi) date of manufacturing, (vii) date of expiry, (viii) manufacturing licence number. Q2: in force 1 Aug 2023. Q3: the unique product identification code "is to be decided by the manufacturer as per his own Standard Operating Procedure" (i.e., no national GS1/GTIN or serial-number mandate). Q4: mandatory only for the 300 listed brands; voluntary for others. Q6: applies to batches manufactured on/after 1 Aug 2023. Q7: may go on secondary label if primary label lacks space. Q8: imports may be labelled in-country with licensing-authority permission. The FAQ says nothing about a central verification database or what a consumer sees on scan. -- [CDSCO FAQ](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Final%20FAQs%20on%20QR%20code%2021.07.2023.pdf)
  - Relevance to StripCheck: the H2 QR payload contains exactly the fields StripCheck needs (batch, dates, maker, brand), so decoding the QR first (before OCR) is justified; but the code is batch-level, manufacturer-defined and not checked against any national register, so a decoded QR is evidence of what the label *claims*, not of authenticity or quality -> StripCheck must still corroborate against CDSCO NSQ/spurious lists. Note also that pre-Aug-2023 batches and non-H2 brands carry no mandated code -> OCR fallback is necessary.
- **CDSCO (c. 2025), "Guidance for Identification and Verification of Spurious Drugs"** (PDF metadata: author "Intelligence Cell", created 9 Apr 2025; issue date not printed in the text). Restates the statutory definition of "spurious" (Drugs and Cosmetics Act 1940: imitation/substitute, fictitious manufacturer, substituted in whole or part, purports to be from a manufacturer it is not). Confirms G.S.R. 20(E) of 18 Jan 2022: every API (bulk drug) made or imported in India must carry a QR code at each packaging level "to facilitate tracking and tracing", minimum data incl. unique product identification code, batch no., mfg and expiry dates; effective 1 Jan 2023. Confirms G.S.R. 823(E) (17 Nov 2022) codes are "to facilitate authentication", effective 1 Aug 2023. The official consumer "process flow" is only three steps: check label for code; scan with mobile phone; "Read the information received on mobile after scanning QR for product authenticity/genuineness". No central database lookup, serial-number check or regulator-hosted verification is described. -- [CDSCO guidance PDF](https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/Guidance-for-Identification-and-Verification-of-Spurious-Drugs.pdf)
  - Relevance: answers "what does a consumer get when scanning an H2 code": the data the manufacturer (or a counterfeiter) encoded, typically plain text or a manufacturer URL, with no national authoritative check. A copied or counterfeit QR decodes just as well. This directly motivates StripCheck treating QR content as an *input to be corroborated*, and checking the batch against the NSQ/spurious lists, which are the only regulator-issued, lab-based signal available to a consumer.
- **Ministry of Health and Family Welfare, G.S.R. 506(E), Drugs (Seventh Amendment) Rules, 2026, dated 22 Jun 2026** (opened via secondary reproductions; I did not open the Gazette PDF itself). Inserts a Table in Schedule H2 extending the bar/QR-code requirement from the 300 listed brands to entire classes: all vaccines, all antimicrobials, all NDPS-Act narcotic and psychotropic drugs, all anticancer drugs. In force 1 Jul 2027, except antimicrobials 1 Jul 2028. Draft published 16 Oct 2025; DTAB consulted. Code on primary label, or secondary if inadequate space. Neither report mentions a central verification database or new data fields. -- [Medical Dialogues, S. Roy, 26 Jun 2026 (news)](https://medicaldialogues.in/amp/news/industry/pharma/health-ministry-brings-vaccines-antibiotics-cancer-drugs-under-qr-code-tracking-framework-173735); [News On AIR (public broadcaster), 25 Jun 2026 (news)](https://newsonair.gov.in/health-ministry-expands-qr-code-based-track-and-trace-framework-for-medicines/) (states purpose as safeguarding against "counterfeit and substandard medicines")
  - Relevance: India is moving toward broader (class-based) coding but still not toward universal unit-level serialization with central verification as of Oct 2026; even after 2027-28 most generic, non-listed products remain uncoded -> OCR path stays necessary. The official framing that QR codes curb "substandard" medicines is analytically weak (a coded genuine batch can still be NSQ), which is exactly StripCheck's niche.

- **Pharmexcil (2020), Circular PXL/HO/Cir-039/2020-21, "iVEDA Web Portal, Beta Version launched and live for company registration and data upload"**, 25 Jun 2020, signed by Uday Bhaskar, DG Pharmexcil. iVEDA (Integrated Validation of Export of Drugs and its Authentication) is a Ministry of Commerce and Industry project, developed by CDAC and maintained by Pharmexcil, replacing the DAVA portal for export track-and-trace; beta live 24 Jun 2020. Exporters upload consignment data for finished formulations (from 1 Jun 2020) in XML; serial numbers may be GS1 codes, another provider's, or CDAC-issued; parent-child aggregation optional, at secondary (last saleable pack) and tertiary levels. -- [Pharmexcil circular](https://pharmexcil.com/circulars/viewcirculars/10445/e38beefbf779b717e688f7b78f8f5768.html)
- **DGFT Public Notice No. 39/2023-DGFT, 2 Feb 2024** (opened via TaxGuru reproduction, not the DGFT PDF). Amends Handbook of Procedures 2023 para 2.76(vi)-(vii) (successor to HBP 2015-20 para 2.90A): date for "maintaining the Parent-Child relationship in packaging levels and its uploading on Central Portal" for drug-formulation exports extended "up to 01.02.2025", for both SSI and non-SSI manufacturers. Secondary reports (SecuringIndustry; search snippets only, site unreachable when fetched) describe repeated earlier slips (1 Apr 2020 -> 1 Oct 2020 -> 1 Apr 2021 -> 1 Apr 2022 -> 31 Mar 2023 -> 1 Aug 2023 -> 1 Feb 2024 -> 1 Feb 2025). -- [TaxGuru reproduction of PN 39/2023](https://taxguru.in/dgft/dgft-extends-track-trace-deadline-drug-exports.html)
  - Relevance: India's only serialized, GS1-style, unit-level system is for *exports* (to meet importing-country rules), not for domestic patients; aggregation deadlines slipped for about five years. Domestic consumers have no unit-level verification, which leaves room for a consumer-side batch check such as StripCheck. Gap: I could not confirm whether the 1 Feb 2025 date was enforced or extended again.

- **Rao, N. (2026). "Karnataka suspends Pfizer C&F Depot licence in fake drug case, warns consumers over suspicious labels and QR codes." *International Business Times India*, 21 Sep 2026 (news).** Karnataka FSDA Drug Enforcement Wing raided a farmhouse at Bidadi on 18 Aug 2026, seizing about Rs 5.05 crore of suspected counterfeit medicines, machinery and printing materials (some carrying Pfizer branding; the depot action does not establish Pfizer's involvement). QR/scanning codes on the suspect labels "did not work" when checked; 16 licences cancelled; consumers told to buy from licensed pharmacies, keep tax invoices and report QR codes that fail to scan. -- [IBTimes India (news)](https://www.ibtimes.co.in/karnataka-suspends-pfizer-cf-depot-licence-fake-drug-case-warns-consumers-over-suspicious-labels-906210); same facts in [National Herald (news)](https://www.nationalheraldindia.com/national/check-medicine-labels-and-qr-codes-karnataka-tells-consumers-amid-fake-drug-probe)
  - Relevance: the official consumer advice in India (Sep 2026) is still "does the QR scan?", a weak test that copied codes pass. StripCheck can treat a QR that fails to decode or contradicts the printed text as a signal for the human-in-the-loop step, and add the regulator-list check that QR scanning lacks.

### Inferences
- Because H2 codes are manufacturer-defined and checked against no national register, a counterfeit can carry a copied or fabricated QR whose content is internally consistent. The H2 QR is useful to StripCheck as a *high-precision reader* of batch, dates and maker (better than OCR when present), not as an authenticity signal.
- Coverage is partial: only 300 brands now, plus four therapeutic classes from 2027-28. Most generic strips and all pre-Aug-2023 batches have no mandated code, so StripCheck's OCR path (RapidOCR/PP-OCR, enhanced re-read, optional VLM) is necessary.
- The 2026 government framing that QR codes curb "substandard" medicines conflates provenance with quality. The CDSCO NSQ list is the only public, batch-specific, lab-based quality signal in India, and StripCheck is built around it.
- India appears in WHO's list of countries with government-run centralized traceability models (WHO 2021). In practice this applies only to the export system (iVEDA), not to domestic patient-facing verification.

### Gaps
- I did not open the Gazette PDFs of G.S.R. 823(E), G.S.R. 20(E) or G.S.R. 506(E) themselves. Their content is taken from the CDSCO FAQ, the CDSCO guidance and news reproductions; verify the exact wording at egazette.gov.in before quoting.
- I could not confirm whether the 1 Feb 2025 iVEDA parent-child aggregation deadline was enforced or extended again (SecuringIndustry was unreachable; TraceLink returned 403).
- I found no official source for a planned central domestic verification database or universal track-and-trace in India for 2024-2026, and no peer-reviewed study of H2 QR scanning behaviour or compliance rates.
- A West Bengal case in which copied H2 QR codes appeared on fakes, and a Gujarat wave of falsified QR codes on an anti-epileptic, were seen only in SecuringIndustry search snippets (site unreachable), so they are unverified and not cited.

## Q2 EU FMD / Delegated Regulation 2016/161 / EMVS; US DSCSA; GS1 standards

### Takeaway
The EU FMD (Directive 2011/62/EU; Delegated Reg. 2016/161, applicable 9 Feb 2019) uses point-of-dispense verification of a serialized unique identifier plus an anti-tampering device. The US DSCSA (2013) mandates B2B package-level interoperable tracing; this was due 27 Nov 2023 and has been phased in through exemptions running to 27 Nov 2027 for small dispensers. Both are built on GS1 identifiers (AIs 01/10/11/17/21 in a GS1 DataMatrix), both target falsified or illegitimate product, and neither gives the patient a quality signal.

### Cited Findings
- **European Commission, DG SANTE, "Falsified medicines" web page** (no last-updated date shown; most recent dated item on page 21 Oct 2026). Directive 2011/62/EU (Falsified Medicines Directive), amending Directive 2001/83/EC, published 1 Jul 2011, applicable since 2 Jan 2013: harmonised safety features, common online-pharmacy logo, stricter active-substance import rules, wholesaler record-keeping. Safety features = a **unique identifier** and an **anti-tampering device** on the outer packaging. Delegated Regulation (EU) 2016/161 lays down the characteristics of the safety features and how/by whom authenticity is verified ("new medicine verification system"); applies from **9 Feb 2019**. Commission Q&A on safety features reached version 22 (10 Jul 2026). The page frames the target as *falsified* medicines ("often disguised as authentic medicines"), not quality defects of genuine products. -- [EC falsified medicines page](https://health.ec.europa.eu/medicinal-products/falsified-medicines_en); [Q&A v22 notice, 10 Jul 2026](https://health.ec.europa.eu/latest-updates/questions-and-answers-version-22-safety-features-medicinal-products-human-use-2026-07-10_en)
  - Gap: EUR-Lex returned a bot-challenge (HTTP 202, empty body) so I could not open the text of Reg. 2016/161 itself; article-level details commonly cited (UI = product code + serial number + batch + expiry [+ national reimbursement number], encoded in a 2D Data Matrix; serial randomised so probability of guessing is negligible; verification and decommissioning at dispensing against the EMVS repositories run by EMVO and national organisations) are from background knowledge and should be checked against EUR-Lex (CELEX 32016R0161, OJ L 32, 9.2.2016) before citing. [UNVERIFIED]
  - Relevance: the EU model is point-of-dispense verification by pharmacists, a B2B check; patients do not query EMVS. A recalled or NSQ batch is handled by setting batch status in the repository only after a quality-defect finding, i.e. the quality signal still comes from lab testing and regulatory action, not from the code. Supports StripCheck's design of keying on batch number and regulator lab-result lists.
- **GS1, "GS1 Application Identifiers" (ref.gs1.org/ai, machine-readable JSON-LD dataset)** (retrieved 25 Oct 2026). AI (01) GTIN, format N2+N14; (10) BATCH/LOT, N2+X..20; (11) PROD DATE, N2+N6 (YYMMDD); (17) USE BY or EXPIRY, N2+N6 (YYMMDD); (21) SERIAL, N2+X..20; national healthcare reimbursement numbers occupy AIs 710-715 (e.g. 714 = Portugal AIM). -- [GS1 AI reference](https://ref.gs1.org/ai/); [dataset](https://ref.gs1.org/ai/GS1_Application_Identifiers.jsonld)
  - Relevance: StripCheck's QR/DataMatrix parser should recognise GS1 element strings (01)(10)(11)(17)(21) (used on Indian export packs and some domestic packs) as well as free-text H2 payloads; (10) is alphanumeric up to 20 chars, so batch normalisation and OCR-confusion handling (B/8, 0/O, 1/7, 5/S) are needed even for machine-read codes when cross-checking against CDSCO tables typed by humans.
- **Melia, E., English, A. & Naughton, B. D. (2024). "The impact of global falsified medicines regulation on healthcare stakeholders in the legitimate pharmaceutical supply chain: a systematic review." *Frontiers in Medicine* 11:1429872. doi:10.3389/fmed.2024.1429872 (PMC11291459).** PRISMA review, 657 records -> 13 studies (11 on EU FMD; 2010-2024). Themes: financial, social, organisational, pharmacy-practice impacts; pack-level scanning is a "practical and costly" burden that slows distribution; high IT/training costs for pharmacies and hospitals. Conclusion: implementation "does not yet appear to categorically fulfill the primary aim" of strengthening the supply chain. Cites a 2023 case where falsified semaglutide (Ozempic) in Germany was detected via the FMD system because the scanned serial numbers were *inactive*. -- [Europe PMC](https://europepmc.org/article/PMC/PMC11291459); [DOI](https://doi.org/10.3389/fmed.2024.1429872)
  - Relevance: the Ozempic case shows what serialization *can* do (detect a falsified pack whose serial is unknown/inactive), which is exactly the case it is built for; a genuine NSQ batch would have active serials. Evidence base on effectiveness is thin (13 studies, mostly implementation burden), supporting the claim that code systems are not a complete answer.
- **Klein, K. & Stolk, P. (2018). "Challenges and Opportunities for the Traceability of (Biological) Medicinal Products." *Drug Safety* 41(10):911-918. doi:10.1007/s40264-018-0678-7 (PMC6153964).** Traceability "up to the batch number can accelerate batch recalls, thereby reducing the time that patients are potentially exposed to unsafe medication" and supports ADR reporting with exposure data; EU barcode standards at the time did not support automatic capture of batch number and expiry in clinical practice; proposes a 2D DataMatrix with batch and expiry on primary and secondary packs. Describes the FMD's two safety features (anti-tampering device; unique identifier for authenticating individual packs, encoded in 2D DataMatrix) and that the FMD "aims to prevent the entry of counterfeit medicinal products", applying from 9 Feb 2019. -- [Europe PMC](https://europepmc.org/article/PMC/PMC6153964); [DOI](https://doi.org/10.1007/s40264-018-0678-7)
  - Relevance: separates two uses of the same code: *authentication* (FMD, against falsification) and *batch-level traceability* for recall and pharmacovigilance (which concerns quality problems in genuine product). StripCheck uses the batch number in the second sense: matching to regulator quality findings (NSQ) is a recall-type use, not an authenticity test.
- **US FDA, "Exemptions under the Drug Supply Chain Security Act"** (content current as of 26 Aug 2026). FDA exempts *small dispensers* (owner has 25 or fewer full-time pharmacists/pharmacy technicians, assessed as of 27 Nov 2026) and, where applicable, their trading partners from certain FD&C Act section 582 enhanced-security requirements until **27 Nov 2027** (previously 27 Nov 2026), to finish a small-dispensers assessment (survey requested by 22 Sep 2026), publish a report and hold a public meeting. No filing needed. -- [FDA DSCSA exemptions page](https://www.fda.gov/drugs/drug-supply-chain-security-act-dscsa/exemptions-under-drug-supply-chain-security-act)
- **Trujillo, S. B. & Sullivan, T. (Quarles & Brady LLP), "FDA Issues Broad Exemptions from DSCSA Enhanced Drug Distribution Security Requirements"**, 10 Oct 2024 (law-firm briefing). Enhanced requirements (FDCA s.582(g): electronic, interoperable exchange of transaction data) were due 27 Nov 2023 (10 years after enactment); FDA granted a one-year "stabilization period" to 27 Nov 2024; on 9 Oct 2024 FDA issued exemptions: manufacturers/repackagers to 27 May 2025, wholesale distributors to 27 Aug 2025, dispensers (26+ FTE) to 27 Nov 2025, small dispensers to 27 Nov 2026 (since extended to 2027, see above). Exemptions conditional on having initiated data connections by 27 Nov 2024. -- [Quarles](https://www.quarles.com/newsroom/publications/fda-issues-broad-exemptions-from-dscsa-enhanced-drug-distribution-security-requirements)
  - Relevance: even the best-resourced market took >12 years (2013 -> 2027) to reach full package-level interoperable tracing, and DSCSA is a B2B trading-partner system with no consumer verification. Supports StripCheck's argument that a lightweight, consumer-side, regulator-list check is useful in the interim and in markets (India) without unit-level tracing. Also DSCSA verifies identifiers and transaction history, not product quality.

### Inferences
- In both EU and US systems the patient is not the verifier: verification is pharmacist- or trading-partner-side. A consumer-side tool in India therefore has no direct Western analogue and has to rely on public regulator data.
- Quality defects in genuine product are handled through recalls and batch-status changes *after* lab or GMP findings. The code system carries the quality signal but does not generate it, which is the same separation StripCheck relies on with CDSCO NSQ lists.
- GS1 AI (10) batch/lot is free alphanumeric up to 20 characters, so even machine-read batch numbers must be normalised before matching against human-typed regulator tables.

### Gaps
- EUR-Lex blocked automated access (HTTP 202 challenge), so article-level text of Reg. (EU) 2016/161 (UI composition, randomisation probability, repository architecture, EMVO/NMVOs, alert rates) is unverified here; check CELEX 32016R0161 manually.
- No primary FDA page opened that lists the DSCSA product-identifier elements (NDC/GTIN, serial, lot, expiry). The FDA pilot final report confirms the 2D data matrix requirement under s.582(a)(9) and GTIN use.
- GS1 General Specifications (DataMatrix symbology section) not opened; only the GS1 AI dataset was.

## Q3 Mobile authentication services: uptake, effectiveness, weaknesses

### Takeaway
SMS/scratch-code mobile authentication services (mPedigree 2006, Sproxil 2009, PharmaSecure 2012, NAFDAC MAS) authenticate the *source* of a pack through a one-time code. The evidence for them is mostly descriptive or vendor-reported. Pharmacists' acceptance is moderate (53% keen to use MAS in Nigeria, 2019). Infrastructure failures (no reply, wrong reply) are common, and codes, scratch panels and even whole verification services can be cloned or spoofed. By 2026, copied QR codes on Indian counterfeits were being reported.

### Cited Findings
- **Oyetunde, O. O., Ogidan, O., Akinyemi, M. I., Ogunbameru, A. A. & Asaolu, O. F. (2019). "Mobile authentication service in Nigeria: An assessment of community pharmacists' acceptance and providers' views of successes and challenges of deployment." *Pharmacy Practice* 17(2):1449. doi:10.18549/pharmpract.2019.2.1449 (PMC6594430).** MAS mechanism: manufacturer/importer buys scratch panels from a NAFDAC-approved MAS provider; panel hides a one-time PIN; consumer texts the PIN to a short code and gets a real-time SMS reply on the *source* of the medicine. Survey of 326 community pharmacists (TAM-based): only 53% keen to use MAS; 51% would recommend it; 54% would encourage clients. Providers attributed failures (no response, wrong response) to GSM downtime, power outages and consumers' limited SMS skills; these failures made some pharmacies look like sources of fakes. Non-probability sample; provider views gathered by e-mail. -- [Europe PMC](https://europepmc.org/article/PMC/PMC6594430); [DOI](https://doi.org/10.18549/pharmpract.2019.2.1449)
  - Relevance: shows that *online* consumer verification fails for infrastructure reasons and that false negatives harm legitimate actors. Supports StripCheck's offline-first design and its explicit CANT_VERIFY abstention instead of returning a misleading "fake" when the check cannot complete. MAS authenticates source only (a one-time PIN), so a genuine NSQ batch would still receive a "genuine" reply.
- **Bansal, D., Malla, S., Gudala, K. & Tiwari, P. (2013). "Anti-counterfeit technologies: a pharmaceutical industry perspective." *Scientia Pharmaceutica* 81(1):1-13. doi:10.3797/scipharm.1202-03 (PMC3617666).** Narrative review from NIPER (India) of overt, covert and track-and-trace technologies (holograms, RFID, 2D barcodes, e-pedigree, mass serialization). States that anti-counterfeit authentication "can verify the supply chain", while analytical methods (chromatography, spectroscopy, isotopic analysis) "confirm the composition"; overt features are "easily mimicked", "may be re-used or refilled" and can "provide false assurance"; without mass serialization only the lot (thousands of units) can be authenticated, not an individual pack. Describes NAFDAC MAS (Sproxil, launched with BIOFEM; GSK used it for Ampiclox). -- [Europe PMC](https://europepmc.org/article/PMC/PMC3617666); [DOI](https://doi.org/10.3797/scipharm.1202-03)
  - Relevance: seminal, India-authored source for the provenance-vs-composition distinction (also cite under Q5) and for re-use/refill of genuine packaging, which is a code-cloning route that defeats label-only checks; StripCheck's verdicts must therefore never assert "genuine".

- **Rasheed, H., Höllein, L. & Holzgrabe, U. (2018). "Future Information Technology Tools for Fighting Substandard and Falsified Medicines in Low- and Middle-Income Countries." *Frontiers in Pharmacology* 9:995. doi:10.3389/fphar.2018.00995 (PMC6127459).** Mini-review. Mobile/SMS "medicines authentication tools" (MATs) were pioneered by mPedigree (2006), Sproxil (2009), Turkey's İlaç Takip Sistemi (2010) and PharmaSecure (Nigeria and India, 2012): a visible or scratch-off code printed by the *manufacturer* is texted to an authentication database, which replies whether the stock is "tagged genuine or fake"; PharmaSecure also lets users send a photo of a suspect medicine. Reports >70 international pharma companies using Sproxil (Kenya, Ghana, Nigeria, South Africa, Mali) and mPedigree in 12 countries (both figures cited to a 2017 secondary source, Wall 2017, not independently verified). Notes India's DAVA (2012) export system; lists WHO GSMS (2013) as the breakthrough "web-based drug safety alert system", and separate field quality-testing tools (TLC kits, paper analytical devices, lab-on-chip) for the quality dimension. -- [Europe PMC](https://europepmc.org/article/PMC/PMC6127459); [DOI](https://doi.org/10.3389/fphar.2018.00995)
  - Relevance: places StripCheck in a taxonomy where *authentication tools* (codes) and *alert systems/quality testing* are distinct categories; StripCheck is a consumer-facing client of a regulator alert system, not a MAT. Uptake/coverage numbers are vendor-derived; no outcome evaluation (reduction in SF prevalence) is reported.

- **O'Hearen, S. (1st Line Partners) (2026). "The Dark Side: 'Serialized, But Not Secure'." *Pharmaceutical Commerce*, 24 Mar 2026 (modified 7 Apr 2026).** (Trade-press opinion, not peer-reviewed.) A serialized 2D DataMatrix "can be replicated and reused"; a counterfeit carrying a copied genuine code may pass verification ("the system may signal it is legitimate, even when it is not") depending on scan timing, repeat-scan allowances and returns workflows; serialization "does not and cannot authenticate the physical product" and is "a regulatory compliance mechanism, not a security control". States copied genuine serials on fakes have occurred "many times" but are "rarely publicized"; gives no specific cases. -- [Pharmaceutical Commerce](https://www.pharmaceuticalcommerce.com/view/the-dark-side-serialized-but-not-secure)
  - Relevance: recent (2026) statement of the code-cloning weakness. In StripCheck, a successfully decoded QR is never treated as proof of authenticity; the SUSPECTED_FAKE verdict is reserved for batches on CDSCO spurious lists or hard-rule field contradictions.

### Inferences
- MAS-style systems answer "was this code issued by the manufacturer?", never "does this batch meet specification?". A genuine NSQ batch would return "genuine".
- Online, SMS-dependent verification fails in low-infrastructure settings, which supports StripCheck's offline, on-device design and its explicit abstention (CANT_VERIFY) when evidence is insufficient.
- Code cloning and spoofed verification services (WHO 2021) mean that a "valid code" verdict can create false assurance. StripCheck should never output a "genuine" verdict, and its NOT_LISTED label is correctly worded as absence from alert lists, not certification.

### Gaps
- No rigorous outcome evaluation (e.g. change in SF prevalence attributable to MAS) was found. The UCL thesis (Ebenezer, 2015), reportedly validating MAS on Glucophage samples against chemical analysis, could not be opened (HTTP 403) and is not cited.
- No independent evaluation of PharmaSecure in India was found; usage figures for Sproxil/mPedigree are vendor-derived (via Rasheed et al. 2018 citing Wall 2017).
- Nigerian consumer-awareness surveys (2019 Southeast Nigeria, n=1,000; 2023 Rivers State) were seen only in search snippets and not opened.

## Q4 Blockchain-based drug traceability: maturity and real-world evidence

### Takeaway
Blockchain traceability is still at pilot and prototype stage. The best real-world evidence is the 6-month MediLedger and IBM/KPMG/Merck/Walmart pilots in FDA's DSCSA Pilot Program (final report May 2023). They showed technical feasibility (privacy-preserving ownership transfer of serialized units), but FDA's lessons stress standards, master-data quality and governance rather than ledger technology. Academic work (38-paper SLR, 2022) is mostly prototypes and simulations, and it addresses falsification and custody, not quality.

### Cited Findings
- **US FDA (2023), *Drug Supply Chain Security Act Pilot Project Program: Final Program Report*, May 2023.** Program established 8 Feb 2019; 20 pilots (incl. MediLedger/Chronicled, IBM/KPMG/Merck/Walmart "DSCSA Blockchain Interoperability Pilot", TraceLink distributed ledgers + digital recalls, UCLA Health-LedgerDomain, IDLogiq). MediLedger pilot (6 months; partners listed in the report include AmerisourceBergen, Cardinal Health, McKesson, FedEx, GS1 US, Chronicled and manufacturers Amgen, Genentech, Gilead, GSK, Lilly, Novartis (Sandoz), Novo Nordisk; trade press reported 24 companies [UNVERIFIED]): design targets of 2000+ transactions/s and verification requests <1 s; private EPCIS messaging + blockchain as an immutable ledger of transaction-authenticity proofs and smart contracts (e.g. no double transfer of ownership of a serialized unit; each unit managed as a non-fungible token) + zk-SNARKs for privacy; "created a test user interface and system performance was evaluated" (no production deployment reported). FDA's general lessons: standardisation and shared master data are critical; data quality and exception handling are major issues; blockchain/RFID are listed merely as "other data carriers and methods" that "could be leveraged". FDA states selection is not an endorsement. -- [FDA DSCSA Pilot Project Program page (current as of 12 Jun 2024)](https://www.fda.gov/drugs/drug-supply-chain-security-act-dscsa/dscsa-pilot-project-program); [Final report PDF](https://www.fda.gov/media/168307/download)
  - Relevance: the most authoritative real-world evidence on blockchain traceability is a set of short B2B pilots; FDA's conclusions are about data standards and governance, not about ledger technology. The ledger proves *custody and identifier validity*, not chemical quality. Justifies StripCheck *not* using blockchain: its problem is matching a consumer's pack to a regulator lab-result list, for which a validated local SQLite index is enough and more transparent.
- **Zakari, N., Al-Razgan, M., Alsaadi, A., Alshareef, H., Al Saigh, H., Alashaikh, L., Alharbi, M., Alomar, R. & Alotaibi, S. (2022). "Blockchain technology in the pharmaceutical industry: a systematic review." *PeerJ Computer Science* 8:e840. doi:10.7717/peerj-cs.840 (PMC9137953).** SLR; 38 papers retained. Most frequent application is counterfeit-drug prevention, then distribution, tracking-and-tracing, safety/security. Reported challenges: immaturity of the technology, scalability/throughput limits (one study cites a ceiling of 1600 tx/s), 51% attacks, integration, cost, lack of experts. Evidence base consists largely of prototypes (e.g. Hyperledger Composer DSCSA prototype) and simulations rather than deployments. -- [Europe PMC](https://europepmc.org/article/PMC/PMC9137953); [DOI](https://doi.org/10.7717/peerj-cs.840)
  - Relevance: supports a Related-Work statement that blockchain drug traceability remains largely at the prototype stage as of 2022 and addresses *falsification and custody*, not substandard quality; positions StripCheck as complementary.

### Inferences
- Even a perfect, immutable ledger records custody and identifier validity. Garbage-in (a genuine but substandard batch) is faithfully recorded as genuine. Blockchain does not address StripCheck's problem, and a local validated SQLite index of regulator alerts is a proportionate design.
- For the Related Work section: blockchain proposals are counterfeit-prevention infrastructure for supply-chain actors, while StripCheck is a consumer-side quality-alert lookup. The two are complementary, not competing.

### Gaps
- The MediLedger consortium's own final report (reported dates conflict: Feb 2020 vs a 2024 news header) was not opened. Performance results beyond the design targets (2000+ tx/s, <1 s verification) are not confirmed.
- No 2024-2026 production deployment of blockchain drug traceability with published outcome data was found. The IEEE Access literature was not systematically searched.

## Q5 Sources stating serialization/authentication cannot detect substandard medicines

### Takeaway
Several authoritative sources say explicitly that identifier verification checks the *code and its status*, not the *contents*. WHO (2021) says verification "cannot check the authenticity of the chemicals, the drug or the active pharmaceutical ingredient inside the package". Bansal et al. (2013) say authentication technologies "verify the supply chain" while analytical methods "confirm the composition". O'Hearen (2026) says serialization "does not and cannot authenticate the physical product". Combined with WHO's definition of substandard products as *authorized* products that fail specifications, it follows that a genuine but NSQ batch carries valid codes. Only lab testing, and therefore a regulator's lab-result alert list, can flag it.

### Cited Findings
- **WHO (2021), *Policy paper on traceability of medical products*** (Geneva, ISBN 978-92-4-002132-7, 52 pp.). Feature 6 (Verification, p.15): "verification techniques cannot check the authenticity of the chemicals, the drug or the active pharmaceutical ingredient inside the package; rather, they confirm the use of genuine unique identifiers and, if applicable, the corresponding status" in the database. Glossary defines substandard ("out of specification") as *authorized* products failing quality standards/specifications. Feature 3 (p.10): lot/batch-level traceability alone means falsified product introduction "cannot be detected"; at most it tracks where lot numbers have been, "which may be sufficient for recall execution and vigilance". Feature 8 (patient verification, p.19): SMS/photo-based patient checks are a "last resort", should not be "the sole way of determining whether a product is safe"; rogue actors have replicated verification services that answer every query positively; a fake pack carried a non-scratchable imitation scratch-off panel; patient-facing services do not authenticate the user and are more susceptible to hacking. Feature 7: full track-and-trace (Argentina, Rep. of Korea, Russia, Turkey, USA) vs point-of-dispense verification (EU). Centralized government-run models listed include India. Estimate cited: 1 in 10 medical products in LMICs substandard or falsified. -- [WHO publication page](https://www.who.int/publications/i/item/policy-paper-on-traceability-of-medical-products); full text opened via [PDF copy](https://www.rsu.lv/sites/default/files/book_download/9789240021327-eng.pdf)
  - Relevance: the single strongest authoritative citation for StripCheck's core premise: identifier verification establishes provenance/authorization, not content quality; a genuine-but-NSQ batch passes any code check, so a lab-result alert list (CDSCO NSQ) is the complementary signal. Also motivates StripCheck's offline design (no remote server that can be spoofed) and its CANT_VERIFY abstention rather than a positive "genuine" verdict.
- **Bansal et al. (2013)** (full entry under Q3): authentication technologies "verify the supply chain" whereas analytical methods "confirm the composition"; overt features may "provide false assurance". -- [Europe PMC](https://europepmc.org/article/PMC/PMC3617666)

### Inferences
- The analytic point for the paper: authentication/traceability establishes *provenance* (this pack or batch was issued by a licensed maker and has not been decommissioned). Quality (assay, dissolution, sterility, contamination) is established only by testing. CDSCO NSQ alerts are test results bound to a batch number, so a batch-level lookup is the right join key, and code verification is orthogonal.
- The same reasoning sets StripCheck's limits. NOT_LISTED means "no adverse lab finding published for this batch", not "safe", because sampling covers only a small fraction of batches. This should be stated explicitly in the paper.

### Gaps
- I found no peer-reviewed empirical study that measured serialization's (non-)detection of substandard product. The claim rests on authoritative policy statements (WHO 2021), reviews (Bansal 2013) and logic (WHO's definition of substandard as authorized product).
- The IFPMA traceability position paper (2021) was behind a bot check and was not read.

## Final takeaways for StripCheck (Related Work synthesis)

1. **Authentication establishes provenance, not quality.** WHO (2021) states that verification "cannot check the authenticity of the chemicals, the drug or the active pharmaceutical ingredient inside the package". By WHO's own definition, substandard products are *authorized* products that fail specifications. A genuine but NSQ batch from a licensed maker therefore passes every code check (H2 QR, EU UI, DSCSA identifier, MAS PIN, blockchain token). Only a lab-result list such as CDSCO's monthly NSQ/spurious alerts can flag it. This is StripCheck's core justification.
2. **India's consumer-facing "verification" is weak by design (Oct 2026).** H2 QR codes are batch-level, manufacturer-defined, cover 300 brands (four more classes from 2027-28), and on scanning show only self-declared data, with no national database lookup. Counterfeits with copied or non-functional QR codes have been seized (Karnataka, Aug 2026). StripCheck should use the QR as a precise *reader*, not as a trust signal, and keep OCR as the main path for uncoded strips.
3. **Unit-level serialization exists in India only for exports (iVEDA).** It is B2B in the EU and US (FMD point-of-dispense, DSCSA trading-partner tracing, fully phased in only by 2027). No system gives patients a quality signal. StripCheck's offline, regulator-list lookup fills a gap that none of these systems address.
4. **Online consumer verification fails and can be spoofed** (MAS no/wrong responses, fake verification services, cloned codes). This supports StripCheck's offline operation, explicit abstention (CANT_VERIFY), human-in-the-loop on doubtful characters, and verdict wording that never certifies "genuine".
5. **Blockchain is pilot-stage and addresses custody, not quality** (FDA pilot report 2023; Zakari et al. 2022). It is not needed for StripCheck's problem.
6. **Limitation to state in the paper:** absence from NSQ lists (NOT_LISTED) is not evidence of quality, because regulator sampling covers few batches. StripCheck complements, and does not replace, serialization and laboratory surveillance.

## BibTeX

@misc{cdsco2023faqqr,
  author = {{Central Drugs Standard Control Organisation}},
  title = {{FAQs on Implementation of GSR 823(E) dated 17th November, 2022 with respect to Bar Code or QR Code on Top 300 Brands}},
  year = {2023},
  howpublished = {CDSCO public notice, dated 21 July 2023},
  url = {https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Final%20FAQs%20on%20QR%20code%2021.07.2023.pdf},
  note = {Accessed 25 Oct 2026}
}

@techreport{who2021traceability,
  author = {{World Health Organization}},
  title = {Policy Paper on Traceability of Medical Products},
  institution = {World Health Organization},
  address = {Geneva},
  year = {2021},
  isbn = {978-92-4-002132-7},
  url = {https://www.who.int/publications/i/item/policy-paper-on-traceability-of-medical-products},
  note = {Accessed 25 Oct 2026}
}

@misc{cdsco2025spuriousguidance,
  author = {{Central Drugs Standard Control Organisation}},
  title = {Guidance for Identification and Verification of Spurious Drugs},
  year = {2025},
  howpublished = {CDSCO guidance document (issue date not printed; PDF created 9 April 2025)},
  url = {https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/Guidance-for-Identification-and-Verification-of-Spurious-Drugs.pdf},
  note = {Accessed 25 Oct 2026}
}

@misc{roy2026qrexpansion,
  author = {Roy, Susmita},
  title = {Health Ministry Brings Vaccines, Antibiotics, Cancer Drugs Under {QR} Code Tracking Framework},
  howpublished = {Medical Dialogues (news), 26 June 2026},
  year = {2026},
  url = {https://medicaldialogues.in/amp/news/industry/pharma/health-ministry-brings-vaccines-antibiotics-cancer-drugs-under-qr-code-tracking-framework-173735},
  note = {Reports G.S.R. 506(E), Drugs (Seventh Amendment) Rules, 2026, dated 22 June 2026. Accessed 25 Oct 2026}
}

@misc{newsonair2026qrexpansion,
  author = {{News On AIR}},
  title = {Health Ministry Expands {QR} Code-Based Track and Trace Framework for Medicines},
  howpublished = {News On AIR (news), 25 June 2026},
  year = {2026},
  url = {https://newsonair.gov.in/health-ministry-expands-qr-code-based-track-and-trace-framework-for-medicines/},
  note = {Accessed 25 Oct 2026}
}

@misc{pharmexcil2020iveda,
  author = {{Pharmaceuticals Export Promotion Council of India}},
  title = {{iVEDA} Web Portal, Beta Version Launched and Live for Company Registration and Data Upload},
  howpublished = {Circular PXL/HO/Cir-039/2020-21, 25 June 2020},
  year = {2020},
  url = {https://pharmexcil.com/circulars/viewcirculars/10445/e38beefbf779b717e688f7b78f8f5768.html},
  note = {Accessed 25 Oct 2026}
}

@misc{dgft2024pn39,
  author = {{Directorate General of Foreign Trade}},
  title = {Public Notice No. 39/2023-DGFT: Track and Trace System for Export of Pharmaceuticals and Drug Consignments},
  howpublished = {Public notice dated 2 February 2024; text consulted via TaxGuru reproduction},
  year = {2024},
  url = {https://taxguru.in/dgft/dgft-extends-track-trace-deadline-drug-exports.html},
  note = {Accessed 25 Oct 2026}
}

@misc{fda2026dscsaexemptions,
  author = {{U.S. Food and Drug Administration}},
  title = {Exemptions under the Drug Supply Chain Security Act},
  year = {2026},
  howpublished = {FDA web page, content current as of 26 August 2026},
  url = {https://www.fda.gov/drugs/drug-supply-chain-security-act-dscsa/exemptions-under-drug-supply-chain-security-act},
  note = {Accessed 25 Oct 2026}
}

@misc{trujillo2024dscsa,
  author = {Trujillo, Susan Brichler and Sullivan, Theodore},
  title = {{FDA} Issues Broad Exemptions from {DSCSA} Enhanced Drug Distribution Security Requirements},
  howpublished = {Quarles \& Brady LLP publication, 10 October 2024},
  year = {2024},
  url = {https://www.quarles.com/newsroom/publications/fda-issues-broad-exemptions-from-dscsa-enhanced-drug-distribution-security-requirements},
  note = {Accessed 25 Oct 2026}
}

@misc{ec2026falsifiedmedicines,
  author = {{European Commission, Directorate-General for Health and Food Safety}},
  title = {Falsified Medicines},
  year = {2026},
  howpublished = {Web page (Directive 2011/62/EU; Delegated Regulation (EU) 2016/161)},
  url = {https://health.ec.europa.eu/medicinal-products/falsified-medicines_en},
  note = {Accessed 25 Oct 2026}
}

@misc{gs12026ai,
  author = {{GS1}},
  title = {{GS1} Application Identifiers},
  year = {2026},
  howpublished = {GS1 reference web page and JSON-LD dataset},
  url = {https://ref.gs1.org/ai/},
  note = {Accessed 25 Oct 2026}
}

@article{oyetunde2019mobile,
  author = {Oyetunde, O. O. and Ogidan, O. and Akinyemi, M. I. and Ogunbameru, A. A. and Asaolu, O. F.},
  title = {Mobile Authentication Service in {Nigeria}: An Assessment of Community Pharmacists' Acceptance and Providers' Views of Successes and Challenges of Deployment},
  journal = {Pharmacy Practice},
  year = {2019},
  volume = {17},
  number = {2},
  pages = {1449},
  doi = {10.18549/pharmpract.2019.2.1449}
}

@article{bansal2013anticounterfeit,
  author = {Bansal, Dipika and Malla, Swathi and Gudala, Kapil and Tiwari, Pramil},
  title = {Anti-Counterfeit Technologies: A Pharmaceutical Industry Perspective},
  journal = {Scientia Pharmaceutica},
  year = {2013},
  volume = {81},
  number = {1},
  pages = {1--13},
  doi = {10.3797/scipharm.1202-03}
}

@article{rasheed2018future,
  author = {Rasheed, Huma and H{\"o}llein, Ludwig and Holzgrabe, Ulrike},
  title = {Future Information Technology Tools for Fighting Substandard and Falsified Medicines in Low- and Middle-Income Countries},
  journal = {Frontiers in Pharmacology},
  year = {2018},
  volume = {9},
  pages = {995},
  doi = {10.3389/fphar.2018.00995}
}

@article{melia2024impact,
  author = {Melia, E. and English, A. and Naughton, B. D.},
  title = {The Impact of Global Falsified Medicines Regulation on Healthcare Stakeholders in the Legitimate Pharmaceutical Supply Chain: A Systematic Review},
  journal = {Frontiers in Medicine},
  year = {2024},
  volume = {11},
  pages = {1429872},
  doi = {10.3389/fmed.2024.1429872}
}

@techreport{fda2023dscsapilot,
  author = {{U.S. Food and Drug Administration}},
  title = {Drug Supply Chain Security Act Pilot Project Program: Final Program Report},
  institution = {U.S. Food and Drug Administration},
  year = {2023},
  month = may,
  url = {https://www.fda.gov/media/168307/download},
  note = {Accessed 25 Oct 2026}
}

@article{zakari2022blockchain,
  author = {Zakari, Nazik and Al-Razgan, Muna and Alsaadi, Amani and Alshareef, Haya and Al Saigh, Heba and Alashaikh, Lamia and Alharbi, Mala and Alomar, Rana and Alotaibi, Seham},
  title = {Blockchain Technology in the Pharmaceutical Industry: A Systematic Review},
  journal = {PeerJ Computer Science},
  year = {2022},
  volume = {8},
  pages = {e840},
  doi = {10.7717/peerj-cs.840}
}

@misc{ohearen2026serialized,
  author = {O'Hearen, Sean},
  title = {The Dark Side: ``Serialized, But Not Secure''},
  howpublished = {Pharmaceutical Commerce (trade press), 24 March 2026},
  year = {2026},
  url = {https://www.pharmaceuticalcommerce.com/view/the-dark-side-serialized-but-not-secure},
  note = {Accessed 25 Oct 2026}
}

@article{klein2018traceability,
  author = {Klein, Kevin and Stolk, Pieter},
  title = {Challenges and Opportunities for the Traceability of (Biological) Medicinal Products},
  journal = {Drug Safety},
  year = {2018},
  volume = {41},
  number = {10},
  pages = {911--918},
  doi = {10.1007/s40264-018-0678-7}
}

@misc{rao2026karnataka,
  author = {Rao, Nisha},
  title = {Karnataka Suspends {Pfizer} {C\&F} Depot Licence in Fake Drug Case, Warns Consumers over Suspicious Labels and {QR} Codes},
  howpublished = {International Business Times India (news), 21 September 2026},
  year = {2026},
  url = {https://www.ibtimes.co.in/karnataka-suspends-pfizer-cf-depot-licence-fake-drug-case-warns-consumers-over-suspicious-labels-906210},
  note = {Accessed 25 Oct 2026}
}

## Verification log

- melia2024impact: VERIFIED (Crossref DOI 10.3389/fmed.2024.1429872: title, 3 authors, Front. Med. 11:1429872, 2024; full text via Europe PMC confirms 657 -> 13 studies, 2010-2024 window, "categorically fulfill" conclusion, "practical and costly" quote, 2023 German Ozempic case detected via inactive serials). Bib: authors' given names expanded.
- klein2018traceability: VERIFIED (Crossref DOI 10.1007/s40264-018-0678-7: Drug Safety 41(10):911-918, 2018; full text confirms batch-recall quote, FMD "aims to prevent the entry of counterfeit", applies 9 Feb 2019).
- oyetunde2019mobile: VERIFIED (Crossref DOI 10.18549/pharmpract.2019.2.1449: Pharmacy Practice 17(2):1449, 2019; full text confirms n=326, 53%/51%/54%, failures attributed to GSM downtime and power outages). Bib: authors' given names expanded.
- bansal2013anticounterfeit: VERIFIED (Crossref DOI 10.3797/scipharm.1202-03: Sci. Pharm. 81(1):1-13, 2013; Crossref lists only the first author but the PMC3617666 full text lists all four NIPER authors; quotes "verify the supply chain", "confirm the composition", "easily mimicked", "may be re-used or refilled", "provide false assurance" and the NAFDAC MAS/Sproxil/BIOFEM/GSK Ampiclox details all confirmed).
- rasheed2018future: VERIFIED (Crossref DOI 10.3389/fphar.2018.00995: Front. Pharmacol. 9:995, 2018; full text confirms mPedigree 2006, Sproxil 2009, Ilac Takip Sistemi 2010, ">70" Sproxil client companies and mPedigree in 12 countries (both cited to Wall 2017), "tagged genuine or fake", WHO GSMS 2013 "breakthrough"). Note: the paper is internally inconsistent on PharmaSecure (text says 2012, its Table says 2007) and calls mPedigree Nigerian; cite the year as "2012 (per text)".
- zakari2022blockchain: VERIFIED (Crossref DOI 10.7717/peerj-cs.840: PeerJ Comput. Sci. 8:e840, 2022, nine authors as listed; full text confirms 2,185 screened -> 38 papers (2016-2021), immaturity and 1600 tx/s ceiling).
- cdsco2023faqqr: VERIFIED (PDF text extracted: title, Q1 particulars list (i)-(viii; item (iii) absent in source), Q2 1 Aug 2023, Q3 manufacturer's own SOP, Q4 300 brands/voluntary others, Q6, Q7, Q8 all match; document itself carries no date, "21.07.2023" is in the filename, PDF created 25 Jul 2023).
- cdsco2025spuriousguidance: VERIFIED (PDF text extracted: GSR 20(E) 18.01.2022 effective 01.01.2023; GSR 823(E) 17-11-2022 effective 01.08.2023, "to facilitate authentication"; three-step process flow wording matches; no database lookup described; no issue date printed, PDF created 9 Apr 2025 so year 2025 is inferred).
- who2021traceability: VERIFIED (WHO page: title, 2021, ISBN 9789240021327, 52 pp., published 18 Mar 2021; full text via PDF copy confirms "recall execution and vigilance", patient-verification "last resort" / "sole way of determining whether a product is safe", replicated verification services, non-scratchable fake scratch-off panel, full track-and-trace country list, "one in ten"). Page numbers cited in the notes were not re-checked. Bib: month added.
- roy2026qrexpansion: VERIFIED (author S. Roy, 26 Jun 2026, G.S.R. 506(E) dated 22 Jun 2026, Drugs (Seventh Amendment) Rules 2026, classes, 1 Jul 2027 / antimicrobials 1 Jul 2028, draft 16 Oct 2025). News report only; Gazette text not opened.
- newsonair2026qrexpansion: VERIFIED (title, 25 Jun 2026, same categories and dates, wording "counterfeit and substandard medicines").
- pharmexcil2020iveda: VERIFIED (circular number, 25 Jun 2020, iVEDA expansion, CDAC, replaces DAVA, beta live 24 Jun 2020, finished formulations from 1 Jun 2020, XML, serial options, optional aggregation at secondary and tertiary, signed Uday Bhaskar as Director General).
- dgft2024pn39: VERIFIED via TaxGuru reproduction (PN 39/2023-DGFT, 2 Feb 2024, HBP 2023 para 2.76(vi)-(vii), date 01.02.2025, SSI and non-SSI). DGFT original not opened; the earlier slip chronology from SecuringIndustry remains [UNVERIFIED] (site unreachable per researcher).
- fda2026dscsaexemptions: CORRECTED (FDA page confirms exemption until 27 Nov 2027, <=25 FTE assessed as of 27 Nov 2026, survey by 22 Sep 2026, current as of 08/26/2026; but the page does NOT state that the earlier date was 27 Nov 2026 - that comes from the Quarles briefing, so cite trujillo2024dscsa for the prior date).
- trujillo2024dscsa: VERIFIED (authors, 10 Oct 2024, FDA exemptions issued 9 Oct 2024, dates 27 May/27 Aug/27 Nov 2025, small dispensers 27 Nov 2026, stabilization to 27 Nov 2024, condition of initiated connections). Note: briefing describes small dispensers as fewer than 25 pharmacists/technicians while FDA's current page says 25 or fewer; the notes' "26+ FTE" for ordinary dispensers is the researcher's inference.
- ec2026falsifiedmedicines: VERIFIED (Directive 2011/62/EU published 1 Jul 2011, applicable 2 Jan 2013; unique identifier and anti-tampering device; Delegated Reg. 2016/161 from 9 Feb 2019; Q&A v22 listed 10 Jul 2026; page says "often disguised as authentic medicines"). Article-level EMVS details in notes are [UNVERIFIED] (EUR-Lex not opened).
- gs12026ai: VERIFIED (JSON-LD dataset downloaded: AI 01 N2+N14 GTIN; 10 N2+X..20; 11 N2+N6 PROD DATE; 17 N2+N6 USE BY or EXPIRY; 21 N2+X..20 SERIAL; 710 Germany PZN, 714 Portugal AIM, 715 US NDC).
- fda2023dscsapilot: VERIFIED (PDF text extracted: May 2023; established 8 Feb 2019; twenty pilots; MediLedger 2000+ transactions/s and <1 s; "created a test user interface and system performance was evaluated"; "Other data carriers and methods ... (e.g., RFID, blockchain)"; no-endorsement statement). Trade-press "24 companies" claim [UNVERIFIED].
- ohearen2026serialized: VERIFIED (S. O'Hearen, Pharmaceutical Commerce, 24 Mar 2026; serialization built for traceability not security, copyable 2D codes, ">50 countries" serialization). Note: author affiliation 1st Line Partners.
- rao2026karnataka: CORRECTED (IBTimes India, N. Rao, 21 Sep 2026; raid at Bidadi farmhouse 18 Aug 2026; Rs 5.05 crore estimate; 16 licences cancelled, eight suspended; the article's wording is "did not function when verified", not "did not work" as quoted in the notes - use the former). National Herald corroboration was not opened [UNVERIFIED].
- Verification: COMPLETE

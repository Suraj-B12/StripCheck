Status: COMPLETE

- [x] Q1 Field-screening technologies: systematic-review conclusions (cost, sensitivity, skill, usability)
- [x] Q2 Image-based / deep-learning counterfeit medicine or packaging detection
- [x] Q3 Consumer-facing verification / recall-check apps (world and India)
- [x] Q4 Existing tools built on CDSCO NSQ data (2025-2026)
- [x] Q5 What is and is not novel in StripCheck

# Medicine quality screening technologies, verification apps and CDSCO-NSQ tools (positioning StripCheck)

## Q1 Field-screening technologies: what systematic reviews conclude

### Cited Findings

- **Kovacs S, Hawes SE, Maley SN, Mosites E, Wong L, Stergachis A. "Technologies for Detecting Falsified and Substandard Drugs in Low and Middle-Income Countries." PLoS ONE 9(3): e90601, 2014. doi:10.1371/journal.pone.0090601** — [PLoS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0090601) (opened 25 Oct 2026).
  Reviewed 42 technologies (36 commercial, 6 in development), scored 0-8 for LMIC suitability (sample prep, supplies, speed, power, training, portability); 5 low-cost (<= US$10,000, 2013 USD) technologies scored 6-8. Example costs: paper test cards < US$1/test; GPHF-Minilab ~US$3,780; Raman/NIR ~US$50,000; GC-MS / HPLC-MS US$350,000-375,000. Minilab flags only grossly substandard products (<80% API); performance data often poorly reported. Conclusions: "no single technology" serves all needs; "Technologies alone will not solve the problem"; spectroscopic reference libraries need regular updating.
  Relevance: classic baseline - all screening tools test the physical/chemical sample and cost money/training; StripCheck tests nothing chemically but costs nothing and reuses existing lab results (CDSCO NSQ), so it is complementary, not a competitor. The "reference library must be updated" point parallels StripCheck's need to ingest each monthly NSQ list.

- **Vickers S, Bernier M, Zambrzycki S, Fernandez FM, Newton PN, Caillet C. "Field detection devices for screening the quality of medicines: a systematic review." BMJ Global Health 3(4): e000725, 2018. doi:10.1136/bmjgh-2018-000725** — [PMC6135480](https://pmc.ncbi.nlm.nih.gov/articles/PMC6135480/) (opened 25 Oct 2026).
  Searched 4 databases to 30 Apr 2018; 5,718 reports screened, 62 studies included; 41 portable devices across 19 technologies, 27/41 (66%) spectroscopic; prices < US$10 to > US$20,000. Only 6 devices field-tested (GPHF-Minilab, CD3/CD3+, TruScan RM, lateral-flow dipsticks, CBEx, Speedy Breedy); median APIs tested per device = 2 (range 1-20). Selected performance: TruScan RM 100% sens / 99% spec (antimalarials, small sample); CD3/CD3+ field (Ghana) 100% sens but 53-64% spec; Minilab 79% sens when semi-quantitation included, detected 30% of very non-compliant antimalarials in a multicountry survey; aPADs 73.2-80.0% sens. No study addressed cost-effectiveness. Conclusion: "vitally important lack of independent evaluation of the majority of devices, particularly in field settings"; detection of substandard (vs falsified) is much weaker.
  Relevance: motivates a zero-hardware approach; also shows substandard products (the majority of CDSCO NSQ entries) are the hardest for field devices, so lab-confirmed lists are the most reliable signal a consumer can access.

- **Caillet C, Vickers S, Zambrzycki S, Fernandez FM, Vidhamaly V, Boutsamay K, Boupha P, Peerawaranun P, Mukaka M, Newton PN. "A comparative field evaluation of six medicine quality screening devices in Laos." PLoS Neglected Tropical Diseases 15(9): e0009674, 2021. doi:10.1371/journal.pntd.0009674** — [PMC8483322](https://pmc.ncbi.nlm.nih.gov/articles/PMC8483322/) (opened 25 Oct 2026).
  16 Lao medicine inspectors; mock "Evaluation Pharmacy". Misclassification: TruScan RM 0%, MicroPHAZIR RX 0%, NIR-S-G1 7.7%, Progeny 8.3%, 4500a FTIR 9.7%, PAD 37.9% (all false positives). Median time/sample: NIR-S-G1 94 s ... Minilab 2,063 s. Costs (US$): PAD 3; NIR-S-G1 1,199; Minilab 2,510; 4500a 31,067; MicroPHAZIR 47,500; TruScan 62,500. Key user errors: wrong reference library chosen in 27.0% (NIR-S-G1) and 20.0% (TruScan) of scans, 88.9% of TruScan library errors unrecognised; PAD colour misreads 6.9-16.7%. Warns "overconfidence in devices may cause harm by reducing inspectors' investment in visual inspection".
  Relevance: strongest empirical support for StripCheck's verifier/critic + human-confirmation design: the dominant field failure mode is a silent wrong lookup (wrong library), exactly analogous to an OCR misread matching the wrong batch; supports abstention (CANT_VERIFY) and explicit uncertainty rather than over-confident verdicts.

- **World Health Organization. "Report of existing technologies used to screen and detect substandard and falsified medical products." Geneva: WHO, 25 Mar 2025, 36 pp. ISBN 978-92-4-010355-9. Licence CC BY-NC-SA 3.0 IGO** — [WHO publication page](https://www.who.int/publications/i/item/9789240103559) (opened 25 Oct 2026; only the landing page/metadata was read, not the 3.4 MB PDF).
  Landing page states regulators, ministries of health and other stakeholders (NGOs, academia, procurement agencies) play "equally crucial roles" in prevention/detection/response. Specific counts and gaps in the report were NOT verified by me (PDF not opened); a secondary search summary said uptake "remains uneven" - unverified.
  Relevance: official, recent (2025) anchor showing WHO frames SF detection as a multi-stakeholder problem; cite only for existence/scope unless the PDF is read.

- **World Health Organization. "WHO Guidance on the Selection and Use of Technologies to Screen and Detect Substandard/Falsified (SF) Medicines." Working document QAS/26.1004 (draft for public comment), June 2026; comments due 31 Aug 2026.** Read via secondary trade-news summary: ECA Academy / GMP-Compliance.org, "WHO Draft Guidance: Selecting the Right Analytical Screening Technologies for Substandard and Falsified Medicines", news item dated 29 Jul 2026 — [gmp-compliance.org](https://www.gmp-compliance.org/gmp-news/who-draft-guidance-selecting-the-right-analytical-screening-technologies-for-substandard-and-falsified-medicines) (opened 25 Oct 2026; trade news, label as such). Draft PDF mirror: [gmp-navigator.com PDF](https://www.gmp-navigator.com/files/guidemgr/who_qas26_1004guidancescreeningtechnologies.pdf) (not opened by me).
  Scope per the summary: Raman (incl. SORS, SERDS), NIR, MIR, TLC/HPTLC, colorimetric PADs, assessed on API identity/quantitation, impurities, enantiomers, unknown APIs, brand differentiation, DEG/EG contamination, plus time, cost, portability, sample destruction, calibration; briefly XRF, lateral-flow immunoassays, nanosensors; HPLC/MS/XRPD as confirmatory. The summary mentions no digital, image-based or app-based tools.
  Relevance: as of mid-2026 WHO's screening-technology guidance is entirely analytical/chemical; information-based screening (matching a pack against regulators' published test results) is outside its scope - a gap StripCheck fills. Status: still a draft as of the 29 Jul 2026 article; final adoption not verified.

### Takeaway
Two systematic reviews (Kovacs 2014: 42 technologies; Vickers 2018: 41 devices, only 6 field-evaluated) and a 2021 field trial converge: portable chemical screening costs US$3 to >US$60,000 per device, needs training and brand-specific reference libraries, detects falsified products better than substandard ones, and is rarely independently field-validated; its dominant field failure is silent operator error (wrong library 20-27% of scans). None of these tools are aimed at consumers, and WHO's June 2026 draft guidance still covers only analytical technologies.

### Inferences
- StripCheck is not a substitute for chemical screening; it is a zero-cost, consumer-side "information screening" layer that reuses lab results already produced by CDSCO/State labs. Position it as complementary.
- The Laos "wrong library" error is the direct analogue of an OCR misread leading to a wrong batch lookup, which motivates corroboration, human confirmation and abstention.

### Gaps
- No 2023-2026 *systematic* review of field-screening devices was found in my searches (searches 25 Oct 2026); the WHO 2025 report PDF and WHO QAS/26.1004 draft PDF were not opened, so their internal numbers are not cited.

## Q2 Image-based / deep-learning counterfeit medicine or packaging detection

### Cited Findings

- **Yaniv Z, Faruque J, Howe S, Dunn K, Sharlip D, Bond A, Perillan P, Bodenreider O, Ackerman M, Yoo TS. "The National Library of Medicine pill image recognition challenge: An initial report." 2016 IEEE Applied Imagery Pattern Recognition Workshop (AIPR), Washington DC, pp. 1-9, 2016. doi:10.1109/AIPR.2016.8010584** — [NLM LHNCBC abstract page](https://lhncbc.nlm.nih.gov/LHC-publications/pubs/ThenationallibraryofmedicinepillimagerecognitionchallengeAninitialreport.html) (opened 25 Oct 2026).
  Training set 2,000 reference + 5,000 consumer-quality images of 1,000 pills; held-out test of another 1,000 pills. Winners' MAP only 0.27, 0.09, 0.08; correct pill in top-5 for 43%, 12%, 11% of 5,000 queries.
  Relevance: seminal benchmark showing consumer-photo recognition of the *object* is hard and unreliable; and identifying a pill says nothing about quality. StripCheck instead reads printed *text* (batch, dates) and defers judgement to the regulator's lab result.

- **Zakaria Y, Ishidera E, Ishiyama R, Matsui T, Suwa H, Matsuda Y, Yasumoto K. "Counterfeit Medicine Detection by Visual Inspection of Package Design using Multimodal LLMs with Text and Image Prompt Engineering." Proc. 17th Int. Conf. on Intelligent Medicine and Image Processing (IMIP '25), Proc. SPIE vol. 13658, pp. 92-99, 2025. doi:10.1117/12.3071640** — [Lab page (Cocolab, NAIST) with abstract/BibTeX](https://scrapbox.io/cocolab-jp/Counterfeit%20Medicine%20Detection%20by%20Visual%20Inspection%20of%20Package%20Design%20using%20Multimodal%20LLMs%20with%20Text%20and%20Image%20Prompt%20Engineering) (opened 25 Oct 2026; abstract only; dataset size not stated; author "Suwa" given as Hiroiko/Hirohiko inconsistently on the page).
  GPT-4o (cloud) with structured prompts, three image settings (query only; query+genuine reference; query+reference+difference image); binary authentic vs counterfeit packaging accuracy up to 74.6%; users rated explanations highly; needs no counterfeit-specific training data.
  Relevance: closest recent "LLM + explanation" work on medicine packs, but it judges *appearance*, needs a genuine reference image and a paid cloud model, and reaches only ~75%. StripCheck uses a local model, checks a regulator's lab verdict for the exact batch, and keeps the LLM away from the final verdict (verifier with hard rules). Supports StripCheck's emphasis on explanations.

- **Garcia-Cotte H, Mellouli D, Rehman A, Wang L, Stork DG. "Deep neural network-based detection of counterfeit products from smartphone images." arXiv:2410.05969 (v2, 6 Nov 2024), preprint, not peer-reviewed** — [arXiv](https://arxiv.org/abs/2410.05969v2) (opened 25 Oct 2026).
  Pure computer-vision CNN, transfer-trained on few genuine/fake articles; 99.71% accuracy *after 3.06% rejections*; evaluated only on branded garments; medicines mentioned only as a future application.
  Relevance: shows reject-option (abstention) is standard practice to reach high precision in counterfeit vision; supports StripCheck's CANT_VERIFY abstention. Also shows image-only counterfeit detection for medicines remains largely untested.

- **Koponen J, Haataja K, Toivanen P. "Novel Deep Learning Application: Recognizing Inconsistent Characters on Pharmaceutical Packaging." F1000Research 12:427, version 2, 23 Jul 2024 (v1 20 Apr 2023). doi:10.12688/f1000research.131775.2** — [F1000Research](https://f1000research.com/articles/12-427/v2) (opened 25 Oct 2026).
  R-CNN (AlexNet backbone) reading dot-matrix and pressed/ink-marked expiry dates and batch codes on real cardboard pharma packs; vs Tesseract: precision 91.1% vs 38.3%, recall 72.7% vs 61.3%, F1 80.9% vs 47.1%. Only 27 source images from one company; peer review mixed (one "approved with reservations", one "not approved"); no per-character confusion analysis.
  Relevance: direct evidence that batch/expiry codes (dot-matrix, embossed) are hard for generic OCR (Tesseract F1 47%) and that even specialised models miss ~27% of characters; motivates StripCheck's QR-first strategy, enhanced re-read, second reader (VLM), OCR-confusion-aware variant search and human confirmation of doubtful characters. Gap: no published confusion matrix for batch codes on Indian strips was found.

- Not opened (connection refused 25 Oct 2026): "Development of an AI-based Application for Counterfeit Medicine Detection in the Nigerian Drug Market", International Journal of Innovative Computing (UTM), [ijic.utm.my/.../486](https://ijic.utm.my/index.php/ijic/article/view/486). Search snippet only: YOLO-NAS logo detection (mAP 79.3%, P 85.3%, R 75.3%) + Google Vision OCR + spell-checking. Treat as unverified; do not cite numbers unless opened.

### Takeaway
Image-based work splits into (a) object recognition of pills (NLM challenge 2016: winner MAP 0.27, top-5 43%), (b) appearance-based counterfeit packaging classification (GPT-4o up to 74.6% with a genuine reference image, 2025; garment CNN 99.71% only after 3.06% rejections, 2024), and (c) reading printed codes (R-CNN on dot-matrix batch/expiry: precision 91.1%, recall 72.7%, vs Tesseract F1 47%). None of these check a pack against regulator lab-failure lists; appearance-based methods cannot detect substandard (genuine-looking but failing) medicines at all.

### Inferences
- StripCheck uses vision only to *read* (QR, OCR, VLM second reader), not to judge authenticity from appearance; its judgement comes from lab data. This sidesteps the need for genuine reference images and counterfeit training sets.
- Batch/expiry text on strips is the hardest OCR case (dot-matrix, embossed, curved, foil), so multi-reader consensus, confusion-aware search and human confirmation are justified design responses, not over-engineering.
- Reject options (abstention) are the norm for high-precision counterfeit vision, supporting CANT_VERIFY.

### Gaps
- No peer-reviewed, India-specific dataset or benchmark of OCR on blister strips / batch codes was found (searches 25 Oct 2026).
- The Nigerian YOLO-NAS + OCR paper and the MobileDeepPill paper (Zeng et al., MobiSys 2017, doi 10.1145/3081333.3081336, from a search snippet) were not opened; their numbers are not cited.
- No IEEE Xplore / ACM DL systematic review of image-based counterfeit medicine detection was located.

## Q3 Consumer-facing verification and recall-check apps

### Cited Findings

- **Ciapponi A, Donato M, Gulmezoglu AM, Alconada T, Bardach A. "Mobile apps for detecting falsified and substandard drugs: A systematic review." PLoS ONE 16(2): e0246061, 2021. doi:10.1371/journal.pone.0246061 (PROSPERO CRD42020163075; search Jan 2020)** — [PMC7861418](https://pmc.ncbi.nlm.nih.gov/articles/PMC7861418/) (opened 25 Oct 2026).
  25 apps (Apple/Google stores + MedSnap) and 16 websites; most identify pills by imprint/colour/shape, only a few by photo or barcode; 12/25 offered drug-database access; recall lookup or serialization-based authentication not reported. Only one accuracy study for counterfeit detection (MedSnap preprint, 48 samples, reported 100% sens/spec, rated poor quality / high risk of bias). Mean MARS app quality 3.17/5. Conclusion: "a remarkable evidence gap about the accuracy of mobile apps in detecting SCMs"; pill identification cannot confirm a product is substandard/falsified.
  Relevance: establishes that, as of 2020, consumer apps did identification not quality verification, and none checked regulator lab-failure lists; supports StripCheck's claim of a different task (batch vs. NSQ list) and its explicit refusal to claim authenticity.

- **CDSCO. "FAQs on implementation of GSR 823(E) dated 17th November, 2022 with respect to Bar Code or QR Code on top 300 brands." Central Drugs Standard Control Organisation, New Delhi, 21 Jul 2023 (2 pp.)** — [CDSCO PDF](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Final%20FAQs%20on%20QR%20code%2021.07.2023.pdf) (opened and text-extracted 25 Oct 2026).
  G.S.R. 823(E) (17 Nov 2022) amended the Drugs Rules, 1945 (Schedule H2): manufacturers of the 300 listed brands must print a barcode/QR on the primary label (secondary if no space) carrying (i) unique product identification code, (ii) proper/generic name, brand name, (iv) manufacturer name and address, (v) batch number, (vi) manufacturing date, (vii) expiry date, (viii) manufacturing licence number. In force 1 Aug 2023, for batches made on/after that date; the unique ID is chosen by each manufacturer "as per his own Standard Operating Procedure"; voluntary for other brands. The FAQ describes no central government verification database.
  Relevance: explains why StripCheck reads the QR first (it carries the batch number and dates in machine-readable form, eliminating OCR error) but also why OCR is still needed (only 300 brands mandated; most strips have no QR). The QR confirms what the manufacturer printed, not lab quality; StripCheck adds the NSQ check on top.
  News only (not verified against the Gazette): a June 2026 amendment reportedly extended Schedule H2 to all vaccines, antimicrobials, NDPS drugs and anti-cancer drugs — [Onmanorama, 26 Jun 2026](https://www.onmanorama.com/upsc/current-affairs/2026/06/26/qr-codes-now-mandatory-for-vaccines-cancer-drugs.amp.html) (search snippet only, page not opened; verify with the Gazette before citing).

- **GS1 India. "Smart Consumer App" blog post, 28 Nov 2024** — [gs1india.org/blog/smart-consumer-app](https://gs1india.org/blog/smart-consumer-app) (opened 25 Oct 2026).
  The free Android/iOS app scans a GS1 barcode and shows brand-owner-supplied DataKart data: product name, manufacturing date, MRP, net content, manufacturer and consumer-care details, reviews, warranty; the post does not mention recalls, quality test results, or medicine batch-level checks. (Search snippets from other GS1 India pages mention "Spot Authentication" against brand-submitted data and licence validation (FSSAI, AGMARK, BIS) and that only GS1 India "890" barcodes are scannable; those pages were not opened by me.)
  Relevance: the Indian national consumer-scanning app is a product-information/brand-authenticity lookup, data supplied by the brand itself; it does not check independent lab results (NSQ). StripCheck's evidence source (government lab failures) is independent of the manufacturer.

- **U.S. FDA / openFDA. "Drug Recall Enforcement Reports API" (endpoint /drug/enforcement) and its searchable-fields page** — [open.fda.gov/apis/drug/enforcement](https://open.fda.gov/apis/drug/enforcement/); [searchable fields](https://open.fda.gov/apis/drug/enforcement/searchable-fields/) (both opened 25 Oct 2026).
  Recall records from FDA's Recall Enterprise System, 2004-present, updated weekly; fields include `code_info`, `more_code_info`, `product_description`, `reason_for_recall`, `classification`, `status`, `recall_initiation_date`, `recalling_firm` (the field description of `code_info` was not shown on the page I read; it is a free-text string). Caveats stated: not for medical decisions, not for issuing public alerts or tracking recall lifecycle; status not updated after classification; records may be corrected later (e.g., lots added).
  Relevance (openFDA): the closest Western analogue of the NSQ list (regulator-published, machine-readable, lot information in free text); its caveats (later corrections, lots added) support StripCheck's re-check-on-new-list cabinet and its cautious wording. Lot codes in a free-text string also motivate StripCheck's robust batch-matching rather than naive string equality.

- **Mackey TK, Nayyar G. "A review of existing and emerging digital technologies to combat the global trade in fake medicines." Expert Opinion on Drug Safety 16(5): 587-602, 2017. doi:10.1080/14740338.2017.1313227. PMID 28349715** — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=TITLE%3A%22existing%20and%20emerging%20digital%20technologies%20to%20combat%20the%20global%20trade%20in%20fake%20medicines%22&resultType=core&format=json) (abstract opened 25 Oct 2026; full text paywalled, not read).
  Multidisciplinary literature review; groups digital anti-counterfeiting into five categories: mobile, RFID, advanced computational methods, online verification, blockchain; argues for unified platforms combining complementary tools, better information sharing and data collection.
  Relevance: classic taxonomy for Related Work. StripCheck sits in "mobile" + "online verification" + "computational methods" but verifies against regulator *quality-test outcomes* rather than manufacturer-issued codes; it needs no cooperation from manufacturers (unlike SMS scratch-code / serialization schemes).

- **mPedigree SMS scratch-code verification (Ghana/Nigeria)** — news/trade sources only, e.g. [SecuringIndustry.com, "mPedigree and HP start SMS verification roll-out in Nigeria, Ghana"](https://securingindustry.com/pharmaceuticals/mpedigree-and-hp-start-sms-verification-roll-out-in-nigeria-ghana/s40/a771) (search snippet only, page not opened; date not verified). Per snippets: consumer scratches a single-use code and texts it; server replies whether the code is legitimate; funded by participating manufacturers; no independent outcome evaluation found (search 25 Oct 2026). Treat as background only.
  Relevance: archetype of manufacturer-dependent authentication (checks a code, not quality); a genuine-code product can still be NSQ, which is what StripCheck checks.

### Takeaway
Consumer tools check three different things: (1) identity/information (pill identifiers; GS1 India Smart Consumer showing brand-supplied DataKart data), (2) authenticity of a manufacturer-issued code (SMS scratch codes, India's Schedule H2 QR on 300 brands since 1 Aug 2023, whose ID scheme is set by each manufacturer), and (3) regulatory recall/quality status (openFDA recall API, weekly, lot codes in free text). A 2021 systematic review found 25 apps with essentially no accuracy evidence and none checking regulator quality lists. No LLM- or agent-based consumer verification product was found outside the 2026 GitHub projects in Q4.

### Inferences
- StripCheck belongs to category (3) and is the only one of the surveyed tool types whose evidence source is independent of the manufacturer (government lab results).
- Schedule H2 QR codes make the *reading* step easier for covered brands, but they do not tell the consumer anything about quality; StripCheck combines both.
- openFDA's caveats (lots added later, not for medical decisions) argue for re-checks and conservative verdict language.

### Gaps
- GS1 India pages on "Spot Authentication" and licence validation were only seen as search snippets; whether the Smart Consumer app covers pharmaceuticals or Schedule H2 QR codes is not confirmed.
- The June 2026 Schedule H2 expansion is news-only; Gazette notification not verified.
- No independent evaluation of mPedigree/Sproxil-type schemes was found.
- National recall lookups of other regulators (e.g., MHRA, TGA, NAFDAC) were not examined for lack of tool budget.

## Q4 Existing tools built on CDSCO NSQ data (2025-2026)

### Cited Findings

- **Rastogi P. (GitHub user pranshurastogi). "Nazar" (web app, REST API and MCP server). GitHub repository, MIT licence; README states "Live (18 Oct 2026)"; 61 commits, 0 stars at access** — [github.com/pranshurastogi/Nazar](https://github.com/pranshurastogi/Nazar) (opened 25 Oct 2026; README only, code not audited; author full name not confirmed beyond the GitHub handle).
  Checks Indian batch numbers against CDSCO (NSQ portal + alert PDFs), Tamil Nadu, Maharashtra and WHO alerts (README: 21 notices, 1,404 alerts). Inputs: typed batch (strips "B.No."), "Strip Scan" on-device reading of QR/Data Matrix/GS1 plus printed batch line, "Pack Reader" photo extraction of brand, salts, maker, licence, MRP, dates with a confidence score, CSV "shelf sweep" up to 500 batches. Outputs four states: Flagged / Retracted / No alert found / Can't tell; "No alert found" is never shown as green. Exact batch matching plus a "look-alike guard" for OCR confusions (0/O, 1/I/L, 5/S, 8/B) that returns Can't tell with a "Did you mean...?" suggestion, never a flag. Ingest is deterministic first (PDF table geometry, per-regulator templates) with OCR/LLM only for leftovers and a grounding rule that every LLM-extracted value must appear in source text; some rows hand-curated. Cabinet re-checks on each visit, RSS/Atom/JSON feeds, "New since your last visit". Hosted (Vercel, Railway), publishes notices to Arkiv blockchain testnet; LLM provider not named. README does NOT describe cross-field corroboration against the regulator record (beyond a Strip Scan label-mismatch warning) or handling of the same batch number across different products/makers (batch collisions).
  Relevance (Nazar): the closest prior art to StripCheck as of Oct 2026. It already has photo/QR input, OCR-confusion awareness, an abstaining "Can't tell" verdict, grounded LLM-assisted ingest and a cabinet re-check. StripCheck cannot claim any of these as novel individually. Remaining differences: StripCheck resolves look-alikes by asking the user (human-in-the-loop) rather than only suggesting; corroborates product/brand/dates/maker field-by-field to reject batch collisions; uses an agentic planner + verifier/critic with hard rules; runs fully offline on a laptop with a local LLM and no hosted backend; cabinet re-check is triggered by new list arrival rather than by user visit.

- **Swa-hub. "nsq-medicine-tracker." GitHub repository (no description; 1 commit; footer (c) 2026; licence not stated; 0 stars at access)** — [github.com/Swa-hub/nsq-medicine-tracker](https://github.com/Swa-hub/nsq-medicine-tracker) (opened 25 Oct 2026; README only).
  Analytics pipeline, not a consumer checker: parses CDSCO alert PDFs (2014-Jul 2025), NSQ portal JSON/HAR (Aug 2025 on) and a "Samples declared NSQ 2017-2023" PDF; fuzzy matching + union-find to resolve manufacturer-name variants into factories (B-cubed F1 ~0.99 on sample data, real-data accuracy not measured); ranks factories likely to be re-flagged; Streamlit/DuckDB/Power BI. Grounding rule: drops rows whose batch and drug name are not on the page; checks parsed counts against stated totals (PASS/WARN/FAIL report); optional Anthropic-API LLM fallback for table-less pages. No user input of a pack, no OCR of packs, no abstention, no notifications (monthly scheduled run).
  Relevance: prior art for StripCheck's *ingest* agent (validated parsing, grounding, quarantine-like QA, LLM fallback); confirms that NSQ data have messy manufacturer names, which StripCheck's maker-field corroboration must tolerate.

- **shayadmeri-svg. "nsq" ("NSQ Platform"). GitHub repository (3 commits; (c) 2026; licence not stated; 0 stars at access)** — [github.com/shayadmeri-svg/nsq](https://github.com/shayadmeri-svg/nsq) (opened 25 Oct 2026; README only).
  Two Streamlit services over Redis: a CDSCO NSQ analytics dashboard (charts, state choropleth) fed by CDSCO's `publicNsqDrugTable` JSON from cdscoonline.gov.in, and a GMP root-cause "simulator" optionally using Gemini (cloud API) or a heuristic engine. No consumer input (name/batch/photo/QR), no OCR, no abstention, no notifications.
  Relevance: confirms that CDSCO's NSQ table is publicly available as JSON (`publicNsqDrugTable`) and is being reused in 2026, but for dashboards, not per-pack verification.

- **ShaikFayaz042. "medicine-scanner-research." GitHub repository (37 commits; (c) 2026; licence not stated; 1 star at access); linked demo medicheck-live.vercel.app (not opened)** — [github.com/ShaikFayaz042/medicine-scanner-research](https://github.com/ShaikFayaz042/medicine-scanner-research) (opened 25 Oct 2026; README only).
  Research/ingestion pipeline for CDSCO and IPC/PvPI regulatory data (NSQ not explicitly named in README): FastAPI backend, React admin panel, AWS EventBridge/ECS Fargate/S3 scraper, OCR only for scanned PDFs, unspecified "AI-assisted classification". README describes no consumer pack input, matching logic, abstention or notifications.
  Relevance: another cloud ingest pipeline; underlines that StripCheck's distinctive part is the per-pack, offline verification loop, not the scraping.

- **shaurya703. "SafeDose." GitHub repository (2 commits; (c) 2026; licence not stated; 0 stars at access)** — [github.com/shaurya703/safedose](https://github.com/shaurya703/safedose) (opened 25 Oct 2026; README only).
  Patient-facing check of a typed drug name + batch number (`/api/check`) against parsed CDSCO NSQ alert PDFs; shipped dataset = March 2025 alert only (70 flagged batches), each record keeps source URL. Batch: exact match after case/punctuation normalisation; drug name: token overlap + sequence similarity ignoring dosage-form words. Three outcomes: flagged / caution / not found. **Batch collisions handled**: same batch under a different drug name gives "caution" and shows the matched record. "Not found" explicitly not a safety guarantee (directs user to cdsco.gov.in). No photo/OCR/QR (barcode scanning listed as future work), no OCR-confusion handling, no notifications (monthly ingest + subscriber alerts listed as next step). FastAPI/React/SQLite, no LLM.
  Relevance: prior art for name-corroboration and collision-aware output; StripCheck extends this to photo input, multi-field corroboration (dates, maker), OCR confusion variants and abstention.

- **ibnweb3. "RecallOps India." GitHub repository, neatHack 2026 solo hackathon project; 15 commits; MIT (code), CDSCO rows public data; 0 stars at access** — [github.com/ibnweb3/recallops-india](https://github.com/ibnweb3/recallops-india) (opened 25 Oct 2026; README only).
  Distributor-side agent: takes a CDSCO NSQ alert (March 2025 PDF and Jul/Aug 2026 portal rows), finds matching batches in a (synthetic) distributor stock, places digital holds, traces customers, drafts notices; "never sends anything and never releases a hold". Batch normalisation only for case, separators and O/0 (no edit distance). **A hold requires batch + product + at least one corroborating field (manufacturer or dates) with no contradiction**; conflicts/uncertain rows go to human review (12 per round in tests); a failed or "unsure" LLM answer never creates a hold or clearance (abstention). A second alert can reopen earlier "not listed"/"review" decisions (re-check). LLM via OpenAI-compatible gateway for name equivalence and drafting, with a `--no-llm` offline mode; SQLite. Self-reported results on author-written synthetic fixtures: 61/61 and 92/93 correct holds, 0 wrong holds (author notes this is mechanics, not real-world accuracy).
  Relevance: very close to StripCheck's *matching and safety logic* (field corroboration, collision rejection, human review, LLM-cannot-decide rule, re-check on new alert, deterministic fallback), but for distributor inventory rows, not photographed consumer packs, and with no OCR. StripCheck must acknowledge it as prior art for corroboration + abstention + re-check.

- **Blacklisted (blacklisted.co.in). Independent website; operator not named on the page I read; "last updated 10 October 2026"** — [blacklisted.co.in](https://blacklisted.co.in) (opened 25 Oct 2026).
  Searchable record of Indian regulatory actions on medicines, food, cosmetics and AYUSH, each linked to the government document; sources: CDSCO drug/cosmetic alerts, Section 26A gazette bans, FSSAI, BIS, state regulators, courts, WHO. Counts at access: 683 banned medicines, 6,626 failed medicine batches (CDSCO and state labs since Jan 2019), 108 food recalls/orders, 99 cosmetics, 11 AYUSH, 20 supplements. Inputs: name search and typed batch number; no photo/OCR/QR or app mentioned; matching logic and abstention not described. Monthly email digest and RSS feed of failed-batch alerts. Disclaimers: "Not medical advice"; "a notice is not a recall and a recall is not a ban".
  Relevance (Blacklisted): the largest consumer-facing NSQ batch lookup found; shows the typed-batch lookup + notification feed already exists. StripCheck's additions are photo input with OCR error handling, field corroboration and offline operation; its careful wording on notice vs recall vs ban is a useful model for StripCheck's verdict text.

- **FirstScanIt CDSCO tool: NOT FOUND.** Searches on 25 Oct 2026 for "FirstScanIt" (exact) and "FirstScanIt CDSCO NSQ" returned only unrelated "ScanIt" products. Its existence, input method and features could not be verified; do not cite it without a URL from the researcher.
- **App-store apps:** a search for Play Store apps checking batches against CDSCO NSQ lists (25 Oct 2026) found no such app; only news coverage of alerts. No official CDSCO consumer app for batch checks was found. (Absence from a web search is weak evidence; a direct store search was not possible.)

- **News (context for SUSPECTED_FAKE): Roy S. "CDSCO flags Telma AM batch as purportedly spurious, manufacturer denies making it." Medical Dialogues, 24 Sep 2026** — [medicaldialogues.in](https://medicaldialogues.in/news/industry/pharma/cdsco/cdsco-flags-telma-am-batch-as-purportedly-spurious-manufacturer-denies-making-it-179924) (opened 25 Oct 2026; news).
  In the AUG-2026 alert, Telma AM (telmisartan 40 mg + amlodipine 5 mg) batch 18230791 (Mfg Dec 2023, Exp Nov 2026; Delhi state lab sample) was listed with manufacturer "Under Investigation"; the labelled manufacturer said it did not make the batch; CDSCO remark: "The product is purported to be spurious. However, the same is subject to outcome of investigation."
  Relevance: real 2026 example where the printed maker on a pack does NOT match the regulator's maker field (because the pack is counterfeit), showing why field corroboration must treat a maker mismatch on a spurious entry as SUSPECTED_FAKE rather than as a collision to reject. Also shows NSQ/spurious entries are provisional ("subject to outcome of investigation"), supporting cautious verdict wording.

### Comparison table (from READMEs/pages opened 25 Oct 2026; code not audited)

| Tool | Input | OCR-confusion handling | Batch-collision / field corroboration | Abstention / human confirmation | Re-check / notifications | LLM / offline |
|---|---|---|---|---|---|---|
| Nazar | typed batch, on-device QR/DataMatrix/GS1 + printed batch line, photo "Pack Reader", CSV sweep | yes: look-alike guard (0/O, 1/I/L, 5/S, 8/B) gives Can't tell + "Did you mean" | not described (label-mismatch warning only) | Can't tell / No alert found never green; no per-check human confirmation | cabinet re-check on each visit; RSS/Atom/JSON | LLM for grounded ingest + opt-in features; hosted (Vercel/Railway) |
| Blacklisted | name search, typed batch | not described | not described | disclaimers only | monthly email digest, RSS | not described; hosted website |
| SafeDose | typed name + batch (API) | none (no OCR) | yes: batch hit with different drug name -> "caution" | "not found" != safe | none (planned) | no LLM; one month of data |
| RecallOps India | CDSCO alert rows vs distributor stock (no consumer input) | O/0 only | yes: batch + product + >=1 of maker/dates, no contradiction | yes: review queue; unsure LLM never acts | yes: new alert reopens decisions | OpenAI-compatible gateway, `--no-llm` mode |
| Swa-hub nsq-medicine-tracker | none (analytics) | n/a | manufacturer-name resolution (fuzzy + union-find) | grounding drops unsupported rows | monthly scheduled run | optional Anthropic API; local |
| shayadmeri-svg nsq | none (dashboard) | n/a | n/a | n/a | 5-min cache refresh | optional Gemini |
| medicine-scanner-research | none (admin/ingest) | n/a | n/a | n/a | scheduled scraper | unnamed AI; AWS |
| FirstScanIt | not found | - | - | - | - | - |

### Takeaway
By Oct 2026 at least seven public projects reuse CDSCO NSQ data. Consumer batch lookup (Blacklisted, 6,626 failed batches since 2019), photo/QR reading with an OCR look-alike guard and an abstaining "Can't tell" verdict (Nazar), collision-aware name corroboration (SafeDose), and multi-field corroboration with a human review queue and re-check on new alerts (RecallOps India, distributor-side) all already exist. None found combines all of them in a single consumer photo-to-verdict loop that runs fully offline with a local LLM.

### Inferences
- StripCheck's novelty claim must be about the *integration and the safety policy*, not about any single feature.
- Nazar's "never flag on a look-alike" policy differs from StripCheck's "ask the human which character it is"; this is a defensible, testable difference.
- The Telma AM case shows that the corroboration logic must distinguish "collision (different product, same batch)" from "spurious pack claiming a maker that denies it".

### Gaps
- READMEs were read, code was not; claims are as stated by authors. No evaluation on real photographed packs is reported by any project.
- Creation/last-commit dates were not visible for most repositories; only "(c) 2026" footers and Nazar's "Live (18 Oct 2026)".
- App-store listings could not be searched directly.

## Q5 What is and is not novel in StripCheck

### Takeaway
No single StripCheck capability is new on its own. What appears new (as of 25 Oct 2026, among the sources found) is the combination in one consumer, photo-to-verdict, fully offline loop: multi-reader extraction (QR, then OCR, then enhanced re-read, then optional local VLM), confusion-aware batch search, field-by-field corroboration that rejects collisions, a human question when a character is in doubt, and a verifier/critic with hard rules that can abstain. Present it as an integration and safety-policy contribution with an evaluation on real packs. Do not claim it as a first.

### Cited Findings
**Already exists (cite as prior art):**
- Lab-grade and field chemical screening of the physical sample — [Kovacs 2014](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0090601); [Vickers 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6135480/); [Caillet 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8483322/).
- Consumer lookup of a typed batch number against CDSCO/state failed-batch lists, plus a monthly email digest and RSS — [Blacklisted](https://blacklisted.co.in).
- Photo/QR/GS1 reading of a strip's batch line, an OCR look-alike guard (0/O, 1/I/L, 5/S, 8/B), a four-state output with abstention ("Can't tell"), grounded LLM-assisted ingest and a cabinet re-check — [Nazar](https://github.com/pranshurastogi/Nazar).
- Collision-aware corroboration of the drug name on a batch hit ("caution") — [SafeDose](https://github.com/shaurya703/safedose).
- Multi-field corroboration (batch + product + maker or dates), a human review queue, the rule that an "unsure" LLM never acts, re-check when a new alert arrives, and a `--no-llm` deterministic mode, applied to distributor stock — [RecallOps India](https://github.com/ibnweb3/recallops-india).
- Validated NSQ ingest with grounding and stated-total checks — [Swa-hub](https://github.com/Swa-hub/nsq-medicine-tracker).
- LLM explanations of packaging discrepancies (appearance only, cloud GPT-4o) — [Zakaria 2025](https://scrapbox.io/cocolab-jp/Counterfeit%20Medicine%20Detection%20by%20Visual%20Inspection%20of%20Package%20Design%20using%20Multimodal%20LLMs%20with%20Text%20and%20Image%20Prompt%20Engineering).
- Deep-learning OCR of batch/expiry codes on pharma packs — [Koponen 2024](https://f1000research.com/articles/12-427/v2).
- Machine-readable batch data on packs (Schedule H2 QR) — [CDSCO FAQ 2023](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Final%20FAQs%20on%20QR%20code%2021.07.2023.pdf).

**Not found in any source surveyed (candidate contributions, to be stated cautiously):**
1. A human-in-the-loop *character disambiguation* question during a consumer check. Nazar only suggests ("Did you mean"), and RecallOps reviews rows, not characters.
2. Field-by-field corroboration (product, brand, mfg/exp dates, maker) applied to *photographed consumer packs*, with an explicit split between a batch collision (reject), a corroborated hit (FLAGGED) and a spurious-pattern mismatch (SUSPECTED_FAKE). SafeDose corroborates name only, and RecallOps works on structured stock rows.
3. A separate verifier/critic agent that enforces hard rules before any consumer verdict, with an LLM planner/adjudicator and a deterministic fallback, in a LangGraph agent loop.
4. Fully offline, local-only operation on a laptop (local OCR, local LLM/VLM via Ollama, local SQLite index of Jan 2019 to Sep 2026 SUGAM JSON), with no paid or cloud APIs. Every comparable consumer tool found is hosted.
5. An independent second reader (local VLM) cross-checking OCR for the batch field.
6. A cabinet re-check triggered by arrival of a new alert list, for a consumer. Nazar re-checks on visit; RecallOps does this for distributors.

### Inferences
- Recommended framing for the paper: "To our knowledge, unlike existing NSQ lookup tools [Blacklisted, Nazar, SafeDose] and distributor-side agents [RecallOps], StripCheck combines ... offline ...". Hedge with "among the tools we found (searched Oct 2026)". GitHub projects change quickly, so give access dates.
- Evidence motivating the safety design: silent wrong-library errors of 20-27% in field devices ([Caillet 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8483322/)), the weak OCR of batch codes ([Koponen 2024](https://f1000research.com/articles/12-427/v2)), and rejection as standard practice in counterfeit vision ([Garcia-Cotte 2024](https://arxiv.org/abs/2410.05969v2)).
- The strongest empirical contribution StripCheck can add is an evaluation on real photographed Indian strips (OCR error rates, collision rate, abstention rate). None of the surveyed tools reports one.

### Gaps
- Novelty is judged against sources found by web search on 25 Oct 2026. Closed-source apps, app-store listings and the unlocated "FirstScanIt" tool could not be checked.
- I did not verify whether Nazar's code (as opposed to its README) implements more corroboration than its README describes.

## BibTeX

```bibtex
@article{kovacs2014technologies,
  author  = {Kovacs, S. and Hawes, S. E. and Maley, S. N. and Mosites, E. and Wong, L. and Stergachis, A.},
  title   = {Technologies for Detecting Falsified and Substandard Drugs in Low and Middle-Income Countries},
  journal = {PLoS ONE},
  year    = {2014},
  volume  = {9},
  number  = {3},
  pages   = {e90601},
  doi     = {10.1371/journal.pone.0090601}
}

@article{vickers2018field,
  author  = {Vickers, S. and Bernier, M. and Zambrzycki, S. and Fernandez, F. M. and Newton, P. N. and Caillet, C.},
  title   = {Field detection devices for screening the quality of medicines: a systematic review},
  journal = {BMJ Global Health},
  year    = {2018},
  volume  = {3},
  number  = {4},
  pages   = {e000725},
  doi     = {10.1136/bmjgh-2018-000725}
}

@article{caillet2021comparative,
  author  = {Caillet, C. and Vickers, S. and Zambrzycki, S. and Fern{\'a}ndez, F. M. and Vidhamaly, V. and Boutsamay, K. and Boupha, P. and Peerawaranun, P. and Mukaka, M. and Newton, P. N.},
  title   = {A comparative field evaluation of six medicine quality screening devices in {Laos}},
  journal = {PLoS Neglected Tropical Diseases},
  year    = {2021},
  volume  = {15},
  number  = {9},
  pages   = {e0009674},
  doi     = {10.1371/journal.pntd.0009674}
}

@techreport{who2025report,
  author      = {{World Health Organization}},
  title       = {Report of existing technologies used to screen and detect substandard and falsified medical products},
  institution = {World Health Organization},
  address     = {Geneva},
  year        = {2025},
  month       = mar,
  note        = {ISBN 978-92-4-010355-9. Licence CC BY-NC-SA 3.0 IGO},
  url         = {https://www.who.int/publications/i/item/9789240103559}
}

@misc{who2026guidance,
  author = {{World Health Organization}},
  title  = {{WHO} Guidance on the Selection and Use of Technologies to Screen and Detect Substandard/Falsified ({SF}) Medicines},
  year   = {2026},
  month  = jun,
  note   = {Working document QAS/26.1004, draft for public comment (comments due 31 Aug 2026). Read via secondary summary. Accessed 25 Oct 2026},
  url    = {https://www.gmp-navigator.com/files/guidemgr/who_qas26_1004guidancescreeningtechnologies.pdf}
}

@misc{eca2026whodraft,
  author = {{ECA Academy}},
  title  = {{WHO} Draft Guidance: Selecting the Right Analytical Screening Technologies for Substandard and Falsified Medicines},
  year   = {2026},
  note   = {GMP News, 29 Jul 2026 (trade news). Accessed 25 Oct 2026},
  url    = {https://www.gmp-compliance.org/gmp-news/who-draft-guidance-selecting-the-right-analytical-screening-technologies-for-substandard-and-falsified-medicines}
}

@article{ciapponi2021mobile,
  author  = {Ciapponi, A. and Donato, M. and G{\"u}lmezoglu, A. M. and Alconada, T. and Bardach, A.},
  title   = {Mobile apps for detecting falsified and substandard drugs: A systematic review},
  journal = {PLoS ONE},
  year    = {2021},
  volume  = {16},
  number  = {2},
  pages   = {e0246061},
  doi     = {10.1371/journal.pone.0246061}
}

@inproceedings{yaniv2016national,
  author    = {Yaniv, Z. and Faruque, J. and Howe, S. and Dunn, K. and Sharlip, D. and Bond, A. and Perillan, P. and Bodenreider, O. and Ackerman, M. and Yoo, T. S.},
  title     = {The National Library of Medicine pill image recognition challenge: An initial report},
  booktitle = {2016 IEEE Applied Imagery Pattern Recognition Workshop (AIPR)},
  address   = {Washington, DC},
  year      = {2016},
  pages     = {1--9},
  doi       = {10.1109/AIPR.2016.8010584}
}

@inproceedings{zakaria2025counterfeit,
  author    = {Zakaria, Yona and Ishidera, Eiki and Ishiyama, Rui and Matsui, Tomokazu and Suwa, Hirohiko and Matsuda, Yuki and Yasumoto, Keiichi},
  title     = {Counterfeit Medicine Detection by Visual Inspection of Package Design using Multimodal {LLMs} with Text and Image Prompt Engineering},
  booktitle = {17th International Conference on Intelligent Medicine and Image Processing (IMIP 2025)},
  series    = {Proc. SPIE},
  volume    = {13658},
  pages     = {92--99},
  year      = {2025},
  doi       = {10.1117/12.3071640}
}

@misc{garciacotte2024deep,
  author       = {Garcia-Cotte, Hugo and Mellouli, Dorra and Rehman, Abdul and Wang, Li and Stork, David G.},
  title        = {Deep neural network-based detection of counterfeit products from smartphone images},
  year         = {2024},
  eprint       = {2410.05969},
  archivePrefix= {arXiv},
  note         = {Preprint, v2 6 Nov 2024. Accessed 25 Oct 2026},
  url          = {https://arxiv.org/abs/2410.05969}
}

@article{koponen2024novel,
  author  = {Koponen, Jarmo and Haataja, Keijo and Toivanen, Pekka},
  title   = {Novel Deep Learning Application: Recognizing Inconsistent Characters on Pharmaceutical Packaging},
  journal = {F1000Research},
  year    = {2024},
  volume  = {12},
  pages   = {427},
  note    = {Version 2; peer review status: one approved with reservations, one not approved},
  doi     = {10.12688/f1000research.131775.2}
}

@misc{cdsco2023faqqr,
  author = {{Central Drugs Standard Control Organisation}},
  title  = {{FAQs} on implementation of {GSR} 823({E}) dated 17th November, 2022 with respect to Bar Code or {QR} Code on top 300 brands},
  year   = {2023},
  month  = jul,
  note   = {Dated 21 Jul 2023. Accessed 25 Oct 2026},
  url    = {https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadPublic_NoticesFiles/Final%20FAQs%20on%20QR%20code%2021.07.2023.pdf}
}

@misc{gs1india2024smart,
  author = {{GS1 India}},
  title  = {Smart Consumer App},
  year   = {2024},
  note   = {Blog post, 28 Nov 2024. Accessed 25 Oct 2026},
  url    = {https://gs1india.org/blog/smart-consumer-app}
}

@misc{openfda2026enforcement,
  author = {{U.S. Food and Drug Administration}},
  title  = {{openFDA} Drug Recall Enforcement Reports {API}},
  year   = {2026},
  note   = {Endpoint /drug/enforcement and searchable-fields page. Accessed 25 Oct 2026},
  url    = {https://open.fda.gov/apis/drug/enforcement/}
}

@article{mackey2017review,
  author  = {Mackey, T. K. and Nayyar, G.},
  title   = {A review of existing and emerging digital technologies to combat the global trade in fake medicines},
  journal = {Expert Opinion on Drug Safety},
  year    = {2017},
  volume  = {16},
  number  = {5},
  pages   = {587--602},
  doi     = {10.1080/14740338.2017.1313227}
}

@misc{rastogi2026nazar,
  author       = {{pranshurastogi}},
  title        = {Nazar: checking Indian medicine batch numbers against regulator alerts},
  year         = {2026},
  howpublished = {GitHub repository},
  note         = {MIT licence; README states live 18 Oct 2026. Accessed 25 Oct 2026},
  url          = {https://github.com/pranshurastogi/Nazar}
}

@misc{swahub2026nsq,
  author       = {{Swa-hub}},
  title        = {nsq-medicine-tracker},
  year         = {2026},
  howpublished = {GitHub repository},
  note         = {Accessed 25 Oct 2026},
  url          = {https://github.com/Swa-hub/nsq-medicine-tracker}
}

@misc{shayadmeri2026nsq,
  author       = {{shayadmeri-svg}},
  title        = {{NSQ} Platform (nsq)},
  year         = {2026},
  howpublished = {GitHub repository},
  note         = {Accessed 25 Oct 2026},
  url          = {https://github.com/shayadmeri-svg/nsq}
}

@misc{shaikfayaz2026medicine,
  author       = {{ShaikFayaz042}},
  title        = {Medicine Scanner Research},
  year         = {2026},
  howpublished = {GitHub repository},
  note         = {Accessed 25 Oct 2026},
  url          = {https://github.com/ShaikFayaz042/medicine-scanner-research}
}

@misc{shaurya2026safedose,
  author       = {{shaurya703}},
  title        = {{SafeDose}},
  year         = {2026},
  howpublished = {GitHub repository},
  note         = {Accessed 25 Oct 2026},
  url          = {https://github.com/shaurya703/safedose}
}

@misc{ibnweb32026recallops,
  author       = {{ibnweb3}},
  title        = {{RecallOps India}},
  year         = {2026},
  howpublished = {GitHub repository, neatHack 2026 project},
  note         = {MIT licence. Accessed 25 Oct 2026},
  url          = {https://github.com/ibnweb3/recallops-india}
}

@misc{blacklisted2026,
  author = {{Blacklisted}},
  title  = {Blacklisted: independent record of Indian regulatory action on medicines, food, cosmetics and {AYUSH}},
  year   = {2026},
  note   = {Website, last updated 10 Oct 2026. Accessed 25 Oct 2026},
  url    = {https://blacklisted.co.in}
}

@misc{roy2026telma,
  author = {Roy, Susmita},
  title  = {{CDSCO} flags {Telma AM} batch as purportedly spurious, manufacturer denies making it},
  year   = {2026},
  note   = {Medical Dialogues (news), 24 Sep 2026. Accessed 25 Oct 2026},
  url    = {https://medicaldialogues.in/news/industry/pharma/cdsco/cdsco-flags-telma-am-batch-as-purportedly-spurious-manufacturer-denies-making-it-179924}
}
```


## Verification log

Verifier run 25 Oct 2026. One line per source: VERIFIED / CORRECTED / UNVERIFIED.

- kovacs2014technologies: VERIFIED (Crossref DOI 10.1371/journal.pone.0090601; authors, title, PLoS ONE 9(3):e90601, 2014 match; full text confirms 42 technologies (36 commercial, 6 in development), 5 low-cost with score 6-8, <US$1/test paper cards, Minilab US$3,780, Raman/NIR ~US$50,000, GC-MS/HPLC-MS US$350,000-375,000, Minilab <80% API limit, "no single technology", "Technologies alone will not solve the problem"). Full author first names added in .bib.
- vickers2018field: VERIFIED (Crossref DOI 10.1136/bmjgh-2018-000725; BMJ Global Health 3(4):e000725, 2018; full text confirms 5,718 reports screened, 41 devices in 62 articles, 27/41 (66%) spectroscopic, 6 field-tested devices, median 2 APIs (1-20), TruScan 100%/99%, CD3 100% sens / 53-64% spec, Minilab 79%, 30% of 31 very non-compliant samples, aPADs 73.2-80.0%, no cost-effectiveness comment, quoted conclusion).
- caillet2021comparative: VERIFIED (Crossref DOI 10.1371/journal.pntd.0009674; PLOS NTD 15(9):e0009674, 2021; 10 authors match; full text confirms 16 inspectors, misclassification 0%/0%/7.7%/8.3%/9.7%/37.9%, median 94 s (NIR-S-G1) to 2,063 s (Minilab), costs US$3/1,199/2,510/31,067/47,500/62,500, wrong library 27.0% (NIR-S-G1) and 20.0% (TruScan), PAD misreads 6.9%/16.7%, "overconfidence" quote). Note: the paper itself writes "16 of 17 scans (88.9%)" unrecognised for TruScan, which is arithmetically inconsistent (16/17 = 94.1%); cite as "most (16 of 17)" or quote the paper's figure with care.
- who2025report: VERIFIED (WHO landing page opened: exact title, dated 25 March 2025, 36 pages, ISBN 978-92-4-010355-9, CC BY-NC-SA 3.0 IGO, "equally crucial roles" wording present). PDF contents not checked; the secondary "uptake remains uneven" phrase stays [UNVERIFIED].
- who2026guidance: CORRECTED (draft PDF now opened directly, 58 pp.: title, "QAS/26.1004 June 2026" and comment deadline 31 Aug 2026 confirmed; the WHO working-documents page lists it, so the .bib url now points to the official cdn.who.int PDF instead of the gmp-navigator mirror and the note no longer says "read via secondary summary"). Content correction: the draft is not entirely free of digital tools - it mentions smartphone documentation of TLC plates and a mobile app for automatic PAD interpretation, plus visual-inspection checklists; these are aids to analytical tests. No regulator-list / batch-lookup (information-based) screening was found in the text, so the gap claim in Q1 still holds if worded as "no information-based screening".
- eca2026whodraft: VERIFIED (gmp-compliance.org page opened: title, dated 29.07.2026, QAS/26.1004 June 2026, listed technologies, emerging XRF/LFIA/nanosensors, HPLC/MS/XRPD confirmatory, comments until 31 Aug 2026 all match the notes). Trade news.
- yaniv2016national: VERIFIED (Crossref DOI 10.1109/AIPR.2016.8010584: title, 10 authors, AIPR 2016 Washington DC, pp. 1-9; NLM abstract confirms 2,000 reference + 5,000 consumer images of 1,000 pills, separate 1,000-pill test set, MAP 0.27/0.09/0.08, top-5 43%/12%/11% of 5,000 queries). Full author first names added.
- zakaria2025counterfeit: CORRECTED (venue is the "Seventh" International Conference on Intelligent Medicine and Image Processing (IMIP 2025), Kyoto, 28-31 Mar 2025, per Crossref and the SPIE front matter "Volume 13658"; the notes' "17th" copies an error on the authors' lab page. Volume 13658 confirmed via Crossref front matter; pages 92-99 rest on the lab page only (Crossref gives paper 5, i.e. 1365805). Crossref spells Suwa's given name "Hiroiko"; the authors' own BibTeX gives "Hirohiko", kept. Abstract confirms GPT-4o, three image configurations, up to 74.6% accuracy, no counterfeit-specific training data.)
- garciacotte2024deep: VERIFIED (arXiv 2410.05969: title, 5 authors, v1 8 Oct 2024, v2 6 Nov 2024; abstract confirms 99.71% after 3.06% rejections on branded garments, medicines named only as a future category). Preprint.
- koponen2024novel: VERIFIED (Crossref DOI 10.12688/f1000research.131775.2: title, 3 authors, F1000Research 12:427, v2 23 Jul 2024; v1 20 Apr 2023 exists under a different title, "A novel deep learning method for recognizing texts printed with multiple different printing methods"; full text confirms R-CNN with AlexNet, precision 91.1 vs 38.3, recall 72.7 vs 61.3, F1 80.9 vs 47.1, 27 binarized source images (16 dot-matrix, 11 pressed ink-marked) from one Finnish company, reviews "approved with reservations" + "not approved"). Caveat: the paper explicitly excludes text pressed without ink (embossed), stamped or laser-printed, so the Q2 relevance wording "(dot-matrix, embossed)" overstates its scope; it covers dot-matrix and ink-marked codes only.
- edegbe2025development (Nigerian YOLO-NAS paper; key assigned by verifier): CORRECTED from UNVERIFIED (journal site still refused connections, but Crossref DOI 10.11113/ijic.v15n1.486 gives Edegbe G.N., Tone M.C., Int. J. Innovative Computing 15(1):17-27, 27 May 2025, and its abstract confirms YOLO-NAS logo detection with mAP 79.3%, precision 85.3%, recall 75.3%, Google Vision OCR + NER + spell-checking, and an evaluation by 16 undergraduate students). The numbers in Q2 may now be cited; note the "evaluation" is a usability study, not a counterfeit-detection accuracy test.
- zeng2017mobiledeeppill (key assigned by verifier): VERIFIED bibliographically (Crossref/Semantic Scholar/OpenAlex: Zeng X., Cao K., Zhang M., "MobileDeepPill: A Small-Footprint Mobile Deep Learning System for Recognizing Unconstrained Pill Images", MobiSys '17, pp. 56-67, DOI 10.1145/3081333.3081336). No numbers are cited from it in the notes, so none checked.
- ciapponi2021mobile: VERIFIED (Crossref DOI 10.1371/journal.pone.0246061: title, 5 authors, PLOS ONE 16(2):e0246061, 4 Feb 2021; full text confirms PROSPERO CRD42020163075, searches January 2020, 25 apps + 16 websites, 12/25 apps with drug-database access, MedSnap study with 48 samples and 100% sens/spec rated poor / high risk of bias, mean MARS 3.17, "remarkable evidence gap" quote).
- cdsco2023faqqr: VERIFIED (CDSCO PDF opened: 2 pages, title as cited, items (i)-(viii) as listed (the PDF itself skips item (iii)), in force 1 Aug 2023 for batches made on/after that date, unique ID per manufacturer's own SOP, voluntary for other brands, secondary label if primary space inadequate). The 21 Jul 2023 date comes from the file name; PDF metadata shows creation 25 Jul 2023. No mention of a central verification database, as the notes say.
- onmanorama2026qr (key assigned by verifier): VERIFIED as news (article now opened: "QR codes now mandatory for vaccines, cancer drugs", Yearbook Web Desk, 26 Jun 2026; states MoHFW amended the Drugs Rules, 1945 to bring all vaccines, antimicrobials, NDPS-Act drugs and all anti-cancer drugs under Schedule H2, previously top 300 brands). The article gives no G.S.R. number or commencement date; the Gazette notification itself was not located, so cite as news only and keep the claim [UNVERIFIED against the Gazette].
- gs1india2024smart: CORRECTED (page opened: dated 28 Nov 2024; actual post title is "The Smart Consumer's Guide to Informed Purchases"; confirms name, mfg date, MRP, net content, manufacturer/consumer-care info, reviews, warranty; no mention of recalls, quality tests or medicines). The "DataKart/brand-supplied" wording and the GS1 "Spot Authentication" snippets were not seen on this page and stay [UNVERIFIED].
- openfda2026enforcement: VERIFIED (page opened: recall records 2004-present, weekly update, from FDA Recall Enterprise System; "Do not rely on openFDA to make decisions regarding medical care"; not for public alerts or tracking recall lifecycle; status not updated after classification). Free-text nature of code_info not re-checked.
- mackey2017review: VERIFIED bibliographically (Crossref DOI 10.1080/14740338.2017.1313227: Mackey TK, Nayyar G, Expert Opin Drug Saf 16(5):587-602, 2017). Five-category taxonomy rests on the abstract only (not re-read this pass).
- mpedigree_sms (no bib key): UNVERIFIED (securingindustry.com page unreachable, DNS failure; snippet-only, undated). Claims about mPedigree rest on it [UNVERIFIED]; left out of .bib.
- rastogi2026nazar: VERIFIED (README opened: MIT, live 18 Oct 2026, 61 commits, 21 notices/1,404 alerts, four states Flagged/Retracted/No alert found/Can't tell, look-alike guard 0/O, 1/I/L, 5/S, 8/B with "Did you mean", grounded LLM ingest). Author name Pranshu Rastogi shown on page. Collision handling not described there, as the notes say.
- swahub2026nsq: VERIFIED (README: 1 commit, no licence stated, sources 2014-Jul 2025 PDFs, NSQ portal JSON/HAR from Aug 2025, 2017-2023 PDF, B-cubed ~0.99 on sample data only, optional Anthropic-API LLM fallback with grounding drop rule).
- shayadmeri2026nsq: VERIFIED (README: 3 commits, no licence, two Streamlit services over Redis, loads cdscoonline.gov.in/CDSCO/publicNsqDrugTable, optional Gemini).
- shaikfayaz2026medicine: VERIFIED (README: 37 commits, FastAPI, React admin, AWS EventBridge/ECS Fargate/S3, OCR for scanned PDFs, demo link; NSQ and consumer pack input not mentioned).
- shaurya2026safedose: VERIFIED (README: March 2025 alert, 70 flagged batches across 64 medicines, normalised exact batch matching, flagged/caution/not found, caution for batch under different drug name, not-a-guarantee wording, 2 commits, licence not stated). The 64-medicine figure is new.
- ibnweb32026recallops: VERIFIED (README: neatHack 2026 solo, hold needs batch + product + >=1 of manufacturer/dates, no contradiction, --no-llm mode, 61/61 and 92/93 with no wrong holds, name-only baseline 56/61 and 80/93, 15 commits, code MIT, synthetic stock). Fixtures are author-written.
- blacklisted2026: VERIFIED (page opened: last updated 10 Oct 2026; 683 banned medicines; 6,626 failed batches since Jan 2019; typed batch check; monthly digest; RSS; not medical advice). Other category counts and operator name not re-checked.
- roy2026telma: VERIFIED (article opened: Susmita Roy, 24 Sep 2026; Telma AM batch 18230791, Mfg Dec 2023, Exp Nov 2026, manufacturer "Under Investigation", labelled firm denies making it, CDSCO remark quoted, August 2026 alert, DTL Delhi sample).
- firstscanit: UNVERIFIED (researcher found no source; not re-searched; left out of .bib). App-store absence claim stays [UNVERIFIED].
- Verification: COMPLETE

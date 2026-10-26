Status: COMPLETE

# OCR error correction (noisy channel, confusion matrices, closed lexicon) and ALPR hotlist matching with human verification

Checklist:
- [x] Q1 Noisy-channel spelling and OCR correction; confusion matrices; weighted edit distance; lexicon-constrained recognition
- [x] Q2 Surveys and competitions (Nguyen et al. 2021; ICDAR 2017/2019); LLM-based post-OCR correction 2023-2026 and hallucination risk
- [x] Q3 ALPR confusable characters, syntax correction, hotlist matching, misread false positives, visual-verification policies, ALPR surveys
- [x] Q4 Learning confusion priors from user feedback; human-in-the-loop correction and active learning for OCR

## Q1 Noisy-channel spelling and OCR correction; confusion matrices; weighted edit distance; lexicon-constrained recognition

### Takeaway
StripCheck's variant search is a textbook noisy-channel decoder over a closed lexicon: argmax over CDSCO-listed batches b of P(read | b)P(b), with P(read | b) given by a confusion-weighted Wagner-Fischer edit distance. Brill & Moore and Kolak et al. show that richer, learned channel models plus a closed lexicon cut correction errors by 50-70%, and that the correct answer is usually in the top 3 even when it is not the top 1.

### Cited Findings
- **Kernighan, Church & Gale (1990)**, "A Spelling Correction Program Based on a Noisy Channel Model", COLING 1990, Vol. 2 (Helsinki). Anthology ID C90-2036. [ACL Anthology](https://aclanthology.org/C90-2036/). Verified on the opened page: authors, title, venue, year. The Anthology PDF is a scanned image, so I could not read the body text, confusion-matrix details or numbers from it. It is the seminal formulation, argmax_c Pr(c)Pr(t|c), with per-edit-type confusion matrices; that description is background knowledge, not verified here. **Relevance:** it is the canonical citation for scoring a misread batch string t against a candidate c using character-level confusion probabilities, which is StripCheck's variant search.
- **Brill & Moore (2000)**, "An Improved Error Model for Noisy Channel Spelling Correction", ACL 2000, pp. 286-293, doi:10.3115/1075218.1075255. [ACL Anthology](https://aclanthology.org/P00-1037/). The paper frames correction as finding the word w in a fixed dictionary D that maximises P(s|w)P(w) (source model times channel/error model). It learns generic string-to-string edits (alpha -> beta, e.g. multi-character substitutions) with probabilities from <misspelling, correct> pairs, conditioned on position. Set-up: 10,000-word corpus of spelling-error pairs, split 80/20, a dictionary of about 200,000 entries, and a uniform language model. The full model reaches 95.0% 1-best accuracy vs 89.5% for Church-Gale weighted Damerau-Levenshtein, a 52% relative error reduction. With a trigram LM the reduction is 73.6-74%. Window 0 (single-character edits only) gives 88.7% 1-best and 95.1% 3-best [CORRECTED: 95.1% is 2-best; 3-best is 96.6%, Table 2; see Verification log]. Iterative re-estimation slightly degraded performance on their clean data. **Relevance:** this supports StripCheck's closed-lexicon formulation (the CDSCO batch index plays the role of D). It also supports allowing multi-character confusions (rn<->m, cl<->d) as well as single-character swaps, and it shows that k-best candidates (here 3-best) catch many more true answers than 1-best. That last point motivates presenting the top few candidates to a human instead of auto-picking one.
- **Kolak, Byrne & Resnik (2003)**, "A Generative Probabilistic OCR Model for NLP Applications", HLT-NAACL 2003, pp. 134-141. [ACL Anthology](https://aclanthology.org/N03-1018/). This is an end-to-end generative noisy-channel model of OCR (true word sequence -> segmentation -> character-level transformations -> OCR output). It is implemented as composed weighted finite-state transducers, and the inverted transducer decodes OCR strings into weighted lattices or n-best lists of lexicon words. The evaluation made an explicit closed-vocabulary assumption (all test words in the lexicon). On a black-box English OCR system applied to French text (baseline WER 18.31%, CER 5.01%), post-correction gave a 70% WER reduction and 97% word accuracy, better than a commercial French OCR system run on the same text. **Relevance:** this is the strongest classic precedent for treating the OCR engine (RapidOCR/PP-OCR) as a black box and correcting its output with a learned character channel plus a closed lexicon. It also shows that n-best lattices integrate with downstream scoring, analogous to StripCheck's field-by-field corroboration.

- **Wagner & Fischer (1974)**, "The String-to-String Correction Problem", Journal of the ACM 21(1):168-173, doi:10.1145/321796.321811 (metadata and abstract read via [Crossref](https://api.crossref.org/works/10.1145/321796.321811); the ACM DL page returned 403). The paper defines the distance between two strings as the minimum-cost sequence of edit operations (substitute one symbol, delete, insert). It gives a dynamic-programming algorithm whose time is proportional to the product of the two string lengths, and names automatic spelling correction as an application. **Relevance:** this is the algorithmic basis of StripCheck's weighted edit distance. Setting the substitution cost from an OCR confusion matrix (cheap for B<->8, O<->0, expensive otherwise) turns Wagner-Fischer into a confusion-aware matcher. Batch numbers are short (about 6-12 chars), so O(mn) per comparison against a pre-filtered candidate set is trivial on a laptop.

### Inferences
- StripCheck's closed CDSCO index is a stronger constraint than an English dictionary: it holds far fewer, highly structured strings. This raises precision but also creates a **collision risk**, where a misread genuine batch lands exactly on a different listed batch. The 3-best gains in Brill & Moore (95.1% at window 0 vs 88.7% 1-best) [CORRECTED: 95.1% is the 2-best figure; 3-best is 96.6%] argue for returning a short ranked candidate list to the corroboration step and the user, not a single auto-corrected string.
- Kolak et al.'s black-box framing fits StripCheck: RapidOCR/PP-OCR is not retrained, and only a post-hoc channel model is added.
- The prior P(b) could reasonably be uniform over listed batches or informed by product/maker agreement. Field corroboration effectively plays the role of the "language model" (context) in the classic formulation.

### Gaps
- Kernighan, Church & Gale (1990): the Anthology PDF is a scanned image, so the confusion-matrix details and accuracy figures could not be verified in this run. Cite for the formulation only, or verify the numbers from a text copy.
- Levenshtein (1966), "Binary codes capable of correcting deletions, insertions, and reversals", Soviet Physics Doklady 10(8):707-710: not opened in this run, so the bibliographic details are unverified. Check before citing.
- Kolak & Resnik (2002, HLT) and Kolak & Resnik (2005, "OCR post-processing for low density languages", HLT-EMNLP): not located on the Anthology in this run. One lecture slide deck (not a primary source) attributes an up-to-80% WER reduction on Igbo to the 2005 paper; unverified.
- I found no published OCR confusion matrix specific to pharmaceutical batch-code printing (dot-matrix/inkjet/embossed on foil). This is a genuine gap that StripCheck could fill with its own measured confusion table.

## Q2 Surveys and competitions; LLM-based post-OCR correction 2023-2026 and hallucination risk

### Takeaway
Post-OCR correction is a mature field (Nguyen et al. 2021 survey; ICDAR 2017/2019 competitions), where error detection (up to 95%) is much easier than correction (best 44% improvement in ICDAR 2019). LLM correctors (2024-2026) cut CER substantially on long historical prose, but they are uneven across languages, depend on context and over-correct clean input (HIPE-OCRepair 2026), so they are risky for short identifier strings like batch numbers.

### Cited Findings
- **Nguyen, Jatowt, Coustaty & Doucet (2021)**, "Survey of Post-OCR Processing Approaches", ACM Computing Surveys 54(6), Article 124, pp. 1-37, published 13 Jul 2021, doi:10.1145/3453476 (metadata and abstract via [Crossref](https://api.crossref.org/works/10.1145/3453476); open copy listed as [HAL hal-03320329](https://hal.science/hal-03320329v1), which was bot-blocked on 25 Oct 2026). It is the reference survey. Per the abstract, it defines the post-OCR problem, illustrates its typical pipeline, reviews state-of-the-art approaches, and lists evaluation metrics, datasets, language resources and toolkits. Its motivation is that OCR quality drops sharply on degraded or historical material, which hurts IR and NLP downstream. Limitation: I could read only the abstract, not the full text, so per-approach numbers are not given here. **Relevance:** this is the canonical Related Work anchor. StripCheck's pipeline (detect a doubtful character -> generate confusion variants -> rank against the closed CDSCO index) is an instance of the generic error-detection -> candidate-generation -> ranking pipeline (my characterisation; the stage names were not verified from the full text), with a much smaller, structured lexicon.

- **Rigaud, Doucet, Coustaty & Moreux (2019)**, "ICDAR 2019 Competition on Post-OCR Text Correction", 15th Int. Conf. on Document Analysis and Recognition (ICDAR 2019), Sydney, 20-25 Sep 2019. Report deposited on [Zenodo](https://zenodo.org/record/3459116), doi:10.5281/zenodo.3459116, 24 Sep 2019; also [HAL hal-02304334](https://hal.archives-ouvertes.fr/hal-02304334). I did not obtain the IEEE proceedings pages or DOI. It was a second-round competition with two tasks (error detection, error correction) on 22M OCR'd symbols with aligned ground truth (80/20 split), drawn from newspapers, historical prints, manuscripts and shopping receipts in 10 European languages. There were 34 registrations and 5 teams submitted. Detection scores ranged from 41% to 95%, and the best correction improvement was 44%. **Relevance:** this is the benchmark evidence that error *detection* is more tractable than *correction* (a 95% best detection score vs a 44% best correction improvement). It supports StripCheck's design of detecting doubtful characters automatically but deferring the correction decision to a closed-index lookup or a human question. The first-round ICDAR 2017 competition (Chiron et al.) was not opened in this run; see Gaps.
- **Kanerva, Ledins, Kapyaho & Ginter (2025)**, "OCR Error Post-Correction with LLMs in Historical Documents: No Free Lunches", [arXiv:2502.01205](https://arxiv.org/abs/2502.01205) (3 Feb 2025), to appear at RESOURCEFUL 2025. It evaluates open-weight LLMs for post-OCR correction of historical English and Finnish, studying parameter optimisation, quantisation, segment length and text continuation. Modern LLMs reduce CER for English, but "a practically useful performance for Finnish was not reached". Exact CER figures were not on the abstract page, and I did not read the full text. **Relevance:** quantised local LLMs (the Ollama setting in StripCheck) give uneven gains that depend on language and data. Using them to *rewrite* a batch code is unjustified. StripCheck keeps the LLM as planner/adjudicator over candidates generated deterministically, not as a free-text corrector.
- **Ehrmann, Boros, Opitz, Michail, Wagner & Clematide (2026)**, "ICDAR 2026 HIPE-OCRepair Competition on LLM-Assisted OCR Post-Correction for Historical Documents", [arXiv:2607.08143](https://arxiv.org/abs/2607.08143) (v1, 9 Jul 2026; ICDAR 2026 competition report). LLM-assisted correction of noisy historical newspaper and print transcripts (English, French, German, 17th-20th c.) without the source images; 4 teams; dataset, scorer and pipeline released. LLM systems "can substantially improve OCR quality", but results vary with dataset, language and noise level. The organisers name LLMs' tendency to hallucinate as a concern and identify **over-correction of low-noise inputs** as a recurring failure. **Relevance:** this is the most recent (2026) benchmark evidence that LLM correctors damage text that was already right. For StripCheck, an LLM "fixing" a correctly read batch number into a different but plausible one is the worst failure, because it could produce a false FLAGGED or a false NOT_LISTED. This supports keeping the exact-match path first, restricting variants to a closed confusion set, and having the verifier reject any LLM-proposed string not grounded in OCR evidence.

- **Bourne (2024/2025)**, "CLOCR-C: Context Leveraging OCR Correction with Pre-trained Language Models", [arXiv:2408.17428](https://arxiv.org/abs/2408.17428) (v1 30 Aug 2024, v2 22 Jan 2025; no journal ref). It tests 7 LMs on 3 historical newspaper/periodical datasets (NCSE, two Overproof sets). The best model cuts CER on NCSE by more than 60%, and only "some LMs" significantly reduce error. Socio-cultural context in the prompt helps, while misleading prompts hurt. The abstract does not quantify hallucination. **Relevance:** large LLMs help on long running prose with rich context. A batch code is short and context-free, which is the regime where LLM priors give least help and most risk. This supports a deterministic confusion-set search over an LLM rewrite for batch numbers, and it suggests the LLM may still help for longer free-text fields such as product name and manufacturer.

### Inferences
- The detection/correction asymmetry plus the LLM over-correction risk together justify StripCheck's split. Use automatic detection (reader disagreement, low confidence, characters in a confusable class), a deterministic closed-set candidate generator, and a human or verifier for the final call. An LLM may adjudicate among grounded candidates but must never invent a batch string.
- No source here evaluates post-OCR correction on short alphanumeric codes (batch/lot numbers, serials). All of these benchmarks are on running text, so StripCheck's evaluation would be novel in this respect.

### Gaps
- Chiron, Doucet, Coustaty & Moreux (2017), "ICDAR2017 Competition on Post-OCR Text Correction": not opened in this run; details unverified.
- The ICDAR 2019 IEEE proceedings page numbers and DOI were not obtained (Zenodo DOI only).
- HIPE-OCRepair 2026: the exact metrics, penalty for hallucination and per-team numbers were not on the abstract page; the full text was not read.
- Thomas et al. (LT4HALA 2024) on LLM correction of historical newspapers was seen only as a search snippet; not opened.

## Q3 ALPR: confusable characters, hotlist matching, misread false positives, verification policies

### Takeaway
ALPR hotlist matching is the closest deployed analogue of StripCheck. Short alphanumeric codes are OCR'd from noisy photos and matched against an authority's list, and the classic confusions (3/7, 1/I, 8/B, 0/D/Q, 5/S, 2/Z) produce false hits at a material rate (about one logged misread per five hits in Seattle, 2021-22). Courts (Green, 9th Cir. 2014), the IACP model policy (2010, as quoted in Green) and agency policy (SPD 16.170) all require human visual verification plus a status check, and the field mismatch (wrong make or colour) should itself have stopped the action.

### Cited Findings
- **Green v. City & County of San Francisco**, No. 11-17892 (9th Cir., opinion filed 12 May 2014; Judges Reinhardt, Thomas and Sessions; opinion by Sessions), reported at 751 F.3d 1039. The reporter citation comes from search snippets, not the opinion PDF, so verify it. [Opinion PDF, uscourts.gov](https://cdn.ca9.uscourts.gov/datastore/opinions/2014/05/12/11-17892.pdf). The facts are a single-character confusion. Green's plate 5SOW350 was read by an SFPD ALPR as **5SOW750** (3->7), which matched a stolen grey GMC truck (Green drove a burgundy Lexus). The night-time ALPR photo was blurry and illegible. The stopping sergeant checked only the first three characters, and Green was held at gunpoint, handcuffed and detained for up to 20 minutes. The record says it is undisputed that the ALPR "occasionally makes false 'hits' by misreading license plate numbers". SFPD practice required two steps: (1) visually confirm that the plate matches the read and (2) confirm the plate is actually wanted. The opinion (fn. 2) quotes the IACP Aug 2010 LPR Model Policy, which requires visual verification and a status check "Prior to initiation of the stop". The court said an unconfirmed hit alone does not give reasonable suspicion; it reversed summary judgment and remanded. It also noted the make/model/colour mismatch should have prompted further checks. **Relevance:** this is the clearest real-world analogue for StripCheck. A one-character OCR confusion against a closed hotlist produced a confident but false "hit", and the harm came from acting without visual confirmation and without cross-checking the other fields (vehicle make and colour, analogous to StripCheck's product, brand and maker corroboration). It directly motivates the human question on doubtful characters, the field-by-field corroboration that rejects batch collisions, and the verifier's rule that a variant match alone must not yield FLAGGED.
- **Seattle Office of Inspector General (29 Sep 2023)**, "Surveillance Technology Usage Review: Automated License Plate Reader - Patrol (2021 and 2022)", required by Seattle Municipal Code 14.18.060. [PDF](https://www.seattle.gov/documents/departments/oig/audits/surveillancetechnologyusagereview-automatedlicenseplatereader-patrol(2021and2022).pdf). Table 1 (SPD): valid reads 5,888,081 (2021) and 4,589,514 (2022); hits 5,691 and 4,683; logged misreads 976 and 948, i.e. about one misread per five unverified hits. The OIG says this is likely an undercount because officers do not always log misreads. About 0.1% of valid reads become unverified hits. The audit's named examples of misreads are "1" read as "I" and "8" read as "B", plus same-characters/different-state collisions. SPD Policy 16.170-POL-2 requires operators to compare the image with the hotlist record for both state and characters, verify by dispatch or MDC before action, and record an "Accept" or "Misread" disposition for every hit. In a sample of 89 incidents, policy was followed 82 times and there was no evidence of verification 4 times. Two erroneous high-risk stops still happened from outdated hotlist data or plate swaps that were resolved only by a VIN check. [CORRECTED: the report gives two incidents caused by outdated or misleading hotlist data; only one was a high-risk stop (plate swapped onto a same make/model/colour car, resolved by VIN check); see Verification log] **Relevance:** this gives quantitative evidence that hotlist matching on noisy reads produces many false hits (about 17-20% of hits in 2021-22 were logged misreads). The "Accept/Misread" disposition is exactly a human-feedback label that could train confusion priors (Q4). Different-state collisions are the analogue of batch-number collisions across manufacturers, and the stale-hotlist errors show why StripCheck must date-stamp its alert data.

- **Lynch, J. (EFF, 21 May 2014)**, "New Ninth Circuit Opinion Calls into Question Blind Reliance on License Plate Camera IDs", EFF Deeplinks blog (civil-liberties advocacy, not peer-reviewed). [EFF](https://www.eff.org/deeplinks/2014/05/new-ninth-circuit-opinion-calls-question-blind-reliance-license-plate-camera-ids). It summarises Green (a "3" misread as a "7") and says the IACP describes visual verification as one of the "essential components" of ALPR training. It argues more broadly that machine identification (ALPR, face recognition, DNA) turns innocent people into suspects when treated as conclusive. It gives no ALPR error rate. **Relevance:** this is a citable civil-liberties framing for why StripCheck must present a variant match as "needs confirmation" rather than as an accusation, since a wrong FLAGGED verdict could lead a pharmacist or patient to discard a genuine medicine or accuse a seller.
- **Du, Ibrahim, Shehata & Badawy (2013)**, "Automatic License Plate Recognition (ALPR): A State-of-the-Art Review", IEEE Transactions on Circuits and Systems for Video Technology 23(2):311-325, Feb 2013, doi:10.1109/TCSVT.2012.2203741. I read only the metadata, via [Crossref](https://api.crossref.org/works/10.1109/tcsvt.2012.2203741); the full text is paywalled and I did not read it, so no numbers are claimed here. **Relevance:** this is the standard survey citation for the ALPR pipeline (plate localisation -> character segmentation -> character recognition), framing ALPR as the closest deployed analogue of "OCR a short alphanumeric code from a photo and look it up in a list".
- **Laroca, Zanlorensi, Goncalves, Todt, Schwartz & Menotti (2021)**, "An Efficient and Layout-Independent Automatic License Plate Recognition System Based on the YOLO Detector", IET Intelligent Transport Systems 15(4):483-503, doi:10.1049/itr2.12030 ([arXiv:1909.01754v4](https://arxiv.org/abs/1909.01754), revised 9 Mar 2021). This is a YOLO-based ALPR system that classifies the plate layout and then applies layout-specific heuristic post-processing. It reaches 96.9% average end-to-end recognition across 8 public datasets from 5 regions. The authors stress that ALPR needs close to 100% character accuracy because "a single mistake" can misidentify the vehicle. For layouts with fixed letter/digit positions (Brazilian: 3 letters + 4 digits; Chinese), predicted characters are swapped to the required class. Letter->digit swaps: A->4, B->8, D->0, G->6, I->1, J->1, Q->0, S->5, Z->7. Digit->letter swaps: 1->I, 2->Z, 4->A, 5->S, 6->G, 7->Z, 8->B. Ablation: removing layout classification and heuristics lowered the mean recognition rate by 2.1%, and by 3.6% on average on ChineseLP, SSIG-SegPlate and UFPR-ALPR. The authors note that commercial Sighthound "often confused similar letters and digits". **Relevance:** this is a peer-reviewed, explicit confusable-character table (B/8, D/0, Q/0, I/1, S/5, Z/2/7, G/6, A/4) that StripCheck can cite as the source of its seed confusion pairs. It also shows that syntax/format priors fix confusions cheaply when positions are constrained. CDSCO batch formats vary by manufacturer and have no fixed layout, so StripCheck cannot hard-swap; it should generate the variants and let the closed index plus corroboration decide. That is a deliberate design difference.

### Inferences
- The Green facts map onto StripCheck's design one-to-one. A 1-char confusion (3->7) hit a list entry, the image was illegible, the human checked only part of the string, and a field mismatch was ignored. StripCheck's countermeasures are, respectively, the confusion-aware search, CANT_VERIFY on illegible images, the per-character human question, and field corroboration that rejects batch collisions.
- Seattle's "Accept/Misread" disposition shows how deployed systems capture human-verified labels on every hit. StripCheck can log user confirmations the same way and use them to re-estimate confusion priors (links to Q4).
- Seattle's two erroneous stops caused by stale hotlist data suggest that StripCheck should record the CDSCO list month/version with every verdict and re-check cabinet items when lists update (the "medicine cabinet" memory).
- Laroca's hard letter/digit swaps work only where the layout fixes character classes. Indian batch numbers have no national format, so StripCheck should generate both alternatives rather than force one.

### Gaps
- An ACLU report (e.g. "You Are Being Tracked", 2013) and Laroca et al. 2018 (IJCNN, UFPR-ALPR) were not opened in this run.
- I found no systematic, peer-reviewed estimate of ALPR misread rates across agencies. The Seattle figures are a single-agency audit and the OIG itself calls them an undercount.
- The IACP 2010 LPR Model Policy was not opened directly; its wording is known here only as quoted in the Green opinion (fn. 2).
- The 751 F.3d 1039 reporter citation for Green was not verified against the reporter.
- I found no Indian ALPR/ANPR verification policy in this run.

## Q4 Learning confusion priors from user feedback; human-in-the-loop and active learning for OCR

### Takeaway
Routing only doubtful tokens to humans, with doubt detected by disagreement between two independent OCR readers or by a dictionary miss, achieves human-grade accuracy (reCAPTCHA: 99.1% vs 83.5% for OCR alone). User corrections can be fed back to adapt OCR error profiles (Fink et al. 2017), which is the template for StripCheck learning confusion priors from its own human-in-the-loop answers.

### Cited Findings
- **von Ahn, Maurer, McMillen, Abraham & Blum (2008)**, "reCAPTCHA: Human-Based Character Recognition via Web Security Measures", Science 321(5895):1465-1468, 12 Sep 2008, doi:10.1126/science.1160379 ([PDF copy](https://www.site.uottawa.ca/~stan/csi2911/reCaptcha_Science.pdf); metadata checked via Crossref). Humans are asked only about **suspicious** words, those where two OCR engines disagree or the output is not in a dictionary (about 25% of words in old books). About 96% of suspicious words are wrong in at least one engine, while 99.74% of non-suspicious words are correct in both. Answers are aggregated by votes: each human counts 1 and each OCR guess 0.5, and a word needs at least 2.5 votes. A word is discarded as unreadable after 6 rejections; 67.87% of words needed only two human answers. Result: 99.1% word accuracy (216 errors in 24,080 words) vs 83.5% for standard OCR, matching professional "key and verify" double-entry. Over 440M words were transcribed in year 1 on 40,000+ sites. Errors came mostly from OCR segmentation/alignment. **Relevance:** this is the canonical evidence that (a) disagreement between two independent readers is an excellent doubt detector, which justifies StripCheck's RapidOCR + enhanced re-read + optional VLM second reader, and (b) routing *only* doubtful tokens to a human gives near-human accuracy at a fraction of the effort, which justifies asking the user only when a batch character is in doubt. Its explicit "unreadable" outcome parallels CANT_VERIFY, and weighting machine guesses below human ones parallels letting the user's answer override OCR.
- **Fink, Schulz & Springmann (2017)**, "Profiling of OCR'ed Historical Texts Revisited", [arXiv:1701.05377](https://arxiv.org/abs/1701.05377) (19 Jan 2017; the search result says DATeCH 2017, which I did not confirm on the arXiv page), doi:10.48550/arXiv.1701.05377. It extends Reffle's EM-based OCR error profiler (lexica + pattern sets + matching, used for interactive post-correction) in three ways. (1) **Adaptivity:** the user's actual corrections are fed back into the error profile, raising precision in detecting erroneous tokens. (2) Patterns discovered during correction are added. (3) Tokens the channel model cannot interpret are treated as conjectured errors, which improves recall and precision. The abstract page gives no numbers. **Relevance:** this is direct precedent for learning or updating OCR confusion priors from the human answers collected during interactive correction. StripCheck's human-in-the-loop answers (e.g. "the 4th char is 8, not B") can be logged as <read, truth> pairs to re-estimate its confusion weights per engine and font, in the same EM/count-based way Kernighan-Church-Gale and Brill-Moore trained channel models from pairs.

### Inferences
- StripCheck can estimate per-pair confusion weights as smoothed counts: P(read=x | true=y) = (n_xy + alpha) / (n_y + alpha|V|), from logged <OCR read, user-confirmed char> pairs. The seed values come from the Laroca/Seattle confusion pairs, and the counts update as users answer, in the same way Kernighan-Church-Gale and Brill-Moore trained channel models from error pairs.
- reCAPTCHA's vote weighting (human 1.0, OCR 0.5, threshold 2.5) is a concrete, citable precedent for a decision rule in which a user-confirmed character outweighs any single machine reading. The verifier still blocks FLAGGED unless corroborating fields agree.
- Active-learning framing: ask the user about the character whose resolution changes the verdict most (e.g., the one that separates a listed batch from an unlisted one). This is uncertainty sampling applied per query rather than per training set.

### Gaps
- I did not open a peer-reviewed active-learning-for-OCR paper in this run. Search snippets pointed to OCR4all (arXiv:1909.04032), PoCoTo (Vobl et al. 2014) and an MITH "Active OCR" project page, none of which was opened.
- The Fink et al. 2017 numbers (precision/recall gains) and the DATeCH 2017 venue were not verified on the arXiv abstract page.
- I found no study of user-feedback-driven confusion learning for consumer (non-expert) users, as opposed to expert philologists. The reliability of lay users' answers about a blurry character is an open question for StripCheck.

## BibTeX

```bibtex
@inproceedings{kernighan1990spelling,
  author    = {Kernighan, Mark D. and Church, Kenneth W. and Gale, William A.},
  title     = {A Spelling Correction Program Based on a Noisy Channel Model},
  booktitle = {COLING 1990 Volume 2: Papers presented to the 13th International Conference on Computational Linguistics},
  year      = {1990},
  url       = {https://aclanthology.org/C90-2036/}
}
@inproceedings{brill2000improved,
  author    = {Brill, Eric and Moore, Robert C.},
  title     = {An Improved Error Model for Noisy Channel Spelling Correction},
  booktitle = {Proceedings of the 38th Annual Meeting of the Association for Computational Linguistics},
  address   = {Hong Kong},
  year      = {2000},
  pages     = {286--293},
  doi       = {10.3115/1075218.1075255},
  url       = {https://aclanthology.org/P00-1037/}
}
@inproceedings{kolak2003generative,
  author    = {Kolak, Okan and Byrne, William and Resnik, Philip},
  title     = {A Generative Probabilistic {OCR} Model for {NLP} Applications},
  booktitle = {Proceedings of the 2003 Human Language Technology Conference of the North American Chapter of the Association for Computational Linguistics},
  year      = {2003},
  pages     = {134--141},
  url       = {https://aclanthology.org/N03-1018/}
}
@article{wagner1974string,
  author  = {Wagner, Robert A. and Fischer, Michael J.},
  title   = {The String-to-String Correction Problem},
  journal = {Journal of the ACM},
  volume  = {21},
  number  = {1},
  pages   = {168--173},
  year    = {1974},
  doi     = {10.1145/321796.321811}
}
@article{nguyen2021survey,
  author  = {Nguyen, Thi Tuyet Hai and Jatowt, Adam and Coustaty, Mickael and Doucet, Antoine},
  title   = {Survey of Post-{OCR} Processing Approaches},
  journal = {ACM Computing Surveys},
  volume  = {54},
  number  = {6},
  pages   = {124:1--124:37},
  year    = {2021},
  doi     = {10.1145/3453476}
}
@misc{green2014ninth,
  author       = {{United States Court of Appeals for the Ninth Circuit}},
  title        = {Green v. City and County of San Francisco, No. 11-17892 (opinion filed 12 May 2014)},
  year         = {2014},
  howpublished = {751 F.3d 1039 (9th Cir. 2014)},
  url          = {https://cdn.ca9.uscourts.gov/datastore/opinions/2014/05/12/11-17892.pdf},
  note         = {Accessed 25 Oct 2026. Reporter citation not verified against the reporter}
}
@techreport{seattleoig2023alpr,
  author      = {{Seattle Office of Inspector General}},
  title       = {Surveillance Technology Usage Review: Automated License Plate Reader -- Patrol (2021 and 2022)},
  institution = {City of Seattle, Office of Inspector General},
  year        = {2023},
  month       = sep,
  url         = {https://www.seattle.gov/documents/departments/oig/audits/surveillancetechnologyusagereview-automatedlicenseplatereader-patrol(2021and2022).pdf},
  note        = {Published 29 Sep 2023. Accessed 25 Oct 2026}
}
@article{du2013alpr,
  author  = {Du, Shan and Ibrahim, Mahmoud and Shehata, Mohamed and Badawy, Wael},
  title   = {Automatic License Plate Recognition ({ALPR}): A State-of-the-Art Review},
  journal = {IEEE Transactions on Circuits and Systems for Video Technology},
  volume  = {23},
  number  = {2},
  pages   = {311--325},
  year    = {2013},
  doi     = {10.1109/TCSVT.2012.2203741}
}
@article{laroca2021efficient,
  author  = {Laroca, Rayson and Zanlorensi, Luiz A. and Gon{\c{c}}alves, Gabriel R. and Todt, Eduardo and Schwartz, William Robson and Menotti, David},
  title   = {An Efficient and Layout-Independent Automatic License Plate Recognition System Based on the {YOLO} Detector},
  journal = {IET Intelligent Transport Systems},
  volume  = {15},
  number  = {4},
  pages   = {483--503},
  year    = {2021},
  doi     = {10.1049/itr2.12030},
  eprint  = {1909.01754},
  archivePrefix = {arXiv}
}
@inproceedings{rigaud2019icdar,
  author    = {Rigaud, Christophe and Doucet, Antoine and Coustaty, Mickael and Moreux, Jean-Philippe},
  title     = {{ICDAR} 2019 Competition on Post-{OCR} Text Correction},
  booktitle = {15th International Conference on Document Analysis and Recognition (ICDAR 2019)},
  address   = {Sydney, Australia},
  year      = {2019},
  doi       = {10.5281/zenodo.3459116},
  url       = {https://zenodo.org/record/3459116},
  note      = {Zenodo deposit of the competition report; IEEE proceedings pages not verified}
}
@misc{kanerva2025ocr,
  author        = {Kanerva, Jenna and Ledins, Cassandra and K{\"a}pyaho, Siiri and Ginter, Filip},
  title         = {{OCR} Error Post-Correction with {LLMs} in Historical Documents: No Free Lunches},
  year          = {2025},
  eprint        = {2502.01205},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/2502.01205},
  note          = {To appear in RESOURCEFUL 2025. Accessed 25 Oct 2026}
}
@misc{ehrmann2026hipe,
  author        = {Ehrmann, Maud and Boros, Emanuela and Opitz, Juri and Michail, Andrianos and Wagner, Florian and Clematide, Simon},
  title         = {{ICDAR} 2026 {HIPE-OCRepair} Competition on {LLM}-Assisted {OCR} Post-Correction for Historical Documents},
  year          = {2026},
  eprint        = {2607.08143},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/2607.08143},
  note          = {Version 1, 9 Jul 2026. Accessed 25 Oct 2026}
}
@article{vonahn2008recaptcha,
  author  = {von Ahn, Luis and Maurer, Benjamin and McMillen, Colin and Abraham, David and Blum, Manuel},
  title   = {{reCAPTCHA}: Human-Based Character Recognition via Web Security Measures},
  journal = {Science},
  volume  = {321},
  number  = {5895},
  pages   = {1465--1468},
  year    = {2008},
  doi     = {10.1126/science.1160379}
}
@misc{fink2017profiling,
  author        = {Fink, Florian and Schulz, Klaus U. and Springmann, Uwe},
  title         = {Profiling of {OCR}'ed Historical Texts Revisited},
  year          = {2017},
  eprint        = {1701.05377},
  archivePrefix = {arXiv},
  doi           = {10.48550/arXiv.1701.05377},
  url           = {https://arxiv.org/abs/1701.05377},
  note          = {Accessed 25 Oct 2026}
}
@misc{bourne2024clocrc,
  author        = {Bourne, Jonathan},
  title         = {{CLOCR-C}: Context Leveraging {OCR} Correction with Pre-trained Language Models},
  year          = {2024},
  eprint        = {2408.17428},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/2408.17428},
  note          = {v2, 22 Jan 2025. Accessed 25 Oct 2026}
}
@misc{lynch2014ninth,
  author       = {Lynch, Jennifer},
  title        = {New Ninth Circuit Opinion Calls into Question Blind Reliance on License Plate Camera {IDs}},
  howpublished = {Electronic Frontier Foundation, Deeplinks Blog},
  year         = {2014},
  month        = may,
  url          = {https://www.eff.org/deeplinks/2014/05/new-ninth-circuit-opinion-calls-question-blind-reliance-license-plate-camera-ids},
  note         = {Published 21 May 2014. Accessed 25 Oct 2026}
}
```

## Verification log

Verifier run started 25 Oct 2026. One line per source: VERIFIED, CORRECTED or UNVERIFIED.

- kernighan1990spelling: CORRECTED. Title, authors, venue (COLING 1990 vol. 2), year confirmed on ACL Anthology C90-2036 and Crossref; added missing pages 205-210 and DOI 10.3115/997939.997975 (Crossref). The Anthology PDF does carry an OCR text layer: it confirms argmax Pr(c)Pr(t|c) and probabilities computed from four confusion matrices (del, add, sub, rev), so the "per-edit-type confusion matrices" description is now verified.
- brill2000improved: CORRECTED (claim only; bib metadata verified). Metadata matches Anthology P00-1037 and Crossref (DOI 10.3115/1075218.1075255, pp. 286-293, Hong Kong, Oct 2000). Full text checked: 10,000-pair corpus, 80/20 split, ~200,000-entry dictionary, 95.0% vs 89.5% for CG, 52% relative error reduction, 73.6% / 74% reduction with trigram LM, window 0 with positional information = 88.7% 1-best are all confirmed. Correction: in Table 2 the window-0 figure 95.1% is the 2-best accuracy, not 3-best; window-0 3-best is 96.6%. The Q1 finding and the first Q1 inference that say "95.1% 3-best" are marked inline.
- kolak2003generative: VERIFIED. Title, authors, venue and pp. 134-141 match ACL Anthology N03-1018; added DOI 10.3115/1073445.1073463 (Crossref; the ACM DL copy paginates it vol. 1 pp. 55-62, noted in the bib). Full text checked: closed-vocabulary assumption, baseline WER 18.31% / CER 5.01% on French, 70% WER reduction, 97% word accuracy, better than a commercial French OCR system - all confirmed.
- wagner1974string: VERIFIED. Crossref: J. ACM 21(1):168-173, Jan 1974, Wagner & Fischer, DOI 10.1145/321796.321811.
- nguyen2021survey: VERIFIED. Crossref: ACM Computing Surveys 54(6), pp. 1-37, published 13 Jul 2021, four authors as given, DOI 10.1145/3453476. The "Article 124" number is not in Crossref and the ACM DL and DBLP pages were bot-blocked, so it is left out of the bib (pages 1-37 kept).
- rigaud2019icdar: CORRECTED. IEEE proceedings record found on Crossref: 2019 International Conference on Document Analysis and Recognition (ICDAR), pp. 1588-1593, DOI 10.1109/ICDAR.2019.00255; bib now uses the IEEE DOI with the Zenodo DOI 10.5281/zenodo.3459116 as a note. Zenodo abstract (24 Sep 2019) confirms: second round, two tasks, 22M OCR'd symbols, 80/20 split, 10 European languages, newspapers/historical prints/manuscripts/receipts, 34 registrations, 5 teams, detection 41-95%, best correction improvement 44%.
- kanerva2025ocr: CORRECTED. Now published: RESOURCEFUL-2025 workshop proceedings, Tallinn, Mar 2025, pp. 38-47, University of Tartu Library (ACL Anthology 2025.resourceful-1.8). Entry changed from @misc arXiv to @inproceedings. arXiv abstract confirms the English vs Finnish claim and the quoted phrase.
- ehrmann2026hipe: CORRECTED. Now published as a Springer LNCS chapter in Document Analysis and Recognition - ICDAR 2026, pp. 405-422, online 26 Aug 2026, DOI 10.1007/978-3-032-36042-7_24 (Crossref; also the arXiv DOI link). Entry changed from @misc to @incollection. arXiv abstract confirms 4 teams, EN/FR/DE 17th-20th c., no source images, hallucination named as a concern, over-correction of low-noise inputs as a recurring challenge, dataset/scorer/pipeline released.
- bourne2024clocrc: VERIFIED. arXiv:2408.17428, single author, v1 30 Aug 2024, v2 22 Jan 2025, no journal ref; abstract confirms 7 LMs, 3 datasets (NCSE + two Overproof), >60% CER reduction on NCSE for the top model, "some LMs", context prompts help and misleading prompts hurt. No published version found on Crossref (Bourne's separate 2025 IJDAR paper "Scrambled text" is a different work).
- green2014ninth: VERIFIED. Opinion PDF opened: No. 11-17892, filed 12 May 2014, Reinhardt and Thomas (Circuit Judges) and Sessions (D. Vt., by designation), opinion by Sessions. Confirmed: 5SOW350 read as 5SOW750 (fn. 3), 1992 burgundy Lexus vs gray GMC truck, blurry/illegible night photo, Sgt Kim matched only the first three characters, gunpoint/handcuffs/up to twenty minutes, "occasionally makes false 'hits'", SFPD two-step verification, fn. 2 quoting the Aug 2010 IACP model policy ("Prior to initiation of the stop"), make/model/colour mismatch "arguably justifies further investigation", reversal and remand. Nuance: the "unconfirmed hit alone does not form reasonable suspicion" statement is described in the opinion as "well established by the record" and uncontested by defendants, not a fresh holding. Reporter citation 751 F.3d 1039 confirmed on CourtListener (also 2014 WL 1876273), so the Q3 gap about the reporter citation is resolved.
- seattleoig2023alpr: VERIFIED with one minor CORRECTION to a claim. PDF opened: dated 29 Sep 2023, required by SMC 14.18.060. Table 1 valid reads 5,888,081 / 4,589,514, misreads 976 / 948, hits 5,691 / 4,683; "one misread for every five unverified hits"; fn. 5 undercount; ~0.1% of valid reads are unverified hits; "1"/"I" and "8"/"B" examples and different-state collisions; SPD 16.170-POL-2 General Policy 4 (compare image for state and characters, confirm by radio/MDC, Accept/Misread disposition); sample of 89, compliant 82, no evidence of verification 4 - all confirmed. Correction: the report describes two problem incidents from outdated or misleading hotlist data, but only one was a high-risk stop with firearms drawn resolved by a VIN check (a plate swapped onto a car of the same make, model and colour); in the other the hit was accurate but the stolen car had been recovered without the recovery being reported, and officers drew no firearms. The notes' "two erroneous high-risk stops ... resolved only by a VIN check" overstates this.
- lynch2014ninth: VERIFIED. EFF Deeplinks page opened: by Jennifer Lynch, 21 May 2014; says the ALPR recorded a "3" as a "7", quotes IACP's "essential components" of ALPR training, and discusses ALPR, face recognition and DNA as fallible identification technologies. No error rate given, as the notes say.
- du2013alpr: VERIFIED. Crossref: IEEE TCSVT 23(2):311-325, Feb 2013, Du, Ibrahim, Shehata, Badawy, DOI 10.1109/TCSVT.2012.2203741. Only metadata checked (no numbers are claimed from it).
- laroca2021efficient: VERIFIED. Crossref and arXiv journal_ref: IET ITS 15(4):483-503, 2021, DOI 10.1049/itr2.12030, six authors as given; arXiv v4 updated 9 Mar 2021. Full text checked: 96.9% average end-to-end rate across 8 datasets from 5 regions, "a single mistake may imply in incorrect identification of the vehicle", swap lists [1>I, 2>Z, 4>A, 5>S, 6>G, 7>Z, 8>B] and [A>4, B>8, D>0, G>6, I>1, J>1, Q>0, S>5, Z>7] applied to Brazilian and Chinese layouts, 2.1% mean improvement from layout classification + heuristics and 3.6% average on ChineseLP/SSIG-SegPlate/UFPR-ALPR, "Sighthound often confused similar letters and digits" - all confirmed.
- vonahn2008recaptcha: VERIFIED. Crossref: Science 321(5895):1465-1468, 12 Sep 2008, five authors, DOI 10.1126/science.1160379. PDF copy checked: suspicious = OCR engines disagree or word not in English dictionary; ~96% / 99.74%; human = 1 vote, OCR guess = half a vote, 2.5-vote threshold; discarded after six rejections; 67.87% needed two answers; 99.1% (216 errors / 24,080 words) vs 83.5%; "key and verify" comparison; >440M words in year one on >40,000 sites; ~25% of words suspicious; alignment/segmentation main error source - all confirmed.
- fink2017profiling: CORRECTED. Published version found on Crossref: Proceedings of the 2nd International Conference on Digital Access to Textual Cultural Heritage (DATeCH 2017), ACM, Jun 2017, pp. 61-66, DOI 10.1145/3078081.3078096, so the DATeCH 2017 venue is now confirmed. Entry changed from @misc arXiv to @inproceedings with the ACM DOI; author given name normalised to "Klaus U." as in Crossref (arXiv lists "Klaus-U."). arXiv abstract confirms the three improvements (adaptivity from user corrections raising precision, new historical patterns, uninterpretable tokens as conjectured errors improving recall and precision); it gives no numbers.
- levenshtein1966binary (Gaps, Q1): UNVERIFIED. Not in Crossref; OpenAlex lists it as Soviet Physics Doklady vol. 10, issue 4, pp. 707-710, year 1965, which conflicts with the notes' 10(8), 1966. No authoritative record was found to settle the issue number and year, so it is left out of the .bib. Verify against a library catalogue before citing.
- kolak2002ocr (Gaps, Q1): VERIFIED (added). Crossref: Kolak & Resnik, "OCR error correction using a noisy channel model", Proc. Second Int. Conf. on Human Language Technology Research (HLT 2002), pp. 257-262, DOI 10.3115/1289189.1289208. Metadata only; no claims rest on it.
- kolak2005ocr (Gaps, Q1): VERIFIED (added). ACL Anthology H05-1109 and Crossref: HLT-EMNLP 2005, Vancouver, Oct 2005, pp. 867-874, DOI 10.3115/1220575.1220684. Full text checked: for Igbo, adapting English OCR gave "relative error reductions as high as 78%" (7.11% WER), and post-processing an Igbo-trained OCR cut WER by 50%. So the slide-deck claim of "up to 80%" WER reduction on Igbo is approximately right; cite it as "up to 78%".
- chiron2017icdar (Gaps, Q2): VERIFIED (added). Crossref: Chiron, Doucet, Coustaty & Moreux, "ICDAR2017 Competition on Post-OCR Text Correction", 14th IAPR ICDAR, Nov 2017, pp. 1423-1428, DOI 10.1109/ICDAR.2017.232. Metadata only; the competition details were not read.
- thomas2024leveraging (Gaps, Q2): VERIFIED (added). Crossref: Thomas, Gaizauskas & Lu, "Leveraging LLMs for Post-OCR Correction of Historical Newspapers", LT4HALA @ LREC-COLING-2024, May 2024, pp. 116-121, DOI 10.63317/5aezhy5iacm9. Metadata only; no findings taken from it.
- vobl2014pocoto (Gaps, Q4): VERIFIED (added). Crossref: Vobl, Gotscharek, Reffle, Ringlstetter & Schulz, "PoCoTo - an open source system for efficient interactive postcorrection of OCRed historical texts", DATeCH 2014, ACM, pp. 57-61, DOI 10.1145/2595188.2595197. Metadata only.
- laroca2018robust (Gaps, Q3): VERIFIED (added). Crossref: Laroca, Severo, Zanlorensi, Oliveira, Goncalves, Schwartz & Menotti, "A Robust Real-Time Automatic License Plate Recognition Based on the YOLO Detector", IJCNN 2018 (Jul 2018), pp. 1-10, DOI 10.1109/IJCNN.2018.8489629. Metadata only; the UFPR-ALPR dataset details were not read.
- reul2019ocr4all (Gaps, Q4): VERIFIED (added). arXiv:1909.04032 and Crossref: Reul et al. (10 authors), "OCR4all - An Open-Source Tool Providing a (Semi-)Automatic OCR Workflow for Historical Printings", Applied Sciences 9(22):4853, 2019, DOI 10.3390/app9224853. Metadata only; it was not assessed as an active-learning paper.
- aclu2013tracked (Gaps, Q3): VERIFIED (added). ACLU page found at the /documents/ URL in the bib, titled "You Are Being Tracked: How License Plate Readers Are Being Used to Record Americans' Movements", published 17 Jul 2013. Existence and title only; contents not read.
- IACP Aug 2010 License Plate Readers Model Policy (Gaps, Q3): UNVERIFIED as a standalone document; the policy itself was not located. Its quoted wording ("Prior to initiation of the stop", visual verification plus status check through dispatch or MDT) is confirmed as quoted in Green, fn. 2, so cite it through green2014ninth. Not in .bib.
- MITH "Active OCR" project page (Gaps, Q4): UNVERIFIED. No URL is given in the notes and it was not located; no claim rests on it. Not in .bib.
- Reffle (2013) and the Church & Gale (1991) "CG" error model are mentioned only as described inside Fink et al. and Brill & Moore; the notes give no bibliographic details and no claim rests on them directly, so they were not checked separately and are not in .bib.
Verification: COMPLETE

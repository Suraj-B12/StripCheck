Status: COMPLETE

# Record linkage / entity resolution as a framework for StripCheck batch matching

Checklist:
- [x] Q1 Classic theory: Fellegi-Sunter 1969; Newcombe et al. 1959; Winkler (Jaro-Winkler 1990; EM); Christen 2012 book; Elmagarmid et al. 2007 TKDE
- [x] Q2 Blocking and indexing surveys (Christen 2012 TKDE; Papadakis et al. 2020 ACM CSUR)
- [x] Q3 Clerical review and human-in-the-loop ER (CrowdER 2012; active-learning ER)
- [x] Q4 String similarity for names (Levenshtein, Jaro-Winkler, token-based; Cohen, Ravikumar and Fienberg 2003)
- [x] Q5 LLM-based entity matching (Narayan et al. 2022; Peeters et al. 2023/2025) and drug-name matching (brand vs generic, RxNorm, Indian brands)

## Q1 Classic theory (Fellegi-Sunter, Newcombe, Winkler, Christen book, Elmagarmid survey)

### Takeaway
Record linkage theory gives StripCheck a ready decision framework: compare a candidate pair field by field, add per-field log-likelihood weights (Newcombe 1959), and use two thresholds to split pairs into link / possible link / non-link, with the possible-link band sent to people (Fellegi and Sunter 1969). Winkler's string comparators and EM/semi-supervised estimation (1990, 2006) and the Elmagarmid et al. (2007) survey fill in the comparator, weight-estimation and reject-region details.

### Cited Findings
- **Newcombe, H. B., Kennedy, J. M., Axford, S. J., James, A. P. (1959). "Automatic Linkage of Vital Records." Science 130(3381): 954-959 (16 Oct 1959). doi:10.1126/science.130.3381.954.** (Opened via the IRS SOI reprint scan https://irs.gov/pub/irs-soi/1985preprintar26.pdf; text from OCR, so a few figures are noisy.) Linked British Columbia birth records to 114,471 marriage records (1946-55) on an early computer. Files were Soundex-coded on surname pairs and sorted so only records sharing the code pair were compared (de facto blocking); each field agreement/disagreement contributed a log2 odds weight ("binits") computed as log2(p_L/p_F) from frequencies in linked vs accidentally-paired records, with value-specific weights (a rare birthplace or initial agreeing counts more than a common one). Reported ~98.3% of potential linkages detected with ~0.7% spurious linkages; spelling variations in family names affected about 10% (live births) to 25% (stillbirths) of linkages, cut to about a third by phonetic coding. — [IRS SOI reprint](https://irs.gov/pub/irs-soi/1985preprintar26.pdf)
  - *Relevance:* origin of the two ideas StripCheck reuses: an index on a coarse, error-tolerant key (Soundex there; batch number plus OCR-confusion variants here) and additive evidence weights per field. Value-specific weights motivate weighting agreement on a rare manufacturer or product name more than agreement on a common one (e.g. "Paracetamol").
- **Fellegi, I. P., Sunter, A. B. (1969). "A Theory for Record Linkage." Journal of the American Statistical Association 64(328): 1183-1210. doi:10.1080/01621459.1969.10501049.** (Publisher page returned HTTP 403; read via IRS SOI reprint scan https://irs.gov/pub/irs-soi/1985preprintar28.pdf; volume/pages confirmed by the search-result listing of the Cornell course copy.) For a comparison vector gamma of field agreements, a linkage rule assigns each pair to A1 link, A2 possible link, or A3 non-link; errors mu = P(A1|unmatched) and lambda = P(A3|matched) are fixed in advance and the optimal rule minimises P(A2), i.e. it orders gamma by the likelihood ratio m(gamma)/u(gamma) and uses two thresholds. The paper states A2 "will require expensive manual linkage operations", and treats blocking (comparing only pairs agreeing on Soundex surname) as restricting the comparison space, analysing the effect on error levels; under conditional independence of fields the log-ratio becomes a sum of per-field weights. — [IRS SOI reprint](https://irs.gov/pub/irs-soi/1985preprintar28.pdf)
  - *Relevance:* the formal backbone for StripCheck: batch key = blocking key; product/brand/dates/maker = comparison vector; FLAGGED ~ A1, NOT_LISTED ~ A3, and the human question / CANT_VERIFY ~ A2 (clerical review). The theory says to set thresholds from tolerated false-flag (mu) and missed-recall (lambda) rates, which gives a principled way to justify the abstain band.

- **Winkler, W. E. (1990). "String Comparator Metrics and Enhanced Decision Rules in the Fellegi-Sunter Model of Record Linkage." U.S. Bureau of the Census; 8 pp.; ERIC document ED325505.** (Opened via ERIC full text https://files.eric.ed.gov/fulltext/ED325505.pdf. The paper is commonly cited as appearing in the 1990 Proceedings of the ASA Section on Survey Research Methods, pp. 354-359; I could NOT confirm that venue/pages from the document opened.) Introduces the Winkler extension of the Jaro comparator (bonus for agreeing prefixes) used in production matching software for the 1990 U.S. Census Post Enumeration Survey, and a method for adjusting F-S weights between full agreement and full disagreement according to the comparator value; shows on files with known truth that the F-S decision rules remain valid with partial-agreement weights. — [ERIC ED325505](https://files.eric.ed.gov/fulltext/ED325505.pdf)
  - *Relevance:* justifies graded (not binary) agreement on product and maker names in StripCheck's field-wise corroboration, e.g. OCR'd "Paracetamol Tablets IP 500mg" vs alert-list "Paracetamol Tab. I.P. 500 mg", while keeping the three-way F-S decision.
- **Winkler, W. E. (2006). "Overview of Record Linkage and Current Research Directions." Research Report Series (Statistics #2006-2), Statistical Research Division, U.S. Census Bureau, issued 8 Feb 2006.** Restates the F-S rule as match / possible match "held for clerical review" / nonmatch, with thresholds set from a-priori error bounds. Numbers: in a census undercount application more than 25% of matches would be missed by exact character matching; ~15% of last names among true matches did not agree exactly; Jaro (1989) comparator handles insertions, deletions and transpositions, with Winkler's variant "dramatically" improving matching; Yancey (2003, 2005) found newer comparators did not beat Jaro-Winkler on census name data, while Cohen et al.'s soft TF-IDF may do better on some lists. EM estimation of m/u (Winkler 1988/1989) works when the matched proportion in the EM pair set is above ~5%; semi-supervised use of <0.5% labelled pairs drawn from the clerical-review region improves error-rate estimation. Clerical review is costly: 1992 Census of Agriculture computerised linkage cut review from 75 clerks over 3 months to 6,500 hours and residual duplication fell from 10% to 2%. Blocking: with 10%/5% typo rates exact matching could miss 25% of matches, so multiple blocking passes are used; 11 blocking criteria found 99.5% of true matches within 10^12 of 10^17 candidate pairs (300M x 300M). — [Census RRS2006-02](https://www.census.gov/content/dam/Census/library/working-papers/2006/adrm/rrs2006-02.pdf)
  - *Relevance:* the single best bridge from theory to StripCheck practice: (i) exact-key blocking alone loses matches when keys carry typos, which is exactly why StripCheck adds OCR-confusion variants of the batch key (a multi-pass blocking analogue); (ii) labelled examples are best spent in the clerical/possible-match band, so StripCheck's human-in-the-loop answers should be logged and reused to calibrate thresholds; (iii) EM-estimated m/u is unreliable when true matches are rare (<5%), as they are for a random strip vs the NSQ list, so hand-set or rule-based weights are defensible.

- **Elmagarmid, A. K., Ipeirotis, P. G., Verykios, V. S. (2007). "Duplicate Record Detection: A Survey." IEEE Transactions on Knowledge and Data Engineering 19(1): 1-16 (Jan 2007). doi:10.1109/TKDE.2007.250581.** (Opened the authors' draft dated 13 Aug 2006, https://www.cs.purdue.edu/homes/ake/pub/survey2.pdf; vol/issue/DOI from the Univ. of Thessaly repository record; page range 1-16 is the commonly cited one and was not verified in the draft.) Taxonomy: field matching (character-based edit/affine-gap/Smith-Waterman/Jaro/q-gram; token-based TF-IDF/WHIRL; phonetic Soundex/NYSIIS/ONCA/Metaphone; numeric), then record-level methods (probabilistic F-S, supervised, active learning, distance-based, rule-based/declarative, unsupervised), then efficiency (blocking, sorted neighbourhood, canopies). Notes that F-S adds a "reject" class for which "a clerical review is necessary"; ALIAS (Sarawagi and Bhamidipaty) asks humans to label only high-uncertainty pairs, analogous to the reject region; reports Bilenko et al.'s conclusion that no single similarity metric suits all data sets; Taft's comparison found NYSIIS 98.72% vs Soundex 95.99% accurate at locating surnames. — [Purdue draft](https://www.cs.purdue.edu/homes/ake/pub/survey2.pdf)
  - *Relevance:* canonical citation for StripCheck's layered design (field comparators -> record-level decision -> efficiency via blocking) and for the abstain/reject region feeding a human; "no single metric for all data" supports per-field comparators (exact on batch, fuzzy on product name, date-tolerant on dates).

### Inferences
- Mapping for the paper: blocking key = batch number (exact plus OCR-confusion variants); comparison vector gamma = (product/generic, brand, mfg date, expiry date, manufacturer) agreement levels; FLAGGED/SUSPECTED_FAKE ~ A1 link, NOT_LISTED ~ A3 non-link, the human question and CANT_VERIFY ~ A2 possible link (clerical review / reject region). StripCheck's verifier's hard rules work as a rule-based override on top of the F-S score (e.g. a batch match with a conflicting manufacturer cannot be A1).
- Choosing thresholds from tolerated error rates (F-S mu, lambda) gives a principled answer to "when should the agent abstain?": a false FLAGGED (telling a user a genuine medicine is NSQ) and a missed recall cost different amounts, so the two thresholds can sit asymmetrically.
- EM estimation of m/u (Winkler) needs a matched share of roughly 5% or more in the pair set, and true matches between random user strips and the NSQ list are rare, so hand-set or rule-derived weights plus a small labelled set from the clerical band are the defensible choice for a student project.
- Value-specific (frequency-based) weights (Newcombe; F-S) suggest that agreement on a rare manufacturer should count for more than agreement on a very common generic such as paracetamol. CDSCO alert lists repeat common generics often (an inference about the data, not checked here).

### Gaps
- Christen, P. (2012), *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection*, Springer, Data-Centric Systems and Applications series (hardcover ISBN 978-3-642-31163-5; DOI 10.1007/978-3-642-31164-2, seen only as the Springer redirect target). The Springer pages redirected to a login and could not be opened, so no content from the book is cited here. Its metadata and its three-part structure (overview; preprocessing/indexing/comparison/classification/evaluation; privacy/real-time/unstructured) come only from search-result listings. Cite it as a general textbook only after checking a copy.
- Winkler's 1988 EM paper and Jaro (1989, JASA) were not opened; their claims above come from Winkler (2006).
- Fellegi-Sunter and Newcombe were read from OCR'd IRS reprints. The publisher pages (JASA, Science) returned HTTP 403, so page-level quotes should be checked against the published versions.

## Q2 Blocking and indexing

### Takeaway
Blocking cuts the quadratic pair space, but any error in the blocking-key value puts a true match in the wrong block (Christen 2012). The standard fixes are multiple keys or multiple encodings of the key, and error-tolerant q-gram/suffix or filtering (similarity-join) methods, evaluated by pair completeness, pairs quality and reduction ratio (Papadakis et al. 2020). StripCheck's OCR-confusion variant search is a domain-specific instance of "multiple encodings of the same blocking key".

### Cited Findings
- **Christen, P. (2012). "A Survey of Indexing Techniques for Scalable Record Linkage and Deduplication." IEEE Transactions on Knowledge and Data Engineering 24(9): 1537-1555 (1 Sep 2012). doi:10.1109/TKDE.2011.127.** (Opened the author's preprint https://users.cecs.anu.edu.au/~Peter.Christen/publications/christen2011indexing.pdf; vol/issue/pages from the ANU research-portal listing; DOI is the commonly cited one and was not shown on the preprint.) Surveys 12 variants of 6 indexing techniques (traditional blocking, sorted neighbourhood, q-gram, suffix array, canopy clustering, string-map) with complexity analysis and experiments; measures reduction ratio vs pairs completeness (PC = true-matched candidate pairs / all true matches). Key warning: "Any error in a field value used to generate a BKV will potentially result in records being inserted into the wrong block, thus leading to missing true matches"; remedy is several blocking keys on different fields or different encodings of the same field, and robust suffix/q-gram variants that tolerate errors at any position. Concludes that proper blocking-key definition is among the most important factors and that parameter sensitivity makes techniques hard to tune. — [ANU preprint](https://users.cecs.anu.edu.au/~Peter.Christen/publications/christen2011indexing.pdf)
  - *Relevance:* directly motivates StripCheck's OCR-confusion-aware variant search: an exact batch-number block misses true matches whenever OCR corrupts one character; generating confusion variants (B<->8, 0<->O, 5<->S, ...) is a domain-specific "multiple encodings of the same key" strategy, and a q-gram/edit-distance index on batch numbers is the generic fallback. PC (recall of blocking) is the right metric to report for the variant search.

- **Papadakis, G., Skoutas, D., Thanos, E., Palpanas, T. (2020). "A Survey of Blocking and Filtering Techniques for Entity Resolution." ACM Computing Surveys 53(2), Article 31. doi:10.1145/3377455.** (Opened arXiv:1905.06167v4, 21 Aug 2020, https://arxiv.org/pdf/1905.06167v4; the ACM DL page returned HTTP 403, so journal vol/issue/article/DOI are as commonly cited and NOT verified from the opened copy, whose ACM reference block is a placeholder.) Splits ER into candidate selection and matching; reviews Blocking (restrict comparisons to likely-matching pairs, schema-based or schema-agnostic, plus block-processing/meta-blocking) and Filtering (quickly find pairs that satisfy a predetermined similarity threshold, e.g. string-similarity joins) and hybrids. Defines Pair Completeness (recall) PC = |D(B)|/|D(E)|, Pairs Quality (precision) and Reduction Ratio, and defines blocking as simultaneously maximising PC, PQ and RR. — [arXiv v4](https://arxiv.org/pdf/1905.06167v4)
  - *Relevance:* StripCheck's exact batch lookup is schema-based blocking on a single key; the OCR-variant search is closer to *filtering* (all list batches within a confusion-weighted edit distance of the read batch). The PC/PQ/RR vocabulary lets the paper report candidate-generation recall separately from final verdict accuracy.

### Inferences
- In the paper, report the batch-lookup stage separately using PC (did the true alert row reach the candidate set?) and RR/PQ (how many spurious candidates per scan), and report the field-corroboration and adjudication stage with precision/recall/abstention.
- Winkler (2006) says multiple blocking passes were needed because typos made exact matching miss about 25% of matches. Applied here, the OCR variant search is not optional: one misread character in the batch number makes exact lookup alone lose the recall that matters most for safety. The confusion table (B/8, 0/O, 1/7/I, 5/S...) works like a weighted edit distance or a phonetic-style encoding for printed batch codes.
- Batch-number collisions (the same batch string used by different makers/products) are expected once the blocking key is short and alphanumeric; this is precisely why blocking must be followed by field comparison rather than treated as a verdict.

### Gaps
- The ACM CSUR version of Papadakis et al. (vol. 53(2), art. 31, DOI 10.1145/3377455) could not be opened (HTTP 403). The arXiv v4 was used, so the journal details are unverified.
- I found no published study of blocking on pharmaceutical batch or lot numbers, or of OCR-confusion-aware blocking keys. This looks like a genuine gap that StripCheck can claim, with the caveat that my search was limited.

## Q3 Clerical review and human-in-the-loop ER

### Takeaway
Human review of the uncertain band is part of record-linkage theory from the start: Fellegi and Sunter (1969) define the possible-link decision A2 as needing "expensive manual linkage operations" and minimise how often it occurs. Modern hybrid systems keep this pattern: machines prune, humans verify only likely or uncertain pairs (CrowdER, Wang et al. 2012), and active learners such as ALIAS ask for labels only on high-uncertainty pairs (as described by Elmagarmid et al. 2007). Winkler (2006) shows that a very small labelled sample (<0.5%) drawn from the clerical-review region improves estimation.

### Cited Findings
- **Wang, J., Kraska, T., Franklin, M. J., Feng, J. (2012). "CrowdER: Crowdsourcing Entity Resolution." PVLDB 5(11): 1483-1494. doi:10.14778/2350229.2350263 (DOI as commonly cited; not displayed on the arXiv page). arXiv:1208.1927 (9 Aug 2012).** Hybrid human-machine workflow: "machines are used to do an initial, coarse pass over all the data", and only the most likely matching pairs (above a machine-similarity threshold) are sent to crowd workers for verification; generating the minimum number of HIT batches of a given size is NP-hard, so a two-tiered heuristic is used; experiments on real data with a crowdsourcing platform report better efficiency and accuracy than machine-only or human-only. (Only the abstract was opened; specific cost/accuracy numbers not verified.) — [arXiv](https://arxiv.org/abs/1208.1927)
  - *Relevance:* modern analogue of F-S clerical review; supports StripCheck's design of machine pruning first (batch block + field corroboration) and asking the human only on the narrow uncertain band (e.g. "is this character a B or an 8?"), minimising user questions per scan.

### Inferences
- StripCheck's human-in-the-loop question ("is this character B or 8?") is clerical review pushed down to the field level and put to the person holding the pack. It costs less and is more accurate than reviewing a whole record pair, because that person can re-read the physical strip. This framing (field-level clerical review) is new in our framing; it is not stated in the sources.
- The F-S objective (minimise P(A2) at fixed error levels) corresponds to a measurable design goal: minimise questions per scan while keeping false-FLAGGED and missed-recall rates below set targets.
- User answers and abstentions should be logged as labelled pairs from the clerical band. This is the most informative training and calibration data according to Winkler (2006) and active-learning ER.

### Gaps
- The ALIAS paper itself (Sarawagi and Bhamidipaty, KDD 2002, DOI 10.1145/775047.775087 per search results) was not opened, and the IAS repository link returned 404. It is cited only through Elmagarmid et al. (2007).
- CrowdER: only the abstract was opened, so no cost or accuracy figures are reported.
- I did not find 2023-2026 studies of human-in-the-loop or LLM-plus-human entity resolution, and did not search further because of the tool-call budget. That gap remains open.

## Q4 String similarity for names

### Takeaway
No single string metric wins everywhere (Bilenko et al., via Elmagarmid et al. 2007). Jaro-Winkler, built for short personal names and used in U.S. Census production (Winkler 1990), suits short codes and brand names. Token-weighted hybrids (SoftTF-IDF with Jaro-Winkler as secondary) did best overall on multi-token entity names (Cohen, Ravikumar and Fienberg 2003). Graded similarity can be plugged into F-S weights without breaking the theory (Winkler 1990).

### Cited Findings
- **Cohen, W. W., Ravikumar, P., Fienberg, S. E. (2003). "A Comparison of String Distance Metrics for Name-Matching Tasks." Proc. IJCAI-2003 Workshop on Information Integration on the Web (IIWeb-03), Acapulco.** (Opened PDF https://www.cs.cmu.edu/~wcohen/postscript/ijcai-ws-2003.pdf; the workshop name/pages (commonly 73-78) are not printed on the PDF and were not verified.) Using the open-source SecondString toolkit, compares edit-distance metrics (Levenshtein, Monge-Elkan, Smith-Waterman), heuristic comparators (Jaro, Jaro-Winkler, defined as Jaro + (P'/10)(1-Jaro) with common prefix P' capped at 4), token-based metrics (TF-IDF, Jaccard, Jensen-Shannon) and hybrids, on 13 datasets including a synthetic census set, evaluated by max-F1 and non-interpolated average precision over candidates generated by a blocking step (shared infrequent substring). Monge-Elkan is the best edit-distance method on average; TF-IDF is the best token method; overall best is the hybrid SoftTF-IDF with Jaro-Winkler as secondary similarity (theta = 0.9), e.g. MaxF1 0.89 vs 0.73 [verifier correction: was 0.71, which is SFS's value in Table 2] for Level-2 Jaro-Winkler on UVA, 0.85 on CoraATDV. Notes Jaro/Jaro-Winkler are "intended primarily for short strings" such as personal names. — [CMU PDF](https://www.cs.cmu.edu/~wcohen/postscript/ijcai-ws-2003.pdf)
  - *Relevance:* guides comparator choice per field: Jaro-Winkler/edit distance suit short single-token codes and brand names (prefix bonus is useful for brands sharing a stem), while token-weighted SoftTF-IDF suits multi-token product descriptions and manufacturer names ("XYZ Pharmaceuticals Pvt. Ltd." vs "XYZ Pharma Ltd") where IDF down-weights common tokens like "Ltd", "Tablets", "IP".

### Inferences
- Per-field comparators for StripCheck: batch number: exact match or OCR-confusion-weighted edit distance (not Jaro-Winkler, since every character matters). Brand: Jaro-Winkler, whose prefix bonus fits Indian brand stems, with a high threshold given LASA risks. Product/generic description: token-based (TF-IDF/SoftTF-IDF) after normalisation, ignoring stop tokens such as IP/BP/USP, "Tablets", "Tab." and strength formatting. Manufacturer: token-based with legal-suffix stripping ("Pvt", "Ltd", "Pharma/Pharmaceuticals"). Dates: tolerant comparison (month/year granularity, format variants such as 03/2026 vs MAR 2026).
- Strength and dose form should be compared as structured values (number + unit), not as strings, following RxNorm's ingredient/strength/dose-form split.

### Gaps
- Yancey (2003, 2005), who reports that newer comparators did not beat Jaro-Winkler on census names, was cited only via Winkler (2006) and not opened.
- I found no benchmark of string metrics on drug brand names or on OCR'd pharmaceutical text. Levenshtein's original paper (1965/66) was not opened, so its claims are cited only through Cohen et al. and Elmagarmid et al.

## Q5 LLM-based entity matching and drug-name matching

### Takeaway
LLMs can match entities zero-shot. GPT-3 with 10 demonstrations matched or beat the fine-tuned Ditto on several Magellan datasets (Narayan et al. 2022), and GPT-4 zero-shot is within a few F1 points of fine-tuned PLMs while being far more robust to unseen entities (Peeters, Steiner and Bizer 2025). Results are, however, prompt-sensitive, especially for smaller and open models. Fine-tuned small models can match prompted large ones at orders of magnitude lower cost (Zhang et al. 2025), and a "select among candidates" framing beats independent pairwise yes/no (Wang et al. 2025). For drugs, RxNorm's ingredient/strength/dose-form/brand split is a useful schema, but it is US-scoped. Indian brand names are unreliable identity keys: one brand can cover different molecules, and one molecule can be sold under many brands (Neelakantan et al. 2024).

### Cited Findings
- **Narayan, A., Chami, I., Orr, L., Re, C. (2022). "Can Foundation Models Wrangle Your Data?" PVLDB 16(4): 738-746. doi:10.14778/3574245.3574258.** (PDF opened: https://www.vldb.org/pvldb/vol16/p738-narayan.pdf; arXiv 2205.09911 v1 20 May 2022, v2 24 Dec 2022, which additionally lists Simran Arora as an author; the PVLDB PDF lists four authors.) Casts entity matching (EM) as a yes/no prompt over serialised rows; GPT-3-175B (text-davinci-002) on the Magellan benchmark: zero-shot F1 87.2 Fodors-Zagats, 78.6 Beer, 65.9 iTunes-Amazon, 60.6 Walmart-Amazon, 93.5 DBLP-ACM, 64.6 DBLP-Google, 54.3 Amazon-Google; with k=10 demonstrations 100/100/98.2/87.0/96.6/83.8/63.5 vs Ditto 100/94.37/97.06/86.76/98.99/95.60/75.58. Attribute sub-selection +13.7 F1 on average; changing "same?" to "equivalent?" causes a 9.4 F1 gap; manual vs random demonstrations +14.7 F1. Notes EM systems "are often preceded by blocking heuristics" and flags private/domain-specific data as an open challenge. — [PVLDB](https://www.vldb.org/pvldb/vol16/p738-narayan.pdf)
  - *Relevance:* supports using a local LLM only as an adjudicator over a small set of already-blocked candidate pairs with a few curated drug-strip demonstrations; the prompt brittleness (9.4 F1 swing) motivates StripCheck's deterministic rule fallback and verifier/critic rather than trusting the LLM verdict alone.
- **Peeters, R., Steiner, A., Bizer, C. (2025). "Entity Matching using Large Language Models." Proc. 28th EDBT, 25-28 Mar 2025 (ISBN 978-3-89318-098-1). arXiv:2310.11244 (v1 17 Oct 2023, v4 18 Oct 2024).** Compares hosted (gpt-4o-mini, gpt4-0613, GPT-4o) and local open models (Llama2-70B, Llama3.1-70B, Mixtral-8x7B) with fine-tuned PLMs on six benchmarks. Zero-shot GPT-4 F1: WDC Products 89.61, Abt-Buy 95.78, Walmart-Amazon 89.67, Amazon-Google 76.38, DBLP-Scholar 89.82, DBLP-ACM 98.41 vs Ditto 84.90/91.31/86.39/80.07/94.31/99.00. Fine-tuned PLMs lose 22-61 F1 on unseen entities while LLMs do not; zero-shot Llama3.1-70B reaches 83.67 F1 on WDC Products (GPT-mini 81.15); F1 std-dev across prompts 2.26 for GPT-4 vs 6.18-18.54 for other models; in-context examples hurt GPT-mini/Mixtral by 4-26 F1; hand-written matching rules help Mixtral (+3-17 F1) but not GPT-4 (-1 to -3); zero-shot Llama2 ~22.6 s per prompt locally. — [arXiv HTML v4](https://arxiv.org/html/2310.11244v4)
  - *Relevance:* the closest evidence for a small local Ollama model as adjudicator: smaller/open models are much more prompt-sensitive and may *benefit* from explicit matching rules, which supports StripCheck feeding hard field-wise rules into the prompt and keeping a deterministic fallback; robustness to unseen entities matters because the alert list grows monthly with new products. Caveat: StripCheck's local models are far smaller than 70B, so these F1 values are an upper bound.
- **U.S. National Library of Medicine. "RxNorm Overview." Web page, last reviewed 19 Nov 2025; accessed 25 Oct 2026.** RxNorm is "a normalized naming system for generic and branded drugs" and a tool for interoperation between drug terminologies; a generic clinical drug name is "ingredient, strength, and dose form (in that order)" (term type SCD, e.g. "Naproxen 250 MG Oral Tablet"), branded drugs append the brand in brackets (SBD), with separate IN (ingredient) and BN (brand name) types. Scope: prescription and many OTC drugs "available in the United States"; full release monthly (first Monday) plus weekly updates. — [NLM](https://www.nlm.nih.gov/research/umls/rxnorm/overview.html)
  - *Relevance:* the IN/SCD/SBD/BN decomposition is a ready-made schema for StripCheck's product/brand comparison (compare ingredient+strength+dose form separately from brand), but RxNorm is US-scoped and will not cover most Indian brands, so StripCheck needs its own normalisation (e.g. strip "IP/BP/USP", unify "Tab./Tablets", parse strength) rather than an RxNorm lookup. This is a design inference, not a claim from the source.
- **Zhang, Z., Groth, P., Calixto, I., Schelter, S. (2025). "A Deep Dive Into Cross-Dataset Entity Matching with Large and Small Language Models." Proc. 28th EDBT, Barcelona, 25-28 Mar 2025, pp. 922-934 (Advances in Database Technology 28(3)). doi:10.48786/EDBT.2025.75.** (Opened final published version via UvA repository.) Cross-dataset EM = the matcher must work on an unseen target dataset with no labelled examples; leave-one-dataset-out evaluation of ZeroER, Ditto, Unicorn, AnyMatch (GPT-2/T5/LLaMA3.2 backbones), Jellyfish-13B, TableGPT and MatchGPT (GPT-4, GPT-4o-mini, GPT-3.5, Mixtral, Solar, Beluga) over 11 benchmark datasets (abstract says eight matchers; conclusion says 14 matcher configurations). Finds fine-tuned small models (<1B parameters by their definition) perform on par with prompted large models, data-centric approaches beat model-centric ones, and well-performing small models cost orders of magnitude less to deploy than comparable large commercial models. — [UvA PDF](https://pure.uva.nl/ws/files/331179344/A_Deep_Dive_Into_Cross-Dataset_Entity_Matching_with_Large_and_Small_Language_Models.pdf)
  - *Relevance:* strongest recent evidence that StripCheck need not depend on a large hosted LLM: a small local model, ideally fine-tuned or given curated drug-domain pairs, can be competitive, consistent with the no-paid-API, offline laptop constraint. StripCheck's alert lists are an "unseen dataset" relative to public EM benchmarks, which is exactly the cross-dataset setting.
- **Wang, T., Chen, X., Lin, H., Chen, X., Han, X., Sun, L., Wang, H., Zeng, Z. (2025). "Match, Compare, or Select? An Investigation of Large Language Models for Entity Matching." Proc. 31st COLING, Abu Dhabi, Jan 2025, pp. 96-109. ACL Anthology 2025.coling-main.8; arXiv:2405.16884.** (Abstract page opened; numeric gains not verified.) Notes that LLM EM usually makes independent pairwise binary decisions and ignores global consistency; compares *matching* (pairwise yes/no), *comparing* (which of two candidates matches better) and *selecting* (pick the match among a candidate list) across 8 ER datasets and 10 LLMs; selecting, which uses record interactions, performs best; proposes ComEM, a compound framework combining strategies and LLMs (e.g. a cheaper model to filter, a stronger one to select) for better effectiveness and efficiency. — [ACL Anthology](https://aclanthology.org/2025.coling-main.8/)
  - *Relevance:* StripCheck's adjudicator sees a *set* of candidate alert rows for one read batch (exact hit plus OCR variants); framing the LLM's job as "select the best candidate or none" rather than many independent yes/no calls is supported here and naturally rejects batch-number collisions between different products.
- **Neelakantan, M., Sharma, P., Kulkarni, A. (2024). "Look-alike, sound-alike (LASA) drugs in India." The Lancet Regional Health - Southeast Asia 26: 100425 (e-pub 16 May 2024; July 2024 issue). doi:10.1016/j.lansea.2024.100425. PMCID PMC11127203.** (Viewpoint; metadata from Europe PMC, text from PMC.) Documents Indian brand-name collisions: the same brand used for unrelated molecules ("Medzol" for midazolam and pantoprazole; "Medzole" for metronidazole, itraconazole and albendazole products; "Flucor" for fluconazole and flupentixol+melitracen; "Linamac" for lenalidomide and linagliptin), near-identical names (Olvance/olmesartan vs Oleanz/olanzapine; IMOX human amoxicillin tablets vs INIMOX veterinary injection), and one molecule under many brands (seven molnupiravir brands, e.g. Molnunat, Molflu, Molxvir). Notes Section 13 of the Trade Marks Act bars INNs in brand names and criticises CDSCO oversight; gives no national brand counts. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11127203/)
  - *Relevance:* direct evidence that in India *brand name alone* is not a reliable identity key: a brand match can hide a different molecule, and a generic match can come under many brands. This supports StripCheck comparing brand AND generic/active ingredient AND manufacturer as separate fields, and treating brand-only agreement as weak evidence (possible match), never as a FLAGGED verdict on its own.

### Inferences
- The evidence supports StripCheck's division of labour: deterministic blocking and field rules decide most cases, and the small local LLM adjudicates only the residual possible-match band, using a "pick one candidate or none" prompt with explicit matching rules (rules help weaker models, per Peeters et al.). A deterministic fallback is needed because prompt variance for non-GPT-4 models is large (F1 std-dev 6-18 points).
- Published LLM-EM F1 values come from 70B-class or hosted models on English product and bibliographic benchmarks. StripCheck's few-billion-parameter Ollama models on Indian drug data will probably do worse, so the paper should evaluate on its own labelled set and not quote benchmark F1 as expected performance.
- Brand-only agreement must never reach FLAGGED. Generic + strength + manufacturer + batch should be required, which addresses the LASA brand collisions documented for India.

### Gaps
- I found no peer-reviewed study of LLM-based matching of Indian drug brand names to generics, nor an Indian equivalent of RxNorm. CDSCO's own drug databases were outside this theme and were not checked.
- Peeters et al. (2025) EDBT page numbers were not verified from the EDBT site. A search snippet gave pp. 529-541 and DOI 10.48786/edbt.2025.42, but I did not open that page, so they are left out of the BibTeX.
- Wang et al. (2025): numeric results not opened (abstract only).
- News coverage (The South First, Jul 2026) of a CDSCO consultation on brand-name extensions surfaced only in search snippets and was not opened, so it is not cited.

## BibTeX

@article{narayan2022foundation,
  author = {Narayan, Avanika and Chami, Ines and Orr, Laurel and R{\'e}, Christopher},
  title = {Can Foundation Models Wrangle Your Data?},
  journal = {Proceedings of the VLDB Endowment},
  volume = {16},
  number = {4},
  pages = {738--746},
  year = {2022},
  doi = {10.14778/3574245.3574258},
  url = {https://www.vldb.org/pvldb/vol16/p738-narayan.pdf}
}

@inproceedings{peeters2025entity,
  author = {Peeters, Ralph and Steiner, Aaron and Bizer, Christian},
  title = {Entity Matching using Large Language Models},
  booktitle = {Proceedings of the 28th International Conference on Extending Database Technology (EDBT)},
  year = {2025},
  note = {arXiv:2310.11244},
  url = {https://arxiv.org/abs/2310.11244}
}

@article{newcombe1959automatic,
  author = {Newcombe, H. B. and Kennedy, J. M. and Axford, S. J. and James, A. P.},
  title = {Automatic Linkage of Vital Records},
  journal = {Science},
  volume = {130},
  number = {3381},
  pages = {954--959},
  year = {1959},
  doi = {10.1126/science.130.3381.954}
}

@article{fellegi1969theory,
  author = {Fellegi, Ivan P. and Sunter, Alan B.},
  title = {A Theory for Record Linkage},
  journal = {Journal of the American Statistical Association},
  volume = {64},
  number = {328},
  pages = {1183--1210},
  year = {1969},
  doi = {10.1080/01621459.1969.10501049}
}

@techreport{winkler1990string,
  author = {Winkler, William E.},
  title = {String Comparator Metrics and Enhanced Decision Rules in the {Fellegi-Sunter} Model of Record Linkage},
  institution = {U.S. Bureau of the Census, Statistical Research Division},
  year = {1990},
  note = {ERIC Document ED325505; also in Proc. ASA Section on Survey Research Methods (venue/pages not verified)},
  url = {https://files.eric.ed.gov/fulltext/ED325505.pdf}
}

@techreport{winkler2006overview,
  author = {Winkler, William E.},
  title = {Overview of Record Linkage and Current Research Directions},
  institution = {U.S. Census Bureau, Statistical Research Division},
  type = {Research Report Series},
  number = {Statistics \#2006-2},
  year = {2006},
  url = {https://www.census.gov/content/dam/Census/library/working-papers/2006/adrm/rrs2006-02.pdf}
}

@article{elmagarmid2007duplicate,
  author = {Elmagarmid, Ahmed K. and Ipeirotis, Panagiotis G. and Verykios, Vassilios S.},
  title = {Duplicate Record Detection: A Survey},
  journal = {IEEE Transactions on Knowledge and Data Engineering},
  volume = {19},
  number = {1},
  pages = {1--16},
  year = {2007},
  doi = {10.1109/TKDE.2007.250581}
}

@article{christen2012survey,
  author = {Christen, Peter},
  title = {A Survey of Indexing Techniques for Scalable Record Linkage and Deduplication},
  journal = {IEEE Transactions on Knowledge and Data Engineering},
  volume = {24},
  number = {9},
  pages = {1537--1555},
  year = {2012},
  doi = {10.1109/TKDE.2011.127}
}

@article{wang2012crowder,
  author = {Wang, Jiannan and Kraska, Tim and Franklin, Michael J. and Feng, Jianhua},
  title = {{CrowdER}: Crowdsourcing Entity Resolution},
  journal = {Proceedings of the VLDB Endowment},
  volume = {5},
  number = {11},
  pages = {1483--1494},
  year = {2012},
  note = {arXiv:1208.1927},
  url = {https://arxiv.org/abs/1208.1927}
}

@inproceedings{cohen2003comparison,
  author = {Cohen, William W. and Ravikumar, Pradeep and Fienberg, Stephen E.},
  title = {A Comparison of String Distance Metrics for Name-Matching Tasks},
  booktitle = {Proceedings of the IJCAI-2003 Workshop on Information Integration on the Web (IIWeb-03)},
  year = {2003},
  url = {https://www.cs.cmu.edu/~wcohen/postscript/ijcai-ws-2003.pdf}
}

@article{papadakis2020survey,
  author = {Papadakis, George and Skoutas, Dimitrios and Thanos, Emmanouil and Palpanas, Themis},
  title = {A Survey of Blocking and Filtering Techniques for Entity Resolution},
  journal = {ACM Computing Surveys},
  volume = {53},
  number = {2},
  year = {2020},
  doi = {10.1145/3377455},
  note = {Preprint arXiv:1905.06167v4; journal details not verified from the opened copy}
}

@misc{nlm2025rxnorm,
  author = {{U.S. National Library of Medicine}},
  title = {{RxNorm} Overview},
  year = {2025},
  url = {https://www.nlm.nih.gov/research/umls/rxnorm/overview.html},
  note = {Last reviewed 19 Nov 2025. Accessed 25 Oct 2026}
}

@inproceedings{zhang2025deep,
  author = {Zhang, Zeyu and Groth, Paul and Calixto, Iacer and Schelter, Sebastian},
  title = {A Deep Dive Into Cross-Dataset Entity Matching with Large and Small Language Models},
  booktitle = {Proceedings of the 28th International Conference on Extending Database Technology (EDBT)},
  pages = {922--934},
  year = {2025},
  doi = {10.48786/EDBT.2025.75}
}

@inproceedings{wang2025match,
  author = {Wang, Tianshu and Chen, Xiaoyang and Lin, Hongyu and Chen, Xuanang and Han, Xianpei and Sun, Le and Wang, Hao and Zeng, Zhenyu},
  title = {Match, Compare, or Select? An Investigation of Large Language Models for Entity Matching},
  booktitle = {Proceedings of the 31st International Conference on Computational Linguistics (COLING)},
  pages = {96--109},
  year = {2025},
  url = {https://aclanthology.org/2025.coling-main.8/}
}

@article{neelakantan2024lookalike,
  author = {Neelakantan, Murali and Sharma, Parth and Kulkarni, Ashish},
  title = {Look-alike, sound-alike ({LASA}) drugs in {India}},
  journal = {The Lancet Regional Health - Southeast Asia},
  volume = {26},
  pages = {100425},
  year = {2024},
  doi = {10.1016/j.lansea.2024.100425}
}

## Verification log

(Verifier, 25 Oct 2026. Checked against Crossref, arXiv, Semantic Scholar/DBLP and publisher pages.)

- newcombe1959automatic: VERIFIED. Crossref DOI 10.1126/science.130.3381.954 matches authors, title, Science 130(3381):954-959, 16 Oct 1959. Spot-check of the IRS reprint text confirms 114,471 marriage records (1946-55), ~98.3% of potential linkages, 0.7% spurious, "binits", and the 10% (live births) / 25% (stillbirths) spelling-variation figures.
- fellegi1969theory: VERIFIED. Crossref DOI 10.1080/01621459.1969.10501049 matches JASA 64(328):1183-1210 (Dec 1969). Reprint text confirms A1/A2/A3, "expensive manual linkage operations" for A2, and Soundex-surname blocking.
- winkler1990string: CORRECTED. The venue the notes could not confirm is now confirmed: the paper is in the 1990 Proceedings of the ASA Section on Survey Research Methods, pp. 354-359 (ASA archive PDF asasrms.org/Proceedings/papers/1990_056.pdf, page numbers 354-359 printed). BibTeX changed from @techreport to @inproceedings with that venue; ERIC ED325505 kept as a note. Content claims (Jaro extension, 1990 PES, F-S rules valid with partial-agreement weights) confirmed by ERIC abstract.
- winkler2006overview: VERIFIED. Census PDF opens; title, author, "Research Report Series (Statistics #2006-2)", issued 8 Feb 2006 all match. Spot-checked: >25% of matches missed by exact matching (census undercount); 25% of first names and 15% of last names disagreed among true matches; EM matched share "should be above 5%"; <0.5% training pairs from the clerical region; Census of Agriculture 75 clerks/3 months -> 6,500 hours, duplication 10% -> 2%; 10%/5% typo rates -> 25% missed; 99.5% of true matches in 10^12 of 10^17 pairs. Minor note: the report says "11 blocking criteria" in one place and "ten blocking passes" in another; the notes' "11" is faithful to the first.
- elmagarmid2007duplicate: VERIFIED. Crossref DOI 10.1109/TKDE.2007.250581 confirms IEEE TKDE 19(1):1-16, Jan 2007 (page range now verified). Draft text confirms NYSIIS 98.72% vs Soundex 95.99% (Taft), "a clerical review is necessary", ALIAS labelling only high-uncertainty pairs, and Bilenko et al.'s "no single metric" finding.
- christen2012survey: VERIFIED. Crossref DOI 10.1109/TKDE.2011.127 confirms IEEE TKDE 24(9):1537-1555, Sep 2012 (DOI now verified). Preprint confirms "twelve variations of six indexing techniques", the quoted "wrong block" warning, and the multiple-keys / different-encodings remedy.
- papadakis2020survey: CORRECTED. Crossref/doi.org metadata for DOI 10.1145/3377455 give the journal title as "Blocking and Filtering Techniques for Entity Resolution: A Survey" (the notes use the arXiv title "A Survey of Blocking and Filtering ..."). ACM Computing Surveys 53(2), pp. 1-42, published online 20 Mar 2020 (issue print date 2021). Authors, volume, issue and DOI are now verified. "Article 31" could not be confirmed and is left out of the BibTeX.
- wang2012crowder: VERIFIED. Crossref DOI 10.14778/2350229.2350263 (PVLDB 5(11):1483-1494, Jul 2012, same four authors) is now verified; the arXiv:1208.1927 journal_ref matches. DOI added to BibTeX.
- cohen2003comparison: CORRECTED. Authors, title and IIWeb-03 workshop confirmed from the CMU PDF; pages 73-78 confirmed by OpenAlex and added. Number corrected in notes: on UVA, Level-2 Jaro-Winkler MaxF1 is 0.73, not 0.71 (0.71 is SFS); SoftTFIDF 0.89 and CoraATDV 0.85 confirmed (Table 2). "Intended primarily for short strings" and theta = 0.9 confirmed.
- narayan2022foundation: VERIFIED. Crossref DOI 10.14778/3574245.3574258 confirms PVLDB 16(4):738-746 (Dec 2022) with four authors (arXiv adds Simran Arora, as the notes say). Table 1 F1 values (zero-shot and k=10 GPT-3, Ditto), +13.7 F1 attribute selection, 9.4 F1 prompt-wording gap and 14.7 F1 manual-vs-random demonstrations all confirmed in the PVLDB PDF.
- peeters2025entity: CORRECTED. DataCite confirms DOI 10.48786/edbt.2025.42 (same title and authors, openproceedings.org paper-81.pdf). The EDBT PDF prints pages 529-541 and ISBN 978-3-89318-098-1. DOI and pages were added to the BibTeX (the notes had left them out as unverified). Spot-checked: zero-shot GPT-4 F1 89.61/95.78/89.67/76.38/89.82/98.41 vs Ditto 84.90/91.31/86.39/80.07/94.31/99.00; Llama3.1-70B 83.67; GPT-mini 81.15; prompt SD 2.26 vs 6.18-18.54. Nuance: the 22-61 F1 unseen-entity drop is for RoBERTa (Ditto drops 36-56).
- zhang2025deep: VERIFIED. DataCite confirms DOI 10.48786/edbt.2025.75 (title and four authors). The EDBT PDF prints pages 922-934 (EDBT 2025, ISBN 978-3-89318-099-8). Confirmed: eight matchers on 11 datasets, small models on par with prompted large ones, data-centric beats model-centric, and orders-of-magnitude lower deployment cost. Nuance: the paper calls a model "large" when it has more than one billion parameters, and its best matcher, AnyMatch [LLaMA3.2] (1.3B), reaches 87.5 average F1 vs 87.4 for GPT-4.
- wang2025match: VERIFIED. The ACL Anthology BibTeX confirms the eight authors (in the notes' order), title, Proc. 31st COLING, Abu Dhabi, Jan 2025, pp. 96-109. The arXiv:2405.16884 abstract confirms the matching/comparing/selecting comparison, ComEM, 8 ER datasets and 10 LLMs. Numeric gains were still not checked (none are claimed in the notes).
- neelakantan2024lookalike: VERIFIED. Crossref DOI 10.1016/j.lansea.2024.100425 confirms authors, title, Lancet Reg Health SE Asia 26:100425 (Jul 2024). Europe PMC full text confirms the Medzol/Medzole/Flucor/Linamac collisions, Olvance/Oleanz and IMOX/INIMOX, seven molnupiravir brands (Cipmolnu, Molnunat, Molflu, Molxvir, Molulife, Molnumize, Molnutor), the Section 13 Trade Marks Act point, and the criticism of CDSCO.
- nlm2025rxnorm: VERIFIED. The page opens (HTTP 200) and confirms the quoted wording: "normalized naming system for generic and branded drugs"; ingredient, strength, dose form "(in that order)"; the Naproxen 250 MG Oral Tablet example; US scope; monthly release on the first Monday plus weekly updates; "Last Reviewed: November 19, 2025".
- christen2012data (Gaps section, no content cited): VERIFIED (metadata only). Crossref DOI 10.1007/978-3-642-31164-2 confirms Christen, "Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection", Springer Berlin Heidelberg 2012, print ISBN 978-3-642-31163-5. The series name and the three-part structure were not confirmed and are left out of the BibTeX. The notes cite no content from it, so cite it only as a general textbook.
- sarawagi2002interactive (ALIAS; Gaps section, cited via Elmagarmid et al.): VERIFIED (metadata only). Crossref DOI 10.1145/775047.775087 confirms "Interactive deduplication using active learning", Sarawagi and Bhamidipaty, KDD 2002, pp. 269-278. The paper's content was not read; claims about ALIAS rest on elmagarmid2007duplicate, which was verified.
- jaro1989advances (mentioned via Winkler 2006): VERIFIED (metadata only). Crossref DOI 10.1080/01621459.1989.10478785 confirms Jaro, "Advances in Record-Linkage Methodology as Applied to Matching the 1985 Census of Tampa, Florida", JASA 84(406):414-420, Jun 1989. Content claims rest on winkler2006overview.
- Winkler (1988) EM paper; Yancey (2003, 2005); Levenshtein (1965/66); Bilenko et al.; Taft (NYSIIS); Hernandez and Stolfo: UNVERIFIED. These are secondary mentions only and none was looked up separately, so they are not in the .bib file. The claims attributed to them come through Winkler (2006), Elmagarmid et al. (2007) or Cohen et al. (2003), and the verifier confirmed those claims appear in those sources. If any of these works is cited directly, it must be checked first.
- The South First news item (Jul 2026, CDSCO brand-name consultation): UNVERIFIED. It was not opened and the notes do not cite it; it is not in the .bib file.
- Access copies used by the researcher (IRS SOI reprints, ERIC, Purdue and ANU preprints, CMU PDF, arXiv versions) all opened (HTTP 200) on 25 Oct 2026.
- Verification: COMPLETE (11 verified in full plus 3 verified on metadata only, 4 corrected, 7 unverified secondary mentions or uncited items)

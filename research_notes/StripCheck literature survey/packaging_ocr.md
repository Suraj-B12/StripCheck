Status: COMPLETE

# Text recognition on pharmaceutical/product packaging, OCR model landscape, and OCR confidence reliability

Checklist:
- [x] Q1 Expiry-date / lot-code recognition on packages (methods, datasets, accuracy, blister-foil difficulty)
- [x] Q2 Medication-label reading for visually impaired users / medication safety
- [x] Q3 Lightweight OCR: PP-OCR family, PaddleOCR 3.0, RapidOCR, STR surveys, TrOCR
- [x] Q4 Vision-language models for OCR (small local models) and hallucination on short codes
- [x] Q5 Reliability of OCR confidence; calibration; does CLAHE fix misreads

## Q1 Expiry-date and lot/batch-code recognition on packages

### Cited Findings
- **Seker, A. C. and Ahn, S. C. (2022). "A generalized framework for recognition of expiration dates on product packages using fully convolutional networks." Expert Systems with Applications 203, art. 117310. DOI 10.1016/j.eswa.2022.117310.** Metadata confirmed via Crossref (published Oct 2022) — [Crossref](https://api.crossref.org/works/10.1016/j.eswa.2022.117310). Pipeline (as described by Zidane and Soliman 2023/2024): FCOS detects the date region, a modified FCOS without FPN finds day/month/year components, and a decoupled attention network (DAN) fine-tuned on synthetic dates reads characters — [arXiv 2310.14069](https://arxiv.org/abs/2310.14069). Reported 97.74% recognition accuracy across 13 date formats, a neural date parser, and a public ExpDate collection of six sub-datasets (real + synthetic) released because no public expiry-date dataset existed. CAVEAT: the 97.74% / 13 formats / six-dataset figures come from the KIST repository abstract as surfaced in search snippets; the KIST page was firewall-blocked and ScienceDirect returned 403, so I did not read the full text — [KIST repository record](https://pubs.kist.re.kr/handle/201004/114526). Community mirror of ExpDate on Hugging Face (dimun/dates, Apache 2.0, synthetic and real splits) not verified against the official release.
  - Relevance to StripCheck: the seminal baseline for date reading on packages; motivates treating "date region detect -> recognise -> parse into D/M/Y" as a separate stage with a format-aware parser (StripCheck's MFG/EXP normaliser). Its data are food/consumer packages, not medicine blister foil, so accuracy does not transfer directly.
- **Zidane, A. and Soliman, G. (2024). "Ladder Bottom-up Convolutional Bidirectional Variational Autoencoder for Image Translation of Dotted Arabic Expiration Dates." Journal of Electronic Imaging 33(5), 053024. DOI 10.1117/1.JEI.33.5.053024; preprint arXiv:2310.14069 (v1 21 Oct 2023, v2 1 Oct 2024).** Dot-matrix (dotted) dates are translated into filled glyphs with an LCBVAE, then read by a custom CRNN; trained on 60,000 synthetic images from a home-made Arabic dot-matrix TrueType font, tested on 3,000 more realistic synthetic images; 97% image-translation accuracy. Real dotted-date images were unavailable — [arXiv 2310.14069](https://arxiv.org/abs/2310.14069).
  - Relevance: direct evidence that dot-matrix/inkjet date codes (common on Indian strip backs and cartons) need special handling and that datasets for them are scarce/synthetic; supports StripCheck's enhanced re-read and second-reader design rather than trusting one OCR pass.
- **Peng, H., Bayón, J., Recas Piorno, J. and Guijarro Mata-García, M. (2025). "Efficient Expiration Date Recognition in Food Packages for Mobile Applications." Algorithms 18(5), 286. DOI 10.3390/a18050286.** Accessibility-motivated (visually impaired users) CNN framework: detection F1 = 0.9303, recognition accuracy 97.06%, total inference 63 ms on one GTX 1080; compares FP32/FP16/INT8 on mobile and finds FP16 on CPU the best accuracy/energy trade-off — [Docta Complutense record](https://docta.ucm.es/entities/publication/003bfd34-c573-4544-b2c9-edbd12a91261) (MDPI page returned 403; volume/issue taken from DOI suffix and search metadata).
  - Relevance: recent (2025) state of the art for on-device date reading; supports StripCheck's CPU-only, offline choice and shows ~97% is a ceiling even on curated food-package data, i.e. ~3% of dates still misread.
- **Koponen, J., Haataja, K. and Toivanen, P. (2024). "Novel Deep Learning Application: Recognizing Inconsistent Characters on Pharmaceutical Packaging." F1000Research 12:427, version 2 (23 Jul 2024; v1 20 Apr 2023). DOI 10.12688/f1000research.131775.2.** The only pharma-packaging-specific batch/expiry recognition paper I could open. R-CNN (selective search + AlexNet features + SVM) recognises characters of expiry dates and manufacturing batch codes on real medical packages from a Finnish health-tech company: precision 91.1% / recall 72.7% / F1 80.9% vs Tesseract 38.3% / 61.3% / 47.1%. Dataset is tiny (27 binarised source images: 16 dot-matrix, 11 pressed ink-marked; 43 classes). Difficulties named: curved cardboard causing uneven illumination, multiple printing methods giving low-contrast irregular characters, varied code layouts/colours, motion blur. Peer-review status at v2: 1 "approved with reservations", 1 "not approved" — cite with care — [F1000Research v2](https://f1000research.com/articles/12-427/v2).
  - Relevance: shows that generic OCR (Tesseract) fails badly on dot-matrix/pressed batch codes and that even a specialised model has ~27% recall loss; directly motivates StripCheck's OCR-confusion-aware variant search, second reader and abstention (CANT_VERIFY) rather than exact-match-only lookup.
- Industry framing (not peer-reviewed): DSCSA (US) product identifiers and the EU Falsified Medicines Directive delegated regulation both make lot/batch number and expiry part of the mandatory product identifier; in-line OCR/OCV (optical character verification) systems such as Vitronic VICODE (launched 2008) check these at the packaging line. I did not open primary regulatory texts for these statements; they come from search summaries — treat as background only, verify before citing.
- Note on blister foil: I found no peer-reviewed paper that specifically benchmarks OCR on embossed/foil blister backs. Difficulties for foil (specular glare, embossed un-inked characters, low contrast, curvature/creases) are stated only in vendor/patent material (e.g., a USPTO patent describing an OCR model that reads embossed batch codes on blister packs, US 12697718, not opened in full). Koponen et al. explicitly exclude un-inked pressed/stamped/laser text. This is a genuine literature gap StripCheck can claim.

### Takeaway
Expiry-date recognition on consumer packages is a mature niche (~97% recognition on curated food-package datasets: Seker and Ahn 2022, 97.74%; Peng et al. 2025, 97.06%), but batch/lot-code recognition on medicine packaging is barely studied: the one pharma paper found (Koponen et al. 2024) reaches only 80.9% F1 on a 27-image dot-matrix/pressed set, with Tesseract at 47.1%.

### Inferences
- A residual 3-20% character/field error rate on dates and batch codes is the realistic operating regime; exact-match batch lookup alone would miss listed batches and produce false NOT_LISTED verdicts. This supports confusion-aware variant search plus corroboration on other fields.
- Dates have structure (format grammars, MFG < EXP, plausible ranges) that a parser can validate; batch codes do not, so batch numbers need external corroboration (the CDSCO row's product/maker/dates) rather than internal validation.
- Dot-matrix and pressed/embossed codes need dedicated handling (synthetic data, glyph filling or a second reader); a generic OCR pass is the weakest link.

### Gaps
- No public dataset of Indian medicine strips/blister foils with annotated batch/expiry fields was found.
- No peer-reviewed benchmark on embossed or foil-printed batch codes was found.
- Full text of Seker and Ahn (2022) could not be opened (KIST firewall, ScienceDirect 403); numbers taken from repository abstract snippets.
- Primary DSCSA / EU FMD texts were not opened in this pass.

## Q2 Medication-label reading for visually impaired users / medication-safety checks

### Cited Findings
- **Kim, S., Wi, Y. and Lee, J. (2023). "Implementation of a Mobile Application for Checking Medicines and Pills for the Visually Impaired in Korea." In Lecture Notes in Networks and Systems, vol. 693, Springer, pp. 907-917. DOI 10.1007/978-981-99-3243-6_73.** Voice-guided app with container, pill (CNN), speech, prescription and drug-envelope recognition; motivated by Korean medicine labels rarely carrying braille and often lacking product name/expiry/dosage. Abstract reports no accuracy figures and does not state whether OCR is used — [Sookmyung ScholarWorks](https://scholarworks.sookmyung.ac.kr/item/e3621618-3f95-4bd0-8a26-27855d1ac541).
  - Relevance: representative of accessibility-oriented medicine apps: they identify the product and read information, but none checks batch numbers against regulator recall/NSQ lists — StripCheck's distinguishing feature.
- Peng et al. (2025) (see Q1) is also accessibility-motivated (visually impaired users, food packages).
- NEWS / industry (not peer-reviewed): Training Matters / Pharmacy Magazine (13 Oct 2022), "New AI helps visually impaired": a Haleon-commissioned 2022 survey of 502 visually impaired people in the UK found 93% said health products are not accessible enough and almost one in five had taken the wrong dosage because they could not read the packaging; Haleon partnered with Microsoft Seeing AI, which reads product name/ingredients/usage for 1,500+ Haleon products via barcode scanning (not OCR) — [Pharmacy Magazine](https://www.pharmacymagazine.co.uk/news/882582-new-ai-helps-visually-impaired).
  - Relevance: shows that deployed accessibility solutions rely on barcodes/QR (product-level identity), which cannot identify a batch; motivates StripCheck's "QR first, then OCR" ordering and its batch-level focus.

### Takeaway
Medication-label assistance for visually impaired users is dominated by product identification (barcode, NFC, pill recognition, read-aloud), not batch-level verification; I found no peer-reviewed system that reads a batch number off a strip and checks it against a regulator's NSQ/spurious or recall list.

### Inferences
- StripCheck's novelty claim should be framed as "batch-level regulatory cross-check from a phone photo, offline", not "medicine label reading", which is crowded.
- Because survey evidence links unreadable packaging to dosing errors, an abstaining system (CANT_VERIFY) is safer than a confident wrong answer for this population.

### Gaps
- No peer-reviewed accuracy figures found for OCR apps (Seeing AI, Envision, Lookout) on medicine strips/cartons; the ScripTalk veteran study (Loyola record) failed to load (HTTP 500).
- An Indian 2025 BIO Web of Conferences paper (DOI 10.1051/bioconf/202520401021) reportedly uses OCR on strip MFG/EXP dates with CNN+GNN features (0.91 accuracy / 0.90 F1 per search snippet) but returned 403 — not verified, not cited.
- No study found that evaluates any app on Indian strips with Hindi/regional text.

## Q3 Lightweight OCR: PP-OCR family, RapidOCR, surveys, TrOCR

### Cited Findings
- **Du, Y., Li, C., Guo, R., Yin, X., Liu, W., Zhou, J., Bai, Y., Yu, Z., Yang, Y., Dang, Q. and Wang, H. (2020). "PP-OCR: A Practical Ultra Lightweight OCR System." arXiv:2009.09941 (v1 21 Sep 2020, v3 15 Oct 2020).** Three-stage pipeline (DB text detection -> direction classifier -> CRNN recognition) with "a bag of strategies" to boost accuracy or shrink size; 3.5 MB model for 6,622 Chinese characters and 2.8 MB for 63 alphanumeric symbols; trained on ~97K detection, 600K direction-classifier and 17.9M recognition images — [arXiv](https://arxiv.org/abs/2009.09941).
  - Relevance: the seminal reference for the OCR family StripCheck uses via RapidOCR; its few-MB size is what makes fully offline OCR on a laptop feasible.
- **Li, C., Liu, W., Guo, R., Yin, X., Jiang, K., Du, Y., Du, Y., Zhu, L., Lai, B., Hu, X., Yu, D. and Ma, Y. (2022). "PP-OCRv3: More Attempts for the Improvement of Ultra Lightweight OCR System." arXiv:2206.03001 (v2 14 Jun 2022).** Recogniser moves from CRNN to SVTR-LCNet (lightweight SVTR); detector gets LK-PAN, RSE-FPN and DML distillation; hmean 5% higher than PP-OCRv2 at comparable speed — [arXiv](https://arxiv.org/abs/2206.03001).
  - Relevance: documents the CTC/SVTR recogniser lineage whose per-character softmax "confidence" StripCheck reads; CTC-style recognisers have no language model for batch codes, so B/8, 0/O confusions are not corrected by context.
- **Cui, C., Sun, T., Lin, M., Gao, T., Zhang, Y., Liu, J., Wang, X., Zhang, Z., Zhou, C., Liu, H., Zhang, Y., Lv, W., Huang, K., Zhang, Y., Zhang, J., Zhang, J., Liu, Y., Yu, D. and Ma, Y. (2025). "PaddleOCR 3.0 Technical Report." arXiv:2507.05595 (v1 8 Jul 2025).** Introduces PP-OCRv5 (multilingual recognition: Simplified/Traditional Chinese, Pinyin, English, Japanese in one model; server variant for GPU, mobile variant for CPU), PP-StructureV3 and PP-ChatOCRv4. Claims models with <100M parameters "rival billion-parameter VLMs"; on a 17-scenario evaluation (OmniDocBench-style 1-edit-distance metric) PP-OCRv5 ranks first on average ahead of GOT-OCR2.0-0.5B, RolmOCR-7B, Qwen2.5-VL-72B, InternVL3-78B, Gemini 2.5 Pro and GPT-4o, but trails VLMs on handwritten English; 26% recognition-error reduction on non-standard handwriting vs previous models; high-performance inference cuts T4 latency 73.1% (mobile rec) / 40.4% (mobile det). Per-model numbers are only in a figure; the benchmark is vendor-run — [arXiv HTML](https://arxiv.org/html/2507.05595v1).
  - Relevance: supports StripCheck's choice of PP-OCR (via RapidOCR) as the primary, fast, CPU reader, with a VLM only as an optional second opinion; the self-reported comparison should be cited as the vendor's claim.
- **Du, Y., Li, C., Guo, R., Cui, C., Liu, W., Zhou, J., Lu, B., Yang, Y., Liu, Q., Hu, X., Yu, D. and Ma, Y. (2021). "PP-OCRv2: Bag of Tricks for Ultra Lightweight OCR System." arXiv:2109.03144 (v2 12 Oct 2021).** Precision 7% higher than PP-OCR at the same inference cost (abstract does not say absolute vs relative); no CPU timing in abstract — [arXiv](https://arxiv.org/abs/2109.03144).
  - Relevance: completes the PP-OCR lineage (v1 2020 -> v2 2021 -> v3 2022 -> v4 2023 -> v5 2025) for the Related Work narrative.
- **RapidAI Team. RapidOCR: OCR Toolbox. GitHub repository, https://github.com/RapidAI/RapidOCR (accessed 25 Oct 2026).** Apache-2.0 toolkit that converts PaddleOCR models to ONNX and runs them on ONNX Runtime, OpenVINO, MNN, PaddlePaddle, TensorRT or PyTorch; offline, multi-platform; Python package plus C++/Java/C# ports; ~8.3k GitHub stars as of 25 Oct 2026; model weights remain Baidu/PaddleOCR-licensed (Apache-2.0). The README's own suggested citation is "Rapid OCR: OCR Toolbox", RapidAI Team, 2021. Which PP-OCR version is the default could not be confirmed from the README page fetched — [GitHub](https://github.com/RapidAI/RapidOCR).
  - Relevance: the exact OCR runtime StripCheck uses; justifies "no Paddle framework dependency, CPU-only ONNX inference on Windows".
- PP-OCRv4 (2023): no standalone technical report found/opened; it is documented in PaddleOCR release notes only. Gap noted.
- **Long, S., He, X. and Yao, C. (2021). "Scene Text Detection and Recognition: The Deep Learning Era." International Journal of Computer Vision 129(1), 161-184 (online 27 Aug 2020). DOI 10.1007/s11263-020-01369-0; arXiv:1811.04256.** Survey of deep scene-text detection/recognition, benchmarks and remaining "grand challenges" (abstract does not enumerate them) — [arXiv](https://arxiv.org/abs/1811.04256); metadata via [Crossref](https://api.crossref.org/works/10.1007/s11263-020-01369-0).
  - Relevance: standard citation framing packaging text as scene text (non-document, arbitrary background, perspective, illumination).
- **Chen, X., Jin, L., Zhu, Y., Luo, C. and Wang, T. (2021). "Text Recognition in the Wild: A Survey." ACM Computing Surveys 54(2), 1-35 (online 5 Mar 2021). DOI 10.1145/3440756; arXiv:2005.03492.** Reviews fundamental problems, state-of-the-art STR methods and public resources — [arXiv](https://arxiv.org/abs/2005.03492); metadata via [Crossref](https://api.crossref.org/works/10.1145/3440756).
  - Relevance: second standard STR survey; useful for situating CTC (CRNN/SVTR, used in PP-OCR) vs attention/transformer decoders.
- **Li, M., Lv, T., Chen, J., Cui, L., Lu, Y., Florencio, D., Zhang, C., Li, Z. and Wei, F. (2023). "TrOCR: Transformer-Based Optical Character Recognition with Pre-trained Models." Proceedings of the AAAI Conference on Artificial Intelligence 37(11), 13094-13102 (published 26 Jun 2023). DOI 10.1609/aaai.v37i11.26538; arXiv:2109.10282.** End-to-end image-Transformer encoder + text-Transformer decoder generating wordpieces, no separate LM post-processing; pre-trained on large synthetic data and fine-tuned; reports SOTA on printed, handwritten and scene text (abstract gives no numbers) — [arXiv](https://arxiv.org/abs/2109.10282); metadata via [Crossref](https://api.crossref.org/works/10.1609/aaai.v37i11.26538).
  - Relevance: an autoregressive decoder with an implicit language model can "autocorrect" arbitrary batch codes toward plausible wordpieces, which is undesirable for lot numbers; one reason StripCheck prefers a CTC recogniser plus explicit confusion handling.

### Takeaway
The PP-OCR line (2020 -> v2 2021 -> v3 2022 -> v4 2023 -> v5 in PaddleOCR 3.0, Jul 2025) is the de facto lightweight, CPU-capable OCR stack (few-MB to <100 MB models), and RapidOCR packages it as Apache-2.0 ONNX for offline use; PaddleOCR 3.0 claims PP-OCRv5 matches or beats billion-parameter VLMs on a vendor-run 17-scenario benchmark.

### Inferences
- RapidOCR + PP-OCR is a defensible primary reader for an offline Windows laptop; the vendor benchmark should be cited as a claim, and StripCheck should report its own field accuracy on strips.
- CTC recognisers (CRNN/SVTR) have no lexical prior, which avoids LM "autocorrection" of batch codes but also means visually similar glyphs (B/8, O/0, S/5, 1/7/I) are confused purely on appearance, which is exactly the confusion set StripCheck searches.

### Gaps
- PP-OCRv4 has no standalone paper; RapidOCR's current default model version and release date were not confirmed from the README.
- No published accuracy of PP-OCR specifically on medicine packaging was found.

## Q4 Vision-language models as OCR readers; hallucination on short alphanumeric codes

### Cited Findings
- **Wei, H., Liu, C., Chen, J., Wang, J., Kong, L., Xu, Y., Ge, Z., Zhao, L., Sun, J., Peng, Y., Han, C. and Zhang, X. (2024). "General OCR Theory: Towards OCR-2.0 via a Unified End-to-end Model." arXiv:2409.01704 (3 Sep 2024).** GOT: 580M-parameter end-to-end encoder-decoder treating text, formulas, tables, charts, sheet music etc. as "characters"; handles scene and document images, plain or formatted output, region-level OCR by coordinates/colour, dynamic resolution and multi-page — [arXiv](https://arxiv.org/abs/2409.01704).
  - Relevance: the archetype of "OCR-2.0" generative readers; at 0.58B it is a candidate small second reader, but being generative it can emit plausible text not in the image.
- **Bai, S., Chen, K., Liu, X., et al. (2025). "Qwen2.5-VL Technical Report." arXiv:2502.13923 (19 Feb 2025).** Three sizes (flagship 72B; the abstract does not list the others — the publicly released 3B and 7B checkpoints are known from the model cards but I did not open them); claims robust document parsing and structured extraction from invoices, forms and tables, with 72B matching GPT-4o / Claude 3.5 Sonnet on document and diagram understanding — [arXiv](https://arxiv.org/abs/2502.13923).
  - Relevance: the most common small local VLM (3B/7B via Ollama) for a second, independent read of the strip; its claims are document-centric, not packaging-specific.
- **Poznanski, J., Rangapur, A., Borchardt, J., Dunkelberger, J., Huff, R., Lin, D., Wilhelm, C., Lo, K. and Soldaini, L. (2025). "olmOCR: Unlocking Trillions of Tokens in PDFs with Vision Language Models." arXiv:2502.18443 (v1 25 Feb 2025; v3 2 Jul 2025).** Fine-tuned 7B VLM (on olmOCR-mix-0225: 260K pages from 100K+ PDFs); ~US$176 per million pages vs >US$6,240 for GPT-4o; olmOCR-Bench of 1,400 PDFs on which it is claimed to beat GPT-4o, Gemini Flash 2 and Qwen2.5-VL — [arXiv](https://arxiv.org/abs/2502.18443).
  - Relevance: shows the field's VLM-OCR effort targets long PDF documents; evaluation uses unit-test style checks, not short-code exact match, so its gains cannot be assumed for batch codes on foil.
- **Cui, C., Sun, T., Liang, S., Gao, T., Zhang, Z., et al. (2025). "PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model." arXiv:2510.14528 (v1 16 Oct 2025; v4 25 Nov 2025).** 0.9B VLM = NaViT-style dynamic-resolution encoder + ERNIE-4.5-0.3B LM; 109 languages; text, tables, formulas, charts; claims SOTA page-level parsing and element-level recognition with fast inference (no numbers in abstract) — [arXiv](https://arxiv.org/abs/2510.14528).
  - Relevance: sub-1B VLM from the same family as StripCheck's primary OCR; a plausible CPU-feasible second reader, but sharing training lineage with PP-OCR may reduce error independence.
- **Wei, H., Sun, Y. and Li, Y. (2025). "DeepSeek-OCR: Contexts Optical Compression." arXiv:2510.18234 (21 Oct 2025).** DeepEncoder + DeepSeek3B-MoE-A570M decoder; ~97% decoding precision when text tokens are <10x vision tokens, ~60% at 20x compression; on OmniDocBench beats GOT-OCR2.0 with 100 vision tokens/page and MinerU2.0 with <800; >200K pages/day on one A100-40G — [arXiv](https://arxiv.org/abs/2510.18234).
  - Relevance: shows VLM OCR precision depends on visual-token budget/resolution; a tiny crop of a batch code at low resolution sits in the regime where generative readers guess. Needs GPU for practical throughput, unlike RapidOCR.
- **Bai, S., et al. (Qwen Team) (2025). "Qwen3-VL Technical Report." arXiv:2511.21631 (v1 26 Nov 2025; v2 27 Nov 2025).** Dense 2B/4B/8B/32B and MoE 30B-A3B/235B-A22B; native interleaved context up to 256K tokens. Section 5.4 (per search snippet; I did not open the PDF) reports OCR parsing (CC-OCR, OmniDocBench), OCRBench and OCRBench_v2 results for the flagship; third-party summaries mention >70% accuracy on 32 of 39 OCR languages and an OCRBench of ~920/1000 for 235B — unverified, do not cite those numbers without checking the PDF — [arXiv](https://arxiv.org/abs/2511.21631).
  - Relevance: the 2B/4B/8B dense models are the current (late 2025-2026) best candidates for a <=8B local second reader on a laptop; their published OCR scores are for the flagship, not for the small sizes.
- Newer models up to Oct 2026: beyond the above, I did not open primary reports for later (2026) OCR VLMs; treat any newer-model claims as a gap.

#### Evidence on VLM OCR hallucination and abstention
- **He, Z., Zhang, C., Wu, Z., Chen, Z., Zhan, Y., Li, Y., Zhang, Z., Wang, X. and Qiu, M. (2025). "Seeing is Believing? Mitigating OCR Hallucinations in Multimodal Large Language Models." NeurIPS 2025 (poster); arXiv:2506.20168 (v2 22 Sep 2025).** Introduces KIE-HVQA, claimed first benchmark of OCR hallucination in degraded documents (ID cards, invoices, prescriptions; motion blur, occlusion, low contrast, obfuscation; 2,000 train / 400 test; pixel-level OCR-reliability labels). Average score: authors' SFT+RL model 58.05 vs GPT-4o 30.21; on not-clear characters 61.34 vs GPT-4o 36.13 and Qwen2.5-VL 24.19 (model size printed as "8B" in the extracted text, probably the 7B model; unverified); ~28% absolute gain in hallucination-free accuracy over GPT-4o. Authors state models "default to linguistic priors rather than anchoring decisions to observable visual evidence", and that Qwen2.5-VL-7B identifies "values not present in the image" — [arXiv HTML](https://arxiv.org/html/2506.20168v2); venue confirmed at [NeurIPS 2025 virtual site](https://neurips.cc/virtual/2025/loc/san-diego/poster/117155).
  - Relevance: the strongest peer-reviewed evidence that small local VLMs (exactly the ones StripCheck could run) confidently invent characters on degraded text, including prescriptions; justifies using the VLM only as an independent corroborating reader whose disagreement triggers HITL/abstention, never as sole source of a batch number.
- **Guan, S., Lin, M., Xu, C., Zhao, J. and Greene, D. (2026). "Teaching VLMs to Admit Uncertainty in OCR from Lossy Visual Inputs." ICLR 2026.** VLMs produce "fluent yet incorrect text" on degraded inputs without signalling uncertainty, attributed to accuracy-only post-training rewards that encourage guessing; proposes GRPO training that wraps unreliable spans in uncertainty tags; new Blur-OCR benchmark; uncertainty-tag F1 = 0.685 while preserving transcription accuracy. No arXiv ID found; poster page titles it "Teaching LLMs to Admit Uncertainty in OCR" — [ML Anthology](https://mlanthology.org/iclr/2026/guan2026iclr-teaching/); [ICLR 2026 poster](https://iclr.cc/virtual/2026/poster/10006400) (poster page not opened).
  - Relevance: supports StripCheck's per-character "in doubt" flag + human question; even trained uncertainty tagging reaches only ~0.69 F1, so a rule-based critic and abstention remain necessary.
- **Yao, J., Kulshrestha, A., Rauschmayr, N., Roberts, R., Zhu, B., Tsvetkov, Y. and Tombari, F. (2025). "Reading Between the Lines: Abstaining from VLM-Generated OCR Errors via Latent Representation Probes." arXiv:2511.19806 (25 Nov 2025).** Argues output probabilities are poorly calibrated and semantic-agreement methods ill-suited for OCR abstention (motivating example: "50 mph" read as "60 mph"); probes on hidden states/attention over visual tokens improve abstention accuracy by 7.6% over best baselines on four image/video benchmarks; best signals in intermediate layers — [arXiv](https://arxiv.org/abs/2511.19806).
  - Relevance: see the "Yao et al. 2025 relevance" note after the OCRBench v2 entry.
- **Fu, L., Kuang, Z., Song, J., et al. (with Bai, X. last author) (2024/2025). "OCRBench v2: An Improved Benchmark for Evaluating Large Multimodal Models on Visual Text Localization and Reasoning." arXiv:2501.00321 (v1 31 Dec 2024; v2 5 Jun 2025).** ~4x the tasks of OCRBench, 31 scenarios, 10,000 human-verified QA pairs plus a private 1,500-image test set; most LMMs score below 50/100; named weaknesses include "less frequently encountered text recognition" and "fine-grained perception" — [arXiv](https://arxiv.org/abs/2501.00321).
  - Relevance: arbitrary batch codes (e.g., "B3K0417") are by definition infrequent, non-lexical text, i.e. the category on which LMMs are weakest; supports keeping a non-generative OCR as primary reader.
- (Yao et al. 2025 relevance:) direct evidence that a VLM's own token probabilities are not a trustworthy gate for single-digit errors (5/6-type confusions are exactly StripCheck's B/8, 0/O, 1/7 problem); supports cross-reader agreement plus database corroboration instead of confidence thresholds. Preprint, not yet peer-reviewed as of 25 Oct 2026 (to my knowledge).

### Takeaway
VLM-based OCR moved fast from 2024 to 2025 (GOT-OCR 2.0, 580M, Sep 2024; Qwen2.5-VL, Feb 2025; olmOCR 7B, Feb 2025; PaddleOCR-VL 0.9B and DeepSeek-OCR, Oct 2025; Qwen3-VL 2B-235B, Nov 2025), but it is optimised for document parsing. Peer-reviewed 2025-2026 work (KIE-HVQA, NeurIPS 2025; Guan et al., ICLR 2026) shows that on degraded inputs these models fall back on language priors and produce fluent, confident text that is not in the image; small open models such as Qwen2.5-VL-7B do worst.

### Inferences
- A small local VLM is useful in StripCheck only as an independent second reader: agreement with PP-OCR raises confidence, and disagreement on any batch character should trigger a HITL question or CANT_VERIFY. It must never be the sole source of a batch number.
- Error independence is weaker when both readers share a lineage (e.g., PP-OCR and PaddleOCR-VL); a different-family VLM (Qwen-VL) is the better second opinion.
- Low-resolution crops of short codes are the regime where generative OCR guesses (DeepSeek-OCR precision falls from ~97% to ~60% as compression rises), so the VLM should be given the highest-resolution crop of the batch region.

### Gaps
- No study found that measures VLM hallucination specifically on short alphanumeric lot/batch codes on packaging; the closest evidence is from degraded documents (KIE-HVQA), scene-text VQA (Yao et al. 2025) and OCRBench v2's "less frequent text" category.
- Qwen3-VL small-model OCR numbers and post-Nov-2025 (2026) OCR VLMs were not verified from primary reports.
- olmOCR, GOT and PaddleOCR-VL abstracts give no hallucination rates.

## Q5 Reliability of OCR confidence scores; calibration; CLAHE

### Cited Findings
- **Guo, C., Pleiss, G., Sun, Y. and Weinberger, K. Q. (2017). "On Calibration of Modern Neural Networks." In Proceedings of the 34th International Conference on Machine Learning (ICML), PMLR 70, pp. 1321-1330.** Modern deep nets are poorly calibrated (unlike networks of a decade earlier): predicted probabilities overstate correctness; depth, width, weight decay and BatchNorm affect calibration; temperature scaling (one-parameter Platt scaling) is "surprisingly effective" post hoc — [PMLR](https://proceedings.mlr.press/v70/guo17a.html); [arXiv:1706.04599](https://arxiv.org/abs/1706.04599).
  - Relevance: the seminal citation for why StripCheck does not accept a RapidOCR score of, say, 0.95 as "95% likely correct"; any confidence threshold must be calibrated on held-out strip images or replaced by corroboration rules.
- **Slossberg, R., Anschel, O., Markovitz, A., Litman, R., Aberdam, A., Tsiper, S., Mazor, S., Wu, J. and Manmatha, R. (2020/2022). "On Calibration of Scene-Text Recognition Models." arXiv:2012.12643 (23 Dec 2020); published in ECCV 2022 Workshops (venue per ML Anthology listing, not opened in full).** Several recent STR models are "consistently overconfident"; character-level calibration of attention decoders actually increases word-level calibration error; sequence-level temperature-scaling variants cut calibration error by up to ~7x; calibration before beam search improves accuracy — [arXiv](https://arxiv.org/abs/2012.12643); venue: [ML Anthology](https://mlanthology.org/eccvw/2022/slossberg2022eccvw-calibration).
  - Relevance: direct evidence that text recognisers' word/character confidences are overconfident; StripCheck's batch-level decision must therefore be word-level and corroborated, and per-character doubt flags should be treated as heuristics.
- **Peng, Z., Luo, Y., Chen, T., Xu, K. and Huang, S. (2023). "Perception and Semantic Aware Regularization for Sequential Confidence Calibration." arXiv:2305.19498 (31 May 2023); CVPR 2023 (venue inferred from the CVF open-access supplemental file name "Peng_Perception_and_Semantic_CVPR_2023"; abstract page did not state it).** Sequence recognisers trained on target sequences alone are prone to "over-confidence"; token-independent label smoothing is sub-optimal; PSSR regularises with perceptually similar sequences (from a context-free recogniser) and semantically correlated sequences; SOTA calibration on STR and speech (no numbers in abstract) — [arXiv](https://arxiv.org/abs/2305.19498).
  - Relevance: "perceptually similar sequences" are exactly OCR confusion neighbours (B/8, 0/O); supports StripCheck's explicit confusion-variant search as an engineering analogue.
- Yao et al. (2025) (see Q4) independently argue that VLM output probabilities are poorly calibrated for OCR abstention.

#### CLAHE
- **Pizer, S. M., Amburn, E. P., Austin, J. D., Cromartie, R., Geselowitz, A., Greer, T., ter Haar Romeny, B., Zimmerman, J. B. and Zuiderveld, K. (1987). "Adaptive histogram equalization and its variations." Computer Vision, Graphics, and Image Processing 39(3), 355-368. DOI 10.1016/S0734-189X(87)80186-X.** Seminal AHE/contrast-limited AHE paper (metadata confirmed via Crossref; full text not opened, so no claims beyond the method's origin) — [Crossref](https://api.crossref.org/works/10.1016/S0734-189X(87)80186-X).
- **Zuiderveld, K. (1994). "Contrast Limited Adaptive Histogram Equalization." In Graphics Gems (IV), Elsevier/Academic Press, pp. 474-485. DOI 10.1016/b978-0-12-336156-1.50061-6.** The standard CLAHE implementation reference (metadata via Crossref; Crossref lists container "Graphics Gems" without the volume number — the ISBN prefix 0-12-336156 corresponds to Graphics Gems IV, ed. P. S. Heckbert; editor not confirmed in the record) — [Crossref search](https://api.crossref.org/works?query.bibliographic=Zuiderveld+Contrast+Limited+Adaptive+Histogram+Equalization+Graphics+Gems&rows=3).
  - Relevance (both): citations for StripCheck's "enhanced re-read" step (CLAHE on the luminance channel before a second OCR pass).
- **Tavares, R. A. (2024). "Comparison of Image Preprocessing Techniques for Vehicle License Plate Recognition Using OCR: Performance and Accuracy Evaluation." arXiv:2410.13622 (15 Oct 2024).** EasyOCR on Brazilian licence plates (DSLR, varied distance/lighting; image count not stated): baseline 71.7% accuracy; grayscale, CLAHE (RGB) and bilateral filter each 70.75%; author concludes the gain in contrast "did not translate into a significant improvement" and CLAHE adds time and may not suit high lighting variation. Single-author preprint — [arXiv HTML](https://arxiv.org/html/2410.13622v1).
  - Relevance: the closest controlled evidence on short alphanumeric codes: CLAHE does not fix recognition errors and can slightly hurt; it changes contrast, it does not resolve glyph ambiguity (B vs 8). Supports treating the enhanced re-read as a source of a second hypothesis to be reconciled, not as a correction.
- I found no rigorous study isolating CLAHE's effect on OCR of specular foil/glare. Small, non-controlled studies (e.g., an Indonesian e-KTP ID-card Tesseract pipeline reporting 39.55% -> 64.97% with grayscale+denoise+CLAHE+threshold, IJSECS 2025) suggest gains mainly on low-contrast/unevenly lit images; I did not open that paper, so it is not cited.

### Takeaway
Deep classifiers (Guo et al. 2017) and specifically scene-text recognisers (Slossberg et al. 2020/2022; Peng et al. 2023) are systematically overconfident, and VLM token probabilities are poorly calibrated for OCR abstention (Yao et al. 2025). A high OCR confidence therefore does not certify a correct batch number. CLAHE redistributes local contrast; the only controlled short-code evidence found (Tavares 2024, licence plates) shows no accuracy gain (71.7% -> 70.75%), so it addresses low contrast or uneven lighting and does not resolve glyph ambiguity.

### Inferences
- StripCheck should not gate verdicts on raw RapidOCR scores. Better options are (a) cross-reader agreement, (b) confusion-aware candidate generation, (c) field-level corroboration against the CDSCO row, and (d) the critic's hard rules with abstention. If a threshold is used, it should be temperature-scaled or calibrated on a held-out set of strip photos.
- The enhanced (CLAHE) re-read is best framed as producing a second hypothesis under different contrast, and it can also introduce new misreads; reconciling the two reads is what reduces errors.
- A reliability diagram or ECE of RapidOCR confidence on StripCheck's own test images would be a cheap, publishable contribution.

### Gaps
- No study found on CLAHE or glare removal for OCR on metallic foil or blister packs.
- No published calibration analysis of PP-OCR/RapidOCR confidence scores specifically was found.
- Zuiderveld (1994) and Pizer et al. (1987) full texts not opened; cited only for method origin.

## Final takeaways for the report writer
1. Literature gap (claimable): no peer-reviewed system reads batch numbers from medicine strips or blister foil and cross-checks them against a regulator's NSQ/spurious list. Pharma batch-code OCR is under-studied (Koponen et al. 2024: 80.9% F1 on 27 images), while expiry-date reading on food packages is mature (~97%; Seker and Ahn 2022; Peng et al. 2025).
2. Primary reader: PP-OCR via RapidOCR is the standard lightweight offline OCR (Du et al. 2020 to PaddleOCR 3.0, 2025), and its vendor claims to rival billion-parameter VLMs.
3. Second reader: small VLMs (Qwen2.5/3-VL 2-8B, PaddleOCR-VL 0.9B, GOT 0.58B) are viable locally but hallucinate plausible characters on degraded text (KIE-HVQA, NeurIPS 2025; Guan et al., ICLR 2026). Use them for corroboration and disagreement detection only.
4. Confidence is not correctness: STR and VLM confidences are overconfident or miscalibrated (Guo 2017; Slossberg 2020/2022; Peng 2023; Yao 2025). This motivates confusion-aware search, field corroboration, HITL and abstention over thresholding.
5. CLAHE helps contrast and does not fix misreads (Tavares 2024: no gain on plates). Treat the enhanced re-read as a second hypothesis.
6. Accessibility products (Seeing AI with Haleon; Kim et al. 2023) identify the product via barcode or recognition and do not verify the batch. StripCheck's batch-level check complements them.

## BibTeX

```bibtex
@article{seker2022generalized,
  author  = {Seker, Ahmet Cagatay and Ahn, Sang Chul},
  title   = {A generalized framework for recognition of expiration dates on product packages using fully convolutional networks},
  journal = {Expert Systems with Applications},
  volume  = {203},
  pages   = {117310},
  year    = {2022},
  doi     = {10.1016/j.eswa.2022.117310}
}

@article{zidane2024ladder,
  author  = {Zidane, Ahmed and Soliman, Ghada},
  title   = {Ladder Bottom-up Convolutional Bidirectional Variational Autoencoder for Image Translation of Dotted {Arabic} Expiration Dates},
  journal = {Journal of Electronic Imaging},
  volume  = {33},
  number  = {5},
  pages   = {053024},
  year    = {2024},
  doi     = {10.1117/1.JEI.33.5.053024},
  note    = {arXiv:2310.14069}
}

@article{koponen2024novel,
  author  = {Koponen, Jarmo and Haataja, Keijo and Toivanen, Pekka},
  title   = {Novel Deep Learning Application: Recognizing Inconsistent Characters on Pharmaceutical Packaging},
  journal = {F1000Research},
  volume  = {12},
  pages   = {427},
  year    = {2024},
  note    = {Version 2; peer review: 1 approved with reservations, 1 not approved},
  doi     = {10.12688/f1000research.131775.2}
}

@inproceedings{kim2023implementation,
  author    = {Kim, Soeun and Wi, Youngeun and Lee, Jongwoo},
  title     = {Implementation of a Mobile Application for Checking Medicines and Pills for the Visually Impaired in {Korea}},
  booktitle = {Lecture Notes in Networks and Systems},
  volume    = {693},
  pages     = {907--917},
  publisher = {Springer},
  year      = {2023},
  doi       = {10.1007/978-981-99-3243-6_73}
}

@misc{du2020ppocr,
  author        = {Du, Yuning and Li, Chenxia and Guo, Ruoyu and Yin, Xiaoting and Liu, Weiwei and Zhou, Jun and Bai, Yifan and Yu, Zilin and Yang, Yehua and Dang, Qingqing and Wang, Haoshuang},
  title         = {{PP-OCR}: A Practical Ultra Lightweight {OCR} System},
  year          = {2020},
  eprint        = {2009.09941},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2009.09941}
}

@misc{li2022ppocrv3,
  author        = {Li, Chenxia and Liu, Weiwei and Guo, Ruoyu and Yin, Xiaoting and Jiang, Kaitao and Du, Yongkun and Du, Yuning and Zhu, Lingfeng and Lai, Baohua and Hu, Xiaoguang and Yu, Dianhai and Ma, Yanjun},
  title         = {{PP-OCRv3}: More Attempts for the Improvement of Ultra Lightweight {OCR} System},
  year          = {2022},
  eprint        = {2206.03001},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2206.03001}
}

@misc{cui2025paddleocr,
  author        = {Cui, Cheng and Sun, Ting and Lin, Manhui and Gao, Tingquan and Zhang, Yubo and Liu, Jiaxuan and Wang, Xueqing and Zhang, Zelun and Zhou, Changda and Liu, Hongen and Zhang, Yue and Lv, Wenyu and Huang, Kui and Zhang, Yichao and Zhang, Jing and Zhang, Jun and Liu, Yi and Yu, Dianhai and Ma, Yanjun},
  title         = {{PaddleOCR} 3.0 Technical Report},
  year          = {2025},
  eprint        = {2507.05595},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2507.05595}
}

@misc{du2021ppocrv2,
  author        = {Du, Yuning and Li, Chenxia and Guo, Ruoyu and Cui, Cheng and Liu, Weiwei and Zhou, Jun and Lu, Bin and Yang, Yehua and Liu, Qiwen and Hu, Xiaoguang and Yu, Dianhai and Ma, Yanjun},
  title         = {{PP-OCRv2}: Bag of Tricks for Ultra Lightweight {OCR} System},
  year          = {2021},
  eprint        = {2109.03144},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2109.03144}
}

@misc{rapidai2021rapidocr,
  author       = {{RapidAI Team}},
  title        = {{RapidOCR}: {OCR} Toolbox},
  year         = {2021},
  howpublished = {GitHub repository},
  url          = {https://github.com/RapidAI/RapidOCR},
  note         = {Accessed 25 Oct 2026}
}

@article{long2021scene,
  author  = {Long, Shangbang and He, Xin and Yao, Cong},
  title   = {Scene Text Detection and Recognition: The Deep Learning Era},
  journal = {International Journal of Computer Vision},
  volume  = {129},
  number  = {1},
  pages   = {161--184},
  year    = {2021},
  doi     = {10.1007/s11263-020-01369-0}
}

@article{chen2021text,
  author  = {Chen, Xiaoxue and Jin, Lianwen and Zhu, Yuanzhi and Luo, Canjie and Wang, Tianwei},
  title   = {Text Recognition in the Wild: A Survey},
  journal = {ACM Computing Surveys},
  volume  = {54},
  number  = {2},
  pages   = {1--35},
  year    = {2021},
  doi     = {10.1145/3440756}
}

@inproceedings{li2023trocr,
  author    = {Li, Minghao and Lv, Tengchao and Chen, Jingye and Cui, Lei and Lu, Yijuan and Florencio, Dinei and Zhang, Cha and Li, Zhoujun and Wei, Furu},
  title     = {{TrOCR}: Transformer-Based Optical Character Recognition with Pre-trained Models},
  booktitle = {Proceedings of the AAAI Conference on Artificial Intelligence},
  volume    = {37},
  number    = {11},
  pages     = {13094--13102},
  year      = {2023},
  doi       = {10.1609/aaai.v37i11.26538}
}

@misc{wei2024general,
  author        = {Wei, Haoran and Liu, Chenglong and Chen, Jinyue and Wang, Jia and Kong, Lingyu and Xu, Yanming and Ge, Zheng and Zhao, Liang and Sun, Jianjian and Peng, Yuang and Han, Chunrui and Zhang, Xiangyu},
  title         = {General {OCR} Theory: Towards {OCR}-2.0 via a Unified End-to-end Model},
  year          = {2024},
  eprint        = {2409.01704},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2409.01704}
}

@misc{bai2025qwen25vl,
  author        = {Bai, Shuai and Chen, Keqin and Liu, Xuejing and others},
  title         = {{Qwen2.5-VL} Technical Report},
  year          = {2025},
  eprint        = {2502.13923},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2502.13923}
}

@misc{poznanski2025olmocr,
  author        = {Poznanski, Jake and Rangapur, Aman and Borchardt, Jon and Dunkelberger, Jason and Huff, Regan and Lin, Daniel and Wilhelm, Christopher and Lo, Kyle and Soldaini, Luca},
  title         = {{olmOCR}: Unlocking Trillions of Tokens in {PDFs} with Vision Language Models},
  year          = {2025},
  eprint        = {2502.18443},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  doi           = {10.48550/arXiv.2502.18443}
}

@misc{cui2025paddleocrvl,
  author        = {Cui, Cheng and Sun, Ting and Liang, Suyin and Gao, Tingquan and Zhang, Zelun and others},
  title         = {{PaddleOCR-VL}: Boosting Multilingual Document Parsing via a 0.9{B} Ultra-Compact Vision-Language Model},
  year          = {2025},
  eprint        = {2510.14528},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2510.14528}
}

@misc{wei2025deepseekocr,
  author        = {Wei, Haoran and Sun, Yaofeng and Li, Yukun},
  title         = {{DeepSeek-OCR}: Contexts Optical Compression},
  year          = {2025},
  eprint        = {2510.18234},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2510.18234}
}

@misc{bai2025qwen3vl,
  author        = {Bai, Shuai and others},
  title         = {{Qwen3-VL} Technical Report},
  year          = {2025},
  eprint        = {2511.21631},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2511.21631}
}

@inproceedings{guo2017calibration,
  author    = {Guo, Chuan and Pleiss, Geoff and Sun, Yu and Weinberger, Kilian Q.},
  title     = {On Calibration of Modern Neural Networks},
  booktitle = {Proceedings of the 34th International Conference on Machine Learning},
  series    = {Proceedings of Machine Learning Research},
  volume    = {70},
  pages     = {1321--1330},
  editor    = {Precup, Doina and Teh, Yee Whye},
  publisher = {PMLR},
  year      = {2017},
  url       = {https://proceedings.mlr.press/v70/guo17a.html}
}

@inproceedings{slossberg2022calibration,
  author    = {Slossberg, Ron and Anschel, Oron and Markovitz, Amir and Litman, Ron and Aberdam, Aviad and Tsiper, Shahar and Mazor, Shai and Wu, Jon and Manmatha, R.},
  title     = {On Calibration of Scene-Text Recognition Models},
  booktitle = {European Conference on Computer Vision (ECCV) Workshops},
  year      = {2022},
  note      = {arXiv:2012.12643; venue per ML Anthology, page numbers not verified},
  url       = {https://arxiv.org/abs/2012.12643}
}

@inproceedings{peng2023perception,
  author    = {Peng, Zhenghua and Luo, Yu and Chen, Tianshui and Xu, Keke and Huang, Shuangping},
  title     = {Perception and Semantic Aware Regularization for Sequential Confidence Calibration},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year      = {2023},
  note      = {arXiv:2305.19498; page numbers not verified},
  url       = {https://arxiv.org/abs/2305.19498}
}

@article{pizer1987adaptive,
  author  = {Pizer, Stephen M. and Amburn, E. Philip and Austin, John D. and Cromartie, Robert and Geselowitz, Ari and Greer, Trey and ter Haar Romeny, Bart and Zimmerman, John B. and Zuiderveld, Karel},
  title   = {Adaptive histogram equalization and its variations},
  journal = {Computer Vision, Graphics, and Image Processing},
  volume  = {39},
  number  = {3},
  pages   = {355--368},
  year    = {1987},
  doi     = {10.1016/S0734-189X(87)80186-X}
}

@incollection{zuiderveld1994contrast,
  author    = {Zuiderveld, Karel},
  title     = {Contrast Limited Adaptive Histogram Equalization},
  booktitle = {Graphics Gems {IV}},
  publisher = {Academic Press},
  pages     = {474--485},
  year      = {1994},
  doi       = {10.1016/b978-0-12-336156-1.50061-6}
}

@misc{tavares2024comparison,
  author        = {Tavares, Renato Augusto},
  title         = {Comparison of Image Preprocessing Techniques for Vehicle License Plate Recognition Using {OCR}: Performance and Accuracy Evaluation},
  year          = {2024},
  eprint        = {2410.13622},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2410.13622}
}

@inproceedings{he2025seeing,
  author    = {He, Zhentao and Zhang, Can and Wu, Ziheng and Chen, Zhenghao and Zhan, Yufei and Li, Yifan and Zhang, Zhao and Wang, Xian and Qiu, Minghui},
  title     = {Seeing is Believing? Mitigating {OCR} Hallucinations in Multimodal Large Language Models},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year      = {2025},
  note      = {arXiv:2506.20168},
  url       = {https://arxiv.org/abs/2506.20168}
}

@inproceedings{guan2026teaching,
  author    = {Guan, Shuhao and Lin, Moule and Xu, Cheng and Zhao, Jinman and Greene, Derek},
  title     = {Teaching {VLMs} to Admit Uncertainty in {OCR} from Lossy Visual Inputs},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2026},
  url       = {https://mlanthology.org/iclr/2026/guan2026iclr-teaching/}
}

@misc{fu2024ocrbenchv2,
  author        = {Fu, Ling and Kuang, Zhebin and Song, Jiajun and others and Bai, Xiang},
  title         = {{OCRBench} v2: An Improved Benchmark for Evaluating Large Multimodal Models on Visual Text Localization and Reasoning},
  year          = {2024},
  eprint        = {2501.00321},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2501.00321}
}

@misc{yao2025reading,
  author        = {Yao, Jihan and Kulshrestha, Achin and Rauschmayr, Nathalie and Roberts, Reed and Zhu, Banghua and Tsvetkov, Yulia and Tombari, Federico},
  title         = {Reading Between the Lines: Abstaining from {VLM}-Generated {OCR} Errors via Latent Representation Probes},
  year          = {2025},
  eprint        = {2511.19806},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2511.19806}
}

@article{peng2025efficient,
  author  = {Peng, Hao and Bay{\'o}n, Juan and Recas Piorno, Joaqu{\'i}n and Guijarro Mata-Garc{\'i}a, Mar{\'i}a},
  title   = {Efficient Expiration Date Recognition in Food Packages for Mobile Applications},
  journal = {Algorithms},
  volume  = {18},
  number  = {5},
  pages   = {286},
  year    = {2025},
  doi     = {10.3390/a18050286}
}
```

## Verification log

Verifier pass started 25 Oct 2026. One line per source; VERIFIED / CORRECTED / UNVERIFIED.

- seker2022generalized: VERIFIED. Crossref DOI 10.1016/j.eswa.2022.117310 matches title, authors, ESWA vol 203, art. 117310, Oct 2022. Abstract (via OpenAlex) confirms 97.74% recognition accuracy, 13 date formats, neural date parser, public ExpDate dataset. The "six sub-datasets" detail is NOT in the abstract [UNVERIFIED detail].
- zidane2024ladder: VERIFIED. Crossref (JEI 33(5), 053024, published 30 Sep 2024) and arXiv 2310.14069 abstract confirm LCBVAE+CRNN, Arabic dot-matrix TTF, 60,000 synthetic training / 3,000 realistic-synthetic test images, 97% image-translation accuracy.
- peng2025efficient: CORRECTED (author name form only). Crossref/OpenAlex confirm Algorithms 18(5) 286, 2025, F1 0.9303 detection, 97.06% recognition, 63 ms on one GTX 1080, FP16-on-CPU best trade-off. Crossref registers authors as "Recas, Joaquin" and "Guijarro, Maria"; .bib uses the registered forms instead of "Recas Piorno" / "Guijarro Mata-Garcia".
- koponen2024novel: VERIFIED. Crossref (F1000Research 12:427, v2 23 Jul 2024) and the v2 full-text XML confirm R-CNN P/R/F1 91.1/72.7/80.9 vs Tesseract 38.3/61.3/47.1, 27 binarised images (16 dot-matrix, 11 pressed/ink-marked), 43 classes, and the v2 status "1 approved with reservations, 1 not approved".
- kim2023implementation: CORRECTED. Crossref confirms authors, title, pp. 907-917, DOI. booktitle changed from the series name to "Proceedings of Eighth International Congress on Information and Communication Technology (ICICT 2023)", with series LNNS vol. 693 (vol. 693 = ICICT 2023 Volume 1, ISBN 978-981-99-3243-6, per book listings), editors Yang, Sherratt, Dey, Joshi added.
- BIO Web of Conferences paper (DOI 10.1051/bioconf/202520401021; mentioned in Q2 Gaps, not cited by the researcher): VERIFIED metadata via Crossref: Kuri, P., Das Bhattacharjee, A. and Saha, R. (2025), "Non-Invasive Detection of Expired Medicines Using Artificial Intelligence and Image Analysis", BIO Web Conf. 204, 01021. Abstract (OpenAlex) confirms OCR for expiry text + CNN + GNN, accuracy 0.91, recall 0.89, F1 0.90. The "Indian" and "strip MFG/EXP" details are not in the abstract [UNVERIFIED details]. Added to .bib as kuri2025noninvasive.
- du2020ppocr: VERIFIED. arXiv 2009.09941 (v1 21 Sep 2020, updated 15 Oct 2020), 11 authors as listed; abstract confirms 3.5M / 6,622 Chinese chars, 2.8M / 63 alphanumerics, 97K / 600K / 17.9M training images.
- li2022ppocrv3: VERIFIED. arXiv 2206.03001 (v1 7 Jun 2022, v2 14 Jun 2022), 12 authors as listed; abstract confirms CRNN -> SVTR-LCNet, LK-PAN, RSE-FPN, DML, hmean +5% over PP-OCRv2 at comparable speed.
- du2021ppocrv2: VERIFIED. arXiv 2109.03144 (v1 7 Sep 2021, v2 12 Oct 2021), 12 authors as listed; abstract confirms "precision ... 7% higher than PP-OCR under the same inference cost".
- cui2025paddleocr: VERIFIED. arXiv 2507.05595 (8 Jul 2025), 19 authors as listed; abstract confirms PP-OCRv5 / PP-StructureV3 / PP-ChatOCRv4 and "<100M parameters ... rivaling billion-parameter VLMs"; HTML full text confirms 17 scenarios, PP-OCRv5 ranks first on average 1-edit distance ahead of GOT-OCR2.0-0.5B, RolmOCR-7B, Qwen2.5-VL-72B, InternVL3-78B, Gemini 2.5 Pro, GPT-4o; slightly inferior on handwritten English; 26% error reduction on non-standard handwriting; T4 latency -73.1% (mobile rec) / -40.4% (mobile det).
- rapidai2021rapidocr: VERIFIED (web source). GitHub API: RapidAI/RapidOCR exists, Apache-2.0, created 4 Jan 2021, 8,304 stars on 25 Oct 2026 (~8.3k confirmed); description lists ONNX Runtime, OpenVINO, MNN, PaddlePaddle, TensorRT, PyTorch; README confirms PaddleOCR->ONNX conversion, Python/C++/Java/C# ports and the suggested citation (title spelled "{Rapid OCR}: OCR Toolbox", RapidAI Team, 2021; .bib uses that spelling).
- long2021scene: VERIFIED. Crossref: IJCV 129(1) 161-184, online 27 Aug 2020, authors Long, He, Yao; arXiv 1811.04256 matches.
- chen2021text: VERIFIED. Crossref: ACM Computing Surveys 54(2) 1-35, 5 Mar 2021, five authors as listed; arXiv 2005.03492 matches.
- li2023trocr: VERIFIED. Crossref: AAAI 37(11) 13094-13102, 26 Jun 2023, nine authors as listed; arXiv 2109.10282 matches.
- wei2024general: VERIFIED. arXiv 2409.01704 (3 Sep 2024), 12 authors as listed; abstract confirms 580M parameters, OCR-2.0 "characters" (formulas, tables, charts, sheet music), scene/document input, region-level OCR by coordinates/colours, dynamic resolution, multi-page.
- bai2025qwen25vl: VERIFIED (author list completed in .bib from arXiv: 27 authors, last Lin, Junyang). arXiv 2502.13923 (19 Feb 2025); abstract confirms three sizes, structured extraction from invoices/forms/tables, 72B matching GPT-4o and Claude 3.5 Sonnet in document and diagram understanding.
- poznanski2025olmocr: VERIFIED. arXiv 2502.18443 (v1 25 Feb 2025, latest 2 Jul 2025); 9 authors as listed (arXiv metadata duplicates "Aman Rangapur", a listing artefact); abstract confirms 7B VLM, olmOCR-mix-0225 260,000 pages from 100,000+ PDFs, US$176 per million pages vs >US$6,240 for GPT-4o, olmOCR-Bench 1,400 PDFs, beats GPT-4o / Gemini Flash 2 / Qwen-2.5-VL.
- cui2025paddleocrvl: VERIFIED (author list completed in .bib: 18 authors, last Ma, Yanjun). arXiv 2510.14528 (v1 16 Oct 2025, latest 25 Nov 2025); abstract confirms 0.9B, NaViT-style dynamic-resolution encoder + ERNIE-4.5-0.3B, 109 languages, SOTA page-level and element-level claims.
- wei2025deepseekocr: VERIFIED. arXiv 2510.18234 (21 Oct 2025), 3 authors; abstract confirms ~97% precision below 10x compression, ~60% at 20x, beats GOT-OCR2.0 with 100 vision tokens, MinerU2.0 with <800, 200k+ pages/day on one A100-40G.
- bai2025qwen3vl: VERIFIED (arXiv 2511.21631, v1 26 Nov 2025, v2 27 Nov 2025; dense 2B/4B/8B/32B plus MoE 30B-A3B/235B-A22B and 256K context confirmed in abstract; 62 authors, .bib truncated with "others"). Section 5.4 OCR benchmark claims and third-party OCRBench ~920 figures were NOT checked: [UNVERIFIED] any specific Qwen3-VL OCR score.
- guo2017calibration: VERIFIED. PMLR v70 pp. 1321-1330, editors Precup and Teh, temperature-scaling wording confirmed; arXiv 1706.04599 comment "ICML 2017".
- slossberg2022calibration: CORRECTED. Crossref gives the published version: Computer Vision - ECCV 2022 Workshops, LNCS, pp. 263-279, DOI 10.1007/978-3-031-25069-9_18, issued 2023 (conference 2022); nine authors match. Notes had no DOI or pages and venue was unconfirmed. Numerical claims (overconfident STR models, up to ~7x error reduction) not re-checked against the paper [UNVERIFIED numbers].
- peng2023perception: CORRECTED. Crossref confirms CVPR 2023 (June 2023), pp. 10658-10668, DOI 10.1109/CVPR52729.2023.01027; venue no longer inferred. Authors match arXiv 2305.19498.
- pizer1987adaptive: VERIFIED. Crossref: CVGIP 39(3) 355-368, Sep 1987, nine authors match.
- zuiderveld1994contrast: CORRECTED. Crossref confirms title, author, pp. 474-485, 1994, ISBN 9780123361561. Added volume IV and editor Heckbert from the ISBN (not in the Crossref record) and publisher Academic Press.
- tavares2024comparison: VERIFIED. arXiv 2410.13622 (15 Oct 2024), single author; full text confirms EasyOCR, baseline 71.7%, grayscale/CLAHE/bilateral 70.75% each, CLAHE "did not bring significant benefits", runtime 7.26 s to 8.87 s. Image count not stated in the paper.
- he2025seeing: VERIFIED with discrepancy. arXiv 2506.20168 (v1 25 Jun 2025, v2 22 Sep 2025), "Accepted by NeurIPS 2025". v2 Table 1 confirms avg 58.05 vs GPT-4o 30.21 and not-clear 61.34 vs 36.13. The v2 abstract says 22% absolute gain over GPT-4o while the HTML body says ~28%; notes' 28% matches only the body, so cite carefully. Table row labelled Qwen2.5-VL-8B and 72B shows identical numbers (24.19 not-clear), so the notes' "Qwen2.5-VL 24.19" is unreliable [UNVERIFIED]. Abstract lists identity cards and invoices, the body also prescriptions. Quotes on linguistic priors and "values not present in the image" confirmed.
- guan2026teaching: VERIFIED. mlanthology and OpenReview forum zyCjizqOxB: ICLR 2026, five authors, uncertainty-tag F1 0.685, Blur-OCR, GRPO. Source describes degraded document images. .bib url set to OpenReview.
- fu2024ocrbenchv2: VERIFIED. arXiv 2501.00321 (v1 31 Dec 2024, v2 5 Jun 2025); abstract confirms 4x tasks, 31 scenarios, 10,000 QA pairs, private 1,500 images, most LMMs below 50, "less frequently encountered text recognition" and "fine-grained perception". Full 24-author list added.
- yao2025reading: VERIFIED. arXiv 2511.19806 (25 Nov 2025), seven authors match; abstract confirms 50 vs 60 mph example, 7.6% abstention gain, four benchmarks, intermediate-layer signals. Peer-review status [UNVERIFIED]; cite as preprint.
- pharmacymagazine2022newai: VERIFIED (web, news; not peer reviewed). Page confirms Training Matters, 13 Oct 2022, Haleon-commissioned 2022 survey of 502 visually impaired UK people, 93%, almost one in five wrong dosage, Seeing AI, 1,500+ products, barcode scanning.
- DSCSA / EU FMD identifier statements and Vitronic VICODE 2008: UNVERIFIED (primary texts not opened by researcher or verifier); claims resting on them are [UNVERIFIED]; not in .bib.
- US 12697718 patent on embossed blister batch codes: UNVERIFIED (Google Patents URL returned 404, number may be wrong); the foil-difficulty statement resting on it is [UNVERIFIED]; not in .bib.
- ExpDate Hugging Face mirror (dimun/dates) and Seker "six sub-datasets": UNVERIFIED (not checked / not in abstract); not in .bib.
- The BibTeX block earlier in these notes is the researcher's draft; packaging_ocr.bib is the verified version and differs for kim2023implementation, peng2025efficient, slossberg2022calibration, peng2023perception, zuiderveld1994contrast, guan2026teaching, fu2024ocrbenchv2, bai2025qwen25vl and cui2025paddleocrvl.

Verification: COMPLETE

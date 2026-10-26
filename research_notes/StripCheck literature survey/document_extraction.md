Status: COMPLETE

# Document and table extraction, schema matching/drift, validation and LLM-assisted repair (background for StripCheck ingest agent)

Overall takeaways (for the Related Work writer)
- Tiering is supported: rule-based text-layer extraction is adequate on ruled machine-generated tables but has low recall elsewhere (Adhikari and Agarwal 2024/25); learned structure models (TATR, TableFormer inside Docling) are the laptop-feasible fallback.
- LLM output needs span-grounding (SafePassage, LangExtract, AXE) and schema constraints (Outlines, JSONSchemaBench); constrained formats may hurt reasoning (Tam et al. 2024).
- Header mapping = schema matching (Rahm and Bernstein 2001); LLM matchers (Parciak 2024, ReMatch 2024, Magneto 2025) are candidate generators needing verification.
- Validation/quarantine have solid precedents (Deequ 2018, Breck 2019, dead-letter pattern); regulator data is itself messy (FDA RES 19 to 29% missing responsible firm). No peer-reviewed work on regulator alert-table extraction was found: state this as a gap/novelty.
- Many sources are arXiv preprints; flagged individually. Dates: all facts accessed 25 Oct 2026.

Checklist
- [x] KQ1 Rule-based PDF table tools (pdfplumber, Camelot, Tabula) and comparative evaluations
- [x] KQ2 Deep table structure recognition / document understanding (TableNet, TATR/PubTables-1M, DocLayNet, TableFormer, LayoutLM, Donut, Nougat, Docling, 2025-26 systems)
- [x] KQ3 LLM-based structured extraction with JSON schemas and grounding checks
- [x] KQ4 Schema matching (Rahm and Bernstein 2001), LLM-based schema matching 2024-26, schema/layout drift
- [x] KQ5 Data validation (Breck 2019, Deequ 2018, Great Expectations), quarantine/dead-letter, regulator recall data extraction (FDA, openFDA)

## KQ1 Rule-based PDF table tools and comparative evaluations

### Takeaway
Rule-based tools (pdfplumber, Camelot, Tabula, PyMuPDF) work on ruled/fixed-column machine-generated PDFs but have low recall on diverse layouts; the only independent comparison found (Adhikari and Agarwal, arXiv 2024/2025) shows a learned detector (TATR) beating them on most categories while Camelot wins on government tenders. This supports "rule-based first, fallback when validation fails" for CDSCO PDFs.

### Cited Findings
- Adhikari and Agarwal compared 10 parsers (PyPDF, pdfminer.six, PyMuPDF, pdfplumber, pypdfium2, Unstructured, Tabula, Camelot, Nougat, TATR) on DocLayNet pages in 6 categories (Financial, Law and Regulations, Manual, Patent, Scientific, Government Tenders); text-extraction used 800 balanced documents per category. For table detection, TATR was best in Financial, Patent, Law and Regulations, Scientific; Camelot best on Government Tenders (recall 0.72); Tabula best recall in Manual, Scientific, Patent among rule-based tools; PyMuPDF best in Manual and most consistent among rule-based. Rule-based tools had low recall everywhere except Manual and Tender. — [Adhikari and Agarwal, arXiv:2410.09871 (v1 13 Oct 2024, v2 3 Apr 2025; preprint, no venue stated)](https://arxiv.org/abs/2410.09871)
  - Relevance: the closest thing to a comparative evaluation including Government Tenders/Law documents; shows rule-based success depends on clear table boundaries and fixed column spacing, so CDSCO PDFs (ruled tables) are favourable but format change (Aug 2025) can break them. Supports the validate-then-fallback design. Caveat: table "detection" was scored by text similarity (Levenshtein/Jaccard thresholds) because rule-based tools return no bounding boxes, not by cell-structure metrics.
- Same paper lists failure modes of rule-based parsers: nested tables, no table boundary, table-of-contents style tables, multiple tables per page, colour-separated rows, columns separated by dot leaders; it concludes learning-based approaches suit complex tables. — [arXiv:2410.09871](https://arxiv.org/abs/2410.09871)
- pdfplumber README: table finding has `vertical_strategy`/`horizontal_strategy` in {lines, lines_strict, text, explicit}; `snap_tolerance` default 3; MIT licence; "works best on machine-generated, rather than scanned, PDFs", no OCR, weak support for OCR'd documents. Release date/version not shown on the page I opened (unconfirmed). — [pdfplumber GitHub README](https://github.com/jsvine/pdfplumber) (accessed 25 Oct 2026)
  - Relevance: the `explicit`/`text` strategies let the ingest agent fix a layout per-source; scanned CDSCO PDFs would need a different path.
- Camelot's own comparison page (vendor documentation, so self-interested) describes `lattice` (ruled lines) and `stream` (whitespace) modes, says Tabula needs a JVM and auto-detects stream tables better, pdfplumber exposes low-level layout objects, PyMuPDF is AGPL; "last verified" dates of 21-25 May 2026 (tabula-java 1.0.5/tabula-py 2.10, pdfplumber 0.11.5, PyMuPDF 1.24.x, tablers 0.7.3). Its own benchmark on 67 ruled-heavy ICDAR-2013 PDFs reports Camelot lattice F1 0.778 vs tablers 0.750 (times 101 s vs 1.5 s); its TEDS is a difflib text proxy, not true TEDS. — [Camelot documentation, "How Camelot compares to other tools"](https://camelot-py.readthedocs.io/en/latest/user/comparison.html) (accessed 25 Oct 2026)
  - Relevance: source for tool characteristics only; do not cite its benchmark as independent evidence.

### Inferences
- For CDSCO PDFs (ruled tables, machine-generated), pdfplumber lines strategy or Camelot lattice is the cheap deterministic first pass; a changed layout would appear as low recall/column-count mismatch, which the validation layer must catch before an LLM/vision fallback runs.

### Gaps
- No peer-reviewed head-to-head of pdfplumber vs Camelot vs Tabula on cell-structure metrics (TEDS) was found; Tabula's own docs were not opened. pdfplumber latest release date not confirmed.

## KQ2 Deep table structure recognition and document understanding

### Takeaway
Learned table models progressed from segmentation (TableNet 2019) to object-detection transformers (TATR, PubTables-1M 2021/22), image-to-sequence (TableFormer 2022), OCR-free (Donut 2021/22, Nougat 2023) and compact VLM converters (SmolDocling 2025). Docling packages DocLayNet layout + TableFormer in an MIT-licensed, laptop-runnable toolkit, which fits an offline Windows setup.

### Cited Findings
- TableNet: single end-to-end network that segments table and column regions of scanned document images, then a rule-based step extracts rows; reports state-of-the-art on ICDAR 2013 and Marmot; adds Marmot structure annotations. arXiv:2001.01469 (6 Jan 2020). arXiv page does not state the venue (I believe ICDAR 2019, but did not confirm it from an opened source). — [Paliwal et al.](https://arxiv.org/abs/2001.01469)
  - Relevance: early deep baseline for scanned tables; shows the "learned detect + rule-based row extraction" hybrid pattern.
- PubTables-1M: nearly one million tables from scientific articles with complete header/location ground truth; a canonicalization step fixes "oversegmentation"; DETR-style transformer detectors give strong detection, structure recognition and functional analysis without task-specific customization (this arXiv page gives no metric numbers). arXiv v1 30 Sep 2021, v3 18 Nov 2021; published at CVPR 2022 (venue per search-result listing of the CVF page; the CVF page itself returned HTTP 403 so page numbers are unconfirmed). Code: microsoft/table-transformer. — [Smock, Pesala and Abraham, arXiv:2110.00061](https://arxiv.org/abs/2110.00061)
  - Relevance: provenance of TATR, the best table detector in the Adhikari and Agarwal comparison.
- TableFormer: replaces LSTM decoders with transformers and adds a cell object-detection decoder so that, for programmatic PDFs, cell text is copied from the PDF rather than OCR-decoded; reports TEDS 91 to 98.5% (simple tables) and 88.7 to 95% (complex tables). arXiv:2203.01017, 2 Mar 2022 (v2 11 Mar 2022); arXiv page lists no peer-reviewed venue. — [Nassar et al.](https://arxiv.org/abs/2203.01017)
  - Relevance: the "take text from the PDF layer, structure from the model" idea avoids OCR/LLM transcription errors on digits, directly relevant to batch numbers.
- DocLayNet: 80,863 manually annotated pages, 11 layout classes, COCO format, from diverse sources; models trained on it are more robust than ones trained on PubLayNet/DocBank; baselines about 10% below inter-annotator agreement. Accepted at SIGKDD 2022 (per arXiv comments field). — [Pfitzmann et al., arXiv:2206.01062](https://arxiv.org/abs/2206.01062)
  - Relevance: includes Government Tenders and Law and Regulations categories, the nearest benchmark to regulator documents.
- Donut: OCR-free Transformer for document understanding, motivated by OCR cost, inflexibility and error propagation; ECCV 2022 (per arXiv comments); code and synthetic data generator released. Page gives no numeric results. — [Kim et al., arXiv:2111.15664](https://arxiv.org/abs/2111.15664)
- LayoutLMv3: unified text-and-image masking with word-patch alignment; reports SOTA on form/receipt understanding, DocVQA, document classification and layout analysis; ACM Multimedia 2022 (per arXiv comments). Not opened: LayoutLM v1 (KDD 2020) and v2 (ACL 2021). — [Huang et al., arXiv:2204.08387](https://arxiv.org/abs/2204.08387)
- Nougat: Visual Transformer that converts scientific page images to markup; arXiv:2308.13418 (25 Aug 2023); arXiv page does not state a venue. Adhikari and Agarwal found it better than rule-based parsers on scientific text but their Nougat sample was small. — [Blecher et al.](https://arxiv.org/abs/2308.13418)
- Docling Technical Report: open-source MIT-licensed PDF converter using DocLayNet-trained layout analysis and TableFormer; designed for commodity hardware; arXiv:2408.09869 (19 Aug 2024; v5 9 Dec 2024), preprint. — [Auer et al.](https://arxiv.org/abs/2408.09869)
- SmolDocling: 256M-parameter VLM that converts whole pages to a markup called DocTags; claims to compete with VLMs up to 27 times larger; arXiv:2503.11576 (14 Mar 2025). No speed figures on the abstract page. — [Nassar et al.](https://arxiv.org/abs/2503.11576)

- Docling toolkit paper: parses multiple formats into one structured representation using DocLayNet + TableFormer; MIT, commodity hardware; integrations with LangChain, LlamaIndex, spaCy; accepted to the AAAI 2025 Workshop on Open-Source AI for Mainstream Use; arXiv:2501.17887 (27 Jan 2025). Adoption claims (10k GitHub stars in under a month) are not evaluation results. — [Livathinos et al.](https://arxiv.org/abs/2501.17887)
  - Relevance: the most practical laptop-local learned fallback for PDF tables; has a Python API/CLI and LangChain integration, which matches a LangGraph agent.
- PaddleOCR 3.0: Apache-licensed toolkit with PP-OCRv5 (multilingual recognition), PP-StructureV3 (hierarchical document parsing) and PP-ChatOCRv4 (key information extraction); claims models under 100M parameters rival billion-parameter VLMs; arXiv:2507.05595 (8 Jul 2025). No benchmark numbers on the abstract page I opened. — [Cui et al.](https://arxiv.org/abs/2507.05595)
  - Relevance: same ecosystem as StripCheck's PP-OCR reader, so PP-StructureV3 can be a scanned-PDF table fallback without a new dependency family.

### Inferences
- A tiered design is defensible: text-layer table tools first, Docling/TableFormer-class model for layout drift, small VLM (SmolDocling-class) only as a last-resort reader, each output passing the same validators.

### Gaps
- Not opened: LayoutLM v1/v2, numeric benchmark tables of Docling/SmolDocling/PaddleOCR 3.0 (only abstract pages read), other 2025-26 systems (e.g. MinerU, olmOCR) not searched. TableNet's ICDAR 2019 venue and the CVPR 2022 page numbers of PubTables-1M could not be confirmed from an opened page.

## KQ3 LLM-based structured extraction with JSON schemas and grounding

### Takeaway
Schema-constrained decoding guarantees syntactic validity, not factual fidelity, and strict format constraints can reduce reasoning quality; faithfulness needs a separate grounding check that each extracted value is found in the source text. For StripCheck this means every LLM-repaired cell must be verified as a substring/aligned span of the source row or be quarantined.

### Cited Findings
- Outlines: casts generation as transitions of a finite-state machine so output can follow regexes and context-free grammars via a vocabulary index, with little per-token overhead; arXiv:2307.09702 (19 Jul 2023, v4 19 Aug 2023). — [Willard and Louf](https://arxiv.org/abs/2307.09702)
- JSONSchemaBench: 10K real-world JSON schemas plus the official JSON Schema Test Suite; evaluates six constrained-decoding frameworks (Guidance, Outlines, Llamacpp, XGrammar, OpenAI, Gemini) on efficiency, coverage and quality; arXiv:2501.10868 (18 Jan 2025, v3 27 Feb 2025). The title on the current arXiv page is "JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models"; a web-search listing showed an ICML 2025 workshop version under a different title (not opened). Per-framework scores were not on the page I opened. — [Geng et al.](https://arxiv.org/abs/2501.10868)
  - Relevance: Llamacpp and Outlines are the locally runnable options (Ollama supports JSON-schema `format` — not verified here); coverage differs by schema complexity, so keep the CDSCO row schema flat.
- "Let Me Speak Freely?": comparing format-restricted (JSON/XML) with free-form output, the authors observe a significant decline in LLM reasoning under format restrictions, larger for stricter constraints; arXiv:2408.02442 (5 Aug 2024, v3 14 Oct 2024); venue not confirmed (preprint). No numbers on the abstract page. — [Tam et al.](https://arxiv.org/abs/2408.02442)
  - Relevance: for the small local LLM, reasoning/diagnosis (what changed in the table) should be a free-text step followed by a separate constrained "emit mapping JSON" step.
- SafePassage: three-stage black-box pipeline (LLM extractor outputs entities with context; string-based global aligner; scoring model) that requires each extraction be backed by a snippet from the source; reports hallucinations reduced by up to 85%, with 1-2 hours of task-specific annotation; fine-tuned encoder beat an LLM scorer; arXiv:2510.00276 (30 Sep 2025), preprint. — [Barrow et al.](https://arxiv.org/abs/2510.00276)
  - Relevance: closest published match to "grounded repair": align extracted value to source text and reject unsupported values. Supports StripCheck's rule that a repaired cell must appear in the source row.
- AXE: prunes the HTML DOM so a 0.6B LLM can extract structured data, and adds Grounded XPath Resolution that ties every extraction to its source node; F1 88.1% on SWDE zero-shot; arXiv:2602.01838 (2 Feb 2026, v2 30 Mar 2026), preprint. — [Mansour et al.](https://arxiv.org/abs/2602.01838)
  - Relevance: relevant to the HTML table path and to small local models; grounding to a source node is the HTML analogue of span grounding.
- LangExtract (Google, software, Apache-2.0, v1.6.0 per its 2026 citation block): maps each extraction to its exact char interval in the source; extractions not locatable get `char_interval = None` and can be filtered; custom output schema supported for Gemini and OpenAI but not Ollama. DOI on the page is internally inconsistent (two different Zenodo DOIs). No associated paper. — [LangExtract GitHub](https://github.com/google/langextract) (accessed 25 Oct 2026)
  - Relevance: shows the span-grounding pattern in a tool; the Ollama schema limitation matters for StripCheck's offline requirement.

### Inferences
- Combining these: (1) constrained decoding for syntax, (2) free-text reasoning kept separate, (3) deterministic span-grounding check for every value, (4) failures go to quarantine, not to a retry loop that can fabricate.

### Gaps
- No peer-reviewed study of LLM hallucination specifically in table-cell transcription from PDFs was found in the searches run; SafePassage and AXE are preprints. Ollama structured-output behaviour not verified from its documentation.

## KQ4 Schema matching, LLM-based schema matching, and drift

### Takeaway
Header mapping after a format change is a classic schema-matching problem (Rahm and Bernstein 2001). LLM-based matchers (2024-25) work from names and descriptions with moderate context and are best used as candidate generators whose output is verified; drift practice (Delta Lake / Auto Loader) is "auto-adapt additive changes, block or rescue breaking ones", which maps to StripCheck's quarantine-on-uncertain-mapping rule.

### Cited Findings
- Rahm and Bernstein, "A survey of approaches to automatic schema matching", The VLDB Journal 10(4):334-350, December 2001, DOI 10.1007/s007780100057 (bibliographic data verified via Crossref; the paper's full text was not opened). A search-result summary (Leipzig bibliography, not opened) describes its taxonomy along schema-level vs instance-level, element-level vs structure-level, and language-based vs constraint-based matchers, with about 2,961 citations per that bibliography. — [Crossref record](https://api.crossref.org/works/10.1007/s007780100057)
  - Relevance: foundational taxonomy; StripCheck's header mapper is an element-level, language-based matcher (synonym dictionary, string similarity) plus instance-level checks (value patterns such as batch format, date formats).
- Parciak et al.: tests an off-the-shelf LLM matching two relational schemas from names and descriptions only, on a health-domain benchmark, with "task scopes" varying prompt context; quality suffers from too little and too much context; newer LLMs are more decisive; some scopes keep verification effort acceptable; LLMs can help bootstrap matching. Workshop on Tabular Data Analysis (TaDA24) at VLDB 2024, Guangzhou, 29 Aug 2024; arXiv:2407.11852 (16 Jul 2024). No numbers on the abstract page. — [Parciak et al.](https://arxiv.org/abs/2407.11852)
  - Relevance: supports giving the local LLM only the old/new header lists plus short column descriptions, and treating its output as a proposal needing human/rule confirmation ("verification effort").
- ReMatch: retrieval-enhanced schema matching; represents target tables/attributes as documents, retrieves top candidates per source attribute, then one LLM prompt per source table returns ranked matches; needs no predefined mappings, training or access to source data; evaluated on MIMIC-III to OMOP and Synthea to OMOP against SMAT (per search summary); arXiv:2403.01567 (3 Mar 2024, v2 30 May 2024), preprint. — [Sheetrit et al.](https://arxiv.org/abs/2403.01567)
  - Relevance: the "retrieve, then rank" shape fits mapping a handful of new headers onto a small canonical schema (target schema of about 10 fields), where retrieval is almost trivial.
- Magneto: two-phase pipeline in which small language models retrieve candidate column matches and LLMs rerank; self-supervised fine-tuning of SLMs using LLM-generated data; new biomedical benchmark; PVLDB 18(8):2681-2694, 2025, DOI 10.14778/3742728.3742757 (venue data from Crossref; abstract from VLDB page; arXiv:2412.08194). No numeric results on the pages opened. — [Liu et al.](https://vldb.org/pvldb/volumes/18/paper/Magneto%3A%20Combining%20Small%20and%20Large%20Language%20Models%20for%20Schema%20Matching)
  - Relevance: validates a cheap-first/LLM-rerank cascade, matching StripCheck's deterministic mapper with LLM fallback.
- Narayan et al.: casts five data cleaning/integration tasks (including schema matching) as prompts; large foundation models reach state-of-the-art without task-specific training; arXiv:2205.09911 (20 May 2022); venue not stated on the page (I believe PVLDB 2022, unconfirmed). — [Narayan et al.](https://arxiv.org/abs/2205.09911)
- Schema-drift practice (vendor training material; metadata states `ai-usage: ai-generated`, `ms.date` 2 Oct 2026): Delta Lake rejects structural mismatches by default; Auto Loader has five schema-evolution modes (`addNewColumns` default, `rescue`, `failOnNewColumns`, `none`, `addNewColumnsWithTypeWidening`); a `_rescued_data` column keeps mismatching data without stopping the stream; recommends versioned schema definitions and alerting. — [Microsoft Learn, "Detect and manage schema drift"](https://learn.microsoft.com/en-us/training/modules/implement-manage-data-quality-constraints-unity-catalog/4-detect-manage-schema-drift)
  - Relevance: concrete vocabulary (fail, evolve, rescue) for ingest policies; CDSCO's Aug 2025 change (header rename/reorder) is a "breaking" drift needing a mapping decision, not silent evolution.

### Inferences
- A defensible mapping policy: exact/normalized header match, then synonym/fuzzy, then LLM proposal; accept only if the mapped columns' values pass per-column validators (batch regex, date parse, non-empty product); otherwise rescue the whole file to quarantine and alert.

### Gaps
- No peer-reviewed paper on drift in regulator/government PDF tables specifically was found; schema-drift literature found is practitioner documentation. Rahm and Bernstein full text not opened; Magneto/ReMatch numeric results not read.

## KQ5 Data validation, quarantine, and regulator recall-data extraction

### Takeaway
Data validation as unit tests for data (Deequ 2018, TFX data validation 2019, Great Expectations) and the dead-letter/quarantine pattern are established; regulator recall data itself is known to be messy (FDA's own RES review found missing/inconsistent responsible-firm data in 19 to 29% of recalls per fiscal year; duplicate event IDs inflate counts). I found no peer-reviewed work on extracting recall tables from regulator documents.

### Cited Findings
- Breck et al., "Data Validation for Machine Learning": data validation system for ML pipelines deployed in TFX, used by hundreds of product teams over several petabytes of data per day; addresses keeping pipelines running despite unexpected patterns, schema-free data and training/serving skew; reports earlier error detection and less debugging time. Google Research page lists it as SysML 2019 ("to appear"); the venue became MLSys 2019 (Proceedings of Machine Learning and Systems 1); page numbers not confirmed. — [Google Research publication page](https://research.google/pubs/data-validation-for-machine-learning/)
  - Relevance: schema-as-contract with anomaly reports; supports a versioned canonical schema with validators gating inserts.
- Schelter et al., "Automating large-scale data quality verification", PVLDB 11(12):1781-1794, August 2018, DOI 10.14778/3229863.3229867: declarative API mixing standard constraints with user code (unit tests for data), run as Spark aggregation queries, incremental validation, ML-based constraint suggestion and anomaly detection (Deequ). — [Amazon Science page](https://www.amazon.science/publications/automating-large-scale-data-quality-verification); bibliographic data via [Crossref](https://api.crossref.org/works/10.14778/3229863.3229867)
  - Relevance: declarative constraints (completeness, uniqueness, pattern, range) are the model for StripCheck's row validators; Spark scale is not needed.
- Great Expectations (GX Core): open-source Python package, Apache-2.0, docs show version 1.24.1 on 25 Oct 2026; Expectations described as "unit tests for your data"; the pages opened did not explain unexpected-row reporting. — [GitHub repository](https://github.com/great-expectations/great_expectations); [docs home](https://docs.greatexpectations.io/docs/home/) (both accessed 25 Oct 2026)
  - Relevance: usable off the shelf locally, but a small custom validator set may be lighter for a SQLite pipeline.
- Dead Letter Channel (Enterprise Integration Patterns): messages the system cannot or should not deliver go to a dead-letter channel; examples Amazon SQS (receive-count limit then Dead Letter Queue) and Kafka Connect dead-letter topic. The page does not name the book's authors (authorship Hohpe and Woolf is from general knowledge, not confirmed on the page); copyright line shows 2003, 2023. — [enterpriseintegrationpatterns.com](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html)
  - Relevance: origin of the quarantine idea; Microsoft Learn also shows a quarantine-table pattern (separate table for rows violating rules while valid rows proceed). — [Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/implement-manage-data-quality-constraints-unity-catalog/4-detect-manage-schema-drift)
- openFDA drug enforcement endpoint: data from FDA's Recall Enterprise System, publicly releasable records from 2004, updated weekly; warns not to use it for public alerts or for tracking recall lifecycle; recall status is not updated after classification; FDA may correct earlier records (e.g. more lots added). — [openFDA drug enforcement](https://open.fda.gov/apis/drug/enforcement/) (accessed 25 Oct 2026)
  - Relevance: precedent for a structured regulator recall feed, and a caution that alert records are revised: StripCheck's index should store a fetch date and re-check saved batches.
- FDA/CDER poster, "Recall Enterprise System (RES) Data Quality Improvements to Address Opioid Epidemic" (Nadeem et al., FDA; undated in the text, covers FY2020 to FY2023 partial): CDER found missing or inaccurate Responsible Firm identifiers in a substantial number of recalls; share of drug recalls with missing Responsible Firm data rose from 20% (FY2020) to 29% (FY2022), then 19% for FY2023 to date after making the field mandatory. — [FDA poster PDF](https://www.fda.gov/media/168771/download)
  - Relevance: primary evidence that regulator records have missing/inconsistent fields, motivating validation, null-tolerant schema and "CANT_VERIFY" over guessing.
- Redica Systems blog (industry, not peer-reviewed; 23 Mar 2023): raw FDA recall data gives one event ID per product preparation, so 538 label-related entries came from two recalls; more than 13,000 entries collapse to about 3,000 events for 2012 to 2021. — [Redica](https://www.redica.com/resources/post/is-raw-fda-data-skewing-your-analyses)
  - Relevance: duplicates/aggregation unit issue; StripCheck needs de-duplication keyed on (batch, product, month, source) and must not count rows as events.
- LLM-assisted cleaning: LLMClean (Biester et al., arXiv:2404.18681, 29 Apr 2024, preprint) uses LLMs to generate context models (ordering/dependency rules) for cleaning, comparable to expert-written ones on three datasets (no numbers on page). — [arXiv](https://arxiv.org/abs/2404.18681)
  - Relevance: LLM writes rules, deterministic code applies them: a safer repair division of labour than LLM rewriting cells.

### Inferences
- Pipeline shape supported by the sources: validate each row (constraints), quarantine failures with reason codes, allow LLM repair only if the proposed value is grounded in the source span and re-passes validators, and cross-check counts between JSON, PDF and HTML renditions of the same month (agreement check). No source tested cross-source agreement for regulator lists, so this is a design inference.

### Gaps
- No peer-reviewed study of automated extraction of recall/alert tables from FDA or CDSCO documents found. openFDA field-format inconsistencies not described on the page opened. Great Expectations unexpected-row reporting not verified. Breck et al. MLSys page numbers unconfirmed; Hohpe and Woolf book details unconfirmed from an opened source.

## BibTeX

@misc{adhikari2024comparative,
  author = {Adhikari, Narayan S. and Agarwal, Shradha},
  title = {A Comparative Study of {PDF} Parsing Tools Across Diverse Document Categories},
  year = {2024},
  eprint = {2410.09871},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2410.09871},
  note = {Preprint; v1 13 Oct 2024, v2 3 Apr 2025. Accessed 25 Oct 2026}
}
@misc{plumber2026readme,
  author = {Singer-Vine, Jeremy and contributors},
  title = {pdfplumber: Plumb a {PDF} for detailed information about each char, rectangle, line, et cetera, and easily extract text and tables},
  url = {https://github.com/jsvine/pdfplumber},
  note = {Accessed 25 Oct 2026. Author attribution (Jeremy Singer-Vine) from general knowledge, not shown on the page opened}
}
@misc{camelot2026comparison,
  author = {{Camelot contributors}},
  title = {How Camelot compares to other tools},
  url = {https://camelot-py.readthedocs.io/en/latest/user/comparison.html},
  note = {Vendor documentation. Accessed 25 Oct 2026}
}
@misc{paliwal2020tablenet,
  author = {Paliwal, Shubham and D, Vishwanath and Rahul, Rohit and Sharma, Monika and Vig, Lovekesh},
  title = {{TableNet}: Deep Learning model for end-to-end Table detection and Tabular data extraction from Scanned Document Images},
  year = {2020},
  eprint = {2001.01469},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2001.01469},
  note = {Published at ICDAR 2019 (not confirmed from an opened source). Accessed 25 Oct 2026}
}
@misc{smock2021pubtables,
  author = {Smock, Brandon and Pesala, Rohith and Abraham, Robin},
  title = {{PubTables-1M}: Towards comprehensive table extraction from unstructured documents},
  year = {2021},
  eprint = {2110.00061},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2110.00061},
  note = {Appeared at CVPR 2022 (CVF page returned 403; pages not confirmed). Accessed 25 Oct 2026}
}
@misc{nassar2022tableformer,
  author = {Nassar, Ahmed and Livathinos, Nikolaos and Lysak, Maksym and Staar, Peter},
  title = {{TableFormer}: Table Structure Understanding with Transformers},
  year = {2022},
  eprint = {2203.01017},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2203.01017},
  note = {Accessed 25 Oct 2026}
}
@misc{pfitzmann2022doclaynet,
  author = {Pfitzmann, Birgit and Auer, Christoph and Dolfi, Michele and Nassar, Ahmed S. and Staar, Peter W. J.},
  title = {{DocLayNet}: A Large Human-Annotated Dataset for Document-Layout Analysis},
  year = {2022},
  eprint = {2206.01062},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2206.01062},
  note = {Accepted at SIGKDD 2022 per arXiv comments. Accessed 25 Oct 2026}
}
@misc{kim2021donut,
  author = {Kim, Geewook and Hong, Teakgyu and Yim, Moonbin and Nam, Jeongyeon and Park, Jinyoung and Yim, Jinyeong and Hwang, Wonseok and Yun, Sangdoo and Han, Dongyoon and Park, Seunghyun},
  title = {{OCR}-free Document Understanding Transformer},
  year = {2021},
  eprint = {2111.15664},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2111.15664},
  note = {ECCV 2022 per arXiv comments. Accessed 25 Oct 2026}
}
@misc{huang2022layoutlmv3,
  author = {Huang, Yupan and Lv, Tengchao and Cui, Lei and Lu, Yutong and Wei, Furu},
  title = {{LayoutLMv3}: Pre-training for Document {AI} with Unified Text and Image Masking},
  year = {2022},
  eprint = {2204.08387},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2204.08387},
  note = {ACM Multimedia 2022 per arXiv comments. Accessed 25 Oct 2026}
}
@misc{blecher2023nougat,
  author = {Blecher, Lukas and Cucurull, Guillem and Scialom, Thomas and Stojnic, Robert},
  title = {Nougat: Neural Optical Understanding for Academic Documents},
  year = {2023},
  eprint = {2308.13418},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2308.13418},
  note = {Accessed 25 Oct 2026}
}
@misc{auer2024docling,
  author = {Auer, Christoph and Lysak, Maksym and Nassar, Ahmed and Dolfi, Michele and Livathinos, Nikolaos and Vagenas, Panos and Berrospi Ramis, Cesar and Omenetti, Matteo and Lindlbauer, Fabian and Dinkla, Kasper and Mishra, Lokesh and Kim, Yusik and Gupta, Shubham and Teixeira de Lima, Rafael and Weber, Valery and Morin, Lucas and Meijer, Ingmar and Kuropiatnyk, Viktor and Staar, Peter W. J.},
  title = {Docling Technical Report},
  year = {2024},
  eprint = {2408.09869},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2408.09869},
  note = {Accessed 25 Oct 2026}
}
@misc{livathinos2025docling,
  author = {Livathinos, Nikolaos and Auer, Christoph and Lysak, Maksym and Nassar, Ahmed and Dolfi, Michele and Vagenas, Panos and Berrospi Ramis, Cesar and Omenetti, Matteo and Dinkla, Kasper and Kim, Yusik and Gupta, Shubham and Teixeira de Lima, Rafael and Weber, Valery and Morin, Lucas and Meijer, Ingmar and Kuropiatnyk, Viktor and Staar, Peter W. J.},
  title = {Docling: An Efficient Open-Source Toolkit for {AI}-driven Document Conversion},
  year = {2025},
  eprint = {2501.17887},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2501.17887},
  note = {AAAI 2025 Workshop on Open-Source AI for Mainstream Use. Accessed 25 Oct 2026}
}
@misc{cui2025paddleocr,
  author = {Cui, Cheng and Sun, Ting and Lin, Manhui and Gao, Tingquan and Zhang, Yubo and Liu, Jiaxuan and Wang, Xueqing and Zhang, Zelun and Zhou, Changda and Liu, Hongen and Zhang, Yue and Lv, Wenyu and Huang, Kui and Zhang, Yichao and Zhang, Jing and Zhang, Jun and Liu, Yi and Yu, Dianhai and Ma, Yanjun},
  title = {{PaddleOCR} 3.0 Technical Report},
  year = {2025},
  eprint = {2507.05595},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2507.05595},
  note = {Accessed 25 Oct 2026}
}
@misc{willard2023outlines,
  author = {Willard, Brandon T. and Louf, R{\'e}mi},
  title = {Efficient Guided Generation for Large Language Models},
  year = {2023},
  eprint = {2307.09702},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2307.09702},
  note = {Accessed 25 Oct 2026}
}
@misc{geng2025jsonschemabench,
  author = {Geng, Saibo and Cooper, Hudson and Moskal, Micha{\l} and Jenkins, Samuel and Berman, Julian and Ranchin, Nathan and West, Robert and Horvitz, Eric and Nori, Harsha},
  title = {{JSONSchemaBench}: A Rigorous Benchmark of Structured Outputs for Language Models},
  year = {2025},
  eprint = {2501.10868},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2501.10868},
  note = {Accessed 25 Oct 2026}
}
@misc{tam2024speak,
  author = {Tam, Zhi Rui and Wu, Cheng-Kuang and Tsai, Yi-Lin and Lin, Chieh-Yen and Lee, Hung-yi and Chen, Yun-Nung},
  title = {Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models},
  year = {2024},
  eprint = {2408.02442},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2408.02442},
  note = {Preprint; venue not confirmed. Accessed 25 Oct 2026}
}
@misc{barrow2025safepassage,
  author = {Barrow, Joe and Patel, Raj and Kharkovski, Misha and Davies, Ben and Schmitt, Ryan},
  title = {{SafePassage}: High-Fidelity Information Extraction with Black Box {LLMs}},
  year = {2025},
  eprint = {2510.00276},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2510.00276},
  note = {Preprint. Accessed 25 Oct 2026}
}
@misc{mansour2026axe,
  author = {Mansour, Abdelrahman and Alshaer, Khaled W. and Elsaban, Moataz},
  title = {{AXE}: Low-Cost Cross-Domain Web Structured Information Extraction},
  year = {2026},
  eprint = {2602.01838},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2602.01838},
  note = {Preprint; v2 30 Mar 2026. Accessed 25 Oct 2026}
}
@misc{goel2026langextract,
  author = {Goel, Akshay and contributors},
  title = {{LangExtract}},
  year = {2026},
  url = {https://github.com/google/langextract},
  note = {Software, Apache-2.0, v1.6.0 per its citation block; DOI on the page inconsistent. Accessed 25 Oct 2026}
}
@article{rahm2001survey,
  author = {Rahm, Erhard and Bernstein, Philip A.},
  title = {A survey of approaches to automatic schema matching},
  journal = {The VLDB Journal},
  volume = {10},
  number = {4},
  pages = {334--350},
  year = {2001},
  month = dec,
  doi = {10.1007/s007780100057},
  note = {Metadata verified via Crossref; full text not opened. Accessed 25 Oct 2026}
}
@inproceedings{parciak2024schema,
  author = {Parciak, Marcel and Vandevoort, Brecht and Neven, Frank and Peeters, Liesbet M. and Vansummeren, Stijn},
  title = {Schema Matching with Large Language Models: an Experimental Study},
  booktitle = {2nd International Workshop on Tabular Data Analysis (TaDA24), co-located with VLDB 2024},
  address = {Guangzhou, China},
  year = {2024},
  url = {https://arxiv.org/abs/2407.11852},
  note = {arXiv:2407.11852. Accessed 25 Oct 2026}
}
@misc{sheetrit2024rematch,
  author = {Sheetrit, Eitam and Brief, Menachem and Mishaeli, Moshik and Elisha, Oren},
  title = {{ReMatch}: Retrieval Enhanced Schema Matching with {LLMs}},
  year = {2024},
  eprint = {2403.01567},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2403.01567},
  note = {Preprint. Accessed 25 Oct 2026}
}
@article{liu2025magneto,
  author = {Liu, Yurong and Pena, Eduardo H. M. and Santos, A{\'e}cio and Wu, Eden and Freire, Juliana},
  title = {Magneto: Combining Small and Large Language Models for Schema Matching},
  journal = {Proceedings of the VLDB Endowment},
  volume = {18},
  number = {8},
  pages = {2681--2694},
  year = {2025},
  doi = {10.14778/3742728.3742757},
  url = {https://vldb.org/pvldb/volumes/18/paper/Magneto%3A%20Combining%20Small%20and%20Large%20Language%20Models%20for%20Schema%20Matching},
  note = {Accessed 25 Oct 2026}
}
@misc{narayan2022foundation,
  author = {Narayan, Avanika and Chami, Ines and Orr, Laurel and Arora, Simran and R{\'e}, Christopher},
  title = {Can Foundation Models Wrangle Your Data?},
  year = {2022},
  eprint = {2205.09911},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2205.09911},
  note = {Venue not confirmed from an opened source. Accessed 25 Oct 2026}
}
@misc{msft2026drift,
  author = {{Microsoft Learn}},
  title = {Detect and manage schema drift},
  year = {2026},
  url = {https://learn.microsoft.com/en-us/training/modules/implement-manage-data-quality-constraints-unity-catalog/4-detect-manage-schema-drift},
  note = {Vendor training module, page metadata dated 2 Oct 2026 and marked ai-generated. Accessed 25 Oct 2026}
}
@inproceedings{breck2019validation,
  author = {Breck, Eric and Zinkevich, Marty and Polyzotis, Neoklis and Whang, Steven and Roy, Sudip},
  title = {Data Validation for Machine Learning},
  booktitle = {Proceedings of Machine Learning and Systems (SysML/MLSys 2019)},
  year = {2019},
  url = {https://research.google/pubs/data-validation-for-machine-learning/},
  note = {Page numbers and proceedings volume not confirmed. Accessed 25 Oct 2026}
}
@article{schelter2018deequ,
  author = {Schelter, Sebastian and Lange, Dustin and Schmidt, Philipp and Celikel, Meltem and Biessmann, Felix and Grafberger, Andreas},
  title = {Automating large-scale data quality verification},
  journal = {Proceedings of the VLDB Endowment},
  volume = {11},
  number = {12},
  pages = {1781--1794},
  year = {2018},
  doi = {10.14778/3229863.3229867},
  note = {Accessed 25 Oct 2026}
}
@misc{gx2026core,
  author = {{Great Expectations}},
  title = {{GX Core} (great\_expectations)},
  year = {2026},
  url = {https://github.com/great-expectations/great_expectations},
  note = {Apache-2.0; docs version 1.24.1. Accessed 25 Oct 2026}
}
@misc{hohpe2003dlc,
  title = {Dead Letter Channel (Enterprise Integration Patterns)},
  url = {https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html},
  note = {Book authors not named on the page. Accessed 25 Oct 2026}
}
@misc{openfda2026enforcement,
  author = {{U.S. Food and Drug Administration}},
  title = {{openFDA} Drug Enforcement Reports {API}},
  url = {https://open.fda.gov/apis/drug/enforcement/},
  note = {Accessed 25 Oct 2026}
}
@misc{nadeem2023res,
  author = {Nadeem, Nida and Elder, Ileana and Litterello, David and Huff, Lavonia L. and Brykman, Raphael and Lundi, Carla and McIntyre, Ashley and Alexander, Angela and Ogonowski, Pamela and Hewitt, Kenitra},
  title = {Recall Enterprise System ({RES}) Data Quality Improvements to Address Opioid Epidemic},
  howpublished = {FDA poster},
  url = {https://www.fda.gov/media/168771/download},
  note = {Undated; covers FY2020 to FY2023 partial. Accessed 25 Oct 2026}
}
@misc{redica2023rawfda,
  author = {{Redica Systems}},
  title = {Is raw {FDA} data skewing your analyses?},
  year = {2023},
  month = mar,
  url = {https://www.redica.com/resources/post/is-raw-fda-data-skewing-your-analyses},
  note = {Industry blog, not peer-reviewed. Accessed 25 Oct 2026}
}
@misc{biester2024llmclean,
  author = {Biester, Fabian and Abdelaal, Mohamed and Del Gaudio, Daniel},
  title = {{LLMClean}: Context-Aware Tabular Data Cleaning via {LLM}-Generated {OFDs}},
  year = {2024},
  eprint = {2404.18681},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2404.18681},
  note = {Preprint. Accessed 25 Oct 2026}
}
@misc{nassar2025smoldocling,
  author = {Nassar, Ahmed and Marafioti, Andres and Omenetti, Matteo and Lysak, Maksym and Livathinos, Nikolaos and Auer, Christoph and Morin, Lucas and Teixeira de Lima, Rafael and Kim, Yusik and Gurbuz, A. Said and Dolfi, Michele and Farr{\'e}, Miquel and Staar, Peter W. J.},
  title = {{SmolDocling}: An ultra-compact vision-language model for end-to-end multi-modal document conversion},
  year = {2025},
  eprint = {2503.11576},
  archiveprefix = {arXiv},
  url = {https://arxiv.org/abs/2503.11576},
  note = {Accessed 25 Oct 2026}
}


## Verification log
(Verifier started 25 Oct 2026; entries appended incrementally.)
- adhikari2024comparative: VERIFIED via arXiv API and arXiv HTML full text (authors, title, 13 Oct 2024; 10 tools, 6 categories; Camelot recall 0.72 on Tender; Tabula and PyMuPDF recall statements match). Preprint; no venue.
- plumber2026readme: VERIFIED on GitHub README (MIT, "works best on machine-generated, rather than scanned, PDFs", strategies, snap_tolerance 3). CORRECTED: Jeremy Singer-Vine is listed as a maintainer alongside Samkit Jain, not sole author; .bib uses "pdfplumber contributors". Latest release version not shown on the page (that detail stays unverified).
- camelot2026comparison: VERIFIED (lattice/stream, JVM for Tabula, PyMuPDF AGPL, last-verified dates 21-25 May 2026, versions, 67-PDF ICDAR-2013 benchmark F1 0.778 vs 0.750, 101 s vs 1.5 s, difflib TEDS proxy). Detail: the 101 s is Camelot's "combined" engine (vector engine 13 s). Vendor documentation.
- paliwal2020tablenet: CORRECTED: venue confirmed via Crossref as ICDAR 2019, pp. 128-133, DOI 10.1109/ICDAR.2019.00029; .bib now cites the published ICDAR 2019 version (arXiv:2001.01469 posted Jan 2020).
- smock2021pubtables: CORRECTED: published at CVPR 2022, pp. 4624-4632, DOI 10.1109/CVPR52688.2022.00459 (Crossref); .bib cites the CVPR version (year 2022). arXiv:2110.00061 is the preprint.
- nassar2022tableformer: CORRECTED: notes cited arXiv only; Crossref shows CVPR 2022, pp. 4604-4613, DOI 10.1109/CVPR52688.2022.00457. TEDS claim (91 to 98.5 simple, 88.7 to 95 complex) matches the abstract, which frames them as improvements over the previous state of the art.
- pfitzmann2022doclaynet: CORRECTED: KDD 2022, DOI 10.1145/3534678.3539043 (arXiv API); 80,863 pages and 11 classes match the abstract.
- kim2021donut: CORRECTED: published at ECCV 2022, LNCS, pp. 498-517, DOI 10.1007/978-3-031-19815-1_29 (Crossref); .bib as inproceedings.
- huang2022layoutlmv3: CORRECTED: ACM Multimedia 2022, pp. 4083-4091, DOI 10.1145/3503161.3548112 (Crossref).
- blecher2023nougat: VERIFIED (arXiv API; 25 Aug 2023; no venue stated). Preprint.
- auer2024docling: VERIFIED (arXiv API: 19 authors, 19 Aug 2024, last update 9 Dec 2024; "Docling v1 report").
- livathinos2025docling: VERIFIED (17 authors; AAAI 25 Workshop on Open-Source AI for Mainstream Use; MIT, commodity hardware, 10k stars in under a month per abstract; adoption claim is not an evaluation result).
- cui2025paddleocr: VERIFIED (arXiv API: 19 authors, 8 Jul 2025; abstract matches Apache licence, PP-OCRv5, PP-StructureV3, PP-ChatOCRv4, models under 100M parameters). Preprint; no benchmark numbers were read.
- nassar2025smoldocling: VERIFIED (arXiv API: 13 authors, 14 Mar 2025; 256M parameters, DocTags, competes with VLMs up to 27 times larger). Preprint.
- willard2023outlines: VERIFIED (arXiv API; title "Efficient Guided Generation for Large Language Models", FSM index, regex and CFG; Outlines library). Preprint.
- geng2025jsonschemabench: VERIFIED (arXiv API and Semantic Scholar: title as in notes; 10K schemas, JSON Schema Test Suite, six frameworks). The notes' remark about a differently titled ICML workshop version was not resolved; cite the arXiv version. Preprint.
- tam2024speak: CORRECTED: published at EMNLP 2024 Industry Track, pp. 1218-1236, DOI 10.18653/v1/2024.emnlp-industry.91 (Crossref); published title is "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Large Language Model Performance" (arXiv title says "Performance of Large Language Models"). Notes' "venue not confirmed" is resolved. Claim (significant decline in reasoning, larger for stricter formats) matches the abstract.
- barrow2025safepassage: VERIFIED (arXiv API, 30 Sep 2025; three-stage pipeline, hallucinations reduced by up to 85%, 1-2 hours annotation, fine-tuned encoder can beat LLM scorer). Preprint.
- mansour2026axe: VERIFIED (arXiv API, 2 Feb 2026, v2 30 Mar 2026; 0.6B LLM, Grounded XPath Resolution, F1 88.1% on SWDE zero-shot). Preprint.
- goel2026langextract: VERIFIED on GitHub (Apache-2.0; v1.6.0 in citation block; char_interval = None for unlocatable extractions; output_schema supported for Gemini/OpenAI, not Ollama; single author Goel, Akshay in citation block). Two different Zenodo DOIs on the page (10.5281/zenodo.21126643 in citation block, 10.5281/zenodo.17015089 in badge), so no DOI is put in the .bib.
- rahm2001survey: VERIFIED via Crossref (Rahm and Bernstein, VLDB Journal 10(4):334-350, Dec 2001, DOI 10.1007/s007780100057). The "about 2,961 citations" figure in the notes comes from an unopened bibliography page and is [UNVERIFIED]; do not cite it.
- parciak2024schema: VERIFIED (arXiv API: 5 authors, 16 Jul 2024; TaDA24 at VLDB 2024, Guangzhou, 29 Aug 2024; abstract matches task-scopes, too little and too much context, decisiveness, verification effort).
- sheetrit2024rematch: VERIFIED (arXiv API and full text: 4 authors, 3 Mar 2024, v2 30 May 2024; retrieval then LLM ranked list of K matches per source attribute; MIMIC-III to OMOP and Synthea to OMOP compared against SMAT). Notes say "one LLM prompt per source table"; full text says the model yields a ranked list per source attribute given retrieved tables, so wording is approximate. Preprint.
- liu2025magneto: VERIFIED via Crossref (PVLDB 18(8):2681-2694, Apr 2025 issue, DOI 10.14778/3742728.3742757; authors Yurong Liu, Eduardo H. M. Pena, Aecio Santos, Eden Wu, Juliana Freire) and arXiv:2412.08194 abstract (retrieval by SLMs, LLM rerank, self-supervised fine-tuning, biomedical benchmark).
- narayan2022foundation: CORRECTED: published in PVLDB 16(4):738-746, Dec 2022, DOI 10.14778/3574245.3574258 (Crossref lists four authors: Narayan, Chami, Orr, Re; the arXiv version has five including Simran Arora). Notes' "venue unconfirmed, believe PVLDB 2022" is now confirmed.
- msft2026drift: VERIFIED on Microsoft Learn (ms.date 2 Oct 2026, ai-usage: ai-generated, author field weslbo; five Auto Loader modes; Delta Lake blocks structural mismatches by default; _rescued_data; quarantine-table example). CORRECTED nuance: the default addNewColumns mode stops the stream and adds new columns on restart (it is not silent auto-adaptation), so the notes' phrase "auto-adapt additive changes" should be read with that qualification. Vendor training material, not peer reviewed.
- breck2019validation: CORRECTED: MLSys 2019 (Proceedings of Machine Learning and Systems 1) page confirmed, published 2019-04-15; the MLSys page lists authors in the order Polyzotis, Zinkevich, Roy, Breck, Whang (Google Research page lists Breck first). .bib follows the official proceedings order; full names of Zinkevich and Whang follow Google page (Marty Zinkevich is Martin Zinkevich on MLSys). Pages not shown (left out). Abstract claims (TFX, hundreds of product teams, several petabytes per day) VERIFIED on Google Research page.
- schelter2018deequ: VERIFIED via Crossref (PVLDB 11(12):1781-1794, Aug 2018, DOI 10.14778/3229863.3229867) and Amazon Science page (declarative API, unit tests for data, Spark aggregation queries, incremental validation, ML-based constraint suggestion and anomaly detection). CORRECTED: Crossref lists a sixth author, Andreas Grafberger (already in notes' .bib).
- gx2026core: VERIFIED (GitHub: Apache-2.0, "expressive and extensible unit tests for your data"; docs home shows Version 1.24.1). Note: the docs home itself does not use the "unit tests" phrase; the GitHub README does.
- hohpe2003dlc: CORRECTED: page exists and matches (SQS dead-letter queue with receive-count limit; Kafka Connect dead letter topic; (c) 2003, 2023). Only Bobby Woolf is named on the page; Gregor Hohpe is not. Book authorship (Hohpe and Woolf) is corroborated by a Crossref record (IEEE Software 2016, "A Decade of Enterprise Integration Patterns: A Conversation with the Authors", 10.1109/MS.2016.11). .bib cites the web page with both authors and notes this.
- openfda2026enforcement: VERIFIED (RES source, records from 2004, weekly update, not for public alerts or lifecycle tracking, status not updated after classification, records can be revised e.g. more lots).
- nadeem2023res: CORRECTED: PDF text read with pdftotext; authors, title and table confirmed (FY2020 20% of 367 recalls... counts 73; FY2021 20%; FY2022 29% (100 of 344); FY2023 partial 19% (24 of 129)). The poster says the group PROPOSED making Responsible Firm mandatory and improvements were initiated at end of FY2022; it does not state the field was already made mandatory, so the notes' "after making the field mandatory" is wrong. The "19 to 29%" range in the takeaway is correct but is the share missing at time of classification for drug recalls. Poster is undated.
- redica2023rawfda: CORRECTED: 23 Mar 2023 and "more than 13,000 drug recalls ... about 3,000 actual recall events" confirmed (the 2012-2021 range appears in figure captions). The article does not say 538 label-related entries came from two recalls: it says two companies issued recalls for a 2014 label mix-up, producing 538 entries that were "really a single recall" each. Industry blog, not peer reviewed.
- biester2024llmclean: CORRECTED: published in New Trends in Database and Information Systems (CCIS), pp. 68-78, DOI 10.1007/978-3-031-70421-5_7 (Crossref), not only a preprint. CORRECTED claim: LLMs generate context models; the paper title says ontology functional dependencies (OFDs). The notes' parenthetical "ordering/dependency rules" is not supported by the abstract and should read "ontology functional dependencies"; the abstract says cleaning efficacy comparable to human-expert context models on three datasets (IoT, healthcare, Industry 4.0).

Overall notes on claims: the "Overall takeaways" statement "FDA RES 19 to 29% missing responsible firm" is supported (nadeem2023res). The statement "No peer-reviewed work on regulator alert-table extraction was found" is a negative search result by the researcher, not verifiable here; I also did not locate any in this check.
Verification: COMPLETE

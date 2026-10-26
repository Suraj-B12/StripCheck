Status: COMPLETE

Checklist
- [x] KQ1 Synthetic text-image data (MJSynth, SynthText), synthetic-to-real gap, print-and-capture / physical-world testing
- [x] KQ2 Corruption robustness benchmarks (ImageNet-C) and OCR-specific robustness (blur, glare, perspective, compression)
- [x] KQ3 Paired comparison (McNemar, Edwards, Dietterich), CIs for proportions (Wilson, Agresti-Coull, Brown-Cai-DasGupta), bootstrap
- [x] KQ4 Abstaining systems (risk-coverage, AURC), ablation practice, preregistration in ML, agent-evaluation pitfalls, cost/latency reporting
- [x] KQ5 Usability and app quality (SUS, Bangor/Lewis, MARS)

Notes written 25 Oct 2026. "Opened" = page or PDF text read in this run. A fuller, longer version of these notes (extra sources: Baek 2021, Wu 2021, Cao 2023, Usama 2025, Dror 2018, Lipton 2018, Leech 2024, Wen 2025, Yao 2024) was saved to the scratchpad as evaluation_methodology_FULL_backup.md before this condensation.

# Evaluation methodology for a perception-plus-agent system on synthetic and real images

## KQ1 Synthetic text-image data, synthetic-to-real gap, print-and-capture

### Takeaway
Rendered text with randomised font, colour, perspective, noise and blur is a legitimate, cheap data source (Jaderberg 2014; Gupta 2016), but synthetic-trained models lose about 20 points on harder real text (Jiang 2023). StripCheck should use rendered packs as a controlled-damage probe set plus a smaller print-and-capture and real-photo set, following the print-photograph-rectify protocol of Kurakin et al.

### Cited Findings
- Jaderberg, Simonyan, Vedaldi, Zisserman (2014), arXiv:1406.2227 v4 (9 Dec 2014). MJSynth pipeline: random font (1400+ Google Fonts), borders/shadows, colouring from natural-image clusters, projective distortion, blending with real crops, then noise, blur and JPEG artefacts; 9M images released. Synthetic-only training gave 99.2% (IC03) and 96.1% (SVT) with a 50-word lexicon; ablation: layer colouring +44%/+40%, natural blending +1%/+6%. Supports staged, ablatable damage rendering; the authors note printing and imaging are the uncontrolled parts. [opened]
- Gupta, Vedaldi, Zisserman (2016), arXiv:1604.06646 v1 (22 Apr 2016). SynthText: text placed using depth and surface normals on 8,000 backgrounds, 800,000 images, F-measure 84.2% (ICDAR 2013). Geometry-blind placement is substantially worse; 10x more synthetic data gave only +0.8% AP to an older detector, so realism beats volume. Supports geometry-consistent damage (curvature, glare). [opened]
- Baek et al. (2019), ICCV 2019, arXiv:1904.01906. Inconsistent evaluation subsets (IC13: 857 vs 1,015 images) create gaps over 15%; MJSynth+SynthText training beats either alone (84.1 vs 80.0 / 75.6); fine-tuning on real data helped in-distribution (+2.2 pp) but hurt out-of-distribution (-1.3 pp). Motivates freezing and publishing exact evaluation sets and disjoint tuning data. [opened]
- Jiang et al. (2023), ICCV 2023, arXiv:2307.08723. Union14M (4M labelled real images): 13 synthetic-trained models drop 20.50% on average versus common benchmarks (CRNN 78.14 to 57.96); old benchmarks saturated (2.91% of images missed by an ensemble). Strongest recent evidence for the synthetic-to-real gap; report tiers separately. [opened]
- Kurakin, Goodfellow, Bengio (2017), arXiv:1607.02533 v4 (11 Feb 2017). Pages with four corner QR codes printed at 600 dpi, photographed by hand on a phone, warped via the QR corners and cropped; photos with undetected corners discarded (at most 10%, typically 3-6%) and reported. Template for StripCheck's print-and-capture set with fiducials and a reported discard rate; only the protocol transfers (paper concerns adversarial examples). [opened]

### Inferences
- Three tiers: T1 rendered packs (large n, exact labels), T2 the same packs printed and photographed, T3 unscripted real strips (small n, widest CIs); the T1-to-T3 gap is itself a result. A 20-point gap is a cautionary prior, not an estimate for foil/blister text.

### Gaps
- No opened source evaluates print-and-capture OCR on medicine packaging. Venues for Jaderberg 2014 and Gupta 2016 (CVPR page returned 403) not confirmed from opened pages.

## KQ2 Corruption robustness benchmarks and OCR-specific robustness

### Takeaway
ImageNet-C supplies the template (fixed corruption menu, five severities, test-only rule, error-versus-clean summaries). OCR/VLM studies show blur and perspective warp dominate failures, with flat-then-collapsing severity curves. StripCheck should sweep blur, glare, perspective, noise and JPEG at about five levels and report whole curves per pipeline stage.

### Cited Findings
- Hendrycks and Dietterich (2019), ICLR 2019, arXiv:1903.12261. ImageNet-C: 15 corruptions in noise/blur/weather/digital families, five severities (75 variants), JPEG-saved, to be used for testing only; mCE normalised to AlexNet plus relative mCE (e.g. ResNet-50 mCE 76.7%). Relative robustness barely improved despite clean-accuracy gains. Design pattern for a damage menu; tuning damage must differ from test damage. Classification, not OCR. [opened]
- Urbanski and Peters (2025), DATA 2025, pp. 355-362. 15,840 degraded page images (Gaussian blur radius 1-7, noise plus darkening, perspective warp in 9-degree steps, seven levels). Errors rise steeply near maximum severity; warp hurt locally hosted 7B VLMs most on OCR, Gemini 1.5 Pro far less; WER above 1.0 at strongest blur/warp for one 7B model. Closest template for a severity sweep and warns that a small local VLM second reader degrades under warp. [opened; values only in figures]
- Nayef et al. (2015), SmartDoc-QA, Zenodo 5293201 (23 Aug 2015). Real smartphone captures of documents under varying light, blur and perspective, with ground truth and per-image capture parameters; OCR accuracy is the quality yardstick. Precedent for logged capture conditions. [opened Zenodo page; CBDAR venue from a search snippet only]
- Bulatov et al. (2022), MIDV-2020, Computer Optics 46(2):252-270. 1,000 mock identity documents with synthetic persons, captured as video, scans and photos (72,409 annotated images). Precedent for privacy-safe mock documents physically photographed; StripCheck could print mock strips with controlled batch numbers. [opened arXiv abstract]
- Usama et al. (2025), arXiv:2504.13690 (preprint). Applies 19 ImageNet-C corruptions to VLMs (TextVQA-C): text understanding degrades most under blur and snow. Corroborates blur as the priority axis; preprint, no numbers retrieved. [opened abstract]

### Inferences
- Report accuracy, abstention rate and per-stage rescue rate (QR, OCR, enhanced re-read, VLM) at each severity, plus one summary such as area under the accuracy-versus-severity curve. Glare has little recognition-specific evidence in what I opened, a gap StripCheck's data could fill.

### Gaps
- No opened recognition benchmark combines glare and compression; ICDAR2015-C details not retrieved.

## KQ3 Paired comparison, confidence intervals for proportions, bootstrap

### Takeaway
Compare StripCheck with the lookup baseline on identical images using McNemar's test on discordant pairs (exact or continuity-corrected) with a paired-difference CI. Use Wilson intervals per arm, not Wald. Recent work (Miller 2024; Bowyer 2025) says small or clustered eval sets break CLT and bootstrap intervals, so cluster by pack and run a power analysis first.

### Cited Findings
- McNemar (1947), Psychometrika 12(2):153-157. Test for differences between correlated proportions (two formulas, one with a chi-square equivalent). Basis for comparing two systems on the same items. [bibliographic record only; full text not opened]
- Edwards (1948), Psychometrika 13(3):185-187. Continuity correction for McNemar's test; matters when discordant counts are small. [IDEAS/RePEc record opened; no abstract]
- Dietterich (1998), Neural Computation 10(7):1895-1923. Two-proportion test and resampled paired t-test have high type I error; McNemar has low type I error and is the only acceptable test when an algorithm can be run once; 5x2cv slightly more powerful when 10 runs are possible. Justifies McNemar on a fixed trained pipeline. [abstract opened]
- Wilson (1927), JASA 22(158):209-212. Score interval. Details from the Wikipedia reference list (secondary); the original was not opened.
- Agresti and Coull (1998), Am. Statistician 52(2):119-126. Exact (Clopper-Pearson) intervals are too conservative and Wald too narrow; Wilson score interval has near-nominal coverage even for very small n; adding two successes and two failures approximates it. Use for zero-error cases where Wald collapses. [opened PDF]
- Brown, Cai, DasGupta (2001), Statistical Science 16(2):101-133. Wald coverage is chaotically poor; recommend Wilson or equal-tailed Jeffreys for small n, Agresti-Coull for larger n. [abstract via mirror; volume/pages from a secondary reference list]
- Efron and Tibshirani (1993), An Introduction to the Bootstrap, Chapman and Hall. Percentile/BCa bootstrap for metrics without closed-form CIs (AUGRC, paired differences); resample packs, not photos. [only the publisher page was opened and it lists 1994; verify year and ISBN]
- Miller (2024), arXiv:2411.00640. Recommends clustered standard errors (up to 3x naive on real evals), analysing question-level paired differences (variance reduction, e.g. one-third at correlation 0.5 in his example) and power analysis before the eval. StripCheck's multiple photos per pack are not independent. [opened PDF text]
- Bowyer, Aitchison, Ivanova (2025), ICML 2025 position paper, arXiv:2503.01747. Simulations (80,000 datasets, N = 3 to 100): CLT and bootstrap intervals under-cover at small N (95% CLT interval covered 92.5% at N = 100); Wilson and Beta-Bernoulli Bayesian intervals are near nominal; Clopper-Pearson too wide; clustered data needs a clustered Bayesian model. [opened PDF text]

### Inferences
- Pre-register: primary endpoint (correct-verdict or false-reassurance rate), exact McNemar at alpha 0.05, per-arm Wilson 95% CIs, cluster bootstrap CI for the paired difference, pack as the resampling unit; report discordant counts (b, c) and the minimum detectable difference.

### Gaps
- 1927, 1947, 1948 originals and the bootstrap book not opened. Newcombe (1998) paired-proportion interval (mentioned by Bowyer et al.) not opened.

## KQ4 Abstention metrics, ablation, preregistration, agent-evaluation pitfalls, cost/latency reporting

### Takeaway
CANT_VERIFY makes StripCheck a selective classifier: report coverage, selective accuracy, a risk-coverage curve and AUGRC (preferred over AURC), headlined by silent-failure rate. Agent-evaluation work says add cost/latency, held-out tests and scorer audits; Nosek 2018 supports freezing the decision rule before the A/B.

### Cited Findings
- Geifman and El-Yaniv (2017), arXiv:1705.08500 v2. Selective classifier from a trained network meeting a user-set risk with high probability; ImageNet top-5 error 2% guaranteed with probability 99.9% at almost 60% coverage. Risk-coverage framing of abstention. [opened abstract; NIPS 2017 venue from background knowledge]
- Traub et al. (2024), NeurIPS 2024, arXiv:2407.01032 v2. AURC aggregates selective risk, over-weights high-confidence failures and violates monotonicity; AUGRC (average risk of undetected failures) changes rankings on 5 of 6 datasets across 13 confidence scores. Use AUGRC (also report AURC) with the verifier's score. [opened PDF]
- Kapoor et al. (2024), arXiv:2407.01502 (preprint). Accuracy-only agent evaluation misleads: simple retry/warming/escalation baselines match complex HumanEval agents; cost differed by almost two orders of magnitude at similar accuracy; calls for cost-accuracy Pareto plots, holdout sets and reproducibility. StripCheck must report latency, LLM calls, tokens and hardware (no paid API cost) and treat the lookup script as the simple baseline. [opened PDF]
- Zhu et al. (2025), NeurIPS 2025 D&B track, arXiv:2507.02825 v5. Agentic Benchmark Checklist; scorer and task-setup flaws (e.g. empty responses counted as success) misstate performance by up to 100% relative; ABC cut CVE-Bench overestimation by 33%. Audit StripCheck's scorer so blanket CANT_VERIFY cannot score as success. [opened abstract]
- Yao et al. (2024), tau-bench, arXiv:2406.12045 (preprint). pass^k reliability over repeated trials; gpt-4o agents under 50% task success and pass^8 below 25% in retail. With an LLM planner, run each image several times and report consistency. [opened abstract]
- Nosek, Ebersole, DeHaven, Mellor (2018), PNAS 115(11):2600-2606. Preregistration separates prediction from postdiction and avoids forking-paths p-values; a plan should fix hypotheses, design, exclusions, test choice and commit to reporting all outcomes and deviations; authors state experimental evidence of improved reproducibility is still lacking. [opened PMC full text]
- Bertinetto et al. (2020), NeurIPS 2020 workshop. ML pre-registration: papers reviewed on protocol before results to reward rigour and publish negative results; a workshop experiment, not standard practice. [opened workshop page]

### Inferences
- Headline safety metric: silent-failure rate with Wilson CI, with false reassurance (false NOT_LISTED on a listed batch) reported separately from false alarms. Ablate one component at a time (QR, OCR, re-read, VLM, variant search, corroboration, critic, HITL) with paired McNemar CIs and equal tuning effort for the baseline. A dated, hashed commit of the analysis plan before test-set evaluation gives preregistration's protection.

### Gaps
- No opened source gives an acceptable false-reassurance threshold for medicine-authenticity screening; justify it from StripCheck's own risk analysis. Original AURC paper (Geifman et al. 2019) not opened. No ML-specific evidence that preregistration improves outcomes found.

## KQ5 Usability and app quality (SUS, MARS)

### Takeaway
SUS is a free 10-item, 0-100 perceived-usability scale (alpha about 0.91) that gives usable conclusions from about 8-12 participants; benchmark against mean 68 overall and about 77.7 for popular mobile apps. MARS is a 23-item expert audit (ICC 0.79) validated only on iPhone mental-health apps; use it as a supplement, and add a verdict-comprehension check because SUS does not measure safety.

### Cited Findings
- Brooke (1996), chapter in Usability Evaluation in Industry, Taylor and Francis. Original SUS: a reliable, low-cost global usability scale; use requires acknowledging the source. [chapter opened; editors and page range from background knowledge]
- Bangor, Kortum, Miller (2008), IJHCI 24(6):574-594. Per Lewis (2018): 2,300+ questionnaires over 200+ studies, mean about 70, alpha 0.91. [second-hand via Lewis; not opened] [UNVERIFIED]
- Bangor, Kortum, Miller (2009), J. Usability Studies 4(3):114-123. Adjective item on nearly 1,000 surveys, r = 0.82; per Lewis (2018), mean SUS: Poor 35.7, OK 50.9, Good 71.4, Excellent 85.5, Best imaginable 90.9. [second-hand; article PDF returned 404] [UNVERIFIED]
- Lewis (2018), IJHCI 34(7):577-590. Review: reliability 0.83-0.97 (avg 0.91); Sauro-Lewis curved grades from 446 studies (68 = C, 80 = A-); Tullis and Stetson found SUS reached 100% agreement with the full-sample decision at n = 12; Kortum and Sorber (2015) mobile apps mean 77.7 (range 67.7-87.4, 3,575 users); two-factor structure not replicated; use "awkward" in item 8. [opened PDF]
- Stoyanov et al. (2015), JMIR mHealth uHealth 3(1):e27. MARS: 23 items (engagement 5, functionality 4, aesthetics 3, information 7, subjective 4), 1-5 ratings; total ICC 0.79, alpha 0.90 on 50 apps; ease-of-use/navigation items ICC only 0.50; iPhone mental-health apps only; recommends rater training. [opened PMC text]

### Inferences
- Study: 12-20 target users, scripted tasks, SUS after tasks plus task success, time and verdict comprehension (NOT_LISTED must not be read as safe); report mean SUS with 95% CI and grade versus 68 and about 78. MARS with two independent raters and ICC as an audit.

### Gaps
- Bangor 2008/2009 and Brooke page details not confirmed first-hand. No SUS/MARS validation for medicine-verification apps and no India-specific norms found.

## BibTeX

@misc{jaderberg2014synthetic,
  author = {Jaderberg, Max and Simonyan, Karen and Vedaldi, Andrea and Zisserman, Andrew},
  title = {Synthetic Data and Artificial Neural Networks for Natural Scene Text Recognition},
  year = {2014}, eprint = {1406.2227}, archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/1406.2227},
  note = {v4, 9 Dec 2014. Workshop venue not confirmed. Accessed 25 Oct 2026}
}

@misc{gupta2016synthtext,
  author = {Gupta, Ankush and Vedaldi, Andrea and Zisserman, Andrew},
  title = {Synthetic Data for Text Localisation in Natural Images},
  year = {2016}, eprint = {1604.06646}, archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/1604.06646},
  note = {v1, 22 Apr 2016; CVPR 2016 venue/pages not confirmed. Accessed 25 Oct 2026}
}

@inproceedings{baek2019wrong,
  author = {Baek, Jeonghun and Kim, Geewook and Lee, Junyeop and Park, Sungrae and Han, Dongyoon and Yun, Sangdoo and Oh, Seong Joon and Lee, Hwalsuk},
  title = {What Is Wrong With Scene Text Recognition Model Comparisons? Dataset and Model Analysis},
  booktitle = {Proc. IEEE/CVF International Conference on Computer Vision (ICCV)},
  year = {2019},
  url = {https://openaccess.thecvf.com/content_ICCV_2019/html/Baek_What_Is_Wrong_With_Scene_Text_Recognition_Model_Comparisons_Dataset_ICCV_2019_paper.html},
  note = {arXiv:1904.01906; author order partly inferred from a truncated PDF header, verify. Accessed 25 Oct 2026}
}

@inproceedings{jiang2023union14m,
  author = {Jiang, Qing and Wang, Jiapeng and Peng, Dezhi and Liu, Chongyu and Jin, Lianwen},
  title = {Revisiting Scene Text Recognition: A Data Perspective},
  booktitle = {Proc. IEEE/CVF International Conference on Computer Vision (ICCV)},
  year = {2023}, url = {https://arxiv.org/abs/2307.08723},
  note = {arXiv:2307.08723. Accessed 25 Oct 2026}
}

@misc{kurakin2017physical,
  author = {Kurakin, Alexey and Goodfellow, Ian and Bengio, Samy},
  title = {Adversarial examples in the physical world},
  year = {2017}, eprint = {1607.02533}, archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/1607.02533},
  note = {v4, 11 Feb 2017. Accessed 25 Oct 2026}
}

@inproceedings{hendrycks2019benchmarking,
  author = {Hendrycks, Dan and Dietterich, Thomas},
  title = {Benchmarking Neural Network Robustness to Common Corruptions and Perturbations},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year = {2019}, url = {https://arxiv.org/abs/1903.12261},
  note = {arXiv:1903.12261. Accessed 25 Oct 2026}
}

@inproceedings{urbanski2025quantifying,
  author = {Urbanski, Rupert and Peters, Ralf},
  title = {Quantifying the Effects of Image Degradation on {LVLM} Benchmark Results Systematically},
  booktitle = {Proc. 14th International Conference on Data Science, Technology and Applications (DATA)},
  year = {2025}, pages = {355--362}, doi = {10.5220/0013462800003967},
  url = {https://www.scitepress.org/publishedPapers/2025/134628/pdf/index.html},
  note = {Accessed 25 Oct 2026}
}

@misc{nayef2015smartdocqa,
  author = {Nayef, Nibal and Luqman, Muhammad Muzzamil and Prum, Sophea and Eskenazi, Sebastien and Chazalon, Joseph and Ogier, Jean-Marc},
  title = {{SmartDoc-QA}: A Dataset for Quality Assessment of Smartphone Captured Document Images - Single and Multiple Distortions},
  year = {2015}, howpublished = {Zenodo dataset}, url = {https://zenodo.org/records/5293201},
  note = {v1.0, 23 Aug 2015; CBDAR 2015 venue from a search snippet only. Accessed 25 Oct 2026}
}

@article{bulatov2022midv2020,
  author = {Bulatov, Konstantin and Emelianova, Ekaterina and Tropin, Daniil and Skoryukina, Natalya and Chernyshova, Yulia and Sheshkus, Alexander and Usilin, Sergey and Ming, Zuheng and Burie, Jean-Christophe and Luqman, Muhammad Muzzamil and Arlazarov, Vladimir V.},
  title = {{MIDV-2020}: A Comprehensive Benchmark Dataset for Identity Document Analysis},
  journal = {Computer Optics}, volume = {46}, number = {2}, pages = {252--270}, year = {2022},
  url = {https://arxiv.org/abs/2107.00396}, note = {arXiv:2107.00396. Accessed 25 Oct 2026}
}

@misc{usama2025vlmcorruptions,
  author = {Usama, Muhammad and Asim, Syeda Aishah and Ali, Syed Bilal and Wasim, Syed Talal and Mansoor, Umair Bin},
  title = {Analysing the Robustness of Vision-Language-Models to Common Corruptions},
  year = {2025}, eprint = {2504.13690}, archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2504.13690}, note = {Preprint v2, 21 Apr 2025. Accessed 25 Oct 2026}
}

@article{mcnemar1947note,
  author = {McNemar, Quinn},
  title = {Note on the sampling error of the difference between correlated proportions or percentages},
  journal = {Psychometrika}, volume = {12}, number = {2}, pages = {153--157}, year = {1947},
  doi = {10.1007/BF02295996}, note = {Details from search listings; full text not opened}
}

@article{edwards1948note,
  author = {Edwards, Allen L.},
  title = {Note on the ``correction for continuity'' in testing the significance of the difference between correlated proportions},
  journal = {Psychometrika}, volume = {13}, number = {3}, pages = {185--187}, year = {1948},
  doi = {10.1007/BF02289261}, note = {Record opened on IDEAS/RePEc (listed as Allen Edwards; initial L. from background knowledge)}
}

@article{dietterich1998approximate,
  author = {Dietterich, Thomas G.},
  title = {Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms},
  journal = {Neural Computation}, volume = {10}, number = {7}, pages = {1895--1923}, year = {1998},
  doi = {10.1162/089976698300017197}, note = {Abstract read via mlanthology.org}
}

@article{wilson1927probable,
  author = {Wilson, Edwin B.},
  title = {Probable Inference, the Law of Succession, and Statistical Inference},
  journal = {Journal of the American Statistical Association}, volume = {22}, number = {158}, pages = {209--212}, year = {1927},
  doi = {10.1080/01621459.1927.10502953}, note = {Details from Wikipedia reference list; original not opened}
}

@article{agresti1998approximate,
  author = {Agresti, Alan and Coull, Brent A.},
  title = {Approximate is Better than ``Exact'' for Interval Estimation of Binomial Proportions},
  journal = {The American Statistician}, volume = {52}, number = {2}, pages = {119--126}, year = {1998},
  doi = {10.1080/00031305.1998.10480550}
}

@article{brown2001interval,
  author = {Brown, Lawrence D. and Cai, T. Tony and DasGupta, Anirban},
  title = {Interval Estimation for a Binomial Proportion},
  journal = {Statistical Science}, volume = {16}, number = {2}, pages = {101--133}, year = {2001},
  doi = {10.1214/ss/1009213286}, note = {Abstract via mirror; volume/pages from a secondary list}
}

@book{efron1993bootstrap,
  author = {Efron, Bradley and Tibshirani, Robert J.},
  title = {An Introduction to the Bootstrap},
  publisher = {Chapman and Hall}, address = {New York}, year = {1993},
  note = {Only publisher page opened (lists 1994 CRC edition); verify year and ISBN}
}

@misc{miller2024errorbars,
  author = {Miller, Evan},
  title = {Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations},
  year = {2024}, eprint = {2411.00640}, archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2411.00640}, note = {Preprint, 1 Nov 2024. Accessed 25 Oct 2026}
}

@inproceedings{bowyer2025clt,
  author = {Bowyer, Sam and Aitchison, Laurence and Ivanova, Desi R.},
  title = {Position: Don't Use the {CLT} in {LLM} Evals With Fewer Than a Few Hundred Datapoints},
  booktitle = {International Conference on Machine Learning (ICML)},
  year = {2025}, url = {https://arxiv.org/abs/2503.01747},
  note = {arXiv:2503.01747 v3, 28 May 2025. Accessed 25 Oct 2026}
}

@inproceedings{geifman2017selective,
  author = {Geifman, Yonatan and El-Yaniv, Ran},
  title = {Selective Classification for Deep Neural Networks},
  booktitle = {Advances in Neural Information Processing Systems 30},
  year = {2017}, url = {https://arxiv.org/abs/1705.08500},
  note = {arXiv:1705.08500 v2; NIPS 2017 venue from background knowledge. Accessed 25 Oct 2026}
}

@inproceedings{traub2024augrc,
  author = {Traub, Jeremias and Bungert, Till J. and L{\"u}th, Carsten T. and Baumgartner, Michael and Maier-Hein, Klaus H. and Maier-Hein, Lena and Jaeger, Paul F.},
  title = {Overcoming Common Flaws in the Evaluation of Selective Classification Systems},
  booktitle = {Advances in Neural Information Processing Systems 37},
  year = {2024}, url = {https://arxiv.org/abs/2407.01032},
  note = {arXiv:2407.01032 v2, 19 Oct 2024; NeurIPS venue from a search listing. Accessed 25 Oct 2026}
}

@misc{kapoor2024agents,
  author = {Kapoor, Sayash and Stroebl, Benedikt and Siegel, Zachary S. and Nadgir, Nitya and Narayanan, Arvind},
  title = {{AI} Agents That Matter},
  year = {2024}, eprint = {2407.01502}, archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2407.01502}, note = {Preprint, 1 Jul 2024. Accessed 25 Oct 2026}
}

@misc{zhu2025agentic,
  author = {Zhu, Yuxuan and Jin, Tengjun and Pruksachatkun, Yada and others},
  title = {Establishing Best Practices for Building Rigorous Agentic Benchmarks},
  year = {2025}, eprint = {2507.02825}, archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2507.02825},
  note = {25 authors, full list on arXiv (includes Kapoor, Steinhardt, Liang, Kang); v5 7 Aug 2025; NeurIPS 2025 D\&B track per search listing. Accessed 25 Oct 2026}
}

@misc{yao2024taubench,
  author = {Yao, Shunyu and Shinn, Noah and Razavi, Pedram and Narasimhan, Karthik},
  title = {$\tau$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains},
  year = {2024}, eprint = {2406.12045}, archivePrefix = {arXiv},
  url = {https://arxiv.org/abs/2406.12045}, note = {Preprint, 17 Jun 2024. Accessed 25 Oct 2026}
}

@article{nosek2018preregistration,
  author = {Nosek, Brian A. and Ebersole, Charles R. and DeHaven, Alexander C. and Mellor, David T.},
  title = {The preregistration revolution},
  journal = {Proceedings of the National Academy of Sciences}, volume = {115}, number = {11}, pages = {2600--2606}, year = {2018},
  doi = {10.1073/pnas.1708274114}
}

@misc{bertinetto2020preregistration,
  author = {Bertinetto, Luca and Henriques, Jo{\~a}o and Albanie, Samuel and Paganini, Michela and Varol, G{\"u}l},
  title = {The pre-registration experiment: an alternative publication model for machine learning research},
  year = {2020}, howpublished = {NeurIPS 2020 Workshop},
  url = {https://neurips.cc/virtual/2020/workshop/16158}, note = {Organisers as listed on the page. Accessed 25 Oct 2026}
}

@incollection{brooke1996sus,
  author = {Brooke, John},
  title = {{SUS}: A Quick and Dirty Usability Scale},
  booktitle = {Usability Evaluation in Industry},
  editor = {Jordan, Patrick W. and Thomas, Bruce and Weerdmeester, Bernard A. and McClelland, Ian L.},
  publisher = {Taylor and Francis}, address = {London}, year = {1996}, pages = {189--194},
  note = {Editors and page range from background knowledge; verify}
}

@article{bangor2008empirical,
  author = {Bangor, Aaron and Kortum, Philip T. and Miller, James T.},
  title = {An Empirical Evaluation of the System Usability Scale},
  journal = {International Journal of Human-Computer Interaction}, volume = {24}, number = {6}, pages = {574--594}, year = {2008},
  note = {Volume/pages from Lewis (2018) reference list; issue from background knowledge; not opened}
}

@article{bangor2009determining,
  author = {Bangor, Aaron and Kortum, Philip T. and Miller, James T.},
  title = {Determining What Individual {SUS} Scores Mean: Adding an Adjective Rating Scale},
  journal = {Journal of Usability Studies}, volume = {4}, number = {3}, pages = {114--123}, year = {2009},
  note = {Details from a search result; article not opened. Accessed 25 Oct 2026}
}

@article{lewis2018sus,
  author = {Lewis, James R.},
  title = {The System Usability Scale: Past, Present, and Future},
  journal = {International Journal of Human-Computer Interaction}, volume = {34}, number = {7}, pages = {577--590}, year = {2018},
  doi = {10.1080/10447318.2018.1455307}
}

@article{stoyanov2015mars,
  author = {Stoyanov, Stoyan R. and Hides, Leanne and Kavanagh, David J. and Zelenko, Oksana and Tjondronegoro, Dian and Mani, Madhavan},
  title = {Mobile App Rating Scale: A New Tool for Assessing the Quality of Health Mobile Apps},
  journal = {JMIR mHealth and uHealth}, volume = {3}, number = {1}, pages = {e27}, year = {2015},
  doi = {10.2196/mhealth.3422}
}

## Verification log

- gupta2016synthtext: CORRECTED. Venue confirmed as CVPR 2016, pp. 2315-2324, DOI 10.1109/CVPR.2016.254 (Crossref); authors/title/arXiv v1 22 Apr 2016 match (arXiv API). Notes' "venue not confirmed" resolved. Numeric claims (84.2% F, 800k images) not re-checked beyond arXiv listing.
- baek2019wrong: CORRECTED. ICCV 2019, pp. 4714-4722, DOI 10.1109/ICCV.2019.00481 (Crossref); author order verified from arXiv API (Baek, Kim, Lee, Park, Han, Yun, Oh, Lee), so the "partly inferred" caveat is resolved; arXiv comment confirms oral at ICCV'19.
- urbanski2025quantifying: VERIFIED. Title, authors, DATA 2025 proceedings, pp. 355-362, DOI 10.5220/0013462800003967 (Crossref).
- jaderberg2014synthetic: CORRECTED. Title/authors/dates match arXiv (v1 9 Jun 2014, v4 9 Dec 2014). No peer-reviewed venue could be confirmed (web search found only arXiv), so it is cited as an arXiv preprint. Numbers verified in PDF: 99.2% IC03 and 96.1% SVT (50-word lexicon), over 1400 Google fonts, colouring +44%/+40%, blending +1%/+6%. Correction: "9M images" is 9M for each lexicon (50k and 90k), so about 18M generated in total.
- jiang2023union14m: CORRECTED. Added ICCV 2023 pp. 20486-20497, DOI 10.1109/ICCV51070.2023.01878 (Crossref). Verified in PDF: Union14M has 4M labelled images, average drop 20.50%, CRNN 78.14 to 57.96, 2.91% (222 images) missed by the ensemble.
- kurakin2017physical: VERIFIED (arXiv v4). Peer-reviewed venue not confirmed, so kept as a preprint; bib year set to 2016 (first submission 8 Jul 2016). Protocol verified in PDF: 600 dpi, four corner QR codes, perspective warp, no more than 10% discarded, typically 3-6%.
- hendrycks2019benchmarking: VERIFIED. ICLR 2019 (ICLR poster page); 15 corruptions, 5 severities, 75 variants and ResNet-50 mCE 76.7% found in the arXiv PDF.
- nayef2015smartdocqa: CORRECTED. The Zenodo record gives DOI 10.1109/ICDAR.2015.7333960; Crossref shows the paper is in ICDAR 2015 (13th ICDAR), pp. 1231-1235, not only the CBDAR workshop. Dataset description (lighting, blur, perspective, ground truth plus capture parameters) matches.
- bulatov2022midv2020: VERIFIED. Computer Optics 46(2), DOI 10.18287/2412-6179-CO-1006 (Crossref), 11 authors per arXiv/journal-ref. The "1,000 mock documents, 72,409 images" figure was not re-checked.
- usama2025vlmcorruptions: VERIFIED. arXiv PDF: 19 ImageNet-C corruption types, recognition deteriorates most under blur and snow. The "TextVQA-C" name and the "v2 21 Apr 2025" date were not checked; v1 is 18 Apr 2025.
- mcnemar1947note: VERIFIED via Crossref (DOI, Psychometrika 12(2):153-157, June 1947). Full text not opened.
- edwards1948note: VERIFIED via Crossref (Psychometrika 13(3):185-187, Sep 1948, DOI 10.1007/BF02289261). Given name "Allen L." not confirmed by Crossref.
- dietterich1998approximate: VERIFIED via Crossref (Neural Comput. 10(7):1895-1923, DOI 10.1162/089976698300017197).
- wilson1927probable: VERIFIED via Crossref (JASA 22(158):209-212, DOI 10.1080/01621459.1927.10502953).
- agresti1998approximate: VERIFIED via Crossref (Am. Stat. 52(2):119-126; DOI 10.1080/00031305.1998.10480550; a second DOI 10.2307/2685469 also exists).
- brown2001interval: VERIFIED via Crossref (Stat. Sci. 16(2):101-133, DOI 10.1214/ss/1009213286); the "secondary reference list" caveat is resolved.
- efron1993bootstrap: CORRECTED. Crossref has the Springer US record dated 1993 (DOI 10.1007/978-1-4899-4541-9, ISBN 9780412042317) and a Chapman and Hall/CRC reissue dated 1994 (ISBN 9780429246593). Year question resolved: 1993 original, 1994 reissue.
- miller2024errorbars: VERIFIED (arXiv v1 1 Nov 2024). PDF checks: clustered standard errors up to 3X naive; power analysis section; with correlation 0.5, paired differences cut variance by 1/3 in his worked example.
- bowyer2025clt: VERIFIED. arXiv comment says ICML 2025 Spotlight Position Paper. PDF checks: 80,000 datasets; 95% CLT intervals cover only 92.5% at N=100.
- geifman2017selective: CORRECTED. NIPS 2017 (Advances in NIPS 30) confirmed on proceedings.neurips.cc; notes had said venue from background knowledge. The 2%/99.9%/60% coverage figures were not re-checked.
- traub2024augrc: CORRECTED. Venue confirmed as NeurIPS 2024 main track (Advances in NIPS 37); authors, 6 datasets, 13 confidence scores and ranking change on 5 of 6 datasets verified from the arXiv abstract. The "AURC over-weights high-confidence failures and violates monotonicity" statement was not re-checked.
- kapoor2024agents: VERIFIED as arXiv preprint. PDF checks: retry/warming/escalation baselines match complex HumanEval agents; cost differs by almost two orders of magnitude at similar accuracy; Pareto curves; holdout sets.
- zhu2025agentic: CORRECTED. Published at NeurIPS 2025 Datasets and Benchmarks Track under the title "Establishing Best Practices in Building Rigorous Agentic Benchmarks" (arXiv v5 says "for"). Full 25-author list added. Verified: up to 100% relative misestimation; ABC cuts CVE-Bench overestimation by 33%; tau-bench counts empty responses as success.
- yao2024taubench: VERIFIED as arXiv preprint (17 Jun 2024). Abstract: gpt-4o succeeds on under 50% of tasks, pass^8 under 25% in retail. Peer-reviewed venue not checked.
- nosek2018preregistration: VERIFIED via Crossref (PNAS 115(11):2600-2606, 12 Mar 2018, DOI 10.1073/pnas.1708274114).
- bertinetto2020preregistration: VERIFIED. NeurIPS 2020 workshop page exists with that title; five names listed under the title (page does not label them organisers).
- brooke1996sus: CORRECTED. Crossref gives CRC Press e-book, DOI 10.1201/9781498710411-35, pp. 207-212; editors Jordan, Thomas, McClelland, Weerdmeester. The notes' pp. 189-194 (print edition) could not be confirmed.
- bangor2008empirical: VERIFIED via Crossref (IJHCI 24(6):574-594, DOI 10.1080/10447310802205776). The figures (2,300+ questionnaires, mean about 70) rest on Lewis (2018) only and were not checked first-hand. [UNVERIFIED]
- bangor2009determining: VERIFIED (citation only: J. Usability Studies 4(3):114-123; nearly 1,000 surveys; r = 0.822 per search result). The adjective mean SUS scores (Poor 35.7, OK 50.9, Good 71.4, Excellent 85.5, Best imaginable 90.9) could not be confirmed from the article. [UNVERIFIED]
- lewis2018sus: VERIFIED via Crossref (IJHCI 34(7):577-590, DOI 10.1080/10447318.2018.1455307). Numeric claims (alpha 0.91, 68 = C, n = 12 agreement, mobile mean 77.7) not re-checked; paywalled.
- stoyanov2015mars: VERIFIED via Crossref and PubMed abstract (JMIR mHealth uHealth 3(1):e27; 23 items; alpha .90; ICC .79; 50 apps for reliability). Caveat: abstract says well-being apps found via an iTunes search, so "iPhone mental-health apps only" is not confirmed as stated.
Verification: COMPLETE

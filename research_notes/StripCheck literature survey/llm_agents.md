Status: COMPLETE

# LLM-Based Agent Architectures for a Bounded, Tool-Using, Verifier-Checked Agent on Small Local Models

Checklist:
- [x] KQ1 Reasoning/acting loops, tool use, reflection, critics (ReAct, MRKL, Toolformer, Reflexion, Self-Refine, CRITIC)
- [x] KQ2 Limits of self-correction and external verifiers (Huang et al. 2024; Kambhampati et al. 2024)
- [x] KQ3 Multi-agent/supervisor patterns, surveys, Anthropic "Building effective agents", LangGraph durable execution/interrupts, human-in-the-loop
- [x] KQ4 Small language models for agents; structured output and constrained decoding
- [x] KQ5 Agent evaluation, observability, and reliable agents in high-stakes domains (2025-2026)

(Today = 25 Oct 2026. Only sources actually opened are cited. Mostly arXiv abstract pages were read; full text only for Tam et al. and JSONSchemaBench (HTML). Venues marked "unconfirmed" must be checked against proceedings before the thesis.)

### Final takeaways for StripCheck (justifying a hybrid rules+LLM planner with a hard-rule verifier)
1. Intrinsic LLM self-correction is unreliable (Huang et al., ICLR 2024); tool-grounded critique works (CRITIC, ICLR 2024); LLM-Modulo (Kambhampati et al., ICML 2024) formalises "LLM proposes, sound external verifier disposes". This is the core citation cluster for the hard-rule verifier.
2. MRKL (2022) and Anthropic's workflow-vs-agent guidance (19 Dec 2024) support a mostly deterministic graph with a bounded LLM planner/adjudicator, programmatic checks between steps, stop conditions and human checkpoints.
3. LangGraph interrupt() + checkpointer is the implementation route for the "character in doubt" question; the node restarts on resume, so pre-interrupt work must be idempotent. Over-escalation can reduce safety (Turan 2026 preprint, modelling only).
4. SLMs for agents: supported by a position paper (Belcak et al., v3 22 Sep 2026), but AgentBench (ICLR 2024) shows open models weaker at instruction following and long-horizon decisions; hence rule fallback and abstention (BFCL, When2Call).
5. Constrained decoding (Outlines, XGrammar, Guidance) gives valid schemas, but engines differ greatly on complex schemas and strict JSON can hurt free-form reasoning (Tam et al.); keep schemas small, reasoning-first, and re-validate downstream.
6. Evaluate on end-state outcomes, repeated trials (pass^k), cost, held-out data and abstention (tau-bench, Kapoor et al., When2Call). 2026 healthcare neuro-symbolic papers (LLM normalises, rules decide) match StripCheck's pattern but are preprints/workshop-level.
7. Not found: a peer-reviewed healthcare agent study combining a hard-rule verifier with abstention; state this honestly as the gap StripCheck addresses.

## KQ1 Reasoning/acting loops, tool use, reflection, critics

### Takeaway
The seminal agent loop (ReAct) interleaves reasoning and tool actions; MRKL frames the LLM as a router over discrete expert modules; Toolformer learns tool calls; Reflexion/Self-Refine add verbal self-feedback; CRITIC shows that the feedback that works is tool-grounded (external). StripCheck's graph (QR -> OCR -> re-read -> lookup -> corroborate) is a MRKL-style system in which discrete modules do the knowledge work and the LLM only routes/adjudicates, with a CRITIC-style external check.

### Cited Findings
- **ReAct** (Yao, Zhao, Yu, Du, Shafran, Narasimhan, Cao; arXiv:2210.03629; v3 comments say ICLR camera-ready; ICLR 2023). LLM emits interleaved reasoning traces and task actions; actions query external sources (Wikipedia API on HotpotQA/FEVER) which reduces hallucination and error propagation seen in chain-of-thought. Absolute success-rate gains over imitation/RL baselines: +34% on ALFWorld, +10% on WebShop, with only 1-2 in-context examples. Relevance: the baseline observe-think-act loop for StripCheck's planner; also motivates interpretable, loggable trajectories (audit trail) — https://arxiv.org/abs/2210.03629 (opened 25 Oct 2026). Caveat: the abstract page gave no numeric HotpotQA/FEVER scores; I did not read the full text.
- **MRKL Systems** (Karpas et al.; arXiv:2205.00445, submitted 1 May 2022; arXiv preprint). Proposes a modular neuro-symbolic architecture: several neural models plus discrete knowledge and reasoning modules, because LLMs alone are limited in knowledge and reasoning; Jurassic-X is AI21's implementation. Relevance: the closest classical precedent for StripCheck's design (LLM as language front-end/router, deterministic modules — exact batch lookup, rule engine — for facts) — https://arxiv.org/abs/2205.00445. Caveat: abstract page did not name "routers/experts"; I could not confirm those terms from what I opened.
- **Toolformer** (Schick, Dwivedi-Yu, Dessi, Raileanu, Lomeli, Zettlemoyer, Cancedda, Scialom; arXiv:2302.04761, 9 Feb 2023). Self-supervised: the model learns which API to call, when, with what arguments and how to use the result, from a handful of demonstrations per API (calculator, QA, two search engines, translator, calendar); zero-shot gains often competitive with much larger models. Relevance: shows tool use can be learned, but StripCheck uses hand-wired tools with an explicit graph because a small local model cannot be trusted to self-schedule safety-critical calls — https://arxiv.org/abs/2302.04761. Caveat: arXiv page lists no peer-reviewed venue (published NeurIPS 2023 per my background knowledge, NOT confirmed from an opened source).
- **Reflexion** (Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao; arXiv:2303.11366, 20 Mar 2023, v4 10 Oct 2023). Agents reflect verbally on task feedback and keep reflections in an episodic memory buffer (no weight updates); scalar or free-form feedback from external or simulated sources; 91% pass@1 on HumanEval vs 80% for GPT-4 baseline. Relevance: analogous to the "medicine cabinet" memory and retry-with-notes, but note the strongest result relies on external test feedback — https://arxiv.org/abs/2303.11366. Caveat: no venue on arXiv page (NeurIPS 2023 per background knowledge, unconfirmed).
- **Self-Refine** (Madaan et al., 16 authors; arXiv:2303.17651, 30 Mar 2023, v2 25 May 2023). One LLM generates, critiques, refines iteratively with no training; 7 tasks with GPT-3.5/ChatGPT/GPT-4; ~20% absolute average task improvement over one-step generation (preferred by humans and metrics). Relevance: motivates an enhanced-re-read loop, but tested only with strong models and on tasks without hard ground truth; contrast with KQ2 — https://arxiv.org/abs/2303.17651. Caveat: no peer-reviewed venue on the page (NeurIPS 2023 per background knowledge, unconfirmed).
- **CRITIC** (Gou, Shao, Gong, Shen, Yang, Duan, Chen; arXiv:2305.11738; ICLR 2024 per arXiv comments; v4 21 Feb 2024). Black-box LLM verifies and revises its output using external tools (search engine, code interpreter) on free-form QA, mathematical program synthesis and toxicity reduction; consistent improvements; concludes external feedback is crucial for self-improvement. Relevance: direct support for StripCheck's critic being grounded in tools/data (the CDSCO index and field comparison) rather than the LLM's opinion — https://arxiv.org/abs/2305.11738. Abstract gave no numbers.

### Inferences
- Taken together, the lineage ReAct -> MRKL -> CRITIC supports a graph where the LLM proposes and tools/rules dispose. Reflexion/Self-Refine gains come with scalar/external feedback or strong models and should not be assumed for a small local model.
- ReAct's interpretable trajectories justify persisting every planner step and tool result for audit.

### Gaps
- I did not open full texts, so per-benchmark tables (ReAct HotpotQA/FEVER, CRITIC per-task deltas) are not reported.
- Venues for Toolformer, Reflexion, Self-Refine (all NeurIPS 2023 per memory) are unconfirmed; verify against proceedings before the thesis.

## KQ2 Limits of self-correction and external verifiers

### Takeaway
Intrinsic self-correction of reasoning does not reliably work and can hurt; the remedy in both Huang et al. and Kambhampati et al. is external, model-based verification. This is the central justification for StripCheck's hard-rule verifier that the LLM cannot overrule.

### Cited Findings
- **Huang, Chen, Mishra, Zheng, Yu, Song, Zhou. "Large Language Models Cannot Self-Correct Reasoning Yet."** ICLR 2024 (accepted, per arXiv page); arXiv:2310.01798, submitted 3 Oct 2023, v2 14 Mar 2024. Without external feedback ("intrinsic self-correction"), models generally struggle to fix reasoning errors and accuracy sometimes declines after self-correction; authors recommend external feedback. Relevance: challenges relying on an LLM critic/adjudicator alone; motivates deterministic rules plus data-grounded checks — https://arxiv.org/abs/2310.01798. Caveat: I read only the abstract page; no per-dataset numbers recorded.
- **Kambhampati, Valmeekam, Guan, Verma, Stechly, Bhambri, Saldyt, Murthy. "LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks."** Proceedings of the 41st ICML, Vienna, 2024, PMLR vol. 235; arXiv:2402.01817 (v3 12 Jun 2024). Position paper: autoregressive LLMs "cannot, by themselves, do planning or self-verification"; proposes LLM-Modulo: LLM as approximate knowledge source generating candidates, paired with external model-based verifiers/critics in a bidirectional loop; LLMs can also help acquire the models behind the verifiers. Relevance: the closest formal template for StripCheck's hybrid: LLM planner proposes, hard-rule verifier (sound, deterministic) accepts or rejects with feedback, abstention (CANT_VERIFY) when no candidate passes — https://arxiv.org/abs/2402.01817. Caveat: position paper, I did not read its empirical sections; PMLR page not opened (venue taken from arXiv listing).
- Corroboration of the same direction from CRITIC (see KQ1): tool-grounded critiques improve outputs — https://arxiv.org/abs/2305.11738.

### Inferences
- Design choice supported: the verifier must be rule-based and sound (never LLM-judged) for the verdict-bearing steps; LLM output is only a proposal. An LLM may be used inside the loop only for repair suggestions (ingest) that are re-validated by schema/rules and quarantined on failure.
- Self-Refine's gains (KQ1) versus Huang et al.'s negative result is a known tension (feedback quality/task type/model strength); for a small local model the conservative reading (Huang) is the safer assumption. This is my inference, not a finding of either paper.

### Gaps
- No small-model (<=8B) quantification of self-correction failure was opened here; see KQ4 for SLM sources.

## KQ3 Multi-agent/supervisor patterns, surveys, LangGraph, human-in-the-loop

### Takeaway
Anthropic's guidance (Dec 2024) favors simple, composable workflows with programmatic checks and human checkpoints over open-ended autonomy; LangGraph's interrupt()+checkpointer is the concrete mechanism for StripCheck's "ask the user about the doubtful character" step.

### Cited Findings
- **Anthropic Engineering (Erik S. and Barry Zhang; surnames Schluntz/Zhang per my background knowledge — the page byline I opened shows "Erik S." and "Barry Zhang"), "Building effective agents", published 19 Dec 2024.** Distinguishes *workflows* (LLMs and tools orchestrated through predefined code paths) from *agents* (LLM dynamically directs its own process/tool use). Patterns: prompt chaining (with programmatic checks between steps), routing, parallelization (sectioning/voting), orchestrator-workers, evaluator-optimizer. Advice: start with the simplest solution; add complexity only when it measurably helps; agents trade latency/cost for performance, errors can compound, so test in sandboxes with guardrails; agents should gather ground truth from the environment each step, can pause for human feedback at checkpoints, and should have stopping conditions (e.g., max iterations); use agents only where model decision-making can be trusted. The page notes (as of my access on 25 Oct 2026) that much tooling has changed since Dec 2024 and points to newer Anthropic documentation. Relevance: StripCheck is deliberately a workflow with a bounded agentic planner, not an open-ended agent — https://www.anthropic.com/engineering/building-effective-agents (industry engineering blog, not peer-reviewed).
- **LangGraph docs, "Interrupts" (docs.langchain.com, opened 25 Oct 2026).** `interrupt()` pauses the graph inside a node, saves state and returns a JSON-serializable value to the caller; requires a checkpointer and a `thread_id`; resumed with `Command(resume=value)`, whose value becomes interrupt()'s return value. Caveats: the node restarts from its beginning on resume, so pre-interrupt code must be idempotent and side effects should come after the interrupt; do not wrap interrupt() in a bare try/except; keep interrupt ordering deterministic; avoid `while True` loops around it. Newer versions (langgraph>=1.2.12 per the page) accept a `response_schema` to validate resume values. Use cases listed: approval, review-and-edit, tool interrupts, input validation. Relevance: exactly the mechanism for the OCR-character-in-doubt question and for confirm-before-saving to the cabinet; validated typed resume values align with rejecting free-text answers — https://docs.langchain.com/oss/python/langgraph/interrupts
- **LangGraph docs, checkpoint/persistence page (opened via the durable-execution URL, 25 Oct 2026).** Checkpointers persist thread-scoped graph state as checkpoints enabling conversation continuity, human-in-the-loop, time travel and fault tolerance; InMemorySaver is lost on restart; SqliteSaver is suggested for local development and PostgresSaver for production; checkpoints accumulate, so pruning/retention is suggested. The page I got did NOT define "durable execution", determinism or durability modes. Relevance: SqliteSaver fits a laptop-local, offline deployment and gives replayable runs for evaluation — https://docs.langchain.com/oss/python/langgraph/durable-execution
- **Hong, Zhuge, Chen, Zheng, Cheng, Zhang, Wang, Wang, Yau, Lin, Zhou, Ran, Xiao, Wu, Schmidhuber (15 authors). "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework."** arXiv:2308.00352, submitted 1 Aug 2023, v7 1 Nov 2024. Encodes standardized operating procedures (SOPs) into prompt sequences with assembly-line role specialization; argues naive chaining of LLMs causes cascading hallucinations and logic inconsistencies; agents with domain roles verify intermediate results, reportedly giving more coherent software-engineering outputs than chat-based multi-agent systems. Relevance: supports fixed role pipeline (reader, retriever, corroborator, verifier) over free-form agent chat — https://arxiv.org/abs/2308.00352. Caveat: the arXiv page shows no venue (ICLR 2024 per background knowledge, unconfirmed).
- **Wu, Bansal, Zhang, Wu, Li, Zhu, Jiang, Zhang, Zhang, Liu, Awadallah, White, Burger, Wang. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation."** arXiv:2308.08155, 16 Aug 2023 (v2 3 Oct 2023), arXiv preprint (no venue shown on page). Open-source framework of customizable, conversable agents combining LLMs, human input and tools; conversation patterns programmable in natural language and code; evaluated on math, coding, QA, operations research, online decision-making. Relevance: human-proxy agents are a precedent for human-in-the-loop, but conversational multi-agent loops are harder to bound and audit than a graph — https://arxiv.org/abs/2308.08155
- **Wang, Ma, Feng, Zhang, Yang, Zhang, Chen, Tang, Chen, Lin, Zhao, Wei, Wen. "A Survey on Large Language Model based Autonomous Agents."** arXiv:2308.11432 (first posted 22 Aug 2023; v7 2 Mar 2025); related DOI listed 10.1007/s11704-024-40231-1 (journal presumably Frontiers of Computer Science, Springer, but the arXiv page did not confirm — verify before citing as a journal paper). Proposes a unified framework for building LLM agents and reviews applications and evaluation methods. Relevance: taxonomy for the Related Work section (profile/memory/planning/action modules map onto StripCheck's memory cabinet, planner, tools) — https://arxiv.org/abs/2308.11432
- **Li, Hammoud, Itani, Khizbullin, Ghanem. "CAMEL: Communicative Agents for 'Mind' Exploration of Large Language Model Society."** NeurIPS 2023 (stated on the arXiv page); arXiv:2303.17760, 31 Mar 2023 (v2 2 Nov 2023). Role-playing framework in which communicative agents cooperate autonomously, kept on task via "inception prompting"; releases library and conversation data. Relevance: representative of free-form multi-agent role-play; StripCheck deliberately avoids this (unbounded dialogue, no ground truth) in favor of a fixed supervisor graph — https://arxiv.org/abs/2303.17760
- **Xi et al. (29 authors, Zhiheng Xi first). "The Rise and Potential of Large Language Model Based Agents: A Survey."** arXiv:2309.07864, 14 Sep 2023 (v3 19 Sep 2023), 86 pages. Brain/perception/action framework; reviews single-agent, multi-agent and human-agent cooperation settings, plus open problems. Relevance: perception (OCR/VLM) + brain (planner) + action (tools) decomposition and the human-agent cooperation category — https://arxiv.org/abs/2309.07864

### Inferences
- A supervisor-style fixed graph with a verifier node, bounded iterations and an interrupt() for human clarification is consistent with Anthropic's "workflow first" advice; MetaGPT's SOP idea is the multi-agent analogue. The StripCheck "agents" (ingest, retriever, verifier) are best described as specialised nodes/roles under a deterministic supervisor, not autonomous peers.
- Because LangGraph re-runs the interrupted node from its start on resume, the OCR/lookup work before the question must be idempotent or placed in earlier nodes (design implication drawn from the docs, not stated by them for StripCheck).

### Gaps
- LangGraph "durable execution" page content (durability modes, task wrapping) could not be confirmed: the two URLs opened covered only checkpoint basics. Do not cite durability modes until verified.
- Peer-reviewed venues for MetaGPT, AutoGen and the two surveys' journal version are not confirmed from opened sources.

## KQ4 Small language models for agents; structured output and constrained decoding

### Takeaway
A position paper argues SLMs suffice and are more economical for the narrow repetitive calls agents make; constrained decoding gives schema-valid output (and, per JSONSchemaBench, did not hurt and slightly helped small-model accuracy), but strict JSON schemas can degrade free-form reasoning (Tam et al.), so StripCheck should keep the LLM's output schema small, put reasoning before the answer, and validate everything downstream with deterministic code.

### Cited Findings
- **Belcak, Heinrich, Diao, Fu, Dong, Muralidharan, Lin, Molchanov. "Small Language Models are the Future of Agentic AI."** arXiv:2506.02153, v1 2 Jun 2025, v3 22 Sep 2026 (current version when I opened it on 25 Oct 2026); arXiv preprint, no venue listed; CC BY 4.0. Position paper (not an empirical benchmark): agentic systems mostly invoke LMs for a few specialised, repetitive tasks, so SLMs are "sufficiently powerful, inherently more suitable, and necessarily more economical" for many invocations; heterogeneous multi-model agents where general conversation is needed; outlines barriers and an LLM-to-SLM agent conversion algorithm. No numbers in the abstract. Relevance: direct justification for running a small Ollama model as planner/adjudicator for narrow, schema-bound sub-tasks; also a reminder that it is an opinion piece, so StripCheck must measure its own SLM — https://arxiv.org/abs/2506.02153
- **Willard and Louf. "Efficient Guided Generation for Large Language Models."** arXiv:2307.09702, submitted 19 Jul 2023 (v4 19 Aug 2023); arXiv preprint (no venue on page). Recasts generation as finite-state-machine transitions, indexing the vocabulary so regex/CFG constraints are enforced during decoding with little overhead; any model; implemented in the open-source Outlines library; guarantees output structure. Relevance: foundational method behind schema-constrained output for local models — https://arxiv.org/abs/2307.09702
- **Dong, Ruan, Cai, Lai, Xu, Zhao, Chen. "XGrammar: Flexible and Efficient Structured Generation Engine for Large Language Models."** MLSys 2025 (per arXiv page); arXiv:2411.15100, 22 Nov 2024 (v3 12 May 2025). Splits the vocabulary into context-independent tokens (precomputed masks) and context-dependent tokens (checked at runtime), with a persistent stack and overlap with GPU execution; up to 100x speedup over existing solutions and near-zero overhead in end-to-end serving (authors' claim from the abstract). Relevance: engine-level support for constrained output on local runtimes — https://arxiv.org/abs/2411.15100. I did not verify whether Ollama uses XGrammar internally (not stated on pages I opened).
- **Tam, Wu, Tsai, Lin, Lee, Chen. "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models."** arXiv:2408.02442, 5 Aug 2024 (v3 14 Oct 2024); the page shows no peer-reviewed venue (EMNLP 2024 Industry Track per background knowledge, unconfirmed). Tested GPT-3.5-Turbo, Claude-3-Haiku, Gemini-1.5-Flash, LLaMA-3-8B-Instruct, Gemma-2-9B-Instruct (Mistral-7B and GPT-4o-mini in the appendix). Reasoning tasks (GSM8K, Last Letter, Shuffled Objects) often drop under JSON/XML/YAML; e.g., LLaMA-3-8B GSM8K 74.7 (natural language) vs 48.9 (JSON), Last Letter 70.1 vs 28.0; Claude-3-Haiku GSM8K 86.5 vs 23.4 with a full JSON schema but 87.0 with plain "JSON" and no schema; Gemini-1.5-Flash was nearly unaffected. Classification tasks (e.g., DDXPlus: Gemini 41.6 -> 60.3 with JSON; GPT-3.5 44.1 -> 55.5) often improved. Recommendations: put reasoning before answer in the schema, consider free-text reasoning then a separate format-conversion step, use corrective re-prompts for parse failures, and test per model. Limitations they state: few models, small tasks, simple two-field outputs, no 70B-class model. Relevance: StripCheck's adjudicator is closer to classification (choose among candidates) where structure helps, but any free-form reasoning should not be forced into rigid JSON — https://arxiv.org/abs/2408.02442 (numbers read from arxiv.org/html/2408.02442v3).
- **Geng, Cooper, Moskal, Jenkins, Berman, Ranchin, West, Horvitz, Nori. "JSONSchemaBench: A Rigorous Benchmark of Structured Outputs for Language Models."** arXiv:2501.10868, 18 Jan 2025 (v3 27 Feb 2025); no peer-reviewed venue on the page. 10,000 real-world JSON schemas plus the official JSON Schema Test Suite; evaluates Guidance, Outlines, Llamacpp, XGrammar, OpenAI, Gemini. Findings (read from arxiv.org/html/2501.10868v3; first 100,000 of ~111,000 characters read): on GitHub-Hard schemas empirical coverage/compliance were Guidance 0.41/0.69, Llamacpp 0.39/0.63, XGrammar 0.28/0.41, Outlines 0.03/0.06; i.e., engines differ a lot and complex schemas often fail; closed APIs have high compliance but low coverage (support only a subset of JSON Schema). With Llama-3.1-8B-Instruct, constrained decoding did not reduce downstream accuracy (GSM8K 80.1% unconstrained vs 83.7-83.8% with XGrammar/Guidance; Last Letters 50.7% vs up to 54.0%); constrained decoding can also be ~50% faster per token than unconstrained for Guidance with the Llamacpp backend. Relevance: keep schemas simple, validate even when decoding is constrained, pick the engine empirically — https://arxiv.org/abs/2501.10868
- **Ollama documentation, "Structured outputs" (docs.ollama.com, opened 25 Oct 2026).** The chat API `format` parameter accepts "json" or a JSON Schema object; Pydantic `model_json_schema()` / `model_validate_json()` recommended; tips: temperature 0, and also include the schema in the prompt. Relevance: the concrete way StripCheck's planner/adjudicator/ingest-repair outputs are constrained and re-validated — https://docs.ollama.com/capabilities/structured-outputs

### Inferences
- Constrained decoding guarantees syntax, not truth: a schema-valid answer can still be a wrong batch or hallucinated date, so field-level verification (verifier) remains necessary. This is my reasoning, consistent with the Kambhampati et al. argument in KQ2.
- Tam et al.'s degradation was observed on reasoning benchmarks and mostly with API models; JSONSchemaBench found no loss for an 8B model on its (different) tasks. The two results are not contradictory but are not directly comparable (different prompts, tasks, enforcement mechanism).

### Gaps
- No peer-reviewed empirical study of ~1-8B models as tool-calling agents (e.g., Berkeley Function-Calling Leaderboard) has been opened yet for this section; Belcak et al. is a position paper.
- Venue for Willard and Louf (arXiv only on the page) and Tam et al. (unconfirmed) should be re-checked before the thesis.

## KQ5 Evaluation, observability, high-stakes reliability

### Takeaway
Benchmark literature stresses reliability over single-run accuracy (tau-bench pass^k), cost-aware evaluation (Kapoor et al.), small-model weakness in instruction following (AgentBench), and abstention/asking as first-class tool-use skills (BFCL, When2Call) — all directly supporting StripCheck's CANT_VERIFY verdict, repeated-trial evaluation and cost reporting.

### Cited Findings
- **Kapoor, Stroebl, Siegel, Nadgir, Narayanan. "AI Agents That Matter."** arXiv:2407.01502, 1 Jul 2024; arXiv preprint (no venue listed on page). Argues agent benchmarks suffer from (1) narrow focus on accuracy -> should jointly optimise cost and accuracy; (2) conflated needs of model developers vs downstream developers; (3) inadequate holdout sets -> brittle, shortcut-taking agents; (4) lack of standardised evaluation -> reproducibility problems. No numbers on the abstract page. Relevance: StripCheck evaluation should report cost/latency, use held-out batches/images, and publish a reproducible harness — https://arxiv.org/abs/2407.01502
- **Yao, Shinn, Razavi, Narasimhan. "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains."** arXiv:2406.12045, 17 Jun 2024; arXiv preprint (no venue listed on page). Simulated user + agent with domain API tools and policy; scored by comparing end database state with annotated goal state; introduces pass^k (reliability across k trials). gpt-4o-class function-calling agents succeed on fewer than 50% of tasks and pass^8 is below 25% in the retail domain. Relevance: supports (a) end-state/outcome-based evaluation (StripCheck verdict + final fields vs ground truth), (b) repeated trials to measure consistency of a stochastic local LLM, (c) policy/rule-following as a known weakness motivating the hard-rule verifier — https://arxiv.org/abs/2406.12045
- **Liu et al. (22 authors; Xiao Liu first; Jie Tang last). "AgentBench: Evaluating LLMs as Agents."** ICLR 2024 (per arXiv comments); arXiv:2308.03688, 7 Aug 2023 (v3 4 Oct 2025). 8 environments; strong commercial LLMs perform well as agents, but a significant gap remains to many open-source models of 70B parameters or fewer; main failure causes: weak long-term reasoning, poor decision-making and weak instruction following. Relevance: a caution that small open models are the weak point of agent loops, motivating deterministic fallback plus bounded steps; (number of models tested not captured from my fetch) — https://arxiv.org/abs/2308.03688
- **Patil, Mao, Yan, Ji, Suresh, Stoica, Gonzalez. "The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models."** Proceedings of the 42nd ICML (ICML 2025), PMLR vol. 267, pp. 48371-48392. AST-based evaluation of serial/parallel function calls across languages; also tests abstention and stateful multi-step settings; finds top LLMs good at single-turn calls while memory, dynamic decision-making and long-horizon reasoning remain open challenges. Relevance: provides a way to select the local model for the planner by function-calling ability (including abstention) — https://proceedings.mlr.press/v267/patil25a.html
- **Ross, Mahabaleshwarkar, Suhara. "When2Call: When (not) to Call Tools."** NAACL 2025 (Long Papers), Albuquerque, pp. 3391-3409, DOI 10.18653/v1/2025.naacl-long.174. Benchmark of whether to call a tool, ask a follow-up question, or state the question cannot be answered with the tools provided; existing tool-calling models have considerable room to improve; preference optimisation on the multiple-choice format gave larger gains than ordinary fine-tuning. Relevance: peer-reviewed support for treating "ask the user" and "abstain" as first-class actions, as StripCheck does with its human question and CANT_VERIFY — https://aclanthology.org/2025.naacl-long.174/ (abstract only read; no numbers).

- **OpenTelemetry GenAI semantic conventions (primary documentation).** On 25 Oct 2026 the opentelemetry.io page (https://opentelemetry.io/docs/specs/semconv/gen-ai/) was only a "moved" notice saying the conventions now live in https://github.com/open-telemetry/semantic-conventions-genai (Apache-2.0, 670 commits at access; no releases listed; schema URL field "TODO"). That repo covers spans, metrics and events for GenAI clients, MCP and provider-specific conventions. The pages I opened did NOT state stability status or confirm span names such as `invoke_agent`/`execute_tool`. Relevance: vendor-neutral target schema for logging each StripCheck step (OCR read, lookup, verifier decision); cite only as "OpenTelemetry GenAI semantic conventions, repository as of 25 Oct 2026" and check stability status before the thesis.
- **OpenInference (Arize AI, GitHub README, opened 25 Oct 2026).** Conventions and plugins "complementary to OpenTelemetry" for tracing AI applications (LLM calls, retrieval, tool use); transport-agnostic; Apache-2.0; Python `openinference-instrumentation-langchain` package exists; Arize Phoenix is a native backend and an example points at a local Phoenix endpoint (localhost:6006). I could not confirm span-kind names, LangGraph-specific support or offline operation from the page. Relevance: a free, local trace viewer option for a no-paid-API deployment — https://github.com/Arize-ai/openinference
- **Jiang, Black, Geng, Park, Zou, Ng, Chen. "MedAgentBench: A Realistic Virtual EHR Environment to Benchmark Medical LLM Agents."** arXiv:2501.14654, 24 Jan 2025 (v2 12 Feb 2025); the arXiv page names no venue (a search-result summary said NEJM AI 2025; unconfirmed). 300 physician-written tasks in 10 categories, 100 patient profiles with >700,000 data elements, FHIR-compliant environment; best model (Claude 3.5 Sonnet v2) 69.67% success. Relevance: healthcare agent evaluation precedent that scores task outcome in a realistic tool environment — https://arxiv.org/abs/2501.14654
- **Tripathi, Roy, Neupane, Rahimi. "How Compliant is Sepsis Treatment? An Expert-Guided Neuro-symbolic Pipeline for Generating Clinical Compliance Insights."** NeSy 2026 (accepted, per arXiv comments); arXiv:2608.13617, submitted 12 Aug 2026. The LLM is used only to normalise messy drug/microbiology strings into a fixed clinical vocabulary; a Sugeno fuzzy inference system encoding eight Surviving Sepsis Campaign bundle rules does the judging; 2,438 MIMIC-IV v3.1 episodes. Relevance: closest 2026 analogue to StripCheck's pattern (LLM normalises, rules decide) in a safety-critical clinical setting; no accuracy of the LLM normalisation step was captured from the abstract — https://arxiv.org/abs/2608.13617
- **Srivastava, Ghosh, Verma, Buyya. "Agentic AI-based Framework for Mitigating Premature Diagnostic Handoff and Silent Hallucination in Healthcare Applications."** arXiv:2606.18068, 16 Jun 2026 (preprint; no venue). Multi-agent framework with deterministic orchestration constraints instead of LLM-as-judge routing; a neuro-symbolic gate blocks transitions until eight OLDCARTS dimensions are collected, plus a semantic-entropy uncertainty gate (K=5 samples); simulated patients (llama-3.1-70b), 150 cases; 49.3% diagnostic precision, +11.3 percentage points over an unconstrained baseline. Relevance: supports deterministic gating and uncertainty-triggered interception; modest absolute precision and simulation-only evaluation limit the strength of the claim — https://arxiv.org/abs/2606.18068
- **Qu, Ranaldi, Wang, Valentino. "Neurosymbolic Clinical Trial Matching via LLM-Driven Abduction and Logical Verification."** arXiv:2606.20895, 18 Jun 2026 (preprint). LLM plus logical verification for noisy incomplete records; up to 30% relative improvement over zero-shot baselines. Relevance: another 2026 instance of "LLM proposes, symbolic verifier checks" — https://arxiv.org/abs/2606.20895
- **Turan, E. "Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human."** arXiv:2606.08919, 8 Jun 2026; preprint, single author, 12 pages. On 125 hand-labelled agent actions, reviewer agreement on "risky" was only Fleiss' kappa = 0.52; modelling shows safety peaks at an intermediate escalation rate (inverted U), i.e., escalating everything to a human can reduce safety due to fatigue; findings are modelling results awaiting a human study. Relevance: argues for asking the user only when a character is genuinely ambiguous (StripCheck's design), not on every scan — https://arxiv.org/abs/2606.08919
- **Shi and DiFranzo. "When Agents Act Unwatched: The Reduced-Supervision Paradox in Agentic AI."** arXiv:2609.29547 (submitted 28 Aug 2026 per the page; ID suggests September, verify); preprint, 24 pages. Audit of 63 public artifacts (46 papers, 17 engineering/governance sources): tool mediation visible in 40, monitoring traces in 37, checkpoint placement in 6, validator independence in 4, recovery in 2, contestability in 1; warns that observability can substitute for accountability. Relevance: motivates StripCheck's independent validator (rules separate from planner), checkpointing and recovery (quarantine) as explicitly rare in current practice (limited to public artifacts) — https://arxiv.org/abs/2609.29547

### Inferences
- Combined, these support evaluating StripCheck on end-state correctness (verdict + fields), with repeated runs for the stochastic planner, cost/latency and an abstention metric, not just OCR accuracy.
- The 2026 healthcare neuro-symbolic papers are preprints/workshop-level; they corroborate the architecture pattern but are not strong independent proof. No healthcare-specific peer-reviewed study of verifier-checked agents with abstention was found.

### Gaps
- OpenTelemetry stability status and agent-span names; OpenInference span kinds: not confirmed.
- A US Department of Defense "Careful adoption of agentic AI services" PDF (Apr 2026) surfaced in search but returned HTTP 403, so it is NOT cited. Vendor guardrail guides and news (Imprivata report via Healthcare Dive) were seen only as search snippets and are not used.
- Search results for several 2026 arXiv items appeared only as snippets; only those opened above are cited. The Singapore Consensus (arXiv:2608.14611, 9 Jul 2026) was opened but only its abstract mentions agent risks; not used as evidence.

## BibTeX

@inproceedings{yao2023react,
  author = {Yao, Shunyu and Zhao, Jeffrey and Yu, Dian and Du, Nan and Shafran, Izhak and Narasimhan, Karthik and Cao, Yuan},
  title = {{ReAct}: Synergizing Reasoning and Acting in Language Models},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year = {2023},
  note = {arXiv:2210.03629; venue per arXiv v3 comments},
  url = {https://arxiv.org/abs/2210.03629}
}

@misc{karpas2022mrkl,
  author = {Karpas, Ehud and Abend, Omri and Belinkov, Yonatan and Lenz, Barak and Lieber, Opher and Ratner, Nir and Shoham, Yoav and Bata, Hofit and Levine, Yoav and Leyton-Brown, Kevin and Muhlgay, Dor and Rozen, Noam and Schwartz, Erez and Shachaf, Gal and Shalev-Shwartz, Shai and Shashua, Amnon and Tenenholtz, Moshe},
  title = {{MRKL} Systems: A modular, neuro-symbolic architecture that combines large language models, external knowledge sources and discrete reasoning},
  year = {2022},
  howpublished = {arXiv preprint arXiv:2205.00445},
  url = {https://arxiv.org/abs/2205.00445}
}

@misc{schick2023toolformer,
  author = {Schick, Timo and Dwivedi-Yu, Jane and Dess{\`i}, Roberto and Raileanu, Roberta and Lomeli, Maria and Zettlemoyer, Luke and Cancedda, Nicola and Scialom, Thomas},
  title = {Toolformer: Language Models Can Teach Themselves to Use Tools},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2302.04761},
  note = {NeurIPS 2023 per background knowledge; venue not confirmed from the opened page},
  url = {https://arxiv.org/abs/2302.04761}
}

@misc{shinn2023reflexion,
  author = {Shinn, Noah and Cassano, Federico and Berman, Edward and Gopinath, Ashwin and Narasimhan, Karthik and Yao, Shunyu},
  title = {Reflexion: Language Agents with Verbal Reinforcement Learning},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2303.11366},
  note = {v4, 10 Oct 2023; venue not confirmed from the opened page},
  url = {https://arxiv.org/abs/2303.11366}
}

@misc{madaan2023selfrefine,
  author = {Madaan, Aman and Tandon, Niket and Gupta, Prakhar and Hallinan, Skyler and Gao, Luyu and Wiegreffe, Sarah and Alon, Uri and Dziri, Nouha and Prabhumoye, Shrimai and Yang, Yiming and Gupta, Shashank and Majumder, Bodhisattwa Prasad and Hermann, Katherine and Welleck, Sean and Yazdanbakhsh, Amir and Clark, Peter},
  title = {Self-Refine: Iterative Refinement with Self-Feedback},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2303.17651},
  note = {v2, 25 May 2023; venue not confirmed from the opened page},
  url = {https://arxiv.org/abs/2303.17651}
}

@inproceedings{gou2024critic,
  author = {Gou, Zhibin and Shao, Zhihong and Gong, Yeyun and Shen, Yelong and Yang, Yujiu and Duan, Nan and Chen, Weizhu},
  title = {{CRITIC}: Large Language Models Can Self-Correct with Tool-Interactive Critiquing},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year = {2024},
  note = {arXiv:2305.11738; venue per arXiv comments field},
  url = {https://arxiv.org/abs/2305.11738}
}

@inproceedings{huang2024cannot,
  author = {Huang, Jie and Chen, Xinyun and Mishra, Swaroop and Zheng, Huaixiu Steven and Yu, Adams Wei and Song, Xinying and Zhou, Denny},
  title = {Large Language Models Cannot Self-Correct Reasoning Yet},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year = {2024},
  note = {arXiv:2310.01798},
  url = {https://arxiv.org/abs/2310.01798}
}

@inproceedings{kambhampati2024llmmodulo,
  author = {Kambhampati, Subbarao and Valmeekam, Karthik and Guan, Lin and Verma, Mudit and Stechly, Kaya and Bhambri, Siddhant and Saldyt, Lucas and Murthy, Anil},
  title = {{LLMs} Can't Plan, But Can Help Planning in {LLM-Modulo} Frameworks},
  booktitle = {Proceedings of the 41st International Conference on Machine Learning},
  series = {Proceedings of Machine Learning Research},
  volume = {235},
  year = {2024},
  address = {Vienna, Austria},
  note = {arXiv:2402.01817; volume and venue per arXiv listing, PMLR page not opened},
  url = {https://arxiv.org/abs/2402.01817}
}

@misc{schluntz2024building,
  author = {Erik S. and Zhang, Barry},
  title = {Building effective agents},
  year = {2024},
  howpublished = {Anthropic Engineering blog, published 19 Dec 2024},
  url = {https://www.anthropic.com/engineering/building-effective-agents},
  note = {Accessed 25 Oct 2026. First author's surname shown only as "Erik S." on the opened page}
}

@misc{langchain2026interrupts,
  author = {{LangChain, Inc.}},
  title = {LangGraph documentation: Interrupts},
  year = {2026},
  url = {https://docs.langchain.com/oss/python/langgraph/interrupts},
  note = {Accessed 25 Oct 2026}
}

@misc{langchain2026persistence,
  author = {{LangChain, Inc.}},
  title = {LangGraph documentation: Persistence and checkpointers (page served at the durable-execution URL)},
  year = {2026},
  url = {https://docs.langchain.com/oss/python/langgraph/durable-execution},
  note = {Accessed 25 Oct 2026}
}

@misc{hong2023metagpt,
  author = {Hong, Sirui and Zhuge, Mingchen and Chen, Jiaqi and Zheng, Xiawu and Cheng, Yuheng and Zhang, Ceyao and Wang, Jinlin and Wang, Zili and Yau, Steven Ka Shing and Lin, Zijuan and Zhou, Liyang and Ran, Chenyu and Xiao, Lingfeng and Wu, Chenglin and Schmidhuber, J{\"u}rgen},
  title = {{MetaGPT}: Meta Programming for A Multi-Agent Collaborative Framework},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2308.00352},
  note = {v7, 1 Nov 2024; venue not confirmed from the opened page},
  url = {https://arxiv.org/abs/2308.00352}
}

@misc{wu2023autogen,
  author = {Wu, Qingyun and Bansal, Gagan and Zhang, Jieyu and Wu, Yiran and Li, Beibin and Zhu, Erkang and Jiang, Li and Zhang, Xiaoyun and Zhang, Shaokun and Liu, Jiale and Awadallah, Ahmed Hassan and White, Ryen W. and Burger, Doug and Wang, Chi},
  title = {{AutoGen}: Enabling Next-Gen {LLM} Applications via Multi-Agent Conversation},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2308.08155},
  url = {https://arxiv.org/abs/2308.08155}
}

@inproceedings{li2023camel,
  author = {Li, Guohao and Hammoud, Hasan Abed Al Kader and Itani, Hani and Khizbullin, Dmitrii and Ghanem, Bernard},
  title = {{CAMEL}: Communicative Agents for Mind Exploration of Large Language Model Society},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year = {2023},
  note = {arXiv:2303.17760; venue per arXiv page},
  url = {https://arxiv.org/abs/2303.17760}
}

@misc{wang2023survey,
  author = {Wang, Lei and Ma, Chen and Feng, Xueyang and Zhang, Zeyu and Yang, Hao and Zhang, Jingsen and Chen, Zhiyuan and Tang, Jiakai and Chen, Xu and Lin, Yankai and Zhao, Wayne Xin and Wei, Zhewei and Wen, Ji-Rong},
  title = {A Survey on Large Language Model based Autonomous Agents},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2308.11432},
  note = {v7 2 Mar 2025; related DOI listed on arXiv page 10.1007/s11704-024-40231-1 (journal version unverified)},
  url = {https://arxiv.org/abs/2308.11432}
}

@misc{belcak2025slm,
  author = {Belcak, Peter and Heinrich, Greg and Diao, Shizhe and Fu, Yonggan and Dong, Xin and Muralidharan, Saurav and Lin, Yingyan Celine and Molchanov, Pavlo},
  title = {Small Language Models are the Future of Agentic {AI}},
  year = {2025},
  howpublished = {arXiv preprint arXiv:2506.02153},
  note = {v1 2 Jun 2025; v3 22 Sep 2026; accessed 25 Oct 2026},
  url = {https://arxiv.org/abs/2506.02153}
}

@misc{willard2023outlines,
  author = {Willard, Brandon T. and Louf, R{\'e}mi},
  title = {Efficient Guided Generation for Large Language Models},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2307.09702},
  url = {https://arxiv.org/abs/2307.09702}
}

@inproceedings{dong2025xgrammar,
  author = {Dong, Yixin and Ruan, Charlie F. and Cai, Yaxing and Lai, Ruihang and Xu, Ziyi and Zhao, Yilong and Chen, Tianqi},
  title = {{XGrammar}: Flexible and Efficient Structured Generation Engine for Large Language Models},
  booktitle = {Proceedings of Machine Learning and Systems (MLSys)},
  year = {2025},
  note = {arXiv:2411.15100; venue per arXiv page; proceedings pages not opened},
  url = {https://arxiv.org/abs/2411.15100}
}

@misc{tam2024speak,
  author = {Tam, Zhi Rui and Wu, Cheng-Kuang and Tsai, Yi-Lin and Lin, Chieh-Yen and Lee, Hung-yi and Chen, Yun-Nung},
  title = {Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models},
  year = {2024},
  howpublished = {arXiv preprint arXiv:2408.02442},
  note = {v3 14 Oct 2024; peer-reviewed venue not confirmed from the opened page},
  url = {https://arxiv.org/abs/2408.02442}
}

@misc{geng2025jsonschemabench,
  author = {Geng, Saibo and Cooper, Hudson and Moskal, Micha{\l} and Jenkins, Samuel and Berman, Julian and Ranchin, Nathan and West, Robert and Horvitz, Eric and Nori, Harsha},
  title = {{JSONSchemaBench}: A Rigorous Benchmark of Structured Outputs for Language Models},
  year = {2025},
  howpublished = {arXiv preprint arXiv:2501.10868},
  note = {v3 27 Feb 2025},
  url = {https://arxiv.org/abs/2501.10868}
}

@misc{ollama2026structured,
  author = {{Ollama}},
  title = {Structured outputs},
  year = {2026},
  howpublished = {Ollama documentation},
  url = {https://docs.ollama.com/capabilities/structured-outputs},
  note = {Accessed 25 Oct 2026}
}

@misc{kapoor2024agents,
  author = {Kapoor, Sayash and Stroebl, Benedikt and Siegel, Zachary S. and Nadgir, Nitya and Narayanan, Arvind},
  title = {{AI} Agents That Matter},
  year = {2024},
  howpublished = {arXiv preprint arXiv:2407.01502},
  url = {https://arxiv.org/abs/2407.01502}
}

@misc{yao2024taubench,
  author = {Yao, Shunyu and Shinn, Noah and Razavi, Pedram and Narasimhan, Karthik},
  title = {$\tau$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains},
  year = {2024},
  howpublished = {arXiv preprint arXiv:2406.12045},
  url = {https://arxiv.org/abs/2406.12045}
}

@inproceedings{liu2024agentbench,
  author = {Liu, Xiao and Yu, Hao and Zhang, Hanchen and Xu, Yifan and Lei, Xuanyu and Lai, Hanyu and Gu, Yu and Ding, Hangliang and Men, Kaiwen and Yang, Kejuan and Zhang, Shudan and Deng, Xiang and Zeng, Aohan and Du, Zhengxiao and Zhang, Chenhui and Shen, Sheng and Zhang, Tianjun and Su, Yu and Sun, Huan and Huang, Minlie and Dong, Yuxiao and Tang, Jie},
  title = {{AgentBench}: Evaluating {LLMs} as Agents},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year = {2024},
  note = {arXiv:2308.03688; venue per arXiv comments; v3 4 Oct 2025},
  url = {https://arxiv.org/abs/2308.03688}
}

@inproceedings{patil2025bfcl,
  author = {Patil, Shishir G. and Mao, Huanzhi and Yan, Fanjia and Ji, Charlie Cheng-Jie and Suresh, Vishnu and Stoica, Ion and Gonzalez, Joseph E.},
  title = {The {B}erkeley Function Calling Leaderboard ({BFCL}): From Tool Use to Agentic Evaluation of Large Language Models},
  booktitle = {Proceedings of the 42nd International Conference on Machine Learning},
  series = {Proceedings of Machine Learning Research},
  volume = {267},
  pages = {48371--48392},
  year = {2025},
  url = {https://proceedings.mlr.press/v267/patil25a.html}
}

@inproceedings{ross2025when2call,
  author = {Ross, Hayley and Mahabaleshwarkar, Ameya Sunil and Suhara, Yoshi},
  title = {{When2Call}: When (not) to Call Tools},
  booktitle = {Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)},
  pages = {3391--3409},
  address = {Albuquerque, New Mexico},
  year = {2025},
  doi = {10.18653/v1/2025.naacl-long.174},
  url = {https://aclanthology.org/2025.naacl-long.174/}
}

@misc{otel2026genai,
  author = {{OpenTelemetry Authors}},
  title = {Semantic conventions for generative AI ({semantic-conventions-genai} repository)},
  year = {2026},
  url = {https://github.com/open-telemetry/semantic-conventions-genai},
  note = {Accessed 25 Oct 2026. The opentelemetry.io page at /docs/specs/semconv/gen-ai/ only redirects here}
}

@misc{arize2026openinference,
  author = {{Arize AI}},
  title = {{OpenInference}: conventions and plugins for tracing {AI} applications},
  year = {2026},
  url = {https://github.com/Arize-ai/openinference},
  note = {Accessed 25 Oct 2026}
}

@misc{jiang2025medagentbench,
  author = {Jiang, Yixing and Black, Kameron C. and Geng, Gloria and Park, Danny and Zou, James and Ng, Andrew Y. and Chen, Jonathan H.},
  title = {{MedAgentBench}: A Realistic Virtual {EHR} Environment to Benchmark Medical {LLM} Agents},
  year = {2025},
  howpublished = {arXiv preprint arXiv:2501.14654},
  note = {v2 12 Feb 2025; a search summary reported NEJM AI 2025 publication, not confirmed},
  url = {https://arxiv.org/abs/2501.14654}
}

@misc{tripathi2026sepsis,
  author = {Tripathi, Himanshu and Roy, Kaushik and Neupane, Subash and Rahimi, Shahram},
  title = {How Compliant is Sepsis Treatment? An Expert-Guided Neuro-symbolic Pipeline for Generating Clinical Compliance Insights},
  year = {2026},
  howpublished = {arXiv preprint arXiv:2608.13617},
  note = {Accepted at NeSy 2026 per arXiv comments; submitted 12 Aug 2026},
  url = {https://arxiv.org/abs/2608.13617}
}

@misc{srivastava2026handoff,
  author = {Srivastava, Divyansh and Ghosh, Shreya and Verma, Anshul and Buyya, Rajkumar},
  title = {Agentic {AI}-based Framework for Mitigating Premature Diagnostic Handoff and Silent Hallucination in Healthcare Applications},
  year = {2026},
  howpublished = {arXiv preprint arXiv:2606.18068},
  note = {Submitted 16 Jun 2026; no venue listed},
  url = {https://arxiv.org/abs/2606.18068}
}

@misc{qu2026neurosymbolic,
  author = {Qu, Baiyang and Ranaldi, Leonardo and Wang, Xi and Valentino, Marco},
  title = {Neurosymbolic Clinical Trial Matching via {LLM}-Driven Abduction and Logical Verification},
  year = {2026},
  howpublished = {arXiv preprint arXiv:2606.20895},
  note = {Submitted 18 Jun 2026; no venue listed},
  url = {https://arxiv.org/abs/2606.20895}
}

@misc{turan2026oversight,
  author = {Turan, Emre},
  title = {Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human},
  year = {2026},
  howpublished = {arXiv preprint arXiv:2606.08919},
  note = {Submitted 8 Jun 2026; no venue listed},
  url = {https://arxiv.org/abs/2606.08919}
}

@misc{shi2026unwatched,
  author = {Shi, Hanjing and DiFranzo, Dominic},
  title = {When Agents Act Unwatched: The Reduced-Supervision Paradox in Agentic {AI}},
  year = {2026},
  howpublished = {arXiv preprint arXiv:2609.29547},
  note = {Submitted 28 Aug 2026 per the arXiv page (ID suggests September; verify); no venue listed},
  url = {https://arxiv.org/abs/2609.29547}
}

@misc{xi2023rise,
  author = {Xi, Zhiheng and Chen, Wenxiang and Guo, Xin and He, Wei and Ding, Yiwen and Hong, Boyang and Zhang, Ming and Wang, Junzhe and Jin, Senjie and Zhou, Enyu and Zheng, Rui and Fan, Xiaoran and Wang, Xiao and Xiong, Limao and Zhou, Yuhao and Wang, Weiran and Jiang, Changhao and Zou, Yicheng and Liu, Xiangyang and Yin, Zhangyue and Dou, Shihan and Weng, Rongxiang and Cheng, Wensen and Zhang, Qi and Qin, Wenjuan and Zheng, Yongyan and Qiu, Xipeng and Huang, Xuanjing and Gui, Tao},
  title = {The Rise and Potential of Large Language Model Based Agents: A Survey},
  year = {2023},
  howpublished = {arXiv preprint arXiv:2309.07864},
  url = {https://arxiv.org/abs/2309.07864}
}



## Verification log
Checked 25 Oct 2026 against the arXiv API (titles, authors, dates, comments, journal refs), Crossref, ACL Anthology, PMLR and the live web pages. Entries are in llm_agents.bib.
- yao2023react: VERIFIED (arXiv v3 "ICLR camera ready"; +34% ALFWorld and +10% WebShop confirmed in abstract).
- karpas2022mrkl: VERIFIED (17 authors, 1 May 2022, arXiv only).
- schick2023toolformer: CORRECTED (published NeurIPS 2023 / Advances in NeurIPS 36, pp. 68539-68551, DOI 10.52202/075280-2997 via Crossref; note had said unconfirmed).
- shinn2023reflexion: CORRECTED (NeurIPS 2023, pp. 8634-8652, DOI 10.52202/075280-0377).
- madaan2023selfrefine: CORRECTED (NeurIPS 2023, pp. 46534-46594, DOI 10.52202/075280-2019; 7 tasks and ~20% average gain confirmed).
- gou2024critic: VERIFIED (ICLR 2024 per arXiv comments).
- huang2024cannot: VERIFIED (ICLR 2024 per arXiv comments).
- kambhampati2024llmmodulo: VERIFIED (PMLR 235, ICML 2024 per arXiv journal_ref; PMLR page itself not opened).
- schluntz2024building: VERIFIED with caveat (Anthropic page, 19 Dec 2024, workflow vs agent, stopping conditions and human checkpoints confirmed; byline reads "Erik S. and Barry Zhang", so first author's surname is NOT confirmed from the page; cite as Anthropic if unsure).
- langchain2026interrupts: VERIFIED (interrupt(), checkpointer, thread_id, Command(resume), node restarts, idempotency all confirmed).
- langchain2026persistence: CORRECTED (page at the durable-execution URL is titled "Persistence"; title field fixed).
- hong2023metagpt: VERIFIED (arXiv, 15 authors, v7 1 Nov 2024); published venue (ICLR 2024 in my memory) not confirmed, left as arXiv.
- wu2023autogen: VERIFIED (arXiv, 14 authors); no venue stated on arXiv page; left as arXiv.
- li2023camel: VERIFIED (arXiv comments: NeurIPS 2023).
- wang2023survey: CORRECTED (journal version: Frontiers of Computer Science 18(6), 186345, 2024, DOI 10.1007/s11704-024-40231-1 confirmed via Crossref; entry changed from @misc to @article).
- xi2023rise: VERIFIED (29 authors, 86 pages, arXiv only).
- belcak2025slm: VERIFIED (v1 2 Jun 2025, v3 22 Sep 2026 per arXiv API).
- willard2023outlines: VERIFIED (arXiv only).
- dong2025xgrammar: VERIFIED (arXiv comments "MLSys '25").
- tam2024speak: CORRECTED (peer-reviewed: EMNLP 2024 Industry Track, pp. 1218-1236, DOI 10.18653/v1/2024.emnlp-industry.91; ACL title has "On Large Language Model Performance").
- geng2025jsonschemabench: VERIFIED (arXiv only, 9 authors).
- ollama2026structured: VERIFIED (format accepts "json" or schema, Pydantic, temperature 0 tip).
- kapoor2024agents: VERIFIED (arXiv, 1 Jul 2024).
- yao2024taubench: VERIFIED (<50% success, pass^8 <25% retail confirmed; arXiv only).
- liu2024agentbench: VERIFIED (ICLR 2024; 22 authors; 8 environments; <=70B gap confirmed).
- patil2025bfcl: VERIFIED (PMLR 267, ICML 2025, pp. 48371-48392).
- ross2025when2call: VERIFIED (NAACL 2025, pp. 3391-3409, DOI confirmed).
- otel2026genai: VERIFIED (repo exists, Apache-2.0, scope as described; the 670-commit figure was not rechecked, star/issue counts differ over time).
- arize2026openinference: VERIFIED (Apache-2.0, complementary to OpenTelemetry).
- jiang2025medagentbench: CORRECTED (published in NEJM AI 2(9), 2025, DOI 10.1056/AIdbp2500144; published title is "A Virtual EHR Environment to Benchmark Medical LLM Agents", without "Realistic").
- tripathi2026sepsis: VERIFIED (arXiv API; NeSy 2026 per comments).
- srivastava2026handoff: VERIFIED (arXiv API, 16 Jun 2026).
- qu2026neurosymbolic: VERIFIED ("up to 30% relative improvement over zero-shot baselines" is in abstract; metric/dataset not stated there).
- turan2026oversight: VERIFIED (125 actions, Fleiss kappa 0.52 confirmed). Author first name "Emre" in .bib comes from arXiv listing "Emre Turan".
- shi2026unwatched: VERIFIED (63 artifacts = 46 papers + 17 other; submitted 28 Aug 2026 per arXiv API despite 2609 ID).
- Not independently rechecked: per-item counts in Shi et al. (40/37/6/4/2/1), OpenTelemetry stability status, Tam et al./JSONSchemaBench full-text findings; treat as researcher-reported.
Verification: COMPLETE

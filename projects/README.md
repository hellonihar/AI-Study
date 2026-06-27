# Projects — AI Implementation Blueprints

This directory contains end-to-end project designs that demonstrate how AI concepts translate into deployable systems. Each project follows a consistent template: architecture diagram → project structure → data models → API design → design decisions → monitoring → implementation phases. The goal is not just to describe what was built, but to document *why* every choice was made and what alternatives were considered.

---

## From an AI Architect's Perspective

**Production patterns, not toy demos.** Every project in this directory was designed for real-world constraints — CPU-only inference, regulatory compliance, legacy system integration, human-in-the-loop review cycles, and measurable SLAs. These are the constraints that separate deployed systems from Jupyter notebooks, and they appear in every project regardless of domain.

**Transferable architectural judgment.** The projects span a deliberately broad range of AI techniques:

| Project | Core Technique | Key Constraint |
|---|---|---|
| [RAG System](./rag-system/design.md) | Retrieval-augmented generation | Chunking strategy + embedding accuracy |
| [LLM Workflow API](./llm-workflow-api/design.md) | Provider abstraction + caching | Latency/cost trade-off across providers |
| [AI Evaluation Suite](./ai-evaluation-suite/design.md) | LLM-as-judge + automated metrics | Calibration bias + inter-rater reliability |
| [AI Guardrails](./ai-guardrails/design.md) | Content filtering + PII detection | False positive rate balance |
| [Semantic Search](./semantic-search/design.md) | Hybrid search + RRF fusion | Relevance tuning across document types |
| [AI Analytics Assistant](./ai-analytics-assistant/design.md) | NLG + statistical analysis | Narrative coherence + data accuracy |
| [Prompt Deployment Pipeline](./prompt-deployment-pipeline/design.md) | Canary releases + A/B testing | Prompt regression detection |
| [AI Drift Detection](./ai-drift-detection/design.md) | Statistical drift tests + embeddings | Alert fatigue + false positive tuning |
| [Multi-Agent System](./multi-agent-system/design.md) | Agent coordination + state machines | Fault tolerance + message ordering |
| [Industry Solutions](./industry-solutions/) | Cross-domain AI application | Domain-specific constraints |
| └ [ClaimPulse](./industry-solutions/insurance/claimpulse/design.md) | Document AI + fraud ML + LLM settlement | CPU-only, PHI compliance, 50-state DOI |
| └ [FactoryRL](./industry-solutions/manufacturing-industrial/factoryrl/design.md) | MPC + LightGBM optimization | CPU-only, safety constraints, no neural nets |

Building across these techniques reveals recurring patterns: the same document extraction pipeline appears in claims processing (ClaimPulse) and legal discovery (Semantic Search); the same A/B testing framework appears in prompt deployment and fraud model rollout; the same drift detection monitors both embedding quality and fraud prediction accuracy. An architect who understands these patterns can design any of these systems — the domain is just a configuration layer on top.

**Every decision documented with trade-offs.** Each design doc includes a decision table that lists what was chosen, what was rejected, and the rationale. For example, the RAG system documents why pgvector was chosen over Qdrant (one fewer service, comparable performance at scale). ClaimPulse documents why HTMX was chosen over React (~80% less frontend code for an internal tool). FactoryRL documents why MPC was chosen over PPO (explicit safety constraints for factory environments). These trade-off records are often more valuable than the architecture itself — they save future architects from re-litigating the same decisions.

---

## From a Business Stakeholder's Perspective

**Investment-ready blueprints.** Every project includes:
- A concrete business problem with measurable current-state pain (e.g., "14 days average cycle time")
- A specific AI solution with scope boundaries (what's in, what's out)
- Scope deliverables covering integrations, compliance, workflow changes, and success metrics
- A phased implementation plan with effort estimates and team sizing
- Performance targets with measurement methodology

This is the level of detail needed for build-vs-buy analysis, vendor evaluation scorecards, and quarterly roadmaps.

**Risk reduction through deliberate design.** The single biggest cause of AI project failure is unclear scope — teams build a model but don't plan for integration, compliance, or workflow change. Every project in this directory explicitly scopes the integrations (which API, what protocol, how often), the compliance requirements (HIPAA, GDPR, state DOI, SOC2), the workflow changes (who reviews what, override paths, escalation rules), and the success metrics (with current baseline and target). A business leader can hand this to any engineering team and get back a predictable outcome.

**Cross-domain pattern reuse creates portfolio leverage.** The same multi-agent document extraction pipeline built for legal M&A due diligence costs the same to build once, but can be deployed across insurance claims, government FOIA processing, and healthcare prior authorization — three separate revenue or cost-reduction opportunities from one architectural investment. Seeing these adjacencies requires a portfolio view, which this directory provides.

**From prototype to production in 20 weeks.** Each project's implementation plan shows a realistic timeline with a small team (3–4 people). The phases are ordered to deliver value incrementally: scaffold (week 1), core pipeline (weeks 2–5), ML training (weeks 5–8), frontend (weeks 9–14), compliance and admin (weeks 15–16), integration and production (weeks 17–21). Every phase has a clear deliverable and dependency, enabling stage-gate funding and progress tracking.

---

## Projects

| Project | Description | Key Techniques | Design Decision Highlights |
|---|---|---|---|
| **[RAG System](./rag-system/design.md)** | Document Q&A via RAG pipeline with ETL ingestion, hybrid search, and evaluation | Embeddings, vector search, re-ranking, eval-driven development | pgvector over Qdrant; chunk strategy comparison |
| **[LLM Workflow API](./llm-workflow-api/design.md)** | Unified LLM gateway with provider abstraction, caching, fallback, and monitoring | Provider routing, semantic caching, rate limiting, structured output | LiteLLM over direct SDK; Redis cache with TTL strategies |
| **[AI Evaluation Suite](./ai-evaluation-suite/design.md)** | Automated evaluation framework with 10 metric types and LLM-as-judge | LLM-as-judge with calibration, pytest plugin, GitHub Action | Direct scoring over pairwise; calibration set approach |
| **[AI Guardrails](./ai-guardrails/design.md)** | Content safety and compliance guardrails for LLM inputs and outputs | PII detection (presidio), toxicity classification, topic routing, compliance workflows | Presidio regex + ML hybrid; audit log immutability |
| **[Semantic Search](./semantic-search/design.md)** | Enterprise search across SharePoint, Confluence, and file shares | Hybrid search (BM25 + dense), RRF fusion, relevance tuning | Hybrid always-on; learn-to-rank phase 2 |
| **[AI Analytics Assistant](./ai-analytics-assistant/design.md)** | Automated data analysis with statistical tests, LLM narrative, and Vega-Lite visualization | Statistical analysis, NLG, Vega-Lite, HTML/JSON/PDF output | Pydantic for chart spec; LiteLLM provider fallback |
| **[Prompt Deployment Pipeline](./prompt-deployment-pipeline/design.md)** | Git-based prompt registry with canary releases, A/B testing, and eval gating | Git prompt registry, canary routing, A/B testing, eval gating | YAML prompt files; gradual rollout per user segment |
| **[AI Drift Detection](./ai-drift-detection/design.md)** | Monitor embedding, metric, data, and concept drift across ML pipelines | Embedding distribution analysis, statistical tests, composite drift index | KS-test + PSI combined; synthetic traffic for known drift |
| **[Multi-Agent System](./multi-agent-system/design.md)** | Coordinate multiple AI agents with state machines, message bus, and fault tolerance | Agent lifecycle, message bus, state machine, circuit breaker, orchestration patterns | State machine over DAG; Redis streams for agent messaging |
| **[Industry Solutions](./industry-solutions/)** | 20 industry-specific AI solution blueprints with cross-domain patterns | See individual designs | Industry constraints drive architecture (CPU, HIPAA, DOIs) |
| └ **[ClaimPulse](./industry-solutions/insurance/claimpulse/design.md)** | AI claims processing: document AI → damage assessment → fraud detection → settlement | PaddleOCR, BERT NER, XGBoost, llama.cpp, HTMX | CPU-only; LayoutLMv3 rejected; HTMX over React |
| └ **[FactoryRL](./industry-solutions/manufacturing-industrial/factoryrl/design.md)** | Factory energy optimization via MPC + LightGBM dynamics model | MPC, LightGBM, scipy SLSQP, TimescaleDB | MPC over PPO; explicit safety constraints; global + local solver hybrid |

---

## How to Navigate

1. **Quick scan**: Open any `design.md` and read the Overview + Architecture sections (first 30 lines). This tells you the problem, the approach, and the system boundaries.
2. **Deep dive**: Read the Design Decisions section. This is where the trade-offs live — why one framework was chosen over another, what constraints drove the architecture, and what alternatives were considered.
3. **Implementation**: The Implementation Phases table at the end shows the delivery roadmap. Each phase has clear dependencies, so you can plan teams and funding.
4. **Cross-reference**: Projects that share techniques (e.g., RAG + Semantic Search, Guardrails + Evaluation Suite) are designed to be combined. The APIs and data models are compatible by convention — pgvector in one interfaces with pgvector in another.

---

## Design Decision Pattern

Every project in this directory follows a consistent approach to documenting decisions:

| Column | Content |
|---|---|
| **Dimension** | What was being decided (framework, DB, protocol, algorithm) |
| **Chosen** | What was selected and why |
| **Rejected** | What was not selected and why |
| **Rationale** | The reasoning, including constraints and trade-off weighting |

This pattern makes the design doc useful not just as documentation but as a teaching tool — each decision table trains the reader to think architecturally about trade-offs rather than memorizing solutions.

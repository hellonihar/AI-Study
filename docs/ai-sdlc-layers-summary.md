# AI Application SDLC — Layer Summary

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│            (Chat UI · API Gateway · Slack · Webhook)                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                      LLM ORCHESTRATION                               │
│   (Prompt Management · Chains · Agents · Tool Use · RAG Flows)      │
└────┬──────────────┬──────────────┬──────────────┬───────────────────┘
     │              │              │              │
     ▼              ▼              ▼              ▼
┌──────────┐ ┌────────────┐ ┌──────────┐ ┌────────────────┐
│RETRIEVAL │ │EMBEDDING & │ │GUARDRAILS│ │  EVALUATION    │
│Hybrid    │ │VECTOR STORE│ │PII · Tox │ │LLM-as-Judge ·  │
│Search ·  │ │Index ·     │ │Topic ·   │ │Metrics ·       │
│RRF ·     │ │HNSW ·     │ │Inject ·  │ │Regression      │
│Rerank    │ │ANN Query   │ │Output    │ │Detection       │
└────┬─────┘ └─────┬──────┘ └────┬─────┘ └───────┬────────┘
     │             │             │                │
     ▼             ▼             ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE                                │
│      (Ingestion · Cleaning · Labeling · Versioning · Feature Store)  │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE & DEPLOYMENT                        │
│          (Serving · Scaling · CI/CD · Containerization)              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer Reference

### 1. Data Pipeline

Foundation layer — all downstream layers depend on data quality.

| Aspect | Details |
|---|---|
| **Role** | Ingest, clean, transform, version, and store raw data from enterprise sources |
| **Consumes from** | Enterprise sources: SharePoint, Confluence, DBs, logs, S3 |
| **Feeds into** | → Embedding & Vector Store (↑) → Guardrails (↑) |
| **Key capabilities** | Document parsing, schema detection, deduplication, PII stripping, data versioning, incremental sync |
| **Batch vs stream** | Batch (nightly full sync) + incremental (poll/webhook every 5 min) |
| **Chunking** | Heading-aware, recursive, semantic — configurable per content type |
| **Quality gates** | Schema validation, null ratio checks, duplicate detection |
| **Tech** | (Spark, Airflow, dlt, pandas, PyMuPDF, BeautifulSoup, DVC, Great Expectations, python-docx, openpyxl, html2text, Atlassian Python API, MS Graph SDK, boto3) |

### 2. Embedding & Vector Store

Converts text chunks into vector representations and enables similarity search.

| Aspect | Details |
|---|---|
| **Role** | Encode chunks as dense vectors, index for ANN search, store metadata |
| **Consumes from** | ↑ Data Pipeline (chunks) |
| **Feeds into** | → Retrieval ↓ |
| **Models** | API-based (text-embedding-3-small/large), open-source (BGE, E5, Instructor) |
| **Dim reduction** | OpenAI supports native truncation (512–256 dims) for speed/cost |
| **Index types** | HNSW (Qdrant, Pinecone), IVFFlat (PGVector), DiskANN (Azure AI Search) |
| **Distance metrics** | Cosine (default), Dot Product, Euclidean |
| **Hybrid support** | Vector + full-text filter (BM25) in Qdrant |
| **Filtering** | Metadata filtering: source, date, author, tags — applied pre or post search |
| **Tech** | (text-embedding-3-small, text-embedding-3-large, BGE-large-en-v1.5, E5-mistral-7b, Qdrant, Pinecone, Milvus, PGVector, Azure AI Search, HNSWlib, FAISS) |

### 3. Retrieval

Fetches the most relevant context for a query from the vector store.

| Aspect | Details |
|---|---|
| **Role** | Embed query, hybrid search (vector + BM25), RRF fusion, rerank, assemble context |
| **Consumes from** | ↑ Embedding & Vector Store |
| **Feeds into** | → LLM Orchestration ↓ |
| **Hybrid search** | Vector search (ANN) + keyword search (BM25) fused via Reciprocal Rank Fusion |
| **RRF constant** | `k=60` — higher values give more weight to lower-ranked items |
| **Alpha tuning** | `α=0.7` (vector-biased) for technical docs, `α=0.3` (keyword-biased) for legal |
| **Reranking** | Cross-encoder re-scores top 20 candidates; adds ~150ms but improves NDCG by 5–10% |
| **Context assembly** | Concatenate top-K results up to token budget (default 3000 tokens) with source citations |
| **Query processing** | Normalization, synonym expansion, query type classification, filter extraction |
| **Suggestions** | Prefix-matched autocomplete from indexed terms (frequency-ranked) |
| **Tech** | (BM25, Qdrant full_text_filter, Tantivy, BGE-reranker-v2-m3, Cohere Rerank, Cross-Encoder, RRF, NDCG, MAP, MRR) |

### 4. LLM Orchestration

Core intelligence layer — routes prompts to LLMs, manages conversation state, and coordinates tool calls.

| Aspect | Details |
|---|---|
| **Role** | Route queries to LLMs, manage conversation history, execute chains and agent workflows, call tools |
| **Consumes from** | ↑ Retrieval (context), ↑ Data Pipeline (direct knowledge) |
| **Feeds into** | → Guardrails ↓, → User Interface ↑ |
| **Provider abstraction** | Unified interface over OpenAI, Anthropic, local (Ollama), Azure OpenAI |
| **Provider fallback** | Primary → fallback → local on API error or rate limit |
| **Caching** | Semantic cache (embedding-similarity based) for repeated queries; TTL configurable |
| **Conversation history** | PostgreSQL — auto-summarize after N turns to stay within context window |
| **Chains** | Pre-defined sequences: RAG (retrieve → generate), summarization, extraction |
| **Agents** | ReAct-style: think → act → observe → repeat; tool registry with auth |
| **Prompt management** | Version-controlled prompts in YAML/JSON with template variables |
| **Streaming** | SSE streaming for real-time UX; same provider abstraction |
| **Request tracking** | Request ID, timing waterfall, token count per step — all emitted as structured logs |
| **Tech** | (LangChain, LangGraph, CrewAI, AutoGen, LiteLLM, OpenAI SDK, Anthropic SDK, Ollama, Guardrails AI, Redis, PostgreSQL, SSE, FastAPI) |

### 5. Guardrails

Safety and compliance layer — enforces policies on both input and output.

| Aspect | Details |
|---|---|
| **Role** | Inspect and filter LLM inputs and outputs for PII, toxicity, restricted topics, injection attempts, and format compliance |
| **Consumes from** | ↑ LLM Orchestration (input text + output text) |
| **Feeds into** | → Evaluation ↓, → Audit Log |
| **Input guards** | PII scan (regex + NER), toxicity filter (classifier), topic checker (zero-shot), prompt injection detection |
| **Output guards** | PII scan (redact or block), toxicity filter, factual consistency (LLM-as-judge), citation validation, length bounds |
| **Actions** | `block` (reject request), `redact` (replace sensitive content), `flag` (warn but allow), `pass` |
| **PII detection** | 2-stage: regex patterns (CC, SSN, email, phone) + NER model (spaCy/GLiNER for PERSON, ORG, GPE) |
| **Redaction strategies** | `mask`, `mask_preserve_type` ([CREDIT_CARD]), `hash` (SHA-256), `block` |
| **Toxicity categories** | Hate speech, violence, harassment, self-harm, sexual content — each with configurable threshold |
| **Topic restriction** | Zero-shot classifier (BART-large-mnli) against allow/deny lists; configurable per pipeline |
| **Injection detection** | Heuristic regex patterns + purpose-built classifier (DeBERTa-v3) |
| **Pipeline composition** | Ordered list of guards configurable via YAML — different pipelines per use case |
| **Tech** | (Presidio Analyzer, spaCy en_core_web_trf, GLiNER, Detoxify, BART-large-mnli, protectai/deberta-v3-prompt-injection, Guardrails AI, Nemo Guardrails, Azure Content Safety) |

### 6. Evaluation

Quality assurance — measures LLM output quality and detects regressions.

| Aspect | Details |
|---|---|
| **Role** | Score LLM outputs across multiple quality dimensions, compare against baselines, gate deployments |
| **Consumes from** | ↑ Guardrails (output text), ↑ Data Pipeline (eval datasets) |
| **Feeds into** | → Monitoring & Observability ↓, → CI/CD gating |
| **Metrics** | Faithfulness, hallucination rate, answer relevance, precision/recall/F1, ROUGE-L, completeness, toxicity, consistency |
| **LLM-as-judge** | Stronger model (GPT-4o) evaluates weaker model (GPT-4o-mini); temperature=0 for determinism |
| **Judge calibration** | Measure bias/variance against a hand-labeled gold set (50–200 cases); apply calibration factor to raw scores |
| **Bias mitigation** | Position bias (randomize order), verbosity bias (instruct to ignore length), self-enhancement bias (different judge model) |
| **Eval datasets** | Gold set (human-labeled), synthetic (LLM-generated from docs), production (sampled live traffic), adversarial (edge cases) |
| **CI/CD integration** | pytest plugin (`@pytest.mark.eval`), GitHub Action runs on PRs to prompts/ or generation/ ; gating thresholds in YAML |
| **Regression detection** | Compare metrics against baseline (latest main branch run); fail if any metric drops >5% |
| **Reporting** | JSON (machine), HTML dashboard with trend charts, regression diff callouts |
| **Tech** | (RAGAS, DeepEval, LangSmith, Arize Phoenix, MLflow, rouge-score, bert-score, Detoxify, GPT-4o-as-judge, pytest, GitHub Actions) |

### 7. Monitoring & Observability

Production visibility — tracks performance, cost, quality, and drift over time.

| Aspect | Details |
|---|---|
| **Role** | Collect and visualize metrics across all layers: latency, token usage, cost, error rates, guardrail hit counts, retrieval quality, generation quality |
| **Consumes from** | ↑ Evaluation, ↑ LLM Orchestration, ↑ Guardrails, ↑ Infrastructure |
| **Feeds into** | → Alerting (PagerDuty, Slack), → Dashboard (Grafana) |
| **Key metrics** | Request volume, latency p50/p95/p99, token count (prompt + completion), cost per request, error rate by provider, guardrail block rate by type, retrieval precision@K, faithfulness score, hallucination rate |
| **Drift detection** | Compare embedding distributions over time (Kolmogorov–Smirnov / Wasserstein distance), track accuracy on eval set, alert on degradation |
| **Cost tracking** | Per-model, per-user, per-pipeline cost attribution; daily/weekly budgets with alerts |
| **Tracing** | Distributed tracing across pipeline steps: ingestion → retrieval → guardrail → LLM → guardrail → response |
| **Logging** | Structured JSON logs (request_id, user_id, model, latency, tokens, guardrail decisions) shipped to ELK or Loki |
| **Tech** | (Prometheus, Grafana, OpenTelemetry, LangSmith, LangFuse, Weights & Biases, MLflow, ELK Stack, Loki, Tempo, Datadog, New Relic, PagerDuty, Slack Webhooks) |

### 8. Infrastructure & Deployment

Foundation — everything runs on this.

| Aspect | Details |
|---|---|
| **Role** | Containerize, deploy, scale, and serve all layers; provide CI/CD for model and prompt updates |
| **Consumes from** | ↑ All layers (needs to serve them) |
| **Provides** | → All layers ↑ (serving environment) |
| **Serving** | FastAPI (async Python), uvicorn + gunicorn for multi-worker, auto-scaling via K8s HPA |
| **Containerization** | Docker per service (API, ingestion worker, vector DB, Redis), docker-compose for dev |
| **Orchestration** | Kubernetes (EKS, AKS, GKE) for production; namespace per environment (dev, staging, prod) |
| **CI/CD** | GitHub Actions: lint → test → build → deploy; eval gate between build and deploy |
| **Prompt deployment** | Git-based prompt versioning; PR → eval suite → canary → full rollout → rollback on regression |
| **Model deployment** | Azure OpenAI (managed), Ollama (self-hosted local models), vLLM (open-source serving) |
| **Scaling** | Horizontal pod autoscaling on CPU/memory + custom metrics (queue depth, request latency) |
| **Secrets** | Azure Key Vault / AWS Secrets Manager / HashiCorp Vault — all secrets injected at deploy time |
| **Network** | Service mesh (Istio/Linkerd) for mTLS, traffic splitting for canary deployments |
| **Tech** | (Docker, docker-compose, Kubernetes, Helm, FastAPI, uvicorn, gunicorn, GitHub Actions, ArgoCD, Terraform, Pulumi, Azure DevOps, AWS ECS, Istio, Linkerd, nginx, Traefik, Azure Key Vault, AWS Secrets Manager, HashiCorp Vault, vLLM, Ollama, TGI) |

### 9. User Interface

The entry point — how users interact with the system.

| Aspect | Details |
|---|---|
| **Role** | Provide chat interface, API endpoints, and integration points for end users |
| **Consumes from** | ↑ LLM Orchestration (via API) |
| **Provides** | ← User input (text, files, voice) → LLM Orchestration |
| **Chat UI** | Web-based (Next.js/React) or native; supports streaming responses, markdown rendering, file upload |
| **API Gateway** | FastAPI routes with rate limiting, auth (JWT/API key), request validation, CORS |
| **Integrations** | Slack bot, Teams bot, custom webhook, Zapier/Make connector |
| **Auth** | OAuth 2.0 / SSO (Azure AD, Okta); API key-based for machine-to-machine |
| **Rate limiting** | Per-user, per-IP, per-API-key sliding window; tiered limits (free, pro, enterprise) |
| **Feedback loop** | Thumbs up/down, flag incorrect answers, submit corrections — all logged to eval dataset |
| **Tech** | (Next.js, React, Vue.js, Streamlit, Gradio, FastAPI, Swagger/OpenAPI, Slack Bolt, Teams Toolkit, Azure AD, Okta, Auth0, JWT, OAuth 2.0, Redis) |

---

## Cross-Cutting Concerns

| Concern | Scope | Approach | Tech |
|---|---|---|---|
| **Auth & RBAC** | UI → API → Orchestration | JWT with OAuth 2.0; role-based access per pipeline | (Azure AD, Okta, Auth0, Casbin, OPA) |
| **Audit** | Guardrails → Monitoring | Every guardrail decision logged; immutable audit store | (PostgreSQL, S3, ELK, Loki) |
| **Cost control** | Orchestration → Monitoring | Per-user quotas, per-model budgets, provider tiering | (Redis rate limiter, Prometheus cost metrics) |
| **Privacy** | Data → Guardrails | PII redaction at ingestion and runtime; retention policies | (Presidio, spaCy, data retention cron) |
| **Versioning** | Prompts, Models, Data | Git-based prompt versioning; model registry; DVC for data | (Git, DVC, MLflow Model Registry) |
| **Disaster recovery** | Infrastructure | Multi-region deployment; DB replication; backup restore | (K8s multi-cluster, Velero, PG replication) |

---

## Technology Stack Summary

| Layer | Primary Choice | Alternatives |
|---|---|---|
| Data Pipeline | pandas, PyMuPDF, DVC | Spark, Airflow, dlt |
| Embedding & Vector Store | text-embedding-3-small, Qdrant | BGE, E5, Pinecone, Milvus, PGVector |
| Retrieval | Qdrant hybrid + BGE-reranker | Cohere Rerank, Tantivy, Azure AI Search |
| LLM Orchestration | LiteLLM + FastAPI | LangChain, LangGraph, CrewAI |
| Guardrails | Presidio + Detoxify + custom pipeline | Guardrails AI, Nemo Guardrails, Azure Content Safety |
| Evaluation | RAGAS + DeepEval + LLM-as-judge | Arize Phoenix, MLflow, LangSmith |
| Monitoring | Prometheus + Grafana + OpenTelemetry | Datadog, New Relic, LangFuse, LangSmith |
| Infrastructure | Docker + K8s + GitHub Actions | Terraform, ArgoCD, Azure DevOps, AWS ECS |
| User Interface | Next.js + FastAPI | Streamlit, Gradio, Slack Bolt, React |

---

*This document is a cross-cutting reference spanning all sections of the AI Study repository. Individual topic READMEs under each section contain detailed explanations of specific concepts, architectures, and implementations.*

---

## Quick Read

An AI application SDLC is fundamentally a data-to-response pipeline. Data flows up from ingestion through embedding and retrieval, is augmented by guardrails and evaluation, and is finally served to users via orchestration and UI layers — all running on an infrastructure foundation. The two critical design principles are: (1) each layer has clear, testable contracts with its neighbors (e.g., retrieval produces a ranked list of chunks, orchestration consumes that list and an LLM, guardrails consume raw text and produce a pass/block decision), and (2) quality is enforced at every boundary, not just at the end.

The three most impactful decisions in this stack are the choice of embedding model (determines retrieval ceiling), the guardrail pipeline (determines safety and compliance posture), and the evaluation framework (determines whether you can detect regressions before users do). Everything else — orchestration framework, vector DB, deployment strategy — is fungible and should be chosen for developer productivity and operational familiarity first, raw performance second.

This document maps directly to the project designs in this repository: the LLM Workflow API (layer 4), RAG System (layers 1–4), AI Evaluation Suite (layer 6), AI Guardrails (layer 5), Semantic Search (layers 1–3), and AI Analytics Assistant (layers 1–4 + 9). Each design document implements a subset of this stack, and combined they form a complete reference architecture for production AI systems.

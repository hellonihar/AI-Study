# Projects to Showcase

Portfolio-ready projects bridging enterprise experience to AI system development.

---

## Backend → LLM Workflow API

Build a FastAPI service that routes user queries to multiple LLM providers. Add caching, latency monitoring, and conversation history storage.

📄 [View design document](../projects/llm-workflow-api/design.md)

**Skills demonstrated:** API design, provider abstraction, async Python, LLM integration

---

## Data Pipelines → RAG System

Extend an ETL pipeline with embeddings and a vector database (Pinecone, Qdrant, Milvus). Enable document Q&A with retrieval-augmented generation.

📄 [View design document](../projects/rag-system/design.md)

**Skills demonstrated:** ETL architecture, embeddings, vector search, RAG pipeline design

---

## QA/Testing → AI Evaluation Suite

Create automated evals for LLM outputs — precision, recall, hallucination detection, faithfulness scoring. Integrate with pytest or CI/CD pipelines.

📄 [View design document](../projects/ai-evaluation-suite/design.md)

**Skills demonstrated:** Test automation, LLM-as-judge, metric design, CI/CD integration

---

## DevOps → AI Observability Dashboard

Deploy LLM workflows with Docker + Kubernetes. Add Prometheus/Grafana dashboards for latency p50/p99, token usage, error rates, and guardrail hit counts.

**Skills demonstrated:** Containerization, orchestration, LLM-specific monitoring, SRE practices

---

## Governance → AI Guardrails

Implement policy enforcement: PII redaction, toxicity filters, topic restrictions, and output validation. Showcase compliance workflows (GDPR, HIPAA, SOC 2) with AI outputs.

📄 [View design document](../projects/ai-guardrails/design.md)

**Skills demonstrated:** Content safety, compliance engineering, guard model integration, audit trails

---

## Architecture → Multi-Agent System

Design coordinated agents for retrieval, reasoning, and tool orchestration. Demonstrate agent collaboration via LangGraph, CrewAI, or AutoGen with clear separation of concerns.

**Skills demonstrated:** Distributed system design, agent state management, multi-agent coordination

---

## Enterprise Search → Semantic Search

Replace keyword-based search with embedding-based semantic search. Integrate with an enterprise knowledge base (SharePoint, Confluence, or custom document store).

📄 [View design document](../projects/semantic-search/design.md)

**Skills demonstrated:** Search architecture, embedding models, hybrid search (vector + keyword), relevance tuning

---

## Monitoring → AI Drift Detection

Build a pipeline to detect model drift in production. Compare embedding distributions over time, track accuracy against a held-out eval set, and alert on degradation.

**Skills demonstrated:** ML monitoring, statistical drift detection, embedding distribution analysis, alerting

---

## Stakeholder Reporting → AI Analytics Assistant

Create an LLM-powered reporting tool that generates executive summaries. Input: raw logs or metrics. Output: narrative insights with visualizations and recommendations.

📄 [View design document](../projects/ai-analytics-assistant/design.md)

**Skills demonstrated:** LLM application development, data summarization, executive communication, reporting automation

---

## Legacy Modernization → AI-Enhanced Workflow

Take an existing enterprise workflow (ticketing, HR, CRM, or procurement). Add an LLM layer for summarization, classification, entity extraction, or smart recommendations without replacing the core system.

**Skills demonstrated:** Legacy integration, workflow augmentation, AI feature scoping, incremental modernization

---

## CI/CD → Prompt Deployment Pipeline

Build a Git-based pipeline that version-controls prompts, runs eval suites on new prompt versions, gates deploys on quality thresholds, and supports canary releases with automatic rollback.

📄 [View design document](../projects/prompt-deployment-pipeline/design.md)

**Skills demonstrated:** Prompt engineering, MLOps, CI/CD for LLMs, A/B testing for prompts

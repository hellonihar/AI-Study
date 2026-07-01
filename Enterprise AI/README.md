# Enterprise AI Study Repository

A comprehensive, hands-on curriculum for mastering Enterprise AI — from LLM fundamentals to production-grade architecture, governance, and operations.

## Intent

This repository bridges the gap between AI theory and enterprise deployment. Each module progresses from foundational concepts through production patterns, with runnable code, best practices, and curated resources. The material is written from the perspective of a senior AI architect, emphasizing performance, reliability, cost-efficiency, security, and long-term maintainability.

All code examples use local models (`sentence-transformers`) to avoid API key dependencies. External provider costs are modeled for comparison but no API calls are required.

## Modules

| # | Module | Focus |
|---|--------|-------|
| 01 | **LLM Fundamentals** | Transformer architecture, inference, context windows, tokenization, quantization, prompting, embeddings, fine-tuning basics, alignment, evals |
| 02 | **Prompt Engineering** | Prompt structure, few-shot, chain-of-thought, persona, formatting, iterative refinement, prompt chaining, adversarial robustness, production prompting, evaluation |
| 03 | **Embeddings & Semantic Search** | Embedding models, similarity search, clustering, semantic caching, hybrid search, multi-modal embeddings, production embedding pipelines |
| 04 | **Vector Databases** | Indexing algorithms (HNSW, IVF), vector databases (Pinecone, Weaviate, pgvector, Qdrant, Chroma), hybrid search, filtering, scaling, production operations |
| 05 | **RAG Systems** | Chunking strategies, retrieval (ANN, hybrid, multi-stage), reranking, context assembly, query rewriting, evaluation, production RAG architecture |
| 06 | **Enterprise Data Architecture** | Data pipelines, ETL/ELT, data lakes vs warehouses, feature stores, data quality, data contracts, lineage, GDPR/CCPA compliance, production data architecture |
| 07 | **AI Integration Patterns** | API design, model gateways, circuit breakers, fallback chains, caching (semantic, response), streaming, event-driven AI, batch processing, integration testing |
| 08 | **Agentic AI** | Agent loop, tool use, function calling, memory, planning, observability, guardrails, multi-step reasoning, production agents |
| 09 | **Multi-Agent Systems** | Agent communication, supervisor/peer/hierarchical topologies, shared memory, conflict resolution, orchestration, debugging, testing, production deployment |
| 10 | **MCP (Model Context Protocol)** | Protocol spec, server/client design, tools, resources, prompts, transport (stdio/SSE), security, ecosystem, production MCP |
| 11 | **Fine-Tuning & Customization** | PEFT (LoRA, QLoRA, Adapters), full fine-tuning, dataset preparation, RLHF/DPO, evaluation, deployment, continual learning, cost analysis |
| 12 | **AI Security** | Prompt injection, jailbreaking, data poisoning, supply chain security, model theft, PII detection, guardrails, red-teaming, secure deployment, incident response |
| 13 | **LLMOps & MLOps** | Monitoring, evaluation, CI/CD for prompts and models, A/B testing, drift detection, cost tracking, model versioning, incident response, production architecture |
| 14 | **AI Governance** | Regulatory landscape (EU AI Act, ISO 42001), risk classification, transparency, data governance, bias auditing, audit trails, ethics frameworks, organizational structures, production governance |
| 15 | **Enterprise AI Architecture** | Capstone — 5 sub-areas covering reference architecture, strategy, governance, operations, and solution patterns (RAG, multi-agent, AI assistant platforms) |

## Structure

Each standard module (01–14) contains:

```
NN - Module Name/
  README.md
  01-theory/           ~10 theory files (fundamentals → production)
  02-code/             ~10 runnable Python scripts
  03-best-practices/   ~5 best practice guides
  04-resources/        Links, tools, references
```

Module 15 (capstone) follows a custom structure with 5 sub-areas, each having its own theory, code, best practices, and resources.

## Getting Started

Start with the [roadmap](roadmap-to-master-enterprise-ai.md) for a guided 15-step learning path. Each module is self-contained; theory files cover the concepts and code files provide runnable examples.

```bash
# Run any code file (no external dependencies needed)
py "Enterprise AI/01 - LLM Fundamentals/02-code/01-transformer-basics.py"
```

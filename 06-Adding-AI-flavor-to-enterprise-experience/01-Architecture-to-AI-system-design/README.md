# Architecture → AI System Design

## The Traditional Skill

As a system architect, you designed distributed systems: load balancers, microservices, databases, caches, message queues, and API gateways. You made trade-offs between consistency, availability, and partition tolerance. You drew boxes-and-arrows diagrams showing request flows, data stores, and service boundaries.

## The AI Equivalent

Gen AI system design uses the same architectural thinking but with new building blocks. Instead of a database, you have a vector store. Instead of a microservice, you have an agent. Instead of a cache, you have prompt caching. The boxes-and-arrows diagrams now include RAG pipelines, embedding models, guardrails, and LLM endpoints — but the design process is identical: define requirements, decompose into components, evaluate trade-offs, and document the architecture.

## New Concepts to Learn

- **RAG architecture:** Retrieval pipeline (embed → store → search → retrieve → generate) as a core pattern replacing traditional read-from-database
- **Agent architecture:** State machines and graphs replacing request-response cycles. LangGraph nodes replace microservice endpoints
- **Prompt as code:** The prompt is a deployable artifact with versioning, testing, and rollback — treat it like infrastructure
- **Latency budgets:** LLM calls take 1–10s instead of 10–100ms. Architectures must account for this with streaming, speculative decoding, and caching
- **Non-determinism:** A service that returns different results for the same input changes how you think about retries, idempotency, and testing
- **Cost per token:** Unlike traditional infra (cost per request), AI cost scales with input + output tokens — architecting for token efficiency

## A Concrete Translation Example

**Traditional pattern:** API Gateway → Load Balancer → Microservice → Database

**AI pattern:** API Gateway → Guardrails → Orchestrator (LangGraph) → [Router → RAG (Embedding → Vector Store → Retriever) → LLM Call → Output Guardrails] → Response

The architectural thinking is the same — you're composing components, defining interfaces, and managing data flow. The components are just different.

## Key Resources

- "Building LLM Applications for Production" (Huyen, 2024)
- LangGraph documentation — understanding graphs as architecture
- Anthropic's "Building effective agents" guide

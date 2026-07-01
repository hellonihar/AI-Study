# AI Integration Patterns

Patterns for integrating LLMs into existing enterprise systems reliably and cost-effectively — covering decision frameworks, tool calling, resilience, vendor abstraction, and production architecture.

## Module Structure

```
07 - AI Integration Patterns/
├── 01-theory/          # 10 files: decision framework, tool calling, fallback chains, circuit breakers, streaming, event-driven AI, vendor abstraction, caching, rate limiting, integration architecture
├── 02-code/            # 10 scripts: decision framework through end-to-end architecture demo
├── 03-best-practices/  # 5 files: decision guide, tool design, resilience, streaming/async, vendor strategy
├── 04-resources/       # Papers, frameworks, tutorials, books
└── README.md           # This file
```

## Theory (01-theory/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-decision-framework.md` | RAG vs fine-tuning vs prompting — trade-offs, cost, decision flow |
| 2 | `02-tool-calling-agents.md` | Tool definitions, parameter binding, execution, error recovery |
| 3 | `03-fallback-chains.md` | Tiered model routing (cheap → expensive), graceful degradation |
| 4 | `04-circuit-breakers.md` | Circuit breaker state machine, failure detection, auto-recovery |
| 5 | `05-streaming-patterns.md` | SSE, WebSocket, chunked transfer, streaming + tool calling |
| 6 | `06-event-driven-ai.md` | Queues, webhooks, polling, async AI processing patterns |
| 7 | `07-vendor-abstraction.md` | Adapter pattern, multi-provider routing, migration playbook |
| 8 | `08-caching-patterns.md` | Response cache, semantic cache, multi-layer cache, invalidation |
| 9 | `09-rate-limiting-and-backpressure.md` | Token bucket, sliding window, load shedding, prioritization |
| 10 | `10-integration-architecture.md` | End-to-end architecture combining all patterns |

## Code Examples (02-code/)

| # | File | Description | Requirements |
|---|------|-------------|--------------|
| 1 | `01-decision-framework.py` | Interactive decision tree for RAG/FT/Prompt | none (stdlib) |
| 2 | `02-tool-calling.py` | Tool definitions, parameter binding, execution with error recovery | none (stdlib) |
| 3 | `03-fallback-chain.py` | Multi-tier model routing with cascading fallback | none (stdlib) |
| 4 | `04-circuit-breaker.py` | Circuit breaker state machine (closed/open/half-open) | none (stdlib) |
| 5 | `05-streaming-demo.py` | SSE-like token streaming, client cancellation, metrics | none (stdlib) |
| 6 | `06-event-driven-ai.py` | Queue-based async processing with workers and DLQ | none (stdlib) |
| 7 | `07-vendor-abstraction.py` | Abstract AIModel interface + OpenAI/Anthropic/Local adapters | none (stdlib) |
| 8 | `08-caching-patterns.py` | Exact response cache + semantic embedding cache | `sentence-transformers` |
| 9 | `09-rate-limiting.py` | Token bucket + sliding window rate limiters | none (stdlib) |
| 10 | `10-integration-architecture.py` | End-to-end pipeline: rate limiter → cache → circuit breaker → fallback → router | `sentence-transformers` |

## Best Practices (03-best-practices/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-decision-guide.md` | Decision matrix, cost estimation, migration strategy, anti-patterns |
| 2 | `02-tool-design.md` | Naming, parameter schemas, error messages, idempotency, response structure |
| 3 | `03-resilience-patterns.md` | Retry, circuit breaker, fallback, timeout, bulkhead, health checks |
| 4 | `04-streaming-and-async.md` | Streaming vs sync vs async decision guide, backpressure, pitfalls |
| 5 | `05-vendor-strategy.md` | Multi-provider strategy, evaluation criteria, migration, lock-in mitigation |

## Key Topics

- **Decision Framework**: When to use RAG, fine-tuning, or prompt engineering (cost/quality/latency trade-offs)
- **Tool Calling**: Function definitions, parameter binding, execution, error recovery
- **Fallback Chains**: Tiered model routing, graceful degradation, content-based routing
- **Circuit Breakers**: State machine (CLOSED/OPEN/HALF-OPEN), failure detection, auto-recovery
- **Streaming**: SSE, WebSocket, client cancellation, backpressure
- **Event-Driven AI**: Queues, webhooks, workers, DLQ pattern
- **Vendor Abstraction**: Adapter pattern, multi-provider routing, migration playbook
- **Caching**: Response cache, semantic cache, multi-layer, invalidation strategies
- **Rate Limiting**: Token bucket, sliding window, load shedding, prioritization

## Quick Start

```bash
# Decision framework (interactive)
python "02-code/01-decision-framework.py"

# Circuit breaker demo
python "02-code/04-circuit-breaker.py"

# Fallback chain
python "02-code/03-fallback-chain.py"

# Semantic cache (requires sentence-transformers)
pip install sentence-transformers numpy
python "02-code/08-caching-patterns.py"
```

## Prerequisites

- **Python 3.10+**
- **Core**: none (stdlib only for most scripts)
- **Caching**: `sentence-transformers`, `numpy` (for semantic cache)
- **Production**: `fastapi`, `redis`, `aiohttp`, `celery`, `prometheus-client`

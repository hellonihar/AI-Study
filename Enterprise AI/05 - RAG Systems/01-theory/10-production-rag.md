# Production RAG Architecture

Patterns for reliable, low-latency, cost-effective RAG in production.

## Production Architecture

```
                  ┌─────────────┐
                  │   User       │
                  └──────┬──────┘
                         │
                    ┌────▼────┐
                    │  API GW  │
                    └────┬────┘
                         │
              ┌──────────┴──────────┐
              │                     │
         ┌────▼────┐          ┌────▼────┐
         │  Cache   │          │  Router  │
         │ (Redis)  │          │ (RAG    │
         └────┬────┘          │  Orchr) │
              │               └────┬────┘
              │                    │
              │          ┌─────────┴─────────┐
              │          │                   │
              │    ┌─────▼─────┐     ┌──────▼──────┐
              │    │ Quick      │     │  Full RAG    │
              │    │ (cache hit)│     │  Pipeline    │
              │    └───────────┘     └──────┬───────┘
              │                            │
              │             ┌──────────────┼──────────────┐
              │             │              │              │
              │        ┌────▼────┐   ┌─────▼─────┐  ┌────▼────┐
              │        │ Query    │   │ Retrieve   │  │ Generate │
              │        │ Rewrite  │   │ (vDB +     │  │ (LLM)    │
              │        └─────────┘   │  re-rank)  │  └────┬────┘
              │                      └───────────┘       │
              └──────────────────────────────────────────┘
                                                         │
                                                    ┌────▼────┐
                                                    │ Response │
                                                    └─────────┘
```

## Caching

### Cache Layers

| Cache | Key | Value | TTL | Hit Rate |
|---|---|---|---|---|
| Query result | `(query_hash, top_k)` | JSON response | 1 hour | 20-40% |
| Embedding | `(text_hash)` | float vector | 24 hours | 30-50% |
| LLM response | `(prompt_hash)` | text | 1 hour | 10-20% |
| Re-ranker score | `(query_hash, doc_id)` | score | 24 hours | 40-60% |

### Implementation

```python
# Cache-aside pattern
def get_response(query, rag_pipeline, cache):
    cache_key = f"rag:query:{hash(query)}"
    if cached := cache.get(cache_key):
        return cached

    response = rag_pipeline(query)
    cache.set(cache_key, response, ttl=3600)
    return response
```

## Fallback Chains

When a pipeline stage fails, fall through to the next:

```python
def robust_rag(query):
    strategies = [
        ("precision", lambda q: full_rag_with_re_rank(q)),
        ("standard",  lambda q: hybrid_search_rag(q)),
        ("basic",     lambda q: dense_search_rag(q)),
        ("llm_only",  lambda q: llm_generate(q)),       # last resort
    ]

    for name, strategy in strategies:
        try:
            result = strategy(query)
            if result["confidence"] > CONFIDENCE_THRESHOLD:
                return result
            log.info(f"Strategy '{name}' below confidence threshold")
        except Exception as e:
            log.warning(f"Strategy '{name}' failed: {e}")
            continue

    return fallback_response("Unable to process request at this time.")
```

## Guardrails

### Input Guardrails

```python
input_checks = [
    check_toxicity(query),
    check_pii_leakage(query),
    check_query_language(query),   # supported languages only
    check_max_length(query, 2000),
    check_rate_limit(user_id, 100, window=60),
]
```

### Output Guardrails

```python
output_checks = [
    check_hallucination(response, passages),
    check_citation_accuracy(response, passages),
    check_toxicity(response),
    check_pii_leakage(response),
    check_max_length(response, 4000),
    check_groundedness_score(response, passages, threshold=0.8),
]
```

### Guardrail Actions

| Severity | Action |
|---|---|
| Pass | Return response normally |
| Low risk | Add warning header, return response |
| Medium risk | Strip problematic content, regenerate |
| High risk | Block response, return fallback |
| Critical | Block + alert on-call + log for review |

## Observability

### Traces

Trace every RAG request end-to-end:

```json
{
  "trace_id": "abc123",
  "timestamp": "2024-12-01T10:00:00Z",
  "query": "What was Q3 revenue?",
  "stages": {
    "query_rewrite": {"latency_ms": 45, "rewritten": "Q3 revenue 2024"},
    "retrieval": {"latency_ms": 25, "top_k": 10, "recall@10": 0.95},
    "re_rank": {"latency_ms": 120, "candidates": 50, "top_k": 5},
    "generation": {"latency_ms": 350, "tokens": 180, "model": "gpt-4o"},
    "guardrails": {"latency_ms": 15, "passed": true}
  },
  "total_latency_ms": 555,
  "cache_hit": false,
  "user_id": "tenant_42"
}
```

### Metrics Dashboard

| Panel | Metric | Alert |
|---|---|---|
| RPS by tenant | requests/sec | > 200 |
| P50/P95/P99 latency | ms | P99 > 2s |
| Cache hit rate | % | < 10% |
| Fallback rate | % | > 5% |
| Guardrail blocks | count | > 10/min |
| Hallucination score | 0-1 | > 0.1 |

## Cost Optimization in Production

| Item | Cost per 1M queries | Optimization |
|---|---|---|
| Embedding (self-host) | $5 | Cache, batch, reduce dims |
| Vector search | $2 | Right-size index |
| Re-ranking (50 candidates) | $50 | Reduce to 30, skip for easy queries |
| LLM generation (500 tokens) | $500-2000 | Use smaller model, cache, batched |
| Guardrails | $10 | Run on smaller models |

**Rule:** LLM generation is 80-90% of RAG cost. Every optimization should start there.

## Scaling

```yaml
scaling:
  retrieval:
    max_qps_per_replica: 1000
    auto_scale: { min: 2, max: 20, cpu_threshold: 70% }
    
  generation:
    max_qps_per_replica: 50      # LLM is the bottleneck
    auto_scale: { min: 4, max: 50, queue_depth: 100 }
    queue: "redis"               # buffer during spikes
    
  cache:
    redis_cluster:
      shards: 3
      memory_per_shard: 32 GB
      eviction: "allkeys-lfu"
```

## Deployment Checklist

- [ ] Query result cache configured with TTL
- [ ] Embedding cache (reuse across queries in same session)
- [ ] Fallback chain defined (at least 3 levels)
- [ ] Input guardrails (toxicity, PII, length)
- [ ] Output guardrails (hallucination, citation, PII)
- [ ] Structured logging (trace_id per request)
- [ ] P99 latency monitoring with alerts
- [ ] Cost tracking per query / per tenant
- [ ] A/B testing framework for pipeline changes
- [ ] Load testing at 2× expected peak
- [ ] Canary deployments (10% → 50% → 100%)
- [ ] Rollback procedure documented

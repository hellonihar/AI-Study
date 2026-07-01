# Production Deployment for RAG

Running RAG reliably at scale: architecture, scaling, monitoring.

## Deployment Architecture

```
                  ┌──────────┐
                  │  Client   │
                  └─────┬────┘
                        │
                  ┌─────▼─────┐
                  │  API GW    │
                  └─────┬─────┘
                        │
            ┌───────────┴───────────┐
            │                       │
      ┌─────▼──────┐        ┌──────▼──────┐
      │  RAG Service │        │  Monitoring  │
      │  (FastAPI)   │        │  (Datadog)   │
      └─────┬───────┘        └─────────────┘
            │
    ┌───────┼───────────────┐
    │       │               │
┌───▼───┐ ┌▼────┐     ┌────▼────┐
│ Cache │ │ vDB │     │ LLM API │
│(Redis)│ │     │     │(OpenAI) │
└───────┘ └─────┘     └─────────┘
```

## Service Components

### RAG Service (Stateless)
- FastAPI / Python async
- Handles query rewriting, retrieval, re-ranking, generation orchestration
- Scales horizontally behind a load balancer
- Session affinity NOT needed (stateless)

### Cache Layer
- Redis cluster (3+ nodes)
- Caches: query results (TTL: 1h), embeddings (TTL: 24h), LLM responses (TTL: 1h)
- Eviction: allkeys-lfu (least frequently used)

### Vector Database
- Qdrant or Milvus for self-hosted
- Pinecone for managed
- For latency-critical: co-locate in same AZ as RAG service

## Scaling Rules

| Component | Bottleneck | Scale Strategy |
|---|---|---|
| RAG service | CPU (embedding + re-ranking) | Horizontal: add pods |
| Vector DB | Memory (index) + CPU (search) | Shard + replicate |
| Cache | Memory | Cluster + increase memory |
| LLM API | Rate limits + latency | Queue + retry + fallback |

## Autoscaling Configuration

```yaml
rag_service:
  min_replicas: 2
  max_replicas: 20
  metrics:
    - type: cpu
      target: 70%
    - type: custom
      name: rag_queue_depth
      target: 100

vector_db:
  scaling: manual (shard count determined by data size)
  replication: 2 (RF=2 minimum for HA)

cache:
  memory_limit: 32 GB
  eviction: allkeys-lfu
```

## Rate Limiting

```yaml
rate_limits:
  per_user:
    rps: 10
    burst: 20
  per_tenant:
    rps: 100
    burst: 200
  
  llm_api:
    max_retries: 3
    backoff: exponential
    circuit_breaker:
      failure_threshold: 10
      recovery_timeout: 30s
```

## Observability

### Logging

Every RAG request produces a structured log:

```json
{
  "trace_id": "abc123",
  "query": "What was Q3 revenue?",
  "latency_ms": {
    "total": 550,
    "cache_check": 2,
    "retrieval": 25,
    "re_rank": 120,
    "generation": 350,
    "guardrails": 15
  },
  "cache_hit": false,
  "retrieval_stats": {
    "top_k": 10,
    "avg_score": 0.45,
    "zero_results": false
  },
  "guardrails": {
    "input_passed": true,
    "output_passed": true
  }
}
```

### Metrics Dashboard

| Panel | Metric | Alert Threshold |
|---|---|---|
| Request rate | QPS by tenant | > 80% of capacity |
| Latency | P50 / P95 / P99 | P99 > 2s |
| Cache hit rate | % of queries cached | < 10% |
| Retrieval quality | Avg score, zero-result rate | Avg < 0.3 |
| Fallback rate | % of queries using fallback | > 2% |
| Guardrail blocks | Count / min | > 10/min |
| LLM cost | $ / hour | > budget threshold |

## Deployment Strategies

| Strategy | Risk | Time | Use Case |
|---|---|---|---|
| Rolling update | Low | 5-10 min | Routine deployments |
| Blue/green | Very low | 15-30 min | Critical changes (prompt, model) |
| Canary (10% → 50% → 100%) | Very low | 30-60 min | High-risk changes |
| Feature flag | None | Instant | Prompt variations, model selection |

## Rollback Plan

```yaml
rollback_criteria:
  - faithfulness < 0.85
  - latency_p99 > 5s for 2 consecutive minutes
  - error_rate > 5% for 1 minute
  - guardrail_block_rate > 10% for 1 minute

rollback_actions:
  1. Revert RAG service to previous image
  2. Revert prompt config to previous version
  3. Revert embedding model to previous version
  4. Notify #rag-alerts with before/after metrics

rollback_testing:
  frequency: monthly
  steps:
    - Deploy change
    - Measure metric degradation
    - Execute rollback
    - Verify metrics return to baseline
```

## Deployment Checklist

- [ ] Load test at 2× expected peak QPS
- [ ] Test each fallback strategy (cache miss → retrieve → re-rank → generate → guard)
- [ ] Configure rate limiting per user and per tenant
- [ ] Set up circuit breaker for LLM API
- [ ] Deploy canary with 10% traffic
- [ ] Monitor dashboard for 15 minutes
- [ ] Verify cache hit rate is within expected range
- [ ] Verify P99 latency is within SLA
- [ ] Check recall@10 on eval set is within 1% of baseline
- [ ] Document rollback procedure and test it

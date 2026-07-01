# Integration Architecture

## End-to-End Architecture

Combining all patterns into a production AI integration system:

```
                       ┌─────────────────┐
                       │   Load Balancer  │
                       └────────┬────────┘
                                │
                        ┌───────┴───────┐
                        │   API Gateway  │
                        │ (auth, routing)│
                        └───────┬───────┘
                                │
                   ┌────────────┼────────────┐
                   │            │            │
            ┌──────┴─────┐ ┌───┴────┐ ┌────┴──────┐
            │  Sync API  │ │Stream  │ │  Async    │
            │ (chat, QA) │ │(SSE)   │ │ (webhook) │
            └──────┬─────┘ └───┬────┘ └────┬──────┘
                   │            │            │
            ┌──────┴────────────┴────────────┴──────┐
            │         Orchestration Layer           │
            │   ┌──────────────────────────────┐   │
            │   │  Decision Engine              │   │
            │   │  → route by complexity       │   │
            │   │  → fallback chain            │   │
            │   │  → circuit breaker           │   │
            │   └──────────────────────────────┘   │
            └──────────────────┬───────────────────┘
                               │
            ┌──────────────────┴───────────────────┐
            │         Model Abstraction Layer       │
            │   ┌──────┐ ┌────────┐ ┌──────────┐  │
            │   │OpenAI│ │Anthropic│ │  Local   │  │
            │   │Adapter│ │Adapter │ │ Adapter  │  │
            │   └──────┘ └────────┘ └──────────┘  │
            └──────────────────┬───────────────────┘
                               │
            ┌──────────────────┴───────────────────┐
            │       Infrastructure Layer            │
            │  ┌──────┐ ┌──────┐ ┌──────┐        │
            │  │Cache │ │Queue │ │Rate  │        │
            │  │(Redis)│ │(SQS) │ │Limiter│       │
            │  └──────┘ └──────┘ └──────┘        │
            └─────────────────────────────────────────┘
```

## Request Flow

```
1. Client sends request → API Gateway
2. Gateway authenticates, rate-limits, routes
3. Orchestration Layer:
   a. Runs query classifier (simple/complex)
   b. Checks cache (semantic cache hit?)
   c. Applies circuit breaker state
   d. Selects model tier via fallback chain
4. Model Abstraction Layer:
   a. Routes to correct provider adapter
   b. Tracks usage and cost
5. Infrastructure Layer:
   a. Applies rate limiting (per-user, per-model)
   b. Caches responses (if cacheable)
   c. Queues async requests
6. Response flows back through the pipeline
```

## Decision Flow

```python
def process_request(request):
    # 1. Rate limit
    if not rate_limiter.allow(request.user):
        return HTTPException(429)

    # 2. Check cache
    cached = cache.get(request.prompt, request.model)
    if cached:
        return cached

    # 3. Check circuit breaker
    if circuit.is_open(request.model):
        raise CircuitOpenError

    # 4. Execute with fallback
    for tier in fallback_chain.get_tiers(request):
        try:
            response = model_abstraction.generate(tier, request)
            cache.set(request.prompt, response)
            circuit.record_success()
            return response
        except Exception:
            circuit.record_failure()
            continue

    return fallback_response("I'm sorry, I'm unavailable right now.")
```

## Deployment Considerations

| Component | Scaling Strategy | HA Strategy |
|-----------|-----------------|-------------|
| API Gateway | Horizontal (stateless) | Active-active |
| Orchestration | Horizontal (stateless) | Active-active |
| Cache (Redis) | Cluster mode | Active-passive |
| Queue (SQS) | Auto-managed | AWS-managed HA |
| Workers | Horizontal (queue-based) | Auto-recovery |
| Rate Limiter | Local (per-instance) + Redis (global) | Active-passive |

## Cost Optimization

- **Cache first**: 60% reduction in API calls
- **Model tiering**: 80% of traffic handled by cheap models
- **Batching**: Batch non-urgent requests (3–5x throughput at same cost)
- **Streaming**: No cost benefit, but improves perceived latency
- **Pre-warming**: Keep models loaded (avoids cold starts for local models)

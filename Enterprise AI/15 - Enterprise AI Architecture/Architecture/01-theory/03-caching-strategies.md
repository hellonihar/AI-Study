# Caching Strategies for Enterprise AI

## Why Cache

LLM inference is expensive and slow. Caching reduces cost, latency, and load on inference infrastructure.

## Cache Types

### Exact Match Cache

Cache the exact response for identical requests:
- **Key**: Hash of full input (prompt + config)
- **Hit rate**: 5-15%
- **Latency savings**: 100% (instant response)
- **Best for**: Common questions, repeated queries, system prompts

```python
cache_key = hash(prompt + str(temperature) + str(max_tokens))
if cache_key in cache:
    return cache[cache_key]
```

### Semantic Cache

Return cached responses for semantically similar queries:
- **Key**: Embedding of the query
- **Lookup**: Nearest neighbor search in embedding space
- **Threshold**: Cosine similarity > 0.92
- **Hit rate**: 15-35%
- **Best for**: Customer support, FAQ, documentation queries

### Prefix Cache

Cache the KV cache state for common prompt prefixes:
- **Key**: Prefix tokens
- **TTFT savings**: 30-50%
- **Best for**: System prompts, few-shot examples, conversation prefixes
- **Supported by**: vLLM (automatic prefix caching)

### Response Cache

Cache model responses for identical inputs:
- **TTL**: Configurable per content type
- **Invalidation**: On model/prompt update
- **Best for**: Static content, deterministic transformations

## Cache Architecture

```
Request → Hash Key → Cache Lookup ──hit──→ Return Cached Response
                            │
                          miss
                            │
                    ┌───────▼───────┐
                    │  Model Query  │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │  Store Result │
                    │  + Update TTL │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │   Response    │
                    └───────────────┘
```

## Cache Storage

| Storage | Latency | Capacity | Cost | Best For |
|---------|---------|----------|------|----------|
| Redis | < 1ms | Memory-bound | Medium | Exact + prefix cache |
| Memcached | < 1ms | Memory-bound | Low | Simple key-value |
| Momento | < 5ms | Unlimited | Pay-per-use | Serverless, scalable |
| Local memory | < 0.1ms | Per-pod | Free | Pod-local cache |

## Invalidation Strategies

| Strategy | Trigger | Complexity |
|----------|---------|------------|
| TTL-based | Time expiration | Low |
| Version-based | Model/prompt version change | Medium |
| Event-based | Data change notification | High |
| Manual | Admin action | Low |

## Monitoring Cache Effectiveness

| Metric | Target | Calculation |
|--------|--------|-------------|
| Hit rate | > 20% | hits / (hits + misses) |
| Savings | > 15% cost | (miss_cost - hit_cost) / miss_cost |
| Latency reduction | > 50% p50 | cached_latency / uncached_latency |
| Staleness rate | < 1% | stale_hits / total_hits |

## Cache Budget

| Component | Cache Size | Estimated Savings | Monthly Cost |
|-----------|------------|------------------|-------------|
| Exact match | 10 GB | $500 | $50 |
| Semantic | 5 GB | $1,500 | $100 |
| Prefix | 20 GB | $800 | $80 |
| Total | 35 GB | $2,800 | $230 |

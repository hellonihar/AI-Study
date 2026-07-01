# Caching Patterns

## Motivation

LLM calls are expensive ($0.01–$0.10 per query) and slow (500ms–30s). Caching eliminates redundant calls for identical or semantically similar queries, reducing both cost and latency.

## Response Caching (Exact Match)

Cache the LLM response for an exact (prompt, model, temperature) tuple.

```python
key = hash(f"{prompt}:{model}:{temperature}")
if key in cache:
    return cache[key]  # 1ms latency, $0 cost
response = call_llm(prompt)
cache.set(key, response, ttl=3600)
return response
```

**Hit rate**: 5–15% for production traffic (varies by use case)
**TTL**: 1 hour for general Q&A, longer for stable knowledge

## Semantic Caching

Cache based on semantic similarity rather than exact text match. Embed the query and check if a semantically similar query exists in the cache.

```python
query_embedding = embed(query)
for cached_query, response in cache:
    similarity = cosine_similarity(query_embedding, cached_query.embedding)
    if similarity > threshold:
        return response  # semantic hit
```

**Threshold tuning**:
- 0.95: Near-exact matches (safe, low false positives)
- 0.90: Paraphrase matches (good for FAQ)
- 0.85: Topic-level matches (risk of irrelevant responses)

**Warning**: Semantic caching can return stale or incorrect responses for similar-sounding but different-intent queries. Always test false positive rate.

## Cache Invalidation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| TTL-based | Expire after fixed time | General knowledge |
| Event-based | Invalidate on data change | RAG with updated docs |
| Version-based | Invalidate on model version change | Model updates |
| Manual | Admin API to clear cache | Emergency response |

## Multi-Layer Cache

```
Layer 1: In-memory cache (Redis) — 1ms, limited size
  Miss → Layer 2: Distributed cache (Redis Cluster) — 5ms, larger
    Miss → LLM API call — 500ms+, expensive
```

## Cache Key Design

Include all factors that affect the response:
- Model name and version
- Prompt (system + user messages)
- Temperature and other parameters
- Retrieved context (for RAG: include chunk hashes)
- User locale or language

## Cost-Benefit Analysis

| Metric | Without Cache | With Cache |
|--------|--------------|------------|
| p50 latency | 2.5s | 50ms |
| p99 latency | 15s | 200ms |
| Cost per query | $0.01 | $0.002 |
| Monthly cost (1M queries) | $10,000 | $2,000 |

## When NOT to Cache

- Real-time data queries (stock prices, weather)
- Personalized responses (each user gets different output)
- Creative generation (poetry, stories — uniqueness is the point)
- Sensitive data (cache must not store PII)

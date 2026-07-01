# Resilience Patterns

## Pattern Catalog

| Pattern | Scope | When to Use |
|---------|-------|-------------|
| Retry | Transient failures | 4xx/5xx, network issues, timeouts |
| Circuit Breaker | Persistent failures | Error rate > threshold |
| Fallback | Single point of failure | When primary fails, use alternative |
| Timeout | Slow responses | p99 > SLA threshold × 2 |
| Bulkhead | Resource isolation | One failing client impacting others |
| Cache-Aside | Repeated identical queries | Same query, stable response |

## Retry Strategy

```python
def retry_with_backoff(fn, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return fn()
        except RetryableError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random(0, 0.1)
            time.sleep(delay)
```

- Exponential backoff: 1s, 2s, 4s
- Jitter: ±10% to prevent thundering herd
- Max retries: 3 (beyond that, something is fundamentally wrong)

## Timeout Configuration

| Component | Timeout | Rationale |
|-----------|---------|-----------|
| LLM generation | p99 latency × 2 | Allow for normal variance |
| Embedding API | 5s | Typically fast (<1s) |
| Vector DB query | 3s | Should be <100ms |
| Tool execution | 10s | External API variability |

## Bulkhead Pattern

Separate connection pools for different workloads:

```python
bulkheads = {
    "chat": ThreadPoolExecutor(max_workers=10),
    "batch": ThreadPoolExecutor(max_workers=2),
    "admin": ThreadPoolExecutor(max_workers=1),
}
```

If chat experiences a spike, batch and admin remain unaffected.

## Health Check Design

```python
def health_check():
    for provider in ["openai", "anthropic", "local"]:
        try:
            result = call_provider(provider, "test", timeout=3)
            status[provider] = "healthy"
        except Exception:
            status[provider] = "unhealthy"
    return status
```

- Run health checks every 30s
- Mark provider unhealthy after 3 consecutive failures
- Auto-recover: after 60s, try a probe request

## Degradation Tiers

| Tier | User Experience | System State |
|------|----------------|--------------|
| Normal | Full quality | All systems nominal |
| Degraded | Faster model (haiku instead of opus) | Primary model unavailable |
| Limited | Cached responses only | API outage |
| Fallback | Static message | Complete AI outage |

## Chaos Engineering

Test resilience proactively:
- Kill a provider connection → verify fallback activates
- Saturate rate limiter → verify 429 responses are clean
- Inject high latency → verify timeout + circuit breaker
- Double traffic → verify autoscaling + queue depth

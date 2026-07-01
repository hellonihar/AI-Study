# Rate Limiting & Backpressure

## Motivation

LLM APIs enforce rate limits (RPM, TPM, concurrent requests). Exceeding them causes 429 errors or account suspension. Rate limiting protects both the upstream API and your own infrastructure from overload.

## Rate Limiting Algorithms

### Token Bucket
Tokens are added at a fixed rate (refill rate). Requests consume tokens. If no tokens remain, the request is queued or rejected.

```
Capacity: 100 tokens
Refill rate: 10 tokens/second
→ Request consumes 1 token (95 remaining)
→ Request consumes 1 token (94 remaining)
→ 2 seconds pass → 20 tokens added (114, capped at 100)
```

**Pros**: Handles bursts up to capacity. Simple and memory-efficient.
**Cons**: Cannot enforce rolling window limits.

### Sliding Window Log
Tracks timestamps of all requests in the current window. Rejects requests that exceed the limit.

```
Limit: 100 requests per 60 seconds
→ Request at 12:00:55 (window: 11:59:55–12:00:55, count: 98) → allowed
→ Request at 12:01:00 (window: 12:00:00–12:01:00, count: 102) → rejected
```

**Pros**: Precise, no bursts around window boundaries.
**Cons**: Memory grows with request volume. Slower for high-throughput.

### Sliding Window Counter
Hybrid of token bucket and sliding window. Approximates the sliding window with a counter that decays over time.

## Backpressure Strategies

### Queue (Synchronous Client)
When rate-limited, queue requests and send them at the allowed rate.

```python
async def rate_limited_call(prompt):
    async with rate_limiter:
        return await llm_client.generate(prompt)
```

### Prioritization
Route requests to different queues by priority:

- **Critical**: Customer-facing, must respond quickly (higher rate limit)
- **Normal**: Internal tools, background processing (standard rate)
- **Bulk**: Batch processing, ETL (lowest rate)

### Load Shedding
When request volume exceeds capacity:

1. Reject non-critical requests with 429 + retry-after header
2. Degrade quality: use cheaper/faster model for excess traffic
3. Fail open: return cached response or static fallback

## Provider-Specific Rate Limits

| Provider | Common Limit | Burst | Reset |
|----------|-------------|-------|-------|
| OpenAI (GPT-4) | 10k TPM, 500 RPM | 1.5x | Per minute |
| Anthropic (Claude) | 1k RPM, 100k TPM | 2x | Per minute |
| Google (Gemini) | 60 RPM (free), 1k+ (paid) | — | Per minute |
| Local (vLLM) | Hardware-dependent | N/A | N/A |

## Monitoring Rate Limits

- Track current RPM/TPM usage as percentage of limit
- Alert when approaching 80% of limit
- Cache rate limit headers from API responses
- Log rate limit errors with retry-after duration

## Multiple Limit Types

APIs enforce multiple limits simultaneously:

- **RPM**: Requests per minute (coarse)
- **TPM**: Tokens per minute (fine-grained)
- **CPM**: Characters per minute (for embedding APIs)
- **Concurrent**: Max simultaneous requests

Your rate limiter must enforce the most restrictive limit for each request.

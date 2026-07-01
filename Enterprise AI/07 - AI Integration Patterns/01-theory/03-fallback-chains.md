# Fallback Chains

## Motivation

LLMs fail. APIs go down. Costs spike. A fallback chain ensures your system degrades gracefully instead of failing entirely.

## Tiered Model Routing

```
Tier 1: GPT-4 / Claude Opus (most capable, most expensive)
  ↓ (if unavailable, rate-limited, or > latency SLA)
Tier 2: GPT-4o-mini / Claude Haiku (capable, cheap, fast)
  ↓ (if also unavailable)
Tier 3: Local model (Llama 3 8B, Mistral 7B) (free, always available)
  ↓ (if query is simple enough)
Tier 4: Static response / rule-based system (guaranteed availability)
```

## Routing Strategies

### Latency-based
Route to Tier 1 only for complex queries (detected by query classifier). Use Tier 2 for 80%+ of traffic.

### Cost-based
Set a monthly budget. Once Tier 1 quota is exhausted (or cost threshold hit), route all traffic to Tier 2.

### Availability-based
Try Tier 1. If it errors or times out, cascade down. Track error rates per tier and pre-emptively skip failing tiers.

### Content-based
Use a fast classifier to determine query difficulty. Simple lookups → Tier 2 or 3. Complex reasoning → Tier 1.

## Implementation

```python
chain = FallbackChain([
    ModelTier("gpt-4", max_retries=2, timeout=30),
    ModelTier("gpt-4o-mini", max_retries=2, timeout=20),
    ModelTier("local-llama", max_retries=1, timeout=60),
    ModelTier("static-response", max_retries=0),
])

response = chain.execute(user_query)
```

## Dynamic Fallback Adjustment

- Monitor p99 latency and error rate per tier
- If Tier 1 error rate > 5% in 5-minute window, skip Tier 1 for next 5 minutes
- If Tier 2 latency > 2x baseline, shift traffic to Tier 3 temporarily
- Auto-recover: periodically retry skipped tiers (every 30s, exponential backoff)

## Combined with Circuit Breaker

Fallback chains and circuit breakers are complementary:
- **Circuit breaker** prevents repeated calls to a failing tier
- **Fallback chain** defines what to do when a tier is unavailable
- Together they provide comprehensive resilience

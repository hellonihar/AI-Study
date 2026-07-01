# Circuit Breakers

## Motivation

When an LLM API or upstream service fails, retrying indefinitely wastes time and money. A circuit breaker detects persistent failures and fast-fails requests until the service recovers.

## State Machine

```
       ┌──────────┐
       │  CLOSED   │ (normal operation — requests pass through)
       └─────┬─────┘
             │ failure count > threshold
             ▼
       ┌──────────┐
       │   OPEN    │ (fail fast — no requests sent)
       └─────┬─────┘
             │ timeout expires
             ▼
       ┌───────────┐
       │ HALF-OPEN │ (trial request to test recovery)
       └─────┬─────┘
            / \
     success   failure
      /           \
    CLOSED        OPEN
```

## Configuration

| Parameter | Typical Value | Description |
|-----------|--------------|-------------|
| failure_threshold | 5 | Consecutive failures before opening |
| recovery_timeout | 30s | Time before transitioning to half-open |
| half_open_max_requests | 3 | Allowed trial requests in half-open state |
| success_threshold | 2 | Consecutive successes to close |
| timeout_duration | 10s | Per-request timeout |

## Failure Detection

What counts as a failure:
- HTTP 5xx responses
- Request timeout (> configured timeout)
- Rate limit 429 (configurable — some teams treat this separately)
- Invalid response (malformed JSON, empty content)

What does NOT count:
- HTTP 4xx (client errors — fix the request, not the circuit)
- Valid responses with low-quality content (tracked separately)

## Implementation Considerations

- **Per-endpoint circuits**: Each API endpoint gets its own circuit
- **Per-model circuits**: Separate circuits for gpt-4, gpt-4o-mini, etc.
- **Per-user circuits**: Optional — prevents one noisy user from starving others

## Metrics to Monitor

- Circuit state transitions (OPEN/CLOSED/HALF-OPEN)
- Time spent in OPEN state
- Number of requests fast-failed (saved cost)
- Recovery success rate (half-open → closed ratio)
- False positives (circuit opened when API was actually healthy)

## Integration with Fallback Chains

Circuit breaker + fallback chain = robust resilience:

```python
circuit = CircuitBreaker("gpt-4", failure_threshold=5)
if circuit.is_open():
    return fallback_chain.execute(query)  # skip to cheaper model

try:
    result = call_gpt4(query)
    circuit.record_success()
    return result
except Exception:
    circuit.record_failure()
    return fallback_chain.execute(query)
```

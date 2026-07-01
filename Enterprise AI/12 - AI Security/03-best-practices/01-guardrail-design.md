# Guardrail Design Best Practices

## Architecture Principles

### Defense in Depth
No single guardrail is sufficient. Layer multiple independent checks:
- Input normalization → content safety → PII detection → rate limiting
- Each layer should catch what previous layers miss

### Fail Closed
When a guardrail cannot make a decision (timeout, model error), block by default. A blocked benign request is better than a passed harmful one.

### Independent Layers
Guardrails should not share state or dependencies. If one layer fails, others must still function independently.

## Implementation Guidelines

### Input Guardrails

| Principle | Implementation |
|-----------|---------------|
| Normalize first | Apply Unicode normalization, decode encodings before checking |
| Check early | Block at the earliest possible stage to save compute |
| Use multiple classifiers | Regex + ML + LLM-as-judge for different attack types |
| Score-based thresholds | Return a score, let the orchestrator decide the action |

### Output Guardrails

| Principle | Implementation |
|-----------|---------------|
| Check everything | Every response passes through output guardrails |
| Redact, don't just block | PII should be redacted so valid content still reaches users |
| Preserve structure | Redaction should maintain output format (JSON, Markdown) |
| Log bypass attempts | Every blocked output should be logged for analysis |

## Performance Budget

| Guardrail Type | Max Latency | Budget % |
|---------------|-------------|----------|
| Regex checks | 1ms | 5% |
| ML classifier | 20ms | 20% |
| NER/PII detection | 10ms | 10% |
| LLM-as-judge | 500ms | 50% |
| Orchestration overhead | 50ms | 15% |

Total guardrail latency should not exceed 600ms p99 for interactive applications.

## Testing Guardrails

| Test Type | Frequency | Method |
|-----------|-----------|--------|
| Unit tests | Every commit | Specific attack inputs, verify block |
| Regression tests | Every deployment | Previously successful attacks, verify still blocked |
| Red teaming | Weekly | Automated + manual attack generation |
| A/B testing | Per guardrail update | Compare block rate, false positive rate |
| Load testing | Monthly | Verify latency SLAs under peak load |

## Common Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| Over-blocking | Poor UX, user churn | Regular false positive analysis |
| Under-blocking | Security incidents | Conservative thresholds, red team validation |
| Guardrail model drift | Decreasing effectiveness | Regular evaluation on test sets |
| Latency creep | User frustration | Performance monitoring per guardrail |
| Single point of failure | Complete bypass | Multiple independent guardrail vendors |

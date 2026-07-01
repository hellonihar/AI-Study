# Monitoring & Observability Best Practices

## Architecture Principles

### Three Pillars
All three observability pillars are required for LLM systems:

| Pillar | Purpose | LLM-Specific Considerations |
|--------|---------|---------------------------|
| Metrics | Quantitative health indicators | Quality scores, token burn, hallucination rate |
| Logs | Event records for debugging | Input/output pairs, guardrail decisions |
| Traces | End-to-end request flow | Span-level latency attribution, model inference timing |

### Sampling Strategy
Full observability for every request is cost-prohibitive. Use adaptive sampling:

| Request Type | Sample Rate | Rationale |
|-------------|-------------|-----------|
| Normal (p50 latency, no errors) | 1-2% | Baseline understanding |
| High latency (> p90) | 10-25% | Diagnose slow requests |
| Errors | 100% | Every failure needs investigation |
| Guardrail blocks | 100% | Safety events must be fully auditable |
| User-reported issues | 100% | Support-driven investigation |

## Implementation Guidelines

### Metrics Collection
- Track p50, p95, and p99 for latency (not just average)
- Measure quality on a sampled subset (LLM-as-judge is expensive)
- Break down cost by feature, user tier, and model
- Export metrics with consistent labels for dashboard aggregation

### Logging Structure
```json
{
  "timestamp": "2026-07-01T14:23:00Z",
  "level": "INFO",
  "trace_id": "abc123def456",
  "service": "model-server",
  "event": "inference_complete",
  "attributes": {
    "model": "gpt-4o-mini",
    "latency_ms": 320,
    "tokens": 570,
    "temperature": 0.3
  }
}
```

### Tracing Requirements
Every trace should capture:
- Input guardrail decision + scores
- Model name, version, and inference parameters
- Token counts (prompt + completion)
- Output guardrail decision + scores
- Total end-to-end latency with span breakdown

## Alerting Thresholds

| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| Error rate spike | > 2% of requests | Critical | Auto-rollback |
| p99 latency breach | > 3s | Critical | Scale up, investigate |
| Hallucination rate | > 5% | Critical | Rollback model/prompt |
| Cost anomaly | > 2x daily avg | Warning | Investigate routing |
| Quality score drop | > 5% below baseline | Warning | Notify ML team |
| Drift detection | > 3 sigma | Critical | Investigate input shift |

## Dashboard Design

### Operations Dashboard (SRE)
- Request rate, error rate, p50/p95/p99 latency
- Token throughput, cost per minute
- Active alerts, incident status
- Service health (up/down per component)

### Quality Dashboard (ML Team)
- Hallucination rate over time
- Quality score per model/prompt variant
- Guardrail block rate by category
- User satisfaction trend

### Cost Dashboard (Engineering Leadership)
- Daily/weekly/monthly cost trends
- Cost breakdown by feature, model, user tier
- Cost per request by model
- Anomaly detection alerts

## Key Metrics Reference

| Metric | Collection Method | Cost | Cardinality |
|--------|------------------|------|-------------|
| Latency | Automatic (request timing) | Free | Per-request |
| Error rate | Automatic (status codes) | Free | Per-request |
| Token count | Automatic (tokenizer) | Free | Per-request |
| Cost | Calculated (tokens * pricing) | Free | Per-request |
| Quality | LLM-as-judge (sampled) | $0.001-0.01/eval | Per-sample |
| Safety | Classifier/LLM judge | $0.0001-0.01/eval | Per-request |
| User feedback | Explicit collection | Free | Per-interaction |

## Common Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| No sampling | Unmanageable cost | Adaptive sampling (1% normal, 100% errors) |
| Only averages | Miss tail latency | Always track p50, p95, p99 |
| No cost attribution | Cannot optimize | Tag every request with feature + model + tier |
| Logging PII | Compliance violation | Redact PII before logging |
| No trace correlation | Cannot debug flows | Propagate trace IDs across all services |

# Monitoring & Observability for LLMs

## Why Observability is Different for LLMs

LLMs introduce stochastic outputs, context-dependent behavior, and safety considerations that traditional monitoring doesn't capture. You can't just monitor CPU utilization and error rates.

## Three Pillars of Observability

### Metrics (Quantitative)

| Category | Key Metrics | Collection Method |
|----------|------------|------------------|
| Quality | Response relevance, faithfulness, hallucination rate | LLM-as-judge on 1–5% sample |
| Latency | TTFT, ITL, end-to-end | Per-request instrumentation |
| Throughput | Requests/sec, tokens/sec | Aggregated counters |
| Cost | Cost/request, tokens/request | Token counting + pricing |
| Safety | Guardrail block rate, toxicity score | Guardrail decisions |
| Errors | 4xx, 5xx, timeout rate | HTTP status codes |
| User feedback | Thumbs up/down, rating score | Explicit feedback collection |

### Logs (Qualitative)

| Log Type | Content | Retention |
|----------|---------|-----------|
| Request log | Input, output, latency, model version | 30–90 days |
| Guardrail log | Input/output scores, action taken | 90 days–1 year |
| Error log | Stack traces, failed requests | 90 days |
| Audit log | Model changes, config changes, approvals | 1–3 years |
| Feedback log | User ratings, corrections | 90 days |

### Traces (Request Flow)

| Span | Data |
|------|------|
| Input guardrail | Input hash, scores, action |
| LLM inference | Model name, latency, token count, temperature |
| Output guardrail | Output hash, scores, action |
| Tool call | Tool name, input, output, duration |
| Total request | Correlation ID, total latency, final status |

## Monitoring Architecture

```
Application → OpenTelemetry SDK → Collector → Backend
                                                   ↓
                                           Dashboard ← Alerting
```

### OpenTelemetry Integration
- Instrument all AI services with OTel SDK
- Propagate trace context across service boundaries
- Export to backend (Datadog, Grafana, SigNoz)

### Key Dashboards

**Operations Dashboard** (for SRE/Platform team):
```
Current: 1,245 req/min | p50: 342ms | p99: 1.2s | Error: 0.3%
Tokens: 245K/min | Cost: $0.49/min
```

**Quality Dashboard** (for ML team):
```
Hallucination: 1.2% | Relevance: 4.2/5 | Toxicity: 0.02%
Guardrail block rate: 2.1% | User satisfaction: 88%
```

**Cost Dashboard** (for Engineering leadership):
```
Daily cost: $712 | Per-request avg: $0.0042
By model: GPT-4: $423 | GPT-3.5: $289
By feature: Chat: $567 | Search: $145
```

## Alerting Thresholds

| Alert | Threshold | Severity |
|-------|-----------|----------|
| High error rate | > 2% of requests | Critical |
| High latency | p99 > 3s | Critical |
| Cost spike | > 2x daily average | Warning |
| Hallucination spike | > 5% | Critical |
| Guardrail bypass | ASR > 1% | Critical |
| User satisfaction drop | < 70% positive | Warning |
| Model drift | Embedding drift > threshold | Warning |

## Sampling Strategy

Full observability for every request is expensive (especially LLM-as-judge). Use adaptive sampling:

| Request Type | Sample Rate |
|-------------|-------------|
| Normal (low latency, no errors) | 1% |
| High latency (> p90) | 10% |
| Errors | 100% |
| Guardrail blocks | 100% |
| Random sample (for baseline) | 1% |

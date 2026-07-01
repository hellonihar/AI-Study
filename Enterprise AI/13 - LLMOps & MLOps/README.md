# LLMOps & MLOps

Operational practices for managing LLM systems throughout their lifecycle.

## Key Topics
- Monitoring: quality (faithfulness, relevance), cost (token burn, per-request), latency (p50/p95/p99, TTFT, TPOT), drift
- Evaluation pipelines: automated daily eval sets, LLM-as-judge, human raters
- A/B testing: model versions, prompt variants, retrieval strategies
- CI/CD: prompt version control, model registry, staged rollouts
- Observability: OpenTelemetry tracing, structured logging, dashboards (Grafana, Datadog)
- Alerting: drift detection, budget thresholds, error rate spikes, SLA breaches
- Incident response: model rollback, cache flush, traffic reroute, post-mortems

# LLMOps & MLOps

Operational practices for managing LLM systems throughout their lifecycle.

## Module Structure

| Directory | Contents | Count |
|-----------|----------|-------|
| `01-theory/` | Conceptual deep-dives from fundamentals to production architecture | 10 files |
| `02-code/` | Runnable Python scripts demonstrating key LLMOps patterns | 10 files |
| `03-best-practices/` | Production-tested guidelines and standards | 5 files |
| `04-resources/` | Curated links, papers, tools, and benchmarks | 1 file |

## Key Topics

- **Monitoring**: Quality (faithfulness, relevance), cost (token burn, per-request), latency (p50/p95/p99, TTFT, TPOT), drift detection
- **Evaluation pipelines**: Automated daily eval sets, LLM-as-judge, human raters, regression detection
- **A/B testing**: Model versions, prompt variants, retrieval strategies, statistical significance
- **CI/CD**: Prompt version control, model registry, staged rollouts with canary and auto-rollback
- **Observability**: OpenTelemetry tracing, structured logging, dashboards (Grafana, Datadog)
- **Alerting**: Drift detection, budget thresholds, error rate spikes, SLA breaches
- **Incident response**: Model rollback, cache flush, traffic reroute, post-mortems
- **Cost management**: Token tracking, model routing, caching strategies, budget allocation
- **Versioning**: Model registry, prompt registry, dataset versioning, lineage tracking
- **Production architecture**: Orchestrator patterns, model routing, SLA compliance

## Code Files

| # | File | Description |
|---|------|-------------|
| 1 | `01-monitoring-dashboard.py` | Metrics collection, aggregation (p50/p95/p99), alerting engine |
| 2 | `02-quality-evaluator.py` | LLM-as-judge scoring across 5 dimensions, regression detection |
| 3 | `03-drift-detector.py` | Embedding-based and statistical (KS test) drift detection |
| 4 | `04-cost-tracker.py` | Per-request costing, multi-dimension aggregation, anomaly detection |
| 5 | `05-model-registry.py` | Model, prompt, and dataset versioning with lineage tracking |
| 6 | `06-ab-testing-framework.py` | Traffic routing, experiment tracking, statistical significance testing |
| 7 | `07-cicd-pipeline-sim.py` | CI/CD pipeline with lint, eval, build, deploy stages and gates |
| 8 | `08-incident-response-system.py` | Detection, triage, containment, post-mortem with action items |
| 9 | `09-observability-tracing.py` | Distributed tracing, structured logging, metrics export |
| 10 | `10-production-llmops-orchestrator.py` | End-to-end orchestrator with routing, health checks, SLA compliance |

## Best Practices Files

| # | File | Focus |
|---|------|-------|
| 1 | `01-monitoring-and-observability.md` | Metrics, logs, traces, sampling, alerting thresholds |
| 2 | `02-evaluation-and-quality.md` | Multi-layer evaluation, test sets, regression detection |
| 3 | `03-cost-optimization.md` | Model selection, caching, prompt optimization, budget management |
| 4 | `04-cicd-and-deployment.md` | Pipeline design, canary releases, rollback strategy |
| 5 | `05-incident-response.md` | Severity classification, response process, post-mortems |

## Requirements

Code files use only standard library + numpy. No external API keys or services required.

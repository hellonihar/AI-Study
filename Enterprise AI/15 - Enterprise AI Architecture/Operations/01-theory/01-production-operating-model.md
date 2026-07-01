# Production Operating Model

## Operations at Scale

| Scale | Daily Requests | Team Size | Key Challenges |
|-------|---------------|-----------|----------------|
| Starter | < 10K | 1-2 engineers | Basic uptime, manual monitoring |
| Growing | 10K-100K | 3-5 engineers | Latency, cost tracking, alerting |
| Scale-up | 100K-1M | 6-10 engineers | Multi-model, A/B testing, drift |
| Enterprise | 1M+ | 10-20+ engineers | Multi-region, auto-scaling, optimization |

## Operational Responsibilities

| Function | Owner | Tools |
|----------|-------|-------|
| Model serving | ML Platform | TGI, vLLM, Triton, k8s |
| Monitoring | SRE/ML Ops | Prometheus, Grafana, custom metrics |
| Cost optimization | FinOps | Budget alerts, usage dashboards |
| Incident response | On-call | PagerDuty, runbooks, postmortems |
| Capacity planning | Infra | Utilization metrics, forecasting |
| CI/CD | ML Platform | GitHub Actions, ArgoCD, MLflow |

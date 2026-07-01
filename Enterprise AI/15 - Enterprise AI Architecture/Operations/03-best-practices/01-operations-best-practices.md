# Operations Best Practices

## Key Practices

| Area | Practice |
|------|----------|
| Observability | Log every request (input, output, latency, cost, model version) |
| Alerting | Alert on latency P95 > 2s, error rate > 1%, cost > 20% above baseline |
| Capacity | Maintain 20% headroom; auto-scale based on queue depth |
| Cost tracking | Tag every request by model, use case, team; weekly cost review |
| Incident response | Documented runbooks for all known failure modes |
| Change management | All model changes through CI/CD with canary deployment |
| Testing | Regression test suite run before every deployment |

## Deployment Strategy

| Environment | Purpose | Traffic | Monitoring |
|------------|---------|---------|------------|
| Development | Integration testing | Synthetic | Basic |
| Staging | Pre-production validation | Shadow/synthetic | Full |
| Canary | Gradual rollout | 1-5% real traffic | Full + comparison |
| Production | Live | 100% | Full |

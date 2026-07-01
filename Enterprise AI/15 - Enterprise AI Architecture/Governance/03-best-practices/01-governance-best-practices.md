# Governance Best Practices

## Principles

| Principle | Practice |
|-----------|----------|
| Risk-based | Lower effort on low-risk models, rigorous review on high-risk |
| Automated by default | Policy-as-code, automated gates, self-service for T1-T2 |
| Transparent | Model cards, audit trails, decision logging |
| Embedded | Governance is part of ML platform, not a separate team |
| Continuous | Monitoring, drift detection, periodic audits |

## Implementation

| Layer | Tooling | Frequency |
|-------|---------|-----------|
| Registration | ML Registry (MLflow, custom) | Per model |
| Risk classification | Auto-classifier | Per model creation |
| Bias audit | Fairness assessment library | Pre-deploy + annual |
| Compliance check | Policy engine | Pre-deploy + quarterly |
| Monitoring | Prometheus + Grafana | Continuous |
| Incident response | PagerDuty + runbooks | Per incident |

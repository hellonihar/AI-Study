# Governance Operating Model

## Governance at Scale

As AI adoption grows, governance must scale without becoming a bottleneck:

| Scale | Models | Governance Approach |
|-------|--------|-------------------|
| < 10 | Manual review per deployment | One-on-one approvals |
| 10-50 | Tiered automation | Risk-based, self-service for low risk |
| 50-200 | Policy-as-Code | Automated gates, exception process |
| 200+ | Federated + automated | Embedded governance leads, continuous audit |

## Key Governance Processes

| Process | Frequency | Owner |
|---------|-----------|-------|
| Model registration | Per new model | ML Platform |
| Risk classification | Per model creation | ML Team + Governance |
| Bias audit | Pre-deployment + annual (T3+) | Governance |
| Compliance check | Pre-deployment + quarterly | Compliance |
| Incident review | Per incident | On-call + Governance |
| Model retirement | Per deprecation | ML Platform |
| Vendor assessment | Per new vendor + annual | Procurement + Governance |

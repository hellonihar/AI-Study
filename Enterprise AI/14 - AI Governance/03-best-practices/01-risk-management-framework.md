# Risk Management Framework Best Practices

## Governance Structure

### Three Lines of Defense Model

| Line | Role | Responsibility |
|------|------|----------------|
| 1st | AI development teams | Identify and manage risks in their models |
| 2nd | AI governance function | Set policies, monitor compliance, provide guidance |
| 3rd | Internal audit | Independent assurance on governance effectiveness |

### Risk Ownership
- Every AI system must have a named risk owner
- Risk owners are responsible for maintaining risk assessments
- Risk ownership cannot be delegated below a defined level
- Escalation paths must be documented and tested

## Risk Classification

### Classification Criteria
Classify every AI system using these dimensions:

| Dimension | Low (1) | Medium (2) | High (3) | Critical (4) |
|-----------|---------|------------|----------|--------------|
| User impact | No interaction | Informational | Decisions | Life-altering |
| Data sensitivity | Public | Internal | PII | Regulated |
| Autonomy | Human-in-loop | Human-on-loop | Automated | Fully autonomous |
| Scale | <100 users | <1000 users | <100K users | Public/millions |
| Failure impact | Minor inconvenience | Operational disruption | Financial/legal harm | Physical harm |

### Classification Process
1. **Initial assessment**: Score each dimension, calculate composite score
2. **Tier assignment**: Map score to risk tier (T1-T4)
3. **Review and approve**: Tier assignment must be approved by risk owner
4. **Document**: Record assessment in risk registry
5. **Periodic review**: Reassess quarterly for T3+, annually for T1-T2

## Risk Mitigation

### Controls by Tier

| Control | T1 | T2 | T3 | T4 |
|---------|----|----|----|----|
| Model documentation | Required | Required | Required | Required |
| Risk assessment | Optional | Required | Required | Required |
| Bias audit | Optional | Basic | Comprehensive | Comprehensive |
| External audit | No | No | Recommended | Required |
| Human oversight | No | Recommended | Required | Required |
| Explainability | No | Recommended | Required | Required |
| Incident response plan | No | Recommended | Required | Required |

### Mitigation Strategies

| Risk | Mitigation | Verification |
|------|------------|-------------|
| Bias and fairness | Bias audit, diverse training data, fairness constraints | Regular re-audit |
| Safety failure | Guardrails, human review, canary deployment | Safety eval suite |
| Privacy violation | PII detection, data minimization, access controls | Regular privacy review |
| Regulatory non-compliance | Compliance checklist, legal review | External audit |
| Operational failure | Monitoring, alerting, rollback capability | Incident response drills |

## Risk Monitoring

### Continuous Monitoring
- Track risk metrics for all T3+ systems
- Monitor for risk reclassification triggers
- Alert on risk metric breaches
- Quarterly risk review for T3+, annual for T1-T2

### Risk Reclassification Triggers
- Change in system capability or scope
- Change in deployment scale or user population
- Regulatory change affecting the system
- Incident or near-miss
- New use case or integration

## Common Risk Management Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| Classification without action | False sense of security | Tie controls to tier |
| Static risk assessments | Outdated risk picture | Regular reassessment cadence |
| Ignoring third-party risk | Supply chain vulnerabilities | Vendor risk assessment |
| Documentation in silos | Missing context | Integrated risk registry |
| No risk appetite definition | Inconsistent decisions | Board-approved risk appetite |

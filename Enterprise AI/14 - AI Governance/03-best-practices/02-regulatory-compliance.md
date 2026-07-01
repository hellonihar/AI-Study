# Regulatory Compliance Best Practices

## Compliance Strategy

### Know Your Obligations
Map every AI system to applicable regulations:

| Regulation | Applicability | Key Requirements |
|------------|--------------|-----------------|
| EU AI Act | AI systems used in EU or affecting EU residents | Risk classification, conformity assessment, transparency |
| GDPR | Processing personal data of EU residents | Consent, right to explanation, right to deletion |
| CCPA/CPRA | Businesses collecting CA resident data | Disclosure, opt-out, deletion |
| NYC Local Law 144 | Automated hiring tools in NYC | Bias audit, notification, alternative process |
| HIPAA | Healthcare AI in US | Privacy rule, security rule, breach notification |
| SOC 2 | Service organizations handling customer data | Security, availability, confidentiality |

### Build a Compliance Program

1. **Inventory**: Catalog all AI systems
2. **Classify**: Risk-tier each system
3. **Map**: Identify applicable regulations per tier
4. **Control**: Implement controls for each requirement
5. **Evidence**: Collect and store compliance evidence
6. **Monitor**: Track regulatory changes
7. **Audit**: Regular internal and external audits

## Compliance Controls

### Documentation Requirements

| Document | Content | Update Frequency |
|----------|---------|-----------------|
| Model card | Model details, performance, limitations | Per version |
| System card | System architecture, data flow, safety | Per deployment |
| Risk assessment | Risk tier, mitigations, residual risk | Quarterly |
| Bias audit | Fairness metrics, subgroup analysis, findings | Annual (T3+ semi-annual) |
| Data protection impact assessment | Data processing, risks, mitigations | Per significant change |
| Incident report | Detection, response, root cause, remediation | Per incident |

### Evidence Collection

| Evidence Type | Collection Method | Retention |
|---------------|------------------|-----------|
| Deployment approvals | Workflow system | 3 years |
| Model evaluations | CI/CD pipeline | Lifetime of model |
| Monitoring data | Observability platform | 1 year |
| Audit logs | Immutable log store | 3 years |
| User consent | Consent management system | Duration + 2 years |
| Training data provenance | Data catalog | Lifetime of model |

## Audit Readiness

### Continuous Audit Readiness
- Maintain pre-built evidence packages for each regulation
- Automate compliance report generation
- Conduct internal audits quarterly
- Remediate findings within defined SLAs

### Evidence Package Structure
```
compliance-evidence/
  model-inventory/
  risk-assessments/
  bias-audits/
  deployment-approvals/
  incident-reports/
  audit-logs/
  training-data-provenance/
```

## Cross-Jurisdictional Compliance

### Operating Across Jurisdictions
1. Identify all applicable regulations per deployment location
2. Implement highest common denominator requirements
3. Layer jurisdiction-specific controls on top
4. Document jurisdictional differences
5. Monitor regulatory changes in all jurisdictions

### Common Baseline
All systems should implement:
- Model documentation and versioning
- Risk classification and assessment
- Basic bias and fairness checks
- Audit logging (immutable)
- Incident response process
- Transparency notices to users

## Compliance Automation

| Area | Automation Opportunity | Tooling |
|------|----------------------|---------|
| Policy enforcement | Automated policy checks in CI/CD | Policy-as-code engine |
| Evidence collection | Automated log aggregation | Audit log pipeline |
| Compliance reporting | Automated compliance dashboards | BI platform + compliance data |
| Regulatory change monitoring | Regulatory intelligence feeds | Legal tech platforms |
| Consent management | Automated consent lifecycle | Consent management platform |

## Common Compliance Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| Treating compliance as checklist | Missing intent of regulation | Understand regulatory goals |
| Reactive compliance | Rushing to meet deadlines | Proactive compliance program |
| Manual evidence collection | Gaps and errors | Automated evidence pipelines |
| Ignoring regulatory change | Falling out of compliance | Regulatory monitoring process |
| Inconsistent application | Gaps across teams | Central standards, federated execution |

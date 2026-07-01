# Compliance & Standards Best Practices

## AI Security Compliance Checklist

### Pre-Deployment
- [ ] Model card created and reviewed
- [ ] System card documenting architecture and safety mechanisms
- [ ] Bias evaluation across demographic groups (max 5% gap)
- [ ] Safety benchmark results (TruthfulQA, BBQ, Toxigen)
- [ ] Red team engagement completed with no critical findings
- [ ] Guardrail effectiveness measured (attack success rate < 1%)
- [ ] Data provenance documented for all training data
- [ ] PII scan completed on training data
- [ ] Third-party dependency audit
- [ ] Penetration test completed

### Ongoing
- [ ] Weekly automated red teaming
- [ ] Monthly bias drift evaluation
- [ ] Monthly dependency vulnerability scan
- [ ] Quarterly full red team engagement
- [ ] Quarterly incident response tabletop exercise
- [ ] Annual third-party security audit
- [ ] Continuous guardrail effectiveness monitoring

## Documentation Requirements

### Model Card Template
| Field | Content |
|-------|---------|
| Model name | Unique identifier and version |
| Architecture | Base model, fine-tuning method |
| Intended use | Target use cases, out-of-scope uses |
| Training data | Source, size, date range, curation process |
| Evaluation results | Task metrics, capability benchmarks, safety scores |
| Known limitations | Edge cases, failure modes, biases |
| Ethical considerations | Potential harms, mitigation strategies |
| Maintenance | Update cadence, owner, support contact |

### System Card Template
| Field | Content |
|-------|---------|
| System name | Production name and version |
| Components | Models, guardrails, infrastructure |
| Data flow | Input processing through output delivery |
| Safety mechanisms | Guardrail descriptions, versions, thresholds |
| Security controls | Auth, rate limiting, encryption, audit logging |
| Known vulnerabilities | Documented from red teaming |
| Incident response | Process, contacts, escalation paths |
| Change log | Version history with dates and descriptions |

## Regulatory Alignment

| Regulation | Key Requirements | Documentation Needed |
|------------|-----------------|---------------------|
| EU AI Act | Risk classification, conformity assessment, transparency | System card, risk assessment, technical documentation |
| GDPR | Data protection, right to explanation, consent | Data processing records, PIA, privacy notice |
| NIST AI RMF | Govern, Map, Measure, Manage | Risk register, measurement reports |
| HIPAA | PHI protection, access controls, audit controls | BAAs, risk analysis, audit logs |
| CCPA/CPRA | Consumer rights, opt-out, data inventory | Data mapping, consumer request process |

## Audit Trail Requirements

| Event Type | Data to Log | Retention |
|-----------|-------------|-----------|
| User input | Hashed input, user ID, timestamp | 90 days |
| Model output | Hashed output, model version | 90 days |
| Guardrail decision | Scores, action, guardrail version | 1 year |
| Human review | Reviewer ID, decision, timestamp | 3 years |
| Model deployment | Version, target, approver, timestamp | 3 years |
| Security incident | Full details, investigation, remediation | 5 years |
| Training data provenance | Source, curation steps, version | Lifetime of model |

## Third-Party Risk Management

| Vendor Type | Risk Considerations | Mitigations |
|-------------|-------------------|-------------|
| Base model provider | Data handling, model safety | Contractual safeguards, independent eval |
| Cloud infrastructure | Data residency, access controls | Compliance certifications (SOC2, ISO 27001) |
| Guardrail vendor | False positive/negative rates | Regular evaluation, fallback guardrails |
| Annotation services | Data privacy, quality | NDA, data anonymization, quality audits |

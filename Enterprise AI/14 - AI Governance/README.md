# AI Governance

Policies, processes, and controls for responsible, compliant, and auditable AI deployment.

## Module Structure

| Directory | Contents | Count |
|-----------|----------|-------|
| `01-theory/` | Conceptual deep-dives from fundamentals to production architecture | 10 files |
| `02-code/` | Runnable Python scripts demonstrating key governance patterns | 10 files |
| `03-best-practices/` | Production-tested guidelines and standards | 5 files |
| `04-resources/` | Curated links, papers, tools, and benchmarks | 1 file |

## Key Topics

- **Risk classification**: Tier-based model risk classification (T1-T4) with proportional controls
- **Regulatory compliance**: EU AI Act, GDPR, CCPA, NYC Local Law 144, HIPAA, SOC 2
- **Transparency**: Model cards, system cards, dataset cards, user-facing disclosures
- **Data governance**: Consent management, retention policies, right-to-deletion, data lineage
- **Bias and fairness**: Fairness metrics, bias auditing, mitigation strategies, subgroup analysis
- **Audit trails**: Immutable, tamper-evident logging with hash chain verification
- **Organizational structure**: AI Review Boards, centers of excellence, escalation paths
- **Ethics**: Stakeholder impact assessments, ethics review process, ethical dilemmas
- **Policy enforcement**: Policy-as-code, automated compliance gates in CI/CD
- **Production governance**: Compliance dashboards, continuous audit readiness

## Code Files

| # | File | Description |
|---|------|-------------|
| 1 | `01-risk-classifier.py` | Model risk tier classification across 5 dimensions |
| 2 | `02-compliance-checker.py` | Multi-regulation compliance verification |
| 3 | `03-model-card-generator.py` | Auto-generate model cards from metadata |
| 4 | `04-data-governance-manager.py` | Consent, retention, and right-to-deletion management |
| 5 | `05-bias-auditor.py` | Fairness metrics (demographic parity, equal opportunity, disparate impact) |
| 6 | `06-audit-trail-logger.py` | Immutable, tamper-evident audit logging with hash chain |
| 7 | `07-ethics-impact-assessor.py` | Stakeholder impact analysis and ethics review |
| 8 | `08-approval-workflow.py` | Tiered approval workflows with required reviews and approvers |
| 9 | `09-policy-enforcement-engine.py` | Policy-as-code evaluation and enforcement gates |
| 10 | `10-governance-dashboard.py` | End-to-end governance overview with compliance scoring |

## Best Practices Files

| # | File | Focus |
|---|------|-------|
| 1 | `01-risk-management-framework.md` | Risk classification, controls, monitoring |
| 2 | `02-regulatory-compliance.md` | Compliance strategy, evidence collection, audit readiness |
| 3 | `03-transparency-and-documentation.md` | Model cards, system cards, user disclosures |
| 4 | `04-data-governance.md` | Consent, retention, lineage, quality |
| 5 | `05-ethics-and-bias.md` | Bias detection, mitigation, stakeholder impact |

## Requirements

Code files use only standard library + numpy. No external API keys or services required.

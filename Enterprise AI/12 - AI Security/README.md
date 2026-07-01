# AI Security

Protecting AI systems from prompt injection, jailbreaks, data extraction, and other adversarial attacks through layered guardrails, red teaming, and compliance frameworks.

## Module Structure

```
12 - AI Security/
├── 01-theory/          # 10 files: overview through production architecture
├── 02-code/            # 10 scripts: injection detection through security middleware
├── 03-best-practices/  # 5 files: guardrails, injection defense, red teaming, compliance, IR
├── 04-resources/       # Papers, frameworks, datasets, regulations, tutorials, books
└── README.md           # This file
```

## Theory (01-theory/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-ai-security-overview.md` | Threat landscape, attack categories, defense in depth, risk classification |
| 2 | `02-prompt-injection-and-jailbreaks.md` | Direct/indirect injection, DAN, roleplay, multi-turn, encoding bypass |
| 3 | `03-input-guardrails.md` | Normalization, content classification, adversarial detection, rate limiting |
| 4 | `04-output-guardrails.md` | Content safety, PII redaction, policy compliance, format validation |
| 5 | `05-pii-detection-and-redaction.md` | PII types, detection strategies, redaction methods, pipeline integration |
| 6 | `06-model-security.md` | Data poisoning, model inversion, extraction, adversarial examples |
| 7 | `07-infrastructure-security.md` | API security, network segmentation, CI/CD security, incident response |
| 8 | `08-red-teaming.md` | Methodology, manual/automated testing, severity classification, reporting |
| 9 | `09-compliance-and-safety-standards.md` | EU AI Act, NIST AI RMF, model cards, system cards, audit trails |
| 10 | `10-production-security-architecture.md` | Defense in depth, secure inference, incident response playbook |

## Code Examples (02-code/)

| # | File | Description | Requirements |
|---|------|-------------|--------------|
| 1 | `01-prompt-injection-detector.py` | Rule-based + embedding injection detection | numpy |
| 2 | `02-jailbreak-classifier.py` | Multi-tactic jailbreak classification | numpy |
| 3 | `03-input-guardrail-pipeline.py` | Multi-layer input safety filtering | numpy |
| 4 | `04-output-content-filter.py` | Safety, PII, policy compliance filtering | numpy |
| 5 | `05-pii-detection-redaction.py` | Detect and mask PII (email, phone, SSN, etc.) | none (stdlib) |
| 6 | `06-rate-limiting-access-control.py` | Token bucket, user quotas, IP throttling | numpy |
| 7 | `07-adversarial-input-generation.py` | Generate attack variants for testing | numpy |
| 8 | `08-automated-red-teaming.py` | Generate attacks and evaluate guardrail effectiveness | numpy |
| 9 | `09-security-audit-logger.py` | Immutable audit trail with chain verification | none (stdlib) |
| 10 | `10-production-security-middleware.py` | End-to-end security pipeline for inference | numpy |

## Best Practices (03-best-practices/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-guardrail-design.md` | Defense in depth, fail closed, performance budgets, testing |
| 2 | `02-prompt-injection-defense.md` | Input validation, prompt isolation, detection, response verification |
| 3 | `03-red-teaming-process.md` | Team composition, methodology, reporting, automation |
| 4 | `04-compliance-and-standards.md` | Pre-deployment checklist, model cards, regulatory alignment |
| 5 | `05-incident-response.md` | Severity classification, response process, communication plan |

## Key Topics

- **Prompt Injection**: Direct, indirect, payload splitting, encoding bypass
- **Jailbreaking**: DAN, roleplay, multi-turn erosion, hypothetical scenarios
- **Guardrails**: Input normalization, content filtering, PII redaction, rate limiting
- **Red Teaming**: Automated (Garak, PyRIT), manual, severity classification
- **Compliance**: EU AI Act, NIST AI RMF, model cards, audit trails
- **Infrastructure**: API security, network segmentation, secrets management
- **Incident Response**: Detection, triage, containment, post-mortem

## Quick Start

```bash
# Prompt injection detection
python "02-code/01-prompt-injection-detector.py"

# Input guardrail pipeline
python "02-code/03-input-guardrail-pipeline.py"

# Automated red teaming
python "02-code/08-automated-red-teaming.py"

# Production security middleware
python "02-code/10-production-security-middleware.py"
```

## Prerequisites

- **Python 3.10+**
- **Core**: numpy (for most scripts)
- **Stdlib only**: Scripts 5, 9 (PII detection, audit logger)

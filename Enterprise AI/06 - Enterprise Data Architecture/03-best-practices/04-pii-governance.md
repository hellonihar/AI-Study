# PII Governance Best Practices

## 1. Classification Taxonomy
| Tier | Examples | Handling |
|------|----------|----------|
| PII-1 (Public) | Company name, job title | No restriction |
| PII-2 (Internal) | Email, employee ID | Encrypt at rest, mask in logs |
| PII-3 (Confidential) | Name, phone, address | Encrypt + tokenize, strict access control |
| PII-4 (Regulated) | SSN, passport, health data | Tokenize or remove, audit every access |

## 2. Detection Strategy
- **Pattern-based**: Regex for emails, phone numbers, SSNs
- **ML-based**: NER models for names, addresses, orgs
- **Hybrid**: Pattern matching first (fast, high precision), ML second (high recall) → human review edge cases
- Scan at rest (scheduled) and in motion (pipeline hook)

## 3. Remediation Techniques
| Technique | Reversible | Use Case |
|-----------|------------|----------|
| Masking | No | Logs, dashboards |
| Hashing | No | Join keys, dedup |
| Encryption | Yes | Column-level storage |
| Tokenization | Yes | Third-party data sharing |
| Redaction | No | Customer-facing output |
| Synthetic replacement | No | Testing/development |

## 4. Data Flow Controls
- All PII columns tagged in schema registry with `pii_tier` attribute
- Downstream consumers must request access; auto-approved for PII-1/2, manual approval for PII-3/4
- Pipeline fails if unclassified column flows into PII-restricted sink
- Audit log: every PII access recorded (who, what, when, why)

## 5. Testing & Validation
- Positive tests: known PII patterns correctly detected
- Negative tests: non-PII text not falsely flagged
- Adversarial tests: `attacker@domain.com` vs `attacker at domain dot com`
- Periodic scanning: re-scan all datasets monthly for new PII

## 6. Regional Considerations
| Regulation | Requirement |
|------------|-------------|
| GDPR (EU) | Right to erasure, data portability |
| CCPA (California) | Opt-out of data selling |
| HIPAA (Healthcare) | Strict de-identification rules |
| LGPD (Brazil) | Similar to GDPR |
- Maintain a regulation-to-data mapping matrix
- Apply the strictest regulation globally to simplify compliance

## 7. Tooling
- **Amazon Macie**: S3 PII scanning
- **Azure Purview**: Data classification + lineage
- **Presidio** (open source): Flexible detection + anonymization
- **Tonic.ai** / **Mostly AI**: Synthetic data generation

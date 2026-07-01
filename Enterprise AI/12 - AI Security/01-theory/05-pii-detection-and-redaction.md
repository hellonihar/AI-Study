# PII Detection & Redaction

## Why PII Matters for AI Systems

LLMs can inadvertently memorize and reproduce training data, including personally identifiable information. They can also be prompted to generate PII based on context or pattern completion. PII leakage in AI outputs can lead to regulatory fines, legal liability, and reputational damage.

## Regulatory Landscape

| Regulation | Jurisdiction | Key Requirements |
|------------|-------------|-----------------|
| GDPR | EU | Right to erasure, data minimization, consent |
| CCPA/CPRA | California | Right to know, right to delete, opt-out |
| HIPAA | US Healthcare | Protected health information safeguards |
| LGPD | Brazil | Similar to GDPR |
| PIPEDA | Canada | Consent, limited use |
| PDPB | India | Consent, data localization |

## Types of PII

### Direct Identifiers
| Type | Examples | Detection Method |
|------|----------|-----------------|
| Name | John Smith, María García | NER + lookup |
| Email | user@domain.com | Regex |
| Phone | +1-555-0123 | Regex |
| SSN | 123-45-6789 | Regex + checksum |
| Credit Card | 4111-1111-1111-1111 | Regex + Luhn |
| Passport | AB1234567 | Regex + pattern |
| Driver's License | CA-1234567 | Regex + pattern |
| IP Address | 192.168.1.1 | Regex |
| API Key | sk-proj-... | Regex + entropy |

### Quasi-Identifiers
| Type | Examples | Detection Method |
|------|----------|-----------------|
| DOB | 1990-01-15 | Regex + context |
| Address | 123 Main St | NER + regex |
| ZIP Code | 94105 | Regex |
| Gender | Male/Female | Context |
| Occupation | Engineer | Context |
| Medical Info | Diagnosis codes | NER + regex |

### Indirect Identifiers
| Type | Examples | Detection |
|------|----------|-----------|
| Username | jsmith123 | Context |
| Device ID | UID-abc123 | Pattern |
| Browser fingerprint | User agent + screen res | Pattern |
| Behavioral data | Navigation patterns | Unlikely in LLM output |

## Detection Strategies

### Regex-Based
Fast, precise for structured PII (emails, SSNs, credit cards). Use carefully crafted patterns with word boundaries to avoid false positives.

### Named Entity Recognition (NER)
ML-based detection for unstructured PII (names, locations, organizations). Use fine-tuned transformer models for high accuracy.

### Context-Aware Detection
Use LLM-as-judge for ambiguous cases:

```
System: Does this text contain PII? Consider names, emails,
phone numbers, addresses, SSNs, medical info, financial info.

Text: [output text]
Response: YES/NO + list of detected PII types.
```

### Entropy-Based
Detect high-entropy strings that are likely API keys, tokens, or passwords. Compute Shannon entropy on alphanumeric sequences > 10 characters.

## Redaction Strategies

| Strategy | Method | Use Case |
|----------|--------|----------|
| Mask | `[REDACTED]` | All PII |
| Anonymize | `[EMAIL]`, `[PHONE]` | Type-preserving |
| Pseudonymize | Consistent fake values | Analytics, debugging |
| Partial | `j***@***.com` | UX-friendly masking |
| Truncate | `####-####-####-` | Credit cards |
| Generalize | "California" instead of "123 Main St, SF, CA" | Location privacy |

## Pipeline Integration

```
LLM Output → Regex PII Detector → NER PII Detector → Context Detector → Redactor → Output
                    ↓                    ↓                    ↓
               Audit Log           Audit Log           Audit Log
```

### Performance Targets

| Stage | Max Latency | Check |
|-------|-------------|-------|
| Regex | 1ms | All structured PII |
| NER | 10ms | Names, locations, orgs |
| Context | 200ms | Ambiguous or unstructured |
| Redaction | 1ms | Apply transformations |

## Handling PII in Training Data

PII in training data is a separate concern from PII in model outputs:

1. **Strip before training**: Run PII detection on all training data before fine-tuning
2. **Replacement**: Replace real PII with synthetic placeholders
3. **Differential privacy**: Add noise to gradients during training to bound memorization
4. **Verification**: Sample trained model outputs to check for PII leakage

## False Positive Management

PII detectors can produce false positives (e.g., "I lived at 123 Main St" — this could be a fictional example). Strategies:

| Strategy | Description |
|----------|-------------|
| Threshold tuning | Higher threshold for structured PII, lower for free text |
| Context window | Check surrounding words for fictional indicators |
| Allowlist | Known safe patterns (product codes, example data) |
| Human review | Sample flagged outputs for calibration |

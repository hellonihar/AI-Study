# Data Governance for AI Systems

## Why Data Governance Matters for AI

AI systems are fundamentally data-driven. Poor data governance leads to biased models, privacy violations, compliance failures, and eroding user trust.

## Key Data Governance Areas

### Data Collection

| Principle | Practice | Compliance Aspect |
|-----------|----------|-------------------|
| Consent | Explicit, informed consent for data collection | GDPR Art. 7, CCPA |
| Purpose limitation | Collect only data needed for specified purpose | GDPR Art. 5(1)(b) |
| Minimization | Minimize data collected, especially sensitive data | GDPR Art. 5(1)(c) |
| Transparency | Clear privacy notice at collection point | GDPR Art. 13-14 |
| Age verification | Ensure minors are protected | COPPA, GDPR Art. 8 |

### Data Storage & Retention

| Data Type | Retention Period | Rationale |
|-----------|-----------------|-----------|
| Training data | Lifetime of model + 2 years | Audit, retraining, reproduction |
| Evaluation data | 3 years | Benchmarking, regression testing |
| Production inputs | 30-90 days | Debugging, monitoring |
| Production outputs | 90 days-1 year | Quality analysis, incident investigation |
| User feedback | Duration of user relationship | Continuous improvement |
| Audit logs | 1-3 years | Compliance, legal hold |

### Right to Deletion

When a user requests data deletion:

1. Identify all systems containing user data
2. Remove from active datasets
3. Retrain or fine-tune models if user data was in training set
4. Confirm deletion for user
5. Document the request and resolution

### Data Lineage

Every dataset should track:
- Source of data (how was it collected?)
- Processing steps (what was done to it?)
- Purpose (what was it used for?)
- Access (who used it?)
- Changes (what changed and when?)

### Data Quality

| Dimension | Definition | Monitoring |
|-----------|------------|------------|
| Accuracy | Data correctly represents reality | Sampling and validation |
| Completeness | No missing required fields | Schema validation |
| Consistency | Same values across systems | Cross-system comparison |
| Timeliness | Data is current for its purpose | Age tracking |
| Representativeness | Data reflects target population | Demographic analysis |

## Training Data Governance

### Consent for Training Data

| Data Source | Consent Required | Method |
|-------------|-----------------|--------|
| User interactions | Yes | Terms of service + explicit opt-in |
| Public datasets | Varies | License compliance, terms of use |
| Synthetic data | Internal approval | Quality review, bias check |
| Third-party data | Yes | Data processing agreement |
| Customer data | Yes | Customer consent, data use agreement |

### Data Quality Gates for Training

```
Data Ingestion → Schema Validation → Quality Checks → PII Scan → Consent Check → Approved for Training
```

Each gate must pass before data enters the training pipeline. Failed data is quarantined for review.

## Production Data Governance

### Input Governance
- Log all inputs (with PII redaction for sensitive fields)
- Validate input against allowed schema
- Check for prohibited content
- Rate-limit to prevent data extraction attacks

### Output Governance
- Check outputs for PII leakage
- Monitor for memorization of training data
- Log outputs for incident investigation
- Provide users with access to their data

## Data Protection Impact Assessment (DPIA)

Required under GDPR for high-risk data processing:

| Section | Content |
|---------|---------|
| Description | What data is processed, how, and why |
| Necessity | Why the processing is necessary |
| Risk assessment | Risks to individual rights and freedoms |
| Mitigation | Measures to address identified risks |
| Consultation | Input from data protection officer |

## Common Data Governance Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| Shadow data | Data used without governance | Data discovery, inventory automation |
| Consent gaps | Regulatory violation | Consent management platform |
| Retention overruns | Legal exposure | Automated retention enforcement |
| Lineage gaps | Cannot reproduce results | Automated lineage tracking |
| Quality blind spots | Model degradation | Data quality monitoring |

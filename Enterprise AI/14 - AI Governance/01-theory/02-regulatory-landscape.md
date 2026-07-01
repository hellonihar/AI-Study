# Regulatory Landscape for AI

## Overview

AI regulation is rapidly evolving globally. Organizations deploying AI must navigate a complex web of existing and emerging regulations.

## Major AI Regulations

### EU AI Act

The world's first comprehensive AI regulation, taking a risk-based approach:

| Risk Tier | Examples | Requirements |
|-----------|----------|-------------|
| Unacceptable | Social scoring, real-time biometric surveillance | Prohibited |
| High | Employment, credit, critical infrastructure, law enforcement | Conformity assessment, risk management, human oversight, transparency |
| Limited | Chatbots, emotion recognition, deepfakes | Transparency obligations |
| Minimal | AI-enabled video games, spam filters | No obligations (voluntary codes of conduct) |

Key deadlines:
- 2025: Prohibited practices take effect
- 2026: Most obligations apply
- 2027: High-risk system requirements for specific categories

Penalties: Up to 35 million euros or 7% of global annual revenue.

### US Executive Order on AI (2023)

| Area | Requirement |
|------|-------------|
| Safety | Developers of powerful AI must share safety test results with government |
| Privacy | Support privacy-preserving techniques, evaluate commercial data use |
| Equity | Guidance to prevent AI-driven discrimination |
| Civil rights | Address algorithmic discrimination, study AI's impact on criminal justice |
| Innovation | Expand AI research grants, streamline immigration for AI talent |

### GDPR (General Data Protection Regulation)

Applies to AI systems that process personal data:

| Requirement | AI-Specific Implication |
|-------------|------------------------|
| Right to explanation | Users can request explanation of automated decisions |
| Data minimization | Only collect data necessary for the specific purpose |
| Right to deletion | Training data subject to deletion requests |
| Consent | Explicit consent required for data collection |
| Data protection impact assessment | Required for high-risk processing |
| Automated decision-making | Article 22 restricts solely automated decisions with legal effects |

### Sector-Specific Regulations

| Sector | Regulation | AI Implications |
|--------|-----------|----------------|
| Healthcare | HIPAA, GDPR, EU MDR | Medical AI as a device, patient data protection |
| Finance | SOX, Basel III, EC AI Act | Credit scoring models, algorithmic trading |
| Employment | EEOC, NYC Local Law 144 | Bias in hiring tools, adverse impact analysis |
| Insurance | State regulations | Pricing models must be explainable |
| Criminal justice | Various | Risk assessment tool validation |

## Cross-Jurisdictional Compliance

Operating across jurisdictions requires:

1. **Mapping**: Identify all applicable regulations for each deployment location
2. **Common baseline**: Implement highest common denominator requirements
3. **Layered controls**: Meet specific requirements per jurisdiction
4. **Documentation**: Maintain evidence for each regulatory framework
5. **Monitoring**: Track regulatory changes across all jurisdictions

## Compliance Framework

### Building a Compliance Program

1. **Inventory**: Catalog all AI systems in production or development
2. **Classify**: Risk-tier each system
3. **Map**: Map regulations to each tier
4. **Control**: Implement controls for each requirement
5. **Evidence**: Collect and store compliance evidence
6. **Audit**: Regular internal and external audits
7. **Remediate**: Address findings and update controls

### Evidence Collection

| Evidence Type | Examples | Retention |
|---------------|----------|-----------|
| Design documentation | Model cards, system cards, risk assessments | Lifetime of system + 2 years |
| Training records | Dataset provenance, training configs | Lifetime of model |
| Test results | Bias audits, safety evals, performance tests | 3 years |
| Deployment records | Approvals, change logs, rollback records | 3 years |
| Monitoring data | Production metrics, incident reports | 1 year |
| User-facing notices | Transparency notices, consent forms | Lifetime of deployment |

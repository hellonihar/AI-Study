# Compliance & Safety Standards for AI

## Regulatory Landscape

### EU AI Act

The first comprehensive AI regulation, categorized by risk level:

| Risk Level | Examples | Requirements |
|------------|----------|--------------|
| Unacceptable | Social scoring, real-time biometric surveillance | Banned |
| High | CV screening, credit scoring, medical devices | Conformity assessment, risk management, human oversight |
| Limited | Chatbots, emotion recognition | Transparency obligations |
| Minimal | AI-enabled video games, spam filters | No obligations |

**For LLM-based systems:**
- General-purpose AI models must comply with transparency requirements
- Systemic risk models (10^25+ FLOPs training compute) have additional obligations
- Fines up to 7% of global annual revenue or €35M

### US Executive Order on AI (2023)

Key requirements for AI systems:
- Developers of powerful models must share safety test results with the government
- Development of standards for AI safety and security
- Protection of privacy through federal support for privacy-preserving techniques
- Addressing algorithmic discrimination

### NIST AI Risk Management Framework

| Function | Description |
|----------|-------------|
| Govern | Culture, processes, and accountability |
| Map | Understand context and risks |
| Measure | Assess and analyze risks |
| Manage | Prioritize and respond to risks |

### Other Regulations

| Regulation | Region | Key Focus |
|------------|--------|-----------|
| GDPR | EU | Data protection, right to explanation |
| CCPA/CPRA | California | Consumer privacy, opt-out of automated decisions |
| HIPAA | US Healthcare | Protected health information |
| PIPEDA | Canada | Consent, transparency |
| LGPD | Brazil | Similar to GDPR |

## Safety Standards

### Model Cards

A standardized document describing model behavior:

| Section | Content |
|---------|---------|
| Model details | Name, version, architecture, training data |
| Intended use | Target users, use cases, out-of-scope uses |
| Factors | Demographic groups, environmental contexts |
| Metrics | Performance across groups, fairness metrics |
| Evaluation data | Datasets used for evaluation |
| Ethical considerations | Potential harms, mitigation strategies |
| Caveats | Known limitations, recommended usage |

### System Cards

Similar to model cards but for the full system (model + guardrails + infrastructure):

| Section | Content |
|---------|---------|
| System architecture | Components and data flow |
| Safety mechanisms | Guardrails, filters, human oversight |
| Known vulnerabilities | Documented from red teaming |
| Monitoring | Metrics tracked, alerting thresholds |
| Incident response | Process for handling failures |
| Version history | Changes to system over time |

## Safety Evaluation Requirements

### Pre-deployment Evaluation

| Check | Method | Pass Criteria |
|-------|--------|--------------|
| Bias evaluation | Test across demographic groups | Max 5% performance gap |
| Safety benchmark | TruthfulQA, BBQ, Toxigen | Score > 90th percentile |
| Red team results | Automated + manual | No critical findings |
| Guardrail effectiveness | Attack success rate | ASR < 1% |

### Ongoing Monitoring

| Monitoring | Frequency | Action on Threshold Breach |
|------------|-----------|---------------------------|
| User satisfaction | Daily | Investigate if drop > 10% |
| Content flags | Real-time | Escalate if > 0.1% of responses flagged |
| Bias drift | Weekly | Retrain if demographic skew emerges |
| New attack patterns | Continuous | Update guardrails within 48h |

## Documentation Requirements

Maintain for each production AI system:

1. **Model card** (updated per version)
2. **System card** (updated per significant change)
3. **Data card** (training data provenance and characteristics)
4. **Evaluation report** (pre-deployment and ongoing)
5. **Red team report** (latest engagement)
6. **Incident log** (all safety incidents)
7. **Change log** (model and system changes)

## Audit Trail Requirements

| Event | Data to Log | Retention |
|-------|-------------|-----------|
| User input | Hashed input, user ID, timestamp | 90 days |
| Model output | Hashed output, model version | 90 days |
| Guardrail decision | Scores, action, version | 1 year |
| Human review | Reviewer ID, decision, timestamp | 3 years |
| Training data | Source, curation steps, version | Lifetime of model |
| Model deployment | Version, target, approver | 3 years |

## Third-Party Audits

Annual third-party audit should cover:
1. **Model evaluation**: Bias, safety, robustness
2. **Security assessment**: Infrastructure, API, access controls
3. **Privacy review**: Data handling, PII protection
4. **Compliance check**: Regulatory requirements met
5. **Red team engagement**: Independent vulnerability assessment

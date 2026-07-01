# Ethics & Bias Best Practices

## Ethical AI Principles

### Core Principles to Enforce

| Principle | Definition | Implementation |
|-----------|------------|----------------|
| Fairness | AI should not discriminate or create unfair outcomes | Bias auditing, fairness constraints |
| Transparency | AI decisions should be explainable | Model cards, explainability tools |
| Accountability | Someone is responsible for AI outcomes | Named owners, audit trails |
| Privacy | Personal data must be protected | Data governance, PII controls |
| Beneficence | AI should benefit people | Stakeholder impact assessments |
| Non-maleficence | AI should not cause harm | Safety testing, guardrails |
| Human autonomy | Humans should remain in control | Human oversight, opt-outs |

### Embedding Ethics in Development

```
Requirements → Design → Development → Testing → Deployment → Monitoring
     |           |           |           |            |            |
 Ethics     Stakeholder   Privacy     Bias        Human       Continuous
 check      mapping       review      audit       oversight    monitoring
```

## Bias Detection and Mitigation

### Pre-Deployment Bias Checks

| Check | Method | Threshold |
|-------|--------|-----------|
| Demographic parity | Compare selection rates across groups | Disparate impact > 0.8 |
| Equal opportunity | Compare true positive rates | Difference < 0.1 |
| Subgroup accuracy | Compare accuracy across groups | Gap < 0.05 |
| Counterfactual fairness | Test with modified attributes | Same prediction |

### Post-Deployment Monitoring

| Metric | Frequency | Alert |
|--------|-----------|-------|
| Prediction distribution by group | Daily | Distribution shift > 3 sigma |
| User satisfaction by group | Weekly | Satisfaction gap > 10% |
| Error rate by group | Daily | Error rate gap > 2x |
| Drift by demographic slice | Weekly | Quality drop > 5% |

### Bias Mitigation Strategies

| Stage | Strategy | Best For |
|-------|----------|----------|
| Pre-processing | Re-weighting, resampling, data augmentation | Imbalanced data |
| In-processing | Adversarial debiasing, fairness constraints | Training stage |
| Post-processing | Threshold adjustment, calibration | Production fixes |

## Stakeholder Impact Assessment

### Required Assessments
- Every T3+ model must have a stakeholder impact assessment
- Assessment must identify affected groups and potential harms
- Mitigation plan must be reviewed and approved
- Assessment must be updated on significant change

### Assessment Components
1. System description and purpose
2. Stakeholder mapping (direct and indirect)
3. Potential benefits and harms per stakeholder
4. Risk severity and likelihood
5. Mitigation measures
6. Residual risk assessment
7. Monitoring plan

## Ethics Review Process

### Triggers for Ethics Review
- New T3+ model deployment
- Model applied to new use case
- Performance disparity across groups detected
- External criticism or regulatory attention
- Significant capability change

### Review Timeline
| Phase | Duration | Participants |
|-------|----------|-------------|
| Prepare assessment | 1-2 weeks | Development team |
| Ethics panel review | 1 week | Ethics panel members |
| Decision and documentation | 2-3 days | Panel chair |
| Remediation (if needed) | 1-4 weeks | Development team |

## Organizational Ethics

### Ethics Board Composition
- Ethics/Responsible AI lead (chair)
- Legal representative
- Technical representative
- Business stakeholder
- External advisor (for high-risk reviews)

### Ethics Training
- Annual ethics training for all AI developers
- Specialized training for ethics board members
- Case study-based learning from actual incidents
- Ethics consideration in developer onboarding

## Common Ethics Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| Ethics washing | Policies without practice | Enforceable requirements and audits |
| Single-point bias check | Missing drift over time | Continuous bias monitoring |
| Ignoring indirect stakeholders | Unforeseen harms | Comprehensive stakeholder mapping |
| No ethics escalation path | Issues buried | Clear whistleblower process |
| Treating ethics as PR | Eroded trust | Genuine commitment from leadership |

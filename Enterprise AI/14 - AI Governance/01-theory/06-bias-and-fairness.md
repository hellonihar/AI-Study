# Bias Auditing & Fairness

## Understanding AI Bias

AI bias occurs when a model systematically produces outcomes that are unfair to certain groups or individuals. Bias can enter at any stage of the AI lifecycle.

### Sources of Bias

| Stage | Source | Example |
|-------|--------|---------|
| Problem definition | Framing bias | Defining success in a way that disadvantages certain groups |
| Data collection | Sampling bias | Under-representation of minority groups in training data |
| Data preparation | Label bias | Annotator bias in ground truth labels |
| Feature engineering | Measurement bias | Proxy features that correlate with protected attributes |
| Model training | Algorithmic bias | Model amplifies existing data skew |
| Deployment | Deployment bias | Model used on population different from training data |
| Monitoring | Feedback loop bias | User behavior changes based on model outputs |

## Fairness Metrics

### Group Fairness Metrics

| Metric | Definition | When to Use |
|--------|------------|-------------|
| Demographic parity | Equal positive rate across groups | When selection should be balanced |
| Equal opportunity | Equal true positive rate across groups | When false negatives are costly |
| Equalized odds | Equal TPR and FPR across groups | When both error types matter |
| Predictive parity | Equal positive predictive value across groups | When precision consistency is needed |

### Individual Fairness Metrics

| Metric | Definition |
|--------|------------|
| Consistency | Similar individuals receive similar predictions |
| Counterfactual fairness | Prediction would be same if protected attribute changed |
| Individual fairness | Distance in outcome space <= distance in feature space |

## Bias Detection Techniques

### Pre-Deployment Detection

| Method | Description | Effort |
|--------|-------------|--------|
| Disparate impact analysis | Compare selection rates across groups | Low |
| Subgroup performance analysis | Evaluate metrics per demographic slice | Medium |
| Adversarial debiasing | Train adversary to detect protected attributes | High |
| Counterfactual evaluation | Test with modified protected attributes | Medium |

### Post-Deployment Monitoring

| Method | Frequency | Signal |
|--------|-----------|--------|
| Prediction distribution monitoring | Daily | Distribution shift by group |
| User outcome monitoring | Daily | Different treatment by group |
| Feedback monitoring | Continuous | Differential satisfaction by group |
| Drift detection per slice | Weekly | Quality degradation for specific groups |

## Fairness Thresholds

| Risk Tier | Required Metrics | Threshold |
|-----------|-----------------|-----------|
| Critical | Demographic parity, equal opportunity, equalized odds | Disparate impact > 0.8 |
| High | Demographic parity, equal opportunity | Disparate impact > 0.8 |
| Medium | Demographic parity | Disparate impact > 0.7 |
| Low | Documentation only | N/A |

## Bias Mitigation Strategies

### Pre-Processing (Data Level)

| Strategy | Description | Best For |
|----------|-------------|----------|
| Re-weighting | Assign weights to balance group representation | Imbalanced datasets |
| Resampling | Over-sample underrepresented groups | Small datasets |
| Data augmentation | Generate synthetic data for gaps | Scarce groups |
| Bias-aware labeling | Detect and correct label bias | Annotation quality issues |

### In-Processing (Training Level)

| Strategy | Description | Trade-off |
|----------|-------------|-----------|
| Adversarial debiasing | Train to remove protected attribute information | May reduce overall accuracy |
| Fairness constraints | Add fairness regularization to loss function | Requires tuning lambda |
| Equal opportunity training | Calibrate for equal TPR | Complexity |

### Post-Processing (Output Level)

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| Threshold adjustment | Different thresholds per group | When groups have different base rates |
| Output calibration | Adjust scores to equalize rates | Production systems with fixed thresholds |
| Rejection option | Withhold predictions below confidence | High-stakes decisions |

## Fairness Testing in CI/CD

```
Commit → Unit Tests → Fairness Tests → Integration → Deploy
                         ↓
                   Disparate impact check
                   Subgroup performance
                   Counterfactual test
```

Fairness test failures block deployment for Tier 3+ models.

## Audit Trail for Fairness

Every bias audit should record:
- Date and version of model
- Test dataset used (with provenance)
- Metrics computed and results
- Thresholds applied and rationale
- Mitigation actions taken
- Reviewer and approval

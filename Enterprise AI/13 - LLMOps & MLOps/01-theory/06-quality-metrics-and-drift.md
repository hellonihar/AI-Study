# Quality Metrics & Drift Detection

## Quality Metrics for LLMs

### Automated Quality Metrics

| Metric | Description | Collection |
|--------|-------------|------------|
| Response relevance | Does output address the query? | LLM-as-judge on sample |
| Faithfulness | Is output grounded in provided context? | Factual consistency check |
| Hallucination rate | % of responses containing fabricated info | Automated fact-checking |
| Task completion | Did the model accomplish the requested task? | Rule-based or LLM judge |
| Safety score | Free of toxic/harmful content | Content safety classifier |
| Format compliance | Output matches expected structure | Schema validation |
| Conciseness | Appropriate length for query | Token count vs expectation |

### User-Facing Metrics

| Metric | Collection | Target |
|--------|------------|--------|
| Thumbs up/down | Inline feedback | > 90% positive |
| Rating (1–5) | Post-interaction survey | > 4.0 average |
| Follow-up rate | User asks clarifying question | < 20% of interactions |
| Copy/paste rate | User copies output | > 30% (indicates value) |
| Retention | User returns within 7 days | > 40% |

## Drift Detection

### Types of Drift

| Drift Type | Description | Detection Method |
|------------|-------------|-----------------|
| Input drift | User queries change over time | Embedding distribution comparison |
| Output drift | Model output characteristics change | Quality metric trend analysis |
| Concept drift | What "good" means changes | User satisfaction trend |
| Data drift | Retrieved documents change | Embedding comparison on corpus |
| Model drift | Model behavior changes | Same eval set, different scores |

### Detection Methods

#### Statistical Drift Detection
Compare current metrics against baseline using:

| Method | Use Case | Sensitivity |
|--------|----------|-------------|
| Moving average | Gradual drift over hours/days | Low |
| Page-Hinkley test | Sudden change detection | Medium |
| KS test | Distribution comparison | High |
| Z-score | Outlier detection on metrics | Low |
| Embedding similarity | Input/output distribution shift | Medium |

#### Embedding-Based Drift

```python
reference_embeddings = embed(reference_inputs)
current_embeddings = embed(current_inputs)

# Compare distributions
reference_mean = np.mean(reference_embeddings, axis=0)
current_mean = np.mean(current_embeddings, axis=0)
drift_score = np.linalg.norm(reference_mean - current_mean)

if drift_score > threshold:
    alert("Input distribution drift detected")
```

### Alerting on Drift

| Drift Level | Action | Response Time |
|-------------|--------|---------------|
| Warning (1–2σ) | Monitor, investigate root cause | 24h |
| Alert (2–3σ) | Notify ML team, prepare rollback | 4h |
| Critical (> 3σ) | Auto-rollback or block traffic | Immediate |

## Quality Baselines

### Establishing Baselines

1. Run evaluation on current production model
2. Record metrics across all dimensions
3. Compute 95% confidence intervals
4. Set thresholds as baseline ± margin

Example baseline:

```yaml
quality_baseline:
  model: gpt-4o-mini-v2
  date: 2026-07-01
  metrics:
    relevance: 0.92 +- 0.02
    faithfulness: 0.95 +- 0.01
    hallucination_rate: 0.02 +- 0.005
    toxicity: 0.001 +- 0.0005
    user_satisfaction: 0.88 +- 0.03
```

## Quality Degradation Response

When quality metrics drop below thresholds:

1. **Detect**: Alert fires
2. **Triage**: Is this a real degradation or metric noise?
3. **Diagnose**: Which user segment, which model, which prompt?
4. **Contain**: Rollback model or prompt if needed
5. **Investigate**: Root cause analysis
6. **Remediate**: Fix issue, update tests, redeploy
7. **Monitor**: Verify metrics return to baseline

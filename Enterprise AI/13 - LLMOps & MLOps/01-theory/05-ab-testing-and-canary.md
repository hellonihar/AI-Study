# A/B Testing & Canary Deployments

## A/B Testing for LLMs

A/B testing compares two versions of a model, prompt, or configuration on live traffic to determine which performs better.

### What to A/B Test

| Variant | Example |
|---------|---------|
| Model | GPT-4 vs GPT-4o-mini |
| Prompt | System prompt v1 vs v2 |
| Temperature | 0.3 vs 0.7 |
| Context window | 4K vs 8K tokens |
| Guardrail | Current guardrail vs updated |
| Fine-tuned model | Base vs fine-tuned |

### Experiment Design

#### Hypothesis
```
H0: Model B has the same quality as Model A (no difference)
H1: Model B has higher quality than Model A
```

#### Metrics

| Metric Type | Primary | Secondary |
|-------------|---------|-----------|
| Quality | LLM-as-judge score | User satisfaction, task accuracy |
| Performance | p95 latency | p50 latency, throughput |
| Cost | Cost per request | Token usage |
| Safety | Guardrail block rate | Toxicity score |

#### Sample Size

| Expected Effect Size | Users Needed (per variant) | Duration |
|---------------------|---------------------------|----------|
| 5% improvement | ~1,500 | 2–3 days |
| 2% improvement | ~10,000 | 1–2 weeks |
| 1% improvement | ~40,000 | 2–4 weeks |

### Traffic Splitting

```
User → Router (hash-based) → Variant A (50%)
                           → Variant B (50%)
```

Use consistent hashing (user ID or session ID) so the same user always sees the same variant within an experiment.

## Canary Deployments

### Canary Release Process

```
Phase 0: Internal testing (ML team, 0.1% traffic)
Phase 1: 5% traffic, 24h monitoring
Phase 2: 25% traffic, 24h monitoring
Phase 3: 50% traffic, 12h monitoring
Phase 4: 100% traffic
```

### Canary Success Criteria

| Metric | Success | Rollback |
|--------|---------|----------|
| Error rate | < baseline + 0.5% | > baseline + 1% |
| p95 latency | < baseline + 20% | > baseline + 50% |
| Quality score | > baseline - 2% | < baseline - 5% |
| Cost per request | < baseline + 10% | > baseline + 30% |
| User satisfaction | > baseline - 2% | < baseline - 5% |

### Automated Rollback

```python
def should_rollback(canary_metrics, baseline_metrics):
    if canary_metrics.error_rate > baseline_metrics.error_rate + 0.01:
        return True, "error_rate_exceeded"
    if canary_metrics.p95_latency > baseline_metrics.p95_latency * 1.5:
        return True, "latency_exceeded"
    if canary_metrics.quality_score < baseline_metrics.quality_score - 0.05:
        return True, "quality_drop"
    return False, ""
```

## Multi-Variant Testing

For testing more than 2 variants simultaneously:

| Variant | Traffic | Purpose |
|---------|---------|---------|
| Control (current) | 50% | Baseline |
| Variant A (new prompt) | 25% | Test prompt change |
| Variant B (new model) | 25% | Test model change |

## Statistical Rigor

| Concept | Practice |
|---------|----------|
| Randomization | Hash-based consistent assignment |
| Sample size | Calculate before experiment starts |
| Duration | Run for at least one full business cycle |
| Multiple comparisons | Bonferroni correction for multiple metrics |
| Stopping rules | Pre-register stopping criteria (don't peek) |
| Significance | p < 0.05 (or stricter for safety metrics) |

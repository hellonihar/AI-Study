# Evaluation & Regression Testing Best Practices

## Before Every Training Run

1. Define success criteria: What metrics must improve? What must NOT degrade?
2. Lock baseline: Record current production model metrics
3. Reserve test set: Never use test data for training decisions
4. Set thresholds: Define automatic pass/fail for each metric category

## Three-Axis Evaluation

Always evaluate on all three axes before deployment:

| Axis | What | Minimum Threshold |
|------|------|------------------|
| Task Performance | Primary metrics | +2% improvement or within 1% of target |
| General Capability | Regression benchmarks | No single benchmark drops >3% |
| Safety & Robustness | Safety suite | All scores >90% |

## Regression Test Suite

Maintain a dedicated regression test set of 500–2000 examples covering:
- Core task performance (40% of test set)
- Previously fixed failure modes (20%)
- Edge cases and corner cases (20%)
- Adversarial inputs (10%)
- General capability probes (10%)

## Statistical Rigor

- Report 95% confidence intervals for all metrics
- Use bootstrap resampling for confidence intervals
- Minimum 500 examples per metric for reliable results
- Compare against baseline using statistical significance tests (McNemar's test for classification)

## Catastrophic Forgetting Detection

Run a benchmark suite covering: reasoning, knowledge, coding, math, safety.

Flag if:
- Any single benchmark drops >5% → investigate
- Two or more benchmarks drop >3% → automatic rejection
- Safety score drops below 85% → automatic rejection

## Evaluation Automation

```yaml
# Every training run triggers:
1. Run task-specific evaluation
2. Run capability regression suite
3. Run safety evaluation
4. Generate comparison report vs previous model
5. If all pass → stage for deployment
6. If any fail → notify team, block deployment
```

## A/B Testing in Production

| Phase | Traffic | Duration | Success Criteria |
|-------|---------|----------|-----------------|
| Canary | 1–5% | 24h | Error rate < baseline, user feedback stable |
| Expanded canary | 10–25% | 48h | All metrics stable, no regression |
| Gradual rollout | 25→50→100% | Monitoring per step | Automatic rollback on any alarm |

## Rollback Criteria

Automatically rollback if:
- Error rate increases by >0.5% absolute
- P95 latency increases by >20%
- User negative feedback increases by >2x
- Business metric (if tracked) decreases by >5%

# Evaluation & Quality Best Practices

## Evaluation Strategy

### Multi-Layer Evaluation
No single evaluation method is sufficient. Layer multiple approaches:

| Layer | Method | Frequency | Cost |
|-------|--------|-----------|------|
| Unit tests | Expected outputs for known inputs | Per commit | Free |
| Golden set | Curated test set with known answers | Per deployment | Low |
| LLM-as-judge | Strong model rates output quality | Per deployment | Medium |
| Human eval | Expert raters on sampled outputs | Per release | High |
| Online eval | A/B testing on live traffic | Continuous | Medium |

### Test Set Management

| Test Set | Content | Size | Update Frequency |
|----------|---------|------|-----------------|
| Golden set | Core capabilities (QA, summarization, code) | 500-2000 | Quarterly |
| Regression set | Known failure modes from incidents | 100-500 | Per incident |
| Safety set | Harmful inputs, edge cases | 500-1000 | Monthly |
| Production sample | Representative live traffic | 1000-5000 | Weekly |

## Quality Metrics

### Mandatory Quality Gates
Every deployment must pass these gates before reaching production:

| Gate | Metric | Threshold |
|------|--------|-----------|
| Relevance | Response addresses query | > 0.75 |
| Faithfulness | Facts grounded in context | > 0.80 |
| Safety | No toxic/harmful content | > 0.95 |
| Format compliance | Output matches schema | 100% |

### Automated Quality Scoring
Use LLM-as-judge with structured rubrics:

```json
{
  "rubric": {
    "relevance": "Does the response directly address the user's query?",
    "faithfulness": "Are all claims supported by the provided context?",
    "conciseness": "Is the response appropriately brief?",
    "safety": "Is the response free of harmful content?"
  },
  "scale": "1-5",
  "threshold": 3.5
}
```

### Regression Detection
Compare every new model/prompt against baseline:

- Run identical test set on both versions
- Flag any metric drop > 5% as regression
- Require ML team sign-off before deploying with regressions
- Add failing cases to regression test suite

## Best Practices by Phase

### Offline Evaluation (Pre-Deployment)
- Run golden set on every commit
- Run safety set on every model change
- Test edge cases explicitly (empty input, very long input, adversarial)
- Compare against baseline and report delta

### Online Evaluation (In-Production)
- Monitor quality metrics on sampled traffic
- Track user feedback (thumbs up/down, ratings)
- Detect quality drift daily
- Alert on any metric dropping below 3-sigma from baseline

### Incident-Driven Evaluation
- Add every incident input/output to regression set
- Verify fix resolves the specific case
- Run full regression to check for side effects
- Update monitoring thresholds if incident was missed by alerts

## Evaluation Infrastructure

### Pipeline Design
```
Trigger (commit/schedule)
  -> Fetch test set from registry
  -> Run eval in parallel across test cases
  -> Compute aggregate metrics
  -> Compare against baseline
  -> Generate report with pass/fail per dimension
  -> Gate deployment on all thresholds met
```

### Required Tooling
- Test set registry (versioned, immutable)
- Evaluation runner (parallel execution, caching)
- Metrics database (store all historical evaluations)
- Reporting dashboard (trend view, regression alerts)
- Baseline comparator (statistical significance testing)

## Common Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| LLM-as-judge bias | Overestimating quality | Use multiple judges, randomize order |
| Stale test sets | Missing new failure modes | Refresh test sets quarterly and per incident |
| Threshold drift | Gradual quality degradation | Fixed baselines, periodic recalibration |
| Only automated eval | Missing nuance | Regular human eval on sampled outputs |
| No regression detection | Silent regressions | Automated comparison against baseline |

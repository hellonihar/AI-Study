# Evaluation Pipelines for LLMs

## The Need for Automated Evaluation

Manual evaluation doesn't scale. A production LLM system needs automated evaluation that runs before every deployment and continuously monitors live traffic.

## Evaluation Types

### Offline Evaluation (Pre-deployment)

| Type | Purpose | Frequency |
|------|---------|-----------|
| Unit eval | Single prompt/task correctness | Per commit |
| Regression eval | Compare against baseline | Per deployment |
| Capability eval | General knowledge retention | Per model change |
| Safety eval | Toxicity, bias, jailbreak resistance | Per model/guardrail change |
| Load eval | Latency, throughput under load | Per infrastructure change |

### Online Evaluation (In-production)

| Type | Purpose | Frequency |
|------|---------|-----------|
| A/B evaluation | Compare model A vs model B | Continuous |
| Drift detection | Monitor quality over time | Continuous |
| User feedback | Satisfaction, corrections | Continuous |
| Cost monitoring | Cost per request trends | Continuous |

## Evaluation Pipeline Architecture

```
Trigger (commit/schedule) → Fetch Baseline → Run Eval Suite → Compare → Decision
                                                                               ↓
                                                                     Pass → Deploy
                                                                     Fail → Notify
```

### Pipeline Components

1. **Trigger**: Git push, schedule, manual
2. **Data fetcher**: Retrieve test sets from registry
3. **Executor**: Run evaluations in parallel
4. **Scorer**: Compute metrics
5. **Comparator**: Compare against baseline
6. **Decision gate**: Pass/fail based on thresholds
7. **Notifier**: Slack, email, PagerDuty

## Evaluation Methods

### LLM-as-Judge

Use a strong LLM to evaluate output quality:

```
System: Rate the following response on a scale of 1-5 for:
- Helpfulness (does it answer the question?)
- Harmlessness (is it safe and appropriate?)
- Honesty (is it accurate and does it acknowledge uncertainty?)

Response: [model output]
Rating: [score]
```

**Pros:** Flexible, no human annotation needed, consistent criteria
**Cons:** LLM bias (position, verbosity), cost, latency

### Task-Specific Metrics

| Task | Metric | Implementation |
|------|--------|---------------|
| Classification | Accuracy, F1 | Exact match or partial match |
| Summarization | ROUGE, BERTScore | n-gram overlap, embedding similarity |
| QA | Exact Match, F1 | Token overlap with answer |
| Code | Pass@k | Execute generated code |
| Translation | BLEU, chrF | n-gram precision |

### Human Evaluation

| Method | Description | Cost | Scale |
|--------|-------------|------|-------|
| Side-by-side | Rate A vs B | Medium | 100s |
| Likert scale | Rate 1–5 | Medium | 100s |
| Best-worst | Pick best, worst | Low | 1000s |
| Correction | Edit output | High | 10s |

## Test Set Management

| Test Set | Purpose | Size | Refresh |
|----------|---------|------|---------|
| Golden set | Core capability regression | 500–2000 | Quarterly |
| Edge cases | Known failure modes | 100–500 | Per incident |
| Safety set | Harmful input detection | 500–1000 | Monthly |
| Production sample | Live traffic reflection | 1000–5000 | Weekly |
| Adversarial | Red team findings | Variable | Per engagement |

## Evaluation as a Gate

| Stage | Gate | Action on Fail |
|-------|------|---------------|
| CI | Unit evals pass | Block merge |
| Staging | Regression evals pass | Block deployment |
| Canary | Quality + safety metrics OK | Auto-rollback |
| Production | Continuous monitoring | Alert and rollback |

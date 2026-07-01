# CI/CD & Deployment Best Practices

## Pipeline Architecture

### Standard CI/CD Pipeline for LLMs

```
Commit -> Lint -> Eval -> Build -> Stage -> Canary -> Production
   |         |        |        |        |         |           |
   |    Prompt      Golden   Package  Integ.    5% traffic  25->50->100%
   |    syntax      set      prompts  tests     24h monitor
   |    secrets     Safety   + config load test auto-rollback
   |    PII check   set
```

### Gate Criteria

| Gate | Checks | Fail Action |
|------|--------|-------------|
| Lint | Prompt syntax, secrets, PII, config schema | Block merge |
| Evaluation | Golden set accuracy >= 0.70, safety >= 0.80 | Block deploy |
| Build | Package creation, artifact signing | Block deploy |
| Stage | Integration tests pass, latency SLA met | Block deploy |
| Canary | Error rate, latency, quality within thresholds | Auto-rollback |
| Production | Continuous monitoring | Alert and manual rollback |

## Prompt Version Control

### Repository Structure
```
prompts/
  feature-name/
    system-prompt-v1.yaml
    templates/
configs/
  model-configs/
  routing-configs/
```

### Prompt Metadata Requirements
Every prompt version must include:
- Version number (semver)
- Author and creation date
- Target model and parameters (temperature, max_tokens)
- Evaluation results compared to baseline
- Change log describing what changed and why

## Deployment Strategies

| Strategy | Risk | Time to Rollback | Best For |
|----------|------|------------------|----------|
| Canary | Low | < 60s (auto) | Model swaps, prompt changes |
| Blue-green | Low | < 30s (DNS) | Infrastructure changes |
| Feature flag | Low | Instant | Gradual feature rollouts |
| Shadow testing | Very low | N/A | First-time model evaluation |

### Canary Release Process

```
Phase 0: Internal (0.1% traffic, ML team)
Phase 1: 5% traffic, 24h monitoring
Phase 2: 25% traffic, 24h monitoring
Phase 3: 50% traffic, 12h monitoring
Phase 4: 100% traffic
```

### Canary Success Criteria
All must be met for promotion:

| Metric | Success Threshold | Auto-Rollback Threshold |
|--------|------------------|------------------------|
| Error rate | < baseline + 0.5% | > baseline + 1% |
| p95 latency | < baseline + 20% | > baseline + 50% |
| Quality score | > baseline - 2% | < baseline - 5% |
| Cost per request | < baseline + 10% | > baseline + 30% |

## Rollback Strategy

| Scenario | Action | Time |
|----------|--------|------|
| Error rate spike | Auto-rollback to previous version | < 60s |
| Latency degradation | Auto-rollback | < 60s |
| Quality regression | Manual rollback after investigation | < 1h |
| Safety incident | Immediate rollback + traffic block | Immediate |

### Rollback Readiness
- Always keep previous production version deployable
- Test rollback procedure regularly (at least quarterly)
- Maintain ability to roll back prompts independently from models
- Document rollback steps in runbook

## CI/CD for Fine-Tuned Models

```
Data change -> Validate -> Train -> Evaluate -> Registry -> Deploy
```
- Validate training data format and quality before training
- Launch training as CI job with GPU resources
- Run full evaluation suite against baseline
- Register in model registry with lineage metadata
- Deploy via same canary process as prompt changes

## Testing Requirements

| Test Type | Frequency | Minimum Coverage |
|-----------|-----------|-----------------|
| Unit tests | Per commit | All known edge cases |
| Golden set | Per deployment | 500+ curated examples |
| Safety set | Per model/guardrail change | 500+ adversarial examples |
| Load test | Per infra change | 2x expected peak traffic |
| Integration test | Per deployment | All critical paths |

## Common Pitfalls

| Pitfall | Impact | Mitigation |
|---------|--------|------------|
| No eval gate | Deploy quality regressions | Mandatory eval gate in pipeline |
| Skipping canary | Full blast radius on failure | Enforce canary for all changes |
| Manual rollback | Slow incident response | Automated rollback on threshold breach |
| No prompt versioning | Cannot trace regressions | Git-based prompt management |
| Stale test sets | Missing new failure modes | Refresh test sets quarterly |

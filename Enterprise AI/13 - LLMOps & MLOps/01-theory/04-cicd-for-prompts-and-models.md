# CI/CD for Prompts and Models

## Why CI/CD for LLMs

Prompts and model configurations are code. They change frequently, have bugs, and need versioning, testing, and controlled rollout — just like application code.

## CI/CD Pipeline Architecture

```
Commit → Lint → Eval → Build → Stage → Canary → Production
```

### Stages

#### 1. Commit & Lint
- Validate prompt template syntax
- Check for hardcoded secrets or PII in prompts
- Validate config schema (temperature, max_tokens, model)
- Run unit tests (expected outputs for known inputs)

#### 2. Evaluation
- Run golden test set
- Run regression test set
- Run safety evaluation
- Compare metrics against baseline
- **Gate**: All metrics within thresholds

#### 3. Build
- Package prompt templates and configs
- Build container image (for model server)
- Tag with version
- Push to artifact registry

#### 4. Stage
- Deploy to staging environment
- Run integration tests (end-to-end with guardrails)
- Load test (2x expected peak traffic)
- **Gate**: Integration tests pass, latency SLA met

#### 5. Canary
- Route 5% of production traffic to new version
- Monitor for 24h minimum
- **Gate**: Error rate, latency, quality metrics stable

#### 6. Production
- Gradual rollout: 25% → 50% → 100%
- Monitor continuously
- Automated rollback on any alarm

## Prompt Version Control

### Repository Structure
```
prompts/
├── chat/
│   ├── system-prompt-v1.yaml
│   ├── system-prompt-v2.yaml
│   └── templates/
│       ├── greeting.hbs
│       └── response.hbs
├── search/
│   ├── query-rewrite-v1.yaml
│   └── summarization-v2.yaml
└── configs/
    ├── model-config-v1.yaml
    └── routing-config-v1.yaml
```

### Prompt Metadata
```yaml
version: 2.1.0
created: 2026-07-01
author: ml-team
model: gpt-4o-mini
temperature: 0.3
max_tokens: 1024
description: Chat system prompt for customer support
evaluation:
  accuracy: 0.94
  safety: 0.99
  latency_p50: 320ms
  baseline: v2.0.0
```

## Deployment Strategies

| Strategy | Risk | Speed | Complexity |
|----------|------|-------|------------|
| Direct deploy | High | Fast | Low |
| Canary | Low | Medium | Medium |
| Blue-green | Low | Fast | Medium |
| Feature flag | Low | Fast | Medium |
| Shadow testing | Very low | Slow | High |

### Canary Deployment for LLMs

```
1. Deploy new model/prompt alongside existing
2. Route 5% of traffic to new version
3. Monitor for 24h:
   - Error rate < baseline + 0.5%
   - Latency < baseline + 20%
   - Quality score > baseline - 2%
4. If stable: increase to 25%, then 50%, then 100%
5. If unstable: auto-rollback to previous version
```

## Rollback Strategy

| Scenario | Rollback Action | Time |
|----------|----------------|------|
| Error rate spike | Auto-rollback to previous version | < 60s |
| Latency degradation | Auto-rollback | < 60s |
| Quality drop | Manual rollback after investigation | < 1h |
| Safety incident | Immediate rollback + block traffic | Immediate |

## CI/CD for Fine-Tuned Models

```
Data Change → Validate → Train → Evaluate → Registry → Deploy
```

Same pipeline but with training step:
- Validate training data format and quality
- Launch training job (PEFT or full FT)
- Run full evaluation suite
- Compare against baseline model
- Register in model registry
- Deploy via same canary process

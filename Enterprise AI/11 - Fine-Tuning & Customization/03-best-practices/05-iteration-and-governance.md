# Iteration & Governance Best Practices

## Model Lifecycle Governance

| Stage | Requirements | Approvals |
|-------|-------------|-----------|
| Research | Experiment tracking, no production use | Team lead |
| Staging | Full evaluation, integration tests | Tech lead + QA |
| Canary | 1–5% traffic for 24h minimum | Product owner |
| Production | Full rollout after canary passes | Engineering director |
| Deprecated | Traffic migrated, model archived | Documentation |

## Versioning Conventions

```
{base_model}-{method}-{major}.{minor}.{patch}
```

- **Major**: Architecture change, new base model, new training paradigm
- **Minor**: New dataset, hyperparameter changes
- **Patch**: Bug fix, data quality improvement, same dataset

Example: `llama-3-8b-lora-2.1.0`

## Experiment Tracking Requirements

Every training run must log:
1. **Config**: All hyperparameters (LR, batch size, epochs, rank, alpha, target modules)
2. **Data**: Dataset version, size, class distribution, date range
3. **Metrics**: Training loss, validation loss, task metrics, benchmark scores, safety scores
4. **System**: GPU hours, peak memory, throughput, total cost
5. **Environment**: Base model version, framework versions (torch, transformers, peft)
6. **Artifacts**: Checkpoint path, adapter weights, merged model path, eval reports

## Continuous Improvement Process

### Weekly Cadence
- Review user feedback from production (sampled, not exhaustive)
- Identify top 3 failure modes
- Collect 50–100 new examples addressing each failure mode
- Retrain and evaluate

### Monthly Cadence
- Full regression suite on production data distribution
- Benchmark against latest base models (new Llama, Mistral, etc.)
- Review cost-per-request trend
- Update evaluation thresholds if needed

### Quarterly Cadence
- Red team the model (automated + manual)
- Review alignment quality (bias, safety, fairness)
- Assess whether fine-tuning is still the right approach vs RAG or prompting
- Update data collection strategy based on production learnings

## Rollback Protocol

```
1. Alarm fires (error rate, latency, or quality metric)
2. Automated rollback triggers within 60 seconds
3. Traffic reverts to previous production model
4. Incident investigation begins
5. Root cause documented
6. Fix deployed as new version (not a revert of the same version)
```

## Compliance Considerations

- **Data retention**: Training data should not be kept indefinitely. Define retention policy.
- **Consent**: Ensure training data includes only data collected with appropriate consent.
- **Audit trail**: Every model version must have a clear, auditable lineage from training data to deployment.
- **Model cards**: Publish a model card for each production model following the standard template.
- **Bias monitoring**: Regularly evaluate for demographic bias in model outputs.

## Cost Optimization

| Area | Strategy | Potential Savings |
|------|----------|-------------------|
| Training | Start with PEFT before full FT | 4–16x |
| Training | Use spot/preemptible instances | 60–80% |
| Evaluation | Subset sampling for benchmarks | 5–10x |
| Serving | Right-size GPU (don't overprovision) | 30–50% |
| Serving | Quantize to FP8 or INT4 | 2–4x throughput |
| Storage | Archive old checkpoints, retain only production versions | Variable |

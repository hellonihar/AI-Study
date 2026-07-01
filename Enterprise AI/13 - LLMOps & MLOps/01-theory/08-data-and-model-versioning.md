# Data & Model Versioning

## Why Versioning Matters

Without versioning, you cannot:
- Reproduce a model's behavior from a specific date
- Roll back to a known good state
- Audit which data and code produced a given model
- Compare model versions on identical eval sets

## Data Versioning

### What to Version

| Artifact | Versioning Strategy | Storage |
|----------|-------------------|---------|
| Training datasets | Dataset registry (DVC, Hugging Face Datasets) | Object store |
| Evaluation datasets | Immutable, tagged by date | Object store |
| Test sets | Pinned versions for regression testing | Git + object store |
| User feedback logs | Time-partitioned, compressed | Data lake |
| Production logs | Sampled, hashed (PII removed) | Data lake |

### Dataset Metadata

```yaml
dataset: chat-training-v3
created: 2026-07-01
source: production_logs + expert_curation
size: 15000 examples
tokens_total: 12_500_000
avg_tokens_per_example: 833
languages: [en]
quality_checks:
  - dedup_exact: 1200 removed
  - dedup_near: 340 removed
  - pii_scan: 12 flagged, removed
  - human_review: 5% sampled, 98% approved
parent: chat-training-v2
change_log: "Added 5000 new expert-curated examples for edge cases"
```

### Dataset Registry

| Dataset | Version | Date | Size | Quality | Status |
|---------|---------|------|------|---------|--------|
| chat-training | v3 | 2026-07-01 | 15K | 98% | Active |
| chat-training | v2 | 2026-06-01 | 10K | 97% | Deprecated |
| chat-training | v1 | 2026-05-01 | 5K | 95% | Archived |

## Model Versioning

### Model Registry

| Field | Example |
|-------|---------|
| Model ID | llama-3-8b-ft-v2.1.0 |
| Base model | meta-llama/Llama-3-8B |
| Training dataset | chat-training-v3 |
| Method | LoRA (r=8, alpha=16) |
| Training config | learning_rate=2e-4, epochs=3 |
| Evaluation metrics | accuracy=0.94, mmlu=0.68 |
| Artifact path | s3://models/llama-3-8b-ft/v2.1.0/ |
| Status | production |
| Deployment date | 2026-07-02 |
| Owner | ml-team |

### Model Registry API

| Operation | Description |
|-----------|-------------|
| Register | Add new model with metadata |
| Promote | Change stage (staging → production) |
| Deprecate | Mark as no longer active |
| Rollback | Promote previous version back to production |
| Compare | Side-by-side metrics comparison |

## Prompt Versioning

### Prompt Registry

```yaml
prompt: chat-system-v4
version: 4.1.0
created: 2026-07-01
template: |
  You are a helpful assistant. Respond concisely.
  Context: {{context}}
  User: {{query}}
model: gpt-4o-mini
temperature: 0.3
max_tokens: 1024
evaluation:
  relevance: 0.93
  conciseness: 0.88
  baseline: chat-system-v3
```

## Experiment Tracking

Every experiment should track:

| Category | Fields |
|----------|--------|
| Code | Git commit hash, branch |
| Data | Dataset version, preprocessing version |
| Config | Model, hyperparameters, prompt template |
| Metrics | All eval metrics, cost, duration |
| Artifacts | Model weights, eval results, logs |
| Environment | Python version, CUDA version, libraries |

### Experiment Tracking Tools

| Tool | Best For |
|------|----------|
| MLflow | General purpose, self-hosted |
| Weights & Biases | Deep learning, visualization |
| Neptune | Large-scale experiment management |
| Comet | Collaborative experiment tracking |
| DVC | Data + pipeline versioning |

## Lineage Tracking

End-to-end lineage from data to production:

```
Data → Training → Model → Eval → Registry → Deployment → Monitoring
  ↓        ↓         ↓       ↓        ↓           ↓           ↓
 v3      branch     v2.1    run-42    reg-101    prod-v2    dashboard
```

Each artifact knows its parents. Given any model version, you can trace back to:
- The exact training data used
- The code commit that trained it
- The evaluation results
- The deployment history
- The monitoring metrics

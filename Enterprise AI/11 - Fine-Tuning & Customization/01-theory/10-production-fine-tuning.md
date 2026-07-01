# Production Fine-Tuning Pipeline

## End-to-End Architecture

A production fine-tuning pipeline connects data, training, evaluation, and deployment into an automated workflow.

```
Data Sources → Pipeline → Training → Evaluation → Registry → Deployment
                                                      ↓
                                                Monitoring ← Feedback
```

## Pipeline Components

### 1. Data Ingestion

```
Production Logs ─┐
Expert Curated ──┤→ Data Lake → Validation → Transformation → Versioned Dataset
Synthetic ───────┘
Public Datasets ─┘
```

**Storage:** Parquet files in cloud storage (S3, ADLS, GCS) with dataset versioning via DVC or Hugging Face Datasets.

**Validation rules:**
- Schema conformance (required fields, data types)
- Value range checks (token count, length bounds)
- Quality thresholds (min examples, class balance)
- PII scan (no training on sensitive data)

### 2. Training Orchestration

Use a job scheduler or workflow engine:

```yaml
# training_pipeline.yaml
pipeline:
  - prepare_data:
      input: dataset:v3
      output: processed/train, processed/val, processed/test
  - train:
      base_model: llama-3-8b
      method: lora
      config: configs/lora-ft.yaml
      tracking: mlflow
  - evaluate:
      model: train.output
      suites: [task_test, capability_regression, safety]
      baseline: production:current
  - register:
      condition: metrics.task.f1 > 0.92 AND metrics.capability_drop < 2%
      registry: models:v2
  - deploy:
      model: register.output
      target: staging
      wait: 24h
```

### 3. Experiment Tracking

Every training run logs:

| Category | Fields |
|----------|--------|
| Config | base_model, method, lr, batch_size, epochs, rank, alpha, target_modules |
| Data | dataset_id, size, date_range, class_distribution |
| Metrics | train_loss, val_loss, task_metrics, benchmark_scores, safety_scores |
| Artifacts | checkpoint_path, adapter_weights, merged_model_path |
| System | gpu_hours, max_memory, throughput, cost |

**Tools:** MLflow, Weights & Biases, Neptune, Comet.

### 4. Model Registry

A central catalog of all trained models:

```
models/
├── v1.0/             # Initial production model
│   ├── config.yaml
│   ├── metrics.json  # Full eval report
│   └── model/        # Weights
├── v1.1/             # Bug fix (same dataset)
│   └── ...
├── v2.0/             # New dataset
│   └── ...
└── production/       # Symlink to current production model
    └── → v2.0
```

### 5. Deployment Pipeline

#### Staging Deployment
- Deploy to staging endpoint (same infrastructure, isolated traffic)
- Run integration tests against downstream services
- Load test at 2x expected peak traffic
- Validate latency SLAs (TTFT < 200ms, ITL < 30ms)

#### Canary Deployment
- Route 5% of production traffic to new model
- Monitor for 24h minimum:
  - Error rate vs baseline (increase > 0.5% → rollback)
  - Latency degradation (p95 > 1.2x baseline → rollback)
  - User feedback rate (negative feedback > 2x baseline → rollback)
  - Business metrics (conversion, retention — depends on use case)

#### Full Rollout
```
Rollout: 5% → 25% (2h) → 50% (4h) → 100% (if stable)
Rollback: Immediate switch to previous model if any alarm fires
```

### 6. Monitoring & Feedback Loop

#### Real-Time Monitoring
| Metric | Collection | Alert |
|--------|-----------|-------|
| Response quality | LLM-as-judge on 1% sample | Score drop > 5% |
| Hallucination rate | Factual consistency check | Rate > 2% |
| User feedback | Thumbs up/down | Negative rate > 10% |
| Latency | Per-request timing | p95 > 1s |
| Error rate | 4xx/5xx responses | > 1% |
| Input distribution | Embedding drift detector | Drift score > threshold |

#### Feedback Loop Integration

```
Production → Sample 5% → Judge LLM → Score → Score < Threshold → Flag
                                                                    ↓
                                                           Add to training queue
                                                                    ↓
                                                           Next training run includes
```

## Infrastructure as Code

### Kubernetes Deployment

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ft-model-server
spec:
  selector:
    app: ft-model-server
  ports:
    - port: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ft-model-server
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: vllm
          image: vllm/vllm-openai:latest
          args: ["--model", "models/ft-v2", "--port", "8000"]
          resources:
            limits:
              nvidia.com/gpu: 1
```

### CI/CD Integration

```yaml
# .github/workflows/fine-tune.yaml
on:
  push:
    paths:
      - 'training/data/**'
      - 'training/configs/**'
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate data
        run: python scripts/validate_data.py
  train:
    needs: validate
    runs-on: [self-hosted, gpu]
    steps:
      - name: Train model
        run: python scripts/train.py --config configs/prod.yaml
  evaluate:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Evaluate
        run: python scripts/evaluate.py --model ${{ needs.train.outputs.model_path }}
  deploy-staging:
    needs: evaluate
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: python scripts/deploy.py --target staging
  deploy-production:
    needs: deploy-staging
    environment: production
    steps:
      - name: Canary deploy
        run: python scripts/deploy.py --target canary --percentage 5
```

## Cost Management

| Component | Cost Driver | Optimization |
|-----------|------------|--------------|
| Data preparation | Human annotation | Active learning (label uncertain examples only) |
| Training | GPU hours | PEFT, mixed precision, early stopping |
| Evaluation | Inference on eval sets | Subset sampling, parallel eval |
| Storage | Checkpoints, datasets | Keep last 3 checkpoints, archive old datasets |
| Serving | GPU inference | Batch size tuning, quantization, auto-scaling |

## Reliability & Disaster Recovery

| Scenario | Impact | Mitigation |
|----------|--------|------------|
| Training job failure | Delayed release | Automatic retry with checkpoint resume |
| Model quality regression | User-facing degradation | Canary + automated rollback |
| Serving infrastructure failure | Service outage | Multi-AZ deployment, redundant model servers |
| Data corruption | Bad training run | Dataset versioning, validation gates |
| GPU failure | Training interruption | Checkpoint every N steps, node replacement |

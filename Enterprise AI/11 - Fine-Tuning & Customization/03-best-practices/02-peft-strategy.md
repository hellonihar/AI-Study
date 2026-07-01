# PEFT Strategy Best Practices

## Method Selection

| Scenario | Method | Why |
|----------|--------|-----|
| Consumer GPU (8–24GB) | Q-LoRA (4-bit) | Only option for most users |
| Single A100 (40–80GB) | LoRA (FP16) | Best quality/compute trade-off |
| Production with hot-swap | LoRA | Multiple adapters, one base model |
| 100+ tasks to serve | LoRA | Modular, switch without reloading |
| Latency-critical | LoRA (merged) | No inference overhead after merge |
| Very large model (70B+) | Q-LoRA | Memory constraints |
| Edge deployment | LoRA + INT4 quantization | Smallest footprint |

## LoRA Configuration

| Parameter | Recommendation | Notes |
|-----------|---------------|-------|
| Rank (r) | Start at 8, increase if underfitting | r=4 for simple tasks, r=16–32 for complex |
| Alpha | Default = r, increase for stronger adapter | alpha=2r for aggressive adaptation |
| Target modules | Start with Q, V only | Add K, O, FFN for more capacity |
| Dropout | 0.05–0.1 | Higher for small datasets (<500 examples) |

## Training Hyperparameters

| Parameter | LoRA | Q-LoRA |
|-----------|------|--------|
| Learning rate | 2e-4 to 5e-4 | 1e-4 to 3e-4 |
| Batch size | Max that fits GPU | Max that fits GPU |
| Optimizer | AdamW (8-bit) | AdamW (paged) |
| Warmup steps | 10% of total | 10% of total |
| LR schedule | Cosine | Cosine |
| Max grad norm | 1.0 | 1.0 |

## Avoiding Overfitting

| Signal | Action |
|--------|--------|
| Training loss < validation loss significantly | Reduce epochs, increase dropout |
| Validation loss increases | Early stopping |
| High variance across runs | Increase dataset size, reduce LR |
| Perfect training accuracy | Overfitting — simplify model or add regularization |

## Adapter Management

- Store each adapter with a unique ID and metadata (base model, dataset, date, metrics)
- Test adapter compatibility with base model versions
- Benchmark inference speed with N adapters loaded (vLLM recommends < 100–200 per GPU)
- Monitor for adapter interference when serving multiple adapters from one base model

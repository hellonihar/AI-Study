# Parameter-Efficient Fine-Tuning (PEFT)

## Why PEFT

Full fine-tuning is expensive. A 70B model requires ~560GB of GPU memory for training (parameters + gradients + optimizer states + activations). PEFT reduces this to a fraction while retaining most of the performance gain.

| Method | Trainable Parameters | Memory Reduction | Performance vs Full FT |
|--------|---------------------|------------------|----------------------|
| Full FT | 100% | 1x | Baseline |
| LoRA | 0.1–1% | 2–4x | ~95–99% |
| Q-LoRA | 0.1–1% | 8–16x | ~93–98% |
| Adapter | 1–3% | 2–3x | ~94–98% |
| Prefix Tuning | 0.01–0.1% | 4–8x | ~90–95% |
| IA3 | 0.01% | 16x | ~93–97% |

## LoRA (Low-Rank Adaptation)

### How It Works

LoRA injects trainable low-rank decomposition matrices into attention layers. Instead of updating the full weight matrix W (d×k), LoRA learns two smaller matrices A (d×r) and B (r×k) where r << min(d, k).

The forward pass becomes:
```
h = Wx + BAx
```

W is frozen. Only A and B are trained.

### Rank Selection

| Rank | Capacity | Memory | Typical Use |
|------|----------|--------|-------------|
| r=1 | Minimal | Lowest | Simple classification |
| r=8 | Good | Low | General purpose |
| r=16 | Better | Low | Complex tasks |
| r=32 | High | Medium | Very complex tasks |
| r=64 | Maximum | Medium | Multi-task |

Rule of thumb: start with r=8, increase if underfitting.

### Target Modules

For transformer models, LoRA is typically applied to:
- Query and Value projection matrices (Q, V) — most effective for adaptation
- All attention projections (Q, K, V, O) — more capacity
- Feed-forward layers (up, down, gate) — for style/task adaptation

### Alpha Scaling

The LoRA update is scaled by alpha/r. A higher alpha gives the adapter more influence:
- alpha = r: balanced
- alpha = 2r: stronger adapter influence
- alpha = 0.5r: weaker adapter influence

## Q-LoRA

### What Makes It Different

Q-LoRA combines LoRA with 4-bit NormalFloat quantization of the base model. This enables fine-tuning 70B models on a single 48GB GPU.

**Key innovations:**
1. **4-bit NormalFloat**: Information-theoretically optimal quantization for normally distributed weights
2. **Double Quantization**: Quantize the quantization constants themselves (saving ~0.5 bits/param)
3. **Paged Optimizers**: Use CPU memory for optimizer states during gradient checkpointing

### Memory Comparison for 7B Model

| Method | VRAM Required | GPU |
|--------|---------------|-----|
| Full FT (FP16) | ~56 GB | A100 80GB |
| LoRA (FP16) | ~28 GB | A100 40GB |
| Q-LoRA (4-bit) | ~10 GB | RTX 3090/4090 |
| Q-LoRA (4-bit + gradient checkpointing) | ~6 GB | RTX 3080 |

### Throughput Trade-off

Q-LoRA is ~30% slower than LoRA due to quantization/dequantization overhead, but enables fine-tuning on consumer hardware.

## Adapter Layers

Adapters insert small bottleneck layers between transformer blocks:

```
LayerNorm → Down-project(d→h) → Activation → Up-project(h→d) → Residual
```

Where h << d (typically h = d/8 to d/64). Adapters add ~2–3% parameters but introduce sequential computation that slightly slows inference.

## Prefix Tuning

Prepends learnable "virtual tokens" to each layer's key/value projections. The model processes these soft prompts as if they were actual tokens.

**Pros:** Extremely parameter-efficient (0.01–0.1%)
**Cons:** Reduces effective context length, can be less stable than LoRA

## IA3 (Infused Adapter by Inhibiting and Amplifying Activations)

Learns rescaling vectors for key, value, and FFN activations. Adds only 0.01% parameters — the most parameter-efficient PEFT method.

Works well for simple tasks but may underfit on complex reasoning or generation tasks.

## Selecting a PEFT Method

| Scenario | Recommended Method | Rationale |
|----------|-------------------|-----------|
| Consumer GPU (8–24GB) | Q-LoRA (4-bit) | Only viable option |
| Single A100 (40–80GB) | LoRA (FP16) | Better throughput, simpler |
| Multi-GPU setup | LoRA or Full FT | Scale depends on model size |
| Very large model (70B+) | Q-LoRA | Memory constraints |
| Many tasks (100+) | LoRA (separate adapters) | Modular, no interference |
| Production latency-critical | LoRA (mergeable) | No inference overhead |

## Merging LoRA into Base Model

After training, LoRA weights can be merged into the base model:
```
W_merged = W_base + (alpha / r) * B @ A
```

This eliminates inference overhead — the merged model runs at full base model speed with no adapter compute cost. The trade-off is you can't easily swap adapters without re-merging.

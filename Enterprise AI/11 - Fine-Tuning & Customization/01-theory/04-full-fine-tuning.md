# Full Fine-Tuning

## When Full Fine-Tuning is Justified

Full fine-tuning updates every parameter in the model. It is appropriate when:

1. **PEFT methods underperform**: The task requires widespread weight changes that low-rank adapters cannot capture
2. **Domain shift is extreme**: Moving from general text to a highly specialized domain (e.g., legal reasoning, protein sequences, financial modeling)
3. **Architecture changes**: Modifying the model structure (adding new tokens, changing vocabulary, adding output heads)
4. **Maximum performance is required**: Every percentage point of improvement matters
5. **Pre-training from scratch is infeasible**: Full FT is a middle ground between PEFT and full pre-training

## Infrastructure Requirements

### Memory Components

During full fine-tuning, GPU memory holds:
- Model parameters (fp16): 2 bytes × params
- Gradient: 2 bytes × params
- Optimizer states (Adam): 8 bytes × params (2 for momentums + 6 for variances in mixed precision)
- Activations: depends on sequence length and batch size (often the dominant term)

**Total for a 7B model in fp16 with Adam:**
- Parameters: 14 GB
- Gradients: 14 GB
- Optimizer states: 56 GB
- Activations: ~8 GB (batch=1, seq=2048)
- **Total: ~92 GB**

### Hardware Recommendations

| Model Size | Minimum GPUs | Recommended | Interconnect |
|------------|-------------|-------------|--------------|
| 1–3B | 1× A100 40GB | 1× A100 80GB | N/A |
| 7B | 2× A100 40GB | 4× A100 80GB | NVLink |
| 13B | 4× A100 40GB | 8× A100 80GB | NVLink |
| 34B | 8× A100 80GB | 16× A100 80GB | InfiniBand |
| 70B | 16× A100 80GB | 32× A100 80GB | InfiniBand |
| 405B | 64+ A100 80GB | 128× H100 | InfiniBand |

## Memory Optimization Techniques

### Gradient Checkpointing
Trade compute for memory: store only selected activations, recompute the rest during backward pass. Reduces activation memory by ~60–70% at ~20% training slowdown.

### Gradient Accumulation
Aggregate gradients over multiple micro-batches before updating weights. Enables effective large batch sizes on limited hardware.

### Mixed Precision Training (fp16/bf16)
Use 16-bit for forward/backward, 32-bit for optimizer state. bf16 is preferred for stability (same exponent range as fp32).

### DeepSpeed ZeRO Stages
| Stage | What It Shards | Memory Reduction | Communication Overhead |
|-------|---------------|------------------|----------------------|
| ZeRO-1 | Optimizer states | 4x | Minimal |
| ZeRO-2 | Optimizer + gradients | 8x | Moderate |
| ZeRO-3 | Optimizer + gradients + parameters | Multiple of model size | Significant |

### Fully Sharded Data Parallel (FSDP)
PyTorch's native sharding, similar to ZeRO-3. Easier to use than DeepSpeed for PyTorch-native workflows.

## Training Configuration

### Learning Rate
Full fine-tuning typically uses a lower learning rate than pre-training or PEFT:
- Peak LR: 1e-5 to 5e-5
- Warmup: 1–3% of total steps
- Schedule: Cosine decay to 10% of peak

### Batch Size
- Effective batch size: 32–256 examples
- Larger batch for simpler tasks, smaller for complex reasoning
- Gradient accumulation to reach target effective batch

### Epochs
- Typically 1–3 epochs
- Monitor validation loss closely — overfitting happens quickly with full FT
- Use early stopping on validation loss

## Checkpointing Strategy

### What to Save
- Model weights (every N steps, keep last N checkpoints)
- Optimizer state (for training resume)
- Training config and hyperparameters
- Evaluation metrics at each checkpoint

### Checkpoint Frequency
- Every 500–1000 steps for models under 13B
- Every 500 steps for larger models (cost of failure is higher)
- Keep: last 3 checkpoints + best checkpoint by validation loss

### Resuming Training
- Save `trainer_state.json` with step, epoch, random seed state
- Save learning rate scheduler state
- Save data loader state (for deterministic resume)

## Evaluation During Training

Run evaluation every N steps on:
1. **Validation loss**: Primary training signal
2. **Task-specific metrics**: Accuracy, F1, BLEU, ROUGE, etc.
3. **General capability benchmarks**: A small subset of MMLU, HellaSwag, etc.
4. **Log perplexity**: Monitor for loss spikes indicating instability

If validation loss increases while training loss decreases → overfitting. Stop training or increase regularization.

## Post-Training Steps

1. **Merge LoRA if used**: Only for PEFT
2. **Quantize**: FP16 → FP8/INT4 for deployment if acceptable quality
3. **Benchmark**: Full eval suite on test set
4. **A/B test**: Compare against baseline model on real traffic (10% for 24h minimum)
5. **Release**: Tag model version, update model registry, document changes

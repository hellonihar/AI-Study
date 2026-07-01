# Fine-Tuning Overview

## What is Fine-Tuning

Fine-tuning adapts a pre-trained language model to a specific task or domain by continuing training on targeted data. Unlike prompting, which extracts knowledge already present in the model, fine-tuning *modifies* the model's weights to improve performance on a defined distribution.

## When to Fine-Tune vs Alternatives

| Approach | Use Case | Cost | Performance | Maintenance |
|----------|----------|------|-------------|-------------|
| Prompting | General knowledge, simple tasks | Lowest | Baseline | Minimal |
| RAG | Factual recall, dynamic data | Low | High for retrieval | Pipeline maintenance |
| Fine-Tuning | Style, format, domain depth | Medium-High | Highest for domain | Retraining cycles |
| Pre-training | New knowledge from scratch | Prohibitive | Full control | Data pipeline |

### Fine-Tuning is Best When:
- The target task has a specific format or style the base model cannot produce via prompting (e.g., legal document generation, medical report formatting)
- Latency/cost matter — a smaller fine-tuned model can match or beat a larger prompted model
- The domain has specialized vocabulary or reasoning patterns poorly represented in pre-training data
- You need consistent output structure that few-shot prompting cannot guarantee

### Fine-Tuning is NOT Best When:
- The data changes frequently (use RAG instead)
- The task is well-served by prompting with minimal examples
- You lack high-quality training data (at least 500–1000 examples minimum)
- The base model already performs adequately

## Types of Fine-Tuning

### Full Fine-Tuning
All model weights are updated. Requires significant compute (GPU memory for all parameters, optimizer states, gradients). Typical hardware: 4–8 A100 80GB for a 7B model, proportional scaling for larger models.

### Parameter-Efficient Fine-Tuning (PEFT)
Only a small fraction of parameters are trained. Methods include:
- **LoRA**: Low-rank adapters injected into attention layers
- **Q-LoRA**: LoRA + 4-bit quantization for consumer GPUs
- **Adapter**: Small bottleneck layers between transformer blocks
- **Prefix Tuning**: Learnable virtual tokens prepended to input
- **IA3**: Learned rescaling vectors for key/value/FFN activations

### Alignment Tuning
Post-training methods to align model behavior with human preferences:
- **RLHF**: Reinforcement Learning from Human Feedback
- **DPO**: Direct Preference Optimization (no RL needed)
- **ORPO**: Odds Ratio Preference Optimization (combines SFT + alignment)
- **KTO**: Kahneman-Tversky Optimization (reference-free)

## Key Considerations

### Data Quality Over Quantity
1,000 curated examples beat 10,000 noisy ones. Invest in deduplication, format consistency, and expert review before any training run.

### Catastrophic Forgetting
Fine-tuning on a narrow distribution can erase general capabilities. Mitigate with:
- Learning rate scheduling (warmup + cosine decay)
- Replay buffers (mix in general data)
- Elastic Weight Consolidation (EWC)
- Regular evaluation on general benchmarks during training

### Compute Budget
| Model Size | Full FT (A100-hours) | LoRA (A100-hours) | Q-LoRA (consumer GPU) |
|------------|---------------------|--------------------|----------------------|
| 7B | 50–100 | 5–10 | Yes (24GB VRAM) |
| 13B | 100–200 | 10–20 | Yes (48GB VRAM) |
| 70B | 500–1000 | 50–100 | Limited |
| 405B | 5000+ | 500+ | No |

## Evaluation Strategy

Fine-tuning requires three distinct evaluation axes:
1. **Task performance**: Does it do the target task better than before?
2. **General capability**: Did we lose basic reasoning, coding, or general knowledge?
3. **Safety and bias**: Did fine-tuning introduce undesirable behaviors?

Never deploy a fine-tuned model without measuring all three.

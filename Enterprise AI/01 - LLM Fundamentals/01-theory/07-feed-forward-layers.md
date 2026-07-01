# Feed-Forward Layers

FFNs (also called MLP blocks) are where the model stores and transforms parametric knowledge. They account for ~2/3 of total parameters.

## Standard FFN

Three-layer design:

```
FFN(x) = down_proj(activation(up_proj(x)))
```

- `up_proj`: expands from d_model to d_ff (typically 4× d_model)
- `activation`: non-linearity (ReLU, GELU, Swish)
- `down_proj`: projects back to d_model

**Parameters:** 2 × d_model × d_ff (two large matrices)

## Modern FFN Variants

### SwiGLU (used in LLaMA, Mistral, PaLM, Gemma)

```
SwiGLU(x) = (swish(x · W_gate) ⊙ (x · W_up)) · W_down
```

Three weight matrices instead of two (gate, up, down). d_ff is ~2.7× d_model instead of 4×, so total parameters are similar.

**Why better:** The gating mechanism lets the network learn which information to pass through.

### GEGLU (T5, some GPT variants)

Same structure as SwiGLU but uses GELU instead of Swish.

## The Knowledge Storage View

Recent research (Meng et al., 2022; Geva et al., 2020) suggests FFNs act as key-value memories:

- **Up-projection neurons** detect specific patterns (first token of a fact, relation type).
- **Down-projection neurons** produce the resulting token (the object of a fact).

Editing specific FFN neurons can update factual knowledge without retraining.

## Impact on Inference

- FFNs account for ~65% of FLOPs per forward pass.
- Quantization (FP8/INT4) concentrates on FFN weights since they dominate.
- MoE (Mixture of Experts) replaces FFNs with multiple "expert" FFNs routed by a learned gate — each token activates only 2 of 8 experts, keeping FLOPs low while increasing total parameters.

## Best Practices

- **For fine-tuning:** LoRA on FFN layers (especially down_proj) often gives the best quality-to-cost ratio.
- **For knowledge editing:** Target specific FFN neurons identified by causal tracing.
- **For MoE models:** Set routing top-k carefully — k=2 is standard; higher k increases quality but adds latency.

```python
# PyTorch-style SwiGLU
class SwiGLU(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.w_gate = nn.Linear(d_model, d_ff, bias=False)
        self.w_up = nn.Linear(d_model, d_ff, bias=False)
        self.w_down = nn.Linear(d_ff, d_model, bias=False)

    def forward(self, x):
        return self.w_down(F.silu(self.w_gate(x)) * self.w_up(x))
```

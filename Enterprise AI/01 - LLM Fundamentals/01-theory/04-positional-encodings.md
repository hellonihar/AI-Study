# Positional Encodings

Attention is permutation-invariant — without positional information, "cat sat on mat" and "mat sat on cat" produce the same representations. Positional encodings break this symmetry.

## Sinusoidal (Vaswani et al., 2017)

Fixed frequencies, no learned parameters:

```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

- **Absolute** — each position has a unique encoding added to the token embedding.
- **Extrapolates poorly** — models trained on 512 positions don't generalize to 1024.

## RoPE — Rotary Position Embedding (2021)

Applied by multiplying query and key vectors with a rotation matrix that depends on position.

```
q'_i = Rot(θ_i · pos) · q_i
k'_j = Rot(θ_i · pos) · k_j
# Attention score q'_i · k'_j now depends on (pos_j - pos_i)
```

**Used by:** LLaMA, Mistral, GPT-4, Gemma, Qwen.

**Advantages:**
- **Relative position** — attention naturally decays with distance.
- **Extrapolates** — works at longer sequences than trained on (with some quality loss).
- **No extra parameters.**

## ALiBi (2022)

Instead of modifying queries/keys, add a bias to attention scores proportional to distance:

```
Attention(Q, K, V) = softmax(QK^T / √d + m · [-(i-j)]) · V
```

**Used by:** MPT, Bloom.

**Advantages:**
- Simpler than RoPE.
- Strong extrapolation — trained on 2K, can run at 8K+.
- **Disadvantage:** Slightly worse perplexity than RoPE at trained length.

## Impact on Inference

- **RoPE + NTK-aware scaling:** Extends context by adjusting rotation frequencies. LLaMA-3 uses 8K base, scaled to 128K with YaRN.
- **Positional encoding + KV cache:** The KV cache stores key vectors already rotated by RoPE — no re-computation needed for cached tokens.

## Best Practices

- **Prefer RoPE** for new models — it's the most widely adopted and best supported.
- **Use YaRN or NTK-aware scaling** when extending context beyond trained length.
- **Never use sinusoidal** for new models — it's strictly worse than RoPE.

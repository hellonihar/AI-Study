# Attention Mechanism

Attention computes a weighted sum of values where weights depend on the similarity between queries and keys.

## Scaled Dot-Product Attention

```
Attention(Q, K, V) = softmax(Q · K^T / √d_k) · V
```

With shape annotations:
- Q: (batch, heads, seq_len, d_k) — "What am I looking for?"
- K: (batch, heads, seq_len, d_k) — "What do I contain?"
- V: (batch, heads, seq_len, d_v) — "What should I pass along?"
- Output: (batch, heads, seq_len, d_v)

The softmax is row-wise: for each query position, it produces a distribution over key positions.

## Multi-Head Attention

Instead of one attention function, run `h` heads in parallel, then concatenate and project:

```
MHA(x) = Concat(head_1, ..., head_h) · W_O
head_i = Attention(QW_Q_i, KW_K_i, VW_V_i)
```

- **d_k = d_model / h** — typically 64 or 128.
- 32 heads for 4096-dim model → each head is 128-dim.
- Each head can learn a different attention pattern (syntax, semantics, position, etc.).

## Causal (Masked) Attention

In decoder-only models, tokens can't attend to future tokens. Apply a mask:

```
mask[i][j] = 0 if j <= i else -inf
# After softmax, masked positions contribute 0.
```

## Flash Attention (2022)

Standard attention materializes the full (seq_len × seq_len) matrix — O(n²) memory. Flash Attention:

1. Tiles Q, K, V on-chip (SRAM).
2. Computes attention in blocks without writing the full matrix to HBM.
3. Uses online softmax (tiling-safe).
4. **Result:** 2–4× faster, memory reduces from O(n²) to O(n).

## Multi-Query and Grouped Query Attention

- **MHA:** Each head has its own K, V → most parameters, highest quality.
- **MQA (Multi-Query):** All heads share one K, V → less memory, slightly lower quality.
- **GQA (Grouped Query):** Heads share K, V in groups. LLaMA-2-70B uses 8 KV heads, 64 query heads. Pareto-optimal trade-off.

## Best Practices

- **Use GQA** for models > 7B — MQA saves memory but hurts quality. GQA with ratio 1:4 captures most of MHA's quality at MQA's memory cost.
- **Use Flash Attention** in production — it's the single highest-impact optimization for long contexts.
- **Attention sink:** The first token often receives disproportionate attention. Models learn to store "global state" in the first token's value.

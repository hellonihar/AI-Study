# Embeddings

Embeddings are dense vector representations that map discrete token IDs into a continuous semantic space.

## Token Embedding Matrix

Shape: `(vocab_size, d_model)` — a lookup table. Row index = token ID, output = vector of length `d_model`.

```python
# Conceptual
embedding = nn.Embedding(vocab_size=128000, d_model=4096)
# input_ids shape: (batch, seq_len)
# output shape: (batch, seq_len, 4096)
x = embedding(input_ids)
```

## Properties

- **Semantic clustering:** Similar tokens cluster together (e.g., "king" and "queen" have nearby vectors).
- **Linear relationships:** `vector("king") - vector("man") + vector("woman") ≈ vector("queen")`.
- **Random initialization:** Embeddings start random and learn structure during pre-training.
- **Tied embeddings:** Many models share weights between the embedding matrix and the LM head (output projection) to reduce parameter count and improve training.

## Subword Semantics

- Individual tokens like "un" or "est" have less semantic meaning. Meaning emerges from their context across attention layers.
- The embedding layer alone produces no understanding — it's just a lookup. All semantic processing happens in the transformer layers.

## Impact on Model Quality

- **Vocab size affects embedding quality.** Larger vocab means more parameters in the embedding layer (e.g., 128K × 4096 = 500M params), leaving fewer parameters for the transformer layers at the same total parameter count.
- **Special tokens** (EOS, BOS, PAD, role tokens) also get embeddings — they learn special meanings during training.

## Best Practices

- **Don't fine-tune the embedding layer** unless adding new tokens — it's large and rarely needs adjustment.
- **When adding domain tokens,** initialize their embeddings as the mean of semantically related existing tokens.
- **Tied embeddings** save ~20% parameters for small models, but separating them can improve quality for large models (> 30B).

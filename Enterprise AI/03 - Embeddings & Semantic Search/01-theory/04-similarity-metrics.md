# Similarity Metrics

How to measure the distance or similarity between two embedding vectors.

## Common Metrics

| Metric | Range | Formula | When to Use |
|---|---|---|---|
| **Cosine similarity** | [-1, 1] | (A · B) / (||A|| × ||B||) | Default. Works with normalized embeddings. |
| **Dot product** | (-∞, ∞) | Σ(Aᵢ × Bᵢ) | Equivalent to cosine when vectors are normalized. Faster. |
| **Euclidean distance** | [0, ∞) | √(Σ(Aᵢ - Bᵢ)²) | Distance-based clustering, some ANN indexes. |
| **MIP (Max Inner Product)** | (-∞, ∞) | max(A · B) | Recommendation systems (unnormalized). |

## Cosine Similarity

The most widely used metric for text embeddings:

```
cos_sim(A, B) = (A · B) / (|A| × |B|)
             = Σ(Aᵢ × Bᵢ) / (√ΣAᵢ² × √ΣBᵢ²)
```

- **Range:** -1 (opposite) to 1 (identical). 0 = orthogonal (unrelated).
- **Scale-invariant:** Length of vectors doesn't matter — only direction.
- **Default for:** Nearly all text embedding models.

## Normalized vs Unnormalized

Most modern embedding models output **normalized** vectors (unit length, |v| = 1):

```python
# For normalized vectors, cosine = dot product
cos_sim(A, B) = A · B  # because |A| = |B| = 1
```

**Advantages of normalization:**
- Cosine and dot product become equivalent (saves one operation).
- The embedding space is bounded (simplifies ANN index tuning).
- Training converges more stably.

**When NOT to normalize:**
- MIP-based recommenders (unnormalized preserves popularity signal).
- Models specifically trained without normalization (rare, check model card).

## Euclidean Distance

```
euclidean(A, B) = √(Σ(Aᵢ - Bᵢ)²)
```

- **Relationship:** `euclidean² = 2 × (1 - cosine)` for normalized vectors.
- **Preferred by:** Some ANN index types (IVF, some HNSW implementations).
- **Practical difference:** Cosine and Euclidean produce identical rankings for normalized vectors. Use whichever is faster for your index.

## Which Metric Should You Use?

```
Model outputs normalized vectors?
├── Yes → Use dot product (fastest, equivalent to cosine)
│         dot = Σ(Aᵢ × Bᵢ)
│
├── No, but model card says "use cosine" → Normalize then use dot product
│   A_norm = A / |A|
│   similarity = A_norm · B_norm
│
└── No, model is trained unnormalized (e.g., some OpenAI legacy models)
    → Use cosine similarity explicitly
    similarity = (A · B) / (|A| × |B|)
```

## Implementation

```python
import numpy as np

def cosine_similarity(A, B):
    """A, B: (d,) or (n, d) arrays."""
    if A.ndim == 1:
        A = A.reshape(1, -1)
    if B.ndim == 1:
        B = B.reshape(1, -1)
    A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)
    B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)
    return A_norm @ B_norm.T

def dot_product_similarity(A, B):
    """Faster, but only valid for normalized vectors."""
    return A @ B.T if A.ndim == 2 else np.dot(A, B)
```

## Best Practices

- **Know what your model outputs.** Read the model card — does it normalize? Expected metric?
- **Normalize before storing.** Store normalized embeddings — saves computation at query time.
- **Use dot product for speed.** It's one operation vs three (numerator, denominator, division).
- **Test at query time.** 100 cosine calculations should take < 1ms. If slower, batch or use ANN.

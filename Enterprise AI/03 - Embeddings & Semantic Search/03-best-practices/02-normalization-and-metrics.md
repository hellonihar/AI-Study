# Normalization and Metrics

Getting the math right — normalization rules and metric selection.

## The Golden Rule

**Normalize all embeddings before storing.** Always.

```python
def normalize(embeddings):
    norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / norm

# Use dot product for search (equivalent to cosine on normalized vectors)
similarity = normalized_query @ normalized_docs.T
```

## Why Normalize?

| Reason | Impact |
|---|---|
| **Cosine ≈ dot product** | One less operation per comparison |
| **Bounded space** | All vectors lie on unit sphere — simplifies ANN tuning |
| **Consistent score range** | Similarity scores are always in [-1, 1] |
| **Fair comparison** | Long documents don't get higher scores just because their embedding has larger magnitude |

## Metric Selection by ANN Index

| ANN Index | Expected Metric | Notes |
|---|---|---|
| **FAISS IndexFlatIP** | Inner product (dot) | Use normalized vectors → equivalent to cosine |
| **FAISS IndexFlatL2** | L2 (Euclidean) | For normalized vectors: L2² = 2 - 2×cosine → equivalent ranking |
| **HNSW (most impl.)** | Dot product | Normalize → dot = cosine |
| **HNSW with L2** | Euclidean | Works, but same ranking as dot for normalized vectors |
| **IVF** | L2 or IP | Use IP with normalized vectors |

## Practical Rule

```
Model output → Normalize to unit length → Store as FP16/INT8 → Search with dot product
```

This is the simplest, fastest, and most compatible setup.

## Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| **Storing unnormalized, searching with cosine** | Correct but 10–30% slower computing cosine explicitly | Normalize at index time, use dot product at search time |
| **Searching with dot product on unnormalized vectors** | Long documents rank higher | Normalize or use cosine explicitly |
| **Using L2 distance as a similarity metric** | Scores are non-intuitive (lower = more similar) | Convert to similarity: `sim = 1 / (1 + l2_dist)` |
| **Mixing normalized and unnormalized** | Index contains both → unpredictable results | Re-index with consistent normalization |
| **Not checking model's native normalization** | May double-normalize or miss required normalization | Check model card |

## Checking Model Normalization

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
vec = model.encode("test sentence")
print(f"Vector norm: {np.linalg.norm(vec):.6f}")
# If ≈ 1.0, model already normalizes → don't re-normalize
# If ≠ 1.0, normalize before use
```

- **Sentence-transformers models:** Most normalize by default.
- **OpenAI embeddings:** Normalized (L2 = 1.0).
- **BGE models:** Not normalized by default — normalize before use.
- **E5 models:** Not normalized — normalize before use.

## Best Practices

- **Always normalize.** Even if the model says it does — verify. The cost is negligible (microseconds) and prevents a class of hard-to-debug issues.
- **Use dot product for search.** It's the same as cosine for normalized vectors and is the fastest operation supported by ANN indexes.
- **Test with your actual similarity function.** If you compute cosine explicitly in eval but dot product in production, you might miss a normalization bug.
- **Document your normalization in the model metadata.** Embedding vectors without normalization metadata are a debugging liability.

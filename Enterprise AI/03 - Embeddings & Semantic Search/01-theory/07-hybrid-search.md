# Hybrid Search

Combining dense and sparse retrieval to get the best of both worlds.

## Why Hybrid?

| Method | Exact Match | Semantic Match | Handling Rare Terms | Handling Synonyms |
|---|---|---|---|---|
| BM25 (sparse) | ✅ Excellent | ❌ None | ✅ Excellent | ❌ None |
| Dense (embedding) | ❌ Sometimes misses | ✅ Excellent | ❌ Can miss rare terms | ✅ Excellent |
| **Hybrid** | ✅ | ✅ | ✅ | ✅ |

**Production recall gain:** Hybrid typically outperforms the best individual method by 10–20% recall@10.

## Fusion Methods

### Reciprocal Rank Fusion (RRF)

```python
def rrf(results_sparse, results_dense, k=60):
    scores = {}
    for rank, doc_id in enumerate(results_sparse):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    for rank, doc_id in enumerate(results_dense):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
```

- **k=60** is the recommended default (constant from the RRF paper).
- No score normalization needed — operates on ranks only.
- Simple, robust, works well in practice.

### Weighted Score Fusion

```python
def weighted_fusion(dense_scores, sparse_scores, alpha=0.5):
    # Normalize both to [0, 1]
    dense_norm = (dense_scores - min(dense_scores)) / (max(dense_scores) - min(dense_scores) + 1e-9)
    sparse_norm = (sparse_scores - min(sparse_scores)) / (max(sparse_scores) - min(sparse_scores) + 1e-9)
    # Weighted combination
    combined = alpha * dense_norm + (1 - alpha) * sparse_norm
    return combined
```

- **alpha=0.5:** Equal weight.
- **alpha=0.7:** Biased toward dense.
- **alpha=0.3:** Biased toward sparse.

### Learned Weighting

Train a lightweight model (logistic regression, XGBoost) to combine features:

```
features = [dense_score, sparse_score, overlap_ratio, query_length, ...]
→ learned_weight = model.predict(features)
```

- **+2–5% over RRF** with enough training data.
- **Risk:** Overfitting. Start with RRF, move to learned only if you have 10K+ labeled queries.

## Adaptive Hybrid Search

Route queries to the best method dynamically:

```
Query
├── Short (≤3 words), contains named entities → BM25-heavy (alpha=0.3)
├── Long, conversational → Dense-heavy (alpha=0.7)
└── Medium → Balanced (alpha=0.5)
```

**Additional signal:** Query embedding entropy (high entropy = ambiguous → prefer sparse; low entropy = specific → prefer dense).

## Implementation Architecture

```
                   ┌──────────────┐
                   │   Query      │
                   └──────┬───────┘
                          │
              ┌───────────┴───────────┐
              │                       │
        ┌─────┴─────┐          ┌─────┴─────┐
        │   BM25    │          │  Dense    │
        │ (sparse)  │          │ (vector)  │
        └─────┬─────┘          └─────┬─────┘
              │                       │
        ┌─────┴───────┐       ┌──────┴──────┐
        │ Top-100 IDs │       │ Top-100 IDs │
        │ + scores    │       │ + scores    │
        └─────┬───────┘       └──────┬──────┘
              │                       │
              └───────────┬───────────┘
                          │
                    ┌─────┴─────┐
                    │   Fusion  │
                    │ (RRF/Wt.) │
                    └─────┬─────┘
                          │
                    ┌─────┴─────┐
                    │  Re-rank  │
                    │ (cross-   │
                    │  encoder) │
                    └─────┬─────┘
                          │
                    ┌─────┴─────┐
                    │  Top-5    │
                    │  Results  │
                    └───────────┘
```

## Best Practices

- **Make hybrid search your default.** Both BM25 and dense indexing are cheap to maintain. The fusion step adds < 1ms.
- **Use RRF initially** — no parameters to tune, works consistently well.
- **Normalize scores before fusion** if using weighted combination. RRF handles this automatically.
- **Tune alpha on your first 500 labeled queries** — the optimal balance varies by domain (legal favors BM25, conversational favors dense).
- **Log fusion weights per query** — helps debug retrieval failures. If the dense component always dominates, BM25 quality may be poor.

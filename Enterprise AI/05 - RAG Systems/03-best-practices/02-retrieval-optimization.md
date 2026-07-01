# Retrieval Optimization

Tuning the retrieval stage for maximum recall and precision at minimum latency.

## The Retrieval Budget

Retrieval latency is additive across components:

```
Total = query_embed (5ms) + vector_search (10ms) + re_rank (50ms) + network (2ms)
       = ~67ms at P50
```

For a 500ms end-to-end budget, retrieval should consume < 20% of total.

## Retrieval Parameters

### top_k

| k | Recall@k | Precision@k | Latency | Cost |
|---|---|---|---|---|
| 1 | 0.50-0.60 | 0.50-0.60 | Baseline | 1× |
| 3 | 0.70-0.80 | 0.25-0.35 | +10% | 1× |
| 5 | 0.80-0.85 | 0.16-0.20 | +20% | 1× |
| 10 | 0.85-0.92 | 0.08-0.12 | +40% | 1× |
| 50 | 0.92-0.96 | 0.02-0.03 | +100% | 1× (search) + 50× (rerank) |

**Rule:** retrieve 50, re-rank to 10. If latency is tight, retrieve 20, re-rank to 5.

### Score Threshold

Filter out low-scoring chunks before they reach the LLM:

```python
MIN_SIMILARITY = 0.3  # Cosine similarity threshold

retrieved = [doc for doc in retrieve(query, top_k=50)
             if doc.score > MIN_SIMILARITY]
```

Setting a threshold prevents noisy passages from entering the LLM context. Start at 0.3, tune on your data. Too high = missing information; too low = irrelevant context.

## Hybrid Search Weighting

Dense and sparse retrieval capture different signals. Weight them appropriately:

```python
# Balanced (default for general text)
dense_weight = 0.5
sparse_weight = 0.5

# Code / technical docs (exact match matters)
dense_weight = 0.3
sparse_weight = 0.7

# Conversational / ambiguous (semantics matter)
dense_weight = 0.7
sparse_weight = 0.3

# Weighted score
score = dense_weight * dense_score + sparse_weight * sparse_score
```

## Query-Side Optimization

| Technique | Recall Gain | Latency Cost | When to Use |
|---|---|---|---|
| Query expansion | +5-10% | +0ms (rule-based) | Every query |
| HyDE | +3-8% | +100-300ms (LLM call) | Complex queries only |
| Query decomposition | +10-20% | +200-500ms | Multi-part questions |
| Query rewriting (LLM) | +5-15% | +50-200ms | Failed retrieval retry |

**Recommendation:** Always use rule-based query expansion (zero latency cost). Add LLM-based rewriting as a corrective step only when initial retrieval quality is low.

## Index-Side Optimization

| Technique | Recall Impact | Latency Impact | Memory Impact |
|---|---|---|---|
| Increase efSearch (HNSW) | +2-5% | +20-50% | None |
| Increase nprobe (IVF) | +3-8% | +50-200% | None |
| Switch from IVF to HNSW | +3-5% | -20-40% | +10-20% |
| Add re-ranker (50→10) | +5-10% | +50-300ms | None |
| Product quantization | -2-4% | -10-20% | -80-90% |

## Metadata Pre-Filtering

Use metadata filters to reduce search space before vector search:

```python
# Without filter: search all 10M vectors
# With filter: search only 100K vectors with category='finance'
results = vector_db.search(
    query_emb,
    top_k=10,
    filter={"category": "finance"}  # Pre-filter
)
```

Pre-filtering speeds up search proportionally to the selectivity of the filter. A filter that selects 1% of data makes search ~100× faster.

## Re-Ranking Timing

| Strategy | Quality | Latency |
|---|---|---|
| No re-ranking | Baseline | Baseline |
| Re-rank 50→10 | +5-10% | +50-150ms |
| Re-rank 100→10 | +6-11% | +100-300ms |
| Re-rank 200→10 | +6-12% | +200-600ms |
| Cascade (retrieve 100, coarse re-rank 30, fine re-rank 10) | +8-12% | +100-200ms |

Cascade re-ranking gives most of the benefit at half the latency. Coarse re-ranker (MiniLM), fine re-ranker (BGE-large).

## Retrieval Monitoring

| Metric | Good | Investigate |
|---|---|---|
| Recall@10 | > 0.90 | < 0.85 |
| Avg retrieval score | > 0.4 | < 0.3 |
| Zero-result rate | < 1% | > 5% |
| Re-ranking score delta | > 0.1 | < 0.05 (re-ranker not adding value) |

## Optimization Workflow

1. Measure baseline recall@10 on your eval set
2. Enable hybrid search (dense + sparse) → expect +5-15% recall
3. Tune top_k (start with 50) → expect +3-5% recall over k=10
4. Add re-ranker → expect +5-10% recall
5. Add query expansion → expect +3-8% recall
6. Add corrective logic (retry on low relevance) → expect +5-10% recall on hard queries
7. Profile and optimize slow queries

Each step adds complexity and latency. Stop when recall > 0.95 or when latency budget is exhausted.

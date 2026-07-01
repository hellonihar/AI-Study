# Hybrid Search and Filtering

Combining vector similarity with metadata filtering and keyword search.

## The Filtering Problem

Vector search finds *semantically similar* documents. But real queries also require *exact* filters:

```
"Find documents about machine learning where:
  - author = 'Smith'
  - date > 2024-01-01
  - category IN ('research', 'whitepaper')
  - language = 'en'"
```

ANN indexes don't natively understand filters. Applying them correctly is the difference between a working and broken search system.

## Pre-Filter vs Post-Filter

| Approach | Description | Performance |
|---|---|---|
| **Pre-filter** | Apply metadata filter first, then search vector index only on filtered subset | Slow if filters are selective (small candidate pool degrades ANN quality) |
| **Post-filter** | Search vector index, then filter results | Fast but may return < k results after filtering |
| **Filtered ANN** | Modify ANN search to skip non-matching nodes during traversal | Best of both, but product-specific |

### Pre-Filter

```
Query → Filter by metadata → Search vector index on filtered IDs → Results
```

- **Works well when filters are selective** (> 50% of data matches).
- **Fails when filters are restrictive** (< 1% matches): ANN needs many candidates to find good ones; with too few, recall plummets.

### Post-Filter

```
Query → Search vector index (top-k × oversample_factor) → Apply filter → Return top-k
```

- **Oversample:** Retrieve `k × (1 / estimated_selectivity)` candidates before filtering.
- If selectivity is 10%, retrieve 10× oversample.
- **Risk:** If oversample is too low, you get < k results after filtering.

### Filtered ANN (over-filtered search)

Supported by some vector databases:

```
During HNSW traversal: if node's metadata doesn't match filter, skip it.
```

- **Available in:** Milvus (bitset filtering), Weaviate (inverted index + HNSW), Qdrant (payload filtering during HNSW).
- **Best latency** — no two-phase process.
- **But:** If filters are very restrictive, the search may visit many skipped nodes before finding matches.

## Hybrid: Dense + Sparse

Combining vector search with keyword search:

```
Query → [Dense search] ──┐
        [Sparse search] ──┼── Fusion → Re-rank → Results
                          │
        [Metadata filter] ┘
```

**Fusion methods** (covered in Embeddings module):

| Method | Latency Overhead | Quality |
|---|---|---|
| RRF (Reciprocal Rank Fusion) | < 1ms | Good |
| Weighted score combination | < 1ms | Better (with tuned weights) |
| Learned weighting | 2–5ms (ML inference) | Best |

## Filtering Performance by Product

| Product | Method | Filtering Speed | Notes |
|---|---|---|---|
| **Pinecone** | Post-filter (with oversampling) | Fast | Supports metadata filtering natively |
| **Milvus** | Bitset filtering (during search) | Fast | Can combine with IVF/IVF-PQ |
| **Qdrant** | Payload filtering during HNSW | Fast | Efficient for moderately selective filters |
| **Weaviate** | Inverted index + HNSW | Moderate | Strong for text + vector hybrid |
| **pgvector** | SQL WHERE clause + index | Moderate | Full SQL filtering power |
| **Elasticsearch** | Post-filter | Moderate | Combined with BM25 + dense |

## Practical Strategy

```
Selectivity of filter?
├── High (> 50% matches) → Pre-filter (search filtered subset)
├── Medium (10–50%) → Filtered ANN (skip non-matching)
├── Low (1–10%) → Post-filter with oversample factor = 1/selectivity
└── Very low (< 1%) → Consider re-designing your schema
```

## Best Practices

- **Always oversample when post-filtering.** If you need 10 results and the filter selects 10% of data, retrieve 100 candidates before filtering.
- **Measure filter selectivity on your real data.** Static estimates are often wrong. Log selectivity per query type.
- **Use filtered ANN when your database supports it.** It's strictly better than pre/post-filter.
- **Index frequently-filtered fields.** Most vector DBs support scalar indexes on metadata (e.g., inverted index on category, B-tree on date).
- **Monitor "empty result" rate.** If post-filtering frequently returns < k results, increase oversample factor.

# Re-Ranking

The critical second stage that separates production RAG from toy RAG.

## Why Re-Rank?

Dense retrieval (cosine similarity) is a bi-encoder: query and document are encoded independently, then compared with a dot product. This is fast but lossy — the interaction between query and document terms is compressed into a single vector comparison.

Re-ranking uses a cross-encoder: query and document are processed together, allowing full attention between every token of both. This is much more accurate but also much slower.

```
Bi-encoder (retrieval):        Cross-encoder (re-ranking):
    QEnc → q_vec                ┌─────────────────────┐
    DEnc → d_vec                │ [CLS] query [SEP]   │
    score = q_vec · d_vec       │       document [SEP]│
    ├─ Fast: 2-5ms per 10K      │ └─────────┬───────────┘
    └─ Lossy: coarse ranking    │           ▼
                                │      classifier
                                ├─ Slow: 3-5ms per passage
                                └─ Accurate: fine-grained ranking
```

## Re-Ranking Pipeline

```
Query
  │
  ▼
┌──────────────┐
│  Stage 1     │  Hybrid search (dense + sparse)
│  Retrieve    │  top_k = 50-100
│  2-5ms       │
└──────┬───────┘
       │ 50 candidates
       ▼
┌──────────────┐
│  Stage 2     │  Cross-encoder re-ranker
│  Re-rank     │  score each (query, passage) pair
│  50-500ms    │
└──────┬───────┘
       │ top 5-10
       ▼
┌──────────────┐
│  Stage 3     │  LLM generation with re-ranked context
│  Generate    │
└──────────────┘
```

## Re-Ranker Models

| Model | Params | Latency (per passage) | Quality (NDCG@10) | Notes |
|---|---|---|---|---|
| MiniLM-L6-v2 cross-encoder | 22M | 3-5ms | 0.85 | CPU-friendly, good baseline |
| BGE-reranker-base | 278M | 10-15ms | 0.92 | Strong general-purpose |
| BGE-reranker-large | 1.3B | 20-40ms | 0.94 | Best quality, needs GPU |
| Cohere Rerank v3 | API | 50-100ms | 0.93 | No infra, paid API |
| BGE-reranker-v2-M3 | 568M | 15-25ms | 0.93 | Multilingual |
| ColBERTv2 | 110M | 2-5ms | 0.90 | Late interaction (fast) |

## When Re-Ranking Is Worth It

| Scenario | Recall without Re-rank | Recall with Re-rank | Improvement |
|---|---|---|---|
| Simple fact lookup | 0.92 | 0.95 | +3% |
| Multi-hop reasoning | 0.75 | 0.88 | +13% |
| Domain-specific terms | 0.80 | 0.91 | +11% |
| Long-tail entities | 0.60 | 0.82 | +22% |
| Ambiguous queries | 0.70 | 0.85 | +15% |

Re-ranking adds the most value when queries are complex, domain-specific, or ambiguous.

## Candidate Count Trade-Off

| Candidates | Rerank Time | Recall@10 | Relative Recall |
|---|---|---|---|
| 10 | 30ms | 0.80 | Baseline |
| 20 | 60ms | 0.88 | +10% |
| 50 | 150ms | 0.93 | +16% |
| 100 | 300ms | 0.95 | +19% |
| 200 | 600ms | 0.96 | +20% |

**Rule:** Increasing candidates beyond 50 yields minimal recall gain. 50 is the sweet spot for most systems.

## Batch Re-Ranking

Cross-encoders support batching: process (query, passage) pairs in mini-batches for GPU efficiency.

```
batch_size = 32
pairs = [(query, doc) for doc in candidates]
scores = model.predict(pairs, batch_size=32)
# 50 candidates → 2 batches → 2× faster than sequential
```

## Latency Budgeting

For a 500ms total RAG latency budget:

| Stage | Time | Budget % |
|---|---|---|
| Embed query | 5ms | 1% |
| Vector search (hybrid) | 15ms | 3% |
| **Re-rank 50 candidates** | **150ms** | **30%** |
| LLM generation (500 tokens) | 300ms | 60% |
| Pre/post processing | 30ms | 6% |

Re-ranking is the second-largest latency cost after LLM generation. Optimize by:
1. Reducing candidate count (50 → 30 saves 40% re-rank time, loses 2% recall)
2. Smaller re-ranker model (MiniLM instead of BGE-large)
3. Caching re-ranker scores for frequent query-doc pairs

## Code Example Sketch

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

def retrieve_and_rerank(query, top_k=50, rerank_top_k=10):
    # Stage 1: retrieve candidates
    candidates = hybrid_search(query, top_k=top_k)

    # Stage 2: re-rank
    pairs = [(query, doc["text"]) for doc in candidates]
    scores = reranker.predict(pairs)
    for doc, score in zip(candidates, scores):
        doc["rerank_score"] = score
    candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

    return candidates[:rerank_top_k]
```

## When NOT to Re-Rank

- **Latency-critical** (< 50ms P99) — skip re-ranking, optimize retrieval instead
- **Low query volume** (< 100 QPS) — re-ranking cost is negligible
- **High-recall retrieval already** (recall > 0.95) — diminishing returns
- **Simple keyword queries** — BM25 already finds the right passage

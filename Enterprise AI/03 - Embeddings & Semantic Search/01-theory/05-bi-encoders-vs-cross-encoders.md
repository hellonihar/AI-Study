# Bi-Encoders vs Cross-Encoders

Two fundamentally different architectures for text pair scoring, with very different speed/quality trade-offs.

## Bi-Encoder

```
Query → [Encoder] → Vector_q
Doc   → [Encoder] → Vector_d
                     ↓
            similarity(Vector_q, Vector_d)
```

- **Each input encoded independently.**
- **Output:** A single vector per input (the embedding).
- **Similarity computed post-hoc** (cosine, dot product).
- **Pre-computable:** Documents can be encoded once and indexed.

**Latency:** O(N) for N documents (one index lookup).
**Quality:** Good — captures semantic similarity, but misses fine-grained interactions.

## Cross-Encoder

```
[Query | Doc] → [Encoder] → Score
```

- **Query and document processed together** as a single input.
- **Output:** A single similarity score (not an embedding).
- **Cannot pre-compute.** Full forward pass per (query, doc) pair.

**Latency:** O(N) full forward passes for N documents. 50–500ms per pair.
**Quality:** Excellent — full attention between query and document captures subtle relevance signals.

## Performance Comparison

| Aspect | Bi-Encoder | Cross-Encoder |
|---|---|---|
| **Recall@10** | Baseline | +15–25% over bi-encoder |
| **Latency per query (10K docs)** | 5–20ms (index lookup) | 50–500ms (re-ranking) |
| **Pre-computable** | Yes | No |
| **Storage** | Embeddings (KB each) | None |
| **Training complexity** | Moderate (contrastive) | Simple (binary classification) |
| **Model size (typical)** | 100M–350M params | 100M–400M params |

## The Standard Production Pattern: Retrieve → Re-rank

```
1. Bi-encoder: Retrieve top-50 from 1M docs (5–20ms)
2. Cross-encoder: Re-rank top-50 (50–200ms)
3. Return top-5 to user
```

**Why this works:**
- Bi-encoder broad search (fast, covers recall).
- Cross-encoder precision filter (slow, but only on 50 candidates).
- **Total cost:** 20ms + 100ms = 120ms — acceptable for most applications.
- **Recall gain:** +15–25% over bi-encoder alone.

## Cross-Encoder Distillation

You can distill a cross-encoder's quality into a bi-encoder:

1. Run cross-encoder on 100K (query, doc) pairs.
2. Use cross-encoder scores as soft labels.
3. Train bi-encoder to match the scores.
4. Result: Bi-encoder with 70–80% of cross-encoder quality at 100× the speed.

## Popular Models

| Type | Model | Speed | Quality |
|---|---|---|---|
| Bi-encoder | BGE-base-en-v1.5 | Fast | Strong |
| Bi-encoder | E5-mistral-7b | Slow (7B) | Best |
| Cross-encoder | ms-marco-MiniLM-L6-v2 | Very fast (~10ms/pair) | Good |
| Cross-encoder | BGE-reranker-v2-m3 | Fast (~20ms/pair) | Strong |
| Cross-encoder | Cohere Rerank v3 | API (~50ms/pair) | Best |

## Best Practices

- **Always use a cross-encoder in production RAG** if latency budget allows > 100ms. It's the single highest-ROI retrieval improvement.
- **Retrieve 50–100 candidates** with bi-encoder, re-rank top 5–10. Retrieving more doesn't help — cross-encoder is good at ranking, not finding.
- **Use the same cross-encoder for eval.** If your eval uses cross-encoder NDCG, optimize for that metric.
- **Distill cross-encoder into bi-encoder** when latency is critical (< 50ms total). You get most of the gain at bi-encoder speed.

# What Are Embeddings?

Embeddings are dense vector representations that map discrete data (text, images, audio) into a continuous semantic space. Similar items cluster together; dissimilar items are far apart.

## Key Properties

- **Dense:** Every dimension carries information (unlike sparse bag-of-words).
- **Fixed-dimensional:** Typically 384–3072 dimensions regardless of input length.
- **Semantic:** "dog" and "puppy" are closer than "dog" and "table."
- **Composable:** `vector("king") - vector("man") + vector("woman") ≈ vector("queen")`.

## Dimensionality Trade-offs

| Dimensions | Storage (1M vectors) | Recall@10 | Latency (HNSW) | Model Example |
|---|---|---|---|---|
| 128 | 512 MB | 0.82 | 3ms | MiniLM-L6-v2 (384→128 via Matryoshka) |
| 256 | 1 GB | 0.89 | 5ms | BGE-small |
| 384 | 1.5 GB | 0.92 | 7ms | all-MiniLM-L6-v2 |
| 768 | 3 GB | 0.95 | 12ms | BGE-base, E5-base |
| 1024 | 4 GB | 0.96 | 16ms | BGE-large, E5-large |
| 3072 | 12 GB | 0.97 | 35ms | OpenAI text-embedding-3-large |

**Key insight:** Diminishing returns after 768 dims. For most workloads, 384–768 dimensions capture 95%+ of the quality.

## Matryoshka Embeddings (2024)

A single model trained to produce embeddings that work at multiple dimensions:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")
# Flexible dimensions — truncate the output vector
embedding_768 = model.encode("text", truncate_dim=768)
embedding_512 = model.encode("text", truncate_dim=512)
embedding_256 = model.encode("text", truncate_dim=256)
```

- **Use high dims for indexing, low dims for routing.** Index at 768, cache at 256.
- **Recall drop from 768→256 is typically < 3%.** Well worth the 3× storage savings.

## How Embeddings Are Different from LLM Hidden States

| | Embeddings | LLM Hidden States |
|---|---|---|
| **Training objective** | Contrastive (pairs similar items) | Next-token prediction |
| **Output** | Single vector per input | Sequence of vectors |
| **Length handling** | Pooling (mean, CLS, last token) | Autoregressive |
| **Optimized for** | Retrieval, clustering, classification | Generation |
| **Typical use** | Search, RAG, similarity | Chat, writing, analysis |

## Production Relevance

Embeddings are the foundation of RAG, semantic search, deduplication, clustering, and classification. Every enterprise AI system that deals with unstructured data relies on them.

**Performance insight:** The embedding model is called once per indexed document and once per query. For a system with 10M docs and 100K queries/day, embedding cost dominates the indexing phase but is negligible during serving (vector search dominates).

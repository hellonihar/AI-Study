# Embedding Caching and Cost

Minimizing embedding computation costs through caching and batching.

## Where the Cost Goes

| Component | Cost Share | Notes |
|---|---|---|
| **Initial indexing** | 90%+ of lifetime embedding cost | One-time cost per document |
| **New documents** | Ongoing, but proportional to change rate | Usually small % daily |
| **Query embedding** | 5–10% of daily cost | Small, but adds up at scale |
| **Re-indexing** | Can spike cost (new model, re-processing) | Plan ahead |

## Caching Strategies

### Embedding Cache (Document Level)

Cache the embedding alongside the document — never re-embed on re-index:

```python
class EmbeddingCache:
    def __init__(self, model, cache_dir="./embedding_cache"):
        self.model = model
        self.cache_dir = cache_dir
    
    def get_embedding(self, doc_id, text):
        cache_path = f"{self.cache_dir}/{doc_id}.npy"
        if os.path.exists(cache_path):
            return np.load(cache_path)
        emb = self.model.encode(text)
        np.save(cache_path, emb)
        return emb
```

**Benefit:** If you switch vector DBs or re-index with different chunk sizes, cached embeddings save 100% recomputation. Keep them alongside your source data.

### Query Embedding Cache

Cache query embeddings for repeated queries:

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=10000)
def get_query_embedding(query_text):
    return model.encode(query_text)
```

- **Hit rate:** 30–50% for enterprise apps with repetitive queries.
- **TTL:** 24 hours (query meanings drift over time).

### Prefix Cache

If many queries share a prefix or a common context description, cache the prefix embedding:

```python
# Frequent context prefixes
prefixes = {
    "technical": "In the context of software engineering and technology: ",
    "medical": "In the context of medical and healthcare: ",
}
prefix_embeddings = {k: model.encode(v) for k, v in prefixes.items()}
```

## Batching

Embedding models are 10–50× faster with batched input:

```python
# Slow: 1000 individual calls
embeddings = [model.encode(text) for text in texts]  # ~10s

# Fast: 1 batched call
embeddings = model.encode(texts)  # ~0.3s for 1000 texts
```

**Guidelines:**
- Batch size 64–512 for GPU inference.
- Batch size 32–128 for CPU inference.
- Fill batches completely before calling encode — partial batches waste throughput.
- Use `show_progress_bar=False` in production logs (adds overhead).

## Dimension Tuning

Cost scales with embedding dimension in both storage and search:

```
Cost ≈ O(dimensions × log(n)) for search
Storage ≈ O(dimensions × n) for index
```

With Matryoshka models, you can tune dimension to your exact recall needs:

```python
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")

# Production: 768 dims for index, 256 dims for routing
index_emb = model.encode(texts, truncate_dim=768)      # 100% quality
routing_emb = model.encode(texts, truncate_dim=256)     # 97% quality, 3× cheaper
```

## Cost Budgeting

```python
def estimate_monthly_embedding_cost(docs_per_day, queries_per_day, model):
    dims = model.get_sentence_embedding_dimension()
    
    # Approximation: cost scales with dims and model size
    # BGE-base: ~$0.001 per 1000 embeddings (GPU compute)
    index_cost = docs_per_day * 30 * 0.001 / 1000  # monthly indexing
    query_cost = queries_per_day * 30 * 0.001 / 1000  # monthly queries
    
    return {
        "monthly_indexing": round(index_cost, 2),
        "monthly_querying": round(query_cost, 2),
        "total_monthly": round(index_cost + query_cost, 2),
    }
```

## Best Practices

- **Cache aggressively.** Embedding computation is cheap per vector but expensive at scale (10M docs = thousands of GPU-minutes).
- **Batch all embedding operations.** Never call `model.encode()` on single texts in a loop.
- **Use the smallest dimension that meets your recall requirement.** Each halving of dimension cuts storage and search cost by ~50%.
- **Monitor cost-per-embedding.** If you're on an API provider, track this monthly — it should decrease as you optimize.
- **Separate indexing and serving infrastructure.** Indexing can run on cheaper spot instances at off-peak hours.

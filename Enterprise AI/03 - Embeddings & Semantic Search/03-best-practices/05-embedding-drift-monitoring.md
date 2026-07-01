# Embedding Drift Monitoring

Tracking how your embedding space changes over time — and what to do about it.

## What Is Embedding Drift?

The distribution of query embeddings changes over time as user behavior evolves, new topics emerge, or the underlying model is updated.

```
Day 1: Queries about "login" = 30% of traffic
Day 90: Queries about "login" = 10% (users learned it), "AI features" = 40%
```

## Why Monitor Drift?

| Problem | Impact | Detection |
|---|---|---|
| **Query distribution shift** | Recall degrades for new query types | Centroid shift |
| **Document distribution shift** | New content isn't well-indexed | Cluster quality metrics |
| **Model version change** | Embedding space reshuffles, previous thresholds invalidate | Embedding similarity between versions |
| **Data quality degradation** | Bad embeddings poison the index | Outlier ratio increase |

## Metrics to Track

### Embedding Centroid

```python
def compute_centroid(embeddings):
    return np.mean(embeddings, axis=0)

def centroid_shift(embeddings_day1, embeddings_day90):
    c1 = compute_centroid(embeddings_day1)
    c2 = compute_centroid(embeddings_day90)
    return 1 - np.dot(c1, c2) / (np.linalg.norm(c1) * np.linalg.norm(c2))
```

- **Track daily.** Alert if centroid moves > 0.1 cosine distance in 7 days.

### Outlier Ratio

```python
def outlier_ratio(embeddings, threshold=0.3):
    centroid = compute_centroid(embeddings)
    distances = 1 - (embeddings @ centroid)
    return np.mean(distances > threshold)
```

- **High outlier ratio** = new topics not well-covered by the embedding model.

### Recall on Held-Out Eval Set

```python
# Run daily against a fixed eval set
recall_today = evaluate_retrieval(model, fixed_eval_set)
if recall_today < baseline_recall - 0.05:
    alert("Retrieval quality degraded!")
```

- **The most important metric.** If recall drops, something is wrong — investigate.

## Detecting Model Version Shift

When switching embedding models, measure the alignment:

```python
def model_alignment(old_model, new_model, texts):
    old_emb = old_model.encode(texts)
    new_emb = new_model.encode(texts)
    
    old_emb = old_emb / np.linalg.norm(old_emb, axis=1, keepdims=True)
    new_emb = new_emb / np.linalg.norm(new_emb, axis=1, keepdims=True)
    
    # Similarity between corresponding vectors
    pair_sim = np.sum(old_emb * new_emb, axis=1)
    print(f"Pairwise similarity: {pair_sim.mean():.3f} ± {pair_sim.std():.3f}")
    
    # Kendall rank correlation on nearest neighbors
    from scipy.stats import kendalltau
    tau = kendalltau(old_emb @ old_emb.T, new_emb @ new_emb.T)
    print(f"Rank correlation: {tau:.3f}")
```

- **Pairwise similarity > 0.95:** Safe to swap, no re-indexing needed.
- **0.85–0.95:** Expect some quality change, recommend re-indexing.
- **< 0.85:** Must re-index — ranking will change significantly.

## Alerting Thresholds

| Metric | Warning | Critical |
|---|---|---|
| Centroid shift (7d) | > 0.05 | > 0.15 |
| Outlier ratio | > 10% | > 25% |
| Recall drop (vs baseline) | > 3% | > 5% |
| Model alignment (new vs old) | < 0.90 | < 0.85 |
| Empty search rate | > 5% | > 10% |

## Remediation Actions

| Drift Type | Action |
|---|---|
| Query distribution shift | Re-sample training data, fine-tune if persistent |
| Document distribution shift | Re-index with adapted chunking |
| Model version change | Re-index or run A/B test before switching |
| Recall degradation | Investigate first: is it embedding quality, indexing, or retrieval config? |

## Implementation

```python
class EmbeddingMonitor:
    def __init__(self, eval_set, baseline_embeddings):
        self.eval_set = eval_set
        self.baseline_centroid = compute_centroid(baseline_embeddings)
        self.baseline_recall = None
    
    def daily_report(self, queries, documents, model):
        q_emb = model.encode(queries)
        d_emb = model.encode(documents)
        
        return {
            "centroid_shift": centroid_shift(self.baseline_centroid, q_emb),
            "outlier_ratio": outlier_ratio(q_emb),
            "qps": len(queries) / 86400,
            "avg_query_length": np.mean([len(q.split()) for q in queries]),
        }
```

## Best Practices

- **Monitor recall on a fixed eval set daily.** It's the single best indicator of retrieval health.
- **Log query embeddings for post-hoc analysis.** Store a 1% sample of query embeddings to analyze drift retrospectively.
- **Set up automated rollback.** If recall drops > 5% after a model change, roll back to the previous embedding model.
- **Re-evaluate embedding model quarterly.** New models are released frequently and often bring meaningful quality improvements.
- **Don't overreact to short-term drift.** Weekly patterns (weekday vs weekend queries) cause natural drift. Use 7-day rolling averages.

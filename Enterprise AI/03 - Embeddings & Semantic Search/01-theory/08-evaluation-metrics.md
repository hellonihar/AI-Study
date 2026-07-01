# Evaluation Metrics

Measuring and improving retrieval quality — the metrics that matter for production RAG.

## Core Metrics

| Metric | What It Measures | Range | Target |
|---|---|---|---|
| **Recall@k** | Fraction of relevant docs in top-k | [0, 1] | > 0.9 @ 10 |
| **Precision@k** | Fraction of top-k that are relevant | [0, 1] | > 0.5 @ 10 |
| **MRR** (Mean Reciprocal Rank) | Rank of first relevant result | [0, 1] | > 0.9 |
| **NDCG@k** (Normalized Discounted Cumulative Gain) | Ranking quality with graded relevance | [0, 1] | > 0.8 @ 10 |
| **MAP** (Mean Average Precision) | Precision across all recall levels | [0, 1] | > 0.7 |

## Recall@k — The Most Important Metric

```
recall@k = (number of relevant documents in top-k) / (total relevant documents)
```

- **The ceiling for RAG quality.** If recall@10 is 0.7, the LLM can never answer correctly for 30% of queries regardless of generation quality.
- **Target:** > 0.9@10 for production retrieval.
- **Improving recall:** Hybrid search (+10%), query rewriting (+10–15%), re-ranking (+15–25%).

## NDCG — When Relevance Is Graded

Not all relevant documents are equally useful:

```
Relevance scale:
  2 = Highly relevant (answers the question directly)
  1 = Somewhat relevant (background information)
  0 = Not relevant

NDCG = DCG / IDCG
DCG = Σ (2^{rel_i} - 1) / log₂(i + 1)
```

- **NDCG@10** is the standard retrieval metric in MTEB.
- **Penalizes ranking errors** — a highly relevant doc at position 10 hurts NDCG more than at position 1.

## Building an Eval Dataset

### Option 1: Human Labeling (Gold Standard)

- 500+ query-document relevance pairs.
- Each pair labeled 0/1 (or graded 0–2).
- 2+ labelers per pair (measure inter-rater agreement).
- **Cost:** ~$0.50–$2.00 per query.

### Option 2: LLM-as-Judge

```python
judge_prompt = """
Given the query and document, rate relevance:
2 = Directly answers the query
1 = Contains related information
0 = Not relevant

Query: {query}
Document: {document}
Relevance score (0/1/2):
"""
```

- Cheaper than human labeling (~$0.01/query).
- Correlates well with human judgment (r > 0.8).
- Calibrate against a small human-labeled set.

### Option 3: Click Logs (Implicit)

- User clicked result = relevant (proxy).
- User didn't click = not relevant (noisy).
- **Bias:** Position bias (users click top results regardless of relevance).
- **Requires correction:** Inverse propensity weighting.

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| **Leakage** | Eval score is 0.99 but production is 0.70 | Ensure eval queries weren't seen during training/indexing |
| **Label scarcity** | Small eval set → high variance | Bootstrap confidence intervals |
| **Metric mismatch** | High recall, low NDCG | You're returning relevant docs but not ranking them well → add re-ranker |
| **Query distribution mismatch** | Eval score high, user satisfaction low | Sample eval queries from production logs, not curated |
| **Judge bias** | LLM-as-Judge consistently over/under-scores | Calibrate against human labels |

## Production Monitoring

```python
def compute_retrieval_metrics(queries, relevant_docs, retriever):
    results = {"recall_5": [], "recall_10": [], "mrr": [], "ndcg_10": []}
    for query, relevant in zip(queries, relevant_docs):
        retrieved = retriever.retrieve(query, k=10)
        retrieved_ids = [r["id"] for r in retrieved]
        
        # Recall@10
        hits = sum(1 for id in relevant if id in retrieved_ids)
        results["recall_10"].append(hits / len(relevant))
        
        # MRR
        for rank, id in enumerate(retrieved_ids):
            if id in relevant:
                results["mrr"].append(1 / (rank + 1))
                break
        else:
            results["mrr"].append(0)
    
    return {k: np.mean(v) for k, v in results.items()}
```

## Best Practices

- **Track recall@10 daily** — it's the single metric that best predicts RAG quality.
- **Maintain a held-out eval set** — never optimize against your test set.
- **Include production queries in your eval set** — curated benchmarks don't reflect real user behavior.
- **Report confidence intervals** — a 2-point improvement isn't significant on 50 queries.
- **Fix the metric that's lowest first.** Low recall? Fix retrieval. Low NDCG? Add re-ranking. High recall but bad answers? The problem is generation, not retrieval.

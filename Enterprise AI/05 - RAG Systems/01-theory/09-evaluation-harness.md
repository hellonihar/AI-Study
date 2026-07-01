# Evaluation Harness

Measuring RAG system quality: component-level and end-to-end metrics.

## Why Evaluate RAG?

RAG systems have two independent failure modes:
1. **Retrieval fails** — passages don't contain the answer
2. **Generation fails** — passages contain the answer, but LLM ignores or misuses them

Evaluating both stages independently is essential for debugging and optimization.

## Component-Level Evaluation

### Retrieval Metrics

| Metric | What It Measures | Formula | Target |
|---|---|---|---|
| **Recall@k** | Relevant passages in top-k | `hits_k / total_relevant` | > 0.90 |
| **Precision@k** | Retrieved passages that are relevant | `relevant_k / k` | > 0.70 |
| **MRR** | Rank of first relevant passage | `1 / rank_first_relevant` | > 0.85 |
| **NDCG@k** | Rank-weighted relevance | Discounted cumulative gain | > 0.85 |
| **Context coverage** | % of answer-required info in retrieved passages | Human annotation | > 0.95 |

### Generation Metrics

| Metric | What It Measures | Formula | Target |
|---|---|---|---|
| **Faithfulness** | Claims supported by passages | `supported_claims / total_claims` | > 0.95 |
| **Answer relevance** | Answer addresses the query | LLM-judged relevance | > 0.90 |
| **Citation precision** | Citations map to supporting text | `valid_citations / total_citations` | > 0.95 |
| **Hallucination rate** | Unsupportable claims | `unsupported_claims / total_claims` | < 0.05 |
| **Completeness** | All aspects of query answered | Human evaluation | > 0.85 |

## End-to-End Metrics

### RAGAS Framework (RAG Assessment)

RAGAS defines 4 core metrics computed without ground-truth labels, using LLM-as-judge:

1. **Faithfulness** — Are claims in the answer supported by retrieved passages?
2. **Answer Relevance** — How relevant is the answer to the question?
3. **Context Precision** — Are retrieved passages relevant to the question?
4. **Context Recall** — Do retrieved passages contain all needed information?

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

result = evaluate(
    dataset=rag_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision]
)
```

### ARES Framework

Alternative to RAGAS with fine-tuned classifiers for faithfulness and relevance. More accurate but requires labeled training data.

### TruLens

Track RAG quality over time with three metrics:
- **Answer relevance** — The answer addresses the question
- **Context relevance** — Retrieved passages are relevant to the question
- **Groundedness** — The answer is supported by the retrieved passages

## Building an Evaluation Dataset

### Requirements

| Item | Minimum | Recommended |
|---|---|---|
| Number of queries | 100 | 500+ |
| Ground-truth passages per query | 1 | 3-5 |
| Ground-truth answer | 1 | 1 (with citations) |
| Domains covered | 1 | 3-5 |
| Query difficulty mix | — | 60% easy / 30% medium / 10% hard |

### Synthetic Data Generation

```python
def generate_eval_set(documents, n_queries=500):
    queries = []
    for doc_sample in sample(documents, n_queries):
        # Ask LLM to generate a question answerable by this document
        query = llm.generate(
            f"Generate a question that can be answered by this passage:\n{doc_sample}"
        )
        queries.append({
            "query": query,
            "relevant_passages": [doc_sample],
            "hard_negatives": sample(documents, 3)  # similar but not relevant
        })
    return queries
```

**Quality check:** Have humans verify 10-20% of synthetic queries. Typical accuracy: 70-85%.

## Evaluation Pipeline

```python
def evaluate_rag(rag_system, eval_dataset):
    results = []
    for item in eval_dataset:
        # Run RAG
        response = rag_system.answer(item["query"])

        # Collect metrics
        result = {
            "query": item["query"],
            "response": response["answer"],
            "retrieved_passages": response["passages"],
            "citations": response.get("citations", []),
        }

        # Compute retrieval metrics
        result["recall@10"] = recall_at_k(
            response["passages"],
            item["relevant_passages"],
            k=10
        )

        # Compute generation metrics (LLM-based)
        result["faithfulness"] = faithfulness_score(
            response["answer"],
            response["passages"]
        )
        result["answer_relevance"] = answer_relevance(
            item["query"],
            response["answer"]
        )

        results.append(result)

    return aggregate(results)
```

## A/B Testing in Production

```yaml
experiment:
  name: "re-ranker-vs-baseline"
  variants:
    - name: "control"
      config: { reranker: None }
    - name: "treatment"
      config: { reranker: "cross-encoder/ms-marco-MiniLM-L6-v2" }

  metrics:
    primary: "user_click_rate"       # did user click a citation?
    secondary:
      - "answer_satisfaction"        # thumbs up/down
      - "response_latency_p99"
      - "follow_up_rate"             # did user need to ask again?

  duration: 7_days
  sample_rate: 10%  # of traffic
```

## Continuous Evaluation

```yaml
daily_eval:
  dataset: "evaluation/queries_v2.json"  # 500 queries
  triggers:
    - schedule: "0 6 * * *"              # daily at 6 AM
    - deploy: true                        # on every deployment

  actions:
    - compute_all_metrics
    - compare_with_baseline
    - if faithfulness < 0.90:
        alert: "#rag-alerts"
        rollback: true                    # revert to previous model/config
    - log_to: "metrics/rag_eval.jsonl"

  dashboard:
    - metric: "faithfulness"
      chart: "time_series"
      alert_threshold: 0.90
    - metric: "recall@10"
      chart: "time_series"
      alert_threshold: 0.85
```

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| **LLM-as-judge bias** | Overestimates faithfulness | Use multiple LLMs, average scores |
| **Leakage in eval set** | Queries overlap with training data | Hold out recent documents |
| **Single query type** | System tuned to one pattern | Diversify eval dataset |
| **Vanilla metrics** | Uninformative averages | Break down by query difficulty |
| **No human validation** | Metrics misaligned with user satisfaction | Quarterly human eval studies |

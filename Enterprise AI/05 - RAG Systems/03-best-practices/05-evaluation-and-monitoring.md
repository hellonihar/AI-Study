# Evaluation and Monitoring

Measuring and maintaining RAG quality in production.

## Quality Dimensions

| Dimension | What It Measures | Why It Matters |
|---|---|---|
| **Grounding** | Are answers supported by retrieved passages? | Hallucination prevention |
| **Completeness** | Are all aspects of the query addressed? | User satisfaction |
| **Relevance** | Does the answer actually answer the question? | User satisfaction |
| **Citation accuracy** | Do citations point to supporting text? | Trust and verifiability |
| **Timeliness** | How recent is the information? | Freshness requirements |

## Evaluation Pipeline

### Offline Evaluation (Pre-Deployment)

Run before every deployment:

```yaml
offline_eval:
  dataset: "evaluation/rag_v3.json"   # 500 labeled queries
  metrics:
    - faithfulness                    # LLM-judged
    - answer_relevance                # LLM-judged
    - recall@10                       # Retrieval quality
    - citation_accuracy               # Verified against passages
    - latency_p50_p95_p99             # Performance budget
  
  thresholds:
    faithfulness: 0.90
    recall@10: 0.85
    latency_p99: 2000  # ms
  
  actions:
    - if any_metric_below_threshold:
        block_deployment
        alert: "#rag-alerts"
```

### Online Evaluation (In Production)

Continuous quality monitoring:

```yaml
online_monitoring:
  sampling_rate: 0.1     # Evaluate 10% of traffic
  
  automated_metrics:
    - name: faithfulness
      sampler: "LLM-as-judge (GPT-4o mini)"
      interval: "every 100 requests"
    
    - name: answer_relevance
      sampler: "LLM-as-judge"
      interval: "every 100 requests"
    
    - name: retrieval_score
      sampler: "avg score of top-3 retrieved passages"
      interval: "every request"
    
    - name: zero_result_rate
      sampler: "% of queries with 0 relevant passages"
      interval: "every request"
  
  user_signals:
    - name: thumbs_up_rate
      source: "user feedback widget"
    - name: follow_up_rate
      source: "% of queries with follow-up in 5 minutes"
    - name: session_length
      source: "avg queries per session"
```

## LLM-as-Judge Setup

Use a separate, smaller LLM (GPT-4o mini, Claude 3 Haiku) to evaluate your RAG system:

```python
def evaluate_faithfulness(answer, passages):
    prompt = f"""
    Determine if the following answer is FAITHFUL to the provided passages.
    
    Passage: {passages[0]}
    
    Answer: {answer}
    
    Is each claim in the answer supported by the passage?
    Respond with JSON: {{"faithful": true/false, "reason": "..."}}
    """
    response = judge_llm(prompt)
    return json.loads(response)["faithful"]
```

**Caveats:**
- LLM-as-judge is biased toward verbose, well-structured answers
- Use multiple judges and average scores for reliability
- Periodically validate judge against human annotations

## Alerting Thresholds

```yaml
alerts:
  critical:
    - faithfulness < 0.80 for 5 minutes
    - error_rate > 5% for 1 minute
    - P99 latency > 5s for 2 minutes
  
  warning:
    - faithfulness < 0.88 for 15 minutes
    - recall@10 < 0.80 for 30 minutes
    - cache_hit_rate < 10% for 1 hour
    - zero_result_rate > 3% for 30 minutes

  info:
    - recall@10 dropped 5% from baseline
    - avg retrieval score dropped 0.1 from baseline
    - citation_accuracy < 0.90
```

## Drift Detection

Monitor these signals for system drift:

| Signal | Likely Cause | Response |
|---|---|---|
| Recall@10 declining | Embedding model drift, data drift | Re-index, update embedding model |
| Faithfulness declining | LLM behavior shift | Update prompt, pin LLM version |
| Avg retrieval score dropping | Query distribution shift | Review query logs, update index |
| Citation accuracy dropping | LLM behavior shift | Update citation prompt, add post-hoc verification |
| Latency increasing | Data growth, index fragmentation | Re-index, scale shards |

## Regression Testing

```yaml
regression_tests:
  schedule: "daily"
  dataset: "evaluation/rag_regression.json"  # 100 edge cases
  
  test_cases:
    - query: "What's the refund policy?"
      expected: "Must cite refund policy document"
    - query: "I don't know"  # Out-of-knowledge query
      expected: "Must refuse, not hallucinate"
    - query: ""  # Empty query
      expected: "Must return error, not generate"
    - query: "SELECT * FROM users"  # SQL injection
      expected: "Must refuse safely"
```

## A/B Testing Framework

```yaml
experiment:
  name: "reranker-model-upgrade"
  variants:
    control: "current reranker (MiniLM)"
    treatment: "new reranker (BGE-reranker)"
  
  metrics:
    primary: "faithfulness"
    secondary:
      - "answer_relevance"
      - "latency_p99"
  
  duration: 7_days
  min_sample: 10000  # per variant
  
  decision_rules:
    - if treatment.faithfulness > control.faithfulness + 0.02:
        roll_out: "100%"
    - elif treatment.faithfulness > control.faithfulness - 0.01:
        roll_out: "50% for 1 more week"
    - else:
        roll_back: true
```

## Monitoring Runbook

### Faithfulness Alert Triggers

1. Check if LLM model version changed (deployed new model?)
2. Check if system prompt was modified (recent change?)
3. Check if retrieval quality degraded (recall@10 dropping?)
4. Check if query distribution changed (new use case?)
5. Temporary fix: Pin model version, revert prompt
6. Permanent fix: Update prompt, improve retrieval, or retrain model

### Recall@10 Alert Triggers

1. Check if new documents were indexed (data drift?)
2. Check if embedding model changed
3. Check if vector DB index needs rebuild (mutations accumulated)
4. Run eval on old data to isolate root cause
5. Temporary fix: Rebuild index with more data
6. Permanent fix: Update chunking, retrain embedding, add re-ranker

## Weekly Quality Review

```yaml
weekly_review:
  metrics_to_review:
    - faithfulness_7d_avg
    - recall_7d_avg
    - latency_p50_p95_7d_avg
    - cost_per_query_7d_avg
    - user_feedback_score_7d_avg
  
  actions:
    - if faithfulness trending down: schedule prompt review
    - if recall trending down: schedule index review
    - if cost trending up: review caching, model size, tier
  
  report_to: "#rag-team"
```

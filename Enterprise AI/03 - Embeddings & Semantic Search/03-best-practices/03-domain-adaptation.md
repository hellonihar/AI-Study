# Domain Adaptation

Making general embedding models work well on specialized domains.

## When Domain Adaptation Is Needed

| Sign | Impact | Action |
|---|---|---|
| General terms work, domain terms don't | "contract" finds legal docs, but "indemnification" finds nothing | Fine-tune or add domain vocabulary |
| Top results are topically correct but miss key documents | Recall@10 is 0.6 on your domain vs 0.9 on general benchmarks | Fine-tune with domain data |
| Query ambiguity hurts more than expected | "Apple" returns fruit before company | Add domain-specific training pairs |

## How Much Data Do You Need?

| Data Size | Expected Recall Gain | Method |
|---|---|---|
| 100–500 pairs | +2–5% | Lightweight fine-tuning with contrastive loss |
| 1K–5K pairs | +5–10% | Full contrastive fine-tuning with hard negatives |
| 5K–50K pairs | +10–15% | Fine-tuning + hard negative mining + longer training |
| 50K+ pairs | +15–20% | Train from a strong base (E5, BGE) with optimized hyperparameters |

**Diminishing returns:** Beyond 10K pairs, each additional 1K pairs gives ~0.5% improvement.

## Creating Training Data

### Option 1: From Click Logs

```
User searched "password reset" → clicked result 7 (password reset guide)
→ (query="password reset", positive=7, negatives=BM25 top-10 excluding 7)
```

- **Advantage:** Real user behavior, large volume, free.
- **Disadvantage:** Noisy (users sometimes click irrelevant results).

### Option 2: LLM-Generated

```python
prompt = """Generate 5 questions that would be answered by this document,
and 5 questions that seem related but are NOT answered by it.

Document: {document}

Output JSON:
{"positive_queries": [...], "negative_queries": [...]}
"""
```

- **Advantage:** Scalable, no human labeling needed.
- **Disadvantage:** LLM-generated queries may not match real user behavior.

### Option 3: Human Annotated

- **Advantage:** Highest quality.
- **Disadvantage:** Expensive ($1–3 per query-doc pair).

## Fine-Tuning Recipe

```
1. Base model: BGE-base or BGE-large (strong general foundation)
2. Training data: 5K+ query-document pairs from your domain
3. Negative mining: BM25 top-100, exclude positives, sample 1–3 hard negatives per query
4. Loss: InfoNCE (MultipleNegativesRankingLoss)
5. Batch size: 64–256 (larger = better negatives)
6. Learning rate: 2e-5 for base model, 1e-5 for large
7. Epochs: 3–5 (stop when eval recall plateaus)
8. Eval every 100 steps on held-out domain test set
```

## Evaluation Before and After

```python
# Before fine-tuning
base_recall = evaluate(base_model, domain_test_set)
print(f"Base recall@10: {base_recall:.3f}")

# After fine-tuning
ft_recall = evaluate(ft_model, domain_test_set)
print(f"Fine-tuned recall@10: {ft_recall:.3f}")
print(f"Improvement: {(ft_recall - base_recall) * 100:+.1f}%")
```

## When NOT to Fine-Tune

| Scenario | Better Approach |
|---|---|
| < 100 domain queries | Use hybrid search (BM25 handles domain terms) |
| Domain vocabulary in 5% of corpus | Add domain terms to BM25 or use SPLADE |
| Only need better ranking, not retrieval | Add a cross-encoder re-ranker (cheaper than fine-tuning) |
| General performance already acceptable | Don't fix what isn't broken |

## Best Practices

- **Benchmark before fine-tuning.** Many teams fine-tune when they should first try hybrid search or a better base model.
- **Never fine-tune on < 500 pairs.** You'll overfit to noise and degrade general performance.
- **Add a general-domain replay buffer.** Include 10–20% general domain data in training to prevent catastrophic forgetting.
- **Monitor general benchmark performance.** Ensure fine-tuning doesn't degrade quality on standard tasks — if it drops > 2%, reduce domain-specific training ratio.
- **Re-fine-tune every 3–6 months** as new data and query patterns emerge.

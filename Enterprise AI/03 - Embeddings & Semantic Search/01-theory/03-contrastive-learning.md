# Contrastive Learning

The training paradigm behind embedding models — learning to pull similar pairs together and push dissimilar pairs apart.

## Core Idea

Learn an embedding function `f(x)` such that:

```
similarity(f(x), f(x⁺)) >> similarity(f(x), f(x⁻))
```

Where `x⁺` is a positive pair (similar) and `x⁻` is a negative pair (dissimilar).

## Loss Functions

### Contrastive Loss

```
L = y · d² + (1-y) · max(0, margin - d)²
```

- `y = 1` for similar pairs, `y = 0` for dissimilar.
- `d = ||f(x₁) - f(x₂)||` (Euclidean distance).
- **Simple but requires careful margin tuning.**

### Triplet Loss

```
L = max(0, d(anchor, positive)² - d(anchor, negative)² + margin)
```

- Three items: anchor, positive (similar), negative (dissimilar).
- **Requires hard negative mining** — random negatives are too easy and produce loss = 0.

### InfoNCE (NT-Xent Loss)

Used by SimCSE, CLIP, and most modern embedding models:

```
L = -log( exp(sim(x, x⁺)/τ) / Σ exp(sim(x, xᵢ)/τ) )
```

- `sim` = cosine similarity.
- `τ` = temperature (lower = sharper distribution).
- Negatives come from in-batch examples (efficient, scales with batch size).
- **Currently dominant approach** — simpler than triplet, better than contrastive.

## In-Batch Negatives

A key efficiency technique: treat all other items in the same batch as negatives for each item.

```
Batch: [A, A⁺, B, B⁺, C, C⁺]

For anchor A:
  Negative candidates: B, B⁺, C, C⁺  (everything except A⁺)
```

- **Larger batch = more negatives = better training.** Batch sizes of 256–4096 are common.
- **Memory-bound** — GPUs with more memory train better embedding models.

## Hard Negative Mining

Not all negatives are equally useful. Random negatives are too easy — the model quickly learns to distinguish them. Hard negatives (similar but different meaning) force the model to learn finer distinctions:

| Negative Type | Difficulty | Source |
|---|---|---|
| Random | Easy | Any random document |
| BM25 top non-relevant | Medium | Retrieve with BM25, pick non-relevant results |
| Embedding top non-relevant | Hard | Retrieve with current model, pick false positives |
| Cross-encoder bottom | Hardest | Use cross-encoder to find most confusing negatives |

**Production tip:** Mine hard negatives from production logs — false positives (results users didn't click) are ideal.

## SimCSE (2022)

A breakthrough method that removes the need for labeled pairs:

- **Unsupervised:** Use the same sentence twice with different dropout masks → positive pair.
- **Supervised:** Use NLI datasets (entailment = positive, contradiction = hard negative).
- **Results:** Matches or exceeds supervised models without human-labeled pairs.

## Domain Fine-Tuning

To adapt a general embedding model to your domain:

1. Start with a strong base (BGE, E5).
2. Collect 10K+ query-document pairs from your domain.
3. Fine-tune with InfoNCE loss, in-batch negatives, and hard negatives from BM25.
4. Evaluate on held-out retrieval task — expect 5–15% recall improvement.

## Best Practices

- **Use InfoNCE loss with in-batch negatives** — it's the simplest and most effective setup.
- **Large batch size matters more than large model** for embedding training. A 7B model with batch size 64 underperforms a 350M model with batch size 2048.
- **Hard negatives are essential** for domain adaptation. Without them, the model learns to distinguish domain vs. non-domain rather than subtle within-domain differences.
- **Evaluate, don't assume.** A lower loss doesn't guarantee better retrieval — always measure recall@k.

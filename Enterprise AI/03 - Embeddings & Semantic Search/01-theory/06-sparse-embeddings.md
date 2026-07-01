# Sparse Embeddings

Traditional term-based representations that complement dense embeddings.

## What Are Sparse Embeddings?

A vector where most dimensions are zero. Each dimension corresponds to a term (word, subword, or token), and the value represents importance.

```
"the quick brown fox"
→ {"the": 0.5, "quick": 1.2, "brown": 1.0, "fox": 1.5}
→ [0, 0, ..., 1.2, 0, ..., 1.0, 0, ..., 1.5, 0, ...]
```

## Sparse vs Dense

| Property | Sparse | Dense |
|---|---|---|
| Vector size | 50K–500K (vocabulary) | 384–4096 (fixed) |
| Non-zero entries | 1–100 per document | All dimensions |
| Vocabulary | Fixed (or learned) | Learned latent space |
| Exact match | Yes (terms are atomic) | No (semantic neighbors) |
| Out-of-vocabulary | Missed | Captured semantically |
| Storage | ~0.1 MB / 1M docs (inverted index) | ~3 GB / 1M docs (768 dims) |

## BM25

The most widely used sparse retrieval method:

```
BM25 score = Σ IDF(t) × (TF(t, d) × (k₁ + 1)) / (TF(t, d) + k₁ × (1 - b + b × |d|/avgdl))
```

- **IDF:** How rare is the term? Rare terms get higher weight.
- **TF:** How frequent in this document? Higher = more relevant.
- **k₁, b:** Tunable parameters (k₁=1.2, b=0.75 recommended).

**Strengths:**
- Fast — inverted index with O(1) lookup per term.
- Handles exact matches perfectly.
- Works out of the box — no training or GPU needed.
- Strong on domain-specific terms and named entities.

**Weaknesses:**
- Vocabulary mismatch: "car" and "automobile" don't match.
- No semantic understanding: "not helpful" matches "helpful."
- Sensitive to term weighting parameters.

## SPLADE (2021)

Learned sparse embeddings — the model learns which terms are important:

```
"car repair shop" → {"car": 2.1, "repair": 3.0, "shop": 1.8, "auto": 1.2, "mechanic": 0.9}
```

- **Best of both worlds:** Sparse representation + learned semantic expansion.
- **FLOPS regularization:** Penalty for too many non-zero terms — encourages efficiency.
- **Performance:** Matches or exceeds dense models on domain-specific retrieval.

## When Sparse Wins Over Dense

| Scenario | Sparse | Dense |
|---|---|---|
| Exact name matching ("John Smith") | ✅ Perfect | ❌ May miss |
| Domain terminology ("myocardial infarction") | ✅ Term matches | ✅ Captures synonyms |
| Short queries (1–2 words) | ✅ Strong | ⚠️ Weak (lack of context) |
| Long, conversational queries | ❌ Missing terms | ✅ Captures intent |
| Cross-language | ❌ | ✅ Shared space |

## Implementation

```python
from rank_bm25 import BM25Okapi  # pip install rank-bm25

# Index
tokenized_corpus = [doc.split() for doc in documents]
bm25 = BM25Okapi(tokenized_corpus)

# Search
query = "car repair shop"
tokenized_query = query.split()
scores = bm25.get_scores(tokenized_query)
top_k = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
```

## Best Practices

- **Never deploy dense-only retrieval in production.** BM25 is free (no model, no GPU) and catches cases dense misses.
- **Use hybrid search** (dense + sparse) as the baseline — see [07-hybrid-search.md](07-hybrid-search.md).
- **SPLADE is worth considering** if you want learned spare but can't afford two systems (dense + BM25). It replaces both.
- **BM25 parameters matter.** Tune k₁ and b on your first 1000 queries — default parameters are rarely optimal for your specific domain.

# Retrieval Strategies

How to find the right passages for a query before sending them to the LLM.

## The Retrieval Challenge

```
User Query: "What was Q3 revenue for the European division?"

Relevant passage: "European division revenue reached €12.4M in Q3 2024,
                   a 15% increase year-over-year, driven by..."

Vector similarity: The query and passage share few surface-level tokens.
BM25 score: Low (no lexical overlap with "European", "Q3", "revenue")
```

The core challenge: the query and the relevant passage may have zero lexical overlap but be semantically identical.

## Retrieval Methods Ranked by Recall

| Method | Recall@20 (typical) | Latency | Cost |
|---|---|---|---|
| Dense (vector) only | 0.75-0.85 | 2-5ms | Low |
| Sparse (BM25) only | 0.50-0.65 | 1-3ms | Very low |
| Hybrid (dense + sparse) | 0.85-0.95 | 5-15ms | Low |
| Hybrid + re-ranking | 0.90-0.98 | 20-100ms | Medium |
| Multi-stage retrieval | 0.92-0.99 | 50-500ms | High |

## 1. Dense Retrieval (Vector Search)

Embed query → cosine similarity → return top-k.

```
query_emb = model.encode("What was Q3 revenue for European division?")
results = vector_db.search(query_emb, top_k=20)
```

**Strengths:** Semantic understanding, handles vocabulary mismatch
**Weaknesses:** Requires training data, poor at exact match (names, IDs, dates)
**Best for:** Open-ended questions, conceptual queries

## 2. Sparse Retrieval (BM25 / SPLADE)

Lexical matching with TF-IDF weighting and term saturation.

```
from rank_bm25 import BM25Okapi
scores = bm25.get_scores(query.split())
```

**Strengths:** Exact match (names, codes), zero training, interpretable
**Weaknesses:** No semantic understanding, vocabulary mismatch
**Best for:** Keyword-heavy queries, named entity lookup, low-resource setups

## 3. Hybrid Retrieval

Combine dense + sparse scores via Reciprocal Rank Fusion (RRF):

```
RRF(d) = Σ 1 / (k + rank_dense(d)) + Σ 1 / (k + rank_sparse(d))
```

Typical k=60. See `02-code/07-hybrid-search.py` from Vector Databases module.

**Result:** 5-15% recall improvement over either method alone. This is the production default for RAG.

## 4. Query Rewriting

Transform the user's raw query into one or more search-optimized queries.

### Query Expansion
```
User query: "How do I reset my password?"
    ↓
Expanded: "How do I reset my password? password reset steps forgot password
           change password account recovery"
```

### Query Decomposition
```
User query: "Compare the Q3 results of North America and Europe"
    ↓
Sub-queries: "Q3 results for North America division",
             "Q3 results for European division"
```

### Hypothetical Document Embeddings (HyDE)
```
User query → LLM generates hypothetical answer → embed that → search
```

**Rationale:** The hypothetical answer looks more like the target passage than the query does in embedding space.

```
Step 1: hypothetical = llm.generate("A document that answers: {query}")
Step 2: hyp_emb = embed(hypothetical)
Step 3: results = vector_db.search(hyp_emb, top_k=20)
```

HyDE improves recall by 3-8% for complex queries at the cost of one LLM call per query.

**Trade-off:** Query rewriting adds latency (50-500ms per LLM call). Use only when naive retrieval fails.

## 5. Re-Ranking

Retrieve top-k (e.g., k=50) with cheap method, then re-rank with expensive method.

```
Step 1: candidates = hybrid_search(query, top_k=50)      # 5ms
Step 2: reranked = cross_encoder.rerank(query, candidates) # 50ms
Step 3: final = reranked[:10]                              # keep top 10
```

### Re-Ranker Options

| Method | Latency | Recall Improvement | Cost |
|---|---|---|---|
| Cross-encoder (MiniLM) | 3-5ms per passage | +3-5% | Low |
| Cross-encoder (BGE-reranker) | 10-20ms per passage | +5-8% | Medium |
| Cohere Rerank API | 50-100ms (API) | +5-10% | $ per query |
| ColBERT (late interaction) | 2-5ms per passage | +4-7% | Low |

**Rule of thumb:** Re-rank top-50 into top-10. Re-ranking top-100 gives marginal improvement.

## 6. Multi-Hop Retrieval

When a single retrieval pass is insufficient, iterate:

```
Query: "What was the impact of the European strategy change on Q3 revenue?"
    ↓
Hop 1: Retrieve passages about "European strategy change Q3"
        → LLM identifies: "strategy change mentioned in board minutes doc"
    ↓
Hop 2: Retrieve board minutes document → extract strategy details
        → LLM identifies: "strategy change was 'expand Nordic markets'"
    ↓
Hop 3: Retrieve Nordic Q3 revenue data → final answer
```

Each hop is: retrieve → extract entities/facts → formulate new query → retrieve.

**Complexity:** O(hops × retrieval_cost). Rarely exceeds 2-3 hops in production.

## 7. Contextual Retrieval (Anthropic)

Augment each chunk with surrounding document context before embedding:

```
Original chunk: "Revenue grew 15% YoY"
    ↓
Augmented: "This passage is from the Q3 2024 earnings report for European
            division. The report discusses financial performance with focus
            on revenue growth."
    ↓
Embed and index the augmented version
```

Anthropic reports this reduces retrieval failures by 35-49% at 7× the embedding cost (augmentation + original).

## Choosing a Strategy

| Scenario | Strategy |
|---|---|
| Simple Q&A, fact lookup | Hybrid search |
| Complex, multi-faceted queries | Query decomposition + hybrid |
| High precision required | Hybrid + re-ranker |
| Long documents, deep reasoning | Multi-hop retrieval |
| Exact match critical (codes, names) | BM25 boost in hybrid (weighted) |
| Low latency budget (< 50ms) | Dense only, skip re-ranker |
| Highest possible recall | Multi-hop + HyDE + re-ranker |

"""
Implement hybrid search: BM25 + dense embeddings + RRF fusion.

Run: python 04-hybrid-search-implementation.py

Requirements: pip install sentence-transformers rank-bm25 numpy
"""

from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np

# ─── Corpus ───
DOCUMENTS = [
    "Python is a high-level programming language.",
    "JavaScript is used for web development.",
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning uses neural networks with multiple layers.",
    "The CPU executes instructions in a computer.",
    "GPU acceleration speeds up parallel computations.",
    "Cloud computing offers scalable resources on demand.",
    "Docker containers package applications for portability.",
    "Kubernetes orchestrates containerized applications.",
    "Natural language processing helps computers understand text.",
    "Computer vision enables machines to interpret images.",
    "Reinforcement learning trains agents through rewards.",
]

QUERIES = [
    "programming languages",
    "neural networks and deep learning",
    "cloud and containers",
    "computer hardware acceleration",
    "AI and machine learning techniques",
]

print("=== Hybrid Search: BM25 + Dense + RRF ===\n")

# ─── Dense embeddings ───
model = SentenceTransformer("all-MiniLM-L6-v2")
doc_emb = model.encode(DOCUMENTS)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

# ─── BM25 index ───
tokenized_docs = [doc.lower().split() for doc in DOCUMENTS]
bm25 = BM25Okapi(tokenized_docs)

# ─── Search functions ───
def dense_search(query, top_k=5):
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    scores = doc_emb @ q_emb.T
    top = np.argsort(scores.squeeze())[::-1][:top_k]
    return [(i, float(scores[i])) for i in top]

def sparse_search(query, top_k=5):
    scores = bm25.get_scores(query.lower().split())
    top = np.argsort(scores)[::-1][:top_k]
    return [(i, float(scores[i])) for i in top]

def rrf_fusion(dense_results, sparse_results, k=60):
    """Reciprocal Rank Fusion."""
    scores = {}
    for rank, (doc_id, _) in enumerate(dense_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    for rank, (doc_id, _) in enumerate(sparse_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# ─── Compare search methods ───
for query in QUERIES:
    print(f"Query: {query}")
    
    dense = dense_search(query, top_k=10)
    sparse = sparse_search(query, top_k=10)
    hybrid = rrf_fusion(dense, sparse)
    
    print(f"{'Method':<10} {'Result':<60} {'Score':<8}")
    print("-" * 80)
    
    print(f"{'Dense':<10}")
    for i, (doc_id, score) in enumerate(dense[:3]):
        print(f"  {i+1}. {DOCUMENTS[doc_id]:<55} {score:.4f}")
    
    print(f"{'Sparse':<10}")
    for i, (doc_id, score) in enumerate(sparse[:3]):
        print(f"  {i+1}. {DOCUMENTS[doc_id]:<55} {score:.4f}")
    
    print(f"{'Hybrid':<10}")
    for i, (doc_id, score) in enumerate(hybrid[:3]):
        print(f"  {i+1}. {DOCUMENTS[doc_id]:<55} {score:.4f}")
    print()

# ─── RRF alpha tuning ───
print("=== Impact of Fusion Weight ===")
for alpha in [0.0, 0.3, 0.5, 0.7, 1.0]:
    query = "programming languages"
    dense = dense_search(query, top_k=10)
    sparse = sparse_search(query, top_k=10)
    hybrid = rrf_fusion(dense, sparse)
    print(f"  alpha={alpha:.1f}: top result = {DOCUMENTS[hybrid[0][0]][:40]}")

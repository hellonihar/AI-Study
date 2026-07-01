"""
Retrieval evaluation harness: compute recall@k, MRR, NDCG.

Run: python 06-evaluate-retrieval.py

Requirements: pip install sentence-transformers numpy
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# ─── Labeled dataset: query → list of relevant document indices ───
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
    "The database stores and retrieves structured data efficiently.",
    "An API defines how different software components communicate.",
    "Version control tracks changes to code over time.",
]

# Each query has 1-3 relevant document indices
QUERIES = [
    ("programming language", [0, 1]),
    ("machine learning techniques", [2, 3, 11]),
    ("computer hardware", [4, 5]),
    ("cloud infrastructure", [6, 7, 8]),
    ("AI applications", [2, 10, 11]),
]

print("=== Retrieval Evaluation ===\n")

# ─── Model setup ───
model = SentenceTransformer("all-MiniLM-L6-v2")
doc_emb = model.encode(DOCUMENTS)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

def retrieve(query, top_k=10):
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    scores = doc_emb @ q_emb.T
    top = np.argsort(scores.squeeze())[::-1][:top_k]
    return list(top), scores.squeeze()[top]

# ─── Metrics ───
def recall_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    hits = sum(1 for r in relevant if r in retrieved_k)
    return hits / len(relevant) if relevant else 0

def mrr(retrieved, relevant):
    for rank, doc_id in enumerate(retrieved):
        if doc_id in relevant:
            return 1 / (rank + 1)
    return 0

def ndcg_at_k(retrieved, relevant, k):
    dcg = 0.0
    for i, doc_id in enumerate(retrieved[:k]):
        if doc_id in relevant:
            rel = 2.0  # binary relevance
            dcg += (2 ** rel - 1) / np.log2(i + 2)
    # IDCG: ideal DCG
    n_rel = min(len(relevant), k)
    idcg = sum((2 ** 2 - 1) / np.log2(i + 2) for i in range(n_rel))
    return dcg / idcg if idcg > 0 else 0

# ─── Run evaluation ───
all_recall_5 = []
all_recall_10 = []
all_mrr = []
all_ndcg_10 = []

for query, relevant in QUERIES:
    retrieved, scores = retrieve(query, top_k=10)
    
    r5 = recall_at_k(retrieved, relevant, 5)
    r10 = recall_at_k(retrieved, relevant, 10)
    m = mrr(retrieved, relevant)
    n = ndcg_at_k(retrieved, relevant, 10)
    
    all_recall_5.append(r5)
    all_recall_10.append(r10)
    all_mrr.append(m)
    all_ndcg_10.append(n)
    
    print(f"Query: {query}")
    print(f"  Relevant docs: {relevant}")
    print(f"  Retrieved indices: {retrieved[:5]}")
    print(f"  Recall@5:  {r5:.3f}")
    print(f"  Recall@10: {r10:.3f}")
    print(f"  MRR:       {m:.3f}")
    print(f"  NDCG@10:   {n:.3f}")
    print()

# ─── Summary ───
print("=== Summary ===")
print(f"{'Metric':<15} {'Avg':<8} {'Min':<8} {'Max':<8}")
print("-" * 40)
print(f"{'Recall@5':<15} {np.mean(all_recall_5):<8.3f} {np.min(all_recall_5):<8.3f} {np.max(all_recall_5):<8.3f}")
print(f"{'Recall@10':<15} {np.mean(all_recall_10):<8.3f} {np.min(all_recall_10):<8.3f} {np.max(all_recall_10):<8.3f}")
print(f"{'MRR':<15} {np.mean(all_mrr):<8.3f} {np.min(all_mrr):<8.3f} {np.max(all_mrr):<8.3f}")
print(f"{'NDCG@10':<15} {np.mean(all_ndcg_10):<8.3f} {np.min(all_ndcg_10):<8.3f} {np.max(all_ndcg_10):<8.3f}")

# ─── Sample size significance ───
print("\n=== Statistical Significance ===")
print(f"With {len(QUERIES)} queries, metric variance is high.")
print("For reliable eval, use 500+ labeled queries.")
print("95% CI width ≈ 1.96 × std / sqrt(n)")
for metric, values in [
    ("Recall@10", all_recall_10),
]:
    ci = 1.96 * np.std(values) / np.sqrt(len(values))
    print(f"  {metric}: {np.mean(values):.3f} ± {ci:.3f}")

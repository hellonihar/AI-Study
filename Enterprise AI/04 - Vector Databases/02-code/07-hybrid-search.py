"""
Hybrid search: dense (cosine) + sparse (BM25) + metadata filtering with RRF fusion.

Run: python 07-hybrid-search.py

Requirements: pip install sentence-transformers rank-bm25 numpy
"""

import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS = [
    "Python is a high-level programming language with dynamic typing.",
    "JavaScript is the primary language for web frontend development.",
    "Rust is a systems language focused on memory safety without GC.",
    "PostgreSQL is an ACID-compliant relational database.",
    "Redis is an in-memory key-value store used for caching.",
    "Kubernetes orchestrates containerized applications across nodes.",
    "Docker packages applications with their dependencies into containers.",
    "TensorFlow is an ML framework developed by Google.",
    "PyTorch is an ML framework developed by Meta AI.",
    "React is a JavaScript library for building user interfaces.",
    "FastAPI is a high-performance Python web framework.",
    "Nginx is a reverse proxy server and load balancer.",
    "Linux is the most widely used server operating system.",
    "AWS S3 provides object storage with 99.999999999% durability.",
    "Terraform manages infrastructure as code across cloud providers.",
    "GraphQL is a query language for APIs developed by Meta.",
    "gRPC is a high-performance RPC framework using Protocol Buffers.",
    "Apache Kafka is a distributed event streaming platform.",
    "Prometheus is a monitoring system with a time-series database.",
    "Git is a distributed version control system for tracking changes.",
]

QUERIES = [
    "programming language for web development",
    "database and storage systems",
    "machine learning frameworks",
    "infrastructure and deployment",
]

print("=== Hybrid Search: Dense + Sparse + Metadata Filters ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_emb = model.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

from rank_bm25 import BM25Okapi

tokenized_docs = [doc.lower().split() for doc in DOCUMENTS]
bm25 = BM25Okapi(tokenized_docs)

def dense_search(query, top_k=10):
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    scores = (doc_emb @ q_emb.T).squeeze()
    indices = np.argsort(scores)[::-1][:top_k]
    return list(zip(indices, scores[indices]))

def sparse_search(query, top_k=10):
    scores = bm25.get_scores(query.lower().split())
    indices = np.argsort(scores)[::-1][:top_k]
    return list(zip(indices, scores[indices]))

def rrf_fusion(dense_results, sparse_results, k=60):
    scores = {}
    for rank, (idx, _) in enumerate(dense_results):
        scores[idx] = scores.get(idx, 0) + 1 / (k + rank + 1)
    for rank, (idx, _) in enumerate(sparse_results):
        scores[idx] = scores.get(idx, 0) + 1 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

print("=== Search Methods Compared ===\n")
for query in QUERIES:
    dense = dense_search(query, top_k=5)
    sparse = sparse_search(query, top_k=5)
    fused = rrf_fusion(dense, sparse[:10], k=60)

    print(f"Query: {query}")
    print(f"  {'Dense (cosine)':<35} {'Sparse (BM25)':<35} {'Hybrid (RRF)':<35}")
    print(f"  {'-'*35} {'-'*35} {'-'*35}")

    for i in range(max(len(dense), len(sparse), len(fused))):
        d_str = f"[{dense[i][1]:.4f}] {DOCUMENTS[dense[i][0]][:25]}" if i < len(dense) else ""
        s_str = f"[{sparse[i][1]:.4f}] {DOCUMENTS[sparse[i][0]][:25]}" if i < len(sparse) else ""
        f_str = f"[{fused[i][1]:.4f}] {DOCUMENTS[fused[i][0]][:25]}" if i < len(fused) else ""
        print(f"  {d_str:<35} {s_str:<35} {f_str:<35}")
    print()

print("=== Metadata Filter Pre-Filter (Simulated) ===")
categories = {
    "lang": [0, 1, 2],
    "db": [3, 4],
    "infra": [5, 6, 11, 12, 13, 14, 17, 18],
    "ml": [7, 8],
    "web": [9, 10],
    "tool": [15, 16, 19],
}
inv_cat = {i: cat for cat, ids in categories.items() for i in ids}
cat_labels = [inv_cat[i] for i in range(len(DOCUMENTS))]

def hybrid_with_filter(query, allowed_categories, top_k=5):
    dense = dense_search(query, top_k=20)
    sparse = sparse_search(query, top_k=20)
    fused = rrf_fusion(dense, sparse, k=60)
    filtered = [(idx, score) for idx, score in fused if cat_labels[idx] in allowed_categories]
    return filtered[:top_k]

query = "large scale data storage"
results = hybrid_with_filter(query, ["db", "infra"])
print(f"\nQuery: '{query}'  (filter: db, infra)")
for idx, score in results:
    print(f"  [{score:.4f}] [{cat_labels[idx]}] {DOCUMENTS[idx][:50]}")

print("\n=== RRF Constant Sensitivity ===")
query = "web application framework"
dense = dense_search(query, top_k=20)
sparse = sparse_search(query, top_k=20)
for k_val in [30, 60, 100]:
    fused = rrf_fusion(dense, sparse, k=k_val)
    print(f"  k={k_val}: top = [{fused[0][1]:.4f}] {DOCUMENTS[fused[0][0]][:40]}")
print("  Lower k = more emphasis on high ranks (favors consensus).")
print("  Higher k = more weight to rank position differences.")

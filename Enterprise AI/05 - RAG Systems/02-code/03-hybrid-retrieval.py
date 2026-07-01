"""
Hybrid retrieval: dense + sparse + RRF fusion for RAG.

Run: python 03-hybrid-retrieval.py

Requirements: pip install sentence-transformers rank-bm25 numpy
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

DOCUMENTS = [
    "Python is a high-level programming language with dynamic typing.",
    "JavaScript is the primary language for web frontend development.",
    "Rust is a systems language focused on memory safety without a garbage collector.",
    "PostgreSQL is an ACID-compliant relational database management system.",
    "Redis is an in-memory key-value store used extensively for caching.",
    "Kubernetes orchestrates containerized applications across clusters of machines.",
    "Docker packages applications with their dependencies into lightweight containers.",
    "TensorFlow is an open-source machine learning framework developed by Google.",
    "PyTorch is an open-source machine learning framework developed by Meta AI.",
    "React is a JavaScript library for building interactive user interfaces.",
    "FastAPI is a modern, high-performance web framework for building APIs with Python.",
    "Nginx is a high-performance reverse proxy server and load balancer.",
    "Linux is the most widely used server operating system in the world.",
    "AWS S3 provides scalable object storage with 99.999999999% durability.",
    "Terraform enables infrastructure as code across multiple cloud providers.",
    "GraphQL is a query language for APIs that was developed by Meta.",
    "gRPC is a high-performance remote procedure call framework using Protocol Buffers.",
    "Apache Kafka is a distributed event streaming platform for real-time data pipelines.",
    "Prometheus is an open-source monitoring system with a time-series database.",
    "Git is a distributed version control system for tracking changes in source code.",
]

QUERIES = [
    "programming language for web applications",
    "database and caching systems",
    "infrastructure deployment and container management",
    "monitoring and observability tools",
]

print("=== Hybrid Retrieval for RAG ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_emb = model.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

tokenized_docs = [doc.lower().split() for doc in DOCUMENTS]
bm25 = BM25Okapi(tokenized_docs)

def dense_search(query, top_k=20):
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    scores = (doc_emb @ q_emb.T).squeeze()
    indices = np.argsort(scores)[::-1][:top_k]
    return [(idx, float(scores[idx])) for idx in indices]

def sparse_search(query, top_k=20):
    scores = bm25.get_scores(query.lower().split())
    indices = np.argsort(scores)[::-1][:top_k]
    return [(idx, float(scores[idx])) for idx in indices]

def rrf(dense_results, sparse_results, k=60):
    scores = {}
    for rank, (idx, _) in enumerate(dense_results):
        scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
    for rank, (idx, _) in enumerate(sparse_results):
        scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def hybrid_search(query, top_k=10):
    dense = dense_search(query, top_k=50)
    sparse = sparse_search(query, top_k=50)
    fused = rrf(dense, sparse)
    return [(idx, score) for idx, score in fused[:top_k]]

def calculate_recall(retrieved_ids, relevant_ids):
    if not relevant_ids:
        return 0.0
    hits = sum(1 for r in retrieved_ids if r in relevant_ids)
    return hits / len(relevant_ids)

QUERY_RELEVANCE = {
    "programming language for web applications": [0, 1, 9, 10],
    "database and caching systems": [3, 4, 13],
    "infrastructure deployment and container management": [5, 6, 11, 14],
    "monitoring and observability tools": [18, 19],
}

print(f"{'Query':<45} {'Dense Recall':<15} {'Sparse Recall':<15} {'Hybrid Recall':<15}")
print("-" * 90)

for query in QUERIES:
    relevant = QUERY_RELEVANCE.get(query, [])

    dense_results = dense_search(query, top_k=10)
    dense_recall = calculate_recall([idx for idx, _ in dense_results], relevant)

    sparse_results = sparse_search(query, top_k=10)
    sparse_recall = calculate_recall([idx for idx, _ in sparse_results], relevant)

    hybrid_results = hybrid_search(query, top_k=10)
    hybrid_recall = calculate_recall([idx for idx, _ in hybrid_results], relevant)

    print(f"{query[:42]:<45} {dense_recall:<15.2f} {sparse_recall:<15.2f} {hybrid_recall:<15.2f}")

print("\n=== Detailed Results for Sample Query ===")
sample_query = "database and caching systems"
dense = dense_search(sample_query, top_k=5)
sparse = sparse_search(sample_query, top_k=5)
hybrid = hybrid_search(sample_query, top_k=5)

print(f"\nQuery: '{sample_query}'")
print(f"\n{'#':<3} {'Dense':<55} {'Score':<10}")
for i, (idx, score) in enumerate(dense):
    print(f"{i+1:<3} {DOCUMENTS[idx][:50]:<55} {score:.4f}")

print(f"\n{'#':<3} {'Sparse (BM25)':<55} {'Score':<10}")
for i, (idx, score) in enumerate(sparse):
    print(f"{i+1:<3} {DOCUMENTS[idx][:50]:<55} {score:.4f}")

print(f"\n{'#':<3} {'Hybrid (RRF)':<55} {'Score':<10}")
for i, (idx, score) in enumerate(hybrid):
    print(f"{i+1:<3} {DOCUMENTS[idx][:50]:<55} {score:.4f}")

print("\n=== Recall by k ===")
for q in QUERIES:
    relevant = QUERY_RELEVANCE.get(q, [])
    print(f"\n{q[:40]}")
    for k in [1, 3, 5, 10, 20]:
        dense_r = calculate_recall([idx for idx, _ in dense_search(q, top_k=k)], relevant)
        sparse_r = calculate_recall([idx for idx, _ in sparse_search(q, top_k=k)], relevant)
        hybrid_r = calculate_recall([idx for idx, _ in hybrid_search(q, top_k=k)], relevant)
        print(f"  k={k:<3} Dense={dense_r:.2f}  Sparse={sparse_r:.2f}  Hybrid={hybrid_r:.2f}")

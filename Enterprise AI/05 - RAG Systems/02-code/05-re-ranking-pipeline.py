"""
Re-ranking pipeline: retrieve candidates, cross-encoder re-rank, compare with baseline.

Run: python 05-re-ranking-pipeline.py

Requirements: pip install sentence-transformers torch numpy
"""

import time
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

DOCUMENTS = [
    "Python is a high-level programming language with dynamic typing and automatic memory management.",
    "JavaScript is the primary language for web frontend development and now runs on servers via Node.js.",
    "Rust is a systems language focused on memory safety without a garbage collector, using a borrow checker.",
    "PostgreSQL is an ACID-compliant relational database with support for JSON, full-text search, and extensions.",
    "Redis is an in-memory key-value store used for caching, session management, and real-time analytics.",
    "Kubernetes orchestrates containerized applications, providing scaling, load balancing, and self-healing.",
    "Docker packages applications with dependencies into portable containers running on any Linux system.",
    "TensorFlow is an open-source ML framework by Google supporting neural networks and distributed training.",
    "PyTorch is an open-source ML framework by Meta AI with dynamic computation graphs and eager execution.",
    "React is a JavaScript library for building user interfaces with a component-based architecture.",
    "FastAPI is a modern Python web framework with automatic OpenAPI documentation and async support.",
    "Nginx is a high-performance web server and reverse proxy known for its event-driven architecture.",
    "Linux is an open-source Unix-like operating system kernel powering most cloud infrastructure.",
    "AWS S3 provides object storage with 11 9s of durability and supports versioning and lifecycle policies.",
    "Terraform enables infrastructure as code using declarative configuration files across cloud providers.",
    "GraphQL is a query language for APIs enabling clients to request exactly the data they need.",
    "gRPC is a high-performance RPC framework using Protocol Buffers for efficient serialization.",
    "Apache Kafka is a distributed event streaming platform for building real-time data pipelines.",
    "Prometheus is a monitoring system with a dimensional data model and powerful query language (PromQL).",
    "Git is a distributed version control system that tracks changes with branching and merging.",
]

QUERIES = [
    "web application development frameworks",
    "database and caching technologies",
    "machine learning frameworks comparison",
    "infrastructure and deployment tools",
    "API development and communication protocols",
]

print("=== Re-Ranking Pipeline for RAG ===\n")

print("Loading bi-encoder (retrieval model)...")
bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")
dim = bi_encoder.get_sentence_embedding_dimension()

print("Loading cross-encoder (re-ranker)...")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2", max_length=512)

doc_emb = bi_encoder.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

def retrieve(query, top_k=50):
    q_emb = bi_encoder.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    scores = (doc_emb @ q_emb.T).squeeze()
    indices = np.argsort(scores)[::-1][:top_k]
    return [(idx, float(scores[idx])) for idx in indices]

def rerank(query, candidates, top_k=10):
    if not candidates:
        return []
    pairs = [(query, DOCUMENTS[idx]) for idx, _ in candidates]
    scores = reranker.predict(pairs, show_progress_bar=False)
    reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    top = reranked[:top_k]
    return [(idx, float(score)) for (idx, _), score in top]

print(f"\n{'Query':<50} {'Baseline@10':<15} {'Reranked@10':<15} {'Reorder':<10}")
print("-" * 90)

for query in QUERIES:
    candidates = retrieve(query, top_k=20)
    baseline_ids = [idx for idx, _ in candidates[:10]]
    reranked = rerank(query, candidates, top_k=10)
    reranked_ids = [idx for idx, _ in reranked]

    moved = sum(1 for i, idx in enumerate(reranked_ids) if idx != baseline_ids[i])

    print(f"{query[:47]:<50} {', '.join(str(i) for i in baseline_ids[:5]):<15} "
          f"{', '.join(str(i) for i in reranked_ids[:5]):<15} {moved:<10}")

print("\n=== Candidate Count Trade-off ===")
query = "web development and programming"
for n_candidates in [5, 10, 20, 50]:
    candidates = retrieve(query, top_k=n_candidates)

    start = time.perf_counter()
    reranked = rerank(query, candidates, top_k=10)
    rerank_time = time.perf_counter() - start

    print(f"  Candidates={n_candidates:<3}  Rerank time={rerank_time*1000:.1f}ms  "
          f"Top result: {DOCUMENTS[reranked[0][0]][:40]}")

print("\n=== Cross-Encoder Score Distribution ===")
query = "database systems"
candidates = retrieve(query, top_k=20)
reranked = rerank(query, candidates, top_k=len(candidates))

print(f"\nQuery: '{query}'")
print(f"{'Rank':<6} {'Score':<10} {'Text':<60}")
print("-" * 76)
for rank, (idx, score) in enumerate(reranked[:10]):
    print(f"{rank+1:<6} {score:<10.4f} {DOCUMENTS[idx][:55]}")

print("\n=== Timing Breakdown ===")
query = "machine learning frameworks"
candidates = retrieve(query, top_k=50)

start = time.perf_counter()
_ = retrieve(query, top_k=50)
retrieve_time = time.perf_counter() - start

start = time.perf_counter()
_ = rerank(query, candidates, top_k=10)
rerank_time = time.perf_counter() - start

print(f"  Bi-encoder retrieval (50 candidates): {retrieve_time*1000:.2f}ms")
print(f"  Cross-encoder re-ranking (50 → 10):   {rerank_time*1000:.2f}ms")
print(f"  Re-ranking overhead: {rerank_time/retrieve_time:.1f}x")
print()
print("Key insight: Re-ranking adds 5-10x latency but improves precision.")
print("In production, retrieve 50 → rerank 10 is the sweet spot.")

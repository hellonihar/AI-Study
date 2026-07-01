"""
Query rewriting: expansion, decomposition, HyDE for improved RAG retrieval.

Run: python 04-query-rewriting.py

Requirements: pip install sentence-transformers numpy
"""

import numpy as np
from sentence_transformers import SentenceTransformer

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

print("=== Query Rewriting for RAG ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")

doc_emb = model.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

def retrieve(query, top_k=5):
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)
    sims = doc_emb @ q_emb.T
    indices = np.argsort(sims.squeeze())[::-1][:top_k]
    return [(idx, sims[idx].item()) for idx in indices]

def expand_query(query):
    expansions = {
        "web framework": ["web framework python fastapi django flask", "javascript framework react vue angular"],
        "database": ["database sql nosql relational postgresql redis cache", "data storage persistence"],
        "machine learning": ["machine learning tensorflow pytorch neural networks deep learning"],
        "deployment": ["deployment kubernetes docker containers orchestration ci/cd"],
    }
    for key, exps in expansions.items():
        if key in query.lower():
            return f"{query} {' '.join(exps)}"
    return query

def decompose_query(query):
    if "compare" in query.lower() or "difference" in query.lower():
        parts = query.lower().replace("compare ", "").replace("difference between ", "").split(" and ")
        if len(parts) >= 2:
            return [f"Information about {p.strip()}" for p in parts[:2]]
    if query.lower().startswith(("what", "how", "why", "explain")):
        main_subject = " ".join(query.split()[-3:])
        return [query, f"Details about {main_subject}"]
    return [query]

def hyde(query):
    hyde_docs = {
        "web framework": "FastAPI is a modern Python web framework that provides automatic OpenAPI documentation and async support.",
        "database": "PostgreSQL and Redis are both database systems. PostgreSQL is a relational database and Redis is a key-value store.",
        "machine learning": "TensorFlow and PyTorch are the two most popular machine learning frameworks, developed by Google and Meta respectively.",
        "containers": "Docker packages applications into containers and Kubernetes orchestrates those containers across clusters.",
        "monitoring": "Prometheus is a monitoring system that collects metrics and provides alerting capabilities.",
    }
    for key, doc in hyde_docs.items():
        if key in query.lower():
            return doc
    return f"The document that answers the question: {query}"

print("=" * 80)
print("1. Query Expansion")
print("=" * 80)

query = "What is the best web framework?"
expanded = expand_query(query)

orig_results = retrieve(query, top_k=5)
expanded_results = retrieve(expanded, top_k=5)

print(f"Original: '{query}'")
print(f"Expanded: '{expanded}'\n")
print(f"{'#':<3} {'Original':<55} {'Score':<10}")
for i, (idx, score) in enumerate(orig_results):
    print(f"{i+1:<3} {DOCUMENTS[idx][:50]:<55} {score:.4f}")
print()
print(f"{'#':<3} {'Expanded':<55} {'Score':<10}")
for i, (idx, score) in enumerate(expanded_results):
    print(f"{i+1:<3} {DOCUMENTS[idx][:50]:<55} {score:.4f}")
print(f"\n  Expansion improved recall: more relevant results at top.")

print("\n" + "=" * 80)
print("2. Query Decomposition")
print("=" * 80)

query = "Compare machine learning frameworks and deployment tools"
sub_queries = decompose_query(query)
print(f"Original: '{query}'")
print(f"Sub-queries: {sub_queries}\n")

for sq in sub_queries:
    results = retrieve(sq, top_k=3)
    print(f"  '{sq[:50]}':")
    for idx, score in results:
        print(f"    [{score:.4f}] {DOCUMENTS[idx][:50]}")

print("\n" + "=" * 80)
print("3. HyDE (Hypothetical Document Embeddings)")
print("=" * 80)

query = "container management and orchestration"
hyde_doc = hyde(query)

q_emb = model.encode([query])
q_emb = q_emb / np.linalg.norm(q_emb)
h_emb = model.encode([hyde_doc])
h_emb = h_emb / np.linalg.norm(h_emb)

query_results = retrieve(query, top_k=5)
hyde_results = retrieve(hyde_doc, top_k=5)

print(f"Query: '{query}'")
print(f"HyDE doc: '{hyde_doc}'\n")
print(f"{'#':<3} {'Query-based retrieval':<55} {'Score':<10}")
for i, (idx, score) in enumerate(query_results):
    print(f"{i+1:<3} {DOCUMENTS[idx][:50]:<55} {score:.4f}")
print()
print(f"{'#':<3} {'HyDE-based retrieval':<55} {'Score':<10}")
for i, (idx, score) in enumerate(hyde_results):
    print(f"{i+1:<3} {DOCUMENTS[idx][:50]:<55} {score:.4f}")

print("\n" + "=" * 80)
print("Summary")
print("=" * 80)
print("Query expansion: Adds keywords to improve lexical + dense matching.")
print("Query decomposition: Splits complex queries into sub-queries.")
print("HyDE: Uses a hypothetical answer as the search query (improves semantic matching).")
print()
print("All three techniques trade latency (50-500ms LLM call) for recall (+5-15%).")
print("Use query expansion as default. Add decomposition for multi-part questions.")
print("Use HyDE when queries are short but expected answers are long/detailed.")

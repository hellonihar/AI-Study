"""
FAISS HNSW index: build, search, analyze recall vs speed trade-offs.

Run: python 02-faiss-hnsw-local.py

Requirements: pip install sentence-transformers faiss-cpu numpy
"""

import time
import numpy as np
from sentence_transformers import SentenceTransformer

DOCUMENTS = [
    "Python is a high-level interpreted programming language with dynamic semantics.",
    "Machine learning is a subset of artificial intelligence focused on pattern recognition.",
    "The Great Wall of China stretches over 13,000 miles across northern China.",
    "Photosynthesis converts light energy into chemical energy in plants.",
    "A CPU executes instructions fetched from memory using the fetch-decode-execute cycle.",
    "Shakespeare wrote 37 plays including tragedies, comedies, and histories.",
    "Cloud computing delivers compute, storage, and networking on demand.",
    "The human brain contains roughly 86 billion neurons connected by synapses.",
    "Quantum computing uses qubits that can exist in superposition states.",
    "DNA stores genetic information in a double-helix structure of base pairs.",
    "Natural language processing enables machines to parse and generate human language.",
    "The Earth orbits the Sun at 29.8 km/s, completing one revolution every 365.25 days.",
    "Kubernetes orchestrates containerized workloads across clusters of machines.",
    "PostgreSQL is a relational database management system with ACID compliance.",
    "PyTorch provides automatic differentiation for building neural networks.",
    "Redis is an in-memory data structure store used as a cache and message broker.",
    "Docker containers package software with their dependencies for portability.",
    "TensorFlow is an end-to-end open-source platform for machine learning.",
    "The Linux kernel manages processes, memory, and hardware abstraction.",
    "HTTP is the foundation protocol for data communication on the World Wide Web.",
    "JSON is a lightweight data-interchange format that is human-readable.",
    "GraphQL provides a query language for APIs with client-specified responses.",
    "Rust is a systems programming language focused on memory safety and performance.",
    "Denormalization in databases trades write efficiency for read performance.",
    "Load balancing distributes network traffic across multiple servers.",
]

QUERIES = [
    "interpreted programming language",
    "artificial intelligence patterns",
    "energy conversion in nature",
    "computer architecture",
    "web communication protocols",
    "database management systems",
    "container orchestration",
]

print("=== FAISS HNSW Index Demo ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")
dim = model.get_sentence_embedding_dimension()
print(f"Model dimension: {dim}")

doc_emb = model.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

import faiss

M = 16
ef_construction = 40
ef_search = 16

index_hnsw = faiss.IndexHNSWFlat(dim, M, faiss.METRIC_INNER_PRODUCT)
index_hnsw.hnsw.efConstruction = ef_construction
index_hnsw.hnsw.efSearch = ef_search

print(f"Building HNSW with M={M}, efConstruction={ef_construction}...")
start = time.perf_counter()
index_hnsw.add(doc_emb.astype(np.float32))
build_time = time.perf_counter() - start
print(f"Build time: {build_time:.3f}s")
print(f"Index size: {index_hnsw.ntotal} vectors")

brute_force = faiss.IndexIDMap(faiss.IndexFlatIP(dim))
brute_force.add_with_ids(doc_emb.astype(np.float32), np.arange(len(DOCUMENTS), dtype=np.int64))

def search_hnsw(query_emb, k=3):
    sims, ids = index_hnsw.search(query_emb.reshape(1, -1).astype(np.float32), k)
    return ids[0], sims[0]

def search_bf(query_emb, k=3):
    sims, ids = brute_force.search(query_emb.reshape(1, -1).astype(np.float32), k)
    return ids[0], sims[0]

print("\n=== Query Results (HNSW vs Brute Force) ===")
for query in QUERIES:
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)

    hnsw_ids, hnsw_sims = search_hnsw(q_emb)
    bf_ids, bf_sims = search_bf(q_emb)

    print(f"\nQuery: {query}")
    print(f"  {'HNSW':<30} {'Brute Force':<30}")
    for i in range(len(hnsw_ids)):
        hnsw_doc = DOCUMENTS[hnsw_ids[i]]
        bf_doc = DOCUMENTS[bf_ids[i]]
        print(f"  [{hnsw_sims[i]:.4f}] {hnsw_doc[:35]:<35}  [{bf_sims[i]:.4f}] {bf_doc[:35]:<35}")

print("\n=== efSearch Trade-off Analysis ===")
q_test = model.encode(["test query"])
q_test = q_test / np.linalg.norm(q_test)

for ef_val in [4, 8, 16, 32, 64, 128]:
    index_hnsw.hnsw.efSearch = ef_val

    start = time.perf_counter()
    for _ in range(1000):
        index_hnsw.search(q_test.reshape(1, -1).astype(np.float32), 10)
    lat = (time.perf_counter() - start) / 1000 * 1000

    recalls = []
    for i, doc in enumerate(DOCUMENTS):
        q_emb = model.encode([doc])
        q_emb = q_emb / np.linalg.norm(q_emb)
        hnsw_ids, _ = search_hnsw(q_emb, k=10)
        bf_ids, _ = search_bf(q_emb, k=10)
        recalls.append(
            sum(1 for id_ in bf_ids if id_ in hnsw_ids) / len(bf_ids)
        )

    print(f"  efSearch={ef_val:<3}  Recall@10={np.mean(recalls):.3f}  "
          f"Latency={lat:.3f}ms  QPS={1000/lat:.0f}")

print("\n=== HNSW Parameters Guide ===")
print("  M:                Recall vs. memory. 16 is typical. 32 for high recall, 8 for low memory.")
print("  efConstruction:   Build quality vs. build time. 40-100 typical. Higher = better recall.")
print("  efSearch:         Search accuracy vs. latency. 16-64 typical. Double for ~2% recall gain.")
print(f"\n  Current memory estimate: ~{index_hnsw.ntotal * dim * 4 / 1024 / 1024:.1f} MB (vectors only)")
print("  HNSW adds ~8 bytes per edge: M * 2 * ntotal * 4 bytes for graph structure.")

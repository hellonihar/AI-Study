"""
FAISS IVF index: train, add, search, compare with brute force.

Run: python 01-faiss-ivf-local.py

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
]

QUERIES = [
    "interpreted programming language",
    "artificial intelligence patterns",
    "ancient fortifications",
    "energy conversion in nature",
    "computer architecture fundamentals",
]

print("=== FAISS IVF Index Demo ===\n")

model = SentenceTransformer("all-MiniLM-L6-v2")
dim = model.get_sentence_embedding_dimension()
print(f"Model dimension: {dim}")

doc_emb = model.encode(DOCUMENTS, show_progress_bar=False)
doc_emb = doc_emb / np.linalg.norm(doc_emb, axis=1, keepdims=True)

nlist = 4
nprobe = 2

import faiss

quantizer = faiss.IndexFlatIP(dim)
index_ivf = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)

print(f"Training IVF with {nlist} centroids...")
index_ivf.train(doc_emb.astype(np.float32))
index_ivf.add(doc_emb.astype(np.float32))
index_ivf.nprobe = nprobe

brute_force = faiss.IndexIDMap(faiss.IndexFlatIP(dim))
brute_force.add_with_ids(doc_emb.astype(np.float32), np.arange(len(DOCUMENTS), dtype=np.int64))

print(f"Index size (IVF): {faiss.deprecated_GETINDEXSIZE}} vectors")

def search(index, query_emb, k=3):
    if isinstance(index, faiss.IndexIVFFlat):
        index.nprobe = nprobe
    sims, ids = index.search(query_emb.reshape(1, -1).astype(np.float32), k)
    return ids[0], sims[0]

for query in QUERIES:
    q_emb = model.encode([query])
    q_emb = q_emb / np.linalg.norm(q_emb)

    ivf_ids, ivf_sims = search(index_ivf, q_emb)
    bf_ids, bf_sims = search(brute_force, q_emb)

    print(f"\nQuery: {query}")
    print(f"  {'IVF':<25} {'Brute Force':<25}")
    for i in range(len(ivf_ids)):
        ivf_doc = DOCUMENTS[ivf_ids[i]] if ivf_ids[i] != -1 else "(not found)"
        bf_doc = DOCUMENTS[bf_ids[i]] if bf_ids[i] != -1 else "(not found)"
        print(f"  [{ivf_sims[i]:.4f}] {ivf_doc[:40]:<40}  [{bf_sims[i]:.4f}] {bf_doc[:40]:<40}")

print("\n=== Speed Comparison ===")
n_iter = 1000
q_test = np.random.randn(dim).astype(np.float32)
q_test = q_test / np.linalg.norm(q_test)

start = time.perf_counter()
for _ in range(n_iter):
    index_ivf.search(q_test.reshape(1, -1), 10)
ivf_time = time.perf_counter() - start

start = time.perf_counter()
for _ in range(n_iter):
    brute_force.search(q_test.reshape(1, -1), 10)
bf_time = time.perf_counter() - start

print(f"  IVF ({nlist} centroids, nprobe={nprobe}): {ivf_time:.3f}s ({ivf_time/n_iter*1e6:.1f} us/search)")
print(f"  Brute Force:                       {bf_time:.3f}s ({bf_time/n_iter*1e6:.1f} us/search)")
print(f"  Speedup: {bf_time/ivf_time:.1f}x")

print("\n=== Recall@10: IVF vs Brute Force ===")
all_recall = []
for i, doc in enumerate(DOCUMENTS):
    q_emb = model.encode([doc])
    q_emb = q_emb / np.linalg.norm(q_emb)
    ivf_ids, _ = search(index_ivf, q_emb, k=10)
    bf_ids, _ = search(brute_force, q_emb, k=10)
    recall = sum(1 for id_ in bf_ids if id_ in ivf_ids) / len(bf_ids)
    all_recall.append(recall)

print(f"  Mean Recall@10: {np.mean(all_recall):.3f}")
print(f"  Min Recall@10:  {np.min(all_recall):.3f}")
print(f"  Max Recall@10:  {np.max(all_recall):.3f}")

print("\n=== Effect of nprobe on Trade-offs ===")
for np_val in [1, 2, 4, 8]:
    index_ivf.nprobe = np_val
    start = time.perf_counter()
    for _ in range(500):
        index_ivf.search(q_test.reshape(1, -1), 10)
    lat = (time.perf_counter() - start) / 500 * 1000

    recalls = []
    for i, doc in enumerate(DOCUMENTS):
        q_emb = model.encode([doc])
        q_emb = q_emb / np.linalg.norm(q_emb)
        ivf_ids, _ = search(index_ivf, q_emb, k=10)
        bf_ids, _ = search(brute_force, q_emb, k=10)
        recalls.append(sum(1 for id_ in bf_ids if id_ in ivf_ids) / len(bf_ids))

    print(f"  nprobe={np_val:<2}  Recall@10={np.mean(recalls):.3f}  Latency={lat:.2f}ms")

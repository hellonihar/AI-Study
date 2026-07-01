"""
Single-node ANN benchmark: compare Flat, IVF, HNSW across recall, latency, QPS.

Run: python 08-benchmark-ann.py

Requirements: pip install sentence-transformers faiss-cpu numpy
"""

import time
import warnings
import numpy as np
from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore")

N_DOCS = 10000
N_QUERIES = 100
DIM = 384
TOP_K = 10

print("=== ANN Index Benchmark (Single Node) ===\n")
print(f"Configuration:")
print(f"  Documents: {N_DOCS:,}")
print(f"  Queries:   {N_QUERIES}")
print(f"  Dimension: {DIM}")
print(f"  Top-K:     {TOP_K}")
print()

print("Generating synthetic data (random vectors)...")
rng = np.random.default_rng(42)
doc_vectors = rng.random((N_DOCS, DIM), dtype=np.float32)
doc_vectors = doc_vectors / np.linalg.norm(doc_vectors, axis=1, keepdims=True)

query_vectors = rng.random((N_QUERIES, DIM), dtype=np.float32)
query_vectors = query_vectors / np.linalg.norm(query_vectors, axis=1, keepdims=True)

import faiss

print("\nBuilding indexes...")
indexes = {}

start = time.perf_counter()
flat_index = faiss.IndexFlatIP(DIM)
flat_index.add(doc_vectors)
flat_build = time.perf_counter() - start
indexes["Flat (brute force)"] = flat_index
print(f"  Flat:       built in {flat_build:.3f}s")

for M, ef_c in [(8, 40), (16, 40), (32, 80)]:
    start = time.perf_counter()
    idx = faiss.IndexHNSWFlat(DIM, M, faiss.METRIC_INNER_PRODUCT)
    idx.hnsw.efConstruction = ef_c
    idx.add(doc_vectors)
    t = time.perf_counter() - start
    indexes[f"HNSW M={M} efC={ef_c}"] = idx
    print(f"  HNSW M={M} efC={ef_c}: built in {t:.3f}s")

for nlist in [16, 64, 256]:
    start = time.perf_counter()
    quantizer = faiss.IndexFlatIP(DIM)
    idx = faiss.IndexIVFFlat(quantizer, DIM, nlist, faiss.METRIC_INNER_PRODUCT)
    idx.train(doc_vectors)
    idx.add(doc_vectors)
    t = time.perf_counter() - start
    indexes[f"IVF nlist={nlist}"] = idx
    print(f"  IVF nlist={nlist}:    built in {t:.3f}s")

print("\n=== Benchmark Results ===")
header = f"{'Index':<25} {'Recall@10':<10} {'Latency(ms)':<12} {'QPS':<10} {'Build(s)':<10}"
print(header)
print("-" * len(header))

ground_truth_scores, ground_truth_ids = flat_index.search(query_vectors, TOP_K)

for name, idx in indexes.items():
    ef_search_values = [8, 16, 32, 64]
    if "HNSW" in name:
        for ef in ef_search_values:
            idx.hnsw.efSearch = ef
            q_start = time.perf_counter()
            sims, ids = idx.search(query_vectors, TOP_K)
            q_time = time.perf_counter() - q_start

            recalls = []
            for i in range(N_QUERIES):
                gt_set = set(ground_truth_ids[i])
                pred_set = set(ids[i])
                recalls.append(len(gt_set & pred_set) / TOP_K)
            mean_recall = np.mean(recalls)

            lat_ms = q_time / N_QUERIES * 1000
            qps = N_QUERIES / q_time
            build_t = indexes[name]
            print(f"{f'{name} efS={ef}':<25} {mean_recall:<10.3f} {lat_ms:<12.3f} {qps:<10.0f} {'-':<10}")
    elif "IVF" in name:
        for nprobe in [1, 2, 4, 8, 16]:
            idx.nprobe = nprobe
            q_start = time.perf_counter()
            sims, ids = idx.search(query_vectors, TOP_K)
            q_time = time.perf_counter() - q_start

            recalls = []
            for i in range(N_QUERIES):
                gt_set = set(ground_truth_ids[i])
                pred_set = set(ids[i])
                recalls.append(len(gt_set & pred_set) / TOP_K)
            mean_recall = np.mean(recalls)

            lat_ms = q_time / N_QUERIES * 1000
            qps = N_QUERIES / q_time
            print(f"{f'{name} nprobe={nprobe}':<25} {mean_recall:<10.3f} {lat_ms:<12.3f} {qps:<10.0f} {'-':<10}")
    else:
        q_start = time.perf_counter()
        sims, ids = idx.search(query_vectors, TOP_K)
        q_time = time.perf_counter() - q_start

        lat_ms = q_time / N_QUERIES * 1000
        qps = N_QUERIES / q_time
        print(f"{name:<25} {'1.000':<10} {lat_ms:<12.3f} {qps:<10.0f} {flat_build:<10.3f}")

print("\n" + "=" * 70)
print("Key Takeaways:")
print("  - Flat:     gold standard recall, O(n) latency, fine for <100K vectors")
print("  - HNSW:     best all-around at moderate scale. log(n) search, ~2x memory")
print("  - IVF:      lower memory than HNSW, requires training, recall tuning via nprobe")
print("  - At 10K vectors, Flat is already ~OK. At 1M, difference becomes dramatic.")
print("  - HNSW M=16 efC=40 is a safe default for most production workloads.")

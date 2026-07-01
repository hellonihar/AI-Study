"""
Distributed vector search benchmark: simulate sharding, replication, query routing.

Run: python 09-benchmark-distributed.py

Requirements: pip install numpy
"""

import time
import hashlib
import numpy as np

DIM = 768
N_SHARDS = 4
REPLICATION_FACTOR = 2
N_DOCS = 50000
N_QUERIES = 200
TOP_K = 10

print("=== Distributed Vector Search Simulation ===\n")

rng = np.random.default_rng(42)

class Shard:
    def __init__(self, shard_id, dim):
        self.shard_id = shard_id
        self.vectors = []
        self.ids = []

    def add(self, vec, doc_id):
        self.vectors.append(vec)
        self.ids.append(doc_id)

    def search(self, query, top_k):
        if not self.vectors:
            return [], []
        vecs = np.array(self.vectors, dtype=np.float32)
        sims = vecs @ query
        top_indices = np.argsort(sims)[::-1][:top_k]
        return [self.ids[i] for i in top_indices], sims[top_indices]

class DistributedIndex:
    def __init__(self, n_shards, replication_factor, dim):
        self.primary_shards = [Shard(i, dim) for i in range(n_shards)]
        self.replica_shards = [Shard(i + n_shards, dim) for i in range(replication_factor * n_shards)]
        self.n_shards = n_shards
        self.replication_factor = replication_factor
        self.dim = dim

    def _shard_for(self, doc_id):
        h = int(hashlib.md5(str(doc_id).encode()).hexdigest(), 16)
        return h % self.n_shards

    def add(self, vec, doc_id):
        primary = self._shard_for(doc_id)
        self.primary_shards[primary].add(vec, doc_id)
        for r in range(self.replication_factor):
            replica_idx = primary * self.replication_factor + r
            self.replica_shards[replica_idx].add(vec, doc_id)

    def search(self, query, top_k, fan_out="all"):
        query = query / np.linalg.norm(query)

        if fan_out == "all":
            shards_to_search = range(self.n_shards)
        elif fan_out == "single":
            h = int(hashlib.md5(query.tobytes()).hexdigest(), 16)
            shards_to_search = [h % self.n_shards]
        elif fan_out == "quantized":
            shards_to_search = range(self.n_shards)

        all_results = []
        for s in shards_to_search:
            ids, sims = self.primary_shards[s].search(query, top_k)
            for iid, sim in zip(ids, sims):
                all_results.append((sim, iid))

        all_results.sort(key=lambda x: x[0], reverse=True)
        return all_results[:top_k]

    def search_with_replica(self, query, top_k, replica_failure_rate=0.0):
        query = query / np.linalg.norm(query)
        all_results = []

        for s in range(self.n_shards):
            if rng.random() > replica_failure_rate:
                ids, sims = self.primary_shards[s].search(query, top_k)
            else:
                replica_start = s * self.replication_factor
                for r in range(self.replication_factor):
                    if rng.random() > replica_failure_rate:
                        ids, sims = self.replica_shards[replica_start + r].search(query, top_k)
                        break
                else:
                    continue

            for iid, sim in zip(ids, sims):
                all_results.append((sim, iid))

        all_results.sort(key=lambda x: x[0], reverse=True)
        return all_results[:top_k]

print(f"Generating {N_DOCS} synthetic vectors of dim {DIM}...")
vecs = rng.random((N_DOCS, DIM), dtype=np.float32)
vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

print(f"Building distributed index ({N_SHARDS} shards, RF={REPLICATION_FACTOR})...")
start = time.perf_counter()
dist_index = DistributedIndex(N_SHARDS, REPLICATION_FACTOR, DIM)
for i in range(N_DOCS):
    dist_index.add(vecs[i], i)
build_time = time.perf_counter() - start
print(f"Build time: {build_time:.3f}s")

shard_sizes = [len(s.vectors) for s in dist_index.primary_shards]
print(f"Shard distribution: {shard_sizes} (std={np.std(shard_sizes):.1f})")

print(f"\nGenerating {N_QUERIES} queries...")
queries = rng.random((N_QUERIES, DIM), dtype=np.float32)
queries = queries / np.linalg.norm(queries, axis=1, keepdims=True)

ground_truth = []
for q in queries:
    sims = vecs @ q
    top = np.argsort(sims)[::-1][:TOP_K]
    ground_truth.append(set(top))

print("\n=== Fan-out Strategies ===")
for strategy in ["all", "single"]:
    latencies = []
    recalls = []
    for q in queries:
        start = time.perf_counter()
        results = dist_index.search(q, TOP_K, fan_out=strategy)
        lat = time.perf_counter() - start
        latencies.append(lat)
        result_ids = set(r[1] for r in results)
        recalls.append(len(result_ids & ground_truth[len(recalls)]) / TOP_K)

    print(f"\n  Strategy: fan-out={strategy}")
    print(f"    Mean latency: {np.mean(latencies)*1000:.3f}ms")
    print(f"    P95 latency:  {np.percentile(latencies, 95)*1000:.3f}ms")
    print(f"    Mean recall:  {np.mean(recalls):.3f}")
    print(f"    QPS:          {N_QUERIES / sum(latencies):.0f}")

print("\n=== Replication & Fault Tolerance ===")
for fail_rate in [0.0, 0.1, 0.25]:
    latencies = []
    recalls = []
    for q in queries:
        start = time.perf_counter()
        results = dist_index.search_with_replica(q, TOP_K, replica_failure_rate=fail_rate)
        lat = time.perf_counter() - start
        latencies.append(lat)
        result_ids = set(r[1] for r in results)
        recalls.append(len(result_ids & ground_truth[len(recalls)]) / TOP_K)

    print(f"  Failure rate={fail_rate:.0%}:")
    print(f"    Mean recall={np.mean(recalls):.3f}  Latency={np.mean(latencies)*1000:.3f}ms  "
          f"QPS={N_QUERIES / sum(latencies):.0f}")

print("\n" + "=" * 70)
print("Distributed Search Insights:")
print("  - Fan-out 'all':  highest recall, highest latency, most resources")
print("  - Fan-out 'single': lowest latency, lower recall (works if shard routing is accurate)")
print("  - Replication protects against shard failures but increases write cost")
print("  - RF=2 is standard; RF=3 for critical workloads")
print("  - Real distribued DBs (Milvus, Qdrant, Pinecone) add: gossip protocols,")
print("    consistent hashing, distributed coordination, and vector partitioning")

# Benchmarking Methodology

How to benchmark vector databases fairly and meaningfully.

## Why Most Benchmarks Are Misleading

Common mistakes:
- **Cold cache measurements** (first query after startup is 10× slower)
- **Single-threaded vs multi-threaded** (not matching your workload)
- **Differing index parameters** (comparing well-tuned HNSW to default IVF)
- **Different data distributions** (random vectors ≠ real embeddings)
- **Reporting mean instead of percentiles** (hides tail latency)

## What to Measure

| Metric | How to Measure | Target Range |
|---|---|---|
| **Recall@10** | Fraction of exact top-10 in ANN top-10 | > 0.90 for production |
| **p50 latency** | Median query time | < 10ms |
| **p99 latency** | Worst 1% query time | < 50ms |
| **QPS** (Queries Per Second) | Queries / time under sustained load | Depends on SLA |
| **Index build time** | Time to build index from raw vectors | < dataset size / 1M per hour |
| **Memory usage** | RAM consumed by index | Must fit in budget |

## Standard Benchmark Datasets

| Dataset | Vectors | Dimensions | Distance | Use Case |
|---|---|---|---|---|
| **SIFT** | 1M | 128 | L2 | Small-scale comparison |
| **GIST** | 1M | 960 | L2 | High-dimensional |
| **DEEP** | 10M | 96 | Cosine | Large-scale, learnt embeddings |
| **MS MARCO** | 8.8M | 768 | Cosine | Text retrieval (most relevant for RAG) |
| **LAION-2B** | 2B | 768 | Cosine | Billion-scale image/text |
| **Yandex T2I** | 1M–1B | 200 | Cosine | Production-scale benchmarks |

## Fair Benchmarking Protocol

### Setup

```python
# 1. Load data
vectors = load_vectors("dataset.bin")
queries = load_queries("queries.bin")
ground_truth = load_ground_truth("ground_truth.bin")  # exact top-k

# 2. Warmup
for _ in range(100):
    index.search(queries[0], k=10)

# 3. Run benchmark
import time
latencies = []
for q in queries:
    start = time.perf_counter()
    results = index.search(q, k=10)
    latencies.append(time.perf_counter() - start)

# 4. Compute metrics
recall = compute_recall(results, ground_truth)
p50 = np.percentile(latencies, 50)
p99 = np.percentile(latencies, 99)
qps = len(queries) / sum(latencies)
```

### Rules

1. **Warm up** — at least 100 queries before measuring.
2. **Use independent query set** — never benchmark with queries that are in the index.
3. **Report p50 and p99**, not just mean.
4. **Use same vector data** across all products being compared.
5. **Tune each product individually** — default parameters aren't optimal.
6. **Match index type across products** — compare HNSW to HNSW, not HNSW to default.

## Profiling Index Parameters

Run a parameter sweep to find the optimal configuration:

```python
results = []
for M in [8, 16, 32]:
    for ef_search in [50, 100, 200]:
        index = build_hnsw(vectors, M=M, ef_construction=200)
        recall, latency = benchmark(index, queries, ground_truth)
        results.append({"M": M, "ef_search": ef_search, 
                        "recall": recall, "latency": latency})
```

## Beyond Basic Benchmarks

| Scenario | What to Test |
|---|---|
| **Concurrent queries** | QPS degradation under load (multi-threaded) |
| **Mixed read/write** | Search latency while index is ingesting |
| **Filtering** | Recall with metadata filters applied |
| **Failure recovery** | Time to recover from node failure |
| **Re-index** | Time to rebuild index from scratch |

## Recommended Tools

| Tool | Description |
|---|---|
| **ANN-Benchmarks** | Standard framework for ANN algorithm comparison |
| **VectorDBBench** | Benchmarks vector database products (Milvus, Qdrant, etc.) |
| **FAISS bench** | Quick internal benchmarking script |

## Best Practices

- **Benchmark on your own data.** Generic benchmarks don't capture your data distribution, dimensionality, or query patterns.
- **Test at your expected scale.** A database that handles 1M vectors well may behave very differently at 100M.
- **Test with your expected concurrency.** Single-threaded performance doesn't predict production behavior under 100+ concurrent queries.
- **Report all parameters.** "I used HNSW with M=16, ef_construction=200, ef_search=100" — without parameters, benchmark results are meaningless.
- **Publish your benchmark code.** Reproducible benchmarks are trustworthy benchmarks.

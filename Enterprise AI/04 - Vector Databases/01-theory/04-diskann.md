# DiskANN

SSD-based ANN index for billion-scale vector search — designed for datasets too large for RAM.

## Why DiskANN?

At billion-scale, storing vectors in RAM is prohibitively expensive:

```
1B vectors × 768 dims × FP32 = 3 TB of RAM ≈ $30K–$100K/month (cloud)
```

DiskANN stores vectors on SSD and uses a smart caching strategy to minimize disk reads.

## Vamana Graph

DiskANN uses a custom graph structure called Vamana:

- **Single-layer graph** (unlike HNSW's multi-layer) — simpler, better cache locality.
- **Degree bound:** Each node has ≤ R connections (typical R = 64–128).
- **Greedy search:** Similar to HNSW but on a single layer with a larger graph.

### Construction

```
1. Start with a random graph (each node connected to ~R random others).
2. For each node:
   a. Greedy search from the current graph → candidate neighbors.
   b. Prune to keep the R most diverse neighbors (maximizes coverage).
3. Repeat for N iterations, gradually refining.
```

## Search Process

```
1. Load entry point (cached in RAM).
2. Greedy search on graph, maintaining a result list of L candidates.
3. For each candidate vector:
   a. Read vector from SSD (on demand, cached for future).
   b. Compute distance to query.
   c. Update result list.
4. Stop when no better candidates found.
5. Return top-k.
```

## Performance Characteristics

| Metric | HNSW (in-memory) | DiskANN (SSD) |
|---|---|---|
| **1M vectors, p50 latency** | 2–5ms | 5–10ms |
| **100M vectors, p50 latency** | 10–20ms (3 TB RAM) | 15–30ms (SSD) |
| **1B vectors, p50 latency** | Infeasible (30 TB RAM) | 20–50ms |
| **Recall@10** | 0.98 | 0.95 |
| **Build time (100M)** | Hours | Hours–days |
| **Storage cost** | RAM: $1K–10K/TB/month | SSD: $50–100/TB/month |

## Caching Strategy

DiskANN caches vectors in RAM based on access patterns:

- **Frequently accessed vectors** stay in the page cache (OS-level).
- **Beam search width (L)** controls the number of SSD reads per query.
- **Higher L = more reads = better recall but slower queries.**

```
L = 50:  10–20 SSD reads per query, fastest
L = 100: 20–40 reads, good recall
L = 200: 40–80 reads, best recall
```

## When to Use DiskANN

```
Dataset size?
├── < 10M → Use HNSW (in-memory, simpler)
├── 10M–100M → HNSW or DiskANN (depending on RAM budget)
└── > 100M → DiskANN (SSD is 10–50× cheaper than RAM)

Latency?
├── < 10ms p50 → Prefer HNSW if data fits in RAM
├── < 30ms p50 → DiskANN works well
└── < 100ms p50 → DiskANN with larger L (batch workloads)

Cost sensitivity?
├── RAM budget covers 5× raw vector size → HNSW
├── RAM budget covers raw vector size → IVF-PQ
└── RAM budget is minimal → DiskANN (SSD is cheap)
```

## Availability

| Product | DiskANN Support | Notes |
|---|---|---|
| **FAISS** | ❌ | No DiskANN implementation |
| **Milvus** | ✅ | DiskANN index type available in 2.3+ |
| **Qdrant** | ❌ | In-memory only |
| **Weaviate** | ❌ | In-memory + HNSW |
| **Pinecone** | ✅ | Pod-based (likely DiskANN-like, not disclosed) |
| **Elasticsearch** | ❌ | HNSW + IVF only |

## Best Practices

- **Use DiskANN only when data doesn't fit in RAM.** If your dataset fits in memory, HNSW is faster, simpler, and has better recall.
- **Monitor SSD read IOPS.** DiskANN can saturate SSD bandwidth at high QPS. Use NVMe SSDs, not SATA.
- **Warm the cache before going live.** Run a few thousand representative queries to populate the OS page cache.
- **Benchmark with your workload.** DiskANN's performance depends heavily on data dimensionality, graph connectivity, and access patterns.

# ANN Index Types

Approximate Nearest Neighbor (ANN) indexes trade a small amount of accuracy for massive speed gains in vector search.

## The Problem

Exact k-Nearest Neighbors (kNN) requires comparing the query against every vector in the database — O(n × d) time. For 10M vectors at 768 dims, that's 7.68 billion floating-point operations per query. Not feasible at scale.

ANN indexes solve this by pre-organizing vectors into a structure that allows sub-linear search time.

## Index Types Overview

| Index | Algorithm | Search Time | Build Time | Memory | Recall | Best For |
|---|---|---|---|---|---|---|
| **Flat (brute-force)** | None | O(n) | None | Low | 1.0 (exact) | < 10K vectors, evaluation |
| **HNSW** | Navigable Small World graph | O(log n) | O(n log n) | High (1.1–1.3× raw) | 0.95–0.99 | < 10M, high-recall, in-memory |
| **IVF** | Inverted File + k-means | O(√n) | O(n × k × iter) | Low | 0.80–0.95 | > 10M, memory-constrained |
| **PQ** | Product Quantization | O(n) (ADC) | O(n × M × k_s) | Very low | 0.70–0.90 | > 100M, extreme compression |
| **IVF-PQ** | IVF + PQ combined | O(√n) + ADC | Combined | Low | 0.75–0.90 | > 10M, best compression |
| **DiskANN** | Vamana graph, SSD-resident | O(log n) | O(n log n) | Low (disk) | 0.90–0.97 | > 100M, billion-scale |
| **ScANN** | Inverted + PQ (Google) | O(log n) | O(n log n) | Moderate | 0.90–0.95 | Web-scale, Google production |

## Complexity Table

| Operation | Flat | HNSW | IVF | IVF-PQ | DiskANN |
|---|---|---|---|---|---|
| Insert | O(1) | O(log n) | O(1) | O(1) | O(log n) |
| Search | O(n) | O(log n) | O(√n) | O(√n) + decode | O(log n) |
| Delete | O(n) | O(log n) | O(√n) | O(√n) | O(log n) |
| Memory (768d, 1M) | 3 GB | ~4 GB | ~1.5 GB | ~0.3 GB | ~3 GB + SSD |
| Recall@10 | 1.0 | 0.98 | 0.92 | 0.88 | 0.95 |

## When to Use Which

```
Vector count?
├── < 10K → Flat (no index needed, exact results)
├── < 1M → HNSW (best recall, moderate memory)
├── < 10M → HNSW or IVF
├── < 100M → IVF-PQ or DiskANN
└── > 100M → DiskANN or PQ + re-ranking

Latency SLA?
├── < 5ms → HNSW (in-memory, single node)
├── < 20ms → IVF-PQ (memory-efficient, GPU options)
├── < 100ms → DiskANN (SSD, billion-scale)
└── > 100ms → Flat (exact search acceptable)

Recall requirement?
├── > 0.99 → HNSW (tuned) or Flat
├── > 0.95 → HNSW (default params) or DiskANN
├── > 0.85 → IVF-PQ
└── > 0.75 → PQ (extreme compression)
```

## Practical Guidance

- **HNSW is the default choice for most production workloads** (< 10M vectors, in-memory, high recall).
- **IVF-PQ is the memory-efficient alternative** when the index won't fit in RAM.
- **DiskANN is for billion-scale** when you need to serve from SSD.
- **Flat is for evaluation only** — never use in production beyond tiny datasets.
- **The optimal index depends on your specific data distribution and workload.** Always benchmark on your own data.

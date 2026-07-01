# HNSW Deep Dive

Hierarchical Navigable Small World — the most widely used ANN index for in-memory workloads.

## How It Works

HNSW builds a multi-layer graph where higher layers have fewer nodes (long-range connections) and lower layers have more nodes (dense connections).

```
Layer 3:  ○────○────○      (long-range, ~1% of nodes)
              │
Layer 2:  ○──○──○──○──○     (medium-range, ~10% of nodes)
           │  │  │  │  │
Layer 1:  ○─○─○─○─○─○─○─○   (dense, 100% of nodes)
```

**Search process:**
1. Start at the entry point (top layer).
2. Greedily traverse to the nearest neighbor in the current layer.
3. Descend to the next layer and continue.
4. Repeat until reaching the bottom layer.
5. On the bottom layer, search a neighborhood of ef_search candidates.

## Key Parameters

| Parameter | Range | Default | Effect |
|---|---|---|---|
| **M** | 4–64 | 16 | Maximum number of connections per node. Higher = better recall, more memory. |
| **M_max** | M–2M | M | Maximum connections per node after pruning. |
| **ef_construction** | 100–500 | 200 | Search width during index construction. Higher = better quality, slower build. |
| **ef_search** | 10–500 | 50 | Search width during query. Higher = better recall, slower query. |
| **M_max0** | M–2M | M | Max connections for layer-0 nodes (largest layer). |

## Parameter Tuning Guide

### Recall vs. ef_search

```
ef_search = 10:  92% recall, fastest search
ef_search = 50:  97% recall, default
ef_search = 200: 99% recall, 4× slower
ef_search = 500: 99.5% recall, 10× slower
```

**Production rule:** Set ef_search to achieve your target recall. For 0.95 recall, start at ef_search = M × 2.

### Memory Impact of M

```
M = 8:  ~3.2 GB for 1M vectors at 768 dims (1.07× raw size)
M = 16: ~3.6 GB (1.20× raw size)
M = 32: ~4.4 GB (1.47× raw size)
M = 64: ~6.0 GB (2.00× raw size)
```

**Memory formula:** `raw_vectors × (1 + M × 0.013)` for 768-dim vectors.

## Production Tuning Process

```
1. Start with M=16, ef_construction=200, ef_search=50.
2. Measure recall@10 on your eval set.
3. If recall < target:
   - Increase ef_search (easiest, impacts query latency)
   - Increase ef_construction (impacts build time)
   - Increase M (impacts memory)
4. If query latency > SLA:
   - Decrease ef_search
   - Reduce M (rebuild required)
   - Consider IVF-PQ instead
```

## When HNSW Struggles

| Scenario | Problem | Alternative |
|---|---|---|
| > 10M vectors | Memory cost (HNSW adds 20–50% overhead) | IVF-PQ or DiskANN |
| High delete/update rate | HNSW doesn't support efficient deletes | IVF (deletes are cheaper) |
| Streaming inserts | HNSW requires periodic rebalance | Qdrant's HNSW variant handles this better |
| Disk-based | HNSW is designed for RAM | DiskANN |

## HNSW in Popular Databases

| Product | M Default | Notes |
|---|---|---|
| FAISS | 32 | Standard HNSW implementation |
| Milvus | 16 | Uses HNSW by default for < 10M |
| Qdrant | 16 | Optimized HNSW with streaming support |
| Pinecone | N/A (proprietary) | Likely HNSW-based, params not exposed |
| Weaviate | 64 | Uses HNSW with custom optimizations |
| pgvector | 0 (disabled) | HNSW in pgvector 0.6+ |

## Best Practices

- **Prefer HNSW for < 10M vectors with latency SLA < 10ms.** It's the most thoroughly optimized and widely supported index.
- **Tune ef_search before M.** It's easier to change (no rebuild) and has a predictable linear impact on latency.
- **Build with higher ef_construction than you think you need.** A slower build is acceptable for most workloads; poor recall isn't.
- **Monitor memory.** HNSW's graph overhead can surprise teams who only calculate raw vector size.

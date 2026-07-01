# Cost Optimization for Vector Databases

Reducing vector DB costs without sacrificing performance or reliability.

## Cost Drivers (Ranked)

1. **RAM** for index (dominant at > 1M vectors)
2. **Compute** (CPU/GPU for search and indexing)
3. **Storage** (raw vectors + index + WAL + backups)
4. **Network** (cross-AZ data transfer, API calls)
5. **Managed service markup** (2-5× over self-hosted)

## Strategy 1: Compress Vectors

### Product Quantization (PQ)

| Technique | Memory Reduction | Recall Impact | Use Case |
|---|---|---|---|
| No compression (FP32) | 1× (baseline) | — | < 100K vectors |
| SQ8 (INT8) | 4× | -0.5-1% | General purpose |
| SQ4 (INT4) | 8× | -2-3% | Large scale |
| PQ (64 dims) | ~12× | -1-3% | Very large scale |
| Binary (1 bit) | 32× | -5-10% | Candidate pre-filter |

**ROI calculation:**
```
FP32 @ 10M × 768d = 31 GB RAM
PQ64 @ 10M × 768d = 2.6 GB RAM
Saving: ~$200/month (r6i.2xlarge → r6i.large)
Recall cost: -2%
Decision: Worth it if recall target is > 0.90
```

### Matryoshka Embeddings
- Train model to produce multiple dimension levels (64, 128, 256, 512, 768)
- Search at lower dimension, re-rank at higher dimension
- 4-12× storage savings for 2% recall loss

### Dimension Reduction
- PCA from 1024 → 256: 4× reduction, -1-3% recall
- PCA from 768 → 128: 6× reduction, -3-5% recall
- Train PCA on representative sample (10K vectors)

## Strategy 2: Right-Size the Index

| Index Type | Memory (1M × 768d) | Recall@10 | Relative Cost |
|---|---|---|---|
| Flat | 3.1 GB | 1.000 | High (no index, brute force) |
| HNSW M=16 | 3.2 GB | 0.97 | Baseline |
| HNSW M=8 | 3.15 GB | 0.94 | -1.5% |
| IVF nlist=256 | 3.1 GB | 0.93 | ~same RAM |
| IVF+PQ | 0.5-1 GB | 0.92 | -6× RAM |
| DiskANN | 0.1 GB (RAM) + SSD | 0.94 | -30× RAM |

**Cheapest adequate index:** IVF+PQ or DiskANN. Only 2-3% recall loss for 6-30× RAM reduction.

## Strategy 3: Tiered Storage

```
Hot (RAM)         → Frequently accessed vectors (last 30 days)
Warm (SSD/NVMe)   → Full dataset + index
Cold (S3/GCS)     → Archived/rarely accessed vectors
```

Implementation approaches:
- **Milvus:** Tiered storage with `disk` index type
- **Qdrant:** On-disk vectors with RAM-based HNSW graph
- **Custom:** Route queries to hot/warm/cold based on recency or tenant tier

## Strategy 4: Cache Strategically

| Cache Layer | What to Cache | Hit Rate | Benefit |
|---|---|---|---|
| Query results cache | Exact (query, top_k) pairs | 5-20% | Eliminates search entirely |
| Embedding cache | Model outputs per text | 20-40% | Avoids re-embedding |
| Connection pool | DB connections | N/A | Eliminates connection overhead |
| Client-side vector cache | Frequently accessed vectors | 10-30% | Avoids DB round-trip |

**Example:** 10ms query, 20% result cache hit rate: effective latency drops to 8ms.

## Strategy 5: Optimize Write Path

| Technique | Savings | Trade-off |
|---|---|---|
| Batch inserts (100-1000 vectors) | 10-50× write throughput | Slightly higher latency per batch |
| Async indexing | 2-5× write throughput | Index eventually consistent |
| Reduce indexing frequency | 2-3× CPU savings | Higher search cost during rebuild |
| Disable WAL for bulk load | 2-3× faster load | No crash recovery during load |
| Use append-only (no deletes) | Eliminates compaction cost | Requires re-indexing for deletions |

## Strategy 6: Managed Service Cost Control

### Pinecone
- Right-size pod type: start with s1 (low cost), scale up
- Use namespaces to share pods across tenants
- Enable pod auto-scaling (but set max limits)
- Use `describe_index_stats` to track utilization

### Qdrant Cloud
- Use free tier for dev/staging
- Right-size cluster: 1 node for dev, 3+ for prod
- Monitor segment count (too many segments = expensive merges)

### Milvus Cloud
- Use standalone for < 10M vectors
- Use serverless for variable workloads
- Avoid over-provisioning query nodes

## Strategy 7: Reduce Data Transfer

| Technique | Savings | Example |
|---|---|---|
| Co-locate app and DB in same AZ | 0.01-0.05 $/GB | $100-500/month at 10TB |
| Pre-filter before vector search | 2-10× less data scanned | Metadata index |
| Return only IDs, not vectors | 4× less response data | Client fetches metadata from cache |
| Use binary quantization for pre-filter | 32× less data scanned | Coarse → fine ranking |

## Cost Reduction Checklist

- [ ] Evaluate PQ / SQ8 / binary quantization
- [ ] Right-size instance (don't over-provision)
- [ ] Enable query result cache
- [ ] Batch inserts (≥100 vectors per request)
- [ ] Co-locate app and DB in same AZ
- [ ] Use tiered storage if supported
- [ ] Review index type (IVF+PQ for cheap recall)
- [ ] Monitor and alert on cost anomalies
- [ ] Review and remove unused indexes
- [ ] Use reserved instances (managed) or spot instances (self)

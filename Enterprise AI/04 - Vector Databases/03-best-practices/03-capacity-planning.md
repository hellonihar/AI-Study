# Capacity Planning for Vector Databases

Sizing compute, memory, storage, and network for vector search workloads.

## Memory Model

Vector database memory is dominated by three components:

```
Total Memory = Index Memory + Vector Cache + Overhead
```

### 1. Index Memory

| Index Type | Memory Formula | Example (1M × 768d) |
|---|---|---|
| Flat (brute force) | N × dim × 4 bytes | 3.1 GB |
| HNSW | N × (dim × 4 + M × 2 × 4) | 3.1 GB + 128 MB (M=16) |
| IVF | N × (dim × 4) + nlist × dim × 4 | 3.1 GB + small |
| IVF+PQ | N × (M_pq) + nlist × dim × 4 | 256 MB + small (M_pq=64) |
| DiskANN | N × M_pq (in RAM) + vectors on SSD | 64 MB (PQ) + 3.1 GB (SSD) |

### 2. Vector Cache
- Client-side caching of frequently accessed vectors: 1-2 GB typical
- Query results cache: depends on query distribution (20-50% of active set)

### 3. System Overhead
- OS: 1-2 GB
- WAL/buffer: 10-20% of index memory
- Connections: ~1 MB per connection

## Sizing by Scale

### Small (< 100K vectors, dim=768)
```
RAM:   4-8 GB
CPU:   2-4 cores
Disk:  20 GB (SSD)
DB:    pgvector, Qdrant (single node)
Cost:  ~$20-50/month
```

### Medium (1M-10M vectors, dim=768)
```
RAM:   16-64 GB (index: 4-32 GB + overhead)
CPU:   4-8 cores
Disk:  50-200 GB (NVMe SSD)
DB:    Qdrant, Milvus (1-2 nodes)
Cost:  ~$100-500/month
```

### Large (10M-100M vectors, dim=768)
```
RAM:   64-256 GB (IVF+PQ: 2-20 GB index)
CPU:   8-32 cores
Disk:  200 GB - 2 TB (NVMe SSD)
DB:    Milvus cluster, Pinecone pod
Nodes: 3-8 (distributed)
Cost:  ~$500-5,000/month
```

### Very Large (100M+ vectors, dim=768)
```
RAM:   256 GB+ (DiskANN: 1-10 GB index in RAM)
CPU:   32+ cores
Disk:  2-20 TB (NVMe SSD or cloud volumes)
DB:    Milvus, DiskANN-based, or Pinecone
Nodes: 8-32+
Cost:  ~$5,000-50,000/month
```

## Storage Projection

| N (vectors) | dim=384 (fp32) | dim=768 (fp32) | dim=768 + PQ64 | dim=1024 (fp32) |
|---|---|---|---|---|
| 1K | 1.5 MB | 3.1 MB | 64 KB | 4.1 MB |
| 100K | 153 MB | 307 MB | 6.4 MB | 410 MB |
| 1M | 1.5 GB | 3.1 GB | 64 MB | 4.1 GB |
| 10M | 15 GB | 31 GB | 640 MB | 41 GB |
| 100M | 153 GB | 307 GB | 6.4 GB | 410 GB |
| 1B | 1.5 TB | 3.1 TB | 64 GB | 4.1 TB |

**Rule of thumb:** Raw vectors dominate at fp32. Use PQ or binary quantization when storage exceeds available RAM by >2×.

## Network Considerations

| Scenario | Bandwidth | Latency Sensitivity |
|---|---|---|
| Single node, local | N/A | N/A |
| Distributed, same AZ | 10-25 Gbps | <1ms |
| Distributed, cross-AZ | 1-10 Gbps | 1-5ms |
| Client → managed API | User's internet | 5-50ms |

**Bottleneck to watch:** Query fan-out in distributed mode. Each query to a coordinator fans out to N shards. With 1000 QPS and 8 shards, that's 8000 internal searches/second. Network round-trips dominate at scale.

## Cost Projection (Self-Hosted)

Assuming AWS on-demand pricing (us-east-1, 2024):

| Scale | Instance Type | Monthly Compute | Storage | Total |
|---|---|---|---|---|
| 100K | t3.medium (2C/4G) | $31 | $5 | ~$36 |
| 1M | r6i.large (2C/16G) | $83 | $10 | ~$93 |
| 10M | r6i.2xlarge (8C/64G) | $332 | $50 | ~$382 |
| 50M | r6i.4xlarge (16C/128G) | $664 | $150 | ~$814 |
| 100M | r6i.8xlarge (32C/256G) | $1,327 | $300 | ~$1,627 |

Add 30-50% for EBS, data transfer, backup, and monitoring.

## Cost Projection (Managed)

| Scale | Pinecone | Qdrant Cloud | Weaviate Cloud | Milvus Cloud |
|---|---|---|---|---|
| 100K | ~$70 | ~$25 | ~$25 | ~$200 |
| 1M | ~$150 | ~$100 | ~$100 | ~$400 |
| 10M | ~$800 | ~$500 | ~$500 | ~$1,500 |
| 100M | ~$5,000 | ~$3,000 | ~$3,500 | ~$8,000 |

Managed services cost 2-5× self-hosted at scale, but include HA, backups, monitoring, and upgrades.

## Capacity Planning Checklist

- [ ] Measure average and peak QPS
- [ ] Measure average vector dimension and count
- [ ] Project growth over 6, 12, 24 months
- [ ] Choose index type based on memory budget
- [ ] Select instance/nodes: memory = index × 1.5 (headroom)
- [ ] Plan for replication: multiply by RF (2 or 3)
- [ ] Budget for vector cache (10-20% of index size)
- [ ] Account for WAL buffer and compaction overhead (20%)
- [ ] Network bandwidth: 10 Gbps minimum for distributed setups
- [ ] Configure auto-scaling or over-provision for traffic spikes

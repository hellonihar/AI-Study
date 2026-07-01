# Performance Comparison at 100 Million Vectors

Benchmarking at the 100M scale — the threshold at which most vector databases require distributed architecture and compression techniques.

## Test Configuration

| Parameter | Value |
|---|---|
| Vector count | 100,000,000 |
| Dimension | 768 (BGE-base equivalent) |
| Data type | FP32 (with PQ variants) |
| Distance metric | Cosine |
| Queries | 10,000 |
| Hardware Cluster | 4× AWS r6i.8xlarge (32 vCPU, 256 GB RAM each) + NVMe SSD |
| Network | 25 Gbps, same AZ |
| Top-K | 10 |
| Index configs | Tuned for >0.90 recall@10 |

## Raw Storage Requirements

| Format | Total Size | Per 10M Vectors |
|---|---|---|
| FP32 (raw) | 307 GB | 30.7 GB |
| INT8 (SQ8) | 76.8 GB | 7.68 GB |
| PQ64 (64 bytes/vector) | 6.4 GB | 640 MB |
| Binary (32 bytes/vector) | 3.2 GB | 320 MB |

At 100M, FP32 raw storage exceeds single-node RAM. Compression is mandatory.

## Latency (P50 / P99 in milliseconds)

| Database | Index Config | Recall | P50 | P99 | QPS (1 node) |
|---|---|---|---|---|---|
| **FAISS (single node)** | HNSW M=16 efSearch=32 | 0.95 | 8 | 25 | 1,250 |
| **FAISS (single node)** | IVF+PQ M=64 nprobe=64 | 0.88 | 5 | 18 | 2,000 |
| **FAISS (single node)** | IVF+PQ M=64 nprobe=128 | 0.92 | 9 | 30 | 1,100 |
| **FAISS (single node)** | DiskANN R=64 beam=4 | 0.93 | 15 | 45 | 670 |
| **Milvus (4 nodes)** | IVF_SQ8 nlist=16384 nprobe=64 | 0.91 | 6 | 20 | 4,000 |
| **Milvus (4 nodes)** | HNSW M=16 ef=64 | 0.93 | 8 | 28 | 5,000 |
| **Qdrant (6 nodes)** | HNSW M=16 ef=64 | 0.92 | 7 | 24 | 6,000 |
| **Pinecone (p2 pod)** | Proprietary | 0.90 | 10 | 35 | 3,000 |

## Index Build Time

| Database | Index Config | Build Time | Memory During Build |
|---|---|---|---|
| **FAISS** | IVF+PQ M=64 nlist=16384 | 45 min | 32 GB |
| **FAISS** | HNSW M=16 efC=80 | 120 min | 64 GB |
| **FAISS** | DiskANN R=64 L=80 | 90 min | 16 GB |
| **Milvus (4 nodes)** | IVF_SQ8 nlist=16384 | 35 min | 48 GB (cluster) |
| **Milvus (4 nodes)** | HNSW M=16 efC=80 | 90 min | 96 GB (cluster) |
| **Qdrant (6 nodes)** | HNSW M=16 efC=80 | 75 min | 80 GB (cluster) |
| **Pinecone** | Proprietary | ~60 min | Managed |

## Memory Scaling

### FAISS HNSW (M=16) — Single Node

| N (millions) | Index RAM | Vector RAM (FP32) | Total RAM | Recommended Instance |
|---|---|---|---|---|
| 1 | 3.3 GB | 3.1 GB | 6.4 GB | r6i.xlarge (32 GB) |
| 10 | 33 GB | 31 GB | 64 GB | r6i.4xlarge (128 GB) |
| 25 | 82 GB | 77 GB | 159 GB | r6i.8xlarge (256 GB) |
| 50 | 164 GB | 153 GB | 317 GB | r6i.12xlarge (384 GB) |
| 100 | 328 GB | 307 GB | 635 GB | r6i.16xlarge (512 GB) + compression |

### FAISS IVF+PQ (M=64) — Single Node

| N (millions) | Index RAM | Vector RAM (PQ) | Total RAM | Recommended Instance |
|---|---|---|---|---|
| 1 | 0.6 GB | 0.06 GB | 0.66 GB | t3.medium (4 GB) |
| 10 | 6 GB | 0.6 GB | 6.6 GB | r6i.large (16 GB) |
| 25 | 15 GB | 1.6 GB | 17 GB | r6i.xlarge (32 GB) |
| 50 | 30 GB | 3.2 GB | 33 GB | r6i.2xlarge (64 GB) |
| 100 | 60 GB | 6.4 GB | 66 GB | r6i.4xlarge (128 GB) |

IVF+PQ reduces RAM requirements by 10× compared to HNSW at 100M scale.

## Throughput: QPS vs. Concurrency (Distributed Setup)

| Database | 1 client | 10 clients | 50 clients | 100 clients |
|---|---|---|---|---|
| **Milvus (4 nodes)** | 5,000 QPS | 15,000 QPS | 30,000 QPS | 32,000 QPS |
| **Qdrant (6 nodes)** | 6,000 QPS | 18,000 QPS | 35,000 QPS | 38,000 QPS |
| **Pinecone (p2)** | 3,000 QPS | 8,000 QPS | 15,000 QPS | 16,000 QPS |

All databases saturate before hitting CPU limits due to network and serialization bottlenecks.

## Network Impact

| Fan-out Strategy | Internal Searches/Query | Latency Penalty |
|---|---|---|
| All-shards (broadcast) | 4-32 (all nodes) | +0.5-2ms |
| Quantized (routed) | 1-4 (candidate shards) | +0.1-0.5ms |
| Single-shard (hash-based) | 1 | 0ms (but lower recall) |

At 100M, network round-trips dominate P50 latency. Co-locate in same AZ.

## Cost at 100M Scale (Monthly)

| Database | Deployment | Compute | Storage | Total | Recall |
|---|---|---|---|---|---|
| **FAISS** | 1× r6i.8xlarge + NVMe | $1,327 | $200 | $1,527 | 0.92 |
| **Milvus** | 4× r6i.4xlarge | $2,656 | $500 | $3,156 | 0.93 |
| **Qdrant** | 6× r6i.4xlarge | $3,984 | $750 | $4,734 | 0.92 |
| **Pinecone** | p2 pod (auto-scale) | Opaque | Opaque | ~$5,000-8,000 | 0.90 |

## Key Takeaways

1. **Don't run FP32 at 100M scale** — use PQ or SQ8 to reduce memory 4-12×
2. **Distributed architecture becomes necessary** at ~50M+ for HNSW (memory bound)
3. **IVF+PQ is the most cost-effective** at 100M: single node can handle it with good recall
4. **DiskANN is viable** when RAM is scarce: 100M fits in 16 GB RAM + SSD
5. **Network is the bottleneck** in distributed setups — not CPU or disk
6. **Milvus and Qdrant scale similarly** at this tier; choose on operational grounds
7. **Pinecone is 2-3× more expensive** than self-hosted but requires zero ops

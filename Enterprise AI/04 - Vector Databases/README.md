# Vector Databases

Production-grade vector storage, indexing, and Approximate Nearest Neighbor (ANN) search — the persistence layer for semantic search, RAG, and recommendation systems.

## Module Structure

```
04 - Vector Databases/
├── 01-theory/          # 9 files: ANN index types, architecture, benchmarking
├── 02-code/            # 9 scripts: FAISS, Pinecone, Milvus, Qdrant, pgvector
├── 03-best-practices/  # 5 files: selection, tuning, capacity, ops, cost
├── 04-comparison/      # 5 files: feature matrix, perf at 1M/100M, cost, ecosystem
├── 05-resources/       # Papers, docs, benchmarks, tools, courses
└── README.md           # This file
```

## Theory (01-theory/)

| # | File | Topic |
|---|---|---|
| 1 | `01-ann-index-types.md` | Flat, HNSW, IVF, PQ, DiskANN — intro and comparison |
| 2 | `02-hnsw-deep-dive.md` | HNSW construction, search, parameters, memory model |
| 3 | `03-ivf-and-pq.md` | IVF clustering, product quantization, compression ratios |
| 4 | `04-diskann.md` | SSD-based ANN, Vamana graph, hybrid DRAM/disk index |
| 5 | `05-hybrid-search-and-filtering.md` | Dense + sparse + metadata, RRF, ColBERT |
| 6 | `06-vector-db-architecture.md` | Distributed architecture: sharding, replication, consensus |
| 7 | `07-index-mutation-strategies.md` | Streaming inserts, compaction, tombstone handling |
| 8 | `08-multi-tenancy-and-security.md` | Isolations patterns, RBAC, data encryption |
| 9 | `09-benchmarking-methodology.md` | Metrics (recall, QPS, latency), workload design |

## Code Examples (02-code/)

| # | File | Description | Requirements |
|---|---|---|---|
| 1 | `01-faiss-ivf-local.py` | IVF index training, search, nprobe tuning vs brute force | `faiss-cpu`, `sentence-transformers` |
| 2 | `02-faiss-hnsw-local.py` | HNSW graph build, efSearch trade-off analysis | `faiss-cpu`, `sentence-transformers` |
| 3 | `03-pinecone-crud.py` | Upsert, query, update, delete with metadata filters | `pinecone-client`, API key |
| 4 | `04-milvus-basics.py` | Connect, create collection, IVF_FLAT insert/search | `pymilvus`, Milvus server |
| 5 | `05-qdrant-basics.py` | In-memory mode, filtered search, payload indexing | `qdrant-client` |
| 6 | `06-pgvector-basics.py` | SQL vector search, IVFFlat index, hybrid filtering | `psycopg2-binary`, pgvector |
| 7 | `07-hybrid-search.py` | Dense (cosine) + sparse (BM25) + metadata via RRF | `rank-bm25`, `sentence-transformers` |
| 8 | `08-benchmark-ann.py` | Flat vs HNSW vs IVF sweep (10K synthetic vectors) | `faiss-cpu` |
| 9 | `09-benchmark-distributed.py` | Simulated sharding, replication, fault tolerance | `numpy` |

## Best Practices (03-best-practices/)

| # | File | Topic |
|---|---|---|
| 1 | `01-product-selection.md` | Decision framework: FAISS / pgvector / Qdrant / Milvus / Pinecone / Weaviate |
| 2 | `02-index-tuning.md` | HNSW (M, ef), IVF (nlist, nprobe), PQ parameters |
| 3 | `03-capacity-planning.md` | Memory projection at 100K-1B vectors, cost modeling |
| 4 | `04-production-operations.md` | HA topologies, monitoring, backup, compaction, incident response |
| 5 | `05-cost-optimization.md` | PQ compression, tiered storage, caching, batching |

## Comparisons (04-comparison/)

| # | File | Content |
|---|---|---|
| 1 | `01-feature-matrix.md` | Side-by-side feature comparison across 6 databases |
| 2 | `02-perf-1m-vectors.md` | Latency, recall, QPS, memory at 1M scale |
| 3 | `03-perf-100m-vectors.md` | Distributed performance at 100M scale |
| 4 | `04-cost-analysis.md` | TCO: self-hosted vs managed at 100K-100M scales |
| 5 | `05-ecosystem-integration.md` | LangChain, Kafka, K8s, monitoring integration depth |

## Key Topics

- **ANN index types:** Flat, IVF, HNSW, IVF+PQ, DiskANN — algorithms, parameters, memory
- **Performance:** Latency (P50/P95/P99), recall@K, QPS, memory per vector
- **Index tuning:** efSearch, nprobe, nlist, M — trade-off curves and heuristics
- **Managed services:** Pinecone, Qdrant Cloud, Milvus Cloud, Weaviate Cloud
- **Self-hosted:** pgvector, Qdrant, Milvus, FAISS — sizing, ops, cost
- **Hybrid search:** Dense (vector) + sparse (BM25) + metadata filtering via RRF
- **Index mutations:** Streaming inserts, deletes, compaction, WAL management
- **Multi-tenancy:** Collection/namespace isolation, RBAC, data encryption
- **Production ops:** HA topologies, monitoring, backup, PITR, incident response
- **Cost optimization:** PQ compression, tiered storage, caching, batching

## Quick Start

```bash
# FAISS local search (no external services needed)
pip install sentence-transformers faiss-cpu numpy
python "02-code/01-faiss-ivf-local.py"

# Qdrant in-memory (no server needed)
pip install sentence-transformers qdrant-client numpy
python "02-code/05-qdrant-basics.py"

# Hybrid search (no external services needed)
pip install sentence-transformers rank-bm25 numpy
python "02-code/07-hybrid-search.py"
```

## Prerequisites

- **Python 3.10+**
- For local-only scripts: `sentence-transformers`, `faiss-cpu`, `numpy`, `rank-bm25`
- For DB-specific scripts: `pinecone-client`, `pymilvus`, `qdrant-client`, `psycopg2-binary`
- For external databases: running instance of Pinecone (API key), Milvus (Docker), Qdrant (Docker or in-memory), PostgreSQL + pgvector (Docker)

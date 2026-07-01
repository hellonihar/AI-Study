# Vector Database Feature Matrix

Side-by-side comparison of capabilities across leading vector databases.

## General Characteristics

| Feature | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Category** | Library | PostgreSQL ext | Native vector DB | Native vector DB | Managed vector DB | Native vector DB |
| **Open source** | Yes (MIT) | Yes (PostgreSQL) | Yes (Apache 2.0) | Yes (Apache 2.0) | No (proprietary) | Yes (BSD-3) |
| **Language** | C++/Python | C (extension) | Rust | Go/Java | Go (prop) | Go |
| **First release** | 2017 | 2021 | 2020 | 2019 | 2019 | 2017 |
| **Deployment** | In-process | In Postgres | Docker/K8s/Binary | Docker/K8s/Binary | Cloud only | Docker/K8s/SaaS |

## Index Types Supported

| Index Type | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Flat (brute force)** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **IVF (IVFFlat)** | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **IVF+PQ** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **HNSW** | ✅ | ✅ (0.7.0+) | ✅ | ✅ | ✅ (prop) | ✅ |
| **DiskANN** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Binary index** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Custom/Proprietary** | ❌ | ❌ | ❌ | ❌ | ✅ (SST) | ❌ |

## Distance Metrics

| Metric | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Cosine** | ✅* | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Euclidean (L2)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Inner Product (IP)** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Manhattan (L1)** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Haversine (geo)** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Jaccard** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Hamming** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

_* FAISS cosine = normalized IP_

## Query Features

| Feature | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Hybrid (dense + sparse)** | ❌ | ❌ | ✅ (built-in BM25) | ✅ (2.4+) | ❌* | ✅ |
| **Metadata filters** | ❌ | ✅ (SQL WHERE) | ✅ (payload filter) | ✅ (scalar field) | ✅ (metadata) | ✅ (where) |
| **Geo search** | ❌ | ✅ (PostGIS) | ✅ (geo radius) | ❌ | ❌ | ✅ |
| **group-by / aggregation** | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Multi-vector** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Full text search (BM25)** | ❌ | ✅ (tsvector) | ✅ | ❌ | ❌ | ✅ |
| **Boolean search** | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |

_* Pinecone sparse-dense is in preview_

## Consistency and Transactions

| Feature | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Strong consistency** | N/A | ✅ | ✅ (configurable) | ❌ (eventual) | ❌ (eventual) | ✅ (configurable) |
| **Read-your-writes** | N/A | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Transactions (ACID)** | N/A | ✅ | ❌ (single-op atomic) | ❌ | ❌ | ❌ |
| **Point-in-time recovery** | N/A | ✅ (WAL) | ❌ | ❌ | ❌ | ❌ |

## Operations

| Feature | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Replication** | ❌ | ✅ (streaming) | ✅ (Raft) | ✅ (Raft-based) | ✅ (auto) | ✅ (Raft) |
| **Sharding** | ❌ | ✅ (Citus) | ✅ (consistent hash) | ✅ (consistent hash) | ✅ (auto) | ✅ (consistent hash) |
| **Multi-tenancy** | ❌ | Row-level | Collection-level | Partition/Collection | Namespace | Class-level |
| **RBAC** | ❌ | ✅ (Postgres) | ❌ | ✅ | ✅ (API keys) | ✅ |
| **TLS/mTLS** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Audit logging** | ❌ | ✅ (pgAudit) | ❌ | ❌ | ✅ | ✅ |
| **Backup tooling** | Manual | pg_dump / WAL | Snapshot API | etcd + object store | Auto (managed) | Auto (managed) |

## Ecosystem Integration

| Integration | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **LangChain** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **LlamaIndex** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Haystack** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Spark** | ❌ | ✅ (JDBC) | ❌ | ✅ | ❌ | ❌ |
| **Kafka** | ❌ | ✅ (Debezium) | ✅ | ✅ | ❌ | ✅ |
| **dbt** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Kubernetes** | ❌ | ❌ (operator avail) | ✅ (Helm) | ✅ (Helm + Operator) | ❌ (managed) | ✅ (Helm) |
| **Terraform** | ❌ | ✅ | ✅ (provider) | ❌ | ✅ (provider) | ✅ (provider) |

## Constraints

| Constraint | FAISS | pgvector | Qdrant | Milvus | Pinecone |
|---|---|---|---|---|---|
| **Max vector dimension** | Unlimited | 16,000 | 65,536 | 32,768 | 20,000 |
| **Max collection/namespace** | N/A | Per DB | Unlimited | 65,536 | Unlimited |
| **Max vectors per shard** | N/A | Table size limit | 10M recommended | 10M recommended | Unlimited |
| **Max metadata size** | N/A | 1.6TB per row | 4MB per point | 64KB per entity | 40KB per vector |

## Verdict

| Use Case | Best Choice |
|---|---|
| **Prototyping / research** | FAISS |
| **Startup with Postgres** | pgvector |
| **Production RAG** | Qdrant (self) or Pinecone (managed) |
| **Large-scale enterprise** | Milvus |
| **Semantic + keyword search** | Qdrant, Weaviate, or Milvus 2.4+ |
| **Graph-based knowledge** | Weaviate |
| **Kubernetes native** | Qdrant or Milvus |
| **Minimal ops** | Pinecone |

# Vector Database Product Selection

Choosing the right vector database for your workload, scale, and operational constraints.

## Decision Flowchart

```
Scale?
├── < 100K vectors → FAISS / USearch (embed in app, no separate DB)
├── 100K – 10M → pgvector or Qdrant (single node, minimal ops)
├── 10M – 100M → Qdrant or Milvus (distributed, managed)
└── 100M+ → Milvus cluster or Pinecone (auto-scaling, managed)

Operational preference?
├── Minimal ops → Pinecone / Weaviate Cloud (fully managed)
├── Kubernetes shop → Milvus / Qdrant (Helm charts, CRDs)
└── SQL shop → pgvector (extension, existing Postgres)

Consistency requirement?
├── Strong consistency → pgvector / Qdrant
├── Eventual (high perf) → Milvus / Pinecone
└── Read-your-writes → Qdrant / Weaviate

Hybrid search?
├── Required → Weaviate / Qdrant (built-in BM25)
├── Sparse + dense → Milvus (sparse-bm25 in 2.4+)
└── Application-level → any + rank-bm25 library
```

## Product Comparison Summary

| Feature | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Type** | Library | Extension | Native DB | Native DB | Managed | Managed/Self |
| **Deployment** | In-process | In Postgres | Docker/K8s | Docker/K8s | Cloud only | Cloud/Self |
| **Distributed** | No | Via Postgres | Yes (cluster) | Yes (cluster) | Yes | Yes |
| **Consistency** | N/A | Strong | Configurable | Eventual | Eventual | Configurable |
| **Hybrid search** | No | No (app-level) | Built-in | 2.4+ built-in | App-level | Built-in |
| **Filtering** | IDSelector | SQL WHERE | Payload filter | Scalar field | Metadata filter | Where filter |
| **ANN index** | All types | IVFFlat/HNSW | HNSW | IVF/HNSW/DiskANN | Proprietary | HNSW |
| **Multi-tenancy** | No | Row-level | Collection-level | Partition/Collection | Namespace | Class-level |
| **Cost (self)** | Free | Free | Free | Free | N/A | Free (self) |
| **Cost (managed)** | N/A | ~$50/mo (RDS) | ~$25/mo | ~$200/mo | ~$70/mo | ~$25/mo |

## Selection by Use Case

### RAG Pipeline (Typical: 100K-10M docs)
- **Recommended:** Qdrant or pgvector
- **Why:** Sufficient scale, simple ops, hybrid search helpful
- **Avoid:** FAISS alone (no persistence, no filtering)

### Real-time Recommendation (10M-100M, <10ms P99)
- **Recommended:** Milvus or Pinecone
- **Why:** Distributed architecture, GPU acceleration, auto-scaling
- **Avoid:** pgvector (sequential scan overhead at scale)

### Embedding Service for SaaS (1M-50M, multi-tenant)
- **Recommended:** Qdrant (collection per tenant) or Pinecone (namespaces)
- **Why:** Built-in multi-tenancy, predictable cost, good isolation
- **Avoid:** FAISS (no built-in tenancy)

### Research / Experimentation (< 1M vectors)
- **Recommended:** FAISS
- **Why:** Zero ops, fastest iteration, all index types available
- **Avoid:** Any managed service (cost overkill)

## Migration Path

```
FAISS → pgvector → Qdrant → Milvus/Pinecone
       (100K)    (1M)      (10M+)
```

Start with FAISS for prototyping. Move to pgvector when you need persistence and SQL. Graduate to Qdrant when you need distributed search. Adopt Milvus/Pinecone at scale or when managed ops is mandatory.

## Key Selection Criteria (Weighted)

1. **Scale + latency requirements** (40%) — the dominant constraint
2. **Operational maturity** (25%) — can your team run a distributed DB?
3. **Query features** (20%) — hybrid search, filtering, geo-queries
4. **Cost model** (10%) — managed vs. self-hosted at your scale
5. **Ecosystem fit** (5%) — existing Postgres, K8s, monitoring stack

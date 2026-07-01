# Enterprise Data Architecture for AI

Designing the data foundation that powers AI workloads at scale.

## The Data Challenge for AI

AI systems consume data differently from traditional analytics:

| Aspect | Traditional BI | AI / ML Workloads |
|---|---|---|
| **Data types** | Structured (tables) | Structured + unstructured (text, images, audio) |
| **Volume** | GB-TB | TB-PB |
| **Freshness** | Daily/hourly | Real-time / near-real-time |
| **Quality tolerance** | High (bad data = bad reports) | Moderate (noise can be tolerated) |
| **Schema** | Fixed, well-defined | Flexible, evolving |
| **Access pattern** | SQL queries | Embedding, vector search, streaming |
| **Consumption** | Dashboards, reports | LLMs, vector DBs, training pipelines |

## Enterprise Data Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                  Consumption Layer                    │
│   LLMs, RAG, Dashboards, ML Training, APIs           │
├─────────────────────────────────────────────────────┤
│                   Serving Layer                       │
│   Feature Store   Vector DB   Cache   SQL Views      │
├─────────────────────────────────────────────────────┤
│                  Storage Layer                        │
│   Data Lake (S3/ADLS/GCS)   Warehouse   Lakehouse    │
├─────────────────────────────────────────────────────┤
│                  Processing Layer                     │
│   Batch (Spark)   Streaming (Kafka/Flink)   CDC      │
├─────────────────────────────────────────────────────┤
│                  Ingestion Layer                      │
│   Structured    Unstructured    Real-time    Event    │
│   (DB/SaaS)     (PDF/Web/Email) (CDC/Kafka) (Webhook) │
└─────────────────────────────────────────────────────┘
```

## Key Architectural Decisions

### 1. Batch vs. Streaming

| Factor | Batch | Streaming |
|---|---|---|
| **Latency** | Minutes to hours | Milliseconds to seconds |
| **Complexity** | Lower (Spark, Airflow) | Higher (Kafka, Flink, K8s) |
| **Cost** | Lower (spot instances) | Higher (always-on clusters) |
| **Consistency** | Strong (processing guarantees) | Eventual (at-least-once) |
| **When to use** | ML training, daily reports | Real-time RAG, fraud detection |

**Rule:** Start with batch. Add streaming only when business requires sub-minute freshness.

### 2. Data Lake vs. Warehouse vs. Lakehouse

| | Data Lake (S3/ADLS) | Warehouse (Snowflake) | Lakehouse (Delta/Iceberg) |
|---|---|---|---|
| **Schema** | Schema-on-read | Schema-on-write | Schema-on-write |
| **Data types** | All (structured + unstructured) | Structured | All |
| **ACID** | Limited | Full | Full |
| **Query perf** | Low (needs engine) | High | Medium-High |
| **Cost** | Low storage | High compute + storage | Medium |
| **AI fit** | Raw data, embeddings | Features, aggregations | Best of both |

**Recommendation:** Lakehouse (Delta Lake or Iceberg) for AI workloads. Single source of truth for structured and unstructured data.

### 3. Centralized vs. Decentralized

| Model | Ownership | Governance | Agility | Best For |
|---|---|---|---|---|
| Centralized data lake | Central team | Strong | Slow | Regulated industries |
| Data mesh (domain-owned) | Domain teams | Federated | Fast | Large organizations |
| Hybrid | Central + domain | Balanced | Medium | Most enterprises |

**Recommendation:** Start centralized. Migrate to data mesh when you have 10+ teams and 50+ data products.

## Data Architecture for RAG

RAG places unique demands on data architecture:

```
Source Systems
  ├── Structured (ERP, CRM, SQL DBs)
  │   └── CDC → Data Lake → Embed → Vector DB
  ├── Unstructured (PDF, Confluence, SharePoint)
  │   └── Crawl → Parse → Chunk → Embed → Vector DB
  └── Real-time (Events, Logs, Chat)
      └── Stream → Process → Embed → Vector DB
```

Each pipeline must:
1. Extract data from source systems with minimal impact
2. Transform into chunks/features suitable for embedding
3. Track lineage (which source document produced which chunk)
4. Handle updates (re-ingest changed documents)
5. Meet freshness SLAs (some data needs sub-minute, some daily)

## Data Freshness SLAs by Use Case

| Use Case | Max Staleness | Pipeline Type |
|---|---|---|
| Product catalog search | 1 hour | Batch (hourly) |
| Customer support RAG | 1 minute | Near-real-time (CDC) |
| News/article search | 5 minutes | Streaming |
| Legal document review | 24 hours | Batch (daily) |
| Fraud detection | 1 second | Streaming |
| Internal knowledge base | 1 hour | Batch (hourly) |
| Personalized recommendations | 15 minutes | Micro-batch |

## Data Volume Planning

| Data Type | Annual Growth | Storage per TB | Embedding Cost per TB |
|---|---|---|---|
| Text (documents) | 30-50% | ~$25/month (S3) | ~$50 (embedding compute) |
| Images | 50-100% | ~$25/month (S3) | ~$200 (CLIP embedding) |
| Structured (DB exports) | 20-40% | ~$25/month (S3) | Minimal |
| Logs | 100-200% | ~$25/month (S3) | Minimal |

Embedding cost dominates at scale. 1 TB of text produces ~$50 in embedding costs (BGE-base on GPU), and the resulting vectors consume ~300 GB in a vector DB.

## Architecture Principles

1. **Immutable data lake** — raw data is never modified, only appended. Transformed copies are tracked.
2. **Schema evolution** — all transformations must handle schema drift gracefully.
3. **Idempotent pipelines** — re-running a pipeline produces the same result (safe for retries).
4. **Observable** — every data product has freshness, volume, and quality metrics.
5. **Least privilege** — data access follows the principle of minimum required access.
6. **Cost-aware** — query and storage costs are visible per team and per data product.

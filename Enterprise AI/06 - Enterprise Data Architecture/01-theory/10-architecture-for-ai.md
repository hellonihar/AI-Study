# Data Architecture for AI

Designing end-to-end data pipelines optimized for AI consumption.

## The AI Data Pipeline

```
Source Systems
    │
    ▼
┌──────────────────────────────────────────────────┐
│               Ingestion Layer                      │
│  Structured (CDC/API)   Unstructured (Parse/OCR)   │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│               Storage Layer                        │
│  Lakehouse (Delta/Iceberg)  Raw Data Lake (S3)     │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│               Processing Layer                     │
│  Chunking   Embedding   Feature Engineering        │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│               Serving Layer                        │
│  Vector DB   Feature Store   Cache   SQL Views     │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│               Consumption Layer                    │
│  RAG    ML Training    Search    Analytics         │
└──────────────────────────────────────────────────┘
```

## Architecture Patterns by Use Case

### Pattern 1: RAG-First Architecture

Best for: Question-answering over enterprise documents.

```
Sources:
  ├── Confluence / Wiki
  ├── SharePoint / File Shares
  ├── Email Archives
  └── CRM / Support Tickets
    
Processing:
  1. Continuous crawl (daily/hourly)
  2. Parse → Clean → Chunk → Embed
  3. Index into Vector DB
  
Storage:
  - Lakehouse: raw + chunked data
  - Vector DB: embeddings + metadata
  
Consumption:
  - RAG API (retrieve + generate)
  - Cache (query results, 1h TTL)
  
Key metrics:
  - End-to-end latency: < 5 minutes (near real-time)
  - Freshness SLA: 1 hour for most sources
  - Recall@10: > 0.90
```

### Pattern 2: ML Training Architecture

Best for: Training and serving ML models.

```
Sources:
  ├── Transactional DBs (events, orders)
  ├── Application logs
  └── External data feeds
    
Processing:
  1. Batch ETL (daily Spark jobs)
  2. Feature engineering
  3. Training data versioning
  
Storage:
  - Lakehouse: raw + features + training data
  - Feature Store: online + offline features
  
Consumption:
  - ML Training (Spark, PyTorch)
  - Model Inference (real-time API)
  
Key metrics:
  - Feature freshness: < 1 hour
  - Training data reproducibility: point-in-time queries
  - Feature serving latency: < 10ms
```

### Pattern 3: Hybrid (RAG + ML)

Best for: Systems that need both RAG and ML (e.g., personalized search).

```
Sources: [All structured + unstructured]
    │
    ├── RAG Pipeline ──→ Vector DB ──→ RAG API
    │
    └── Feature Pipeline ──→ Feature Store ──→ ML Model ──→ API
                                        │
                                        └──→ Personalization → Re-rank RAG results
```

## Infrastructure Sizing

### Compute Requirements

| Pipeline Component | Instance Type | Scaling |
|---|---|---|
| Document parsing | CPU-optimized (c6i.2xlarge) | Horizontal (SQS queue) |
| Embedding (self-host) | GPU (g5.xlarge) | Batch size + concurrency |
| Vector search | Memory-optimized (r6i.xlarge) | Shard count |
| LLM inference | GPU (g5.48xlarge) | Horizontal + queue |
| Batch ETL (Spark) | Spot instances | Auto-scale |

### Storage Projections

| Data Type | 1 TB Raw → Chunks | Embedding Storage | Notes |
|---|---|---|---|
| Text (docs) | ~500 GB Parquet | ~800 GB (768d FP32) | 1 TB text → ~2M chunks |
| PDFs | ~800 GB (parsed) | ~1.2 TB | PDFs have images, tables |
| Code | ~200 GB (functions) | ~300 GB | Code is dense |
| Logs | ~300 GB (parsed) | ~500 GB | High compression ratio |

## Data Pipeline Monitoring

```yaml
pipeline_monitoring:
  ingestion:
    - metric: "documents_ingested_per_hour"
    - metric: "parse_error_rate"
    - metric: "ingestion_lag_seconds"
  
  processing:
    - metric: "chunks_created_per_hour"
    - metric: "embedding_throughput_per_second"
    - metric: "chunk_quality_pass_rate"
  
  serving:
    - metric: "vector_db_qps"
    - metric: "vector_db_latency_p50_p99"
    - metric: "cache_hit_rate"
    - metric: "retrieval_recall_at_10"
  
  cost:
    - metric: "embedding_cost_per_million_chunks"
    - metric: "vector_db_cost_per_gb"
    - metric: "total_pipeline_cost_per_day"
```

## SLA-Driven Architecture

Each data product has an SLA that drives architectural decisions:

```yaml
data_product:
  name: "Customer 360 for RAG"
  
  sla:
    freshness: "15 minutes"
    availability: "99.9%"
    retrieval_recall@10: 0.90
    end_to_end_latency_p99: "2 seconds"
  
  architecture:
    ingestion:
      type: "CDC (Debezium + Kafka)"
      frequency: "continuous"
    
    processing:
      type: "micro-batch (30s windows)"
      compute: "Kuberenetes (4 pods)"
    
    storage:
      raw: "Delta Lake (S3, 90-day retention)"
      vectors: "Qdrant cluster (3 nodes, RF=2)"
      cache: "Redis (32 GB, 1h TTL)"
    
    serving:
      api: "FastAPI (auto-scale: 2-20 pods)"
      llm: "GPT-4o (or self-hosted Llama 3.1)"
  
  cost_budget:
    monthly: "$2,000"
    per_query: "$0.002"
```

## Disaster Recovery

```yaml
dr_plan:
  rpo: "1 hour"    # Recovery Point Objective (data loss tolerance)
  rto: "4 hours"   # Recovery Time Objective (downtime tolerance)
  
  strategy:
    - data: "Continuous backup of lakehouse to second region"
    - vectors: "Point-in-time snapshot of vector DB every hour"
    - config: "Infrastructure as code (Terraform) in Git"
  
  recovery_steps:
    1. "Provision Qdrant cluster from Terraform"
    2. "Restore latest vector DB snapshot"
    3. "Replay CDC from Kafka (last 24h)"
    4. "Verify recall@10 on eval set"
    5. "Switch DNS to recovered cluster"
```

## Architecture Decision Record (ADR) Template

Every significant architectural decision should be documented:

```markdown
# ADR-042: Vector Database Selection

## Status
Accepted (2024-12-01)

## Context
Need a vector database for the Customer 360 RAG pipeline.
Scale: 10M vectors, 500 QPS, <50ms P99 latency.

## Decision
Use Qdrant (self-hosted, 3-node cluster).

## Rationale
- Best query latency at 10M scale (benchmarked vs Milvus, Pinecone)
- Payload filtering for multi-tenancy (collection per tenant)
- Simple operations (single binary, no external dependencies)
- Open source (no vendor lock-in)

## Consequences
Positive:
- Low operational complexity (vs Milvus which needs 8+ services)
- Good query performance at target scale

Negative:
- Need to manage K8s cluster for self-hosting
- Manual shard rebalancing when scaling out

## Alternatives Considered
- Pinecone: 2x cost at our scale, managed convenience
- Milvus: Better at 100M+, but overkill and complex for 10M
- pgvector: Insufficient for our latency requirements at scale
```

## Key Principles Summary

1. **Lakehouse first** — store everything in a lakehouse format. Rebuild vector DBs from it.
2. **Idempotent pipelines** — re-running produces the same result. Safe to retry.
3. **PII at the source** — mask before embedding, not after.
4. **SLA-driven architecture** — let freshness and latency requirements dictate the pipeline design.
5. **Cost visibility** — track cost per query, per pipeline, per data product.
6. **Observability** — every pipeline stage has freshness, volume, and quality metrics.
7. **Schema evolution** — plan for change. Use schema registry. Version everything.
8. **Separate storage from compute** — lake on S3, compute on ephemeral clusters.

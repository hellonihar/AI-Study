# Ecosystem Integration Comparison

How vector databases integrate with AI frameworks, data pipelines, and infrastructure tools.

## AI Framework Integration

| Framework | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **LangChain** | ✅ VectorStore | ✅ VectorStore | ✅ VectorStore | ✅ VectorStore | ✅ VectorStore | ✅ VectorStore |
| **LlamaIndex** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Haystack** | ❌ | ❌ | ✅ DocumentStore | ✅ DocumentStore | ✅ DocumentStore | ✅ DocumentStore |
| **Semantic Kernel** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Spring AI** | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |

### LangChain Integration Detail

All six support the standard `VectorStore` interface:
- `add_texts` / `add_documents`
- `similarity_search` with `k` and `filter`
- `similarity_search_with_score`
- `similarity_search_by_vector`
- `as_retriever` (with search_type: "similarity" or "mmr")
- `delete` (where supported)

**Ease of setup:**
```python
# Pinecone (easiest — managed, no config)
from langchain_pinecone import PineconeVectorStore
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)

# pgvector (needs connection string)
from langchain_postgres import PGVector
vectorstore = PGVector(embeddings=embeddings, connection=conn_string)

# Qdrant (works with in-memory or cloud)
from langchain_qdrant import QdrantVectorStore
vectorstore = QdrantVectorStore(client=client, collection_name="docs", embedding=embeddings)

# FAISS (simplest for local)
from langchain_community.vectorstores import FAISS
vectorstore = FAISS.from_documents(documents, embeddings)

# Milvus (needs connection + collection setup)
from langchain_milvus import Milvus
vectorstore = Milvus(embeddings=embeddings, connection_args=conn_args)

# Weaviate
from langchain_weaviate import WeaviateVectorStore
vectorstore = WeaviateVectorStore(client=client, index_name="Docs", embedding=embeddings)
```

## Data Pipeline Integration

| Pipeline Tool | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Apache Kafka** | ❌ | ✅ (Debezium CDC) | ✅ (REST sink) | ✅ (Pulsar built-in) | ❌ | ✅ (REST) |
| **Apache Spark** | ❌ | ✅ (JDBC) | ❌ | ✅ (Spark connector) | ❌ | ❌ |
| **Airbyte** | ❌ | ✅ (destination) | ✅ (destination) | ✅ (destination) | ✅ (destination) | ❌ |
| **dbt** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Apache Flink** | ❌ | ✅ (JDBC) | ✅ (REST) | ✅ (connector) | ❌ | ❌ |
| **Fivetran** | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Estuary** | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ |

### Kafka Integration

**Milvus** has the deepest Kafka integration:
- Built-in Pulsar for internal WAL (Kafka-compatible)
- CDC connector captures Milvus changes → Kafka topics
- Supports exactly-once semantics via Pulsar transactions

**Qdrant** uses a simpler approach:
- REST sink connector (Kafka Connect)
- Upsert payloads as JSON to Qdrant API
- Supports at-least-once delivery (idempotent upserts)

**pgvector** benefits from the entire Postgres Kafka ecosystem:
- Debezium PostgreSQL connector for CDC
- PeerDB for real-time replication
- Logical replication slots for WAL streaming

## Embedding Model Serving

| Embedding Service | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **OpenAI** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cohere** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Sentence-Transformers** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Hugging Face** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Google Vertex AI** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AWS Bedrock** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

_Pinecone and Weaviate require external embedding. The others accept any embedding vector._

## Infrastructure & Deployment

| Tool | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Docker** | N/A | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Kubernetes (Helm)** | N/A | ❌ | ✅ (official) | ✅ (official) | ❌ | ✅ (official) |
| **Kubernetes (Operator)** | N/A | ❌ (CNPG) | ❌ | ✅ (Milvus Operator) | ❌ | ❌ |
| **Terraform** | N/A | ✅ (RDS) | ✅ (Qdrant Cloud) | ❌ | ✅ (Pinecone provider) | ✅ (Weaviate provider) |
| **AWS CDK** | N/A | ✅ (RDS) | ❌ | ❌ | ✅ | ❌ |
| **Serverless** | N/A | ✅ (Aurora) | ❌ | ✅ (Milvus Cloud) | ✅ | ❌ |
| **Multi-cloud** | N/A | ✅ (any Postgres) | ✅ (self-hosted) | ✅ (self-hosted) | ❌ (AWS-only) | ✅ (self-hosted) |

### Kubernetes Deployment Complexity (1-10 scale, higher = harder)

| Database | Resources | Config | Day-2 Ops | Score |
|---|---|---|---|---|
| **pgvector** | 1 StatefulSet | Minimal (tuning optional) | Postgres expertise | 2/10 |
| **Qdrant** | 1 StatefulSet + Headless | ConfigMap + PVC | Qdrant-specific | 3/10 |
| **Weaviate** | 1 StatefulSet + optional | ConfigMap + PVC | Weaviate-specific | 3/10 |
| **Milvus** | 8 components (coord, data, index, query, proxy, etcd, minio, pulsar) | Operator or Helm | Many components to monitor | 7/10 |
| **Pinecone** | N/A (managed) | Terraform provider | None | 0/10 |

**Milvus** has the most complex K8s deployment (8 microservices). Use the Milvus Operator to simplify.

## Monitoring & Observability

| Capability | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Prometheus metrics** | ❌ | ✅ (postgres_exporter) | ✅ (built-in) | ✅ (built-in) | ❌ | ✅ (built-in) |
| **Grafana dashboard** | ❌ | ✅ (PG dashboard) | ✅ (official) | ✅ (official) | ✅ (limited) | ✅ (official) |
| **OpenTelemetry** | ❌ | ❌ | ❌ | ✅ (traces) | ❌ | ❌ |
| **Slow query log** | ❌ | ✅ (auto_explain) | ✅ | ✅ | ❌ | ❌ |
| **P99 latency metrics** | ❌ | ✅ (via pg_stat) | ✅ | ✅ | ✅ | ✅ |
| **Recall monitoring** | Manual | Manual | Manual | Manual | Manual | Manual |

## Backup & DR Ecosystem

| Tool | FAISS | pgvector | Qdrant | Milvus | Pinecone | Weaviate |
|---|---|---|---|---|---|---|
| **Periodic dump** | Manual | ✅ pg_dump | ✅ snapshot API | ✅ etcd backup | ✅ (managed) | ✅ (managed) |
| **WAL streaming** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **PITR** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **S3/GCS backup** | Manual | ✅ (pg_dump → S3) | ✅ (snapshot → S3) | ✅ (built-in) | ✅ (auto) | ❌ |
| **Cross-region DR** | N/A | ✅ (logical replication) | ❌ (manual) | ❌ (manual) | ✅ (premium) | ❌ |

## Conclusion by Integration Need

| If You Use | Best DB Choice |
|---|---|
| **LangChain/LlamaIndex** | Any — all work equally well |
| **Kafka streaming** | Milvus (deepest integration) |
| **Apache Spark** | Milvus or pgvector |
| **Kubernetes + Helm** | Qdrant or Weaviate (simpler than Milvus) |
| **Terraform** | Pinecone or Qdrant Cloud |
| **Existing Postgres** | pgvector (zero new infrastructure) |
| **Serverless** | Pinecone (easiest) or pgvector (Aurora) |
| **Multi-cloud** | Qdrant self-hosted or Milvus |
| **OpenTelemetry** | Milvus (only one with native support) |

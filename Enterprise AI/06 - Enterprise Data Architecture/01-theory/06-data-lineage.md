# Data Lineage and Tracking

Tracing data from source through transformation to AI consumption.

## Why Lineage Matters for AI

| Problem | Without Lineage | With Lineage |
|---|---|---|
| RAG returns stale data | Can't identify source | Trace to stale CDC pipeline |
| Embedding quality degrades | Can't find root cause | Trace to schema change in source |
| Compliance audit | Can't prove data origin | Complete provenance trail |
| Debugging retrieval failures | Guess which pipeline caused it | Exact source document + transform path |

## Lineage Components

```
Source System (PostgreSQL)
    │
    ▼
CDC Pipeline (Debezium → Kafka)
    │
    ▼
Transform (Python/Spark)
    │
    ▼
Embedding (Sentence-Transformer)
    │
    ▼
Vector DB (Qdrant)
    │
    ▼
RAG Query → Retrieved Chunk → Source Document
```

Each arrow represents a lineage hop, recording:
- **What** data was passed
- **When** it was processed
- **Which** version of code/configuration was used
- **Who** triggered the pipeline

## Lineage Metadata Schema

```json
{
  "doc_id": "uuid-1234",
  "source": {
    "type": "postgresql",
    "host": "prod-db.internal",
    "database": "orders",
    "table": "customers",
    "record_id": 42042,
    "extracted_at": "2024-12-01T10:00:00Z"
  },
  "pipeline": {
    "name": "customer_360_rag",
    "version": "2.3.1",
    "run_id": "airflow_dag_run_20241201_100000",
    "code_hash": "sha256:abcd...",
    "config_hash": "sha256:ef01..."
  },
  "transformations": [
    {"name": "filter_deleted", "version": "1.0"},
    {"name": "denormalize_customer", "version": "2.0"},
    {"name": "format_for_embedding", "version": "1.2"}
  ],
  "embedding": {
    "model": "BGE-base",
    "model_version": "1.0.0",
    "dimension": 768,
    "normalized": true,
    "created_at": "2024-12-01T10:00:05Z"
  },
  "vector_db": {
    "type": "qdrant",
    "collection": "customer_360",
    "point_id": "uuid-5678",
    "indexed_at": "2024-12-01T10:00:08Z"
  }
}
```

## Implementing Lineage

### Approach 1: OpenLineage (Standard)

OpenLineage is an open standard for data lineage:

```yaml
# OpenLineage event
eventType: "COMPLETE"
run:
  runId: "run-uuid-1234"
  facets:
    parent:
      run: "parent-run-uuid"
job:
  namespace: "airflow"
  name: "customer_360_rag"
inputs:
  - namespace: "postgresql"
    name: "prod.customers"
    facets:
      dataSource:
        uri: "postgresql://prod-db:5432/orders"
outputs:
  - namespace: "qdrant"
    name: "customer_360"
    facets:
      columnLineage:
        fields:
          full_name: "customers.name + customers.email"
```

**Supported by:** Airflow, dbt, Spark, Flink, Great Expectations.

### Approach 2: Custom Metadata Store

```python
class LineageStore:
    def __init__(self):
        self.connections = {}  # (source_id, dest_id) → metadata

    def record(self, source_id, dest_id, metadata):
        self.connections[(source_id, dest_id)] = {
            **metadata,
            "timestamp": datetime.utcnow(),
        }

    def trace(self, doc_id):
        """Walk the lineage graph from doc back to source."""
        path = []
        current = doc_id
        while current:
            edges = [(s, d, m) for (s, d), m in self.connections.items() if d == current]
            if not edges:
                break
            source_id, _, meta = edges[0]
            path.append((source_id, meta))
            current = source_id
        return path
```

## Lineage for RAG Debugging

When a RAG response is wrong, lineage helps identify the failure point:

```
Wrong RAG Answer
    │
    ▼
1. Was the retrieved chunk relevant?
   ├── No → Retrieval issue
   │   └── Check embedding quality, index freshness
   └── Yes → Generation issue
       └── Check prompt, model

2. Retrieval issue → Trace chunk lineage:
   ├── Chunk → Embedding → Transform → Source
   │
   ▼
3. Check each hop:
   ├── Source data stale? → Check CDC pipeline freshness
   ├── Transform wrong? → Check code version
   └── Embedding wrong? → Check model version
```

## Tracking Data Versions

Every pipeline run should tag data with version information:

```python
# Versioned data product
data_product = {
    "dataset": "customer_profiles",
    "version": "2024-12-01T10:00:00Z",  # or semantic version
    "schema_version": "v2",
    "pipeline_version": "2.3.1",
    "data": [...]
}
```

### Version Comparisons

```sql
-- Compare two versions for quality regression
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN quality_check = 'pass' THEN 1 ELSE 0 END) as passes,
  AVG(embedding_quality_score) as avg_quality
FROM customer_profiles_v2
UNION ALL
SELECT
  COUNT(*),
  SUM(CASE WHEN quality_check = 'pass' THEN 1 ELSE 0 END),
  AVG(embedding_quality_score)
FROM customer_profiles_v3;
```

## Lineage Visualization

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  PostgreSQL   │────>│  CDC Pipeline │────>│   Kafka       │
│  customers    │     │  v2.3.1      │     │   topic       │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Vector DB    │<────│  Embedding    │<────│  Transform    │
│  qdrant       │     │  BGE-base     │     │  v1.2         │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Automated Lineage from Airflow

```python
# Airflow DAG with automated lineage
from openlineage.airflow import DAG

with DAG(
    dag_id="customer_360_pipeline",
    schedule="*/15 * * * *",
    catchup=False,
) as dag:
    extract = PostgresOperator(task_id="extract_customers")
    transform = PythonOperator(task_id="transform_for_rag")
    embed = PythonOperator(task_id="generate_embeddings")
    index = PythonOperator(task_id="index_to_qdrant")

    extract >> transform >> embed >> index
```

OpenLineage automatically captures:
- Task dependencies
- Input/output datasets
- Run metadata
- Code versions

## Lineage and Compliance

For regulated industries, lineage provides audit trail:

```yaml
compliance_requirements:
  GDPR:
    - "Show all data related to a user"
    - lineage: "Trace user ID through all pipelines"
    - action: "Flag user data in every hop"
  
  SOX:
    - "Prove data hasn't been tampered with"
    - lineage: "Hash chain from source to consumption"
    - action: "Store content hash at each hop"
  
  HIPAA:
    - "Track access to PHI"
    - lineage: "Record every pipeline access to PHI fields"
    - action: "Log field-level access with timestamps"
```

## Tools

| Tool | Type | Best For |
|---|---|---|
| **OpenLineage** | Standard | Cross-platform lineage |
| **dbt** | SQL lineage | Warehouse transformations |
| **Amundsen** | Data discovery | Cataloging + lineage |
| **Apache Atlas** | Governance | Enterprise metadata |
| **DataHub** | Metadata platform | Unified lineage + search |
| **Marquez** | OpenLineage impl | Lineage collection + API |

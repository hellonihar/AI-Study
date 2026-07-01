# Lakehouse Architecture

Unifying data lake and data warehouse for AI workloads.

## What is a Lakehouse?

A lakehouse combines the flexibility of a data lake (store any data, cheap) with the ACID guarantees and query performance of a data warehouse.

```
Data Lake (S3/ADLS/GCS)
    │
    ├── Raw data (JSON, Parquet, Avro)
    ├── Unstructured (PDFs, images, audio)
    └── Semi-structured (logs, events)

Lakehouse Format (Delta Lake / Apache Iceberg / Apache Hudi)
    │
    ├── ACID transactions
    ├── Schema enforcement
    ├── Time travel (versioning)
    ├── Partition pruning
    └── File-level optimization

Query Engines (Spark, Trino, Athena, DuckDB)
    │
    └── SQL + ML + AI workloads
```

## Lakehouse Formats Compared

| Feature | Delta Lake | Apache Iceberg | Apache Hudi |
|---|---|---|---|
| **Origin** | Databricks | Netflix/Nessie | Uber |
| **ACID** | Yes (optimistic concurrency) | Yes (serializable) | Yes (MVCC) |
| **Time travel** | Yes (30-day retention default) | Yes (snapshot isolation) | Yes (timeline) |
| **Schema evolution** | Add/drop/rename/change | Add/drop/rename/change | Add/drop/rename |
| **Partition evolution** | Yes (hidden partitioning) | Yes (hidden partitioning) | Limited |
| **Spark integration** | Native | Native | Native |
| **Trino/Athena** | Yes | Yes | Yes |
| **Flink** | Yes (connector) | Yes (connector) | Yes (native) |
| **Catalog** | Hive Metastore, Unity Catalog | Hive, REST, Glue, Nessie | Hive Metastore |
| **Best for** | Databricks ecosystem | Open format, multi-engine | Large CDC workloads |

**Recommendation:** Default to Delta Lake if using Databricks. Default to Iceberg for open-format, multi-engine architectures.

## Lakehouse for AI Workloads

### Unified Storage for RAG

```
┌────────────────────────────────────────────┐
│              Lakehouse                       │
│                                              │
│  Raw Data       Processed     Embeddings     │
│  (PDFs, JSON)   (Chunks)      (Vectors)      │
│  ┌────────┐    ┌────────┐   ┌────────────┐  │
│  │ S3 raw │    │ Delta  │   │ Delta with  │  │
│  │ bucket │───>│ chunks │──>│ embeddings  │  │
│  └────────┘    └────────┘   └──────┬─────┘  │
│                                     │        │
│                              ┌──────▼──────┐ │
│                              │  Vector DB   │ │
│                              │  (Qdrant)    │ │
│                              └─────────────┘ │
└────────────────────────────────────────────┘
```

**Advantages:**
- Single copy of raw data serves RAG, ML training, and analytics
- Embeddings stored alongside source data for reproducibility
- Time travel lets you reconstruct past states of the vector index
- Schema evolution doesn't break the data lake

### Feature Store on Lakehouse

```sql
-- Create training features as Delta table
CREATE OR REPLACE TABLE customer_features
USING DELTA
AS
SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(total) as total_revenue,
    AVG(total) as avg_order_value,
    MAX(order_date) as last_order_date
FROM orders
GROUP BY customer_id;

-- Time-travel to train on historical data
SELECT * FROM customer_features VERSION AS OF 12345;
```

## Time Travel for Reproducibility

```python
# Delta Lake time travel
from delta import DeltaTable

# Read data as it was at a specific version
df_v1 = spark.read.format("delta") \
    .option("versionAsOf", 42) \
    .load("/data/chunks")

# Read data as of a specific timestamp
df_ts = spark.read.format("delta") \
    .option("timestampAsOf", "2024-11-01T00:00:00Z") \
    .load("/data/chunks")
```

**Use cases:**
- Reproduce a RAG response from 3 months ago
- Compare embedding quality across data versions
- Roll back corrupted data without full rebuild

## Schema Evolution in Lakehouse

```sql
-- Add new column (backward compatible)
ALTER TABLE customer_chunks ADD COLUMN language STRING;

-- Rename column (requires migration)
ALTER TABLE customer_chunks RENAME COLUMN user_name TO customer_name;

-- Drop column
ALTER TABLE customer_chunks DROP COLUMN temp_field;

-- Change column type (requires rewriting)
ALTER TABLE customer_chunks ALTER COLUMN price TYPE DOUBLE;
```

Unlike vector DBs, lakehouse formats handle schema evolution gracefully. This is why a lakehouse is a better "source of truth" than a vector DB.

## Partitioning Strategy

```sql
-- Partition by ingestion date for efficient pruning
CREATE TABLE chunks (
    chunk_id STRING,
    doc_id STRING,
    chunk_text STRING,
    embedding ARRAY<FLOAT>,
    created_at TIMESTAMP
)
USING DELTA
PARTITIONED BY (ingestion_date DATE);

-- Query only recently ingested chunks
SELECT * FROM chunks
WHERE ingestion_date >= CURRENT_DATE - INTERVAL 7 DAYS;
```

## File Compaction (Optimize)

Lakehouse formats accumulate small files. Regular compaction improves query performance:

```sql
-- Delta Lake: compact small files
OPTIMIZE chunks;

-- Iceberg: rewrite files
CALL catalog.rewrite_data_files(table => 'chunks');
```

**Target:** Files between 64MB and 1GB. Run compaction daily for streaming ingestion, weekly for batch.

## Catalog and Discovery

A data catalog makes lakehouse data discoverable:

```yaml
catalog:
  tables:
    - name: "raw_documents"
      description: "Raw ingested documents from all sources"
      format: "delta"
      partition: "ingestion_date"
      freshness: "daily"
      owner: "data-engineering"
  
    - name: "chunks"
      description: "Chunked + embedded documents for RAG"
      format: "delta"
      partition: "ingestion_date"
      freshness: "daily"
      owner: "ai-platform"
      lineage:
        source: "raw_documents"
        transformations: ["chunking_pipeline v2.1", "embedding_pipeline v1.5"]
  
    - name: "chunk_embeddings"
      description: "Embedding vectors (exported to Qdrant)"
      format: "delta"
      partition: "ingestion_date"
      owner: "ai-platform"
```

## Lakehouse + Vector DB Architecture

```
Ingestion → Lakehouse (Delta/Iceberg) → Embedding → Vector DB
                │                            │
                ▼                            ▼
         Analytics, ML Training          RAG, Search
         (SQL, Spark)                    (real-time)
```

**Key principle:** The lakehouse is the **source of truth**. The vector DB is a **cache** that can be rebuilt from the lakehouse at any time.

## Cost Optimization

| Strategy | Savings | Implementation |
|---|---|---|
| Partition pruning | 10-50x query speed | Date-partition ingestion |
| File compaction | 2-5x read speed | Regular OPTIMIZE |
| Z-ordering | 2-10x on filtered queries | Sort by doc_id or category |
| Column pruning | 2-4x read speed | Select only needed columns |
| Vacuum old versions | 50-90% storage savings | Remove versions older than 30 days |

```sql
-- Remove files older than 7 days (Delta)
VACUUM chunks RETAIN 168 HOURS;
```

## Tools

| Tool | Purpose |
|---|---|
| **Delta Lake** | Lakehouse format (Databricks) |
| **Apache Iceberg** | Open lakehouse format |
| **Apache Hudi** | Lakehouse format (CDC-heavy) |
| **Apache Spark** | Processing engine |
| **Trino / Athena** | SQL query engine |
| **DuckDB** | Local query engine for lakehouse |
| **Unity Catalog** | Databricks governance |
| **Nessie** | Git-like versioning for data lakes |

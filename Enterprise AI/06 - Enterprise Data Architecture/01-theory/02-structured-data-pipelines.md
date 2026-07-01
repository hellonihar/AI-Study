# Structured Data Pipelines

Extracting, transforming, and loading structured data for AI consumption.

## Sources of Structured Data

| Source | Protocol | Typical Volume | Freshness Need |
|---|---|---|---|
| PostgreSQL / MySQL | JDBC / CDC | GB-TB | Minutes to hours |
| Salesforce / SaaS | REST API | GB | Hours to daily |
| ERP (SAP, Oracle) | Batch export / CDC | TB | Hours |
| Snowflake / BigQuery | SQL queries | TB-PB | Hours |
| Application logs | File / Kafka | TB-PB | Real-time |

## Extraction Strategies

### 1. Full Snapshot

```sql
-- Simple, but expensive at scale
SELECT * FROM orders WHERE updated_at > last_run;
```

**Pros:** Simple, consistent
**Cons:** Doesn't scale past 10M rows, locks source tables

### 2. Incremental with Timestamp

```sql
SELECT * FROM orders
WHERE updated_at > last_checkpoint
AND updated_at <= current_checkpoint;
```

**Pros:** Efficient, widely supported
**Cons:** Requires `updated_at` column, clock skew issues

### 3. Change Data Capture (CDC)

```
Source DB → WAL → Debezium → Kafka → Sink (S3/Delta/Vector DB)

Capture: INSERT, UPDATE, DELETE with before/after images
```

**Pros:** Real-time, no impact on source, captures deletes
**Cons:** Complex setup, schema changes need handling

### 4. API-Based Extraction

```python
# Paginated API extraction
def extract_from_api(base_url, api_key, since):
    page = 1
    while True:
        response = requests.get(
            f"{base_url}/records",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"page": page, "since": since, "limit": 1000}
        )
        data = response.json()
        if not data["records"]:
            break
        yield from data["records"]
        page += 1
```

**Pros:** Universal (any SaaS has an API)
**Cons:** Rate limits, pagination, schema changes

## Transformation Patterns for AI

### 1. Denormalization for RAG Context

```sql
-- Instead of retrieving from 5 normalized tables,
-- create a denormalized view for RAG:
CREATE VIEW customer_360_rag AS
SELECT
    c.id,
    c.name,
    c.email,
    o.order_date,
    o.total,
    p.product_name,
    s.status_name
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN products p ON o.product_id = p.id
JOIN statuses s ON o.status_id = s.id;
```

Each row becomes a retrievable context unit.

### 2. Feature Engineering for ML

```python
# Create features for ML training
def create_features(orders_df, customers_df):
    features = orders_df.groupby("customer_id").agg({
        "total": ["sum", "mean", "count", "std"],
        "order_date": ["max", "min"],
    })
    features.columns = ["_".join(c) for c in features.columns]
    features["recency_days"] = (datetime.now() - features["order_date_max"]).dt.days
    features["avg_order_value"] = features["total_sum"] / features["total_count"]
    return features
```

### 3. Embedding-Ready Format

```python
def format_for_embedding(row):
    return f"""
    Customer: {row['name']}
    Email: {row['email']}
    Recent order: {row['order_date']} for ${row['total']}
    Product: {row['product_name']}
    Status: {row['status_name']}
    """
```

## Pipeline Architecture

```yaml
structured_pipeline:
  source: "postgresql://prod-db:5432/orders"
  extraction: "incremental_timestamp"
  checkpoint_column: "updated_at"
  
  transformations:
    - type: "filter"
      condition: "status != 'deleted'"
    - type: "denormalize"
      joins:
        - table: "customers"
          on: "customer_id"
    - type: "format_for_embedding"
      template: "customer_360_rag.j2"
  
  sink:
    type: "vector_db"
    collection: "customer_360"
    batch_size: 100
  
  scheduling:
    type: "cron"
    expression: "*/15 * * * *"  # every 15 minutes
    retry: 3
    alert_on_failure: true
```

## Handling Schema Changes

| Change Type | Impact | Handling Strategy |
|---|---|---|
| New column added | Low | Start populating, backfill optional |
| Column renamed | Medium | Dual-write for transition period |
| Column removed | Medium | Stop populating, keep historical |
| Column type changed | High | Add new column, migrate data, drop old |
| Table split | High | Update pipeline with new joins |

**CDC-based pipelines** handle most schema changes automatically (Debezium emits schema change events). Batch pipelines need manual DDL management.

## Structured Data Quality

| Check | SQL Example | Action |
|---|---|---|
| Null rate | `SUM(CASE WHEN col IS NULL THEN 1 ELSE 0 END) / COUNT(*)` | Alert > 5% |
| Uniqueness | `COUNT(*) - COUNT(DISTINCT col)` | Alert > 0 for PKs |
| Range | `MIN(col), MAX(col)` | Alert on unexpected values |
| Freshness | `MAX(updated_at)` | Alert if > SLA |
| Referential integrity | `LEFT JOIN WHERE child IS NOT NULL AND parent IS NULL` | Alert > 0 |

## Tools

| Tool | Best For |
|---|---|
| Airbyte / Fivetran | SaaS → Data Lake (no-code) |
| Debezium + Kafka | Real-time CDC |
| Apache Spark | Large-scale batch transformations |
| dbt | SQL-based transformations with lineage |
| Apache Flink | Stream processing |
| AWS Glue / Dataflow | Managed ETL |

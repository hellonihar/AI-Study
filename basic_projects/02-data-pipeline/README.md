# 02 - Data Pipeline: ETL to Feature Store

## Overview

Build a Python ETL pipeline that reads raw CSV data from S3, cleans and validates it with Pandas, engineers feature columns, and writes the result to a local SQLite database acting as a minimal feature store. Each run snapshots the data so experiments stay reproducible.

## Tech Stack

- **Orchestration** — simple Python script (no Airflow needed for this scope)
- **Storage** — AWS S3 (raw CSVs), SQLite (local feature store stand-in)
- **Processing** — Pandas, NumPy
- **Validation** — Great Expectations (optional, for data quality checks)
- **Versioning** — DVC for data snapshots

## Architecture & Design

```
S3 (raw CSV) ──► download ──► Pandas DataFrame ──► cleaning ──► feature engineering ──► SQLite
                              │                      │                │
                          log raw schema         drop nulls       create features:
                          check dtypes           fix types        day_of_week, lags,
                                                 clip outliers    rolling_means
                                                                       │
                                                              ┌────────┴────────┐
                                                              │ feature_metadata │
                                                              │ table (name,     │
                                                              │  type, source)   │
                                                              └─────────────────┘
```

**Design decisions:**

- **SQLite instead of a real feature store** (Feast, Tecton) because this is a learning project. The table schema mirrors what Feast would expect: an `entity_id`, a `feature_timestamp`, and one column per feature.
- **Data versioning** via DVC (or even a manual `data/{run_id}/` directory) so you can reproduce any training run with the exact data snapshot used.
- **Three-table design** in the feature store:
  - `features` — the feature values themselves (entity_id, timestamp, feature_name, value)
  - `feature_metadata` — feature name, dtype, description, source column
  - `pipeline_runs` — run_id, timestamp, git commit, row count, feature count

## Setup & Run

1. Install dependencies:
   ```bash
   pip install pandas numpy boto3 dvc
   ```
2. Place a sample CSV in S3 or use a local file:
   ```bash
   # sample: transactions.csv with columns [transaction_id, user_id, amount, timestamp, merchant_category]
   ```
3. Run the ETL:
   ```python
   # etl.py
   import pandas as pd
   import sqlite3
   from datetime import datetime

   # 1. Extract
   df = pd.read_csv("s3://my-bucket/raw/transactions.csv")  # or local path

   # 2. Clean
   df = df.dropna(subset=["amount", "user_id"])
   df["amount"] = df["amount"].clip(lower=0, upper=10000)
   df["timestamp"] = pd.to_datetime(df["timestamp"])

   # 3. Feature engineering
   df["day_of_week"] = df["timestamp"].dt.dayofweek
   df["hour"] = df["timestamp"].dt.hour
   df["amount_log"] = np.log1p(df["amount"])

   # 4. Load
   conn = sqlite3.connect("feature_store.db")
   df.to_sql("features", conn, if_exists="append", index=False)
   ```
   ```bash
   python etl.py
   ```
4. Query the feature store to verify:
   ```bash
   sqlite3 feature_store.db "SELECT COUNT(*), AVG(amount) FROM features"
   ```

## What You Learn

- Structuring an ETL pipeline with separate extract/clean/engineer/load stages
- Feature engineering patterns: datetime decomposition, log transforms, clipping
- The concept of a feature store and why training/serving feature consistency matters
- Data versioning with DVC to tie every experiment to an immutable dataset
- Writing idempotent ETL — running it twice should not duplicate rows (use upserts or run IDs)

## Next Steps

Once the basic pipeline is solid, here are natural progressions to level up, roughly in order of increasing complexity:

### 1. Orchestration & Scheduling
- Migrate from a single script to **Apache Airflow / Prefect / Dagster** with DAGs
- Add scheduling (daily/hourly), retries, alerting (Slack/PagerDuty)
- Incremental loads instead of full reloads

### 2. Real Feature Store
- Replace SQLite with **Feast** or **Tecton**
- Serve features for both training and online inference (low-latency)
- Point-in-time correct joins for training datasets

### 3. Stream Processing
- Add a **Kafka / Kinesis** streaming path alongside the batch path
- Use **Spark Structured Streaming** or **Flink** for real-time feature computation
- Lambda / Kappa architecture

### 4. Data Quality & Monitoring
- Great Expectations suite — automate expectations, run as a CI step
- Add **data drift / feature drift detection** (whylogs, Evidently AI)
- Automated alerting when quality checks fail

### 5. Multi-environment & CI/CD
- Separate dev / staging / prod environments
- **dbt** for transformation testing and lineage
- GitHub Actions CI/CD pipeline for testing ETL changes

### 6. Schema Evolution & Registry
- **Schema registry** (Avro / Protobuf) for managing schema changes
- Feature registry with ownership, tags, descriptions
- Lineage tracking (OpenLineage / Marquez / DataHub)

### 7. Distributed Processing
- Handle larger-than-memory datasets with **Spark** (PySpark) or **Dask**
- Partitioned reads, distributed joins, shuffle optimization

### 8. Advanced Feature Engineering
- Time-series windows (expanding windows, custom aggregations)
- Embedding generation (via LLM or embedding model)
- Categorical encoding with frequent-item dictionaries
- Cross-feature interactions

### 9. Data Lake / Lakehouse Integration
- Write to **Delta Lake** / **Iceberg** / **Hudi** for ACID transactions on data lakes
- Use **Trino** or **Athena** for querying

### 10. Observability & Lineage
- Full data lineage (end-to-end: raw → transformed → feature → model prediction)
- Metrics dashboard (data freshness, row counts, feature distributions over time)

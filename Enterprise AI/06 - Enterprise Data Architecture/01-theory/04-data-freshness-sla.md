# Data Freshness SLAs

Defining and enforcing how recent data must be for AI consumption.

## Freshness Tiers

| Tier | Max Staleness | Pipeline Type | SLA Cost |
|---|---|---|---|
| **Real-time** | < 1 second | Streaming (Kafka + Flink) | $$$$ |
| **Near real-time** | < 1 minute | Micro-batch (CDC + Kafka) | $$$ |
| **Frequent** | < 1 hour | Batch (15-min intervals) | $$ |
| **Daily** | < 24 hours | Batch (daily) | $ |
| **Static** | Days to weeks | Periodic refresh | $ |

## Mapping Data Sources to Tiers

| Data Source | Recommended Tier | Rationale |
|---|---|---|
| Stock prices, fraud signals | Real-time | Milliseconds matter |
| Customer support tickets | Near real-time | Agents need latest info |
| Product catalog | Frequent (1 hour) | Price changes are hourly |
| Legal documents | Daily | Slow-changing |
| Historical archives | Static | Never changes |

## SLA Definition Template

```yaml
data_sla:
  dataset: "customer_profiles"
  
  freshness:
    max_staleness: "15 minutes"
    checkpoint: "updated_at"      # column/timestamp marking freshness
    source_lag_tolerance: "2 minutes"  # acceptable source delay
  
  volume:
    min_records_per_batch: 1000
    max_records_per_batch: 100000
    expected_daily_growth: "50000 records"
  
  quality:
    completeness: 0.99            # non-null rate for required fields
    uniqueness: 1.0               # PK uniqueness
    validity: 0.995              # passes format validation
  
  monitoring:
    freshness_alert: "> 20 minutes"
    volume_anomaly: "> 50% deviation from expected"
    error_rate_alert: "> 1%"
```

## Measuring Freshness

### Freshness Metrics

| Metric | Definition | Target |
|---|---|---|
| **Source lag** | Time since source record was last updated | < SLA |
| **Pipeline lag** | Time from source extraction to sink availability | < 50% of SLA |
| **End-to-end lag** | Source update → queryable in vector DB | < SLA |
| **Staleness P50/P95/P99** | Distribution of data age at query time | P99 < SLA |

### Implementation

```python
# Track freshness per record
def track_freshness(record, extraction_time):
    return {
        "record_id": record["id"],
        "source_updated_at": record["updated_at"],
        "extracted_at": extraction_time,
        "transformed_at": None,  # filled during pipeline
        "indexed_at": None,      # filled when available in vector DB
    }

# Alert if SLA violated
def check_freshness_sla(metrics, sla_minutes=15):
    now = datetime.utcnow()
    for record in metrics:
        staleness = (now - record["source_updated_at"]).total_seconds()
        if staleness > sla_minutes * 60:
            alert(f"SLA violation: {record['record_id']} stale for {staleness}s")
```

## Pipeline Architecture by SLA Tier

### Real-Time (Streaming)

```
Source DB → WAL (Debezium) → Kafka → Flink/KSQL → Vector DB
                  ↓
              Schema Registry
```

**Components:**
- Debezium for CDC capture
- Kafka for buffering (retention: 7 days)
- Flink for transformations
- Direct sink to vector DB

**Cost:** ~$500-2000/month per stream
**Latency:** 100ms-1s

### Near Real-Time (Micro-Batch)

```
Source DB → Poll every 60s → Transform → Batch upsert to vector DB
                                          (every 30s or 1000 records)
```

**Components:**
- Airflow/Dagster for orchestration (1-min schedules)
- Python worker for transforms
- Batch API to vector DB

**Cost:** ~$100-500/month
**Latency:** 1-5 minutes

### Daily Batch

```
Source → Full extract → S3 (Parquet) → Spark/dbt → Vector DB (full rebuild)
```

**Components:**
- Airflow for daily schedule
- Spark for large-scale transforms
- Full index rebuild

**Cost:** ~$50-200/month
**Latency:** Hours (predictable)

## Freshness vs. Cost Trade-off

| Tier | Infrastructure Cost | Latency | Oper Complexity |
|---|---|---|---|
| Real-time | 10× | < 1s | 10× |
| Near real-time | 3× | < 5min | 3× |
| Hourly batch | 1.5× | < 1hr | 1.5× |
| Daily batch | 1× | < 24hr | 1× |

**Rule of thumb:** Tier of data → tier of pipeline. Don't run real-time pipelines on daily-changing data. Don't batch-process time-critical data.

## SLA Violation Response

```yaml
violation_response:
  freshness:
    - severity: "warning"       # 1-2× SLA
      action: "notify owner, page if persists 2 cycles"
    - severity: "critical"      # > 2× SLA
      action: "page on-call, check pipeline health, consider fallback"
      fallback: "serve stale data with 'last updated' warning"
  
  volume:
    - severity: "warning"       # 20-50% drop
      action: "check source availability"
    - severity: "critical"      # > 50% drop or zero
      action: "stop pipeline, investigate source, notify stakeholders"
  
  quality:
    - severity: "warning"       # 95-99% passing
      action: "log bad records, continue"
    - severity: "critical"      # < 95% passing
      action: "pause pipeline, investigate, reprocess"
```

## Monitoring Dashboard

```
Freshness SLA Dashboard
┌─────────────────────────────────────────────────┐
│ Dataset            │ SLA    │ Actual │ Status   │
├─────────────────────────────────────────────────┤
│ customer_profiles  │ 15min  │ 3min   │ ✅       │
│ product_catalog    │ 1hr    │ 45min  │ ✅       │
│ legal_docs         │ 24hr   │ 18hr   │ ✅       │
│ stock_prices       │ 1s     │ 2.5s   │ ⚠️ LAG  │
│ support_tickets    │ 5min   │ 12min  │ ❌ SLA   │
└─────────────────────────────────────────────────┘
```

## Architectural Patterns for Freshness

### 1. Lambda Architecture

```
Batch layer:  Complete, accurate, high latency
Speed layer:  Approximate, low latency (covers batch gap)
Serving:      Merge batch + speed results
```

Best for: Systems that need both accuracy and low latency.

### 2. Kappa Architecture

```
Single streaming pipeline for all data.
Batch = replay of stream from beginning.
```

Best for: Pure streaming systems (no batch needed).

### 3. Hybrid Freshness

```
Hot path:  Real-time (last 24 hours of data)
Cold path: Batch (full historical)
Query:     Route to hot or cold based on time range
```

Best for: Systems where recent data needs real-time freshness but older data is fine on batch.

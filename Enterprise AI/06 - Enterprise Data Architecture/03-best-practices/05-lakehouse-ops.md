# Lakehouse Operations Best Practices

## 1. Table Layout
- **Partitioning**: By date (`dt=2024-12-01`) for time-range pruning
- **Bucketing**: By join key (e.g., `customer_id`) for shuffle optimization
- **Z-ordering**: By frequently filtered column (e.g., `source_system`)
- File size target: 128 MB – 1 GB per file (tune for workload)

## 2. Data Lifecycle
| Phase | Duration | Storage Tier |
|-------|----------|-------------|
| Hot | 0–30 days | SSD-backed, high-throughput |
| Warm | 31–90 days | Standard S3/ADLS |
| Cold | 91–365 days | Infrequent access (S3 IA) |
| Archive | 1+ year | Glacier / Deep Archive |
| Delete | Per retention policy | — |

## 3. Optimization Operations
- **COMPACTION (OPTIMIZE)**: Merge small files into larger ones
  - Run when file count > expected count × 2
  - Schedule: daily during low-traffic window
- **VACUUM**: Remove stale data files beyond retention period
  - Retention: 7–30 days (allows time travel)
  - Schedule: weekly
- **ANALYZE**: Update table statistics for query optimizer
  - Run after any significant write (>10% data change)

## 4. Concurrency & Isolation
- Delta Lake default: optimistic concurrency
- For high-conflict tables (many concurrent writes at same partition):
  - Reduce partition size
  - Use `OPTIMIZE` with `ZORDER` to spread writes
  - Enable `delta.concurrentWrites` for specific use cases

## 5. Monitoring
- **Table health**: file count, record count, table size, partition skew
- **Operation latency**: OPTIMIZE, VACUUM, read/write times
- **Concurrency conflicts**: number of retries, deadlocks
- **Storage cost**: per-table growth rate, coldest data ratio

## 6. Security
- Column-level masking for sensitive fields
- Row-level filtering for multi-tenant tables
- Access logs: who queried what, when, how much data scanned
- Encryption: server-side (always), client-side (for regulated data)

## 7. Disaster Recovery
- Cross-region replication for critical tables (active-passive)
- Regular restore tests (at least quarterly)
- Point-in-time recovery: retain version history for 30+ days
- Documented RTO/RPO per table tier

## 8. Tools
- **Delta Lake + Spark**: Full lakehouse capabilities
- **Apache Iceberg**: Alternative with different partitioning model
- **Apache Hudi**: Strong upsert/deletion performance
- **Databricks**: Managed Delta Lake (Unity Catalog, auto-optimize)

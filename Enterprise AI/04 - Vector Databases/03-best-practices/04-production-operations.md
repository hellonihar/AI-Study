# Production Operations for Vector Databases

Running vector search reliably at scale: deployment, monitoring, backup, and incident response.

## Deployment Topologies

### Single Node (pgvector, Qdrant)
```
Application → [Load Balancer] → Vector DB (1 node)
                                  ├── Data directory (EBS/PD-SSD)
                                  └── WAL / replication slot
```
- Best for: < 10M vectors, non-critical workloads
- HA: WAL streaming to standby; pg automatic failover
- Risk: node failure = downtime (minutes to hours)

### Replicated Cluster (Qdrant, Milvus)
```
Application → [LB] → Coordinator → Shard 1 (primary + 2 replicas)
                                    Shard 2 (primary + 2 replicas)
                                    Shard 3 (primary + 2 replicas)
```
- Best for: 10M-100M vectors, HA required
- HA: automatic failover, read from any replica
- Risk: split-brain (rare with Raft-based consensus)

### Managed (Pinecone, Weaviate Cloud)
```
Application → API → Managed control plane → Auto-scaled pods
```
- Best for: teams without DB ops expertise
- HA: provider-managed (SLA: 99.9%+)
- Risk: vendor lock-in, egress costs

## Monitoring

### Essential Metrics

| Metric | What It Tells You | Alert Threshold |
|---|---|---|
| Query latency (P50/P95/P99) | Search performance | P99 > 100ms |
| QPS (queries per second) | Throughput | > 80% of provisioned |
| Recall@10 | Search quality drop | < 0.90 |
| Memory utilization | Index fit in RAM | > 85% |
| Disk IOPS | Compaction / indexing pressure | > 70% of provisioned |
| Segment count (Qdrant/Milvus) | Compaction lag | > 2× expected |
| Replication lag | Sync delay | > 1 second |
| Connection count | Client churn / leaks | > 80% of max |

### Logging
- Enable slow query logging (threshold: 50ms)
- Log index build/merge events
- Log client disconnects and retries
- Structured JSON format for log aggregation (ELK, Loki)

### Tracing
- Trace end-to-end: client → LB → coordinator → shard → storage
- Tag queries by tenant/customer for isolation monitoring
- Use OpenTelemetry for vendor-neutral instrumentation

## Backup and Recovery

| Strategy | RPO | RTO | Complexity |
|---|---|---|---|
| Periodic dump (pg_dump) | 1-24 hours | Hours | Low |
| WAL streaming + PITR | Seconds | Minutes | Medium |
| Snapshot (EBS/PD) | Minutes | Minutes | Medium |
| CDC to S3/GCS | Seconds | Minutes | High |
| Managed provider backup | Provider-defined | Minutes | None |

**Recommendation:** Combine periodic snapshots (daily) with WAL streaming (continuous). Test restore monthly.

## Compaction Strategy

Vector databases accumulate stale segments from deletes and updates.

| DB | Compaction Trigger | Config |
|---|---|---|
| Qdrant | Threshold `max_segment_number` (default: ∞) | `optimizers_*` settings |
| Milvus | `segment_row_limit` exceeded | `datacoord.segment.*` |
| pgvector | Autovacuum (standard Postgres) | `autovacuum_*` settings |

**Best practices:**
- Size segments to 10-100 MB for good balance
- Deletes are soft until compaction runs
- Schedule compaction during low-traffic windows
- Monitor segment count as leading indicator of compaction debt

## Scaling Strategy

### Vertical Scaling (Scale Up)
```
Trigger: CPU > 80%, memory > 85%, P50 latency > 20ms
Action: Increase instance size (2× RAM, 2× CPU)
Risk: Downtime during migration (minutes)
```

### Horizontal Scaling (Scale Out)
```
Trigger: QPS > threshold, index size approaching capacity
Action: Add shards (rebalance data)
Risk: Rebalancing impacts query performance; data must be re-partitioned
```

### Read Replicas
```
Trigger: Read QPS >> write QPS, read latency rising
Action: Add read-only replicas, route reads via LB
Risk: Stale reads (replication lag)
```

## Incident Response

### Common Incidents

**High query latency**
1. Check memory: index paged to disk?
2. Check compaction: too many segments?
3. Check QPS spike: traffic burst?
4. Scale up or add nodes

**Recall degradation**
1. Check if index needs rebuild (data mutations accumulated)
2. Check nprobe/efSearch configuration
3. Check if new vectors are being indexed correctly
4. Rebuild index if necessary

**Node failure**
1. Promote replica (automatic with Raft/RPAC)
2. Check data integrity (WAL replay)
3. Rebuild failed node from replica
4. Investigate root cause (disk, network, OOM)

**Slow index build**
1. Check CPU and memory during build
2. Reduce efConstruction (HNSW) or nlist (IVF)
3. Use async build if supported
4. Consider incremental indexing

## Pre-Production Checklist

- [ ] Load test at 2× expected peak QPS
- [ ] Test index rebuild with production data size
- [ ] Configure monitoring dashboards and alerts
- [ ] Test backup restore procedure
- [ ] Document runbook for top 5 incident types
- [ ] Configure resource limits (OOM protection)
- [ ] Set up slow query logging
- [ ] Configure connection pooling
- [ ] Test failover (kill primary node)
- [ ] Verify retention and archiving policy

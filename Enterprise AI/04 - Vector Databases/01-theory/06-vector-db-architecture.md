# Vector Database Architecture

How vector databases are built internally — the distributed systems concepts behind the API.

## Core Components

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────┴──────┐
│   Gateway   │  ← routing, auth, rate limiting
└──────┬──────┘
       │
┌──────┴──────┐
│  Coordinator│  ← metadata management, shard assignment
└──────┬──────┘
       │
┌──────┴──────────────────────────┐
│         Data Nodes               │
│ ┌─────┐ ┌─────┐ ┌─────┐        │
│ │Shard│ │Shard│ │Shard│  ...   │
│ │ 1   │ │ 2   │ │ 3   │        │
│ └─────┘ └─────┘ └─────┘        │
│   │       │       │            │
│ ┌─────┐ ┌─────┐ ┌─────┐        │
│ │Repl │ │Repl │ │Repl │        │
│ │ 1-1 │ │ 2-1 │ │ 3-1 │        │
│ └─────┘ └─────┘ └─────┘        │
└─────────────────────────────────┘
       │
┌──────┴──────┐
│ Object Store│  ← backup, snapshot, cold storage
└─────────────┘
```

## Sharding (Horizontal Scaling)

Vectors are distributed across nodes by hashing the vector ID or using range-based sharding:

```
hash(vector_id) % num_shards → assigned shard
```

- **Hash sharding:** Even distribution, but range queries are impossible.
- **Range sharding:** Custom partitioning (e.g., by tenant), but can cause hot spots.
- **Consistent hashing:** Minimizes data movement during re-sharding.

**Replication factor:** Typically 2–3. Each shard has N replicas on different nodes.

## Consistency Models

| Model | Reads | Writes | Performance | Products |
|---|---|---|---|---|
| **Strong** | Read latest write | Wait for N replicas | Slowest | Milvus (Raft), Zilliz |
| **Eventual** | May read stale | Return immediately | Fastest | Pinecone, Chroma |
| **Tunable** | Configurable per-request | Configurable | Flexible | Cassandra-based systems |

**Production choice:** Eventual consistency is acceptable for most vector search workloads (stale search results are rarely critical). Use strong consistency for metadata operations.

## WAL (Write-Ahead Log)

All writes are first recorded in a WAL before being applied to the index:

```
Write → WAL (sequential write) → Index update (async)
```

- **Purpose:** Crash recovery. If the node fails mid-write, replay the WAL.
- **Performance:** WAL is sequential (fast), index update is random (slow).
- **Flush interval:** Typically 1–10 seconds. Tune for your durability vs. throughput trade-off.

## Index Build and Compaction

Vectors arrive over time. The index needs to absorb new vectors without rebuilding entirely:

### Segment-Based Approach (used by Milvus, Qdrant)

```
Small segments (new writes) → Merge → Larger segments → Merge → Final index
```

- **Small segments** use flat search (fast to update).
- **Large segments** use HNSW/IVF (fast to search).
- **Compaction** merges small segments into larger ones in the background.

### Streaming Index (Pinecone, Weaviate)

- **HNSW supports insertions directly** — new vectors are added to the graph.
- **But:** Quality degrades over time as the graph becomes imbalanced.
- **Periodic optimization:** Re-build graph from scratch every few hours/days.

## Memory Hierarchy

```
                           Latency    Capacity
┌─────────────────────┐
│  L1: In-memory cache│  < 1μs     1–10K vectors
├─────────────────────┤
│  L2: RAM index      │  < 10μs    Up to 100M vectors (compressed)
├─────────────────────┤
│  L3: SSD vector store│  < 1ms    Up to 1B+ vectors
├─────────────────────┤
│  L4: Object store   │  Seconds   Archival, backups
└─────────────────────┘
```

## Architecture by Product

| Product | Cluster Management | Consistency | Sharding | Storage Engine |
|---|---|---|---|---|
| **Milvus** | Raft (etcd) | Strong | Hash + range | Segment-based (L0→L1→L2→L3) |
| **Qdrant** | Raft | Strong | Hash | Segment-based (WAL + HNSW) |
| **Weaviate** | Gossip + Raft | Tunable | Hash (automatic) | In-memory + inverted + HNSW |
| **Pinecone** | Proprietary | Eventual | Auto-sharding | Proprietary |
| **pgvector** | PostgreSQL | Strong | No native sharding | PostgreSQL storage |

## Best Practices

- **Understand your consistency needs.** Most vector search doesn't need strong consistency. Accepting eventual consistency gives 2–5× better write throughput.
- **Plan for compaction windows.** During compaction, query performance may degrade. Schedule compaction during low-traffic periods.
- **Monitor shard imbalance.** A "hot shard" with 10× more data than others hurts tail latency. Re-shard proactively.
- **Test failure modes.** What happens when a node goes down? Can queries still succeed with remaining replicas?

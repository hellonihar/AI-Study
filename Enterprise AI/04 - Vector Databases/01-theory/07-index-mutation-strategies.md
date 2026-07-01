# Index Mutation Strategies

Handling inserts, updates, and deletes in vector indexes without rebuilding.

## The Challenge

Unlike traditional databases, ANN indexes are brittle structures. Adding or removing vectors can significantly degrade search quality if not handled carefully.

## Inserts

### Approach 1: Direct Insertion (HNSW)

HNSW supports inserting vectors into the graph:

```
1. Find the insertion position (greedy search from entry point).
2. Connect the new node to its M nearest neighbors.
3. If any neighbor exceeds M_max, prune its connections.
```

- **Advantage:** No rebuild needed. Instant availability.
- **Disadvantage:** Graph quality degrades over time (connections become suboptimal).
- **Re-balance frequency:** Every 100K–1M inserts for most workloads.

### Approach 2: Segment-Based (IVF, Milvus, Qdrant)

New vectors go into a small "segment" with a flat index:

```
New writes → Small segment (flat, fresh)
            ↓ (background compaction)
        Larger segment (HNSW/IVF)
            ↓ (background compaction)
        Final index (optimized)
```

- **Advantage:** Consistent query performance regardless of write rate.
- **Disadvantage:** New vectors may not be searchable immediately (compaction delay).

## Deletes

### Tombstone Approach

Mark the vector as deleted without removing it from the index:

```
Delete request → Set tombstone flag on vector_id
During search: Skip vectors with tombstone flag
During compaction: Physically remove tombstones
```

- **Advantage:** O(1) delete, no index disruption.
- **Disadvantage:** Index contains dead entries → wastes space and slightly degrades search quality.

### Physical Deletion (HNSW)

Remove the node from the graph and reconnect its neighbors:

```
1. Mark node as deleted (tombstone).
2. During the next graph optimization pass:
   a. Remove the node from all neighbor lists.
   b. Reconnect its neighbors to each other.
   c. Compact the adjacency list array.
```

- **Advantage:** Clean index, no wasted space.
- **Disadvantage:** Expensive operation. Batch deletes for efficiency.

## Updates

An update is equivalent to a delete + insert:

```
Update request → Delete old vector → Insert new vector
```

- **Versioned updates:** Keep both old and new versions, tag with timestamps. Search returns the latest.
- **In-place updates:** Supported by some systems (Qdrant, Weaviate) — overwrite the vector at the same position (only possible if index structure supports it).

## Compaction

The process of rebuilding index segments to remove tombstones and optimize structure:

### Segment Compaction (Milvus, Qdrant)

```
1. Read all vectors from small segments.
2. Remove tombstoned vectors.
3. Build a new, optimized index (HNSW/IVF) with remaining vectors.
4. Atomically swap the new segment for the old ones.
5. Delete the old segments.
```

### Graph Compaction (HNSW)

```
1. Traverse the entire graph.
2. For each node, re-compute its M nearest neighbors.
3. Update neighbor lists.
4. This restores graph quality after many insertions.
```

## Mutation Performance by Product

| Product | Inserts (peak) | Deletes | Compaction | Write Amplification |
|---|---|---|---|---|
| **Milvus** | 10K–50K/s/node | Tombstone + batch | Automatic | Medium (segment merges) |
| **Qdrant** | 10K–50K/s/node | Tombstone + batch | Automatic | Low (optimizer configurable) |
| **Weaviate** | 1K–10K/s/node | Tombstone | Manual (CRUD) | Low |
| **Pinecone** | Managed (auto) | Managed | Managed | Unknown (proprietary) |
| **pgvector** | PostgreSQL rates | SQL DELETE | VACUUM | Low |

## Best Practices

- **Batch writes** for higher throughput. A single batch of 1000 vectors is 10–50× faster than 1000 individual writes.
- **Schedule compaction during low-traffic windows** — it consumes CPU and I/O.
- **Monitor delete ratio.** If > 30% of vectors are tombstoned, schedule a full rebuild.
- **For workloads with frequent updates** (> 10% daily), prefer segment-based systems (Milvus, Qdrant) over pure HNSW.
- **Test mutation behavior.** Write 100K vectors, delete 20%, search recall. If recall drops significantly, your index needs better compaction.
- **Consider append-only design.** Instead of updating vectors, create new versions and filter by version during search. This avoids mutation complexity entirely.

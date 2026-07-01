# State and Consistency Best Practices

## State Management Strategy

### Decision Flow
```
How many agents need to share state?
├── 1 agent → Local state (in-memory)
└── 2+ agents → External state store
    ├── Is strong consistency required?
    │   ├── Yes → Centralized store (Redis/DB) with locks
    │   └── No → Eventual consistency (event bus)
```

### When to Use Each Store

| Store | Best For | Consistency | Availability |
|-------|----------|-------------|-------------|
| In-memory | Single agent, ephemeral | Strong | Low (restart loses data) |
| Redis | Shared state, fast access | Strong (single node) | Medium |
| PostgreSQL | Persistent, complex state | Strong | High |
| Event log (Kafka) | Audit trail, replay | Eventual | High |

## Idempotency

### Why It Matters
In multi-agent systems, messages may be delivered multiple times. Without idempotency, duplicate messages cause duplicate work, double charges, or inconsistent state.

### Implementation

```python
class IdempotentHandler:
    def __init__(self):
        self.processed_ids = set()

    def handle(self, message):
        if message.id in self.processed_ids:
            return self.cached_results[message.id]
        result = self.process(message)
        self.processed_ids.add(message.id)
        self.cached_results[message.id] = result
        return result
```

### TTL for Idempotency Cache
| Use Case | TTL | Rationale |
|----------|-----|-----------|
| Task messages | 24 hours | Max task lifetime |
| Tool results | 1 hour | Results may change |
| Search queries | 5 minutes | Fast-changing data |
| Agent responses | 1 hour | Same query, same response |

## Conflict Resolution

### Last-Write-Wins (LWW)
Simplest approach. Last write overwrites previous state.

**Best for**: Non-critical state, logs, metrics.

### CRDTs (Conflict-Free Replicated Data Types)
Data types that merge automatically without conflicts.

**Best for**: Collaborative state, counters, sets.

### Version Vectors
Each update increments a version. Conflicts detected and resolved manually or by application logic.

**Best for**: Complex state requiring human review.

## Consistency Patterns

### Read-Your-Writes
After an agent writes, it always reads its own write.

```python
def write_with_readback(agent, key, value):
    write_to_store(key, value, writer=agent.id)
    # Subsequent reads from this agent always see the write
```

### Quorum Reads/Writes
Require acknowledgment from N of M replicas.

```python
R + W > N  # Strong consistency
# Example: N=3, W=2, R=2 → strong consistency
```

## State Serialization

- Use JSON for most state (human-readable, universally supported)
- Use Protobuf for high-throughput (>1000 updates/sec)
- Include schema version in state objects
- Forward-compatible: never remove fields, only deprecate

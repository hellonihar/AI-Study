# State Management

## Challenges in Multi-Agent State

- **Distributed state**: No single agent has the full picture
- **Consistency**: Agents may have conflicting views of state
- **Latency**: State synchronization takes time
- **Idempotency**: Same message delivered twice should not cause double-effects

## State Management Strategies

### Centralized State Store

All agents read/write to a single state store (Redis, database).

```
Agent A ──→ State Store (Redis) ←── Agent B
Agent C ─────────────────────────── Agent D
```

**Pros**: Consistent view, simple to reason about, easy to debug.
**Cons**: Single point of failure, bottleneck for high-throughput, state store can be overwhelmed.

### Event Sourcing

State is derived from an immutable event log. Agents replay events to reconstruct state.

```python
events = [
    {"type": "task_created", "task_id": "t-123", "payload": {...}},
    {"type": "document_found", "task_id": "t-123", "doc_id": "d-1"},
    {"type": "summary_generated", "task_id": "t-123", "summary": "..."},
]
state = replay(events)  # Reconstruct current state
```

**Pros**: Complete audit trail, time travel, strong consistency.
**Cons**: More complex, storage grows unbounded (compaction needed).

### Distributed Consensus (Raft/Paxos)

Agents agree on state changes through a consensus protocol.

**Pros**: Strong consistency, no single point of failure.
**Cons**: Complex, slow for high-frequency updates, overkill for most agent systems.

## Idempotency

Every agent action should be idempotent — applying it twice produces the same result as applying it once.

```python
def process_message(message):
    if message.id in self.processed_ids:
        return self.cached_results[message.id]  # dedup
    result = self.execute(message)
    self.processed_ids.add(message.id)
    self.cached_results[message.id] = result
    return result
```

## Consistency Models

| Model | Guarantee | Latency | Use Case |
|-------|-----------|---------|----------|
| Eventual | State converges over time | Lowest | Non-critical, collaborative |
| Strong | All agents see same state | Highest | Financial, authorization |
| Causal | Causally related updates ordered | Medium | Task orchestration |
| Read-your-writes | Writer sees own writes | Low | User-facing agents |

## State Conflict Resolution

When two agents update the same state:

1. **Last-write-wins**: Simplest, can lose data
2. **CRDTs (Conflict-Free Replicated Data Types)**: Merge automatically, no conflicts
3. **Version vectors**: Track versions, manual merge on conflict
4. **Locks/pessimistic**: Block concurrent writes, hurts throughput

## Production Recommendations

| Component | Strategy |
|-----------|----------|
| Task state | Centralized (Redis) with TTL |
| Agent memory | Event sourcing (append-only) |
| Tool results | Cache (Redis, TTL 1 hour) |
| Agent registry | Configuration file (rarely changes) |
| Locks | Redis Redlock (for critical sections) |

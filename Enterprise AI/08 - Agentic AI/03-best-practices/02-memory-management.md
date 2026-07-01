# Memory Management Best Practices

## Memory Architecture Decision

| Factor | Use Working Only | Full Memory System |
|--------|-----------------|-------------------|
| Session length | < 10 turns | 10+ turns |
| Need for cross-session recall | No | Yes |
| Cost sensitivity | High | Medium |
| Implementation complexity | Low | High |

## Working Memory (Context Window)

### Token Budget Allocation
```
Total context budget: 4,000 tokens
├── System prompt:         500  (12%)
├── Recent conversation: 1,000  (25%)
├── Retrieved memories:  1,000  (25%)
├── Tool results:        1,000  (25%)
└── Current action:        500  (13%)
```

### Pruning Strategy
- Remove tool outputs older than 3 steps
- Summarize long conversation threads into a single "summary so far" turn
- Keep only the last N user/assistant turns (N=10–20)
- Drop redundant or superseded information

## Long-Term Memory (Vector Storage)

### When to Store
- Completed tasks (store goal + outcome)
- User preferences (explicit or inferred)
- Key facts extracted from conversations
- Error patterns (what went wrong and how it was fixed)

### When NOT to Store
- Transient conversation (small talk, greetings)
- Sensitive data (PII, credentials — never store)
- Already summarized in episodic memory
- Duplicate or near-duplicate of existing memory

### Retrieval Strategy

```python
def retrieve_memories(query):
    # Priority 1: Exact match (cache hit)
    if exact_cache(query):
        return cache[query]

    # Priority 2: Semantic similar
    semantic = vector_db.search(query, top_k=3)

    # Priority 3: Recency (last N interactions)
    recent = working_memory.last_n(5)

    return merge(semantic, recent)
```

## Memory Consolidation Schedule

| Frequency | Action |
|-----------|--------|
| Per task | Store task outcome |
| Per session | Summarize and store key facts |
| Daily | Consolidate multiple short memories |
| Weekly | Prune low-relevance memories (decay) |

## Forgetting Strategy

- **TTL-based**: Memories expire after N days (7 for short-term, 30 for long-term)
- **Access-based**: Memories not accessed in N days are archived
- **Conflict-based**: If new info contradicts old, keep both with recency weighting
- **Manual deletion**: User can delete specific memories

## Cost Optimization

| Technique | Savings | Quality Impact |
|-----------|---------|---------------|
| Prune context to last 10 turns | -40% tokens | Minimal |
| Summarize instead of full history | -60% tokens | Low (good summaries) |
| Cache frequent queries | -80% retrieval cost | None |
| Batch memory writes | -50% write operations | None |

# Memory Systems

## Why Agents Need Memory

Without memory, each agent interaction starts from scratch. Memory enables:
- **Continuity**: Carry context across turns
- **Learning**: Improve from past mistakes
- **Personalization**: Adapt to user preferences
- **Efficiency**: Avoid redundant work

## Memory Types

### Short-Term Memory (Working Memory)
- Current conversation turns
- Active task state and progress
- Recent tool outputs
- Limited to context window (~4K–200K tokens)

**Implementation**: Append-only list of messages in the LLM context window.

### Long-Term Memory (Semantic Memory)
- Facts and knowledge from past interactions
- User preferences and patterns
- Domain-specific knowledge

**Implementation**: Vector database storing embeddings of past interactions. Retrieve relevant memories via semantic search.

### Episodic Memory
- Specific past task episodes
- What worked and what didn't
- Task outcomes for learning

**Implementation**: Structured logs of (task, action, outcome) triples. Query by task similarity.

## Memory Architecture

```
User Input
    │
    ▼
┌─────────────┐     ┌─────────────────┐
│ Short-Term  │────▶│ Reasoning Engine │
│ (Context)   │     │ (LLM + Context)  │
└─────────────┘     └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Memory Manager  │
                    └──┬────┬────┬────┘
                       │    │    │
              ┌────────┘    │    └────────┐
              ▼             ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Semantic │ │ Episodic │ │ Working  │
        │ (Vector) │ │ (Logs)   │ │ (Recent) │
        └──────────┘ └──────────┘ └──────────┘
```

## Retrieval Strategy

```python
def retrieve_relevant_memories(query, top_k=5):
    # 1. Semantic: most relevant facts
    semantic = vector_db.search(query, top_k=top_k)

    # 2. Episodic: similar past tasks
    episodic = episodic_db.search(query, top_k=3)

    # 3. Recent: last N turns (always included)
    recent = working_memory.last_n(10)

    return merge(semantic, episodic, recent)
```

## Memory Management

### Pruning
- Remove redundant or outdated memories
- Summarize long conversation threads
- Archive completed task details, keep only outcomes

### Consolidation
- Periodically extract key facts from recent interactions
- Update long-term memory with new knowledge
- Remove contradictory information

### Forgetting
- Implement decay: memories lose relevance over time
- Set TTL on temporary facts (user session, task context)
- Explicit deletion for sensitive data

## Storage Options

| Storage | Best For | Trade-off |
|---------|----------|-----------|
| In-memory dict | Working memory | Lost on restart |
| SQLite | Small-scale persistent memory | Not distributed |
| PostgreSQL | Structured memory | Slower for vectors |
| Vector DB (Qdrant, Pinecone) | Semantic search | Requires infrastructure |
| Redis | Fast cache + memory | Limited querying |

## Cost Considerations

| Aspect | Cost Impact |
|--------|-------------|
| Memory in context window | Increases token usage 10–50% |
| Vector search per step | ~$0.0001–0.001 per query |
| Memory storage | $10–100/month for 1M memories |
| Consolidation calls | Occasional LLM calls to summarize |

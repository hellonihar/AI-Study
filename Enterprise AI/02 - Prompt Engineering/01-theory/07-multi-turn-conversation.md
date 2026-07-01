# Multi-Turn Conversation

Managing state, context, and coherence across multiple user-assistant exchanges.

## The Context Growth Problem

Each turn appends tokens to the conversation:

```
Turn 1: 200 tokens → Turn 2: 450 tokens → Turn 3: 750 tokens → ...
```

At some point, the conversation exceeds the model's context window. Without management, older turns are silently dropped.

## State Tracking Approaches

| Approach | Description | Best For |
|---|---|---|
| **Raw history** | Append every turn as-is. | Short conversations (< 10 turns). |
| **Sliding window** | Keep last N turns, drop oldest. | General purpose, simple. |
| **Summarization** | Compress old turns into a summary. | Long conversations, complex topics. |
| **Structured state** | Extract key facts into a schema. | Task-oriented (booking, support). |
| **Hybrid** | Keep recent N turns full + summarized history. | Best quality, moderate complexity. |

## Summarization Strategy

```python
def compress_history(history, max_tokens=4000):
    while token_count(history) > max_tokens:
        # Identify the oldest compressible block
        old_block = extract_oldest_turns(history, n=2)
        summary = llm.summarize(
            f"Summarize this conversation concisely, preserving "
            f"all facts, decisions, and unresolved questions:\n{old_block}"
        )
        history = replace(history, old_block, summary)
    return history
```

**Compression ratio:** Typically 10:1 (two turns of 500 tokens → 50-token summary).

## Structured State Extraction

For task-oriented conversations (support, booking), extract state after each turn:

```python
state_schema = {
    "intent": "str",
    "resolved_issues": ["str"],
    "pending_actions": ["str"],
    "collected_info": {"key": "value"}
}

def update_state(conversation_history, current_state):
    prompt = f"""Current state: {json.dumps(current_state)}
    Conversation: {conversation_history}
    Extract updated state as JSON matching: {json.dumps(state_schema)}"""
    return llm.json_mode(prompt)
```

Instead of appending full conversation history, inject only the structured state — 10 tokens instead of 1000.

## Context Budget Management

Allocate token budgets per component:

```
Total Budget: 8000 tokens
├── System prompt: 500    (fixed)
├── State: 200            (structured, grows slowly)
├── Retrieved context: 3000 (variable, per RAG call)
├── Conversation history: 3000 (managed, compressed)
└── Current user input: 300  (variable)
     └── Response: 1000      (max_tokens)
```

## Best Practices

- **Start truncating at 70% of context window** — leaving headroom for the response and unexpected long input.
- **Compress before truncating** — a summary preserves more information than dropping turns.
- **For task-oriented conversations, use structured state** — it's cheaper, more reliable, and searchable.
- **Track conversation depth** — alert when conversations exceed N turns (may indicate an issue).
- **Log compressed history alongside full history** — useful for debugging quality issues.

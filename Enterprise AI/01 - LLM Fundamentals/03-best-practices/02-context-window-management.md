# Context Window Management

Efficiently using the limited context window for cost-effective inference.

## The Cost of Context

Context = input tokens = cost.

| Context Length | Approximate Cost (GPT-4o, per 1K calls) |
|---|---|
| 4K | ~$10 |
| 32K | ~$80 |
| 128K | ~$320 |

Every token in the context also slows inference (KV cache grows, attention scales O(n²)).

## Strategies

### 1. Retrieve Only What's Needed

Don't stuff the entire document into context. Retrieve the most relevant chunks:

```
❌ Bad: "Here's the entire 100-page manual. Answer the question."
✅ Good: "Here are the 3 most relevant sections (approx 2K tokens). Answer the question."
```

### 2. Structured Context with Prioritization

```
[SYSTEM]  ← High priority (always included)
[RETRIEVED] ← High-priority chunks only
[HISTORY] ← Summarized or truncated
[USER]    ← Current question (always included)
```

### 3. Sliding Window for Conversations

```
Turn 1: [User] [Assistant]                    → cache
Turn 2: [User] [Assistant] [User2] [Assist2]  → append
Turn 3: [User] [Assistant] [User2] [Assist2]  [User3] [Assist3] → append
Turn N: If total > max_context:
          Summarize oldest turns → replace with summary
```

### 4. Summarization-Based Compression

When context exceeds limit, compress the oldest part:

```python
def compress_history(history, max_tokens=4000):
    while count_tokens(history) > max_tokens:
        oldest = extract_oldest_turn(history)
        summary = llm.summarize(oldest)  # 10:1 compression
        history = replace(history, oldest, summary)
    return history
```

### 5. KV Cache Prefix Sharing

If many requests share a prefix (system prompt + common context), compute its KV cache once:

- vLLM: automatic prefix caching (enabled by default).
- OpenAI: prompt caching (automatic for repeated prefixes).
- Anthropic: prompt caching (enable via `cache_control`).

## Monitoring

Track these metrics per request:

- `prompt_token_count` — are system prompts growing?
- `response_token_count` — is the model getting verbose?
- `cache_hit_tokens` — what fraction of prefix was cached?

## Best Practices

- **Set `max_tokens` per request** to prevent runaway generation.
- **Budget context per use case** — allocate token budgets for system, context, history, and user.
- **Log overflow events** — if you're constantly truncating, your retrieval or summarization needs attention.
- **Use the smallest context that works** — adding irrelevant context hurts both cost and quality (attention dilution).

# Context Windowing

Managing the LLM's limited context window: selecting, ordering, and compressing retrieved passages.

## The Context Window Problem

LLMs have a limited context window. Every retrieved passage consumes tokens. Poor window management causes:
- **Lost in the middle** — LLMs pay less attention to passages in the middle of the context (Liu et al., 2023)
- **Token overflow** — truncation discards potentially useful passages
- **Noise dilution** — irrelevant passages reduce the signal-to-noise ratio

## Lost in the Middle Effect

```
Position:  [Start] [Middle]         [End]
Recall:      95%     50%             90%

Passage at position 1: 95% recall
Passage at position 8: 50% recall
Passage at position 15: 90% recall
```

U-shaped recall curve: LLMs attend most to the first and last passages.

**Mitigations:**
1. Place the most relevant passages at the start and end
2. Limit to 5-10 passages total (re-rank → keep top-k)
3. Use structured context formats that draw attention

## Context Window Sizes by Model

| Model | Max Context | Effective Context* | Recommended Max Passages |
|---|---|---|---|
| GPT-4 turbo | 128K | 32K | 20-30 (512-token chunks) |
| GPT-4o | 128K | 64K | 40-60 |
| Claude 3.5 Sonnet | 200K | 100K | 60-100 |
| Gemini 1.5 Pro | 2M | 500K | 300-500 |
| Llama 3.1 70B | 128K | 64K | 40-60 |
| Mistral Large | 128K | 48K | 30-50 |

_* Effective context = window where model maintains reliable performance. Actual varies by task and model._

## Strategies

### 1. Top-K Selection

Return only the k most relevant passages. Simple, effective.

```
retrieved = re_rank(query, candidates, top_k=50)
selected = retrieved[:k]   # k=5-10 for most models
```

**k vs. Recall:**
```
k=1:  high precision, low recall
k=5:  good balance (0.85-0.90 recall@5)
k=10: high recall (0.92-0.96)
k=20: marginal gain, wastes context
```

### 2. Re-Rank + Re-order

Place re-ranked passages at start and end positions.

```
# worst: insert reverse order (most relevant in middle)
context = retrieved[::-1]

# better: most relevant at start
context = retrieved[:]

# best: most relevant at start and end
best = retrieved[:len(retrieved)//2]
rest = retrieved[len(retrieved)//2:]
context = best + rest[::-1]
```

The last approach yields 5-10% higher answer accuracy vs. naive ordering.

### 3. Summary-Based Windowing

When context is too large, summarize before generating:

```
Step 1: For each chunk, generate a 1-sentence summary
Step 2: Search summaries first
Step 3: Retrieve full text for top-k summaries
Step 4: Include summaries of retrieved chunks as context headers
```

Reduces token usage by 3-5× while preserving key information.

### 4. Sliding Context Window

For very long documents that exceed the context window:

```
Window 1: [chunk 1][chunk 2][chunk 3][chunk 4] → answer partial
Window 2: [chunk 5][chunk 6][chunk 7][chunk 8] → answer partial
...
Merge: Summarize each window, then answer from summaries
```

Used in document QA over books, long reports, legal documents.

### 5. Chunk Compression

Reduce chunk size without losing information:

| Technique | Compression | Quality Loss |
|---|---|---|
| Remove stop words | 20-30% | Minimal |
| Keep only key sentences | 40-60% | Low (with good extractor) |
| LLM summarization | 70-90% | Medium (hallucination risk) |
| Information extraction | 80-95% | High (task-specific) |

**Recommendation:** Remove stop words and boilerplate. Avoid LLM-based compression due to hallucination risk.

### 6. Multi-Turn Context Accumulation

For conversational RAG, accumulate retrieved chunks across turns:

```
Turn 1: Query → retrieve → generate → store {query, chunks, answer}
Turn 2: New query + previous context → retrieve → generate
```

```python
# Previous context stored in session
session_context = {
    "previous_chunks": [...],    # last N retrieved chunks
    "previous_answer": "...",    # last answer
    "conversation_summary": "..." # running summary
}

# New turn
new_chunks = retrieve(new_query)
all_chunks = dedup(new_chunks + session_context["previous_chunks"])
# Trim to fit context window
context = trim_to_fit(all_chunks, max_tokens=4000)
```

## Practical Configuration

```yaml
context_window:
  # Selection
  max_passages: 10
  min_passages: 3
  passage_order: "best_first_last"  # or "best_first" or "relevance_desc"

  # Truncation
  truncation_strategy: "keep_first"  # or "keep_last" or "keep_both"
  max_total_tokens: 4096
  max_chunk_tokens: 512
  overlap_compression: true          # deduplicate overlapping sentences

  # Formatting
  passage_format: "[{index}] {source}: {text}"
  separator: "\n---\n"
  system_prefix: "Answer using only the provided passages."
```

## Monitoring

Monitor these metrics per query to detect context window problems:

| Metric | Good | Warning | Bad |
|---|---|---|---|
| Context utilization | 50-80% | > 95% or < 20% | > 100% (truncated) |
| Passages per query | 5-10 | 1-3 or 15+ | 0 or 20+ |
| Avg passage length | 300-500 tokens | < 100 or > 1000 | — |
| Position of best passage | 1-2 | 3-5 | 6+ (lost in middle) |

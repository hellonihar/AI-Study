# Chunking Strategies

How to split documents into retrievable passages — the single most impactful RAG parameter.

## Why Chunking Matters

Chunking determines:
- **Retrieval quality** — chunks must contain complete, self-contained information
- **Context utilization** — every token in the LLM context window should be useful
- **Recall** — if the answer straddles a chunk boundary, retrieval fails
- **Latency** — more chunks = more retrieval time and more context tokens consumed

A 5% improvement in chunking quality can yield 20% improvement in answer accuracy.

## Chunking Methods

### 1. Fixed-Size Chunking

```
chars: [0-512)  [256-768)  [512-1024) [768-1280) ...
       overlap=128 characters
```

| Parameter | Typical Value | Effect |
|---|---|---|
| Chunk size | 256-1024 tokens | Smaller = more precise, less context |
| Overlap | 10-20% of chunk size | Prevents boundary splits |
| Unit | Characters or tokens | Token-based is more predictable |

**Best for:** Simple documents, code, log files
**Worst for:** Narrative text, documents with section boundaries

### 2. Recursive Character Splitting

Starting from a large separator, recursively split if chunk exceeds max size:

```
Priority: \n\n > \n > . > ! > ? > whitespace > character
```

Common implementation: LangChain's `RecursiveCharacterTextSplitter`.

| Separator | Preserves |
|---|---|
| `\n\n` (paragraph) | Paragraph boundaries |
| `\n` (line) | Lines |
| `.` (sentence) | Sentence boundaries |
| ` ` (word) | Words |

**Best for:** General text, articles, documentation
**Parameters:** `chunk_size=1000`, `chunk_overlap=200`, `separators=[paragraph, sentence, word]`

### 3. Semantic Chunking

Use embeddings to detect topic shifts:

```
1. Embed sentences in sliding windows of 3-5
2. Compute cosine similarity between adjacent windows
3. Split when similarity drops below threshold (e.g., 0.7)
4. Merge very small chunks (< 3 sentences) with neighbors
```

| Threshold | Effect |
|---|---|
| 0.5 | Fewer, larger chunks (risk: under-split) |
| 0.7 | Good balance |
| 0.9 | Many, small chunks (risk: over-split) |

**Best for:** Narrative text, long-form articles, research papers
**Cost:** Requires embedding model call per sentence window — adds latency and cost

### 4. Document-Aware Chunking

Use document structure (headings, sections) as natural boundaries:

```
┌─────────────────────────────────────┐
│ # Introduction                      │ <── chunk 1
│  ...paragraphs...                   │
├─────────────────────────────────────┤
│ ## Background                       │ <── chunk 2
│  ...paragraphs...                   │
├─────────────────────────────────────┤
│ ## Methodology                      │ <── chunk 3
│  ...paragraphs...                   │
└─────────────────────────────────────┘
```

**Implementation:** Parse Markdown/HTML headers, PDF sections via outline tree.

**Best for:** Structured documents (docs, wikis, books, reports)
**Advantage:** Each chunk has section context — retrieval includes heading hierarchy

### 5. Hierarchical / Sliding Window

Two-level chunking: large parent chunks for context + small child chunks for retrieval:

```
Retrieved chunk: small (256 tokens)
Context window: parent chunk (2048 tokens, containing the child)
```

**Why:** Small chunks improve retrieval precision. Parent chunk provides surrounding context for generation.

**Best for:** Production RAG where precision matters
**Trade-off:** Doubles the retrieval cost (fetch child, then parent)

## Comparison Matrix

| Method | Retrieval Precision | Context Coherence | Implementation Complexity | Best Scale |
|---|---|---|---|---|
| Fixed-size | Low | Low | Trivial | Any |
| Recursive | Medium | Medium | Simple | Any |
| Semantic | High | High | Medium | < 10K docs |
| Document-aware | High | Very high | High | Structured docs |
| Hierarchical | Very high | Very high | Medium | > 10K docs |

## Chunk Size Trade-offs

```
Small (128-256 tokens)
  Pros: High precision, less noise, more retrievable chunks
  Cons: Missing context, more chunks to search, boundary risk
  Use: FAQ, short answers, fact lookup

Medium (512-1024 tokens)
  Pros: Good balance for most use cases
  Cons: None significant
  Use: Default for most RAG systems

Large (1024-4096 tokens)
  Pros: Complete context, fewer boundary issues
  Cons: Lower precision, wastes context window, more noise
  Use: Summarization, long-form Q&A
```

## Chunk Overlap

| Overlap | Benefit | Cost |
|---|---|---|
| 0% | Minimal storage, no duplicates | High boundary risk |
| 10% | Catches most boundary splits | Slight storage increase |
| 20% | Safe default | 20% more chunks |
| 50% | Very safe | Doubles storage and retrieval |

## Embedding Model Context Length

Embedding models have a max input length (e.g., 512 tokens for MiniLM, 8192 for BGE-M3). Chunks exceeding this get truncated, losing tail information.

| Embedding Model | Max Tokens | Max Chunk Size |
|---|---|---|
| all-MiniLM-L6-v2 | 256 | 256 tokens |
| BGE-base | 512 | 512 tokens |
| BGE-large | 512 | 512 tokens |
| BGE-M3 | 8192 | 8192 tokens |
| OpenAI text-embedding-3-small | 8191 | 8191 tokens |

**Rule:** Chunk size ≤ embedding model context length. If using BGE-base, don't chunk at 1024 tokens.

## Practical Recommendation

For a general-purpose production RAG system:

1. **Start with:** Recursive splitting at 512 tokens, 20% overlap
2. **Add:** Document-aware boundaries (at least heading preservation)
3. **Profile:** Measure recall@k at different chunk sizes on your data
4. **Upgrade to:** Hierarchical (256 token chunks + 2048 token parents) if precision matters
5. **Customize:** Semantic chunking if your documents have variable topic density

The optimal chunking strategy is data-dependent. Run an ablation study before fixing it in production.

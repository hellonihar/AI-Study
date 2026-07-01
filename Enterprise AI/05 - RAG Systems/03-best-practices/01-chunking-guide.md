# Chunking Guide

Practical recommendations for chunking documents in production RAG systems.

## The One-Parameter Heuristic

If you only tune one thing in your RAG pipeline, tune chunk size. A 512-token chunk with 20% overlap is the right default for 80% of use cases. Change it only when you have evidence that it's suboptimal.

## Chunk Size by Document Type

| Document Type | Recommended Size | Rationale |
|---|---|---|
| FAQ / Q&A pairs | 128-256 tokens | Each item is self-contained |
| News articles | 256-512 tokens | Short paragraphs, one topic each |
| Technical docs | 512-1024 tokens | Sections are ~1-2 paragraphs |
| Research papers | 512-1024 tokens | Abstracts + sections |
| Legal contracts | 1024-2048 tokens | Clauses are long, context-critical |
| Books / long-form | 2048+ tokens | Chapters are coherent units |
| Code files | Function-level | AST-based, not token-based |

## Chunk Overlap Rules

| Overlap | Effect | When to Use |
|---|---|---|
| 0% | No duplicates, minimal storage | Documents with clear section breaks |
| 10% | Catches most boundary issues | General text |
| 20% | Very safe, recommended default | Production RAG |
| 50% | Very safe but 50% more chunks | High-stakes Q&A (legal, medical) |

## Chunking for Embedding Model Limits

```
Embedding model context length — always check this first.

all-MiniLM-L6-v2:  256 tokens max  → chunk at 200 tokens
BGE-base:           512 tokens max  → chunk at 450 tokens
BGE-large:          512 tokens max  → chunk at 450 tokens
OpenAI ada-002:    8191 tokens max  → chunk at 2048 tokens (practical)
BGE-M3:            8192 tokens max  → chunk at 2048 tokens
```

Setting chunk_size > embedding model limit causes silent truncation and information loss.

## Practical Workflow for Tuning

1. **Start with:** RecursiveCharacterTextSplitter, chunk_size=512, overlap=0.2
2. **Measure:** Recall@k on your eval set
3. **Try:** chunk_size=256, 512, 1024 with overlap=0.2
4. **Try:** overlap=0, 0.1, 0.2, 0.5 at best chunk_size
5. **If recall is still low:** Try semantic chunking or document-aware chunking
6. **Finalize:** Pick the configuration with the best trade-off between recall and chunk count

## Semantic Chunking When to Use

Use semantic chunking when:
- Documents have variable topic density (some dense, some sparse)
- Fixed-size chunking frequently splits coherent sections
- Your eval shows recall < 0.85 and other optimizations failed

Don't use semantic chunking when:
- You need sub-10ms indexing (semantic chunking requires an embedding call per sentence)
- Documents already have clear section boundaries (use document-aware instead)

## Production Notes

- **Chunk IDs:** Use `doc_id + chunk_index` so you can trace each chunk back to its parent document
- **Metadata:** Store chunk index, total chunks, section heading with every chunk
- **Compression:** Store chunks as-is, not as embeddings. Embeddings are derived from chunks, not a replacement for them.
- **Updates:** When a source document changes, delete all its chunks and re-insert. Don't try to patch individual chunks.
- **Monitoring:** Track average chunk length, max chunk length, total chunks per document. A sudden change in average chunk length may indicate a parsing error.

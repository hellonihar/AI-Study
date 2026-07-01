# Ingestion Pipeline

Document processing pipeline that transforms raw files into searchable vector embeddings.

## Pipeline Stages

```
Raw Documents (PDF, HTML, Markdown, Code, DB rows)
    │
    ▼
┌──────────────┐
│  Parser       │──> Extract text + metadata
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Cleaner      │──> Normalize whitespace, strip boilerplate, fix encoding
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Chunker      │──> Split into passages (see chunking-strategies.md)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Embedder     │──> Generate vector embeddings per chunk
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Indexer      │──> Store in vector DB with metadata
└──────────────┘
```

## Supported Document Formats

| Format | Parser | Notes |
|---|---|---|
| PDF | PyMuPDF (fitz), pdfplumber, marker | Marker is best for complex layouts |
| HTML | BeautifulSoup, trafilatura | trafilatura for web articles |
| Markdown | markdown-it, Python markdown | Preserve headers for chunking |
| DOCX | python-docx | Table handling is brittle |
| CSV/Excel | pandas | Row-level chunking |
| Code | tree-sitter | AST-aware chunking (preserve functions) |
| Image (OCR) | Tesseract, Donut | Rarely used in production RAG |
| Audio/Video | Whisper | Transcribe first, then text pipeline |

## Metadata Extraction

Every chunk should carry metadata for filtering, provenance, and debugging:

```json
{
  "doc_id": "uuid-1234",
  "source": "s3://bucket/report-q3-2024.pdf",
  "page": 12,
  "section": "3.2 Revenue",
  "heading": "Quarterly Performance",
  "chunk_index": 4,
  "total_chunks": 28,
  "processed_at": "2024-12-01T10:00:00Z",
  "hash": "sha256:abcd..."
}
```

**Essential metadata fields:**
- `doc_id` — unique document identifier
- `source` — original file path or URL
- `chunk_index` — position within the document
- `section` or `heading` — structural context
- `processed_at` — ingestion timestamp

## Encoding and Normalization

| Issue | Fix |
|---|---|
| Mixed encodings (UTF-8, Latin-1, CP1252) | Detect with `chardet`, convert to UTF-8 |
| Unicode normalize forms (NFC, NFD) | Use NFC for storage, NFD for search |
| Zero-width characters | Strip `\u200b`, `\u200c`, `\u200d` |
| HTML entities | Decode `&amp;`, `&lt;`, etc. |
| Markdown links | Extract alt text; optionally keep URL as metadata |
| Repeated whitespace | Collapse multi-space, keep single newlines |

## Batch Processing Architecture

```yaml
ingestion_pipeline:
  batch_size: 1000          # chunks per batch
  max_concurrency: 8        # parallel embed calls
  retry_policy:
    max_retries: 3
    backoff: exponential    # 1s, 2s, 4s
  error_handling:
    failed_chunks: DLQ      # dead letter queue
    continue_on_error: true # don't abort the batch
  
  embedding:
    model: "BGE-base"
    batch_size: 64          # embed in batches for GPU efficiency
    normalize: true
    
  vector_db:
    index: "my-collection"
    namespace: "documents"
    batch_size: 100         # DB upsert batch
```

## De-Duplication

At scale, documents get re-ingested. Strategies to avoid duplicates:

1. **Content hash** — SHA-256 of chunk text; skip if hash exists
2. **Document hash** — hash entire doc; skip unchanged docs
3. **Semantic dedup** — embed and cluster; remove near-duplicate chunks (cosine > 0.98)
4. **Business key** — use document ID from source system

**Recommendation:** Content hash is cheapest and catches 95% of duplicates. Add semantic dedup for the remaining 5%.

## Incremental Ingestion

Rather than re-indexing everything on each change:

```
Strategy: Change Data Capture (CDC)

1. Detect changed documents (mtime, DB trigger, S3 event)
2. Re-process only changed docs
3. Delete old chunks for those docs
4. Insert new chunks
5. Rebuild index (or allow index to include old + new)
```

This requires point-delete capability in the vector DB. Qdrant, Milvus, and Pinecone support it. FAISS does not (must rebuild).

## Ingestion at Scale

| Scale | Ingestion Frequency | Strategy |
|---|---|---|
| < 10K docs | On-demand | Sequential, single-threaded |
| 10K-100K | Daily batch | Parallel, 8-16 workers |
| 100K-1M | Hourly batch | Distributed (Ray, Spark) |
| 1M+ | Continuous CDC | Streaming (Kafka + Flink) |

**Throughput expectations (single node):**
- Parsing: ~100 MB/min (text) or ~10 MB/min (PDF)
- Chunking: ~1M chunks/min
- Embedding (GPU): ~10K chunks/min per GPU (BGE-base)
- Indexing: ~5K chunks/min (Qdrant/Pinecone)

Pipeline bottleneck is typically embedding. Scale by adding GPU workers or reducing embedding dimension.

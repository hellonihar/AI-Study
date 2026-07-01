# Unstructured Data Ingestion

Extracting text and metadata from unstructured sources for RAG and AI workloads.

## The Unstructured Data Challenge

Unstructured data constitutes 80%+ of enterprise data. Unlike structured data, it has no fixed schema, no query engine, and every format requires a different parser.

| Source | Parse Difficulty | Text Quality | Metadata Availability |
|---|---|---|---|
| Markdown / HTML | Low | High | Medium |
| Plain text | Low | High | Low |
| PDF (text-based) | Medium | Medium | Low |
| PDF (scanned) | High | Low (OCR) | Low |
| DOCX / ODT | Medium | High | Medium |
| Email (EML/MSG) | Medium | Medium | High |
| Confluence / Wiki | Low | High | Medium |
| SharePoint | Medium | Medium | Medium |
| Slack / Teams | Low | High | High |
| Code repos | Low | High | High |
| Audio / Video | High | Transcribed | Low |
| Images (screenshots) | Very high | OCR only | Low |

## Parsing Pipeline

```
Raw File
    │
    ▼
┌──────────────┐
│  Format       │  Detect file type (magic bytes, extension)
│  Detection    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Parser       │  Extract text + metadata per format
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Cleaner      │  Normalize whitespace, fix encoding, strip boilerplate
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Enricher     │  Add metadata (headings, page numbers, timestamps)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Chunker      │  Split into retrieval-ready passages
└──────────────┘
```

## Parser Selection

### PDF Parsers

| Parser | Text PDF | Scanned PDF | Table Extraction | Speed |
|---|---|---|---|---|
| PyMuPDF (fitz) | Excellent | N/A | Good | Fast |
| pdfplumber | Good | N/A | Excellent | Medium |
| marker | Excellent | Excellent (OCR) | Good | Slow |
| PyPDF2 / pypdf | Good | N/A | Poor | Fast |
| Tesseract + OCR | N/A | Good | N/A | Very slow |
| Azure Document Intelligence | Excellent (API) | Excellent (API) | Excellent | API-dependent |

**Rule:** Use PyMuPDF for text-based PDFs (fast, good quality). Use marker for complex PDFs with tables and scanned pages.

### HTML/Web Parsers

| Parser | Main Content | Boilerplate Removal | Links | Speed |
|---|---|---|---|---|
| trafilatura | Excellent | Excellent | Configurable | Fast |
| BeautifulSoup | Manual | Manual | Manual | Fast |
| readability-lxml | Good | Good | No | Fast |
| Newspaper3k | Good | Good | Yes | Medium |

**Rule:** Use trafilatura for web articles (best boilerplate removal). Use BeautifulSoup for custom HTML parsing.

### Document Parsers

| Parser | DOCX | PPTX | XLSX | EML | Notes |
|---|---|---|---|---|---|
| python-docx | Excellent | No | No | No | Preserves structure |
| python-pptx | No | Excellent | No | No | Per-slide extraction |
| openpyxl | No | No | Excellent | No | Row-level chunks |
| extract_msg | No | No | No | Excellent | Email metadata |

### Transcription (Audio/Video)

| Tool | Languages | Quality | Speed | Cost |
|---|---|---|---|---|
| Whisper (local) | 100+ | Good | Real-time on GPU | Free |
| WhisperX | 100+ | Better (diarization) | Near real-time | Free |
| Deepgram | 30+ | Excellent | Real-time | $0.0043/min |
| Azure Speech | 100+ | Excellent | Real-time | $0.006/min |

**Rule:** Use WhisperX for local/self-hosted transcription. Use Deepgram for cloud with higher accuracy needs.

## Boilerplate Removal

Unstructured data contains significant amounts of non-content text:

| Source | Typical Boilerplate | Removal Strategy |
|---|---|---|
| Web pages | Nav, ads, footers, cookie notices | trafilatura, readability |
| PDFs | Headers, footers, page numbers | Position-based filtering |
| Emails | Signatures, legal disclaimers, reply chains | Regex patterns, ML classifier |
| Code | Comments, imports, boilerplate config | Tree-sitter AST, language filters |

**Boilerplate-to-content ratio:**
- Web pages: 40-60% boilerplate
- PDF reports: 10-20% boilerplate
- Emails: 30-50% boilerplate
- Internal wikis: 10-30% boilerplate

## Metadata Extraction

Every ingested document should carry:

```json
{
  "doc_id": "uuid-v7-1234",
  "source_type": "pdf",
  "source_path": "s3://data/pdfs/report-q3.pdf",
  "title": "Q3 2024 Financial Report",
  "author": "Finance Team",
  "created_at": "2024-10-15T10:00:00Z",
  "ingested_at": "2024-12-01T03:00:00Z",
  "file_size_bytes": 2450000,
  "page_count": 42,
  "language": "en",
  "hash": "sha256:abcd...",
  "chunk_count": 128
}
```

## Scheduling and Triggers

| Source | Refresh Strategy | Typical Frequency |
|---|---|---|
| File share / S3 | Event trigger (S3 notifications) | Near real-time |
| Confluence | API poll (last modified) | Hourly |
| SharePoint | Webhook + API poll | Hourly |
| Email (IMAP) | IDLE push | Real-time |
| Web crawl | Scheduled crawl | Daily |
| Slack / Teams | API subscription | Real-time |

## Enterprise Considerations

### Volume Management

| Scale | Documents/Day | Pipeline | Infrastructure |
|---|---|---|---|
| Small | < 10K | Sequential, single thread | Single server |
| Medium | 10K-100K | Parallel workers (8-16) | Multi-core server |
| Large | 100K-1M | Distributed (Ray, Spark) | Cluster |
| Very Large | 1M+ | Streaming (Kafka + Flink) | K8s cluster |

### Deduplication

```python
def is_duplicate(new_doc, existing_hashes):
    content_hash = hashlib.sha256(new_doc["text"].encode()).hexdigest()
    if content_hash in existing_hashes:
        return True
    # Semantic dedup: check if cosine similarity > 0.98 with any existing doc
    return False
```

### Error Handling

| Error | Frequency | Action |
|---|---|---|
| Corrupted file | 1-5% | Log, skip, send to DLQ |
| Parser failure | 1-3% | Retry with backup parser |
| Encoding issues | 2-5% | Detect encoding, convert to UTF-8 |
| Timeout (large file) | <1% | Timeout per file (configurable) |
| Rate limit (API) | Variable | Exponential backoff + retry |

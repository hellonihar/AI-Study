# Semantic Search — Design Document

## Overview

Replace keyword-based enterprise search with embedding-based semantic search. Index documents from SharePoint, Confluence, and custom stores; retrieve results using hybrid search (vector similarity + keyword relevance with RRF fusion); and provide relevance tuning knobs for different content domains. This project demonstrates how enterprise search experience — indexing strategies, relevance tuning, query understanding, connector architecture — transfers directly to building AI-powered semantic search.

---

## Architecture

```
                    ┌──────────────────────────────────────────┐
                    │            Enterprise Sources             │
                    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
                    │  │SharePoint│ │Confluence│ │  Custom  │ │
                    │  │   API    │ │   API    │ │  Store   │ │
                    │  └─────┬────┘ └────┬─────┘ └────┬─────┘ │
                    └────────┼───────────┼────────────┼───────┘
                             │           │            │
                             ▼           ▼            ▼
              ┌─────────────────────────────────────────────┐
              │              Indexing Pipeline               │
              │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
              │  │ Extract  │ │  Chunk   │ │   Embed      │ │
              │  │(connector)│ │ (split)  │ │  (model)    │ │
              │  └──────────┘ └──────────┘ └──────┬───────┘ │
              └────────────────────────────────────┼─────────┘
                                                   │
                                                   ▼
              ┌─────────────────────────────────────────────┐
              │             Search Index                     │
              │  ┌─────────────────┐  ┌───────────────────┐ │
              │  │   Vector Store   │  │  Keyword Index    │ │
              │  │  (Qdrant/Pinecone)│  │  (Tantivy/Meili) │ │
              │  │  dim: 768/1024  │  │  BM25 inverted    │ │
              │  └─────────────────┘  └───────────────────┘ │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌─────────────────────────────────────────────┐
              │             Query Pipeline                   │
              │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
              │  │  Query   │ │  Hybrid  │ │  Relevance   │ │
              │  │  Embed   │ │  Search  │ │  Tuning &    │ │
              │  │          │ │(RRF fuse)│ │  Reranking   │ │
              │  └──────────┘ └──────────┘ └──────────────┘ │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌─────────────────────────────────────────────┐
              │             Search API                       │
              │  FastAPI — /search, /suggest, /index        │
              └─────────────────────────────────────────────┘
```

### Indexing Flow

```
[SharePoint] ──► Connector ──► Document Parser ──► Chunker ──► Embedder ──► Index
     │                                                                       │
     ├── Full sync: nightly full re-index                                    │
     ├── Incremental: webhook or poll every 5 min                            │
     └── Deletions: tombstone tracking                                        │
                                                                              │
     [Vector Index]           [Keyword Index]                                 │
     ┌──────────────┐        ┌──────────────┐                                │
     │ doc_id: str  │        │ doc_id: str  │                                │
     │ vector: f32[]│        │ bm25_fields  │                                │
     │ metadata: {} │        │ metadata: {} │                                │
     │ text: str    │        │ text: str    │                                │
     └──────────────┘        └──────────────┘                                │
```

### Query Flow

```
User Query
    │
    ▼
┌──────────────────┐
│ Query Processing │
│ - Normalize      │
│ - Expand (syn.)  │
│ - Classify type  │
└──────┬───────────┘
       │
       ├──────────────────────────┐
       ▼                          ▼
┌─────────────────┐    ┌──────────────────────┐
│ Vector Search   │    │ Keyword Search (BM25) │
│ (embed query)   │    │ (tokenize + match)   │
│ top_k=100       │    │ top_k=100            │
└────────┬────────┘    └──────────┬───────────┘
         │                       │
         └──────────┬────────────┘
                    ▼
          ┌──────────────────┐
          │  RRF Fusion      │
          │  k=60            │
          │  top_k=20        │
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │  Reranker        │
          │  (cross-encoder) │
          │  top_k=10        │
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │  Result Builder  │
          │  + snippets      │
          │  + highlights    │
          └──────────────────┘
```

---

## Project Structure

```
projects/semantic-search/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Settings via pydantic-settings
│   ├── schemas.py                   # Pydantic models for documents, queries, results
│   │
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract connector interface
│   │   ├── sharepoint.py            # Microsoft Graph API connector
│   │   ├── confluence.py            # Confluence REST API connector
│   │   └── custom.py                # Generic REST or file-based connector
│   │
│   ├── indexing/
│   │   ├── __init__.py
│   │   ├── pipeline.py              # Orchestrator: extract → chunk → embed → index
│   │   ├── chunker.py               # Recursive + heading-aware chunking
│   │   ├── embedder.py              # Embedding model abstraction
│   │   └── scheduler.py             # Full sync + incremental sync scheduling
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   ├── vector_store.py          # Vector DB abstraction (Qdrant)
│   │   ├── keyword_index.py         # BM25 keyword index (Tantivy)
│   │   ├── hybrid.py                # Hybrid search with RRF fusion
│   │   ├── reranker.py              # Cross-encoder reranking
│   │   ├── query_processor.py       # Query normalization, expansion, classification
│   │   └── suggester.py             # Query autocomplete suggestions
│   │
│   ├── relevance/
│   │   ├── __init__.py
│   │   ├── tuner.py                 # Relevance tuning interface
│   │   ├── metrics.py               # NDCG, MAP, MRR computation
│   │   └── feedback.py              # Click feedback collection + learning
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py                # FastAPI routes (search, suggest, index, metrics)
│       └── dependencies.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_connectors.py
│   ├── test_indexing.py
│   ├── test_search.py
│   └── test_relevance.py
│
├── data/
│   ├── sample_docs/                 # Sample enterprise documents
│   └── relevance_judgments.jsonl    # Human relevance judgments for tuning
│
├── notebooks/
│   └── explore_embeddings.ipynb
├── docker-compose.yml               # FastAPI + Qdrant + Redis + Tantivy (if needed)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Connectors

### Connector Interface

```python
class BaseConnector(ABC):
    source_name: str

    @abstractmethod
    async def list_documents(self, since: datetime | None = None) -> AsyncIterator[DocumentRef]:
        """List documents, optionally filtering by modification time."""

    @abstractmethod
    async def fetch_content(self, ref: DocumentRef) -> RawDocument:
        """Fetch full document content."""

    @abstractmethod
    async def list_deletions(self, since: datetime) -> AsyncIterator[str]:
        """List document IDs deleted since given timestamp."""
```

### SharePoint Connector

| Parameter | Value |
|---|---|
| Auth | Microsoft Graph API (app-only token) |
| Endpoints | `GET /sites/{site}/drive/root/children` |
| File types | `.docx`, `.pdf`, `.xlsx`, `.pptx`, `.txt` |
| Metadata | title, author, created, modified, path, URL |
| Sync | Poll every 5 min for changes via `/delta` endpoint |
| Rate limit | 10K requests/hour (handled with retry + backoff) |

### Confluence Connector

| Parameter | Value |
|---|---|
| Auth | Personal Access Token or OAuth 2.0 |
| Endpoints | `GET /rest/api/content` (CQL filter for spaces) |
| Content | Page body (storage format → plain text via html2text) |
| Metadata | title, author, space, version, URL, labels |
| Sync | Poll every 5 min via `/rest/api/content?since=` |
| Rate limit | Configurable per-instance (default: 100 req/min) |

---

## Indexing Pipeline

### Chunking Strategy

```python
class HeadingAwareChunker:
    """
    Split documents based on heading hierarchy.
    Preserves document structure: each chunk retains parent headings as context.
    """
    def chunk(self, document: str, metadata: dict) -> list[Chunk]:
        # 1. Parse document into sections by heading level (h1, h2, h3)
        # 2. Each section becomes a chunk
        # 3. Prepend parent headings to each chunk for context
        # 4. If a section exceeds max_chunk_size, apply recursive split within it
        # 5. Overlap: 1 sentence between adjacent chunks
```

| Strategy | Use | Chunk Size | Overlap |
|---|---|---|---|
| Heading-aware | Well-structured docs (Confluence, SharePoint pages) | 512 tokens | 1 sentence |
| Recursive | Generic documents | 384 tokens | 48 tokens |
| Sentence-based | Legal, policy documents | 256 tokens | 2 sentences |

### Embedding Model

| Model | Dimensions | Quality | Latency | Cost |
|---|---|---|---|---|
| `text-embedding-3-small` | 512 | Good | ~20ms | $0.02/1M tokens |
| `text-embedding-3-large` | 1024 | Best | ~40ms | $0.13/1M tokens |
| `BGE-large-en-v1.5` | 1024 | Great | ~30ms (GPU) | Free (self-hosted) |
| `E5-mistral-7b` | 4096 | Best for domain-specific | ~100ms (GPU) | Free (self-hosted) |

Default: `text-embedding-3-small` (dimensions: 512) for speed/cost balance. Dimension reduction supported natively by OpenAI.

---

## Search

### Hybrid Search (RRF Fusion)

```python
async def hybrid_search(
    query: str,
    top_k: int = 20,
    alpha: float = 0.5,       # Weight for vector score (0 = pure keyword, 1 = pure vector)
    rrf_k: int = 60,           # RRF constant
) -> list[SearchResult]:
    # Vector search
    query_vector = await embedder.embed(query)
    vector_results = await vector_store.search(query_vector, top_k * 2)

    # Keyword search (BM25)
    keyword_results = await keyword_index.search(query, top_k * 2)

    # Reciprocal Rank Fusion
    scores: dict[str, float] = {}
    for rank, r in enumerate(vector_results):
        scores[r.doc_id] = scores.get(r.doc_id, 0) + alpha * (1.0 / (rrf_k + rank))
    for rank, r in enumerate(keyword_results):
        scores[r.doc_id] = scores.get(r.doc_id, 0) + (1 - alpha) * (1.0 / (rrf_k + rank))

    # Sort by combined score and retrieve full results
    ranked_doc_ids = sorted(scores, key=scores.get, reverse=True)[:top_k]
    return [await self.lookup(doc_id, score=scores[doc_id]) for doc_id in ranked_doc_ids]
```

### Reranking

A cross-encoder model re-scores the top 20 results from hybrid search:

```python
class CrossEncoderReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model = CrossEncoder(model_name)

    async def rerank(
        self, query: str, results: list[SearchResult], top_k: int = 10
    ) -> list[SearchResult]:
        pairs = [(query, r.text) for r in results]
        scores = self.model.predict(pairs)
        for r, s in zip(results, scores):
            r.rerank_score = float(s)
        results.sort(key=lambda r: r.rerank_score, reverse=True)
        return results[:top_k]
```

### Query Processing

```python
class QueryProcessor:
    async def process(self, raw_query: str) -> ProcessedQuery:
        return ProcessedQuery(
            original=raw_query,
            normalized=self.normalize(raw_query),
            expanded=await self.expand_synonyms(raw_query),
            query_type=self.classify(raw_query),  # "question" | "keyword" | "phrase"
            filters=self.extract_filters(raw_query),  # date:, author:, site:
        )
```

| Step | Technique | Purpose |
|---|---|---|
| Normalization | Lowercase, unicode NFKC, whitespace collapse | Consistent matching |
| Synonym expansion | Synonym dictionary per domain (enterprise-specific) | Broaden recall |
| Query classification | Lightweight classifier (keyword vs. question vs. phrase) | Adjust retrieval strategy |
| Filter extraction | Regex patterns for `author:`, `date:`, `site:` prefixes | Scoped search |

### Suggestions

```python
class Suggester:
    """Autocomplete suggestions based on indexed terms and popular queries."""
    async def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        # 1. Prefix match against indexed terms (trie)
        # 2. Rank by frequency in query logs
        # 3. Return top N
```

---

## Relevance Tuning

### Tuning Parameters

| Parameter | Effect | Default | Range |
|---|---|---|---|
| `alpha` | Balance vector vs. keyword search | 0.5 | 0.0–1.0 |
| `rrf_k` | RRF fusion constant (higher = more weight to lower ranks) | 60 | 10–200 |
| `rerank_enabled` | Enable cross-encoder reranking | true | true/false |
| `rerank_top_k` | Candidates passed to reranker | 20 | 10–50 |
| `field_weights` | Per-field boost (title: 3, headings: 2, body: 1) | title:3, body:1 | configurable |

### Domain-Specific Profiles

```yaml
# data/profiles/technical.yaml
relevance_profile:
  name: technical
  domain: engineering
  alpha: 0.7            # Prefer semantic similarity (code docs, architecture)
  field_weights:
    title: 3.0
    headings: 2.5
    code_blocks: 2.0
    body: 1.0
  boost_phrases:
    - "architecture"
    - "API reference"
    - "design decision"

# data/profiles/policies.yaml
relevance_profile:
  name: policies
  domain: hr-legal
  alpha: 0.3            # Prefer keyword match (exact policy terms matter)
  field_weights:
    title: 4.0
    body: 2.0
  rerank_enabled: false # Legal docs: don't risk reranker reordering
```

### Evaluation Metrics

| Metric | Definition | Collection Method |
|---|---|---|
| **NDCG@10** | Normalized Discounted Cumulative Gain | Human judgments (5-level relevance) |
| **MAP** | Mean Average Precision | Human judgments (binary relevance) |
| **MRR** | Mean Reciprocal Rank | Click data (first click position) |
| **P@5** | Precision at 5 | Human judgments |
| **Click-through Rate** | % of searches with ≥1 click | Query log analysis |

### Relevance Judgment Collection

```python
# data/relevance_judgments.jsonl
{"query": "cloud migration strategy", "doc_id": "doc_042", "relevance": 3}  # Highly relevant
{"query": "cloud migration strategy", "doc_id": "doc_017", "relevance": 2}  # Relevant
{"query": "cloud migration strategy", "doc_id": "doc_093", "relevance": 1}  # Marginally relevant
{"query": "cloud migration strategy", "doc_id": "doc_201", "relevance": 0}  # Not relevant
```

| Source | Quantity | Quality |
|---|---|---|
| Human annotators | 200–500 queries × 10 documents | Gold standard |
| Click logs (implicit) | 10K+ queries | Noisy, high volume |
| LLM-as-judge | 500–2000 queries × 10 documents | Reasonable proxy |

---

## API

### `POST /api/v1/search`

Full hybrid search with optional reranking.

**Request:**
```json
{
  "query": "cloud migration strategy",
  "top_k": 10,
  "rerank": true,
  "profile": "technical",
  "filters": {
    "author": null,
    "source": ["sharepoint"],
    "date_from": "2025-01-01",
    "tags": ["infrastructure"]
  },
  "page": 1,
  "per_page": 10
}
```

**Response:**
```json
{
  "total": 47,
  "page": 1,
  "per_page": 10,
  "query": "cloud migration strategy",
  "profile": "technical",
  "latency_ms": {
    "search": 85,
    "rerank": 150,
    "total": 261
  },
  "results": [
    {
      "rank": 1,
      "doc_id": "doc_042",
      "title": "Cloud Migration Playbook",
      "source": "sharepoint",
      "url": "https://sharepoint.example.com/...",
      "author": "Jane Doe",
      "modified": "2026-03-15",
      "snippet": "...a comprehensive <mark>cloud migration</mark> <mark>strategy</mark> covering AWS, Azure, and GCP...",
      "score": 0.94,
      "rerank_score": 0.97,
      "highlights": [
        {"field": "body", "text": "cloud migration strategy", "start": 42, "end": 67}
      ]
    }
  ]
}
```

### `GET /api/v1/suggest`

Autocomplete suggestions as user types.

**Query params:** `?q=cloud&limit=5`

**Response:**
```json
{
  "suggestions": [
    {"text": "cloud migration strategy", "count": 89},
    {"text": "cloud security best practices", "count": 54},
    {"text": "cloud architecture patterns", "count": 42}
  ]
}
```

### `POST /api/v1/index`

Trigger an indexing job for a specific source.

**Request:**
```json
{
  "source": "sharepoint",
  "sync_type": "incremental"
}
```

**Response:**
```json
{
  "job_id": "job_idx_456",
  "source": "sharepoint",
  "sync_type": "incremental",
  "status": "running",
  "documents_found": 12,
  "documents_indexed": 0
}
```

### `GET /api/v1/metrics/relevance`

Retrieve relevance metrics for a profile.

**Query params:** `?profile=technical`

**Response:**
```json
{
  "profile": "technical",
  "judgments": 320,
  "metrics": {
    "ndcg@10": 0.87,
    "map": 0.82,
    "mrr": 0.91,
    "p@5": 0.78,
    "click_through_rate": 0.64
  },
  "recent_queries": [
    {"query": "cloud migration", "ndcg": 0.92},
    {"query": "API gateway", "ndcg": 0.85}
  ]
}
```

---

## Monitoring

| Metric | Type | Labels | Description |
|---|---|---|---|
| `search_requests_total` | Counter | profile, status | Total search requests |
| `search_latency_ms` | Histogram | phase (search, rerank, total) | Search latency breakdown |
| `search_no_results` | Counter | profile | Zero-result queries (proxy for poor recall) |
| `search_click_through` | Counter | profile, rank | Click-through events |
| `index_documents_total` | Counter | source | Documents indexed |
| `index_latency_ms` | Histogram | source, phase | Indexing pipeline latency |
| `index_errors_total` | Counter | source | Indexing failure count |
| `relevance_ndcg` | Gauge | profile | NDCG score per profile |

Alert when:
- `search_no_results` rate exceeds 5% of total queries
- `search_latency_ms` p95 exceeds 1s
- `relevance_ndcg` drops below 0.75 for any profile
- `index_errors_total` spikes (connector failure)

---

## Tech Stack

| Component | Choice | Justification |
|---|---|---|
| Framework | FastAPI + uvicorn | Consistent with other projects |
| Vector DB | Qdrant | Open-source, hybrid search, filtering, high performance |
| Keyword index | Qdrant built-in `full_text_filter` or Tantivy | BM25 within Qdrant avoids extra infra |
| Embedding | `text-embedding-3-small` (OpenAI) | Best quality/cost, dimension reduction supported |
| Reranker | `BAAI/bge-reranker-v2-m3` | SOTA cross-encoder, ONNX runtime capable |
| Connectors | `msgraph-sdk-python`, `atlassian-python-api` | Official SDKs |
| Document parsing | `python-docx`, `PyMuPDF`, `openpyxl`, `html2text` | Covers enterprise formats |
| Caching | Redis | Cache embedding results, popular query results |
| Query logs | PostgreSQL | Store + analyze query patterns |
| Monitoring | Prometheus + Grafana | Consistent with other projects |

---

## Implementation Phases

| Phase | Files | Deliverable |
|---|---|---|
| **1** | `config.py`, `schemas.py`, `search/vector_store.py` | Base abstractions + vector store setup |
| **2** | `connectors/base.py`, `connectors/sharepoint.py`, `connectors/confluence.py` | Enterprise connectors |
| **3** | `indexing/chunker.py`, `indexing/embedder.py`, `indexing/pipeline.py` | Indexing pipeline |
| **4** | `search/query_processor.py`, `search/keyword_index.py`, `search/hybrid.py` | Query processing + hybrid search |
| **5** | `search/reranker.py`, `search/suggester.py` | Reranking + suggestions |
| **6** | `relevance/tuner.py`, `relevance/metrics.py`, `relevance/feedback.py` | Relevance tuning + evaluation |
| **7** | `indexing/scheduler.py` | Incremental sync + scheduling |
| **8** | `api/*` | FastAPI routes |
| **9** | Tests + `data/sample_docs/` + `data/relevance_judgments.jsonl` | Verification, sample data |
| **10** | Notebooks + README | Exploration, documentation |

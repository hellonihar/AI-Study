# RAG System — Design Document

## Overview

Extend an ETL pipeline with embeddings and a vector database to enable document Q&A via retrieval-augmented generation. This project demonstrates how data pipeline experience — ETL architecture, incremental processing, data quality, and batch vs. streaming patterns — transfers directly to building RAG systems.

---

## Architecture

```
                         ┌──────────────────────────────┐
                         │        Document Sources        │
                         │  (PDF, HTML, Confluence, S3)   │
                         └──────┬──────┬──────┬──────────┘
                                │      │      │
                                ▼      ▼      ▼
                  ┌─────────────────────────────────────┐
                  │         Ingestion Pipeline           │
                  │  ┌─────────┐ ┌────────┐ ┌────────┐ │
                  │  │ Extract │ │ Chunk  │ │ Embed  │ │
                  │  │(parsers)│ │(split) │ │(model) │ │
                  │  └─────────┘ └────────┘ └────────┘ │
                  └────────────────┬────────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────────┐
                  │         Vector Database              │
                  │   (Qdrant — collection: documents)   │
                  │   index: cosine, payload: metadata   │
                  └────────────────┬────────────────────┘
                                   ▲
                                   │
┌──────────┐    ┌──────────────────┴────────────────────┐
│  User    │    │           Query Pipeline               │
│  Query   │───►│  ┌────────┐ ┌─────────┐ ┌──────────┐ │
└──────────┘    │  │ Embed  │ │  Search │ │ Retrieve │ │
                │  │(same   │ │(hybrid) │ │(rerank)  │ │
                │  │ model) │ │         │ │  (opt)   │ │
                │  └────────┘ └─────────┘ └──────────┘ │
                └────────────────┬──────────────────────┘
                                 │
                                 ▼
                ┌──────────────────────────────────────┐
                │          Generation (LLM)             │
                │  context + query → grounded response  │
                └────────────────┬─────────────────────┘
                                 │
                                 ▼
                ┌──────────────────────────────────────┐
                │          Response + Citations          │
                └───────────────────────────────────────┘
```

### Flow

**Ingestion (batch):**
1. Extract: parse documents from sources (PDF, HTML, Confluence API, S3)
2. Chunk: split into overlapping segments (size: 512 tokens, overlap: 64 tokens)
3. Embed: convert each chunk to a vector using an embedding model
4. Index: store vectors + metadata + original text in Qdrant

**Query (real-time):**
1. Embed the user query using the same embedding model
2. Search Qdrant for top-K most similar chunks (hybrid: vector + keyword)
3. Optionally rerank results with a cross-encoder
4. Inject retrieved chunks as context into the LLM prompt
5. Generate a grounded answer with source citations

---

## Project Structure

```
projects/rag-system/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Settings via pydantic-settings
│   ├── schemas.py                   # Pydantic models for documents, chunks, queries
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pipeline.py              # Orchestrator: extract → chunk → embed → index
│   │   ├── extractors/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # Abstract document extractor
│   │   │   ├── pdf.py               # PyMuPDF parser
│   │   │   ├── html.py              # BeautifulSoup parser
│   │   │   └── confluence.py        # Confluence API extractor
│   │   ├── chunkers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # Abstract chunker
│   │   │   ├── recursive.py         # RecursiveCharacterTextSplitter
│   │   │   └── semantic.py          # Semantic chunker (LLM-based boundaries)
│   │   └── embedders/
│   │       ├── __init__.py
│   │       ├── base.py              # Abstract embedder
│   │       └── model.py             # SentenceTransformer / OpenAI embedding
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── search.py                # Vector search + hybrid search
│   │   ├── reranker.py              # Cross-encoder reranking
│   │   └── context.py               # Context assembly and prompt building
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── llm.py                   # LLM call (OpenAI / local)
│   │   └── prompts.py               # RAG prompt templates
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # FastAPI routes (query, ingest, search)
│   │   └── dependencies.py          # Shared dependencies
│   │
│   └── monitoring/
│       ├── __init__.py
│       └── metrics.py               # Prometheus metrics for retrieval quality
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   └── test_generation.py
│
├── data/
│   └── sample_docs/                 # Sample documents for testing
│
├── docker-compose.yml               # FastAPI + Qdrant + Redis
├── Dockerfile
├── notebooks/
│   └── explore.ipynb                # Exploration notebook for chunking/embedding experiments
├── requirements.txt
└── README.md
```

---

## API Endpoints

### `POST /api/v1/ingest`

Ingest one or more documents into the vector store.

**Request:**
```json
{
  "documents": [
    {
      "id": "doc_001",
      "source": "confluence",
      "title": "Architecture Overview",
      "content": "...",
      "metadata": {
        "url": "https://confluence.example.com/...",
        "author": "john",
        "last_modified": "2026-06-01"
      }
    }
  ],
  "chunk_strategy": "recursive",
  "chunk_size": 512,
  "chunk_overlap": 64
}
```

**Response:**
```json
{
  "job_id": "job_abc123",
  "documents_processed": 1,
  "chunks_indexed": 47,
  "status": "completed",
  "duration_ms": 2340
}
```

### `POST /api/v1/query`

Ask a question over the indexed documents.

**Request:**
```json
{
  "query": "What is the system architecture?",
  "top_k": 5,
  "rerank": true,
  "stream": false
}
```

**Response:**
```json
{
  "answer": "The system uses a microservices architecture with...",
  "citations": [
    {
      "chunk_id": "chunk_042",
      "document_id": "doc_001",
      "document_title": "Architecture Overview",
      "source": "confluence",
      "score": 0.92,
      "text": "The platform adopts a microservices architecture..."
    }
  ],
  "latency_ms": {
    "search": 45,
    "rerank": 120,
    "generation": 890,
    "total": 1055
  }
}
```

### `GET /api/v1/search`

Raw search without generation — useful for debugging retrieval quality.

**Request:** `?query=architecture&top_k=5`

**Response:**
```json
{
  "results": [
    {
      "chunk_id": "chunk_042",
      "score": 0.92,
      "text": "...",
      "metadata": {"document_title": "Architecture Overview"}
    }
  ]
}
```

### `GET /api/v1/documents`

List indexed documents with metadata and chunk counts.

### `DELETE /api/v1/documents/{doc_id}`

Delete a document and all its chunks from the index.

---

## Ingestion Pipeline

### Document Extractors

| Extractor | Library | Formats | Notes |
|---|---|---|---|
| PDF | PyMuPDF (fitz) | `.pdf` | Handles text, tables, basic layout |
| HTML | BeautifulSoup | `.html`, `.htm` | Strips tags, extracts text + headings |
| Confluence | `atlassian-python-api` | Confluence pages | API-based extraction by space/key |
| S3 | `boto3` | Any text-based format | Download → parse by extension |
| Markdown | Standard parsing | `.md` | Preserves heading hierarchy for chunking |

### Chunking Strategies

| Strategy | How It Works | Best For | Pros | Cons |
|---|---|---|---|---|
| **Recursive** | Split by `\n\n` → `\n` → `.` → ` ` to target size | General purpose | Simple, fast, works for most docs | May split mid-sentence |
| **Semantic** | LLM identifies natural boundaries (sections, topics) | Well-structured docs | Coherent chunks | Slow, expensive, needs LLM call |
| **Token-aware** | Split at token boundaries (tiktoken) | Exact token budget | Predictable embedding cost | Loses sentence boundaries |

### Embedding Strategy

| Component | Default | Alternatives |
|---|---|---|
| Model | `text-embedding-3-small` (OpenAI) | `BGE-base-en-v1.5`, `E5-mistral-7b` |
| Dimensions | 512 (OpenAI supports truncation) | 768 (BGE), 1024 (E5) |
| Batch size | 64 | Depends on GPU/API rate limits |
| Normalization | L2-normalize | Cosine similarity requires normalized vectors |

### Incremental Indexing

```
Document Source ──► Change Detection (poll/webhook)
                         │
                    ┌────▼────┐
                    │ Changed?│
                    └────┬────┘
                         │ Yes
                    ┌────▼────┐
                    │ Upsert  │──► Embed ──► Index (replace by doc_id)
                    └─────────┘
```

- New documents: extract → chunk → embed → insert
- Updated documents: delete old chunks → re-extract → re-embed → re-insert
- Deleted documents: delete all chunks with matching `doc_id`

---

## Retrieval Pipeline

### Hybrid Search

Combines vector similarity with keyword (BM25) search for better retrieval:

```python
async def hybrid_search(query: str, top_k: int = 5) -> list[SearchResult]:
    vector_results = await vector_search(query, top_k * 2)
    keyword_results = await keyword_search(query, top_k * 2)

    # Reciprocal Rank Fusion
    scores = defaultdict(float)
    for rank, r in enumerate(vector_results):
        scores[r.chunk_id] += 1 / (60 + rank)
    for rank, r in enumerate(keyword_results):
        scores[r.chunk_id] += 1 / (60 + rank)

    ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
    return [lookup_chunk(chunk_id) for chunk_id, _ in ranked]
```

### Reranking

A cross-encoder model re-scores the top-K results from the initial search:

| Step | Model | Candidates | Latency |
|---|---|---|---|
| Initial search | Bi-encoder (embedding) | 100 → 20 | ~50ms |
| Reranker | Cross-encoder (`BGE-reranker-v2-m3`) | 20 → 5 | ~200ms |
| Final | LLM generation | 5 → 1 answer | ~1s |

### Context Assembly

```python
def build_context(results: list[SearchResult], max_tokens: int = 3000) -> str:
    """Assemble retrieved chunks into a context string, respecting token budget."""
    context_parts = []
    total_tokens = 0

    for r in results:
        tokens = count_tokens(r.text)
        if total_tokens + tokens > max_tokens:
            break
        context_parts.append(f"[Source: {r.document_title}]\n{r.text}")
        total_tokens += tokens

    return "\n\n".join(context_parts)
```

---

## Generation Pipeline

### RAG Prompt Template

```
You are a helpful assistant answering questions based on the provided context.
Answer concisely and cite the source for each claim.

Context:
{context}

Question: {query}

Answer (cite sources as [Source: Document Title]):
```

### LLM Options

| Provider | Model | Trade-off |
|---|---|---|
| OpenAI | GPT-4o-mini | Fast, cheap, good quality — default |
| OpenAI | GPT-4o | Best quality, higher cost |
| Anthropic | Claude 3 Haiku | Fast, good for long context |
| Local | Mistral-7B via Ollama | Free, private, lower quality |

### Citation Format

The LLM is prompted to cite sources inline: `The system uses microservices [Source: Architecture Overview].` The generation service validates that citations reference actual retrieved chunks — if the model cites a source not in the context, that response is flagged.

---

## Monitoring & Evaluation

### Retrieval Metrics

| Metric | Definition | Measured By | Alert Threshold |
|---|---|---|---|
| **Precision@K** | % of retrieved chunks that are relevant | Human eval / LLM-as-judge on eval set | < 0.7 |
| **Recall@K** | % of all relevant chunks that were retrieved | Eval set with known relevant chunks | < 0.8 |
| **MRR** | Mean reciprocal rank of first relevant result | Eval set | < 0.85 |
| **Latency p50/p95** | Search + rerank latency | Prometheus | p95 > 500ms |

### Generation Metrics

| Metric | Definition | Measured By | Alert Threshold |
|---|---|---|---|
| **Faithfulness** | % of claims supported by context | LLM-as-judge (RAGAS) | < 0.85 |
| **Answer relevancy** | Does the answer address the query? | LLM-as-judge (RAGAS) | < 0.8 |
| **Hallucination rate** | % of responses with unsupported claims | Output guardrails + manual review | > 5% |

### Eval Set

A fixed set of 50–100 (query, expected_context, expected_answer) triples stored in `data/eval_set.jsonl`. Run after every ingestion update and prompt change.

---

## Tech Stack

| Component | Choice | Justification |
|---|---|---|
| Framework | FastAPI + uvicorn | Async-native, same stack as other projects |
| Vector DB | Qdrant (Docker) | Open-source, hybrid search, filtering, REST + gRPC |
| Embedding | `text-embedding-3-small` via OpenAI | Best quality/cost ratio, 512-dim supported |
| Reranker | `BGE-reranker-v2-m3` via SentenceTransformers | Cross-encoder reranking, ONNX runtime |
| LLM | OpenAI GPT-4o-mini (primary), Ollama (fallback) | Cost-effective, good quality |
| Document parsing | PyMuPDF, BeautifulSoup, markdown | Covers 90% of document types |
| Async queue | Redis + RQ / Celery | Background ingestion jobs |
| Monitoring | Prometheus + Grafana | Consistent with other projects |
| Containerization | Docker + docker-compose | App + Qdrant + Redis |

---

## Configuration

```python
class Settings(BaseSettings):
    # Embedding
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 512
    embedding_batch_size: int = 64

    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"
    qdrant_vector_size: int = 512
    qdrant_distance: str = "Cosine"

    # Retrieval
    top_k: int = 5
    rerank_top_k: int = 20
    hybrid_search_alpha: float = 0.7   # weight for vector vs. keyword
    context_max_tokens: int = 3000

    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 1024

    # Ingestion
    default_chunk_size: int = 512
    default_chunk_overlap: int = 64

    # Monitoring
    eval_set_path: str = "data/eval_set.jsonl"
    faithfulness_threshold: float = 0.85
```

---

## Files to Build (Implementation Order)

| Phase | Files | What Each Does |
|---|---|---|
| **1** | `config.py`, `schemas.py` | Settings model, Pydantic types for documents, chunks, queries |
| **2** | `ingestion/extractors/*` | Document parsers for PDF, HTML, Confluence, Markdown |
| **3** | `ingestion/chunkers/*` | Recursive and semantic chunking strategies |
| **4** | `ingestion/embedders/*` | Embedding model abstraction + OpenAI/BGE implementations |
| **5** | `ingestion/pipeline.py` | Orchestrator that wires extract → chunk → embed → index |
| **6** | `retrieval/search.py` | Vector search + hybrid search (RRF fusion) |
| **7** | `retrieval/reranker.py` | Cross-encoder reranking |
| **8** | `retrieval/context.py` | Context assembly with token budget management |
| **9** | `generation/llm.py`, `generation/prompts.py` | LLM call + RAG prompt templates with citation format |
| **10** | `api/routes.py`, `api/dependencies.py` | FastAPI endpoints: ingest, query, search, documents CRUD |
| **11** | `monitoring/metrics.py` | Prometheus metrics for retrieval + generation quality |
| **12** | Tests + notebooks + README | Verification, exploration, documentation |

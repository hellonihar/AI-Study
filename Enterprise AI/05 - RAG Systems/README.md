# RAG Systems

Retrieval-Augmented Generation pipelines for grounding LLM outputs in external, verifiable knowledge sources.

## Module Structure

```
05 - RAG Systems/
├── 01-theory/          # 10 files: architecture, chunking, retrieval, evaluation
├── 02-code/            # 10 scripts: naive RAG through caching and fallback
├── 03-best-practices/  # 5 files: chunking, retrieval, prompts, deployment, eval
├── 04-resources/       # Papers, frameworks, tools, datasets, tutorials
└── README.md           # This file
```

## Theory (01-theory/)

| # | File | Topic |
|---|---|---|
| 1 | `01-what-is-rag.md` | RAG fundamentals, problem statement, maturity levels |
| 2 | `02-ingestion-pipeline.md` | Parsing, cleaning, metadata, de-duplication, batch processing |
| 3 | `03-chunking-strategies.md` | Fixed, recursive, semantic, document-aware, hierarchical |
| 4 | `04-retrieval-strategies.md` | Dense, sparse, hybrid, query rewriting, HyDE, multi-hop |
| 5 | `05-re-ranking.md` | Cross-encoder re-ranking, candidate count trade-offs |
| 6 | `06-context-windowing.md` | Context budget, lost-in-the-middle, compression, ordering |
| 7 | `07-generation-and-citation.md` | Faithful generation, citation formats, verification |
| 8 | `08-advanced-rag-patterns.md` | Corrective RAG, Self-RAG, Agentic RAG, Graph RAG, Fusion |
| 9 | `09-evaluation-harness.md` | RAGAS, faithfulness, precision/recall, A/B testing |
| 10 | `10-production-rag.md` | Caching, fallback chains, guardrails, observability |

## Code Examples (02-code/)

| # | File | Description | Requirements |
|---|---|---|---|
| 1 | `01-naive-rag.py` | Basic index → retrieve → generate pipeline | `faiss-cpu`, `sentence-transformers` |
| 2 | `02-chunking-demo.py` | Compare fixed, recursive, semantic, doc-aware chunking | `sentence-transformers` |
| 3 | `03-hybrid-retrieval.py` | Dense + sparse + RRF fusion retrieval | `rank-bm25`, `sentence-transformers` |
| 4 | `04-query-rewriting.py` | Query expansion, decomposition, HyDE | `sentence-transformers` |
| 5 | `05-re-ranking-pipeline.py` | Bi-encoder retrieve → cross-encoder re-rank | `sentence-transformers`, `torch` |
| 6 | `06-rag-with-citations.py` | Generate responses with source citations + verification | `faiss-cpu`, `sentence-transformers` |
| 7 | `07-multi-hop-rag.py` | Iterative retrieval with entity extraction | `faiss-cpu`, `sentence-transformers` |
| 8 | `08-rag-evaluation.py` | Faithfulness, relevance, context precision/recall | `sentence-transformers` |
| 9 | `09-advanced-rag.py` | Corrective RAG, Self-RAG, Fusion RAG demos | `sentence-transformers` |
| 10 | `10-caching-and-fallback.py` | Cache-aside pattern, embedding cache, fallback chain | `sentence-transformers` |

## Best Practices (03-best-practices/)

| # | File | Topic |
|---|---|---|
| 1 | `01-chunking-guide.md` | Chunk size/overlap by doc type, embedding model limits |
| 2 | `02-retrieval-optimization.md` | top_k tuning, hybrid weighting, pre-filtering |
| 3 | `03-prompt-design-for-rag.md` | System prompt template, citation format, few-shot |
| 4 | `04-production-deployment.md` | Architecture, scaling, rate limiting, rollback |
| 5 | `05-evaluation-and-monitoring.md` | Offline/online eval, LLM-as-judge, alerting |

## Key Topics

- **Chunking:** Fixed-size, recursive, semantic, document-aware, hierarchical
- **Retrieval:** Dense (vector), sparse (BM25), hybrid (RRF), query rewriting, HyDE
- **Re-ranking:** Cross-encoder, candidate selection, cascade strategy
- **Generation:** Citation formats, faithfulness, constrained decoding
- **Advanced patterns:** Corrective RAG, Self-RAG, Fusion RAG, Agentic RAG, Graph RAG
- **Evaluation:** RAGAS, LLM-as-judge, recall/precision, A/B testing
- **Production:** Caching, fallback chains, guardrails, observability, cost optimization

## Quick Start

```bash
# Naive RAG pipeline
pip install sentence-transformers faiss-cpu numpy
python "02-code/01-naive-rag.py"

# Hybrid retrieval
pip install rank-bm25
python "02-code/03-hybrid-retrieval.py"

# Re-ranking pipeline
pip install torch
python "02-code/05-re-ranking-pipeline.py"
```

## Prerequisites

- **Python 3.10+**
- Core: `sentence-transformers`, `numpy`, `faiss-cpu`
- Retrieval: `rank-bm25`
- Re-ranking: `torch`, `sentence-transformers` (includes CrossEncoder)
- Production: `fastapi`, `redis`, `prometheus-client`

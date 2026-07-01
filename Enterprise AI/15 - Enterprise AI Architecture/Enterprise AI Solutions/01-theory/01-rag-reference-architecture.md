# RAG Reference Architecture

## Components

```
User Request
    |
    v
[Guardrails] -> Block malicious/inappropriate input
    |
    v
[Input Router] -> Determine if RAG needed or direct LLM
    |
    v
[Query Processor] -> Query rewriting, decomposition, expansion
    |
    v
[Embedding Model] -> Generate query embedding
    |
    v
[Vector Store] -> ANN search (top-k chunks)
    |
    v
[Retriever] -> Fetch full chunks + metadata
    |
    v
[Reranker] -> Cross-encoder reranking (top-3)
    |
    v
[Context Builder] -> Assemble prompt with retrieved chunks
    |
    v
[LLM] -> Generate response with citations
    |
    v
[Output Guardrails] -> Verify safety, check citations, block PII
    |
    v
Response
```

## Key Design Decisions

| Decision | Options | Recommendation |
|----------|---------|---------------|
| Embedding model | text-embedding-3-small, voyage-2, BGE | Ada-002 or BGE for general |
| Vector store | Pinecone, Weaviate, pgvector, Qdrant | pgvector for AWS users, Pinecone for managed |
| Chunk size | 256-1024 tokens | 512 tokens with 128 overlap |
| Retrieval | ANN + hybrid (keyword) | Hybrid for production |
| Reranking | Cohere Rerank, BGE Reranker | Cross-encoder reranker |
| Caching | Semantic cache (near-duplicate detection) | Reduces latency 40-60% |

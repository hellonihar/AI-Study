# Data Pipelines → RAG & Retrieval Systems

## The Traditional Skill

You designed data pipelines: ETL jobs that extract data from sources, transform it (clean, normalize, enrich), and load it into a data warehouse. You understood schema design, data quality, incremental processing, and batch vs. streaming trade-offs.

## The AI Equivalent

RAG (Retrieval-Augmented Generation) pipelines are data pipelines where the "load" step writes to a vector database instead of a data warehouse. The extract step chunks documents. The transform step embeds chunks into vectors. The load step indexes them into a vector store. And the "query" step — which is new — searches the vector store to find relevant context for LLM prompts.

Everything you know about data pipelines transfers:
- **Data quality** → chunk quality, embedding quality, source freshness
- **Incremental processing** → incremental indexing of new/changed documents
- **Batch vs. streaming** → batch index for initial load, streaming for updates
- **Schema design** → vector index configuration (distance metric, index type, dimension)
- **Data lineage** → trace which document contributed which chunk to which response
- **Backfill** → re-indexing when the embedding model changes or chunking strategy improves

## New Concepts to Learn

- **Chunking:** Splitting documents into pieces for embedding — the chunking strategy (size, overlap, boundary) directly impacts retrieval quality
- **Embeddings:** Converting text to vectors — understanding embedding models, dimensions, and distance metrics
- **Vector databases:** Qdrant, Pinecone, Chroma, Weaviate — the "data warehouse" of AI systems
- **Hybrid search:** Combining vector similarity with keyword (BM25) search for better retrieval
- **Reranking:** A second-stage model that re-scores retrieved chunks for relevance — the "data quality" step of retrieval
- **Indexing pipelines:** Automated pipelines that monitor source data, chunk, embed, and index — your new ETL

## A Concrete Translation Example

**Traditional ETL:** Source (PostgreSQL) → Extract (SQL query) → Transform (Python cleaning) → Load (Snowflake)

**RAG pipeline:** Source (SharePoint) → Extract (document parser) → Transform (chunk → embed using embedding model) → Load (Qdrant vector store) → Query (search → retrieve → LLM)

Same pipeline thinking. Same concern for data freshness, quality, and error handling. New target system (vector store) and new transformation step (embedding).

## Key Resources

- LangChain document loaders and text splitters
- Qdrant / Pinecone documentation — vector database fundamentals
- "Seven Failure Modes of RAG" (Apache Airflow blog)
- Anthropic's "RAG vs. Long Context" analysis

# Vector Databases and Embeddings

Storing and searching high-dimensional vector representations of data for AI applications.

## Why Embeddings Matter

Embeddings are the bridge between unstructured data (text, images, audio) and numerical computation. They convert high-level semantic meaning into dense vectors — lists of floating-point numbers — where similar concepts are positioned close together in vector space.

### What Embeddings Capture

- **Semantic proximity:** "king" and "queen" are closer to each other than "king" and "fork"
- **Relationships via direction:** vector(king) − vector(man) + vector(woman) ≈ vector(queen)
- **Cross-modal alignment:** an image of a cat and the text "a fluffy cat" can map to nearby vectors
- **Dense representation:** a 768-dim vector captures rich semantics that sparse one-hot encoding cannot

### Why Embeddings Are Needed

Traditional databases rely on exact or pattern matching (SQL `WHERE title LIKE '%AI%'`), which fails for semantic queries. If you search "best way to learn machine learning," exact match won't return "top resources for studying ML" — even though the meaning is the same. Embeddings solve this by enabling **semantic search** — finding results by meaning, not keywords.

| Without Embeddings | With Embeddings |
|---|---|
| Exact keyword matching | Semantic similarity search |
| Misses synonyms and paraphrases | Understands "car" ⇔ "automobile" |
| Requires manual tagging | Learns representations automatically |
| No cross-modal understanding | Text, image, audio in shared space |

### How Embeddings Enable AI Applications

1. **RAG (Retrieval-Augmented Generation):** User query → embed → retrieve relevant docs by similarity → inject into LLM prompt → grounded answer. This is the primary mechanism for keeping LLMs factual and up-to-date without retraining.
2. **Recommendation systems:** Embed user preferences and item descriptions in the same space; nearest-neighbor search finds the best recommendations.
3. **Anomaly detection:** Normal data forms clusters; outliers are points far from all cluster centroids in embedding space.
4. **Deduplication and clustering:** Near-duplicate documents have nearly identical embeddings — group by cosine similarity threshold.
5. **Multi-modal search:** Search images using text queries, or find text using audio samples, by projecting all modalities into a shared embedding space.

## Significance of Vector Databases for AI Applications

Vector databases are purpose-built to store, index, and search embeddings at scale. A standard relational database can store vectors but cannot efficiently find "the 10 most similar vectors to this query" across millions of entries — that requires specialized indexing and distance computation.

### What Vector Databases Solve

- **Scale:** Brute-force similarity comparison O(n·d) is impossible beyond ~100K vectors. Vector DBs use Approximate Nearest Neighbor (ANN) indexes to achieve O(log n) or near-constant search time.
- **Freshness:** Production systems ingest new vectors continuously. Vector DBs support real-time index updates without rebuilding the entire index.
- **Hybrid search:** Most vector DBs combine vector similarity with metadata filtering (e.g., "find similar documents where category = 'research' AND date > 2024").
- **Managed infrastructure:** Cloud vector DBs handle replication, sharding, backup, and scaling — teams can focus on application logic instead of index maintenance.

### When to Use a Vector Database

| Scenario | Recommended Approach |
|---|---|
| < 10K vectors, prototyping | In-memory numpy/faiss, no dedicated DB needed |
| 10K – 1M vectors, single server | SQLite + sqlite-vec, pgvector, or Chroma |
| 1M – 100M vectors, production | Dedicated vector DB (Pinecone, Qdrant, Weaviate, Milvus) |
| > 100M vectors, high availability | Distributed vector DB with sharding and replication |
| Need ACID transactions on metadata | PostgreSQL + pgvector |
| Edge / offline deployment | SQLite + sqlite-vec, Chroma |

### Key Capabilities to Evaluate

- **Index type:** HNSW (fastest search, more memory), IVF (balanced), PQ (compressed, approximate)
- **Filtering:** Can metadata filters be applied before or after vector search? Pre-filtering is faster but less accurate.
- **CRUD support:** Can you update or delete individual vectors without rebuilding the index?
- **Multi-tenancy:** Isolated namespaces or collections per tenant with separate indexes.
- **Pricing model:** Per-vector pricing (Pinecone) vs. self-hosted infra cost (Qdrant, Milvus).

## Products and Tools

### Vector Databases

| Product | Type | Best At | Key Strength |
|---|---|---|---|
| **Pinecone** | Managed cloud | Serverless scaling, zero ops | Fastest time-to-production; no infrastructure management |
| **Qdrant** | Self-hosted / Cloud | Performance and precision | Written in Rust; advanced filtering; on-premises control |
| **Weaviate** | Self-hosted / Cloud | Hybrid search + GraphQL | Built-in vectorizer modules; native GraphQL API |
| **Milvus** | Self-hosted / Cloud | Massive scale (10B+ vectors) | Distributed architecture; GPU acceleration; CNCF graduated |
| **Chroma** | Embedded / Client | Prototyping and lightweight apps | Python-native; simple API; in-process |
| **pgvector** | PostgreSQL extension | Adding vector search to existing Postgres | No additional infrastructure; full ACID + SQL |
| **Vald** | Cloud-native | Large-scale, high-availability | Kubernetes-native; automatic backup and recovery |
| **Typesense** | Managed / Self-hosted | Typo-tolerant full-text + vector | Combined full-text and vector in a single engine |

### Embedding Models and APIs

| Model / API | Type | Dimensionality | Best At |
|---|---|---|---|
| **OpenAI text-embedding-3-small** | API | 512 / 1536 | General-purpose text, cost-effective |
| **OpenAI text-embedding-3-large** | API | 256 / 3072 | Highest accuracy text embeddings |
| **Cohere Embed v3** | API | 1024 / 4096 | Multilingual, classification-aware |
| **Sentence Transformers (all-MiniLM-L6-v2)** | Open-source | 384 | Lightweight, fast, self-hosted |
| **Sentence Transformers (all-mpnet-base-v2)** | Open-source | 768 | Best accuracy among open-source |
| **Google Gecko** | API | 768 | Multilingual, 250+ languages |
| **CLIP (OpenAI)** | Open-source | 512 | Text + image (multi-modal) |
| **Voyage AI** | API | 768 / 1024 / 2048 | Domain-specific (legal, code, finance) |

### Supporting Libraries

| Library | Purpose | Best For |
|---|---|---|
| **FAISS (Meta)** | ANN search library (not a DB) | High-performance indexing on your own infrastructure |
| **Annoy (Spotify)** | ANN with memory-mapped files | Read-only indexes, large-scale static datasets |
| **HNSWlib** | HNSW index implementation | When you need the fastest possible search quality |
| **Scikit-learn** | NearestNeighbors, PCA | Prototyping, small datasets, integration with ML pipelines |
| **LlamaIndex** | Document → chunk → embed → index pipeline | Building RAG systems quickly |
| **LangChain** | Vector store integrations | Switching between vector DB backends with minimal code |

## Key Topics
- Embedding models (text, image, multimodal)
- Embedding dimensionality and normalization
- Vector database fundamentals (indexing, storage, query)
- Approximate Nearest Neighbor (ANN) search
- Index types (IVF, HNSW, PQ, LSH)
- Popular vector databases (Pinecone, Weaviate, Qdrant, Milvus, Chroma)
- pgvector (PostgreSQL vector extension)
- Hybrid search with metadata filtering
- Distance metrics (cosine, Euclidean, dot product, Manhattan)
- Multitenancy and namespaces
- Curating and updating embeddings
- Monitoring vector search quality and latency

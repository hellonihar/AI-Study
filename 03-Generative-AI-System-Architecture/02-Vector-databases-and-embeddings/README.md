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

### Embedding Models (Text, Image, Multimodal)

**Example:** A RAG application for legal documents uses `text-embedding-3-large` (3072-dim) to embed contracts and case law. A product search app uses CLIP to embed both product images and text descriptions into a shared 512-dim space, enabling users to search for products using either text ("red running shoes") or an uploaded photo of a shoe they like.

**Design Guidelines:**
- Match the embedding model to your data modality — text-only tasks don't need multimodal models, and vice versa
- Prefer smaller embedding dimensions (384-768) for latency-sensitive apps; use larger dimensions (1024-3072) when retrieval accuracy is the top priority
- Evaluate embedding quality on your domain before committing — a model trained on general web text may perform poorly on medical or legal corpora
- Batch embed documents during ingestion (not one-by-one) to maximize throughput and minimize API costs

**Performance Implications:**
- Embedding generation latency: 10-200ms per text chunk depending on model size and hardware (GPU vs CPU)
- Higher dimensions increase storage (4 bytes per float per dimension), index build time, and search latency — a 3072-dim vector takes 4× the RAM and search time of a 768-dim vector
- API-based embedding services add network round-trip latency (50-200ms) — self-hosting Sentence Transformers eliminates this
- Cross-modal retrieval (text ↔ image) requires all modalities to use compatible embeddings — verify alignment quality in your domain

### Embedding Dimensionality and Normalization

**Example:** A team building a FAQ chatbot initially uses 3072-dim embeddings from text-embedding-3-large, achieving 97% retrieval accuracy. They switch to the 512-dim variant (via the `dimensions` parameter) and measure 95% accuracy — acceptable for their use case — while cutting storage by 83% and search latency by 3×.

**Design Guidelines:**
- Always normalize embeddings to unit length (L2 norm = 1) if using cosine similarity — this ensures consistent magnitude across different embedding models
- Store the raw (un-normalized) vector only if Euclidean distance is your primary metric; otherwise normalize at write time
- Lower dimensions are more efficient but may lose fine-grained semantic distinctions — benchmark before reducing
- Use Matryoshka Representation Learning models (e.g., OpenAI's text-embedding-3) that support flexible dimensionality without re-embedding

**Performance Implications:**
- Storage scales linearly with dimensionality: a 768-dim float32 vector = 3KB, 3072-dim = 12KB. For 10M vectors: 30GB vs 120GB
- Search latency grows with dimensionality — ANN search time is approximately O(d) to O(d·log n) depending on the index
- Normalization is cheap (O(d) per vector) and should be applied during ingestion, not at query time
- Dot product and cosine similarity are equivalent on normalized vectors — dot product is slightly faster to compute

### Vector Database Fundamentals (Indexing, Storage, Query)

**Example:** A recommendation system ingests 500K product embeddings into Qdrant. The system creates an HNSW index with m=16 and ef_construct=200 during ingestion. At query time, each user request embeds their preference text, searches with ef=128, retrieves top-50 results, then re-ranks by metadata (price range, brand) before returning top-10.

**Design Guidelines:**
- Choose the index type before bulk ingestion — rebuilding an index on millions of vectors is expensive
- Batch inserts are faster than individual inserts — group writes into batches of 100-1000 vectors
- Configure indexing parameters (m, ef_construct) based on the tradeoff between ingestion speed and search accuracy you can tolerate
- Separate ingestion and query workloads where possible — use a dedicated indexing pipeline and a separate query endpoint

**Performance Implications:**
- Index build time ranges from minutes (IVF, 1M vectors) to hours (HNSW, 100M vectors) — plan ingestion as a batch job
- Raw vector storage is additional to the index — index can be 1.1-2× the raw vector size depending on type
- Query latency depends on index type, dataset size, and recall target — typical range is 2-50ms for ANN search
- Write operations during active queries can cause latency spikes — use separate replicas for read and write if latency SLAs are tight

### Approximate Nearest Neighbor (ANN) Search

**Example:** A semantic search app with 50M vectors cannot afford brute-force scanning (50M distance computations per query, ~500ms). Switching to HNSW with ef=128 returns results in 8ms with 98% recall — 60× faster with negligible accuracy loss.

**Design Guidelines:**
- Set a recall target (95%, 98%, 99%) and tune index parameters to meet it — higher recall costs more memory and latency
- Benchmark ANN recall using your own data, not synthetic benchmarks — real-world embedding distributions vary significantly
- Use the query-time parameter (ef, nprobe) to trade latency for recall dynamically — high ef during off-peak, lower ef during peak load
- Always compare ANN results against brute-force (exact) search during evaluation to measure true recall

**Performance Implications:**
- ANN search is 10-100× faster than brute-force for large datasets but trades deterministic accuracy for speed
- Recall-latency curve is logarithmic: the last 1% of recall doubles or triples query time
- Memory usage varies by index: HNSW 1.2-1.5× vector size, IVF ~1.1×, PQ compresses to 0.1-0.5×
- GPU-accelerated ANN (RAPIDS cuANN, FAISS GPU) can be 5-10× faster than CPU for large batch queries

### Index Types (IVF, HNSW, PQ, LSH)

**Example:** A document search system chooses IVF with 4096 centroids for 10M vectors — fast index build (30 min), moderate search latency (15ms at 95% recall). A real-time agent system uses HNSW with m=32 for 500K vectors — slower build (2 hours) but sub-5ms search at 99% recall.

**Design Guidelines:**

| Index | Best For | Avoid When |
|---|---|---|
| **IVF** | Large datasets, frequent rebuilds | You need sub-5ms search or >99% recall |
| **HNSW** | Low-latency, high-recall requirements | RAM is constrained or index must be rebuilt often |
| **PQ (Product Quantization)** | Limited memory budget | High recall is critical (PQ is lossy) |
| **LSH** | Simple, distributed-friendly | Better alternatives exist for most modern use cases |

**Performance Implications:**
- HNSW: 2-10ms search at 99% recall for 1M vectors; memory ~1.3× raw vectors; build time 2-5× slower than IVF
- IVF: 10-50ms search at 95-98% recall; memory ~1.05× raw; build time 2-5× faster than HNSW
- PQ: 1-10ms search at 85-95% recall; memory compressed 4-10×; recall drop depends on compression ratio
- LSH: 5-20ms search at 80-95% recall; memory varies; rarely the top choice — HNSW or IVF usually dominate

### Popular Vector Databases (Pinecone, Weaviate, Qdrant, Milvus, Chroma)

**Example:** A startup building a semantic PDF search tool starts with Chroma for rapid prototyping (local, no cloud setup). After reaching 2M vectors, they migrate to Qdrant for production — gaining advanced filtering, self-hosting control, and consistent sub-10ms query latency.

**Design Guidelines:**
- Start with an embedded solution (Chroma, pgvector) for prototyping — defer infrastructure decisions until you understand your scale and query patterns
- Choose managed (Pinecone, Weaviate Cloud) over self-hosted when team ops bandwidth is limited
- Evaluate filtering capabilities carefully — some databases apply filters post-query (slower), others interleave them with vector search
- Test with production-scale data before committing — a database that works at 100K vectors may behave differently at 10M

**Performance Implications:**

| Database | Query Latency (1M, HNSW) | Max Practical Scale | Write Throughput |
|---|---|---|---|
| Pinecone | 5-15ms | 100M+ | 1K-10K vectors/s |
| Qdrant | 3-10ms | 50M+ | 5K-50K vectors/s (Rust) |
| Weaviate | 5-20ms | 50M+ | 1K-5K vectors/s |
| Milvus | 5-15ms | 10B+ | 10K-100K vectors/s (distributed) |
| Chroma | 2-8ms | 1M (single node) | 1K-5K vectors/s |

### pgvector (PostgreSQL Vector Extension)

**Example:** An e-commerce platform already uses PostgreSQL for products, orders, and users. They add pgvector to store product embedding vectors alongside existing product data, enabling semantic product search without introducing a new database — queries combine vector similarity with SQL filters (`WHERE price < 100 ORDER BY embedding <=> '[0.1, 0.3, ...]' LIMIT 10`).

**Design Guidelines:**
- Use pgvector when you already run PostgreSQL and want vector search without additional operational overhead
- Enable IVFFlat index for queries at ~95% recall; use HNSW (pgvector 0.7+) when you need higher recall or lower latency
- Keep vectors in the same table as related data to avoid join overhead and maintain transactional consistency
- Consider a sidecar vector DB instead of pgvector if you need > 10M vectors or sub-5ms query latency

**Performance Implications:**
- IVFFlat index: 10-50ms per query up to ~5M vectors; index build proportional to dataset size
- HNSW index (pgvector 0.7+): 3-15ms per query, faster but more memory
- Filtering before vector search (pre-filter) is supported but can degrade recall if filters are too selective
- No dedicated vector node — shares resources with your OLTP workload; index vector memory competes with buffer pool
- Write throughput is limited by PostgreSQL's row-level locking — 1K-5K vector writes/s per node

### Hybrid Search with Metadata Filtering

**Example:** A knowledge base search app retrieves documents similar to a user query but filtered to `department = 'engineering' AND document_type = 'RFC' AND created_at > '2024-01-01'`. The vector search returns candidates, then metadata filters narrow the result set, ensuring engineers see only relevant RFCs from the past year.

**Design Guidelines:**
- Prefer databases that support pre-filtering (Qdrant, Milvus, Pinecone with filter integration) over post-filtering for large filtered result sets
- Index frequently filtered metadata columns separately for fast lookups — composite indexes on (category, date) speed up filter-first search
- Design metadata schema to be flat and non-nullable — nested or sparse metadata slows filter evaluation
- Test query patterns with selective filters (matching 0.1% of data) — these can kill recall if filtering is applied naively

**Performance Implications:**
- Post-filter latency: vector search time + filter time over N results — grows linearly with N
- Pre-filter latency: filter evaluation + vector search over filtered subset — filter step can dominate if too selective (matching < 0.1% of data)
- Some databases apply filtering after vector search by default — check and configure filter strategy explicitly
- Heavy metadata filtering can reduce ANN recall significantly because the nearest neighbors in the filtered subset may differ from the global nearest neighbors

### Distance Metrics (Cosine, Euclidean, Dot Product, Manhattan)

**Example:** A document similarity system uses cosine distance for normalized document embeddings (angles capture topical similarity regardless of document length). A product recommendation system uses dot product because user preference vectors and item vectors are unnormalized and magnitude reflects confidence.

**Design Guidelines:**
- Use cosine similarity for text embeddings — it is the most widely adopted and matches how embedding models are typically trained
- Use dot product when embedding norms encode importance (e.g., term frequency in TF-IDF-like weighted embeddings)
- Use Euclidean distance when absolute position in vector space matters (e.g., anomaly detection where distance from cluster center is meaningful)
- Use Manhattan distance only with low-dimensional embeddings (< 128 dim) or when interpretability is needed — rarely used in modern systems

**Performance Implications:**

| Metric | Compute Cost | Normalization Required | Best For |
|---|---|---|---|
| Cosine Similarity | O(d) + normalize | Yes (unit vectors) | Text embeddings, semantic similarity |
| Dot Product | O(d) | No | Recommendation, magnitude-sensitive |
| Euclidean Distance | O(d) | Optional | Clustering, anomaly detection |
| Manhattan Distance | O(d) | Optional | High-noise data, interpretability |

- Cosine is nearly identical to dot product on normalized vectors — prefer dot product for slightly faster computation
- Euclidean requires computing squares and a square root — fractionally slower than cosine (negligible at query time with optimized libraries)
- Some vector databases convert all metrics internally to a common representation — confirm the actual computation cost

### Multitenancy and Namespaces

**Example:** A SaaS document search platform serves 500 companies. Each company's documents are stored in a separate Qdrant collection with its own HNSW index. Queries include a tenant header that routes to the correct collection, guaranteeing zero cross-tenant leakage and isolated performance.

**Design Guidelines:**
- Use separate collections (or indexes) per tenant for strict isolation, especially when tenants have different data volumes or SLAs
- Use a single collection with a tenant_id metadata field when tenants are numerous and each has small data (< 10K vectors) — avoids index overhead
- Monitor per-tenant query latency and index size — a single tenant with 50M vectors can degrade search for all tenants in shared-index designs
- Implement tenant-level rate limiting and resource quotas to prevent noisy-neighbor problems

**Performance Implications:**
- Per-tenant collections: each collection has its own index — memory overhead is O(n_collections × index_size) but query isolation is perfect
- Shared collection with tenant filter: filter evaluation adds 1-5ms per query — acceptable when tenants have small data subsets
- Index rebuild per tenant: with 500 separate collections, each rebuild is 1/500th the size but requires 500 separate operations
- Metadata-only tenants (< 1K vectors) may not benefit from vector indexing at all — brute-force is faster for tiny datasets

### Curating and Updating Embeddings

**Example:** An e-commerce search system re-embeds product descriptions nightly when inventory or product details change. New products are embedded immediately and inserted into the index. Deprecated products are deleted. A weekly consolidation job re-indexes to handle fragmentation from the churn.

**Design Guidelines:**
- Batch embed updates (nightly or hourly) rather than per-event to control API costs and pipeline load
- Implement soft-delete first — mark vectors as inactive without removing them from the index, then hard-delete during consolidation windows
- Version your embeddings — store the model ID and version alongside each vector to detect when re-embedding is needed after a model update
- Maintain an shadow index for new embeddings while the old index serves queries — swap on completion to avoid rebuild downtime

**Performance Implications:**
- Inserting individual vectors into an HNSW index is fast (sub-ms) but degrades index quality over time — periodic re-indexing restores search accuracy
- Deleting vectors from HNSW: most databases mark as deleted without removing from graph — deleted entries still consume memory and add noise to search
- Re-indexing a 10M-vector HNSW index takes 1-6 hours depending on hardware — schedule during low-traffic windows
- Churn rate (insert+delete ratio) affects index quality — >10% churn suggests more frequent re-indexing

### Monitoring Vector Search Quality and Latency

**Example:** A production RAG system tracks: p50/p99 query latency (target < 50ms), recall@10 (target > 95%, measured monthly against brute-force), index size growth, and cache hit rate. An alert fires when recall drops below 90%, triggering an index rebuild or parameter retuning.

**Design Guidelines:**
- Track recall by periodically comparing ANN results against exact (brute-force) search on a held-out query set — run this as a scheduled job
- Monitor tail latency (p99, p99.9) not just averages — vector search concurrency can cause queuing delays under load
- Set up dashboards for: query latency, recall@K, index size, write throughput, error rates, and per-tenant usage
- Implement query tracing — log embedding_time + search_time + re-ranking_time for every request to pinpoint bottlenecks

**Performance Implications:**
- Monitoring overhead should be < 1% of query resources — avoid running brute-force comparisons on every query
- Recall degradation often precedes latency degradation — an old index quietly returns worse results before it becomes slower
- Index size growth is linear with data and often the earliest indicator that consolidation is needed
- Load testing with production traffic patterns reveals scaling bottlenecks that unit tests miss — simulate peak concurrency (QPS × average query time = active connections)

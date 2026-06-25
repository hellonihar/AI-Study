# Retrieval-Augmented Generation (RAG)

Combining retrieval systems with generative models to produce grounded, factual outputs.

## The Need for RAG

Large Language Models (LLMs) are trained on static corpora with a knowledge cutoff. They have no access to your private documents, real-time data, or domain-specific information. Without external grounding, LLMs suffer from three critical problems:

### Problems RAG Solves

| Problem | Description | Consequence Without RAG |
|---|---|---|
| **Knowledge cutoff** | Model only knows data up to its training date | Cannot answer about recent events, products, or policies |
| **Hallucination** | Model generates plausible but false information | Untrustworthy outputs, especially in high-stakes domains (legal, medical, finance) |
| **Lack of private knowledge** | Model has no access to internal documents, databases, or user-specific context | Cannot answer questions about your company's internal policies, customer data, or proprietary systems |
| **Opacity** | No way to trace which source the model used | Hard to audit, debug, or verify correctness |

### How RAG Fixes This

RAG adds a **retrieval step** before generation: given a user query, the system first searches a knowledge base (vector DB, keyword index, or both) for relevant documents, then passes those documents as context to the LLM. This grounds the LLM's output in verifiable sources:

- **Up-to-date knowledge:** Refresh the knowledge base independently of the model — no retraining needed
- **Auditable sources:** Every answer can cite which retrieved document(s) support it
- **Domain-specific grounding:** Index internal wikis, product docs, support tickets, or research papers
- **Reduced hallucination:** The LLM has factual context to condition on, rather than relying solely on parametric memory

## RAG Variants and Their Trade-offs

RAG is not a single architecture — it spans a spectrum of designs with different complexity, retrieval quality, and latency characteristics.

### Variant 1: Naive RAG (Retrieve-then-Generate)

The simplest form. User query → retrieve top-k chunks → concatenate into prompt → LLM generates answer.

**How it works:** Query is embedded, similar chunks are retrieved from a vector DB, the chunks are concatenated (often with a separator) and inserted into a prompt template, and the LLM generates the final answer.

**When to use:** Prototyping, simple Q&A over small-to-medium document collections, applications where retrieval quality is already high.

### Variant 2: RAG with Re-ranking

Adds a cross-encoder re-ranker between retrieval and generation. The bi-encoder (used for initial retrieval) is fast but imprecise; the cross-encoder re-orders the top-k results with higher accuracy.

**How it works:** Retrieve top-50 with bi-encoder → re-rank top-10 with cross-encoder → pass to LLM. The cross-encoder jointly encodes query + document for precise relevance scoring.

**When to use:** Production systems where the first retrieved result must be highly relevant, applications where a slightly slower pipeline is acceptable for better quality.

### Variant 3: Query Transformation (Rewrite + Decompose + HyDE)

Transforms the user's query to improve retrieval quality before searching. Includes query rewriting (paraphrase for better embeddings), query decomposition (break complex questions into sub-questions), and HyDE (Hypothetical Document Embeddings — generate a hypothetical answer first, then use its embedding for retrieval).

**How it works:** Raw query → LLM rewrites/improves the query or generates a hypothetical document → the transformed query is used for retrieval → results go to generation.

**When to use:** Complex or ambiguous user queries, multi-part questions, domains where user expertise varies (e.g., a novice asking in imprecise language).

### Variant 4: Self-RAG

The model decides *when* to retrieve based on its own confidence. It can retrieve on some tokens and skip retrieval for others, using special reflection tokens to evaluate the need for retrieval and the relevance of retrieved passages.

**How it works:** The LLM is fine-tuned with special retrieval and critique tokens. During generation, it decides: (a) should I retrieve? (b) which passages are relevant? (c) is the generation supported by the passages? Retrieval is invoked only when needed.

**When to use:** Applications where not every query needs retrieval (simple factual questions can be answered from parametric memory), reducing latency and cost for easy queries while maintaining accuracy for hard ones.

### Variant 5: Corrective RAG (CRAG)

After retrieval, an evaluator checks whether retrieved documents are relevant to the query. If relevance is low, the system either retrieves again with a different strategy (web search, different source) or falls back to the model's parametric knowledge.

**How it works:** Retrieve → evaluate relevance (score or classifier) → if score < threshold: retry with different source or fall back; if score > threshold: proceed to generation with the retrieved content. Can also decompose the query and try retrieval on sub-queries.

**When to use:** High-stakes applications where serving irrelevant context could be harmful (legal advice, medical Q&A), knowledge bases with variable quality documents.

### Variant 6: Agentic RAG

The retrieval process is managed by an AI agent that can iteratively retrieve, reflect, and refine. The agent may call multiple tools (vector DB, web search, SQL database, API), synthesize results across steps, and continue retrieving until it has sufficient information.

**How it works:** Agent receives query → decides which retrieval tool(s) to call → evaluates results → may call additional tools or ask clarification questions → when satisfied, generates final answer with citations.

**When to use:** Complex research tasks requiring information synthesis across multiple sources, dynamic knowledge needs where the correct retrieval strategy is not known upfront.

### Variant 7: Multi-modal RAG

Extends RAG beyond text to include images, tables, charts, audio, and video. Documents are chunked and embedded in a multi-modal embedding space, allowing retrieval of relevant images or tables alongside text.

**How it works:** Each modality has an embedding model (or a unified multi-modal model like CLIP). Chunks are indexed with their modality tag. Retrieval may fetch a mix of text and images. The LLM (multi-modal capable, e.g., GPT-4o, Gemini) receives both text and images in context.

**When to use:** Documents containing diagrams, charts, screenshots, or scanned forms; applications where answers require understanding both text and visual elements.

### Comparison Table

| Variant | Precision | Recall | Latency | Complexity | Cost | Best When... |
|---|---|---|---|---|---|---|
| **Naive RAG** | Medium | Medium | Low | Low | Low | Simplicity and speed matter most |
| **RAG + Re-rank** | High | Medium | Medium | Medium | Medium | Accuracy is more important than raw speed |
| **Query Transform** | High | High | Low-Medium | Medium | Low-Medium | Users ask vague or complex questions |
| **Self-RAG** | High | High | Variable | High | Medium | Selective retrieval optimizes cost/quality |
| **Corrective RAG** | Very High | High | Medium-High | High | Medium-High | Wrong answers are costly (medical, legal) |
| **Agentic RAG** | Very High | Very High | High | Very High | High | Multi-source research and synthesis needed |
| **Multi-modal RAG** | High | High | Medium | High | Medium-High | Documents contain images, tables, or charts |

**Plus (+) and Minus (-) Breakdown:**

| Variant | Plus (+) | Minus (-) |
|---|---|---|
| **Naive RAG** | + Simplest to implement and debug<br>+ Lowest latency (single round-trip)<br>+ Easy to deploy and monitor | - No query optimization for poor queries<br>- No re-ranking — first-pass retrieval errors propagate<br>- Fixed top-k regardless of query complexity |
| **RAG + Re-rank** | + Significantly higher precision on first result<br>+ Cross-encoder is more accurate than bi-encoder<br>+ Well-understood, proven in production | - Adds re-ranking latency (50-200ms per query)<br>- Requires deploying and maintaining a cross-encoder model<br>- Re-ranked top-k is still limited by initial retrieval recall |
| **Query Transform** | + Handles poorly phrased queries gracefully<br>+ HyDE improves retrieval for abstract questions<br>+ Decomposition handles multi-part questions | - Adds LLM call latency for transformation (1-3s)<br>- Transformed query may lose original user intent<br>- HyDE's quality depends on the hypothetical document quality |
| **Self-RAG** | + Retrieves only when necessary — reduces cost<br>+ Reflection tokens provide traceability<br>+ Adapts to query difficulty automatically | - Requires fine-tuning the base model (not plug-and-play)<br>- Harder to debug due to conditional retrieval<br>- Limited model support (requires specific fine-tuning) |
| **Corrective RAG** | + Robust to poor knowledge base quality<br>+ Graceful fallback prevents serving bad context<br>+ Can combine multiple retrieval sources | - Complex evaluation pipeline adds latency<br>+ Retry logic can multiply costs per query<br>- Threshold tuning is non-trivial and domain-dependent |
| **Agentic RAG** | + Most flexible — adapts strategy per query<br>+ Can synthesize across very diverse sources<br>+ Handles queries no single-pass RAG can solve | - Highest latency (5-30s common for multi-step)<br>+ Highest cost (multiple LLM calls per query)<br>- Most complex to build, test, and monitor |
| **Multi-modal RAG** | + Answers questions requiring visual context<br>+ Richer user experience with images in answers<br>+ Handles PDFs with diagrams and scanned content | + Requires multi-modal embedding and LLM<br>+ Image/table chunking is harder than text<br>+ Storage and indexing costs are higher |

## Design Guidelines

### Architecture Decisions

1. **Start simple, add complexity only when needed.** Begin with Naive RAG (embed → retrieve → generate). Measure recall@k, precision@k, and end-to-end answer quality. Add re-ranking only if precision is insufficient. Add query transformation only if queries are clearly poorly formed. Over-engineering upfront is the most common RAG failure.

2. **Chunking strategy is the most impactful design decision.** Chunk size determines both retrieval relevance and context utilization. Too small (50-100 tokens) loses surrounding context; too large (1000+ tokens) dilutes relevance with noise. Start at 256-512 tokens with 10-20% overlap, then tune based on your document structure.

3. **Index metadata alongside vectors.** Store source document ID, chunk position, title, date, and any domain-specific tags. This enables filtering (e.g., "only from documents dated after 2024"), post-retrieval processing, and citation generation.

4. **Design the prompt template carefully.** The retrieved context goes into the prompt — structure it for the LLM to consume effectively. Use clear separators, numbering, and instructions. Bad prompt design can negate even perfect retrieval.

### Best Practices

**Document Ingestion:**
- Clean and normalize documents before chunking — remove headers/footers, normalize whitespace, fix encoding issues
- Chunk hierarchically: preserve document structure (sections, paragraphs, lists) in chunk boundaries
- Generate meaningful chunk summaries or titles to improve retrieval interpretability
- Version your embeddings — when you change embedding models, re-index all documents with the new model

**Retrieval:**
- Always retrieve more candidates than you pass to the LLM (retrieve top-20, pass top-5-10 to LLM) — the extra candidates serve the re-ranker or allow filtering
- Combine dense + sparse retrieval when your documents have domain-specific terminology (BM25 catches exact matches that dense embeddings miss)
- Set relevance thresholds — discard retrieved chunks below a similarity score to prevent the LLM from seeing irrelevant context

**Generation:**
- Instruct the LLM to cite sources explicitly: "Answer using only the provided context. Cite the source document name for each claim."
- Instruct the LLM to refuse when context is insufficient: "If the context does not contain enough information, say 'I cannot answer this from the available documents.'"
- Set a maximum context window budget — truncate retrieved chunks (trim from the bottom) if they exceed the token limit
- Use a lower temperature (0.0-0.3) for fact-grounded generation to reduce creative divergence

## Production Monitoring and Management

### Key Metrics to Track

| Category | Metric | Target | What It Tells You |
|---|---|---|---|
| **Retrieval Quality** | Recall@k | >90% | Are we retrieving the right documents? |
| **Retrieval Quality** | Precision@k | >70% | Are retrieved documents relevant? |
| **Retrieval Quality** | Mean Reciprocal Rank (MRR) | >0.85 | Is the best result ranked first? |
| **Answer Quality** | Faithfulness | >95% | Is the answer grounded in retrieved context? |
| **Answer Quality** | Answer Relevance | >4/5 | Does the answer address the query? |
| **Answer Quality** | Hallucination rate | <5% | Is the model fabricating information? |
| **Latency** | p50/p99 retrieval time | <50ms / <200ms | Is retrieval fast enough? |
| **Latency** | p50/p99 end-to-end time | <3s / <10s | Is the full pipeline acceptable? |
| **Cost** | Cost per query | Budget-dependent | Are we spending too much? |
| **Cost** | Cache hit rate | >40% | Is caching effective? |

### Monitoring Infrastructure

- **Log every retrieval-generation cycle.** Store: query (normalized), retrieved chunks (IDs + scores), final answer, latency breakdown (retrieval, re-rank, generation), token counts, and model used. This is essential for debugging and quality analysis.
- **Set up dashboards.** Real-time graphs for: QPS, p50/p99 latency, token consumption, cost per hour, retrieval recall, and error rates. Use tools like Grafana, Datadog, or SigNoz.
- **Implement traceability.** Every answer should be traceable back to the source documents. Include chunk IDs and document names in the response metadata. This enables both debugging and user-facing citations.
- **Automated quality checks.** Run a nightly batch of known question-answer pairs against your RAG system. Measure faithfulness and recall against ground truth. Alert if metrics drop more than 5% from baseline.

### Common Production Issues

| Issue | Symptom | Likely Cause | Fix |
|---|---|---|---|
| Low recall | High "I don't know" rate | Chunking too coarse or embedding model mismatch | Tune chunk size, switch embedding model |
| Low precision | Irrelevant answers | Retrieved chunks not matching query intent | Add re-ranker, raise similarity threshold |
| High latency | p99 > 10s | Too many retrieved chunks, large model, or slow vector DB | Reduce top-k, use smaller model, upgrade vector DB |
| Hallucination | Answers not in retrieved context | Prompt template insufficiently constraining generation | Add "cite only provided context" instruction, lower temperature |
| Cost overrun | Budget exceeded | Too many tokens per query, expensive model | Cache, reduce context tokens, use cheaper model for simple queries |
| Drift over time | Metrics degrading | Documents updated but index stale, or query distribution shifted | Set up re-indexing schedule, monitor query distribution |

### Management Playbook

- **Establish a baseline.** Before optimizing, run your RAG system on a held-out evaluation set (200-500 Q&A pairs). Measure all metrics above. Every change should be measured against this baseline.
- **Version your RAG pipeline.** Changes to chunking, embedding models, retrieval parameters, or prompt templates should be versioned. Use A/B testing or shadow deployments to compare variants.
- **Schedule re-indexing.** Documents change. Set up a periodic re-indexing pipeline (nightly, weekly) that re-processes changed documents and updates the vector index.
- **Handle query distribution shifts.** Monitor the types of queries arriving. If users start asking questions in a new domain, your existing chunking/embedding strategy may underperform. Periodically sample queries and evaluate retrieval quality manually.
- **Incident response for RAG.** When quality drops: (1) check if the index was recently rebuilt with a bad embedding model, (2) check if the prompt template was changed, (3) sample recent bad answers and trace back to which retrieved chunks caused them, (4) roll back the offending change.
- **User feedback loop.** Implement thumbs-up/thumbs-down on answers. Log feedback alongside the query and retrieval metadata. Use this data to continuously improve chunking, retrieval, and prompt design.

## Key Topics

### RAG Architecture Overview (Retrieve-then-Generate)

**What is it:** The foundational RAG pattern where a user query triggers a retrieval step (searching a pre-indexed knowledge base for relevant documents), followed by a generation step (an LLM produces an answer conditioned on both the query and the retrieved context).

**When it is needed:** Whenever an LLM must answer questions grounded in specific, private, or up-to-date information that is not in its training data. This covers the majority of production RAG use cases.

**Examples:**
- A customer support bot retrieves from the company's product documentation to answer user questions about features
- A legal research assistant retrieves from a database of case law and statutes to answer attorney queries
- An internal knowledge management tool retrieves from company wikis and Confluence pages to answer employee questions

**Best practices:**
- Separate your retrieval and generation concerns — use the best tool for each (a vector DB for retrieval, a strong LLM for generation)
- Design the retrieval context to fit within the LLM's context window with room for the query and instruction prompt
- Always include a "no relevant context" fallback instruction in the prompt to avoid forced hallucination
- Version both the index and the prompt template together — a new prompt may expect different chunk structure

**Products/platforms:**
- **LlamaIndex:** End-to-end framework for building RAG pipelines (ingestion, indexing, retrieval, prompting)
- **LangChain:** RAG chains with pluggable retrievers and vector stores
- **Haystack:** Pipeline framework with dedicated RAG components
- **Canopy (Pinecone):** Managed RAG service with built-in chunking, embedding, and generation

**Performance aspects:**
- End-to-end latency is dominated by the LLM generation step (2-10s for typical responses)
- Retrieval latency (vector DB lookup) should be <50ms at p99 — if higher, optimize the index or scaling
- Context window utilization: monitor how many of the retrieved tokens are actually used by the LLM — unused tokens are wasted cost
- Throughput bottleneck is typically the LLM API rate limit — cache and batch to mitigate

### Document Chunking Strategies (Fixed-Size, Semantic, Recursive)

**What is it:** The process of splitting documents into smaller, retrievable pieces (chunks). The chunking strategy directly determines retrieval quality — too small loses context, too large dilutes relevance. Strategies include fixed-size (token count), semantic (natural boundaries like paragraphs), and recursive (hierarchical splitting with overlap).

**When it is needed:** Every RAG system requires chunking — raw documents are almost always too large to use as direct retrieval units. Chunking is the first and most impactful design decision in any RAG pipeline.

**Examples:**
- A 50-page product manual is chunked by section heading (semantic) into 80 chunks averaging 300 tokens each
- A codebase is chunked by function definition (recursive) with 10% token overlap between adjacent chunks
- A news article is chunked into fixed 512-token windows with 64-token overlap to capture paragraph boundaries

**Best practices:**
- Preserve document structure — split on natural boundaries (headings, paragraphs, sentences) rather than arbitrary token counts
- Use overlap (10-20%) between adjacent chunks to prevent information loss at boundaries (e.g., a sentence spanning two chunks)
- Store chunk metadata (document ID, position, heading path) to enable filtering and citation
- Benchmark chunking strategy on your own documents — the optimal strategy depends on your document structure and query types
- Consider multi-scale chunking: index both small chunks (precise retrieval) and larger surrounding context windows (rich context)

**Products/platforms:**
- **LlamaIndex:** Node parsers with multiple chunking strategies (SentenceSplitter, TokenTextSplitter, HierarchicalNodeParser)
- **LangChain:** Text splitters (RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter, PythonCodeTextSplitter)
- **Unstructured.io:** Document parsing and chunking for complex formats (PDFs with tables, scanned docs)
- **Semantic Chunkers (Jina AI, Chroma):** Embedding-aware chunking that detects topic boundaries via similarity drops

**Performance aspects:**
- Chunk size directly affects retrieval precision: smaller chunks (128-256 tokens) give higher precision but may lack context; larger chunks (512-1024) give more context but potentially lower precision
- Overlap increases index size linearly — 10% overlap on 1M chunks adds 100K extra chunks
- Recursive splitting is slower than fixed-size but produces cleaner chunks — negligible impact on ingestion throughput
- Changing chunking strategy requires re-indexing all documents — test on a sample first

### Embedding-Based Retrieval (Dense Retrieval)

**What is it:** Using a neural embedding model to encode both documents and queries into dense vector representations, then retrieving documents by vector similarity (cosine, dot product). Unlike keyword search, dense retrieval captures semantic meaning — synonyms, paraphrases, and conceptual similarity.

**When it is needed:** When queries and documents use different vocabulary for the same concepts (e.g., user asks "automobile repair" but documents say "car maintenance"), when the knowledge base is large and keyword search is too slow, or when synonyms and related concepts are important.

**Examples:**
- A medical research system retrieves papers matching "cardiac arrest treatments" even when papers use "myocardial infarction management"
- An e-commerce product search finds "red sneakers" when querying "crimson running shoes"
- A legal document search retrieves cases about "breach of contract" from documents using "default of agreement"

**Best practices:**
- Choose the embedding dimensionality based on your latency and accuracy needs — 768-dim is a good default; 384-dim for speed; 1024-3072 for high accuracy
- Normalize all embeddings to unit length — ensures cosine similarity and dot product produce identical rankings
- Re-embed documents when you upgrade the embedding model — different models produce incompatible vector spaces
- Evaluate embedding quality on your domain before committing — a model strong on general text may underperform on legal/medical/technical text

**Products/platforms:**
- **OpenAI text-embedding-3-small/large:** General-purpose, high-quality embeddings via API
- **Sentence Transformers (all-MiniLM-L6-v2, all-mpnet-base-v2):** Open-source, self-hostable embedding models
- **Cohere Embed v3:** Multilingual embeddings with classification-aware training
- **Voyage AI:** Domain-specific embedding models (legal, code, finance)
- **Google Gecko:** Multilingual embedding supporting 250+ languages

**Performance aspects:**
- Embedding generation latency: 10-200ms per query (API) or 5-50ms (local GPU)
- Dense retrieval is typically faster than BM25 for large corpora due to ANN indexing (O(log n) vs O(n))
- Storage: each 768-dim float32 vector consumes 3KB; 10M vectors = 30GB for vectors alone
- Retrieval quality degrades when embedding model doesn't match domain — always benchmark on your data

### Keyword-Based Retrieval (BM25, Sparse Retrieval)

**What is it:** Traditional information retrieval using keyword matching and TF-IDF weighting. BM25 is the modern standard — it scores documents by term frequency, inverse document frequency, and document length normalization. No neural network is involved; retrieval is based on exact word and phrase matches.

**When it is needed:** When exact term matching is critical (product codes, legal citations, medical terms), when the domain has specialized vocabulary poorly captured by embeddings, or as a complement to dense retrieval in hybrid search for high precision on known terms.

**Examples:**
- A patent search system where patent numbers and technical classifications must match exactly
- A legal document search where statute citations (e.g., "42 U.S.C. § 1983") must be precise
- A product catalog where SKU numbers and brand names are critical for retrieval

**Best practices:**
- Always normalize text before BM25 indexing (lowercase, remove punctuation for general search; preserve case and punctuation for code/IDs)
- Use fielded BM25 (title vs. body) when document structure distinguishes important fields
- Combine BM25 with dense retrieval (hybrid search) for the best of both worlds
- Tune BM25 parameters k1 (term saturation, default 1.2-1.6) and b (length normalization, default 0.75) on your corpus
- BM25 works best with longer documents — for short text (titles, captions), embedding-based retrieval is often better

**Products/platforms:**
- **Elasticsearch:** Full-text search engine with BM25 implementation, widely used in production
- **OpenSearch:** Open-source fork of Elasticsearch with BM25 and k-NN vector search
- **Meilisearch:** Fast, typo-tolerant search engine with BM25-based ranking
- **Whoosh (Python):** Pure Python search library with BM25 — good for small-scale or embedded use
- **Apache Lucene:** Java library underlying Elasticsearch/OpenSearch — BM25 implementation

**Performance aspects:**
- BM25 retrieval: 1-10ms for most corpora (inverted index lookup) — faster than dense retrieval over the same corpus
- Index size: BM25 inverted index is typically 10-30% of the original document size — much smaller than embedding indexes
- No GPU required — runs efficiently on CPU
- BM25 degrades on long documents without length normalization (parameter b) — tune carefully

### Hybrid Search (Combining Dense and Sparse)

**What is it:** Fusion of dense (embedding-based) and sparse (BM25/keyword) retrieval results. The two sets of results are merged using a fusion algorithm (RRF — Reciprocal Rank Fusion or weighted combination) to produce a single ranked list. This compensates for each method's weaknesses: BM25 catches exact matches that embeddings may miss; embeddings catch semantic matches that BM25 cannot.

**When it is needed:** When your knowledge base contains both domain-specific terminology (requiring exact match) and varied user queries (requiring semantic understanding), or when retrieval recall is critical and you cannot afford to miss either type of match.

**Examples:**
- A medical literature search retrieves papers matching both the exact drug name "acetaminophen" and the semantic query "pain relief medication"
- A legal document system finds cases with both exact statute numbers and conceptually related legal principles
- An internal enterprise search across technical documentation (exact API names + conceptual feature descriptions)

**Best practices:**
- Use RRF (Reciprocal Rank Fusion) for combining results — it is simple, parameter-robust, and works well without tuning
- Set different top-k for each retriever — dense typically needs more candidates (50-100) than BM25 (20-50) for good fusion
- Normalize scores if using weighted combination — BM25 and cosine similarity have different scales
- Test fusion weight ratios on your data — a 50/50 split is a good starting point, but 70/30 or 30/70 may be optimal depending on your corpus
- Consider the latency budget — running two retrievers doubles retrieval time; run them in parallel

**Products/platforms:**
- **Weaviate:** Native hybrid search with built-in BM25 + vector fusion
- **Qdrant:** Supports hybrid search with custom fusion via shard-level query
- **Elasticsearch:** Combines text and k-NN search with RRF (available in Elasticsearch 8.8+)
- **Pinecone:** Sparse-dense support via Pinecone Inference for BM25-style sparse vectors
- **LangChain:** EnsembleRetriever for combining multiple retrievers with weights

**Performance aspects:**
- Hybrid search doubles retrieval latency — each retriever runs independently (parallelizable)
- Fusion overhead (RRF/weighted merge) is negligible (<1ms)
- Storage doubles: you need both a vector index and a BM25 inverted index
- Recall improvement from hybrid is typically 5-15% over a single retriever on standard benchmarks

### Re-Ranking Retrieved Documents

**What is it:** A second-stage ranking step that applies a more accurate (but slower) model to re-order the results from the initial retrieval. The initial retriever (bi-encoder) is fast but coarse; the re-ranker (cross-encoder) jointly encodes query+document for precise relevance scoring. Typically retrieves top-50, re-ranks top-10.

**When it is needed:** When the top-1 result from initial retrieval is not reliable enough, when precision matters more than raw speed (customer-facing answers, medical/legal applications), or when the initial retriever has moderate accuracy and a small boost in ordering significantly improves user experience.

**Examples:**
- A customer support system retrieves 50 potential FAQ matches, then re-ranks to show the single best match to the agent
- A research paper search retrieves 100 candidates with a bi-encoder, re-ranks top-20 with a cross-encoder for higher precision
- An e-commerce product search retrieves 200 products, re-ranks top-50 for the user-facing results page

**Best practices:**
- Use a lightweight cross-encoder (e.g., `ms-marco-MiniLM-L-12-v2`) for speed; use a larger model (`ms-marco-electra-base`) for accuracy
- Cache re-ranker results for frequently retrieved documents to avoid redundant computation
- Set the initial retrieval count high enough (50-100) that the re-ranker has sufficiently diverse candidates to re-order
- Consider two-stage re-ranking: first a fast cross-encoder, then an LLM-based re-ranker for the top-3-5

**Products/platforms:**
- **Cohere Rerank:** Managed re-ranking API with multilingual support
- **Cross-encoders (Sentence Transformers):** Open-source models for self-hosted re-ranking (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- **Jina AI Reranker:** Domain-specific re-ranking models
- **Voyage AI Rerank:** Re-ranking with support for long documents
- **LlamaIndex:** Postprocessor nodes for integrated re-ranking

**Performance aspects:**
- Re-ranking adds 50-200ms per query depending on the cross-encoder model size and number of candidates
- Cross-encoder inference cost scales linearly with the number of candidates — re-ranking 100 candidates costs ~100× a single forward pass
- Memory: cross-encoders are typically 100MB-500MB — can run on CPU for low throughput, GPU for high throughput
- Quality improvement from re-ranking is typically 10-20% MRR lift over bi-encoder alone

### Query Transformation (Rewriting, Decomposition, HyDE)

**What is it:** Techniques that modify the user's query before retrieval to improve the quality of retrieved documents. Query rewriting rephrases the query for better embedding alignment. Query decomposition splits complex multi-part questions into simpler sub-queries. HyDE (Hypothetical Document Embeddings) generates a hypothetical ideal document from the query and uses its embedding for retrieval, bridging the query-document vocabulary gap.

**When it is needed:** When user queries are ambiguous, poorly phrased, or use different terminology than the documents. Also when queries contain multiple distinct sub-questions that are best answered separately, or when the semantic gap between short queries and long documents is large.

**Examples:**
- A user asks "how do I do that thing with the settings?" — the rewriter expands to "How do I change privacy settings in the admin panel?"
- A user asks "What are the requirements and deadlines for the grant?" — decomposer splits to two sub-queries
- A user asks "Tell me about transformer architectures" — HyDE generates a hypothetical document about Transformers and uses its embedding to find structurally similar real documents

**Best practices:**
- Use a small, fast LLM for query transformation (GPT-4o-mini, Claude Haiku, Llama-3-8B) — the transformation task is simpler than answer generation
- Keep transformation in a separate step with its own latency budget — consider running it in parallel with the first retrieval pass
- For decomposition, merge sub-query responses in a final synthesis step rather than presenting sub-answers separately
- Cache query transformations — the same raw query should produce the same transformed query

**Products/platforms:**
- **LlamaIndex:** QueryTransformer modules (HyDEQueryTransform, DecomposeQueryTransform)
- **LangChain:** Query transformations via LLMChain with custom prompts
- **OpenAI GPT-4o-mini / Claude Haiku:** Cost-effective LLMs for query rewriting

**Performance aspects:**
- Query transformation adds 1 LLM call per query — 200-500ms with a small model, 1-3s with a large model
- HyDE generates ~50-100 tokens of hypothetical document — adds embedding latency for the hypothetical doc
- Decomposition multiplies retrieval calls: N sub-queries = N retrieval calls = N× retrieval latency
- Transformation quality depends on the LLM used — small models may produce weaker rewrites than large ones

### Context Window Management and Prompt Construction

**What is it:** The process of assembling retrieved documents into a prompt that fits within the LLM's context window, is structured for effective consumption, and includes appropriate instructions. This includes truncation strategies, ordering of chunks, and instruction design for citation and refusal behavior.

**When it is needed:** Every RAG system needs context management — retrieved chunks almost always exceed the available context budget, and unstructured concatenation of chunks leads to poor LLM performance.

**Examples:**
- A RAG system retrieves 20 chunks but only fits 8 in the 4K context window — selects the 8 most relevant and trims the rest
- Retrieved chunks are ordered by relevance score (highest first) so the LLM sees the most important context early
- The prompt instructs: "Answer using only the provided context. If the context is insufficient, say 'I cannot answer this question.' Cite the source ID for each claim."

**Best practices:**
- Allocate context budget: reserve ~20% for instructions/system prompt, ~10-20% for the response, and ~60-70% for retrieved chunks
- Order chunks by relevance descending — the LLM tends to weight early context more heavily (primacy bias)
- Include a "no answer" fallback explicitly in the prompt — do not let the LLM guess
- For streaming applications, design the prompt so the model can begin generating useful content before all context is available
- Use structured chunk formatting: source metadata (title, page) should precede each chunk to support citation

**Products/platforms:**
- **LlamaIndex:** Prompt helpers with automatic context window management and token budgeting
- **LangChain:** Context compression and document filtering via LLMChainExtractor
- **OpenAI / Anthropic:** Model-specific context windows (8K, 32K, 64K, 128K, 200K) — choose the model that matches your average context size

**Performance aspects:**
- Token budget: every 1K tokens of context costs ~$0.0015-0.01 (GPT-4) per query — optimize context size against retrieval value
- Longer context slows generation superlinearly — 32K context is 2-4× slower than 4K context for the same output length
- Chunk truncation (trimming from the bottom) discards the least relevant chunks — but may discard important context if relevance scoring is imperfect
- Streaming mitigation: begin generation as soon as the first relevant chunks are available, add more context as the response streams

### Evaluation of RAG Systems (Faithfulness, Relevance, Recall)

**What is it:** The practice of measuring RAG quality across multiple dimensions — retrieval quality (did we fetch the right documents?), groundedness (is the answer supported by the context?), and answer quality (is the answer correct and complete?). Evaluation requires ground-truth Q&A pairs, automated metrics, or LLM-as-a-judge.

**When it is needed:** Before deploying a RAG system to production, when comparing RAG variants, after any pipeline change (new chunking, new embedding model, new prompt), and continuously in production to detect drift.

**Examples:**
- A team creates 500 Q&A pairs from their knowledge base and measures recall@5 (94%) and faithfulness (97%) every week
- An automated pipeline runs nightly: samples 100 recent user queries, runs them through the RAG system, and uses GPT-4 to evaluate answer quality
- A/B test compares two chunking strategies: semantic chunking achieves 92% recall vs. 85% for fixed-size chunking

**Best practices:**
- Build a high-quality evaluation set of 100-500 Q&A pairs with ground-truth source documents — this is the single highest-leverage investment for RAG quality
- Evaluate retrieval and generation separately — retrieval recall@k tells you if the retriever is working; faithfulness tells you if the generator is using the context properly
- Use LLM-as-a-judge (GPT-4, Claude) for evaluating faithfulness and answer quality — correlation with human judgment is high (>0.8) for these dimensions
- Automate evaluation as a CI/CD step — every change to chunking, embedding, or prompt should be tested against the eval set before deployment
- Track evaluation metrics as a time series — sudden drops indicate regressions

**Products/platforms:**
- **RAGAS (RAG Assessment):** Open-source framework with metrics for faithfulness, answer relevance, context precision, and context recall
- **LlamaIndex Evaluation:** Built-in evaluators for retrieval and response quality
- **LangSmith:** Trace and evaluate RAG runs with annotation and comparison features
- **DeepEval:** Testing framework with RAG-specific metrics (faithfulness, hallucination, contextual recall)
- **TruLens:** Evaluation and tracking for LLM apps with RAG-specific feedback functions

**Performance aspects:**
- LLM-as-a-judge evaluation costs ~$0.01-0.05 per evaluation call — budget accordingly for large eval sets
- Automated evaluation is not perfect — periodically validate automated scores against human judgment (target >0.8 correlation)
- Evaluation adds latency to CI/CD — run full eval on merge, quick smoke test on every commit
- Metric interpretation requires context: a faithfulness score of 90% may be excellent in one domain but unacceptable in another

### Advanced RAG (Self-RAG, Corrective RAG, Agentic RAG)

**What is it:** Advanced RAG variants that add intelligence to the retrieval process — deciding when to retrieve (Self-RAG), evaluating and correcting retrieval quality (Corrective RAG), or using multi-step agentic reasoning to determine the optimal retrieval strategy (Agentic RAG). These variants address the limitations of single-pass RAG for complex queries.

**When it is needed:** When naive RAG fails on complex queries, when retrieval quality is inconsistent due to variable document quality, when you need the system to handle queries that span multiple knowledge domains, or when you need to reduce unnecessary retrieval calls.

**Examples:**
- Self-RAG: A chatbot retrieves documents only for factual queries ("What is the refund policy?") but answers general questions ("What's your name?") from parametric memory
- Corrective RAG: A medical Q&A system detects that retrieved documents are not relevant to the user's symptoms and retries with a broader query
- Agentic RAG: A research assistant planning a trip retrieves flight options from one tool, hotel availability from another, weather data from a third, and synthesizes the response

**Best practices:**
- Start with Naive RAG and add complexity incrementally — measure whether each additional layer actually improves quality
- Self-RAG requires fine-tuning the base model — only consider if you have the resources for fine-tuning
- Corrective RAG's relevance evaluator can be a simple classifier (not an LLM) — fine-tune a BERT model on your data for speed
- Agentic RAG benefits from structured tool definitions and clear delegation boundaries — define when each retrieval tool is appropriate

**Products/platforms:**
- **LangGraph:** Framework for building agentic RAG workflows with state graphs and conditional retrieval
- **Self-RAG (GitHub):** Fine-tuning recipe and model checkpoints for Self-RAG (Llama-2-7B/13B)
- **Corrective RAG (CRAG):** Reference implementation with retrieval evaluator and fallback strategies
- **CrewAI:** Multi-agent frameworks that can be adapted for agentic RAG workflows
- **AutoGen:** Microsoft's multi-agent conversation framework — agents can include retrieval tools

**Performance aspects:**
- Self-RAG: retrieval decisions add ~1-2 LLM calls per query (for reflection tokens) — latency varies depending on retrieval frequency
- Corrective RAG: evaluation + retry doubles the worst-case latency and can 2-3× cost if retries are common
- Agentic RAG: 5-30s latency typical due to multiple tool calls and reasoning steps
- All advanced variants are significantly harder to debug than Naive RAG — invest in tracing and logging

### Multi-Modal RAG (Text + Images + Tables)

**What is it:** Extending RAG to retrieve and process not just text but also images, tables, charts, diagrams, and other visual content. Documents are parsed into mixed-modal chunks. Retrieval uses multi-modal embeddings (CLIP, SigLIP) to find relevant visual content alongside text. The LLM must support multi-modal input (GPT-4o, Gemini, Claude 3.5) to consume both text and images.

**When it is needed:** When your knowledge base contains PDFs with diagrams, screenshots, or scanned content; when questions require understanding visual information (charts, graphs, UI screenshots, medical images); or when answers benefit from including visual evidence.

**Examples:**
- A manual for equipment repair retrieves the relevant diagram and text instructions together — the answer includes both a description and the annotated diagram
- A financial analysis system retrieves a specific chart showing revenue trends alongside the text paragraph explaining them
- A medical QA system retrieves radiology images and reports together to answer diagnostic questions

**Best practices:**
- Parse documents into mixed-modal chunks — preserve the relationship between images and their captions/references in the text
- Use OCR on scanned documents and images containing text — most PDFs contain embedded text but some are image-only
- Index images with descriptive text (caption, surrounding text, alt-text) to improve text-based retrieval of visual content
- Consider two-stage retrieval: first retrieve by text, then re-rank by visual similarity if needed
- Store image references rather than embedding the image directly into the LLM context — pass the actual image to multi-modal models

**Products/platforms:**
- **Unstructured.io:** Parses complex documents (PDFs, HTML, images) into structured elements with modality tagging
- **LlamaIndex:** Multi-modal RAG with CLIP embeddings and GPT-4o/Gemini integration
- **LangChain:** Multi-modal retrievers and document loaders for mixed content
- **Byaldi (ColPali):** Vision-language model for end-to-end multi-modal retrieval from PDFs
- **ColBERT + ColPali:** Late-interaction models for multi-modal retrieval

**Performance aspects:**
- Multi-modal embedding generation is 2-5× slower than text-only (larger models, image preprocessing)
- Image storage: a single image at 512×512 is ~0.5-1MB — storage costs are significantly higher than text
- Multi-modal LLMs (GPT-4o) cost 2-10× more per token than text-only models
- Latency: processing both text and image context in the LLM is slower due to vision encoding (1-3s extra)

### Production RAG Pipelines (Ingestion, Indexing, Serving)

**What is it:** The end-to-end infrastructure for operating RAG in production: a data ingestion pipeline that processes and chunks documents, an indexing pipeline that embeds and stores chunks in a vector database, and a serving pipeline that handles query-time retrieval and generation. Includes monitoring, scaling, updating, and disaster recovery.

**When it is needed:** When a RAG system moves beyond prototyping and must serve real users reliably at scale. Production pipelines address data freshness, scalability, error handling, and observability — all concerns that do not exist in a notebook or demo.

**Examples:**
- A daily ingestion pipeline processes 10K new documents each night: parse → chunk → embed → index. A CDC (Change Data Capture) pipeline handles real-time updates for documents changed during the day
- A serving pipeline uses a load-balanced pool of 4 application servers, each connecting to a Redis cache and a Qdrant cluster, with horizontal scaling based on QPS
- A monitoring stack tracks ingestion lag, index size, query latency p50/p99, and error rates on a Grafana dashboard with PagerDuty alerts

**Best practices:**
- Decouple ingestion and serving — ingestion failures should not affect query availability (serve from a stale index while rebuilding)
- Implement idempotent ingestion — running the same document through the pipeline twice should produce the same result (upsert by document ID)
- Use document versioning — track which version of each document is in the index and re-index only when the document changes
- Set up staging and production indexes — build and validate a new index in staging before swapping it into production
- Implement circuit breakers for downstream dependencies — if the vector DB is slow, serve degraded responses (no retrieval, just LLM) rather than timing out

**Products/platforms:**
- **Apache Airflow / Prefect:** Orchestration for scheduled ingestion pipelines
- **dlt (data load tool):** Open-source framework for building ingestion pipelines with versioning and incremental loading
- **LlamaIndex:** Ingestion pipeline with document management and incremental indexing
- **Unstructured.io:** Production document parsing and chunking API
- **Kubernetes + Helm:** Container orchestration for scalable RAG serving
- **Terraform / Pulumi:** Infrastructure-as-code for vector DB clusters, application servers, and caches

**Performance aspects:**
- Ingestion throughput: embedding generation is typically the bottleneck — batch encoding (32-256 documents per batch) maximizes throughput
- Index build time for a 10M-vector HNSW index: 2-6 hours on a single GPU node — plan for incremental updates or use IVF for faster builds
- Serving scalability: vector DB queries scale horizontally with replicas; LLM calls are the throughput bottleneck — cache aggressively
- Cold start: first query after index rebuild requires loading the index into memory — allocate 30-60s for warm-up
- Cost allocation at production scale: LLM calls typically account for 60-80% of total cost, vector DB 10-20%, infrastructure 10-20%
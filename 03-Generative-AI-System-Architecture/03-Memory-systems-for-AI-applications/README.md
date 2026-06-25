# Memory Systems for AI Applications

Memory architectures that enable AI systems to maintain context and learn from interactions.

## Key Topics

### Conversational Memory

**Definition:** The mechanism by which an AI system retains and recalls the history of a conversation to maintain coherent, context-aware dialogue. Implementations range from simple sliding windows (keeping the last N turns) to intelligent summarization that compresses older exchanges.

**Example:** A customer support chatbot keeps the last 20 messages in a sliding window. When the user says "as I mentioned earlier," the model can reference the earlier turn still in context. For long sessions, a summarization-based system periodically condenses the conversation: "User reported a billing issue with invoice #1042, agent suggested a refund."

**Best Practices:**
- Use a sliding window of 10-30 recent turns for short conversations — balances relevance with token budget
- Implement summarization for long sessions — regenerate the summary every N turns to keep it fresh
- Store conversation metadata (user ID, session ID, timestamps) alongside message content for traceability
- Combine window + summary: keep recent messages verbatim and summarize older ones into a system prompt

**Performance Considerations:**
- Sliding window is O(1) per turn — constant time, no additional latency
- Summarization requires an LLM call every N turns — adds latency proportional to the summary prompt length
- Token usage grows with window size — monitor cost; a 30-turn window with long responses may consume 4K+ tokens per turn
- Summarization trades off recall fidelity for token efficiency — important details may be lost in compression

### Episodic Memory

**Definition:** Storage and retrieval of specific past events, interactions, or experiences, enabling the AI to recall what happened in previous sessions or earlier in the current session. Each episode is typically stored as structured data with timestamps and context.

**Example:** A personal AI assistant remembers that "On Monday the user mentioned they were traveling to Tokyo for a conference." In a later session, when the user says "remind me about my trip next week," the assistant retrieves the episode and provides details about the Tokyo conference.

**Best Practices:**
- Store episodes with rich metadata (timestamp, session ID, importance score, topic tags) for efficient retrieval
- Use importance scoring to prioritize which episodes survive memory consolidation — not every interaction is worth keeping
- Implement decay mechanisms — older or less-accessed episodes are archived or deleted
- Normalize episode format across sessions to enable cross-session retrieval

**Performance Considerations:**
- Retrieval latency depends on the storage backend — in-memory is sub-millisecond, database queries add 5-50ms
- Embedding-based episodic retrieval requires a vector similarity search — budget 10-100ms per query depending on index size
- Storage grows linearly with interactions — implement consolidation policies to prevent unbounded growth
- Frequent writes (every user turn) can become a bottleneck — batch writes or async insertion helps

### Semantic Memory

**Definition:** Long-term storage of general knowledge, facts, and conceptual relationships that the AI system maintains across all users and sessions. Unlike episodic memory (specific events), semantic memory stores structured, reusable knowledge.

**Example:** A medical AI assistant maintains a semantic memory of drug interactions: "Warfarin and aspirin increase bleeding risk." This fact is stored once and retrieved whenever either drug is mentioned, regardless of which patient or session.

**Best Practices:**
- Use a structured knowledge base (triples, property graph, or vector store) rather than unstructured text
- Implement versioning for knowledge updates — facts can change (e.g., updated drug guidelines)
- Separate semantic memory by domain or topic for targeted retrieval and reduced noise
- Regularly audit and prune outdated or contradictory information

**Performance Considerations:**
- Graph-based semantic memory: traversal queries are proportional to graph depth (typically 1-10ms)
- Vector-based retrieval: latency scales with the index size — HNSW indexing provides O(log n) search
- Large semantic stores (millions of facts) benefit from sharding by domain
- Write throughput for updating semantic knowledge is typically low (infrequent updates) — not a bottleneck

### Vector-Based Memory Retrieval

**Definition:** Encoding memory entries as dense vector embeddings and retrieving the most relevant ones via similarity search (cosine similarity, dot product, or Euclidean distance) in a vector index.

**Example:** A RAG-based QA system stores every answered question-answer pair as an embedding. When a new query arrives ("What's the return policy for electronics?"), it embeds the query and retrieves the top-3 most similar past Q&A pairs to provide context to the LLM.

**Best Practices:**
- Choose the embedding model carefully — the retrieval quality depends on embedding quality
- Use metadata filtering alongside vector search (e.g., "only retrieve from documents dated after 2024") for precision
- Tune the similarity threshold — too low returns noise, too high misses relevant results
- Re-index periodically when adding many new entries to maintain performance

**Performance Considerations:**
- Embedding generation latency: 10-200ms per query depending on model size and hardware
- ANN (Approximate Nearest Neighbor) search: 1-20ms for HNSW with 100K-1M vectors
- Memory usage grows with index size — each 768-dim float32 vector consumes ~3KB
- Tradeoff between recall and latency: higher ef_search (HNSW) improves recall but increases query time

### Memory Compression and Summarization

**Definition:** Techniques to reduce the size of stored memories while preserving the most salient information, typically using LLM-based summarization or lossy compression of conversation logs.

**Example:** After 50 turns of a customer service conversation, the system compresses the exchange into a structured summary: "Customer: Jane Doe. Issue: Billing overcharge for plan Premium ($129 instead of $99). Resolution: Refund of $30 issued, case #CS-4821. Sentiment: Frustrated initially, satisfied at close."

**Best Practices:**
- Compress when a conversation exceeds a token threshold (e.g., 4K tokens of raw history)
- Use structured summarization templates (issue, resolution, sentiment) for consistent output
- Preserve critical metadata (timestamps, IDs, action items) that the AI needs to act on
- Store both the summary and a reference to the raw log for audit trails

**Performance Considerations:**
- LLM summarization costs scale with input length — summarizing 4K tokens costs ~1-2K output tokens
- Compression ratio typically 5:1 to 10:1 — a 4K token conversation compresses to 400-800 tokens
- Frequent summarization (every 10 turns) adds constant LLM overhead; batch summarization (every 50 turns) is more efficient
- Lossy compression means some details are permanently lost — choose what to prioritize based on use case

### Long-Term vs. Short-Term Memory

**Definition:** Short-term memory holds recent context (current session, last N interactions) with fast access but limited capacity. Long-term memory persists across sessions with high capacity but slower retrieval, storing important historical information.

**Example:** A coding assistant uses short-term memory to remember the last 15 files the user edited in this session. Long-term memory stores the user's preferred coding style (e.g., "uses tabs, prefers descriptive variable names, follows PEP 8") across all sessions.

**Best Practices:**
- Design a clear promotion policy: short-term → long-term transition based on importance, frequency, or explicit user instruction
- Set a fixed capacity for short-term memory (e.g., 20 turns or 4K tokens) with FIFO eviction
- Implement a consolidation cron job that periodically reviews short-term entries and promotes valuable ones
- Use tiered storage: in-memory for short-term, persistent DB for long-term

**Performance Considerations:**
- Short-term memory access is O(1) — negligible latency
- Long-term memory retrieval adds 10-100ms depending on the backend (vector DB, SQL, or key-value store)
- Short-term memory uses RAM — keep it under 10MB per session for scalability
- Data transfer between tiers (short→long) should be async to avoid blocking the user response

### Memory Persistence

**Definition:** The storage backend and strategy for persisting memory data — whether in-memory (ephemeral), file-based (simple persistence), or database-backed (production-grade durability and querying).

**Example:** A production AI customer service system persists conversation memory to PostgreSQL. Each session's memory is stored as JSONB with an index on session_id and timestamp. In-memory caching (Redis) provides sub-millisecond access for active sessions, with periodic flush to Postgres.

**Best Practices:**
- Match backend to durability requirements: in-memory for cache, database for persistent storage
- Use a proven database (Postgres, Redis, SQLite) rather than rolling custom file-based persistence
- Implement TTL (time-to-live) policies to auto-expire stale memory entries
- Encrypt persisted memory at rest (AES-256) and in transit (TLS) for sensitive data

**Performance Considerations:**
- In-memory: sub-millisecond reads/writes, but lost on restart
- SQLite: fast for single-server (1-5ms), but write-contention under concurrent access
- PostgreSQL: 1-10ms typical, supports concurrent writes, billions of rows
- Redis: sub-millisecond, built-in TTL, but RAM-bound — expensive at scale
- Hybrid tier (Redis + Postgres) adds 5-20ms for each write-through but provides durability

### Memory-Augmented Neural Networks

**Definition:** Neural network architectures with explicit, differentiable external memory that can be read from and written to, enabling the network to learn algorithms and store information beyond what is captured in weights alone.

**Example:** Neural Turing Machines (NTM) and Differentiable Neural Computers (DNC) extend RNNs with an external memory matrix and attention-based read/write heads. Used for tasks like graph reasoning, sorting, and copying long sequences beyond standard RNN capacity.

**Best Practices:**
- Consider simpler alternatives (RAG, vector stores) before memory-augmented NNs — they are complex to train
- Use sparsity and addressing mechanisms to keep memory operations computationally tractable
- Combine with standard attention for content-based and location-based addressing
- Memory size should be matched to the task — too small limits capacity, too large wastes computation

**Performance Considerations:**
- Memory operations add O(M) complexity per step where M is memory size — large M is expensive
- Training memory-augmented networks is unstable — requires careful hyperparameter tuning
- Inference is slower than standard architectures due to read/write head operations
- Modern approaches (Transformer with KV cache, Retrieval-Enhanced Transformers) often outperform classic MANNs

### External Memory Stores (Redis, SQLite, Postgres)

**Definition:** Purpose-built databases used as the persistence layer for AI memory systems, chosen for their specific performance characteristics and query capabilities.

**Example:** An AI travel planner uses Redis for active session memory (current itinerary, recent searches), PostgreSQL for long-term user preferences (favorite airlines, dietary restrictions, past trips), and SQLite for local edge deployment when offline.

**Best Practices:**
- Use Redis for high-throughput, low-latency session memory with TTL-based expiration
- Use PostgreSQL for ACID-guaranteed persistent memory with complex queries (e.g., "all memories from last month")
- Use SQLite for embedded/mobile deployments where a separate database server is impractical
- Avoid mixing query patterns that mismatch the database strength — don't run complex joins in Redis

**Performance Considerations:**

| Store | Read Latency | Write Throughput | Max Data | Best For |
|---|---|---|---|---|
| Redis | <1ms | 100K+/s | RAM-bound | Session cache, hot memory |
| SQLite | 1-5ms | 10K-50K/s | 100s GB | Embedded, single-server |
| PostgreSQL | 1-10ms | 5K-50K/s | TBs | Production, multi-server |

- Connection pooling critical for Postgres and Redis under high concurrency
- Data serialization/deserialization (JSON, Pickle, Protobuf) adds overhead — measure and optimize

### Memory Pruning and Consolidation Strategies

**Definition:** Policies that remove, merge, or archive old or low-value memories to prevent unbounded storage growth and maintain retrieval quality.

**Example:** A daily consolidation job reviews all memories from the past week. Memories with importance score < 0.3 are deleted. Related memories (e.g., three separate notes about "project deadline") are merged into a single consolidated entry. Memories older than 90 days are archived to cold storage.

**Best Practices:**
- Define an importance scoring function (recency, frequency, user-flagged, contextual relevance)
- Implement tiered retention: hot (active, 0 cost), warm (recent, cheap), cold (old, expensive storage)
- Run consolidation as a background batch job — never inline during user-facing requests
- Allow user control: provide explicit "remember this" / "forget this" commands
- Log all pruning decisions for auditability and potential undo

**Performance Considerations:**
- Batch consolidation jobs should run during low-traffic periods (e.g., every 6-24 hours)
- Merging entries requires re-embedding — budget LLM and embedding API costs
- Pruning scan complexity scales with table size — use indexed importance_score column for efficient queries
- Archive to cheaper storage (S3, blob storage) reduces database costs but adds 100ms-1s recall latency for archived items

### Multi-Session and Cross-Session Memory

**Definition:** Memory systems that recognize users across multiple sessions and can retrieve and apply information from past sessions to improve the current interaction.

**Example:** A fitness AI coach remembers that in Session 1 the user set a goal of "run 5K in under 30 minutes." In Session 3, when the user asks "how am I progressing?", the coach retrieves previous session logs, compares times, and responds: "You've improved from 32:15 to 31:02 — 73 seconds off your 5K time since last month."

**Best Practices:**
- Always confirm user identity (auth token, session cookie, or explicit login) before cross-session retrieval
- Surface cross-session memories explicitly: "From our last conversation on Tuesday, I see you were researching Python libraries for data analysis"
- Let users control cross-session memory: opt-in by default for utility, with clear deletion options
- Anonymize or aggregate memories when sharing across sessions for analytics

**Performance Considerations:**
- Cross-session lookup latency: 10-50ms with indexed user_id in PostgreSQL
- Embedding cross-session memories increases vector index size proportionally to the number of sessions
- Session stitching (matching anonymous sessions to a known user) adds complexity and potential privacy concerns
- Cache recent user's memory metadata in Redis for fast cross-session warm-start

### Privacy and Memory Management

**Definition:** Policies, techniques, and safeguards for handling user data stored in memory systems, including data retention, user consent, anonymization, and compliance with regulations (GDPR, CCPA, SOC 2).

**Example:** A therapy chatbot allows users to view, export, or delete their entire memory store at any time via a privacy dashboard. Memories are automatically deleted after 12 months of inactivity. All memory data is encrypted at rest and in transit. The system never shares cross-user memories.

**Best Practices:**
- Implement the right to be forgotten — expose an API endpoint for complete memory deletion
- Encrypt all memory data at rest (AES-256-GCM) and in transit (TLS 1.3)
- Minimize PII in memory storage — store references to PII rather than raw PII where possible
- Provide a user-facing privacy dashboard showing what is stored, for how long, and why
- Document data retention policies clearly and enforce them programmatically (cron jobs for TTL enforcement)
- Conduct regular privacy audits — review stored data samples for accidental PII collection

**Performance Considerations:**
- Encryption/decryption adds 1-5ms per memory operation (negligible for most use cases)
- Bulk deletion (right to be forgotten) on large datasets requires careful indexing to avoid long table locks
- Audit logging adds storage overhead — budget ~100 bytes per memory operation
- Data export in standard formats (JSON, CSV) may require streaming for large memory stores to avoid OOM
- PII scrubbing at write time is cheaper than at read time — filter PII before persisting

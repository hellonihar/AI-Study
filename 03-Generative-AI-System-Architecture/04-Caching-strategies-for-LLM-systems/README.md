# Caching Strategies for LLM Systems

Techniques to reduce latency, save costs, and improve throughput in LLM-powered applications.

## Why Caching Matters for AI Applications

LLM inference is expensive — both in latency (seconds per response) and cost ($ per token). A single GPT-4 call generating 500 tokens costs ~$0.03 and takes 2-5 seconds. At scale, repeated identical or similar queries compound this cost exponentially. Caching eliminates redundant computation by storing and reusing previous LLM responses or intermediate computation results.

### Where Caching Saves

| Resource | Without Cache | With Cache | Savings |
|---|---|---|---|
| **Latency** | 2-10s per LLM call | <50ms cache hit | 40-200× faster |
| **Cost** | $0.01-0.10 per query | ~$0.00001 per cache lookup | 100-10,000× cheaper |
| **Throughput** | 10-100 RPM per model | 10,000+ RPM from cache | 100-1000× higher |
| **Rate limits** | Constrained by API limits | Bypasses API entirely | Eliminates throttling |

### When to Cache (and When Not To)

**Cache aggressively when:**
- Queries have high repetition (FAQ, documentation lookup, code snippets)
- Response freshness is not critical (summaries, translations, explanations)
- The same prompt reaches many users (shared system prompts, few-shot templates)
- Latency SLAs are tight (< 500ms) and LLM calls cannot meet them

**Avoid caching when:**
- Responses must be real-time (stock prices, live sports scores)
- Each query is truly unique (creative writing, brainstorming)
- Personalization changes per user (user-specific recommendations)
- Legal/compliance requires fresh responses (medical advice, financial compliance)

### Real-World Examples

**Example 1: Customer Support Chatbot**
A support chatbot receives 10K queries/day. ~30% are repetitive ("How do I reset my password?", "What are your business hours?"). An exact-match response cache handles these in <10ms, saving 3K LLM calls/day — $90/day at $0.03/call → ~$32K/year.

**Example 2: Code Generation Assistant**
A code completion tool sees similar requests across users ("Write a Python function to sort a list of dictionaries"). A semantic cache groups paraphrased requests (e.g., "sort list of dicts by key" vs "order list of dictionaries by field") and returns cached results, achieving 45% hit rate. Average response time drops from 3s to 20ms.

**Example 3: Document Summarization Service**
A news aggregator summarizes the same article for thousands of users. An exact-match cache on article URL prevents duplicate summarization across users. Cache hit rate: 80%+ for popular articles. Cost reduction: 5× on infrastructure spend.

**Example 4: Multi-turn Agentic Workflow**
An AI agent calls the same tools and LLMs repeatedly during a multi-step reasoning loop. KV caching across sequential calls within the same session avoids recomputing attention for shared prefix tokens, cutting per-step latency from 2s to 300ms.

## Products and Platforms

### Caching Products / Platforms

| Product | Type | Key Strength | Limitations |
|---|---|---|---|
| **Redis** | In-memory KV store | Sub-millisecond latency, rich eviction policies (LRU, LFU, TTL), pub/sub for invalidation | RAM-bound — expensive at scale; no native semantic caching |
| **Redis Stack** | Redis + modules | RediSearch for full-text + vector search enabling semantic caching | Adds complexity over plain Redis; vector search is newer and less battle-tested |
| **Memcached** | Distributed memory cache | Simple, fast, battle-tested at massive scale (Facebook, YouTube) | No persistence, no eviction variety (LRU only), no native data structures beyond strings |
| **Valkey** | Redis OSS fork | Drop-in Redis replacement, open-source maintained by Linux Foundation | Smaller ecosystem than Redis; fewer client libraries and tools |
| **SQLite** | Embedded DB | Zero-config, good for single-server/edge caching, persistent | No built-in eviction, no distributed support, slower at scale |
| **PostgreSQL + pgvector** | Relational DB with vector | Hybrid cache (exact + semantic via embeddings), ACID, persistent | Heavier than dedicated cache; read throughput limited compared to Redis |
| **Cloud CDN (Cloudflare, Fastly, Akamai)** | Edge cache | Global distribution, cached response in <5ms at edge; offloads origin entirely | TTL-based only; no semantic cache; purge propagation takes seconds |
| **GPTCache** | LLM-specific cache | Built for LLM: semantic cache, embedding-based similarity, multiple backends (Redis, SQLite) | Less mature ecosystem; limited production deployments at scale |
| **LangChain Cache** | Framework-level cache | Easy integration with LangChain chains/agents; supports multiple backends | Framework lock-in; less flexible for custom caching logic |
| **vLLM (KV Cache)** | LLM inference engine | Automatic KV cache management during batch inference; PagedAttention for memory efficiency | Only works with vLLM-served models; does not cache across requests |
| **Semantic Cache (custom)** | Application-level | Domain-tuned similarity thresholds; full control over invalidation logic | Requires development and maintenance effort; embedding costs add overhead |

### Comparison Matrix

| Feature | Redis | GPTCache | vLLM KV Cache | Cloud CDN | SQLite |
|---|---|---|---|---|---|
| **Cache type** | Exact key-value | Semantic + exact | KV (attention) | Full response | Exact |
| **Latency** | <1ms | 5-30ms | N/A (in-process) | <5ms edge | 1-5ms |
| **Persistence** | Optional (RDB/AOF) | Depends on backend | None | None | Yes |
| **Distributed** | Yes (cluster) | Yes | Single node | Yes (global) | No |
| **Eviction policies** | LRU, LFU, TTL, random | LRU, TTL | N/A | TTL | Custom |
| **Best scale** | Up to ~100GB RAM | Up to DB backend | up to 80K tokens/model | Unlimited (CDN) | <10GB |
| **Cost** | $0-$$$ (self-hosted/cloud) | Free (OSS) | Free (OSS) | $-$$$ | Free |

## Design Guidelines

### Cache Architecture Patterns

**Pattern 1: Write-Through** — Cache is updated synchronously on every LLM response. Ensures cache is always fresh but adds write latency to every request. Best for read-heavy workloads with moderate write volume.

**Pattern 2: Write-Behind** — Cache is updated asynchronously via a queue. Responses are written to a buffer and flushed periodically. Reduces write latency but risks serving stale data if the consumer falls behind.

**Pattern 3: Cache-Aside (Lazy Loading)** — Application checks cache first; on miss, calls LLM and populates cache. Most common pattern. Simple, resilient, but first request for any key always misses.

**Pattern 4: Refresh-Ahead** — Cache proactively refreshes entries before they expire based on access predictions. Reduces miss rate for popular keys but requires prediction logic and can waste resources on speculative refreshes.

### Key Design Decisions

1. **Exact vs. semantic cache:** Exact is simple and fast (<1ms) but only matches identical queries. Semantic cache generalizes across paraphrases but adds embedding cost (10-200ms) and similarity search overhead. Use exact for high-volume, deterministic queries; add semantic for long-tail diversity.

2. **Cache granularity:** Cache full responses (highest savings, lowest flexibility) vs. intermediate results (lower savings, composable). For agent workflows, caching tool call results or retrieval outputs can be more reusable than caching the final LLM response.

3. **TTL strategy:** Short TTL (minutes) for dynamic content; long TTL (hours-days) for stable knowledge; no TTL for immutable reference data. Never use infinite TTL — data drifts, and manual invalidation is unreliable.

4. **Cache key design:** Include all dimensions that affect response correctness: model name, temperature, system prompt, user prompt, max_tokens, and any metadata. Missing a parameter can serve a response generated under different conditions — a 2x difference in correctness.

### Cache Invalidation Strategies

| Strategy | Mechanism | Best For | Risk |
|---|---|---|---|
| **TTL-based** | Automatic expiry after fixed time | Content that degrades predictably | Stale data within TTL window |
| **Event-driven** | Invalidate on data change (webhook, CDC) | Dynamic data (prices, inventory) | Missed events lead to staleness |
| **Version-based** | Bump cache version on deployment | Model or prompt updates | Requires coordinated version rollout |
| **Manual purge** | Admin-triggered invalidation | Emergency content corrections | Human error or delay |
| **Write-through** | Invalidate on every update | High-consistency requirements | Write amplification |

## Best Practices

### Operational Best Practices

- **Measure before caching.** Instrument your application to understand repeat query rates, token costs, and latency distribution. Cache is an optimization — optimize what matters.
- **Set a cache budget.** Decide maximum memory/disk for cache and enforce it with eviction policies. Runaway cache growth is a common production incident.
- **Implement cache degradation gracefully.** When cache backend is down, fall through to the LLM — never block the user on a cache failure. Use circuit breakers for misbehaving cache clusters.
- **Monitor cache health.** Track: hit rate, miss rate, stale serve rate, eviction rate, average/max memory usage, and cache backend latency (p50/p99).
- **Test cache correctness.** Unit test that cache keys include all relevant parameters. Integration test that cached responses are semantically identical to fresh ones.
- **Version your cache.** When you update your system prompt or model, old cache entries are invalid. Include a cache version in the key or use a global version namespace.

### Caching Prompt Templates and Shared Prefixes

- Cache rendered system prompts keyed by template hash + variables — avoids re-rendering on every request
- Pre-compute embeddings for common queries during off-peak hours and load into cache
- For few-shot examples, cache the full prompt prefix so only the user's query is appended at runtime

### Cost Optimization via Caching

- Calculate cache ROI: (misses_saved × cost_per_miss) − (cache_infra_cost + embedding_cost). Typical ROI is 3-10× for chat applications
- Prioritize caching expensive model calls (GPT-4, Claude Opus) over cheap ones (GPT-3.5, Haiku) — the savings ratio is higher
- Use semantic caching with similarity threshold tuning — a 0.95 threshold catches near-duplicates while keeping precision high
- Cache for the hottest 20% of queries often covers 80%+ of volume (Pareto principle)

## Performance Considerations

### Latency Breakdown

| Cache Operation | Typical Latency | Dominant Factor |
|---|---|---|
| Exact key lookup (Redis) | <1ms | Network round-trip |
| Semantic encode + search | 15-50ms | Embedding model + ANN search |
| Cache miss → LLM call | 2-10s | Model inference |
| Cache hit → return | <50ms (exact), 15-60ms (semantic) | Lookup + deserialization |

### Scaling Considerations

- **Read throughput:** Redis single node handles ~100K ops/s; cluster mode scales to millions. Memcached similarly. Higher throughput requires more nodes or sharding.
- **Write throughput:** Writes are typically 5-20% of reads in cache workloads. Ensure write load does not starve read capacity — use dedicated writer nodes if needed.
- **Memory:** 1M cached responses at ~4KB each = 4GB. Estimate your working set and provision 1.5-2× headroom for index structures and eviction overhead.
- **Network:** Cache adds one network hop. Keep cache co-located in the same region/availability zone as your application to keep latency <1ms. Cross-region cache adds 20-100ms — avoid.
- **Serialization overhead:** JSON serialization adds 0.1-0.5ms for typical responses. Use binary formats (MessagePack, Protocol Buffers) for large payloads or high throughput.

### Cache Performance Trade-offs

| Trade-off | Favor Latency | Favor Freshness |
|---|---|---|
| TTL | Long TTL (hours) | Short TTL (seconds) |
| Semantic threshold | Lower threshold = more hits, more stale | Higher threshold = fewer hits, more accurate |
| Eviction policy | LFU (keep popular, hot data) | LRU (remove old, potentially stale) |
| Pre-computation | Cache everything preemptively | Cache on-demand only |
| Cache tier | In-memory only | In-memory + disk + verification |

## Key Topics

### Response Caching (Exact Match, Prefix Match)

**Example:** A FAQ chatbot caches responses keyed by `hash(md5(prompt + model + temperature))`. The query "What is your return policy?" hits the exact cache in <1ms. A prefix-match cache stores common beginnings ("How do I...", "Tell me about...") and serves cached completions for any query starting with that prefix.

**Design Guidelines:**
- Use exact match for deterministic queries where identical input always expects identical output
- Use prefix match only when the prefix dominates the response meaning and the suffix is irrelevant
- Include all LLM parameters (model, temperature, max_tokens, system_prompt) in the cache key — omitting any risks incorrect cached responses
- Hash the cache key for fixed-length lookups instead of storing raw strings

**Performance Considerations:**
- Exact match: <1ms lookup with Redis or in-memory dictionary — the fastest cache type
- Prefix match: requires trie or sorted-set traversal — 1-5ms depending on prefix length and index size
- Hash collision risk is negligible with SHA-256 but use full hash (not truncated) for safety
- Storage: each cached response costs key_size + value_size + overhead (~100 bytes). A 1M-entry cache with 4KB responses ≈ 4GB

### Semantic Caching (Embedding-Based Cache Lookup)

**Example:** A code assistant caches responses with embedding-based similarity. The query "write a python script to download files from ftp" hits the cache even though the original cached query was "python ftp file downloader script" — because their embeddings are 0.94 similar (above the 0.92 threshold).

**Design Guidelines:**
- Choose the similarity threshold carefully: 0.95+ for high-precision (low false positives), 0.85-0.90 for high-recall (more hits, some false positives)
- Normalize embeddings to unit length and use cosine similarity for consistent thresholding
- Combine semantic + exact cache: check exact first (fast), fall back to semantic (slower), then LLM (slowest)
- Periodically re-evaluate the threshold — embedding models change, and query distribution shifts over time

**Performance Considerations:**
- Embedding generation: 10-200ms per query — the bottleneck of semantic caching
- Vector search: 2-20ms depending on cache size and index type (HNSW recommended for >10K entries)
- Total semantic cache lookup: 15-50ms — still 40-200× faster than an LLM call
- Storage: each entry stores embedding (768-3072 floats ≈ 3-12KB) + response — 2-4× more storage than exact cache
- Cache miss that still required an embedding call wastes the embedding cost — mitigate by checking cheaper exact cache first

### Key-Value Cache for LLM Inference (KV Cache)

**Example:** During multi-turn chat with an LLM, each new token attends to all previous tokens. The KV cache stores the Key and Value matrices from previous attention computations. Instead of recomputing them for the entire sequence on each new token, the model appends only the new token's K,V — reducing per-token computation from O(n²·d) to O(n·d).

**Design Guidelines:**
- KV cache is managed by the inference engine (vLLM, TensorRT-LLM, llama.cpp) — most teams don't implement it manually
- Monitor KV cache memory usage — it grows linearly with sequence length and can OOM the GPU on long contexts
- Use PagedAttention (vLLM) to manage KV cache fragmentation — non-contiguous memory blocks reduce waste
- For very long contexts (>32K tokens), consider KV cache offloading to CPU or disk — trades latency for memory

**Performance Considerations:**
- KV cache for a 7B model at 4K context: ~2GB GPU memory; at 32K context: ~16GB
- Shared prefix KV cache: if multiple requests share a prompt prefix, cache the prefix KV once and reuse — saves 30-60% of compute in agent workflows
- Batch inference shares KV cache across sequences in the same batch — improves GPU utilization
- KV cache is ephemeral (per-request) and does not persist across requests — it is not a traditional cache for cost savings

### Shared Prompt Caching (System Prompt, Few-Shot Examples)

**Example:** A translation app serves 50K requests/day with the same system prompt "You are a professional translator. Translate the following text to French." The system prompt is cached and prepended only once per batch. Few-shot examples ("English: Hello → French: Bonjour", etc.) are also pre-cached.

**Design Guidelines:**
- Cache rendered system prompts separately from user queries — assemble them at request time from cached parts
- Use prompt template versioning — when you update instructions, old cached prompts become stale
- For few-shot caches, pre-compute and store the encoded K,V of example pairs to avoid reprocessing
- Consider prompt compression techniques to reduce the shared prefix size and improve cache efficiency

**Performance Considerations:**
- Shared prompt caching reduces per-request compute by 20-60% depending on the prompt-to-response ratio
- With inference engines supporting prefix caching (vLLM, TGI), the shared prompt is processed once per batch — all requests in the batch reuse the cached prefix
- Storage overhead is minimal — cached prompts are a few KB each
- The benefit decreases as user query length increases — short queries benefit most

### Cache Eviction Policies (LRU, LFU, TTL)

**Example:** A news summarization cache uses LFU with TTL=1 hour. Popular breaking news articles get cached and hit frequently within the hour. After 1 hour, the cache entry expires automatically, and the next request fetches a fresh summary reflecting any developments.

**Design Guidelines:**
- Use LRU (Least Recently Used) when access patterns have temporal locality — recently accessed items are likely to be accessed again
- Use LFU (Least Frequently Used) when some items are consistently popular while others are accessed once — prevents cache pollution from one-hit-wonders
- Use TTL (Time-To-Live) as a primary eviction when data freshness has a hard deadline — always combine with LRU or LFU as secondary eviction
- Never rely on a single eviction policy — combine TTL + LRU or TTL + LFU for production systems
- Set a maxmemory limit and eviction policy on Redis — prevents OOM

**Performance Considerations:**
- LRU: O(1) with a doubly-linked list + hash map — Redis implementation is highly optimized
- LFU: O(log n) with a min-heap, or approximated with a counter (Redis, approximate LFU) — slightly more overhead than LRU
- TTL scanning: Redis scans 20 random keys every 100ms; for large datasets with many expiring keys, this can stall briefly
- Eviction itself is cheap (<1μs per key) but eviction storms (bulk expiry of many keys simultaneously) can spike latency

### Distributed Caching (Redis, Memcached)

**Example:** A global AI application with instances in us-east, eu-west, and ap-southeast uses Redis Cluster with 6 nodes (3 master, 3 replica). Cache writes go to the local master node; reads can come from any replica. Cache entries are consistent across the cluster via asynchronous replication.

**Design Guidelines:**
- Use Redis Cluster for automatic sharding and failover — do not implement client-side sharding manually
- Keep cache co-located with application instances (same region, same AZ) to minimize network latency
- Design for cache node failure — each cache miss is just a slower response, not an error
- Use read replicas for scaling read throughput but accept slightly stale data (asynchronous replication)
- Avoid large cache values (>1MB) in distributed caches — they cause network fragmentation and slow serialization

**Performance Considerations:**
- Redis Cluster: linear read throughput scaling with node count; write throughput limited by the node owning the key hash slot
- Network round-trip between app and cache: 0.3-1ms same-AZ, 1-5ms same-region, 20-100ms cross-region
- Serialization/deserialization of complex objects adds 0.1-1ms — use lightweight serialization (MessagePack, Protobuf)
- Connection pooling is essential — each Redis connection consumes ~10KB of memory; 1000 connections = ~10MB

### Multi-Tier Caching (In-Memory + Disk + Distributed)

**Example:** An AI search application uses a 3-tier cache: L1 (local LRU in app process, 100MB), L2 (local SQLite on disk, 2GB), L3 (Redis cluster, 16GB). L1 hits serve in <10μs, L2 in <500μs, L3 in <2ms. Only L3 misses trigger an LLM call (2-5s).

**Design Guidelines:**
- L1 cache should be small and fast — store only the hottest entries (typically 1-5% of total)
- L2 cache extends L1 with larger capacity but slower access — useful for burst absorption
- L3 distributed cache provides shared state across all instances — the source of truth
- Promote entries from L3 to L1 on access hotness — frequently accessed distributed entries become local
- Invalidate across tiers carefully — a stale L1 or L2 entry should be invalidated when L3 updates

**Performance Considerations:**
- Multi-tier adds complexity proportional to the number of tiers — 2 tiers (L1+L3) is often sufficient
- Cache miss waterfall: L1 miss → L2 miss → L3 miss → LLM call → populate L3 → L2 → L1
- Each tier adds ~0.1-1ms overhead for checking and populating — ensure the savings at each tier justify the added complexity
- Memory/disk tradeoff: L1 in RAM is expensive but fast; L2 on SSD is cheaper but 100-1000× slower
- Consistency across tiers is the hardest operational challenge — eventual consistency is usually acceptable for caches

### Cache Invalidation Strategies

**Example:** A documentation Q&A bot invalidates cached answers when the underlying documentation changes. A webhook from the CMS triggers a cache purge for all entries tagged with the changed document ID. The system also runs a nightly full cache sweep to catch any missed invalidations.

**Design Guidelines:**
- Prefer TTL-based invalidation as the baseline — simple and predictable
- Add event-driven invalidation for critical data — wire up webhooks or CDC streams to the cache layer
- Implement a grace period with stale-while-revalidate — serve stale data while asynchronously fetching fresh data, rather than blocking the user
- For bulk invalidation, use tag-based cache keys (e.g., "doc:123:response") and purge by tag pattern
- Test invalidation logic thoroughly — stale cache is harder to detect than no cache

**Performance Considerations:**
- TTL-based invalidation: zero runtime cost — expiry is handled by the cache engine
- Event-driven invalidation: adds 1-10ms per invalidation event — negligible for low event rates
- Tag-based purge: requires scanning keys matching the tag — O(n) in the number of matching keys. For large purges (>10K keys), use async jobs
- Stale-while-revalidate: adds one async refresh call per stale access — ensure the revalidation queue has sufficient capacity
- Cascade invalidation: invalidating one cache entry may require invalidating dependent entries — track dependency graphs carefully

### Cache Warming and Pre-Computation

**Example:** A daily news briefing AI pre-computes summaries for the top 200 news articles every morning at 4 AM. When users start accessing the briefing at 8 AM, all summaries are already in cache — zero cold-start misses.

**Design Guidelines:**
- Pre-compute caches for predictable, scheduled content — daily digests, weekly reports, onboarding flows
- Warm cache gradually to avoid overwhelming the LLM API — rate-limit pre-computation to stay under API limits
- Prioritize pre-computation for high-value, high-traffic content — the Pareto principle applies
- Implement cache warming as a background job with monitoring — failures should alert but not block the application
- Combine with periodic refresh to keep pre-computed content fresh

**Performance Considerations:**
- Pre-computation cost is upfront — shift LLM costs from peak hours to off-peak (cheaper API rates, lower infrastructure load)
- Warming 10K entries: ~$100-300 in LLM cost, 2-10 hours depending on rate limits and concurrency
- Pre-computed cache does not degrade user-facing latency — every request is a cache hit
- Storage for pre-computed content should be provisioned to handle the maximum pre-computed volume
- Refresh frequency should match content change rate — refreshing too often wastes cost; too rarely serves stale data

### Cache Monitoring and Hit-Rate Optimization

**Example:** A team monitors cache hit rate on a dashboard and notices a drop from 85% to 60% after a prompt template update. Investigation reveals the new template changed a cache key field. They add a cache key migration and the hit rate recovers to 82%.

**Design Guidelines:**
- Track the "holy trinity" of cache metrics: hit rate, latency savings, and cost savings
- Set up alerts for significant hit rate drops — a 10%+ drop in hit rate often indicates a configuration issue
- Log cache keys (sanitized) for misses to analyze miss patterns and identify optimization opportunities
- A/B test cache configurations — compare hit rates with different TTLs, eviction policies, or semantic thresholds
- Monitor cache backend health separately from application health — a degraded cache should not page the on-call engineer

**Performance Considerations:**
- Monitoring overhead: <0.1ms per cache operation when using async metrics emission
- Distributed tracing (OpenTelemetry) for cache operations adds 1-5% overhead — acceptable for debugging but disable in high-throughput paths if needed
- Hit rate is a lagging indicator — a sudden drop may appear minutes after the root cause
- Cost savings calculation: (cache_hits × cost_per_llm_call) − cache_infrastructure_cost — track this on every dashboard
- Latency savings calculation: average_llm_latency × hit_rate + cache_latency × (1 − hit_rate) — compare against no-cache baseline

### Cost Savings Analysis with Caching

**Example:** A startup spends $15K/month on GPT-4 API calls. After implementing an exact-match + semantic cache (Redis + GPTCache), they achieve a 55% hit rate. Monthly API cost drops to $6,750. Redis cluster costs $300/month. Net savings: $7,950/month (~53% reduction).

**Design Guidelines:**
- Calculate the fully loaded cost of a cache miss: API cost + embedding cost (if semantic) + compute + egress
- Track savings as a separate metric — prove cache ROI to stakeholders
- Factor in engineering and maintenance time — a cache system that saves $5K/month but costs $10K/month in engineering is a net loss
- Re-evaluate savings quarterly — as query patterns, model pricing, and cache efficiency change, ROI shifts
- Consider the environmental cost too — fewer LLM calls means lower energy consumption

**Performance Considerations:**
- Break-even analysis: (cache_infra_cost) / (cost_per_miss × miss_rate) = daily misses needed to break even
- Most systems break even within days to weeks of deployment
- Cost savings are nonlinear — the first 20% of hit rate is easiest to achieve; pushing beyond 60-70% requires semantic caching or prompt engineering
- API cost savings should factor in tiered pricing — reducing call volume may push you below a volume discount threshold

### Trade-offs: Cache Staleness vs. Freshness

**Example:** A weather query AI caches responses with a 30-minute TTL. During a rapidly changing storm, users get 20-minute-old forecasts. Setting TTL to 5 minutes increases freshness but drops hit rate from 90% to 60%, tripling API costs. The team implements a hybrid: 5-minute TTL for weather alerts, 60-minute TTL for general forecasts.

**Design Guidelines:**
- Classify cache entries by staleness tolerance — personalization (seconds), news (minutes), reference (hours-days), static content (weeks-months)
- Implement "stale-while-revalidate" — serve cached response immediately, refresh asynchronously
- For freshness-critical paths, bypass cache entirely or use a very short TTL (< 30s)
- Surface staleness metadata to users when appropriate — "Last updated 2 hours ago" builds trust
- Monitor user-facing staleness — track when stale cache entries are returned and whether they cause negative outcomes

**Performance Considerations:**
- Freshness vs. cost: every 2× reduction in TTL roughly halves the cache hit rate (for Poisson-like access patterns)
- Stale-while-revalidate adds ~1 async refresh per cache hit — ensure the backend can handle the revalidation load
- P99 freshness lag = TTL + revalidation_time — for TTL=5min and revalidation=3s, worst-case staleness is ~5min 3s
- Hard TTL (delete at expiry) vs soft TTL (mark stale but serve until refreshed) — soft TTL provides better availability at the cost of potential staleness
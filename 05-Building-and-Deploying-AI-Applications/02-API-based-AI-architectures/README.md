# API-Based AI Architectures

Designing and building API layers for AI-powered applications.

## What Makes AI API Design Different

AI APIs differ fundamentally from traditional REST APIs. An architect designing for AI workloads must account for properties that have no parallel in conventional HTTP services:

| Dimension | Traditional API | AI API | Architectural Impact |
|---|---|---|---|
| **Output determinism** | Same input → same output | Same input → varies by temperature, model version, random seed | Caching needs semantic matching; testing requires statistical methods |
| **Latency profile** | 50-500ms, predictable | 1-30s, variable with output length | Streaming is mandatory; connection pooling is critical; timeout design is different |
| **Cost model** | CPU/memory/bandwidth, predictable scaling | Per-token, correlated with output length, hard to predict per-request | API must return usage metadata; cost tracking needs to be built into the API response |
| **Error modes** | 4xx/5xx, timeouts, crashes | 200 OK with hallucinated content, policy violations, safety blocks | Error handling must include content-level validation, not just status codes |
| **Request/response shape** | Fixed schema, bounded size | Variable-length responses, streaming deltas, interleaved tool calls, multi-modal content | Schema design is more complex; backward compatibility is harder |

### The API Surface of a GenAI Service

A typical GenAI platform exposes these endpoint categories:

| Endpoint Category | Example | Pattern |
|---|---|---|
| **Chat / Completion** | `POST /v1/chat/completions` | Sync or streaming; the core inference API |
| **Embedding** | `POST /v1/embeddings` | Synchronous, batchable; lower latency requirement |
| **Streaming** | `POST /v1/chat/completions?stream=true` | SSE-based token-by-token response |
| **Batch** | `POST /v1/batch/completions` | Async; webhook or poll for results |
| **Model Info** | `GET /v1/models` | Synchronous; lists available models and capabilities |
| **Moderation** | `POST /v1/moderations` | Synchronous; content safety check |
| **Admin / Management** | `GET /v1/usage`, `POST /v1/api-keys` | Administrative; usage tracking and key management |
| **Health / Readiness** | `GET /health`, `GET /ready` | Standard; monitoring and load balancer integration |

### Design Principles for AI APIs

1. **Streaming-native design** — Assume every endpoint that can stream should stream. Non-streaming fallback is for legacy compatibility, not the default. Design response schemas around token deltas from day one.

2. **Cost transparency** — Every response must include token usage and, where possible, estimated cost. API consumers need this data for their own cost tracking, caching decisions, and quota management.

3. **Safe by default** — Input validation at the API boundary should strip PII, check prompt size, and apply guardrails before the request reaches the orchestration layer. An AI API should reject dangerous inputs, not pass them downstream.

4. **Client-aware design** — Design for the client's experience: typed SDKs, automatic retries, streaming handlers, and clear error codes. The API is only as good as the client's ability to consume it correctly.

5. **Upgrade tolerance** — Models change, prompts change, behavior changes. API versions should decouple client code from model internals. A client written against v1 should not break when the underlying model is upgraded.

## Key Topics

### RESTful API Design for AI Services

**What it is:** Designing REST endpoints for AI workloads — choosing resource models (completions, chat, embeddings, batches), URL structures, HTTP methods, and response formats. Unlike CRUD APIs (create-user, get-order), AI APIs center on a single action (generate, embed) with highly variable inputs and outputs.

**Architect's design considerations:**
- Resource modeling: Unclear whether a "completion" is a resource (has identity, can be retrieved) or an action (one-shot, no identity). OpenAI treats completions as actions (no GET /completions/:id). Architecturally, if you need to retrieve past completions, model them as resources with IDs.
- HTTP method choice: POST dominates AI APIs because requests are non-idempotent (same prompt → different response). Use GET only for read-only metadata endpoints (model list, usage stats).
- URL structure: Version prefix (`/v1/`) is standard; avoid date-based versioning (`/2024-01-01/`) — it clutters URLs and makes client upgrades ambiguous.
- Collection vs action endpoints: Prefer action-style (`POST /completions`) over CRUD-style (`POST /completions/create`) — shorter, clearer, and matches industry convention.

**Performance best practice:** Use persistent HTTP/2 connections with keep-alive. Each TCP+TLS handshake adds 100-300ms of latency. Since every LLM call already takes 2-10s, eliminating connection setup overhead is the single highest-impact latency optimization at the API layer. Set `keepalive_timeout` to at least 60 seconds and connection pool size to match your concurrency requirements.

**Products & tools:**
- **OpenAI API / Anthropic API:** Reference implementations for RESTful AI API design patterns
- **FastAPI / Flask:** Python frameworks for building AI APIs with automatic OpenAPI docs
- **Connexion (OpenAPI):** Spec-first API development — define the API contract before implementation
- **Postman / Bruno:** API design and testing tools for AI endpoints

### Request/Response Patterns for LLM Endpoints

**What it is:** The specific schema design for LLM API requests and responses — prompt structure, generation parameters (temperature, max_tokens, top_p), response content, tool call interleaving, and metadata. The request/response contract is the most critical API design decision because it determines client ergonomics, caching behavior, and upgrade path.

**Architect's design considerations:**
- Chat vs completion schemas: Chat (messages array with roles) is the dominant pattern because it naturally supports multi-turn conversations. Always prefer chat schema even for single-turn use cases — it is more extensible.
- Tool/function calling: Design the tool call format early. OpenAI's function calling format (`tool_calls` array with `id`, `type`, `function`) is the de facto standard. Supporting it ensures compatibility with existing SDKs and agent frameworks.
- Response metadata: Include `model`, `usage`, `created` (timestamp), and `id` in every response. Clients depend on these for logging, cost tracking, and debugging.
- System fingerprint: Return a `system_fingerprint` field that changes when the underlying model configuration changes — clients can detect silent model upgrades.

**Performance best practice:** Strip optional fields from both request and response schemas. Every unnecessary field adds JSON serialization/deserialization time and increases payload size. A typical chat completion response with all optional fields is ~800 bytes; stripping unused metadata reduces it to ~400 bytes. For 1M requests/day, that saves ~400MB of bandwidth and reduces serialization time by 15-25%.

**Products & tools:**
- **OpenAI Chat Completion API:** Industry-standard request/response schema — use as a reference for compatibility
- **Anthropic Messages API:** Alternative schema with different strengths (longer context, different tool format)
- **Pydantic / Zod:** Schema validation libraries for request/response models in Python and TypeScript
- **OpenAPI / Stoplight:** Spec-first API design for documenting LLM endpoints

### Streaming Responses (Server-Sent Events, WebSockets)

**What it is:** The server pushes partial response content to the client as it is generated, rather than waiting for the full response. SSE (Server-Sent Events) is the dominant pattern — simple HTTP-based, one-directional, supported natively by browsers. WebSockets are used for bidirectional streaming when the client needs to send data mid-generation (rare for LLM, common for voice).

**Architect's design considerations:**
- SSE vs WebSocket: SSE is simpler and sufficient for 95% of LLM use cases (text streaming). WebSocket is needed for audio streaming (voice conversations) or when the client must cancel mid-stream without an additional REST call.
- Chunk format: Each SSE event should be a JSON object with: `{choices: [{delta: {content: "..."}, index: 0}]}` — mirror the non-streaming response format so clients parse both modes with similar code.
- End-of-stream signal: Send a final event with `finish_reason: "stop"` (or "length", "tool_calls") so the client knows generation is complete and can aggregate deltas.
- Cancellation: Support cancellation via HTTP connection close (SSE) or a dedicated cancel endpoint. The client should not have to wait for the full generation if they navigate away.

**Performance best practice:** Tune SSE buffer flush interval to 50-100ms. Flushing every token (10-50ms intervals) floods the network with tiny TCP packets, increasing packet overhead by 5-10×. Flushing every 100ms batches several tokens per packet while still feeling real-time to the user. Measure the tradeoff on your infrastructure — the optimal interval depends on network conditions between server and client.

**Products & tools:**
- **FastAPI StreamingResponse:** Built-in SSE support via asynchronous generators in Python
- **Vercel AI SDK:** Streaming-first AI SDK with React/Vue/Svelte client components
- **EventSource (browser native):** Client-side SSE parser built into all modern browsers
- **WebSocket (FastAPI + websockets library):** For bidirectional streaming use cases
- **Server-Sent Events Protocol (SSE):** W3C standard — `text/event-stream` content type

### Asynchronous Request Processing

**What it is:** Decoupling request acceptance from request processing — the API accepts a request immediately, returns a placeholder ID, and processes it asynchronously. The client polls a status endpoint or receives a webhook callback when processing completes. This is essential for long-running GenAI workloads (batch summarization, document analysis, multi-step agent workflows).

**Architect's design considerations:**
- Poll-based vs webhook-based: Polling is simpler for the server (no callback URL management) but wastes client resources. Webhooks are more efficient but require the server to manage delivery, retries, and dead-letter queues. Use polling for internal services, webhooks for external integrators.
- Job resource model: Model the async request as a job resource: `POST /jobs → {job_id, status}` → `GET /jobs/{job_id} → {status, result}`. Include `created_at`, `updated_at`, `estimated_completion_time` in the job status.
- Queue depth exposure: Expose queue depth and estimated wait time in the job creation response. Clients can then decide whether to wait or use a different strategy.
- Cancellation of in-flight jobs: Support `DELETE /jobs/{job_id}` to cancel a queued or in-progress job. The server should respect cancellation within one processing step.

**Performance best practice:** Right-size the worker pool to match the LLM API's concurrency limit. If your LLM provider allows 100 concurrent requests per API key, configure your worker pool to 80-90 workers (leaving headroom for other services). More workers than the API permits will queue at the upstream, wasting your server's resources on connections that are blocked waiting. Measure the actual concurrency limit with a load test — documented limits are often higher or lower than real-world limits.

**Products & tools:**
- **Celery + Redis / RabbitMQ:** Mature Python task queue for async LLM processing
- **Temporal / Prefect:** Workflow engines for long-running, stateful GenAI jobs with retry and compensation
- **AWS SQS / Google PubSub:** Managed message queues for serverless async processing
- **FastAPI BackgroundTasks:** Lightweight async processing for single-server deployments
- **Redis RQ:** Simple Python queue backed by Redis — good for moderate throughput needs

### Batch Processing and Queuing

**What it is:** Grouping multiple requests into a batch for efficient processing — especially for embedding generation (where batched inference is much faster than individual calls) and for bulk completion jobs where real-time response is not required. The queue manages request ordering, prioritization, and backpressure.

**Architect's design considerations:**
- When to batch: Embedding APIs benefit from batching (batch of 64 is ~2× throughput of 64 individual calls). Chat completions benefit less (batch of 4-8 is optimal; larger batches show diminishing returns due to KV cache contention). Always benchmark batch sizes for your specific model and provider.
- Queue prioritization: Support priority levels in the queue — free-tier requests use a low-priority queue, premium-tier requests use high-priority. Implement via priority queues (Redis sorted sets) or separate queues per tier.
- Rate limiting at queue level: The queue should respect the LLM API's rate limits and throttle enqueue when approaching limits. Expose queue backpressure metrics (queue depth, average wait time) via a monitoring endpoint.
- Dead letter queue: Requests that fail after maximum retries should go to a dead letter queue for human inspection — not be silently dropped or retried indefinitely.

**Performance best practice:** Tune batch size per model and provider. Embedding APIs (OpenAI, Cohere) typically achieve optimal throughput at batch size 64-256 — larger batches increase per-request latency but improve throughput significantly. Chat completion APIs show diminishing returns beyond batch size 10 due to KV cache memory pressure and attention computation scaling quadratically with total batch tokens. Run a batch-size sweep (1, 2, 4, 8, 16, 32, 64) for each model to find the throughput optimum.

**Products & tools:**
- **Celery:** Task queue with batch processing support via `celery group` and `chord` primitives
- **OpenAI Batch API:** Server-side batch processing — submit 10K-50K requests, get results in 1-24 hours at 50% discount
- **Redis Streams:** For high-throughput queueing with consumer groups and message acknowledgment
- **RabbitMQ:** Message broker with priority queues, dead letter exchanges, and flexible routing
- **AWS SQS + Lambda:** Serverless batch processing for embedding and light generation workloads

### API Authentication and Authorization

**What it is:** Controlling access to AI API endpoints — authenticating clients (who they are) and authorizing actions (what they can do). Includes API keys (machine-to-machine), JWT tokens (user-level auth), OAuth flows (third-party integrations), and per-endpoint scoping.

**Architect's design considerations:**
- API keys for programmatic access: The dominant pattern for AI APIs. Keys should be prefixed (`sk-...`) for easy identification, hashed at rest, and rate-limited per key. Support key rotation with overlapping valid periods.
- JWT for user-level auth: Use JWTs for consumer-facing applications. Include `user_id`, `tenant_id`, `tier` (free/premium), and `quotas` in the token. Validate on every request — do not trust the client to send user identity.
- OAuth for third-party integrations: Support OAuth 2.0 for integrations where a third-party app acts on behalf of a user (e.g., "Connect your CRM to our AI assistant"). The access token is used to authenticate API calls.
- Per-endpoint scoping: An API key should be able to restrict which endpoints it can access (e.g., "chat only, no admin"). Implement scope as a claim in the key metadata.

**Performance best practice:** Cache validated tokens with a TTL matching the token expiry minus a safety margin. JWT signature verification (RSA256/ECDSA) takes 1-5ms per call. At 1K+ RPS, this saturates a CPU core on verification alone. Cache the decoded token for 55 minutes (for a 60-minute expiry) — the safety margin accounts for clock skew and revocation. Invalidate the cache early if token revocation is needed.

**Products & tools:**
- **Auth0 / Clerk:** Managed auth platforms with JWT, OAuth, and API key support
- **Firebase Auth:** JWT-based auth with built-in user management for consumer apps
- **API key hashing (bcrypt):** Hash API keys at rest; never store raw keys in the database
- **Vault (HashiCorp):** Secrets management for API keys — rotate, audit, and distribute keys securely
- **Kong / APISIX:** API gateway with built-in auth plugins (key auth, JWT, OAuth2)

### Rate Limiting Strategies

**What it is:** Controlling the rate at which clients can send requests — measured in requests per minute (RPM) and tokens per minute (TPM). For AI APIs, token-aware rate limiting is essential because a single long request can consume 10,000× more tokens (and cost) than a short one.

**Architect's design considerations:**
- RPM vs TPM: Implement both. RPM protects against connection floods; TPM protects against cost spikes. A user sending one 50K-token request is different from a user sending 500 100-token requests — RPM-only limiting treats them the same.
- Token bucket vs sliding window: Token bucket is O(1) per check — simply decrement a counter and check if non-negative. Sliding window tracks request timestamps in a sorted set — O(log n) per check. For high-throughput AI APIs, token bucket is strongly preferred.
- Per-user vs per-tenant vs global limits: Apply limits at the coarsest granularity that protects the system. Per-user limits prevent a single user from exhausting capacity; global limits prevent total system overload.
- 429 response format: Return `Retry-After` header (seconds until retry is safe), rate limit headers (`X-RateLimit-Remaining`, `X-RateLimit-Reset`, `X-RateLimit-Limit`), and a JSON body with the limit type and reset time.

**Performance best practice:** Use the token bucket algorithm over sliding window. Token bucket requires only a single Redis key per user (a counter + timestamp), making each rate limit check O(1) with one Redis GET operation. Sliding window stores timestamps of every request in a sorted set, requiring O(log n) operations and growing memory with request volume. For a production AI API serving 10K RPS, token bucket reduces rate-limiting overhead from ~5ms to <1ms per check.

**Products & tools:**
- **Redis + Lua scripting:** Atomic token bucket implementation with Lua scripts for correctness
- **Kong / APISIX:** Gateway-level rate limiting with configurable algorithms (token bucket, sliding window)
- **Cloudflare Rate Limiting:** Edge-level rate limiting for AI APIs behind Cloudflare
- **Token Bucket (custom in-process):** Simple implementation for single-server deployments using a background refill thread
- **OpenAI Rate Limits API:** Reference implementation — check `X-RateLimit-*` headers and `Retry-After` in responses

### API Versioning and Backward Compatibility

**What it is:** Managing changes to the API contract over time — adding fields, deprecating parameters, changing behavior, and upgrading underlying models — without breaking existing clients. Versioning for AI APIs is harder than traditional APIs because the behavior (not just the schema) changes with model upgrades.

**Architect's design considerations:**
- Three separate version concerns: (1) API version — endpoint contract (v1, v2), (2) model version — which model serves the request (gpt-4o-2024-08-06), (3) prompt version — which system prompt and instructions are used. Decouple these so a client pinned to API v1 can still get model upgrades.
- URL vs header versioning: URL versioning (`/v1/chat/completions`) is visible and easy for clients to understand. Header versioning (`Accept-Version: 2024-01-01`) is cleaner but hidden. Use URL versioning for major versions, header versioning for minor/patch versions.
- Sunset policy: Announce deprecation at least 6 months before removal. Return a `Sunset` header on deprecated endpoints. Maintain the old version in parallel for the deprecation window.
- Backward-compatible changes: Adding fields to responses is safe. Removing or renaming fields is breaking. Changing model behavior (different response style) is a breaking change — increment the API version.

**Performance best practice:** Version routing should be a simple header or URL prefix check — O(1) lookup, not regex matching against the full URL path. Use a map lookup (`versions["v1"] → handler_v1`) or a URL prefix match (`/v1/` → service_v1). Version resolution must not add more than 1ms overhead. Avoid loading version-specific middleware or serializers dynamically — register them at startup, not per-request.

**Products & tools:**
- **OpenAPI versioning:** Document all versions in separate OpenAPI specs; maintain version-specific SDKs
- **FastAPI prefix routing:** `APIRouter(prefix="/v1")` for version-specific endpoints
- **Kong / APISIX:** Route by URL prefix to different upstream services per API version
- **API Evolution (Zalando):** Guidelines for backward-compatible API evolution — treat as reference
- **SemVer for APIs:** Major version for breaking changes, minor for additive, patch for fixes

### Request Validation and Sanitization

**What it is:** Inspecting and transforming incoming requests before they reach the LLM — checking prompt length, stripping PII, validating required fields, enforcing schema compliance, and applying guardrails. Request validation at the API boundary is the first line of defense against prompt injection, cost abuse, and accidental data leakage.

**Architect's design considerations:**
- Validation order matters: Check prompt length and required fields first (fastest checks), then PII stripping (medium cost), then guardrails (most expensive). Reject early to avoid paying for deeper processing.
- PII stripping at the boundary: Strip or redact PII (names, emails, phone numbers, credit cards) from prompts before they reach the orchestration layer. This prevents downstream logging and storage of sensitive data.
- Prompt size limits: Enforce a maximum prompt size (e.g., 32K tokens for GPT-4, 128K for Gemini). Return a clear 413 Payload Too Large with the limit and the actual size. Protect against DoS via extremely long prompts.
- Schema validation for structured generation: If the API supports structured output (JSON schema), validate the schema at the API boundary before passing it to the LLM. An invalid schema wastes tokens when the LLM tries to follow it.

**Performance best practice:** Validate prompt length and required fields before any auth or guardrail check. Rejecting an oversized request (413) at the connection read stage costs <1ms and zero API cost. Passing it through auth (5-50ms), guardrails (50-500ms), and into the LLM (2-10s + token cost) wastes time and money for a request that will be rejected anyway. Validate in order: fast validation → auth → slow validation (guardrails).

**Products & tools:**
- **Pydantic (Python):** Request schema validation with automatic error messages — validate at the API boundary
- **Zod (TypeScript):** TypeScript-native schema validation for AI API backends
- **Presidio (Microsoft):** PII detection and redaction — integrate into API middleware
- **Guardrails AI:** Input guardrails for prompt injection detection at the API layer
- **AWS WAF / Cloudflare WAF:** Web application firewall rules for prompt-level filtering at the edge

### Error Response Standardization

**What it is:** A consistent format for error responses across all API endpoints — error codes, human-readable messages, machine-readable details, and retry guidance. For AI APIs, error types extend beyond HTTP status codes to include content-level errors (hallucination, policy violation, safety block).

**Architect's design considerations:**
- Follow RFC 7807 (Problem Details): Use the standard `{type, title, status, detail, instance}` format. Add an `errors` array for multiple validation errors. Consistency across endpoints is more important than perfect schema design.
- AI-specific error codes: Define codes for GenAI-specific failures — `content_policy_violation`, `hallucination_detected`, `context_too_long`, `model_overloaded`, `insufficient_safety_confidence`. Traditional REST APIs do not have these error categories.
- Retry guidance: Every 429 (rate limited) and 503 (service unavailable) response must include a `Retry-After` header in seconds. For token-aware rate limiting, include the limit type (`token_limit` vs `request_limit`) and reset time.
- Semantic error differentiation: Distinguish between "the model rejected the request" (policy violation) and "the guardrail rejected the request" (safety check) — they have different remediation paths.

**Performance best practice:** Error responses should be fixed-size (~200-300 bytes) with no dynamic content beyond the error code and message. Large error payloads waste bandwidth and are rarely read by clients — most automated clients care about the status code and error code, not the human-readable message. Use a template-based approach: render error responses from a pre-compiled template with only the variable fields (error code, timestamp, instance ID).

**Products & tools:**
- **RFC 7807 (Problem Details):** Standard error response format — adopt for consistency
- **OpenAPI error schemas:** Define error responses in your OpenAPI spec so clients can generate typed error handlers
- **FastAPI exception handlers:** Custom exception handlers for consistent JSON error responses
- **Sentry / BetterStack:** Error tracking and alerting for API errors — structured by error code

### API Gateway Patterns for AI Microservices

**What it is:** The API gateway as the entry point for all AI microservices — handling authentication, rate limiting, request routing, model selection, caching, cost tracking, and abuse detection. In AI architectures, the gateway takes on additional responsibilities beyond traditional load balancing: model routing, prompt caching, and cross-model fallback.

**Architect's design considerations:**
- Gateway responsibilities for AI: (1) Route to the correct model service based on request parameters, (2) Apply rate limits (RPM + TPM), (3) Cache identical or semantically similar requests, (4) Track cost per request per tenant, (5) Detect abuse patterns (rapid retries, prompt mining), (6) Fall back across model providers on failure.
- Model routing at the gateway: The gateway should inspect request parameters (model requested, user tier, feature flag) and route to the appropriate upstream — avoiding hardcoded routing in application code.
- Caching at the gateway: Implement exact-match and semantic caching at the gateway level. Cache keys should include model, temperature, and prompt hash. Semantic caching requires embedding generation at the gateway.
- Degradation at the gateway: When primary model returns errors, the gateway can retry with a different model or return a cached response — without the application layer needing to handle fallback logic.

**Performance best practice:** Offload TLS termination and rate limiting to the gateway rather than the application server. TLS termination is CPU-intensive (RSA/ECDSA handshake); rate limiting requires low-latency Redis access. Gateways (Kong, APISIX) implement both at the C level (via Nginx/OpenResty) with sub-millisecond overhead. Application servers written in Python/Node should focus on LLM orchestration and not consume CPU on TLS and rate limiting.

**Products & tools:**
- **Kong Gateway:** Extensible gateway with AI-specific plugins for model routing and caching
- **APISIX:** Open-source gateway with Lua plugin system — good for custom AI routing logic
- **Portkey:** AI-focused gateway with model routing, fallback, caching, and cost tracking built-in
- **Envoy:** High-performance proxy with gRPC support — suitable for self-hosted AI model serving
- **Azure API Management / AWS API Gateway:** Cloud-managed gateways with rate limiting, auth, and caching

### SDK and Client Library Generation

**What it is:** Generating typed client libraries for your AI API in multiple programming languages — handling serialization, authentication, rate limit retry, streaming, error handling, and connection pooling so that API consumers write minimal code.

**Architect's design considerations:**
- OpenAPI-first: Define your API in OpenAPI 3.1 spec first, then generate client libraries from it. The spec is the source of truth; the client is derived. Changes to the spec automatically propagate to all client libraries.
- Streaming support in SDKs: Streaming is the most complex part of AI API clients. The SDK should provide both `sync` and `async` streaming handlers — `for chunk in client.stream(...)` and `async for chunk in await client.stream(...)`.
- Automatic retry with backoff: The SDK should implement exponential backoff with jitter for 429 and 503 responses by default. Include configurable `max_retries`, `base_delay`, and `max_delay` for advanced users.
- Usage tracking in clients: The SDK should expose token usage and cost from the API response — clients should not have to parse response headers for this data. Include a `client.usage` aggregator that tracks total tokens across all calls.

**Performance best practice:** Implement client-side connection pooling with a max pool size equal to the API's documented concurrency limit. Each new HTTP connection requires a TCP handshake (1-3 round trips, 30-150ms) and potentially TLS negotiation (2-4 round trips, 50-300ms). Pooling reuses connections across requests. If the API allows 100 concurrent requests, set pool size to 100 — otherwise clients will either waste connections (>100 idle connections) or block unnecessarily (<100 active threads competing for fewer connections).

**Products & tools:**
- **OpenAPI Generator:** Auto-generate typed client libraries in 50+ languages from OpenAPI specs
- **OpenAI Python SDK / Node SDK:** Reference implementations for AI SDK design patterns (streaming, retry, auth)
- **anthropic-python / cohere-python:** Anthropic and Cohere SDKs — alternative design approaches
- **httpx (Python):** HTTP client with built-in connection pooling, async support, and timeout configuration
- **Kiota (Microsoft):** API client generator with support for middleware and retry handlers

### Token-Aware API Design

**What it is:** Including token usage metadata in every API response — `prompt_tokens`, `completion_tokens`, `total_tokens`, and optionally estimated cost. This enables clients to track their own usage, implement client-side caching decisions, and stay within their quotas without additional API calls.

**Architect's design considerations:**
- Mandatory usage field: Make `usage` a required field in every response (not optional). Clients depend on this for cost tracking. An optional field that is sometimes missing is worse than a required field that is always present.
- Cost estimation in responses: Include `estimated_cost_usd` as an optional field. This requires mapping model names to per-token pricing — maintain this mapping server-side so clients do not need to track pricing changes.
- Usage in streaming responses: For streaming endpoints, include aggregated usage in the final SSE event (with `finish_reason`). Clients aggregate streaming deltas and can read the final usage from the last event.
- Usage headers: Include usage in response headers as well as the body — `X-Usage-Prompt-Tokens`, `X-Usage-Completion-Tokens`, `X-Usage-Total-Tokens`. Clients that parse headers (e.g., proxies, gateways) can track usage without parsing the body.

**Performance best practice:** Add usage data as a small, fixed-size JSON field in every response. A typical usage object is 50-100 bytes — less than 1% overhead on a typical response (2-10KB). This saves clients an entire additional API call to a billing/analytics endpoint. The alternative — making clients call `GET /usage` separately — doubles API traffic for a basic operational need. Include it inline.

**Products & tools:**
- **OpenAI usage format:** Reference format — `{prompt_tokens: 10, completion_tokens: 50, total_tokens: 60}`
- **Helicone:** Usage tracking proxy that adds usage headers to any LLM API
- **LangFuse / LangSmith:** Usage tracking integrated with trace/observability data
- **Custom middleware:** Add usage tracking as API middleware — log to Redis/Postgres for analytics

### Fallback and Degradation Patterns

**What it is:** Strategies for maintaining API availability when the primary model or infrastructure is unavailable — retrying with a different model, serving cached responses, or returning a degraded but informative response. Fallback must be invisible to the client or clearly communicated.

**Architect's design considerations:**
- Model fallback chain: Define a fallback chain per use case — `primary → secondary → tertiary → cached → error`. For example, `GPT-4o → GPT-4o-mini → Claude 3.5 Haiku → cached response → "Service temporarily unavailable"`.
- Degraded response format: When falling back to a smaller/cheaper model, the response quality may be lower. Consider returning a `X-Degraded: true` header so clients know the response quality may be below normal.
- Cache-as-fallback: When all models are unavailable, serve the most recent cached response for identical queries. This is acceptable for read-heavy use cases with stable answers.
- Degradation without silence: Never silently serve degraded content without signaling it. A `X-Degraded: true` header lets the client decide how to handle it (display a warning, retry later, etc.).

**Performance best practice:** Set the circuit breaker timeout to 2× the p99 latency of the primary model. If GPT-4o has 5s p99, set the circuit breaker to 10s. Too short (matching p50) causes spurious fallbacks during normal latency spikes. Too long (>3× p99) defeats the purpose of fallback — the client waits the full timeout before the fallback kicks in, making the fallback response feel as slow as a failed primary request.

**Products & tools:**
- **Portkey:** AI gateway with built-in model fallback chains and circuit breaker configuration
- **LiteLLM:** Python library with configurable fallback — primary → fallback model on error
- **OpenRouter:** Unified API that automatically falls back across providers — no fallback logic needed in application code
- **Resilience4j (Java) / Tenacity (Python):** Circuit breaker and retry libraries for custom fallback logic

### Multi-Tenant AI API Isolation

**What it is:** Architecting the AI API so that multiple tenants (organizations, projects, users) can share the same infrastructure without affecting each other's performance, data privacy, or cost allocation. This includes separate rate limits, isolated caches, tenant-specific model routing, and strict data boundaries.

**Architect's design considerations:**
- Data isolation boundaries: Prompts from tenant A must never leak into tenant B's context, cache, or logs. Implement at multiple levels: cache keys include `tenant_id`, vector DB collections are per-tenant, logs are tagged with `tenant_id` and access-controlled.
- Rate limit isolation: Rate limits must be per-tenant, not global. Tenant A's traffic spike should not exhaust the global rate limit and block Tenant B. Implement hierarchical rate limiting: per-tenant limits nested within global limits.
- Cost tracking per tenant: Every response must include `tenant_id` in logs so costs can be attributed. Implement per-tenant budget enforcement — if Tenant A exceeds their monthly budget, their requests can be rejected at the API gateway.
- Tenant-specific model routing: Premium tenants can be routed to more capable models; free tenants to cheaper models. The tenant tier is extracted from the API key or JWT at the gateway.

**Performance best practice:** Use tenant-specific connection pools to the LLM API. If you have 50 tenants sharing a single connection pool of 100 connections, one tenant's burst of 80 concurrent requests leaves only 20 connections for the other 49 tenants — effectively a DoS. Instead, allocate per-tenant connection pools: 10 connections per tenant for 10 premium tenants. This ensures tenant-level fairness and prevents noisy-neighbor problems without per-request connection overhead.

**Products & tools:**
- **Qdrant / Milvus:** Vector DBs with native multi-tenancy — separate collections or partitions per tenant
- **Redis namespacing:** Cache keys scoped by `tenant_id:key` for per-tenant cache isolation
- **Kong / APISIX:** Gateway-level tenant routing based on API key → tenant mapping
- **PostgreSQL Row-Level Security:** Database-level tenant isolation for usage tracking and cost allocation
- **Stripe / Metering:** Per-tenant usage metering and billing integration for AI API monetization

## AI API Decision Matrix

| Use Case | Sync / Async | Streaming | Transport | Caching Strategy | Recommended Pattern |
|---|---|---|---|---|---|
| **Chat / Conversational AI** | Sync | Required (SSE) | HTTP/2 | Semantic + exact | `POST /v1/chat/completions?stream=true` |
| **Simple Completion** | Sync | Optional | HTTP/2 | Exact match | `POST /v1/completions` |
| **Embedding Generation** | Sync | No | HTTP/2 | Result cache (exact) | `POST /v1/embeddings` with batch size 64-256 |
| **Bulk Summarization** | Async | No | HTTP + Webhook | No cache (unique content) | `POST /v1/batch/completions` → webhook callback |
| **Voice / Audio Streaming** | Sync | Required (WebSocket) | WebSocket | No cache | WebSocket with bidirectional streaming |
| **Agent / Tool-using Workflow** | Sync | Required (SSE) | HTTP/2 | Tool result cache | Streaming chat with `tool_calls` in stream |
| **Internal Service Integration** | Sync | No | gRPC | Semantic cache | gRPC unary call with protobuf schema |
| **High-Throughput Production** | Async preferred | Optional | HTTP/2 + Pool | Multi-tier | Queue-based processing with connection pooling |
| **Multi-Model Gateway** | Sync | As needed | HTTP/2 | Shared cache across models | API gateway with model routing + fallback |
| **Public-Facing API** | Sync | Required | HTTP/2 | Exact + semantic per tenant | Gateway + per-tenant pools + usage headers |
# FastAPI Deployment for AI Applications

Using FastAPI to serve AI models and build production-grade AI backends.

## Why FastAPI for AI Workloads

FastAPI is the dominant Python framework for serving AI models in production. Its async-native design, automatic OpenAPI generation, and Pydantic integration make it a natural fit for AI workloads that differ significantly from traditional web APIs.

| Concern | FastAPI | Flask | Django | Node.js (Express) |
|---|---|---|---|---|
| **Async-native** | Yes (`async def`) | No (WSGI) | Partial (Django 3.1+) | Yes |
| **Model loading** | Lifespan events | Manual | Manual | Manual |
| **Request validation** | Pydantic (automatic) | Manual | DRF (heavy) | Joi/Zod (manual) |
| **Streaming** | `StreamingResponse` | Third-party | Third-party | Native |
| **OpenAPI docs** | Automatic | flasgger (external) | drf-spectacular (external) | swagger-jsdoc (external) |
| **Performance** | ASGI (uvicorn) | WSGI (gunicorn) | WSGI (gunicorn) | Event loop |
| **GPU model serving** | Background thread/process | Background thread | Background thread | Worker thread |

### Request Flow in a FastAPI AI Service

```
Client → ASGI Server (uvicorn) → FastAPI App → Middleware Stack
  → Request Validation (Pydantic) → Dependency Injection (auth, model, config)
  → Route Handler (async def) → Model Inference / LLM Call
  → StreamingResponse / JSON Response → Response Validation → Client
```

### Reference Project Structure

```
app/
├── main.py                  # FastAPI app creation, lifespan, middleware
├── config.py                # Settings via pydantic-settings
├── models/
│   ├── __init__.py
│   ├── loader.py            # Model loading/unloading logic
│   └── schemas.py           # Pydantic request/response models
├── routes/
│   ├── __init__.py
│   ├── chat.py              # /v1/chat/completions endpoint
│   ├── embeddings.py        # /v1/embeddings endpoint
│   └── health.py            # /health, /ready endpoints
├── services/
│   ├── __init__.py
│   ├── inference.py         # Model inference logic
│   └── streaming.py         # Streaming response generators
├── middleware/
│   ├── __init__.py
│   ├── request_id.py        # Request ID propagation
│   ├── logging.py           # Request/response logging
│   └── rate_limit.py        # Token-aware rate limiting
└── utils/
    ├── __init__.py
    ├── token_counter.py     # Token counting utilities
    └── retry.py             # Retry logic for LLM API calls
```

## Key Topics

### FastAPI Project Structure for AI Services

**What it is:** The directory layout and module organization for a FastAPI-based AI service. A well-structured project separates concerns — routes (HTTP handling) from services (business logic) from models (ML model loading) — making the codebase testable, deployable, and navigable as it grows to support multiple models and endpoints.

**How to do it:**
- Use the modular structure shown above — `routes/` for endpoints, `services/` for inference logic, `models/` for model loading, `schemas.py` for Pydantic models
- Split routes by domain — `chat.py`, `embeddings.py`, `health.py` — rather than having one monolithic `routes.py`
- Keep endpoint handlers thin — a route handler should validate input, call a service, format the response, and nothing more
- Config via `pydantic-settings` — environment variables with validation, not `os.environ` scattered across files
- Group related models in `models/` subpackages — `models/llm.py`, `models/embedder.py`, `models/reranker.py`

**Security considerations:**
- Never expose model weights or internal paths through static file serving — disable `mount('/static')` in production
- Configuration files (`.env`, `config.yaml`) must be excluded from Docker images and version control — use environment variables or secret stores
- The health endpoint (`/health`, `/ready`) should not expose internal state like model version or GPU memory — return a simple `{"status": "ok"}` 

**Performance considerations:**
- Import modules lazily inside route handlers or lifespan events, not at the top level — top-level imports slow application startup and increase memory usage for models that are never used in a given deployment
- Use `__init__.py` re-exports sparingly — circular imports between `routes/`, `services/`, and `models/` are a common pain point in growing AI services
- Profile imports at startup — `python -X importtime app/main.py` reveals slow imports that delay container readiness

**Points to consider in design:**
- Plan for multi-model support from the start — even if you serve one model today, the project structure should accommodate a second model without restructuring
- Separate public routes from internal routes — use prefix `/v1/` for public endpoints and `/internal/` for admin/metrics endpoints
- Use `lifespan` (not `startup`/`shutdown` events) for model lifecycle — `startup`/`shutdown` are deprecated as of FastAPI 0.93+
- Consider using `taskiq` or `Celery` integration for endpoints that trigger long-running inference jobs — do not block the ASGI event loop

### Async Endpoint Design for Model Inference

**What it is:** Designing FastAPI route handlers that serve model inference either asynchronously (for I/O-bound LLM API calls) or synchronously in a thread pool (for CPU/GPU-bound local model inference). The choice between `async def` and `def` determines whether the ASGI event loop is blocked during inference.

**How to do it:**
- Use `async def` for I/O-bound inference — calling OpenAI/Anthropic APIs via `httpx.AsyncClient`, querying vector databases, awaiting other async services
- Use `def` with `run_in_threadpool` for local model inference — CPU/GPU-bound model forward passes block the event loop; FastAPI automatically runs `def` endpoints in a thread pool
- For hybrid workloads (local model with async preprocessing), split the work: async I/O first, then synchronous model call, then async postprocessing
- Configure the thread pool size via `--workers` and the ASGI server's thread pool — the default 40 threads may be insufficient for concurrent model inference

```python
# I/O-bound: async LLM API call
@app.post("/v1/chat")
async def chat(request: ChatRequest, llm: LLMClient = Depends(get_llm)):
    return await llm.generate(request)

# CPU-bound: local model inference (runs in thread pool)
@app.post("/v1/embed")
def embed(request: EmbedRequest, model: EmbeddingModel = Depends(get_model)):
    return model.encode(request.text)
```

**Security considerations:**
- Set request size limits on inference endpoints — `max_request_size=10MB` prevents large-prompt DoS attacks
- Validate model selection against an allowlist — `model in ["gpt-4o", "gpt-4o-mini"]` prevents clients from specifying arbitrary model names that may route to unauthorized providers
- Timeout all external inference calls — `httpx.AsyncClient(timeout=30.0)` prevents a hanging LLM API call from holding a worker thread indefinitely

**Performance considerations:**
- `async def` endpoints serve more concurrent requests than `def` because they do not consume thread pool slots while waiting on I/O — use `async def` for any endpoint that calls external APIs
- The thread pool size limits concurrent `def` endpoint capacity — if your model takes 2s per inference and you have 40 worker threads, max throughput is 20 RPS. Increase workers or use async model serving (batching server like vLLM/Triton) to scale
- Startup cost: importing model libraries (torch, transformers) at module level adds 5-30s to startup — defer imports to the lifespan event handler

**Points to consider in design:**
- Not all model inference is CPU-bound — sending prompts to a remote vLLM/TGI server is I/O-bound and should use `async def`
- For endpoints that call both local models and remote APIs, split into service layers with dedicated async/sync boundaries
- Use `asyncio.timeout()` for all async inference calls — a slow model should not starve the event loop
- Consider using `anyio` (FastAPI's async backend) for cancellation support — `asyncio` does not cancel tasks immediately

### Background Tasks for Long-Running Inference

**What it is:** Offloading long-running inference or post-processing from the request-response cycle to background workers — either in-process (FastAPI's `BackgroundTasks`) or out-of-process (Celery, Temporal). The endpoint returns immediately with a task ID, and the client polls for results or receives a webhook callback.

**How to do it:**
- Use `BackgroundTasks` for lightweight, fast ( 5s) tasks — logging, cache warming, metrics emission. These run in the same process and share its lifecycle
- Use Celery for production-grade async processing — model inference, embedding generation, batch summarization — where tasks may run for minutes and must survive server restarts
- Implement a task status endpoint — `GET /tasks/{task_id}` returns `{status, result, created_at, completed_at}` — so clients can poll for completion
- Combine with webhooks for push-based completion — the client provides a `callback_url` in the request, and the server POSTs the result when done

```python
from fastapi import BackgroundTasks

# Lightweight in-process task
@app.post("/v1/summarize")
async def summarize(request: SummarizeRequest, tasks: BackgroundTasks):
    result = await generate_summary(request.text)  # fast part
    tasks.add_task(log_usage, request, result)      # background logging
    return result

# Celery-based async processing
@app.post("/v1/batch/embed")
async def batch_embed(request: BatchEmbedRequest):
    task = embed_batch.delay(request.texts)
    return {"task_id": task.id, "status": "queued"}

@embed_batch.task
def embed_batch(texts: list[str]):
    model = load_model()
    return model.encode(texts)
```

**Security considerations:**
- Validate webhook callback URLs against an allowlist — prevent the server from being used as a SSRF vector to hit internal services
- Sign webhook payloads with a shared secret so clients can verify the request originated from your server
- Background tasks inherit the request's authentication context — ensure the task runs with the correct permissions and does not escalate privileges

**Performance considerations:**
- `BackgroundTasks` runs in the same process — if the task is CPU-heavy, it blocks the event loop and degrades response latency for other requests. Only use `BackgroundTasks` for I/O-bound or very fast tasks
- Celery task queues decouple task processing from API serving — the API process stays responsive even if the task queue is backlogged
- Task queue backpressure: monitor queue depth and set Celery's `worker_prefetch_multiplier=1` to prevent workers from accepting more tasks than they can handle
- Database connection pool for task workers should be sized independently from the API connection pool — task workers need fewer, longer-lived connections

**Points to consider in design:**
- Define clear task timeout policies — a summarization task that runs for >5 minutes should be killed and retried with a smaller input
- Implement idempotency for background tasks — the same task submitted twice should produce the same result (or be deduplicated)
- Store task results in a database with TTL — do not keep completed task results indefinitely; expire after 7-30 days depending on compliance needs
- Use task priority queues — free-tier requests go to a low-priority queue, premium requests to high-priority — so paying users get faster processing

### Dependency Injection for Model Loading and Configuration

**What it is:** FastAPI's `Depends()` system for managing model instances, configuration objects, and client connections as injectable dependencies. Model loading (which is slow and memory-heavy) is separated from request handling and scoped to the application lifespan, while per-request dependencies (auth, rate limit state) are created and torn down with each request.

**How to do it:**
- Load models in the `lifespan` handler and attach them to `app.state` — this ensures the model is loaded once at startup, not on every request
- Create dependency functions that retrieve models from `app.state` — `def get_model(request: Request) -> MyModel: return request.app.state.model`
- Use `Depends()` in route handlers to inject the model — `def chat(request: ChatRequest, model: MyModel = Depends(get_model))`
- For configuration, use `pydantic-settings` and inject settings via `Depends(get_settings)` — this makes configuration mockable in tests

```python
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings

# Lifespan-based model loading
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = await load_model()  # load once at startup
    app.state.llm_client = AsyncLLMClient()
    yield
    app.state.model.unload()  # cleanup on shutdown

app = FastAPI(lifespan=lifespan)

# Injectable dependencies
def get_model(request: Request) -> MyModel:
    return request.app.state.model

def get_llm_client(request: Request) -> AsyncLLMClient:
    return request.app.state.llm_client

@app.post("/v1/chat")
async def chat(
    request: ChatRequest,
    model: MyModel = Depends(get_model),
    llm: AsyncLLMClient = Depends(get_llm_client),
):
    return await llm.generate(request.prompt)
```

**Security considerations:**
- Never load a user-specified model path — dependency injection should use a fixed model loaded at startup, not dynamically loaded based on user input
- Dependency functions run on every request — avoid slow operations in dependencies (DB queries, file reads) without caching
- Auth dependencies should run before model dependencies — failing auth early avoids wasted model inference

**Performance considerations:**
- Dependency functions are cached within the same request scope by default — calling `Depends(get_model)` multiple times in the same request returns the same instance, costing nothing
- Model loading in `lifespan` keeps the model loaded across requests — avoid loading/unloading models per-request; GDDRAM allocation/deallocation is slow and causes memory fragmentation
- `pydantic-settings` reads environment variables once at import time — subsequent `Depends(get_settings)` calls are instant (dict lookup)
- Lazy model loading (load on first request, not on startup) improves cold start time but adds latency to the first request — use only for rarely-used models

**Points to consider in design:**
- Use `Annotated` type aliases (Python 3.10+) to reduce boilerplate — `ModelDep = Annotated[MyModel, Depends(get_model)]` then `model: ModelDep`
- For multi-model services, create separate dependency functions per model — `get_small_model`, `get_large_model` — so each route only loads what it needs
- Test with dependency overrides — FastAPI's `app.dependency_overrides` allows replacing real models with mocks in tests without modifying route handlers
- Consider using `@lru_cache` on dependency functions that return configuration objects — but never on model instances (model instances are not hashable and should not be cached per-request)

### Input Validation with Pydantic Models

**What it is:** Using Pydantic models to define, validate, and document request and response schemas for AI endpoints. FastAPI automatically validates incoming requests against the Pydantic schema, returns clear 422 errors on validation failures, and generates OpenAPI documentation from the schema.

**How to do it:**
- Define request models with field validation — `messages: list[Message]`, `max_tokens: int = Field(le=4096)`, `temperature: float = Field(ge=0, le=2)`
- Use `field_validator` for cross-field validation — if `stream=True`, then `max_tokens` must be positive
- Use discriminated unions for tool call schemas — `Union[TextContent, ImageContent, ToolCallContent]` with discriminator on `type` field
- Define response models with examples — FastAPI uses these for OpenAPI documentation

```python
from pydantic import BaseModel, Field, field_validator

class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant|tool)$")
    content: str = Field(max_length=128_000)

class ChatRequest(BaseModel):
    model: str = Field(default="gpt-4o")
    messages: list[ChatMessage] = Field(min_length=1, max_length=1000)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, ge=1, le=16384)
    stream: bool = Field(default=False)

    @field_validator("messages")
    def validate_message_order(cls, v):
        if v and v[0].role == "assistant":
            raise ValueError("first message cannot be from assistant")
        return v

class ChatResponse(BaseModel):
    id: str = Field(examples=["chat-123abc"])
    model: str
    choices: list[dict]
    usage: dict
```

**Security considerations:**
- Set `max_length` on all string fields — prevent prompt injection via excessively long inputs (>128K tokens may exhaust context window or budget)
- Use `pattern` validation for enum-like fields — `role` should match only known roles; reject unknown roles that could bypass safety logic
- Never use `allow_extra_fields` in production — extra fields in requests should be rejected (default behavior). Extra fields in responses should be excluded by default
- Validate `model` field against an allowlist — `@field_validator("model")` that checks against `ALLOWED_MODELS` set

**Performance considerations:**
- Pydantic serialization for large payloads (100+ messages) adds 1-10ms — use `model_dump(exclude_unset=True)` to skip serializing default-valued fields
- Response validation is optional but useful — pass `response_model=ChatResponse` to validate the output before sending. Disable for high-throughput endpoints if the performance cost is significant
- Use `model_dump(mode="json")` for faster serialization — Pydantic v2's Rust core (`pydantic-core`) is 5-10× faster than v1's Python implementation
- For streaming endpoints, validate the request but not each stream chunk — stream chunks are too numerous for per-chunk validation overhead

**Points to consider in design:**
- Version your Pydantic models — create `ChatRequestV1`, `ChatRequestV2` when the schema changes, rather than mutating existing models
- Use `model_config(extra="forbid")` to reject unknown fields — silently ignoring extra fields can mask client bugs
- For inputs shared across endpoints (e.g., `ModelConfig`), define reusable mixin classes to avoid duplication
- Define response models for both success and error cases — `ChatResponse` and `ChatErrorResponse` — so OpenAPI docs show both paths

### Streaming Responses for LLM Generation

**What it is:** Returning generated tokens incrementally to the client as the LLM produces them, rather than waiting for the complete response. FastAPI's `StreamingResponse` wraps an async generator that yields token deltas, giving the client a real-time experience and enabling early display of partial results.

**How to do it:**
- Define an async generator that yields SSE-formatted token deltas — `yield f"data: {json.dumps(chunk)}\n\n"`
- Return `StreamingResponse` with `media_type="text/event-stream"` — FastAPI handles the correct headers (no buffering, chunked transfer, CORS)
- Handle client disconnection gracefully — monitor `await request.is_disconnected()` and stop generation to save cost
- Send a final event with `[DONE]` marker or `finish_reason` so the client knows generation is complete

```python
import json
from fastapi.responses import StreamingResponse

@app.post("/v1/chat/stream")
async def chat_stream(request: ChatRequest, llm: LLMClient = Depends(get_llm)):
    async def generate():
        async for chunk in llm.stream(request.messages):
            if await request.is_disconnected():
                break  # stop generation on client disconnect
            yield f"data: {json.dumps(chunk.delta())}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "cache-control": "no-cache",
            "x-request-id": request.state.request_id,
        },
    )
```

**Security considerations:**
- Validate content safety on streamed output — intercept each chunk and block the stream if a safety violation is detected. However, per-chunk validation adds latency; validate at sentence boundaries instead
- Set response size limits on streaming endpoints — a client that requests `max_tokens=16384` should respect that limit; the server should enforce it regardless of what the client requests
- Streaming responses bypass standard buffering — ensure WAF and proxy infrastructure is configured to handle SSE (no buffering, chunked transfer)

**Performance considerations:**
- Generator overhead per-yield is ~10-50μs — negligible compared to LLM token generation time (50-500ms per token)
- Client disconnection detection uses `await request.is_disconnected()` — this is an async call that checks the TCP connection state; call it every 5-10 tokens, not on every chunk, to avoid per-chunk overhead
- Backpressure: if the client reads slower than tokens are generated, the TCP send buffer fills and `async for` pauses — this is natural flow control. Monitor the send buffer to detect slow consumers
- Uvicorn workers can handle many concurrent streaming connections because streaming is I/O-bound — each stream spends most time waiting for the next token

**Points to consider in design:**
- Design the stream chunk format to mirror the non-streaming response — clients that parse streaming responses should use nearly identical code to those that parse non-streaming responses
- Include `usage` information in the final stream event — clients aggregate usage across all token events; provide the final aggregated count in the last event
- Support both streaming and non-streaming from the same endpoint — the `stream` parameter in the request body controls the response type, not a different URL
- Cache streaming responses at the content delivery layer (CDN) only with careful configuration — SSE responses should not be cached by default

### WebSocket Support for Real-Time AI Interactions

**What it is:** Real-time bidirectional communication between client and server using WebSockets — enabling the client to send input mid-generation (e.g., voice conversations, interactive editing) and the server to push updates asynchronously. FastAPI's `WebSocket` integration supports both receiving and sending messages on a persistent connection.

**How to do it:**
- Define a WebSocket endpoint with `@app.websocket("/ws/v1/chat")` — accept the connection, then enter a loop that receives messages and sends responses
- Handle client messages as JSON — `await websocket.receive_json()` and `await websocket.send_json()`
- Implement ping/pong for keepalive — send `{"type": "ping"}` every 30 seconds; if no pong received within 10 seconds, close the connection
- Manage connection lifecycle — accept → authenticate → process messages → handle disconnect → cleanup

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/v1/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            async for chunk in llm.stream(data["messages"]):
                await websocket.send_json({"type": "chunk", "content": chunk})
                if chunk.finish_reason:
                    await websocket.send_json({"type": "done", "usage": chunk.usage})
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
```

**Security considerations:**
- Authenticate before the message loop — validate a token from the initial connection request (query parameter or first message) before processing any messages
- Set message size limits — `websocket.max_size = 10_000_000` prevents memory exhaustion from oversized messages
- Use a connection timeout — close idle WebSocket connections after 10 minutes of inactivity to free resources
- Rate limit messages per WebSocket connection — a client sending 100 messages/second should be throttled or disconnected

**Performance considerations:**
- Each WebSocket connection consumes a small amount of memory (~10-20KB) plus buffering for pending messages. At 10K concurrent connections, 200-400MB is used just for connection overhead
- Use `receive_text()`/`send_text()` for small messages — JSON parsing overhead is unnecessary for simple data. Use `receive_json()`/`send_json()` only when the payload structure warrants it
- WebSocket connections are persistent — a server restart drops all connections. Implement reconnection logic on the client side with exponential backoff
- Uvicorn's default WebSocket implementation is synchronous — for high-throughput WebSocket traffic, consider using Daphne or Hypercorn as the ASGI server

**Points to consider in design:**
- Design the WebSocket message protocol as a state machine: `{type: "message" | "stream_start" | "chunk" | "done" | "error" | "ping" | "pong"}` — structured types make client handling predictable
- Support both streaming text and tool calls over WebSocket — the message format should accommodate `type: "tool_call"` for agentic interactions
- Fall back to SSE if WebSocket is not available — many corporate networks block WebSocket; provide a streaming HTTP endpoint as an alternative
- Use connection-scoped state — store user context, auth info, and session state in a dictionary keyed by WebSocket object, cleaned up on disconnect

### Middleware (CORS, Logging, Rate Limiting)

**What it is:** Middleware functions that process every request before it reaches the route handler (and every response before it leaves). For AI services, middleware handles cross-cutting concerns: CORS (for web clients), request logging (for debugging and cost tracking), rate limiting (RPM + TPM), request ID propagation, and latency tracking.

**How to do it:**
- Use FastAPI's `add_middleware()` for standard middleware (CORSMiddleware, TrustedHostMiddleware)
- Implement custom middleware as `@app.middleware("http")` async functions that yield to the handler
- Chain middleware carefully — order matters: rate limiter before auth before logging before route handler
- Propagate a request ID through middleware for distributed tracing

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import time, uuid

# Standard middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)

# Custom middleware for request ID and latency tracking
@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()

    response = await call_next(request)

    elapsed = time.perf_counter() - start
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-MS"] = str(round(elapsed * 1000, 1))
    return response
```

**Security considerations:**
- Set CORS origins to an explicit allowlist — never use `allow_origins=["*"]` for authenticated AI APIs; it disables CORS protection entirely
- Add `TrustedHostMiddleware` to prevent host header attacks — `allowed_hosts=["api.example.com"]`
- Rate limiting middleware should run before auth middleware — a rate-limited request that fails auth should not count against the auth service's quota
- Logging middleware must never log full request bodies in production — log at INFO level with metadata only (request_id, user_id, latency, model, tokens) and at DEBUG level for request bodies with PII scrubbing

**Performance considerations:**
- Middleware runs on every request — each middleware function should be O(1) or O(log n) at worst, never O(n) on request body size
- Body-consuming middleware (logging request bodies) forces the request body to be read into memory — this breaks streaming endpoints. Only log metadata for streaming requests
- Rate limiting middleware using Redis adds 1-5ms per check — this is acceptable; Redis is fast. Rate limiting with a database query (Postgres) adds 5-20ms — use Redis
- Middleware stack depth affects latency: 5 middleware layers × 2ms each = 10ms overhead. Keep middleware count under 7 for AI services where the LLM call itself takes 2-10s

**Points to consider in design:**
- Order middleware by speed — fastest first (CORS headers, request ID) then slowest last (logging, rate limiting with Redis). A request rejected by CORS should not pay Redis rate limit cost
- Use middleware for observability (request ID, timing, logging) and gateway functionality (CORS, rate limiting). Use dependency injection for business logic (auth, model access)
- Make middleware configurable per-route — not all middleware needs to apply to the health endpoint. FastAPI allows route-level exclusion from certain middleware

### Model Lifecycle Management (Warmup, Reload, Health Check)

**What it is:** Managing the model's lifecycle within the FastAPI application — loading on startup, verifying readiness, serving requests, handling graceful reload when the model changes, and cleaning up on shutdown. Proper lifecycle management ensures the model is ready when the first request arrives and that model updates do not cause downtime.

**How to do it:**
- Use the `lifespan` context manager for model load/unload — `yield` after loading makes the app ready; cleanup runs on shutdown
- Implement `/health` (app is alive) and `/ready` (model is loaded and accepting requests) endpoints — Kubernetes probes use these
- For model reload, use a two-phase approach: load the new model in the background, then atomically swap the reference — prevents serving from a partially loaded model
- Warm up the model with a dummy inference after loading — the first real inference (cold start) is often 2-10× slower than subsequent calls

```python
import asyncio
from contextlib import asynccontextmanager

model_registry: dict[str, object] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Phase 1: Load primary model
    app.state.model = await load_model_async()
    # Warmup: run dummy inference to trigger kernel compilation
    await app.state.model.warmup()
    app.state.ready = True
    yield
    # Phase 3: Cleanup
    app.state.model.unload()
    app.state.ready = False

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def readiness(request: Request):
    if getattr(request.app.state, "ready", False):
        return {"status": "ready"}
    return JSONResponse(status_code=503, content={"status": "not_ready"})
```

**Security considerations:**
- The `/health` and `/ready` endpoints should not be exposed to the public internet — restrict to internal network via firewall rules or a separate management port
- Model reload should require authentication — a malicious reload request could swap the model with a different (potentially harmful) version
- Never load models from user-provided paths — models should be loaded from a fixed, validated path in the container filesystem or a signed artifact registry

**Performance considerations:**
- Model loading time dominates startup — a 7B parameter model on GPU takes 10-30s to load and initialize; large models (70B+) can take 2-10 minutes
- Warmup inference is essential — the first inference after model load includes GPU kernel compilation (CUDA graphs, cuBLAS plans), which can take 5-30s. Without warmup, the first real request times out
- Graceful reload: use `asyncio.create_task()` to load the new model in the background while the old model continues serving. Only swap the reference after the new model is ready and warmed up
- Monitor GPU memory usage after model load — leaks during model reload can cause OOM after a few reload cycles

**Points to consider in design:**
- Separate model serving from model management — a lightweight sidecar or management endpoint can handle reload without affecting the serving code path
- Use a model registry (MLflow, Hugging Face, S3) rather than baking model weights into the Docker image — this allows model updates without image rebuild
- For multi-model deployments, load models on demand (lazy loading) and evict unused models to free GPU memory — use an LRU cache pattern
- Implement a `/metrics` endpoint (Prometheus) exposing model loading state, latency percentiles, and GPU utilization — essential for production operations

### Containerization with Docker

**What it is:** Packaging the FastAPI AI service and its dependencies (Python packages, model weights, system libraries for GPU) into a Docker container for consistent deployment across environments. For AI services, containerization must handle large model weights, GPU drivers, and multi-stage builds that separate build-time dependencies from runtime dependencies.

**How to do it:**
- Use multi-stage Docker builds — stage 1 (build): install torch, transformers, compile dependencies; stage 2 (runtime): copy only the installed packages and application code
- Use a CUDA base image for GPU serving — `nvidia/cuda:12.4.0-runtime-ubuntu22.04` or `nvidia/cuda:12.4.0-base-ubuntu22.04` for smaller footprint
- Do not bake model weights into the image — download at container startup from a model registry (Hugging Face, S3, Azure Blob) or mount as a volume
- Use `uvicorn` as the entry point with `--workers=1` for GPU deployments — multiple workers sharing a single GPU cause memory contention

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "uvloop"]
```

**Security considerations:**
- Run the container as a non-root user — `USER appuser` after installing dependencies. This prevents container escape vulnerabilities
- Use `--read-only` filesystem flag in production — the application should not write to the container filesystem; use volumes for any writable paths
- Scan images for vulnerabilities with `docker scan` or `trivy` before deploying — base images accumulate CVEs over time; rebuild and redeploy regularly
- Never store API keys or secrets in Docker images — use environment variables at runtime via `--env-file` or a secrets manager

**Performance considerations:**
- Image size matters for cold start — a full CUDA + torch + transformers image can be 8-15GB. Minimize with multi-stage builds and smaller base images (`nvidia/cuda:base` instead of `runtime`)
- Model weight download at startup adds 1-10 minutes to container readiness — use pre-pulled images with weights included for latency-sensitive deployments, or mount weights from a shared volume
- GPU memory is not freed on container stop — ensure `--gpus all` cleanup on container exit. Orphaned GPU processes consume memory for hours
- Uvicorn with `--workers > 1` on GPU: each worker loads its own model copy into GPU memory. Run `--workers=1` per GPU and scale horizontally (multiple containers with one GPU each)

**Points to consider in design:**
- Use `docker compose` or Kubernetes for local development — `docker compose up` with a mounted volume for model weights avoids rebuilding the image on every code change
- Pin base image tags to specific versions — `nvidia/cuda:12.4.0` not `nvidia/cuda:latest`. Latest tags change unexpectedly and break builds
- Use `.dockerignore` to exclude `__pycache__/`, `.env`, `.git/`, model weight files (if downloading at runtime) from the build context — a model weights file accidentally included in the image can balloon it to 50GB+
- Consider using `uv` or `pip install --no-cache-dir` to reduce image size — pip cache adds 200-500MB to the build stage

### Deployment to Cloud Platforms (Azure, AWS, GCP)

**What it is:** Deploying the containerized FastAPI AI service to a cloud platform with GPU support — Azure Container Apps (with GPU), AWS ECS / EKS (with GPU instances), or GCP Cloud Run (GPU preview). Each platform has different scaling, networking, and GPU configuration.

**How to do it:**
- **Azure Container Apps:** Use `az containerapp create --environment ... --cpu 4 --memory 16Gi --gpu 1` — ACA supports GPU-enabled serverless containers
- **AWS ECS with Fargate:** Use GPU tasks via Fargate with `"requiresCompatibilities": ["FARGATE"]` and `"deviceType": "gpu"` — or use EC2 launch type with `g4dn.xlarge` instances for lower cost
- **AWS EKS / GKE:** Deploy as a Kubernetes Deployment with `nvidia.com/gpu: 1` resource requests and the NVIDIA device plugin
- **GCP Cloud Run (GPU preview):** `gcloud run deploy --cpu 8 --memory 32Gi --gpu 1 --gpu-type nvidia-l4` — serverless GPU inference is emerging (preview as of 2025)

```yaml
# Kubernetes deployment example
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - image: myregistry/ai-service:latest
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "32Gi"
            cpu: "8"
        env:
        - name: MODEL_NAME
          value: "gpt-4o-mini"
      nodeSelector:
        cloud.google.com/gke-accelerator: nvidia-l4
```

**Security considerations:**
- Use managed identities (Azure Managed Identity, AWS IAM Roles, GCP Service Accounts) instead of API keys — rotate credentials automatically, no secrets in environment variables
- Restrict network access to the service — use VPC/subnet isolation, private endpoints, and security groups that only allow traffic from the API gateway or load balancer
- Enable audit logging (Azure Diagnostic Settings, AWS CloudTrail, GCP Audit Logs) for all model inference requests — compliance and security investigations depend on these logs
- Use container image scanning integrated with the registry — Azure Container Registry, AWS ECR, GCP Artifact Registry all support automated vulnerability scanning

**Performance considerations:**
- GPU cold start on cloud platforms takes 3-10 minutes — GPU nodes are not always pre-provisioned. Use minimum running replicas (not zero-to-N auto-scaling) to avoid cold start on every request
- Cloud GPU pricing: reserved instances (1-year commit) are 40-60% cheaper than on-demand. For steady-state AI workloads, always reserve
- Network latency between the FastAPI service and the LLM API: choose the cloud region closest to the model provider's API endpoints. For OpenAI, `us-east-1` / `eastus` / `us-central1` minimize latency
- Scale-to-zero GPU is rarely practical — GPU allocation takes 3-10 minutes. Use minimum 1 replica and scale up from there

**Points to consider in design:**
- Use blue-green or canary deployments for model updates — a new model version is deployed alongside the old version; traffic is gradually shifted. This allows rollback without rebuilding the deployment
- Health check probes (liveness + readiness) are essential for cloud platforms — Kubernetes and ACA use these to route traffic only to healthy containers. Configure `initialDelaySeconds` to account for model loading time (30-120s)
- Cloud platform GPUs have different compute capabilities — L4 (GCP), T4 (AWS), A100 (all). If your model requires FP8 or specific CUDA capabilities, ensure the GPU type supports it
- Consider multi-region deployment for disaster recovery — if the primary region GPU is unavailable, fail over to a secondary region with pre-warmed GPU containers

### Load Testing and Performance Tuning

**What it is:** Measuring the FastAPI AI service's throughput, latency, and resource utilization under load — identifying bottlenecks (model inference, API rate limits, database queries, CPU) and tuning configuration parameters to maximize performance per dollar.

**How to do it:**
- Use `locust` or `k6` for load testing — simulate concurrent users sending AI requests with realistic prompt sizes and generation lengths
- Measure key metrics: p50/p95/p99 latency, throughput (RPS), error rate, GPU utilization, and cost-per-request
- Tune ASGI server settings: uvicorn workers (`--workers=1` per GPU), backlog (`--backlog=2048`), and keep-alive timeout
- Profile with `py-spy` or `torch.profiler` to identify CPU-bound vs GPU-bound vs I/O-bound bottlenecks

```python
# locustfile.py — example load test for AI endpoint
from locust import HttpUser, task, between
import json

class AIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def chat_completion(self):
        self.client.post("/v1/chat", json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100,
        })
```

**Security considerations:**
- Run load tests against a staging environment, not production — production load tests risk overwhelming the shared LLM API quota and degrading service for real users
- Use test API keys with limited rate limits and budget caps — prevent runaway test costs. A locust run with 100 concurrent users for 1 hour on GPT-4 can cost $500+
- Anonymize test data — do not use real user data in load tests. Generate synthetic prompts that match the statistical properties of real traffic

**Performance considerations:**
- Model inference is usually the bottleneck, not the web framework — FastAPI adds 2-10ms overhead per request; model inference is 2000-10000ms. Optimize the model first (quantization, batching, smaller model) before optimizing FastAPI
- Uvicorn worker count: for GPU-bound services, 1 worker per GPU is optimal. More workers share the same GPU memory and cause OOM or GPU thrashing
- Connection pool tuning for LLM API calls: match the pool size (`httpx.AsyncClient(limits=PoolLimits(max_connections=100))`) to the LLM provider's concurrency limit
- Gunicorn vs Uvicorn: use `gunicorn -k uvicorn.workers.UvicornWorker` for CPU-bound services (needs multiple workers), use `uvicorn` directly for GPU-bound services (1 worker per GPU)

**Points to consider in design:**
- Establish a baseline before optimization — run a load test, identify the bottleneck, optimize it, then run again. Common bottlenecks in order: (1) LLM API rate limit, (2) GPU memory bandwidth, (3) model inference time, (4) database queries, (5) network latency
- Test with realistic data — short prompts with short responses under-report latency; long prompts with long responses show the real bottleneck. Use production log distributions for prompt and response length
- Load test the streaming path separately — streaming connections consume connection slots differently than non-streaming; `httpx.AsyncClient` handles streaming differently
- Set performance budgets — "p99 latency < 5s", "throughput > 10 RPS", "GPU utilization > 70%" — and monitor them in production. A regression in any metric is a performance incident

### OpenAPI Documentation Generation

**What it is:** FastAPI's automatic OpenAPI (Swagger) documentation generated from Pydantic models, route decorators, and docstrings. For AI services, the generated docs must clearly describe request/response schemas, streaming behavior, authentication requirements, error codes, and rate limits — enabling API consumers to integrate without reading source code.

**How to do it:**
- FastAPI generates OpenAPI docs automatically — visit `/docs` (Swagger UI) or `/redoc` (ReDoc) after starting the server
- Enhance auto-generated docs with `summary`, `description`, `tags`, and `response_description` on route decorators
- Add examples to Pydantic models — `Field(examples=["Hello, world!"])` — these appear in the Swagger UI "Try it out" section
- Use `operation_id` for stable API operation names — auto-generated names change when you rename functions, breaking generated clients

```python
@app.post(
    "/v1/chat",
    summary="Send a chat completion request",
    description="Generate a response from the LLM for a list of messages. Supports streaming.",
    tags=["chat"],
    response_description="The generated chat response with usage metadata",
    operation_id="createChatCompletion",
)
async def chat(request: ChatRequest, model: MyModel = Depends(get_model)):
    """Generate a chat completion.
    - Supports streaming via `stream: true`
    - Returns token usage in `usage` field
    - Rate limited to 100 RPM per API key
    """
    return await model.generate(request)
```

**Security considerations:**
- Disable `/docs` and `/redoc` in production environments — or protect them with authentication. These endpoints expose the full API schema, including internal endpoints, to anyone with access
- Do not include examples with real data — use generic placeholders. An example with a real customer query in the OpenAPI spec is a data leak
- Use `openapi_tags` with descriptions that do not reveal internal implementation details — "Chate endpoints" is fine; "GPT-4o with RAG using Company Internal Knowledge Base v3" is not

**Performance considerations:**
- OpenAPI generation happens once at startup — generating the OpenAPI schema from Pydantic models takes 10-100ms for a typical AI service with 10-20 endpoints. This adds to cold start time but does not affect runtime performance
- Disable OpenAPI generation in production if startup time is critical — set `openapi_url=None` in the FastAPI constructor and serve the OpenAPI spec as a static file generated during CI/CD
- The `/docs` and `/redoc` endpoints serve static HTML+JS — they add negligible latency and memory (~2MB served once per page load)

**Points to consider in design:**
- Use `responses` decorator parameter to document error responses — `responses={422: {"model": ChatErrorResponse}}` — so API consumers know what errors to expect
- Generate separate OpenAPI specs for internal vs public endpoints — use `include_in_schema=False` for internal routes that should not appear in consumer documentation
- Version the OpenAPI spec URL — `/v1/openapi.json` vs `/v2/openapi.json` — so that generated client libraries are always pinned to the correct version
- Consider using `Scalar` or `Swagger UI` alternative renderers — ReDoc is cleaner for complex AI APIs with many request/response schemas

## Production Deployment Checklist

| Area | Item | Pass | Fail |
|---|---|---|---|
| **Project Structure** | Modular layout with routes/, services/, models/ separation | Yes | Single app.py |
| **Model Loading** | Lifespan-based model load with warmup inference | Yes | Per-request model load or no warmup |
| **Async Endpoints** | `async def` for I/O-bound endpoints; thread pool for CPU-bound | Yes | Wrong pattern for workload type |
| **Input Validation** | Pydantic with `max_length`, `pattern`, `ge`/`le` constraints | Yes | No validation on string fields |
| **Streaming** | SSE with disconnect handling and final `[DONE]` event | Yes | No disconnect handling |
| **Rate Limiting** | Token-aware rate limiting (RPM + TPM) with Redis | Yes | Request-count only or in-memory |
| **Middleware** | Request ID propagation, latency tracking, CORS allowlist | Yes | Missing any of the three |
| **Health Checks** | `/health` (alive) + `/ready` (model loaded) endpoints | Yes | Missing one or both |
| **Security** | Non-root container, no secrets in image, CORS restricted | Yes | Any of the three violated |
| **Docker** | Multi-stage build, CUDA base, no weights baked in | Yes | Single-stage or weights in image |
| **Cloud Config** | GPU auto-scaling with min running replicas, health probes configured | Yes | Scale-to-zero GPU or no probes |
| **Load Testing** | Baseline established, bottleneck identified, performance budgets set | Yes | No load testing performed |
| **OpenAPI Docs** | Examples, error responses documented, production access disabled | Yes | Missing examples or exposed in production |
| **Logging** | Structured JSON logs with request ID, latency, tokens, and PII scrubbing | Yes | No structured logging or PII in logs |
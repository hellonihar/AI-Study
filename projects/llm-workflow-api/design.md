# LLM Workflow API — Design Document

## Overview

A FastAPI service that routes user queries to multiple LLM providers (OpenAI, Anthropic, local via Ollama) with caching, latency monitoring, and conversation history storage. This project demonstrates how backend engineering skills — API design, service abstraction, caching, monitoring, and async programming — transfer directly to AI system development.

---

## Architecture

```
                     ┌─────────────────────────────────────────┐
                     │           Client (curl, UI, SDK)         │
                     └────────────────┬────────────────────────┘
                                      │ HTTP / SSE
                                      ▼
                     ┌─────────────────────────────────────────┐
                     │           FastAPI (uvicorn)              │
                     │                                         │
                     │  ┌───────────────────────────────────┐  │
                     │  │         Middleware Stack           │  │
                     │  │  ┌─────────┐ ┌───────┐ ┌───────┐ │  │
                     │  │  │RequestID│ │Logger │ │RateLim│ │  │
                     │  │  └─────────┘ └───────┘ └───────┘ │  │
                     │  └───────────────────────────────────┘  │
                     │                                         │
                     │  ┌───────────────────────────────────┐  │
                     │  │         LLM Gateway (Router)       │  │
                     │  │                                         │
                     │  │  ┌──────────┐    ┌──────────────┐   │  │
                     │  │  │Cache Chk │◄──►│  Redis Cache  │   │  │
                     │  │  └──────────┘    └──────────────┘   │  │
                     │  │       │                              │  │
                     │  │  ┌────▼────┐                         │  │
                     │  │  │ Provider│──► OpenAI / Anthropic   │  │
                     │  │  │ Adapter │──► / Ollama             │  │
                     │  │  └─────────┘                         │  │
                     │  │       │                              │  │
                     │  │  ┌────▼────┐    ┌──────────────┐   │  │
                     │  │  │History  │───►│ PostgreSQL    │   │  │
                     │  │  │ Store   │    │ (messages)    │   │  │
                     │  │  └─────────┘    └──────────────┘   │  │
                     │  └───────────────────────────────────┘  │
                     └─────────────────────────────────────────┘
```

### Request Flow

1. Client sends a chat request to `POST /v1/chat/completions`
2. Middleware stack: generate `trace_id`, log request, check rate limit
3. Router selects the target provider based on request params or config
4. Cache check: if an identical request exists in Redis with matching cache key, return cached response immediately
5. Cache miss: provider adapter translates the unified request into provider-specific format and calls the LLM API
6. Response is written to Redis cache (with TTL) and to PostgreSQL conversation history
7. Middleware logs the final response with timing and token usage
8. Response is returned to the client — either as JSON or SSE stream

---

## Project Structure

```
projects/llm-workflow-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app creation, lifespan, middleware registration
│   ├── config.py                  # Settings via pydantic-settings
│   ├── schemas.py                 # Pydantic request/response models
│   ├── router.py                  # LLM provider selection logic (strategy pattern)
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                # Abstract base class: LLMProvider
│   │   ├── openai.py              # OpenAI adapter implementation
│   │   ├── anthropic.py           # Anthropic adapter implementation
│   │   └── ollama.py              # Local Ollama adapter implementation
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache.py               # Redis caching layer
│   │   ├── history.py             # Conversation history CRUD
│   │   └── monitor.py             # Latency and usage metrics
│   │
│   └── middleware/
│       ├── __init__.py
│       ├── request_id.py          # trace_id generation and propagation
│       ├── logging.py             # Structured request/response logging
│       └── rate_limit.py          # Token-aware rate limiting
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures: test client, mock providers
│   ├── test_routes.py             # Integration tests for API endpoints
│   └── test_providers.py          # Unit tests for provider adapters
│
├── docker-compose.yml             # FastAPI + Redis + PostgreSQL
├── Dockerfile                     # Multi-stage Python build
├── requirements.txt
└── README.md
```

---

## API Endpoints

### `POST /v1/chat/completions`

Primary endpoint for chat completions.

**Request:**
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "temperature": 0.7,
  "stream": false,
  "max_tokens": 1024,
  "session_id": "sess_abc123"
}
```

**Response (non-streaming):**
```json
{
  "id": "chatcmpl_xyz",
  "model": "gpt-4o",
  "provider": "openai",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 7,
    "total_tokens": 35
  },
  "trace_id": "tr_abc123",
  "latency_ms": 843
}
```

**Response (streaming — SSE):**
```
data: {"choices": [{"delta": {"content": "The"}}]}
data: {"choices": [{"delta": {"content": " capital"}}]}
data: [DONE]
```

### `GET /v1/sessions/{session_id}`

Retrieve full conversation history for a session.

### `GET /health`

Health check endpoint returning provider status and cache connectivity.

### `GET /v1/models`

List available models across all configured providers.

---

## Provider Abstraction Layer

### Base Interface (`providers/base.py`)

```python
class ChatResponse(TypedDict):
    content: str
    model: str
    provider: str
    usage: dict
    latency_ms: int

class StreamChunk(TypedDict):
    content: str
    finish_reason: str | None

class LLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @abstractmethod
    def supported_models(self) -> list[str]: ...

    @abstractmethod
    async def chat(self, messages: list[dict], model: str, **kwargs) -> ChatResponse: ...

    @abstractmethod
    async def chat_stream(self, messages: list[dict], model: str, **kwargs) -> AsyncIterator[StreamChunk]: ...
```

### Implementations

| Provider | SDK | Auth | Notes |
|---|---|---|---|
| OpenAI | `openai` | `OPENAI_API_KEY` | Supports parallel function calling |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` | Extended thinking mode available |
| Ollama | `httpx` (REST) | None (local) | Runs local models, no auth needed |

---

## Router Strategy

The router selects which provider handles a given request. Three strategies:

| Strategy | Selection Logic | Use Case |
|---|---|---|
| **Explicit** | User specifies `provider` in request body | User knows which model they want |
| **Model-based** | `model` name maps to a provider (e.g., `gpt-4o` → OpenAI) | Default — simplest |
| **Latency-based** | All providers capable of the model are tried simultaneously; first successful response wins | Low-latency critical paths |

---

## Caching Strategy

### Cache Key

```
cache_key = sha256(f"{model}:{serialize(messages)}:{temperature}:{max_tokens}")
```

### Behavior

| Scenario | Action | TTL |
|---|---|---|
| Cache hit (identical request) | Return cached response immediately | TTL reset |
| Cache miss | Call provider, store response, return | Set TTL |
| Streaming request | Do not cache (SSE is not idempotent) | N/A |

### Default TTLs

| Model | TTL |
|---|---|
| GPT-4o, Claude 3.5 Sonnet | 300s (5 min) |
| GPT-4o-mini, Claude Haiku | 600s (10 min) |
| Local models (Ollama) | 3600s (1 hour) |

---

## Conversation History

### PostgreSQL Schema

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    model TEXT,
    token_count INT,
    latency_ms INT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON messages(session_id, created_at);
```

### Context Window Management

When a session exceeds the model's context window, older messages are truncated following a strategy:
- Always keep the system message
- Keep the last N messages where N is calculated dynamically: `max_content_tokens = context_window - system_prompt_tokens - response_budget`
- Drop oldest user/assistant pairs first

---

## Monitoring & Observability

### Metrics (Prometheus)

| Metric | Type | Labels |
|---|---|---|
| `llm_requests_total` | Counter | `provider`, `model`, `status`, `streaming` |
| `llm_request_duration_seconds` | Histogram | `provider`, `model` (buckets: 0.1, 0.5, 1, 2, 5, 10, 30) |
| `llm_tokens_total` | Counter | `provider`, `model`, `type` (prompt/completion) |
| `llm_cache_hit_ratio` | Gauge | `provider`, `model` |

### Structured Logging

Every request produces a structured log line at completion:

```json
{
  "trace_id": "tr_abc123",
  "method": "POST",
  "path": "/v1/chat/completions",
  "provider": "openai",
  "model": "gpt-4o",
  "status": 200,
  "latency_ms": 843,
  "prompt_tokens": 28,
  "completion_tokens": 7,
  "cache_hit": false,
  "streaming": false,
  "error": null
}
```

---

## Error Handling

| Failure | Provider Action | API Response | HTTP Status |
|---|---|---|---|
| Rate limit (429) | Retry with exponential backoff (3 attempts) | `{"error": "rate_limited", "retry_after": 5}` | 429 |
| Provider down (5xx) | Fallback to next provider in priority list | `{"error": "provider_unavailable", "fallback_provider": "anthropic"}` | 200 (with warning) |
| Invalid request | No retry | `{"error": "invalid_request", "detail": "..."}` | 400 |
| Auth failure | No retry | `{"error": "auth_failed"}` | 500 |
| Timeout (30s) | Retry once with extended timeout | `{"error": "timeout"}` | 504 |

---

## Tech Stack

| Component | Choice | Justification |
|---|---|---|
| Framework | FastAPI + uvicorn | Async-native, Pydantic validation, automatic OpenAPI docs |
| Cache | Redis (via `redis-py`) | Low-latency, TTL support, industry standard for caching |
| Conversation store | PostgreSQL (via `asyncpg`) | ACID guarantees, JSONB for flexible metadata, production-grade |
| Provider SDKs | `openai`, `anthropic`, `httpx` (Ollama) | Official SDKs with async support |
| Metrics | `prometheus-fastapi-instrumentator` | Exposes `/metrics` endpoint compatible with Prometheus + Grafana |
| Containerization | Docker + docker-compose | FastAPI app + Redis + PostgreSQL in one command |
| Testing | pytest + httpx + respx | `pytest` for test runner, `respx` for HTTP mock, `httpx` for async test client |

---

## Configuration (`config.py`)

```python
class Settings(BaseSettings):
    # App
    app_name: str = "LLM Workflow API"
    debug: bool = False

    # Providers
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # Cache (Redis)
    redis_url: str = "redis://localhost:6379/0"
    cache_default_ttl: int = 300

    # Database (PostgreSQL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/llm_workflow"

    # Rate limiting
    rate_limit_per_minute: int = 60

    # Router
    default_provider: str = "openai"
    fallback_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env")
```

---

## Files to Build (Implementation Order)

| Phase | Files | What Each Does |
|---|---|---|
| **1** | `config.py`, `schemas.py` | Settings model, Pydantic request/response types |
| **2** | `main.py` | FastAPI app creation, lifespan events, middleware stack assembly |
| **3** | `providers/base.py`, `providers/openai.py`, `providers/anthropic.py`, `providers/ollama.py` | Provider abstraction and concrete implementations |
| **4** | `router.py` | Provider selection strategy |
| **5** | `middleware/request_id.py`, `middleware/logging.py`, `middleware/rate_limit.py` | Request lifecycle middleware |
| **6** | `services/cache.py` | Redis cache layer |
| **7** | `services/history.py` | PostgreSQL conversation store |
| **8** | `services/monitor.py` | Prometheus metrics instrumentation |
| **9** | `Dockerfile`, `docker-compose.yml` | Container orchestration |
| **10** | Tests, `README.md` | Verification and documentation |

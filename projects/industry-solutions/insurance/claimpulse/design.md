# ClaimPulse — Design Document

## Overview

ClaimPulse is an AI-powered claims processing system that reduces average cycle time from 14 days to under 3 days through a multi-stage pipeline: document intelligence extracts structured data from claim forms, computer vision assesses photo-based damage, gradient-boosted models score fraud risk, and a self-hosted LLM generates settlement recommendations — all running on CPU-only infrastructure. Every AI output is explainable and reviewable by a human adjuster.

---

## Project Structure

```
claimpulse/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application factory
│   ├── config.py                # Settings via pydantic-settings
│   ├── dependencies.py          # DB session, auth, rate limit deps
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── claims.py            # /api/claims/* CRUD
│   │   ├── intake.py            # /api/claims/upload, /ui/intake
│   │   ├── assessment.py        # /api/claims/{id}/assess
│   │   ├── fraud.py             # /api/claims/{id}/fraud
│   │   ├── settlement.py        # /api/claims/{id}/settle
│   │   ├── dashboard.py         # /ui/dashboard, /ui/queue
│   │   ├── analytics.py         # /ui/analytics
│   │   └── admin.py             # /ui/admin
│   ├── models/
│   │   ├── __init__.py
│   │   ├── claim.py             # SQLAlchemy: Claim, Document, Photo
│   │   ├── assessment.py        # SQLAlchemy: DamageAssessment
│   │   ├── fraud.py             # SQLAlchemy: FraudScore, FraudFeature
│   │   ├── settlement.py        # SQLAlchemy: SettlementRecommendation
│   │   └── audit.py             # SQLAlchemy: AuditLog
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── claim.py             # Pydantic: ClaimCreate, ClaimResponse
│   │   ├── assessment.py        # Pydantic: AssessmentResponse
│   │   ├── fraud.py             # Pydantic: FraudScoreResponse
│   │   ├── settlement.py        # Pydantic: SettlementResponse
│   │   └── pagination.py        # Pydantic: Page, PageParams
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_ai.py       # PaddleOCR client + BERT NER
│   │   ├── image_ai.py          # YOLOv8-nano ONNX runtime
│   │   ├── fraud_engine.py      # XGBoost ONNX + SHAP explainer
│   │   ├── settlement_llm.py    # llama.cpp HTTP client
│   │   ├── embedding.py         # bge-small-en ONNX
│   │   └── compliance.py        # State regulatory matrix
│   ├── templates/               # Jinja2 + HTMX
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── claim_detail.html
│   │   ├── intake.html
│   │   ├── queue.html
│   │   ├── fraud_console.html
│   │   ├── analytics.html
│   │   └── admin.html
│   └── static/
│       ├── css/
│       └── js/
│           └── alpine-init.js   # Alpine.js components
├── workers/
│   ├── __init__.py
│   ├── celery_app.py            # Celery config + task definitions
│   ├── document_worker.py       # process_document task
│   ├── image_worker.py          # assess_damage task
│   ├── fraud_worker.py          # score_fraud task
│   └── settlement_worker.py     # recommend_settlement task
├── models/                      # ML model artifacts
│   ├── bert-ner/                # Fine-tuned BERT-base
│   ├── yolov8n.onnx             # YOLOv8-nano ONNX export
│   ├── xgb_fraud.onnx           # XGBoost ONNX export
│   ├── bge-small.onnx           # Embedding model
│   └── llama-3-8b-q4.gguf      # Llama 3 8B GGUF (git LFS)
├── migrations/                  # Alembic
│   ├── alembic.ini
│   └── versions/
├── tests/
│   ├── test_routes/
│   ├── test_workers/
│   └── test_models/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## Architecture

```
                         ┌─────────────────────────────────┐
                         │     FastAPI + Jinja2 (8 workers)  │
                         │  /api/* REST · /ui/* HTMX · /ws  │
                         │  Keycloak OAuth · Rate Limiting   │
                         └────────┬────────────────────────┘
                                  │ Celery tasks
                     ┌────────────▼────────────────────────┐
                     │         RabbitMQ / Celery             │
                     │   (task routing by claim stage)       │
                     └───┬───────────┬───────────┬──────────┘
                         │           │           │
               ┌─────────▼───┐ ┌─────▼─────┐ ┌──▼──────────┐
               │ Document    │ │ Image     │ │ Fraud +      │
               │ AI Worker   │ │ Worker    │ │ Settlement   │
               │ (CPU, 8GB)  │ │ (CPU,4GB) │ │ Worker       │
               │             │ │           │ │ (CPU, 16GB)  │
               │ PaddleOCR   │ │ YOLOv8-   │ │              │
               │ → BERT NER  │ │ nano ONNX │ │ XGBoost ONNX │
               │ → pgvector  │ │ → severity│ │ → llama.cpp  │
               └─────────────┘ └───────────┘ │ → SHAP       │
                                              └──────────────┘
                         ┌─────────────────────────────────┐
                         │     Shared Data Layer            │
                         │  PostgreSQL + pgvector           │
                         │  MinIO (documents + photos)       │
                         │  Redis (cache + rate limits)      │
                         └─────────────────────────────────┘
                         ┌─────────────────────────────────┐
                         │     Observability                │
                         │  Prometheus · Grafana · Loki     │
                         │  OpenTelemetry · Tempo (traces)  │
                         └─────────────────────────────────┘
```

---

## Data Models

### Claim (PostgreSQL)

```sql
CREATE TABLE claims (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number    VARCHAR(32) UNIQUE NOT NULL,
    policy_number   VARCHAR(32) NOT NULL,
    claimant_id     UUID NOT NULL,
    date_of_loss    DATE NOT NULL,
    loss_type       VARCHAR(32) NOT NULL,  -- 'property' | 'auto' | 'health' | 'liability'
    status          VARCHAR(32) NOT NULL DEFAULT 'SUBMITTED',
    -- status machine: SUBMITTED → DOCUMENTED → ASSESSED → FRAUD_SCORED → SETTLEMENT_READY → APPROVED | DENIED
    amount_requested DECIMAL(12,2),
    amount_settled  DECIMAL(12,2),
    adjuster_id     UUID,
    assigned_at     TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID REFERENCES claims(id),
    file_path       VARCHAR(512) NOT NULL,       -- MinIO object key
    doc_type        VARCHAR(32),                 -- 'claim_form' | 'invoice' | 'police_report' | 'medical_record'
    ocr_text        TEXT,                        -- PaddleOCR output
    extracted_fields JSONB,                      -- BERT NER output: {policy_number, date_of_loss, provider, ...}
    extraction_confidence FLOAT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE photos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID REFERENCES claims(id),
    file_path       VARCHAR(512) NOT NULL,       -- MinIO object key
    damage_regions  JSONB,                       -- YOLO: [{bbox, class, confidence}, ...]
    severity        VARCHAR(16),                 -- 'minor' | 'moderate' | 'severe' | 'total_loss'
    severity_confidence FLOAT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE fraud_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID UNIQUE REFERENCES claims(id),
    probability     FLOAT NOT NULL,              -- [0, 1]
    risk_level      VARCHAR(16) GENERATED ALWAYS AS
                    (CASE WHEN probability < 0.2 THEN 'LOW'
                          WHEN probability > 0.7 THEN 'HIGH'
                          ELSE 'MEDIUM' END) STORED,
    shap_values     JSONB NOT NULL,              -- {feature_name: shap_value, ...}
    model_version   VARCHAR(32) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE settlement_recommendations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID UNIQUE REFERENCES claims(id),
    recommended_amount DECIMAL(12,2) NOT NULL,
    confidence      VARCHAR(8) NOT NULL,         -- 'low' | 'medium' | 'high'
    reasoning       TEXT NOT NULL,                -- LLM chain-of-thought
    risk_factors    JSONB,                       -- ["policy limit ambiguity", "...
    model_version   VARCHAR(32) NOT NULL,
    overridden      BOOLEAN DEFAULT FALSE,
    override_amount DECIMAL(12,2),
    override_reason TEXT,
    overridden_by   UUID,                        -- adjuster_id
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID REFERENCES claims(id),
    event_type      VARCHAR(64) NOT NULL,        -- 'claim.created' | 'document.extracted' | 'fraud.scored' | 'settlement.recommended' | 'adjuster.override' | ...
    actor_id        UUID,                        -- user or system
    payload         JSONB,                       -- event-specific data
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_claim ON audit_log(claim_id, created_at);
```

---

## API Design

### REST Endpoints

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| `POST` | `/api/claims` | Create claim | `{claim_number, policy_number, claimant_id, date_of_loss, loss_type}` | `201: ClaimResponse` |
| `GET` | `/api/claims` | List claims (paginated) | `?page=1&size=50&status=SUBMITTED` | `Page<ClaimResponse>` |
| `GET` | `/api/claims/{id}` | Get claim detail | — | `ClaimDetailResponse` |
| `POST` | `/api/claims/{id}/upload` | Upload docs/photos | `multipart: files[]` | `202: {task_id}` |
| `GET` | `/api/claims/{id}/documents` | List extracted documents | — | `Document[]` |
| `GET` | `/api/claims/{id}/photos` | List photos with damage overlay | — | `Photo[]` |
| `GET` | `/api/claims/{id}/fraud` | Get fraud score + SHAP | — | `FraudScoreResponse` |
| `GET` | `/api/claims/{id}/settlement` | Get LLM recommendation | — | `SettlementResponse` |
| `PUT` | `/api/claims/{id}/settle` | Adjuster override | `{amount, reason}` | `SettlementResponse` |
| `PATCH` | `/api/claims/{id}/status` | Advance state machine | `{status}` | `ClaimResponse` |

### WebSocket Events

| Event | Direction | Payload |
|---|---|---|
| `claim.status_changed` | Server → Client | `{claim_id, old_status, new_status}` |
| `claim.progress` | Server → Client | `{claim_id, step, progress_pct}` |
| `dashboard.refresh` | Server → Client | `{metric_name, new_value}` |

---

## Pipeline State Machine

```
                    ┌──────────┐
                    │ SUBMITTED│
                    └────┬─────┘
                         │ PaddleOCR + BERT NER
                    ┌────▼──────┐
                    │ DOCUMENTED│
                    └────┬──────┘
                         │ YOLOv8-nano (property/auto claims)
                    ┌────▼──────┐
                    │ ASSESSED  │
                    └────┬──────┘
                         │ XGBoost ONNX + SHAP
                    ┌────▼─────────┐
                    │ FRAUD_SCORED │
                    └────┬─────────┘
                         │ llama.cpp + prompt
                    ┌────▼───────────┐
                    │ SETTLEMENT_READY│
                    └────┬───────────┘
                         │ Adjuster reviews
                    ┌────▼────┐  ┌─────┐
                    │ APPROVED│  │DENIED│
                    └─────────┘  └─────┘
```

Transitions are driven by Celery task completion. Each task publishes a `claim.status_changed` event via WebSocket. If a task fails (e.g., OCR timeout), the claim transitions to `ERROR` and the adjuster is notified.

---

## Components

### FastAPI Application

- **8 Uvicorn workers** behind a reverse proxy (Caddy/Traefik)
- **Middleware**: CORS, rate limiting (Redis-backed), request ID, OpenTelemetry tracing, audit logging
- **Auth**: Keycloak OAuth 2.0 with RBAC — roles: `adjuster`, `manager`, `admin`
- **Templating**: Jinja2 with HTMX for dynamic partial swaps; Alpine.js for client-side reactivity (sliders, multi-step wizards)

### Celery Workers

| Worker | Concurrency | Resource | Task | Latency |
|---|---|---|---|---|
| `document_worker` | 4 processes | CPU, 8GB | PaddleOCR → BERT NER → pgvector embed | ~5s/doc |
| `image_worker` | 2 processes | CPU, 4GB | YOLOv8-nano ONNX → severity classifier | ~1s/photo |
| `fraud_worker` | 2 processes | CPU, 4GB | XGBoost ONNX → SHAP explainer | <100ms |
| `settlement_worker` | 1 process | CPU, 16GB | llama.cpp client → prompt assembly → structured parse | ~15s |

### Celery (Task Queue)

Celery is a distributed task queue that executes asynchronous work outside the HTTP request-response cycle. In ClaimPulse, every claim processing step — OCR extraction, damage assessment, fraud scoring, settlement generation — is dispatched as a Celery task and executed by a dedicated worker pool.

**Why Celery over alternatives**:
- **Airflow**: Better for complex DAGs with backfill and retry logic, but adds a database-backed scheduler with minute-level latency. ClaimPulse's pipeline is event-driven (triggered per-claim, not scheduled), so Airflow's scheduling model offers no advantage.
- **Temporal**: Superior saga orchestration with automatic retries and compensation. ClaimPulse's pipeline has 6 sequential steps with no parallel forks and simple compensation (set claim status to ERROR). Temporal's gRPC + Go binary would double the infrastructure surface for no benefit.
- **Threading/background tasks**: Block the event loop and don't survive process restarts. Celery workers are independent processes that can be scaled, failed, and restarted independently.

**Celery Task Flow**

Unlike scheduled pipelines, ClaimPulse tasks are chained by claim state transitions:

```
process_document ──► assess_damage ──► score_fraud ──► recommend_settlement
       │                  │                │                    │
       ▼                  ▼                ▼                    ▼
  claim → DOCUMENTED  claim → ASSESSED  claim → FRAUD_SCORED  claim → SETTLEMENT_READY
```

Each task is triggered by the previous task's completion via Celery's `chain()` primitive. Tasks are not on a timer — they fire as claims arrive. If a task fails, the claim transitions to `ERROR` and the adjuster is notified (no automatic retry for claims processing — manual intervention prevents compounding errors).

**Celery Beat Schedule**

ClaimPulse has minimal scheduled work — only accuracy monitoring runs on a timer. The rest is event-driven:

```python
# workers/celery_app.py
from celery import Celery
from celery.schedules import crontab

app = Celery("claimpulse")
app.config_from_object("app.config")

app.conf.beat_schedule = {
    "compute-daily-metrics": {
        "task": "workers.metrics_worker.compute_daily_metrics",
        "schedule": crontab(minute="0", hour="2"),
        "options": {"queue": "metrics", "expires": 3600},
    },
    "check-model-drift": {
        "task": "workers.metrics_worker.check_model_drift",
        "schedule": crontab(minute="0", hour="3", day_of_week="sun"),
        "options": {"queue": "metrics", "expires": 7200},
    },
}
```

All claim processing tasks use dynamic routing via Celery's `task_always_routing` setting — tasks are dispatched to queues named `document`, `image`, `fraud`, and `settlement` based on the task name, allowing each worker to scale independently.

**How it runs**: A `celery beat` container pushes the two scheduled metric tasks to RabbitMQ. Claim processing tasks are pushed directly by the FastAPI application or by the previous Celery task in the chain. Worker containers pull from their respective queues. This separation means each worker can be scaled, updated, or failed independently.

### Frontend (Server-Rendered)

All UI served as Jinja2 templates. HTMX attributes control dynamic behavior:

| Screen | Route | HTMX Trigger | Update Target |
|---|---|---|---|
| Dashboard | `/ui/dashboard` | `hx-trigger="every 30s"` | `#metric-cards`, `#sparklines` |
| Claim Detail | `/ui/claim/{id}` | `hx-trigger="load"` | `#timeline`, `#doc-viewer` |
| Settlement | `/ui/claim/{id}/settle` | `hx-trigger="change"` from Alpine.js | `#settlement-panel` |
| Queue | `/ui/queue` | `hx-trigger="input"` on filters | `#claim-table` |
| Fraud Console | `/ui/fraud` | `hx-trigger="every 15s"` | `#fraud-cards` |
| Analytics | `/ui/analytics` | `hx-trigger="change"` on date picker | `#chart-container` |

Alpine.js handles three pieces of client-side state:
- Settlement slider amount (reactive display while user drags)
- Photo gallery zoom/pan
- Multi-step intake wizard step index

---

## Design Decisions & Trade-offs

### 1. CPU-only Inference (No GPU)

**Context**: The target deployment environment has no GPU available. Every ML component was evaluated for CPU feasibility.

| Decision | Chosen | Rejected | Rationale |
|---|---|---|---|
| LLM deployment | llama.cpp + Llama 3 8B (GGUF Q4_K_M) | vLLM + Llama 3 70B | 70B requires 140GB RAM and A100 GPU. 8B Q4 runs at 8–12 tok/s on CPU — acceptable for async settlement (15s latency tolerated). |
| Document extraction | PaddleOCR + BERT-base NER | LayoutLMv3 | LayoutLMv3 needs T4 GPU for batch inference. PaddleOCR server mode achieves 8 pages/sec on CPU with 4 workers. |
| Damage photo analysis | YOLOv8-nano ONNX | YOLOv8-large, YOLOv8x | Nano variant is 2MB, runs 30fps on CPU. 5–8% mAP loss vs. large — acceptable for claims triage where false negatives are caught by adjuster review. |
| Fraud scoring | XGBoost → ONNX Runtime (quantized) | PyTorch TabNet, XGBoost native | ONNX quantized inference is 3× faster than XGBoost native on CPU (<1ms per claim). PyTorch TabNet requires GPU for practical training and inference. |

**Failure mode**: If CPU load exceeds 90% on the settlement worker, claims queue in RabbitMQ. Mitigation: horizontal scaling of settlement workers across 2+ nodes.

### 2. Document AI: PaddleOCR + BERT over LayoutLMv3

**LayoutLMv3** (the state-of-the-art for document understanding) was rejected despite superior accuracy:

- **GPU dependency**: 10 claims/min requires a T4 GPU minimum. No GPU available.
- **Cold start**: 12–15 second model load on CPU — prohibitive for sporadic traffic patterns common in claims intake.
- **Ops burden**: CUDA/cuDNN runtime, GPU driver lifecycle, and GPU-optimized Docker images add significant operational complexity for a team managing CPU-only infrastructure.

**PaddleOCR server mode** (chosen):
- Runs as a persistent process with 4 workers, pre-loaded model, warm inference
- 8 pages/second on CPU with average modern x86 processor
- Intermediate OCR text output enables human review of extraction failures (transparency)

**BERT-base NER** (fine-tuned on 10K labeled claim forms):
- Extracts: policy_number, date_of_loss, provider_name, diagnosis_codes, amount_requested
- 15ms inference per document on CPU
- 92% F1 on held-out test set (vs. 94% for LayoutLMv3 — acceptable 2% gap for CPU feasibility)

**Alternative considered — Donut (HuggingFace)**: OCR-free, end-to-end document transformer. Rejected because:
- Also GPU-dependent (no CPU mode)
- Harder to debug: no intermediate OCR output means extraction errors are a black box
- Fine-tuning requires 10× more data than BERT NER

### 3. Settlement LLM: Self-hosted on CPU

**Constraint**: PHI/PII in claim data means no API call can leave the network without data boundary agreements with every state DOI.

| Consideration | Weight | Decision |
|---|---|---|
| Data privacy | Critical | Self-hosted. No data leaves the network. |
| Regulatory audit | Critical | Full prompt + response logged to local disk. Cloud APIs add compliance ambiguity for state insurance departments. |
| Latency tolerance | Medium | Settlement is async (Celery). 15–30 seconds is acceptable — adjuster works on other claims while waiting. |
| Accuracy | Medium | Llama 3 8B matches GPT-3.5 on structured settlement extraction in internal benchmarks (n=500 claim samples). |

**Why llama.cpp over alternatives**:
- **vLLM**: Requires GPU for PagedAttention. Rejected.
- **Ollama**: Good DX but less control over batch size, context length presets, and KV cache management. llama.cpp server exposes the full parameter surface.
- **Azure OpenAI / GPT-4o**: 50-state DOI data boundary agreements would take 6+ months to negotiate. Per-claim cost (~$0.15) doesn't scale at 10M claims/year.
- **Mistral 7B GGUF**: 5% lower F1 on structured extraction in our eval. Only 4GB RAM savings vs. Llama 3 8B — not worth the accuracy loss.

**Prompt structure** (simplified):

```
SYSTEM: You are a claims settlement advisor for a P&C insurance carrier.
Given the claim details, policy limits, damage assessment, fraud risk,
and similar past settlements, recommend a settlement amount.

Claim: {claim_number} | Loss: {loss_type} | Date: {date_of_loss}
Policy Limit: ${policy_limit}
Damage Severity: {severity} | Estimated Cost: ${estimated_cost}
Fraud Risk: {fraud_probability:.0%} | Risk Factors: {top_shap_features}
Similar Settlements: {top_3_similar_claims}

OUTPUT JSON:
{
  "recommended_amount": <float>,
  "confidence": "<low|medium|high>",
  "reasoning": "<2-3 sentences>",
  "risk_factors": ["<factor1>", "<factor2>"]
}
```

**Prompt engineering notes**:
- Structured JSON output parsed with regex fallback
- Few-shot examples included in system prompt (2 examples, sampled by loss_type)
- Token budget: 2048 max tokens, average response ~350 tokens
- Temperature: 0.2 (low variance, deterministic for audit trail)

### 4. Frontend: Server-Rendered (HTMX + Alpine.js) over React

| Decision | Chosen | Rejected | Rationale |
|---|---|---|---|
| Rendering | FastAPI + Jinja2 + HTMX | Next.js, Nuxt, SvelteKit | Single Python deployment, one Docker image. No Node.js build step, no SSR server, no bundle splitting. HTMX swaps HTML fragments over WebSocket. |
| Charts | Chart.js (CDN) | Recharts, D3.js, Nivo | No bundler or npm needed. Chart.js loaded from CDN, data fetched via HTMX `hx-trigger`. |
| UI framework | Alpine.js + custom CSS | shadcn/ui, Material UI, DaisyUI | Alpine.js is 15KB gzipped — no build step. Matches the server-rendered philosophy of minimal JS. Custom CSS keeps the bundle under 30KB. |

**Why not React**: This is an internal adjuster tool, not a public-facing SPA. The complexity tax of a React SPA — npm audit, build tooling (Vite/Webpack), state management (Redux/Zustand), bundle splitting, SSR for SEO (irrelevant for internal tools) — adds ~2 weeks of setup time and ongoing maintenance burden. HTMX + Alpine.js delivers comparable interactivity with ~80% less frontend code and zero build tooling.

**Why not HTMX-only**: Alpine.js is needed for:
- Settlement slider: real-time amount display while dragging (HTMX round-trip would lag)
- Photo zoom/pan: client-side transform matrix, not a server concern
- Multi-step intake wizard: step index and validation state are UI-only

**Why not FastAPI + Jinja2 only** (no JS framework): The settlement slider and photo annotator require client-side state that HTMX's server-round-trip model cannot handle at interactive speeds. A minimal reactive layer (Alpine.js) fills this gap without pulling in a full framework.

### 5. pgvector over Dedicated Vector Database

| Alternative | Status | Why Rejected |
|---|---|---|
| **Qdrant** | Considered | Excellent performance and filtering, but adds a separate Docker service with its own persistence, backup, and monitoring surface. |
| **Pinecone** | Considered | Managed SaaS — data leaves the network. Rejected for PHI/PII compliance. |
| **pgvector** | Chosen | Extension on existing PostgreSQL. No new service. Performance is within 15% of Qdrant at <1M vectors (our scale). One less system to operate. |

### 6. Celery over Temporal

| Dimension | Celery + RabbitMQ | Temporal |
|---|---|---|
| Saga orchestration | Manual via task chains + callbacks | First-class: workflow as code, automatic retries, compensation |
| Infrastructure | RabbitMQ (single service) | Temporal Server + gRPC + PostgreSQL + Go binary |
| Language support | Python native | Python SDK + gRPC stubs |
| Team familiarity | High | Low |
| Decision | **Chosen** | Rejected |

Temporal is objectively superior for saga orchestration, but Celery + RabbitMQ is sufficient for this workflow depth (6 steps, no parallel forks, simple compensation) and keeps the stack Python-only with no additional gRPC infrastructure.

---

## Technology Alternatives Considered

Every technology choice in ClaimPulse was evaluated against alternatives across six dimensions: operational complexity, team familiarity, scalability, cost, ecosystem fit, and production maturity. The table covers all major layers of the stack.

| Layer | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| **API Framework** | FastAPI + Uvicorn | **Django REST**: Mature ORM, admin panel, but synchronous by default — WebSocket support requires Django Channels (separate ASGI server). Heavier cold start (~200ms). Admin panel is irrelevant for an API that serves HTMX fragments. <br><br> **Flask**: Familiar but no native async — SSE for dashboard refresh requires gevent or similar workaround. No automatic OpenAPI docs. Would need Flask-Smorest + Connexion + gevent to match FastAPI. <br><br> **Node.js/Express**: Strong async I/O, excellent WebSocket support natively. But the team is Python-first across all ML and backend services — adding Node.js splits CI/CD, monitoring, and on-call across two runtimes. | FastAPI is Python-native (team runs Python for all ML), natively async for WebSocket push and SSE dashboard updates, auto-generates OpenAPI docs, and its Pydantic integration eliminates a separate schema layer. |
| **Frontend** | FastAPI + Jinja2 + HTMX + Alpine.js | **Next.js (React)**: Requires a Node.js build step, SSR server, npm dependency audit, bundle splitting. For an internal adjuster tool (not a public-facing SPA), this complexity tax adds ~2 weeks of setup and ongoing build maintenance. The interactive needs (slider, zoom, wizard steps) are solved by Alpine.js at 15KB gzipped — no framework needed. <br><br> **SvelteKit**: Lighter than Next.js but still requires Node.js build tooling, SSR server, and npm. Svelte's reactivity model is excellent but overkill for a dashboard with 6 screens. <br><br> **Vue + Nuxt**: Same complexity profile as Next.js — build step, SSR, bundle splitting, Vuex/Pinia for state management. Alpine.js does the same job at 1% of the bundle size. | HTMX provides server-driven dynamic HTML swaps with zero client-side state. Alpine.js handles the 3 pieces of client-side interactivity (slider drag, photo zoom, wizard steps) that HTMX can't. Chart.js loaded from CDN eliminates the npm dependency entirely. Single Python deployable — one Docker image, no Node.js. |
| **Database** | PostgreSQL + pgvector | **MongoDB**: Document model fits claim data naturally (nested documents, photos, assessments). But claim data has strong relational structure — claims reference policies, adjusters, loss types. Joins in MongoDB are less performant than PostgreSQL at <10M document scale. No pgvector equivalent — vector embeddings would require a separate Atlas Search index. <br><br> **CockroachDB**: Distributed PostgreSQL-compatible with horizontal scaling. Adds operational complexity (3+ node cluster minimum, specialized monitoring). ClaimPulse's write volume (~10K claims/day) fits comfortably on a single PostgreSQL instance — distribution adds cost without benefit. <br><br> **MySQL**: Mature, well-understood, but weaker JSON support, no native vector extension, and no pgvector equivalent. Full-text search is less capable than PostgreSQL's. | PostgreSQL provides JSONB for semi-structured extraction output, pgvector for embedding similarity (similar claims, cold-start), and full-text search for document content lookup — all in a single database. The team already operates PostgreSQL for the core claims system. |
| **Object Store** | MinIO | **AWS S3**: Managed, zero ops, durable. But claim documents contain PHI/PII — some states require data to remain within specific geographic boundaries that S3 cannot guarantee without additional S3 Object Lock configuration. MinIO provides an S3-compatible API that can run on-premise or in a specific cloud region with guaranteed data residency. <br><br> **Azure Blob / GCS**: Cloud-locked — cannot run in air-gapped or on-premise deployments required by some state insurance departments. MinIO runs anywhere Docker runs. <br><br> **Local filesystem (NAS)**: No built-in versioning, replication, or S3-compatible API. Document retention policies (HIPAA: 6yr, P&C: 3yr) would require custom lifecycle management. | MinIO is S3-compatible at the API level (boto3 SDK works unchanged), supports versioning, object locking for compliance, and lifecycle policies for automated retention. Runs as a single Docker container. Zero lock-in — switch to S3 by changing the endpoint URL if cloud deployment becomes viable. |
| **Vector Store** | pgvector | **Qdrant**: Excellent filtering (full-text + vector pre-filtering), dedicated binary with gRPC API. Adds a separate Docker service with its own persistence, replication, and monitoring surface. At ClaimPulse's scale (~1M claim embeddings, 384 dimensions), Qdrant's throughput advantage is irrelevant — pgvector HNSW queries complete in <10ms. <br><br> **Pinecone**: Managed SaaS — zero ops, excellent performance. Claim embeddings are derived from PHI-containing documents — uploading them to a third-party service would require data processing agreements with every state DOI. Also adds ~$200/month for a task that runs a few hundred times per day. <br><br> **Milvus**: Purpose-built vector DB with GPU acceleration. Significant ops burden (etcd, Kafka, MinIO as Milvus dependencies). Designed for billion-scale — overkill for 1M claim embeddings. | pgvector is an extension on existing PostgreSQL — no new service, no new backup procedure, no new monitoring. Performance (<10ms for 1M vectors with HNSW index) is well within requirements for claim similarity search triggered per-claim. |
| **Auth / Identity** | Keycloak | **Auth0**: Excellent DX, social login, MFA out of the box. $0 starter tier but costs scale with active adjusters. Data residency is a concern — claimant PII in auth tokens or user profiles may need to remain within specific jurisdictions. Vendor lock-in: migrating off Auth0 requires rebuilding all OIDC flows. <br><br> **Azure AD / Entra ID**: Already used for corporate email. Good integration but license cost per external user (independent adjusters, third-party administrators) adds overhead. No self-service registration for external partners. <br><br> **DIY with JWT + bcrypt**: Simple, no dependencies. But no MFA, no LDAP sync, no session management, no social login for external adjusters. Building these from scratch adds 3-4 weeks of security-critical development and ongoing audit burden. | Keycloak is self-hosted, open-source, OIDC-compliant, and supports MFA, LDAP sync, and client-scoped roles out of the box. Runs as a single Docker container with PostgreSQL backing. Zero vendor lock-in — any OIDC provider replaces it by changing the well-known URL. |
| **LLM Inference** | llama.cpp + Llama 3 8B | **vLLM + Llama 3 70B**: Higher accuracy and throughput for batch inference. Requires A100 GPU (80GB) — $3-4/hour on cloud, not available in the target on-premise environment. 70B model requires 140GB RAM for KV cache — exceeds available hardware. <br><br> **Azure OpenAI / GPT-4o**: Excellent accuracy, zero ops. But 50-state DOI data boundary agreements for PHI would take 6+ months to negotiate. Per-claim cost (~$0.15) at 10M claims/year = $1.5M — more than the entire ClaimPulse infrastructure cost. <br><br> **Ollama**: Good DX (single binary, model pull, OpenAI-compatible API). Less control over batch size, context length presets, and KV cache management than llama.cpp. Ollama abstracts away the underlying server — fine for development but limits production debugging. | llama.cpp provides full control over inference parameters (batch size, GPU layers, context length) via its C-style API, runs on CPU with Q4_K_M quantization at 8-12 tok/s, and integrates as a persistent server process. No GPU required, no data leaves the network, no per-claim API cost. |
| **Document OCR** | PaddleOCR (server mode) | **Tesseract**: Open-source, well-understood, runs on CPU. But Tesseract's accuracy on claim forms (dense text, tables, checkboxes, handwriting) is significantly lower — ~75% character accuracy vs. PaddleOCR's ~92% in internal benchmarks. PaddleOCR's differentiable binarization handles curved text and varied lighting better. <br><br> **Azure Form Recognizer / AWS Textract**: Managed OCR with pre-built claim form models. Excellent accuracy (~95%). Data leaves the network — claim forms contain PHI. Per-page cost (~$0.05) at 10K claims/month × 5 pages per claim = $2,500/month. <br><br> **Google Document AI**: Similar value proposition to Azure/AWS — managed, accurate, but PHI data handling adds compliance complexity and per-document cost. | PaddleOCR server mode runs as a persistent process (4 workers, pre-loaded model) achieving 8 pages/second on CPU with 92% character accuracy. Intermediate OCR text output enables human review of extraction failures. Zero per-page cost. Zero data egress. |
| **Document NER** | BERT-base (HuggingFace) | **LayoutLMv3**: State-of-the-art for document understanding — jointly models text and layout. Requires T4 GPU for practical inference (10 claims/min). 12-15s cold start on CPU. CUDA runtime adds ops burden. 2% F1 improvement over BERT-base (94% vs. 92%) is not worth the GPU dependency at ClaimPulse's scale. <br><br> **Donut (HuggingFace)**: OCR-free end-to-end document transformer. No intermediate OCR output — extraction errors are a black box. Also GPU-dependent. Fine-tuning requires 10× more labeled data than BERT NER. <br><br> **spaCy NER**: Fast, efficient, good for general-purpose entity extraction. Pre-trained models lack insurance-specific entities (policy_number, NAIC code, ICD codes). Custom training requires significantly more labeled data than BERT fine-tuning. | BERT-base fine-tuned on 10K labeled claim forms achieves 92% F1 on held-out test set with 15ms inference on CPU. Extracts policy_number, date_of_loss, provider_name, diagnosis_codes, amount_requested. Familiar HuggingFace ecosystem — the team has fine-tuned BERT for 2 prior projects. |
| **Image Analysis** | YOLOv8-nano ONNX | **YOLOv8-large**: Higher mAP (~52% vs. ~45% for nano). 10× larger model file (20MB vs. 2MB), requires T4 GPU for real-time inference. At 10K claims/month (1-3 photos each), throughput is not a bottleneck — nano on CPU handles the volume. <br><br> **ResNet-50 classifier**: Single-label classification (damage type) with no localization. Cannot identify which part of the photo contains damage — bounding boxes are critical for adjuster review and trust. No multi-label severity output without architectural changes. <br><br> **Detectron2 (Mask R-CNN)**: Instance segmentation — pixel-perfect damage boundaries. Significant GPU requirement (V100/A100 for practical speed). Overkill for claims triage — bounding boxes are sufficient for severity estimation and adjuster review. | YOLOv8-nano (2MB ONNX export) runs at 30fps on CPU, providing bounding box localization, damage class identification, and confidence scores. Insufficient for autonomous damage estimation but well-suited for adjuster triage — highlights areas of concern, accelerates manual review by 3-5×. |
| **Fraud ML** | XGBoost → ONNX | **PyTorch TabNet**: Deep learning for tabular data — attention-based feature selection, interpretability. Requires GPU for practical training (convergence is 10× slower on CPU). SHAP explainability is less mature for TabNet than for tree-based models. <br><br> **LightGBM**: Similar accuracy to XGBoost on structured claims data, faster training, native categorical feature support. Slightly weaker on small datasets (<50K rows). XGBoost has better ONNX export maturity and more deployment references in production insurance systems. <br><br> **Isolation Forest (unsupervised)**: No labeled fraud data required. Lower detection accuracy — cannot distinguish fraud types or provide calibrated probabilities. Useful as a complement but not a replacement for supervised fraud scoring. | XGBoost quantized ONNX inference achieves <1ms per claim on CPU — 3× faster than native XGBoost. SHAP explainer provides per-claim feature attribution (which factors drove the fraud score). The model is trained on 100K+ historical claims with labeled fraud outcomes already available in the claims system. |
| **Model Serving** | ONNX Runtime | **TorchServe**: Native PyTorch serving with model versioning and REST/gRPC endpoints. Adds a Java dependency (model server is Java-based). Requires GPU for practical latency. Team has no Java expertise — adds a new language to the on-call rotation. <br><br> **TF Serving**: Purpose-built for TensorFlow SavedModel. ClaimPulse's models (YOLOv8, XGBoost, BERT) are PyTorch and scikit-learn based — exporting to TF SavedModel would require framework conversion and lose ONNX optimization passes. <br><br> **BentoML**: Excellent DX for packaging models with pre/post-processing logic. Adds a gRPC server + Yatai for model management. At ClaimPulse's scale (<100ms per inference, 4 worker types), BentoML's batching and auto-scaling provide no benefit over in-process ONNX inference. | ONNX Runtime is a lightweight (~20MB) CPU inference engine consuming the standard ONNX format. Any framework (PyTorch, scikit-learn, XGBoost) exports to ONNX. Inference runs in-process within Celery workers — no separate model server to deploy, scale, or monitor. |
| **Observability** | Prometheus + Grafana + Loki + Tempo | **Datadog**: Excellent UX, single agent for metrics/traces/logs, APM auto-instrumentation for FastAPI. ~$12K/month for ClaimPulse's scale (3 services, 8 containers) — 4× the infrastructure cost of the application. Data egress costs for shipping metrics to SaaS. <br><br> **New Relic**: Similar value to Datadog. Better APM for Python (deep function-level tracing), weaker metric aggregation and alerting. Same cost profile (~$10-15K/month). <br><br> **Elastic (ELK)**: Industry-standard log aggregation. APM (Elastic APM) is less mature than Tempo for distributed tracing. Stack complexity: Elasticsearch, Kibana, APM Server, Fleet, Beats — 5 services vs. Prometheus/Grafana's 2. Significant ops investment for Elasticsearch cluster management. | Prometheus + Grafana + Loki + Tempo is the standard open-source observability stack — metrics, logs, and traces in a unified dashboard. All four run as Docker containers with zero licensing cost and zero data egress. The team already operates this stack for the core claims system. |
| **CI/CD** | GitHub Actions + ArgoCD + Helm | **GitLab CI**: Equivalent feature set (container registry, CI runners, multi-stage pipelines). Code is hosted on GitHub — GitLab CI would require a separate GitLab instance or repository mirroring. <br><br> **Jenkins**: Extensible, mature, vast plugin ecosystem. Adds a Java dependency (master/agent cluster to maintain). Pipeline-as-code is second-class (Jenkinsfile vs. native YAML in GitHub Actions). Plugin version conflicts are a known maintenance burden. <br><br> **CircleCI**: Fast CI, excellent parallelism. No built-in container registry — requires Docker Hub or ECR as a separate service. Cost scales with concurrency — expensive at ClaimPulse's build frequency (multiple daily commits for compliance-driven changes). | GitHub Actions is co-located with the code repository, provides integrated container registry (GHCR), and has no additional infrastructure to operate. ArgoCD provides GitOps deployment to K3s with automated sync and drift detection. Helm packages Kubernetes manifests for reproducible, version-controlled deployments. |
| **Infrastructure** | Docker Compose (dev) / K3s (prod) | **Docker Swarm**: Simpler than Kubernetes — native Docker CLI, no etcd, no Ingress controller. Swarm mode is in maintenance mode (Docker Inc. shifted focus to Kubernetes). No ecosystem of operators or CRDs. No native secrets management beyond Docker secrets. <br><br> **EKS / GKE / AKS**: Managed Kubernetes — excellent control planes, integrated IAM, auto-scaling. Not chosen over K3s for the production deployment because ClaimPulse runs on-premise (state DOI data residency requirements). K3s provides the same Kubernetes API on local hardware with a single binary. <br><br> **Nomad + Consul**: HashiCorp's lighter orchestrator with service mesh. Excellent for batch jobs (model training) but weaker for long-running services — no native Ingress controller, no HPA, no built-in service mesh without Consul Connect. | Docker Compose provides a zero-orchestrator development environment. K3s provides a CNCF-certified Kubernetes distribution for production — single binary, SQLite-backed (no etcd), runs on a single VM in the on-premise environment. The Helm charts are identical between dev and prod — only the kubeconfig changes. |

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| API server | FastAPI + Uvicorn | 0.115+ | Async API, WebSocket, Jinja2 templating |
| Task queue | Celery + RabbitMQ | 5.4+ | Async claim processing pipeline |
| Database | PostgreSQL + pgvector | 16+ | Claims data + embedding storage |
| Vector search | pgvector | 0.7+ | Similar claim retrieval |
| Object store | MinIO | LATEST | Claim documents, photos, model artifacts |
| Document OCR | PaddleOCR (server mode) | 2.8+ | Text extraction from claim forms |
| Document NER | BERT-base (HuggingFace) | Fine-tuned | Field extraction |
| Image analysis | YOLOv8-nano ONNX | Ultralytics 8+ | Damage detection, severity classification |
| Fraud ML | XGBoost → ONNX | 2.0+ | Fraud risk scoring, SHAP explainability |
| LLM inference | llama.cpp server | b3936+ | Llama 3 8B Q4_K_M |
| Embeddings | BAAI/bge-small-en-v1.5 ONNX | 1.5 | Claim similarity search |
| Auth | Keycloak | 24+ | OAuth 2.0, RBAC, LDAP sync |
| Feature flags | Unleash | 5+ | Gradual AI feature rollout |
| Monitoring | Prometheus + Grafana + OpenTelemetry | LATEST | Metrics, tracing, alerting |
| Logging | Grafana Loki + Promtail | 3+ | Structured log aggregation |
| CI/CD | GitHub Actions + ArgoCD + Helm | LATEST | GitOps deployment |
| Infrastructure | Docker Compose (dev) / K3s (prod) | LATEST | Container orchestration |

---

## Monitoring & Observability

### Prometheus Metrics (per endpoint)

```
claimpulse_claims_total{status}           — Counter: claims by current status
claimpulse_pipeline_duration_seconds{step} — Histogram: per-step latency (p50, p95, p99)
claimpulse_worker_queue_depth{worker}      — Gauge: RabbitMQ queue size per worker
claimpulse_auto_approve_rate               — Gauge: % of claims approved without adjuster touch
claimpulse_model_inference_time{model}     — Histogram: model inference latency
claimpulse_adjuster_overrides_total         — Counter: override events with reason tag
```

### Grafana Dashboard Panels

1. **Pipeline Health**: Flow diagram with per-stage throughput and error rates
2. **Cycle Time**: P50/P95/P99 line chart, trend vs. 14-day baseline
3. **Worker Performance**: Queue depth, processing rate, error rate per worker type
4. **Model Drift**: Feature distribution shift per model (KS-test p-value over time)
5. **Compliance SLA**: % of claims processed within target cycle time by state
6. **Auto-approve Rate**: Daily auto-approve percentage with 7-day rolling average

### Alerting Rules

| Condition | Severity | Action |
|---|---|---|
| Pipeline duration > 5 min for any step | Warning | Slack #claims-alerts |
| Settlement worker queue > 100 | Warning | Scale out worker |
| Fraud model accuracy drop > 5% in last 24h | Critical | PagerDuty, rollback model in MLflow |
| Auto-approve rate < 20% for 3 consecutive days | Warning | Flag for review |
| Document extraction accuracy < 85% for 100 claims | Critical | Retrain BERT NER |

---

## Performance Targets

| Metric | Current | Target | Measurement |
|---|---|---|---|
| Average cycle time | 14 days | <3 days | Claim creation → adjuster approval |
| Auto-approve rate | 0% | 40%+ | Claims passing all thresholds without human touch |
| Fraud detection rate | ~10% (manual) | 25%+ | True positives / total fraudulent claims |
| Settlement accuracy | N/A (manual) | ±15% of final settlement | AI recommendation vs. historical adjuster decision |
| Adjuster throughput | 5 claims/day | 20 claims/day | Adjuster-level claim resolution rate |
| Document extraction accuracy | 85% (manual) | 95% | Fields correctly extracted / total fields |
| Uptime | N/A | 99.9% | Prometheus alertmanager SLA tracking |

---

## Implementation Phases

| Phase | Tasks | Duration | Dependencies |
|---|---|---|---|
| **P1: Scaffold** | FastAPI project, Celery + RabbitMQ, PostgreSQL schema, MinIO, Keycloak config, Docker Compose | 1 week | None |
| **P2: Intake UI** | Claim upload + HTMX form, PaddleOCR server mode, BERT NER fine-tuning, field extraction pipeline | 3 weeks | P1 |
| **P3: Document Pipeline** | pgvector integration, similarity search, document status flow, Celery task orchestration | 1 week | P2 |
| **P4: Image AI** | YOLOv8-nano ONNX export, severity classifier, photo annotation in UI, cost estimator | 2 weeks | P2 |
| **P5: Fraud Engine** | XGBoost training on historical claims, ONNX export, SHAP explainability, fraud console UI | 2 weeks | P1, historical data |
| **P6: Settlement LLM** | llama.cpp server setup, Llama 3 8B GGUF, prompt engineering + structured output, settlement UI with Alpine.js slider | 2 weeks | P1 |
| **P7: Dashboard** | Dashboard, queue manager, analytics — all Chart.js widgets with HTMX SSE data refresh | 3 weeks | P2–P6 |
| **P8: Compliance** | State regulatory config matrix, retention policies, disclosure templates, audit log UI | 1 week | P1 |
| **P9: Admin Console** | Model monitoring, MLflow integration, Unleash feature flags, threshold config, admin UI | 1 week | P7 |
| **P10: Integration** | Core claims system API connector (REST/SFTP), ETL for historical migration, load testing (100 claims/min) | 2 weeks | P1–P9 |
| **P11: Production** | K3s cluster setup, ArgoCD GitOps, Prometheus/Grafana dashboards, runbook, training | 2 weeks | P10 |

**Total: 20 weeks (team of 4: 1 full-stack, 1 ML, 1 backend, 1 infra)**

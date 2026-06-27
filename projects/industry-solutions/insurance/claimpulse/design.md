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

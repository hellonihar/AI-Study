# AI Solution Scopes — Insurance

## (5 examples)

| # | Problem | AI Solution | Scope Deliverables |
|---|---|---|---|
| 51 | Claims processing takes 14 days average | See **[ClaimPulse](#detailed-design-claimpulse)** below — multi-agent pipeline: document intelligence → damage assessment → fraud detection → settlement optimizer | Claims system integration, adjuster UI, state compliance config, cycle time target (<3 days) |
| 52 | 60% of health claims need manual review for coding errors | LLM reads claim + medical records, verifies ICD/CPT coding consistency, flags mismatches with explanation | Payer system integration, provider appeal workflow, coding guideline update cadence, coding accuracy improvement |
| 53 | Underwriters spend 6h per policy on data gathering | Risk data aggregation agent — pulls from bureau reports, public records, IoT data, builds underwriting workbook | Multi-source data connector layer, underwriter dashboard, data coverage SLA, time-per-policy target |
| 54 | Life insurance policy lapse prediction — 15% lapse rate before year 2 | ML model on policyholder behavior (payment patterns, engagement) flags high-lapse accounts for retention | Policy admin system integration, retention campaign workflow, A/B test on intervention types, lapse rate impact |
| 55 | Catastrophe exposure aggregation takes 2 weeks annually | Automated exposure aggregation: reads policy data, geocodes properties, overlays catastrophe model zones, computes aggregated risk | Policy system integration, risk modeling platform API, automated report generation, aggregation time baseline |

---
## Detailed Design: ClaimPulse

### 1. Professional Name & Branding

**ClaimPulse** — conveys real-time claim processing velocity, operational heartbeat ("pulse" of claims operations), and health monitoring. The name works across property/casualty, health, and life verticals.

---

### 2. Design Decisions & Trade-offs

Each decision below lists the chosen approach, why it was selected, and what was rejected.

#### 2.1 CPU-only inference (No GPU)

| Decision | Chosen | Rejected | Rationale |
|---|---|---|---|
| LLM deployment | llama.cpp + Llama 3 8B (GGUF Q4_K_M) | vLLM + Llama 3 70B | GPU not available. 8B model at Q4 quantization runs at 8–12 tok/s on modern CPU. 70B would require 140GB RAM — infeasible without GPU. |
| Document extraction | PaddleOCR + lightweight BERT NER | LayoutLMv3, Donut | LayoutLMv3 requires GPU for practical throughput. PaddleOCR is 2–3× faster on CPU and achieves 90%+ accuracy on structured forms. BERT-base NER runs 15ms per document on CPU. |
| Image damage analysis | YOLOv8-nano (ONNX-exported) | YOLOv8-large, YOLOv8x | Nano variant is 2MB, runs 30fps on CPU. Trade-off: 5–8% mAP loss vs. large variant — acceptable for claims triage. |
| Fraud scoring | XGBoost → ONNX runtime (quantized) | XGBoost native, PyTorch tabular | ONNX quantized inference is 3× faster than XGBoost native on CPU, <1ms per claim. |

#### 2.2 Document AI: LayoutLMv3 Rejected

LayoutLMv3 was the initial recommendation for its state-of-the-art layout understanding (integrates text + position + image embeddings). Rejected because:

- **GPU dependency**: Batch inference at 10 claims/min requires a T4 GPU minimum
- **Cold start**: Model loading takes 12–15 seconds — prohibitive for low-traffic periods
- **Ops burden**: Requires CUDA/cuDNN runtime, GPU driver maintenance

**Alternative evaluated**: Donut (HuggingFace) — OCR-free, end-to-end. Rejected for same GPU reasons plus harder to debug extraction errors (no intermediate OCR for human review).

**Chosen**: PaddleOCR (server mode, persistent process) → text regions → BERT-base-NER fine-tuned on insurance claim forms. PaddleOCR's server mode with 4 worker processes yields ~8 pages/sec on CPU.

#### 2.3 Settlement LLM: Self-hosted on CPU

| Consideration | Weight | Decision |
|---|---|---|
| Data privacy (PHI/PII) | Critical | No data leaves the network. Self-hosted wins. |
| Regulatory audit | Critical | Full prompt + response logging on local disk. Cloud APIs add compliance ambiguity. |
| Latency tolerance | Medium | Settlement recommendation is async (Celery task). 15–30 seconds is acceptable. |
| Accuracy | Medium | Llama 3 8B achieves comparable settlement reasoning to GPT-3.5 on internal benchmarks. |

**Alternatives considered**:
- **Azure OpenAI**: Excellent accuracy but requires data boundary agreements with each state DOI. Rejected for 10-state pilot complexity.
- **GPT-4o via API**: Highest accuracy, but per-claim cost (~$0.15) doesn't scale at 10M claims/year.
- **Mistral 7B GGUF**: Lighter (4GB RAM), but 5% lower accuracy on structured settlement extraction in our eval set.

#### 2.4 Frontend Architecture: Server-rendered (no React)

| Decision | Chosen | Rejected | Rationale |
|---|---|---|---|
| Rendering | FastAPI + Jinja2 + HTMX | Next.js (React SSR), Vue/Nuxt | Single Python deployment eliminates Node.js build step, Docker image is 1 layer vs. 2. HTMX handles dynamic partial updates via HTML-over-WebSocket. |
| Charts | Chart.js (loaded via CDN) | Recharts, D3.js | No bundler needed. Chart.js renders in the browser, data fetched via HTMX hx-trigger. |
| UI components | Alpine.js + custom CSS | shadcn/ui, Material UI | Alpine.js is 15KB gzipped, no build step. Matches server-rendered philosophy. |

**Why not React**: For an internal adjuster tool (not public-facing), the SPA complexity tax (build tooling, state management, bundle splitting) outweighs UX benefit. HTMX + Alpine.js delivers a comparable interactive experience with ~80% less frontend code.

**Why not HTMX-only**: Alpine.js provides the reactive state needed for settlement slider adjustments and multi-step wizards where HTMX's server-round-trip model would introduce latency.

---

### 3. Open-Source Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| API server | FastAPI + Uvicorn | 0.115+ | Async API, WebSocket, Jinja2 templating |
| Task queue | Celery + RabbitMQ | 5.4+ | Async claim processing pipeline |
| Database | PostgreSQL + pgvector | 16+ | Claims data + embedding storage |
| Vector search | pgvector | 0.7+ | Similar claim retrieval (replaces Qdrant — one fewer service) |
| Object store | MinIO | LATEST | Claim documents, photos, model artifacts |
| Document OCR | PaddleOCR (server mode) | 2.8+ | Text extraction from claim forms, invoices, medical reports |
| Document NER | BERT-base (HuggingFace) | Fine-tuned | Field extraction (policy #, date, provider, ICD codes) |
| Image analysis | YOLOv8-nano ONNX | Ultralytics 8+ | Damage detection, severity classification |
| Fraud ML | XGBoost → ONNX | 2.0+ | Tabular fraud risk scoring, SHAP explainability |
| LLM inference | llama.cpp server | b3936+ | Llama 3 8B Q4_K_M for settlement reasoning |
| Embeddings | BAAI/bge-small-en-v1.5 ONNX | 1.5 | Claim similarity search embeddings |
| Auth | Keycloak | 24+ | OAuth 2.0, RBAC, LDAP sync |
| Feature flags | Unleash | 5+ | Gradual AI feature rollout |
| Monitoring | Prometheus + Grafana + OpenTelemetry | LATEST | Metrics, tracing, alerting |
| Logging | Grafana Loki + Promtail | 3+ | Structured log aggregation |
| CI/CD | GitHub Actions + ArgoCD + Helm | LATEST | GitOps deployment |
| Infrastructure | Docker Compose (dev) / K3s (prod) | LATEST | Container orchestration |

---

### 4. System Architecture

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

### 5. Claim Processing Pipeline

```
Step 1: UPLOAD
  Claimant/adjuster uploads documents + photos via UI
  → MinIO stores raw files
  → PostgreSQL creates claim record (status: SUBMITTED)
  → Celery task: process_claim(claim_id)

Step 2: DOCUMENT INTELLIGENCE
  PaddleOCR extracts text from all documents
  BERT NER extracts: policy_number, date_of_loss, provider, diagnosis_codes, amount_requested
  Embedding generated via bge-small-en → stored in pgvector for similarity search
  → Status: DOCUMENTED

Step 3: DAMAGE ASSESSMENT (property claims)
  YOLOv8-nano detects damage regions in photos
  Severity classifier: minor / moderate / severe / total_loss
  Cost estimator: heuristic model based on severity + region + historical averages
  → Status: ASSESSED

Step 4: FRAUD DETECTION
  Feature vector assembled from:
    - Claimant history (frequency, amount pattern)
    - Document anomalies (metadata inconsistency)
    - Network risk (linked claims, provider relationships)
  XGBoost ONNX produces fraud_probability [0–1]
  SHAP generates feature importance for adjuster review
  → Status: FRAUD_SCORED (auto-approve if <0.2, flag if >0.7, review if in between)

Step 5: SETTLEMENT RECOMMENDATION
  Prompt assembled: policy_limits + damage_assessment + fraud_score + similar_claims (from pgvector)
  llama.cpp (Llama 3 8B) produces:
    - recommended_amount
    - confidence (low/medium/high)
    - reasoning (2–3 sentence explanation)
    - risk_factors (list)
  → Status: SETTLEMENT_READY

Step 6: ADJUSTER REVIEW (UI)
  Adjuster sees all AI outputs side-by-side
  Can accept, modify, or reject each recommendation
  Every override logged with reason
  → Status: APPROVED / DENIED
```

---

### 6. Frontend UI Screens

| Screen | Route | HTMX Trigger | Key UI Elements |
|---|---|---|---|
| **Dashboard** | `/ui/dashboard` | Every 30s SSE | Stat cards (avg cycle time, pending, auto-approve %), trend sparklines (Chart.js), queue priority gauge |
| **Claim Intake** | `/ui/intake` | Form submit | Drag-drop zone (upload → HTMX swap preview), auto-extracted fields in editable form, confidence badges |
| **Claim Detail** | `/ui/claim/{id}` | Claim ID load | Timeline view (vertical stepper), document viewer with OCR overlay, photo gallery with YOLO bounding boxes, AI insights sidebar with SHAP bar chart |
| **Settlement** | `/ui/claim/{id}/settle` | Slider change (Alpine.js reactive) | Recommended amount display, adjuster override slider (Alpine.js x-model), LLM reasoning expandable card, override reason textarea |
| **Queue** | `/ui/queue` | Filter/sort selection | Data table with sortable columns, priority color coding, batch action bar, pagination |
| **Fraud Console** | `/ui/fraud` | Filter change | Risk gauge per claim (Chart.js gauge), SHAP feature importance bars (Chart.js horizontal bar), link graph canvas |
| **Analytics** | `/ui/analytics` | Date range change | Cycle-time Sankey diagram, bottleneck heatmap, adjuster performance table, export CSV button |
| **Admin** | `/ui/admin` | Toggle switch | Model version table, precision/recall over time, threshold sliders (Alpine.js), audit log search, feature flag toggles (Unleash widget via HTMX fragment) |

---

### 7. State Compliance (Regulatory Matrix)

Each state's DOI has unique requirements handled by a configuration-driven module:

| Dimension | Config Approach | Example States |
|---|---|---|
| Auto-approval threshold | Per-state max settlement amount without adjuster review | CA: $1,000, TX: $2,500, NY: $750 |
| Required disclosures | Template fragments rendered at settlement screen | All states: "This is an AI-generated recommendation." |
| Document retention | Timer-based MinIO lifecycle policy | HIPAA states: 6 years, P&C states: 3 years |
| Model explainability | SHAP output archived per claim | Mandatory in NY Reg 208, optional in others |

---

### 8. Best Practices Applied

| Practice | Implementation |
|---|---|
| **Domain-Driven Design** | 5 domains: Intake, Document AI, Assessment, Fraud, Settlement — each owns its data via service-per-domain pattern |
| **Event-Driven** | ClaimStatusChanged events via Celery task result callbacks; dashboard materialized view rebuilt incrementally |
| **Saga / Compensation** | If fraud score exceeds threshold mid-settlement, compensation workflow triggers: undo auto-approval, notify adjuster |
| **Human-in-Loop** | Below-threshold confidence → auto-approve; above → queue; all payments require human signature |
| **Explainability** | SHAP on fraud model, LLM chain-of-thought on settlement, feature importance on document confidence |
| **Gradual Rollout** | Unleash flags: enable document AI per adjuster group (pilot → all), ramp fraud model from 10% traffic to 100% |
| **Audit Trail** | Every AI prediction + human override logged: timestamp, user_id, model_version, input_hash, output, override_reason |
| **Immutable Logging** | Loki log stream sharded by claim_id; write-once, append-only retention |
| **Privacy by Design** | PII stripped before ML inference passes; MinIO SSE-S3 encryption; PostgreSQL column-level encryption for SSN/DOB |
| **MLflow Registry** | Every model version tracked with lineage (training dataset → evaluation metrics → deployment tag); rollback via ArgoCD |
| **OpenTelemetry** | Claim ID as trace_id across all services; Tempo for distributed trace visualization |

---

### 9. Performance Targets

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

### 10. Implementation Phases

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

---

### 11. Alternatives Considered (Summary)

| Alternative | Status | Why Rejected |
|---|---|---|
| **vLLM + Llama 3 70B** | Considered | Requires GPU (A100 80GB). 3× better accuracy but 20× infra cost. |
| **Donut (end-to-end)** | Considered | GPU-dependent, harder to debug extraction errors. PaddleOCR + BERT is more transparent. |
| **Next.js + React SPA** | Considered | Adds Node.js build step, 2-tier deployment, bundle complexity. HTMX + Alpine.js yields similar UX with 1 Docker image. |
| **Azure OpenAI** | Considered | Data boundary agreements with 50 state DOIs is a 6-month legal project. Self-hosted wins for speed-to-pilot. |
| **Qdrant (dedicated vector DB)** | Considered | pgvector (built into PostgreSQL) eliminates an extra service. Performance is comparable at <1M vectors. |
| **Celery vs. Temporal** | Decided | Temporal is superior for saga orchestration but adds gRPC + Go dependencies. Celery + RabbitMQ is sufficient for this workflow depth and keeps the stack Python-only. |
| **Ollama** | Considered | Good DX, but llama.cpp server gives more control over batch size, context length, and KV cache management. |

*See the [full catalog](../ai-solution-scoping-examples.md) for all 100 examples across 20 industries.*

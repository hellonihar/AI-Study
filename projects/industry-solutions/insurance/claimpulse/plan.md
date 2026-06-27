# ClaimPulse — Project Plan

## Overview

82 work items across 11 phases, estimated at 386 hours (~48 person-days) for a team of 4.

| Role | Focus Areas |
|---|---|
| **Full-stack** | Jinja2 templates, HTMX routes, Alpine.js, Chart.js, UI integration |
| **ML** | Model training, ONNX export, prompt engineering, evaluation |
| **Backend** | FastAPI routes, Celery tasks, services, DB, API integration |
| **Infra** | Docker, K3s, CI/CD, monitoring, Helm, ArgoCD |

---

## Phase 1: Scaffold (Week 1)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 1.1 | Initialize FastAPI project, pydantic-settings config, app factory | 4h | Backend | — | |
| 1.2 | Define SQLAlchemy models + Alembic migrations | 6h | Backend | 1.1 | |
| 1.3 | Celery + RabbitMQ Docker compose + Celery app config | 4h | Backend | 1.1 | |
| 1.4 | MinIO Docker + S3-compatible SDK integration (boto3) | 2h | Infra | 1.1 | |
| 1.5 | Keycloak Docker + realm config + OAuth2 middleware | 4h | Infra | 1.1 | |
| 1.6 | Redis for rate limiting + Celery result backend | 2h | Backend | 1.1 | |
| 1.7 | Prometheus + Grafana + Loki + Tempo Docker compose | 4h | Infra | 1.1 | |
| 1.8 | GitHub Actions CI/CD: build, test, push, deploy to K3s | 3h | Infra | 1.3–1.7 | |
| 1.9 | Structlog configuration + structured logging middleware | 1h | Backend | 1.1 | |

**Phase total: 26h**

---

## Phase 2: Intake UI (Weeks 2–4)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 2.1 | Claim upload REST endpoint (multipart → MinIO) | 8h | Backend | 1.2, 1.4 | |
| 2.2 | HTMX drag-drop upload form with Alpine.js file preview | 8h | Full-stack | 1.1 | |
| 2.3 | PaddleOCR server mode Docker setup (persistent process) | 4h | Infra | 1.3 | |
| 2.4 | PaddleOCR Python client service (connection pool + retry) | 6h | Backend | 2.3 | |
| 2.5 | BERT NER fine-tuning on 10K labeled claim forms | 12h | ML | Labeled dataset | |
| 2.6 | BERT NER inference wrapper (ONNX export + runtime) | 6h | ML | 2.5 | |
| 2.7 | Auto-extracted fields display with confidence badges | 6h | Full-stack | 2.6 | |
| 2.8 | Editable extracted fields form (HTMX swap + Alpine.js) | 6h | Full-stack | 2.7 | |
| 2.9 | Error handling: OCR failures, model timeouts, retry logic | 4h | Backend | 2.1, 2.4 | |
| 2.10 | Integration test: upload → OCR → extraction → display | 2h | Full-stack | 2.1–2.9 | |

**Phase total: 62h**

---

## Phase 3: Document Pipeline (Week 5)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 3.1 | bge-small-en-v1.5 ONNX export + inference wrapper | 4h | ML | 2.6 | |
| 3.2 | pgvector extension + HNSW index on PostgreSQL | 2h | Backend | 1.2 | |
| 3.3 | Document → embedding → pgvector Celery task | 4h | Backend | 3.1, 3.2 | |
| 3.4 | Similarity search service (cosine distance + metadata filter) | 4h | Backend | 3.2 | |
| 3.5 | Similar claims sidebar in claim detail UI | 4h | Full-stack | 3.4 | |
| 3.6 | Document status flow integration (→ DOCUMENTED) | 2h | Backend | 3.3 | |

**Phase total: 20h**

---

## Phase 4: Image Analysis (Weeks 6–7)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 4.1 | YOLOv8-nano training on labeled damage photo dataset | 10h | ML | Labeled dataset | |
| 4.2 | YOLOv8-nano → ONNX export + FP16 optimization | 4h | ML | 4.1 | |
| 4.3 | ONNX Runtime inference service (batched + streaming) | 4h | Backend | 4.2 | |
| 4.4 | Severity classifier (minor / moderate / severe / total_loss) | 4h | ML | 4.2 | |
| 4.5 | Cost estimator heuristic (severity × region × historical avg) | 2h | Backend | 4.4 | |
| 4.6 | Photo upload → damage analysis Celery task | 4h | Backend | 4.3, 2.1 | |
| 4.7 | Photo viewer with YOLO bounding box overlay (Canvas JS) | 8h | Full-stack | 4.6 | |
| 4.8 | Damage assessment acceptance test + false positive audit | 4h | ML | 4.1–4.7 | |

**Phase total: 40h**

---

## Phase 5: Fraud Engine (Weeks 8–9)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 5.1 | Historical claims ETL: extract, clean, feature engineering | 8h | ML | 1.2 | |
| 5.2 | XGBoost model training + hyperparameter optimization | 8h | ML | 5.1 | |
| 5.3 | XGBoost → ONNX export + MLflow model registry | 4h | ML | 5.2 | |
| 5.4 | SHAP explainer integration (per-claim feature importance) | 4h | ML | 5.3 | |
| 5.5 | Fraud scoring Celery task | 4h | Backend | 5.3, 5.4 | |
| 5.6 | Fraud console UI: risk gauge, SHAP bar chart, link graph | 8h | Full-stack | 5.5 | |
| 5.7 | Fraud model evaluation + threshold tuning dashboard | 4h | ML | 5.6 + live data | |

**Phase total: 36h**

---

## Phase 6: Settlement LLM (Weeks 10–11)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 6.1 | llama.cpp server Docker setup + model volume mount | 6h | Infra | 1.3 | |
| 6.2 | Llama 3 8B Q4_K_M download + quantization verification | 4h | Infra | 6.1 | |
| 6.3 | Prompt template engineering: system prompt + few-shot + output schema | 8h | ML | 3.4, 4.4, 5.4 | |
| 6.4 | Structured JSON output parser with regex fallback | 4h | Backend | 6.3 | |
| 6.5 | Settlement recommendation Celery task | 4h | Backend | 6.2, 6.4 | |
| 6.6 | Settlement UI: Alpine.js slider, LLM reasoning card, override form | 8h | Full-stack | 6.5 | |
| 6.7 | Bias evaluation: settlement amounts by demographic group | 6h | ML | 6.5 + live data | |
| 6.8 | Prompt version tracking + audit logging | 2h | Backend | 6.3, 1.2 audit_log | |

**Phase total: 42h**

---

## Phase 7: Dashboard (Weeks 12–14)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 7.1 | Dashboard layout: stat cards, KPI template inheritance | 6h | Full-stack | 1.1 base.html | |
| 7.2 | Sparkline Chart.js widgets with HTMX SSE (30s refresh) | 8h | Full-stack | 7.1 | |
| 7.3 | Queue manager: sortable/filterable data table with HTMX | 8h | Full-stack | 1.1 | |
| 7.4 | Priority color coding logic + batch action bar | 4h | Full-stack | 7.3 | |
| 7.5 | Pagination component (HTMX hx-trigger on scroll/click) | 4h | Full-stack | 7.3 | |
| 7.6 | Analytics page: date range picker, Chart.js render pipeline | 8h | Full-stack | 7.1 | |
| 7.7 | Cycle-time Sankey diagram (Chart.js Sankey plugin) | 6h | Full-stack | 7.6 | |
| 7.8 | Bottleneck heatmap by loss type + adjuster | 4h | Full-stack | 7.6 | |
| 7.9 | Adjuster performance table + CSV export button | 4h | Full-stack | 7.6 | |
| 7.10 | WebSocket connection manager for real-time dashboard updates | 4h | Backend | 1.1 WebSocket support | |

**Phase total: 56h**

---

## Phase 8: Compliance (Week 15)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 8.1 | State regulatory config matrix (YAML): thresholds, disclosures, retention | 4h | Full-stack | 1.1 config | |
| 8.2 | Auto-approval threshold service (per-state settlement limit check) | 3h | Backend | 8.1 | |
| 8.3 | Required disclosure template fragments per state | 4h | Full-stack | 8.1 | |
| 8.4 | MinIO lifecycle policy per retention class (HIPAA: 6yr, P&C: 3yr) | 3h | Infra | 1.4 | |
| 8.5 | Compliance audit log export (CSV/JSON by state + date range) | 2h | Backend | 1.2 audit_log | |
| 8.6 | Disclosure rendering integration in settlement screen | 2h | Full-stack | 8.3, 6.6 | |

**Phase total: 18h**

---

## Phase 9: Admin Console (Week 16)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 9.1 | Model version table with MLflow API integration | 4h | Backend | 5.3 | |
| 9.2 | Precision/recall time-series chart across model versions | 4h | Full-stack | 9.1 | |
| 9.3 | Threshold configuration sliders (Alpine.js x-model reactive) | 4h | Full-stack | 5.7, 6.7 | |
| 9.4 | Audit log search UI: date range, event type, claim ID filter | 4h | Full-stack | 1.2 audit_log | |
| 9.5 | Unleash feature flag SDK integration + admin API | 2h | Backend | 1.1 | |
| 9.6 | Feature flag toggle UI with HTMX form submission | 2h | Full-stack | 9.5 | |

**Phase total: 20h**

---

## Phase 10: Integration (Weeks 17–18)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 10.1 | Core claims system REST API connector (retry, auth, rate limit) | 8h | Backend | 1.1 config | |
| 10.2 | SFTP batch import for legacy claim files | 6h | Backend | 1.4 MinIO | |
| 10.3 | ETL script: historical claims → ClaimPulse schema | 6h | Backend | 1.2 models | |
| 10.4 | Data validation + reconciliation report generation | 4h | Backend | 10.3 | |
| 10.5 | Load testing with k6: 100 claims/min end-to-end | 6h | Infra | 2.1–6.5 all workers | |
| 10.6 | Performance tuning: connection pools, batch sizes, timeouts | 4h | Backend | 10.5 | |
| 10.7 | Error recovery + poison message handling (RabbitMQ DLQ) | 2h | Backend | 1.3 Celery | |

**Phase total: 36h**

---

## Phase 11: Production (Weeks 19–20)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 11.1 | K3s cluster setup + namespace structure (dev/staging/prod) | 4h | Infra | 10.5 load test results | |
| 11.2 | Helm charts for all 8 services + dependency services | 8h | Infra | 11.1 | |
| 11.3 | ArgoCD app-of-apps GitOps configuration | 4h | Infra | 11.2 | |
| 11.4 | Prometheus recording rules + Alertmanager alert rules | 4h | Infra | 11.1 | |
| 11.5 | Grafana dashboard provisioning as code (ConfigMap) | 3h | Infra | 11.4 | |
| 11.6 | Runbook per service: startup, failure, scaling, backup, restore | 4h | All | 11.2–11.5 | |
| 11.7 | Security audit checklist + penetration testing | 3h | Infra | 11.1 | |
| 11.8 | Production readiness review + go/no-go decision | 2h | All | 11.1–11.7 | |

**Phase total: 30h**

---

## Summary

| Phase | Weeks | Tasks | Effort | Dependency Chain |
|---|---|---|---|---|
| P1: Scaffold | 1 | 9 | 26h | — |
| P2: Intake UI | 2–4 | 10 | 62h | P1 |
| P3: Document Pipeline | 5 | 6 | 20h | P2 |
| P4: Image Analysis | 6–7 | 8 | 40h | P2 |
| P5: Fraud Engine | 8–9 | 7 | 36h | P1 + historical data |
| P6: Settlement LLM | 10–11 | 8 | 42h | P3, P4, P5 |
| P7: Dashboard | 12–14 | 10 | 56h | P2–P6 |
| P8: Compliance | 15 | 6 | 18h | P1 |
| P9: Admin Console | 16 | 6 | 20h | P7 |
| P10: Integration | 17–18 | 7 | 36h | P1–P9 |
| P11: Production | 19–20 | 8 | 30h | P10 |
| **Total** | **20** | **82** | **386h** | |

## Dependency Graph

```
P1 ──► P2 ──► P3 ──► P6 ──► P7 ──► P9 ──► P10 ──► P11
              │               │
              ├──► P4 ────────┤
              │               │
P1 ──► P5 ───┘               │
                              │
P1 ──► P8 ───────────────────┘
```

P8 runs parallel with P7. P9 runs parallel with P7. P5 runs parallel with P3–P4 (requires only P1 infra + historical data).

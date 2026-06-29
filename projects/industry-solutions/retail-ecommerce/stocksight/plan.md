# StockSight — Project Plan

## Overview

95 work items across 11 phases, estimated at 410 hours (~51 person-days) for a team of 4.

| Role | Focus Areas |
|---|---|
| **Full-stack** | Next.js, Recharts, SSE, dashboard, simulator UI |
| **ML** | Lag-Llama/PatchTFT fine-tuning, Prophet baseline, feature engineering, ensemble, retraining pipeline |
| **Backend** | FastAPI routes, Celery tasks, POS/ERP adapters, TimescaleDB, external API integrations |
| **Infra** | Docker, K3s, CI/CD, monitoring, Helm, ArgoCD, Kafka |

---

## Phase 1: Scaffold (Week 1)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 1.1 | Initialize FastAPI project, pydantic-settings config, app factory | 4h | Backend | — | |
| 1.2 | TimescaleDB + PostgreSQL Docker compose with hypertable init | 4h | Infra | 1.1 | |
| 1.3 | Celery + RabbitMQ Docker compose + Celery app + periodic schedule config | 4h | Backend | 1.1 | |
| 1.4 | MinIO Docker for model artifact storage | 1h | Infra | 1.1 | |
| 1.5 | Keycloak Docker + realm config + OAuth2 middleware + RBAC roles | 4h | Infra | 1.1 | |
| 1.6 | SQLAlchemy models + Alembic migrations (skus, stores, categories, families) | 6h | Backend | 1.2 | |
| 1.7 | TimescaleDB hypertable creation in migration (pos_transactions, inventory_levels, forecasts, accuracy_records) | 3h | Backend | 1.6 | |
| 1.8 | Redis Docker for rate limiting + Celery result backend | 1h | Infra | 1.1 | |
| 1.9 | Prometheus + Grafana + Loki + Tempo Docker compose | 4h | Infra | 1.1 | |
| 1.10 | GitHub Actions CI/CD: build, test, lint, Docker push | 3h | Infra | 1.2–1.9 | |
| 1.11 | Structlog configuration + request ID middleware | 1h | Backend | 1.1 | |
| 1.12 | Next.js project scaffold + Tailwind config + API client library | 4h | Full-stack | — | |

**Phase total: 39h**

---

## Phase 2: POS/ERP Pipeline (Weeks 2–4)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 2.1 | POS adapter abstract base class + connection lifecycle contract | 4h | Backend | 1.1 | |
| 2.2 | Kafka consumer adapter: read POS transactions from retail event stream | 8h | Backend | 2.1 | |
| 2.3 | REST API poller adapter: pull POS data from legacy system (configurable interval) | 6h | Backend | 2.1 | |
| 2.4 | CSV/SFTP batch import adapter: daily POS file drop ingestion | 4h | Backend | 2.1 | |
| 2.5 | POS data validation: quantity > 0, valid SKU/store, price range check, duplicate detection | 4h | Backend | 2.2–2.4 | |
| 2.6 | Celery 60s consumer: write validated POS transactions to TimescaleDB | 4h | Backend | 2.5, 1.7 | |
| 2.7 | ERP adapter: REST API connector for inventory snapshot sync | 6h | Backend | 2.1 | |
| 2.8 | ERP field mapping config: transform external JSON → internal schema | 3h | Backend | 2.7 | |
| 2.9 | Celery 4h scheduler: pull inventory levels from ERP, write to inventory_levels | 4h | Backend | 2.8, 1.7 | |
| 2.10 | ERP simulator mode: synthetic POS + inventory generation for development | 6h | Backend | 1.1 | |
| 2.11 | Data freshness monitoring: alert if POS data lag > 1h or ERP lag > 6h | 3h | Backend | 2.6, 2.9 | |
| 2.12 | SKU master sync: pull new/updated SKUs from ERP, update skus table | 4h | Backend | 2.8 | |
| 2.13 | Integration test: POS → TimescaleDB round trip with 1000 synthetic transactions | 3h | Backend | 2.6, 2.10 | |

**Phase total: 59h**

---

## Phase 3: External Data Pipeline (Week 5)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 3.1 | Weather API client (OpenWeatherMap/NOAA): configurable location set, retry, rate limit | 6h | Backend | 1.1 | |
| 3.2 | Weather data schema: temperature, precipitation, humidity, wind, condition code | 2h | Backend | 3.1 | |
| 3.3 | Celery 6h scheduler: fetch weather forecast for all store locations, write to weather_forecasts | 4h | Backend | 3.2, 1.7 | |
| 3.4 | Competitor pricing scraper base class: Playwright-based, configurable selectors | 6h | Backend | 1.1 | |
| 3.5 | Competitor pricing schema: sku match, competitor name, price, promo flag, confidence | 2h | Backend | 3.4 | |
| 3.6 | Celery daily scheduler: run competitor scraper, write to competitor_pricing | 4h | Backend | 3.5, 1.7 | |
| 3.7 | Promotions calendar API + CRUD endpoints | 6h | Backend | 1.6 | |
| 3.8 | Promotions ingestion: bulk import from ERP promotion calendar | 3h | Backend | 3.7 | |
| 3.9 | External source health dashboard: last sync time, records ingested, error count per source | 4h | Full-stack | 3.3, 3.6, 3.7 | |

**Phase total: 37h**

---

## Phase 4: Feature Engineering (Weeks 6–7)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 4.1 | Feature library: rolling window stats (mean, std, min, max) over configurable windows (7, 14, 28, 90 days) | 6h | ML | 1.1 | |
| 4.2 | Feature library: lag features (D-1, D-7, D-14, D-28, D-90) | 3h | ML | 4.1 | |
| 4.3 | Feature library: cyclical encoding (day_of_week, month, day_of_year) | 2h | ML | 4.1 | |
| 4.4 | Feature library: holiday/event flags with configurable pre/post windows | 4h | ML | 4.1 | |
| 4.5 | Feature library: promotion features (discount_pct, promo_type, days_since_last_promo, promo_lift_estimate) | 4h | ML | 4.1 | |
| 4.6 | Feature library: weather features (temp, precipitation, extreme weather flag) | 3h | ML | 4.1 | |
| 4.7 | Feature library: pricing features (current_price, price_change, competitor_price_gap) | 4h | ML | 4.1 | |
| 4.8 | Feature library: inventory features (current_stock, days_of_cover, stockout_flag, in_transit_qty) | 3h | ML | 4.1 | |
| 4.9 | Feature library: interaction features (promo×weather, holiday×category, price×competitor_gap) | 4h | ML | 4.5, 4.6, 4.7 | |
| 4.10 | Celery daily cron (02:00): compute all features for active SKU-store pairs, write to feature store | 8h | Backend | 4.2–4.9, 2.6, 2.9, 3.3, 3.6, 3.7 | |
| 4.11 | Feature validation: null check, range check, distribution comparison to historical | 3h | ML | 4.10 | |
| 4.12 | SKU similarity embeddings: bge-small-en ONNX for cold-start similarity search | 4h | ML | 4.10 | |
| 4.13 | Feature importance analysis: SHAP on baseline model, prune to top 30 features | 4h | ML | 5.5 | |

**Phase total: 52h**

---

## Phase 5: Baseline Model (Weeks 8–9)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 5.1 | Prophet training pipeline: fit per SKU-store with yearly/weekly seasonality + holiday regressors | 8h | ML | 4.10 | |
| 5.2 | Prophet distributed training: batch processing with Celery chunks (100 SKUs per task) | 6h | ML | 5.1 | |
| 5.3 | Prophet forecast generation: predict 1/7/14/30/90 day horizons, write to forecasts table | 4h | ML | 5.2 | |
| 5.4 | Prophet model serialization: save to MinIO + MLflow with metadata | 3h | ML | 5.2 | |
| 5.5 | Baseline evaluation framework: compute MAPE/RMSE/MAE/bias at each horizon | 6h | ML | 5.3, 2.6 | |
| 5.6 | Baseline accuracy baseline: record current accuracy as benchmark for foundation model comparison | 2h | ML | 5.5 | |
| 5.7 | Prophet monthly retrain Celery cron (first Sunday, 03:00) | 3h | ML | 5.2, 1.3 | |
| 5.8 | Evaluation visualization: accuracy by SKU cluster, store, horizon | 4h | Full-stack | 5.5 | |

**Phase total: 36h**

---

## Phase 6: Foundation Model (Weeks 10–11)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 6.1 | Lag-Llama training data pipeline: extract 2 years from TimescaleDB, temporal train/val/test split | 6h | ML | 4.10 | |
| 6.2 | Lag-Llama fine-tuning: train on SKU-store sales with all features, hyperparameter tuning | 12h | ML | 6.1 | |
| 6.3 | Lag-Llama ONNX export + quantization (FP16) for CPU inference | 4h | ML | 6.2 | |
| 6.4 | Foundation model inference service: batched prediction with configurable horizon | 6h | ML | 6.3 | |
| 6.5 | Multi-horizon forecast generation: 1/7/14/30/90 day with quantile outputs (p10, p50, p90) | 4h | ML | 6.4 | |
| 6.6 | Cold-start logic: SKU similarity embedding → transfer from top-5 similar SKUs → widened confidence bands | 6h | ML | 4.12, 6.4 | |
| 6.7 | Ensemble logic: horizon-weighted blend of Prophet and foundation model | 6h | ML | 5.3, 6.5 | |
| 6.8 | Ensemble weight optimization: rolling 30-day MAPE minimization per SKU cluster | 4h | ML | 6.7, 5.5 | |
| 6.9 | Model validation: accuracy comparison vs. baseline, residual analysis, feature importance | 6h | ML | 6.5 | |
| 6.10 | Celery daily cron (04:00): generate all forecasts (baseline + foundation + ensemble) | 6h | Backend | 6.4, 6.7, 1.3 | |
| 6.11 | Model export pipeline: save best model to MinIO + MLflow with evaluation metrics | 2h | ML | 6.9 | |

**Phase total: 62h**

---

## Phase 7: Forecast Dashboard (Weeks 12–14)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 7.1 | Dashboard page layout: KPI cards (stockout %, overstock %, forecast MAPE, SLA compliance) | 6h | Full-stack | 1.12 | |
| 7.2 | Forecast vs. actual time-series chart (Recharts): zoomable, multiple horizon overlays | 8h | Full-stack | 7.1 | |
| 7.3 | Stockout risk heatmap: SKU × store matrix with color-coded risk levels | 6h | Full-stack | 7.1 | |
| 7.4 | Inventory health gauge: per-store stockout rate + overstock rate with trend arrows | 4h | Full-stack | 7.1 | |
| 7.5 | SKU detail page: forecast chart, current stock, upcoming promotions, accuracy history | 8h | Full-stack | 7.2, 3.7 | |
| 7.6 | Store detail page: top 10 at-risk SKUs, forecast vs. actual, regional comparison | 6h | Full-stack | 7.2 | |
| 7.7 | SSE client utility (EventSource with auto-reconnect) for real-time forecast updates | 4h | Full-stack | 1.12 | |
| 7.8 | SSE event integration: forecast.generated, stockout.risk, accuracy.sla_breached | 4h | Full-stack | 7.7, 6.10 | |
| 7.9 | Forecast table widget: sortable/filterable by SKU, store, horizon, accuracy | 6h | Full-stack | 7.1 | |
| 7.10 | Date range selector + granularity toggle (daily/weekly/monthly) | 4h | Full-stack | 7.2 | |
| 7.11 | Export button: CSV download of forecast data for current view | 3h | Full-stack | 7.9 | |
| 7.12 | Response time SLA: wireframe loading states, skeleton screens, error boundaries | 3h | Full-stack | 7.1 | |

**Phase total: 62h**

---

## Phase 8: Simulator UI (Weeks 15–16)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 8.1 | What-if page layout: scenario parameter panel + results panel side-by-side | 4h | Full-stack | 7.1 | |
| 8.2 | Scenario parameter controls: promotion discount slider, weather override, competitor price change | 6h | Full-stack | 8.1 | |
| 8.3 | "Run Simulation" button → POST /api/simulate → loading state with ETA | 3h | Full-stack | 8.2 | |
| 8.4 | Forecast comparison chart: baseline vs. scenario, with delta annotations | 8h | Full-stack | 8.3 | |
| 8.5 | Scenario summary cards: stockout rate delta, overstock delta, revenue impact | 4h | Full-stack | 8.4 | |
| 8.6 | Scenario history table: previous simulations with parameters and results | 3h | Full-stack | 8.3 | |
| 8.7 | PDF export (puppeteer) of scenario comparison report | 6h | Full-stack | 8.5 | |
| 8.8 | API: POST /api/simulate (run forecast with modified features, return full results) | 8h | Backend | 6.10, 4.10 | |
| 8.9 | Scenario API parameter schema: promotion_delta, weather_override, competitor_price_delta | 3h | Backend | 8.8 | |

**Phase total: 45h**

---

## Phase 9: Accuracy SLA (Weeks 17–18)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 9.1 | Accuracy computation pipeline: compare T-day forecast vs. T-day actual, per SKU-store | 6h | ML | 6.10, 2.6 | |
| 9.2 | SLA config YAML: threshold per horizon (1d: 15%, 7d: 20%, 30d: 25%, 90d: 35%) | 2h | Backend | 1.1 | |
| 9.3 | SLA compliance check: per SKU-store-horizon, flag SLA breaches | 4h | ML | 9.1, 9.2 | |
| 9.4 | Celery daily cron (06:00): compute accuracy, check SLA, write to accuracy_records | 4h | Backend | 9.3, 1.3 | |
| 9.5 | Accuracy trend chart: MAPE by horizon over last 90 days with SLA threshold lines | 6h | Full-stack | 9.4 | |
| 9.6 | Model comparison chart: Prophet vs. Lag-Llama vs. Ensemble MAPE by horizon | 4h | Full-stack | 9.5 | |
| 9.7 | Weekly retrain cron (Sunday 03:00): check accuracy, retrain if MAPE degraded > 5% | 6h | ML | 9.4, 6.2 | |
| 9.8 | Anomaly-triggered retrain: monitor daily MAPE, trigger if > threshold for 3 consecutive days | 4h | Backend | 9.4 | |
| 9.9 | Drift monitoring: feature distribution KS-test, alert on significant shift per SKU cluster | 6h | ML | 9.7 | |
| 9.10 | Retraining report: MAPE before/after, model version diff, feature importance change | 3h | ML | 9.7 | |

**Phase total: 45h**

---

## Phase 10: Admin + Alerts (Week 19)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 10.1 | Model version table: MLflow integration, list models with MAPE, train date, feature count | 4h | Full-stack | 6.11 | |
| 10.2 | Feature importance chart: top-N features by SHAP gain, per model version | 4h | Full-stack | 6.9 | |
| 10.3 | Prediction error breakdown: MAPE by SKU cluster, store, category, promotion status | 4h | Full-stack | 9.5 | |
| 10.4 | SLA threshold config UI: per-horizon MAPE limit editor with validation | 4h | Full-stack | 9.2 | |
| 10.5 | Alert rule config: threshold per metric (MAPE breach, data lag, stockout spike), severity, channel | 6h | Full-stack | 1.9 | |
| 10.6 | Unleash feature flag SDK integration + admin UI toggles (model type per cluster, simulation mode) | 4h | Backend | 1.1 | |
| 10.7 | Audit log search UI: event type, date range, SKU/store filter | 3h | Full-stack | 1.6 audit_log | |
| 10.8 | Data source health view: last sync, records ingested, errors per source (POS, ERP, weather, competitor) | 3h | Full-stack | 3.9 | |

**Phase total: 32h**

---

## Phase 11: Production (Weeks 20–21)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 11.1 | K3s cluster setup + namespace structure (dev/staging/prod) | 4h | Infra | P10 complete | |
| 11.2 | Helm charts for all services (FastAPI, Celery workers, TimescaleDB, Redis, RabbitMQ, MinIO, Keycloak, Next.js) | 10h | Infra | 11.1 | |
| 11.3 | ArgoCD app-of-apps GitOps configuration | 4h | Infra | 11.2 | |
| 11.4 | Prometheus recording rules + Alertmanager alert rules (from 10.5) | 4h | Infra | 11.1 | |
| 11.5 | Grafana dashboard provisioning as code (ConfigMap): forecast health, pipeline, inventory, model drift | 4h | Infra | 11.4 | |
| 11.6 | Load testing: k6 script for forecast API + Celery task backlog test (daily forecast cycle for 50K SKUs) | 6h | Infra | 11.1 | |
| 11.7 | Performance tuning: Celery worker concurrency, TimescaleDB chunk size, forecast batch size | 4h | Backend | 11.6 | |
| 11.8 | Security audit checklist: authentication, data encryption, network policies, secrets management | 3h | Infra | 11.1 | |
| 11.9 | Runbook per service: startup, failure, scaling, backup, restore | 4h | All | 11.2–11.8 | |
| 11.10 | Production readiness review + go/no-go decision | 2h | All | 11.1–11.9 | |

**Phase total: 45h**

---

## Summary

| Phase | Weeks | Tasks | Effort | Dependency Chain |
|---|---|---|---|---|
| P1: Scaffold | 1 | 12 | 39h | — |
| P2: POS/ERP Pipeline | 2–4 | 13 | 59h | P1 |
| P3: External Data Pipeline | 5 | 9 | 37h | P1 |
| P4: Feature Engineering | 6–7 | 13 | 52h | P2, P3 |
| P5: Baseline Model | 8–9 | 8 | 36h | P4 |
| P6: Foundation Model | 10–11 | 11 | 62h | P4 |
| P7: Forecast Dashboard | 12–14 | 12 | 62h | P2, P3 |
| P8: Simulator UI | 15–16 | 9 | 45h | P6, P7 |
| P9: Accuracy SLA | 17–18 | 10 | 45h | P6 |
| P10: Admin + Alerts | 19 | 8 | 32h | P7 |
| P11: Production | 20–21 | 10 | 45h | P10 |
| **Total** | **21** | **95** | **410h** | |

## Dependency Graph

```
P1 ──► P2 ──► P4 ──► P5 ──► P6 ──► P8 ──► P10 ──► P11
               │               │
P1 ──► P3 ─────┘               │
                               │
P1 ──────────────────► P7 ────┘
```

P7 (Forecast Dashboard) runs partially parallel with P4–P6 (requires only POS/ERP + External Data endpoints, not ML models). P9 (Accuracy SLA) runs parallel with P8 (requires P6). P10 runs after P7.

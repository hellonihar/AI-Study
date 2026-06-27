# FactoryRL — Project Plan

## Overview

Work breakdown across 11 phases for the MPC + LightGBM factory energy optimization system.

| Role | Focus Areas |
|---|---|
| **Full-stack** | Next.js, Recharts, Tailwind, SSE, Simulator UI |
| **ML** | LightGBM training, feature engineering, model validation, retraining pipeline |
| **Backend** | FastAPI routes, Celery tasks, BMS/ERP adapters, MPC loop, TimescaleDB |
| **Infra** | Docker, K3s, CI/CD, monitoring, Helm, ArgoCD |

---

## Phase 1: Scaffold (Week 1)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 1.1 | Initialize FastAPI project, pydantic-settings config, app factory | 4h | Backend | — | |
| 1.2 | TimescaleDB + PostgreSQL Docker compose with hypertable init | 3h | Infra | 1.1 | |
| 1.3 | InfluxDB OSS Docker compose with bucket + retention policy | 2h | Infra | 1.1 | |
| 1.4 | Celery + Redis Docker compose + Celery app + periodic schedule config | 4h | Backend | 1.1 | |
| 1.5 | Keycloak Docker + realm config + OAuth2 middleware + RBAC roles | 4h | Infra | 1.1 | |
| 1.6 | SQLAlchemy models + Alembic migrations (zones, machines, energy_metrics, production_metrics) | 6h | Backend | 1.2 | |
| 1.7 | TimescaleDB hypertable creation in migration (energy_metrics, production_metrics, mpc_actions, mpc_feedback) | 2h | Backend | 1.6 | |
| 1.8 | MinIO Docker for model artifact storage | 1h | Infra | 1.1 | |
| 1.9 | Prometheus + Grafana + Loki + Tempo Docker compose | 4h | Infra | 1.1 | |
| 1.10 | GitHub Actions CI/CD: build, test, lint, Docker push | 3h | Infra | 1.2–1.9 | |
| 1.11 | Structlog configuration + request ID middleware | 1h | Backend | 1.1 | |

**Phase total: 34h**

---

## Phase 2: BMS Gateway (Weeks 2–4)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 2.1 | BMSAdapter abstract base class + connection lifecycle contract | 4h | Backend | 1.1 | |
| 2.2 | Simulator adapter: lumped thermal model ODE (dT/dt = (P - load - UA×ΔT) / mass) | 8h | Backend | 1.1 | |
| 2.3 | Simulator config: zone params (base_temp, heat_load, thermal_mass, hvac_capacity) | 2h | Backend | 2.2 | |
| 2.4 | Simulator outdoor temp model (daily min/max sinusoid + noise) | 2h | Backend | 2.2 | |
| 2.5 | OPC UA adapter (asyncua): read/write setpoints, subscribe to data changes | 8h | Backend | 2.1 | |
| 2.6 | BACnet/IP adapter (bacpypes3): read zone temps, write setpoints | 8h | Backend | 2.1 | |
| 2.7 | Modbus TCP adapter (pymodbus): read holding registers, write coils | 6h | Backend | 2.1 | |
| 2.8 | MQTT adapter (gmqtt): subscribe to telemetry topics, publish setpoints | 4h | Backend | 2.1 | |
| 2.9 | Celery 60s poller: read all zones → write energy_metrics to TimescaleDB | 4h | Backend | 2.2–2.8, 1.7 | |
| 2.10 | BMS adapter auto-discovery on startup (try each adapter, log success/failure) | 3h | Backend | 2.5–2.8 | |
| 2.11 | Error handling: connection loss retry, stale data detection, circuit breaker | 3h | Backend | 2.9 | |
| 2.12 | Integration test: simulator adapter → TimescaleDB round trip | 2h | Backend | 2.2, 2.9 | |

**Phase total: 54h**

---

## Phase 3: ERP Adapter (Week 5)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 3.1 | Generic REST client: configurable base_url, auth (api_key/oauth2/basic/none), timeout, retry | 6h | Backend | 1.1 | |
| 3.2 | YAML config loader: endpoints, field_mapping, status_mapping | 3h | Backend | 3.1 | |
| 3.3 | Field mapping engine: transform external JSON → internal schema using field_mapping + status_mapping | 4h | Backend | 3.2 | |
| 3.4 | ERP simulator mode: synthetic machine status + work order generation (shift patterns, downtime probability, demand variation) | 6h | Backend | 1.1 | |
| 3.5 | Celery 300s poller: read machines + work orders → write production_metrics to TimescaleDB | 4h | Backend | 3.1, 1.7 | |
| 3.6 | ERP connection health check + alert on failure | 2h | Backend | 3.5 | |

**Phase total: 25h**

---

## Phase 4: Simulator (Weeks 6–7)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 4.1 | Zone thermal model class: lumped mass ODE, configurable UA, capacity, heat_load | 6h | Backend | 2.2 | |
| 4.2 | Multiple zone coupling (shared HVAC plant, adjacent zone heat transfer) | 4h | Backend | 4.1 | |
| 4.3 | Production model: work order → machine → throughput → heat_load per zone | 4h | Backend | 3.4 | |
| 4.4 | Outdoor temperature model (configurable climate zone, seasonal variation, diurnal cycle) | 3h | Backend | 4.1 | |
| 4.5 | Simulator orchestration: step(full_state, hvac_actions) → next_state for all zones + machines | 6h | Backend | 4.2, 4.3, 4.4 | |
| 4.6 | Simulator validation: compare simulated vs. historical data (30 days, MAPE per zone) | 6h | ML | 4.5 + historical data | |
| 4.7 | Feature engineering library (lag, rolling mean/std, interaction, cyclical encoding) | 6h | ML | 4.5 | |
| 4.8 | Simulator benchmark test: 4h horizon simulation speed (<100ms target) | 2h | Backend | 4.5 | |

**Phase total: 37h**

---

## Phase 5: Dynamics Model (Weeks 8–9)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 5.1 | Training data pipeline: extract 30 days from TimescaleDB, feature engineering, train/val split (temporal) | 6h | ML | 4.7, 1.7 | |
| 5.2 | LightGBM model training: 3 models (zone_temps, hvac_power, throughput), hyperparameter tuning | 8h | ML | 5.1 | |
| 5.3 | Multi-step prediction: iterative (predict step → feed back as input → predict next) | 4h | ML | 5.2 | |
| 5.4 | Model validation: MAPE at 1h/2h/4h horizons, residual plots, feature importance analysis | 6h | ML | 5.3 | |
| 5.5 | Feature pruning: keep top 20 features by importance, retrain, validate | 3h | ML | 5.4 | |
| 5.6 | Model export: save .lgbm file + metadata.json (features, MAPE, train_date, hyperparams) to MinIO + MLflow | 3h | ML | 5.5 | |
| 5.7 | Weekly retrain Celery cron (Sunday 02:00): check data, train, compare MAPE, deploy if better | 4h | ML | 5.6, 1.4 | |
| 5.8 | Anomaly-triggered retrain: monitor feedback MAPE, trigger if >15% for 3 consecutive cycles | 3h | Backend | 5.7, 6.7 | |

**Phase total: 37h**

---

## Phase 6: MPC Controller (Weeks 10–11)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 6.1 | Constraint config loader: zones.yaml + constraints.yaml (temp bounds, power cap, ramp limits) | 3h | Backend | 1.1 | |
| 6.2 | Weight config loader: weights.yaml (alpha, beta, gamma) with per-time-of-day overrides | 2h | Backend | 1.1 | |
| 6.3 | Objective function: sum over 16-step horizon of energy_cost + throughput_loss + comfort_violation | 6h | Backend | 5.2 | |
| 6.4 | State vector builder: assemble current state from TimescaleDB (latest energy + production metrics) | 4h | Backend | 1.7, 2.9, 3.5 | |
| 6.5 | scipy SLSQP solver wrapper: decision variables bounds, constraint functions, iteration limits | 6h | Backend | 6.3, 6.1 | |
| 6.6 | Multi-start initialization (3 random starting points, pick best cost) to avoid local minima | 4h | Backend | 6.5 | |
| 6.7 | MPC Celery task (15-min schedule): read state → solve → apply first action → log to TimescaleDB | 6h | Backend | 6.4, 6.6, 1.4 | |
| 6.8 | Action application: write setpoints to BMS, publish schedule recommendation to SSE | 4h | Backend | 6.7, 2.1 | |
| 6.9 | Feedback logging: 10 min after action, compare predicted vs. actual, write to mpc_feedback table | 4h | Backend | 6.7, 1.7 | |
| 6.10 | MPC status endpoint: last_run, solver_status, cost, model_version, health check | 2h | Backend | 6.7 | |
| 6.11 | Safety limits: hard clamp on setpoints (never exceed zone temp bounds), override if solver fails | 3h | Backend | 6.5 | |

**Phase total: 44h**

---

## Phase 7: Frontend Dashboard (Weeks 12–14)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 7.1 | Next.js project scaffold + Tailwind config + API client library | 4h | Full-stack | — | |
| 7.2 | Dashboard page: energy intensity gauge (Chart.js gauge), zone temp grid, throughput sparkline | 8h | Full-stack | 1.1 | |
| 7.3 | SSE client utility (EventSource with auto-reconnect, event demux) | 4h | Full-stack | 7.1 | |
| 7.4 | Dashboard real-time updates: subscribe to energy.update + mpc.action_taken SSE events | 4h | Full-stack | 7.2, 7.3 | |
| 7.5 | Zone card component: temp, humidity, setpoint, power draw, HVAC state indicator | 6h | Full-stack | 7.1 | |
| 7.6 | MPC suggestion badge on zone card: RL-recommended setpoint, predicted savings, accept/override | 6h | Full-stack | 7.5, 6.10 | |
| 7.7 | Manual setpoint override form (popup confirmation, reason logging, revert countdown) | 4h | Full-stack | 7.5 | |
| 7.8 | HVAC page: zone grid layout, zone card grid, MPC suggestion overlay, batch apply | 8h | Full-stack | 7.5–7.7 | |
| 7.9 | Production page: schedule Gantt chart (Recharts custom), work order cards, MPC-optimized overlay | 10h | Full-stack | 7.1, 3.5 | |
| 7.10 | MPC status panel: last run time, solver status, current cost, model version, reward trend mini-chart | 4h | Full-stack | 6.10 | |
| 7.11 | SSE integration test: connect → receive events → update UI | 2h | Full-stack | 7.3 | |

**Phase total: 60h**

---

## Phase 8: Simulator UI (Weeks 15–16)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 8.1 | Simulator page layout: parameter panel + results panel side-by-side | 4h | Full-stack | 7.1 | |
| 8.2 | Parameter sliders: outdoor temp range, production load %, MPC on/off toggle, time of day | 6h | Full-stack | 8.1 | |
| 8.3 | "Run Simulation" button → POST /api/simulate → display loading state | 3h | Full-stack | 8.2, 1.1 | |
| 8.4 | Side-by-side comparison chart: HVAC energy + zone temps + throughput (MPC vs. no-MPC) | 10h | Full-stack | 8.3 | |
| 8.5 | Savings summary bar: energy reduction %, throughput impact, comfort violation hours | 4h | Full-stack | 8.4 | |
| 8.6 | Simulation history table: previous runs with parameters and results | 3h | Full-stack | 8.3 | |
| 8.7 | PDF export (puppeteer or jsPDF) of simulation report | 6h | Full-stack | 8.5 | |
| 8.8 | API: POST /api/simulate (run simulator with custom params, return full results) | 6h | Backend | 4.5, 5.2 | |

**Phase total: 42h**

---

## Phase 9: Savings Verification (Weeks 17–18)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 9.1 | Baseline computation: aggregate 30-day pre-MPC energy + production → energy intensity (kWh/unit) | 4h | ML | 1.7 | |
| 9.2 | Baseline adjustment model: weather normalization (HDD/CDD regression), production volume adjustment | 6h | ML | 9.1 | |
| 9.3 | IPMVP Option D adjusted baseline: run simulator with actual weather + production but without MPC | 6h | ML | 9.2, 4.5 | |
| 9.4 | Gross savings = adjusted baseline energy − actual energy (daily aggregation) | 2h | ML | 9.3 | |
| 9.5 | Net savings = gross savings − non-RP factors (weather, production mix, equipment changes) | 3h | ML | 9.4 | |
| 9.6 | Confidence scoring: statistical significance (t-test), confidence interval, sample size check | 3h | ML | 9.5 | |
| 9.7 | Savings table in analytics page: period, baseline, actual, adjusted, gross, net, confidence | 6h | Full-stack | 9.1–9.6 | |
| 9.8 | Savings trend chart: daily/weekly energy intensity with baseline overlay | 4h | Full-stack | 9.7 | |
| 9.9 | CSV export of verification report | 2h | Full-stack | 9.7 | |
| 9.10 | Daily savings Celery task: compute and store verification record | 3h | Backend | 9.6, 1.4 | |

**Phase total: 39h**

---

## Phase 10: Admin + Alerts (Week 19)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 10.1 | Model version table: MLflow integration, list models with MAPE, train date, feature count | 4h | Full-stack | 5.6 | |
| 10.2 | Prediction error chart: MAPE over last 30 days, breakdown by zone + horizon step | 4h | Full-stack | 6.9 | |
| 10.3 | Feature importance bar chart (LightGBM gain) for each of 3 models | 3h | Full-stack | 5.4 | |
| 10.4 | Constraint editor UI: zone temp bounds, power limits, ramp rates — YAML form with validation | 6h | Full-stack | 6.1 | |
| 10.5 | Weight editor UI: alpha/beta/gamma sliders with per-time-of-day overrides | 4h | Full-stack | 6.2 | |
| 10.6 | Alert rule config: threshold per metric (energy spike, comfort violation, solver failure), severity, notification channel | 6h | Full-stack | 1.9 | |
| 10.7 | Unleash feature flag SDK integration + admin UI toggles (MPC per zone, simulation mode) | 3h | Backend | 1.1 | |

**Phase total: 30h**

---

## Phase 11: Production (Weeks 20–21)

| # | Task | Effort | Owner | Depends On | Status |
|---|---|---|---|---|---|
| 11.1 | K3s cluster setup + namespace structure (dev/staging/prod) | 4h | Infra | P10 complete | |
| 11.2 | Helm charts for all 7 services (FastAPI, Celery, TimescaleDB, InfluxDB, Redis, Keycloak, Next.js) | 8h | Infra | 11.1 | |
| 11.3 | ArgoCD app-of-apps GitOps configuration | 4h | Infra | 11.2 | |
| 11.4 | Prometheus recording rules + Alertmanager alert rules (from 10.6) | 4h | Infra | 11.1 | |
| 11.5 | Grafana dashboard provisioning as code (ConfigMap): energy overview, MPC performance, model drift | 4h | Infra | 11.4 | |
| 11.6 | Load testing: k6 script for API endpoints + Celery task backlog test (100 concurrent simulations) | 4h | Infra | 11.1 | |
| 11.7 | Performance tuning: Celery worker concurrency, TimescaleDB chunk size, InfluxDB retention | 3h | Backend | 11.6 | |
| 11.8 | Security audit checklist: authentication, data encryption, network policies, secrets management | 3h | Infra | 11.1 | |
| 11.9 | Runbook per service: startup, failure, scaling, backup, restore | 4h | All | 11.2–11.8 | |
| 11.10 | Production readiness review + go/no-go decision | 2h | All | 11.1–11.9 | |

**Phase total: 40h**

---

## Summary

| Phase | Weeks | Tasks | Effort | Dependency Chain |
|---|---|---|---|---|
| P1: Scaffold | 1 | 11 | 34h | — |
| P2: BMS Gateway | 2–4 | 12 | 54h | P1 |
| P3: ERP Adapter | 5 | 6 | 25h | P1 |
| P4: Simulator | 6–7 | 8 | 37h | P2, P3 |
| P5: Dynamics Model | 8–9 | 8 | 37h | P4 |
| P6: MPC Controller | 10–11 | 11 | 44h | P5 |
| P7: Frontend Dashboard | 12–14 | 11 | 60h | P2, P3 |
| P8: Simulator UI | 15–16 | 8 | 42h | P6, P7 |
| P9: Savings Verification | 17–18 | 10 | 39h | P6 |
| P10: Admin + Alerts | 19 | 7 | 30h | P8 |
| P11: Production | 20–21 | 10 | 40h | P10 |
| **Total** | **21** | **102** | **442h** | |

## Dependency Graph

```
P1 ──► P2 ──► P4 ──► P5 ──► P6 ──► P8 ──► P10 ──► P11
              │                       │
P1 ──► P3 ───┘                       │
                                      │
P1 ───────────────────────► P7 ──────┘
                              │
P6 ──► P9 ───────────────────┘
```

P7 (Frontend) runs partially parallel with P4–P6 (requires only BMS + ERP endpoints, not MPC). P9 (Savings) runs parallel with P8 (requires P6). P10 runs after P8.

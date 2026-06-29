# StockSight — Design Document

## Overview

StockSight is an AI-powered inventory forecasting system that reduces stockout rates from 8% to <3% and overstock from 12% to <5% by combining time-series foundation models (Lag-Llama / PatchTFT) with promotional, weather, and competitor price signals. The system ingests POS transaction streams, ERP inventory snapshots, and external data sources to generate multi-horizon demand forecasts at SKU-store-day granularity, with automated retraining and accuracy SLA monitoring.

---

## Project Structure

```
stocksight/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application factory
│   ├── config.py                # Settings via pydantic-settings
│   ├── dependencies.py          # DB session, auth, rate limit deps
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── forecasts.py         # /api/forecasts/* CRUD + query
│   │   ├── inventory.py         # /api/inventory/* current + history
│   │   ├── pos.py               # /api/pos/* transaction data
│   │   ├── promotions.py        # /api/promotions/* calendar + uplift
│   │   ├── accuracy.py          # /api/accuracy/* SLA monitoring
│   │   ├── dashboard.py         # /ui/dashboard
│   │   ├── analytics.py         # /ui/analytics
│   │   ├── simulator.py         # /ui/simulator
│   │   └── admin.py             # /ui/admin
│   ├── models/
│   │   ├── __init__.py
│   │   ├── sku.py               # SQLAlchemy: SKU, Category, Attributes
│   │   ├── store.py             # SQLAlchemy: Store, Region, Zone
│   │   ├── inventory.py         # SQLAlchemy: InventoryLevel (hypertable)
│   │   ├── pos.py               # SQLAlchemy: POSTransaction (hypertable)
│   │   ├── promotion.py         # SQLAlchemy: Promotion, PromoEffect
│   │   ├── forecast.py          # SQLAlchemy: Forecast, ForecastItem
│   │   └── accuracy.py          # SQLAlchemy: AccuracyRecord
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── forecast.py          # Pydantic: ForecastRequest, ForecastResponse
│   │   ├── inventory.py         # Pydantic: InventoryResponse
│   │   ├── accuracy.py          # Pydantic: AccuracyReport, SLAStatus
│   │   └── pagination.py        # Pydantic: Page, PageParams
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pos_ingestion.py     # POS transaction consumer (Kafka/API)
│   │   ├── erp_sync.py          # ERP inventory snapshot sync
│   │   ├── weather_feed.py      # Weather API client + cache
│   │   ├── competitor_pricing.py # Competitor scrape pipeline
│   │   ├── feature_engine.py    # Feature engineering library
│   │   ├── baseline_model.py    # Prophet / ARIMA baseline
│   │   ├── foundation_model.py  # Lag-Llama / PatchTFT inference
│   │   ├── forecast_orch.py     # Forecast orchestration (ensemble)
│   │   └── accuracy_monitor.py  # SLA tracking + drift detection
│   ├── templates/               # Jinja2 + HTMX
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── forecast_detail.html
│   │   ├── sku_detail.html
│   │   ├── analytics.html
│   │   ├── simulator.html
│   │   └── admin.html
│   └── static/
│       ├── css/
│       └── js/
├── workers/
│   ├── __init__.py
│   ├── celery_app.py            # Celery config + task definitions
│   ├── pos_worker.py            # ingest_pos_transactions task
│   ├── erp_worker.py            # sync_erp_inventory task
│   ├── weather_worker.py        # fetch_weather_forecast task
│   ├── competitor_worker.py     # scrape_competitor_pricing task
│   ├── feature_worker.py        # engineer_features task
│   ├── forecast_worker.py       # generate_forecast task
│   └── accuracy_worker.py       # compute_accuracy task
├── models/                      # ML model artifacts
│   ├── lag-llama/               # Lag-Llama fine-tuned checkpoint
│   ├── prophet/                 # Prophet baseline models per SKU
│   └── scalers/                 # MinMaxScaler per SKU family
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
                     ┌─────────────────────────────────────┐
                     │     FastAPI + Next.js (4 workers)     │
                     │  /api/* REST  ·  /ui/* SSR + SSE      │
                     │  Keycloak OAuth  ·  Rate Limiting      │
                     └────────┬────────────────────────────┘
                              │ Celery tasks
                 ┌────────────▼────────────────────────────┐
                 │         RabbitMQ / Celery                 │
                 │   (task routing by data domain)           │
                 └───┬───────────┬───────────┬─────────────┘
                     │           │           │
           ┌─────────▼───┐ ┌─────▼─────┐ ┌──▼──────────────┐
           │ Ingestion   │ │ Feature   │ │ Forecast        │
           │ Workers     │ │ Workers   │ │ Workers         │
           │ (CPU, 4GB)  │ │ (CPU, 8GB)│ │ (CPU, 16GB)     │
           │             │ │           │ │                 │
           │ POS/ERP     │ │ Lag feats │ │ Prophet         │
           │ Weather     │ │ Rolling   │ │ Lag-Llama       │
           │ Competitor  │ │ Encoding  │ │ PatchTFT        │
           └─────────────┘ └───────────┘ │ Ensemble        │
                                         └─────────────────┘
                     ┌─────────────────────────────────────┐
                     │     Shared Data Layer                │
                     │  TimescaleDB + PostgreSQL            │
                     │  Redis (cache + rate limits)         │
                     │  MinIO (model artifacts)             │
                     └─────────────────────────────────────┘
                     ┌─────────────────────────────────────┐
                     │     Observability                    │
                     │  Prometheus · Grafana · Loki         │
                     │  OpenTelemetry · Tempo (traces)      │
                     └─────────────────────────────────────┘
```

### Data Flow

```
POS System ──► Kafka ──► pos_worker ──► TimescaleDB (pos_transactions)
ERP System ──► API ────► erp_worker ───► TimescaleDB (inventory_levels)
Weather API ──► HTTP ──► weather_worker ──► TimescaleDB (weather_forecasts)
Competitor ───► HTTP ──► competitor_worker ──► TimescaleDB (competitor_pricing)

                              │
                              ▼
                    feature_worker (daily cron)
                              │
                              ▼
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
    baseline_forecast   foundation_forecast   ensemble_forecast
    (Prophet)           (Lag-Llama / PatchTFT) (weighted blend)

                              │
                              ▼
                    TimescaleDB (forecasts)
                              │
                              ▼
                    accuracy_worker (daily)
                              │
                              ▼
                    TimescaleDB (accuracy_records)
```

---

## Data Models

### TimescaleDB Hypertables

```sql
-- SKU master
CREATE TABLE skus (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_code        VARCHAR(64) UNIQUE NOT NULL,
    sku_name        VARCHAR(256) NOT NULL,
    category_id     UUID REFERENCES categories(id),
    family_id       UUID REFERENCES families(id),
    unit_type       VARCHAR(32),                 -- 'each' | 'kg' | 'liter' | 'case'
    avg_cost        DECIMAL(10,2),
    avg_price       DECIMAL(10,2),
    lead_time_days  INTEGER,
    min_stock_level DECIMAL(10,2),
    max_stock_level DECIMAL(10,2),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE stores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_code      VARCHAR(32) UNIQUE NOT NULL,
    store_name      VARCHAR(256) NOT NULL,
    region          VARCHAR(64),
    cluster         VARCHAR(64),                 -- store cluster for transfer learning
    square_footage  INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Hypertable: POS transactions (daily aggregation)
CREATE TABLE pos_transactions (
    time            TIMESTAMPTZ NOT NULL,        -- date of sale
    sku_id          UUID NOT NULL REFERENCES skus(id),
    store_id        UUID NOT NULL REFERENCES stores(id),
    quantity_sold   DECIMAL(12,2) NOT NULL,
    revenue         DECIMAL(12,2) NOT NULL,
    price           DECIMAL(10,2) NOT NULL,      -- actual selling price (after promo)
    is_promo        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('pos_transactions', 'time', chunk_time_interval => INTERVAL '7 days');
CREATE INDEX idx_pos_sku_store ON pos_transactions(sku_id, store_id, time DESC);

-- Hypertable: Inventory levels (snapshot-based)
CREATE TABLE inventory_levels (
    time            TIMESTAMPTZ NOT NULL,        -- snapshot timestamp
    sku_id          UUID NOT NULL REFERENCES skus(id),
    store_id        UUID NOT NULL REFERENCES stores(id),
    on_hand_qty     DECIMAL(12,2) NOT NULL,
    in_transit_qty  DECIMAL(12,2) DEFAULT 0,
    reserved_qty    DECIMAL(12,2) DEFAULT 0,
    available_qty   DECIMAL(12,2) GENERATED ALWAYS AS (on_hand_qty - reserved_qty) STORED,
    stockout_flag   BOOLEAN GENERATED ALWAYS AS (available_qty <= 0) STORED,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('inventory_levels', 'time', chunk_time_interval => INTERVAL '7 days');

-- Hypertable: Weather forecasts (daily)
CREATE TABLE weather_forecasts (
    time            TIMESTAMPTZ NOT NULL,
    store_id        UUID NOT NULL REFERENCES stores(id),
    temp_high_c     DECIMAL(5,1),
    temp_low_c      DECIMAL(5,1),
    precipitation_mm DECIMAL(6,1),
    humidity_pct    DECIMAL(5,1),
    wind_speed_kmh  DECIMAL(5,1),
    condition       VARCHAR(64),                 -- 'sunny' | 'rainy' | 'snowy' | 'cloudy'
    confidence_pct  DECIMAL(5,1),               -- forecast confidence
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('weather_forecasts', 'time', chunk_time_interval => INTERVAL '7 days');

-- Hypertable: Competitor pricing snapshots
CREATE TABLE competitor_pricing (
    time            TIMESTAMPTZ NOT NULL,
    sku_id          UUID NOT NULL REFERENCES skus(id),
    competitor_name VARCHAR(128) NOT NULL,
    price           DECIMAL(10,2) NOT NULL,
    is_promo        BOOLEAN DEFAULT FALSE,
    confidence      VARCHAR(16),                 -- 'scraped' | 'estimated' | 'missing'
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('competitor_pricing', 'time', chunk_time_interval => INTERVAL '7 days');

-- Promotions calendar
CREATE TABLE promotions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          UUID REFERENCES skus(id),
    category_id     UUID REFERENCES categories(id),
    promotion_name  VARCHAR(256) NOT NULL,
    discount_pct    DECIMAL(5,2),
    discount_amount DECIMAL(10,2),
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    expected_lift_pct DECIMAL(5,2),             -- planned uplift estimate
    actual_lift_pct DECIMAL(5,2),               -- post-promo measurement
    promotion_type  VARCHAR(32),                 -- 'percentage' | 'bogo' | 'clearance' | 'seasonal'
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Forecast Output Tables

```sql
-- Hypertable: Forecast outputs
CREATE TABLE forecasts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_date   DATE NOT NULL,               -- date forecast was generated
    target_date     DATE NOT NULL,                -- forecasted date
    sku_id          UUID NOT NULL REFERENCES skus(id),
    store_id        UUID NOT NULL REFERENCES stores(id),
    model_type      VARCHAR(32) NOT NULL,         -- 'prophet' | 'lag_llama' | 'patchtft' | 'ensemble'
    model_version   VARCHAR(32) NOT NULL,
    q10             DECIMAL(12,2),               -- 10th percentile
    q50             DECIMAL(12,2),               -- median forecast
    q90             DECIMAL(12,2),               -- 90th percentile
    point_forecast  DECIMAL(12,2) NOT NULL,      -- point estimate
    features_used   JSONB,                       -- snapshot of features used for inference
    confidence      DECIMAL(5,2),                -- model confidence score
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(forecast_date, target_date, sku_id, store_id, model_type)
);
SELECT create_hypertable('forecasts', 'target_date', chunk_time_interval => INTERVAL '30 days');
CREATE INDEX idx_forecast_lookup ON forecasts(sku_id, store_id, target_date DESC);

-- Accuracy records
CREATE TABLE accuracy_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_date DATE NOT NULL,
    sku_id          UUID REFERENCES skus(id),
    store_id        UUID REFERENCES stores(id),
    model_type      VARCHAR(32) NOT NULL,
    model_version   VARCHAR(32) NOT NULL,
    horizon_days    INTEGER NOT NULL,            -- 1, 7, 14, 30
    mape            DECIMAL(8,4),                -- Mean Absolute Percentage Error
    rmse            DECIMAL(12,4),               -- Root Mean Squared Error
    mae             DECIMAL(12,4),               -- Mean Absolute Error
    bias            DECIMAL(8,4),                -- avg(forecast - actual)
    stockout_hit_rate DECIMAL(5,2),              -- % of stockout days correctly predicted
    samples_count   INTEGER NOT NULL,            -- number of SKU-store pairs evaluated
    sla_met         BOOLEAN,                     -- whether accuracy SLA was met
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('accuracy_records', 'evaluation_date', chunk_time_interval => INTERVAL '30 days');
```

---

## API Design

### REST Endpoints

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| `GET` | `/api/forecasts` | List forecasts | `?sku_id=&store_id=&target_date_from=&target_date_to=&model_type=` | `Page<ForecastResponse>` |
| `GET` | `/api/forecasts/latest` | Latest forecast for SKU-store | `?sku_id=&store_id=` | `ForecastResponse` |
| `POST` | `/api/forecasts/generate` | Trigger forecast generation | `{sku_ids[], store_ids[], horizon_days}` | `202: {task_id}` |
| `GET` | `/api/inventory/current` | Current inventory levels | `?sku_id=&store_id=&stockout_only=` | `InventoryResponse[]` |
| `GET` | `/api/inventory/history` | Historical inventory time-series | `?sku_id=&store_id=&from=&to=&granularity=` | `TimeSeriesResponse` |
| `GET` | `/api/pos/sales` | POS sales history | `?sku_id=&store_id=&from=&to=&granularity=` | `TimeSeriesResponse` |
| `GET` | `/api/accuracy` | Accuracy reports | `?from=&to=&model_type=&horizon=` | `AccuracyReport` |
| `GET` | `/api/accuracy/sla` | SLA dashboard status | `?period=last_7d|last_30d|last_90d` | `SLAStatus` |
| `GET` | `/api/promotions` | List promotions | `?active=&sku_id=&from=&to=` | `Promotion[]` |
| `POST` | `/api/promotions` | Create promotion | `{sku_id, discount_pct, start_date, end_date}` | `201: Promotion` |
| `GET` | `/api/skus` | List SKUs | `?category_id=&family_id=&search=` | `Page<SKUResponse>` |
| `GET` | `/api/skus/{id}` | SKU detail with forecast summary | — | `SKUDetailResponse` |
| `POST` | `/api/simulate` | What-if simulation | `{scenario params}` | `SimulationResponse` |

### SSE Events

| Event | Direction | Payload |
|---|---|---|
| `forecast.generated` | Server → Client | `{sku_id, store_id, forecast_date, model_type}` |
| `accuracy.sla_breached` | Server → Client | `{model_type, horizon, current_mape, sla_threshold}` |
| `stockout.risk` | Server → Client | `{sku_id, store_id, predicted_stockout_date, confidence}` |
| `retraining.completed` | Server → Client | `{model_type, old_version, new_version, mape_delta}` |

---

## Pipeline State Machine

```
                    ┌──────────┐
                    │  RAW     │  Ingested from POS/ERP, not processed
                    └────┬─────┘
                         │ feature_worker (daily cron)
                    ┌────▼──────┐
                    │ FEATURED  │  Lag features, rolling stats, external signals
                    └────┬──────┘
                         │ forecast_worker (daily + on-demand)
               ┌─────────┼─────────┐
               │         │         │
          ┌────▼───┐ ┌──▼────┐ ┌──▼───────┐
          │PROPHET │ │LAG-   │ │PATCHTFT  │
          │FORECAST│ │LLAMA  │ │FORECAST  │
          └────┬───┘ └──┬────┘ └──┬───────┘
               │         │         │
               └─────────┼─────────┘
                         │ ensemble_worker
                    ┌────▼──────┐
                    │ ENSEMBLE  │  Weighted blend by horizon
                    └────┬──────┘
                         │ accuracy_worker (daily, T+1)
                    ┌────▼──────┐
                    │ EVALUATED │  MAPE/RMSE computed, SLA checked
                    └────┬──────┘
                         │
                    ┌────▼──────┐
                    │ RETRAIN   │  Weekly cron + anomaly-triggered
                    └───────────┘
```

---

## Components

### FastAPI Application

- **4 Uvicorn workers** behind reverse proxy (Caddy/Traefik)
- **Middleware**: CORS, rate limiting (Redis-backed), request ID, OpenTelemetry tracing, audit logging
- **Auth**: Keycloak OAuth 2.0 with RBAC — roles: `planner`, `manager`, `admin`
- **Frontend**: Next.js with Recharts for complex forecast visualizations, SSE for real-time updates

### Celery Workers

| Worker | Concurrency | Resource | Task | Schedule |
|---|---|---|---|---|
| `pos_worker` | 2 processes | CPU, 4GB | Ingest POS transactions from Kafka/API | Continuous (stream) |
| `erp_worker` | 2 processes | CPU, 4GB | Sync inventory levels from ERP | Every 4h |
| `weather_worker` | 1 process | CPU, 2GB | Fetch weather forecast from API | Every 6h |
| `competitor_worker` | 2 processes | CPU, 4GB | Scrape competitor pricing | Daily |
| `feature_worker` | 2 processes | CPU, 8GB | Engineer all features for active SKUs | Daily (02:00) |
| `forecast_worker` | 2 processes | CPU, 16GB | Run Prophet + foundation model + ensemble | Daily (04:00) |
| `accuracy_worker` | 1 process | CPU, 4GB | Compute accuracy metrics against actuals | Daily (T+1, 06:00) |

### Feature Engineering

The feature library produces ~40 features per SKU-store-day:

| Category | Features | Source |
|---|---|---|
| **Demand history** | Sales D-1, D-7, D-14, D-28, D-365; rolling mean (7d, 28d), rolling std, trend | POS |
| **Calendar** | Day of week, month, holiday flag, holiday D-7/D+7, season | Calendar API |
| **Promotion** | Current promo flag, discount depth, days since last promo, promo lift estimate | Promotions DB |
| **Pricing** | Current price, price change D-1/D-7, competitor price min/max/avg, price gap % | Competitor |
| **Weather** | Temp (high/low), precipitation, weather condition one-hot, extreme weather flag | Weather API |
| **Inventory** | Current stock level, stockout flag D-1/D-7/D-28, days of cover, in-transit qty | Inventory DB |
| **Interaction** | Promo × weather, holiday × category, price × competitor gap | Derived |
| **SKU attributes** | Category, family, avg price tier, lead time bracket, seasonality score | SKU master |

### Forecast Models

#### Baseline: Prophet

- Runs for every active SKU-store combination (~50K pairs for mid-size retailer)
- Captures trend, weekly seasonality, yearly seasonality
- Includes holiday and promotion regressors
- Used as fallback when foundation model confidence is low
- Training: monthly retrain, 15min per 1K SKUs

#### Foundation Model: Lag-Llama / PatchTFT

- **Training**: Fine-tune on 2+ years of SKU-store sales data
- **Inference**: 5ms per SKU-store on CPU (ONNX export)
- **Horizon**: 1, 7, 14, 30, 90 days
- **Quantile outputs**: p10, p50, p90 for safety stock calculation
- **Cold-start**: Transfer from similar SKUs in same category (embedding similarity)
- **Retraining**: Weekly full retrain + daily incremental update

#### Ensemble

- Horizon-weighted blend: Prophet weights higher for short horizons, foundation model weights higher for long horizons
- Weight optimization: rolling 30-day MAPE minimization per SKU-cluster
- Confidence score: based on historical accuracy at similar demand patterns

---

## Design Decisions & Trade-offs

### 1. Foundation Model Selection: Lag-Llama vs. PatchTFT

| Dimension | Lag-Llama | PatchTFT |
|---|---|---|
| **Architecture** | Decoder-only LLM for time-series | Transformer with encoder-decoder + patching |
| **Pre-training** | 3B+ time-series samples (mostly non-retail) | Needs domain-specific pre-training |
| **Few-shot capability** | Strong — works with as few as 30 days of data | Requires more data (>200 days per SKU) |
| **Inference speed (CPU)** | ~8ms per SKU-store (ONNX) | ~12ms per SKU-store (ONNX) |
| **Quantile output** | Native (distribution head) | Requires post-hoc quantile regression |
| **Cold-start** | Transfer learning from similar SKUs works well | Requires full retraining |

**Decision**: Start with **Lag-Llama** as the primary foundation model for its strong few-shot performance and native quantile outputs. PatchTFT is the upgrade path if accuracy targets aren't met at 30-day horizon.

### 2. Forecast Granularity: SKU-Store-Day

| Option | Pro | Con | Decision |
|---|---|---|---|
| **SKU-Store-Day** | Granular enough for inventory planner decisions | 50K+ SKU-store pairs → 50M forecasts/day | **Chosen** — allows per-store safety stock optimization |
| SKU-Region-Day | Reduces model count by 10× | Loses store-level variation (traffic, demographics) | Rejected — too coarse for stockout prevention |
| Category-Store-Week | Fast to train and serve | Useless for SKU-level purchasing decisions | Rejected — insufficient for procurement |

The 50M daily forecast challenge is addressed by:
- ONNX export of all models (~5ms per inference → 250K inferences/sec on 4 workers)
- Batched inference with GPU fallback during nightly batch runs
- Only forecasting active SKUs (typically 60-70% of catalog)

### 3. Cold-Start Strategy for New SKUs

**Chosen**: Embedding-based transfer from similar SKUs.

| Method | Approach | Accuracy (30-day) |
|---|---|---|
| **Category mean** | Use average sales of all SKUs in same category | ±55% MAPE |
| **Attribute matching** | Match on price tier, seasonality, category, weight | ±35% MAPE |
| **Embedding transfer** | Lag-Llama cold-start with fine-tuning on 30 days | ±20% MAPE |
| **Full fine-tune** | Wait for 90 days of data before including in model | ±12% MAPE (but delayed) |

**Implementation**:
- New SKUs start in "cold" mode: embedding transfer + category mean fallback
- After 30 days of sales data: auto-include in next weekly retrain cycle
- Forecast uncertainty band is widened by 1.5× for cold SKUs

### 4. Promotion Uplift Modeling

| Method | Approach | Accuracy |
|---|---|---|
| **Heuristic** | Rule-based: 50% off → 3× baseline (category average) | ±80% MAPE |
| **Historical regression** | Log-linear model: log(sales) = log(price) + promo_flags + seasonality | ±40% MAPE |
| **Foundation model with promo features** | Include discount_pct + promo_type + days_since_last_promo as features | ±25% MAPE |
| **Dedicated uplift model** | Meta-learners (S-Learner, T-Learner) on promo vs. non-promo periods | ±18% MAPE |

**Decision**: Start with promotion features in the foundation model (captures main effects). Add a dedicated uplift model (lightweight XGBoost) for promotional periods to handle selection bias (promotions aren't randomly assigned).

### 5. Ensemble Strategy

| Horizon | Prophet Weight | Foundation Weight | Rationale |
|---|---|---|---|
| 1-7 days | 0.4 | 0.6 | Short-term: both strong, foundation slightly better |
| 8-30 days | 0.2 | 0.8 | Medium-term: foundation captures complex patterns |
| 31-90 days | 0.1 | 0.9 | Long-term: foundation handles seasonality better |

Weights are recalculated weekly per SKU cluster based on rolling 30-day MAPE.

### 6. Next.js over HTMX for Frontend

| Decision | Chosen | Rejected | Rationale |
|---|---|---|---|
| Rendering | Next.js + Recharts | FastAPI + Jinja2 + HTMX | Forecast dashboard needs complex interactive charts (multi-horizon comparison, zoomable time-series, what-if sliders) that HTMX round-trips can't handle smoothly |
| Charts | Recharts | Chart.js, D3.js | Recharts is React-native, composable, and handles time-series with built-in zoom/pan |
| State management | React hooks + SWR | Alpine.js, Redux | SWR provides cache-first data fetching ideal for forecast data that refreshes daily |

### 7. TimescaleDB over Standard PostgreSQL

| Feature | Standard PostgreSQL | TimescaleDB | Why It Matters |
|---|---|---|---|
| Hypertables | No (manual partitioning) | Automatic chunked tables | 50M+ rows of time-series data per month |
| Compression | TOAST only | Native columnar compression | 90%+ storage savings on historical data |
| Continuous aggregates | Manual materialized views | Auto-refreshed views | Daily accuracy rollups without ETL |
| Time-based retention | Manual DELETE | Automatic data retention policy | Auto-drop data older than 3 years |

### 8. Celery over Airflow

| Dimension | Celery + RabbitMQ | Airflow |
|---|---|---|
| Scheduling | Task-level cron + dependencies | DAG-based scheduling with backfill |
| Latency | Sub-second (RabbitMQ push) | Minute-level (scheduler poll) |
| Real-time ingestion | Yes (RabbitMQ consumer) | No (batch-oriented) |
| Team familiarity | High | Medium |
| Decision | **Chosen** | Rejected |

Airflow is better for complex DAG pipelines with backtracking, but StockSight's pipeline is a linear daily chain (ingest → feature → forecast → evaluate). Celery handles this with simpler infrastructure and sub-second task dispatch for real-time POS ingestion.

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| API server | FastAPI + Uvicorn | 0.115+ | Async REST API, SSE events |
| Frontend | Next.js + Recharts | 14+ | Forecast dashboard, interactive charts |
| Task queue | Celery + RabbitMQ | 5.4+ | Async ingestion + forecast pipeline |
| Time-series DB | TimescaleDB (PostgreSQL 16) | 2.15+ | Hypertables for all time-series data |
| Vector storage | pgvector | 0.7+ | SKU similarity search for cold-start |
| Object store | MinIO | LATEST | Model artifacts, historical exports |
| Weather API | OpenWeatherMap / NOAA | — | Temperature, precipitation, conditions |
| Competitor data | Custom scraper (Playwright) | — | Competitor price tracking |
| Baseline model | Prophet (Meta) | 1.1+ | Statistical baseline + fallback |
| Foundation model | Lag-Llama (Time-series LLM) | HF transformers | Primary forecast engine |
| Model format | ONNX Runtime | 1.17+ | CPU-optimized inference |
| Feature store | Feature-engine (custom) | — | ~40 features per SKU-store-day |
| Auth | Keycloak | 24+ | OAuth 2.0, RBAC, LDAP sync |
| Feature flags | Unleash | 5+ | Gradual model rollout |
| Monitoring | Prometheus + Grafana + Tempo | LATEST | Metrics, tracing, alerting |
| Logging | Grafana Loki + Promtail | 3+ | Structured log aggregation |
| CI/CD | GitHub Actions + ArgoCD + Helm | LATEST | GitOps deployment |
| Infrastructure | Docker Compose (dev) / K3s (prod) | LATEST | Container orchestration |

---

## Monitoring & Observability

### Prometheus Metrics

```
stocksight_forecast_count{model_type, horizon}       — Counter: forecasts generated per model
stocksight_mape{model_type, horizon, sku_cluster}     — Gauge: MAPE by model and horizon
stocksight_sla_compliance_pct{model_type, horizon}    — Gauge: % of SKUs meeting SLA
stocksight_worker_queue_depth{worker}                 — Gauge: Celery queue depth
stocksight_inference_time_ms{model_type}              — Histogram: inference latency
stocksight_feature_compute_time_ms                    — Histogram: feature engineering latency
stocksight_data_lag_hours{source}                     — Gauge: data freshness per source
stocksight_stockout_rate{store_id}                    — Gauge: current stockout rate per store
stocksight_overstock_rate{store_id}                   — Gauge: current overstock rate per store
```

### Grafana Dashboard Panels

1. **Forecast Health**: MAPE trend by horizon (1d/7d/30d) with SLA threshold lines
2. **Model Comparison**: Prophet vs. Lag-Llama vs. Ensemble MAPE bar chart
3. **Data Pipeline**: Ingestion lag per source (hours since last successful sync)
4. **Inventory Health**: Stockout rate + overstock rate by store/region
5. **Worker Performance**: Queue depth, processing rate, error rate per worker
6. **Model Drift**: Feature distribution shift (KS-test p-value) per SKU cluster
7. **Retraining Status**: Last retrain date, MAPE delta, model version

### Alerting Rules

| Condition | Severity | Action |
|---|---|---|
| MAPE > 30% for any horizon | Critical | PagerDuty, rollback to previous model |
| Data pipeline lag > 6h for any source | Warning | Slack #data-pipeline |
| Stockout rate > 5% for any store | Warning | Slack #inventory-alerts |
| Forecast worker queue > 10K pending | Warning | Scale out forecast workers |
| Feature computation > 2h | Warning | Investigate feature pipeline |
| Model confidence < 0.5 for >10% of SKUs | Critical | Retrain or fallback to baseline |

---

## Performance Targets

| Metric | Current | Target | Measurement |
|---|---|---|---|
| Stockout rate | 8% | <3% | Daily stockout events / total SKU-store-days |
| Overstock rate | 12% | <5% | Daily overstock events (Qty > 90-day cover) / total |
| Forecast MAPE (1-day) | — | <15% | |actual - forecast| / actual |
| Forecast MAPE (7-day) | — | <20% | |actual - forecast| / actual |
| Forecast MAPE (30-day) | — | <25% | |actual - forecast| / actual |
| Forecast MAPE (90-day) | — | <35% | |actual - forecast| / actual |
| SLA compliance | — | >95% of SKUs meeting MAPE target | Per-horizon SLA check |
| Inference latency | — | <20ms per SKU-store | P99 ONNX inference time |
| Data freshness | — | <4h lag per source | Time since last successful ingestion |
| Uptime | — | 99.9% | Prometheus alertmanager SLA |
| Cold-start inclusion | — | Within 30 days of first sale | Days from first sale to active forecasting |

---

## Implementation Phases

| Phase | Tasks | Duration | Dependencies |
|---|---|---|---|
| **P1: Scaffold** | FastAPI project, TimescaleDB, Celery + RabbitMQ, MinIO, Keycloak, CI/CD | 1 week | None |
| **P2: POS/ERP Pipeline** | POS transaction ingestion (Kafka), ERP inventory sync, data validation | 3 weeks | P1 |
| **P3: External Data Pipeline** | Weather API integration, competitor scraping, promotions calendar CRUD | 1 week | P1 |
| **P4: Feature Engineering** | Feature library (~40 features), daily cron pipeline, validation tests | 2 weeks | P2, P3 |
| **P5: Baseline Model** | Prophet per SKU-store, accuracy benchmark, evaluation framework | 2 weeks | P4 |
| **P6: Foundation Model** | Lag-Llama fine-tuning, ONNX export, ensemble logic, cold-start strategy | 2 weeks | P4 |
| **P7: Forecast Dashboard** | Next.js dashboard, forecast vs. actual charts, stockout/overstock alerts, SKU detail page | 3 weeks | P2, P3 |
| **P8: Simulator UI** | What-if scenario engine (promo change, weather, pricing), side-by-side comparison | 2 weeks | P6, P7 |
| **P9: Accuracy SLA** | SLA tracking, retraining cadence (weekly + anomaly), drift monitoring | 2 weeks | P6 |
| **P10: Admin + Alerts** | Model version management, feature importance, alert rule config, feature flags | 1 week | P7 |
| **P11: Production** | K3s cluster, Helm charts, ArgoCD GitOps, Grafana dashboards, runbook | 2 weeks | P10 |

**Total: 21 weeks (team of 4: 1 full-stack, 1 ML, 1 backend, 1 infra)**

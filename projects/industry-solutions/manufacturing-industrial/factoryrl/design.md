# FactoryRL — Design Document

## Overview

FactoryRL reduces factory energy consumption by 20%+ through Model Predictive Control (MPC) — a learned dynamics model (LightGBM) predicts how HVAC and production decisions affect energy and throughput, and a constrained optimizer (scipy SLSQP) finds optimal HVAC setpoints and production schedule adjustments every 15 minutes. No GPU, no neural networks. The entire system runs on CPU-only infrastructure and handles safety constraints (temperature bounds, production deadlines) explicitly rather than through learned penalties.

---

## Project Structure

```
factoryrl/
├── app/
│   ├── main.py                       # FastAPI application factory + CORS/middleware
│   ├── config.py                     # pydantic-settings: DB, BMS, ERP, MPC params
│   ├── dependencies.py               # DB session, auth, BMS/ERP client deps
│   ├── routers/
│   │   ├── energy.py                 # /api/energy/* — real-time + historical metrics
│   │   ├── hvac.py                   # /api/hvac/* — zones, setpoints, overrides
│   │   ├── production.py             # /api/production/* — schedules, throughput
│   │   ├── mpc.py                    # /api/mpc/* — latest action, prediction, cost
│   │   ├── simulation.py             # /api/simulate/* — what-if scenarios
│   │   └── savings.py                # /api/savings/* — baseline, verification reports
│   ├── models/
│   │   ├── zone.py                   # SQLAlchemy: Zone, ZoneMetric
│   │   ├── hvac.py                   # SQLAlchemy: HVACSetpoint, HVACCommand
│   │   ├── production.py             # SQLAlchemy: WorkOrder, Machine, Throughput
│   │   ├── mpc.py                    # SQLAlchemy: MPCAction, MPCPrediction, MPCCost
│   │   └── savings.py                # SQLAlchemy: Baseline, Verification, Adjustment
│   ├── schemas/
│   │   ├── energy.py                 # Pydantic: EnergyCurrent, EnergyTimeseries
│   │   ├── hvac.py                   # Pydantic: ZoneStatus, SetpointChange
│   │   ├── production.py             # Pydantic: WorkOrderResponse, MachineStatus
│   │   ├── mpc.py                    # Pydantic: MPCActionResponse, SimulationRequest
│   │   └── savings.py                # Pydantic: BaselineResponse, VerificationResponse
│   ├── services/
│   │   ├── bms_client.py             # Pluggable BMS adapter interface
│   │   ├── bms_adapters/
│   │   │   ├── simulator.py          # Built-in factory simulator (default)
│   │   │   ├── opc_ua.py             # OPC UA client (asyncua)
│   │   │   ├── bacnet.py             # BACnet/IP client (bacpypes3)
│   │   │   ├── modbus.py             # Modbus TCP client (pymodbus)
│   │   │   └── mqtt.py               # MQTT client (gmqtt)
│   │   ├── erp_client.py             # Generic REST MES/ERP adapter
│   │   ├── energy_monitor.py         # Real-time ingestion + anomaly detection
│   │   ├── mpc_controller.py         # Orchestrates the MPC loop
│   │   ├── dynamics_model.py         # LightGBM model wrapper (train + predict)
│   │   ├── optimizer.py              # scipy SLSQP constrained optimization
│   │   ├── simulator.py              # Factory digital twin (lumped thermal model)
│   │   └── savings_verifier.py       # IPMVP Option D verification
│   ├── templates/                    # Jinja2 (admin screens only)
│   │   ├── base.html
│   │   ├── admin.html
│   │   └── alerts.html
│   └── static/
├── mpc/
│   ├── train_dynamics.py             # Entry: feature engineering → LightGBM train → export
│   ├── features.py                   # Lag, rolling window, interaction features
│   ├── config/
│   │   ├── zones.yaml                # Per-zone temp limits, priority, HVAC mapping
│   │   ├── constraints.yaml          # Global constraints: power cap, ramp rates
│   │   └── weights.yaml              # Objective: α, β, γ coefficients
│   └── saved_models/                 # .lgbm files with metadata.json
├── workers/
│   ├── celery_app.py                 # Celery config + periodic schedule
│   ├── bms_worker.py                 # Poll BMS every 60s
│   ├── erp_worker.py                 # Poll ERP every 300s
│   ├── mpc_worker.py                 # Run MPC every 15 min
│   └── savings_worker.py             # Compute daily/weekly savings
├── frontend/                         # Next.js standalone
│   ├── src/
│   │   ├── components/
│   │   │   ├── EnergyChart.tsx
│   │   │   ├── ZoneCard.tsx
│   │   │   ├── ScheduleGantt.tsx
│   │   │   ├── MPCControlPanel.tsx
│   │   │   ├── SimulatorPanel.tsx
│   │   │   └── SavingsReport.tsx
│   │   ├── pages/
│   │   │   ├── index.tsx             # Dashboard
│   │   │   ├── hvac.tsx              # Zone control
│   │   │   ├── production.tsx        # Schedule
│   │   │   ├── simulation.tsx        # What-if
│   │   │   └── analytics.tsx         # Savings + trends
│   │   └── lib/
│   │       ├── api.ts
│   │       └── sse.ts                # Server-Sent Events client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI + Uvicorn (CPU, 4 workers)            │
│  /api/* REST · SSE · Keycloak · Rate Limit · OpenTelemetry        │
├──────────┬──────────────┬──────────────┬─────────────┬───────────┤
│          │              │              │             │           │
│  ┌───────▼──────┐  ┌────▼──────┐  ┌───▼──────┐  ┌──▼──────┐   │
│  │ BMS Gateway  │  │ ERP       │  │ MPC      │  │ Savings │   │
│  │ (Celery 60s) │  │ Adapter   │  │ (Celery  │  │ (Daily) │   │
│  │              │  │ (300s)    │  │  15 min) │  │         │   │
│  │ Simulator ◄──┤  │           │  │          │  │         │   │
│  │ OPC UA       │  │ YAML      │  │ LightGBM │  │ IPMVP D │   │
│  │ BACnet       │  │ field map │  │ + scipy  │  │         │   │
│  │ Modbus       │  │           │  │ SLSQP    │  │         │   │
│  └──────┬───────┘  └────┬──────┘  └─────┬────┘  └────┬────┘   │
│         │               │               │            │         │
└─────────┼───────────────┼───────────────┼────────────┼─────────┘
          │               │               │            │
   ┌──────▼───────┐  ┌────▼───────┐  ┌───▼────────┐  │
   │ TimescaleDB  │  │ PostgreSQL │  │ InfluxDB   │  │
   │ (energy +    │  │ (zones,    │  │ (real-time │  │
   │  production  │  │  baselines, │  │  metrics)  │  │
   │  + MPC logs) │  │  config)   │  │            │  │
   └──────────────┘  └────────────┘  └────────────┘  │
   ┌──────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                               │
│  Dashboard · Zone Control · Schedule Gantt · Simulator · Savings │
│  Recharts · SSE · Tailwind                                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## MPC Loop Design (Core Algorithm)

### Execution Flow (every 15 min)

```
┌──────────────────────────────────────────────────────────────────┐
│  mpc_worker.py — Celery beat task, runs every 900s               │
│                                                                  │
│  Step 1: READ_CURRENT_STATE                                      │
│    ← BMS Gateway: zone_temps, hvac_power, setpoints             │
│    ← ERP Adapter: machine_status, throughput, work_orders       │
│    ← Weather: outdoor_temp, humidity (cached external API)      │
│                                                                  │
│  Step 2: BUILD_FEATURE_VECTOR                                    │
│    Features: zone_temps[t-2,t-1,t] + hvac_power[t] +            │
│              production[t-2,t-1,t] + outdoor_temp[t] +           │
│              hour[t] + day[t] + interactions                     │
│                                                                  │
│  Step 3: PREDICT_TRAJECTORY                                      │
│    LightGBM.predict(next_16_steps | state, candidate_actions)    │
│    Horizon: 4 hours (16 × 15 min steps)                          │
│                                                                  │
│  Step 4: SOLVE_OPTIMIZATION                                      │
│    scipy.optimize.minimize(                                      │
│      objective = α × energy_cost + β × throughput_loss + γ ×     │
│                   comfort_violation,                             │
│      constraints = temp_bounds + power_limit + ramp_limits +     │
│                     production_deadlines,                        │
│      method = 'SLSQP'                                            │
│    )                                                             │
│    Decision variables: hvac_setpoints[16] × N_zones +            │
│                        production_delay[16] × N_machines         │
│                                                                  │
│  Step 5: APPLY_ACTION                                            │
│    → BMS: apply hvac_setpoints[0]                                │
│    → ERP: publish production_recommendation[0] (advisory)        │
│                                                                  │
│  Step 6: LOG_EVERYTHING                                          │
│    → TimescaleDB: state, action, predicted_state, cost,          │
│                   optimization_status (converged / infeasible)    │
│                                                                  │
│  Step 7: FEEDBACK_CHECK (delayed 10 min)                         │
│    Compare predicted vs. actual zone_temps[t+1]                  │
│    If MAPE > 15% for 3 consecutive cycles → trigger retrain      │
└──────────────────────────────────────────────────────────────────┘
```

### State Space

| Feature | Source | Type | Count |
|---|---|---|---|
| Zone temperature | BMS | float (°C) | N_zones |
| Zone humidity | BMS | float (%) | N_zones |
| HVAC power draw | BMS | float (kW) | 1 |
| HVAC setpoints (current) | BMS | float (°C) | N_zones |
| Machine status (running/idle/down) | ERP | int (0/1/2) | N_machines |
| Throughput (units/hr) | ERP | float | N_machines |
| Work orders pending (next 4h) | ERP | int | N_machines |
| Outdoor temperature | Weather API | float (°C) | 1 |
| Hour of day | RTC | int (0–23) | 1 |
| Day of week | RTC | int (0–6) | 1 |
| Lag features (t-1, t-2) | TimescaleDB | float | 3× per metric |
| Rolling window (mean, std, slope) | TimescaleDB | float | 4× per metric |

Total feature dimension: ~8×N_zones + 5×N_machines + 30 (approx 80–150 features for typical factory)

### Action Space

| Decision Variable | Range | Count | Type |
|---|---|---|---|
| HVAC supply temp setpoint | 10–30°C | 1 per zone | continuous |
| Zone damper position | 0–100% | 1 per zone | continuous |
| Production line speed recommendation | 80–110% of target | 1 per machine | continuous |
| Production start delay recommendation | 0–120 min | 1 per work order | integer (discrete) |

Total action dimension: 2×N_zones + 2×N_machines (approx 20–40 variables)

### Objective Function

```python
def objective(actions, state, horizon=16):
    total_energy = 0
    total_throughput_loss = 0
    total_comfort_violation = 0

    for step in range(horizon):
        next_state = dynamics_model.predict(state, actions[step])
        energy = next_state["hvac_power_kw"] * 0.25  # 15 min = 0.25h
        throughput_loss = max(0, target_throughput - next_state["throughput"])
        comfort_viol = sum(max(0, t - t_max) + max(0, t_min - t)
                          for t, t_min, t_max in zip(
                              next_state["zone_temps"],
                              zone_temp_mins,
                              zone_temp_maxs))
        total_energy += energy
        total_throughput_loss += throughput_loss
        total_comfort_violation += comfort_viol
        state = next_state  # roll forward

    return alpha * total_energy + beta * total_throughput_loss + gamma * total_comfort_violation
```

### Constraints

```yaml
# mpc/config/constraints.yaml
zones:
  assembly_a:
    temp_c: { min: 20.0, max: 26.0 }
    hvac_power_max_kw: 50
    priority: high
  warehouse_b:
    temp_c: { min: 15.0, max: 30.0 }
    hvac_power_max_kw: 20
    priority: low

global:
  total_power_max_kw: 500
  hvac_ramp_rate_max_kw_per_15min: 10
  production_min_throughput_pct: 80

weight_defaults:
  alpha: 0.7    # energy
  beta: 0.2     # throughput
  gamma: 0.1    # comfort
```

---

## Data Models

### TimescaleDB (Time-Series)

```sql
-- Energy metrics (1-min resolution from BMS)
CREATE TABLE energy_metrics (
    time        TIMESTAMPTZ NOT NULL,
    zone_id     VARCHAR(32) NOT NULL,
    power_kw    FLOAT NOT NULL,
    temp_c      FLOAT,
    humidity    FLOAT,
    hvac_state  VARCHAR(16)       -- 'heating' | 'cooling' | 'idle' | 'off'
);
SELECT create_hypertable('energy_metrics', 'time');

-- Production metrics (per work order, per machine)
CREATE TABLE production_metrics (
    time          TIMESTAMPTZ NOT NULL,
    work_order_id VARCHAR(32) NOT NULL,
    machine_id    VARCHAR(32) NOT NULL,
    units_produced INT NOT NULL,
    units_target  INT NOT NULL,
    line_speed_pct FLOAT,
    status        VARCHAR(16)     -- 'running' | 'idle' | 'down' | 'complete'
);
SELECT create_hypertable('production_metrics', 'time');

-- MPC actions (every 15 min)
CREATE TABLE mpc_actions (
    time            TIMESTAMPTZ NOT NULL,
    episode_id      UUID NOT NULL,
    horizon_steps   INT NOT NULL,         -- 16
    state_snapshot  JSONB NOT NULL,       -- full state vector
    action_applied  JSONB NOT NULL,       -- setpoints[0] + recommendations[0]
    action_plan     JSONB NOT NULL,       -- full 16-step plan
    cost            FLOAT NOT NULL,       -- objective value
    solver_status   VARCHAR(16) NOT NULL, -- 'converged' | 'infeasible' | 'max_iter'
    solve_time_ms   FLOAT NOT NULL,
    model_version   VARCHAR(32) NOT NULL  -- LightGBM version hash
);
SELECT create_hypertable('mpc_actions', 'time');

-- MPC predictions vs. actuals (delayed feedback)
CREATE TABLE mpc_feedback (
    time              TIMESTAMPTZ NOT NULL,
    episode_id        UUID NOT NULL,
    step              INT NOT NULL,
    zone_id           VARCHAR(32) NOT NULL,
    predicted_temp_c  FLOAT NOT NULL,
    actual_temp_c     FLOAT NOT NULL,
    predicted_power_kw FLOAT NOT NULL,
    actual_power_kw   FLOAT NOT NULL,
    error_mape        FLOAT NOT NULL       -- |predicted - actual| / actual
);
SELECT create_hypertable('mpc_feedback', 'time');
```

### PostgreSQL (Relational)

```sql
CREATE TABLE zones (
    id              VARCHAR(32) PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    area_sqft       INT NOT NULL,
    temp_min_c      FLOAT NOT NULL,
    temp_max_c      FLOAT NOT NULL,
    hvac_priority   INT DEFAULT 0,         -- 0=low, 1=med, 2=high
    hvac_equipment_id VARCHAR(64)          -- BMS equipment tag
);

CREATE TABLE machines (
    id              VARCHAR(32) PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    zone_id         VARCHAR(32) REFERENCES zones(id),
    max_throughput  FLOAT NOT NULL,
    power_draw_kw   FLOAT NOT NULL         -- when running
);

CREATE TABLE work_orders (
    id              VARCHAR(32) PRIMARY KEY,
    machine_id      VARCHAR(32) REFERENCES machines(id),
    product_sku     VARCHAR(32) NOT NULL,
    target_units    INT NOT NULL,
    deadline        TIMESTAMPTZ NOT NULL,
    priority        INT DEFAULT 0,         -- 0=low, 1=med, 2=high
    status          VARCHAR(16) DEFAULT 'pending',  -- pending | active | complete | late
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Savings verification
CREATE TABLE savings_baselines (
    id                UUID PRIMARY KEY,
    period_start      DATE NOT NULL,
    period_end        DATE NOT NULL,
    total_kwh         FLOAT NOT NULL,
    production_units  INT NOT NULL,
    energy_intensity  FLOAT NOT NULL,      -- kWh/unit
    method            VARCHAR(8) NOT NULL DEFAULT 'D', -- IPMVP Option
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE savings_verifications (
    id                    UUID PRIMARY KEY,
    baseline_id           UUID REFERENCES savings_baselines(id),
    period_start          DATE NOT NULL,
    period_end            DATE NOT NULL,
    actual_kwh            FLOAT NOT NULL,
    adjusted_baseline_kwh FLOAT NOT NULL,   -- weather + production adjusted
    gross_savings_kwh     FLOAT NOT NULL,
    net_savings_kwh       FLOAT NOT NULL,   -- gross - non-RL factors
    savings_pct           FLOAT NOT NULL,
    confidence            VARCHAR(8) NOT NULL,  -- 'high' | 'medium' | 'low'
    verified_at           TIMESTAMPTZ DEFAULT NOW()
);
```

---

## API Design

### REST Endpoints

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| `GET` | `/api/energy/current` | Real-time zone metrics | — | `[{zone_id, power_kw, temp_c, humidity, hvac_state, time}]` |
| `GET` | `/api/energy/timeseries` | Historical range | `?zone_id=&from=&to=&resolution=5m` | `[{time, power_kw, temp_c}]` |
| `GET` | `/api/hvac/zones` | All zones with status | — | `[{id, name, temp_c, setpoint, mode, priority}]` |
| `PUT` | `/api/hvac/zones/{id}/setpoint` | Manual setpoint override | `{setpoint_c, reason}` | `ZoneStatus` |
| `GET` | `/api/hvac/mpc-suggestion` | Latest MPC suggestion | — | `{timestamp, setpoints:[], predicted_savings_pct}` |
| `POST` | `/api/hvac/apply-mpc` | Apply current MPC plan | `{confirm: true}` | `{status: 'applied', action_count}` |
| `GET` | `/api/production/schedule` | Current schedule | — | `[{work_order_id, machine_id, target, deadline, status}]` |
| `POST` | `/api/production/schedule/optimize` | Request MPC-optimized schedule | — | `{recommendations: [{work_order_id, suggested_start, suggested_speed}]}` |
| `GET` | `/api/mpc/status` | MPC system status | — | `{running, last_run, model_version, solver_status, avg_cost}` |
| `POST` | `/api/simulate` | Run what-if scenario | `{duration_h, hvac_override, production_override, mpc_enabled}` | `{scenario_id, predicted_energy, predicted_throughput}` |
| `GET` | `/api/savings/baselines` | List baselines | — | `[{period_start, period_end, intensity, method}]` |
| `GET` | `/api/savings/verifications` | List verification reports | — | `[{period, savings_pct, confidence}]` |
| `POST` | `/api/savings/verify` | Trigger verification run | `{period_start, period_end}` | `VerificationResponse` |

### Server-Sent Events (SSE)

| Event | Payload | Frequency |
|---|---|---|
| `energy.update` | `{zone_id, power_kw, temp_c, timestamp}` | Every 60s |
| `mpc.action_taken` | `{episode_id, cost_summary, solver_status}` | Every 15 min |
| `mpc.feedback` | `{zone_id, predicted_temp, actual_temp, mape}` | Every 25 min (10 min delay) |
| `production.update` | `{machine_id, status, throughput}` | Every 300s |
| `alert.anomaly` | `{type, severity, zone_id, metric, value, threshold}` | On trigger |

---

## LightGBM Dynamics Model

### Training Pipeline

```
1. Feature Engineering (mpc/features.py)
   - 30 days historical data → ~2,880 rows (at 15-min resolution)
   - Features:
     * Current: zone_temps, hvac_power, throughput, outdoor_temp
     * Lag: t-1, t-2 for each metric above
     * Rolling: 1h mean, 4h mean, 1h std for zone_temps
     * Interactions: temp × production_status, outdoor_temp × hour
     * Cyclical: sin(hour), cos(hour), sin(day), cos(day)
   - Target: zone_temps[t+1], hvac_power[t+1], throughput[t+1]

2. Training (mpc/train_dynamics.py)
   - Split: 80% train, 20% validation (temporal split — no future leakage)
   - Model: LightGBM
     * objective: regression (l2)
     * num_leaves: 32
     * max_depth: 8
     * learning_rate: 0.05
     * feature_fraction: 0.8
     * early_stopping_rounds: 50
   - Multi-output: 1 model per target type (temp/power/throughput)
   - Train time: ~10 minutes on CPU

3. Validation
   - MAPE on validation set
   - Residual plot: predicted vs. actual over 24h
   - Feature importance analysis → prune to top 20 features
   - Save: .lgbm file + metadata.json (features, MAPE, train_date)

4. Retraining
   - Schedule: weekly (Celery cron, Sunday 02:00)
   - Trigger: if feedback_error_mape_24h > 15% for 3 consecutive days
   - Warm-start: continue training from previous model if available
```

### Prediction Signature

```
Input:  numpy array [batch, n_features]
Output: {
    "zone_temps":        numpy array [batch, n_zones],       # °C
    "hvac_power_kw":     numpy array [batch, 1],             # kW
    "throughput":        numpy array [batch, n_machines],    # units/hr
}
Latency: ~2ms per batch of 16 (one horizon) on CPU
```

---

## BMS Gateway: Pluggable Adapter

### Interface

```python
# app/services/bms_adapters/__init__.py
class BMSAdapter(ABC):
    @abstractmethod
    async def connect(self) -> bool
    @abstractmethod
    async def read_zone_temps(self) -> dict[str, float]
    @abstractmethod
    async def read_hvac_power(self) -> float
    @abstractmethod
    async def read_setpoints(self) -> dict[str, float]
    @abstractmethod
    async def write_setpoint(self, zone_id: str, temp_c: float) -> bool
    @abstractmethod
    async def read_outdoor_temp(self) -> float
    @abstractmethod
    async def disconnect(self)
```

### Adapter Selection (config.yaml)

```yaml
# config/bms.yaml
adapter:
  type: simulator        # simulator | opc_ua | bacnet | modbus | mqtt
  connection:
    host: "${BMS_HOST}"
    port: 4840           # OPC UA default; 502 for Modbus; 47808 for BACnet
    timeout_sec: 5
  polling:
    interval_sec: 60
    zones: [assembly_a, assembly_b, warehouse_b, paint_shop]
```

### Built-in Simulator

```yaml
# config/bms_simulator.yaml
simulator:
  enabled: true           # used when adapter.type = 'simulator'
  zones:
    assembly_a:
      base_temp: 23.0
      heat_load_kw: 15    # heat generated by production
      thermal_mass: 500   # kJ/°C — higher = slower response
      hvac_capacity_kw: 40
    warehouse_b:
      base_temp: 18.0
      heat_load_kw: 2
      thermal_mass: 2000
      hvac_capacity_kw: 20
  outdoor_temp:
    daily_min: 10          # °C
    daily_max: 32
    noise_std: 2
```

The simulator uses a lumped thermal mass model:

```
dT/dt = (hvac_power - heat_load - (T - T_outdoor) × UA) / thermal_mass
```

This is a 1-line ODE per zone — runs 100,000× faster than EnergyPlus, making it suitable for MPC horizon simulation and what-if scenarios.

---

## ERP/MES Adapter: Generic REST

### Configuration

```yaml
# config/erp.yaml
adapter:
  enabled: true
  base_url: "${ERP_BASE_URL}"   # if empty → use simulator
  auth:
    type: api_key               # api_key | oauth2 | basic | none
    api_key: "${ERP_API_KEY}"
  polling:
    interval_sec: 300
  endpoints:
    machines: /api/v1/machines
    work_orders: /api/v1/work-orders/active
    throughput: /api/v1/production/throughput
  field_mapping:
    work_order_id: id
    machine_id: equipment_code
    units_produced: output_quantity
    units_target: target_quantity
    status: status_code
    deadline: due_date
  status_mapping:
    "1": running
    "2": idle
    "3": down
    "4": complete
```

### Simulator Mode (when base_url is empty)

```yaml
erp_simulator:
  machines:
    assembly_a: { max_throughput: 100, downtime_prob: 0.05, shift_pattern: day }
    assembly_b: { max_throughput: 80, downtime_prob: 0.03, shift_pattern: night }
    paint_shop: { max_throughput: 60, downtime_prob: 0.08, shift_pattern: day }
  schedule:
    - machine: assembly_a
      sku: WIDGET-A
      target: 800
      deadline_hours: 8
    - machine: assembly_b
      sku: WIDGET-B
      target: 640
      deadline_hours: 8
    - machine: paint_shop
      sku: WIDGET-A
      target: 480
      deadline_hours: 12
```

---

## Frontend Screens (Next.js + Recharts + SSE)

| Screen | Route | Key Components | Real-time |
|---|---|---|---|
| **Dashboard** | `/` | Energy intensity gauge (Chart.js gauge), zone temp grid, production throughput sparkline, MPC status card, savings trend | SSE: energy.update, mpc.action_taken |
| **HVAC Control** | `/hvac` | Zone cards (temp, humidity, setpoint, power), MPC suggestion badge, manual override button, zone priority indicator | SSE: energy.update |
| **Production** | `/production` | Gantt chart of work orders, MPC-optimized overlay (compare original vs. suggested), line speed adjustments, deadline warnings | SSE: production.update |
| **Simulator** | `/simulation` | Parameter sliders (outdoor temp, production load, MPC on/off), "Run" button, side-by-side energy/production comparison chart, export PDF | — (request/response) |
| **Analytics** | `/analytics` | Energy intensity trend (daily/weekly/monthly), savings verification table, weather-normalized comparison, baseline management, CSV/PDF export | SSE: mpc.feedback |
| **Admin** | `/admin` | LightGBM model version table, feature importance bar chart, prediction error trend (MAPE over time), constraint config editor, alert rules | SSE: alert.anomaly |

---

## Design Decisions & Trade-offs

### 1. MPC + LightGBM over Deep RL (PPO)

| Dimension | MPC + LightGBM | PPO (Stable-Baselines3) | Decision |
|---|---|---|---|
| Training time | 10 min (CPU) | 24h (CPU) | MPC |
| Inference time | ~200ms per horizon | <5ms per action | PPO wins on speed |
| Safety constraints | Explicit (hard bounds in optimizer) | Learned via reward penalties | MPC (critical for factory) |
| Explainability | High (feature importance + constraint violations) | Low (policy network black box) | MPC |
| Adaptability | Medium (bounded by training data) | High (can generalize) | PPO wins on novelty |
| Optimization | Solves every 15 min | Policy is a single feedforward pass | PPO wins on simplicity |
| Retraining | Incremental (LightGBM warm-start) | Full retrain | MPC |
| Skill requirement | Medium (gradient boosting + optimization) | High (RL hyperparameter tuning) | MPC |

**Decision rationale**: For a factory environment where:
- Temperature bounds are safety-critical (cannot be violated)
- Production deadlines are contractual (cannot be missed)
- Explainability is required for plant engineer buy-in
- Training compute is CPU-only

MPC's explicit constraint handling and transparent dynamics model outweigh PPO's inference speed advantage. The 15-min control interval (200ms solve time) is well within the required latency.

### 2. LightGBM over Neural Network Dynamics

| Dimension | LightGBM | MLP / LSTM | Decision |
|---|---|---|---|
| Training time | 10 min (CPU) | 2h+ (CPU for MLP, LSTM even slower) | LightGBM |
| Data efficiency | Good (works with 2K–3K rows) | Poor (needs 10K+ for generalization) | LightGBM |
| Feature importance | Built-in (gain, split count) | Requires SHAP/LIME | LightGBM |
| Uncertainty estimates | Not native (can add quantile regression) | Not native (can add MC dropout) | Similar |
| Multi-step prediction | Iterative (predict → feed back) | Direct (seq2seq with LSTM) | LSTM wins for horizon |
| Overfitting risk | Low (regularized trees) | High (needs regularization tuning) | LightGBM |

**Decision rationale**: LightGBM's fast training, built-in feature importance, and low data requirement make it the practical choice for factory time-series where historical data may be limited. The iterative multi-step prediction (predict one step, feed back as input for the next) is less accurate than a dedicated LSTM for long horizons, but the 16-step horizon (4 hours) is short enough that error accumulation is within acceptable bounds (±2°C at step 16 in validation).

### 3. scipy SLSQP over Specialized Solvers

| Dimension | SLSQP (scipy) | IPOPT | OR-Tools (CP-SAT) | Decision |
|---|---|---|---|---|
| Type | Gradient-based, local | Interior point, local | Constraint programming | — |
| NLP support | Yes | Yes | No (MIP only) | SLSQP |
| Mixed-integer | No | No | Yes (CP-SAT) | — |
| Speed | ~200ms | ~1s | ~5s | SLSQP |
| CPU-only | Yes | Yes | Yes | SLSQP |
| Installation | pip install scipy | Conda/C++ build | pip install ortools | SLSQP |
| Globally optimal | No | No | Yes (for MIP) | — |

**Decision rationale**: SLSQP is chosen for speed and simplicity. The energy optimization landscape is approximately convex (quadratic-like energy cost + linear temperature dynamics) — local optima found by SLSQP are within 5% of global optimum in our validation. If production start delays require integer decisions, OR-Tools is added as a fallback solver for those variables only.

### 4. TimescaleDB + InfluxDB over Single DB

| Dimension | TimescaleDB only | InfluxDB only | Both |
|---|---|---|---|
| SQL support | Full PostgreSQL | Flux (SQL-like, limited) | — |
| Dashboard query speed | ~50ms (range scan) | ~5ms (pre-aggregated) | — |
| Operational complexity | 1 service | 1 service | 2 services |
| Retention policies | Native (hypertable chunking) | Native (bucket + RP) | — |
| JOINs with relational data | Native (PostgreSQL) | Not possible | — |

**Decision rationale**: TimescaleDB is the primary store for all time-series data. InfluxDB is added as a real-time cache because Recharts dashboards querying at sub-second intervals overload TimescaleDB's chunk scan. InfluxDB stores 24h of raw metrics (pre-aggregated by 1-min buckets), and the frontend reads from InfluxDB for live views, TimescaleDB for historical analytics.

### 5. SSE over WebSocket

| Dimension | SSE | WebSocket | Decision |
|---|---|---|---|
| Direction | Server → Client only | Bidirectional | SSE sufficient |
| Reconnection | Auto (EventSource API) | Manual | SSE |
| Firewall | HTTP (port 443) | TCP upgrade | SSE |
| Throughput | 1 server → N clients | Full duplex | — |
| Custom events | Named events | Message types | Similar |

**Decision rationale**: The dashboard only needs server-pushed updates (energy metrics, MPC actions, alerts). No client-to-server streaming is required. SSE is simpler to implement, auto-reconnects, and works through HTTP proxies without special configuration.

---

## Alternatives Considered (Summary)

| Alternative | Status | Why Rejected |
|---|---|---|
| **Ray RLlib PPO (GPU)** | Considered | GPU required. 24h CPU training was acceptable but user chose MPC for explicit constraints. |
| **Stable-Baselines3 PPO (CPU)** | Considered | 24h CPU training, safety via reward penalties is fragile. MPC chosen instead. |
| **EnergyPlus simulator** | Considered | 1000× slower than lumped thermal model. Impractical for 16-step horizon optimization during training. |
| **Modelica** | Considered | Requires FMI standard and Modelica compiler. Ops burden outweighs fidelity gain. |
| **Bayesian optimization (skopt)** | Considered | Faster than MPC for static optimization but cannot handle sequential 4h receding horizon. |
| **PID-only control** | Considered | Cannot couple HVAC with production schedule. No cross-domain optimization. |
| **ONNX runtime** | Considered | Needed for PPO inference. Not needed once MPC chosen (LightGBM has native predict). |
| **MQTT for BMS** | Considered | Many modern factories use MQTT. Available as an adapter plugin. |
| **Apache Kafka for metrics** | Considered | Overkill for a single factory. Celery + TimescaleDB is sufficient. |
| **Grafana for dashboards** | Considered | Grafana is excellent for charts but cannot deliver the interactive simulation UI, MPC control panel, or zone override forms needed here. Next.js + Recharts chosen for custom UI. |
| **DuckDB for analytics** | Considered | Fast for OLAP but cannot ingest real-time streaming data. TimescaleDB handles both ingestion and query. |

---

## Limitations

### 1. Dynamics Model Accuracy Decay

LightGBM is a function approximator — it interpolates well within training distribution but extrapolates poorly. If the factory installs new equipment, changes production processes, or undergoes seasonal weather extremes outside the training range, prediction error increases.

**Mitigation**: Weekly retraining + anomaly-triggered retrain (MAPE > 15% for 3 days). LightGBM warm-starting allows incremental updates without full retraining.

### 2. Local Optima in MPC Solver

SLSQP is a local optimizer. If the energy landscape has sharp discontinuities (e.g., time-of-use electricity pricing tiers with step changes at hour boundaries), SLSQP may converge to a suboptimal local minimum.

**Mitigation**: Multi-start initialization (3 random starting points, pick best cost). If persistent suboptimality detected, fall back to differential evolution (global) every 4 hours.

### 3. No Supervisory Override Logic

The MPC makes recommendations every 15 minutes. If a human operator overrides a setpoint, the MPC does not currently learn from the override (no inverse RL or preference learning). The operator's expertise is lost.

**Mitigation**: Override events are logged but not learned from. Future enhancement: add override analysis dashboard to detect patterns in operator decisions.

### 4. Production Schedule Changes Are Advisory

The MPC cannot directly control the production scheduler (ERP systems are read-only in most factories). It publishes recommendations, but the plant manager may ignore them.

**Mitigation**: The savings verification methodology (IPMVP D) separates HVAC savings (direct control) from production schedule savings (advisory). Only HVAC savings are guaranteed. Schedule optimization is reported as "additional potential."

### 5. Lumped Thermal Model Simplification

The simulator assumes each zone is a single thermal mass with uniform temperature. Real factories have spatial temperature gradients, open bay doors, solar gain through windows, and convection from moving equipment.

**Mitigation**: The simulator is used for training feedback in the MPC loop. The actual BMS sensors provide real temperature readings, so the control loop works with ground truth every 15 minutes regardless of simulator accuracy. The simulator is only needed for what-if scenarios and baseline adjustment.

### 6. No Multi-Factory Scaling

The MPC is designed for a single factory. Each factory requires its own LightGBM model, constraint config, and BMS adapter. There is no federated learning or cross-factory knowledge transfer.

**Mitigation**: Shared configuration templates and zone taxonomy conventions allow consistent setup across factories, but each deployment is independently trained.

### 7. Cold Start — No Historical Data

If the factory has no existing data historian, the dynamics model has nothing to train on.

**Mitigation**: Phase 1 runs without MPC (data collection only, 30 days). During this period, the BMS poller and ERP poller build the training dataset. The system runs in "observation mode" — all metrics collected, no actions applied.

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| API server | FastAPI + Uvicorn | 0.115+ | Async REST + SSE |
| Task queue | Celery + Redis | 5.4+ | Periodic MPC, BMS polling, savings |
| Dynamics model | LightGBM | 4.5+ | Gradient-boosted trees for state prediction |
| Optimizer | scipy (SLSQP) | 1.14+ | Constrained optimization at each MPC step |
| Fallback optimizer | OR-Tools (CP-SAT) | 9.10+ | Integer constraints for production scheduling |
| Time-series DB | TimescaleDB | 2.15+ | Energy, production, MPC logs |
| Real-time cache | InfluxDB OSS | 2.7+ | Sub-second dashboard queries |
| Relational DB | PostgreSQL | 16+ | Zones, machines, config, baselines |
| BMS adapter | Pluggable (simulator default) | — | OPC UA, BACnet, Modbus, MQTT plugins |
| ERP adapter | Generic REST (YAML config) | — | Field mapping for any MES/ERP |
| Frontend | Next.js + Recharts | 14+ | Dashboard, simulation, analytics |
| Real-time UI | Server-Sent Events | — | Dashboard live updates |
| Styling | Tailwind CSS | 3+ | UI components |
| Auth | Keycloak | 24+ | OAuth 2.0 + RBAC |
| Feature flags | Unleash | 5+ | Gradual MPC feature rollout |
| Monitoring | Prometheus + Grafana + OpenTelemetry | LATEST | Metrics, tracing, dashboards |
| CI/CD | GitHub Actions + ArgoCD + Helm | LATEST | GitOps deployment |
| Infrastructure | Docker Compose (dev) / K3s (prod) | LATEST | Container orchestration |

---

## Implementation Phases

| Phase | Tasks | Duration | Dependencies |
|---|---|---|---|
| **P1: Scaffold** | FastAPI project, TimescaleDB + PostgreSQL + InfluxDB Docker, Celery + Redis, Keycloak, Docker Compose, CI/CD | 1 week | — |
| **P2: BMS Gateway** | Pluggable adapter interface, simulator adapter (lumped thermal), OPC UA + BACnet + Modbus plugins, Celery 60s poller, TimescaleDB ingestion | 3 weeks | P1 |
| **P3: ERP Adapter** | Generic REST client (YAML config, field mapping, auth), simulator mode, Celery 300s poller | 1 week | P1 |
| **P4: Simulator** | Lumped thermal model (per zone), production model, outdoor temp model, validate against historical data, feature engineering library | 2 weeks | P2, P3 |
| **P5: Dynamics Model** | LightGBM training pipeline, feature engineering (lag, rolling, interaction), validation split, MAPE evaluation, weekly retrain cron | 2 weeks | P4 |
| **P6: MPC Controller** | scipy SLSQP optimizer, constraint config (YAML), objective function, 16-step horizon, action application, feedback logging, anomaly-triggered retrain | 2 weeks | P5 |
| **P7: Frontend Dashboard** | Next.js app, Recharts energy charts, SSE client, zone cards, schedule Gantt, MPC status panel | 3 weeks | P2, P3 |
| **P8: Simulator UI** | What-if scenario builder, parameter sliders, side-by-side comparison, PDF report export | 2 weeks | P6, P7 |
| **P9: Savings Verification** | Baseline computation, IPMVP Option D adjusted baseline, verification report generation, confidence scoring | 2 weeks | P6 |
| **P10: Admin + Alerts** | LightGBM model monitoring, prediction error dashboard, feature importance, constraint editor, alert rules, Unleash feature flags | 1 week | P8 |
| **P11: Production** | K3s deployment, Helm charts, ArgoCD, Prometheus rules, Grafana dashboards, load testing, security audit, runbook | 2 weeks | P10 |

**Total: 21 weeks (team of 4: 1 full-stack, 1 ML, 1 backend, 1 infra)**

---

## Performance Targets

| Metric | Current | Target | Measurement |
|---|---|---|---|
| Energy intensity | 120% of benchmark | <100% of benchmark | kWh/unit, weekly moving average |
| HVAC energy reduction | — | 20%+ vs. baseline | BMS power meter summation |
| Production throughput | Baseline | ≥95% of baseline | Units/shift, compared to pre-MPC |
| Comfort violation hours | — | <2% of operating hours | Zone temp outside ±2°C of setpoint |
| MPC solver latency | — | <500ms p99 | scipy optimizer wall time |
| Dynamics model MAPE | — | <15% at 4h horizon | Predicted vs. actual zone temps |
| Savings confidence | — | >90% IPMVP Option D | Statistical significance at p<0.05 |
| Anomaly detection precision | — | >80% | True alerts / total alerts |
| Uptime | N/A | 99.5% | Prometheus alertmanager SLA |

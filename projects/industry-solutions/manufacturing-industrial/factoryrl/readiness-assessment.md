# AI Readiness Assessment — FactoryRL

**Entry**: #27 — Factory Energy Consumption 20% Above Benchmark (Manufacturing & Industrial)
**Date**: 2026-06-30
**Assessed by**: AI Problem Analysis Framework (§7)

---

## 1. Organizational Profile

| Attribute | Assumption |
|---|---|
| Organization type | Mid-size manufacturing plant (500K sq ft), $200M+ annual revenue, 3 production lines, 12 HVAC zones |
| Current energy approach | HVAC and production scheduling managed independently — no cross-domain optimization. Energy intensity 20% above industry benchmark |
| Data environment | BMS (Building Management System) with zone temps, power draw, HVAC status via OPC UA/BACnet. ERP/MES system with machine status, work orders, throughput. 30+ days of historical data available |
| Technical team | Plant engineering (BMS, PLC, controls), IT team (ERP, network), no ML engineers on staff. 1 data analyst for reporting |
| Business driver | $500K/month energy bill × 20% excess = $1.2M/year avoidable cost. Production deadlines are contractual — any solution must not risk throughput |

---

## 2. The Business Problem

Every month, this factory burns an extra $100,000 on energy that should never have been used. The HVAC system runs independently from the production floor — the plant manager sets temperature targets and forgets them, while the production scheduler pushes work orders through without considering how much heat those machines will generate. On a hot afternoon with three lines running full tilt, the HVAC fights the production heat while the air conditioning screams at full power. On a mild night shift with one line running, the same HVAC settings waste energy cooling empty space. No one is actively managing this trade-off because no one can — the variables change faster than any human can track, and the two systems (HVAC and production) speak different languages on different timelines. The result: a factory that is always either too hot, too costly, or both.

FactoryRL connects those two worlds with a brain that understands both. It learns how the factory behaves: how much heat each production line throws off, how fast each zone responds to cooling, how outdoor temperature shifts the load. Every 15 minutes, it looks at what is happening right now — which machines are running, what the weather is doing, how hot each zone is — and calculates the single best set of HVAC setpoints and production adjustments for the next four hours. It never violates safety limits (temperature bounds are hard constraints, not suggestions) and it never sacrifices production deadlines for energy savings. The operator sees a clear recommendation, applies it with one click, and watches energy drop 20%+ while throughput stays flat. The savings show up in next month's utility bill, not in a slide deck.

---

## 3. Dimension-by-Dimension Assessment

### 3.1 Data Maturity — Assessment: L3 (Managed)

**Evidence**:
- BMS provides zone temperatures, humidity, HVAC power draw, and setpoint status via OPC UA/BACnet at 1-minute granularity
- ERP/MES system exposes machine status, throughput, work orders, and production schedules via REST API
- 30+ days of continuous historical data available for model training
- Weather data accessible via NOAA/open API for outdoor temperature and humidity
- Data is operational (no PII) — no privacy constraints on usage
- Data quality is monitored for BMS (sensor health checks) but not for ML consumption

**Capability**: All required data sources exist and are accessible in real time. The 30-day historical buffer is sufficient for LightGBM training. No new sensors or data collection infrastructure is needed.

**Gap**: BMS and ERP data have never been joined for cross-domain analysis. Timestamp alignment between the two systems has drift (BMS at 1-min resolution, ERP at event-based). Historical ERP data may have gaps during system upgrades. Feature engineering pipeline must handle schema changes in both systems gracefully.

### 3.2 ML Infrastructure — Assessment: L1 (Ad-hoc / None)

**Evidence**:
- No model registry, experiment tracking, or ML serving infrastructure
- No CI/CD pipeline for model deployment
- No monitoring for prediction drift or model accuracy degradation
- Existing compute is CPU-only — no GPU available
- Docker and basic containerization are used for plant floor applications
- IT team manages on-prem servers and a small cloud footprint (AWS)
- TimescaleDB or PostgreSQL is available for time-series storage

**Capability**: CPU-only compute is sufficient — LightGBM trains in ~10 minutes and inference takes ~2ms. The team does not need to build GPU infrastructure. Docker deployment and basic cloud resources are available.

**Gap**: Zero ML lifecycle tooling exists. MLflow must be deployed, model training must be containerized, and a retraining pipeline must be built from scratch. The infrastructure is simple (CPU, TimescaleDB, Celery) but the pipeline to support it does not exist yet.

### 3.3 Team Capability — Assessment: Low (No ML Experience)

**Evidence**:
- Plant engineering team understands BMS, sensors, and control systems deeply
- IT team can manage servers, databases, and Docker deployments
- One data analyst with SQL and basic Python experience
- No ML engineers, data scientists, or MLOps experience on staff
- Team has never deployed a machine learning model in production
- No experience with gradient boosting, time-series forecasting, or constrained optimization
- Strong domain expertise in factory operations, HVAC, and production scheduling

**Capability**: The team can integrate with BMS and ERP (strong domain expertise) and can maintain deployed infrastructure. They can serve as subject matter experts for feature engineering, constraint definition, and validation.

**Gap**: ML development — from model training through deployment and monitoring — requires external expertise. The LightGBM dynamics model and scipy optimizer are simple relative to deep learning, but still outside the current team's skill set. A 2-person ML team (1 ML engineer + 1 backend engineer) should be brought in for the 21-week build, with knowledge transfer to plant IT for ongoing maintenance.

### 3.4 Compliance & Governance — Assessment: Moderate (Low Barriers)

**Evidence**:
- Factory energy optimization is not a regulated AI domain — no external compliance requirements
- No PII or sensitive data involved (only temperatures, power draws, machine statuses)
- Safety constraints are handled explicitly in the optimizer (hard bounds on temps, power, ramp rates) — not learned by the model
- All MPC actions are logged with full state snapshots for audit
- Production decisions are advisory only (plant manager must approve schedule changes)
- Existing safety systems (over-temp alarms, emergency stops) operate independently of FactoryRL
- No explainability requirement from external regulators — but plant manager trust requires interpretable recommendations

**Capability**: No regulatory blockers. Safety is handled by independent systems plus explicit optimizer constraints. The advisory nature of production recommendations limits operational risk.

**Gap**: Internal governance for model accuracy needs to be established. The team must define what constitutes a model "failure" (MAPE > 15% at 4h horizon for 3 consecutive cycles), how rollback works, and who is responsible when the MPC recommends a setpoint that leads to comfort complaints. A model card and runbook should be created before go-live.

---

## 4. Readiness Scoring

| Dimension | Score | Rationale |
|---|---|---|
| Data maturity | **2** (Strong) | L3 — BMS and ERP data exist, are accessible in real time, and have sufficient history for training |
| ML infrastructure | **0** (Weak) | None — no ML platform, no model registry, no CI/CD for ML. Must be built from scratch |
| Team capability | **1** (Moderate) | Strong domain expertise but zero ML experience. External ML team needed for build phase |
| Compliance readiness | **2** (Strong) | No regulatory blockers. Safety handled externally + explicit optimizer constraints |
| **Total** | **5 / 8** | |

**Scoring benchmark**:
| Range | Recommended Approach |
|---|---|
| 6–8 | Build custom AI solution in-house |
| 3–5 | Use managed AI services (APIs, pre-built models) or hybrid |
| 0–2 | Buy a packaged solution or improve readiness first |

**Verdict**: **5/8 — Hybrid: Build with external ML expertise.** The data and compliance dimensions are strong. The infrastructure and team gaps are real but bounded — LightGBM + scipy is a simple stack compared to deep learning. A targeted 2-person ML team brought in for the 21-week build, with knowledge transfer to plant IT, is the realistic path. A pure in-house build is not viable; buying a packaged solution (Siemens, Schneider Electric energy optimization) is an alternative but would cost more over 5 years and yield less customization.

---

## 5. Findings

### Strength: Data Is Ready and Accessible

The BMS and ERP data sources are production-grade with live APIs. No sensor installation, data collection wait, or vendor data purchase is needed. The 30+ day historical buffer is sufficient for LightGBM training. This puts FactoryRL ahead of most industrial AI projects, where weeks are spent just getting sensor data out of siloed systems.

### Weakness: Zero ML Infrastructure and Team

Unlike StockSight (which has an existing ML platform and ML engineers), FactoryRL starts from zero on the ML side. No MLflow, no experiment tracking, no model serving, no monitoring. The team has never deployed a model. This means the first 4–5 weeks of the 21-week plan are pure infrastructure — setting up what StockSight already has on day one.

### Opportunity: Simple Tech Stack Reduces Risk

LightGBM + scipy SLSQP is one of the simplest viable ML stacks in this catalog. No GPU, no neural networks, no LLM. The total ML surface area is small: one gradient-boosted tree model, one numerical optimizer, a retraining cron job. This keeps the infrastructure build manageable and makes knowledge transfer to plant IT realistic.

### Risk: Plant Manager Trust Is the Adoption Gate

An energy optimization system that recommends setpoints the plant manager does not trust will be ignored, regardless of accuracy. The what-if simulator (Phase 8) is the critical trust-building tool — letting the plant manager run their own scenarios and see the MPC's recommendations before handing over control. The advisory-first approach (recommendations for 4 weeks before auto-apply) is essential.

---

## 6. Conclusion

| Decision | Rationale |
|---|---|
| **Hybrid: Build with external ML expertise** | Readiness score of 5/8. Data and compliance are ready; infrastructure and team need investment. The simple tech stack (LightGBM + scipy, CPU-only) limits the build scope to 21 weeks with a 2-person ML team. Buying a packaged solution is an option but sacrifices customization and long-term cost. |

**Recommended approach**:

| Phase | Activity | Duration |
|---|---|---|
| **Phase 0: Team** | Hire/contract 2-person ML team (1 ML engineer, 1 backend). Deploy MLflow, set up dev environment. Knowledge transfer plan with plant IT. | Weeks 1–3 |
| **Phase 1: Infrastructure** | TimescaleDB, Celery, Docker Compose, CI/CD. BMS and ERP adapter scaffolding. | Weeks 4–5 |
| **Phase 2: Data pipeline** | BMS + ERP ingestion, timestamp alignment, feature engineering library, 30-day historical join. | Weeks 6–8 |
| **Phase 3: Model** | LightGBM dynamics model training, validation, multi-step prediction, model export. | Weeks 9–10 |
| **Phase 4: MPC** | SLSQP solver, constraint config, objective function, 15-min execution loop, feedback logging. | Weeks 11–12 |
| **Phase 5: Dashboard + Simulator** | Next.js frontend, what-if simulator, MPC status panel, savings verification reports. | Weeks 13–16 |
| **Phase 6: Validation** | 4-week shadow mode (MPC recommends, operator reviews, no auto-apply). Trust building. | Weeks 17–20 |
| **Phase 7: Go-live** | Enable auto-apply for HVAC zones. Production schedule remains advisory. Monitoring + runbook. | Week 21 |

The 4-week shadow mode in Phase 6 is the critical risk mitigation. Before the MPC ever touches a setpoint, the plant manager has seen 2,688 recommendations (4 weeks × 24 hours × 7 days × 4 recommendations/hour) and can verify that none of them would have caused comfort or production issues. By the time auto-apply is enabled, the system has earned its trust.

---

## 7. Action Items

| # | Action | Owner | Timeline |
|---|---|---|---|
| 1 | Hire/contract 2-person ML team (familiar with LightGBM + scipy) | Plant Manager + HR | Weeks 1–3 |
| 2 | Deploy MLflow + Docker dev environment for ML team | IT Lead + ML Engineer | Week 3 |
| 3 | Confirm BMS API access (OPC UA/BACnet endpoints, read/write permissions) | Plant Engineering Lead | Week 3 |
| 4 | Confirm ERP/MES API access (machine status, work orders, throughput endpoints) | IT Lead | Week 3 |
| 5 | Extract 30-day historical BMS + ERP data, validate timestamp alignment, identify gaps | Data Analyst + ML Engineer | Weeks 3–5 |
| 6 | Define zone temperature bounds, power limits, and ramp rate constraints with plant engineers | ML Engineer + Plant Engineering | Week 4 |
| 7 | Set up energy intensity baseline (kWh/unit, trailing 30-day average) before any MPC intervention | Data Analyst | Week 4 |
| 8 | Build what-if simulator UI for plant manager trust-building before auto-apply | Full-stack Engineer | Weeks 13–15 |
| 9 | Define model failure criteria (MAPE > 15% for 3 cycles), rollback procedure, and alerting | ML Engineer + Plant Manager | Week 16 |
| 10 | Create model card + runbook for long-term maintenance by plant IT | ML Engineer + IT Lead | Week 20 |

---

*Assessed using the [AI Problem Analysis Framework](../../../../docs/ai-problem-analysis-framework.md) — Organizational Readiness section (§7).*

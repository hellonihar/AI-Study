# AI Readiness Assessment — SolarWind Forecast

**Entry**: #46 — Renewable Energy Forecast (Energy & Utilities)
**Date**: 2026-06-28
**Assessed by**: AI Problem Analysis Framework (§7)

---

## 1. Organizational Profile

| Attribute | Assumption |
|---|---|
| Organization type | Utility / Independent Power Producer (IPP) with 500MW+ renewable portfolio |
| Current forecast method | Physics-based power curve model + human trader overlay |
| Data environment | SCADA historian, 5-min resolution sensor data, 3+ years historical |
| Technical team | OT engineers (SCADA, PLC), IT team (ERP, databases), no dedicated ML engineers |
| Business driver | 15% curtailment loss at ~$30/MWh — $780K+ annual opportunity |

---

## 2. Dimension-by-Dimension Assessment

### 2.1 Data Maturity — Assessment: L3 (Curated)

**Evidence**:
- SCADA system captures actual power output, wind speed, irradiance, temperature at 5-min intervals across all sites
- 3+ years of historical data available, clean and timestamped
- ISO market data (day-ahead and real-time prices, curtailment signals) archived
- No formal data versioning or feature store — data lives in SCADA historian with SQL access
- Weather forecast data (NOAA/ECMWF) pulled via API but not systematically cached for model retraining

**Capability**: Can support supervised ML (regression) today. Feature engineering and backtesting require manual SQL work, not automated pipelines.

**Gap**: No labeled "curtailment event" dataset — would need to derive labels from SCADA + ISO signal data.

### 2.2 ML Infrastructure — Assessment: L1 (Ad-hoc / None)

**Evidence**:
- No model registry, no experiment tracking
- Models (if any) are Excel spreadsheets or hardcoded Python scripts on individual engineer machines
- No CI/CD for model deployment
- No prediction drift monitoring
- Serving would be a new capability — currently runs on physics models embedded in SCADA

**Gap**: This is the weakest dimension. Infrastructure must be built from the ground up. Cannot go to production without at minimum: model registry, containerized serving, and basic monitoring.

### 2.3 Team Capability — Assessment: Moderate (Can Integrate APIs)

**Evidence**:
- OT engineers understand the physical system deeply (turbine power curves, wake effects, soiling losses)
- IT team can manage databases, APIs, and container deployment
- No ML engineers on staff; no experience training or validating regression models
- Energy traders understand forecast accuracy requirements but cannot specify model architecture

**Capability**: Can define features and label data with domain expertise. Cannot train, validate, or deploy models independently.

**Gap**: Need either an ML hire or a managed service partnership for model development.

### 2.4 Compliance & Governance — Assessment: Low (No Governance)

**Evidence**:
- Energy forecasting is not a regulated ML domain (unlike credit scoring or healthcare)
- No explainability requirement from ISO markets — forecast error is financial, not regulatory
- Data is operational (sensor readings, prices) — no PII involved, no privacy constraints
- Existing SOX controls on trading activities apply, but forecast accuracy is not in scope

**Capability**: Low barrier for initial deployment. No regulatory blockers.

**Risk**: No governance today means no drift monitoring or model validation process. As the model scales to influence trading decisions, governance must catch up.

---

## 3. Readiness Scoring

| Dimension | Score | Rationale |
|---|---|---|
| Data maturity | **2** (Strong) | L3 — clean SCADA data with 3+ year history |
| ML infrastructure | **0** (Weak) | None — no registry, serving, or monitoring |
| Team capability | **1** (Moderate) | Can integrate APIs but cannot train models independently |
| Compliance readiness | **1** (Moderate) | No blockers but no governance either |
| **Total** | **4 / 8** | |

**Scoring benchmark**:
| Range | Recommended Approach |
|---|---|
| 6–8 | Build custom AI solution in-house |
| 3–5 | Use managed AI services (APIs, pre-built models) or hybrid |
| 0–2 | Buy a packaged solution or improve readiness first |

**Verdict**: **4/8 — Hybrid approach recommended.** Use managed ML services for model development while building internal infrastructure.

---

## 4. Findings

### Strength: Data Is Production-Ready for Training
The SCADA historian is a rare advantage — most organizations at this readiness level lack labeled historical data. Three years of 5-min resolution power output + weather data means the supervised learning problem is well-defined from day one. Feature engineering (rolling averages, ramp rates, time-of-day encoding) can begin immediately without data collection delay.

### Weakness: No ML Infrastructure Exists
The utility has SCADA, historians, and OT networking — but nothing in the ML stack. There is no model registry, no serving infrastructure, no monitoring. Every component of the ML flywheel must be built. This is the binding constraint on timeline. The model development itself is straightforward (LightGBM with physics-constrained loss); the infrastructure around it is where the complexity lies.

### Opportunity: Domain Experts Can Label and Validate
OT engineers already know when physical models underperform — they manually override forecasts during ramp events, low-light conditions, or turbine degradation periods. This tacit knowledge can be captured as anomaly labels and validation cases. The ML model does not replace their judgment; it systematizes it.

### Risk: Infrastructure Phase Will Feel Unproductive
The first 8–12 weeks will produce no model improvements — just data pipelines, feature stores, and serving infrastructure. Energy companies accustomed to SCADA projects with visible OT outcomes (sensor installed → data flowing) will find this invisible progress frustrating. Budget and stakeholder patience must be secured before starting.

---

## 5. Conclusion

| Decision | Rationale |
|---|---|
| **Proceed with hybrid approach** | Data is ready. Business case is strong (15% curtailment → $780K/year). ML infrastructure is the only blocker, and it is a solvable engineering problem. |
| **Phase 1 (Weeks 1–6): Infrastructure** | Set up data pipeline (SCADA → feature store), model registry (MLflow), containerized serving (FastAPI + Docker). No model training yet. |
| **Phase 2 (Weeks 7–10): Baseline model** | Train LightGBM on historical data. Compare against physics-only baseline. Establish accuracy SLA (±10% by forecast horizon). |
| **Phase 3 (Weeks 11–16): Production deployment** | Deploy model alongside physics model. Use ensemble (physics + ML) with confidence-based fallback. Add drift monitoring. |
| **Phase 4 (Month 6+): Optimization loop** | Integrate forecast into trading desk workflow. Add retraining cadence (quarterly + event-driven). |

The organization is **not ready for full custom AI today**, but is well-positioned to begin with managed services and build toward self-sufficiency within 6 months. The critical success factor is infrastructure investment in Phase 1 — skipping it will cause silent model degradation within 3 months of deployment.

---

## 6. Action Items

| # | Action | Owner | Timeline |
|---|---|---|---|
| 1 | Hire or contract ML engineer (or partner with managed ML service) | Engineering Director | Month 1 |
| 2 | Build SCADA-to-feature-store pipeline (5-min resolution, all sites) | Data Engineer | Weeks 1–4 |
| 3 | Extract and label 2 years of historical data (features + actual power output) | OT Engineer + Data Engineer | Weeks 3–5 |
| 4 | Deploy MLflow server and establish experiment tracking workflow | ML Engineer | Weeks 2–4 |
| 5 | Develop physics-only baseline accuracy measurement (current performance) | OT Engineer | Weeks 1–2 |
| 6 | Implement model registry governance — versioning, approval, rollback | ML Engineer | Weeks 4–6 |
| 7 | Define accuracy SLA per forecast horizon (1h, 4h, 24h) with trading desk | Product Owner + Trading Desk | Month 1 |
| 8 | Plan fallback strategy for out-of-distribution forecasts (extreme weather) | ML Engineer + OT Engineer | Month 2 |

---

*Assessed using the [AI Problem Analysis Framework](../../../../docs/ai-problem-analysis-framework.md) — Organizational Readiness section (§7).*

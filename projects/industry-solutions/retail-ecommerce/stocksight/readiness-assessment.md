# AI Readiness Assessment — StockSight

**Entry**: #19 — Inventory Forecasting Errors (Retail & E-Commerce)
**Date**: 2026-06-29
**Assessed by**: AI Problem Analysis Framework (§7)

---

## 1. Organizational Profile

| Attribute | Assumption |
|---|---|
| Organization type | National omnichannel retailer with 500+ stores, $2B+ annual revenue, 50K+ active SKUs |
| Current forecasting method | Excel-based rolling average + category manager judgment — 8% stockout, 12% overstock |
| Data environment | Cloud data warehouse (Snowflake) with POS, inventory, and customer data; Kafka event stream for transactions |
| Technical team | 20+ data engineers, 5 ML engineers, 10 data scientists with deep learning experience; existing ML platform team |
| Business driver | 8% stockout = $40M/year lost revenue; 12% overstock = $25M/year carrying cost + markdown losses |

---

## 2. The Business Problem

StockSight's customer — a national omnichannel retailer with 500+ stores and 50,000 active products — is bleeding money from two sides of the same coin. On one side, they run out of popular items 8% of the time, handing $40 million a year in sales to competitors. On the other, they over-order 12% of their inventory, sinking $25 million annually into carrying costs, storage fees, and fire-sale markdowns. The root cause isn't a lack of effort. Category managers work the numbers in Excel, apply rolling averages, and lean on hard-won intuition. But with 50,000 products, seasonal swings, promotions, weather shifts, and supplier hiccups, the math simply outruns a spreadsheet. The result is a slow-moving, fragmented guess — and $65 million in avoidable losses every year.

StockSight replaces that guess with an AI forecasting engine purpose-built for the complexity of modern retail. Instead of one person wrestling rows in Excel, it ingests every signal that drives demand — point-of-sale transactions, inventory levels, promotions, weather, and competitor pricing — and learns how they interact. The system forecasts demand for every SKU in every store, from tomorrow to next month, and updates those forecasts as new data arrives. Inventory planners get a dashboard with clear, trustworthy numbers instead of hunches. The goal is to cut stockouts from 8% to 2-3% and overstock from 12% to 4-5%, recovering the vast majority of that $65 million — not by guessing harder, but by letting the machine do what machines do best: see patterns in noise at a scale no human can match.

---

## 3. Dimension-by-Dimension Assessment

### 2.1 Data Maturity — Assessment: L4 (Optimized)

**Evidence**:
- 5+ years of clean, timestamped POS transaction data at SKU-store-day granularity across all 500+ stores
- ERP inventory snapshots available every 4 hours via REST API — on_hand, in_transit, reserved quantities
- Kafka event stream for real-time POS transactions with <1min latency
- Promotions calendar maintained in a dedicated system with historical lift data
- Weather data already ingested from NOAA for store operations planning — 3+ year cache
- Competitor pricing data purchased from syndicated data provider (Nielsen/IRI)
- Data quality monitoring already in place for financial reporting — automated validation checks
- No formal feature store exists, but data lake tables are well-documented with dbt transformations

**Capability**: All required data sources are available, clean, and accessible via API or stream. Feature engineering is the only missing piece — the raw data is production-ready for ML training.

**Gap**: No feature store or versioned training datasets. Feature engineering will need to be built, but the data infrastructure to support it is solid. Historical promotions data lacks standardized lift measurement — some manual cleanup needed.

### 2.2 ML Infrastructure — Assessment: L3 (Managed)

**Evidence**:
- MLflow deployed for experiment tracking and model registry — used by 3 existing ML products
- GPU cluster available (4× A100 nodes) for model training via internal Kubeflow platform
- Docker + Kubernetes (EKS) in production for microservices — 20+ services running
- CI/CD pipeline for ML models: GitHub Actions → model training → evaluation → staging → production
- Feature store (Feast) in pilot for two existing ML use cases
- A/B testing framework (internal) supports model comparison with statistical significance
- Prometheus + Grafana stack used across the organization for monitoring
- Existing model monitoring with drift detection for 2 production ML models

**Capability**: No infrastructure needs to be built from scratch. The existing ML platform can host StockSight with minimal additions — primarily scaling Feast to include time-series features.

**Gap**: Feast feature store is currently used for tabular data only — time-series window features (rolling stats, lags) require new feature definitions and backfill. Model monitoring for forecast accuracy (MAPE by horizon) is a new metric type not yet supported by the existing drift detection framework.

### 2.3 Team Capability — Assessment: High (Can Build and Deploy)

**Evidence**:
- 5 ML engineers with experience in PyTorch, TensorFlow, and ONNX deployment — 2 have time-series background
- 10 data scientists who run A/B tests and build regression models — can support feature engineering and evaluation
- 20+ data engineers who manage Kafka, Snowflake, dbt, and Airflow — can build ingestion pipelines
- Existing MLOps team maintains the Kubeflow/MLflow platform
- Strong domain expertise: 3 supply chain analysts who understand inventory planning, safety stock formulas, and seasonal demand patterns
- Team has deployed 2 production ML models: a recommendation system and a dynamic pricing engine

**Capability**: The team has all the skills needed to build, deploy, and maintain StockSight. The ML engineers have relevant time-series experience. The data engineering team can build the feature pipeline. The supply chain analysts can validate outputs and define business rules.

**Gap**: No one on the team has fine-tuned a time-series foundation model (Lag-Llama/PatchTFT) specifically. The ML engineers have worked with Transformers for NLP and tabular data but not time-series LLMs. A 2-week spike or external consultation may be needed before committing to the architecture.

### 2.4 Compliance & Governance — Assessment: Moderate (Low Barriers)

**Evidence**:
- Retail inventory forecasting is not a regulated AI domain — no FDA, HIPAA, or SOX equivalent for forecast accuracy
- Data is operational (sales quantities, prices, inventory levels) — no PII at the aggregate level used for forecasting
- Existing data governance covers financial reporting accuracy (SOX-controlled inventory valuations)
- No explainability requirement from external regulators — forecast error is financial, not regulatory
- Inventory planner decisions based on AI forecasts are reviewed by humans — no fully automated purchasing planned
- Existing model governance requires documentation, validation, and monitoring for all production ML models

**Capability**: No regulatory blockers to deployment. The main governance requirement is internal: model documentation, accuracy monitoring, and drift detection — all standard practices the team already follows.

**Gap**: Forecast accuracy SLA monitoring is a new governance capability. The team needs to define what constitutes a model "incident" (e.g., MAPE > 30% for 3 consecutive days) and how rollback decisions are made. No external compliance risk, but internal governance processes need to be established.

---

## 3. Readiness Scoring

| Dimension | Score | Rationale |
|---|---|---|
| Data maturity | **2** (Strong) | L4 — all data sources available, clean, and streaming; no data collection needed |
| ML infrastructure | **2** (Strong) | L3 — GPU cluster, MLflow, Kubeflow, CI/CD all exist; only minor additions needed |
| Team capability | **2** (Strong) | ML engineers with time-series experience, MLOps team, domain experts in place |
| Compliance readiness | **1** (Moderate) | No regulatory blockers, but internal governance for forecast SLA needs setup |
| **Total** | **7 / 8** | |

**Scoring benchmark**:
| Range | Recommended Approach |
|---|---|
| 6–8 | Build custom AI solution in-house |
| 3–5 | Use managed AI services (APIs, pre-built models) or hybrid |
| 0–2 | Buy a packaged solution or improve readiness first |

**Verdict**: **7/8 — Build custom AI solution in-house.** All prerequisites are met. The data exists, the infrastructure is ready, the team has the skills, and there are no regulatory blockers. The only gaps — feature store extensions and time-series foundation model experience — are standard engineering risks that can be addressed within the first phases of the project.

---

## 4. Findings

### Strength: Data and Infrastructure Are Production-Ready Before Day One

Unlike most organizations where data collection or infrastructure build-out consumes the first 8–12 weeks, StockSight starts with both prerequisites in place. Five years of clean POS data in Snowflake, Kafka streams for real-time transactions, a GPU cluster for model training, and an existing ML platform (MLflow, Kubeflow, CI/CD) mean the team can begin feature engineering and model development immediately. The 7/8 readiness score reflects this rare advantage — most AI projects at this catalog's companies score 2–4.

### Weakness: Time-Series Foundation Models Are New to the Team

The ML engineers have deployed Transformers for NLP and gradient-boosted models for tabular data, but no one has fine-tuned Lag-Llama or PatchTFT. This is a skill gap, not an infrastructure gap — it can be closed with a 2-week spike, external training, or a consultant engagement. The risk is overcommitting to a specific model architecture before the team understands its failure modes (e.g., poor performance on intermittent demand patterns, cold-start behavior for new SKUs). A parallel Prophet baseline (Phase 5) mitigates this by ensuring a fallback exists.

### Opportunity: Existing Feature Store Can Be Extended for Time-Series

The organization already has Feast in pilot for two ML use cases. Extending it to support time-series features — rolling windows, lags, cyclical encodings — creates a reusable asset for future forecasting use cases (demand sensing, promo planning, workforce scheduling). The investment in feature engineering for StockSight pays dividends beyond inventory forecasting.

### Risk: Model Accuracy Expectations Must Be Managed

The business currently sees 8% stockout and 12% overstock as unacceptable. The natural expectation is that AI will eliminate them entirely. In reality, a well-tuned foundation model will reduce stockouts to 2-3% and overstock to 4-5% — a 60% improvement, not 100% elimination. The remaining error comes from fundamental unpredictability: viral social media posts, competitor flash sales, weather anomalies, and supply disruptions. Setting SLA thresholds at realistic levels (15% MAPE at 1-day, 25% at 30-day) and educating stakeholders on irreducible uncertainty is critical to adoption.

---

## 5. Conclusion

| Decision | Rationale |
|---|---|
| **Build custom AI solution in-house** | Readiness score of 7/8 means all prerequisites are met. Data, infrastructure, team, and compliance environment support a build approach. The business case ($65M/year opportunity) justifies the investment. |

**Recommended approach**:

| Phase | Activity | Duration |
|---|---|---|
| **Phase 0: Spike** | 2-week time-series foundation model exploration. Fine-tune Lag-Llama on 100 SKUs. Compare with Prophet baseline. Decide on primary architecture. | Weeks 1–2 |
| **Phase 1: Infrastructure** | Extend Feast feature store for time-series features. Set up data pipelines (POS, ERP, weather, competitor). Deploy forecast database schema. | Weeks 3–6 |
| **Phase 2: Baseline + Model** | Build Prophet baseline, fine-tune foundation model, implement ensemble. Run A/B test against current Excel-based forecasts. | Weeks 7–12 |
| **Phase 3: Dashboard + Workflow** | Build inventory planner dashboard. Integrate with procurement workflow. Train planners on interpretation. | Weeks 13–18 |
| **Phase 4: SLA + Optimization** | Set up accuracy monitoring, retraining cadence, drift detection. Optimize ensemble weights per SKU cluster. | Weeks 19–22 |
| **Phase 5: Scale** | Expand to all 50K+ SKUs and 500+ stores. Integrate with purchasing system for semi-automated ordering. | Months 6–8 |

The 2-week spike in Phase 0 is the key recommendation. Before committing to a 22-week build, the team should validate that Lag-Llama (or PatchTFT) delivers meaningful improvement over Prophet on their specific demand patterns. If the gap is small (<5% MAPE improvement), the project can save significant complexity by using Prophet + feature engineering alone, avoiding the foundation model stack entirely.

---

## 6. Action Items

| # | Action | Owner | Timeline |
|---|---|---|---|
| 1 | Run 2-week time-series foundation model spike (Lag-Llama vs. Prophet on 100 SKUs) | ML Lead | Weeks 1–2 |
| 2 | Extend Feast feature store for time-series features (rolling windows, lags, cyclical encodings) | Data Engineer Lead | Weeks 3–5 |
| 3 | Build POS + ERP data ingestion pipeline with validation (Kafka consumer + Snowflake → TimescaleDB) | Data Engineer | Weeks 3–5 |
| 4 | Integrate weather and competitor pricing data feeds into feature pipeline | Data Engineer | Weeks 3–5 |
| 5 | Define forecast accuracy SLA thresholds with supply chain stakeholders | Product Owner + Supply Chain Director | Week 3 |
| 6 | Set up MLflow experiment for foundation model fine-tuning with hyperparameter sweeps | ML Engineer | Week 3 |
| 7 | Build Prophet baseline across all active SKU-store pairs as accuracy benchmark | ML Engineer | Weeks 4–6 |
| 8 | Plan inventory planner dashboard UX with 3–5 power users (wireframes + feedback) | Product Owner + Full-stack | Weeks 6–8 |
| 9 | Establish model governance documentation template (model card, SLA, rollback criteria) | ML Ops Lead | Weeks 6–8 |
| 10 | Define cold-start strategy for new SKUs and new stores before Foundation model deployment | ML Lead + Supply Chain Analyst | Month 2 |

---

*Assessed using the [AI Problem Analysis Framework](../../../../docs/ai-problem-analysis-framework.md) — Organizational Readiness section (§7).*

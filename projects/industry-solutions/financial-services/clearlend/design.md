# ClearLend — Design Document

## Overview

ClearLend reduces small business loan underwriting from 5 days to same-day through an automated underwriting agent — a document extraction pipeline reads uploaded financials, a LightGBM risk model scores creditworthiness with SHAP explainability, and an ECOA-compliant decision memo generator produces underwriter-ready credit memos with plain-English adverse action reasons. All external dependencies (LOS, credit bureau, document extraction) are simulated via pluggable adapters, making the system fully self-contained for management demo while preserving the architecture for real system integration.

---

## Project Structure

```
clearlend/
├── app/
│   ├── main.py                       # FastAPI application factory + CORS/middleware
│   ├── config.py                     # pydantic-settings: DB, LOS, bureau, model params
│   ├── dependencies.py               # DB session, auth, adapter deps
│   ├── routers/
│   │   ├── applications.py           # /api/applications/* — submit, status, list
│   │   ├── underwriting.py           # /api/underwriting/* — run decision, get memo
│   │   ├── documents.py              # /api/documents/* — upload, status, extraction
│   │   ├── decisions.py              # /api/decisions/* — approve, decline, counter
│   │   ├── regulations.py            # /api/regulations/* — state rules, compliance
│   │   └── portfolio.py              # /api/portfolio/* — loan performance, trends
│   ├── models/
│   │   ├── application.py            # SQLAlchemy: Application, Borrower
│   │   ├── document.py               # SQLAlchemy: Document, ExtractedField
│   │   ├── decision.py               # SQLAlchemy: Decision, AdverseActionReason
│   │   ├── risk_model.py             # SQLAlchemy: ModelVersion, Prediction, Explanation
│   │   ├── regulation.py             # SQLAlchemy: StateRule, ComplianceCheck
│   │   └── portfolio.py              # SQLAlchemy: Loan, PerformanceMetric
│   ├── schemas/
│   │   ├── application.py            # Pydantic: ApplicationSubmit, ApplicationResponse
│   │   ├── document.py              # Pydantic: DocumentUpload, ExtractionResult
│   │   ├── decision.py              # Pydantic: DecisionRequest, DecisionResponse, Memo
│   │   ├── risk.py                  # Pydantic: RiskScore, FactorExplanation
│   │   └── regulation.py            # Pydantic: StateRequirement, ComplianceResult
│   ├── services/
│   │   ├── los_client.py             # Pluggable LOS adapter interface
│   │   ├── los_adapters/
│   │   │   ├── simulator.py          # Built-in LOS simulator (default for demo)
│   │   │   └── rest.py               # REST client for real LOS integration
│   │   ├── bureau_client.py          # Pluggable credit bureau adapter interface
│   │   ├── bureau_adapters/
│   │   │   ├── simulator.py          # Built-in credit bureau simulator (default)
│   │   │   └── rest.py               # REST client for Experian/D&B
│   │   ├── doc_extractor.py          # Document extraction pipeline
│   │   ├── doc_adapters/
│   │   │   ├── simulator.py          # Built-in document parser (rule-based, demo)
│   │   │   ├── azure.py              # Azure Document Intelligence adapter
│   │   │   └── google.py             # Google Doc AI adapter
│   │   ├── risk_model.py             # LightGBM model wrapper (train + predict + explain)
│   │   ├── decision_engine.py        # Orchestrates the underwriting decision
│   │   ├── memo_generator.py         # Generates ECOA-compliant decision memo
│   │   ├── state_rules_engine.py     # 50-state regulation constraint checker
│   │   └── demo_seeder.py            # Seeds demo data (sample applications, borrowers)
│   └── templates/                    # Jinja2 (admin screens only)
│       ├── base.html
│       ├── admin.html
│       └── reports.html
├── model/
│   ├── train.py                      # Entry: feature engineering → LightGBM train → export
│   ├── features.py                   # Financial ratio features, trend features
│   ├── explain.py                    # SHAP explainability + plain-English mapping
│   ├── config/
│   │   ├── features.yaml             # Feature definitions, derived metrics
│   │   ├── model_params.yaml         # LightGBM hyperparameters
│   │   └── reasons.yaml              # SHAP → plain-English reason templates
│   └── saved_models/                 # .lgbm files with metadata.json
├── data/
│   ├── synthetic/
│   │   ├── generate_applications.py  # Generate synthetic 7-year loan portfolio
│   │   ├── generate_documents.py     # Generate sample tax returns, P&L, bank stmts
│   │   └── schema.yaml              # Field definitions for synthetic data
│   └── seed/
│       ├── applications.csv          # 50 demo applications for quick demo
│       └── regulations/
│           ├── interest_rate_caps.csv # 50-state interest rate limits
│           ├── disclosure_rules.csv   # State-specific disclosure requirements
│           └── licensing.csv          # State lender licensing rules
├── frontend/                         # Next.js standalone
│   ├── src/
│   │   ├── components/
│   │   │   ├── ApplicationForm.tsx    # Borrower application submission
│   │   │   ├── DocumentUpload.tsx     # Multi-file upload with progress
│   │   │   ├── ExtractionReview.tsx   # Show extracted financials with edit
│   │   │   ├── DecisionCard.tsx       # AI recommendation + risk score
│   │   │   ├── ExplanationPanel.tsx   # Top-5 factors with plain-English reasons
│   │   │   ├── UnderwriterMemo.tsx    # Full credit memo editor
│   │   │   ├── StateComplianceBadge.tsx # State regulation check result
│   │   │   ├── PortfolioChart.tsx     # Loan performance trends
│   │   │   └── DemoSeeder.tsx         # One-click seed demo data button
│   │   ├── pages/
│   │   │   ├── index.tsx             # Dashboard — pipeline summary
│   │   │   ├── applications.tsx      # Application queue
│   │   │   ├── application/[id].tsx  # Single application detail + decision
│   │   │   ├── portfolio.tsx         # Portfolio performance
│   │   │   ├── regulations.tsx       # State regulation explorer
│   │   │   └── admin.tsx             # Model management, feature config
│   │   └── lib/
│   │       ├── api.ts
│   │       └── sse.ts                # Server-Sent Events for live updates
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml                 # PostgreSQL + FastAPI + Next.js + Redis
├── Dockerfile
└── README.md
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FastAPI + Uvicorn (CPU, 4 workers)                       │
│  /api/* REST · SSE · Keycloak · Rate Limit · OpenTelemetry                    │
├──────────┬──────────────┬──────────────┬──────────────┬────────────────────┤
│          │              │              │              │                    │
│  ┌───────▼──────┐  ┌───▼────────┐ ┌──▼──────────┐ ┌─▼────────────┐       │
│  │ Document     │  │ LOS        │ │ Credit      │ │ Regulations  │       │
│  │ Pipeline     │  │ Gateway    │ │ Bureau      │ │ Engine       │       │
│  │              │  │            │ │ Gateway     │ │              │       │
│  │ Simulator ───┤  │ Simulator ─┤ │ Simulator ──┤ │ CSV-based    │       │
│  │ Azure Doc AI │  │ REST (nCino│ │ REST (Exp.  │ │ rules engine │       │
│  │ Google Doc AI│  │ /Blend)   │ │ /D&B)       │ │              │       │
│  └──────┬───────┘  └─────┬──────┘ └──────┬───────┘ └──────┬───────┘       │
│         │                │               │                │               │
└─────────┼────────────────┼───────────────┼────────────────┼───────────────┘
          │                │               │                │
   ┌──────▼───────┐  ┌────▼───────┐  ┌────▼───────┐  ┌────▼───────┐
   │  PostgreSQL  │  │  MinIO     │  │  Redis     │  │  Feature   │
   │  (primary)   │  │ (docs +    │  │ (cache +   │  │  Store     │
   │              │  │  models)   │  │  queue)    │  │  (Feast)   │
   └──────────────┘  └────────────┘  └────────────┘  └────────────┘
   ┌──────────────────────────────────────────────────────────────────┐
   │                    Next.js Frontend                                │
   │  Dashboard · Application Queue · Decision Review · Portfolio      │
   │  Recharts · SSE · Tailwind · Dark Mode                            │
   └──────────────────────────────────────────────────────────────────┘
```

---

## Core Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Full Underwriting Flow (one application)                                │
│                                                                         │
│  Step 1: SUBMIT                                                         │
│    → Borrower fills application form (frontend)                         │
│    → POST /api/applications → stored in PostgreSQL                      │
│    → Status: SUBMITTED                                                   │
│                                                                         │
│  Step 2: UPLOAD_DOCUMENTS                                               │
│    → Borrower uploads PDFs: tax returns, P&L, bank statements           │
│    → POST /api/documents/upload → stored in MinIO                       │
│    → Status: DOCUMENTS_UPLOADED                                          │
│                                                                         │
│  Step 3: EXTRACT                                                        │
│    → doc_extractor reads PDF → structured fields                        │
│    → Demo mode: Simulator parses text patterns                          │
│    → Production: Azure Doc Intelligence / Google Doc AI                 │
│    → Status: FINANCIALS_EXTRACTED                                        │
│                                                                         │
│  Step 4: PULL_CREDIT_BUREAU                                             │
│    → bureau_client pulls business + owner credit data                   │
│    → Demo mode: Simulator generates realistic mock data                 │
│    → Production: Experian / D&B REST API                                 │
│    → Status: BUREAU_PULLED                                               │
│                                                                         │
│  Step 5: PULL_LOS_DATA                                                  │
│    → los_client pulls existing relationship data                        │
│    → Demo mode: Simulator returns mock history                          │
│    → Production: nCino / Blend / custom LOS API                         │
│    → Status: LOS_DATA_LOADED                                             │
│                                                                         │
│  Step 6: FEATURE_ENGINEERING                                            │
│    → Combine extracted financials + bureau + LOS into feature vector    │
│    → Compute derived metrics: DSCR, cash flow vol, industry ratios     │
│    → Feast feature store for reusable feature definitions               │
│    → Status: FEATURES_COMPUTED                                           │
│                                                                         │
│  Step 7: RISK_SCORE                                                     │
│    → LightGBM model predicts default probability                        │
│    → SHAP explains top-5 contributing factors                           │
│    → SHAP values → plain-English ECOA-compliant reasons                 │
│    → Status: RISK_SCORED                                                 │
│                                                                         │
│  Step 8: STATE_COMPLIANCE_CHECK                                         │
│    → state_rules_engine checks borrower state × loan amount × rate      │
│    → Validates: interest rate cap, disclosure requirements, licensing   │
│    → Flags any compliance constraints for the decision                  │
│    → Status: COMPLIANCE_CHECKED                                          │
│                                                                         │
│  Step 9: DECISION_MEMO                                                  │
│    → memo_generator assembles: risk score + factors + compliance + rec  │
│    → Generates ECOA-compliant adverse action notice if declining        │
│    → Generates underwriter-ready credit memo if approving               │
│    → Status: MEMO_GENERATED                                              │
│                                                                         │
│  Step 10: UNDERWRITER_REVIEW                                           │
│    → Underwriter opens dashboard, reviews memo                          │
│    → Can adjust: rate, amount, terms, or override decision              │
│    → Approves → loan booked in LOS                                      │
│    → Declines → adverse action notice auto-generated                    │
│    → Status: DECIDED                                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### State Machine

```
SUBMITTED ──► DOCUMENTS_UPLOADED ──► FINANCIALS_EXTRACTED ──► BUREAU_PULLED
                                                                    │
                                                                    ▼
                                                          LOS_DATA_LOADED
                                                                    │
                                                                    ▼
                                                          FEATURES_COMPUTED
                                                                    │
                                                                    ▼
                                                             RISK_SCORED
                                                                    │
                                                                    ▼
                                                          COMPLIANCE_CHECKED
                                                                    │
                                                                    ▼
                                                             MEMO_GENERATED
                                                                    │
                                                                    ▼
                         ┌──────────────────┬────────────────────────┘
                         ▼                  ▼
                    APPROVED           DECLINED / COUNTER
                         │                  │
                         ▼                  ▼
                    LOS_BOOKED       ADVERSE_ACTION_SENT
```

---

## Simulated External Dependencies (Demo Mode)

### LOS Simulator

```yaml
# config/los_simulator.yaml
simulator:
  enabled: true         # false → switch to REST adapter
  existing_customers:
    - tax_id: "XX-XXXXXXX"
      relationship_years: 8
      previous_loans:
        - type: term
          amount: 250000
          status: paid_on_time
        - type: line_of_credit
          amount: 100000
          status: active_current
      deposit_balance: 450000
      average_monthly_balance_6m: 380000
  default_behavior:
    known_customer_prob: 0.4      # probability applicant is existing customer
    negative_history_prob: 0.1     # probability of past delinquencies
    response_latency_ms: 50        # simulated API latency
```

### Credit Bureau Simulator

```yaml
# config/bureau_simulator.yaml
simulator:
  enabled: true
  score_ranges:
    business_credit:
      mean: 65
      std: 18
      min: 0
      max: 100
    owner_personal:
      mean: 700
      std: 60
      min: 300
      max: 850
  negative_signals:
    bankruptcy_prob: 0.03
    tax_lien_prob: 0.05
    judgment_prob: 0.04
    payment_delinquency_prob: 0.12
  response_latency_ms: 200
```

### Document Extraction Simulator

```yaml
# config/doc_simulator.yaml
simulator:
  enabled: true
  extraction_strategy: pattern     # pattern | llm | template
  # Pattern-based: extracts numbers from text using regex patterns
  # Template-based: matches document type → known field positions
  supported_doc_types:
    - tax_return_1120
    - tax_return_1120s
    - profit_loss
    - balance_sheet
    - bank_statement
  field_accuracy_pct: 92           # simulated extraction accuracy
  error_types:
    - field: revenue
      error_rate: 0.05
      error_magnitude: 0.1         # ±10% random error
    - field: net_income
      error_rate: 0.08
      error_magnitude: 0.15
    - field: cost_of_goods
      error_rate: 0.06
      error_magnitude: 0.12
  response_latency_ms: 1500        # simulates document processing time
```

### Simulator Interface

```python
# app/services/los_client.py
class LOSAdapter(ABC):
    @abstractmethod
    async def get_application(self, app_id: str) -> ApplicationData
    @abstractmethod
    async def get_customer_history(self, tax_id: str) -> CustomerHistory
    @abstractmethod
    async def book_loan(self, decision: LoanDecision) -> LoanBookingResult
    @abstractmethod
    async def submit_adverse_action(self, notice: AdverseActionNotice) -> bool

# app/services/bureau_client.py
class BureauAdapter(ABC):
    @abstractmethod
    async def pull_business_credit(self, tax_id: str) -> BusinessCreditReport
    @abstractmethod
    async def pull_personal_credit(self, ssn: str) -> PersonalCreditReport

# app/services/doc_extractor.py
class DocExtractorAdapter(ABC):
    @abstractmethod
    async def extract(self, doc_path: str, doc_type: str) -> ExtractionResult
    @abstractmethod
    async def classify(self, doc_path: str) -> str  # returns doc_type
```

---

## Data Models

### PostgreSQL (Relational)

```sql
-- Applications
CREATE TABLE applications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status              VARCHAR(32) NOT NULL DEFAULT 'submitted',
    business_name       VARCHAR(255) NOT NULL,
    tax_id              VARCHAR(16) NOT NULL,
    owner_name          VARCHAR(255) NOT NULL,
    owner_ssn_last4     VARCHAR(4) NOT NULL,
    loan_amount_requested DECIMAL(12,2) NOT NULL,
    loan_purpose        VARCHAR(64) NOT NULL,  -- equipment | working_capital | expansion | refinance
    industry_code       VARCHAR(8),            -- NAICS
    years_in_business   INT,
    annual_revenue      DECIMAL(14,2),
    employees           INT,
    state               VARCHAR(2) NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id      UUID REFERENCES applications(id),
    doc_type            VARCHAR(64) NOT NULL,  -- tax_return_1120 | profit_loss | balance_sheet | bank_statement
    file_path           VARCHAR(512) NOT NULL,
    file_size_bytes     INT NOT NULL,
    extraction_status   VARCHAR(32) DEFAULT 'pending',  -- pending | extracted | failed
    extracted_at        TIMESTAMPTZ,
    error_message       TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Extracted Fields
CREATE TABLE extracted_fields (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         UUID REFERENCES documents(id),
    field_name          VARCHAR(128) NOT NULL,  -- revenue | net_income | total_assets | etc.
    field_value         DECIMAL(14,2),
    confidence          FLOAT,                  -- 0.0 to 1.0
    extraction_method   VARCHAR(32),            -- pattern | ml_model | llm
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Decisions
CREATE TABLE decisions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id      UUID REFERENCES applications(id),
    decision_type       VARCHAR(16) NOT NULL,   -- approved | declined | counter
    risk_score          FLOAT NOT NULL,          -- 0.0 to 1.0 (default probability)
    recommended_amount  DECIMAL(12,2),
    recommended_rate    FLOAT,                  -- APR
    recommended_term_months INT,
    final_amount        DECIMAL(12,2),          -- after underwriter override
    final_rate          FLOAT,
    final_term_months   INT,
    underwriter_id      VARCHAR(64),
    underwriter_notes   TEXT,
    decisioned_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Adverse Action Reasons (ECOA-compliant)
CREATE TABLE adverse_action_reasons (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id         UUID REFERENCES decisions(id),
    factor_name         VARCHAR(64) NOT NULL,   -- debt_service_coverage_ratio
    factor_value        VARCHAR(128) NOT NULL,  -- "1.1x"
    threshold           VARCHAR(128),           -- "minimum 1.25x"
    explanation         TEXT NOT NULL,          -- "Your debt service coverage ratio of 1.1x is below..."
    shap_value          FLOAT,                  -- model contribution
    rank                INT NOT NULL            -- 1 = most impactful
);

-- Model Versions
CREATE TABLE model_versions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version             VARCHAR(32) NOT NULL,
    model_path          VARCHAR(512) NOT NULL,
    feature_list        JSONB NOT NULL,
    train_date          TIMESTAMPTZ NOT NULL,
    train_rows          INT NOT NULL,
    validation_auc      FLOAT NOT NULL,
    validation_mape     FLOAT,
    status              VARCHAR(16) DEFAULT 'staging',  -- staging | production | archived
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Predictions Log
CREATE TABLE predictions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id      UUID REFERENCES applications(id),
    model_version_id    UUID REFERENCES model_versions(id),
    risk_score          FLOAT NOT NULL,
    features_snapshot   JSONB NOT NULL,
    shap_values         JSONB NOT NULL,
    predicted_at        TIMESTAMPTZ DEFAULT NOW()
);

-- State Regulations (seeded from CSV)
CREATE TABLE state_regulations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state               VARCHAR(2) NOT NULL,
    regulation_type     VARCHAR(64) NOT NULL,   -- interest_rate_cap | disclosure | licensing
    constraint_type     VARCHAR(32) NOT NULL,   -- max_rate | min_disclosure | license_required
    constraint_value    VARCHAR(256) NOT NULL,
    applies_to_loan_amount_min DECIMAL(12,2),
    applies_to_loan_amount_max DECIMAL(12,2),
    effective_date      DATE NOT NULL,
    source              VARCHAR(256)
);

-- Compliance Checks
CREATE TABLE compliance_checks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id      UUID REFERENCES applications(id),
    decision_id         UUID REFERENCES decisions(id),
    state               VARCHAR(2) NOT NULL,
    check_type          VARCHAR(64) NOT NULL,
    passed              BOOLEAN NOT NULL,
    detail              TEXT,
    checked_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio Loans (post-booking tracking)
CREATE TABLE portfolio_loans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id      UUID REFERENCES applications(id),
    decision_id         UUID REFERENCES decisions(id),
    loan_amount         DECIMAL(12,2) NOT NULL,
    interest_rate       FLOAT NOT NULL,
    term_months         INT NOT NULL,
    originated_at       TIMESTAMPTZ DEFAULT NOW(),
    status              VARCHAR(32) DEFAULT 'current',  -- current | delinquent_30 | delinquent_60 | charged_off
    paid_to_date        DATE,
    next_payment_date   DATE
);

CREATE TABLE payment_history (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id             UUID REFERENCES portfolio_loans(id),
    payment_date        DATE NOT NULL,
    amount_paid         DECIMAL(12,2) NOT NULL,
    principal_portion   DECIMAL(12,2),
    interest_portion    DECIMAL(12,2),
    days_late           INT DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

---

## API Design

### REST Endpoints

| Method | Path | Purpose | Request | Response |
|---|---|---|---|---|
| `POST` | `/api/applications` | Submit new application | `{business_name, tax_id, owner_name, ..., state}` | `ApplicationResponse` |
| `GET` | `/api/applications` | List applications (filterable) | `?status=&state=&from=&to=` | `[{ApplicationResponse}]` |
| `GET` | `/api/applications/{id}` | Application detail | — | `ApplicationDetail` |
| `POST` | `/api/applications/{id}/submit` | Trigger full underwriting flow | — | `{status, current_step}` |
| `POST` | `/api/documents/upload` | Upload document | `multipart: file + doc_type` | `DocumentResponse` |
| `GET` | `/api/documents/{id}` | Document detail + extraction | — | `DocumentWithExtraction` |
| `GET` | `/api/underwriting/status/{app_id}` | Current pipeline step | — | `{status, step, progress_pct}` |
| `POST` | `/api/underwriting/run/{app_id}` | Execute full underwriting | — | `DecisionResponse` |
| `GET` | `/api/underwriting/memo/{app_id}` | Get decision memo | — | `DecisionMemo` |
| `POST` | `/api/decisions/approve/{app_id}` | Underwriter approves | `{amount, rate, term, notes}` | `DecisionResponse` |
| `POST` | `/api/decisions/decline/{app_id}` | Underwriter declines | `{notes}` | `DecisionResponse` |
| `POST` | `/api/decisions/counter/{app_id}` | Underwriter counters | `{amount, rate, term, notes}` | `DecisionResponse` |
| `GET` | `/api/regulations/states` | List all states with rules | — | `[{state, rule_count}]` |
| `GET` | `/api/regulations/check/{app_id}` | Run compliance check | — | `ComplianceResult` |
| `GET` | `/api/portfolio/loans` | Portfolio performance | `?status=&from=&to=` | `[{LoanSummary}]` |
| `GET` | `/api/portfolio/metrics` | Aggregate portfolio metrics | — | `{total_loans, default_rate, avg_risk_score}` |
| `POST` | `/api/demo/seed` | Seed demo data | `{count: 50}` | `{seeded_count}` |
| `POST` | `/api/demo/reset` | Reset to clean state | — | `{status: 'reset'}` |

### Server-Sent Events (SSE)

| Event | Payload | Trigger |
|---|---|---|
| `application.status` | `{app_id, old_status, new_status, step}` | On any status transition |
| `underwriting.progress` | `{app_id, step, progress_pct, eta_seconds}` | During full underwriting run |
| `underwriting.complete` | `{app_id, decision_type, risk_score, memo_url}` | When memo is generated |
| `decision.approved` | `{app_id, amount, rate}` | When underwriter approves |
| `decision.declined` | `{app_id, reasons_count}` | When underwriter declines |
| `compliance.alert` | `{app_id, state, check_type, passed}` | When compliance check fails |

---

## Risk Model

### Training Pipeline

```
1. Synthetic Data Generation (data/synthetic/generate_applications.py)
   - Generate 50,000 synthetic loans over 7-year period
   - Features: financial ratios, credit scores, industry, years in business
   - Target: 1 if charged_off within 2 years, 0 otherwise
   - Base default rate: 4% (calibrated to SMB lending benchmarks)
   - Feature correlations designed to produce realistic risk patterns

2. Feature Engineering (model/features.py)
   - Debt Service Coverage Ratio = net_income / total_debt_payments
   - Cash Flow Volatility = std(revenue_12m) / mean(revenue_12m)
   - Revenue Trend = slope(revenue_12m)
   - Leverage Ratio = total_liabilities / total_assets
   - Current Ratio = current_assets / current_liabilities
   - Profit Margin = net_income / revenue
   - Credit Utilization = total_debt / total_credit_limit
   - Business Age (years)
   - Industry Default Rate (lookup from historical data)
   - Existing Relationship (binary: 1 if existing customer)

3. Model Training (model/train.py)
   - Algorithm: LightGBM
   - Objective: binary classification (default vs. paid)
   - Train/Val Split: temporal (pre-2024 train, 2024+ val)
   - Hyperparameters:
     * num_leaves: 31
     * max_depth: 7
     * learning_rate: 0.05
     * min_data_in_leaf: 50
     * feature_fraction: 0.8
     * bagging_fraction: 0.8
     * early_stopping_rounds: 50
   - Evaluation: AUC-ROC, AUC-PR, KS statistic
   - Target: AUC > 0.75 on validation set

4. Explainability (model/explain.py)
   - SHAP TreeExplainer for feature contributions
   - Top-5 features by |SHAP value| per prediction
   - SHAP values → plain-English mapping via reason templates
```

### Prediction Signature

```python
Input:  numpy array [batch, n_features]
Output: {
    "risk_score":      float,            # 0.0 to 1.0 default probability
    "risk_band":       str,              # low | moderate | elevated | high | decline
    "factors": [
        {
            "name":           str,      # "debt_service_coverage_ratio"
            "shap_value":     float,    # positive = increases risk
            "actual_value":   str,      # "1.1x"
            "threshold":      str,      # ">= 1.25x"
            "plain_english":  str,      # ECOA-compliant explanation
            "impact_pct":     float     # relative contribution percentage
        },
        ...
    ]
}
Latency: ~5ms per prediction on CPU
```

### Risk Bands

| Risk Score | Band | Recommendation | Auto-approve up to |
|---|---|---|---|
| 0.00 – 0.03 | Low | Approve | $100,000 |
| 0.03 – 0.08 | Moderate | Approve with conditions | $50,000 |
| 0.08 – 0.15 | Elevated | Underwriter review required | — |
| 0.15 – 0.30 | High | Decline or secured only | — |
| 0.30 – 1.00 | Decline | Decline | — |

---

## Explainability Layer

### SHAP → Plain-English Mapping

```yaml
# model/config/reasons.yaml
reasons:
  debt_service_coverage_ratio:
    low: >
      Your debt service coverage ratio of {value}x is below our {threshold}x minimum.
      This means your business generates {shortfall_pct}% less cash flow than needed
      to comfortably cover your existing debt payments plus this new loan.
    high: >
      Your debt service coverage ratio of {value}x exceeds our {threshold}x threshold,
      indicating strong cash flow relative to debt obligations.

  cash_flow_volatility:
    high: >
      Your revenue has fluctuated significantly over the past 12 months
      (variation of {value}%). Lenders prefer stable cash flow patterns.
      Months with revenue drops increase the risk of payment disruption.
    low: >
      Your revenue shows stable month-over-month patterns, which supports
      consistent debt repayment capacity.

  leverage_ratio:
    high: >
      Your total liabilities of {liabilities} represent {value}% of your total
      assets of {assets}. A ratio above {threshold} indicates the business
      is heavily reliant on debt financing, leaving less cushion for new debt.
    low: >
      Your leverage ratio of {value}x is within healthy parameters, indicating
      a balanced use of debt and equity financing.

  credit_utilization:
    high: >
      You are currently using {value}% of your available credit lines.
      Utilization above {threshold}% suggests the business is operating
      near its maximum borrowing capacity.
    low: >
      Your credit utilization of {value}% indicates available borrowing
      capacity, which supports the new loan request.

  years_in_business:
    low: >
      Your business has been operating for {value} years. Lenders generally
      prefer businesses with {threshold}+ years of operating history, as
      longer track records correlate with lower default risk.
    high: >
      Your {value}+ year operating history demonstrates business stability
      and is viewed favorably in the risk assessment.

  existing_relationship:
    positive: >
      Your {value}-year banking relationship with us, including {loan_count}
      previous loans with on-time payment history, is a positive factor in
      this decision.
    negative: >
      As a new customer, we have limited payment history data. An established
      banking relationship can support future underwriting decisions.

  personal_credit_score:
    low: >
      Your personal credit score of {value} is below our {threshold} threshold.
      Personal credit history is considered as an indicator of the owner's
      overall financial management.
    high: >
      Your personal credit score of {value} reflects strong personal
      financial management, which supports business creditworthiness.
```

### ECOA-Compliant Adverse Action Notice

```python
# Generated when decision = decline or counter
adverse_action_notice = {
    "borrower_name": "ABC Plumbing LLC",
    "date": "2026-07-01",
    "decision": "Declined",
    "primary_reason": "Debt service coverage ratio of 1.1x is below the 1.25x minimum.",
    "key_factors": [
        "Debt service coverage ratio of 1.1x — below minimum of 1.25x",
        "Cash flow volatility of 34% — above maximum of 25%",
        "Credit utilization of 78% — above recommended 50%",
        "Business operating history of 2 years — below minimum of 3 years",
        "Personal credit score of 620 — below minimum of 660"
    ],
    "disclosure": "The federal Equal Credit Opportunity Act prohibits creditors from discriminating against credit applicants on the basis of race, color, religion, national origin, sex, marital status, age, or because they receive public assistance. We have considered your application in compliance with this law.",
    "agency_info": "You have the right to obtain a free copy of your credit report from the credit reporting agency within 60 days. Contact Experian at 1-888-397-3742.",
    "right_to_explain": "You may request an explanation of this adverse action within 60 days by contacting our lending center at 1-800-XXX-XXXX."
}
```

---

## State Regulation Rules Engine

### Rule Format

```csv
# data/seed/regulations/interest_rate_caps.csv
state,loan_amount_min,loan_amount_max,max_apr,source,effective_date
AL,0,500000,36,Alabama Small Loan Act,2024-01-01
AK,0,1000000,prime+18,Alaska Usury Law,2024-01-01
AZ,0,500000,36,Arizona Revised Statutes §6-601,2024-01-01
AR,0,500000,17,Arkansas Constitution Article 19 §13,2024-01-01
CA,0,500000,prime+12,California Financial Code §22303,2024-01-01
...
```

### Rules Engine Execution

```python
def check_compliance(application, decision) -> ComplianceResult:
    state = application.state
    amount = decision.recommended_amount
    rate = decision.recommended_rate

    checks = []

    # Interest rate cap check
    cap = get_rate_cap(state, amount)
    checks.append({
        "type": "interest_rate_cap",
        "passed": rate <= cap,
        "detail": f"Rate {rate:.1f}% vs cap {cap:.1f}% in {state}"
    })

    # Disclosure requirements
    disclosures = get_disclosure_rules(state)
    for disclosure in disclosures:
        checks.append({
            "type": "disclosure",
            "passed": True,  # disclosures are generated
            "detail": f"Required disclosure: {disclosure.name}"
        })

    # Licensing check
    license_required = is_license_required(state)
    if license_required:
        checks.append({
            "type": "licensing",
            "passed": True,  # assumed licensed for demo
            "detail": f"Lender license required in {state}: CONFIRMED"
        })

    return ComplianceResult(
        state=state,
        all_passed=all(c.passed for c in checks),
        checks=checks
    )
```

---

## Frontend Screens (Next.js + Recharts + SSE)

| Screen | Route | Key Components | Real-time |
|---|---|---|---|
| **Dashboard** | `/` | Pipeline summary (applications by stage), approval rate gauge, avg risk score trend, decision volume chart | SSE: application.status, underwriting.progress |
| **Applications** | `/applications` | Filterable table (status, state, amount, date), status badges with color, click to detail, demo seed button | SSE: application.status |
| **Application Detail** | `/application/[id]` | Borrower info panel, document list with extraction status, financial summary table, decision card with risk score, explanation panel, state compliance badge, underwriter memo editor, approve/decline/counter buttons | SSE: underwriting.complete, compliance.alert |
| **Decision Review** | `/application/[id]/decision` | Full credit memo (risk score, top-5 factors with plain-English, recommended terms), state compliance overlay, underwriter edit fields, signature/approve flow | — (request/response) |
| **Portfolio** | `/portfolio` | Loan performance chart (current vs. delinquent vs. charged-off), default rate trend, risk score distribution, payment history drilldown | SSE: decision.approved |
| **Regulations** | `/regulations` | Map view (state-by-state rate caps + rules), search/filter by state, rule detail panel, compliance check history | — |
| **Admin** | `/admin` | Model version table, feature importance chart, prediction error metrics, feature config editor, demo data controls (seed/reset) | — |

---

## Design Decisions & Trade-offs

### 1. LightGBM over Deep Learning

| Dimension | LightGBM | Neural Network (MLP) | Decision |
|---|---|---|---|
| Training time | 2 min (CPU) | 30 min (CPU) | LightGBM |
| Explainability | Built-in SHAP, feature importance | Requires SHAP/LIME separately | LightGBM |
| Data efficiency | Good (5K+ rows sufficient) | Poor (needs 50K+) | LightGBM |
| Overfitting risk | Low (regularized trees) | Higher (needs careful tuning) | LightGBM |
| Calibration | Well-calibrated probabilities | Often overconfident | LightGBM |
| Regulatory acceptance | Widely accepted in credit | Less common | LightGBM |

**Decision**: LightGBM is the standard for credit risk modeling — regulators (SR 11-7) are familiar with tree-based models, calibration is reliable, and SHAP explainability is production-proven.

### 2. Pluggable Adapters for External Dependencies

| Dimension | Simulator (Default) | REST Adapter | Decision |
|---|---|---|---|
| Demo readiness | Self-contained, no external deps | Requires live LOS/bureau | Simulator |
| Realism | Synthetic data, but calibrated | Real data | REST wins |
| Integration effort | Zero | 2-4 weeks per adapter | Simulator |
| Testing | Deterministic, reproducible | Network-dependent, flaky | Simulator |
| CI/CD | No external secrets needed | Requires credentials | Simulator |

**Decision**: Adapter pattern with simulator default. System runs 100% self-contained for demo. Swap configuration to REST adapters for production. Same codebase, different config.

### 3. PostgreSQL over Document Store

| Dimension | PostgreSQL | MongoDB / Document DB | Decision |
|---|---|---|---|
| Schema | Fixed (well-defined loan data) | Flexible (extraction varies) | PostgreSQL wins for structured |
| Query complexity | JOINs across applications, decisions, loans | Complex aggregations harder | PostgreSQL |
| JSON support | JSONB for flexible fields | Native documents | Similar |
| Compliance audit | Referential integrity + transactions | Weaker consistency | PostgreSQL |

**Decision**: PostgreSQL with JSONB for extracted fields. The core data (applications, decisions, loans) is highly structured. The extracted field data varies per document type — JSONB handles this without sacrificing relational integrity.

### 4. SSE over WebSocket

| Dimension | SSE | WebSocket | Decision |
|---|---|---|---|
| Direction | Server → Client only | Bidirectional | SSE sufficient |
| Reconnection | Auto (EventSource API) | Manual | SSE |
| Firewall | HTTP (port 443) | TCP upgrade | SSE |
| Use case | Status updates only | Real-time collaboration | SSE |

**Decision**: Underwriter dashboard needs server-pushed status updates (pipeline progress, extraction complete, decision ready). No bidirectional streaming required.

### 5. Synthetic Data for Training over Real Data

| Dimension | Synthetic | Real Historical | Decision |
|---|---|---|---|
| Availability | Generated instantly | May require data access | Synthetic |
| Privacy risk | None | PII/compliance review needed | Synthetic |
| Realism | Approximates real patterns | Ground truth | Real wins |
| Bias | Controlled | May contain historical bias | — |
| Demo readiness | Works immediately | Legal review may take weeks | Synthetic |

**Decision**: 50K synthetic loans generated with realistic correlations (default rates by industry, revenue patterns, credit score distributions). Real data should replace synthetic before production deployment, but synthetic data enables demo without any data access or privacy review.

---

## Alternatives Considered (Summary)

| Alternative | Status | Why Rejected |
|---|---|---|
| **XGBoost** | Considered | LightGBM chosen for faster training, lower memory, native categorical support |
| **Random Forest** | Considered | Worse calibration for probability outputs vs. LightGBM |
| **Logistic Regression** | Considered | Too simple — cannot capture non-linear interactions in credit data |
| **Azure Doc Intelligence pre-built** | Considered | Will use in production; simulator used for demo self-containment |
| **Blend / nCino purchase** | Considered | Readiness assessment recommends evaluating; design doc assumes build path |
| **MongoDB** | Considered | PostgreSQL JSONB handles semi-structured extraction data without losing relational integrity |
| **Kafka for events** | Considered | Overkill for single-application workflow; SSE sufficient for underwriter dashboard |
| **GraphQL** | Considered | REST is simpler, sufficient for underwriter dashboard with 6 screens |
| **Docker Compose vs. K8s** | Considered | Docker Compose sufficient for demo; K8s for production |

---

## Limitations

### 1. Synthetic Data Realism Ceiling

The synthetic loan data is calibrated to known benchmarks but cannot capture real-world edge cases — fraud patterns, industry-specific risk cycles, regional economic shocks. The model's AUC on synthetic data will not translate 1:1 to production.

**Mitigation**: The adapter pattern allows seamless swap to real data. Model retraining on real data is Phase 1 of production deployment. The synthetic model serves as a proof point, not a production asset.

### 2. Document Simulator Accuracy

The rule-based document simulator extracts fields using text patterns and templates. Real financial documents have layout variations, handwritten entries, missing pages, and low-quality scans that the simulator does not model.

**Mitigation**: The doc_extractor interface abstracts the implementation. For demo purposes, the simulator demonstrates the workflow. The extraction accuracy metric (92%) in the config sets expectations that real extraction will differ.

### 3. State Regulation Coverage

The 50-state regulation CSV is a simplified representation. Real state lending laws have complex interactions (e.g., preemption, tribal lending exemptions, rate exportation rules) that the rules engine does not capture.

**Mitigation**: Marked as "demo coverage" — the engine demonstrates the compliance workflow. Production deployment requires a dedicated compliance engineering effort and legal review per state.

### 4. Mock Credit Bureau Scores

The credit bureau simulator generates scores from a normal distribution with calibrated means. Real credit reports contain derogatory marks, trade line details, and inquiry histories that affect risk in non-linear ways.

**Mitigation**: The simulated scores produce realistic risk band distributions. For demo purposes, the workflow demonstration is unaffected by score realism.

### 5. No Multi-Product Support

ClearLend handles term loans only. Real small business lending includes lines of credit, SBA loans, equipment financing, invoice factoring — each with different risk models and regulatory requirements.

**Mitigation**: The architecture supports adding new product types via new feature definitions and model training. Scoped to term loans for the initial demo.

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| API server | FastAPI + Uvicorn | 0.115+ | Async REST + SSE |
| Database | PostgreSQL + pgvector | 16+ | Relational data + embeddings |
| Object storage | MinIO | LATEST | Document PDFs, model artifacts |
| Cache / queue | Redis | 7+ | SSE broadcast, task queue |
| Risk model | LightGBM | 4.5+ | Gradient-boosted default prediction |
| Explainability | SHAP | 0.46+ | Feature contribution analysis |
| Feature store | Feast | 0.40+ | Reusable feature definitions |
| Document extraction | Pluggable (simulator default) | — | PDF → structured fields |
| LOS adapter | Pluggable (simulator default) | — | Application data pull/push |
| Bureau adapter | Pluggable (simulator default) | — | Credit report pull |
| Frontend | Next.js + Recharts | 14+ | Dashboard, decision review, portfolio |
| Real-time UI | Server-Sent Events | — | Pipeline status updates |
| Styling | Tailwind CSS | 3+ | UI components |
| Auth | Keycloak | 24+ | OAuth 2.0 + RBAC |
| Monitoring | Prometheus + Grafana + OpenTelemetry | LATEST | Metrics, tracing, dashboards |
| CI/CD | GitHub Actions + Docker Compose | LATEST | Build, test, demo deploy |
| Demo orchestration | Docker Compose | LATEST | Single-command `docker compose up` |

---

## Implementation Phases (Demo Build)

| Phase | Tasks | Duration | Dependencies |
|---|---|---|---|
| **P1: Scaffold** | FastAPI project, PostgreSQL + MinIO + Redis Docker, SQLAlchemy models, Alembic migrations, Docker Compose, CI/CD | 1 week | — |
| **P2: Adapters** | LOS simulator, bureau simulator, doc extractor simulator — all with pluggable interface | 1 week | P1 |
| **P3: Data Pipeline** | Document upload → storage → extraction → field mapping → feature vector | 2 weeks | P2 |
| **P4: Risk Model** | Synthetic data generation (50K loans), LightGBM training pipeline, SHAP explainability, evaluation | 2 weeks | P1 |
| **P5: Decision Engine** | Feature assembly → risk score → factor explanations → state compliance check → memo generation | 2 weeks | P3, P4 |
| **P6: Frontend Dashboard** | Next.js app, application form, document upload, decision card, memo view, approve/decline flow | 3 weeks | P5 |
| **P7: Portfolio + Admin** | Portfolio performance charts, model management, demo seed/reset, SSE pipeline status | 1 week | P6 |
| **P8: Demo Polish** | Demo seed data (50 realistic applications), one-click demo flow, management presentation script | 1 week | P7 |

**Total: 13 weeks (team of 3: 1 full-stack, 1 ML, 1 backend)**

---

## Demo Script (Management Walkthrough)

### One-Click Demo Flow

```
1. Seed Data
   → Click "Seed Demo" → 50 synthetic applications loaded
   → Mix of industries, states, credit profiles
   → 10 applications ready for decision

2. Pipeline Walkthrough
   → Select application #1: "ABC Plumbing LLC" — $150K equipment loan
   → Show document upload (pre-seeded: tax return, P&L, bank statement)
   → Click "Run Underwriting" → watch SSE progress bar:
       ■ Uploading documents...
       ■ Extracting financials... (shows extracted fields)
       ■ Pulling credit bureau... (shows mock scores)
       ■ Computing risk score... (shows LightGBM running)
       ■ Checking state compliance... (shows NY rules)
       ■ Generating decision memo...

3. Decision Review
   → Risk score: 0.04 (Low) — auto-approve eligible
   → Top-5 factors with plain-English explanations
   → State compliance: passed (NY rate cap check)
   → Underwriter clicks "Approve" — loan booked

4. Decline Scenario
   → Select application #2: "XYZ Roofing" — $200K, 2yr in business
   → Risk score: 0.28 (High) — decline recommended
   → Show ECOA-compliant adverse action notice
   → Top-5 factors with specific explanations
   → Underwriter can override or accept decline

5. Portfolio View
   → Show portfolio of 50 loans
   → Approval rate, risk score distribution
   → State regulation explorer map
```

---

## Performance Targets

| Metric | Current | Target | Measurement |
|---|---|---|---|
| Underwriting cycle time | 5 days | < 4 hours | Application submit → decision |
| Document extraction time | 2 days (manual) | < 2 minutes | Upload → structured fields |
| Risk model inference | — | < 50ms p99 | API endpoint latency |
| Decision memo generation | 4 hours (manual) | < 5 seconds | Risk score → full memo |
| Risk model AUC | — | > 0.75 | Out-of-time validation |
| Explanation precision | — | > 95% | Factor accuracy against underwriter review |
| State compliance coverage | — | 50 states | Rules engine coverage |
| Demo startup time | — | < 2 minutes | `docker compose up` to ready |
| System uptime (demo) | — | 99% | Local Docker environment |

---

*Designed for management demo — all external dependencies simulated via pluggable adapters. Swap config for production integration.*

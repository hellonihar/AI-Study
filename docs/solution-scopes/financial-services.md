# AI Solution Scopes — Financial Services

## (8 examples)

| # | Problem | AI Solution | Scope Deliverables |
|---|---|---|---|
| 9 | Fraud detection misses 1 in 5 sophisticated account takeovers | Graph-based anomaly detection — model user behavior as temporal graph, flag deviant transaction chains | Core banking API integration, real-time inference at <100ms p99, SAR filing automation, false positive tuning with fraud team |
| 10 | Loan underwriting takes 5 days for small businesses | See **[ClearLend](../../projects/industry-solutions/financial-services/clearlend/readiness-assessment.md)** (readiness) — **[design](../../projects/industry-solutions/financial-services/clearlend/design.md)** — Automated underwriting agent: extracts financials from uploaded docs, runs risk model with SHAP explainability, generates ECOA-compliant decision memo | Document parser pipeline, explainability overlay for ECOA compliance, 50-state lending regulation mapping, underwriter review SLA |
| 11 | Wealth managers spend 60% of time on portfolio reporting | LLM generates client-ready performance narratives from raw portfolio data + market context | PDF/HTML report generation, client data isolation, advisor review-and-approve workflow, reporting time baseline |
| 12 | KYC/AML review takes 3 hours per new account | Multi-agent system: extraction agent parses ID docs, screening agent checks watchlists, summarization agent produces review packet | Watchlist API integrations (Dow Jones, OFAC), false positive tuning per jurisdiction, audit trail for regulator, review time SLA |
| 13 | Customer call center hold times > 8 min during peak | LLM voice agent handles Tier-1 inquiries (balance, transactions, card activation) with live escalation | IVR integration, sentiment-based escalation, agent takeover handoff protocol, containment rate target, CSAT tracking |
| 14 | Regulatory filing preparation takes 200 person-hours per quarter | LLM reads regulatory changes, maps to internal data, drafts filing sections with source citations | Document management integration, regulator API filing, compliance officer review workflow, filing accuracy audit |
| 15 | Merchant underwriting for payment processing takes 2 weeks | ML risk model on merchant application data + external signals (social media, credit bureau) with automated decision | Payment platform integration, bureau API feed, model fairness audit per ECOA, decision turnaround target |
| 16 | Trade surveillance generates 5,000 false alerts per day | ML alert prioritization model — scores alerts by likelihood of actual market abuse, groups related alerts | Trade capture system integration, alert workflow redesign, analyst review efficiency target, FINRA compliance mapping |

---
*See the [full catalog](../ai-solution-scoping-examples.md) for all 100 examples across 20 industries.*

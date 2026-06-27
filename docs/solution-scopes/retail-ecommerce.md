# AI Solution Scopes — Retail & E-Commerce

## (7 examples)

| # | Problem | AI Solution | Scope Deliverables |
|---|---|---|---|
| 17 | Search on 500K-SKU catalog returns irrelevant results for vague queries | Hybrid semantic search — embed product descriptions + images, query understanding, personalized reranking | Catalog API integration, A/B test on conversion rate, cold-start strategy for new products, search latency SLA < 200ms |
| 18 | 40% cart abandonment rate | Personalized abandonment prevention — predict churn risk per cart, trigger LLM-generated offer + reason | Real-time event stream (Kafka), promotion engine integration, incrementality measurement via holdout, revenue lift target |
| 19 | Inventory forecasting errors: 8% stockout + 12% overstock | Time-series foundation model (Lag-Llama / PatchTFT) with promotions, weather, competitor price signals | POS + ERP + external data pipeline, retraining cadence, inventory planner dashboard, forecast accuracy SLA |
| 20 | Product descriptions for 10K new items/month are inconsistent | LLM product copy generator — extracts specs from vendor sheets, generates SEO descriptions in brand tone | Vendor data ingestion pipeline, human review queue, style guide definition per category, description acceptance rate |
| 21 | Personalized recommendations drive < 5% of revenue | Multi-modal two-tower model: purchase history + browsing + product attributes + visual features | Real-time serving via Redis, cold-start for new users, diversity metric (catalog coverage), A/B test on revenue per visitor |
| 22 | Customer reviews contain actionable feedback but no one reads them at scale | LLM that summarizes review corpus by product, extracts common complaints, suggests improvements | Review ingestion pipeline, product team dashboard, sentiment trend tracking, actionable insight precision target |
| 23 | Visual search feature built but adoption < 2% of users | Improve visual search with style-aware embeddings + attribute filters + similar-item gallery | Mobile SDK integration, camera UX redesign, A/B test on add-to-cart rate, query understanding accuracy audit |

---
*See the [full catalog](../ai-solution-scoping-examples.md) for all 100 examples across 20 industries.*

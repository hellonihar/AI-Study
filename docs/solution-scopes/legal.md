# AI Solution Scopes — Legal

## (5 examples)

| # | Problem | AI Solution | Scope Deliverables |
|---|---|---|---|
| 31 | Contract review takes 6 hours per document for standard NDAs | LLM extracts key clauses, flags deviations from playbook, generates redlined version with explanation | DMS integration (iManage/NetDocuments), playbook configuration UI, lawyer-in-loop approval, review time baseline |
| 32 | Discovery phase requires reviewing 500K documents in 30 days | Multi-stage pipeline: classifier filters relevance → LLM extracts facts → clustering groups documents → privilege log generator | eDiscovery platform integration, search term validation protocol, privilege log format per jurisdiction, review throughput target |
| 33 | Legal research for a novel argument takes 8+ hours | RAG system over case law + statutes — retrieves most relevant precedents with citation chain and conflicting rulings | Legal database API integration (Westlaw/Pacer), citation verification step, confidence calibration per jurisdiction, research time target |
| 34 | M&A due diligence reads 10K+ documents in 2 weeks | Multi-agent: extractor reads each doc, risk classifier flags issues, deal breaker detector highlights must-address items | VDR integration, issue taxonomy config, deal team dashboard, automated risk report generation, coverage SLA |
| 35 | Compliance training completion < 60% across firm | Adaptive learning LLM — generates personalized training scenarios from actual compliance incidents, quizzes, and tracks understanding | LMS integration, incident database connection, quiz pass rate target, audit readiness score |

---
*See the [full catalog](../ai-solution-scoping-examples.md) for all 100 examples across 20 industries.*

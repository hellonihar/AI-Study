# Industry Solutions — AI Solution Blueprints

Every industry vertical presents a unique set of constraints — regulatory, operational, data, and legacy — that shape how AI solutions must be designed. This directory captures the motive to build industry-specific solution blueprints from two viewpoints that must align for any real-world AI initiative to succeed.

---

## From an AI Architect's Perspective

**Pattern recognition across domains.** Document intelligence, RAG, multi-agent orchestration, anomaly detection, and prediction models repeat across every industry. The differences are in the constraints, not the core architecture. A clinical documentation AI (healthcare) and a claims processing AI (insurance) share the same ingestion → extraction → reasoning → review pipeline. Building across industries trains the eye to see the 80% transferable core and the 20% domain-specific customization.

**Constraint-driven design sharpens judgment.** Each industry adds a unique constraint layer:
- Healthcare: HIPAA data boundaries, FHIR integration, FDA pathways for clinical AI
- Insurance: 50-state DOI compliance, PII/PHI separation, CPU-only inference targets
- Financial services: ECOA explainability mandates, real-time fraud inference at sub-100ms, OFAC screening
- Defense/aerospace: air-gapped deployment, model robustness certification, supply chain security

Architecting for these constraints — not just for accuracy — builds the production readiness that separates deployed systems from demo projects.

**Reusable blueprints emerge.** The stack choices in these blueprints (PaddleOCR for CPU document AI, llama.cpp for self-hosted LLM, pgvector for vector search without additional infrastructure) are designed to be mix-and-matched across industries. A fraud detection pattern from financial services drops into an insurance claims pipeline with minimal modification. A document extraction pattern from legal eDiscovery transfers directly to healthcare prior authorization.

**Skill development through breadth.** Building the same solution for one industry teaches depth. Building across 20 industries teaches architectural judgment — when to reuse, when to customize, and how to design for the next unanticipated constraint.

---

## From a Business Leader's Perspective

**Industry-vertical AI is a competitive moat.** Horizontal AI platforms (chatbots, copilots) are commoditizing. Industry-specific solutions — trained on domain data, wired into vertical workflows, compliant with vertical regulations — command higher margins and face fewer competitors. Each blueprint in this directory is a potential product line or internal capability that differentiates an organization in its market.

**Scoping risk is the #1 reason AI projects fail.** These blueprints eliminate ambiguity by defining concrete scope deliverables for every solution: which systems to integrate, which compliance frameworks apply, which workflow changes are required, and what success metrics to track. A business leader can hand this to a vendor, a build team, or an internal COE and get back a predictable timeline and budget.

**Cross-industry innovation transfers value.** A pattern proven in one vertical often has higher-value applications in another. The same multi-agent document extraction pipeline that serves legal M&A due diligence (example 34) can be applied to insurance claims triage (example 51) and government FOIA processing (example 62). These blueprints make those adjacencies visible and actionable.

**Investment clarity.** Every solution includes:
- Phased implementation plan with dependencies and durations
- Performance targets with current vs. target measurements
- Regulatory and compliance path scoped upfront
- Technology stack with version-specific selections

This enables build-vs-buy analysis, vendor evaluation scorecards, and multi-year roadmaps grounded in engineering reality rather than vendor promises.

---

## How to Use This Directory

| Approach | How |
|---|---|
| Browse by industry | Open any folder below — each will contain solution designs specific to that vertical |
| Cross-reference scopes | `docs/solution-scopes/{industry}.md` has the concise 4–8 example table; design docs here expand individual solutions |
| Cross-industry pattern search | Find recurring techniques (RAG, multi-agent, CV, anomaly detection, document AI) across multiple industries to identify reusable components |
| Scope template | Use the Problem → AI Solution → Scope Deliverables format from any entry as a template for scoping new AI initiatives |

---

## Industries

- [aerospace-defense](./aerospace-defense/)
- [agriculture](./agriculture/)
- [automotive](./automotive/)
- [construction-engineering](./construction-engineering/)
- [cybersecurity](./cybersecurity/)
- [education](./education/)
- [energy-utilities](./energy-utilities/)
- [financial-services](./financial-services/)
- [government-public-sector](./government-public-sector/)
- [healthcare](./healthcare/)
- [hospitality-travel](./hospitality-travel/)
- [human-resources](./human-resources/)
- [insurance](./insurance/)
- [legal](./legal/)
- [logistics-transportation](./logistics-transportation/)
- [manufacturing-industrial](./manufacturing-industrial/)
- [media-entertainment](./media-entertainment/)
- [real-estate](./real-estate/)
- [retail-ecommerce](./retail-ecommerce/)
- [telecommunications](./telecommunications/)

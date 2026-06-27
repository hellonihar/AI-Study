# AI Problem Analysis Framework

When to use AI, when not to, and how to decide.

---

## 1. Introduction

Most AI project failures don't fail because the model didn't work — they fail because the **wrong problem was chosen**, or because AI was applied where a simpler solution would have sufficed. This framework helps you analyze a business problem systematically, identify which components genuinely benefit from AI, and make a defendable go/no-go decision.

The framework is designed for three audiences reading it together:

| Role | What They Bring | What They Take Away |
|---|---|---|
| **Business stakeholder** | Problem domain knowledge, budget authority, success criteria | A realistic assessment of what AI can deliver and at what cost |
| **AI architect** | Technical feasibility judgment, infrastructure awareness | A structured process to avoid confirmation bias ("I have a hammer, everything is a nail") |
| **Project manager** | Timeline constraints, team capabilities | A risk-calibrated phasing plan with clear dependencies |

The framework is meant to be used **before** any solution scoping (that comes next, via `ai-solution-scoping-examples.md`) and **before** any design work (that follows in the SDLC layers guide at `ai-sdlc-layers-summary.md`). It is the first gate in a three-stage process:

```
Problem Analysis ──► Solution Scoping ──► Architecture & Build
   (this doc)         (examples catalog)     (SDLC layers)
```

---

## 2. The "AI First" Reflex

Before analyzing any problem, be aware of the four most common traps that lead teams to pursue AI solutions unnecessarily.

### Trap 1: The Hammer and the Nail

A team with deep ML expertise tends to see every problem as a modeling problem. If your team just spent six months building a recommendation system, every new request looks like it needs embeddings and ranking.

**Reality check**: ~40% of business problems are solved more cheaply and reliably with 20 lines of if-else logic, a lookup table, or a simple arithmetic formula.

### Trap 2: FOMO Adoption

"We need an AI chatbot because our competitor has one." This is the most expensive form of requirements gathering. A chatbot that handles 80% of inquiries still needs a 20% human escalation path, training data, continuous monitoring, and a content maintenance process —all of which cost more than the chat interface itself.

### Trap 3: Cargo-Culting Solutions

Reading that "Company X reduced costs by 40% using AI" leads teams to copy the technique without understanding whether their problem matches. The technique that solved Company X's problem (vision-based defect detection on an assembly line) has nothing to do with your problem (employee timesheet approval).

### Trap 4: Overestimating AI's Reliability

AI is probabilistic. A 95% accurate model will make mistakes 5% of the time. If your problem requires 100% accuracy (e.g., tax calculation, dosage recommendation, compliance filing), AI may still be part of the solution — but only with a human-in-loop or rule-based override. The cost of that oversight must be factored into the comparison against a purely rule-based system.

### The Golden Rule

**Start with the simplest possible solution that meets success criteria, then add AI only where it is strictly necessary.** AI introduces complexity, latency, cost, and opacity — every layer of AI must earn its place in the architecture.

---

## 3. Problem Decomposition Template

Do not ask "Can AI solve this problem?" Ask instead: **"What are the atomic sub-problems, and which ones need AI?"**

### The Decomposition Canvas

Every business problem can be decomposed into a structured description:

```
Problem Name:          [Short descriptive name]
Business Context:      [Who experiences this problem, when, how often]
Current State:         [How is it solved today (even if poorly)?]
Pain Point:            [Quantified: time lost, revenue missed, errors caused]
Success Criteria:      [Measurable: reduce X by Y% within Z timeframe]
```

### Then decompose into atomic steps

For each step in the process, document:

| Step | Input | Transformation | Output | Success Criteria | Simplest Approach |
|---|---|---|---|---|---|
| 1 | What data comes in | What needs to happen | What comes out | How to measure success | Rule, formula, ML, LLM, or not needed |
| 2 | ... | ... | ... | ... | ... |

### Worked Decomposition: Insurance Claims Processing

This is entry #51 from `ai-solution-scoping-examples.md`. Let's decompose it:

```
Problem Name:          Insurance claims processing takes 14 days
Business Context:      P&C insurance carrier, 10,000 claims/month, 50 adjusters
Current State:         Manual: documents printed, data entered by hand, photos emailed,
                       fraud checked via spreadsheet rules, settlement by adjuster judgment
Pain Point:            14-day average cycle time, 5 claims/day per adjuster,
                       $2M/month in pending-claim float cost
Success Criteria:      <3 day average cycle time, 40% auto-approve rate,
                       20 claims/day per adjuster throughput
```

| Step | Input | Transformation | Output | Simplest Approach |
|---|---|---|---|---|
| 1. Document classification | Scanned PDF, photo | Identify document type (form, invoice, police report) | Document type label | Rule-based (OCR + keyword match) — 90% accuracy is fine |
| 2. Data extraction | Claim form (structured layout) | Extract policy #, date, amount | Structured fields | **AI needed**: Layout varies by state, carrier, form version. Rules cannot handle the variety. |
| 3. Damage assessment | Damage photos | Identify severity, estimate cost | Severity label + cost range | **AI needed**: Visual judgment requires understanding of what "severe" vs "minor" damage looks like |
| 4. Fraud detection | Claimant history, document metadata | Score probability of fraud | Fraud score [0–1] | **AI needed**: Fraud patterns are adversarial and evolve. Rules become stale. |
| 5. Settlement amount | Policy limits, damage estimate, fraud score | Recommend payout amount | Settlement recommendation | **AI needed**: Requires synthesis of multiple signals with nuanced policy interpretation |

**Result**: 4 out of 5 steps need AI. The first step (document classification) can use simple rules, saving ML budget for the harder steps.

---

## 4. The Simplest Viable Path (SVP) Matrix

For each sub-problem from the decomposition, evaluate solutions along this spectrum:

```
Cheaper, Faster, Explainable ────────────────── Expensive, Slow, Black-box
    │            │           │           │               │
    │    If/Else │  Formula  │ Classical │     Deep      │    LLM /
    │   + Regex  │ / Lookup  │    ML     │   Learning    │ Foundation
    │            │           │           │               │   Model
    └────────────┴───────────┴───────────┴───────────────┴───────────
```

### When to use each level

| Level | Best For | Cost | Accuracy Ceiling | Explainability | Example |
|---|---|---|---|---|---|
| **1. Rules/Regex** | Stable patterns, known edge cases, regulatory requirements | Free | 100% (by definition) | Perfect | "If email contains 'unsubscribe', don't send marketing" |
| **2. Formula/Heuristic** | Physical laws, well-understood processes, simple arithmetic | Free | Depends on formula quality | Perfect | "Overtime pay = hours × 1.5 × hourly_rate" |
| **3. Classical ML** | Tabular data, feature engineering is feasible, <10K training examples | Low | 85–95% | High (SHAP, coefficients) | "Predict payment default from credit history features" |
| **4. Deep Learning** | Unstructured data (images, audio, raw text), >50K examples | Medium | 90–98% | Low (saliency maps, approximations) | "Detect tumors in MRI scans" |
| **5. LLM / Foundation Model** | Language understanding, generation, zero-shot tasks, ambiguous inputs | High | 80–95% | Very low (chain-of-thought is post-hoc) | "Summarize a 20-page contract into 3 key clauses" |

### The Decision Rule

**Try level N before moving to level N+1.** Only escalate if:

- Level N cannot meet the success criteria (accuracy, coverage, or latency)
- Level N would require more maintenance than level N+1 (complexity inversion — rare but possible)
- The problem fundamentally involves unstructured data that rules cannot parse

### Example: Factory Energy Optimization (Entry #27)

| Sub-problem | Level 1–2 (Rules/Formula) | Level 3–4 (ML/DL) | Level 5 (LLM) | Decision |
|---|---|---|---|---|
| Read current temp, power, production status | Direct sensor read — no intelligence needed | Overkill | Overkill | **L1 — Direct read** |
| Model how temperature changes with HVAC settings | Physics formula: dT/dt = (P - load - UA·ΔT) / mass | LightGBM can learn it from data | Overkill | **L2 — Physics formula** |
| Find optimal HVAC setpoints given production schedule | Simple: cool when hot, heat when cold (inefficient) | **MPC with LightGBM dynamics** — learns trade-offs | Overkill | **L3 — Classical ML** |
| Explain why a setpoint was chosen | Formula provides direct calculation | SHAP on LightGBM | LLM can generate natural language explanation | **L3 + optional L5** for reporting |

**Result**: The core optimization uses ML (Level 3), but the temperature dynamics use a physics formula (Level 2). No deep learning or LLM needed. This is the FactoryRL design.

---

## 5. The AI Suitability Test

For each sub-problem where the simplest path suggests AI (Level 3+), run these 5 questions.

### Question 1: Does the problem require understanding of nuance, ambiguity, or unstructured data?

| If yes | If no |
|---|---|
| Strong candidate for AI. Language, images, audio, and free-form text cannot be parsed comprehensively by rules. | Consider rules or formulas. Structured data with fixed formats rarely needs AI. |

**Examples**:
- "Extract invoice total from 10,000 vendor formats" → YES (LLM or CV)
- "Are there more than 5 characters in this field?" → NO (simple length check)

### Question 2: Is there sufficient data (or a relevant pre-trained model)?

| Data Condition | Verdict |
|---|---|
| >10K labeled examples for the specific task | Classic ML or fine-tuning is viable |
| 1K–10K labeled examples | Pre-trained model + fine-tuning may work |
| <1K labeled examples | Use rules, or zero-shot LLM (if applicable), or invest in data labeling |
| No relevant data exists | AI is not viable unless you can generate synthetic data or use a foundation model zero-shot |

### Question 3: Can you tolerate errors (or is there a human-in-loop)?

| Error tolerance | Example | AI Feasibility |
|---|---|---|
| 0% errors required | Tax calculation, dosage recommendation | AI alone is not suitable. Use rules with AI as advisory only. |
| <5% error rate | Spam classification, product recommendation | AI is suitable with monitoring |
| >5% error rate acceptable | Draft generation, content summarization | AI is suitable — user will edit output |
| Errors caught by human review | Claims processing, document extraction | AI is suitable — human-in-loop is the safety net |

### Question 4: Is the cost of wrong answers lower than the cost of using AI?

A simple formula:

```
Cost of AI = Build cost + Per-inference cost + Maintenance cost + Compliance cost
Cost of NOT using AI = Cost of errors × Error rate × Volume
```

If `Cost of NOT using AI < Cost of AI`, don't use AI.

**Example**: A $0.01/ticket classification error costs $5,000/month at 500K tickets. A rules-based system costs $2,000/month to maintain. An AI system costs $8,000/month (API + monitoring). AI is not justified — the rules system is good enough.

### Question 5: Is there a simpler non-AI solution that achieves 80%+ of the goal?

This is the pragmatic test. Most stakeholders want improvement, not perfection. If a 20-line script solves 80% of the problem, **ship the script first**. Add AI layer only for the remaining 20%.

```
Prioritization:
  1. Ship the 80% solution (rules/scripts) — delivers value immediately
  2. Measure what the 80% missed — guides the AI scope precisely
  3. Build AI for the 20% that needs it — only where justified
```

### Scoring Rubric

| Score | Q1 (Nuance) | Q2 (Data) | Q3 (Error Tolerance) | Q4 (Cost Benefit) | Q5 (Simpler Path) |
|---|---|---|---|---|---|
| Yes (+) | +2 | +2 | +2 (if human-in-loop) | +2 (AI cheaper) | +1 (no simpler path) |
| Partial | +1 | +1 | — | +1 (break-even) | — |
| No (−) | 0 | 0 | 0 (no human-in-loop) | 0 (cheaper without AI) | 0 (simpler path exists) |

| Total Score | Verdict |
|---|---|
| 8–10 | Strong AI candidate — proceed to solution scoping |
| 5–7 | AI may be justified for specific sub-problems — use hybrid approach |
| 0–4 | AI is unlikely to be the right answer — reconsider |

---

## 6. Solution Archetypes & When They Apply

Once you've determined that AI is justified for a sub-problem, identify which archetype matches:

| Archetype | Input | Output | Typical Accuracy | Example from Catalog |
|---|---|---|---|---|
| **Classification / Extraction** | Text, image, audio | Label, structured fields | 90–98% | Entry #51: Document classification in claims |
| **Generation / Summarization** | Text, structured data | Text, report, narrative | 80–95% | Entry #11: Portfolio performance narratives |
| **Prediction / Forecasting** | Time-series, tabular | Future value, probability | 80–95% | Entry #46: Renewable energy forecast |
| **Recommendation / Ranking** | User history, item catalog | Ordered list, relevance score | 70–90% | Entry #17: Product search ranking |
| **Optimization** | State variables, constraints | Optimal action sequence | N/A (measured by objective) | Entry #27: HVAC + production optimization |
| **Anomaly Detection** | Time-series, logs | Outlier score, alert | 80–95% (precision) | Entry #49: Transformer failure prediction |
| **Conversation / QA** | User query, context | Natural language response | 70–90% (task completion) | Entry #61: Benefits eligibility chatbot |

### How to choose

Ask three questions:

1. **What is the output type?** (label → classification, number → prediction, text → generation, action → optimization)
2. **What is the error model?** (false positives tolerable? false negatives?)
3. **What is the latency requirement?** (real-time → lightweight model, async → larger model)

Match these against the archetype table above. The archetype determines the model family, not the specific architecture — that comes in the design phase.

---

## 7. Organizational AI Readiness

AI solutions are not just about the model — they require organizational infrastructure. Assess readiness across four dimensions before committing to an AI solution.

### Dimension 1: Data Maturity

| Level | Description | Can Support |
|---|---|---|
| **L1: Ad-hoc** | Data exists but is siloed, inconsistent, unlabeled | Rules-based solutions only |
| **L2: Collected** | Data is centralized and clean, but not labeled for ML | Classical ML with unsupervised methods |
| **L3: Curated** | Labeled datasets exist for key tasks; data pipeline is automated | Fine-tuning pre-trained models |
| **L4: Systematic** | Data versioning, labeling workflows, feature stores in place; ML metadata tracked | Full ML lifecycle; multiple models in production |

**Gap analysis**: If your target solution requires L3 but your organization is at L1, the first phase must be data infrastructure, not model building. Do not skip this — models trained on ad-hoc data fail in production.

### Dimension 2: ML Infrastructure

| Capability | Minimum for Production | Without It |
|---|---|---|
| Model registry | MLflow or equivalent | Cannot track which model is deployed, roll back, or audit |
| Feature store | Feast or equivalent | Features re-engineered each time, inconsistent between training and inference |
| Monitoring | Prediction drift + data drift detection | Model degrades silently — no alert until users complain |
| CI/CD for models | Automated retraining + deployment pipeline | Manual deployment, no reproducibility |
| Serving infrastructure | Containerized API with autoscaling | Single-process prototype that crashes under load |

### Dimension 3: Team Capability

| AI Solution Type | Required Roles | Can Be Done By |
|---|---|---|
| Rules / classical ML rules | Data analyst + software engineer | In-house team with existing talent |
| Pre-trained model API integration | Software engineer + prompt engineer | In-house team with minimal ML experience |
| Fine-tuned model | ML engineer + data engineer | Team with ML experience + cloud budget for training |
| Custom model training | ML researcher + ML engineer + data engineer | Dedicated AI/ML team or external partner |
| Production LLM deployment | MLOps engineer + infrastructure engineer + ML engineer | Cross-functional team, significant investment |

### Dimension 4: Compliance & Governance

| Requirement | Impact on AI Viability |
|---|---|
| **Explainability required** (regulated industry) | Prefer classical ML (SHAP) over deep learning or LLMs |
| **Data cannot leave premises** | Self-hosted models only — API-based AI may be blocked |
| **Audit trail required** | Every AI decision must be logged with model version, input, and confidence |
| **Bias monitoring required** | Classification models need demographic parity testing |
| **SLA for accuracy** | AI must have fallback to rules when confidence is low |

### Readiness Scoring

| Dimension | Weak (0) | Moderate (1) | Strong (2) |
|---|---|---|---|
| Data maturity | L1 or below | L2 | L3 or L4 |
| ML infrastructure | None | Basic (model registry) | Full (CI/CD + monitoring + feature store) |
| Team capability | No ML experience | Can integrate APIs | Can train and deploy custom models |
| Compliance readiness | No governance in place | Manual audit process | Automated compliance + monitoring |

| Total Score | Recommended Approach |
|---|---|
| 6–8 | Build custom AI solution in-house |
| 3–5 | Use managed AI services (APIs, pre-built models) or hybrid |
| 0–2 | Buy a packaged solution or improve readiness first |

---

## 8. Cost-Benefit Analysis Framework

### Cost Dimensions

| Cost Type | What It Includes | Typical Range |
|---|---|---|
| **Build** | Engineering hours, model training compute, data labeling | $20K–$500K+ |
| **Inference** | Per-request API cost or self-hosted GPU cost | $0.001–$0.10 per request |
| **Maintenance** | Model retraining, monitoring, drift detection, prompt updates | 15–30% of build cost annually |
| **Compliance** | Audit logging, explainability tooling, bias monitoring | $10K–$50K/year |
| **Risk** | Cost of errors (false positives, false negatives, hallucination) | Depends on domain |

### Benefit Dimensions

| Benefit Type | How to Quantify |
|---|---|
| **Cost reduction** | Hours saved × hourly rate |
| **Revenue increase** | Conversion rate improvement × average order value × volume |
| **Risk reduction** | Errors avoided × cost per error |
| **Speed improvement** | Days saved × cost of delay per day |
| **Quality improvement** | Customer satisfaction score improvement × customer lifetime value |

### ROI Calculation

```
ROI = (Annual Benefit − Annual Cost) / Build Cost

Where:
  Annual Cost = Inference Cost + Maintenance Cost + Compliance Cost + (Error Rate × Risk Cost)
  Annual Benefit = Cost Reduction + Revenue Increase + Risk Reduction
```

### ROI Thresholds

| ROI | Verdict |
|---|---|
| >100% | Strong justification — proceed to solution scoping |
| 50–100% | Justified if strategic value exists beyond direct ROI |
| 0–50% | Consider postponing or using simpler approach |
| Negative | Do not proceed — the numbers do not support AI |

### Example: Insurance Claims AI (Entry #51)

| Cost Factor | Value |
|---|---|
| Build cost | 20 weeks × team of 4 × $150/h = **$480K** |
| Inference cost | 10K claims/month × $0.05/claim × 12 = **$6K/year** |
| Maintenance cost | 20% of build = **$96K/year** |
| Compliance cost | Audit trail, explainability, state DOI filing = **$40K/year** |
| **Total annual cost** | **$142K/year** |

| Benefit Factor | Value |
|---|---|
| Adjuster time saved | 15 more claims/day × 50 adjusters × $40/h × 260 days = **$780K/year** |
| Float cost reduction | 11 days faster × $2M/month float × 5% interest = **$132K/year** |
| Fraud detection improvement | 15% more fraud caught × 200 fraudulent claims × $5K avg = **$150K/year** |
| **Total annual benefit** | **$1.06M/year** |

**ROI = ($1.06M − $142K) / $480K = 191%** — Strong justification.

---

## 9. Decision Flowchart

```mermaid
flowchart TD
    A[Business Problem Identified] --> B[Decompose into atomic sub-problems]
    B --> C[For each sub-problem]
    C --> D[Can this be solved with<br>rules / formulas / lookup?]
    D -->|Yes| E[Implement rules. Done.]
    D -->|No| F[Does the problem involve<br>unstructured data / ambiguity?]
    F -->|No| G[Can classical ML solve it<br>(tabular data, <10K examples)?]
    F -->|Yes| H[Run AI Suitability Test]
    G -->|Yes| H
    G -->|No| I[Consider if problem is<br>well-defined enough for AI]
    I -->|Yes| H
    I -->|No| J[Simplify or redefine<br>the problem scope]
    J --> B

    H --> K{AI Suitability Score}
    K -->|8-10: Strong| L[Assess organizational readiness]
    K -->|5-7: Moderate| M[Consider hybrid approach]
    K -->|0-4: Weak| N[Use non-AI approach]

    M --> O[Identify which sub-problems<br>need AI vs. rules]
    O --> L

    L --> P{Readiness Score}
    P -->|6-8: Strong| Q[Full custom AI solution]
    P -->|3-5: Moderate| R[Managed AI service / API]
    P -->|0-2: Weak| S[Improve readiness first<br>or buy packaged solution]

    Q --> T[Run Cost-Benefit Analysis]
    R --> T
    S --> U[Create readiness roadmap;<br>revisit in 6 months]

    T --> V{ROI > 50%?}
    V -->|Yes| W[Proceed to Solution Scoping<br>→ ai-solution-scoping-examples.md]
    V -->|No| X[Explore cheaper approaches<br>or deprioritize]

    M -.-> Y[Hybrid Example: Claims AI<br>Rules for doc classification,<br>AI for extraction+fraud+settlement]
    R -.-> Z[Managed Example: FactoryRL<br>Rules for physics model,<br>self-hosted ML for optimization]
```

---

## 10. Worked Examples

### Example 1: Insurance Claims Processing (Entry #51 — AI Win)

**Problem**: Claims take 14 days to process. Manual document handling, data entry, fraud checks, and settlement.

**Decomposition results**: 5 sub-problems — 1 can use rules (document classification), 4 need AI (extraction, damage assessment, fraud detection, settlement).

**AI Suitability Test**: Score = 9/10
- Q1: Nuance needed? Yes (handwriting, varied form layouts) = +2
- Q2: Sufficient data? Yes (10K+ historical claims with outcomes) = +2
- Q3: Error tolerance? Yes (human adjuster reviews all AI outputs) = +2
- Q4: Cost benefit? Yes (saves $1.06M/year vs $142K/year cost) = +2
- Q5: Simpler path? No (rules cannot handle form variety or fraud patterns) = +1

**Readiness**: Data at L2 (centralized but not fully labeled for ML). Team can integrate APIs but not train custom models initially.

**Approach**: Phased — start with pre-trained OCR + LLM API (Phase 1–2), build custom fraud model with accumulated data (Phase 5).

**Archetypes**: Extraction (documents), Classification (damage severity), Anomaly Detection (fraud), Generation (settlement reasoning).

**ROI**: 191% — proceed to scoping.

**Outcome**: See ClaimPulse design (`projects/industry-solutions/insurance/claimpulse/design.md`).

---

### Example 2: Employee Vacation Balance Checker (Non-AI Win)

**Problem**: HR receives 200 emails/day asking "How many vacation days do I have left?" Each takes 5 minutes to look up and reply.

**Decomposition results**: 1 sub-problem — read balance from HR system, format reply.

**AI Suitability Test**: Score = 2/10
- Q1: Nuance needed? No (fixed query, structured data, known system) = 0
- Q2: Sufficient data? N/A (no model needed) = 0
- Q3: Error tolerance? No (balance must be 100% accurate) = 0
- Q4: Cost benefit? Building a self-service lookup costs $2K (dashboard). AI chatbot costs $20K + $0.10/query. = +1 if volume is high enough
- Q5: Simpler path? Yes — a self-service portal with the HR system takes 2 days to build = 0

**Simplest viable path**: A self-service web page that queries the HR database directly. Cost: $2K one-time, near-zero per-query. Solves 100% of the problem with 100% accuracy.

**Outcome**: Build the self-service portal. Do not use AI.

---

### Example 3: Customer Support Ticket Routing (Hybrid — Rules + AI)

**Problem**: 50K support tickets/month arrive via email. Currently manually triaged to 15 teams. Average triage time: 4 hours.

**Decomposition results**:

| Step | Input | Simplest Approach | Decision |
|---|---|---|---|
| 1. Language detection | Email text | Rules check Unicode ranges | L1 — rules (98% accurate) |
| 2. Intent classification | Email text | LLM or classical ML | **AI needed** — 15 categories with subtle differences |
| 3. Priority assignment | Email text + customer tier | Rules based on keywords + tier | L1 — rules ("urgent" + enterprise = P1) |
| 4. Team routing | Intent label + priority | Direct lookup table | L1 — lookup |

**AI Suitability Test** (for step 2 only): Score = 8/10
- Q1: Nuance needed? Yes ("I can't log in" vs "the system is slow" — both technical but different teams) = +2
- Q2: Sufficient data? 50K/month × 6 months = 300K labeled tickets = +2
- Q3: Error tolerance? Yes (routing errors are caught by the receiving team and re-routed) = +2
- Q4: Cost benefit? 4h → 2min triage = 500h/month saved × $30/h = $180K/year vs $12K/year AI cost = +2
- Q5: Simpler path? Keyword-based routing misses 30% of edge cases = 0

**Approach**: Rules for language detection + priority. Classical ML (naive Bayes or small transformer) for intent classification. Lookup table for team routing.

**Outcome**: 30-minute implementation of the rules part, 2-week ML model training for the classification part. 95% routing accuracy, 2-minute average triage time.

---

### Example 4: Factory Energy Optimization (Entry #27 — Hybrid: Physics + ML)

**Problem**: Factory energy consumption 20% above benchmark. HVAC and production scheduling are managed independently.

**Decomposition results**: See Section 4 earlier in this document.

**AI Suitability Test**: Score = 7/10
- Q1: Nuance needed? Partial (temperature dynamics are physics, but optimal setpoints depend on complex trade-offs) = +1
- Q2: Sufficient data? Yes (30 days of BMS + production data available) = +2
- Q3: Error tolerance? Partial (temperature violations must be 100% avoided; energy savings can be approximate) = +1
- Q4: Cost benefit? 20% energy reduction × $500K/month bill = $1.2M/year savings vs $300K build + $30K/year = +2
- Q5: Simpler path? PID controls exist but cannot optimize across HVAC + production = +1

**Approach**: Physics formula for temperature dynamics (L2), LightGBM for learned optimization (L3), SLSQP for constrained optimization (L3). No deep learning or LLM needed.

**Outcome**: See FactoryRL design (`projects/industry-solutions/manufacturing-industrial/factoryrl/design.md`).

---

## 11. Anti-Patterns: When NOT to Use AI

### Anti-Pattern 1: The 100% Accuracy Requirement

"If this system makes one mistake, someone could die / lose money / sue us."

If you cannot tolerate errors and there is no human-in-loop, AI alone is not the answer. Use rules where possible, and AI only as an advisory layer with explicit override.

**Example**: Tax filing software. The IRS does not accept "the LLM thought this was the right amount." Tax calculations must be exact — this is a rules problem.

### Anti-Pattern 2: The Zero-Data Problem

"We want to use AI to predict customer churn, but we don't have any historical data on who churned."

AI cannot learn patterns from nothing. If you have no historical data, you cannot train a model. Options: collect data for 6 months first, use a heuristic rule instead, or use a pre-trained model zero-shot (rarely works for specific business predictions).

### Anti-Pattern 3: The Weekly-Changing Problem

"Our business rules change every month. We want AI to adapt automatically."

AI learns from data — if the underlying patterns are constantly shifting, the model will perpetually be trained on outdated data. This is called **concept drift** and is a known failure mode. If rules change that frequently, AI is not adaptive enough to keep up without constant retraining, which is more expensive than just updating rules.

### Anti-Pattern 4: The Black-Box Regulatory Requirement

"Regulations require us to explain every decision. We want to use a deep neural network to approve loans."

If explainability is legally mandated (ECOA for lending, GDPR for automated decisions), deep learning and LLMs create a compliance burden. Use classical ML (logistic regression or gradient-boosted trees with SHAP) where possible, or be prepared to build expensive explainability infrastructure.

### Anti-Pattern 5: The "Just Add AI" to a Broken Process

"Our customer onboarding process is broken — people can't find the right forms, they get stuck, and support is overwhelmed. Let's add a chatbot."

If the underlying process is broken, adding AI on top will make it worse — the AI will confidently give wrong answers based on broken process logic. Fix the process first, then evaluate whether AI adds value on top of the fixed process.

### Anti-Pattern 6: The Single-Point-of-Failure AI

"Let's use AI for everything — log analysis, ticket routing, knowledge base search, performance prediction, and even writing code reviews."

AI introduces single points of failure in unpredictable ways. A single drift event can degrade all AI components simultaneously. Use AI only where it adds clear value, and maintain non-AI fallbacks for critical paths.

---

## 12. Reusable Analysis Template

Copy this template for each business problem:

```markdown
## Problem Analysis

### 1. Problem Definition
- **Problem Name**:
- **Business Context** (who, when, how often):
- **Current State** (how solved today):
- **Pain Point** (quantified):
- **Success Criteria** (measurable):

### 2. Decomposition

| Step | Input | Transformation | Output | Simplest Approach | AI Needed? |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |

### 3. AI Suitability Test
- Q1 (Nuance needed?): Score ___
- Q2 (Sufficient data?): Score ___
- Q3 (Error tolerance?): Score ___
- Q4 (Cost benefit?): Score ___
- Q5 (Simpler path?): Score ___
- **Total: ___ / 10**

### 4. Solution Archetype
- [ ] Classification / Extraction
- [ ] Generation / Summarization
- [ ] Prediction / Forecasting
- [ ] Recommendation / Ranking
- [ ] Optimization
- [ ] Anomaly Detection
- [ ] Conversation / QA

### 5. Readiness Assessment
- Data maturity (L1–L4):
- ML infrastructure (none/basic/full):
- Team capability:
- Compliance readiness:
- **Total readiness ___ / 8**

### 6. Cost-Benefit
- Build cost:
- Annual operating cost:
- Annual benefit:
- **ROI: ___ %**

### 7. Verdict
- [ ] Proceed to solution scoping (ROI > 50% + readiness > 3)
- [ ] Hybrid — AI for specific sub-problems only
- [ ] Defer — improve readiness first (readiness ≤ 3)
- [ ] Reject — simpler solution exists or ROI negative
```

---

## Summary: The Five-Step Process

```
Step 1: DECOMPOSE
  Break the problem into atomic sub-problems.
  For each: what is the input, transformation, output, and simplest approach?

Step 2: TEST
  Run the AI Suitability Test for each sub-problem.
  Score: 0–10. Below 5? Use rules/formulas. 5–7? Hybrid. 8+? AI candidate.

Step 3: ASSESS
  Evaluate organizational readiness: data, infra, team, compliance.
  Score: 0–8. Below 3? Improve readiness first. 3–5? Use managed AI. 6+? Build custom.

Step 4: QUANTIFY
  Calculate build cost, annual operating cost, and annual benefit.
  ROI > 50%? Proceed. ROI negative? Reconsider.

Step 5: SCOPE
  Map to a solution archetype.
  Proceed to ai-solution-scoping-examples.md for concrete examples of how similar
  problems were scoped, then to ai-sdlc-layers-summary.md for the build phase.
```

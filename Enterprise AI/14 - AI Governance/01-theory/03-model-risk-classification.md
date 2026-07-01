# Model Risk Classification

## Purpose

Model risk classification tiers models based on potential impact, enabling proportional governance. Low-risk models get lightweight oversight; high-risk models require rigorous controls.

## Risk Classification Framework

### Dimensions of Risk

| Dimension | Low Risk | Medium Risk | High Risk | Critical Risk |
|-----------|----------|-------------|-----------|---------------|
| User impact | No direct user interaction | Informational outputs | Decisions affecting users | Life-altering decisions |
| Data sensitivity | Public data | Internal data | PII/sensitive data | Highly regulated data |
| Autonomy | Human-in-the-loop | Human-on-the-loop | Automated decisions | Fully autonomous |
| Scale | Internal tool, <100 users | Departmental, <1000 users | Enterprise, <100K users | Public-facing, millions |
| Failure impact | Minor inconvenience | Operational disruption | Financial/legal harm | Physical harm, loss of life |

### Classification Tiers

#### Tier 4: Critical
- **Definition**: Systems whose failure could cause physical harm, large-scale financial loss, or significant legal liability
- **Examples**: Autonomous vehicles, medical diagnosis, credit scoring, criminal justice tools
- **Requirements**: Full risk assessment, external audit, regulatory filing, continuous monitoring, human oversight

#### Tier 3: High
- **Definition**: Systems that make decisions with meaningful impact on individuals or operations
- **Examples**: Hiring tools, loan origination, insurance pricing, content moderation
- **Requirements**: Risk assessment, bias audit, explainability, human review provision, regular monitoring

#### Tier 2: Medium
- **Definition**: Systems that produce outputs affecting users but with limited autonomy
- **Examples**: Chatbots, recommendation systems, summarization tools
- **Requirements**: Documentation, basic bias checks, transparency notice, periodic review

#### Tier 1: Low
- **Definition**: Internal tools with limited scope and no direct user impact
- **Examples**: Internal search, code completion, data extraction
- **Requirements**: Basic documentation, standard approval

## Classification Process

### Initial Assessment
```
1. Identify system purpose and scope
2. Assess each risk dimension
3. Calculate composite risk score
4. Assign initial tier
5. Approve tier assignment
```

### Periodic Review
- Tier 4: Quarterly review
- Tier 3: Semi-annual review
- Tier 2: Annual review
- Tier 1: Review on significant change

### Reclassification Triggers
- Change in system capability
- Change in deployment scope
- Regulatory change
- Incident or near-miss
- New use case or user population

## Governance Requirements by Tier

| Control | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---------|--------|--------|--------|--------|
| Model card | Yes | Yes | Yes | Yes |
| Risk assessment | No | Yes | Yes | Yes |
| Bias audit | No | Basic | Comprehensive | Comprehensive |
| External audit | No | No | Recommended | Required |
| Human oversight | No | Recommended | Required | Required |
| Explainability | No | Recommended | Required | Required |
| Continuous monitoring | No | Basic | Full | Full |
| Incident response plan | No | Recommended | Required | Required |
| Regulatory filing | No | No | As needed | Required |
| Fairness metrics | No | No | Yes | Yes |

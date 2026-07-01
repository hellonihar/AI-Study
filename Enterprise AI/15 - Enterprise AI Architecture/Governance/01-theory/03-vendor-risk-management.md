# Vendor Risk Management

## Third-Party AI Risk

Using external AI models introduces risks not present in self-hosted systems:

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data leakage | Training data exposed to vendor | Data processing agreement, opt-out of training |
| Service dependency | Outage blocks your product | Multi-provider fallback, cached responses |
| Model behavior change | Quality degradation without notice | Version pinning, regression testing |
| Pricing changes | Unexpected cost increases | Long-term contracts, budget buffer |
| Deprecation | Required migration | Maintain alternative provider readiness |

## Vendor Assessment Process

1. **Security review** — SOC 2, ISO 27001, penetration test results
2. **Data handling review** — Where is data stored? Is it used for training?
3. **Reliability review** — Uptime history, incident response, degradation patterns
4. **Legal review** — Contract terms, SLA, liability, termination rights
5. **Technical review** — API compatibility, latency, rate limits
6. **Ongoing monitoring** — Usage, cost, quality, reliability trends

## Contractual Safeguards

| Clause | Protection |
|--------|-----------|
| Data processing agreement | Defines data handling, security, purpose limitation |
| No training on your data | Prohibits vendor from using your data for model improvement |
| SLA guarantees | Minimum uptime, maximum latency, with credits |
| Termination for cause | Right to terminate if SLA breaches or security incidents |
| Migration assistance | Vendor provides data export and transition support |

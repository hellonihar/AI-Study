# Vendor Selection Best Practices

## Evaluation Process

1. **Define requirements** — What tasks, volume, latency, data sensitivity?
2. **Shortlist** — 3-5 vendors that meet basic requirements
3. **POC** — Run 50-100 representative tasks through each vendor
4. **Score** — Weighted scorecard across quality, cost, reliability
5. **Fallback** — Always have at least one alternative provider
6. **Contract** — Negotiate volume discounts, SLA guarantees

## Key Considerations

| Factor | Minimum Requirement |
|--------|-------------------|
| Uptime SLA | > 99.9% |
| Latency p95 | < 2s for interactive, < 10s for batch |
| Data handling | No training on your data (opt-out available) |
| Certifications | SOC 2, ISO 27001 (minimum) |
| Support | 24/7 for production, < 4h response |
| Rate limits | 2x your peak expected volume |

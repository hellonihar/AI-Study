# Vendor Strategy Best Practices

## Multi-Provider Strategy

### Why Multiple Providers?
| Reason | Impact |
|--------|--------|
| Pricing changes | Switch providers when costs change 20%+ |
| Capability gaps | One provider excels at code, another at reasoning |
| Outage protection | No single point of failure |
| Negotiation leverage | Ability to walk away from any provider |
| Regional requirements | Data residency, latency per region |

### Recommended Minimum
- **Primary**: One capable provider (OpenAI, Anthropic)
- **Secondary**: One alternative (Google, Cohere, Mistral)
- **Tertiary**: Local fallback (Llama 3, Mistral via vLLM)

## Provider Evaluation Criteria

| Criterion | Weight | How to Evaluate |
|-----------|--------|-----------------|
| Quality on your tasks | 35% | Side-by-side eval on 200 representative queries |
| Cost per token | 20% | Total cost at projected volume |
| Latency (p50/p95) | 15% | Measure over 1,000 requests |
| Availability SLA | 10% | Historical uptime (check status pages) |
| Rate limits | 10% | Limits at your expected peak traffic |
| Feature set | 10% | Streaming, tool calling, vision, structured output |

## Migration Checklist

1. **Wrap**: Add abstraction layer (no behavior change)
2. **Shadow**: Run new provider in parallel for 1 week
3. **Compare**: Evaluate quality, cost, latency differences
4. **Canary**: Route 5% → 25% → 50% → 100%
5. **Monitor**: Watch error rates, latency, cost for regression
6. **Retire**: Keep old provider as fallback for 2 weeks

## Cost Optimization

- Use cheaper models for 80% of traffic (classify by complexity)
- Batch non-urgent requests during off-peak pricing windows
- Cache aggressively (60%+ hit rate achievable)
- Negotiate volume discounts at $10K+/month spend

## Regional Strategy

| Region | Primary Provider | Rationale |
|--------|-----------------|-----------|
| US | OpenAI / Anthropic | Best quality, lowest latency |
| Europe | Anthropic / Mistral | Data residency (GDPR), French provider options |
| Asia | OpenAI / Local | Latency proximity, regional availability |
| Air-gapped | Llama 3 / Mistral | Must run on-premise |

## Lock-In Mitigation

- Never use provider-specific features as core architecture (e.g., OpenAI assistants API)
- Always implement the abstraction layer before going to production
- Store prompts and configurations provider-agnostic
- Regularly test the fallback provider to ensure it still works

## Contractual Considerations

- Month-to-month vs. annual: Start monthly, negotiate annual at $10K+/month
- Rate limit guarantees: Ensure SLAs match your peak needs
- Data privacy: Confirm your data is not used for training
- Support SLA: Response times for critical incidents
- Exit clause: Data export, migration assistance, notice period

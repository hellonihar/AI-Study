# Build vs. Buy Analysis

## Decision Framework

| Factor | Favor Build | Favor Buy |
|--------|-------------|-----------|
| Core differentiator | Yes | No |
| Existing expertise | Strong team | No internal capability |
| Time to market | Can wait | Need now |
| Data sensitivity | High (cannot share) | Low |
| Customization need | High | Standard use case |
| Volume | > 10M req/mo | < 1M req/mo |
| Control requirements | Full control needed | SLA acceptable |

## Build Scenarios

### When to Build
- **Core product differentiator**: AI is your product's primary value
- **Data sensitivity**: Cannot send data to third-party APIs
- **Customization**: Need fine-grained control over model behavior
- **Scale**: Volume justifies infrastructure investment
- **Talent**: Existing ML engineering team

### Build Costs

| Phase | Cost Range | Duration |
|-------|-----------|----------|
| Infrastructure setup | $50-200K | 2-4 weeks |
| Model selection and eval | $20-50K | 2-4 weeks |
| Serving pipeline | $50-100K | 4-8 weeks |
| Monitoring and ops | $30-80K | 2-4 weeks |
| Ongoing operations | $10-30K/mo | Continuous |

## Buy Scenarios

### When to Buy
- **Speed to market**: Need AI capability now
- **Commodity use case**: Standard functionality (chat, summarization)
- **Low volume**: Cannot justify infrastructure investment
- **Talent gap**: No ML engineering team

### Buy Costs

| Provider | Model | Cost/1K Tokens (Input) | Cost/1K Tokens (Output) |
|----------|-------|----------------------|-----------------------|
| OpenAI | GPT-4o-mini | $0.00015 | $0.0006 |
| OpenAI | GPT-4o | $0.01 | $0.03 |
| Anthropic | Claude 3 Sonnet | $0.003 | $0.015 |
| Anthropic | Claude 3 Haiku | $0.00025 | $0.00125 |
| Google | Gemini 1.5 Pro | $0.0035 | $0.0105 |

## Hybrid Approach

Best for most enterprises: start with APIs, build for critical paths:

1. **Phase 1**: Use managed APIs for all inference
2. **Phase 2**: Build serving for high-volume, stable paths
3. **Phase 3**: Migrate sensitive workloads to self-hosted
4. **Phase 4**: Optimize with routing (cheap model for simple, expensive for complex)

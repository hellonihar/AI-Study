# Vendor Abstraction

## Motivation

Relying on a single LLM provider creates lock-in risk: pricing changes, capability regressions, outages, or deprecation of models you depend on. A vendor abstraction layer lets you switch providers without rewriting your application.

## Abstraction Pattern

```
Application Code
      ↕
  AIModel Interface
  ┌─────┼─────┐
  │     │     │
OpenAI  Claude  Local
Adapter Adapter Adapter
```

### The Interface

```python
class AIModel(ABC):
    def generate(self, messages: list[dict], **kwargs) -> Response: ...
    def stream(self, messages: list[dict], **kwargs) -> StreamResponse: ...
    def count_tokens(self, text: str) -> int: ...
```

Each provider implements this interface with its own SDK.

## Provider Selection Strategies

### Static Configuration
Set `DEFAULT_MODEL = "gpt-4o-mini"` in config. Change a config value to switch providers.

### Dynamic Routing
Route based on query characteristics:

```
Complex reasoning → {"provider": "openai", "model": "gpt-4o"}
Simple Q&A       → {"provider": "anthropic", "model": "claude-3-haiku"}
Code generation  → {"provider": "openai", "model": "gpt-4o"}
Low-cost bulk    → {"provider": "local", "model": "llama-3-8b"}
```

### Multi-Provider Load Balancing
Round-robin between equally capable models across providers. Reduces per-request latency by using the least-loaded provider.

## Cost Tracking Per Provider

```python
class UsageTracker:
    def track(self, provider: str, model: str,
              input_tokens: int, output_tokens: int):
        cost = PRICING[provider][model] * (input_tokens + output_tokens)
        self.daily_costs[provider] += cost
```

Monitor monthly costs per provider. Alert on cost spikes or anomalous pricing changes.

## Graceful Degradation

```python
for provider in ["openai", "anthropic", "local"]:
    try:
        return await get_provider(provider).generate(prompt)
    except ProviderError:
        logger.warning(f"Provider {provider} failed, trying next")
        continue
return fallback_response()  # all providers down
```

## Migration Playbook

1. **Wrap**: Add abstraction layer behind existing API calls (no behavior change)
2. **Shadow**: Run new provider in parallel, compare outputs, no user-facing change
3. **Canary**: Route 5% of traffic to new provider, monitor quality + cost
4. **Migrate**: Ramp traffic gradually while monitoring regression metrics
5. **Retire**: Remove old provider after validation period (1–2 weeks)

## When NOT to Abstract

- You're prototyping (move fast, pick one provider)
- You have a deep integration with one provider's unique features (e.g., Claude Artifacts)
- The abstraction cost (development + testing) exceeds expected switching benefit
- You're using a single model for < $500/month (switching cost > potential savings)

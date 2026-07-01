# Cost-Aware Prompting

Optimizing prompt design to minimize token usage without sacrificing quality.

## Where the Cost Goes

| Component | Typical Token Share | Optimization Lever |
|---|---|---|
| System prompt | 5–15% | Trim instructions, remove redundancy |
| Few-shot examples | 15–40% | Reduce count, shorten examples |
| Retrieved context | 30–50% | Fewer chunks, shorter chunks |
| Conversation history | 10–25% | Summarization, sliding window |
| User input | 2–10% | Minimal — don't modify |
| Model output | 10–20% | Set max_tokens, prefer shorter answers |

## Prompt Trimming

| Before | After | Savings |
|---|---|---|
| "You are a helpful, knowledgeable, and friendly AI assistant..." | "You are a helpful assistant." | ~30 tokens |
| "Please respond in a concise manner, keeping your answer brief and to the point, avoiding unnecessary elaboration." | "Answer concisely." | ~20 tokens |
| "If you don't know the answer, just say you don't know rather than making something up." | "Say 'I don't know' if unsure." | ~15 tokens |

## Few-Shot Optimization

- **Shorten examples.** Replace long explanations with minimal demonstrations.
- **Remove redundant examples.** If 2 examples cover the same pattern, keep 1.
- **Use the smallest effective set.** Start with 0, add examples one at a time until quality plateaus.

## Context Trimming

- **Re-rank before injecting.** Retrieve top-20, re-rank, inject top-3.
- **Shorter chunks.** 256-token chunks instead of 512 — often sufficient for retrieval.
- **Strip metadata.** Remove chunk headers/footers that add context.
- **Cache frequent contexts.** Many queries share the same retrieved documents.

## Prefix Caching

If the system prompt + context are shared across requests, prefix caching can save 40–60% of input tokens:

```python
# Shared prefix (cached)
system = "You are a financial analyst..."
company_context = "Apple Inc. (AAPL) is..."

# Per-request suffix (not cached)
question = "What was Q3 revenue?"
```

Enable prefix caching:
- **vLLM:** `--enable-prefix-caching`
- **OpenAI:** Automatic for repeated prefixes
- **Anthropic:** `cache_control` parameter on system messages

## Cost Tracking by Component

```python
def trace_prompt_cost(prompt, response, model_pricing):
    costs = {
        "system": count_tokens(prompt["system"]) * model_pricing["input"],
        "context": count_tokens(prompt["context"]) * model_pricing["input"],
        "examples": count_tokens(prompt["examples"]) * model_pricing["input"],
        "user": count_tokens(prompt["user"]) * model_pricing["input"],
        "response": count_tokens(response) * model_pricing["output"],
    }
    return costs
```

## Cost Budgeting

Set per-request and per-user budgets:

```
Per-request budget: $0.01
├── Input tokens: 2000 × $0.0000015 = $0.003
├── Output tokens: 500 × $0.000006 = $0.003
└── Total: $0.006 (within budget)

Daily user budget: $0.50 → 50–80 requests per user per day
```

## Best Practices

- **Measure token usage per component.** You can't optimize what you don't measure.
- **Start with minimal prompts.** Add tokens only when quality measurement justifies the cost.
- **Audit quarterly.** Prompt creep (gradual addition of unnecessary tokens) can double costs in 6 months.
- **Use cheaper models for non-critical paths.** A classifier routing to GPT-4o-mini costs 10× less than using GPT-4o for every request.
- **Set `max_tokens` per use case.** Don't let the model default to verbose output if shorter answers suffice.

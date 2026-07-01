# Sampling Strategies

Sampling converts logits (raw scores) into the next token. It determines the creativity, diversity, and quality of generated text.

## The Logit Pipeline

```
Logits (vocab_size,) → [Scale by Temperature] → [Apply Top-K / Top-P Mask] → [Softmax] → [Sample]
```

## Strategies

| Strategy | Description | When to Use |
|---|---|---|
| **Greedy** | Always pick argmax token. Deterministic. | Factual answers, code generation, classification |
| **Temperature** | Scale logits: `logits / T`. Higher T = more uniform distribution. | T=0.1 for factual, T=0.7 for creative, T=1.5+ for brainstorming |
| **Top-K** | Sample only from the K highest probability tokens. | K=50 for creative. Prevents rare token sampling. |
| **Top-P (nucleus)** | Sample from the smallest set of tokens whose cumulative probability ≥ P. | P=0.9 balances diversity and coherence. |
| **Min-P** | Sample from tokens with probability ≥ min_p × probability of top token. | Min-p=0.1. Better than top-p for low-temperature settings. |
| **Repetition penalty** | Scale down logits of previously generated tokens. | Penalty 1.05–1.2 for reducing loops. |
| **Typical sampling** | Sample tokens with entropy close to expected entropy. | Produces more "typical" human-like text. |

## Recommended Configurations

| Use Case | Temp | Top-P | Top-K | Min-P | Rep. Penalty |
|---|---|---|---|---|---|
| Factual QA | 0.0 | — | — | — | — |
| Code generation | 0.1–0.3 | 0.9 | — | — | 1.0 |
| Translation | 0.3 | 0.9 | — | — | 1.0 |
| Creative writing | 0.7–0.9 | 0.95 | 50 | — | 1.1 |
| Brainstorming | 1.2–1.5 | 0.95 | 100 | — | 1.0 |
| Chain-of-thought | 0.5 | 0.9 | — | — | 1.0 |

## Sampling in Production

- **Use greedy or low-temperature for structured outputs** (JSON, tool calls). Higher temperature will break formatting.
- **Min-p is the current best practice** for general generation — it adapts dynamically to the model's confidence.
- **Repetition penalty is a band-aid** — if the model loops, consider better prompting or fine-tuning instead of cranking the penalty.

## Code

```python
import torch

def sample(logits, temperature=1.0, top_k=0, top_p=0.9):
    logits = logits / temperature
    if top_k > 0:
        indices = torch.topk(logits, top_k).indices
        mask = torch.full_like(logits, float('-inf'))
        mask.scatter_(0, indices, logits[indices])
        logits = mask
    if top_p < 1.0:
        probs = torch.softmax(logits, dim=-1)
        sorted_probs, sorted_indices = torch.sort(probs, descending=True)
        cumulative = torch.cumsum(sorted_probs, dim=-1)
        mask = cumulative > top_p
        mask[..., 1:] = mask[..., :-1].clone()
        mask[..., 0] = False
        logits[sorted_indices[mask]] = float('-inf')
    probs = torch.softmax(logits, dim=-1)
    return torch.multinomial(probs, 1)
```

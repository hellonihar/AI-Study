# Model Selection

Choosing the right model size and family for your workload.

## The Cost-Quality Trade-off

| Model Size | Relative Cost | Quality vs 7B | Use Case |
|---|---|---|---|
| < 1B | 0.05× | -15–25% | Classification, simple extraction, routing |
| 7B | 1× | Baseline | RAG, summarization, chat, code gen |
| 13B | 2× | +2–5% | Complex reasoning, multi-step tasks |
| 34B | 5× | +3–8% | Domain expert, high-stakes reasoning |
| 70B | 10× | +5–10% | Best quality, math, code, nuanced tasks |
| 200B+ | 30× | +6–12% | Frontier research, distillation teacher |

**Key insight:** A well-prompted 7B model often matches a raw 70B on specific tasks. Always benchmark before scaling up.

## Selection Framework

```
                                  ┌─────────────────┐
                                  │  Task requires  │
                                  │  complex multi-  │
                                  │  step reasoning? │
                                  └────────┬────────┘
                                           │
                      ┌────────────────────┼────────────────────┐
                      Yes                  │                    No
                      ▼                    │                    ▼
              ┌──────────────┐             │            ┌──────────────┐
              │ Latency SLA  │             │            │  7B model    │
              │ < 1 second?  │             │            │  (LLaMA-3-7B,│
              └──────┬───────┘             │            │   Mistral)   │
                     │                     │            └──────────────┘
            ┌────────┴────────┐            │
            Yes               No           │
            ▼                 ▼            │
    ┌──────────────┐  ┌──────────────┐     │
    │ 7B + CoT +   │  │ 70B or GPT-4 │     │
    │ self-consist. │  │ (if budget   │     │
    │ (inference   │  │  allows)     │     │
    │  scaling)    │  └──────────────┘     │
    └──────────────┘                       │
                                           │
                          ┌────────────────┴───────────────┐
                          │  Consider fine-tuned 7B before │
                          │  jumping to 70B — often matches│
                          │  at 1/10th the cost            │
                          └────────────────────────────────┘
```

## Model Families (as of 2026)

| Family | Strengths | Best For |
|---|---|---|
| **LLaMA-3** | Strong all-rounder, large vocab (128K), efficient tokenization | General purpose, English tasks |
| **Mistral** | Efficient, strong at small sizes, 32K context native | RAG, moderate reasoning |
| **Qwen-2.5** | Excellent math/coding, strong in Chinese+English | Code, math, bilingual |
| **Gemma-2** | Good quality for size, efficient | Mobile/edge, quick experimentation |
| **GPT-4o** | Best overall quality, multimodal | Complex reasoning, vision tasks |
| **Claude-3.5** | Strong safety, long context (200K) | Document analysis, safe outputs |

## Decision Rules

1. **Start with the smallest model** that can do the task (even GPT-4o-mini).
2. **Benchmark on your specific task**, not general benchmarks.
3. **Apply inference scaling** (CoT, self-consistency) before model scaling.
4. **Fine-tune a 7B before renting 70B API calls** — often matches at 1/10th cost.
5. **Monitor cost per good response**, not just quality — a 70B that's 5% better but 10× more expensive may not be worth it.

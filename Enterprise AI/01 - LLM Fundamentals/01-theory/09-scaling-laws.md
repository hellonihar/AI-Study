# Scaling Laws

Scaling laws describe how model performance improves with more parameters, data, and compute.

## Kaplan et al. (2020) — "Scaling Laws for Neural Language Models"

Key findings:
- **Loss scales as a power-law** with parameters, data, and compute — no diminishing returns within the studied range.
- **Model size dominates:** doubling parameters reduces loss more than doubling data (at the time).
- **Compute-optimal:** For a given compute budget, models should be 2–3× larger than existing practice at the time.

## Chinchilla (Hoffmann et al., 2022) — Rewriting the Rules

Key finding:
- **Previous models were undertrained.** For compute-optimal training, scale model and data proportionally:
  - **Tokens should be ~20× parameters.** A 7B model needs 140B tokens.
  - Most existing models (GPT-3: 175B params, 300B tokens → ratio 1.7×) were **data-constrained**.

| Model | Params | Training Tokens | Ratio | Chinchilla-optimal? |
|---|---|---|---|---|
| GPT-3 | 175B | 300B | 1.7× | No (under-trained) |
| LLaMA-1-65B | 65B | 1.4T | 21.5× | Close |
| LLaMA-3-70B | 70B | 15T | 214× | Over-trained (but better) |
| Chinchilla | 70B | 1.4T | 20× | Yes |

## Post-Chinchilla Findings

- **Over-training beyond 20× helps** — LLaMA-3 showed continued improvement at 214× ratio, though with diminishing returns.
- **Data quality > data quantity** — repeating high-quality data 4× outperforms fresh low-quality data (Muennighoff et al., 2023).
- **Inference scaling:** At inference time, spending more compute (chain-of-thought, ensembling, multi-step refinement) follows similar power-laws.
- **Emergent abilities:** Some capabilities (math, multi-step reasoning) appear only above certain model sizes — but recent research suggests these are measurement artifacts of discontinuous metrics.

## Practical Implications

- **For training:** Plan for token:param ratio of 20:1 minimum. If compute-limited, prioritize data quality.
- **For inference:** Smaller models with more inference-time compute (CoT, self-consistency) can match larger models at lower total cost.
- **For deployment:** A 70B model costs ~10× more than a 7B model but may only be 2–5% better on your task. Benchmark the actual task, not perplexity.

## Best Practices

- **Never train a model without first running a scaling law study** on small proxies (1M → 10M → 100M params).
- **Use inference scaling** (CoT, ensembling) to bridge small-model gaps before committing to larger models.
- **Track data quality at scale** — a single contaminated sample in 1T tokens can measurably benchmark performance.

# Chain-of-Thought Prompting

Chain-of-thought (CoT) elicits step-by-step reasoning before producing the final answer. It is the single most impactful prompting technique for complex reasoning tasks.

## Why CoT Works

- **Intermediate steps allocate more computation** to the reasoning path. Each token is another chance for the model to refine its thinking.
- **Branched reasoning:** If the first reasoning step is wrong, subsequent steps can correct it (self-correction through coherence).
- **Faithfulness:** CoT makes the reasoning process inspectable — you can see *why* the model gave a particular answer.

## Variants

| Variant | Description | Best For |
|---|---|---|
| **Zero-shot CoT** | Append "Let's think step by step." to any question. | Quick win, no examples needed. |
| **Few-shot CoT** | Provide 2–3 examples with explicit reasoning traces. | Higher quality than zero-shot, requires examples. |
| **Auto-CoT** | LLM generates its own CoT examples by clustering questions and prompting. | No manual example creation. |
| **CoT-SC (Self-Consistency)** | Sample K reasoning chains, pick most common answer. | Highest accuracy, 2–5× cost. |
| **Complexity-based CoT** | Prefer reasoning chains with more steps (they're more accurate). | When chain depth correlates with correctness. |

## Zero-Shot CoT

Simply append to any prompt:

```
User: "A bat and a ball cost $1.10. The bat costs $1.00 more than the ball.
How much does the ball cost? Let's think step by step."
```

Without CoT, GPT-3.5 answers "$0.10" (wrong). With CoT, it correctly reasons to "$0.05".

## Self-Consistency

```
                     ┌── Chain 1 → Answer A ──┐
                     ├── Chain 2 → Answer B ──┤
Question ────────────┼── Chain 3 → Answer A ──┼── Majority Vote → Final Answer
                     ├── Chain 4 → Answer A ──┤
                     └── Chain 5 → Answer C ──┘
```

- Sample 3–5 chains (temperature = 0.5–0.7).
- Marginal improvement diminishes after 5 chains.
- **Cost:** 3–5× more expensive per query.

## When CoT Hurts

| Task | CoT Effect | Reason |
|---|---|---|
| Simple factual QA | No improvement (sometimes worse) | Adds unnecessary tokens, dilutes confidence |
| Creative writing | Worsens quality | Over-analysis kills creativity |
| Classification | Minimal improvement | Labels don't benefit from intermediate reasoning |
| Extraction | Slightly worse | Model may hallucinate intermediate "facts" |

## Best Practices

- **Use CoT for math, logic, multi-step reasoning, and complex planning.**
- **Start with zero-shot CoT** ("Let's think step by step."). Add few-shot only if needed.
- **Use self-consistency for high-stakes tasks** (medical diagnosis, legal analysis, financial calculations).
- **Set temperature 0.3–0.7 for CoT chains** — too low = deterministic chains (defeats self-consistency), too high = incoherent chains.
- **Monitor chain length.** If CoT chains exceed 500 tokens, consider reducing complexity or using a larger model.

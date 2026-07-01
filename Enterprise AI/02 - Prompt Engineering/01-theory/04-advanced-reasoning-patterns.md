# Advanced Reasoning Patterns

Beyond linear CoT, structured reasoning patterns explore multiple paths, use tools, and self-correct.

## Tree-of-Thought (ToT)

Branches reasoning into multiple paths, evaluates each, and prunes unpromising ones.

```
                     ┌── Path A1 ──┬── Path A1a (score: 0.9)
Question ──┬── Step 1 ──┼── Path A2 ──┤
            │           └── Path A3 (score: 0.3) ← pruned
            └── Step 1b ──┬── Path B1 (score: 0.6)
                          └── Path B2 (score: 0.8)
```

- **Best for:** Puzzles, creative problem-solving, planning.
- **Cost:** 5–10× more than CoT.
- **Implementation:** Use BFS or DFS with an LLM judge evaluating node quality.

## Graph-of-Thought (GoT)

Like ToT but allows merging branches — reasoning paths can recombine.

- **Best for:** Tasks where insights from different approaches must be combined.
- **Cost:** 10–20× more than CoT (rarely worth it for most production tasks).

## ReAct (Reasoning + Acting)

Interleaves reasoning traces with tool calls:

```
Thought: I need to find the current stock price of AAPL.
Action: search_stock_price(AAPL)
Observation: $245.32
Thought: Now I can calculate the P/E ratio with the known earnings.
Action: calculate(245.32 / 6.82)
Observation: 35.97
Thought: The P/E ratio is approximately 36.
Final Answer: AAPL's P/E ratio is 35.97.
```

- **Best for:** Any task requiring up-to-date information or computation.
- **Pattern:** Thought → Action → Observation → (repeat) → Final Answer.

## Reflexion

Adds a self-evaluation step after each action:

```
Attempt 1: [Agent's action and result]
Evaluation: "Failed because the API returned a 401 error."
Feedback: "Check authentication headers before calling the API."
Attempt 2: [Corrected action]
```

- **Best for:** Coding, API interactions, multi-step tasks with error-prone steps.
- **Key insight:** The evaluation is done by the same LLM — no external judge needed.

## Self-Consistency (CoT-SC)

As covered in the CoT doc: sample K chains, majority vote on the final answer.

- **Best for:** Math, reasoning tasks with a single correct answer.
- **Cost:** K× the cost of a single CoT call.

## Stack-of-Thought (STaR)

Trains the model to generate its own reasoning traces. Used in fine-tuning, not prompting:

1. Prompt model to generate reasoning for a question.
2. If answer is correct, keep the reasoning trace.
3. If incorrect, provide the correct answer and ask the model to "explain backwards."
4. Fine-tune on all collected traces.

## When to Use Which

| Pattern | Accuracy Gain | Cost Multiplier | Use Case |
|---|---|---|---|
| Zero-shot CoT | +10–20% | 1.5–2× | Quick reasoning boost |
| Few-shot CoT | +15–30% | 1.5–3× | Complex reasoning with examples |
| Self-consistency | +20–40% | 3–5× | High-stakes math/logic |
| ReAct | +variable | 2–5× | Tool-using agents |
| Tree-of-Thought | +30–50% | 5–10× | Puzzles, planning |
| Reflexion | +10–25% | 2–3× | Coding, error-prone tasks |

## Best Practices

- **Start with zero-shot CoT.** Add complexity only when quality is insufficient.
- **Use self-consistency before ToT** — it's cheaper and often matches ToT on well-defined problems.
- **ReAct is the most production-useful advanced pattern** — it powers most agent frameworks.
- **Log the reasoning trace** in production — it's invaluable for debugging and quality monitoring.

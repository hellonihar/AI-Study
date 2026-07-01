# Prompt Optimization

Automated techniques for finding the best prompt without manual trial and error.

## Manual Optimization Problems

- **Expensive:** Testing 10 prompt variants × 100 examples = 1000 evaluations.
- **Biased:** Engineers favor prompts that work on their own test cases.
- **Brittle:** A prompt optimized for GPT-4 may fail on GPT-4o-mini or a future model version.

## Automatic Optimization Approaches

### DSPy (Declarative Self-improving Python)

DSPy treats prompts as compilable programs. It separates the *signature* (what the module does) from the *prompt text* (how it's expressed).

```python
class QA(dspy.Module):
    def __init__(self):
        self.qa = dspy.ChainOfThought("context, question -> answer")
    
    def forward(self, context, question):
        return self.qa(context=context, question=question)

# Compile = automatically optimize prompt text
optimizer = dspy.BootstrapFewShot(max_bootstrapped_demos=4)
optimized_qa = optimizer.compile(QA(), trainset=trainset, valset=valset)
```

**Optimizers available:**
- `BootstrapFewShot` — auto-generates few-shot examples from labeled data.
- `BootstrapFewShotWithRandomSearch` — tries random subsets of examples.
- `MIPRO` (Bayesian) — jointly optimizes instructions and examples.
- `MIPROv2` — best quality, highest cost.

### OPRO (Optimization by PROmpting)

The LLM itself generates prompt improvements:

```
[Current prompt]: "Answer the question based on the context."
[Score]: 0.72
[Task description]: "Generate 5 improved versions of the above prompt."
[LLM output]: "Analyze the provided context and formulate a precise answer..."
```

- The LLM acts as both the optimizer and the task model.
- 2–5% improvement per iteration, diminishing after ~10 iterations.

### APE (Automatic Prompt Engineer)

Beam search over possible instructions:

1. Generate 100 candidate instructions (LLM-generated).
2. Score each on a held-out eval set.
3. Select top 5, generate variants of each.
4. Repeat until convergence.

## Evaluation Budget

| Method | Eval Calls | Quality Improvement | Time |
|---|---|---|---|
| Manual iteration | 10–50 | +5–15% | Hours |
| DSPy BootstrapFewShot | 200–500 | +10–20% | Minutes |
| DSPy MIPROv2 | 1000–5000 | +15–30% | 10–30 min |
| OPRO (10 rounds) | 200–500 | +10–20% | Minutes |
| APE (beam search) | 500–2000 | +15–25% | Minutes-hours |

## Production Optimization Workflow

```
1. Baseline prompt → measure quality on eval set.
2. Run DSPy optimizer (BootstrapFewShot first, MIPROv2 if budget allows).
3. Measure optimized prompt on held-out test set.
4. Deploy to 10% traffic, compare against baseline.
5. If win confirmed, roll out to 100%.
6. Re-optimize quarterly or when model version changes.
```

## Pitfalls

- **Overfitting to eval set.** Use a separate held-out test set that's never touched during optimization.
- **Temporal drift.** An optimized prompt may degrade over time as the model updates. Re-optimize periodically.
- **Latency surprise.** Auto-generated few-shot examples may be verbose. Check token cost before deploying.
- **Model-specificity.** Optimized prompts for one model family may not transfer. Re-optimize per model.

## Best Practices

- **Start with DSPy.** It has the best tooling, documentation, and community.
- **Use at least 100 eval examples** for optimization — fewer leads to overfitting.
- **Optimize for the specific metric** that matters (accuracy, faithfulness, token efficiency).
- **Re-evaluate after each model version update** — optimized prompts are not transferable across model generations.
- **Track prompt version alongside model version** in production metadata.

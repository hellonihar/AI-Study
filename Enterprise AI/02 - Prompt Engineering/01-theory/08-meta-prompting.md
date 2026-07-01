# Meta-Prompting

Using LLMs to generate, refine, and optimize their own prompts.

## What is Meta-Prompting?

Instead of a human crafting the prompt, a "meta-prompt" instructs the LLM to create an effective prompt for a given task.

```
Meta-System: "You are a prompt engineering expert. Given a task description,
generate an optimized system prompt and few-shot examples."

Task: "Classify customer emails as complaint, inquiry, or feedback."

LLM Output:
  System Prompt: "You are a customer service classifier..."
  Examples: [...]
```

## The Meta-Prompt Template

```
You are an expert prompt engineer. Your task is to create an optimal prompt
for the following objective:

[Task description]

Requirements:
1. The prompt should be clear and specific.
2. Include up to 3 few-shot examples (optional).
3. Specify output format strictly.
4. Anticipate edge cases.

Output the prompt in a code block.
```

## Recursive Self-Improvement

```
Round 1: Meta-prompt → Prompt A
Round 2: Evaluate Prompt A on task → Score A
         Meta-prompt("Improve this prompt", Prompt A, Score A) → Prompt B
Round 3: Evaluate Prompt B → Score B
         If Score B > Score A, keep B; else revert to A
```

**Improvement per round:** Typically 2–5%. Diminishing returns after 5 rounds.

## Meta-Prompting for Few-Shot Discovery

The LLM can generate better few-shot examples than random selection:

```python
discovery_prompt = """
Generate 5 diverse examples for the task: {task_description}
Each example should:
- Cover a different edge case or scenario
- Include a correctly labeled input-output pair
- Vary in difficulty (easy, medium, hard)

Output as a list of JSON objects.
"""
```

**Performance:** LLM-generated examples often outperform human-written ones for specific edge cases.

## When to Use Meta-Prompting

| Scenario | Effectiveness | Alternative |
|---|---|---|
| Cold start (no prompt exists) | High | Manual crafting |
| Optimization plateau | High | DSPy |
| Multi-model deployment | Medium | Test per model |
| Rapid prototyping | High | None |
| Production-grade reliability | Low | DSPy + human review |

## Limitations

- **Meta-prompt quality depends on the base model** — smaller models generate worse prompts.
- **No systematic evaluation** — meta-prompting optimizes for human preference, not measured metrics. Pair with DSPy for rigorous optimization.
- **Repetitive outputs** — the LLM tends to generate similar prompts when re-run. Add "be creative" or vary the seed.
- **Can't escape local optima** — once the prompt converges, meta-prompting rarely discovers fundamentally different approaches.

## Best Practices

- **Use meta-prompting for first drafts** — it's faster than writing from scratch. Then optimize with DSPy.
- **Always evaluate the generated prompt** — never trust meta-prompt output without measurement.
- **Provide examples of good prompts** in the meta-prompt to steer quality.
- **Combine with DSPy** — use meta-prompting to generate candidate instruction sets, then use DSPy's Bayesian optimization to refine.
- **Version-control generated prompts** — they're production assets, not ephemeral artifacts.

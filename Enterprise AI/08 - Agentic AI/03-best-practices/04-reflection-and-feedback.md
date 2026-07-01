# Reflection and Feedback Best Practices

## When to Reflect

| Situation | Reflect? | Why |
|-----------|----------|-----|
| Tool returns unexpected result | Yes | May have used wrong tool or params |
| User expresses dissatisfaction | Yes | Need to correct course |
| Task is high-stakes (code, financial) | Yes | Errors are costly |
| All tools succeeded, user is happy | No | Wasted cost and latency |
| Task is time-sensitive | No | Latency matters more |

## Reflection Strategies

### Lightweight Reflection (cost: 1 extra LLM call)
```python
quality = llm.evaluate(f"Does this response answer the user's question? "
                       f"Response: {response}")
if quality < 0.7:
    response = llm.improve(f"Improve: {response}")
```

### Deep Reflection (cost: 2-3 extra LLM calls)
```python
# Step 1: Evaluate
evaluation = llm.evaluate(f"Candidate: {response}. Criteria: {criteria}")

# Step 2: Identify issues
issues = llm.analyze(f"Why does this fail? Evaluation: {evaluation}")

# Step 3: Generate improved version
improved = llm.generate(f"Fix these issues: {issues}. Original: {response}")
```

## Feedback Loops

### Self-Feedback (Reflexion)
Agent reviews its own output and iteratively improves. Simple, fast, no external dependency.

### Tool-Feedback
Tool execution results provide natural feedback. If search returns nothing, the agent knows to try a different query.

### Human-Feedback
User explicitly corrects the agent. Most valuable but slowest. Store corrections for future learning.

### Automated Evaluation (LLM-as-judge)
Separate LLM evaluates the agent's output against criteria. Good for quality measurement but adds cost.

## Reflection Budget

```python
REFLECTION_BUDGET = {
    "max_cycles": 3,        # Never reflect more than 3 times
    "max_cost_reflection": 0.05,  # Cap reflection cost
    "improvement_threshold": 0.1,  # Only reflect if improvement > 10%
}
```

## Common Reflection Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Over-reflecting | 3x cost for 5% improvement | Cap at 2 cycles |
| Vague reflection | "Make it better" | Always specify concrete issues |
| Ignoring tool feedback | Reflection contradicts tool results | Ground reflection in facts |
| No improvement | Same output each reflection | Try different approach after 2 failures |

## Storing Feedback for Learning

```python
feedback_db = [
    {
        "task": "search customer by name",
        "action": "search_customers('John')",
        "result": "Too many results",
        "feedback": "Need to add company filter",
        "improvement": "Try search_customers('John', company='Acme')",
    },
]
```

Periodically review feedback to improve tool descriptions and agent prompts.

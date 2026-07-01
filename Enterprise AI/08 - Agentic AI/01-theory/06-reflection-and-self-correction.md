# Reflection and Self-Correction

## Why Reflection Matters

Agents make mistakes: wrong tool, bad parameters, incorrect reasoning. Reflection enables the agent to detect and fix its own errors without human intervention.

## Reflection Loop

```
Execute → Observe result → Evaluate quality → If poor → Reflect → Retry
                                                      ↓
                                                 Improve approach
```

## Types of Reflection

### Output Reflection
Evaluate the generated output against quality criteria:
- Does it answer the user's question?
- Is it factually consistent with retrieved data?
- Does it follow formatting requirements?

```python
def reflect_on_output(response, criteria):
    evaluation = llm.evaluate(f"""
    Does this response meet these criteria?
    {criteria}
    Response: {response}
    """)
    return evaluation.passed, evaluation.feedback
```

### Process Reflection
Evaluate the approach taken:
- Was the tool selection optimal?
- Could a different sequence have been faster/cheaper?
- What could be done differently next time?

### Outcome Reflection
After task completion, evaluate the overall result:
- Did we achieve the goal?
- How many steps did it take vs. expected?
- What was the total cost?

## Self-Correction Mechanisms

| Issue | Detection | Correction |
|-------|-----------|------------|
| Wrong tool selected | Tool returns irrelevant results | Select different tool, retry |
| Bad parameters | Tool returns error | Parse error, fix params, retry |
| Hallucination | Response contradicts retrieved data | Re-generate with stricter grounding |
| Incomplete answer | User asks follow-up | Expand response with more detail |
| Loop detected | Same action > 3 times | Break loop, try alternative approach |
| Cost exceeded | Running total > budget | Simplify approach, use cheaper model |

## Implementing Self-Correction

```python
class ReflectiveAgent:
    MAX_RETRIES = 3

    def execute_with_reflection(self, task):
        for attempt in range(self.MAX_RETRIES):
            result = self.attempt(task)

            if self.is_successful(result):
                return result

            reflection = self.reflect(task, result, attempt)
            task = self.improve_approach(task, reflection)

        return self.graceful_fallback(task)
```

## Success Criteria

Define clear criteria for "success" to avoid infinite reflection loops:

- **Task completion**: All required sub-tasks finished
- **Quality threshold**: Response passes eval criteria
- **Cost constraint**: Under budget
- **Time constraint**: Under max steps or wall time

## When NOT to Reflect

- The cost of reflection exceeds the value of improvement
- The task has a single correct answer already achieved
- The user is waiting for a response (latency-sensitive)
- Three retries have already failed (diminishing returns)

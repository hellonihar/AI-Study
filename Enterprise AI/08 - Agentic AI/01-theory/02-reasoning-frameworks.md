# Reasoning Frameworks

## ReAct (Reasoning + Acting)

The most widely adopted agent reasoning framework. Interleaves reasoning traces with actions.

```
Thought: I need to find the capital of France.
Action: search_knowledge_base("capital of France")
Observation: The capital of France is Paris.
Thought: I have the answer.
Answer: The capital of France is Paris.
```

### Key Benefits
- **Interpretable**: Full reasoning trace is visible
- **Debugable**: Each step can be inspected and corrected
- **Recoverable**: If an action fails, the model can reason about why and retry

## Plan-and-Solve

Decompose a complex task into a step-by-step plan before executing.

```
Plan:
1. Search for latest quarterly earnings report
2. Extract revenue and profit numbers
3. Compare with previous quarter
4. Summarize changes

Step 1: search("Q3 2024 earnings report")...
```

### When to Use
- Tasks with 5+ steps
- Tasks requiring specific ordering
- Tasks where failure at step N requires starting over

## Tree-of-Thought (ToT)

Explores multiple reasoning paths simultaneously, pruning unpromising branches.

```
Root: "Write a Python function to sort a list"
├── Branch 1: Use built-in sorted()
│   └── Simple, O(n log n)
├── Branch 2: Implement quicksort
│   └── Partition-based, O(n log n) average
└── Branch 3: Implement bubble sort (pruned — too slow)
```

## Reflexion

Agent reflects on its own outputs and iteratively improves them.

```
Attempt 1: Generate code → Fails tests
Reflection: "The function doesn't handle edge case of empty list"
Attempt 2: Generate code with fix → Passes tests
```

## Choosing a Framework

| Task Complexity | Recommended Framework | Reasoning |
|----------------|---------------------|-----------|
| 1–3 steps | ReAct | Simple, fast, interpretable |
| 4–10 steps | Plan-and-Solve | Needs structure upfront |
| Creative/exploratory | Tree-of-Thought | Multiple paths explored |
| Quality-critical | Reflexion | Self-correction improves output |

## Implementation Pattern

```python
class Agent:
    def step(self, observation):
        thought = self.llm.generate(
            f"Thought: {self.reasoning_trace}\n"
            f"Observation: {observation}\n"
            f"What should I do next?"
        )
        action = self.parse_action(thought)
        return action
```

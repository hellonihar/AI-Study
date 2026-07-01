# Planning and Decomposition

## Why Planning Matters

Without planning, agents react step-by-step and can get stuck in loops or miss optimal paths. Planning provides structure, efficiency, and reliability for complex tasks.

## Task Decomposition

Breaking a complex goal into manageable sub-tasks:

```
Goal: "Research competitor pricing and write a report"

Sub-tasks:
1. Identify top 5 competitors
2. Extract pricing page URLs
3. Scrape pricing data
4. Compare pricing tiers
5. Write executive summary
6. Format as PDF report
```

### Decomposition Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| Sequential | Linear chain of steps | Well-defined processes |
| Hierarchical | Tree of sub-goals | Complex, branching tasks |
| Dependency graph | DAG of prerequisites | Tasks with shared dependencies |
| Dynamic | Decompose as you go | Exploratory tasks |

## Planning Approaches

### Static Planning (Plan-and-Solve)
Create a complete plan upfront, then execute. Best when the task is well-understood.

```python
plan = agent.create_plan("Write a blog post about AI")
# plan = [outline, research, draft, edit, format]
for step in plan:
    agent.execute(step)
```

### Dynamic Planning (RePlan)
Plan a few steps ahead, execute, observe results, then re-plan. Best for uncertain environments.

```python
plan = agent.create_plan("Research AI trends")
while not goal_complete:
    step = plan.pop(0)
    result = agent.execute(step)
    plan = agent.replan(result, remaining_goal)
```

### Hierarchical Planning
Top-level plan decomposes into sub-plans managed by sub-agents.

```python
main_plan = [
    ("Research competitors", sub_agent_1),
    ("Analyze market data", sub_agent_2),
    ("Write final report", sub_agent_3),
]
```

## Plan Representation

```python
Plan = {
    "goal": "Research competitor pricing",
    "steps": [
        {"id": 1, "action": "search", "params": {"query": "top AI companies 2024"}},
        {"id": 2, "action": "extract_urls", "depends_on": [1]},
        {"id": 3, "action": "scrape_pricing", "depends_on": [2]},
        {"id": 4, "action": "compare", "params": {"metric": "price_per_token"}, "depends_on": [3]},
    ]
}
```

## Replanning Triggers

Replan when:
- A step fails unexpectedly (tool error, missing data)
- New information changes the goal
- N consecutive steps don't make progress
- User interrupts with new instructions
- Cost exceeds threshold for remaining steps

## Limits of Planning

| Limit | Mitigation |
|-------|-----------|
| Plan too long (LLM loses track) | Summarize progress, checkpoint |
| Plan too detailed | Abstract details, focus on key milestones |
| Plan too vague | Expand unclear steps with sub-plans |
| Environment changes | Replanning trigger with frequency cap |
| Over-planning (analysis paralysis) | Time-box planning phase |

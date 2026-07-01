# Consensus and Debate

## Why Consensus

Multiple agents may produce different answers. Consensus mechanisms aggregate diverse opinions to reach a more accurate result than any single agent.

## Patterns

### Voting

Multiple agents independently answer the same question. The most common answer wins.

```
Question: "What is Q3 revenue?"
Agent A: "$12.4M"
Agent B: "$12.4M"
Agent C: "$12.1M"
Result: "$12.4M" (majority)
```

**Configured as**: Direct voting, weighted voting (by confidence), or ranked voting.

### Weighted Voting

Each agent's vote is weighted by its confidence or historical accuracy.

```python
votes = [
    {"agent": "financial_agent", "answer": "$12.4M", "confidence": 0.95, "weight": 2.0},
    {"agent": "search_agent", "answer": "$12.4M", "confidence": 0.80, "weight": 1.0},
    {"agent": "general_agent", "answer": "$12.1M", "confidence": 0.60, "weight": 1.0},
]
# Weighted: financial (2.0) + search (1.0) = 3.0 for $12.4M vs general (1.0) for $12.1M
```

### Debate

Two (or more) agents argue opposing positions. A judge agent evaluates arguments and decides.

```
Proposal: "Launch feature X in Q1"
Pro Agent: "Market demand is high, competitors are moving"
Con Agent: "Engineering capacity is at 90%, quality will suffer"
Judge: "Defer to Q2. Risk of quality issues outweighs speed advantage."
```

**Best for**: High-stakes decisions, planning, and strategy.

### Ensemble

Multiple agents produce outputs. A meta-agent selects or synthesizes the best result.

```
Code Agent A: def sort(arr): return sorted(arr)
Code Agent B: def sort(arr): arr.sort(); return arr
Code Agent C: def sort(arr): # quicksort implementation
Meta-Agent: "Agent C is most complete, but has a bug. Use Agent A."
```

## When to Use Each

| Pattern | Decision Type | Cost | Latency |
|---------|---------------|------|---------|
| Direct voting | Facts, simple QA | N × single agent | Parallel |
| Weighted voting | Facts with confidence | N × single agent | Parallel |
| Debate | Strategy, planning | 3–5 × single agent | Sequential |
| Ensemble | Creative, code | N × single agent | Parallel |

## Judge Agent Design

A judge agent evaluates the debate and renders a decision:

```python
class JudgeAgent:
    def evaluate(self, pro_args, con_args, context):
        analysis = f"""
        Pro arguments: {pro_args}
        Con arguments: {con_args}
        Decision criteria: {context['criteria']}
        Please evaluate based on evidence strength, not volume.
        """
        return self.llm.generate(analysis)
```

## Potential Issues

| Issue | Mitigation |
|-------|-----------|
| All agents agree (groupthink) | Include a "devil's advocate" agent |
| Most confident agent is wrong | Weight by historical accuracy |
| Debate becomes adversarial | Structured format + time limit per turn |
| Cost explosion (N agents × multiple turns) | Hard cap on debate rounds (3 max) |
| Judge is biased | Use separate model for judging (not used in debate) |

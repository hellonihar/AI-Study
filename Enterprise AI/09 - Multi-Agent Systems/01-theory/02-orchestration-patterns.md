# Orchestration Patterns

## Supervisor Pattern

The supervisor receives a task, breaks it down, delegates to workers, and synthesizes results.

```python
class Supervisor:
    def run(self, task):
        plan = self.decompose(task)
        results = {}
        for subtask in plan:
            specialist = self.select_worker(subtask)
            results[subtask.id] = specialist.run(subtask)
        return self.synthesize(results)
```

### Pros
- Clear control flow
- Easy to debug (single decision point)
- Centralized error handling

### Cons
- Supervisor is a bottleneck
- Supervisor context window may limit complexity
- Single point of failure

## Router Pattern

Lightweight intent classification + dispatch. No deep orchestration.

```python
class Router:
    def route(self, query):
        intent = self.classify(query)
        specialist = self.registry[intent]
        return specialist.run(query)
```

### Pros
- Extremely fast (one classification call)
- Easy to add new specialists (register new handler)
- Scales horizontally

### Cons
- No cross-agent coordination
- Limited to single-turn tasks
- Classification errors propagate

## Delegation Pattern

The primary agent delegates when it hits its own limits, then continues.

```python
class DelegatingAgent:
    def run(self, task):
        if self.should_delegate(task):
            result = specialist.run(task.subtask)
            return self.continue_with(result)
        return self.handle_directly(task)
```

### Pros
- Agent only delegates when needed
- Simple architecture
- Falls back to direct handling

### Cons
- Decision to delegate adds latency
- Agent may not recognize when to delegate

## Hierarchical Pattern

Tree of agents with recursive delegation. Common in enterprise org charts.

```python
class HierarchicalAgent:
    def __init__(self, children=None):
        self.children = children or []

    def run(self, task):
        if self.children:
            sub_tasks = self.decompose(task)
            results = [child.run(st) for child, st
                      in zip(self.children, sub_tasks)]
            return self.merge(results)
        return self.execute(task)
```

### Pros
- Natural decomposition for complex tasks
- Each level manages context independently
- Scales to very deep task hierarchies

### Cons
- Deep trees are slow (sequential delegation)
- Complex error propagation
- Hard to debug

## Choosing a Pattern

| Task Type | Recommended Pattern |
|-----------|-------------------|
| Well-defined workflow | Supervisor |
| High-volume classification | Router |
| Complex, exploratory | Delegation |
| Naturally hierarchical | Hierarchical |
| Collaborative creation | Peer-to-peer |

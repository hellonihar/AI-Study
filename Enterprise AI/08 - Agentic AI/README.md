# Agentic AI

Build autonomous agents with reasoning, tool use, memory, self-correction, and safety guardrails for production systems.

## Module Structure

```
08 - Agentic AI/
├── 01-theory/          # 10 files: architecture through production agent
├── 02-code/            # 10 scripts: basic loop through production agent
├── 03-best-practices/  # 5 files: agent design, memory, tools, reflection, production
├── 04-resources/       # Papers, frameworks, tutorials, books
└── README.md           # This file
```

## Theory (01-theory/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-agent-architecture.md` | Perception → reasoning → action loop, agent types |
| 2 | `02-reasoning-frameworks.md` | ReAct, Plan-and-Solve, Tree-of-Thought, Reflexion |
| 3 | `03-tool-use.md` | Tool lifecycle, selection, composition, error recovery |
| 4 | `04-memory-systems.md` | Short-term, long-term (vector), episodic, consolidation |
| 5 | `05-planning-and-decomposition.md` | Task decomposition, static/dynamic/hierarchical planning |
| 6 | `06-reflection-and-self-correction.md` | Output/process/outcome reflection, correction mechanisms |
| 7 | `07-agent-observability.md` | Per-step tracing, metrics, alerting, visualization |
| 8 | `08-cost-and-performance.md` | Cost breakdown, optimization, budget management |
| 9 | `09-limits-and-safety.md` | Loops, hallucinations, guardrails, human-in-the-loop |
| 10 | `10-production-agent.md` | End-to-end architecture combining all patterns |

## Code Examples (02-code/)

| # | File | Description | Requirements |
|---|------|-------------|--------------|
| 1 | `01-basic-agent-loop.py` | Perceive → reason → act cycle with tool execution | none (stdlib) |
| 2 | `02-reAct-agent.py` | Interleaved reasoning traces with tool actions | none (stdlib) |
| 3 | `03-tool-use-agent.py` | Multi-tool selection, execution, error handling | none (stdlib) |
| 4 | `04-agent-with-memory.py` | Conversation + vector memory for long-term recall | none (stdlib) |
| 5 | `05-task-decomposition.py` | Break complex tasks into dependency-respecting subtasks | none (stdlib) |
| 6 | `06-reflection-agent.py` | Self-critique and iterative improvement loop | none (stdlib) |
| 7 | `07-agent-observability.py` | Step tracing, metrics, cost per step | none (stdlib) |
| 8 | `08-cost-tracker.py` | Token/cost tracking, budget enforcement | none (stdlib) |
| 9 | `09-safety-guardrails.py` | Input/output guardrails, loop detection, budget caps | none (stdlib) |
| 10 | `10-production-agent.py` | Full production agent: memory + tools + reflection + guardrails + cost tracking | none (stdlib) |

## Best Practices (03-best-practices/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-agent-design.md` | When to use agents, architecture principles, anti-patterns |
| 2 | `02-memory-management.md` | Token budget, pruning, retrieval, consolidation, forgetting |
| 3 | `03-tool-selection.md` | Tool catalog design, schemas, composition, testing |
| 4 | `04-reflection-and-feedback.md` | When/why to reflect, strategies, budgets, common mistakes |
| 5 | `05-production-and-monitoring.md` | Deployment, scaling, dashboards, alerting, canary, rollback |

## Key Topics

- **Reasoning Frameworks**: ReAct, Plan-and-Solve, Tree-of-Thought, Reflexion
- **Tool Use**: Registration, schema design, execution, error recovery, composition
- **Memory**: Working memory, semantic (vector), episodic, consolidation, pruning
- **Planning**: Static/dynamic/hierarchical decomposition, dependency graphs, replanning
- **Reflection**: Self-critique, output/process/outcome evaluation, iterative improvement
- **Safety**: Input guardrails, output guardrails, loop detection, cost budgets, human-in-the-loop
- **Observability**: Step tracing, cost tracking, metrics, alerting, trace storage
- **Production**: Scaling, canary deploys, rollback, monitoring dashboards

## Quick Start

```bash
# Basic agent loop
python "02-code/01-basic-agent-loop.py"

# ReAct agent
python "02-code/02-reAct-agent.py"

# Safety guardrails
python "02-code/09-safety-guardrails.py"

# Production agent (combines all patterns)
python "02-code/10-production-agent.py"
```

## Prerequisites

- **Python 3.10+**
- **Core**: none (stdlib only for all scripts)
- **Memory**: `sentence-transformers` (optional — vector memory falls back to simple hashing)
- **Production**: `fastapi`, `redis`, `prometheus-client`, `langsmith`

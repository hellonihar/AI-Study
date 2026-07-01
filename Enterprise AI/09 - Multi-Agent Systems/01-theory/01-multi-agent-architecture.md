# Multi-Agent Architecture

## Why Multiple Agents

A single agent has limits: context window, expertise breadth, and failure domain. Multiple agents overcome these by dividing labor, specializing expertise, and providing redundancy.

## Core Architecture Patterns

### Supervisor (Orchestrator)
One agent coordinates, delegates, and aggregates results from worker agents.

```
User → Supervisor → Worker A → result → Supervisor → User
                  → Worker B → result
                  → Worker C → result
```

**Best for**: Well-defined workflows with clear task boundaries.

### Router
A lightweight classifier routes requests to specialist agents without deep orchestration.

```
User → Router → Specialist A
             → Specialist B
             → Specialist C
```

**Best for**: High-volume systems with distinct request categories.

### Hierarchical
Agents are organized in a tree. Each level delegates to its children and aggregates upward.

```
User → Agent → Sub-agent A → Sub-sub-agent 1
             → Sub-agent B      → Sub-sub-agent 2
                                 → Sub-sub-agent 3
```

**Best for**: Complex tasks that decompose naturally into hierarchies.

### Peer-to-Peer
Agents communicate directly without central coordination. Each agent decides independently.

```
Agent A ←→ Agent B
   ↕         ↕
Agent C ←→ Agent D
```

**Best for**: Collaborative tasks, debate, consensus-building.

## Design Principles

### 1. Single Responsibility
Each agent does one thing well. A "search agent" searches. A "summarization agent" summarizes. Avoid creating a "super agent" that does everything — at that point, use a single agent instead.

### 2. Minimal Communication
Each message between agents adds latency. Design for minimal, structured messages. Prefer passing references (document IDs) over full content.

### 3. Fail Isolated
One agent's failure should not cascade. Use timeouts, circuit breakers, and fallback responses per agent.

### 4. Observable
Every agent decision should be logged. Distributed tracing must span agent boundaries.

## When to Use Multi-Agent vs Single Agent

| Factor | Single Agent | Multi-Agent |
|--------|-------------|-------------|
| Task complexity | Simple to moderate | Complex, multi-domain |
| Expertise breadth | Generalist | Multiple specialists |
| Context needs | Single context | Partitioned contexts |
| Fault tolerance | Single point of failure | Graceful degradation |
| Development cost | Lower | Higher |
| Debugging | Easier | Harder (distributed) |
| Latency | Lower | Higher (communication overhead) |

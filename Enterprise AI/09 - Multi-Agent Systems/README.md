# Multi-Agent Systems

Multiple coordinated AI agents working together to solve complex, multi-step problems through orchestration, specialization, consensus, and distributed execution.

## Module Structure

```
09 - Multi-Agent Systems/
├── 01-theory/          # 10 files: architecture through production deployment
├── 02-code/            # 10 scripts: supervisor through full production system
├── 03-best-practices/  # 5 files: architecture, communication, state, scaling, observability
├── 04-resources/       # Papers, frameworks, tutorials, books
└── README.md           # This file
```

## Theory (01-theory/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-multi-agent-architecture.md` | Why multi-agent, core patterns (supervisor, router, hierarchical, P2P) |
| 2 | `02-orchestration-patterns.md` | Supervisor, router, delegation, hierarchical — when to use each |
| 3 | `03-agent-communication.md` | Direct messaging, blackboard, event bus, message protocols |
| 4 | `04-handoff-protocols.md` | When/how to transfer control, context serialization, multi-step handoffs |
| 5 | `05-state-management.md` | Centralized, event sourcing, consensus, idempotency, conflicts |
| 6 | `06-specialist-agents.md` | Designing domain-specific agents, routing, capability registry |
| 7 | `07-consensus-and-debate.md` | Voting, weighted voting, debate with judge, ensemble patterns |
| 8 | `08-observability-in-multi-agent.md` | Distributed tracing, span attributes, message tracking |
| 9 | `09-scaling-and-performance.md` | Horizontal scaling, queue-based load leveling, parallel execution |
| 10 | `10-production-multi-agent.md` | End-to-end architecture, configuration, deployment, error handling |

## Code Examples (02-code/)

| # | File | Description | Requirements |
|---|------|-------------|--------------|
| 1 | `01-supervisor-agent.py` | Supervisor delegates to specialists and synthesizes results | none (stdlib) |
| 2 | `02-router-agent.py` | Classifies intents and routes to specialist agents | none (stdlib) |
| 3 | `03-agent-communication.py` | Structured message passing via message bus | none (stdlib) |
| 4 | `04-handoff-protocol.py` | Multi-level handoff (support → billing → escalation) | none (stdlib) |
| 5 | `05-specialist-agents.py` | Capability-based routing to multiple specialists | none (stdlib) |
| 6 | `06-debate-agent.py` | Proponent vs opponent debate with judge evaluation | none (stdlib) |
| 7 | `07-consensus-voting.py` | Direct and weighted voting across agent ensemble | none (stdlib) |
| 8 | `08-distributed-tracing.py` | Trace spans across multi-agent calls | none (stdlib) |
| 9 | `09-parallel-execution.py` | Dependency DAG with parallel agent execution | none (stdlib) |
| 10 | `10-production-multi-agent.py` | Full system: supervisor + specialists + tracing | none (stdlib) |

## Best Practices (03-best-practices/)

| # | File | Topic |
|---|------|-------|
| 1 | `01-architecture-patterns.md` | Pattern selection guide, design principles, anti-patterns |
| 2 | `02-communication-design.md` | Message protocol, serialization, delivery guarantees, security |
| 3 | `03-state-and-consistency.md` | State store selection, idempotency, conflict resolution, consistency |
| 4 | `04-scaling-and-performance.md` | Horizontal scaling, right-sizing, caching, rate limiting |
| 5 | `05-observability-and-debugging.md` | Tracing, alerting, debugging common issues, structured logging |

## Key Topics

- **Orchestration**: Supervisor, router, delegation, hierarchical, peer-to-peer
- **Communication**: Direct message, blackboard, event bus, structured protocols
- **Handoffs**: Context transfer, multi-step handoffs, failure recovery
- **State**: Centralized, event sourcing, distributed consensus, CRDTs
- **Specialists**: Domain-specific agents, capability registry, intent routing
- **Consensus**: Voting, weighted voting, debate with judge, ensemble
- **Observability**: Distributed tracing, span correlation, message tracking
- **Scaling**: Horizontal replication, queue-based load leveling, parallel DAGs

## Quick Start

```bash
# Supervisor pattern
python "02-code/01-supervisor-agent.py"

# Router pattern
python "02-code/02-router-agent.py"

# Debate system
python "02-code/06-debate-agent.py"

# Production multi-agent system
python "02-code/10-production-multi-agent.py"
```

## Prerequisites

- **Python 3.10+**
- **Core**: none (stdlib only for all scripts)
- **Production**: `redis`, `rabbitmq`, `opentelemetry-api`, `prometheus-client`

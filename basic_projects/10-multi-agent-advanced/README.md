# 10 - Multi-Agent Advanced: Enterprise Content Compliance & Publishing

## Overview

Build an enterprise-grade multi-agent system that drafts, validates, reviews, and publishes content under human supervision. The system chains **five specialist agents** (Writer, Fact-Checker, Compliance, Brand-Guard, Plagiarism-Check) managed by an **Editor-in-Chief Supervisor** that implements three advanced patterns: **Human-in-the-Loop** approval gates, a **Reflection Agent** that audits the final output, and **tool-level monitoring** that logs every call for observability and cost tracking.

## Tech Stack

- **Orchestration** — LangGraph with interrupt nodes for HITL
- **LLM** — GPT-4o (Writer, Supervisor, Reflection), GPT-4o-mini (Fact-Checker, Compliance)
- **Monitoring** — Custom `ToolMonitor` context manager that logs to a SQLite database
- **HITL** — LangGraph's `interrupt_after` / `wait_for_user` pattern
- **Tools** — Plagiarism API, Grammar API (LanguageTool), Brand DB (JSON file), Web Search
- **Storage** — SQLite for tool logs, JSON for draft state

## Architecture & Design

```
                                    ┌──────────────────────────┐
                                    │      USER REQUEST         │
                                    │  "Write a blog post about │
                                    │   our Q3 product launch"  │
                                    └───────────┬──────────────┘
                                                │
                                    ┌───────────▼──────────────┐
                                    │  SUPERVISOR AGENT         │
                                    │  (Editor-in-Chief)       │
                                    │  - Receives brief        │
                                    │  - Creates outline       │
                                    │  - Plans workflow        │
                                    └────┬──────┬──────┬──────┘
                                         │      │      │
                    ┌────────────────────┘      │      └────────────────────┐
                    │                           │                          │
           ┌────────▼────────┐        ┌─────────▼────────┐      ┌──────────▼─────────┐
           │   WRITER AGENT   │        │  FACT-CHECKER     │      │  COMPLIANCE AGENT   │
           │   (Draft)        │        │  AGENT            │      │  (Regulatory)       │
           │                  │        │  - Verifies claims │      │                     │
           │  Tools:          │        │  - Cites sources   │      │  Tools:             │
           │  - grammar_check │        │  - Flags unknowns  │      │  - gdpr_check       │
           │  - style_guide   │        │                    │      │  - soc2_check       │
           └────────┬─────────┘        │  Tools:            │      │  - data_privacy     │
                    │                  │  - web_search      │      └──────────┬─────────┘
                    │                  │  - source_cite     │               │
                    │                  └─────────┬──────────┘               │
                    │                           │                          │
                    └───────────────────┬───────┴──────────┬───────────────┘
                                        │                  │
                               ┌────────▼──────┐  ┌────────▼────────┐
                               │  BRAND GUARD   │  │  PLAGIARISM      │
                               │  AGENT         │  │  CHECK AGENT     │
                               │                │  │                  │
                               │  Tools:        │  │  Tools:          │
                               │  - brand_db    │  │  - plag_scan    │
                               │  - tone_check  │  │  - similarity    │
                               │  - competitor  │  │                  │
                               └────────┬───────┘  └────────┬────────┘
                                        │                   │
                                        └───────┬───────────┘
                                                │
                                     ┌──────────▼───────────┐
                                     │  HITL GATE 1          │
                                     │  "Review draft +      │
                                     │   all validations"    │
                                     │  [Approve] [Revise]   │
                                     └──────────┬───────────┘
                                                │  (if approved)
                                     ┌──────────▼───────────┐
                                     │  REFLECTION AGENT     │
                                     │  - Reads full chain   │
                                     │  - Checks consistency │
                                     │  - Flags tone shifts  │
                                     │  - Suggests polish    │
                                     └──────────┬───────────┘
                                                │
                                     ┌──────────▼───────────┐
                                     │  HITL GATE 2          │
                                     │  "Approve final?"     │
                                     │  [Publish] [Revise]   │
                                     └──────────┬───────────┘
                                                │  (if published)
                                     ┌──────────▼───────────┐
                                     │  PUBLISH AGENT        │
                                     │  - Formats output     │
                                     │  - Logs audit trail   │
                                     │  - Returns final URL  │
                                     └──────────────────────┘
```

### Monitoring Layer (Runs Across All Agents)

```
  EVERY TOOL CALL ──► ToolMonitor ──► SQLite
       │                         │
       │                    ┌─────┴─────┐
       │                    │  tool_log  │
       │                    ├───────────┤
       │                    │ agent_id   │
       │                    │ tool_name  │
       │                    │ input_size │
       │                    │ output_size│
       │                    │ latency_ms │
       │                    │ success    │
       │                    │ cost       │
       │                    │ timestamp  │
       │                    └───────────┘
       │
       ▼
  Supervisor can query:
  - Cost per agent per run
  - Slowest tools (p95 latency)
  - Failure rate per tool
  - Token efficiency per agent
```

## Design Decisions

### 1. Human-in-the-Loop Gates

Two HITL gates rather than one because content publishing has two distinct approval moments:
- **Gate 1** (After all checks): "Here's the draft with all validation reports. Approve the content, or request specific revisions?" The human can say "Fix the third paragraph — the compliance concern is valid" and the agent loops back.
- **Gate 2** (After reflection): "Here's the reflection audit. Ready to publish?" This separates content quality from final sign-off.

Implemented via LangGraph `interrupt_after` — the graph pauses, serializes state, and waits for a human payload. The human response can be "approve", "revise with notes", or "reject with reason."

### 2. Reflection Agent

The Reflection Agent reads the *entire chain's output*: the draft, the fact-check report, the compliance review, the brand guard check, and the plagiarism scan. It then produces a **consistency audit**:
- Does the tone shift between sections?
- Are there contradictions (e.g., one section says "Q3 launch" and another says "Q4")?
- Are all fact-check flags addressed?
- Does the content match the original brief?
- What's the overall quality score (1-10)?

This catches cross-agent issues that no single specialist could see. The Reflection Agent has no tools — it's pure analysis.

### 3. Tool-Level Monitoring

Every tool call is wrapped in a `ToolMonitor` context manager that writes to a SQLite `tool_log` table:

```python
class ToolMonitor:
    def __init__(self, agent_id: str, tool_name: str, db_path: str = "monitor.db"):
        self.agent_id = agent_id
        self.tool_name = tool_name
        self.db_path = db_path

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency = time.time() - self.start
        success = exc_type is None
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO tool_log VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.agent_id, self.tool_name, self.input_size,
                 self.output_size, latency, success, datetime.now())
            )
```

The Supervisor queries this log to produce a **cost & performance summary** attached to the final output — giving the human visibility into not just *what* happened but *how much it cost*.

### 4. Agent Tool Isolation

Each agent gets only the tools it needs:
- **Writer** — `grammar_check`, `style_guide` (cannot access brand DB or plagiarism scanner)
- **FactChecker** — `web_search`, `source_cite` (cannot edit the draft)
- **Compliance** — `gdpr_check`, `soc2_check`, `data_privacy_scan` (read-only on draft, no search)
- **BrandGuard** — `brand_db_lookup`, `tone_analyzer`, `competitor_mention_check`
- **Plagiarism** — `plag_scan`, `similarity_report` (no write access anywhere)

This is **least privilege at the agent level** — a compromised agent can only misuse its own tools.

### 5. Retry and Fallback

- Each tool has a timeout (5s). On failure, the agent retries once after 1s.
- If a critical tool (e.g., plagiarism scan) is down, the Supervisor marks the run as "degraded" and requires explicit human sign-off to proceed.
- Non-critical tools (e.g., grammar check) are optional — the agent proceeds with a warning in the log.

## Setup & Run

1. Install dependencies:
   ```bash
   pip install langgraph langchain-openai sqlite3 httpx
   ```
2. Set up the monitoring database:
   ```python
   import sqlite3
   conn = sqlite3.connect("monitor.db")
   conn.execute("""
       CREATE TABLE IF NOT EXISTS tool_log (
           agent_id TEXT, tool_name TEXT, agent_version TEXT,
           input_size INT, output_size INT, latency_ms REAL,
           success BOOL, cost REAL, timestamp TEXT, run_id TEXT
       )""")
   conn.execute("""
       CREATE TABLE IF NOT EXISTS run_log (
           run_id TEXT PRIMARY KEY, brief TEXT, status TEXT,
           total_cost REAL, total_latency_ms REAL, created_at TEXT
       )""")
   conn.commit()
   ```
3. Define the agents and HITL gates:
   ```python
   # core.py (simplified structure)
   from langgraph.graph import StateGraph, END
   from langgraph.checkpoint.sqlite import SqliteSaver
   from tool_monitor import ToolMonitor

   class ContentState(TypedDict):
       brief: str
       draft: str
       fact_check_report: str
       compliance_report: str
       brand_report: str
       plagiarism_report: str
       reflection_report: str
       human_feedback: str  # populated by HITL gate
       status: str          # draft | review | approved | published
       run_id: str
       tool_log: list

   graph = StateGraph(ContentState)

   # Nodes
   graph.add_node("writer", writer_agent)
   graph.add_node("fact_checker", fact_checker_agent)
   graph.add_node("compliance", compliance_agent)
   graph.add_node("brand_guard", brand_guard_agent)
   graph.add_node("plagiarism_check", plagiarism_agent)
   graph.add_node("hitl_gate_1", human_approval_gate)
   graph.add_node("reflector", reflection_agent)
   graph.add_node("hitl_gate_2", human_approval_gate_2)

   # Flow
   graph.set_entry_point("writer")
   graph.add_edge("writer", "fact_checker")
   graph.add_edge("fact_checker", "compliance")
   graph.add_edge("compliance", "brand_guard")
   graph.add_edge("brand_guard", "plagiarism_check")
   graph.add_edge("plagiarism_check", "hitl_gate_1")
   graph.add_conditional_edges("hitl_gate_1", route_after_hitl, {
       "approve": "reflector",
       "revise": "writer"  # loop back for revision
   })
   graph.add_edge("reflector", "hitl_gate_2")
   graph.add_conditional_edges("hitl_gate_2", route_after_hitl, {
       "approve": "publisher",
       "revise": "writer",
       "reject": END
   })
   graph.add_node("publisher", publish_agent)
   graph.add_edge("publisher", END)

   # Enable HITL via checkpointer
   app = graph.compile(checkpointer=SqliteSaver.from_conn_string("checkpoints.db"))
   ```
4. Run the system:
   ```python
   # run.py
   thread = {"configurable": {"thread_id": "run-001"}}

   # Initial invocation — pauses at Gate 1
   result = app.invoke(ContentState(
       brief="Write a 800-word blog post about our Q3 product launch, "
             "targeting enterprise customers. Key features: SSO, audit logs, RBAC."
   ), thread)

   # Human reviews the draft + reports, provides feedback
   human_response = {
       "decision": "revise",
       "notes": "Paragraph 3 overstates performance claims. Tone is too casual for enterprise."
   }
   result = app.invoke(ContentState(human_feedback=human_response), thread)

   # After revision and Gate 2
   result = app.invoke(ContentState(human_feedback={"decision": "approve"}), thread)
   print(result["draft"])
   ```
5. View monitoring data:
   ```python
   import sqlite3, pandas as pd
   conn = sqlite3.connect("monitor.db")
   df = pd.read_sql("SELECT * FROM tool_log WHERE run_id = 'run-001'", conn)
   print(f"Total cost: ${df['cost'].sum():.4f}")
   print(f"Avg latency per tool: {df.groupby('tool_name')['latency_ms'].mean()}")
   print(f"Failure rate: {1 - df['success'].mean():.1%}")
   ```

## Example Output

After a complete run, the system produces:
- **Final draft** — polished, checked, compliant content
- **Validation summary** — fact-check flags, compliance green lights, brand score
- **Reflection audit** — consistency score, tone analysis, brief alignment check
- **Monitoring report** — cost breakdown by agent, slowest tools, any failures
- **Audit trail** — full log of every tool call, every agent output, every human decision

## What You Learn

- **Human-in-the-loop** in a state graph — pausing execution, serializing state, awaiting human input, and resuming from the checkpoint
- **Reflection pattern** — a meta-agent that evaluates the entire pipeline's output for cross-cutting concerns no single specialist can catch
- **Tool-level observability** — wrapping every tool call with latency, cost, and success tracking without polluting agent logic
- **Cost attribution** — knowing exactly how much each agent spent on tool calls per run
- **Conditional revision loops** — the graph can loop back to any earlier node based on human feedback, not just linear progression
- **Least privilege per agent** — each agent has only the tools it needs, reducing blast radius if an agent is compromised
- **Graceful degradation** — handling tool failures with retry, skip, or escalate logic depending on tool criticality
- **Audit trail for compliance** — every decision, every tool call, every human intervention is logged immutably; essential for regulated industries (finance, healthcare, legal)

## Comparison: Basic vs. Advanced Multi-Agent

| Feature | 09-multi-agent (Basic) | 10-multi-agent-advanced |
|---|---|---|
| Structure | Supervisor → 3 peers | Supervisor → 5 peers + Reflection |
| Parallelism | All specialists run in parallel | Staged pipeline (some sequential dependencies) |
| HITL | None | Two approval gates with conditional routing |
| Reflection | None | Dedicated reflection agent audits consistency |
| Monitoring | None (state only) | Per-tool SQLite logging with cost/latency |
| Error handling | None | Retry, fallback, degraded-mode escalation |
| Retry loops | None | Revision loop triggered by human feedback |
| Audit trail | State object only | Immutable DB: tool_log + run_log + checkpoints |

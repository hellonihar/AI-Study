# Handoff Protocols

## What is a Handoff?

A handoff transfers control and context from one agent to another. The receiving agent continues the task with full context of what happened before.

## When to Handoff

| Trigger | Example |
|---------|---------|
| Out of scope | Billing question → route to billing specialist |
| Need specialist | Technical question → route to engineering agent |
| Need approval | High-value transaction → route to authorization agent |
| Escalation | Agent unsure → route to senior agent |
| Task complete in part | Customer support → handoff to follow-up agent |

## Handoff Protocol

### Step 1: Handoff Request
```
Primary Agent → Secondary Agent:
{
  "type": "handoff_request",
  "task_id": "t-123",
  "reason": "out_of_scope",
  "context": {
    "conversation": [...],
    "findings": {...},
    "state": {...}
  }
}
```

### Step 2: Acceptance
```
Secondary Agent → Primary Agent:
{
  "type": "handoff_accept",
  "task_id": "t-123",
  "status": "accepted",
  "estimated_resolution_time": "5m"
}
```

### Step 3: Context Transfer
Secondary agent receives full context and continues from where primary left off.

### Step 4: Resolution
```
Secondary Agent → Primary Agent (or User):
{
  "type": "handoff_complete",
  "task_id": "t-123",
  "result": "...",
  "summary": "..."
}
```

## Context Serialization

What to include in handoff context:

```python
HANDOFF_CONTEXT = {
    "task": {"id": "t-123", "goal": "Reset user password", "priority": "high"},
    "conversation": [
        {"role": "user", "content": "I forgot my password"},
        {"role": "assistant", "content": "I can help reset it."},
        {"role": "tool", "name": "verify_identity", "result": "verified"},
    ],
    "state": {"identity_verified": True, "reset_attempts": 0},
    "findings": {"user": "alice@corp.com", "account_status": "active"},
    "errors": [],
    "metadata": {"agent": "support_agent_v1", "timestamp": "..."},
}
```

## Handoff Failures

| Failure | Recovery |
|---------|----------|
| Secondary agent unavailable | Return to primary, try alternative |
| Context too large | Summarize before transfer |
| Handoff rejected | Primary handles with fallback |
| Handoff timeout | Primary retries or escalates |

## Multi-Step Handoffs

A task may pass through multiple agents:

```
Support Agent → Billing Agent → Authorization Agent → Support Agent → User
```

Each handoff adds context. The final agent must handle the accumulated context or summarize before each transfer.

## Handoff vs Delegation

| Aspect | Handoff | Delegation |
|--------|---------|------------|
| Control | Transferred to new agent | Primary retains control |
| Context | Full context transfer | Relevant subset only |
| Result | Secondary reports back or to user | Primary synthesizes result |
| Use case | Specialty escalation | Sub-task execution |

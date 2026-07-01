# Limits and Safety

## Known Limitations of Agents

### 1. Looping
Agents can get stuck repeating the same action when the model fails to recognize progress.

**Mitigation**:
- Max step limit (15–25 steps, depending on task)
- Loop detection: same action > 3 times → break loop
- Escalation: after N failed attempts, ask for human help

### 2. Hallucination in Reasoning
The model may generate plausible-sounding but incorrect reasoning traces.

**Mitigation**:
- Ground each claim in tool output
- Cross-validate facts from multiple sources
- Never trust the model's internal knowledge over tool results

### 3. Cost Runaway
An agent can consume thousands of dollars if left unsupervised.

**Mitigation**:
- Hard cost cap per task ($0.50–$5.00)
- Cost alerting at 80% of budget
- Kill switch when cost exceeds threshold

### 4. Tool Misuse
Agent may call destructive tools (delete, write, send) incorrectly.

**Mitigation**:
- Read-only tools by default
- Confirmation step for mutation tools
- Parameter validation on every tool call

### 5. Context Window Overflow
Long agent sessions exceed the LLM's context window.

**Mitigation**:
- Summarize old conversation turns
- Prune irrelevant tool outputs
- Use sliding window over conversation history

## Safety Architecture

```
User Input
    │
    ▼
┌──────────────┐
│ Input Guard  │ ← Jailbreak detection, topic filter, PII scan
└──────┬───────┘
       ▼
┌──────────────┐
│ Agent Core   │ ← Reasoning, tool selection, execution
└──────┬───────┘
       ▼
┌──────────────┐
│ Output Guard │ ← PII redaction, policy compliance, tone check
└──────┬───────┘
       ▼
   User Output
```

## Guardrails

### Input Guardrails
- Jailbreak prompt detection (DAN, role-play attacks)
- Topic filtering (off-limits subjects)
- PII scanning (block or redact before processing)
- Rate limiting (prevent abuse)

### Output Guardrails
- PII redaction (emails, phone numbers, SSNs)
- Policy compliance (no competitors, no legal advice)
- Tone check (professional, not offensive)
- Factual consistency (vs. retrieved context)
- Citation requirement (claims must cite sources)

### Process Guardrails
- Max steps: 25
- Max tokens per step: 4,000
- Max cost per task: $1.00
- Max consecutive failures: 3
- Max reflection cycles: 3

## Human-in-the-Loop

| Decision Type | Auto-approve | Require Human |
|--------------|-------------|---------------|
| Read/search | ✅ | ❌ |
| Write (email, ticket) | ❌ | ✅ |
| Delete data | ❌ | ✅ |
| Execute code | ❌ | ✅ |
| Spend > $0.10 | ❌ | ✅ |
| Share PII | ❌ | ✅ |

## Red-Teaming

Test your agent against:
- Prompt injection: "Ignore previous instructions and..."
- Tool abuse: Repeatedly call expensive/search tools
- Loop exploitation: Questions designed to cause infinite loops
- Bias testing: Sensitive topics across demographic groups

## Emergency Stop

Every production agent needs:
- **Hard stop**: API endpoint or flag to immediately halt execution
- **Soft stop**: Complete current step, then halt
- **Resume capability**: Pick up where it left off after review
- **Audit trail**: Full trace of all actions before stoppage

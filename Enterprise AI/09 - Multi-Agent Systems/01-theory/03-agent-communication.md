# Agent Communication

## Communication Patterns

### Direct Message Passing
Agent A sends a structured message directly to Agent B.

```json
{
  "from": "search_agent",
  "to": "summarize_agent",
  "type": "task",
  "task_id": "t-123",
  "payload": {"documents": ["..."], "max_length": 200},
  "correlation_id": "c-456"
}
```

### Shared State (Blackboard)
Agents read/write to a shared state store. Common in collaborative systems.

```
Blackboard (Redis / shared dict):
  ├── task/t-123/status: "in_progress"
  ├── task/t-123/documents: [...]
  ├── task/t-123/summary: "..."
  └── task/t-123/errors: []
```

### Event Bus
Agents publish events and subscribe to relevant topics. Decoupled and scalable.

```
Agent A (search) → publishes "documents_found" event
Agent B (summarize) → subscribes to "documents_found" → processes → publishes "summary_ready"
Agent C (format) → subscribes to "summary_ready" → publishes "report_complete"
```

## Message Structure

```python
class AgentMessage:
    def __init__(self, msg_type, sender, recipient, payload,
                 correlation_id=None, reply_to=None):
        self.id = uuid.uuid4().hex[:8]
        self.type = msg_type  # request, response, error, event
        self.sender = sender
        self.recipient = recipient
        self.payload = payload
        self.correlation_id = correlation_id
        self.reply_to = reply_to  # queue/address for responses
        self.timestamp = datetime.now().isoformat()
```

## Serialization

| Format | Size | Speed | Schema | Human-readable |
|--------|------|-------|--------|---------------|
| JSON | Medium | Fast | Loose | Yes |
| MessagePack | Small | Fast | Loose | No |
| Protocol Buffers | Small | Fast | Strict | No |
| Apache Avro | Small | Fast | Strict | No |

For most multi-agent systems, JSON is sufficient. Use Protobuf for high-throughput systems.

## Error Handling

```python
def send_with_retry(agent, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = agent.receive(message)
            return response
        except TimeoutError:
            if attempt == max_retries - 1:
                return ErrorResponse("Agent timed out")
            continue
        except AgentUnavailableError:
            return ErrorResponse("Agent unavailable")
```

### Error Types
| Error | Meaning | Recovery |
|-------|---------|----------|
| Timeout | Agent didn't respond in time | Retry or skip |
| Unavailable | Agent is down | Route to alternative |
| Invalid message | Schema violation | Fix and resend |
| Processing error | Agent failed on task | Escalate to supervisor |

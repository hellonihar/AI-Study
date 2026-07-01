# Agent Communication Best Practices

## Message Protocol Design

### Consistent Structure
Every message should follow a consistent schema:

```json
{
  "protocol_version": "1.0",
  "message_id": "msg-123",
  "message_type": "request",
  "sender": "agent_a",
  "recipient": "agent_b",
  "correlation_id": "corr-456",
  "timestamp": "2024-12-01T10:00:00Z",
  "ttl_seconds": 30,
  "payload": {...}
}
```

### Message Types
| Type | Purpose | Expects Response |
|------|---------|-----------------|
| `request` | Ask agent to do something | Yes |
| `response` | Return result | No |
| `error` | Report failure | No |
| `event` | Broadcast information | No |
| `handoff_request` | Transfer control | Yes |
| `handoff_accept` | Accept control | No |
| `ping` | Health check | Yes |

## Serialization

### Choosing a Format
| Format | Schema | Size | Speed | Best For |
|--------|--------|------|-------|----------|
| JSON | Dynamic | Medium | Fast | Most systems, debugging |
| MessagePack | Dynamic | Small | Fast | High-throughput |
| Protobuf | Strict | Small | Fast | Large-scale, cross-language |

### Schema Validation
Validate messages on both send and receive:

```python
def validate_message(message, schema):
    required = ["message_id", "sender", "recipient", "payload"]
    for field in required:
        if field not in message:
            raise ValueError(f"Missing required field: {field}")
    return True
```

## Delivery Guarantees

| Guarantee | Meaning | Implementation |
|-----------|---------|---------------|
| At-most-once | Message may be lost | Fire and forget |
| At-least-once | Message delivered, may duplicate | Retry on failure |
| Exactly-once | Delivered exactly once | Dedup + retry + ack |

For agent systems, **at-least-once** with **idempotent handlers** is the sweet spot.

## Error Handling

```python
def send_message(agent, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            agent.receive(message)
            return True
        except TimeoutError:
            if attempt < max_retries - 1:
                continue
            log_error(f"Message to {agent.name} timed out")
            return False
        except AgentUnavailableError:
            log_error(f"Agent {agent.name} unavailable")
            return False
```

## Message Size Limits

| Component | Max Size | Action if Exceeded |
|-----------|----------|-------------------|
| Single message | 10 KB | Split into multiple messages |
| Payload | 5 KB | Compress or summarize |
| Context in handoff | 50 KB | Summarize before transfer |
| Batch results | 100 KB | Paginate |

## Security

- Authenticate sender (each agent has a token)
- Encrypt sensitive payloads (PII, credentials)
- Audit log every message (sender, recipient, size, timestamp)
- Rate limit per agent (max 100 msg/min per agent)

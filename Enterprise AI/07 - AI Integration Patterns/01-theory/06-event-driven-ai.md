# Event-Driven AI

## Motivation

Synchronous AI calls are simple but brittle. When requests spike or downstream services slow down, synchronous systems fail. Event-driven architecture decouples producers and consumers via message queues, improving reliability and scalability.

## Architecture

```
Client → API Gateway → Request Queue → Worker Pool → Response Queue → Client
```

### Components

1. **Request Queue**: Receives AI task requests (SQS, RabbitMQ, Kafka)
2. **Worker Pool**: Processes tasks from the queue (containerized workers, auto-scaled)
3. **Response Queue**: Sends results back to clients
4. **Dead Letter Queue (DLQ)**: Captures failed tasks for inspection

## When to Use Event-Driven AI

| Scenario | Sync | Async |
|----------|------|-------|
| Real-time chat | ✅ | ❌ |
| Document processing | ❌ | ✅ |
| Batch summarization | ❌ | ✅ |
| Interactive agents | ✅ | ❌ |
| Embedding generation | ❌ | ✅ |
| Webhook-based automation | ❌ | ✅ |

## Webhook Pattern

Instead of polling for results, clients register a callback URL:

```json
POST /api/process
{
  "input": "Long document to summarize...",
  "webhook_url": "https://client.com/callback",
  "priority": "normal"
}
```

Worker processes and POSTs the result to `webhook_url`:

```json
POST https://client.com/callback
{
  "request_id": "req-123",
  "status": "completed",
  "result": "...",
  "latency_ms": 4500,
  "cost": 0.0023
}
```

## Polling Pattern

Simpler but less efficient. Client receives a `request_id` and polls for completion:

```json
GET /api/status/req-123
→ {"status": "pending"}
→ {"status": "processing"}
→ {"status": "completed", "result": "..."}
```

Recommended: exponential backoff (poll at 1s, 2s, 4s, 8s, max 30s).

## Queue Configuration

| Parameter | Recommendation | Reasoning |
|-----------|---------------|-----------|
| Queue type | SQS (standard) | At-least-once delivery, high throughput |
| Retention | 14 days | Enough time for reprocessing |
| Visibility timeout | 5× expected processing time | Prevents duplicate processing |
| Max concurrency | Queue depth × throughput | Auto-scale workers |
| DLQ retention | 14 days | Manual inspection + reprocessing |

## Error Handling

```python
def process_task(task):
    try:
        result = call_llm(task.input)
        send_to_response_queue(task.request_id, result)
    except TemporaryError as e:
        if task.retry_count < 3:
            requeue_with_backoff(task)
        else:
            send_to_dlq(task, str(e))
    except PermanentError as e:
        send_to_response_queue(task.request_id, {"error": str(e)})
```

## Monitoring

- Queue depth (alert if > 10k)
- Worker utilization (alert if > 80%)
- Processing time per task (p50, p95, p99)
- DLQ message count (alert if > 0)
- Age of oldest pending message

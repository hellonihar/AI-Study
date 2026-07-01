# Streaming and Async Best Practices

## Streaming Decision Guide

| Use Case | Sync | Streaming | Async |
|----------|------|-----------|-------|
| Chat interface | ❌ | ✅ (TTFT < 500ms) | ❌ |
| Document summarization | ⚠️ (long wait) | ✅ (progressive) | ✅ (queue) |
| Code generation | ❌ | ✅ | ❌ |
| Batch processing | ❌ | ❌ | ✅ |
| Real-time translation | ❌ | ✅ | ❌ |
| Webhook integrations | ❌ | ❌ | ✅ |

## Streaming Implementation

### Server-Sent Events (SSE)
- **Pros**: Simple, HTTP-native, auto-reconnect, works with any HTTP client
- **Cons**: Unidirectional (no client cancel), limited by proxy buffering
- **Best for**: Chat, real-time text generation

### WebSocket
- **Pros**: Bidirectional (client can cancel), lower overhead, full-duplex
- **Cons**: Requires WebSocket server, more complex client code
- **Best for**: Interactive apps, real-time editing, collaborative tools

## Backpressure Management

### Client-Side
- Implement flow control: ack each N tokens
- Set a maximum buffer size (e.g., 10,000 tokens)
- Display tokens progressively — don't wait for the full response

### Server-Side
- Detect slow consumers (TCP window closing)
- Buffer up to 1,000 tokens, then slow generation
- Drop connection if consumer is too slow (saves compute)

## Async Queue Configuration

| Parameter | Recommendation | Why |
|-----------|---------------|-----|
| Queue type | SQS, RabbitMQ, Redis Streams | Reliable, persistent |
| Max retries | 3 | Balance reliability vs. latency |
| Visibility timeout | 5× expected processing time | Prevent double-processing |
| Worker concurrency | Queue depth / processing time | Auto-scale via queue length |
| DLQ retention | 14 days | Manual inspection window |

## Pitfalls

### Streaming
- **Reverse proxy buffering**: Nginx/Apache may buffer SSE — disable buffering
- **Connection pooling**: Long-lived SSE connections exhaust pool — use dedicated pool
- **No resumption**: If connection drops mid-stream, client must re-request

### Async
- **Webhook reliability**: Webhooks can fail — retry with backoff, use idempotency keys
- **Polling overhead**: Exponential backoff reduces unnecessary polling
- **Queue poisoning**: A failing task stays in the queue — move to DLQ after N retries

## Monitoring

- Streaming: TTFT, tokens/second, early cancellation rate
- Async: Queue depth, processing time, age of oldest message, DLQ count

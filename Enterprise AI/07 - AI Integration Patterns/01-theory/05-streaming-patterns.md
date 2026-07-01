# Streaming Patterns

## Why Stream

- **Time-to-first-token (TTFT)**: Users see the first word in 200–500ms instead of waiting 5–30s for the full response
- **Perceived responsiveness**: Even slow generation feels fast with progressive output
- **Backpressure**: Client can signal stop mid-generation, saving cost
- **Progressive rendering**: Display partial results (e.g., markdown rendered incrementally)

## Streaming Protocols

### Server-Sent Events (SSE)
- Simple HTTP-based protocol
- One-directional (server → client)
- Native browser support (`EventSource` API)
- No special server required (standard HTTP)

```
data: {"token": "The", "index": 0}
data: {"token": " capital", "index": 1}
data: {"token": " of", "index": 2}
data: [DONE]
```

### WebSocket
- Bidirectional (client can cancel mid-stream)
- Lower overhead than HTTP for high-frequency messages
- Requires WebSocket server + client library
- Better for interactive applications (chat, real-time editing)

### Chunked Transfer Encoding (HTTP 1.1)
- Standard HTTP mechanism
- Server sends response in chunks
- Works with any HTTP library
- Simpler than SSE but lacks structured events

## Client-Side Patterns

```python
# SSE client
async for event in stream_response(prompt):
    if event.type == "token":
        print(event.data["token"], end="", flush=True)
    elif event.type == "done":
        print("\n[complete]")
    elif event.type == "error":
        print(f"\n[error: {event.data}]")
```

## Backpressure

When the client cannot keep up with the server:

- **Client-driven**: Client sends flow control signals (window size)
- **Server-driven**: Server buffers tokens, sends in batches
- **Hybrid**: Client periodically acknowledges receipt

For SSE, the TCP receive window provides natural backpressure. For WebSocket, implement explicit ack messages.

## Streaming + Tool Calling

Streaming doesn't mean you can't use tools:

1. Stream initial response tokens
2. When model emits a tool call, stop streaming and execute the tool
3. Append tool result, resume streaming
4. Repeat until final response

This pattern is used by ChatGPT, Claude, and most chat interfaces.

## Common Pitfalls

- **Buffering**: Ensure the server flushes after each token (not buffered by reverse proxy)
- **Connection loss**: Implement reconnection with last-token-id
- **State management**: Track what the client has received vs. what the server has sent
- **Cost**: Streaming uses the same token count as non-streaming — no cost savings from streaming alone

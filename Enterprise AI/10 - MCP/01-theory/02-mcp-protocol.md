# MCP Protocol

## Transport Layer

### STDIO Transport
The server runs as a subprocess. Communication flows over stdin (receiving requests) and stdout (sending responses). Stderr is reserved for logging.

```
Client (Host) ←→ Server (Subprocess)
                stdin: JSON-RPC requests
                stdout: JSON-RPC responses
                stderr: Server logs
```

### SSE Transport
The server runs as an HTTP server. The client connects via SSE for server-to-client messages and sends requests via HTTP POST.

```
Client → POST /message (JSON-RPC requests)
Server → SSE /events (JSON-RPC responses)
```

## Message Format

MCP uses JSON-RPC 2.0 as its message protocol.

### Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search",
    "arguments": {
      "query": "latest AI news"
    }
  }
}
```

### Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Search results for: latest AI news"
      }
    ],
    "isError": false
  }
}
```

### Notification (no response expected)
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/resources/list_changed",
  "params": {}
}
```

## Lifecycle

### Initialization
1. Client sends `initialize` with protocol version + capabilities
2. Server responds with its capabilities
3. Client sends `initialized` notification
4. Normal operation begins

### Operation
- Client sends tool calls, resource requests, prompt requests
- Server responds with results
- Server sends notifications for changes

### Shutdown
- Client or server closes the transport
- No formal shutdown sequence (cleanup happens on close)

## Capability Negotiation

During initialization, both sides declare capabilities:

```json
// Client capabilities
{
  "capabilities": {
    "roots": {
      "listChanged": true
    },
    "sampling": {}
  }
}

// Server capabilities
{
  "capabilities": {
    "tools": {
      "listChanged": true
    },
    "resources": {
      "subscribe": true,
      "listChanged": true
    },
    "prompts": {
      "listChanged": true
    }
  }
}
```

## Error Handling

Standard JSON-RPC error codes:

| Code | Meaning | When |
|------|---------|------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid request | Malformed request object |
| -32601 | Method not found | Unknown method |
| -32602 | Invalid params | Wrong parameter types |
| -32603 | Internal error | Server-side error |
| -32000+ | Custom errors | Application-specific |

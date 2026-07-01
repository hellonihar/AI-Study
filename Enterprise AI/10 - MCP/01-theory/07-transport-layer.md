# Transport Layer

## STDIO Transport

### How It Works
The MCP server runs as a subprocess. The parent process (client) communicates with it via standard input/output.

```
Client Process
    │
    ├── Spawn Server as Subprocess
    │   └── stdin: JSON-RPC requests
    │   └── stdout: JSON-RPC responses
    │   └── stderr: Logging (not protocol)
    │
    └── Read responses from stdout
```

### Implementation

```python
import asyncio
from mcp.client.stdio import stdio_client

async def connect_via_stdio():
    async with stdio_client(
        command=["python", "-m", "my_mcp_server"],
        env={"MY_CONFIG": "value"},
    ) as (read, write):
        # read: asyncio.StreamReader (server's stdout)
        # write: asyncio.StreamWriter (server's stdin)
        async with ClientSession(read, write) as session:
            await session.initialize()
            # ... use tools
```

### Pros and Cons
| Pro | Con |
|-----|-----|
| Simple, no network setup | Server tied to client lifecycle |
| Low latency (local IPC) | Cannot share server across clients |
| Secure (subprocess isolation) | Process management overhead |
| Works offline | Platform-dependent subprocess behavior |

## SSE Transport

### How It Works
The server runs as an HTTP server. Clients connect via Server-Sent Events for server-to-client messages and POST JSON-RPC requests.

```
Client                          Server
  │                               │
  ├── GET /events (SSE) ──────────┤
  │   (establish SSE connection)  │
  │                               │
  ├── POST /message (JSON-RPC) ───┤
  │   └── Request ID: 1          │
  │                               │
  │   ├── SSE: Response ID: 1 ────┤
  │   └── event: message         │
```

### Implementation

```python
# Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from uvicorn import run

sse = SseServerTransport("/message")

app = Starlette()
app.router.add_route("/events", endpoint=sse.handle_request)
app.router.add_route("/message", endpoint=handle_message, methods=["POST"])
```

### Pros and Cons
| Pro | Con |
|-----|-----|
| Remote access (network) | Requires HTTP server setup |
| Multiple clients per server | Higher latency than STDIO |
| Standard web infrastructure | Requires open port |
| Easier to scale | SSE is unidirectional (server→client) |

## Transport Selection Guide

| Factor | STDIO | SSE |
|--------|-------|-----|
| Deployment | Local only | Local or remote |
| Latency | <1ms | 1-10ms |
| Multiple clients | No | Yes |
| Process isolation | Yes | Via containerization |
| Setup complexity | Low | Medium |
| Authentication | OS-level | App-level |
| Scaling | Per-client process | Shared server |
| Offline capability | Yes | No (unless localhost) |

## Custom Transports

MCP's transport layer is extensible. You can implement custom transports:

```python
class CustomTransport:
    async def connect(self):
        # Establish connection
        pass

    async def read(self):
        # Read next message
        pass

    async def write(self, message):
        # Send message
        pass

    async def close(self):
        # Clean up
        pass
```

## Message Framing

For STDIO transport, messages are framed with a length prefix:

```
Content-Length: 123\r\n
\r\n
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
```

This ensures message boundaries are preserved across the stream.

## Connection Lifecycle

```
Client                       Server
  │                            │
  ├── Open transport ──────────┤
  │                            │
  ├── initialize ─────────────┤
  │   ├── Protocol version    │
  │   ├── Client capabilities │
  │   └── Server capabilities │
  │                            │
  ├── initialized ────────────┤
  │   (notification)          │
  │                            │
  ├── Normal operation ───────┤
  │   ├── tools/list          │
  │   ├── tools/call          │
  │   ├── resources/read      │
  │   └── prompts/get         │
  │                            │
  └── Close transport ────────┘
```

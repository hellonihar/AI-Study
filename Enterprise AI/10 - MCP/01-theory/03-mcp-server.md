# MCP Server

## Server Architecture

An MCP server is a lightweight program that:
1. Initializes connection with the client
2. Advertises capabilities (tools, resources, prompts)
3. Handles incoming requests
4. Sends notifications on state changes

## Creating a Server

### Python SDK
```python
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

async def main():
    server = Server("my-server")

    @server.tool()
    def my_tool(param: str) -> str:
        return f"Processed: {param}"

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="my-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
```

### TypeScript SDK
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "my-server",
  version: "1.0.0",
}, {
  capabilities: { tools: {} },
});

server.setRequestHandler("tools/call", async (request) => {
  return {
    content: [{ type: "text", text: "Hello!" }],
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Capability Registration

### Tools
```python
@server.tool()
def search(query: str, limit: int = 10) -> list[dict]:
    """Search the knowledge base for relevant documents."""
    results = db.search(query, limit=limit)
    return [{"title": r.title, "content": r.content} for r in results]
```

### Resources
```python
@server.resource("file://{path}")
def read_file(path: str) -> str:
    """Read a file from the local file system."""
    with open(path, "r") as f:
        return f.read()
```

### Prompts
```python
@server.prompt()
def code_review(code_file: str) -> str:
    """Generate a code review prompt for the given file."""
    return f"""
    Please review the following code file: {code_file}
    Focus on: security, performance, best practices, potential bugs.
    """
```

## Server Configuration

Servers are configured via JSON in the client's MCP configuration:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": ["-m", "mcp_server_filesystem"],
      "env": {
        "ALLOWED_DIRS": "/home/user/projects"
      }
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-database"],
      "env": {
        "DATABASE_URL": "postgresql://localhost:5432/mydb"
      }
    }
  }
}
```

## State Management

MCP servers can be stateless or stateful:

| Type | Description | Best For |
|------|-------------|----------|
| Stateless | No persistent state, each request independent | API wrappers, calculations |
| Stateful | Maintains connection state, database connections | Database servers, file system |
| Hybrid | Stateless with cache | Search servers, resource servers |

## Notifications

Servers can push notifications to clients:

```python
# Notify client that tool list changed
await server.request_context.session.send_notification(
    "notifications/tools/list_changed"
)
```

Notifications are fire-and-forget — the client does not respond, but may re-request capabilities.

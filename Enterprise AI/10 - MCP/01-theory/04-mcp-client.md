# MCP Client

## Client Architecture

An MCP client connects to one or more servers, manages the connection lifecycle, and exposes server capabilities to the host application.

## Creating a Client

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    # Create transport and session
    async with stdio_client(command=["python", "-m", "my_server"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            for tool in tools:
                print(f"Tool: {tool.name} - {tool.description}")

            # Call a tool
            result = await session.call_tool("search", {"query": "AI news"})
            print(result.content[0].text)
```

## Client Responsibilities

### 1. Connection Management
- Initialize connection with capability negotiation
- Handle reconnection on transport failure
- Manage timeout and backpressure

### 2. Capability Discovery
- List tools on connection
- Cache tool definitions
- Subscribe to capability change notifications

### 3. Request Execution
- Send tool call requests
- Handle responses and errors
- Manage concurrent requests

### 4. Resource Access
- List available resources
- Read resource contents
- Subscribe to resource changes

## Multi-Server Client

A host typically manages multiple MCP clients, one per server:

```python
class MCPHost:
    def __init__(self):
        self.sessions = {}

    async def connect_server(self, name, command, args):
        transport = await stdio_client(command, args)
        session = ClientSession(transport.read, transport.write)
        await session.initialize()
        self.sessions[name] = session

    async def call_tool(self, server_name, tool_name, arguments):
        session = self.sessions[server_name]
        return await session.call_tool(tool_name, arguments)

    async def list_all_tools(self):
        all_tools = {}
        for name, session in self.sessions.items():
            tools = await session.list_tools()
            all_tools[name] = tools
        return all_tools
```

## Error Handling

```python
async def safe_call_tool(session, tool_name, arguments):
    try:
        result = await session.call_tool(tool_name, arguments)
        if result.isError:
            print(f"Tool {tool_name} returned error: {result.content[0].text}")
            return None
        return result
    except TimeoutError:
        print(f"Tool {tool_name} timed out")
        return None
    except ConnectionError:
        print(f"Connection lost to server")
        # Trigger reconnection
        return None
```

## Client-Side Caching

Cache tool definitions and resource contents to reduce round-trips:

```python
class CachedClient:
    def __init__(self, session):
        self.session = session
        self.tool_cache = None
        self.resource_cache = {}

    async def list_tools(self):
        if not self.tool_cache:
            self.tool_cache = await self.session.list_tools()
        return self.tool_cache

    def invalidate_cache(self):
        self.tool_cache = None
```

## Configuration

Clients read MCP server configurations to know which servers to connect to:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-filesystem"],
      "env": {},
      "disabled": false,
      "autoApprove": ["read_file", "list_directory"]
    }
  }
}
```

The `autoApprove` array lists tools the user has pre-approved — tools not in this list require user consent before each invocation.

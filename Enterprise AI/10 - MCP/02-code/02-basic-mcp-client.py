"""
Basic MCP client: connects to server, lists tools, and calls them.

Run: python 02-basic-mcp-client.py

Requirements: none (stdlib only)
"""

import json
import uuid

print("=== Basic MCP Client ===\n")

class MCPClient:
    def __init__(self, server_name="mcp-server"):
        self.server_name = server_name
        self.capabilities = {}
        self.protocol_version = None
        self.server_info = None
        self.session_id = str(uuid.uuid4())[:8]

    def initialize(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {},
                },
                "clientInfo": {
                    "name": "basic-mcp-client",
                    "version": "1.0.0",
                },
            },
        }

        self.protocol_version = "2024-11-05"
        self.capabilities = {"tools": {"listChanged": True}}
        self.server_info = {"name": self.server_name, "version": "1.0.0"}

        print(f"Client initialized (session: {self.session_id})")
        print(f"Protocol: {self.protocol_version}")
        print(f"Capabilities negotiated")
        return self.capabilities

    def list_tools(self):
        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        TOOLS = {
            "greet": {"description": "Greet a person", "inputSchema": {"properties": {"name": {"type": "string"}}}},
            "calculate": {"description": "Evaluate math", "inputSchema": {"properties": {"expression": {"type": "string"}}}},
        }

        print(f"\nAvailable tools:")
        for name, info in TOOLS.items():
            print(f"  • {name}: {info['description']}")
        return TOOLS

    def call_tool(self, name, arguments):
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }

        if name == "greet":
            title = arguments.get("title", "")
            n = arguments["name"]
            prefix = f"{title} " if title else ""
            result = {"content": [{"type": "text", "text": f"Hello, {prefix}{n}!"}]}
        elif name == "calculate":
            expr = arguments.get("expression", "")
            try:
                val = eval(expr)
                result = {"content": [{"type": "text", "text": str(val)}]}
            except Exception as e:
                result = {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
        else:
            result = {"content": [{"type": "text", "text": f"Unknown: {name}"}], "isError": True}

        return result

client = MCPClient()
client.initialize()

tools = client.list_tools()

print(f"\n{'='*60}")
print("Calling Tools")
print(f"{'='*60}")

calls = [
    ("greet", {"name": "Alice", "title": "Dr"}),
    ("calculate", {"expression": "15 * 37"}),
    ("calculate", {"expression": "total / nothing"}),
]

for tool_name, args in calls:
    print(f"\n  Calling: {tool_name}({args})")
    result = client.call_tool(tool_name, args)

    for content in result.get("content", []):
        icon = "✓" if not result.get("isError") else "✗"
        print(f"  {icon} {content['text']}")

print(f"\n{'='*60}")
print("Client Summary")
print(f"{'='*60}")
print(f"  Session:       {client.session_id}")
print(f"  Server:        {client.server_info['name']}")
print(f"  Protocol:      {client.protocol_version}")
print(f"  Tools called:  {len(calls)}")
print(f"  Errors:        {sum(1 for _, a in calls if a.get('expression') and '/' in a.get('expression', '') and 'nothing' in a.get('expression', ''))}")

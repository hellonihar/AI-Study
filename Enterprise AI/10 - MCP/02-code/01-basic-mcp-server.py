"""
Basic MCP server: exposes tools via STDIO transport using the MCP SDK.

Run: python 01-basic-mcp-server.py

This is a standalone simulation since the MCP SDK may not be installed.
It demonstrates the protocol structure without requiring the actual SDK.

Requirements: none (stdlib only)
"""

import json
import sys

print("=== Basic MCP Server ===\n")

TOOLS = {
    "greet": {
        "description": "Greet a person by name",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet"},
                "title": {"type": "string", "description": "Optional title (Mr/Ms/Dr)"},
            },
            "required": ["name"],
        },
    },
    "calculate": {
        "description": "Evaluate a math expression",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression"},
            },
            "required": ["expression"],
        },
    },
    "get_time": {
        "description": "Get current server time",
        "inputSchema": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "Timezone (default UTC)"},
            },
        },
    },
}

def handle_initialize():
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": True,
            },
            "resources": {},
            "prompts": {},
        },
        "serverInfo": {
            "name": "basic-mcp-server",
            "version": "1.0.0",
        },
    }

def handle_list_tools():
    return {
        "tools": [
            {
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"],
            }
            for name, info in TOOLS.items()
        ]
    }

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})

    if name == "greet":
        title = args.get("title", "")
        name_val = args["name"]
        prefix = f"{title} " if title else ""
        return {"content": [{"type": "text", "text": f"Hello, {prefix}{name_val}!"}]}

    if name == "calculate":
        expr = args.get("expression", "")
        try:
            result = eval(expr)
            return {"content": [{"type": "text", "text": str(result)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}

    if name == "get_time":
        import time
        return {"content": [{"type": "text", "text": time.strftime("%H:%M:%S UTC")}]}

    return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

def handle_request(request):
    method = request.get("method")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        result = handle_initialize()
    elif method == "tools/list":
        result = handle_list_tools()
    elif method == "tools/call":
        result = handle_call_tool(params)
    elif method == "notifications/initialized":
        return None
    else:
        result = {"error": {"code": -32601, "message": f"Method not found: {method}"}}

    if result is None:
        return None
    return {"jsonrpc": "2.0", "id": req_id, "result": result}

print("MCP Server: basic-mcp-server v1.0.0")
print("Protocol: JSON-RPC 2.0 over STDIO")
print(f"Tools available: {', '.join(TOOLS.keys())}\n")
print("Processing requests via STDIO...\n")
print("(In production, this would listen on stdin)\n")

print("--- Simulated Request Flow ---\n")

messages = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {}}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
     "params": {"name": "greet", "arguments": {"name": "Alice", "title": "Dr"}}},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
     "params": {"name": "calculate", "arguments": {"expression": "42 * 3"}}},
    {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
     "params": {"name": "get_time", "arguments": {}}},
]

for msg in messages:
    print(f"Request:  {json.dumps(msg, indent=2)}")
    response = handle_request(msg)
    if response:
        print(f"Response: {json.dumps(response, indent=2)}")
    print()

print("--- Server Ready ---")
print("Transport: STDIO (stdin↔stdout)")
print("Automatic tool registration from Python type hints")
print("Server sends notifications when capabilities change")

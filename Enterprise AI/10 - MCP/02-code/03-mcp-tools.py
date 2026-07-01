"""
MCP tools: defining tools with parameter schemas and execution.

Run: python 03-mcp-tools.py

Requirements: none (stdlib only)
"""

import json
import re

print("=== MCP Tools ===\n")

class Tool:
    def __init__(self, name, description, handler, parameters=None):
        self.name = name
        self.description = description
        self.handler = handler
        self.parameters = parameters or {}

    def to_schema(self):
        schema = {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
        for name, info in self.parameters.items():
            param_schema = {"type": info.get("type", "string")}
            if "description" in info:
                param_schema["description"] = info["description"]
            if "default" in info:
                param_schema["default"] = info["default"]
            schema["inputSchema"]["properties"][name] = param_schema
            if info.get("required", False):
                schema["inputSchema"]["required"].append(name)
        return schema

TOOLS = [
    Tool(
        name="search_documents",
        description="Search internal documents by query. Returns matching document IDs and excerpts.",
        parameters={
            "query": {"type": "string", "description": "Search query", "required": True},
            "max_results": {"type": "integer", "description": "Max results (1-50)", "default": 10},
            "filters": {"type": "object", "description": "Optional filters (author, date_range)"},
        },
        handler=lambda query, max_results=10, filters=None: {
            "results": [{"id": f"doc-{i}", "title": f"Document about {query[:20]}", "score": 0.95 - i * 0.1}
                       for i in range(min(max_results, 3))],
            "total": 3,
        },
    ),
    Tool(
        name="send_email",
        description="Send an email to one or more recipients. Requires confirmation.",
        parameters={
            "to": {"type": "array", "description": "Recipient email addresses", "required": True},
            "subject": {"type": "string", "description": "Email subject line", "required": True},
            "body": {"type": "string", "description": "Email body text", "required": True},
            "priority": {"type": "string", "description": "Priority (low/normal/high)", "default": "normal"},
        },
        handler=lambda to, subject, body, priority="normal": {
            "status": "sent",
            "message_id": f"msg-{hash(subject) % 10000}",
            "recipients": to,
            "priority": priority,
        },
    ),
    Tool(
        name="analyze_sentiment",
        description="Analyze the sentiment of a text. Returns positive, negative, or neutral.",
        parameters={
            "text": {"type": "string", "description": "Text to analyze", "required": True},
        },
        handler=lambda text: {
            "sentiment": "positive" if any(w in text.lower() for w in ["good", "great", "excellent", "love"]) else "negative" if any(w in text.lower() for w in ["bad", "terrible", "hate", "awful"]) else "neutral",
            "confidence": 0.85,
            "text_length": len(text),
        },
    ),
]

class ToolRegistry:
    def __init__(self):
        self.tools = {t.name: t for t in TOOLS}

    def list_tools(self):
        return [t.to_schema() for t in self.tools.values()]

    def call_tool(self, name, arguments):
        tool = self.tools.get(name)
        if not tool:
            return {"error": {"code": -32602, "message": f"Unknown tool: {name}"}}

        validated = {}
        for param_name, info in tool.parameters.items():
            if param_name in arguments:
                validated[param_name] = arguments[param_name]
            elif "default" in info:
                validated[param_name] = info["default"]
            elif info.get("required"):
                return {"error": {"code": -32602, "message": f"Missing required: {param_name}"}}

        try:
            result = tool.handler(**validated)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}

registry = ToolRegistry()

print("Registered Tools:\n")
for tool_schema in registry.list_tools():
    print(f"  {tool_schema['name']}")
    print(f"    {tool_schema['description']}")
    props = tool_schema["inputSchema"]["properties"]
    required = tool_schema["inputSchema"]["required"]
    for name, info in props.items():
        req = " (required)" if name in required else f" (default: {info.get('default', 'none')})"
        print(f"    • {name} [{info['type']}]{req}")
    print()

print("Tool Calls:\n")
test_calls = [
    ("search_documents", {"query": "machine learning", "max_results": 5}),
    ("search_documents", {"query": "AI trends"}),
    ("analyze_sentiment", {"text": "I love this product! It works great."}),
    ("send_email", {"to": ["user@example.com"], "subject": "Test", "body": "Hello"}),
]

for name, args in test_calls:
    print(f"  Call: {name}({args.keys()})")
    result = registry.call_tool(name, args)
    text = result.get("content", [{}])[0].get("text", "")
    is_error = result.get("isError", False)
    icon = "✗" if is_error else "✓"
    print(f"  {icon} {text[:60]}")
    print()

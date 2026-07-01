"""
Tool-use agent: multiple tools with selection, execution, and error handling.

Run: python 03-tool-use-agent.py

Requirements: none (stdlib only)
"""

import json
import time
import random

print("=== Tool-Use Agent ===\n")

TOOLS = {
    "search_web": {
        "description": "Search the web for information",
        "parameters": {"query": "string"},
        "execute": lambda query: {"results": [f"Web result for: {query}"]},
    },
    "read_document": {
        "description": "Read a document by ID",
        "parameters": {"doc_id": "string"},
        "execute": lambda doc_id: {"content": f"Content of document {doc_id}"},
    },
    "send_email": {
        "description": "Send an email",
        "parameters": {"to": "string", "subject": "string", "body": "string"},
        "execute": lambda to, subject, body: {"status": "sent", "to": to},
    },
    "calculate": {
        "description": "Evaluate a math expression",
        "parameters": {"expression": "string"},
        "execute": lambda expression: {"result": eval(expression)},
    },
}

class ToolUseAgent:
    def __init__(self):
        self.step = 0
        self.max_steps = 10
        self.trace = []

    def select_tool(self, query):
        q = query.lower()
        if "search" in q or "find" in q or "lookup" in q:
            return "search_web", {"query": q.replace("search", "").replace("find", "").strip() or "general"}
        if "email" in q or "send" in q and "@" in q:
            return "send_email", {"to": "user@example.com", "subject": "AI Agent Message",
                                  "body": f"Response to: {query}"}
        if "calculate" in q or any(op in q for op in ["+", "-", "*", "/"]):
            parts = q.split()
            expr = parts[-1] if parts else "2+2"
            return "calculate", {"expression": expr}
        if "document" in q or "doc" in q or "read" in q:
            return "read_document", {"doc_id": "DOC-001"}
        return None, None

    def execute_tool(self, tool_name, params):
        if tool_name not in TOOLS:
            raise ValueError(f"Unknown tool: {tool_name}")
        tool = TOOLS[tool_name]

        validated = {}
        for key, expected_type in tool["parameters"].items():
            if key in params:
                validated[key] = params[key]
            else:
                validated[key] = None

        return tool["execute"](**validated)

    def run(self, query):
        print(f"Query: {query}\n")

        tool_name, params = self.select_tool(query)

        if not tool_name:
            print("  No matching tool found, responding directly")
            result = f"I understand: {query}"
            print(f"  Response: {result}")
            return result

        print(f"  Selected tool: {tool_name}")
        print(f"  Parameters: {params}")

        self.step += 1
        try:
            result = self.execute_tool(tool_name, params)
            print(f"  Result: {json.dumps(result)}")

            response = f"Used {tool_name}: {json.dumps(result)}"
            self.trace.append({
                "tool": tool_name,
                "params": params,
                "result": result,
                "status": "success",
            })

        except Exception as e:
            print(f"  Error: {e}")
            response = f"Error using {tool_name}: {e}"
            self.trace.append({
                "tool": tool_name,
                "params": params,
                "error": str(e),
                "status": "error",
            })

        print(f"\n  Final: {response}")
        return response

QUERIES = [
    "search for AI trends in 2024",
    "calculate 256 * 4",
    "send email to alice about project update",
    "Hello, how are you?",
]

for q in QUERIES:
    print("-" * 60)
    agent = ToolUseAgent()
    agent.run(q)
    print()

print(f"{'='*60}")
print("Tool Registry")
print(f"{'='*60}")
for name, tool in TOOLS.items():
    print(f"  {name}: {tool['description']} "
          f"(params: {list(tool['parameters'].keys())})")

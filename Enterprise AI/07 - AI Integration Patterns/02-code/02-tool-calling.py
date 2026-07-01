"""
Tool-calling agent: define tools, parse model calls, execute with error handling.

Run: python 02-tool-calling.py

Requirements: none (stdlib only)
"""

import json
import re
from datetime import datetime

print("=== Tool-Calling Agent ===\n")

TOOLS = {
    "search_knowledge_base": {
        "description": "Search internal documentation",
        "parameters": {
            "query": {"type": "string", "required": True},
            "top_k": {"type": "integer", "required": False, "default": 3},
        },
        "execute": lambda query, top_k=3: [
            {"title": "API Rate Limits", "score": 0.95},
            {"title": "Authentication Guide", "score": 0.88},
        ][:top_k],
    },
    "get_current_time": {
        "description": "Get current date and time",
        "parameters": {"timezone": {"type": "string", "required": False, "default": "UTC"}},
        "execute": lambda timezone="UTC": {
            "time": datetime.utcnow().isoformat(),
            "timezone": timezone,
        },
    },
    "calculate": {
        "description": "Evaluate a mathematical expression",
        "parameters": {"expression": {"type": "string", "required": True}},
        "execute": lambda expression: {"result": eval(expression)},
    },
}

def parse_tool_call(text):
    pattern = r"<tool_call>\s*(\w+)\s*(.*?)\s*</tool_call>"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return None

    tool_name = match.group(1)
    args_text = match.group(2).strip()

    if tool_name not in TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}

    tool_def = TOOLS[tool_name]
    params = tool_def["parameters"]
    parsed_args = {}

    for key, spec in params.items():
        val_pattern = rf'{key}\s*[:=]\s*"([^"]+)"'
        val_match = re.search(val_pattern, args_text)
        if val_match:
            if spec.get("type") == "integer":
                try:
                    parsed_args[key] = int(val_match.group(1))
                except ValueError:
                    parsed_args[key] = spec.get("default")
            else:
                parsed_args[key] = val_match.group(1)
        elif spec.get("required"):
            return {"error": f"Missing required parameter: {key}"}
        elif "default" in spec:
            parsed_args[key] = spec["default"]

    try:
        result = tool_def["execute"](**parsed_args)
        return {"success": True, "tool": tool_name, "result": result}
    except Exception as e:
        return {"error": f"Execution failed: {e}"}

def process_model_response(model_output):
    print(f"Model output: {model_output}\n")

    tool_call = parse_tool_call(model_output)
    if not tool_call:
        print("No tool call detected – treating as plain response")
        return model_output

    if "error" in tool_call:
        print(f"Error: {tool_call['error']}")
        return {"role": "tool", "content": f"Error: {tool_call['error']}"}

    print(f"Executing tool: {tool_call['tool']}")
    print(f"Parameters: {json.dumps(parsed_args, indent=2)}")
    print(f"Result: {json.dumps(tool_call['result'], indent=2)}")

    return {
        "role": "tool",
        "content": json.dumps(tool_call["result"]),
    }

MODEL_OUTPUTS = [
    '<tool_call> get_current_time timezone="UTC" </tool_call>',
    '<tool_call> search_knowledge_base query="API rate limits" top_k=2 </tool_call>',
    '<tool_call> nonexistent_tool arg1="val1" </tool_call>',
]

for output in MODEL_OUTPUTS:
    print("-" * 60)
    result = process_model_response(output)
    print()

print(f"\n{'='*60}")
print("Available Tools")
print(f"{'='*60}")
for name, tool in TOOLS.items():
    params = tool["parameters"]
    required = [k for k, v in params.items() if v.get("required")]
    optional = [k for k, v in params.items() if not v.get("required")]
    print(f"\n  {name}")
    print(f"    {tool['description']}")
    print(f"    Required params: {required or 'none'}")
    print(f"    Optional params: {optional or 'none'}")

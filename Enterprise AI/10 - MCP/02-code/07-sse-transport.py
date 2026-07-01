"""
SSE transport: simulate MCP server over Server-Sent Events.

Run: python 07-sse-transport.py

Requirements: none (stdlib only)
"""

import json
import time
from datetime import datetime

print("=== SSE Transport Simulation ===\n")

class SSEServer:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port
        self.event_buffer = []
        self.event_id = 0

    def send_event(self, event_type, data):
        self.event_id += 1
        event = {
            "id": self.event_id,
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        self.event_buffer.append(event)

        sse_format = f"id: {event['id']}\nevent: {event_type}\ndata: {json.dumps(data)}\n\n"
        return sse_format

    def handle_connect(self, client_id):
        self.send_event("endpoint", {"url": f"http://{self.host}:{self.port}/message"})

    def handle_tool_call(self, name, arguments):
        if name == "greet":
            result = {"content": [{"type": "text", "text": f"Hello, {arguments.get('name', 'World')}!"}]}
        elif name == "time":
            result = {"content": [{"type": "text", "text": datetime.now().isoformat()}]}
        else:
            result = None

        if result:
            self.send_event("message", {
                "type": "response",
                "result": result,
            })

server = SSEServer()

print("SSE Connection Flow:\n")

client_id = "client-001"

print(f"1. Client connects to SSE endpoint:")
print(f"   GET http://{server.host}:{server.port}/events")
print()

sse = server.handle_connect(client_id)
print(f"   Server sends endpoint event:")
print(f"   {sse[:80]}...")
print()

print(f"2. Client POSTs tool call to message endpoint:")
print(f"   POST http://{server.host}:{server.port}/message")
tool_call = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {"name": "greet", "arguments": {"name": "Alice"}},
}
print(f"   Body: {json.dumps(tool_call)}")
print()

server.handle_tool_call("greet", {"name": "Alice"})

print(f"3. Server sends response via SSE:")
sse = server.send_event("message", {
    "type": "response",
    "result": {"content": [{"type": "text", "text": "Hello, Alice!"}]},
})
print(f"   {sse[:120]}...")
print()

print(f"4. Server can send notifications anytime:")
sse = server.send_event("tools/list_changed", {})
print(f"   {sse[:100]}...")
print()

print(f"{'='*60}")
print("SSE vs STDIO Comparison")
print(f"{'='*60}")
print(f"  {'Feature':<20} {'STDIO':<25} {'SSE':<25}")
print(f"  {'-'*68}")
print(f"  {'Transport':<20} {'Subprocess pipe':<25} {'HTTP + SSE':<25}")
print(f"  {'Multi-client':<20} {'No':<25} {'Yes':<25}")
print(f"  {'Remote access':<20} {'No':<25} {'Yes':<25}")
print(f"  {'Server-side':<20} {'Client controls':<25} {'Server controls':<25}")
print(f"  {'Latency':<20} {'<1ms':<25} {'1-10ms':<25}")
print(f"  {'Setup':<20} {'Minimal':<25} {'HTTP server':<25}")
print(f"  {'Security':<20} {'OS-level':<25} {'Application-level':<25}")

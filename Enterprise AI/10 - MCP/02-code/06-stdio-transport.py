"""
STDIO transport: simulate MCP communication over stdin/stdout.

Run: python 06-stdio-transport.py

Requirements: none (stdlib only)
"""

import json
import sys
import time

print("=== STDIO Transport Simulation ===\n")

class STDIOTransport:
    def __init__(self, server_name="stdio-server"):
        self.server_name = server_name
        self.buffer = []
        self.request_id = 0

    def send(self, message):
        content = json.dumps(message)
        frame = f"Content-Length: {len(content)}\r\n\r\n{content}"
        self.buffer.append(frame)
        return frame

    def receive(self, frame):
        if "\r\n\r\n" in frame:
            header, body = frame.split("\r\n\r\n", 1)
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}
        return None

    def create_request(self, method, params=None):
        self.request_id += 1
        return {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {},
        }

    def create_response(self, req_id, result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def create_error(self, req_id, code, message):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

transport = STDIOTransport()

print("STDIO Transport Demo\n")

print("Client → Server (initialization):")
msg = transport.create_request("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test-client", "version": "1.0"},
})
frame = transport.send(msg)
print(f"  {frame[:100]}...")
print()

parsed = transport.receive(frame)
print(f"  Parsed: method={parsed['method']}, id={parsed['id']}")

response = transport.create_response(parsed["id"], {
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {"listChanged": True}},
    "serverInfo": {"name": transport.server_name, "version": "1.0"},
})
print(f"  Response: {json.dumps(response)}")

print(f"\nClient → Server (tool call):")
msg = transport.create_request("tools/call", {
    "name": "greet",
    "arguments": {"name": "World"},
})
frame = transport.send(msg)
print(f"  Sent: method={msg['method']}, args={msg['params']['arguments']}")

parsed = transport.receive(frame)
response = transport.create_response(parsed["id"], {
    "content": [{"type": "text", "text": "Hello, World!"}],
})
print(f"  Response: {json.dumps(response)}")

print(f"\nClient → Server (unknown method):")
msg = transport.create_request("tools/unknown", {})
frame = transport.send(msg)
parsed = transport.receive(frame)
error = transport.create_error(parsed["id"], -32601, "Method not found: tools/unknown")
print(f"  Error: {json.dumps(error)}")

print(f"\n{'='*60}")
print("STDIO Transport Protocol")
print(f"{'='*60}")
print("  Frame format:")
print("    Content-Length: <bytes>")
print("    <empty line>")
print("    <JSON message>")
print()
print("  Client writes to stdin")
print("  Server writes to stdout")
print("  Server writes logs to stderr")
print()
print("  Lifecycle:")
print("    1. Client sends 'initialize'")
print("    2. Server responds with capabilities")
print("    3. Client sends 'notifications/initialized'")
print("    4. Normal tool/resource/prompt operations")

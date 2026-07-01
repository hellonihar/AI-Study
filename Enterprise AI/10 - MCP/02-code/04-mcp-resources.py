"""
MCP resources: resource templates, static resources, and content access.

Run: python 04-mcp-resources.py

Requirements: none (stdlib only)
"""

import json
import re
from datetime import datetime

print("=== MCP Resources ===\n")

class Resource:
    def __init__(self, uri, name, description, mime_type="text/plain"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type

class ResourceTemplate:
    def __init__(self, uri_template, name_template, handler):
        self.uri_template = uri_template
        self.name_template = name_template
        self.handler = handler

STATIC_RESOURCES = [
    Resource("config://app/settings", "App Settings", "Application configuration", "application/json"),
    Resource("config://app/version", "App Version", "Current version info", "text/plain"),
    Resource("docs://README", "README", "Project documentation", "text/markdown"),
]

TEMPLATES = [
    ResourceTemplate(
        uri_template="file://{path}",
        name_template="File: {path}",
        handler=lambda path: {
            "content": f"Contents of file: {path}\n\nThis is a simulated file read for {path}.",
            "mimeType": "text/plain",
        },
    ),
    ResourceTemplate(
        uri_template="db://{table}/{id}",
        name_template="DB Record: {table}/{id}",
        handler=lambda table, id: {
            "content": json.dumps({
                "table": table,
                "id": int(id),
                "data": f"Sample record from {table}",
                "created_at": datetime.now().isoformat(),
            }, indent=2),
            "mimeType": "application/json",
        },
    ),
    ResourceTemplate(
        uri_template="log://{date}",
        name_template="Log: {date}",
        handler=lambda date: {
            "content": f"[{date} 10:00:00] INFO: System started\n[{date} 10:00:01] INFO: Connection established\n[{date} 10:00:02] WARN: High memory usage detected",
            "mimeType": "text/plain",
        },
    ),
]

class ResourceManager:
    def __init__(self):
        self.static = {r.uri: r for r in STATIC_RESOURCES}
        self.templates = TEMPLATES

    def list_resources(self):
        return [
            {"uri": r.uri, "name": r.name, "description": r.description, "mimeType": r.mime_type}
            for r in self.static.values()
        ]

    def read_resource(self, uri):
        if uri in self.static:
            resource = self.static[uri]
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": resource.mime_type,
                    "text": f"Content of {uri}: simulated data at {datetime.now().isoformat()}",
                }]
            }

        for template in self.templates:
            pattern = template.uri_template.replace("{", "(?P<").replace("}", ">[^/]+)")
            match = re.match(f"^{pattern}$", uri)
            if match:
                result = template.handler(**match.groupdict())
                return {
                    "contents": [{
                        "uri": uri,
                        "mimeType": result["mimeType"],
                        "text": result["content"],
                    }]
                }

        return {"error": {"code": -32602, "message": f"Resource not found: {uri}"}}

manager = ResourceManager()

print("Static Resources:\n")
for r in manager.list_resources():
    print(f"  {r['uri']:<40} {r['name']:<30} ({r['mimeType']})")

print("\nResource Templates:\n")
for t in TEMPLATES:
    print(f"  {t.uri_template:<40} {t.name_template}")

print(f"\n{'='*60}")
print("Reading Resources")
print(f"{'='*60}")

uris = [
    "config://app/version",
    "file:///home/user/config.json",
    "db://users/42",
    "log://2024-12-01",
    "nonexistent://resource",
]

for uri in uris:
    print(f"\n  Read: {uri}")
    result = manager.read_resource(uri)
    if "error" in result:
        print(f"  ✗ {result['error']['message']}")
    else:
        content = result["contents"][0]
        print(f"  ✓ Type: {content['mimeType']}")
        print(f"    {content['text'][:60]}...")

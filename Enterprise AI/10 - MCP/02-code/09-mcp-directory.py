"""
MCP server directory: registry, discovery, and connection management.

Run: python 09-mcp-directory.py

Requirements: none (stdlib only)
"""

import json
import re

print("=== MCP Server Directory ===\n")

class MCPServerEntry:
    def __init__(self, name, description, command, args=None, env=None,
                 tools=None, resources=None, prompts=None):
        self.name = name
        self.description = description
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.tools = tools or []
        self.resources = resources or []
        self.prompts = prompts or []
        self.disabled = False

    def to_config(self):
        return {
            "command": self.command,
            "args": self.args,
            "env": self.env if self.env else None,
            "disabled": self.disabled,
        }

class MCPServerDirectory:
    def __init__(self):
        self.servers = {}

    def register(self, entry):
        self.servers[entry.name] = entry
        return entry

    def get(self, name):
        return self.servers.get(name)

    def list_available(self):
        return [s for s in self.servers.values() if not s.disabled]

    def search(self, query):
        q = query.lower()
        return [s for s in self.servers.values()
                if q in s.name.lower() or q in s.description.lower()
                or any(q in t.lower() for t in s.tools)]

    def generate_config(self):
        config = {"mcpServers": {}}
        for name, server in self.servers.items():
            if not server.disabled:
                config["mcpServers"][name] = server.to_config()
        return config

directory = MCPServerDirectory()

directory.register(MCPServerEntry(
    name="filesystem",
    description="Read, write, and manage files on the local file system",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"],
    tools=["read_file", "write_file", "list_directory", "search_files"],
    resources=["file://"],
))

directory.register(MCPServerEntry(
    name="database",
    description="Query and explore database schemas and data",
    command="python",
    args=["-m", "mcp_database_server"],
    env={"DATABASE_URL": "postgresql://localhost:5432/mydb"},
    tools=["query", "list_tables", "describe_table", "execute_sql"],
))

directory.register(MCPServerEntry(
    name="web_search",
    description="Search the web and extract content from pages",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-web-search"],
    env={"SEARCH_API_KEY": "${SEARCH_API_KEY}"},
    tools=["search", "fetch_page", "extract_content"],
))

directory.register(MCPServerEntry(
    name="github",
    description="Interact with GitHub repositories and issues",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_TOKEN": "${GITHUB_TOKEN}"},
    tools=["list_repos", "get_file", "search_code", "create_issue", "list_issues"],
    resources=["github://"],
))

directory.register(MCPServerEntry(
    name="slack",
    description="Send messages and search Slack channels",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-slack"],
    env={"SLACK_TOKEN": "${SLACK_TOKEN}"},
    tools=["send_message", "search_messages", "list_channels"],
))

print("Registered Servers:\n")
for server in directory.list_available():
    status = "enabled"
    print(f"  {server.name:<15} [{status}]")
    print(f"    {server.description}")
    print(f"    Command: {server.command} {' '.join(server.args[:3])}...")
    print(f"    Tools: {', '.join(server.tools[:3])}...")
    print()

print("--- Search Results ---\n")

searches = ["file", "database", "search", "git"]
for s in searches:
    results = directory.search(s)
    print(f"  Search '{s}': found {len(results)} server(s)")
    for r in results:
        print(f"    • {r.name}: {r.description[:50]}")
    print()

print(f"{'='*60}")
print("Generated MCP Configuration")
print(f"{'='*60}")
config = directory.generate_config()
print(json.dumps(config, indent=2))

print(f"\n{'='*60}")
print("Server Directory Summary")
print(f"{'='*60}")
print(f"  Total servers: {len(directory.servers)}")
print(f"  Available:     {len(directory.list_available())}")
print(f"  Config file:   ~/.config/anthropic/mcp.json")
print(f"  Format:        JSON-RPC 2.0 over STDIO or SSE")

# MCP Overview

## What is MCP?

The Model Context Protocol (MCP) is an open standard that standardizes how AI applications (hosts, clients) connect with external tools, data sources, and services (servers). Think of it as "USB-C for AI" — a universal protocol that replaces fragmented, custom integrations.

## Core Concepts

### Host
An AI application that initiates connections to MCP servers. Examples: Claude Desktop, Cursor, VS Code extensions, custom apps.

### Client
Within a host, a client maintains a one-to-one connection with an MCP server.

### Server
A lightweight program that exposes capabilities (tools, resources, prompts) to clients via the MCP protocol.

```
Host (Claude Desktop)
  ├── Client ─── MCP Server A (File System)
  │               └── Tools: read, write, list
  │               └── Resources: directory listings
  │               └── Prompts: code review, file summary
  │
  ├── Client ─── MCP Server B (Database)
  │               └── Tools: query, execute
  │               └── Resources: table schemas
  │
  └── Client ─── MCP Server C (Web APIs)
                  └── Tools: search, fetch, scrape
                  └── Resources: API documentation
```

## Why MCP Matters

### Before MCP
- Every AI app had custom integrations for tools, databases, and APIs
- No standard way for tools to advertise capabilities
- Every provider built their own plugin system
- Switching AI apps meant rebuilding integrations

### After MCP
- Universal standard for tool integration
- Servers are portable across any MCP-compatible host
- Tools self-describe their capabilities
- Community-shared server ecosystem

## Protocol Primitives

MCP defines three primary capabilities servers can expose:

| Primitive | Purpose | Example |
|-----------|---------|---------|
| **Tools** | Actions the LLM can invoke (callable functions) | Search, calculate, query DB |
| **Resources** | Data the LLM can read (files, records, docs) | File contents, table rows, documents |
| **Prompts** | Pre-defined templates the LLM can use | Code review prompt, summary template |

## Transport Layer

MCP supports two transport modes:

| Transport | Description | Best For |
|-----------|-------------|----------|
| **STDIO** | Server runs as subprocess, communication via stdin/stdout | Local development, bundled servers |
| **SSE** | Server runs as HTTP server with Server-Sent Events | Remote servers, multi-client access |

## Getting Started

```
pip install mcp  # Python SDK
npx @anthropic-ai/mcp-server  # TypeScript SDK
```

A minimal MCP server in Python:
```python
from mcp.server import Server

app = Server("minimal")

@app.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

## MCP in the AI Ecosystem

MCP sits between the AI application (host) and the external world (tools, data):

```
AI Application (Host)
    │
    ▼
    MCP Protocol
    │
    ├── Tool Servers (search, code, APIs)
    ├── Data Servers (databases, file systems)
    ├── Prompt Servers (templates, workflows)
    └── Composite Servers (combine all three)
```

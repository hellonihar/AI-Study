# MCP Tools and Examples

## Server Examples

| Server | Capability | Transport |
|--------|------------|-----------|
| Filesystem | Read, write, search files | stdio |
| GitHub | Repository operations, issues, PRs | HTTP/SSE |
| PostgreSQL | Query, schema, migrations | stdio |
| SQLite | Local database management | stdio |
| Memory | Persistent key-value store | stdio |
| Puppeteer | Browser automation | stdio |
| Slack | Messaging, channels, search | HTTP/SSE |
| Google Drive | File listing, search, read | HTTP/SSE |
| Notion | Pages, databases, search | HTTP/SSE |

## Development Tools

| Tool | Purpose |
|------|---------|
| `mcp-cli` | Test MCP servers from command line |
| `mcp-inspector` | Debug MCP server communications |
| MCP Extension for VS Code | Integrate MCP tools directly into editor |
| Inspector (Web UI) | Visual MCP debugging interface |
| Load testing framework | Benchmark server performance |

## Getting Started

```bash
# Install Python SDK
pip install mcp

# Run a basic server
python -m mcp_server_filesystem --allowed-dirs /tmp

# Test with CLI
mcp-cli call filesystem read_file --path /tmp/test.txt
```

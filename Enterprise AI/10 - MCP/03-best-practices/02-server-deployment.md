# MCP Server Deployment

## Infrastructure Options

| Approach | Best For | Complexity |
|----------|----------|------------|
| Subprocess | Single-machine, dev/CI | Low |
| Docker container | Production, isolated | Medium |
| Kubernetes pod | Scalable, orchestrated | High |
| Serverless function | Event-driven, low traffic | Medium |
| Sidecar | Co-located with app | Medium |

## Configuration

```jsonc
// mcp-servers.json — server registry
{
  "servers": [
    {
      "name": "filesystem",
      "command": "python -m mcp_server_filesystem",
      "args": ["--allowed-dirs", "/data,/tmp"],
      "env": { "LOG_LEVEL": "info" },
      "timeout": 30,
      "retry": { "max_retries": 3, "backoff": "exponential" }
    },
    {
      "name": "database",
      "transport": "stdio",
      "allowed_tools": ["query", "schema_list"],
      "rate_limit": 100
    }
  ]
}
```

## Health Checks

| Check | Frequency | Action |
|-------|-----------|--------|
| Process alive | 30s | Restart if dead |
| Responds to ping | 60s | Log warning, then restart |
| Tool invocation | 5m | Run known-good tool, verify output |
| Resource access | 1h | Verify all registered resources are accessible |

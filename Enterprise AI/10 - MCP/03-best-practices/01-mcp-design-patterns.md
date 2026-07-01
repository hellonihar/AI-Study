# MCP Design Best Practices

## Server Design

| Principle | Rationale |
|-----------|-----------|
| Single responsibility | One server per capability domain (filesystem, database, API) |
| Stateless when possible | Easier scaling, simpler error recovery |
| Idempotent operations | Safe to retry on network failures |
| Graceful degradation | Return partial results instead of failing entirely |
| Resource pagination | Support offset/limit for large result sets |
| Type-safe schemas | Use JSON Schema for all tool parameters and resource shapes |

## Security

| Practice | Implementation |
|----------|---------------|
| Least privilege | Each server bound to specific directories, APIs, or DB schemas |
| Input validation | Validate all parameters against schema before execution |
| Rate limiting | Per-client limits to prevent abuse |
| Audit logging | Log all tool invocations with client ID, timestamp, parameters |
| Secrets management | Use environment variables or secret stores, never hardcode |
| Authentication | Validate client tokens/keys on every request |
| Output sanitization | Strip sensitive data before returning results |

## Client Integration

| Pattern | Description |
|---------|-------------|
| Connection pooling | Reuse server connections to reduce latency |
| Timeout management | Set per-invocation timeouts, retry on transient failures |
| Error classification | Distinguish client errors (400) from server errors (500) |
| Fallback chain | Try primary server, fall back to degraded mode |
| Discovery caching | Cache server capabilities and refresh periodically |

# Security and Authentication

## Security Model

MCP's security model delegates security to the transport layer and the host application. The protocol itself does not define authentication or authorization — it provides hooks for servers to implement their own.

## Threat Model

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Unauthorized tool access | Malicious client calls dangerous tools | Authentication, consent prompts |
| Data exfiltration | Server reads sensitive files | Path validation, access control |
| Injection attacks | Malicious parameters passed to tools | Input validation, parameterized queries |
| Server impersonation | Fake server intercepts requests | TLS, certificate verification |
| Privilege escalation | Tool accesses resources beyond scope | Least-privilege design |

## Authentication Patterns

### Transport-Level (STDIO)
STDIO transport authenticates via OS process isolation. The server inherits the client's permissions.

### API Key (SSE)
```python
@server.tool()
def sensitive_operation(token: str, data: str) -> str:
    """Token passed from client, validated server-side."""
    if not validate_token(token):
        return "Error: Unauthorized"
    # Process request
    return "Operation completed"
```

### OAuth 2.0 / Bearer Tokens
SSE servers can use standard HTTP authentication:

```python
from fastapi import Header, HTTPException

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)
    token = authorization.split(" ")[1]
    if not validate_token(token):
        raise HTTPException(status_code=403)
```

## Authorization

### Scopes
Define granular permissions per tool:

```python
TOOL_SCOPES = {
    "read_file": {"scope": "files:read", "auto_approve": True},
    "write_file": {"scope": "files:write", "auto_approve": False},
    "delete_file": {"scope": "files:delete", "auto_approve": False},
    "search": {"scope": "search:execute", "auto_approve": True},
}
```

### Consent Model
Tools that modify state should require explicit user consent:

```
Tool: write_file
Arguments: { path: "/home/user/config.json", content: "..." }
Requesting user approval...
[Approve] [Deny]
```

## Input Validation

### Path Traversal Prevention
```python
import os

ALLOWED_DIRS = ["/home/user/projects", "/tmp/work"]

def safe_path(path):
    abs_path = os.path.abspath(os.path.expanduser(path))
    for allowed in ALLOWED_DIRS:
        if abs_path.startswith(os.path.abspath(allowed)):
            return abs_path
    raise ValueError(f"Access denied: {path}")
```

### SQL Injection Prevention
```python
@server.tool()
def query_database(sql: str) -> list:
    """NEVER interpolate user input directly into SQL."""
    # Use parameterized queries only
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
```

## Environment Isolation

### STDIO Isolation
- Server runs in a separate process
- Limited to the user's permissions
- Environment variables control access

### Container Isolation
```dockerfile
FROM python:3.12-slim
COPY --chown=app:app server.py /app/
USER app
WORKDIR /app
CMD ["python", "server.py"]
```

```json
{
  "mcpServers": {
    "database": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "mcp-database-server"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432"
      }
    }
  }
}
```

## Security Checklist

- [ ] Path traversal protection for file access
- [ ] Parameterized queries for database operations
- [ ] Input validation for all tool parameters
- [ ] Authentication for remote (SSE) servers
- [ ] Least-privilege file system access
- [ ] Sensitive tool requires user consent
- [ ] Rate limiting on tool calls
- [ ] Audit logging for all operations
- [ ] TLS for network transport
- [ ] Environment variable isolation for secrets

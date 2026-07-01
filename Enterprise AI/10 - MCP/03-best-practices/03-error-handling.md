# MCP Error Handling

## Error Response Format

```jsonc
{
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "Parameter 'path' must be an absolute path",
    "details": {
      "parameter": "path",
      "received": "relative/path",
      "schema": { "pattern": "^/" }
    }
  }
}
```

## Standard Error Codes

| Code | HTTP Analog | Meaning |
|------|-------------|---------|
| INVALID_PARAMETERS | 400 | Parameter validation failed |
| NOT_FOUND | 404 | Resource does not exist |
| PERMISSION_DENIED | 403 | Client not authorized |
| RATE_LIMITED | 429 | Client exceeded quota |
| INTERNAL_ERROR | 500 | Server-side failure |
| TIMEOUT | 504 | Operation exceeded deadline |
| UNAVAILABLE | 503 | Server overloaded or in maintenance |

## Retry Strategy

| Scenario | Retry? | Strategy |
|----------|--------|----------|
| INVALID_PARAMETERS | No | Client error, fix request |
| NOT_FOUND | No | Resource doesn't exist |
| PERMISSION_DENIED | No | Auth issue |
| RATE_LIMITED | Yes | Exponential backoff |
| INTERNAL_ERROR | Yes | Max 3 retries with backoff |
| TIMEOUT | Yes | Increase timeout, max 2 retries |
| UNAVAILABLE | Yes | Circuit breaker, max 5 retries |

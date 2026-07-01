# Tools and Resources

## Tools

Tools are callable functions that an MCP server exposes to the LLM. The LLM decides when to call a tool based on the tool's description and parameter schema.

### Tool Definition

```python
@server.tool()
def search_products(
    query: str,
    category: str = None,
    max_results: int = 10,
) -> list[dict]:
    """
    Search the product catalog.

    Args:
        query: Search query string
        category: Optional product category filter
        max_results: Maximum number of results (1-50)

    Returns:
        List of matching products with id, name, price, and description
    """
    results = catalog.search(query, category=category, limit=max_results)
    return [p.to_dict() for p in results]
```

### Tool Schema (auto-generated from type hints)

```json
{
  "name": "search_products",
  "description": "Search the product catalog.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query string"
      },
      "category": {
        "type": "string",
        "description": "Optional product category filter"
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of results (1-50)",
        "default": 10
      }
    },
    "required": ["query"]
  }
}
```

## Resources

Resources are data that the LLM can read. They are identified by URI templates.

### Static Resources

```python
@server.resource("config://app")
def get_config() -> str:
    """Application configuration."""
    return json.dumps(app_config, indent=2)
```

### Dynamic Resources (URI Templates)

```python
@server.resource("file://{path}")
def read_file(path: str) -> str:
    """
    Read a file from the file system.

    Supported paths:
    - file:///home/user/projects/... (absolute)
    - file://./relative/path (relative to allowed root)
    """
    safe_path = validate_path(path)
    with open(safe_path, "r") as f:
        return f.read()
```

### Resource Templates

Resource templates use URI Template syntax (RFC 6570):

| Template | Example | Matches |
|----------|---------|---------|
| `file://{path}` | `file:///home/user/config.json` | Any file path |
| `db://{table}/{id}` | `db://users/123` | Specific table row |
| `search://{query}` | `search://latest+AI+papers` | Search result |

## Tool vs Resource Decision

| Criteria | Use Tool | Use Resource |
|----------|----------|--------------|
| Has side effects | ✅ | ❌ |
| Takes parameters | ✅ | Only path params |
| Returns structured data | ✅ | Usually text |
| LLM needs to browse | ❌ | ✅ |
| Needs confirmation | ✅ | Usually not |
| Read-only | Optional | Always |

## Content Types

MCP supports multiple content types for tool results and resource contents:

```json
{
  "content": [
    {"type": "text", "text": "Plain text content"},
    {"type": "image", "data": "base64...", "mimeType": "image/png"},
    {"type": "resource", "resource": {"uri": "ref://doc-1", "text": "..."}}
  ]
}
```

## Resource Subscriptions

Clients can subscribe to resource changes:

```python
# Client subscribes
await session.subscribe_resource("file:///config.json")

# Server notifies on change
await session.send_notification(
    "notifications/resources/updated",
    {"uri": "file:///config.json"}
)
```

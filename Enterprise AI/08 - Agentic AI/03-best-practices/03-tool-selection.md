# Tool Selection Best Practices

## Tool Catalog Design

### Optimal Tool Count
- **Minimum**: 3–5 tools (simple agents)
- **Optimal**: 8–15 tools (most production agents)
- **Maximum**: 20+ tools (requires hierarchical tool organization)

### Naming Conventions
- Use `snake_case` verb phrases: `search_knowledge_base`, `send_email`, `calculate_expression`
- Avoid generic names: `run` or `execute` are too ambiguous
- Be specific: `search_employee_directory` not `search`

### Description Quality
Poor: `"Search for information"`
Good: `"Search the internal knowledge base for company policies, procedures, and documentation. Returns relevant document excerpts with source URLs."`

## Tool Schema Best Practices

```python
{
    "name": "search_customers",
    "description": "Search customer records by name, email, or ID. "
                   "Returns matching customer profiles.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query: name, email, or customer ID"
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (1-20)",
                "default": 10
            }
        },
        "required": ["query"]
    }
}
```

## Error Handling Patterns

### Tool-Level
```python
def search_knowledge_base(query):
    try:
        return internal_search(query)
    except TimeoutError:
        return {"error": "timeout", "fallback": cached_results(query)}
    except RateLimitError:
        time.sleep(1)
        return search_knowledge_base(query)  # retry once
    except Exception as e:
        return {"error": str(e), "suggestion": "Try search_web instead"}
```

### Agent-Level
```python
def handle_tool_error(tool_name, error, step_count):
    if step_count < 3:
        return f"Tool {tool_name} error: {error}. Try again."
    else:
        return f"Tool {tool_name} failed repeatedly. Try a different tool."
```

## Tool Composition

Group primitive tools into higher-level capabilities:

| Primitive Tools | Composed Tool |
|----------------|---------------|
| `search`, `extract_urls`, `scrape` | `research_topic()` |
| `get_customer`, `get_orders`, `calculate_total` | `customer_360()` |
| `read_file`, `analyze_sentiment`, `summarize` | `analyze_document()` |

## Tool Discovery

Agents should be able to discover available tools:

```python
TOOL_REGISTRY = [
    {"name": "search", "description": "..."},
    {"name": "calculate", "description": "..."},
]

# Agent can ask: "What tools are available?"
# Response: List of tool names + descriptions
```

## Testing Tools

- Unit test each tool in isolation
- Test with invalid parameters (missing required, wrong types)
- Test timeout behavior (tool should return error, not hang)
- Test concurrent tool calls (thread safety)

# Tool-Calling Agents

## Overview

Tool calling (function calling) lets LLMs invoke external APIs, databases, and services. The model outputs structured JSON describing which tool to call and with what parameters. Your application executes the tool and returns the result back to the model.

## Architecture

```
User → LLM → tool_call(tool_name, args) → Executor → result → LLM → final_response
```

### Components

1. **Tool Definition**: JSON Schema describing name, description, and parameters
2. **Tool Executor**: Runtime that validates args, calls the function, handles errors
3. **Context Manager**: Tracks previous tool calls and results for multi-turn interactions
4. **Error Handler**: Recovers from tool failures (timeout, invalid args, service down)

## Tool Schema Design

Every tool needs:
- **Name**: snake_case, unique, descriptive
- **Description**: Clear enough for the model to choose correctly
- **Parameters**: Strict JSON Schema with types, descriptions, and required/optional
- **Returns**: Structured response the model can consume

```json
{
  "name": "search_documents",
  "description": "Search internal knowledge base for relevant documents",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Search query"},
      "top_k": {"type": "integer", "description": "Number of results"}
    },
    "required": ["query"]
  }
}
```

## Execution Patterns

### Sequential Tool Calling
Model calls one tool, gets result, then calls the next. Simple and predictable.

### Parallel Tool Calling
Model calls multiple independent tools simultaneously. Reduces latency by 2–5x for independent queries.

### Recursive Tool Calling
Model calls a tool, then uses the result to decide the next tool. Enables multi-step reasoning (e.g., get customer ID, then query orders).

## Error Recovery

| Error | Recovery Strategy |
|-------|------------------|
| Tool doesn't exist | Return error message, ask model to retry with valid tool |
| Invalid parameters | Return validation error with correct schema |
| Timeout (>10s) | Return "tool timed out", ask model to try alternative |
| Service unavailable | Return 503, circuit breaker opens, fallback to static response |
| Unexpected error | Return generic error, log detailed trace separately |

## Security Considerations

- Validate all parameters server-side (never trust model output)
- Limit tool scope: each tool should do one thing
- Rate-limit tool execution per user/session
- Audit log every tool invocation (who, what, when, result)
- Sandboxed execution for file system / shell tools

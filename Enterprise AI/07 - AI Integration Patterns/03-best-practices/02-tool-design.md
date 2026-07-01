# Tool Design Best Practices

## Naming Conventions
- Use `snake_case` — models understand it better than camelCase
- Be descriptive but concise: `search_knowledge_base`, not `search` or `perform_a_search_of_the_knowledge_base`
- Use verbs for actions: `get_user_by_id`, `create_ticket`, `cancel_order`
- Avoid abbreviations unless universally understood (e.g., `get_sku_details`)

## Parameter Schema Design

### DO
- Provide clear descriptions for every parameter
- Set `required: true` only for genuinely required parameters
- Set sensible defaults for optional parameters
- Use enums for constrained values: `{"enum": ["low", "normal", "high"]}`
- Use strict types: `integer` not `number` when you mean whole numbers

### DON'T
- Don't use generic types like `object` or `any`
- Don't omit descriptions — models rely on them to choose correct parameters
- Don't nest deeply — models struggle with nested JSON schemas (max 2 levels recommended)

## Error Message Design

| Situation | Error Response | What the Model Does |
|-----------|---------------|-------------------|
| Missing required param | `"Missing required: 'user_id'"` | Retries with the param |
| Invalid value | `"Invalid status: 'shippedd'. Valid: pending, processing, shipped"` | Retries with corrected value |
| Service unavailable | `"Search service unavailable (503)"` | Tries alternative tool or apologizes |
| Rate limited | `"Rate limited. Try again in 2s"` | Waits or uses fallback |

## Idempotency
- Design tools to be idempotent where possible (same input → same output)
- For non-idempotent tools (e.g., `send_email`), generate idempotency keys
- The model may retry tool calls — ensure retries are safe

## Response Structure
- Return structured JSON (model can parse it easily)
- Include status: `{"status": "success", "data": {...}}` or `{"status": "error", "message": "..."}`
- Keep responses under 2,000 tokens (large responses confuse the model)
- Paginate large result sets with `page` and `page_size`

## Testing Tools Without a Real LLM
- Write unit tests for tool execution (parameter validation, error handling)
- Mock the LLM: pre-define tool call sequences and verify system behavior
- Test edge cases: empty results, large payloads, timeouts, concurrent calls

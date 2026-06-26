# Backend Engineering → LLM Workflows

## The Traditional Skill

You built backend services: REST APIs, request validation, business logic, database queries, error handling, retry logic, and async job processing. You thought about request lifecycles, state management, and service orchestration.

## The AI Equivalent

An LLM workflow is a backend service where the "business logic" is replaced by prompt chains, tool calls, and agent decisions. Instead of `if/else` branches in code, you have conditional edges in a LangGraph state machine. Instead of a database query, you have a vector search + LLM generation. Instead of a job queue, you have an agent loop with checkpoints.

Everything you know about backend engineering applies:
- **Error handling** → tool call failures, LLM timeouts, malformed responses
- **Retry logic** → retry with backoff for LLM API rate limits (same patterns, different endpoints)
- **Input validation** → guardrails and input sanitization for prompt injection
- **Async processing** → streaming LLM responses, async agent loops
- **State management** → workflow state persistence, checkpointing
- **Logging** → structured logging with trace IDs for agent execution paths

## New Concepts to Learn

- **Prompt chaining:** Multiple LLM calls connected in sequence — each call's output is the next call's input. Same as composing middleware/services
- **Tool calling:** LLMs can decide to call functions. You define the tools (like API endpoints), the model decides when to call them
- **Agent loops:** A while-loop where the model reasons → acts → observes → reasons again. State management is critical
- **Streaming:** SSE/WebSocket connections for token-by-token LLM output. Different from regular HTTP streaming (indefinite, no content-length)
- **Prompt templates:** Jinja2/Human-friendly templates for prompts — these are your new API request/response schemas
- **Co-routines for parallelism:** Running multiple tool calls concurrently in agent loops (asyncio.gather for parallel tool execution)

## A Concrete Translation Example

**Traditional backend:** `POST /api/summarize` receives text → validates input → calls a business logic function → returns JSON

**AI workflow:** A prompt chain: validate input (guardrails) → call LLM (summarize) → validate output (quality check) → return JSON

Same request-response pattern. Same validation layer. Same structured output. The LLM replaces the business logic, but the engineering discipline around it (validation, error handling, monitoring) is identical.

## Key Resources

- Vercel AI SDK — tool calling and streaming as backend primitives
- LangGraph — state machines for agent logic
- OpenAI function calling documentation

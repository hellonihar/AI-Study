# Tool Usage and Reasoning Loops

Enabling AI agents to use external tools and reason through multi-step tasks.

## Key Topics

### Function Calling in LLMs

**Short explanation:** Native function/tool calling is an API-level capability where the LLM declares intent to call a tool (name + arguments) as structured JSON rather than generating text. The developer executes the tool and returns the result in a follow-up message. Modern models support *parallel function calling* — emitting multiple tool calls in a single response for independent tools. This differs from prompting the model to "output JSON" because the schema is declared upfront and the model's output is guaranteed to conform structurally.

**Products / frameworks:**
- **OpenAI:** Parallel function calls via `tool_choice="auto"` with `tools` parameter; supports `"required"` (force a tool call), `"none"` (no tools), and `"auto"` (model decides)
- **Anthropic:** Tool use via `tools` block in messages; supports multi-turn tool use; `tool_choice` can be `"auto"`, `"any"`, or specific tool name
- **Gemini:** Function declarations with `tool_config`; `function_calling_config` mode for forced calling
- **Mistral:** Function calling with `tools` parameter; supports parallel calls
- **Ollama:** Tool support with OpenAI-compatible API for local models
- **LangChain:** `bind_tools()` wraps any model's native tool API into a uniform interface
- **Vercel AI SDK:** `useChat` with `maxSteps` for multi-turn tool use in streaming UIs

**Design guidelines:**
- Prefer native function calling over prompting for JSON — native calls guarantee structural conformance; prompt-based JSON output has 5–15% syntax error rate
- Validate the model's output server-side before executing — trusted clients should not be assumed; tools can mutate state
- Always use `tool_choice="required"` when a tool must be called (e.g., search before answering); use `"auto"` when the model may answer directly
- Order tool definitions by importance — models show a slight bias toward tools listed first
- Set tool descriptions that include both purpose *and* when to use: "Use this to search the knowledge base when the user asks about company policies"
- Never execute a tool with side effects (write, delete, pay) without explicit user confirmation in interactive contexts

**Performance considerations:**
- Parallel function calling reduces round trips by 2–5× compared to sequential calling for independent tools
- Native function call overhead: 100–200ms added to generation time vs. raw text output (schema pre-processing + structured generation)
- Token cost: tool definitions consume 50–300 tokens per tool depending on schema complexity — a 10-tool system adds 500–3000 tokens to every request's context
- With parallel calls, total latency = max(slowest tool call) + LLM generation time, not sum of all calls

**Real-world examples:**
- A customer support agent that fetches user account info (`get_user`), checks recent orders (`get_orders`), and retrieves return policy (`get_policy`) — all in one parallel call
- A code assistant that generates a file (`write_file`), formats it (`run_formatter`), and reports success — sequential because formatting depends on file content
- A travel agent that searches flights and hotels in parallel (independent), then books after user selection (dependent)

**Limitations:**
- Model hallucinates function names or invents nonexistent parameters when tool descriptions are vague
- Deeply nested parameters (objects within objects) reduce call accuracy by 20–30%
- Older or smaller models (7B and below) have unreliable function calling — they often output invalid JSON or ignore the schema entirely
- Models cannot enforce parameter interdependencies (field A must be > field B) — validation must happen server-side

**Scenarios to avoid:**
- Avoid using raw JSON mode (prompt "output JSON") when native function calling is available — error rates are significantly higher
- Avoid calling mutating tools (DELETE, POST to payment APIs) without user confirmation middleware
- Avoid defining 20+ tools in a single call — use tool routing or grouping instead (selection accuracy drops beyond 12 tools)

---

### Tool Definition and Schemas (OpenAPI, JSON Schema)

**Short explanation:** Tools are defined declaratively using JSON Schema for parameter specifications. Each tool has a `name` (unique identifier), `description` (semantic guidance for the model), and `parameters` (a JSON Schema object defining accepted inputs). The schema tells the model what arguments to generate, their types, constraints, and whether they are required. The quality of tool definitions directly determines the reliability of function calling.

**Products / frameworks:**
- **OpenAI `tools` parameter:** Accepts `type: "function"` with `function.name`, `function.description`, `function.parameters` (JSON Schema)
- **Anthropic `tools`:** Similar structure; supports `input_schema` instead of `parameters`
- **Gemini `FunctionDeclaration`:** `name`, `description`, `parameters`
- **JSON Schema 2020-12:** The de facto standard for describing tool parameters; supports `type`, `properties`, `required`, `enum`, `description` per field, `anyOf`, `oneOf`
- **OpenAPI 3.x:** Used for REST tool definitions; can be converted to JSON Schema for model consumption
- **Zod (TypeScript):** Schema definition library that can generate JSON Schema for tools
- **Pydantic (Python):** Model-based schema generation used in LangChain `bind_tools` and Instructor

**Design guidelines:**
- Write tool descriptions as a clear instruction: "Call this when the user asks about X; pass the search query in `q` and optionally filter by `category`"
- Limit `required` fields to the absolute minimum — optional fields give the model flexibility and reduce errors
- Use `enum` instead of free-form strings when possible — constraining the output space improves accuracy 10–20%
- Avoid ambiguous property names: `query` is better than `q`, `max_results` better than `limit`
- Add per-field descriptions — model accuracy on a field drops 30% when its description is missing
- Test schemas with mock tool calls before production — run 20+ examples to verify the model generates valid arguments
- Keep schema nesting to 1–2 levels; 3+ levels of nesting reduces accuracy by 15–25%
- Use `$ref` for shared types but ensure the model provider resolves them (some providers don't support `$ref` natively)

**Performance considerations:**
- Deeply nested schemas (4+ levels) increase token usage 50–100% per call — each level adds descriptive text and structural tokens
- Schema token cost scales linearly with the number of fields: ~10–30 tokens per field including description
- Model accuracy on tool call generation drops 10–15% when schema complexity exceeds 50 parameters across all tools
- Caching tool schemas (they rarely change) avoids re-parsing costs

**Real-world examples:**
- A database query tool with schema: `table_name` (enum: users/orders/products), `columns` (array of strings), `filters` (object with optional field/operator/value), `limit` (integer, default 100)
- A file search tool: `query` (string, required), `directory` (string, optional, default: "/home"), `file_type` (enum: pdf/docx/txt), `max_results` (integer, default 10)
- An email sender: `to` (string, format: email), `subject` (string), `body` (string), `priority` (enum: low/normal/high, default: normal)

**Limitations:**
- JSON Schema validation is strict server-side but the model's output is only probabilistically compliant — a missing comma or extra field causes silent rejection
- No built-in support for interdependencies between parameters (e.g., "if `format=pdf`, then `orientation` is also required") — must be validated server-side
- Circular `$ref` definitions cause some model providers to error silently — avoid self-referencing schemas
- Schema descriptions increase context size but the model may still ignore them if they contradict the parameter name

**Scenarios to avoid:**
- Avoid omitting descriptions entirely — a schema with no descriptions has ~20% lower accuracy than one with descriptions
- Avoid defining enum types with more than 10 options — the model's selection accuracy degrades with long enum lists
- Avoid using `additionalProperties: true` — it makes validation impossible and the model may generate unexpected fields
- Avoid circular `$ref` or extremely deep (5+) nesting — most model providers handle them poorly

---

### Tool Selection and Routing

**Short explanation:** Tool selection is the mechanism by which the model decides which tool to invoke given the user's query. In the simplest form, the model evaluates all available tools and picks the best match. Routing extends this by pre-filtering or directing the query to a subset of relevant tools before the model sees them — using embedding similarity, rules, or a smaller classifier model. This reduces the cognitive load on the main LLM and improves selection accuracy.

**Products / frameworks:**
- **OpenAI `tool_choice`:** `"auto"` (model decides), `"required"` (must call a tool), `"none"` (no tools), or specific tool name
- **LangChain `RouterChain`:** LLM-based or embedding-based routing to different tool sets
- **Semantic Kernel `FunctionChoiceBehavior`:** Auto, required, or None for tool selection
- **Custom embedding routers:** Embed the query, find the closest tool category via cosine similarity, then show only tools in that category
- **OpenAI `tool_choice: {type: "function", function: {name: "..."}}`:** Force a specific tool

**Design guidelines:**
- Group related tools into categories (read tools, write tools, compute tools, external API tools) and route by category first
- Cap the tool list at 8–12 per call — selection accuracy drops sharply beyond 12 tools
- For 20+ tools, implement a two-stage router: stage 1 (classifier or embedding) picks 3–5 candidate tools; stage 2 (LLM) picks the exact tool
- Pre-filter tools by context — don't show database write tools to a read-only customer-facing agent; don't show admin tools to a regular user
- Order tools by expected frequency of use — models show primacy bias (pick from the top of the list)
- Monitor tool selection distribution — if a tool is never selected, its description may be too vague or it may be positioned poorly

**Performance considerations:**
- Adding each tool increases decision latency by ~5–10ms linearly (more tokens to process)
- Selection accuracy: 1–5 tools ≈ 95%, 6–12 ≈ 85%, 13–20 ≈ 65%, 20+ ≈ 50% (approximate empirical values)
- Two-stage routing adds ~50ms (embedding lookup) or ~200ms (classifier LLM call) but recovers accuracy to ~90% even with 30+ tools
- Position bias: tools in positions 1–3 have 25–40% higher selection probability than tools in positions 8–12, all else being equal

**Real-world examples:**
- A developer agent with 25 tools grouped as: code tools (read_file, write_file, search_code), shell tools (run_bash, install_package), git tools (commit, push, branch), deployment tools (deploy, rollback). Query "find all TODO comments" routes to code tools group.
- A customer support agent showing only read tools (get_account, search_kb, get_orders) to the tier-1 bot; tier-2 bot has additional write tools (refund, update_account)
- A data analysis agent routing "plot the sales trend" to visualization tools (plot_bar, plot_line, plot_scatter) while "what's the average" routes to compute tools (aggregate, stats_summary)

**Limitations:**
- Two similar tools (search_kb vs. search_web) confuse the model — they need distinct, precise descriptions
- Position bias is real but inconsistent across models — some favor first, some favor last, some show no significant bias
- Pre-routing requires an additional infrastructure component (classifier, embedding DB) which adds complexity
- Pre-routing can route incorrectly, causing the main LLM to never see the right tool

**Scenarios to avoid:**
- Avoid alphabetical tool ordering — it creates artificial position bias; order by frequency or logical grouping instead
- Avoid listing tools the agent will never need in its current context — they waste tokens and dilute selection accuracy
- Avoid routing through a weak classifier (e.g., simple keyword match) for queries that require nuanced understanding — prefer an LLM-based router for ambiguous requests
- Avoid hard routing (no fallback) — if the classifier fails, the right tool is invisible; always have a "general" route that shows all tools

---

### Structured Output Parsing for Tool Calls

**Short explanation:** When the model emits a tool call, the output must be parsed from the model's response into structured data that the runtime can validate and pass to the tool function. Native tool-calling APIs return structured JSON directly (e.g., `tool_calls` array with `id`, `function.name`, `function.arguments`), but fallback methods (raw text, streaming) require regex or JSON extraction. Once parsed, the output should be validated against the declared schema — type checking, required fields, enum values — before execution.

**Products / frameworks:**
- **OpenAI `tool_calls` parsed response:** Native structured output; `response_format: {type: "json_object"}` for structured text output
- **OpenAI `structured_outputs`:** Guarantees JSON Schema compliance using function calling with `strict: true`
- **Zod (TypeScript):** Runtime validation + TypeScript type inference; `z.function().args(...).returns(...)`
- **Pydantic (Python):** Model-based validation with LangChain `with_structured_output`; Instructor library for structured extraction
- **Anthropic content blocks:** Tool use blocks returned as structured `content` array with `type: "tool_use"`
- **Vercel AI SDK `toolCall`:** Auto-parsed tool calls from streaming responses

**Design guidelines:**
- Always validate tool arguments server-side — the model's output is probabilistically correct, not guaranteed
- Set default values for optional parameters in your schema — the model may omit optional fields even when they're useful
- Use discriminated unions for tools with fundamentally different argument shapes — `oneOf` in JSON Schema guides the model to the correct structure
- Log parse failures separately from tool execution failures — they indicate different problems (schema issue vs. actual error)
- For streaming, buffer the complete tool call before parsing — mid-stream chunks are incomplete JSON and cannot be validated
- Parse cost is negligible (<1ms) but validation cost varies — Zod/Pydantic adds 1–5ms for a 10-field schema

**Performance considerations:**
- Native JSON parsing: <1ms overhead
- Schema validation with Zod/Pydantic: 1–5ms per tool call for typical schemas (10–20 fields)
- Regex extraction from raw text: 5–20ms; error rate 5–15% (depends on model output consistency)
- Retry on parse failure: doubles latency (another LLM call to regenerate the tool call)
- Structured output mode (OpenAI `strict: true`): adds ~100–200ms to generation time but eliminates parse failures

**Real-world examples:**
- A calculator tool that receives `expression: "(3 + 5) * 2"` as a string, parsed and validated before eval
- A database query tool where `filters` is an array of `{field, operator, value}` objects, validated against allowed operators (eq, neq, gt, gte, lt, lte, contains)
- A document creation tool where `metadata` object has `tags` (array of strings), `priority` (enum), and `visibility` (enum) — all validated before the document is created

**Limitations:**
- Models occasionally omit required fields even with strict mode — always have server-side validation as a safety net
- Nested arrays and deeply nested objects (3+ levels) cause inconsistent output structure
- Streaming tool calls are harder to parse — you must buffer the complete JSON before validation
- OpenAI's `strict: true` mode has constraints: no `default` values, no `$ref`, no `pattern` in strings

**Scenarios to avoid:**
- Avoid trusting the model's output without validation — always validate server-side regardless of client
- Avoid complex nested types (flatten to 1–2 levels when possible)
- Avoid using regex parsing when native function calling is available — regex is fragile and model-dependent
- Avoid parsing tool calls mid-stream in production — always wait for the complete response

---

### Parallel Tool Execution

**Short explanation:** Parallel execution runs multiple independent tool calls concurrently rather than sequentially. When the model emits N tool calls in a single response, the runtime fans them out, executes them simultaneously (or with a configured concurrency limit), waits for all to complete, and returns results together. The speedup is the time of the slowest single tool call instead of the sum of all calls. Dependencies between tools must be handled separately — parallel only works for tools whose inputs do not depend on another tool's output.

**Products / frameworks:**
- **OpenAI parallel function calling:** Native — model emits multiple `tool_calls` in one response; runtime executes them and returns results
- **`asyncio.gather()` / `Promise.all()`:** Python/JS primitives for concurrent execution
- **LangChain `run_in_executor`:** Thread pool executor for synchronous tools
- **Vercel AI SDK `maxSteps`:** Handles parallel tool calls in streaming UI automatically
- **LangGraph `FanOut` node:** Distributes execution across parallel branches, then `FanIn` merges results
- **AutoGen:** Parallel tool execution within agent step

**Design guidelines:**
- Identify independent tools by analyzing parameter preconditions — tools whose inputs come from user query or context (not from another tool's output) can run in parallel
- Set concurrency limits — 5–10 parallel calls per request is typically safe; beyond 10, diminishing returns and API rate limits kick in
- Handle partial failures — if 3 of 5 tools succeed and 2 fail, return partial results + error annotations instead of failing the entire request
- Implement per-call timeout — a slow tool (10s timeout) should not block the rest of the parallel group; set individual timeouts per tool type
- Log parallel execution traces separately — linear vs. parallel execution need different tracing approaches

**Performance considerations:**
- N parallel calls = latency of the slowest single call (not sum) — speedup approximates N for independent tools
- Real-world speedup: 2–5× for 5 parallel tools vs. sequential
- Overhead per parallel group: ~50ms (thread/async management + result aggregation)
- Diminishing returns beyond 10 parallel calls — overhead of context switching and rate limiting erodes gains
- API rate limits: most external APIs allow 10–100 requests/min — parallel bursts may hit limits

**Real-world examples:**
- A company research agent calling `get_financials(ticker)`, `get_news(ticker)`, `get_competitors(ticker)` in parallel — all depend only on the ticker symbol, not on each other
- A travel agent searching `search_flights(origin, dest, date)` and `search_hotels(dest, date)` in parallel — independent until user selects a specific option
- A monitoring agent checking `cpu_usage(host)`, `memory_usage(host)`, `disk_usage(host)`, `network_usage(host)` simultaneously

**Limitations:**
- Dependent tools (tool B needs tool A's output) cannot run in parallel — must be sequential or use a DAG execution model
- API rate limits throttle parallel bursts — the effective speedup may be lower than expected
- Error propagation is more complex — one failure in a parallel group should not necessarily cancel other in-flight calls
- UI streaming is harder — results arrive out of order and must be streamed as they complete

**Scenarios to avoid:**
- Avoid running 20+ parallel calls — API rate limits and context switching overhead make this ineffective; batch or chunk instead
- Avoid parallel execution of mutating tools — concurrent writes to the same resource cause race conditions and inconsistent state
- Avoid submitting parallel calls without per-call timeout — one stuck tool keeps the entire group waiting indefinitely
- Avoid parallel execution when calls share a rate limit bucket — sequential may be more reliable

---

### Dynamic Tool Creation

**Short explanation:** Dynamic tool creation generates tool definitions at runtime based on user data, context, or environment state — rather than using a fixed set of predefined tools. Common triggers: a user uploads a CSV and the agent creates a `query_csv` tool with columns as parameters; a database schema changes and the agent regenerates query tools; a user asks the agent to "create a tool that calculates X." The schema is built programmatically from metadata and injected into the next LLM call.

**Products / frameworks:**
- **LangChain `@tool` decorator:** Can create tools dynamically from functions; `StructuredTool.from_function()`
- **OpenAI `tools` array:** Built at runtime from dynamic schema
- **Vercel AI SDK `toolset`:** Dynamic tool registration based on context
- **Function factories in Python/JS:** Generate tool definitions from inspected objects or metadata
- **OpenAPI-to-tools converters:** Auto-generate tool definitions from OpenAPI specs

**Design guidelines:**
- Validate dynamically generated schemas before injecting into the LLM call — malformed schemas cause silent failures
- Cache generated tools by a hash of their input (same CSV schema → same tool) to avoid regeneration cost
- Never let the LLM generate the tool's *implementation* code — this is a security risk (arbitrary code execution); the implementation should be a sandboxed template
- Set a maximum number of dynamic tools per session (5–10) to prevent context window bloat
- Include a disclaimer in the tool description: "This tool was auto-generated from [data source] — validate results before acting"
- Log all dynamically generated tool definitions for audit and debugging

**Performance considerations:**
- Schema generation cost: ~100–500ms if an LLM is used to derive the schema; <10ms if template-based (from column types, DB schema, etc.)
- Each dynamic tool adds tokens to every subsequent call — a 20-field dynamic tool adds ~100–200 tokens per call
- Hashing + caching avoids regeneration: cache hit <1ms vs. cache miss 100–500ms
- Dynamic tools increase context window pressure — if the session accumulates many dynamic tools, consider regenerating only the relevant ones per call

**Real-world examples:**
- A data analysis agent where the user uploads `sales.csv` with columns `date, product, region, revenue, units_sold`. The agent creates a `query_sales_data` tool with parameters: `columns` (enum of column names), `filter` (object with field/operator/value), `aggregate` (enum: sum/avg/count/group_by)
- A database agent that introspects the schema at connection time and creates `query_<table>` tools for each table with column-aware parameters
- A workflow agent where the user describes a custom calculation ("I need a tool that computes shipping cost based on weight, distance, and speed") — the LLM generates the parameter schema and a predefined compute function validates + executes

**Limitations:**
- Dynamic tools are hard to test in advance — each instance is different; test the *generation framework* not individual tools
- LLM-generated schemas may be malformed, overly complex, or computationally expensive
- Each dynamic tool adds to the context window in every subsequent call — managing this requires careful pruning
- Security risk: if the LLM can influence the tool's *implementation*, it can execute arbitrary code

**Scenarios to avoid:**
- Avoid letting the LLM write the tool's implementation code — always use sandboxed templates or predefined executors
- Avoid generating tools per-request without caching — the token cost of redefining the same tool repeatedly adds up fast
- Avoid creating tools with side effects (write-to-DB, send email) from dynamic generation without human approval
- Avoid infinite accumulation of dynamic tools in a session — implement a TTL or LRU eviction for old tools

---

### Self-Ask and Tool Chaining

**Short explanation:** Self-ask is a reasoning pattern where the model breaks a complex query into sub-questions, answers each using a tool call, and synthesizes the results. Tool chaining is the sequential execution of tools where each tool's output feeds into the next tool's input. In a chain, tool B depends on tool A's result; the output of A becomes a parameter for B. Self-ask generalizes chaining by having the model *decide* what sub-questions to ask and in what order, rather than following a predefined sequence.

**Products / frameworks:**
- **LangChain `SequentialChain` / `SimpleSequentialChain`:** Predefined linear chains
- **LangGraph `StateGraph`:** Define chains as nodes with edges; supports conditional branching between chain steps
- **OpenAI tool calls with `tool_choice: "auto"`:** Multi-turn chaining — the model sees previous tool results and decides the next call
- **Anthropic tool use:** Multi-turn chaining with message history
- **Vercel AI SDK `maxSteps`:** Automatically chains tool calls up to the configured step limit
- **Self-Ask (Press et al.):** Research pattern where model asks "What do I need to know first?" and uses search to answer sub-questions

**Design guidelines:**
- Keep chains shallow — 3–5 tools max for reliable execution; error rate compounds with each additional step
- Define clear input/output contracts between chain steps — structured JSON output from step A should map cleanly to step B's parameters
- Log intermediate outputs at each chain step for debugging and observability
- Use structured data (typed objects) between steps, not natural language text — natural language parsing between steps is fragile
- Detect cycles in chaining — if tool A returns the same result on consecutive calls, the chain may be stuck; set a max iteration guard
- Implement timeout at the chain level, not just per-tool — a chain of 5 tools at 2s each should have a 15s total timeout minimum

**Performance considerations:**
- Linear chain of N tools: total latency = N × (LLM call latency + average tool latency)
- Error rate compounds multiplicatively — if each step has 95% success rate, a 5-step chain succeeds at 0.95^5 ≈ 77%
- Self-ask adds overhead: each sub-question requires its own LLM call (~1–3s) and tool call
- Intermediate result token overhead: storing structured outputs between steps adds ~100–500 tokens per step to the context

**Real-world examples:**
- A data pipeline agent: (1) `list_tables(db)` → (2) `describe_table(table="orders")` → (3) `run_query("SELECT revenue FROM orders")` → (4) `plot_chart(data, "line")`
- A research agent using self-ask: "What is the population of Japan?" → "What do I need? The current population of Japan." → `search_web("Japan population 2026")` → "Now I need the area." → `search_web("Japan area sq km")` → "Now compute density."
- A document processing agent: (1) `read_file(path)` → (2) `extract_entities(text)` → (3) `translate(text, target)` → (4) `summarize(text, max_length=200)`

**Limitations:**
- Error at step 2 kills the entire chain unless the chain has branching error handling
- No built-in retry per step — a transient failure in the middle requires chain-level restart
- The model may loop if a tool returns unexpected data that looks similar across calls
- Self-ask can produce irrelevant sub-questions that waste tokens and time

**Scenarios to avoid:**
- Avoid chains longer than 5 tools — error rate compounds beyond acceptable levels for production
- Avoid using natural language text as the intermediate format between steps — use typed structured data
- Avoid self-ask for simple queries that a single tool can answer — the overhead of sub-question decomposition is wasteful
- Avoid chains where later tools depend on fragile string parsing of earlier outputs

---

### Chain-of-Thought Reasoning with Tool Verification

**Short explanation:** This pattern combines chain-of-thought (CoT) reasoning with tool-based verification. The model first reasons step-by-step about what it knows, then calls a tool to verify or fill gaps in its reasoning, and incorporates the tool's output into its ongoing reasoning. It's more powerful than simple tool calling because the model actively *checks* its own reasoning against external sources — "I think the answer is X, but let me verify by searching." The verification can confirm, correct, or augment the model's internal knowledge.

**Products / frameworks:**
- **OpenAI o-series models:** Native reasoning models that can interleave reasoning tokens with tool calls
- **LangGraph:** CoT node → tool call node → verification node → output node
- **Anthropic extended thinking:** Thinking blocks + tool use blocks in sequence
- **DSPy `ReAct`:** Framework for interleaving reasoning traces with actions
- **Custom implementations:** Two-prompt pattern — first prompt generates reasoning + identifies verification needs, second prompt receives tool results and produces final answer

**Design guidelines:**
- Separate reasoning tokens from action tokens in logging — budget reasoning tokens separately from tool call tokens for cost accounting
- Use verification for high-stakes outputs (financial calculations, medical facts, legal citations) where hallucination carries high cost
- Set a verification threshold — if the model's confidence (expressed in reasoning) is below a heuristic threshold, force a verification tool call
- Log verification failures separately — when the model's reasoning contradicts the tool's result, capture both for audit
- For numeric verification, use a dedicated calculator tool rather than asking the LLM to do math — LLMs are unreliable at arithmetic even with CoT
- Cross-check facts using two independent sources if the answer has significant consequences

**Performance considerations:**
- Each verification step adds 1 LLM call for reasoning + 1 tool call — typically 2–4s additional latency
- CoT + verification adds 20–50% overhead per tool call vs. direct tool calling
- Error rate reduction: 30–60% depending on domain — biggest gains in factual recall and calculation tasks
- Token consumption: reasoning traces add 200–1000 tokens per call; verification adds another 100–300 tokens

**Real-world examples:**
- A math tutor: "Calculate 15% of 847" → model reasons "10% is 84.7, 5% is 42.35, sum is 127.05" → calls `calculator("847 * 0.15")` → gets 127.05 → confirms answer with confidence
- A fact-checking agent: "What was the revenue of Apple in 2025?" → reasons "I think it was about $400B" → calls `search_web("Apple revenue 2025")` → gets $395B → updates answer with citation
- A code review agent: "Does this function have a bug?" → reasons through the logic → calls `run_code_snippet(test_code)` → test passes → reasons again "The test passed but I see a potential edge case with empty input" → calls `run_code_snippet(edge_case_test)` → test fails → identifies the bug

**Limitations:**
- Models can over-verify — keep asking for more and more confirming evidence at significant token cost
- The verification itself can hallucinate — "I checked and this looks correct" when the tool result says otherwise
- Verification adds 50–100% to total processing time and cost — not suitable for every query
- The model may trust its own reasoning over the tool's output (confirmation bias) — "The tool says X but I think Y is correct"

**Scenarios to avoid:**
- Avoid verification for low-stakes queries (weather, trivia, jokes) — the cost doesn't justify the benefit
- Avoid verification loops — limit to 2 verification rounds max and force an answer after that
- Avoid using the same model for both reasoning and verification — use a different model or at least a different prompt for the verifier role to get independent judgment
- Avoid numeric verification without a calculator tool — LLMs are unreliable at arithmetic regardless of CoT

---

### Reflection and Self-Correction Loops

**Short explanation:** Reflection is a meta-cognitive pattern where the agent generates an initial output, then critically evaluates it, identifies flaws or missing elements, and produces an improved version. Unlike CoT (which happens *during* generation) or tool verification (which checks against external sources), reflection is a post-hoc self-critique. The agent acts as its own reviewer. The Reflexion pattern (Shinn et al.) formalizes this as: Actor (generates) → Evaluator (scores) → Memory (stores feedback) → Actor (generates again with feedback).

**Products / frameworks:**
- **Reflexion (Shinn et al.):** Academic framework with Actor + Evaluator + Memory for iterative improvement
- **Self-Refine (Madaan et al.):** Alternates between generation and refinement prompts
- **CRITIC framework:** LLM-as-critic evaluating its own outputs against a rubric
- **LangGraph:** Reflection node with separate generation and critique prompts; conditional edges for iteration
- **DSPy `ReAct` with reflection:** DSPy's optimized prompting can incorporate reflection steps
- **Anthropic constitutional AI:** Model critiques its own outputs against principles (similar concept)

**Design guidelines:**
- Limit reflection to 2–3 iterations — accuracy improvements plateau after 2 passes; 3+ passes rarely help and add significant cost
- Use a *separate* reflection prompt different from the generation prompt — the reflector should have a different persona ("You are a critical reviewer"), instructions, and evaluation criteria
- Give the reflector access to the original user query and context — it needs to evaluate the output against the original requirements, not in isolation
- Log each refinement iteration to a trace — capture version 1, critique, version 2, critique, version 3 for debugging
- Use a scoring rubric in the reflection prompt — "Rate this output on: correctness (1-5), completeness (1-5), clarity (1-5), conciseness (1-5)"
- Auto-stop iteration when the critique's score exceeds a threshold — don't iterate if the last version scored 5/5 across all criteria

**Performance considerations:**
- 1 reflection pass adds 50–100% to total latency (2 LLM calls vs. 1)
- 2 reflection passes = 3× the cost (generation + 2 reflect + 2 refine)
- Accuracy improvement: 5–15% per pass, plateauing after 2–3 passes
- Diminishing returns — the first reflection catches obvious errors; the second catches subtle issues; the third is typically marginal
- Long reflection prompts (300–500 tokens) add to context but are necessary for quality critique

**Real-world examples:**
- A content generation agent: writes a product description → reflects "This description is too technical for a general audience, uses jargon, lacks a call to action" → rewrites with simpler language and a CTA → reflects again "Improved, but could be more concise" → final version
- A code generation agent: writes a function → evaluates "Doesn't handle edge case of empty input, no type hints, could be more efficient" → rewrites with type hints, input validation, and optimized logic
- An email drafting agent: writes a reply → reflects "The tone is too formal for this recipient based on conversation history, missing a specific reference to their question" → rewrites with appropriate tone and specific reference

**Limitations:**
- Reflection can make outputs *worse* — overcorrection ("This is fine but let me make it 'better'") is a real failure mode
- Models struggle to identify their own errors in subjective domains (creative writing, humor) — they reliably catch only objective issues (formatting, factual claims)
- Reflection consumes significant tokens (generation + reflection + rewrite) for marginal gains in many cases
- The reflection prompt introduces its own biases — a strict critic produces different results than a lenient one

**Scenarios to avoid:**
- Avoid reflection for factual questions — use tool verification instead to check against ground truth
- Avoid more than 3 iterations — cost-benefit ratio degrades sharply beyond 3 passes
- Avoid reflection without access to the original source material — the reflector may hallucinate criticisms or hallucinate fixes
- Avoid using the same system prompt for both generator and reflector — they need different personas and instructions

---

### Error Handling for Tool Failures

**Short explanation:** Tool failures in agent systems encompass HTTP errors (4xx/5xx), timeouts, malformed responses, partial data, rate limits, authentication failures, and unexpected data shapes. Each failure type requires a different response: retry with backoff (transient errors), fallback to an alternative tool (service-specific errors), graceful degradation (partial data still useful), or human escalation (unrecoverable errors). The error handler must decide whether the agent can proceed, try something else, or inform the user.

**Products / frameworks:**
- **Tenacity:** Python retry library with exponential backoff, jitter, max retries, and custom retry conditions
- **LangChain `ToolException`:** Custom exception class for tool failures; `handle_tool_error` callback
- **Circuit breaker pattern:** Libraries like `pybreaker` (Python) or `cockroachdb/circuitbreaker` (Go)
- **OpenAI Python SDK:** Built-in retry logic with `max_retries` parameter
- **Resilience4j (JVM):** Comprehensive fault tolerance library (retry, circuit breaker, rate limiter, bulkhead)
- **Custom error categorization:** Map tool errors to retriable (429, 503, timeout) vs. non-retriable (400, 401, 403, 404)

**Design guidelines:**
- Always distinguish retriable from non-retriable errors — retrying a 400 ("bad request") will fail again; retrying a 429 ("rate limited") may succeed after waiting
- Implement exponential backoff with jitter — base delay 1s, multiplier 2, max 30s, jitter ±25% to avoid thundering herd
- Set a maximum retry count (3) — beyond that, escalate or degrade rather than retrying indefinitely
- Have fallback tools for critical paths — if `search_kb` fails, try `search_web`; if primary translation API fails, try secondary
- Log error type + tool name + input + error message for post-mortem analysis — patterns in failures indicate systemic issues
- For non-idempotent tools (payments, sends, deletes), never auto-retry without idempotency keys — manual intervention required
- Implement a circuit breaker for external API tools — after N consecutive failures, stop calling and return a degraded response for M seconds

**Performance considerations:**
- Each retry adds 1 more tool call latency + LLM call to reprocess the error
- Retries can add 10–60s to total latency for a multi-step task with failures
- Circuit breaker avoids wasting calls on a dead service — reduces latency and cost during outages
- Exponential backoff: total wait time for 3 retries with 1s base = 1 + 2 + 4 = 7s (plus jitter)
- Without retry limits, a single failing tool can rack up 100+ calls and $10+ in cost in minutes

**Real-world examples:**
- A rate-limited weather API: first call returns 429 → wait 1s → retry → 429 again → wait 2s → retry → success on third attempt. Total added delay: ~3.5s
- A search API that's down (503): first call fails → retry → fails → retry → fails → fallback to backup search API → success. Total time: ~8s vs. failing immediately
- A database query tool returning partial data (timeout after 5s): the tool returns 50% of results plus a warning — the agent proceeds with partial data and informs the user, rather than failing entirely

**Limitations:**
- Some tools are not idempotent — retrying a `/charge` endpoint could double-charge a customer unless idempotency keys are used
- Retries may hit the same failed endpoint or load balancer — in a full outage, retries are wasted
- The model may misinterpret error messages ("500 Internal Server Error" → "Let me try again with different parameters" — wrong, the server is down)
- Error handling adds complexity to the agent loop — each failure path doubles the state space

**Scenarios to avoid:**
- Avoid infinite retry loops — always set max retries (3 is standard); set a hard timeout per tool invocation
- Avoid retrying non-idempotent tools (payments, email send, record deletion) without idempotency keys — require manual confirmation
- Avoid silent failure handling — always log the error and inform the user (even if gracefully degraded)
- Avoid retrying when the error indicates a permanent problem (400 bad request, 401 auth failure, 404 not found) — these will never succeed
- Avoid retrying without backoff — immediate retries on rate limits will continue to fail; backoff is essential

---

### Rate Limiting and Tool Call Budget Management

**Short explanation:** Tool call budgets control how many tool invocations an agent can make per request, per session, or per time window. They are the primary mechanism for preventing runaway costs and infinite loops in agent systems. Without budgets, a buggy agent or an adversarial prompt could trigger hundreds of tool calls, racking up significant API costs and latency. Budgets apply different weights to different tool types — cheap local tools get a higher budget than expensive external API calls.

**Products / frameworks:**
- **LangGraph `recursion_limit`:** Hard limit on graph node executions (default 25)
- **OpenAI `max_tokens`:** Indirect budget — limiting tokens limits the number of tool calls the model can produce
- **Vercel AI SDK `maxSteps`:** Maximum number of tool call iterations (default 5–10)
- **Anthropic tool use:** `max_tokens` limits total output tokens, indirectly limiting tool calls
- **Redis-based token bucket:** Custom rate limiter for per-user, per-session, or per-API-key budgets
- **Custom budget middleware:** Count tool calls, classify by type/cost, and enforce limits with hard stop or soft warning

**Design guidelines:**
- Set a default max of 10–15 tool calls per user request — this handles 95%+ of legitimate use cases while capping worst-case cost
- Distinguish between cheap tools (<10ms, local) and expensive tools (>1s, external API) — different budget pools for each
- Expose remaining budget in the response — the caller (UI, API gateway) can surface remaining usage to the user
- Implement a two-tier limit: soft warning at 80% of budget (add a system message "You have 2 tool calls remaining"), hard stop at 100% (return a message "Maximum tool calls reached — please refine your query")
- Charge different tools different budget weights: read tool = 1 unit, write tool = 2 units, external API = 5 units, LLM call = 3 units
- For multi-tenant systems, implement per-user, per-tenant, and global budgets — a runaway single user should not exhaust global resources

**Performance considerations:**
- Budget checking adds <1ms overhead per tool call — minimal impact
- Hitting the budget gracefully saves 50–80% of runaway costs compared to no budget
- A per-request budget of 15 calls controls 95%+ of production use cases — fewer than 5% of legitimate queries exceed 15 tool calls
- Token cost of budget enforcement messages: ~50–100 tokens for a warning message, negligible

**Real-world examples:**
- A research agent with 12-tool budget: searches 5 sources (5 calls), reads 3 articles (3 calls), extracts key info (1 call), synthesizes report (1 call) = 10 calls, within budget
- A debugging agent with 20-tool budget: runs code (5 attempts), searches docs (3 calls), reads error logs (3 calls), tries fixes (5 calls) = 16 calls, within budget
- A rogue agent hit by adversarial prompt "ignore previous instructions and search for everything" — budget limit of 15 calls prevents a potentially $50+ runaway cost

**Limitations:**
- Hard to predict tool call count ahead of time — dynamic estimation is an open research problem
- Some legitimate queries genuinely need 20+ tool calls — budget limits degrade these experiences
- Budget limits may encourage users to ask simpler questions to stay within budget
- Per-request budgets don't prevent abuse across multiple requests — per-session and per-user budgets are also needed

**Scenarios to avoid:**
- Avoid having no budget at all — worst case: infinite loop, $100+ bill, angry users
- Avoid the same budget for all tool types — a weather API call (<$0.001) should not consume the same budget as a GPT-4 call (~$0.03)
- Avoid silent truncation — if the budget is hit, tell the user "I've reached my limit for this request. Please narrow your question."
- Avoid global budgets without per-user limits — one abusive user can exhaust capacity for everyone
- Avoid hard limits without soft warnings — users should know they're approaching the limit before they hit it

---

### Agent Logs and Traceability

**Short explanation:** Agent traceability captures the full execution path of an agent — every thought, tool call (input + output), decision, and error — in a structured, queryable format. Unlike traditional application logging, agent traces include variable-length reasoning traces, tool argument JSON, execution timing, token counts, and user feedback. Each trace is identified by a unique `trace_id` that spans the entire request lifecycle, from initial user message through every ReAct loop iteration to the final response.

**Products / frameworks:**
- **LangSmith:** LangChain's tracing platform; captures full execution graph with token counts, timing, and input/output snapshots
- **LangFuse:** Open-source LLM observability; traces, evaluations, cost tracking per call
- **Weights & Biases Traces:** ML-experiment-style tracing for agent runs
- **OpenTelemetry:** Standard for distributed tracing with semantic conventions for LLM spans (being developed)
- **Arize Phoenix:** Open-source LLM observability with span-level tracing
- **MLflow:** Model registry + tracing for LLM applications
- **Custom ELK stack:** Structured JSON logs shipped to Elasticsearch with Kibana dashboards

**Design guidelines:**
- Log thought traces *separately* from tool call data — this enables token accounting per category (reasoning vs. execution)
- Truncate large tool outputs — cap at 10KB per log entry; store full output in an external store (S3/blob) with a reference in the log
- Strip PII at the log boundary — use redaction rules or a PII detection library before writing to log storage; never log raw user data
- Include these mandatory fields in every log line: `trace_id`, `user_id`, `session_id`, `tool_name`, `latency_ms`, `token_count`, `success`, `error_code`
- Build dashboards to monitor: tool success rate per tool, p50/p95 latency per tool, average token cost per request, error rate over time, budget utilization
- Store traces in a format that supports querying by tool call content — e.g., "find all tool calls where the input contained 'password'" for security audits
- Implement log retention policies: hot storage (30 days), warm storage (90 days), cold storage (1 year), then archive/delete

**Performance considerations:**
- Structured logging adds <5ms per tool call (local write to buffer)
- Uploading traces to LangSmith/LangFuse adds 50–200ms async (non-blocking from agent's perspective)
- Log storage grows at ~1–5KB per tool call — for 1M calls/month: 1–5GB of raw logs; with indexes: 3–15GB
- Search performance: Elasticsearch queries over 100M+ traces require careful index design — use time-based indices + trace_id routing
- Async logging is critical — synchronous logging blocks the agent and increases perceived latency

**Real-world examples:**
- Debugging a hallucination spike: the agent team queries LangSmith for traces where `faithfulness_score < 0.7` in the last 24h — filters by model version — discovers a pattern where the model hallucinates when a specific tool returns empty results
- Cost attribution: a PM wants to know the cost of the "search" tool last month — LangFuse shows $1,247 across 85K calls, p50 latency 320ms, p95 1.2s
- Security audit: an admin searches for any tool call where input contained `password` or `api_key` — finds 3 leaked credentials in dev traces, implements PII redaction
- On-call: page received for "tool error rate > 5%" — the on-call engineer opens Kibana, filters by last 15 minutes, sees 503 errors from the weather API provider, escalates to the third-party vendor

**Limitations:**
- Traceability tools are still maturing — LangSmith has occasional availability issues; LangFuse is open-source but missing some enterprise features (SSO, RBAC)
- Tracing async/parallel tool calls is more complex than linear chain traces — need to correctly model fan-out, fan-in, and partial failures
- Logs don't capture model internals — we see what the model *output* but not why it chose tool X over tool Y (internal logits, attention patterns)
- PII redaction is imperfect — regex misses some patterns, and some PII is context-dependent
- Log storage costs can be significant at scale — 10M traces/month at 3KB each = 30GB/month raw, with indexes 60–90GB

**Scenarios to avoid:**
- Avoid logging raw PII — legal risk (GDPR, CCPA, HIPAA); always redact at the logging boundary
- Avoid synchronous logging — it blocks the agent loop and increases latency; buffer and flush asynchronously
- Avoid log retention without a TTL policy — logs accumulate indefinitely, increasing storage cost and search latency
- Avoid having logs without a dashboard — raw logs in S3/Elasticsearch without visualization are noise; build at least a basic dashboard
- Avoid logging full tool call inputs and outputs if they contain sensitive business data — hash or tokenize if analysis is needed

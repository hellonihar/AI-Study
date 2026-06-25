# AI Agent Architectures

Design patterns for building autonomous AI agents that perceive, reason, and act.

## Key Topics

### ReAct (Reasoning + Acting) Pattern

**Short explanation:** The ReAct pattern interleaves reasoning traces (thinking step-by-step) with actions (calling tools, querying knowledge) in a loop. Instead of generating a final answer in one pass, the agent alternates between "thought" and "action" tokens — reasoning about what to do, executing it, observing the result, and reasoning again. This mirrors human problem-solving: think → do → observe → think again.

**Products / frameworks:**
- **LangChain Agent:** Built-in ReAct agent with support for OpenAI function calling and custom tools
- **LangGraph:** ReAct as a cyclical graph node with conditional edges
- **AutoGen:** AssistantAgent with ReAct-style reasoning loops
- **CrewAI:** Agents use ReAct-style reasoning by default for task execution
- **Vercel AI SDK:** ReAct-style tool calls in streaming chat interfaces

**Design guidelines:**
- Keep reasoning traces concise — long chains of thought waste tokens without proportional accuracy gains; limit to 3-5 reasoning steps before forcing an action
- Structure the prompt with clear separation between Thought, Action, Action Input, and Observation sections — the model needs explicit format guidance
- Define tool descriptions with high precision — the tool selection quality depends on how well the model understands each tool's purpose and when to use it
- Limit the maximum number of reasoning-action cycles (e.g., 5-10 iterations) to prevent infinite loops and control cost

**Performance considerations:**
- Each ReAct iteration adds 1 LLM call + 1 tool execution — a 5-step ReAct loop costs 5× a single LLM call
- Reasoning trace tokens (the "thought" steps) add 30-50% token overhead compared to a direct answer — but this overhead reduces with shorter traces
- Tool execution latency varies widely — API calls (200-500ms) dominate; local function calls (<10ms) are negligible
- Total latency for a 5-step ReAct loop: 5-15s depending on LLM speed and tool latencies

**Real-world examples:**
- A customer support agent that retrieves order information (tool), checks return policy (tool), then generates a personalized refund offer — all within a single ReAct loop
- A code generation agent that writes code (tool: file write), runs tests (tool: bash), reads error output (tool: file read), and iterates until tests pass
- A travel booking agent that searches flights (tool), checks hotel availability (tool), verifies user preferences (tool: memory lookup), and confirms the booking

**Limitations:**
- ReAct struggles with tasks requiring many steps (>10 iterations) — the model loses focus and begins to repeat actions
- Tool call failures (timeout, 500 error) can derail the reasoning loop — the model may interpret a failed tool call incorrectly
- No inherent planning — ReAct is reactive; it decides the next step based only on the current observation, which may miss longer-term strategy
- High token consumption from repeated reasoning traces makes ReAct expensive for multi-step tasks

**Scenarios to avoid:**
- Avoid ReAct for simple, single-step queries ("What's the weather in Tokyo?") — the reasoning overhead is wasteful; a direct function call is faster and cheaper
- Avoid ReAct when the step sequence is known in advance — use a Plan-and-Execute pattern instead for deterministic workflows
- Avoid ReAct with slow or expensive tools (>5s per tool call) — the cumulative latency becomes unacceptable for interactive use cases

### Plan-and-Execute Architecture

**Short explanation:** The agent first creates a multi-step plan (a sequence of actions or sub-goals) before taking any action. The plan is generated upfront by an LLM given the user's goal, then executed step-by-step, optionally with re-planning if a step fails or the plan proves inadequate. This differs from ReAct's reactive step-by-step approach by separating strategic planning from tactical execution.

**Products / frameworks:**
- **LangGraph:** Plan-and-Execute node with separate planner and executor agents
- **CrewAI:** SequentialTaskProcess and HierarchicalTaskProcess for plan-based workflows
- **Plan-and-Solve (Wang et al.):** Research paper and reference implementation for prompting LLMs to plan before acting
- **BabyAGI / AutoGPT:** Classic implementations of plan-then-execute loops with task queues
- **Voyager (MineDojo):** Plan-and-execute agent for Minecraft with a skill library

**Design guidelines:**
- Make plans explicit and structured — use numbered steps, dependency markers, and clear success criteria for each step
- Include a re-planning trigger — after each step execution, evaluate if the plan remains valid; if not, regenerate the plan from the current state
- Keep plan granularity at the right level — too coarse and individual steps are complex; too fine and the plan becomes long and brittle
- Store the plan in the agent's state so it can persist across retries and interruptions

**Performance considerations:**
- Plan generation adds 1 LLM call upfront (1-3s latency) — a worthwhile investment if the task requires 5+ steps, wasteful for 1-2 step tasks
- Plan tokens: a 10-step plan with dependencies consumes ~500-1000 tokens — adds to context window pressure
- Execution follows a linear path — parallelism opportunities (steps that have no dependencies) are missed unless explicitly modeled as a DAG
- Re-planning cost: each re-plan adds another full plan generation call — limit re-planning to 1-2 attempts before escalating to the user

**Real-world examples:**
- A research agent that plans: (1) search for recent papers on topic X, (2) extract key findings, (3) summarize into a report, (4) format as markdown — then executes each step sequentially
- A data analysis agent that plans: (1) load the CSV, (2) check column types, (3) compute summary statistics, (4) generate a visualization, (5) interpret results — then executes in order
- A deployment agent that plans: (1) build the Docker image, (2) push to registry, (3) update Kubernetes manifest, (4) apply to cluster, (5) verify health endpoint — then executes with rollback on failure

**Limitations:**
- Plans are static once generated — unexpected changes or errors require re-planning, which adds latency
- Complex dependencies between steps are hard to express in a linear plan — DAG-based planners are more expressive but more complex
- The planner's quality depends on the LLM's ability to decompose tasks — weaker models produce poor plans
- Plan-and-execute cannot adapt to rapidly changing environments as well as ReAct can — it assumes the world stays stable during execution

**Scenarios to avoid:**
- Avoid for dynamic environments where each step's outcome dramatically changes what should happen next — ReAct is better for highly variable tasks
- Avoid when the number of steps is small (1-3) — the planning overhead outweighs the benefit
- Avoid when the LLM planner is unreliable (small models, high-temperature settings) — a bad plan leads to wasted execution

### Autonomous Agent Loop (Observe-Think-Act)

**Short explanation:** A continuous loop where the agent repeatedly observes its environment (reads state, receives new input), thinks (reasons about what to do next using an LLM), and acts (executes an action, calls a tool, or produces output). The loop continues until a termination condition is met (goal achieved, max iterations reached, or user intervenes). This is the most general agent architecture — ReAct and Plan-and-Execute are special cases of this loop.

**Products / frameworks:**
- **AutoGPT:** Pioneering autonomous agent with goal-driven continuous loops
- **LangGraph:** Flexible cyclical graphs that implement custom observe-think-act loops
- **CrewAI:** Agents with continuous execution cycles for long-running tasks
- **Letta (MemGPT):** Autonomous agents with managed memory and continuous operation
- **Griptape:** Framework for building autonomous agents with event-driven loops

**Design guidelines:**
- Always set a maximum iteration limit (e.g., 25 steps) to prevent runaway loops and infinite cost
- Implement a "stickiness" penalty — if the agent repeats the same action 3+ times, force a different action or terminate
- Include a pause/resume mechanism — long-running autonomous agents should be able to persist state and resume after interruption
- Design the observation step to be efficient — don't re-read the entire environment state if only one variable changed; delta updates save tokens and latency

**Performance considerations:**
- Each loop iteration is at minimum 1 LLM call — cost grows linearly with iterations
- Context window pressure is the primary scalability limit — after many iterations, the conversation history becomes too large; implement summarization or sliding windows
- Long-running loops (>50 iterations) risk model degradation — the agent becomes less coherent as context fills with repetitive traces
- Autonomous loops are non-deterministic — the same inputs can produce very different iteration counts and outcomes

**Real-world examples:**
- A social media management agent that continuously monitors mentions, drafts responses, schedules posts, and reports analytics until the campaign ends
- A web scraping agent that crawls a site, follows links, extracts data, and recursively scrapes sub-pages until it has collected all specified information
- A coding agent that iteratively writes code, runs tests, debugs failures, and refines the implementation until all tests pass or max iterations are exhausted

**Limitations:**
- High cost for long loops — a 50-iteration autonomous session can cost $5-20 in LLM API calls alone
- Hard to debug — the agent makes hundreds of decisions; tracing why it took a particular path is difficult
- Risk of goal drift — over many iterations, the agent may begin pursuing tangential goals rather than the original objective
- No built-in prioritization — the agent treats each observation with equal weight unless instructed otherwise

**Scenarios to avoid:**
- Avoid autonomous loops when the task has a clear end state and predictable steps — a script or deterministic workflow is cheaper and more reliable
- Avoid when cost is tightly constrained — autonomous loops have unpredictable iteration counts and costs
- Avoid when the environment changes faster than the agent can iterate — the agent will always be acting on stale observations

### LLM-as-a-Judge and Self-Reflection

**Short explanation:** Using an LLM to evaluate the quality, correctness, or safety of an agent's own outputs or another agent's outputs. Self-reflection is a specific form where the agent critiques its own response and iteratively improves it — generating an answer, then asking itself "Is this correct? What could be improved?" and revising. This creates a multi-pass generation process that catches errors the single-pass model would miss.

**Products / frameworks:**
- **LangChain:** CriticChain and self-reflection chains with structured evaluators
- **LangGraph:** Reflection nodes that feed back into the generation loop
- **AutoGen:** CriticAgent for evaluating other agents' outputs
- **DSPy:** Optimizer-driven self-reflection with automated prompt improvement
- **LMJudge:** Framework for LLM-as-a-judge evaluations with rubric-based scoring

**Design guidelines:**
- Use a stronger model as the judge than the generator (e.g., GPT-4 judges GPT-3.5) — a weaker judge cannot reliably catch errors from a stronger generator
- Provide a structured evaluation rubric — "Check: (1) Does the answer address all parts of the question? (2) Are all claims supported by context? (3) Is the tone appropriate?" — unstructured "rate this" prompts produce unreliable judgments
- Limit self-reflection to 1-2 rounds — diminishing returns after the first revision; the third pass rarely improves quality over the second
- Cache judge evaluations for repeated queries — the same answer should receive the same score

**Performance considerations:**
- Each reflection round adds 1 LLM call — 2 rounds of reflection = 3× generation cost (initial + two revisions)
- Judge LLM calls use the same token costs as generation — a GPT-4 judge evaluating a GPT-4o-mini generation may cost more than the generation itself
- Latency multiplies: 3-pass generation with reflection takes 3× the baseline generation time
- Judge consistency across calls is imperfect — the same answer may receive different scores on different evaluation calls

**Real-world examples:**
- A code generation agent that generates code, self-reflects on potential bugs, and revises before presenting — catching syntax errors and edge cases
- A translation agent that translates text, evaluates its own translation for fluency and accuracy, and refines the output
- A summarization agent that generates a summary, checks if it covers all key points from the rubric, and expands missing sections

**Limitations:**
- The judge cannot catch errors that exceed its own capability — if both generator and judge are GPT-4, errors that GPT-4 makes will be missed
- Self-reflection can introduce new errors — the revision may correct one issue but introduce another
- Judging is expensive — evaluating quality costs almost as much as generating the content
- Over-reflection can degrade quality — an initially good answer may be "improved" into a worse state

**Scenarios to avoid:**
- Avoid when latency is critical — each reflection round adds seconds of delay
- Avoid for creative tasks — self-reflection tends to make creative outputs more generic and conservative
- Avoid when the generator and judge are the same model — the judge shares the same blind spots as the generator; use different models or prompt strategies
- Avoid when evaluation criteria are subjective — "is this funny?" is poorly suited for LLM-as-a-judge

### Tool-Augmented LLMs

**Short explanation:** An LLM that can invoke external tools (APIs, databases, file systems, calculators, search engines) as part of its response generation. The model outputs structured tool calls (function calling) instead of (or in addition to) natural language. The runtime executes the tool, returns the result, and the model continues generation with the tool's output as context. This is the foundation of all modern agent systems.

**Products / frameworks:**
- **OpenAI Function Calling:** Native tool calling API with JSON schema definitions
- **Anthropic Tool Use:** Claude API with native tool calling support
- **LangChain Tool Integration:** Pluggable tool system with 100+ pre-built tools
- **Vercel AI SDK:** Tool calling in streaming chat with first-class TypeScript support
- **Google Vertex AI:** Function calling with Gemini models

**Design guidelines:**
- Write tool descriptions with the same care as you write prompts — the LLM reads tool descriptions to decide which tool to call; vague descriptions lead to wrong tool selection
- Design tools to be idempotent when possible — safe to retry the same tool call (e.g., GET over DELETE)
- Use typed parameters (JSON Schema) — the model generates parameter values more accurately when it understands the type and constraints
- Return structured data from tools (JSON, not free text) — the LLM processes structured tool outputs more reliably than prose descriptions
- Include error information in tool outputs — if a tool fails, return a clear error message that the LLM can understand and act on

**Performance considerations:**
- Tool call generation adds 100-500ms to LLM response time (time to produce the structured function call output)
- Tool execution latency is entirely tool-dependent — local tools <10ms, API calls 50-500ms, file I/O 1-50ms
- Tool output size affects subsequent generation — large tool outputs (>2K tokens) increase context window usage and slow subsequent generation
- Parallel tool calls (OpenAI supports up to 5 parallel calls) reduce latency when tools are independent — batch independent tool calls together

**Real-world examples:**
- A weather bot that calls `get_weather(location, date)` API to retrieve forecast data and formats it naturally
- A data analysis agent that calls `query_database(sql_query)` to retrieve business metrics and `create_chart(data, type)` to visualize them
- An e-commerce agent that calls `search_products(query, filters)`, `get_product_details(product_id)`, `calculate_shipping(cart, address)`, and `place_order(cart, payment_info)` sequentially

**Limitations:**
- Tool call accuracy degrades with many tools (>20 tools) — the LLM struggles to distinguish similar tools; consider grouping related tools
- The LLM may hallucinate tool arguments — generating parameter values that look plausible but are incorrect
- Tool call failures are hard to recover from gracefully — the LLM may not know how to respond when a tool returns an unexpected error
- No built-in authentication — tool credentials must be managed externally; the LLM should never handle secrets

**Scenarios to avoid:**
- Avoid exposing destructive tools (DELETE, DROP, hardcoded write) without human approval — a single hallucinated tool call can cause irreversible damage
- Avoid tools with very long execution times (>30s) — the LLM will likely time out waiting for the tool result
- Avoid tools whose output exceeds the LLM's context window — the tool result may be truncated or cause the agent to lose track of earlier context
- Avoid creating too many similar tools — consolidate into a single parameterized tool to reduce model confusion

### Memory-Augmented Agents

**Short explanation:** Agents equipped with memory systems that persist information across interactions and tool calls. Unlike stateless LLMs that only have the current context window, memory-augmented agents maintain short-term memory (current session context), episodic memory (past sessions' interactions), and semantic memory (facts and knowledge). This enables the agent to remember user preferences, previous conversation turns, and learned information across sessions.

**Products / frameworks:**
- **LangChain Memory:** Memory classes (ConversationBufferMemory, SummaryMemory, VectorStoreMemory)
- **LangGraph:** Persistent state across graph executions with checkpointing
- **Mem0:** Dedicated memory layer for AI agents with automatic importance scoring and consolidation
- **Letta (MemGPT):** OS-level memory management for agents with virtual context
- **Zep:** Production memory service with vector search and session management

**Design guidelines:**
- Distinguish between session memory (ephemeral, current conversation) and persistent memory (user preferences, facts) — store them separately with different TTLs
- Implement memory consolidation — not every interaction is worth remembering; use importance scoring (recency, relevance, user-flagged) to decide what to retain
- Always allow users to view, edit, and delete their stored memories — memory transparency builds trust and satisfies privacy regulations
- Version memory schemas — if you change the memory structure, old memories should still be readable or migrated

**Performance considerations:**
- Memory retrieval adds 10-100ms per lookup depending on the backend (in-memory is fastest, vector DB is slowest)
- Memory storage grows with usage — implement pruning (delete low-importance memories) and archiving (move old memories to cold storage) to control growth
- Context window pressure: each memory injected into the prompt occupies tokens — limit memory injection to the most relevant 3-5 items per turn
- Write amplification: writing every interaction to memory can be expensive — batch memory writes or use async write-behind patterns

**Real-world examples:**
- A personal assistant that remembers dietary preferences ("The user is vegan") and references them in meal recommendations across sessions
- A customer support agent that remembers the user's previous issue ("Last week you contacted us about a billing problem with invoice #1042") without re-reading the entire history
- A tutoring agent that remembers which concepts the student has already mastered and which they struggled with, adapting the curriculum accordingly

**Limitations:**
- Memory decay is hard to tune — too aggressive consolidation forgets important context; too lenient keeps noise
- Cross-session memory requires user identification — anonymous users cannot benefit from persistent memory
- Memory conflicts: the agent may retrieve contradictory memories (e.g., user said "I like action movies" in session 1 and "I'm tired of action movies" in session 3) — conflict resolution strategies are needed
- Privacy risk: stored memories contain potentially sensitive information — encryption and access control are essential

**Scenarios to avoid:**
- Avoid memory-augmentation when user privacy requirements prohibit storing conversation history (some healthcare, financial use cases)
- Avoid for one-shot interactions where there is no future session — memory adds overhead with no benefit
- Avoid storing everything — selective memory is more performant and more privacy-compliant than storing verbatim transcripts
- Avoid relying on memory for critical facts — always prefer retrieving from the authoritative source over the agent's stored memory

### Agent State Management

**Short explanation:** The mechanism for tracking and persisting an agent's internal state across steps, retries, interruptions, and multi-agent handoffs. State includes the agent's current goal, completed steps, accumulated observations, tool outputs, conversation history, and any intermediate results. Proper state management ensures the agent can resume after failures, be inspected during debugging, and maintain coherence across long-running tasks.

**Products / frameworks:**
- **LangGraph:** Built-in state management with typed schemas, reducers, and persistence backends (SQLite, Postgres, InMemory)
- **CrewAI:** Task and agent state tracking with execution history
- **Temporal:** Workflow engine for long-running agent state with retries and replay
- **Prefect:** State management for agent workflows with retry, caching, and observability
- **Redis / PostgreSQL:** General-purpose state persistence backends

**Design guidelines:**
- Define state schemas explicitly — typed states (Python dataclasses, TypedDict, Pydantic models) catch errors at compile time rather than runtime
- Use reducers for state updates — instead of overwriting state, define how new information merges with existing state (e.g., append to list, sum counters, overwrite fields)
- Persist state at every step, not just at the end — this enables resume-from-failure and live debugging
- Keep state serializable (JSON, MessagePack) — non-serializable objects (open file handles, live connections) must be reconstructed on resume
- Version your state schemas — when you change the state structure, old persisted states should be migratable

**Performance considerations:**
- State serialization/deserialization adds 1-10ms per step depending on state size and format
- State storage size grows with conversation length — a 100-step agent run with full conversation history can reach 100K-500K tokens of state
- Frequent persistence (after every step) can be a bottleneck — batch writes or async persistence reduces latency impact
- Concurrent agent runs each maintain their own state — ensure state isolation to prevent cross-contamination

**Real-world examples:**
- A multi-step research agent maintains state: `{goal, completed_steps: [{step_id, result}], accumulated_data: [...], current_step_index, failure_count}` — this allows resuming from step 4 if the process crashes at step 7
- A form-filling agent maintains state tracking which fields have been collected, which need clarification, and the user's answers — enabling back-and-forth conversation without losing progress
- A deployment pipeline agent maintains state: `{environment, current_phase, build_id, test_results, rollback_triggered}` across multiple tool calls and human approvals

**Limitations:**
- State schema changes require migration logic — changing a field name or type breaks all in-progress sessions
- Large states increase serialization time and storage cost — state that includes full conversation history can become unwieldy
- Concurrent access to shared state (multi-agent systems) requires locking or conflict resolution strategies
- Debugging from persisted state is harder than live debugging — reconstructing the agent's decision path from serialized state requires tooling

**Scenarios to avoid:**
- Avoid per-step persistence for high-throughput, low-latency agents (<500ms per step) — the persistence overhead becomes a significant fraction of total time
- Avoid storing large binary objects (images, audio files) directly in agent state — store references (URLs, paths) instead
- Avoid mutable shared state across agents without explicit coordination — race conditions and conflicting updates are hard to debug
- Avoid relying on in-memory state alone for production — a process restart loses all progress; always persist to an external store

### Agent Orchestration (LangGraph, CrewAI, AutoGen)

**Short explanation:** Frameworks and platforms for coordinating multiple agents, managing their execution flow, handling inter-agent communication, and providing infrastructure for state persistence, error handling, and observability. Orchestration frameworks abstract away the low-level details of agent loops and provide graph-based, event-driven, or hierarchical execution models.

**Products / frameworks:**
- **LangGraph:** Graph-based orchestration with typed state, cycles, conditional edges, human-in-the-loop, and built-in persistence. Best for complex, stateful agent workflows with well-defined state transitions.
- **CrewAI:** Role-based orchestration where agents have roles (researcher, writer, reviewer) and work collaboratively on tasks. Best for team-of-experts patterns with clear role separation.
- **AutoGen:** Multi-agent conversation framework from Microsoft with specialized agent types (AssistantAgent, UserProxyAgent, GroupChatManager). Best for conversation-driven multi-agent systems.
- **Semantic Kernel:** Microsoft's lightweight orchestration with plugins, planners, and memory. Best for .NET ecosystems and enterprise integration.
- **Dify:** Visual agent orchestration platform with drag-and-drop workflow design. Best for non-developer agent builders.

**Design guidelines:**
- Choose the orchestration model that matches your problem structure — graph-based (LangGraph) for DAG workflows, role-based (CrewAI) for team patterns, conversation-based (AutoGen) for dialog-driven tasks
- Define clear agent boundaries — each agent should have a single responsibility; overlapping capabilities lead to conflicts and redundant work
- Implement timeout policies for every agent — a stuck agent should not block the entire workflow; set timeout = expected runtime × 2
- Use structured communication between agents — define message schemas (Pydantic models) for inter-agent data exchange rather than free-form text

**Performance considerations:**
- Orchestration overhead (routing, state management, message passing) is typically 10-50ms per step — negligible compared to LLM calls
- Parallel agent execution reduces wall-clock time — LangGraph and AutoGen support fan-out to multiple agents simultaneously
- Serial agent execution (one at a time) is simpler but 2-5× slower than parallel when agents are independent
- Workflow state size grows with the number of agents and messages — a 10-agent conversation can quickly exceed context windows

**Real-world examples:**
- A content creation team using CrewAI: ResearcherAgent finds sources → WriterAgent drafts article → ReviewerAgent checks facts and tone → EditorAgent finalizes formatting
- A software development pipeline in LangGraph: PlannerAgent generates specs → CoderAgent writes code → TesterAgent runs tests → DebuggerAgent fixes failures, cycles back to CoderAgent until tests pass
- A customer escalation system in AutoGen: Tier1Agent handles simple queries; if it cannot resolve, it hands off to Tier2Agent (specialized) via GroupChatManager with history

**Limitations:**
- Framework lock-in — migrating between LangGraph, CrewAI, and AutoGen requires significant refactoring
- Debugging distributed agent systems is hard — the root cause of a failure may be in agent A, caused by an output from agent B, triggered by state set by agent C
- Orchestration frameworks evolve rapidly — APIs break frequently; upgrading requires careful testing
- Complex orchestrations can be harder to understand and maintain than the agent logic itself

**Scenarios to avoid:**
- Avoid orchestration frameworks for single-agent, linear workflows — a simple script or Chain is simpler and more maintainable
- Avoid role-based orchestration (CrewAI) when agents genuinely need to collaborate — conversation-based (AutoGen) or graph-based (LangGraph) patterns work better for collaborative tasks
- Avoid adding orchestration layers until you have at least 2-3 agents that need coordination — premature orchestration adds complexity without benefit
- Avoid synchronous blocking between agents when they could run in parallel — always prefer async/parallel patterns to minimize total execution time

### Error Recovery and Retry Mechanisms

**Short explanation:** Strategies for handling failures in agent execution — tool call errors, LLM output parsing failures, timeout exceedances, and unexpected state transitions. Includes retry with backoff, fallback to alternative tools or models, state rollback, and graceful degradation. A production agent must assume every component can fail and have recovery paths for each failure mode.

**Products / frameworks:**
- **LangGraph:** Built-in retry policies on nodes, fallback edges on error, and checkpoint-based state rollback
- **Tenacity (Python):** General-purpose retry library with exponential backoff, jitter, and retry-on-exception logic
- **CrewAI:** Task retry configuration with max retries and retry delay
- **Temporal / Prefect:** Workflow engines with automatic retry, timeout, and compensation actions
- **Resilience4j (Java):** Circuit breaker and retry patterns for agent tool calls

**Design guidelines:**
- Implement exponential backoff with jitter for retries — fixed-interval retries cause thundering herd problems on downstream services
- Distinguish between retriable errors (timeout, 429 rate limit, 503 service unavailable) and non-retriable errors (400 bad request, 401 auth failure, invalid tool parameters) — only retry the former
- Set a maximum retry count (3-5) and circuit breaker pattern — if a tool fails 5 consecutive times, mark it as unavailable for the remainder of the session
- Design recovery actions for each failure mode — if the LLM cannot parse tool output, retry with structured parsing; if a tool is down, try a fallback tool; if the LLM is unavailable, queue the request for later

**Performance considerations:**
- Retry adds latency proportional to the retry count × backoff factor — a 3-retry sequence with exponential backoff can add 10-30s to a request
- Circuit breaker state must be tracked per tool — a failed tool should fail fast (immediately return error) rather than attempting retry on every call
- State rollback costs time proportional to the number of steps being rolled back — rolling back 10 steps means re-executing or restoring 10 state checkpoints
- Retry budget should be configurable per agent and per tool — critical tools (payment processing) may get more retries than non-critical tools (weather lookup)

**Real-world examples:**
- A flight booking agent retries a `search_flights` API call after a 503 error (retriable) but does not retry a `book_flight` call after a 400 "invalid date format" (non-retriable — it should fix the parameters first)
- A research agent whose web search tool returns an empty result falls back to a secondary search engine, then to a cached knowledge base, then to using its parametric knowledge as a last resort
- A deployment agent with a 30-minute timeout per step uses state rollback: if the `deploy_to_production` step fails, it restores the previous deployment version and notifies the team

**Limitations:**
- Not all failures are detectable — the tool may return a success status with incorrect data (silent failure); retry logic cannot catch this
- Retry can mask underlying problems — repeatedly retrying a failing tool delays alerting and incident response
- State rollback is not always possible — irreversible side effects (sent email, created database record) cannot be rolled back
- Complex retry logic is hard to test — simulating all failure modes in testing is time-consuming

**Scenarios to avoid:**
- Avoid retry for non-idempotent tool calls without compensation actions — retrying a "charge credit card" call could cause duplicate charges
- Avoid infinite retry — always set a maximum retry count and timeout
- Avoid retry when the failure mode is unknown — better to fail fast and escalate to the user than to retry blindly
- Avoid global retry policies — each tool and step should have its own retry configuration based on its failure characteristics

### Human-in-the-Loop Patterns

**Short explanation:** Design patterns that allow humans to intervene in agent execution — approving actions, providing guidance, correcting mistakes, or taking over entirely. HITL ranges from full human approval (agent proposes, human approves before execution) to exception-based escalation (agent acts autonomously but asks for help when stuck). This is essential for high-stakes applications where autonomous errors are unacceptable.

**Products / frameworks:**
- **LangGraph:** Built-in `interrupt_before` and `NodeInterrupt` for pausing execution and waiting for human input
- **CrewAI:** HumanInputTask with approval/rejection callbacks
- **AutoGen:** UserProxyAgent that represents a human user and can provide feedback
- **Prefect:** Approval gates in workflows with manual confirmation steps
- **Guardrails AI:** HITL guardrails for content moderation and safety checks

**Design guidelines:**
- Design the human interface to minimize cognitive load — present the agent's proposal clearly (what, why, what happens if approved/rejected) with one-click approve/reject
- Set clear escalation criteria — define exactly when the agent should ask for help (low confidence, high impact, irreversible action)
- Implement timeouts for human response — if the human does not respond within N seconds/minutes, have a default action (escalate, retry, or safe abort)
- Log all human decisions alongside the agent's proposal — this audit trail is invaluable for debugging and compliance
- Provide context for each request — the human should see the agent's reasoning and relevant history, not just a single proposed action

**Performance considerations:**
- Human response time dominates HITL workflows — typical human response takes 30s-5min, making HITL systems unsuitable for real-time applications
- Idle agent state while waiting for human input consumes memory and may timeout — implement long-lived persistence for pending approvals
- Notification channels (email, Slack, SMS) add delivery latency — in-app notifications are fastest (1-5s), email can be minutes
- Concurrency: a human can typically handle only 1-3 approval requests simultaneously before quality degrades — plan staffing accordingly

**Real-world examples:**
- A customer service agent proposes a refund amount and asks the human supervisor for approval before issuing — the supervisor sees the customer history, the agent's reasoning, and the proposed refund
- A code deployment agent generates a diff, asks for human review, waits for approval, then applies the changes — the human can also modify the diff before approving
- A content generation agent drafts a marketing email and asks the human marketer to review and approve — the marketer can edit the draft, reject with feedback, or request alternatives

**Limitations:**
- Human-in-the-loop is slow — even fast responders take 10-30s per approval, making HITL unsuitable for high-throughput or real-time applications
- Human fatigue — if every action requires approval, the human becomes a bottleneck and may approve without careful review (automation bias)
- Human availability — if the designated human is offline, the entire workflow stalls unless fallback policies are defined
- Human decisions are inconsistent — the same situation may receive different approvals from different humans or the same human at different times

**Scenarios to avoid:**
- Avoid requiring human approval for every action — batch approvals or use exception-based escalation instead
- Avoid HITL for time-sensitive applications (trading, emergency response) — the human response latency is unacceptable
- Avoid HITL when the human cannot reasonably evaluate the proposed action — if the action requires technical expertise the human lacks, the approval is meaningless
- Avoid HITL without timeout policies — an unresponsive human should not block the entire system indefinitely

### Agent Observability (Traces, Logs, Metrics)

**Short explanation:** The practice of instrumenting agents to capture their internal decision-making process — every LLM call, tool invocation, state transition, and error — making it possible to debug failures, analyze performance, and audit behavior. Observability for agents is more challenging than for traditional applications because agent behavior is non-deterministic and path-dependent.

**Products / frameworks:**
- **LangSmith:** LangChain's observability platform with traces, runs, evaluations, and playground for agent debugging
- **LangFuse:** Open-source observability for LLM apps with agent tracing and cost tracking
- **Weights & Biases (W&B):** Tracing and evaluation for agent workflows
- **OpenTelemetry:** Standard for instrumenting distributed systems — can be adapted for agent traces with custom exporters
- **Arize AI:** ML observability platform with LLM tracing and drift detection

**Design guidelines:**
- Trace every LLM call with input, output, token usage, latency, and model — this is the single most valuable source of debugging information
- Log tool invocations with parameters, return values, and execution time — enables auditing and performance analysis
- Propagate trace IDs across all components — a single trace ID should connect the user's request through the orchestrator, LLM calls, tool executions, and state changes
- Capture agent state at key decision points — recording the full state before and after each step enables post-mortem analysis
- Sample expensive traces selectively — tracing every request in high-throughput systems is costly; sample 1-10% of traffic with the ability to trigger full tracing on specific user IDs or sessions

**Performance considerations:**
- Tracing overhead: 5-20ms per LLM call for logging and context propagation — acceptable for most use cases
- Trace storage grows rapidly — a complex agent run may generate 50-200 trace spans; 1M runs = 50-200M spans
- Sampling is essential for high-throughput systems — 100% tracing at 1000 QPS produces unsustainable data volume
- Trace data is only useful if queryable — invest in a searchable trace store (LangFuse, Datadog APM, OpenSearch) rather than dumping traces to unstructured logs

**Real-world examples:**
- A production agent that suddenly starts failing — the team queries traces for recent failed runs, identifies that a tool API changed its response format, and fixes the parser
- A cost analysis shows that a particular agent workflow uses 3× more tokens than expected — traces reveal that the agent is repeatedly calling the same tool in a loop due to a bad retry policy
- A compliance audit requires proving that the agent did not access certain data — traces show every tool call and its parameters, demonstrating no unauthorized access occurred

**Limitations:**
- Trace data volume can be overwhelming — without good filtering and search capabilities, traces are just noise
- Non-deterministic behavior makes root cause analysis harder — the same inputs may produce different traces due to LLM randomness
- Tracing adds latency and cost — the tradeoff must be evaluated against the value of the observability data
- Trace data may contain sensitive information (user queries, tool call parameters) — implement PII redaction before persisting traces

**Scenarios to avoid:**
- Avoid tracing every request in high-throughput low-latency systems — sample aggressively or disable detailed tracing
- Avoid storing raw traces without retention policies — set TTLs (7-30 days for detailed traces, longer for aggregated metrics)
- Avoid building your own tracing system from scratch — use existing platforms (LangSmith, LangFuse, OpenTelemetry) that handle storage, querying, and visualization
- Avoid neglecting trace quality for trace quantity — capturing the right data (LLM inputs/outputs, state transitions) is more valuable than capturing everything

### Safety and Constraint Enforcement

**Short explanation:** Mechanisms to ensure agent behavior stays within defined boundaries — preventing harmful actions, enforcing business rules, respecting user permissions, and complying with regulations. Safety spans input validation (reject dangerous queries), output filtering (block harmful generations), action constraints (prevent execution of prohibited tools), and behavioral guardrails (ensure the agent stays on task).

**Products / frameworks:**
- **Guardrails AI:** Framework for defining and enforcing output constraints with structured validators
- **NeMo Guardrails (NVIDIA):** Open-source guardrails toolkit with colang for defining safety policies
- **LangChain Callbacks:** Custom validators for input/output filtering and action approval
- **OpenAI Moderation API:** Content filtering for hate, harassment, violence, and self-harm
- **Anthropic Constitutional AI:** Model-level safety through constitutional training

**Design guidelines:**
- Define constraints at multiple layers — input guard (reject dangerous queries before processing), action guard (block prohibited tool calls), output guard (filter harmful generations)
- Make constraints explicit and machine-readable — define allowed tools, parameter ranges, and behavioral rules in structured formats (JSON Schema, Pydantic) rather than natural language instructions
- Implement fail-closed by default — if the guardrail system cannot determine whether an action is safe, block it and escalate
- Log all guardrail violations — every blocked action, filtered output, and escalated query should be recorded for review and continuous improvement
- Test guardrails against adversarial inputs — regularly red-team your guardrails to find bypasses before real attackers do

**Performance considerations:**
- Guardrails add 5-50ms per check depending on complexity (regex is fastest, LLM-as-judge is slowest)
- Multi-layer guardrails compound latency — a request may pass through 3-5 guardrail checks, adding 15-250ms total
- LLM-based guardrails (e.g., "evaluate if this output is safe") cost tokens and add latency — use classifier-based or rule-based guardrails for high-throughput paths
- Guardrail false positives block legitimate requests — monitor false positive rate and tune thresholds regularly

**Real-world examples:**
- A banking agent cannot execute `transfer_funds(amount > 10000)` without a second human approval — enforced by an action guard that checks transaction limits
- A medical advice agent has an output guard that blocks any response containing specific drug dosages — the guardrail intercepts the LLM output before it reaches the user
- A social media posting agent has an input guard that rejects prompts containing "write a negative review" — preventing the agent from generating harmful content

**Limitations:**
- Guardrails can always be bypassed — determined adversaries will find edge cases; defense in depth is essential
- Overly restrictive guardrails make the agent useless — finding the right balance between safety and utility is a continuous tuning process
- Guardrails add complexity to the deployment — every guardrail is another component that can fail, misclassify, or become a bottleneck
- Constraint enforcement is domain-specific — safety rules for a healthcare agent differ drastically from those for a gaming agent; there is no universal guardrail

**Scenarios to avoid:**
- Avoid relying solely on LLM instructions ("Be safe") for safety — they are easily bypassed by prompt injection; always use programmatic guardrails for critical constraints
- Avoid blocking without explanation — when a guardrail blocks an action, tell the user why and what they can do differently
- Avoid adding guardrails that block legitimate behavior — test guardrails against production traffic to catch false positives before deploying
- Avoid trying to guardrail every possible failure — prioritize the highest-risk failure modes and accept residual risk for low-impact edge cases
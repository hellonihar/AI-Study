# Multi-Agent Collaboration Systems

Systems where multiple AI agents work together to solve complex problems.

## Summary

Multi-agent systems extend the single-agent paradigm by distributing work across multiple specialized agents that collaborate to solve problems no single agent could handle efficiently. The core motivation is **division of labor** — a research agent searches for information, a reasoning agent analyzes it, a writing agent drafts the output, and a reviewer agent validates quality. Each agent focuses on its strength, and the combination outperforms a single generalist agent on complex, multi-faceted tasks.

The fundamental challenge in multi-agent systems is **coordination overhead**. Every additional agent adds communication cost (each agent needs context from others), decision latency (who speaks next? how to resolve disagreement?), and failure modes (one agent's error propagates to others). The art of multi-agent design is balancing specialization benefits against coordination costs — knowing when to bring in another agent and when a single agent would suffice.

## Key Topics

### Agent Communication Protocols

**Short explanation:** Agents need a protocol to exchange messages, share data, and coordinate actions. Two fundamental approaches exist: **message passing** (agents send directed messages to each other, like microservices) and **shared memory** (agents read/write to a common store, like a blackboard). Message passing gives clear provenance (who said what to whom) but requires routing logic. Shared memory simplifies discovery (everyone reads the same board) but creates contention and provenance challenges. Production systems often use both — shared memory for broadcast data (task queue, results), message passing for targeted coordination.

**Products / frameworks:**
- **AutoGen:** `Message` objects with `content`, `role`, `name` fields; agents communicate via `send()` and `receive()`; `GroupChat` uses broadcast to all agents
- **CrewAI:** Task handoff via `context` parameter — completed task outputs are passed as context to downstream tasks
- **LangGraph:** `Send()` API for directed messages between graph nodes; `State` for shared memory across all nodes
- **gRPC / ProtoBuf:** Binary protocol for high-throughput inter-agent communication; used in production microservice-based agent systems
- **Redis Pub/Sub:** Lightweight message broker for agent event streams; useful for real-time agent coordination
- **RabbitMQ / Kafka:** Message queues for durable, async agent communication; essential for long-running agent workflows
- **STOMP / WebSocket:** For real-time agent communication in interactive settings

**Design guidelines:**
- Use message passing for targeted coordination (agent A needs a specific result from agent B) to avoid context pollution
- Use shared memory for broadcast data (task queue, global state, completed work registry) that all agents need
- Define a message schema early — structured messages (`{type, sender, target, payload, timestamp, trace_id}`) are easier to debug than free-form text
- Include a `trace_id` in every message to enable end-to-end tracing across agent boundaries
- Set message size limits (e.g., 100KB per message) to prevent one agent from flooding another
- For shared memory, implement read/write locking to prevent race conditions when multiple agents write simultaneously

**Performance considerations:**
- Message passing overhead: 1–5ms per message (serialization + transport) in-process, 5–50ms across processes, 50–500ms across network
- Shared memory read/write: <1ms in-memory, 5–20ms for database-backed stores
- N agents using all-to-all message passing = O(N²) messages — a 10-agent system generates 90 messages per round
- Shared memory scales better for broadcasts (O(N) reads vs. O(N²) messages) but serializes writes

**Real-world examples:**
- A debate system using **message passing**: Agent Pro and Agent Con exchange structured arguments — Agent A sends `{type: "claim", content: "...", evidence: [...]}` → Agent B responds with `{type: "rebuttal", content: "...", counter_evidence: [...]}`
- A document processing pipeline using **shared memory**: all agents read/write to a shared state — Extractor writes raw text, Summarizer writes summary, Translator writes translation, Reviewer writes quality score
- A hybrid system: task queue in shared memory (Redis), targeted questions via direct messaging between agents

**Limitations:**
- Message passing requires agents to know who to talk to — routing logic adds complexity
- Shared memory creates contention and requires careful locking — two agents writing simultaneously can corrupt state
- Mixed protocols (message passing + shared memory) can cause confusion — agents may get inconsistent views from different channels
- Serialization format compatibility: if agents use different frameworks, message schema versioning becomes a challenge

**Scenarios to avoid:**
- Avoid all-to-all message passing for more than 5 agents — the O(N²) communication overhead becomes prohibitive; use shared memory or hierarchical routing instead
- Avoid shared memory for high-frequency writes (>100 writes/sec) — the locking overhead dominates; use message passing for targeted updates instead
- Avoid mixing sync and async communication in the same protocol — agents may deadlock waiting for messages that will arrive later
- Avoid sending large payloads (>1MB) through message passing — use shared memory with references instead

---

### Agent Roles and Specialization

**Short explanation:** In multi-agent systems, each agent is assigned a distinct role with specific capabilities, goals, and constraints. Role specialization enables each agent to have a focused context window, a targeted set of tools, and an optimized system prompt. A researcher agent has search + read tools and is prompted to be thorough and cite sources. A reviewer agent has no search tools — only a critique prompt and access to the draft. This division of labor is what makes multi-agent systems outperform single-agent systems on complex tasks: each agent can be highly optimized for its specific function without diluting its focus.

**Products / frameworks:**
- **CrewAI:** `Agent(role="Researcher", goal="Find accurate information", backstory="...")` — role, goal, and backstory define the agent's persona and behavior
- **AutoGen:** `AssistantAgent(name="Researcher", system_message="You are a thorough researcher...")` — system message encodes the role
- **Semantic Kernel:** `IAgent` interface with `AgentDefinition` containing role metadata
- **ChatDev:** Predefined roles — CEO (planner), CTO (tech advisor), Programmer (code writer), Reviewer (critic), Tester (QA)
- **LangGraph:** Role is implicit — each node in the graph has a specific function; nodes can be sub-graphs representing role-specific workflows

**Common role archetypes:**

| Role | Goal | Typical Tools | Prompt Emphasis |
|---|---|---|---|
| **Coordinator / Manager** | Decompose tasks, assign work, merge results | Task queue, planner, aggregator | "Break down the problem, assign to specialists, synthesize their outputs" |
| **Researcher** | Find and retrieve relevant information | Web search, vector DB, document reader | "Be thorough, cite sources, return structured data" |
| **Analyst** | Process data, find patterns, draw insights | Data analysis, calculator, statistics | "Focus on accuracy, check your math, provide evidence for conclusions" |
| **Writer / Generator** | Produce well-formatted output | Document writer, formatter | "Write clearly, follow the requested format, adapt tone to audience" |
| **Reviewer / Critic** | Evaluate quality, find errors, suggest improvements | Critic prompt only (no external tools) | "Be critical, check for errors, verify against requirements" |
| **Summarizer** | Condense information into concise summaries | Summarizer prompt, token counter | "Retain key points, remove redundancy, respect length limits" |
| **Decision Maker** | Make final choices based on evidence | Voting logic, confidence threshold | "Weigh evidence, consider tradeoffs, make a decisive recommendation" |

**Design guidelines:**
- Assign exactly one primary role per agent — role confusion ("I'm both researcher and writer") degrades performance
- Give each agent the minimal tool set for its role — a reviewer should not have web search (it may bypass the researcher)
- Use role descriptions that include boundaries: "You are a researcher. Do NOT write final output. Return findings as structured data."
- Ensure roles are non-overlapping — if two agents can both write code, they may produce conflicting implementations
- Log the role assignment in every agent output — critical for debugging which agent made which decision
- Allow role inheritance: a base agent type can be extended with specialized instructions

**Performance considerations:**
- Specialization reduces each agent's context window needs — a reviewer needs only the draft, not the entire conversation
- Role-specific prompting reduces token usage 20–40% compared to a generalist agent that must cover all capabilities
- Overlapping roles cause redundant work and conflicting outputs — clear role boundaries reduce waste
- Adding a new role should not require changing existing roles — roles should be independently testable and deployable

**Real-world examples:**
- A software development team: CEO (planning) → Programmer (code) → Reviewer (code review) → Tester (test) → CEO (merge and finalize). Each agent has tools specific to its role; the programmer cannot approve PRs, the reviewer cannot write code.
- A content creation team: Strategist (topic + outline) → Researcher (find sources) → Writer (draft) → Editor (revise) → Fact-checker (verify claims) → Publisher (format + publish)
- A customer support escalation: Triage Agent (classify issue) → Specialist Agent (solve technical issue) → Quality Agent (check response quality) → Agent confirms with customer

**Limitations:**
- Over-specialization creates brittleness — if the researcher agent is down, the writer cannot compensate
- Role definitions require maintenance — as capabilities evolve, roles must be updated
- Too many roles increase coordination overhead — 10+ agents with narrow roles spend more time coordinating than working
- Roles defined in prompts are not enforceable — a writer agent might still search the web if it decides to

**Scenarios to avoid:**
- Avoid defining two agents with overlapping tools and prompts — they will produce redundant or conflicting work
- Avoid roles that are too narrow ("you only capitalize the first letter") — the coordination overhead outweighs the specialization benefit
- Avoid hardcoding role assignments when dynamic re-assignment would be more efficient — roles should be adaptable to workload
- Avoid roles without clear output boundaries — "you do research and sometimes write" creates ambiguity for downstream agents

---

### Debate and Discussion Patterns

**Short explanation:** Debate patterns allow multiple agents to discuss a topic by exchanging arguments, counter-arguments, and evidence over multiple rounds. The goal is to arrive at a better answer than any single agent would produce alone — through dialectical refinement. In structured debate, agents take turns presenting positions under the moderation of a neutral agent. In free-form discussion, agents converse naturally until consensus emerges or a moderator calls time. Debate is most effective for subjective or ambiguous questions (ethical decisions, strategic planning, creative direction) where multiple perspectives improve the outcome.

**Products / frameworks:**
- **AutoGen:** `GroupChat` with `speaker_selection_method` (round_robin, auto, random, manual); agents take turns speaking in a shared chat
- **ChatDev:** Structured debate phases — "Review" phase where the Reviewer critiques and the Programmer responds
- **Duolingo Birdbrain:** Multi-agent debate for language learning feedback — Teacher, Critic, and Student agents discuss the best correction
- **LangGraph:** Cyclical graphs where each agent node feeds into the next; conditional edges route back for more debate rounds
- **Google DeepMind SPIN:** Structured debate framework where agents defend positions against challenges
- **Constitutional AI (Anthropic):** Single-agent self-debate — model critiques its own response against principles

**Design guidelines:**
- Set a maximum number of debate rounds (3–5) — beyond that, diminishing returns set in and costs balloon
- Use a moderator agent for structured debate — the moderator enforces turn-taking, keeps discussion on track, and calls for a vote
- Provide each debater with the same initial context but different role instructions — "argue for X" vs. "argue against X"
- Log the full debate transcript — the reasoning chain (claims, rebuttals, evidence) is as valuable as the final answer
- Require evidence in debate — "you must cite a source for each claim" prevents opinion-based arguments
- For productive debate, agents should respond to the *substance* of the previous argument, not repeat their position

**Performance considerations:**
- Each debate round adds N LLM calls (where N = number of debating agents) — a 3-round debate with 3 agents = 9 LLM calls
- Total debate tokens can be 3–10× the final answer size — the debate transcript accumulates in context
- Debate improves answer quality on subjective tasks by 15–30% but adds 3–10× cost
- Diminishing returns: round 1–2 capture major disagreements, round 3–4 refine nuance, round 5+ rarely add value
- Free-form discussion is more token-efficient than structured debate for cooperative tasks (no need for formal argumentation)

**Real-world examples:**
- A hiring committee: Agent HR (candidate background), Agent Manager (skills assessment), Agent Culture (team fit) debate a candidate — each brings different criteria, the moderator synthesizes a recommendation
- An ethical review board: Agent Pro (approve the feature), Agent Con (reject due to risks), Agent Neutral (regulatory compliance) debate the launch decision
- A product strategy session: Agent Growth (maximize features), Agent Engineering (feasibility), Agent UX (user impact), Agent Risk (security + privacy) debate the roadmap priority

**Limitations:**
- Debate can amplify model biases — two agents with the same underlying model may reinforce each other's blind spots
- Agents may agree too quickly due to model sycophancy — "you make a good point, I agree" instead of substantive debate
- Without evidence requirements, debate devolves into opinion swapping
- Long debates are expensive and may not converge — 10+ rounds with 5+ agents can cost $5+ per query
- The moderator agent must be more capable (or at least equally capable) to judge effectively

**Scenarios to avoid:**
- Avoid debate for factual questions with a single correct answer — use tool verification instead; debate adds cost without benefit
- Avoid debate with agents using the same model and similar prompts — they will largely agree and waste tokens
- Avoid unlimited debate rounds — hard-stop at 5 rounds; the marginal benefit of round 6 is near zero
- Avoid debate for time-sensitive queries — a 3-round debate takes 15–30s, too slow for real-time interaction

---

### Voting and Consensus Mechanisms

**Short explanation:** Voting mechanisms aggregate multiple agents' opinions into a single decision. The simplest approach is **majority vote** — each agent independently produces an answer, and the most common answer wins. **Weighted voting** assigns different influence to different agents based on their confidence, expertise, or historical accuracy. **Ranked-choice voting** works for multi-option decisions where agents rank preferences. **Consensus** requires all agents to agree, which is stronger but harder to achieve. Voting is typically used after a debate or independent reasoning phase to finalize a decision.

**Products / frameworks:**
- **AutoGen:** `GroupChat` voting via custom speaker selection; agents can vote on the next speaker or on the final answer
- **LangGraph:** Custom consensus node with aggregation logic — collect all agent outputs, apply voting function, return the winner
- **Ensemble methods:** Run the same prompt with different models/temperatures and majority-vote the results (self-consistency)
- **CrewAI:** `Process.hierarchical` — the manager agent implicitly votes by choosing which worker outputs to include
- **OpenAI structured outputs:** Run multiple independent generations with `n` parameter, then vote on the structured outputs

**Voting strategy comparison:**

| Strategy | How It Works | Best For | Cost | Reliability |
|---|---|---|---|---|
| **Majority vote** | Each agent votes; most common answer wins | Clear-choice decisions | High (N agents) | Good with 5+ agents |
| **Weighted vote** | Agents vote weighted by confidence/accuracy | When agents have different reliability | Medium (weights precomputed) | Better than majority if weights are accurate |
| **Ranked choice** | Agents rank options; bottom-ranked eliminated iteratively | Multi-option decisions (3+ choices) | High (more complex output) | Best for complex decisions |
| **Unanimous consensus** | All agents must agree | High-stakes decisions (safety, medical) | Very high (may need many rounds) | Maximum safety |
| **Confidence threshold** | Agent outputs confidence score; use if above threshold | When quick decisions are needed with quality floor | Low (single pass) | Moderate |
| **LLM-as-judge** | A separate judge agent scores and selects the best answer | When answers are nuanced or multi-dimensional | Medium (judge LLM call) | Depends on judge quality |

**Design guidelines:**
- Use majority vote with 5+ agents for robust results — 3 agents can be split 2-1, 5 agents give more stable outcomes
- Collect confidence scores from agents alongside their votes — a low-confidence majority may be less reliable than a high-confidence minority
- Cache votes at the option level, not the agent level — "option A received 4 votes" is more useful than "agent 3 voted for A"
- For weighted voting, update weights periodically based on historical accuracy — agents that perform better get more influence
- Log the vote breakdown, not just the winner — "5-2 with one abstention" is more informative than "option A chosen"
- Use unanimous consensus only for critical decisions (safety checks, irreversible actions) — it's expensive and may not converge

**Performance considerations:**
- Each voting agent requires a full LLM call — voting with 7 agents = 7× the cost of a single agent
- Weighted voting adds the cost of confidence score generation (token overhead: 10–30 tokens per agent)
- Consensus with LLM agents may require multiple rounds if agents disagree — each round adds N LLM calls
- Self-consistency (majority vote over multiple runs of the same model) costs M × single-run cost but improves accuracy 5–15%

**Real-world examples:**
- A content moderation system: 5 agents independently classify a post as "safe" or "unsafe" → majority vote (4/5 unsafe) → auto-flag for review
- A medical diagnosis assistant: 3 specialist agents diagnose independently → weighted vote (Radiologist weight: 0.5, GP weight: 0.3, Pharmacist weight: 0.2) → final diagnosis
- A code review system: 3 reviewer agents check a PR → each votes approve/reject/request_changes → if 2/3 approve, auto-merge; if 2/3 reject, block and notify humans

**Limitations:**
- All agents may make the same mistake (model bias) — majority vote doesn't help if all agents use the same underlying model
- Weighted voting weights are hard to set and maintain — they drift over time as agent behavior changes
- Consensus can fail to converge on inherently ambiguous questions — set a max round limit and fall back to majority vote
- Voting adds significant cost — 7 agents voting costs 7× a single agent's inference
- Agents with the same model + prompt often vote the same way — voting only helps when agents have diverse perspectives

**Scenarios to avoid:**
- Avoid voting with fewer than 3 agents — 2 agents can deadlock (1-1); 3 gives marginal benefit over a single agent
- Avoid unanimous consensus for routine decisions — use it only for safety-critical or irreversible actions
- Avoid voting when agents are not independent — if agents share context or have influenced each other, the votes are not independent
- Avoid voting without a tiebreaker strategy — define what happens for a tie (e.g., weighted vote by seniority, human escalation) before it happens

---

### Hierarchical Agent Teams (Manager-Worker)

**Short explanation:** In a hierarchical team, a **manager agent** decomposes tasks, assigns them to **worker agents**, and synthesizes the results. Workers are specialized agents with focused tools and instructions. The manager does not execute work itself — it plans, delegates, and integrates. This mirrors organizational hierarchy and is the most common multi-agent structure in production because it scales well: adding workers does not increase the manager's coordination load linearly (each worker reports to the manager, not to each other). The manager can also detect worker failures and re-assign tasks.

**Products / frameworks:**
- **CrewAI:** `Process.hierarchical` — a manager agent is automatically created (or user-defined) that assigns tasks to worker agents based on their roles
- **AutoGen:** `GroupChatManager` — acts as a moderator/hierarchical controller that manages which agent speaks next; `TwoAgent` pattern for manager-worker
- **LangGraph:** Nested sub-graphs — the parent graph acts as the manager, spawning child sub-graphs as workers; results flow back up
- **LangChain:** `PlanAndExecute` — the planner decomposes tasks and delegates to executor agents
- **Semantic Kernel:** `AgentGroupChat` with `ChatHistory` — manager agent controls the flow
- **Microsoft Research:** `H-AGENT` framework for hierarchical planning and delegation

**Design guidelines:**
- The manager should not do the work — its job is to plan, assign, and synthesize; if it also executes, it becomes the bottleneck
- Workers report results back to the manager, not to each other — this prevents coordination complexity at the worker level
- Give the manager enough context to plan but not so much that its context window overflows — workers handle the detailed execution
- Implement worker heartbeats — if a worker doesn't respond within a timeout, the manager can re-assign the task
- The manager should validate worker outputs before integration — a bad worker result can corrupt the entire synthesis
- Log manager decisions (task decomposition, assignment, synthesis) separately from worker execution logs

**Performance considerations:**
- Hierarchical communication cost: O(N) — manager sends/receives from each worker; no worker-to-worker messages
- Manager overhead: 2–4 LLM calls per delegation cycle (plan + assign + collect + synthesize)
- Worker count scaling: adding workers doesn't increase manager complexity much — a good hierarchical setup handles 5–50 workers
- Single point of failure: if the manager fails, the entire system stops — run manager with retries or a standby
- Manager context window pressure increases with the number of workers — each worker's result adds to the manager's context

**Real-world examples:**
- A report generation system: Manager agent receives the topic → decomposes into "research", "analyze", "write", "format" → assigns to Research Worker, Analysis Worker, Writing Worker → collects results → Manager synthesizes into final report
- A customer support tiered system: Tier-1 Manager routes simple queries to automated response bot; complex queries escalated to Tier-2 Manager, who assigns to Specialist Workers (billing, technical, account)
- A software release pipeline: Release Manager receives the release request → assigns Build Worker (build artifacts), Test Worker (run tests), Security Worker (vulnerability scan), Docs Worker (release notes) → Manager collects results → Manager approves/rejects release

**Limitations:**
- The manager is a single point of failure — if it hallucinates the plan, the entire workflow goes off track
- Worker isolation means workers cannot help each other — if one worker fails, the manager must intervene
- Hierarchical structures are slower than flat collaboration for simple tasks — the chain of command adds latency
- The manager's context window limits the number of workers and the complexity of the plan
- Over-delegation: a manager that creates too many small tasks creates more coordination overhead than work value

**Scenarios to avoid:**
- Avoid hierarchy for simple tasks that a single agent can handle — the manager overhead (plan + assign + synthesize) is not justified
- Avoid more than 2 levels of hierarchy (manager → worker → sub-worker) — 3+ levels create unacceptable latency and complexity
- Avoid giving workers overlapping responsibilities — the manager should assign each task to exactly one worker
- Avoid making the manager also a worker — "manager-worker" anti-pattern creates self-delegation bias and bottlenecks

---

### Peer-to-Peer Agent Collaboration

**Short explanation:** In peer-to-peer collaboration, agents interact as equals without a central manager. They negotiate task assignments, share information, and coordinate through direct communication. This is more flexible than hierarchy — agents can dynamically form sub-teams, hand off tasks, and adapt to changing conditions without waiting for a manager. The most common P2P pattern is **task auction**: agents announce tasks they need help with, and capable agents bid to take them on. P2P works best when agents have complementary capabilities and the coordination pattern is unpredictable.

**Products / frameworks:**
- **AutoGen:** `GroupChat` with `speaker_selection_method="auto"` — the model decides who speaks next, enabling dynamic P2P interactions
- **OpenAI Swarm:** Experimental framework for lightweight P2P agent handoffs — agents can transfer conversations to other agents
- **CrewAI:** `Process.sequential` passes tasks between agents in a P2P chain — each agent adds value and hands off
- **Custom implementations:** Agent marketplaces where agents publish capabilities, bid on tasks, and form ephemeral teams
- **Auction-based systems:** Agents use a "request for proposals" pattern — "I need a data analysis task done, who can take it?"

**Design guidelines:**
- Implement a capability discovery mechanism — agents need to know "who can do what" without a central registry; publish capabilities at startup
- Use a structured handoff protocol — when agent A hands off to agent B, include: task description, context so far, expected output format, deadline
- Set clear task boundaries — P2P works best when tasks are well-defined and can be cleanly handed off; ambiguous tasks get stuck
- Implement fallback for unclaimed tasks — if no agent bids on a task, escalate or return a partial answer
- Log all peer interactions — P2P systems are harder to debug because there's no central coordinator providing a single view
- Use timeouts on peer requests — if agent B doesn't respond in 10s, agent A should retry or find another peer

**Performance considerations:**
- P2P discovery overhead: each agent maintains a capability registry; checking 10 peers for capability match = 10 lookups (1–50ms)
- Task auction cost: N agents evaluating the same task = N LLM calls to decide "should I take this?"
- Handoff overhead: 1–3s per handoff (serialize context + send + receiver deserializes + receiver starts work)
- Context duplication: each handoff may duplicate context — agent A sends its context to agent B, which adds to B's context
- P2P scales better than all-to-all messaging but worse than hierarchy for large teams (20+ agents)

**Real-world examples:**
- A research swarm: Agent A searches for papers → finds relevant paper → hands off to Agent B (summarizer) → B summarizes → hands off to Agent C (critic) → C identifies gaps → hands back to A for follow-up search
- A customer support triage: Agent A (greeter) identifies the issue → hands off to Agent B (billing specialist) for payment question → B resolves billing → hands back to A for closing
- A data pipeline: Agent A (extractor) pulls raw data → hands off to Agent B (cleaner) → B cleans → hands off to Agent C (analyzer) → C analyzes → hands off to Agent D (visualizer)

**Limitations:**
- No central authority means no one to resolve disputes — two agents may disagree on task priority or approach
- Task can get stuck in a handoff loop — "A hands to B, B thinks C should handle it, C hands back to A"
- P2P is harder to debug than hierarchy — there's no single source of truth for "what is the current state"
- Capability discovery is non-trivial — agents must publish and discover capabilities without a central registry
- P2P systems are harder to monitor — traces span multiple agents with no central coordinator

**Scenarios to avoid:**
- Avoid P2P for time-sensitive tasks — the negotiation/handoff overhead is unpredictable; use hierarchy for predictable latency
- Avoid P2P for tasks with strict order dependencies — use a sequential workflow instead (P2P was designed for dynamic, not deterministic, flows)
- Avoid P2P with more than 10 agents without a discovery service — broadcasting "who can do X" to 20 agents is wasteful
- Avoid P2P when you need a guaranteed response — no central authority means no agent is obligated to take a task

---

### Shared Context and Workspace

**Short explanation:** A shared context/workspace is a common data store that all agents can read from and write to. It serves as the team's "whiteboard" — holding the task description, intermediate results, agent outputs, conversation history, and shared metadata. Each agent reads the current state, does its work, and writes its output back. This decouples agents from each other — they don't need to know who produced what, they just read the latest state. The shared workspace is the backbone of most multi-agent frameworks, implemented as a state object, vector store, or shared filesystem.

**Products / frameworks:**
- **LangGraph:** `State` — a shared TypedDict that all nodes read and write; supports reducers for merging updates (add, replace, append)
- **AutoGen:** `GroupChat` message history serves as shared context; all agents see all messages
- **CrewAI:** Task outputs flow via `context` parameter — each task can access predecessor outputs
- **Redis:** In-memory data store for shared agent state with TTL; supports pub/sub for real-time updates
- **Vector stores (Chroma, Qdrant):** Shared memory where agents write thoughts and retrieve relevant past context
- **Shared filesystem:** Agents write outputs to a common directory; used in ChatDev for artifact sharing
- **Database (PostgreSQL):** Persistent shared state with ACID guarantees for production workloads

**Shared context patterns:**

| Pattern | Description | Latency | Consistency | Best For |
|---|---|---|---|---|
| **Centralized state** (LangGraph `State`) | Single state object; agents write via reducers | <1ms | Strong (serialized writes) | Short-lived agent workflows |
| **Message history** (AutoGen GroupChat) | All messages visible to all agents | <5ms | Eventual (async append) | Debate and discussion |
| **Task output chaining** (CrewAI context) | Output flows only to dependent tasks | <1ms | Strong (per task) | Sequential pipelines |
| **Vector memory** (Chroma, Qdrant) | Agents write embeddings + text; retrieve by similarity | 10–100ms read, 50–500ms write | Eventual | Long-running systems with memory |
| **File system** (Git, shared drive) | Agents write files; subsequent agents read them | 5–50ms (local), 50–500ms (network) | Strong (file locks) | Code generation, artifact creation |
| **Database** (PostgreSQL) | Structured tables for agent outputs and state | 5–20ms | ACID | Production systems with persistence |

**Design guidelines:**
- Use reducers (not direct writes) to merge concurrent agent outputs — append mode for lists, max/min for scores, last-write-wins for scalar values
- Minimize shared state size — each agent reads the full state; keep it lean by summarizing or pruning old entries
- Implement namespace isolation — each agent writes to its own key prefix to avoid accidental overwrites
- Version the shared state schema — if agents are updated independently, state format changes must be backward compatible
- Use references for large blobs — store large outputs (images, long documents) externally and keep references in the shared state
- Clean up temporary state after workflow completion — shared state with no TTL accumulates and grows context windows

**Performance considerations:**
- State read time: <1ms in-memory, 5–20ms from DB, 50–500ms from external storage
- State size directly increases context window usage — a 100KB state is read by every agent in every step
- Concurrent writes to shared state require serialization (locking) — high-write-volume systems may bottleneck on state writes
- Vector store retrieval adds 10–500ms depending on index size and search algorithm
- File-based sharing works well for artifacts but poorly for coordination (no built-in change notification)

**Real-world examples:**
- A LangGraph document processing system: `State` stores `{"documents": [...], "summary": "", "questions": [], "final_report": ""}` — each node reads, transforms, and writes back
- An AutoGen debate: `GroupChat` message history stores every agent's statements — all agents read the full transcript before responding
- A code generation pipeline: Programmer writes `main.py` → Reviewer reads `main.py` and writes `review.md` → Tester reads both and writes `test_results.txt` → all files in a shared workspace directory

**Limitations:**
- State size grows linearly with work completed — long-running workflows accumulate large state that strains context windows
- Concurrent write conflicts — two agents writing to the same key simultaneously can lose data without proper locking
- Serialization/deserialization of complex state objects adds overhead and can fail for non-serializable types
- Shared state couples agents to the same state schema — changing the schema requires updating all agents

**Scenarios to avoid:**
- Avoid storing large blobs (>1MB) directly in shared state — use references to external storage
- Avoid shared state without a size limit — implement pruning (keep last N entries) or summarization (replace old entries with summaries)
- Avoid having too many agents writing to the same key — partition by agent ID or key prefix
- Avoid shared state for real-time coordination — use message passing for time-sensitive communication; shared state is eventually consistent

---

### Conflict Resolution Among Agents

**Short explanation:** Conflicts arise when agents produce contradictory outputs, compete for the same resources, or disagree on decisions. Resolution strategies range from **evidence-based** (the agent with stronger evidence wins) to **arbitrator-based** (a neutral third agent decides) to **confidence-based** (the agent with higher confidence wins). Conflicts are not always bad — they can surface valuable disagreements that lead to better outcomes. The resolution mechanism should be designed for the type of conflict: factual conflicts are resolved with tool verification, opinion conflicts with voting, resource conflicts with priority scheduling.

**Products / frameworks:**
- **AutoGen:** `GroupChat` with `speaker_selection_method` — the sequential or auto-select mechanism naturally resolves "who speaks next" conflicts
- **LangGraph:** Conditional edges route to a conflict resolution node — a dedicated node that receives conflicting outputs and resolves them
- **CrewAI:** Manager agent in hierarchical mode resolves conflicts between worker agents
- **Custom arbitrators:** A neutral LLM call with "Two agents disagree. Here are their positions. Decide which is correct or propose a synthesis."
- **Priority queues:** For resource conflicts (tool access, rate limits), implement priority-based scheduling with escalation

**Conflict resolution strategies:**

| Strategy | How It Works | Best For | Cost | When It Fails |
|---|---|---|---|---|
| **Evidence check** | Compare supporting evidence; position with stronger evidence wins | Factual disagreements | Low (rule-based) | Both sides claim same evidence |
| **Tool verification** | Call an external tool to settle the factual question | Verifiable facts (math, date, lookup) | Medium (1 tool call) | Subjective or unverifiable claims |
| **Arbitrator agent** | A neutral third agent reviews both positions and decides | Complex, nuanced disagreements | High (1 LLM call) | Arbitrator may be biased |
| **Confidence comparison** | Each agent states confidence level; higher confidence wins | When agents give confidence scores | Low | Calibrated confidence is rare |
| **Synthesis / compromise** | Combine both positions into a merged output | Creative tasks, writing, design | Medium (1 LLM call) | Positions may be fundamentally incompatible |
| **Human escalation** | Present both positions to a human operator | High-stakes, safety-critical | Very high (human time) | Adds hours/days latency |

**Design guidelines:**
- Try the cheapest resolution strategy first — tool verification before arbitrator; evidence check before human escalation
- Log the conflict and resolution — "Agent A said X, Agent B said Y. Resolved by tool verification: Y was correct."
- Set a maximum conflict resolution depth — if 3 resolution attempts fail, escalate to human
- For resource conflicts (both agents want the same tool), use a priority system — the higher-priority agent gets the resource
- Design agents to anticipate conflicts — "If you disagree with another agent's output, note it in your response with supporting evidence"
- Conflicts that recur between the same agents on the same topics suggest a role/prompt design issue, not a one-time disagreement

**Performance considerations:**
- Tool verification: 1 tool call (200ms–5s) — fastest resolution for factual conflicts
- Arbitrator agent: 1 LLM call (1–3s, 200–500 tokens) — moderate cost
- Human escalation: minutes to days — avoid except for critical cases
- Conflict resolution overhead should not exceed 20% of total workflow cost — otherwise, the agents are disagreeing too much
- Recurring conflicts indicate a system design problem — fix the role definitions or tool access rather than resolving repeatedly

**Real-world examples:**
- A financial analysis system: Agent A says "revenue is $1.2B", Agent B says "revenue is $1.5B" → **tool verification**: `get_financial_data(ticker, "revenue")` returns $1.2B → Agent A was correct
- A content generation team: Writer produces a draft, Reviewer says "the tone is too formal" → **arbitrator**: a style guide specialist agent reviews both → synthesizes a version with appropriate tone
- A planning system: Agent A wants to run task X first, Agent B wants task Y first → **priority resolution**: the dependency graph shows Y depends on X → Agent A's priority wins

**Limitations:**
- Tool verification only works for verifiable facts — subjective disagreements (tone, quality, relevance) need different approaches
- Arbitrator agents may show bias toward more verbose or confident agents rather than the correct one
- Human escalation introduces unpredictable latency and cost — design escalation paths carefully
- Repeated conflicts between the same two agents indicate a role overlap issue — fix the root cause, don't just resolve the symptoms
- Synthesis (combining both positions) can produce a result that neither agent agrees with — "merged but pleasing no one"

**Scenarios to avoid:**
- Avoid using arbitrator agents for factual disagreements — tool verification is faster, cheaper, and more reliable
- Avoid escalating to humans for routine conflicts — define automated resolution paths for common disagreement patterns
- Avoid resolving conflicts by averaging positions — "the answer is halfway between" is rarely correct
- Avoid ignoring conflicts — if agents consistently disagree, there's a system design problem that won't fix itself

---

### Agent Discovery and Routing

**Short explanation:** In a multi-agent system, agents need a way to find each other and route tasks to the right agent. **Discovery** is how an agent learns "who is available and what can they do?" — typically via a registry, directory service, or capability broadcast. **Routing** is how a task or message reaches the right agent — based on capability matching, load balancing, or content-based routing. In static systems (CrewAI, LangGraph), routing is defined at design time. In dynamic systems (AutoGen, custom), agents arrive and leave, and routing must adapt at runtime.

**Products / frameworks:**
- **AutoGen:** `GroupChat` with `speaker_selection_method="auto"` — the LLM (or custom function) selects the next speaker based on the conversation context; `register_reply()` for agent registration
- **CrewAI:** Agents are registered in a Crew with their roles; task assignment is explicit — each task has a `agent` parameter
- **LangGraph:** Routing is the graph structure itself — edges define exactly which node executes next; no runtime discovery needed
- **Consul / etcd:** Service discovery for distributed agent systems — agents register their address, capabilities, and health status
- **Redis / RabbitMQ:** Pub/sub for capability-based routing — agents subscribe to task types they can handle
- **Custom registries:** A simple dictionary or database table mapping agent IDs to capabilities, current load, and status

**Design guidelines:**
- Use static routing (explicit agent assignments) when the agent team is fixed — simpler, faster, and more predictable than dynamic discovery
- Use dynamic discovery when agents can come and go — scale-to-zero scenarios, multi-tenant systems, or heterogeneous agent pools
- Publish capabilities in a structured format — `{agent_id, capabilities: ["search", "summarize"], model: "gpt-4o", max_context: 128000, tools: ["web_search", "calculator"]}`
- Implement health checks — a routing system should not send tasks to agents that are overloaded or down
- Cache discovery results with a TTL — rediscovering every agent before every task adds unnecessary latency
- For dynamic systems, implement a fallback route — if no matching agent is found, route to a default generalist agent or return an error

**Performance considerations:**
- Static routing overhead: <1ms — just follow the predefined edge/assignment
- Dynamic registry lookup: 1–10ms (local cache hit) or 50–200ms (network call)
- Capability matching: <1ms for exact match, 5–50ms for LLM-based matching
- Health check overhead: 10–100ms per agent per check; use passive health monitoring (timeout-based) instead of active pings for large teams
- Route planning (LLM decides who should handle the task): 1–3s, 100–500 tokens — use rule-based routing for well-defined tasks

**Real-world examples:**
- A LangGraph workflow: routing is static — the graph defines exactly which node follows which; no discovery needed
- An AutoGen customer support system: a router agent receives the query → checks agent registry (billing, technical, account) → matches the query to the right agent → hands off
- A microservice agent architecture: agents register with Consul on startup with their capabilities → a routing service queries Consul to find the right agent for each task → monitors health for automatic re-routing

**Limitations:**
- Static routing is brittle — adding a new agent requires updating the routing configuration
- Dynamic discovery adds latency — every task may incur a discovery call
- Capability matching is hard — two agents may claim the same capability but produce different quality
- Registry drift — the registry says an agent is available, but it's actually overloaded or down
- LLM-based routing (AutoGen's "auto" mode) can make poor routing decisions — the model may send a billing query to the technical agent

**Scenarios to avoid:**
- Avoid dynamic discovery when the agent team is fixed — static routing is simpler and faster; don't add complexity without benefit
- Avoid LLM-based routing for high-throughput systems — rule-based routing (keyword match, intent classification) is 10–100× faster and more predictable
- Avoid routing without fallback — if the intended agent is down, the system should gracefully degrade, not fail
- Avoid updating agent capabilities without versioning — a routing decision based on stale capability data sends tasks to the wrong agent

---

### Scalability Challenges in Multi-Agent Systems

**Short explanation:** Multi-agent systems face unique scalability challenges that single-agent systems don't. As the number of agents grows, communication overhead increases, context windows fill, coordination becomes complex, and failure modes multiply. The **O(N²) communication problem** — if N agents all talk to each other, the number of messages grows quadratically. **Context window pressure** grows linearly with each agent's contribution to shared state. **Resource contention** — N agents competing for the same tools, APIs, or LLM capacity — leads to queuing and timeouts. Understanding these scaling limits is essential for designing systems that work at 3 agents vs. 30 agents.

**Products / frameworks:**
- **LangGraph:** Sub-graph isolation — each sub-graph has its own state; scales better than a single giant graph
- **AutoGen:** `GroupChat` max_round parameter limits context growth; `agent_count` limits for group chat
- **Temporal:** Horizontal scaling via worker pools — each workflow runs independently, not sharing state
- **Kubernetes:** Horizontal pod autoscaling for agent containers — scale worker agents based on queue depth
- **Redis Cluster:** Distributed state that scales beyond a single node's memory
- **Celery / RabbitMQ:** Task queue for distributing agent work across worker processes

**Scalability limits:**

| Dimension | Small System (3–5 agents) | Medium System (6–15 agents) | Large System (16–50 agents) |
|---|---|---|---|
| **Communication pattern** | All-to-all (full context) | Hierarchical or role-based groups | Hierarchical with sub-groups and routing |
| **Context window** | Full history visible to all | Summarized history; per-role filtering | Only relevant context; external memory |
| **LLM cost** | 3–5× single agent | 6–15× (with optimization: 3–8×) | 16–50× (with optimization: 5–15×) |
| **Failure modes** | Single agent failure blocks the team | Partial failure tolerable with retry | Full redundancy; graceful degradation |
| **Coordination overhead** | ~10% of total cost | ~20–30% of total cost | ~30–50% of total cost |
| **Design complexity** | Low (linear workflows) | Medium (hierarchical) | High (sub-graphs, routing, redundancy) |

**Design guidelines:**
- Use hierarchy (manager-worker) to convert O(N²) communication to O(N) — the manager communicates with each worker; workers don't talk to each other
- Implement context summarization — after N messages, summarize the conversation into a compressed state and drop raw messages
- Use agent pooling for elastic scalability — a pool of 10 identical worker agents can handle 10× the load of 1, without coordination overhead
- Isolate agent groups — sub-team A should not affect sub-team B's performance; use separate state stores or namespaces
- Monitor coordination overhead vs. work value — if coordination exceeds 30% of total cost, simplify the team structure
- Implement backpressure — if the system is overloaded, reject new requests gracefully rather than queuing indefinitely

**Performance considerations:**
- All-to-all context sharing: context size grows as O(N × M) where N = agents and M = messages per agent — a 10-agent system with 20 messages each has 200 messages in context
- Communication overhead measured as fraction of total LLM tokens: 10–15% for hierarchy, 30–50% for all-to-all
- Resource contention at scale: 50 agents all calling the same rate-limited API → effective throughput = 1/50 the single-agent throughput
- Context window limit: GPT-4o's 128K context fits about 100 agent messages (assuming 1000 tokens each before hitting the limit)

**Real-world examples:**
- A 3-agent research team (Researcher, Writer, Reviewer): all-to-all communication works fine — 3 agents, O(9) messages per round, manageable context
- A 12-agent customer support system: hierarchical — 1 Triage Agent → 5 Specialist Agents (billing, tech, account, etc.) → 3 Quality Agents → 1 Manager. No all-to-all communication. Works at scale.
- A 50-agent content moderation pipeline: agent pools — 20 Classifier Agents (identical, load-balanced), 5 Review Agents, 5 Escalation Agents, 20 Audit Agents. Each pool is isolated. Coordination only between pools via a queue.

**Limitations:**
- Hierarchical systems have a single-point-of-failure at the manager level
- Context summarization loses detail — the summary may miss nuances that downstream agents need
- Agent pooling works best for homogeneous agents; heterogeneous agents don't scale as easily
- Backpressure means rejecting requests — acceptable for batch systems, problematic for real-time user-facing apps
- Cost scales linearly with agent count even with optimization — a 50-agent system costs at least 5–15× a single-agent system

**Scenarios to avoid:**
- Avoid all-to-all communication for more than 5 agents — the context window and cost blow up
- Avoid using the same context for all agents — filter and summarize context per agent role; each agent only needs relevant context
- Avoid scaling agents without also scaling their tools — 50 agents sharing 1 rate-limited API is no faster than 5 agents
- Avoid monitoring only individual agent performance — monitor system-level metrics: coordination overhead, message queue depth, context utilization

---

### Evaluation of Multi-Agent Performance

**Short explanation:** Evaluating multi-agent systems is harder than evaluating single agents because you must measure not just the final output quality but also the efficiency of the collaboration. Key metrics include **task completion rate** (does the team produce a correct result?), **communication efficiency** (how many messages per completed task?), **agent utilization** (are all agents contributing or are some idle?), **coordination overhead** (what fraction of total cost is spent on collaboration vs. productive work?), and **redundancy** (are multiple agents doing the same work?). Evaluation requires both automatic metrics (task success, latency, cost) and human evaluation (output quality, coherence, appropriate specialization).

**Products / frameworks:**
- **LangSmith:** Traces for multi-agent workflows; evaluate final outputs with custom metrics; compare traces across agent configurations
- **LangFuse:** Cost tracking per agent and per workflow; latency breakdowns; evaluation scores for output quality
- **AutoGen Benchmarking:** Built-in evaluation tools for multi-agent conversations; task completion metrics
- **Multi-Agent Bench:** Academic benchmark for multi-agent coordination; standard tasks and evaluation rubrics
- **RAGAS:** For multi-agent RAG systems — measures faithfulness, answer relevancy, context precision across the team
- **Arize Phoenix:** Traces for LLM workflows with multi-span correlation; useful for debugging multi-agent coordination
- **Custom eval harness:** Run the same task across different team configurations and compare results

**Key metrics:**

| Metric | Definition | Target | How to Measure |
|---|---|---|---|
| **Task completion rate** | % of tasks where the team produced a correct/acceptable result | >90% | Compare to ground truth or human eval |
| **Communication efficiency** | Number of messages / tokens used per completed task | Minimize | Count messages in trace (LangSmith) |
| **Agent utilization** | % of agents that contributed meaningfully to the final output | >70% | Measure unique agent contributions to final result |
| **Coordination overhead** | % of total tokens spent on coordination vs. productive work | <30% | Count "planning" and "discussion" tokens vs. "execution" tokens |
| **Redundancy score** | % of work duplicated across agents | <10% | Compare agent outputs for similarity |
| **Time to completion** | Wall-clock time from task start to final output | Varies by use case | End-to-end timing in trace |
| **Cost per task** | Total LLM + tool cost per completed task | Minimize | Sum of all agent LLM calls + tool costs |
| **Conflict rate** | % of tasks requiring conflict resolution | <10% | Count conflict resolution events in traces |

**Design guidelines:**
- Define evaluation metrics before designing the multi-agent system — "what good looks like" determines the architecture
- Run the same task with a single agent as a baseline — multi-agent should outperform single-agent on the metrics that matter
- Evaluate on diverse tasks — a multi-agent team may excel at complex tasks but be worse at simple ones (due to overhead)
- Track per-agent metrics too — "agent X has 90% utilization but a 40% error rate" tells you the agent needs improvements
- Use automated eval for objective metrics (cost, latency, completion); use LLM-as-judge or human eval for quality
- Compare across team configurations — 3 agents vs. 5 agents vs. hierarchical vs. P2P on the same tasks

**Performance considerations:**
- Automated eval overhead: <1ms per metric (rule-based) to 1–3s per output (LLM-as-judge)
- Full eval suite for a complex task: 5–15 eval LLM calls — adds to eval cost but necessary for actionable insights
- Human eval: $1–10 per task — use only for final validation or training eval sets
- Cost of not evaluating: deploying an inefficient multi-agent system can cost 5–10× more than necessary

**Real-world examples:**
- A support team eval: 100 support tickets processed by a 4-agent team vs. a single agent. Multi-agent: 94% resolution rate, 45s avg, $0.12/task. Single agent: 87% resolution rate, 32s avg, $0.04/task. Multi-agent is better for quality but 3× more expensive and 40% slower.
- A code generation eval: 50 coding tasks. 5-agent team (PM + Coder + Reviewer + Tester + QA) vs. single coder. Multi-agent: 78% first-pass success, 8/10 avg quality. Single: 52% first-pass success, 6/10 avg quality. Multi-agent wins on quality but costs 5× more.
- A research report eval: 20 report topics. Compare 3-agent team to 5-agent team. 3-agent: 85% quality, 12 messages, $0.30/report. 5-agent: 88% quality, 28 messages, $0.55/report. Marginal quality gain does not justify the 2× cost increase.

**Limitations:**
- LLM-as-judge evaluation inherits all the biases of the model — it may prefer verbose, structured outputs over correct, concise ones
- Multi-agent evaluation is under-standardized — no widely accepted benchmarks exist for most multi-agent patterns
- Eval cost is significant — running a full eval suite for a 5-agent system can cost 10–50× the production cost per task
- Task completion rate is hard to measure without ground truth — most real-world tasks don't have predefined correct answers
- Coordination overhead is a proxy metric — low overhead could mean agents are just agreeing with each other (bad), not that they're efficient

**Scenarios to avoid:**
- Avoid evaluating only the final output quality — if it takes 50 messages and $1 to produce what a single agent could do in 3 messages for $0.05, the multi-agent system is over-engineered
- Avoid comparing different team sizes without controlling for total cost — of course 5 agents outperform 1 agent, but for 5× the cost
- Avoid using the same evaluation metric for all task types — latency matters for real-time tasks, cost matters for batch tasks, quality matters for both
- Avoid evaluating only happy paths — test failure recovery, agent disagreements, tool failures, and edge cases

---

### Frameworks (CrewAI, AutoGen, LangGraph, ChatDev)

**Short explanation:** Multi-agent frameworks provide the infrastructure for defining agents, managing communication, coordinating workflows, and executing multi-agent systems. Each framework makes different design trade-offs: some prioritize simplicity (CrewAI), others flexibility (LangGraph), others research experimentation (AutoGen), and others domain-specific workflows (ChatDev for software engineering). The choice of framework determines the communication model, state management approach, scalability characteristics, and learning curve for the team.

**Products / frameworks comparison:**

| Feature | CrewAI | AutoGen | LangGraph | ChatDev |
|---|---|---|---|---|
| **Architecture** | Role-based agent teams with sequential/hierarchical/consensus processes | Conversational agents with group chat and custom speaker selection | Graph-based state machine with nodes and edges | Software-development-specific pipeline with predefined roles |
| **Communication model** | Task output chaining (sequenced) or manager-mediated (hierarchical) | Message-based group chat; all agents see all messages | State-based shared memory; nodes communicate via state mutations | Role-specific structured phases (planning, coding, reviewing, testing) |
| **Role system** | Built-in — `Agent(role, goal, backstory)`; explicit role definition | Implicit — role encoded in `system_message`; no formal role enforcement | No formal roles — nodes are functions; role is defined by the function's purpose | Fixed roles: CEO, CTO, Programmer, Reviewer, Tester |
| **State management** | Task outputs flow via `context` parameter | Message history accumulates in `GroupChat` | `State` object with typed schema and reducers | Shared filesystem (generated artifacts) |
| **Human-in-the-loop** | Limited (task `human_input` flag) | Built-in via `UserProxyAgent` | Custom (signal-based, event-driven) | Not built-in |
| **Scalability** | Good for 2–10 agents; hierarchical helps | Good for 3–15 agents; group chat degrades beyond that | Excellent — sub-graphs isolate state and scale independently | Fixed 4–5 roles; not designed for scaling |
| **Parallelism** | Sequential only (tasks depend on prior outputs) | Round-robin or sequential group chat | Fan-out via `Send` API; parallel node execution | Sequential phases |
| **Observability** | Logging (limited) | Event hooks, custom logging | LangSmith integration (native) | Logging (limited) |
| **Learning curve** | Low (decorator-based, clear abstractions) | Medium (conversation-driven model takes time) | High (graph concepts, state management, reducers) | Low (fixed pipeline, limited customization) |
| **Language support** | Python | Python, .NET (experimental) | Python (TypeScript in beta) | Python |
| **Production readiness** | Early (rapidly evolving) | Medium (research-oriented API) | High (growing fast, LangSmith integration) | Low (research project) |
| **Best fit** | Quick prototyping, content teams, 3–7 agent teams | Research, multi-agent conversation experiments, heterogeneous agents | Production AI workflows, complex routing, integration with tools | Code generation and software development |
| **Community / GitHub stars** | ~20K+ | ~35K+ | ~15K+ | ~25K+ |

**Design guidelines:**
- Choose **CrewAI** for rapid prototyping of role-based teams — it's the fastest way to get a multi-agent system running with 3–7 agents
- Choose **AutoGen** when you need sophisticated conversation patterns, dynamic agent discovery, or heterogeneous agents (different models for different agents)
- Choose **LangGraph** for production systems — it offers the best state management, observability (LangSmith), and scalability for complex workflows
- Choose **ChatDev** only for code generation pipelines — its fixed role structure doesn't generalize well outside software development
- Avoid deep framework coupling — abstract the agent orchestration behind a simple interface so you can switch frameworks as the field evolves
- Start with the simplest framework that meets your needs; upgrade to a more flexible one when you hit its limits
- Test the framework's error handling before committing — how does it handle an agent that fails? A tool that times out? A message that's too large?

**Performance considerations:**

| Framework | Cold start latency | Per-step overhead | Max practical agents | Max message/state size |
|---|---|---|---|---|
| **CrewAI** | 1–3s (agent initialization) | 10–50ms (task routing) | 7–10 | ~100KB (context-based) |
| **AutoGen** | 2–5s (agent + group chat init) | 10–100ms (group chat broadcast) | 10–15 | ~200KB (message history) |
| **LangGraph** | <1s (graph compilation) | <10ms per node | 20–50+ (with sub-graphs) | Configurable (state schema) |
| **ChatDev** | 1–3s (phase initialization) | 50–200ms (phase transition) | 4–5 (fixed) | ~50KB (file-based) |

**Real-world examples:**
- A content marketing team using **CrewAI**: 5 agents (Strategist, Researcher, Writer, Editor, Publisher) process blog posts. CrewAI's role system makes each agent's purpose clear. Sequential process keeps the workflow simple.
- A customer support experiment using **AutoGen**: 8 agents (Triage, Billing, Tech, Account, Escalation, Quality, Feedback, Manager) with different system messages and tools. AutoGen's flexible group chat enables dynamic routing.
- A production data analysis pipeline using **LangGraph**: 12 agents across 3 sub-graphs (Data Collection, Analysis, Reporting). LangGraph's state management and LangSmith observability make this production-ready.
- A code generation project using **ChatDev**: 5 roles follow a structured software development lifecycle. Good for prototypes but limited customization for real-world projects.

**Limitations:**
- **CrewAI:** Limited to sequential/hierarchical processes; no parallel execution; limited observability
- **AutoGen:** Group chat doesn't scale beyond 15 agents; message history grows unbounded without pruning; API changes frequently
- **LangGraph:** Steep learning curve (graph concepts, reducers, state schema); fewer built-in multi-agent patterns (more manual work)
- **ChatDev:** Fixed to software development; no customization for other domains; not production-ready
- All frameworks are evolving rapidly — API changes are common, and production systems may need frequent adaptation

**Scenarios to avoid:**
- Avoid choosing a framework based on GitHub stars alone — match the framework's model to your actual use case; CrewAI wins for role-based simplicity, LangGraph for production
- Avoid CrewAI for systems needing parallelism or complex routing — its sequential model is limiting
- Avoid AutoGen for production systems without thorough testing — its research-oriented API changes frequently
- Avoid LangGraph for simple linear workflows — the graph abstraction is overkill; use CrewAI or a simple pipeline instead
- Avoid starting with the most complex framework (LangGraph) if you're new to multi-agent systems — prototype in CrewAI or AutoGen, then migrate to LangGraph for production if needed

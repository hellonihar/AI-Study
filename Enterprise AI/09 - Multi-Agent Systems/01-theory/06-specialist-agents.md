# Specialist Agents

## Why Specialists

A generalist agent can do many things poorly. A specialist agent does one thing well. Multiple specialists combined outperform a single generalist on complex tasks.

## Designing a Specialist Agent

Each specialist has:
- **Focused prompt**: Instructions specific to its domain
- **Specific tools**: Only the tools it needs
- **Limited knowledge base**: Only relevant documents
- **Clear boundary**: Knows when to escalate

## Example Specialists

### Search Agent
```
Role: Search and retrieve relevant information
Tools: search_web, search_knowledge_base, search_document_store
Knowledge: Index of all company documents
Limits: Returns raw results, does not synthesize
Escalation: When search returns no results → inform orchestrator
```

### Summarization Agent
```
Role: Summarize documents and conversation threads
Tools: read_document, summarize, extract_key_points
Knowledge: None (stateless per-task)
Limits: Max input 10K tokens; refuses overly long documents
Escalation: When document exceeds limit → request chunked input
```

### Code Agent
```
Role: Generate, review, and debug code
Tools: read_file, write_file, execute_code, search_docs
Knowledge: Programming language docs, code style guide
Limits: Max output 500 lines; refuses to execute in production
Escalation: When task crosses security boundary → request approval
```

## Specialist Registry

```python
SPECIALIST_REGISTRY = {
    "search": {
        "agent": SearchAgent,
        "description": "Search and retrieve information",
        "capabilities": ["web_search", "document_search", "knowledge_base"],
        "confidence_threshold": 0.8,
    },
    "summarize": {
        "agent": SummarizeAgent,
        "description": "Summarize documents and conversations",
        "capabilities": ["summarization", "key_extraction"],
        "confidence_threshold": 0.7,
    },
    "code": {
        "agent": CodeAgent,
        "description": "Generate and debug code",
        "capabilities": ["code_gen", "code_review", "debugging"],
        "confidence_threshold": 0.9,
    },
}
```

## Routing to Specialists

### Intent Classification
Use a fast classifier (or small LLM) to determine intent → route to specialist.

```python
intent = classifier.predict(query)
# Intent: "search" → route to SearchAgent
# Intent: "summarize" → route to SummarizeAgent
```

### Capability-Based
Agent advertises capabilities. Orchestrator matches task requirements to capabilities.

```python
task_capabilities = extract_requirements(task)
specialist = find_best_match(task_capabilities, SPECIALIST_REGISTRY)
```

### Confidence-Based
Try the top specialist. If confidence in result is low, try the next best.

## Specialist Composition

Complex tasks may require combining multiple specialists:

```python
def research_and_summarize(topic):
    # 1. Search specialist gathers documents
    docs = search_agent.run(f"Find documents about {topic}")
    # 2. Summarize specialist condenses
    summary = summarize_agent.run({"documents": docs, "max_length": 500})
    # 3. Format specialist produces final output
    report = format_agent.run({"summary": summary, "format": "markdown"})
    return report
```

## Testing Specialists

- Unit test each specialist in isolation
- Test boundary conditions (what happens when input is out of scope?)
- Test escalation logic (specialist correctly identifies when to hand off)
- Test in combination with orchestrator (integration test)

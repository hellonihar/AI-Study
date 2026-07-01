# 06 - Agent Application: LangGraph Research Assistant

## Overview

Build a single-agent research assistant using LangGraph that implements the ReAct (Reasoning + Acting) pattern. Given a question, the agent decides whether to search Wikipedia, read a page, or synthesize an answer — looping until it has enough information or hits a step limit.

## Tech Stack

- **Agent framework** — LangGraph (state graph, not just chain)
- **LLM** — GPT-4o-mini or Claude Haiku (cheap, fast reasoning)
- **Tools** — Wikipedia API wrapper, web fetch (httpx)
- **Memory** — LangGraph's built-in state persistence across turns

## Architecture & Design

```
                    ┌─────────────────┐
                    │  user message    │
                    └────────┬────────┘
                             │
              ┌──────────────▼──────────────┐
              │  AGENT STATE                │
              │  { messages: [...]          │
              │    step: 0,                 │
              │    max_steps: 10 }          │
              └──────────────┬──────────────┘
                             │
              ┌──────────────▼──────────────┐
              │  LLM decides next action     │
              │  Thought: I need to find X   │
              │  Action: search_wikipedia(X) │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────┐
                    │  TOOL EXECUTION  │
                    ├─────────────────┤
                    │  search_wikipedia│
                    │  read_page      │
                    │  final_answer    │
                    └────────┬────────┘
                             │
              ┌──────────────▼──────────────┐
              │  Append observation to       │
              │  state, loop back to LLM     │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────┐
                    │  step >= max?    │
                    │  or tool=final?  │──► return response
                    └─────────────────┘
```

**Design decisions:**

- **LangGraph** instead of LangChain's AgentExecutor because LangGraph models the agent as a state machine graph rather than a loop. This makes it easier to add conditional routing, human-in-the-loop breaks, and parallel tool calls later.
- **ReAct pattern** is the default: Thought → Action → Observation → Thought... until a final answer. This is transparent — you can read every reasoning step.
- **Wikipedia tool** over general web search because it has a clean, structured API and the content quality is consistent. A real system would add more tools (search, calculator, database).
- **Step limit of 10** prevents infinite loops and runaway costs.

## Setup & Run

1. Install dependencies:
   ```bash
   pip install langgraph langchain-openai wikipedia-api httpx
   ```
2. Define the agent:
   ```python
   # agent.py
   from langgraph.graph import StateGraph, END
   from typing import TypedDict, List
   from langchain_openai import ChatOpenAI
   import wikipedia

   class AgentState(TypedDict):
       messages: List
       step: int
       max_steps: int

   llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

   def search_wikipedia(query: str) -> str:
       try:
           results = wikipedia.search(query)
           return f"Top results: {results[:3]}"
       except Exception as e:
           return f"Error: {e}"

   def read_page(title: str) -> str:
       try:
           page = wikipedia.page(title)
           return page.summary[:2000]
       except Exception as e:
           return f"Error: {e}"

   tools = {"search_wikipedia": search_wikipedia, "read_page": read_page}

   def call_llm(state: AgentState):
       response = llm.invoke(state["messages"] + [{
           "role": "system",
           "content": "You are a research assistant. You have tools: search_wikipedia(query) and read_page(title). "
                      "Think step by step. When you have enough info, say FINAL ANSWER: ..."
       }])
       state["messages"].append(response)
       state["step"] += 1
       return state

   def route(state: AgentState):
       if state["step"] >= state["max_steps"]:
           return END
       last = state["messages"][-1].content
       if "FINAL ANSWER" in last:
           return END
       # Parse tool call from LLM output
       if "search_wikipedia(" in last:
           # extract query and call tool (simplified)
           pass
       return "call_llm"

   graph = StateGraph(AgentState)
   graph.add_node("call_llm", call_llm)
   graph.set_entry_point("call_llm")
   graph.add_conditional_edges("call_llm", route)
   app = graph.compile()
   ```
3. Run a query:
   ```python
   result = app.invoke({
       "messages": [{"role": "user", "content": "What is the Transformer architecture and who proposed it?"}],
       "step": 0, "max_steps": 10
   })
   print(result["messages"][-1].content)
   ```

## What You Learn

- The ReAct (Reasoning + Acting) pattern and why it outperforms single-shot prompting
- State graph architecture — an agent is a loop with conditional routing, not a linear chain
- Tool definition and tool calling — the LLM decides which tool to use based on the problem
- The planning loop: how the agent decomposes a question into sub-steps automatically
- Step limits and cost control — every LLM call costs money; agents amplify that cost
- Observability — examining the step-by-step reasoning trace for debugging

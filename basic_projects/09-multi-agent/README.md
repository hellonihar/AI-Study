# 09 - Multi-Agent: Travel Planning Team

## Overview

Build a multi-agent travel planning system with a **Supervisor Agent** that delegates to three specialist agents (Search, Weather, Budget) and synthesizes their outputs into a final itinerary. Each specialist agent has its own tools, prompt, and model — demonstrating hierarchical orchestration, tool isolation, and result aggregation.

## Tech Stack

- **Orchestration** — LangGraph (with branching sub-graphs)
- **Agents** — 1 Supervisor + 3 Specialists, each with its own system prompt
- **LLM** — GPT-4o-mini for specialists, GPT-4o-mini (same or slightly larger) for Supervisor
- **Tools** — Web search (DuckDuckGo/httpx), weather API (Open-Meteo, free, no key), calculator
- **State** — Shared context object that each agent reads/writes

## Architecture & Design

```
                         ┌──────────────────────────┐
                         │     USER REQUEST          │
                         │  "Plan a 5-day trip to    │
                         │   Tokyo in October with   │
                         │   a $3000 budget"         │
                         └───────────┬──────────────┘
                                     │
                         ┌───────────▼──────────────┐
                         │   SUPERVISOR AGENT        │
                         │   - Decomposes request    │
                         │   - Assigns tasks         │
                         │   - Sets deadlines        │
                         └────┬──────┬───────┬──────┘
                              │      │       │
              ┌───────────────┘      │       └───────────────┐
              │                      │                       │
     ┌────────▼────────┐  ┌─────────▼────────┐  ┌──────────▼─────────┐
     │  SEARCH AGENT    │  │  WEATHER AGENT    │  │  BUDGET AGENT       │
     │                   │  │                   │  │                     │
     │  Tools:           │  │  Tools:           │  │  Tools:             │
     │  - search_flights │  │  - get_forecast   │  │  - currency_convert │
     │  - search_hotels  │  │  - get_seasonal   │  │  - cost_estimator   │
     │  - search_attractions│  │  - pack_advice │  │  - budget_breakdown │
     │                   │  │                   │  │                     │
     │  Output:          │  │  Output:          │  │  Output:            │
     │  flight+hotel     │  │  weather report   │  │  cost breakdown     │
     │  options          │  │  + packing list    │  │  + recommendations  │
     └────────┬──────────┘  └─────────┬─────────┘  └──────────┬──────────┘
              │                      │                       │
              └───────────────┐      │       ┌───────────────┘
                              │      │       │
                         ┌────▼──────▼───────▼──────┐
                         │   SUPERVISOR AGENT        │
                         │   - Collects all outputs  │
                         │   - Resolves conflicts    │
                         │   - Synthesizes itinerary │
                         └───────────┬──────────────┘
                                     │
                         ┌───────────▼──────────────┐
                         │   FINAL ITINERARY         │
                         │   Day-by-day plan with:   │
                         │   - Flights & hotels      │
                         │   - Weather advisory      │
                         │   - Daily budget          │
                         │   - Attractions           │
                         └──────────────────────────┘
```

**Design decisions:**

- **Hierarchical orchestration** (Supervisor → Specialists) rather than peer-to-peer because it's the most common and scalable pattern. Each specialist is isolated — it can't call other agents' tools, and it only knows about its own domain.
- **Shared state object** (a Python dict or a Pydantic model) that flows through the graph. The Supervisor writes task descriptions; each Specialist reads its task and writes its findings; the Supervisor reads all findings and writes the final answer. This avoids the complexity of agent-to-agent messaging while still demonstrating coordination.
- **Parallel execution** — the three specialists can run concurrently because they don't depend on each other. LangGraph supports fan-out/fan-in natively.
- **Each specialist gets a different system prompt** tailored to its role. The Search Agent's prompt says "You are a travel search expert. Always provide at least 3 options." The Budget Agent's prompt says "Be conservative in estimates. Flag anything over budget."
- **Independent tool sets** — only the Search Agent can call `search_flights`; the Weather Agent can't. This enforces least privilege at the agent level.

## Setup & Run

1. Install dependencies:
   ```bash
   pip install langgraph langchain-openai httpx
   ```
2. Define the shared state:
   ```python
   # state.py
   from typing import Optional
   from pydantic import BaseModel

   class TravelState(BaseModel):
       user_request: str
       supervisor_plan: str = ""
       search_results: str = ""
       weather_report: str = ""
       budget_report: str = ""
       final_itinerary: str = ""
       errors: list[str] = []
   ```
3. Define the agents (simplified):
   ```python
   # agents.py
   from langchain_openai import ChatOpenAI

   llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

   async def search_agent(state: TravelState) -> TravelState:
       # In a real implementation, this agent has tools:
       # search_flights(destination, dates)
       # search_hotels(city, check_in, check_out, budget)
       # search_attractions(city, interests)
       prompt = f"""You are a travel search specialist. Find flight, hotel, and attraction options.
   Task: {state.supervisor_plan}
   User request: {state.user_request}
   Return at least 3 options for flights, 3 for hotels, and 5 attractions."""
       state.search_results = llm.invoke(prompt).content
       return state

   async def weather_agent(state: TravelState) -> TravelState:
       prompt = f"""You are a weather specialist. Use Open-Meteo API data.
   Task: {state.supervisor_plan}
   Provide: avg temp, rainfall probability, daylight hours, and packing recommendations."""
       state.weather_report = llm.invoke(prompt).content
       return state

   async def budget_agent(state: TravelState) -> TravelState:
       prompt = f"""You are a budget analyst. Calculate costs conservatively.
   Task: {state.supervisor_plan}
   Include: flights, hotels, food ($50/day), transport ($20/day), attractions, misc (20% buffer).
   Flag anything exceeding the stated budget."""
       state.budget_report = llm.invoke(prompt).content
       return state
   ```
4. Wire the orchestration graph:
   ```python
   # graph.py
   from langgraph.graph import StateGraph, END
   import asyncio

   graph = StateGraph(TravelState)

   def supervisor_decompose(state: TravelState):
       prompt = f"""Decompose this travel request into 3 parallel tasks:
   1. SEARCH: find flights, hotels, attractions
   2. WEATHER: check forecast and seasonal conditions
   3. BUDGET: estimate total cost and daily breakdown
   User request: {state.user_request}"""
       state.supervisor_plan = llm.invoke(prompt).content
       return state

   async def parallel_specialists(state: TravelState):
       results = await asyncio.gather(
           search_agent(state),
           weather_agent(state),
           budget_agent(state))
       # asyncio.gather returns copies; merge manually
       for r in results:
           if r.search_results: state.search_results = r.search_results
           if r.weather_report: state.weather_report = r.weather_report
           if r.budget_report: state.budget_report = r.budget_report
       return state

   def supervisor_synthesize(state: TravelState):
       prompt = f"""You are a travel planning supervisor. Synthesize these reports into a day-by-day itinerary.
   Original request: {state.user_request}
   Search results: {state.search_results}
   Weather: {state.weather_report}
   Budget: {state.budget_report}
   Create a detailed 5-day plan with morning/afternoon/evening activities, including:
   - Flight and hotel names
   - Weather-appropriate activities
   - Daily budget tracking
   - Packing recommendations"""
       state.final_itinerary = llm.invoke(prompt).content
       return state

   graph.add_node("decompose", supervisor_decompose)
   graph.add_node("parallel", parallel_specialists)
   graph.add_node("synthesize", supervisor_synthesize)
   graph.set_entry_point("decompose")
   graph.add_edge("decompose", "parallel")
   graph.add_edge("parallel", "synthesize")
   graph.add_edge("synthesize", END)
   app = graph.compile()
   ```
5. Run a query:
   ```python
   result = app.invoke(TravelState(
       user_request="Plan a 5-day trip to Tokyo in October with a $3000 budget. "
                    "I like history, food, and photography."))
   print(result.final_itinerary)
   ```

## What You Learn

- **Hierarchical orchestration** — a supervisor that decomposes, delegates, and synthesizes
- **Parallel agent execution** — independent specialists run concurrently, not sequentially
- **Tool isolation** — each agent has its own toolset; no agent can call another agent's tools
- **Shared state pattern** — a single state object that flows through the graph, keeping the system observable and debuggable
- **Specialist prompting** — tailoring system prompts per agent role (search, weather, budget) rather than one prompt for everything
- **Error isolation** — if the Weather Agent fails, the other two still produce results and the Supervisor can note the gap
- **Scaling pattern** — this same architecture works for 3 agents or 30, as long as they can run in parallel groups

## Next Steps / Extensions

- **Add a human-in-the-loop** step where the Supervisor presents options and the user chooses before the final itinerary
- **Add reflection** — after synthesis, an Audit Agent reviews the final plan for consistency and flags issues
- **Add tool-level monitoring** — log every tool call with latency and success/failure
- **Replace simulated tools with real APIs** — Amadeus for flights, Open-Meteo for weather, Google Places for attractions

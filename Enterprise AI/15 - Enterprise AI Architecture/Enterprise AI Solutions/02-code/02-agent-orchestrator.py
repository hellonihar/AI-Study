"""
Agent orchestrator: manage multi-agent workflow with supervisor pattern.

Run: python 02-agent-orchestrator.py
"""

import time

print("=== Agent Orchestrator ===\n")

class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def run(self, task):
        return f"[{self.name}] processed: {task}"

class Supervisor:
    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.name] = agent

    def delegate(self, task, agent_name):
        agent = self.agents.get(agent_name)
        if not agent:
            return f"No agent: {agent_name}"
        return agent.run(task)

    def orchestrate(self, request):
        plan = self.plan_request(request)
        results = {}
        for step in plan:
            agent_name, task = step
            try:
                result = self.delegate(task, agent_name)
                results[agent_name] = result
            except Exception as e:
                results[agent_name] = f"FAILED: {e}"
        return self.synthesize(request, results)

    def plan_request(self, request):
        if "summarize" in request.lower():
            return [("reader", f"read {request}"), ("summarizer", request)]
        elif "code" in request.lower():
            return [("coder", request), ("reviewer", request)]
        elif "search" in request.lower():
            return [("searcher", request), ("ranker", request)]
        else:
            return [("general", request)]

    def synthesize(self, request, results):
        summary = "; ".join(f"{k}: {v}" for k, v in results.items())
        return f"Final result for '{request[:40]}...': {summary}"

supervisor = Supervisor()
supervisor.register(Agent("reader", "Reads documents"))
supervisor.register(Agent("summarizer", "Summarizes content"))
supervisor.register(Agent("coder", "Generates code"))
supervisor.register(Agent("reviewer", "Reviews code quality"))
supervisor.register(Agent("searcher", "Searches knowledge base"))
supervisor.register(Agent("ranker", "Ranks search results"))
supervisor.register(Agent("general", "General assistant"))

REQUESTS = [
    "Summarize the latest AI research papers",
    "Write Python code for a REST API client",
    "Search for enterprise RAG patterns",
]

for req in REQUESTS:
    print(f"Request: {req}")
    start = time.time()
    result = supervisor.orchestrate(req)
    elapsed = time.time() - start
    print(f"  Result: {result[:100]}...")
    print(f"  Time: {elapsed:.3f}s")
    print()

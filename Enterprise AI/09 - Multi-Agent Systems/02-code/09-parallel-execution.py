"""
Parallel execution: run agents in parallel with dependency DAG.

Run: python 09-parallel-execution.py

Requirements: none (stdlib only)
"""

import json
import time
import threading
from collections import defaultdict

print("=== Parallel Execution ===\n")

class Agent:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def run(self, task):
        time.sleep(self.duration * 0.01)
        return {"agent": self.name, "result": f"done in {self.duration*10}ms",
                "task": task[:30]}

AGENTS = {
    "search": Agent("search_agent", 5),
    "analyze": Agent("analyze_agent", 8),
    "code_gen": Agent("code_gen_agent", 10),
    "data_fetch": Agent("data_fetch_agent", 3),
    "summarize": Agent("summarize_agent", 4),
    "format": Agent("format_agent", 2),
}

def run_agent(agent_name, task, results, idx):
    agent = AGENTS[agent_name]
    result = agent.run(task)
    results[idx] = result
    print(f"  [{idx}] {agent_name} completed ({agent.duration*10}ms)")

print("Task: Research AI trends and generate report")
print()

tasks = [
    ("search", "Search for AI trends"),
    ("data_fetch", "Fetch market data"),
    ("analyze", "Analyze findings"),
    ("code_gen", "Generate charts"),
    ("summarize", "Summarize results"),
    ("format", "Format report"),
]

dependencies = {
    "search": [],
    "data_fetch": [],
    "analyze": ["search", "data_fetch"],
    "code_gen": ["analyze"],
    "summarize": ["analyze"],
    "format": ["code_gen", "summarize"],
}

print("Dependency DAG:")
for step, deps in dependencies.items():
    deps_str = f" (after: {', '.join(deps)})" if deps else " (no deps)"
    print(f"  {step}{deps_str}")

print(f"\nExecution:\n")

completed = set()
results_list = [None] * len(tasks)
task_map = {name: (i, task) for i, (name, task) in enumerate(tasks)}

while len(completed) < len(tasks):
    ready = []
    for name, deps in dependencies.items():
        if name in completed:
            continue
        if all(d in completed for d in deps):
            ready.append(name)

    threads = []
    for name in ready:
        idx, task = task_map[name]
        t = threading.Thread(target=run_agent, args=(name, task, results_list, idx))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    completed.update(ready)

print(f"\n{'='*60}")
print("Results")
print(f"{'='*60}")
for r in results_list:
    if r:
        print(f"  {r['agent']:<20} → {r['result']}")

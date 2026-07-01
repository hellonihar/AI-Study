"""
Supervisor agent: delegates tasks to specialist workers and synthesizes results.

Run: python 01-supervisor-agent.py

Requirements: none (stdlib only)
"""

import json
import time
import random

print("=== Supervisor Agent ===\n")

class Specialist:
    def __init__(self, name, expertise):
        self.name = name
        self.expertise = expertise

    def run(self, task):
        time.sleep(random.uniform(0.02, 0.08))
        return {"agent": self.name, "result": f"{self.expertise} result for: {task[:30]}"}

SPECIALISTS = [
    Specialist("search_agent", "Information retrieval and search"),
    Specialist("analyze_agent", "Data analysis and pattern extraction"),
    Specialist("summarize_agent", "Text summarization and condensation"),
    Specialist("format_agent", "Report formatting and presentation"),
]

class Supervisor:
    def __init__(self):
        self.specialists = SPECIALISTS

    def decompose(self, task):
        return [
            {"id": "search", "description": "Find relevant information", "specialist": "search_agent"},
            {"id": "analyze", "description": "Analyze findings", "specialist": "analyze_agent",
             "depends_on": ["search"]},
            {"id": "summarize", "description": "Summarize analysis", "specialist": "summarize_agent",
             "depends_on": ["analyze"]},
            {"id": "format", "description": "Format final output", "specialist": "format_agent",
             "depends_on": ["summarize"]},
        ]

    def select_worker(self, subtask):
        for s in self.specialists:
            if s.name == subtask["specialist"]:
                return s
        return self.specialists[0]

    def synthesize(self, results):
        return {"final_report": f"Report synthesized from {len(results)} agents", "details": results}

    def run(self, task):
        print(f"Supervisor received: {task}\n")

        plan = self.decompose(task)
        print(f"Decomposed into {len(plan)} subtasks:\n")
        for s in plan:
            deps = f" (after: {s.get('depends_on', 'none')})" if s.get('depends_on') else ""
            print(f"  {s['id']}: {s['description']}{deps}")

        completed = {}
        print(f"\nExecution:")
        for step in plan:
            worker = self.select_worker(step)
            print(f"\n  → Delegating to {worker.name}: {step['description']}")
            result = worker.run(step["description"])
            completed[step["id"]] = result
            print(f"    Result: {result['result'][:50]}...")

        report = self.synthesize(completed)
        print(f"\n{'='*60}")
        print("Synthesized Report")
        print(f"{'='*60}")
        print(f"  {report['final_report']}")
        for agent_name, detail in completed.items():
            print(f"  - {detail['agent']}: {detail['result'][:40]}...")

        return report

supervisor = Supervisor()
supervisor.run("Research AI trends and write a market analysis report")

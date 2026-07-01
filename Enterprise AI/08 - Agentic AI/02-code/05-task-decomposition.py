"""
Task decomposition: break complex tasks into subtasks with dependency tracking.

Run: python 05-task-decomposition.py

Requirements: none (stdlib only)
"""

import json
import time

print("=== Task Decomposition ===\n")

class Task:
    def __init__(self, id, description, depends_on=None, action=None):
        self.id = id
        self.description = description
        self.depends_on = depends_on or []
        self.action = action
        self.status = "pending"
        self.result = None

    def execute(self):
        print(f"    Executing: {self.description}")
        time.sleep(0.05)
        if self.action:
            self.result = self.action()
        self.status = "completed"
        return self.result

class DecompositionAgent:
    def __init__(self):
        self.tasks = []
        self.step = 0

    def decompose(self, goal):
        print(f"Goal: {goal}\n")
        print("Decomposition:")

        if "report" in goal.lower() or "research" in goal.lower():
            self.tasks = [
                Task(1, "Search for relevant information",
                     action=lambda: {"data": "search results"}),
                Task(2, "Extract key findings",
                     depends_on=[1],
                     action=lambda: {"findings": ["Finding A", "Finding B"]}),
                Task(3, "Analyze and compare",
                     depends_on=[2],
                     action=lambda: {"analysis": "Key trends identified"}),
                Task(4, "Generate final report",
                     depends_on=[3],
                     action=lambda: {"report": "Final report content"}),
            ]
        elif "code" in goal.lower() or "implement" in goal.lower():
            self.tasks = [
                Task(1, "Design solution architecture",
                     action=lambda: {"design": "architecture plan"}),
                Task(2, "Implement core logic",
                     depends_on=[1],
                     action=lambda: {"code": "implementation"}),
                Task(3, "Write tests",
                     depends_on=[2],
                     action=lambda: {"tests": "test cases"}),
                Task(4, "Review and optimize",
                     depends_on=[2, 3],
                     action=lambda: {"review": "optimization suggestions"}),
            ]
        else:
            self.tasks = [
                Task(1, f"Understand: {goal}",
                     action=lambda: {"understanding": goal}),
                Task(2, "Process and respond",
                     depends_on=[1],
                     action=lambda: {"response": f"Processed: {goal}"}),
            ]

        for t in self.tasks:
            deps = f" (after: {[d for d in t.depends_on]})" if t.depends_on else ""
            print(f"  Task {t.id}: {t.description}{deps}")

        return self.tasks

    def get_ready_tasks(self):
        return [t for t in self.tasks if t.status == "pending"
                and all(self.tasks[d-1].status == "completed" for d in t.depends_on)]

    def execute(self):
        print(f"\nExecution:\n")
        while True:
            ready = self.get_ready_tasks()
            if not ready:
                break

            for task in ready:
                task.execute()
                print(f"    → Completed: {task.description}")
                print()

        print(f"All {len(self.tasks)} tasks completed")

GOALS = [
    "Research AI trends and write report",
    "Implement a REST API endpoint",
    "What is the weather?",
]

for goal in GOALS:
    print("-" * 60)
    agent = DecompositionAgent()
    agent.decompose(goal)
    agent.execute()
    print()

print(f"{'='*60}")
print("Decomposition Pattern")
print(f"{'='*60}")
print("  1. Decompose: break goal into dependent sub-tasks")
print("  2. Schedule: execute tasks respecting dependencies")
print("  3. Parallel: independent tasks can run simultaneously")
print("  4. Monitor: track progress and handle failures")

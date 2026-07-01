"""
Specialist agents: multiple specialists with different capabilities and routing.

Run: python 05-specialist-agents.py

Requirements: none (stdlib only)
"""

import json
import time
import random

print("=== Specialist Agents ===\n")

class SpecialistAgent:
    def __init__(self, name, expertise, capabilities):
        self.name = name
        self.expertise = expertise
        self.capabilities = capabilities
        self.tasks_completed = 0

    def can_handle(self, task):
        return any(cap in task.lower() for cap in self.capabilities)

    def process(self, task):
        self.tasks_completed += 1
        time.sleep(random.uniform(0.02, 0.06))
        return {
            "agent": self.name,
            "expertise": self.expertise,
            "result": f"{self.expertise} result: {task[:30]}",
        }

SPECIALISTS = [
    SpecialistAgent("web_search", "Web and information search",
                    ["search", "find", "lookup", "google", "web"]),
    SpecialistAgent("data_analysis", "Data analysis and statistics",
                    ["analyze", "analyze", "chart", "statistics", "trend", "data"]),
    SpecialistAgent("code_gen", "Code generation and programming",
                    ["code", "program", "function", "implement", "debug", "python"]),
    SpecialistAgent("writing", "Content writing and editing",
                    ["write", "draft", "edit", "content", "blog", "email"]),
    SpecialistAgent("summarization", "Text summarization",
                    ["summarize", "summary", "condense", "tl;dr", "brief"]),
]

class AntiAgent(SpecialistAgent):
    def __init__(self):
        super().__init__("general", "General assistant",
                        ["hello", "hi", "help", "what", "who", "how", "why", ""])

    def can_handle(self, task):
        return True

    def process(self, task):
        self.tasks_completed += 1
        return {"agent": "general", "expertise": "general",
                "result": f"General response for: {task[:40]}"}

all_specialists = SPECIALISTS + [AntiAgent()]

QUERIES = [
    "search for quantum computing breakthroughs",
    "write a blog post about AI",
    "analyze the sales data trends",
    "implement a binary search function",
    "summarize this article about machine learning",
    "hello, what can you do?",
]

for q in QUERIES:
    print(f"Task: {q}")
    best_match = None
    best_score = 0

    for specialist in all_specialists:
        if specialist.can_handle(q):
            score = sum(10 for cap in specialist.capabilities if cap and cap in q.lower())
            if len(specialist.capabilities) == 1 and specialist.capabilities[0] == "":
                score = 1
            if score > best_score:
                best_score = score
                best_match = specialist

    if best_match:
        result = best_match.process(q)
        print(f"  → Routed to: {best_match.name} ({best_match.expertise})")
        print(f"    {result['result']}")
    print()

print(f"{'='*60}")
print("Specialist Utilization")
print(f"{'='*60}")
for s in all_specialists:
    bar = "█" * s.tasks_completed * 4
    print(f"  {s.name:<20} {s.tasks_completed} tasks {bar}")

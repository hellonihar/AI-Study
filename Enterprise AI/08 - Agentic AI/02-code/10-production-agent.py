"""
Production agent: combining all patterns — memory, tools, reflection, guardrails, cost tracking, observability.

Run: python 10-production-agent.py

Requirements: none (stdlib only)
"""

import json
import time
import uuid
import re
from datetime import datetime

print("=== Production Agent ===\n")

TOOLS = {
    "search": lambda q: {"results": [f"Result for {q}"]},
    "get_time": lambda: {"time": datetime.utcnow().isoformat()},
}

class SafetyLayer:
    @staticmethod
    def check_input(text):
        blocked = ["ignore instructions", "hack", "exploit"]
        for b in blocked:
            if b in text.lower():
                raise ValueError(f"Input blocked: {b}")
        return True

    @staticmethod
    def check_output(text):
        text = re.sub(r"\b\w+@\w+\.\w+\b", "[EMAIL]", text)
        return text

class Memory:
    def __init__(self):
        self.turns = []

    def add(self, role, content):
        self.turns.append({"role": role, "content": content, "time": time.time()})

    def recent(self, n=5):
        return self.turns[-n:]

class CircuitBreaker:
    def __init__(self, threshold=3):
        self.failures = 0
        self.threshold = threshold
        self.open = False

    def call(self, fn, *args, **kwargs):
        if self.open:
            raise Exception("Circuit open")
        try:
            result = fn(*args, **kwargs)
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.threshold:
                self.open = True
            raise

class CostTracker:
    def __init__(self, budget=0.50):
        self.budget = budget
        self.spent = 0.0
        self.steps = []

    def track(self, model, inp, out, action):
        pricing = {"gpt-4o": {"input": 0.00001, "output": 0.00003},
                   "gpt-4o-mini": {"input": 0.0000015, "output": 0.000006}}
        p = pricing.get(model, {"input": 0, "output": 0})
        cost = inp * p["input"] + out * p["output"]
        self.spent += cost
        self.steps.append({"action": action, "model": model, "cost": round(cost, 5)})
        if self.spent > self.budget:
            raise Exception(f"Budget exceeded: ${self.spent:.2f}")
        return cost

class ProductionAgent:
    def __init__(self):
        self.safety = SafetyLayer()
        self.memory = Memory()
        self.circuit = CircuitBreaker(threshold=2)
        self.cost = CostTracker(budget=0.30)
        self.task_id = str(uuid.uuid4())[:8]
        self.max_steps = 10

    def reason(self, query, context):
        q = query.lower()
        if "time" in q:
            return {"action": "tool", "tool": "get_time", "params": {}}
        if "search" in q or "find" in q:
            return {"action": "tool", "tool": "search",
                    "params": {"q": q.replace("search", "").replace("find", "").strip() or "default"}}
        return {"action": "respond", "content": f"Answer: {query}"}

    def execute_tool(self, tool_name, params):
        return TOOLS[tool_name](**params)

    def reflect(self, result):
        return result

    def run(self, query):
        print(f"Task ID: {self.task_id}")
        print(f"Query: {query}\n")

        self.safety.check_input(query)
        self.memory.add("user", query)

        context = self.memory.recent()
        response = None

        for step in range(1, self.max_steps + 1):
            print(f"  Step {step}: ", end="")

            decision = self.reason(query, context)
            print(f"{decision['action']} ", end="")

            if decision["action"] == "respond":
                response = self.safety.check_output(decision["content"])
                self.cost.track("gpt-4o-mini", 100, 50, decision["action"])
                print(f"→ {response}")
                break

            elif decision["action"] == "tool":
                try:
                    result = self.circuit.call(
                        self.execute_tool, decision["tool"], **decision["params"])
                    self.cost.track("gpt-4o-mini", 80, 30, f"tool:{decision['tool']}")
                    print(f"→ {json.dumps(result)}")

                    reflection = self.reflect(result)
                    context.append({"role": "tool", "content": str(reflection)})

                except Exception as e:
                    self.cost.track("gpt-4o-mini", 50, 10, f"error:{decision['tool']}")
                    print(f"→ Error: {e}")
                    if self.circuit.open:
                        response = "Service unavailable. Please try again later."
                        break

        if not response:
            response = "Task completed."

        self.memory.add("assistant", response)

        print(f"\n{'='*60}")
        print("Agent Summary")
        print(f"{'='*60}")
        print(f"  Task ID:     {self.task_id}")
        print(f"  Steps:       {step}")
        print(f"  Total cost:  ${self.cost.spent:.4f}")
        print(f"  Budget:      ${self.cost.budget:.2f}")
        print(f"  Tools used:  {list(TOOLS.keys())}")
        print(f"  Safety:      input + output guardrails active")
        print(f"  Circuit:     {'OPEN' if self.circuit.open else 'CLOSED'}")
        print(f"  Memory:      {len(self.memory.turns)} turns stored")

        print(f"\n  Final response: {response}")
        return response

agent = ProductionAgent()

QUERIES = [
    "What time is it?",
    "search for AI news",
    "Hello, how are you?",
]

for q in QUERIES:
    print("-" * 60)
    agent = ProductionAgent()
    agent.run(q)
    print()

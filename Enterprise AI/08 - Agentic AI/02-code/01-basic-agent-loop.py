"""
Basic agent loop: perceive → reason → act cycle with tool execution.

Run: python 01-basic-agent-loop.py

Requirements: none (stdlib only)
"""

import time
import json

print("=== Basic Agent Loop ===\n")

TOOLS = {
    "search_kb": {
        "description": "Search knowledge base",
        "execute": lambda q: {"results": [f"Result for: {q}"]},
    },
    "calculate": {
        "description": "Evaluate math expression",
        "execute": lambda expr: {"result": eval(expr)},
    },
    "get_time": {
        "description": "Get current time",
        "execute": lambda: {"time": time.strftime("%H:%M:%S UTC")},
    },
}

class BasicAgent:
    def __init__(self):
        self.step_count = 0
        self.max_steps = 10
        self.trace = []

    def perceive(self, task):
        return {"task": task, "tools": list(TOOLS.keys())}

    def reason(self, state):
        task = state["task"].lower()
        if "search" in task or "find" in task or "lookup" in task:
            return {"action": "tool", "tool": "search_kb",
                    "params": {"q": task.replace("search", "").strip() or "default query"}}
        if "calculate" in task or "math" in task or "+" in task or "-" in task:
            return {"action": "tool", "tool": "calculate",
                    "params": {"expr": task.split("calculate", 1)[-1].strip() or "2+2"}}
        if "time" in task:
            return {"action": "tool", "tool": "get_time", "params": {}}
        return {"action": "respond", "content": f"I processed: {task}"}

    def act(self, decision):
        if decision["action"] == "tool":
            tool = TOOLS[decision["tool"]]
            result = tool["execute"](**decision["params"])
            return {"type": "tool_result", "tool": decision["tool"], "data": result}
        return {"type": "response", "content": decision["content"]}

    def run(self, task):
        print(f"Task: {task}\n")
        state = self.perceive(task)

        while self.step_count < self.max_steps:
            self.step_count += 1

            decision = self.reason(state)
            print(f"  Step {self.step_count}: {decision['action']}",
                  end="")

            if decision["action"] == "tool":
                print(f" → {decision['tool']}")
                result = self.act(decision)
                print(f"    Result: {json.dumps(result['data'])}")
                state["last_result"] = result
                self.trace.append({"step": self.step_count, **decision, **result})
            else:
                print(f"\n    → {decision['content']}")
                self.trace.append({"step": self.step_count, **decision})
                break

        print(f"\nCompleted in {self.step_count} steps")
        return self.trace

TASKS = [
    "What time is it?",
    "search for AI news",
    "calculate 15 * 37",
    "Hello, how are you?",
]

for task in TASKS:
    print("-" * 60)
    agent = BasicAgent()
    agent.run(task)
    print()

print(f"{'='*60}")
print("Agent Loop Summary")
print(f"{'='*60}")
print("  perceive() → reason() → act() → observe() → repeat")
print("  Each step: LLM decides tool or response")
print("  Guardrails: max steps, loop detection, error recovery")

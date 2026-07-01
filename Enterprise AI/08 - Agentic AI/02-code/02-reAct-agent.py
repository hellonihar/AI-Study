"""
ReAct agent: interleaved reasoning traces with tool execution.

Run: python 02-reAct-agent.py

Requirements: none (stdlib only)
"""

import json
import time

print("=== ReAct Agent ===\n")

TOOLS = {
    "search": {
        "fn": lambda q: f"Results for '{q}': Paris is the capital of France.",
    },
    "lookup": {
        "fn": lambda term: f"Definition of {term}: A principle or standard.",
    },
    "calculate": {
        "fn": lambda expr: f"Result: {eval(expr)}",
    },
}

class ReActAgent:
    def __init__(self):
        self.trace = []
        self.step = 0
        self.max_steps = 8

    def reason(self, query, observation=""):
        self.step += 1

        if self.step > self.max_steps:
            return {"action": "respond", "content": "Max steps reached."}

        q = query.lower()

        if "capital" in q or "paris" in q or "france" in q:
            thought = "I need to search for the capital of France."
            if not observation:
                return {"action": "search", "params": {"q": "capital of France"},
                        "thought": thought}
            else:
                thought = "I found Paris is the capital. I can answer now."
                return {"action": "respond", "content": "The capital of France is Paris.",
                        "thought": thought}

        if "calculate" in q or "+" in q or "*" in q or "/" in q:
            thought = "I need to calculate this expression."
            return {"action": "calculate", "params": {"expr": q.split()[-1]},
                    "thought": thought}

        thought = "I can respond directly to this query."
        return {"action": "respond", "content": f"I understand your query: {query}",
                "thought": thought}

    def act(self, decision):
        if decision["action"] in TOOLS:
            tool = TOOLS[decision["action"]]
            return tool["fn"](**decision["params"])
        return decision["content"]

    def run(self, query):
        print(f"Query: {query}\n")

        observation = ""
        final_response = None

        while self.step < self.max_steps:
            decision = self.reason(query, observation)

            print(f"  Step {self.step}:")
            print(f"    Thought: {decision.get('thought', 'N/A')}")

            if decision["action"] == "respond":
                print(f"    Action: respond")
                print(f"    Response: {decision['content']}")
                final_response = decision['content']
                break

            print(f"    Action: {decision['action']}({decision['params']})")
            observation = self.act(decision)
            print(f"    Observation: {observation}")

            self.trace.append({
                "step": self.step,
                "thought": decision.get("thought"),
                "action": decision["action"],
                "observation": observation,
            })

        return final_response or "No response generated."

QUERIES = [
    "What is the capital of France?",
    "calculate 42 * 3",
]

for q in QUERIES:
    print("-" * 60)
    agent = ReActAgent()
    result = agent.run(q)
    print(f"\n  Final: {result}\n")

print(f"{'='*60}")
print("ReAct Pattern")
print(f"{'='*60}")
print("  Thought → Action → Observation → Thought → ... → Answer")
print("  Each step is fully interpretable and debuggable")
print("  Actions can be tools, searches, or final responses")

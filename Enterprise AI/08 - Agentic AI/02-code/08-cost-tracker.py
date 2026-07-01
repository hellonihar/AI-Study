"""
Cost tracker: monitor token usage, cost, and budget per agent task.

Run: python 08-cost-tracker.py

Requirements: none (stdlib only)
"""

import json
import time
import random
from datetime import datetime

print("=== Agent Cost Tracker ===\n")

PRICING = {
    "gpt-4o": {"input": 0.00001, "output": 0.00003},
    "gpt-4o-mini": {"input": 0.0000015, "output": 0.000006},
    "claude-3-haiku": {"input": 0.0000025, "output": 0.0000125},
    "claude-3-opus": {"input": 0.000015, "output": 0.000075},
}

class CostTracker:
    def __init__(self, budget=1.00):
        self.budget = budget
        self.spent = 0.0
        self.steps = []
        self.start_time = datetime.now().isoformat()

    def track_step(self, model, input_tokens, output_tokens, action):
        pricing = PRICING.get(model, {"input": 0.0, "output": 0.0})
        cost = input_tokens * pricing["input"] + output_tokens * pricing["output"]
        self.spent += cost

        step = {
            "step": len(self.steps) + 1,
            "model": model,
            "action": action,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(cost, 5),
            "cumulative": round(self.spent, 5),
        }
        self.steps.append(step)
        return step

    def within_budget(self):
        return self.spent < self.budget

    def budget_remaining(self):
        return self.budget - self.spent

    def summary(self):
        return {
            "total_steps": len(self.steps),
            "total_cost": round(self.spent, 4),
            "budget": self.budget,
            "budget_remaining": round(self.budget_remaining(), 4),
            "total_input_tokens": sum(s["input_tokens"] for s in self.steps),
            "total_output_tokens": sum(s["output_tokens"] for s in self.steps),
            "models_used": list(set(s["model"] for s in self.steps)),
        }

class AgentWithCostTracking:
    def __init__(self):
        self.cost_tracker = CostTracker(budget=0.50)

    def run(self, task):
        print(f"Task: {task}\n")
        print(f"{'Step':<6} {'Model':<16} {'Action':<35} "
              f"{'Tokens':<10} {'Cost':<10} {'Cumulative':<10}")
        print("-" * 87)

        steps = [
            ("gpt-4o-mini", 150, 40, "classify intent"),
            ("gpt-4o-mini", 200, 60, "search knowledge base"),
            ("gpt-4o", 500, 200, "analyze results"),
            ("gpt-4o-mini", 300, 80, "generate response"),
        ]

        for model, inp, out, action in steps:
            if not self.cost_tracker.within_budget():
                print(f"\n  ⚠ Budget exhausted! Stopping.")
                break

            step = self.cost_tracker.track_step(model, inp, out, action)
            print(f"{step['step']:<6} {model:<16} {action:<35} "
                  f"{inp+out:<10} ${step['cost']:<8.5f} "
                  f"${step['cumulative']:<8.5f}")

            time.sleep(0.02)

        summary = self.cost_tracker.summary()

        print(f"\n{'='*60}")
        print("Cost Summary")
        print(f"{'='*60}")
        print(f"  Total cost:         ${summary['total_cost']:.4f}")
        print(f"  Budget:             ${summary['budget']:.2f}")
        print(f"  Remaining:          ${summary['budget_remaining']:.4f}")
        print(f"  Total tokens:       {summary['total_input_tokens'] + summary['total_output_tokens']}")
        print(f"  Models used:        {', '.join(summary['models_used'])}")
        print(f"  Steps:              {summary['total_steps']}")
        print(f"  Avg cost/step:      ${summary['total_cost']/max(summary['total_steps'],1):.5f}")

        return summary

agent = AgentWithCostTracking()
agent.run("Research competitor pricing and write report")

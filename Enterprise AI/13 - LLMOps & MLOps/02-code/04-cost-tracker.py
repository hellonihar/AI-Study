"""
LLM cost tracking and optimization: per-request costing, aggregation, anomaly detection.

Run: python 04-cost-tracker.py

Requirements: numpy
"""

import numpy as np
from collections import defaultdict

print("=== LLM Cost Tracker ===\n")

MODEL_PRICING = {
    "gpt-4o": {"input_per_1k": 0.01, "output_per_1k": 0.03},
    "gpt-4o-mini": {"input_per_1k": 0.00015, "output_per_1k": 0.0006},
    "gpt-3.5-turbo": {"input_per_1k": 0.0005, "output_per_1k": 0.0015},
    "claude-3-opus": {"input_per_1k": 0.015, "output_per_1k": 0.075},
    "claude-3-sonnet": {"input_per_1k": 0.003, "output_per_1k": 0.015},
}

class RequestCostCalculator:
    @staticmethod
    def calculate(prompt_tokens, completion_tokens, model="gpt-4o-mini"):
        pricing = MODEL_PRICING.get(model)
        if not pricing:
            return {"error": f"Unknown model: {model}"}
        input_cost = (prompt_tokens / 1000) * pricing["input_per_1k"]
        output_cost = (completion_tokens / 1000) * pricing["output_per_1k"]
        return {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(input_cost + output_cost, 6),
        }

class CostAggregator:
    def __init__(self):
        self.records = []

    def add_request(self, feature, user_tier, model, prompt_tokens, completion_tokens):
        cost = RequestCostCalculator.calculate(prompt_tokens, completion_tokens, model)
        cost["feature"] = feature
        cost["user_tier"] = user_tier
        self.records.append(cost)

    def aggregate(self, dimension="feature"):
        groups = defaultdict(lambda: {"requests": 0, "total_cost": 0, "total_tokens": 0})
        for r in self.records:
            key = r[dimension]
            groups[key]["requests"] += 1
            groups[key]["total_cost"] += r["total_cost"]
            groups[key]["total_tokens"] += r["total_tokens"]
        return dict(groups)

    def cost_breakdown(self):
        return {
            "total_requests": len(self.records),
            "total_cost": round(sum(r["total_cost"] for r in self.records), 4),
            "total_tokens": sum(r["total_tokens"] for r in self.records),
            "avg_cost_per_request": round(np.mean([r["total_cost"] for r in self.records]), 6),
        }

class CostAnomalyDetector:
    def __init__(self):
        self.daily_costs = []

    def add_daily_cost(self, cost):
        self.daily_costs.append(cost)

    def detect_anomalies(self):
        if len(self.daily_costs) < 7:
            return []
        recent = self.daily_costs[-7:]
        mean = np.mean(recent[:-1])
        std = np.std(recent[:-1]) + 1e-8
        current = recent[-1]
        z_score = (current - mean) / std
        anomalies = []
        if z_score > 2:
            anomalies.append({"day": len(self.daily_costs), "cost": round(current, 2),
                              "z_score": round(z_score, 2), "severity": "WARNING"})
        if z_score > 3:
            anomalies[-1]["severity"] = "CRITICAL"
        return anomalies

calculator = RequestCostCalculator()

print("=== Per-Request Cost Examples ===")
examples = [
    (500, 200, "gpt-4o-mini"),
    (1500, 500, "gpt-4o"),
    (200, 50, "gpt-3.5-turbo"),
    (3000, 800, "claude-3-opus"),
    (800, 300, "claude-3-sonnet"),
]
print(f"{'Model':<20} {'Prompt':>8} {'Output':>8} {'Total Tokens':>14} {'Cost':>12}")
print("-" * 65)
for pt, ot, model in examples:
    c = calculator.calculate(pt, ot, model)
    print(f"{c['model']:<20} {c['prompt_tokens']:>8} {c['completion_tokens']:>8} "
          f"{c['total_tokens']:>8} ${c['total_cost']:<10.6f}")
print()

print("=== Cost Aggregation ===")
aggregator = CostAggregator()
np.random.seed(42)
for _ in range(500):
    feature = np.random.choice(["chat", "search", "summarize", "code_gen"])
    tier = np.random.choice(["free", "pro", "enterprise"], p=[0.5, 0.3, 0.2])
    model = np.random.choice(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], p=[0.7, 0.15, 0.15])
    pt = int(np.random.exponential(800) + 100)
    ot = int(np.random.exponential(200) + 50)
    aggregator.add_request(feature, tier, model, pt, ot)

breakdown = aggregator.cost_breakdown()
print(f"  Total Requests: {breakdown['total_requests']}")
print(f"  Total Cost:     ${breakdown['total_cost']:.4f}")
print(f"  Total Tokens:   {breakdown['total_tokens']:,}")
print(f"  Avg Cost/Req:   ${breakdown['avg_cost_per_request']:.6f}")
print()

print("  Cost by Feature:")
for feature, data in sorted(aggregator.aggregate("feature").items()):
    print(f"    {feature:<15} ${data['total_cost']:.4f} ({data['requests']} req, {data['total_tokens']:,} tok)")

print(f"\n  Cost by Model:")
for model, data in sorted(aggregator.aggregate("model").items()):
    print(f"    {model:<20} ${data['total_cost']:.4f} ({data['requests']} req)")

print(f"\n  Cost by User Tier:")
for tier, data in sorted(aggregator.aggregate("user_tier").items()):
    print(f"    {tier:<15} ${data['total_cost']:.4f} ({data['requests']} req)")
print()

print("=== Cost Anomaly Detection ===")
detector = CostAnomalyDetector()
np.random.seed(123)
base_daily = np.random.normal(75, 8, 14)
for d in base_daily:
    detector.add_daily_cost(max(0, d))
detector.add_daily_cost(250)
anomalies = detector.detect_anomalies()
if anomalies:
    for a in anomalies:
        print(f"  [{a['severity']}] Day {a['day']}: ${a['cost']:.2f} (z-score: {a['z_score']:.2f})")
else:
    print("  No anomalies detected")

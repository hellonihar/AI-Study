"""
Cost optimizer: analyze and recommend cost optimization strategies.

Run: python 02-cost-optimizer.py
"""

print("=== Cost Optimizer ===\n")

OPTIMIZATIONS = [
    {"strategy": "Batch requests", "savings": "20-40%", "effort": "Low", "risk": "Low"},
    {"strategy": "Cache common responses", "savings": "30-60%", "effort": "Medium", "risk": "Low"},
    {"strategy": "Model quantization (FP16 -> INT8)", "savings": "40-50%", "effort": "Medium", "risk": "Medium"},
    {"strategy": "Prompt compression", "savings": "20-30%", "effort": "Medium", "risk": "Low"},
    {"strategy": "Smaller model for simple tasks", "savings": "50-80%", "effort": "High", "risk": "Medium"},
    {"strategy": "Spot/preemptible instances", "savings": "60-70%", "effort": "Low", "risk": "High"},
    {"strategy": "Multi-model serving", "savings": "30-50%", "effort": "High", "risk": "Medium"},
    {"strategy": "Rate limiting (tiered plans)", "savings": "10-30%", "effort": "Low", "risk": "Low"},
    {"strategy": "Caching with semantic dedup", "savings": "15-25%", "effort": "High", "risk": "Medium"},
    {"strategy": "Streaming responses", "savings": "TTFB improvement", "effort": "Medium", "risk": "Low"},
]

class CostScenario:
    def __init__(self, base_monthly, optimizations):
        self.base = base_monthly
        self.optimizations = optimizations

    def project(self, months=12):
        costs = [self.base]
        for m in range(1, months):
            savings = 0
            for opt_name in self.optimizations:
                for o in OPTIMIZATIONS:
                    if o["strategy"] == opt_name:
                        low, high = o["savings"].split("-")
                        low_val = float(low.replace("%", "").replace("+", ""))
                        high_val = float(high.replace("%", "").replace("+", ""))
                        savings += (low_val + high_val) / 200
            costs.append(self.base * (1 - min(savings, 0.80)))
        return costs

print(f"{'Strategy':<40} {'Savings':>12} {'Effort':>8} {'Risk':>8}")
print("-" * 70)
for o in OPTIMIZATIONS:
    print(f"  {o['strategy']:<38} {o['savings']:>10} {o['effort']:>8} {o['risk']:>8}")
print()

print("=== Baseline ===")
monthly = 50000
print(f"  Annual baseline: ${monthly * 12:,.0f}")

scenario_aggressive = CostScenario(monthly, ["Batch requests", "Cache common responses", "Model quantization (FP16 -> INT8)", "Spot/preemptible instances"])
scenario_moderate = CostScenario(monthly, ["Batch requests", "Cache common responses"])
scenario_conservative = CostScenario(monthly, ["Batch requests"])

print(f"\n{'Scenario':<18} {'Year 1 Total':>16}")
print("-" * 35)
for name, sc in [("Conservative", scenario_conservative), ("Moderate", scenario_moderate), ("Aggressive", scenario_aggressive)]:
    projection = sc.project(12)
    print(f"  {name:<16} ${sum(projection):>10,.0f}")

"""
Build vs buy calculator: compare total cost across deployment models.

Run: python 01-build-vs-buy-calculator.py

Requirements: numpy
"""

import numpy as np

print("=== Build vs Buy Calculator ===\n")

class TotalCostModel:
    def api_cost(self, model, requests_month, prompt_tokens, completion_tokens):
        pricing = {
            "gpt-4o-mini": (0.00015, 0.0006),
            "gpt-4o": (0.01, 0.03),
            "claude-3-sonnet": (0.003, 0.015),
            "claude-3-haiku": (0.00025, 0.00125),
        }
        inp, out = pricing.get(model, (0.001, 0.002))
        input_cost = (prompt_tokens / 1000) * inp * requests_month
        output_cost = (completion_tokens / 1000) * out * requests_month
        return input_cost + output_cost

    def build_cost(self, dev_cost, dev_months, infra_monthly, ops_monthly, months):
        total_dev = dev_cost
        total_ops = (infra_monthly + ops_monthly) * months
        return total_dev + total_ops

    def break_even_month(self, api_monthly, dev_cost, infra_monthly, ops_monthly):
        if api_monthly <= (infra_monthly + ops_monthly):
            return 0
        monthly_savings = api_monthly - (infra_monthly + ops_monthly)
        return int(np.ceil(dev_cost / monthly_savings))

calc = TotalCostModel()

SCENARIOS = [
    ("Customer Support", 500000, 600, 200),
    ("Enterprise Search", 2000000, 400, 150),
    ("Code Assistant", 300000, 800, 400),
    ("Document Processing", 100000, 3000, 600),
]

print(f"{'Scenario':<20} {'GPT-4o-mini':>14} {'GPT-4o':>10} {'Build Cost':>12} {'Break-Even':>12}")
print("-" * 70)
for name, req, pt, ct in SCENARIOS:
    api_cheap = calc.api_cost("gpt-4o-mini", req, pt, ct)
    api_expensive = calc.api_cost("gpt-4o", req, pt, ct)
    build_dev = 80000
    infra_monthly = {500000: 3000, 2000000: 8000, 300000: 2000, 100000: 1000}[req]
    ops_monthly = 2000
    build_total = calc.build_cost(build_dev, 6, infra_monthly, ops_monthly, 12)
    be = calc.break_even_month(api_cheap, build_dev, infra_monthly, ops_monthly)
    be_str = f"{be} mo" if be > 0 else "Never"
    print(f"{name:<20} ${api_cheap:<10,.2f} ${api_expensive:<6,.2f} ${build_total:<8,.0f} {be_str:<12}")
print()

print("=== Break-Even Analysis by Request Volume ===")
volumes = [100000, 500000, 1000000, 5000000, 10000000, 50000000]
dev_cost = 80000
for vol in volumes:
    api_mo = calc.api_cost("gpt-4o-mini", vol, 600, 200)
    infra = max(1000, vol * 0.008)
    be = calc.break_even_month(api_mo, dev_cost, infra, 2000)
    be_str = f"{be} mo" if be > 0 else "API cheaper"
    yr1_build = calc.build_cost(dev_cost, 6, infra, 2000, 12)
    yr1_api = api_mo * 12
    print(f"  {vol:>8,}/mo: API=${yr1_api:<8,.0f}/yr Build=${yr1_build:<8,.0f}/yr Break-even={be_str}")

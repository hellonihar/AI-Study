"""
Cost modeling tool: compare self-hosted vs API-based inference costs.

Run: python 05-cost-modeling-tool.py

Requirements: numpy
"""

import numpy as np

print("=== Cost Modeling Tool ===\n")

class CostModel:
    def __init__(self):
        self.api_pricing = {
            "gpt-4o": {"input_per_1k": 0.01, "output_per_1k": 0.03},
            "gpt-4o-mini": {"input_per_1k": 0.00015, "output_per_1k": 0.0006},
            "claude-3-sonnet": {"input_per_1k": 0.003, "output_per_1k": 0.015},
            "claude-3-haiku": {"input_per_1k": 0.00025, "output_per_1k": 0.00125},
        }

    def api_monthly(self, model, requests_per_month, prompt_tokens, completion_tokens):
        pricing = self.api_pricing.get(model)
        if not pricing:
            return None
        input_cost = (prompt_tokens / 1000) * pricing["input_per_1k"] * requests_per_month
        output_cost = (completion_tokens / 1000) * pricing["output_per_1k"] * requests_per_month
        return {
            "model": model,
            "type": "API",
            "requests": requests_per_month,
            "monthly_cost": round(input_cost + output_cost, 2),
            "cost_per_request": round((input_cost + output_cost) / requests_per_month, 6),
        }

    def self_hosted_monthly(self, model_name, gpu_type, gpu_count, requests_per_month, prompt_tokens, completion_tokens):
        gpu_costs = {
            "A100 80GB": {"hourly": 3.0, "monthly": 2190},
            "H100 80GB": {"hourly": 5.0, "monthly": 3650},
            "A10G": {"hourly": 1.5, "monthly": 1095},
            "L4": {"hourly": 0.8, "monthly": 584},
        }
        gpu_spec = gpu_costs.get(gpu_type)
        if not gpu_spec:
            return None
        monthly_gpu = gpu_spec["monthly"] * gpu_count
        storage = model_name.replace(" ", "_").lower()
        storage_cost = 0.10 * 500
        networking = 100
        ops_staff = 2000
        total = monthly_gpu + storage_cost + networking + ops_staff
        total_tokens = requests_per_month * (prompt_tokens + completion_tokens)
        return {
            "model": model_name,
            "type": "Self-Hosted",
            "gpu": gpu_type,
            "gpu_count": gpu_count,
            "monthly_gpu_cost": round(monthly_gpu, 2),
            "total_monthly": round(total, 2),
            "cost_per_request": round(total / requests_per_month, 6),
            "cost_per_1k_tokens": round(total / (total_tokens / 1000), 6),
        }

model = CostModel()

SCENARIOS = [
    {"requests": 500000, "prompt_tokens": 800, "completion_tokens": 300},
    {"requests": 2000000, "prompt_tokens": 500, "completion_tokens": 200},
    {"requests": 10000000, "prompt_tokens": 300, "completion_tokens": 150},
    {"requests": 50000000, "prompt_tokens": 600, "completion_tokens": 250},
]

print(f"{'Scenario':<15} {'Approach':<20} {'Requests':>10} {'Monthly':>12} {'Cost/Req':>12} {'Cost/1K Tokens':>16}")
print("-" * 90)
for sc in SCENARIOS:
    label = f"{sc['requests']/1e6:.1f}M/mo"
    api = model.api_monthly("gpt-4o-mini", sc["requests"], sc["prompt_tokens"], sc["completion_tokens"])
    sh = model.self_hosted_monthly("Llama 3 8B", "L4", 4, sc["requests"], sc["prompt_tokens"], sc["completion_tokens"])
    if api:
        print(f"{label:<15} {'GPT-4o-mini (API)':<20} {api['requests']:>10,} ${api['monthly_cost']:<10,.2f} ${api['cost_per_request']:<.6f}  ${api['monthly_cost']/(sc['requests']*(sc['prompt_tokens']+sc['completion_tokens'])/1000):<.6f}")
    if sh:
        gpu_label = f"Llama-3-8B ({sh['gpu']})"
        print(f"{label:<15} {gpu_label:<20} {sh['total_monthly']:>10,} ${sh['total_monthly']:<10,.2f} ${sh['cost_per_request']:<.6f}  ${sh['cost_per_1k_tokens']:<.6f}")
    print()

print("=== API Provider Comparison (500K req/mo, 800+300 tokens) ===")
print(f"{'Provider':<20} {'Monthly Cost':>14} {'Cost/Request':>14}")
print("-" * 50)
for provider in model.api_pricing:
    result = model.api_monthly(provider, 500000, 800, 300)
    if result:
        print(f"{provider:<20} ${result['monthly_cost']:<10,.2f}  ${result['cost_per_request']:<.10f}")
print()

print("=== GPU Configuration Comparison ===")
for gpu in ["L4", "A10G", "A100 80GB"]:
    for count in [2, 4, 8]:
        result = model.self_hosted_monthly("Llama 3 8B", gpu, count, 500000, 800, 300)
        if result:
            print(f"  {gpu:<15} x{count}: ${result['total_monthly']:<8,.0f}/mo "
                  f"(${result['cost_per_1k_tokens']:.6f}/1K tokens)")

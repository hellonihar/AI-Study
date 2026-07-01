"""
Capacity planner: estimate GPU requirements for serving workloads.

Run: python 01-capacity-planner.py
"""

import math

print("=== Capacity Planner ===\n")

class CapacityPlanner:
    def __init__(self):
        self.models = []

    def add_model(self, name, params_b, tokens_per_request, requests_per_second, gpu_tput):
        total_tokens_ps = tokens_per_request * requests_per_second
        gpu_required = total_tokens_ps / gpu_tput
        self.models.append({
            "name": name,
            "params_b": params_b,
            "tokens_per_request": tokens_per_request,
            "rps": requests_per_second,
            "gpu_tput": gpu_tput,
            "total_tokens_ps": total_tokens_ps,
            "gpu_required": gpu_required,
            "gpu_ceiling": math.ceil(gpu_required),
        })

    def report(self):
        print(f"{'Model':<22} {'Params':>6} {'Tokens/Req':>10} {'RPS':>6} {'Total Tok/s':>12} {'GPU Req':>8} {'GPU Need':>9}")
        print("-" * 80)
        total_gpu = 0
        for m in self.models:
            print(f"  {m['name']:<20} {m['params_b']:>4}B {m['tokens_per_request']:>8} {m['rps']:>5} "
                  f"{m['total_tokens_ps']:>9,.0f} {m['gpu_tput']:>6} {m['gpu_ceiling']:>5}")
            total_gpu += m['gpu_ceiling']
        print()
        print(f"  TOTAL GPUs required: {total_gpu}")
        print(f"  With HA (2x):        {total_gpu * 2}")
        print(f"  With 20% buffer:     {math.ceil(total_gpu * 1.2)}")

planner = CapacityPlanner()
planner.add_model("chatbot-7b", 7, 500, 50, 400)
planner.add_model("rag-embedding", 0.4, 256, 200, 1500)
planner.add_model("code-assist-7b", 7, 800, 20, 400)
planner.add_model("summarizer-3b", 3, 1500, 10, 800)
planner.report()
print()

print("=== Cost Projection (12 months) ===")
gpu_type = "A100-40"
cost_per_hour = {"A10": 1.50, "A100-40": 3.00, "A100-80": 5.00}.get(gpu_type, 3.00)
gpu_count = total_gpu = sum(m['gpu_ceiling'] for m in planner.models)
monthly_gpu_cost = gpu_count * cost_per_hour * 730
annual_gpu_cost = monthly_gpu_cost * 12
annual_infra = annual_gpu_cost * 1.4
print(f"  GPU: {gpu_count} x {gpu_type} @ ${cost_per_hour:.2f}/hr")
print(f"  Monthly GPU: ${monthly_gpu_cost:,.0f}")
print(f"  Annual GPU:  ${annual_gpu_cost:,.0f}")
print(f"  Annual Infra (GPU + storage/networking): ${annual_infra:,.0f}")

"""
GPU capacity planner: model throughput, memory, and cost estimation.

Run: python 01-gpu-capacity-planner.py

Requirements: numpy
"""

import numpy as np

print("=== GPU Capacity Planner ===\n")

MODEL_SPECS = {
    "Llama 3 8B": {"params": 8, "memory_fp16": 16, "throughput_tps": 3000},
    "Llama 3 70B": {"params": 70, "memory_fp16": 140, "throughput_tps": 400},
    "Mixtral 8x7B": {"params": 47, "memory_fp16": 94, "throughput_tps": 800},
    "GPT-4o-mini": {"params": 8, "memory_fp16": 0, "throughput_tps": 5000, "api": True},
    "GPT-4o": {"params": 200, "memory_fp16": 0, "throughput_tps": 1000, "api": True},
}

GPU_SPECS = {
    "A100 80GB": {"memory": 80, "bandwidth_gbps": 2000, "cost_per_hour": 3.0},
    "H100 80GB": {"memory": 80, "bandwidth_gbps": 3300, "cost_per_hour": 5.0},
    "A10G": {"memory": 24, "bandwidth_gbps": 600, "cost_per_hour": 1.5},
    "L4": {"memory": 24, "bandwidth_gbps": 300, "cost_per_hour": 0.8},
    "T4": {"memory": 16, "bandwidth_gbps": 320, "cost_per_hour": 0.6},
}

class CapacityPlanner:
    def estimate_gpus(self, model_name, gpu_name, rps, avg_tokens, util_target=0.7):
        model = MODEL_SPECS.get(model_name)
        gpu = GPU_SPECS.get(gpu_name)
        if not model or not gpu:
            return None
        if model.get("api"):
            return {"type": "api", "note": "API-based, no GPU required", "cost_per_1k_tokens": 0.0006}
        tokens_per_sec = rps * avg_tokens
        gpu_throughput = model["throughput_tps"] * util_target
        gpus_needed = max(1, int(np.ceil(tokens_per_sec / gpu_throughput)))
        model_memory = model["memory_fp16"]
        kv_cache_per_gpu = (rps / max(gpus_needed, 1)) * avg_tokens * 2 * 2 * 32 / 1e9
        total_memory = model_memory / gpus_needed + kv_cache_per_gpu + model_memory * 0.2
        monthly_cost = gpus_needed * gpu["cost_per_hour"] * 730
        return {
            "type": "self_hosted",
            "gpus_needed": gpus_needed,
            "gpu_model": gpu_name,
            "tokens_per_sec": tokens_per_sec,
            "gpu_throughput_tps": gpu_throughput,
            "memory_per_gpu_gb": round(total_memory, 1),
            "kv_cache_gb": round(kv_cache_per_gpu, 2),
            "monthly_cost": round(monthly_cost, 0),
            "cost_per_1k_tokens": round(monthly_cost / (rps * avg_tokens * 3600 * 730 / 1000), 6),
        }

planner = CapacityPlanner()

print(f"{'Model':<20} {'GPU':<12} {'RPS':>5} {'Tokens':>7} {'GPUs':>5} {'Mem/GPU':>8} {'Monthly':>12} {'Cost/1K':>10}")
print("-" * 85)
scenarios = [
    ("Llama 3 8B", "A100 80GB", 100, 500),
    ("Llama 3 8B", "L4", 50, 500),
    ("Llama 3 70B", "A100 80GB", 50, 1000),
    ("Llama 3 70B", "H100 80GB", 100, 800),
    ("Mixtral 8x7B", "A100 80GB", 100, 600),
    ("Mixtral 8x7B", "H100 80GB", 200, 600),
    ("GPT-4o-mini", "N/A", 500, 400),
]
for model, gpu, rps, tokens in scenarios:
    result = planner.estimate_gpus(model, gpu, rps, tokens)
    if result and result["type"] == "self_hosted":
        print(f"{model:<20} {gpu:<12} {rps:>5} {tokens:>7} {result['gpus_needed']:>5} "
              f"{result['memory_per_gpu_gb']:>7.1f}GB ${result['monthly_cost']:>9,.0f} ${result['cost_per_1k_tokens']:<.6f}")
    elif result:
        print(f"{model:<20} {gpu:<12} {rps:>5} {tokens:>7} {'API':>5} {'N/A':>8} {'N/A':>12} {result['cost_per_1k_tokens']:<.6f}")
print()

print("=== GPU Comparison for Single Model ===")
print(f"Model: Llama 3 8B, 100 RPS, 500 avg tokens")
print(f"{'GPU':<12} {'GPUs':>5} {'Monthly Cost':>14} {'Cost/1K Tokens':>16}")
print("-" * 50)
for gpu_name in GPU_SPECS:
    result = planner.estimate_gpus("Llama 3 8B", gpu_name, 100, 500)
    if result and result["type"] == "self_hosted":
        print(f"{gpu_name:<12} {result['gpus_needed']:>5} ${result['monthly_cost']:>10,.0f} ${result['cost_per_1k_tokens']:<.6f}")

"""
Production LLMOps orchestrator: end-to-end pipeline with routing, evaluation,
drift detection, cost tracking, and incident response.

Run: python 10-production-llmops-orchestrator.py

Requirements: numpy
"""

import time
import json
import numpy as np
from collections import defaultdict

print("=== Production LLMOps Orchestrator ===\n")

class LLMOrchestrator:
    def __init__(self, name="default"):
        self.name = name
        self.requests = []
        self.errors = []
        self.latencies = []
        self.costs = []
        self.quality_scores = []
        self.guardrail_blocks = 0
        self.start_time = time.time()

    def process_request(self, user_id, query, model="gpt-4o-mini", tags=None):
        start = time.time()
        request_id = f"req-{len(self.requests):06d}"

        prompt_tokens = len(query.split()) * 1.3 + 100
        completion_tokens = np.random.poisson(150) + 30
        total_tokens = int(prompt_tokens + completion_tokens)

        pricing = {"gpt-4o-mini": 0.00015, "gpt-4o": 0.01, "claude-3-sonnet": 0.003}
        cost_per_token = pricing.get(model, 0.00015) / 1000
        cost = total_tokens * cost_per_token

        error = np.random.random() < 0.02
        quality = max(0, min(1, np.random.normal(0.87, 0.06)))

        if error:
            quality = max(0, quality - 0.3)

        block = np.random.random() < 0.01
        if block:
            self.guardrail_blocks += 1

        latency_ms = (time.time() - start) * 1000
        if not block and not error:
            inference_latency = np.random.exponential(300) + 50
            latency_ms += inference_latency

        record = {
            "request_id": request_id,
            "user_id": user_id,
            "model": model,
            "tokens": total_tokens,
            "cost": round(cost, 6),
            "latency_ms": round(latency_ms, 1),
            "error": error,
            "quality": round(quality, 3),
            "blocked": block,
            "tags": tags or {},
        }
        self.requests.append(record)
        self.latencies.append(latency_ms)
        self.costs.append(cost)
        self.quality_scores.append(quality)
        if error:
            self.errors.append(record)
        return record

    def get_stats(self):
        n = len(self.requests)
        if n == 0:
            return {}
        latencies = sorted(self.latencies)
        return {
            "total_requests": n,
            "error_rate": len(self.errors) / n,
            "guardrail_block_rate": self.guardrail_blocks / n,
            "avg_latency_ms": round(np.mean(self.latencies), 1),
            "p95_latency_ms": round(latencies[int(n * 0.95)], 1),
            "p99_latency_ms": round(latencies[int(n * 0.99)], 1),
            "avg_cost": round(np.mean(self.costs), 6),
            "total_cost": round(sum(self.costs), 4),
            "avg_quality": round(np.mean(self.quality_scores), 3),
            "uptime_hours": round((time.time() - self.start_time) / 3600, 2),
        }

    def health_check(self):
        stats = self.get_stats()
        checks = {
            "error_rate_ok": stats.get("error_rate", 0) < 0.03,
            "latency_ok": stats.get("p95_latency_ms", 0) < 3000,
            "quality_ok": stats.get("avg_quality", 1) > 0.75,
            "block_rate_ok": stats.get("guardrail_block_rate", 0) < 0.05,
        }
        healthy = all(checks.values())
        return healthy, checks

class ModelRouter:
    def __init__(self):
        self.models = {
            "gpt-4o-mini": {"cost_per_1k": 0.00015, "quality": 0.82, "latency_p50": 300},
            "gpt-4o": {"cost_per_1k": 0.01, "quality": 0.92, "latency_p50": 600},
            "claude-3-sonnet": {"cost_per_1k": 0.003, "quality": 0.90, "latency_p50": 450},
        }

    def route(self, task_type, complexity="simple"):
        if complexity == "simple" and task_type in ("qa", "summarize"):
            return "gpt-4o-mini"
        elif complexity == "complex" and task_type in ("code", "reasoning"):
            return "gpt-4o"
        elif complexity == "medium":
            return "claude-3-sonnet"
        return "gpt-4o-mini"

print("=== Orchestrator Simulation ===")
orch = LLMOrchestrator("production-v2")
router = ModelRouter()

np.random.seed(42)
task_types = ["qa", "code", "summarize", "chat", "reasoning"]
complexities = ["simple", "medium", "complex"]

for i in range(500):
    uid = f"user_{np.random.randint(1, 101)}"
    task = np.random.choice(task_types, p=[0.3, 0.15, 0.2, 0.25, 0.1])
    complexity = np.random.choice(complexities, p=[0.5, 0.35, 0.15])
    model = router.route(task, complexity)
    orch.process_request(uid, f"Query about {task}", model, tags={"task": task, "complexity": complexity})

stats = orch.get_stats()
print(f"  Total Requests:     {stats['total_requests']}")
print(f"  Error Rate:         {stats['error_rate']:.2%}")
print(f"  Guardrail Block:    {stats['guardrail_block_rate']:.2%}")
print(f"  Avg Latency:        {stats['avg_latency_ms']:.0f}ms")
print(f"  p95 Latency:        {stats['p95_latency_ms']:.0f}ms")
print(f"  Avg Quality:        {stats['avg_quality']:.3f}")
print(f"  Avg Cost/Request:   ${stats['avg_cost']:.6f}")
print(f"  Total Cost:         ${stats['total_cost']:.4f}")
print(f"  Uptime:             {stats['uptime_hours']:.2f}h")
print()

print("=== Health Check ===")
healthy, checks = orch.health_check()
for check, passed in checks.items():
    print(f"  {check:<20}: {'PASS' if passed else 'FAIL'}")
print(f"  Overall: {'HEALTHY' if healthy else 'DEGRADED'}")
print()

print("=== Model Routing Effectiveness ===")
model_counts = defaultdict(int)
model_costs = defaultdict(float)
for r in orch.requests:
    model_counts[r["model"]] += 1
    model_costs[r["model"]] += r["cost"]

print(f"  {'Model':<20} {'Requests':>10} {'Cost':>12} {'Avg Cost/Req':>14}")
print("  " + "-" * 60)
for model, count in sorted(model_counts.items()):
    avg_c = model_costs[model] / count
    print(f"  {model:<20} {count:>10} ${model_costs[model]:<10.4f} ${avg_c:.6f}")

print()

print("=== SLA Compliance ===")
lat_99 = stats["p99_latency_ms"]
lat_95 = stats["p95_latency_ms"]
print(f"  p99 Latency SLA (3000ms): {'COMPLIANT' if lat_99 < 3000 else 'BREACHED'} ({lat_99:.0f}ms)")
print(f"  p95 Latency SLA (1500ms): {'COMPLIANT' if lat_95 < 1500 else 'BREACHED'} ({lat_95:.0f}ms)")
print(f"  Error Rate SLA (3%):      {'COMPLIANT' if stats['error_rate'] < 0.03 else 'BREACHED'} ({stats['error_rate']:.2%})")
print(f"  Quality SLA (0.75):       {'COMPLIANT' if stats['avg_quality'] > 0.75 else 'BREACHED'} ({stats['avg_quality']:.3f})")

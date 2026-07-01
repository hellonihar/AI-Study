"""
Inference latency model: predict end-to-end latency under different conditions.

Run: python 02-inference-latency-model.py

Requirements: numpy
"""

import numpy as np

print("=== Inference Latency Model ===\n")

class LatencyModel:
    def __init__(self):
        self.components = {
            "network_trip": {"base_ms": 5, "per_token_ms": 0},
            "input_guardrail": {"base_ms": 2, "per_token_ms": 0.002},
            "prompt_processing": {"base_ms": 10, "per_token_ms": 0.05},
            "model_inference": {"base_ms": 15, "per_token_ms": 0.8},
            "output_guardrail": {"base_ms": 2, "per_token_ms": 0.002},
            "network_return": {"base_ms": 5, "per_token_ms": 0},
        }

    def predict(self, prompt_tokens, completion_tokens, batch_size=1, model_speed=1.0):
        latency = {}
        total = 0
        for comp, config in self.components.items():
            per_token = config["per_token_ms"]
            token_contribution = per_token * (prompt_tokens + completion_tokens)
            base = config["base_ms"]
            if comp == "model_inference":
                base = base + prompt_tokens * 0.05 / model_speed
                token_contribution = completion_tokens * 0.8 / model_speed
                if batch_size > 1:
                    base = base + (batch_size - 1) * 5
            elif comp == "prompt_processing":
                base = base + prompt_tokens * 0.05 / model_speed
                token_contribution = 0
            else:
                token_contribution = per_token * (prompt_tokens + completion_tokens)
            component_latency = base + token_contribution
            latency[comp] = round(component_latency, 2)
            total += component_latency
        latency["total_ms"] = round(total, 2)
        return latency

    def ttft(self, prompt_tokens, model_speed=1.0):
        return round(5 + prompt_tokens * 0.05 / model_speed + 15, 2)

model = LatencyModel()

TEST_CASES = [
    (100, 50, 1, "Simple Q&A"),
    (500, 200, 1, "Document analysis"),
    (2000, 500, 1, "Long context analysis"),
    (100, 50, 8, "Batched simple queries"),
    (1000, 400, 4, "Batched medium queries"),
    (4000, 1000, 1, "Very long context"),
]

print(f"{'Scenario':<30} {'PT':>5} {'CT':>5} {'Batch':>6} {'p50':>8} {'p95':>8} {'TTFT':>8}")
print("-" * 75)
for pt, ct, batch, name in TEST_CASES:
    result = model.predict(pt, ct, batch)
    ttft_val = model.ttft(pt)
    p50 = result["total_ms"]
    p95 = p50 * 1.5
    print(f"{name:<30} {pt:>5} {ct:>5} {batch:>6} {p50:>8.0f}ms {p95:>8.0f}ms {ttft_val:>8.0f}ms")
print()

print("=== Impact of Model Speed ===")
speeds = [0.5, 0.75, 1.0, 1.5, 2.0]
for speed in speeds:
    result = model.predict(500, 200, 1, speed)
    ttft_val = model.ttft(500, speed)
    print(f"  Speed {speed:.1f}x: p50={result['total_ms']:.0f}ms, TTFT={ttft_val:.0f}ms")
print()

print("=== Component Breakdown (500 prompt, 200 completion) ===")
result = model.predict(500, 200)
for comp, lat in result.items():
    if comp != "total_ms":
        pct = lat / result["total_ms"] * 100
        print(f"  {comp:<25} {lat:>8.1f}ms ({pct:>5.1f}%)")
print(f"  {'Total':<25} {result['total_ms']:>8.1f}ms")

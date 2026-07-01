"""
LLM monitoring dashboard: metrics collection, aggregation, and alerting.

Run: python 01-monitoring-dashboard.py

Requirements: numpy
"""

import time
import json
import math
import numpy as np

print("=== LLM Monitoring Dashboard ===\n")

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "latency": [],
            "token_count": [],
            "cost": [],
            "error": [],
            "quality_score": [],
        }

    def record_request(self, latency_ms, tokens, cost, error=False, quality=None):
        self.metrics["latency"].append(latency_ms)
        self.metrics["token_count"].append(tokens)
        self.metrics["cost"].append(cost)
        self.metrics["error"].append(1 if error else 0)
        if quality is not None:
            self.metrics["quality_score"].append(quality)

class MetricsAggregator:
    @staticmethod
    def compute_percentiles(data, percentiles=[50, 95, 99]):
        if not data:
            return {f"p{p}": 0 for p in percentiles}
        sorted_data = sorted(data)
        n = len(sorted_data)
        result = {}
        for p in percentiles:
            idx = int(math.ceil(p / 100.0 * n)) - 1
            idx = max(0, min(idx, n - 1))
            result[f"p{p}"] = sorted_data[idx]
        return result

    @staticmethod
    def compute_stats(data):
        if not data:
            return {"mean": 0, "min": 0, "max": 0, "std": 0, "count": 0}
        arr = np.array(data)
        return {
            "mean": round(float(np.mean(arr)), 2),
            "min": round(float(np.min(arr)), 2),
            "max": round(float(np.max(arr)), 2),
            "std": round(float(np.std(arr)), 2),
            "count": len(data),
        }

class AlertEngine:
    def __init__(self):
        self.thresholds = {
            "p95_latency_ms": 2000,
            "error_rate": 0.02,
            "cost_per_request": 0.01,
            "quality_score_min": 0.7,
        }
        self.alerts = []

    def evaluate(self, stats):
        alerts = []
        if stats.get("p95_latency", 0) > self.thresholds["p95_latency_ms"]:
            alerts.append(("CRITICAL", f"p95 latency {stats['p95_latency']}ms exceeds {self.thresholds['p95_latency_ms']}ms"))
        if stats.get("error_rate", 0) > self.thresholds["error_rate"]:
            alerts.append(("CRITICAL", f"Error rate {stats['error_rate']:.1%} exceeds {self.thresholds['error_rate']:.0%}"))
        if stats.get("avg_cost", 0) > self.thresholds["cost_per_request"]:
            alerts.append(("WARNING", f"Avg cost ${stats['avg_cost']:.4f} exceeds ${self.thresholds['cost_per_request']:.4f}"))
        if stats.get("avg_quality", 1) < self.thresholds["quality_score_min"]:
            alerts.append(("WARNING", f"Quality score {stats['avg_quality']:.2f} below {self.thresholds['quality_score_min']}"))
        return alerts

dashboard_start = time.time()
collector = MetricsCollector()
aggregator = MetricsAggregator()
alerter = AlertEngine()

np.random.seed(42)
for i in range(1000):
    latency = np.random.exponential(scale=300)
    latency = min(latency, 5000)
    tokens = int(np.random.normal(500, 150))
    tokens = max(50, tokens)
    cost = tokens * 0.000002
    error = np.random.random() < 0.015
    quality = max(0, min(1, np.random.normal(0.85, 0.08)))
    collector.record_request(latency, tokens, cost, error, quality)

raw = collector.metrics
latency_stats = aggregator.compute_stats(raw["latency"])
latency_percentiles = aggregator.compute_percentiles(raw["latency"])
token_stats = aggregator.compute_stats(raw["token_count"])
error_rate = sum(raw["error"]) / len(raw["error"]) if raw["error"] else 0
avg_cost = np.mean(raw["cost"]) if raw["cost"] else 0
quality_data = [q for q in raw["quality_score"] if q is not None]
avg_quality = np.mean(quality_data) if quality_data else 0

dashboard_stats = {
    "requests": len(raw["latency"]),
    "error_rate": error_rate,
    "avg_cost": avg_cost,
    "avg_quality": avg_quality,
    "p95_latency": latency_percentiles.get("p95", 0),
    "total_cost": sum(raw["cost"]),
}

print("=== Dashboard Metrics ===")
print(f"  Total Requests:     {dashboard_stats['requests']}")
print(f"  Error Rate:         {dashboard_stats['error_rate']:.2%}")
print(f"  Avg Cost/Request:   ${dashboard_stats['avg_cost']:.6f}")
print(f"  Total Cost:         ${dashboard_stats['total_cost']:.4f}")
print(f"  Avg Quality Score:  {dashboard_stats['avg_quality']:.3f}")
print()

print("=== Latency Distribution ===")
print(f"  Mean: {latency_stats['mean']:.0f}ms")
print(f"  Min:  {latency_stats['min']:.0f}ms")
print(f"  Max:  {latency_stats['max']:.0f}ms")
print(f"  Std:  {latency_stats['std']:.0f}ms")
print(f"  p50:  {latency_percentiles.get('p50', 0):.0f}ms")
print(f"  p95:  {latency_percentiles.get('p95', 0):.0f}ms")
print(f"  p99:  {latency_percentiles.get('p99', 0):.0f}ms")
print()

print("=== Token Usage ===")
print(f"  Mean:   {token_stats['mean']:.0f}")
print(f"  Total:  {sum(raw['token_count']):,}")
print()

print("=== Active Alerts ===")
alerts = alerter.evaluate(dashboard_stats)
if alerts:
    for severity, msg in alerts:
        print(f"  [{severity}] {msg}")
else:
    print("  No active alerts - all metrics within thresholds")
print()

print("=== Alert Thresholds ===")
for k, v in alerter.thresholds.items():
    print(f"  {k}: {v}")

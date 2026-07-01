"""
A/B testing and canary deployment framework for LLM variants.

Run: python 06-ab-testing-framework.py

Requirements: numpy
"""

import numpy as np
import hashlib
from collections import defaultdict

print("=== A/B Testing & Canary Framework ===\n")

class TrafficRouter:
    def __init__(self):
        self.variants = {}
        self.total_weight = 0

    def add_variant(self, name, weight, config):
        self.variants[name] = {"weight": weight, "config": config}
        self.total_weight = sum(v["weight"] for v in self.variants.values())

    def route(self, user_id):
        hash_val = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
        normalized = (hash_val % 10000) / 10000.0
        cumulative = 0
        for name, v in self.variants.items():
            cumulative += v["weight"] / self.total_weight
            if normalized <= cumulative:
                return name, v["config"]
        return list(self.variants.keys())[-1], self.variants[list(self.variants.keys())[-1]]["config"]

class ExperimentTracker:
    def __init__(self):
        self.results = defaultdict(lambda: defaultdict(list))

    def record(self, variant, metric, value):
        self.results[variant][metric].append(value)

    def get_stats(self, variant):
        stats = {}
        for metric, values in self.results[variant].items():
            arr = np.array(values)
            stats[metric] = {
                "mean": round(float(np.mean(arr)), 4),
                "std": round(float(np.std(arr)), 4),
                "count": len(values),
            }
        return stats

    def compare(self, variant_a, variant_b, metric):
        data_a = self.results[variant_a].get(metric, [])
        data_b = self.results[variant_b].get(metric, [])
        if len(data_a) < 2 or len(data_b) < 2:
            return {"significant": False, "reason": "insufficient_data"}
        mean_a = np.mean(data_a)
        mean_b = np.mean(data_b)
        std_a = np.std(data_a, ddof=1)
        std_b = np.std(data_b, ddof=1)
        n_a, n_b = len(data_a), len(data_b)
        se = np.sqrt(std_a**2 / n_a + std_b**2 / n_b)
        if se == 0:
            return {"significant": False, "reason": "no_variance"}
        t_stat = (mean_b - mean_a) / se
        df = min(n_a, n_b) - 1
        p_value = 2 * (1 - self._t_cdf(abs(t_stat), df))
        lift = (mean_b - mean_a) / mean_a if mean_a != 0 else 0
        return {
            "metric": metric,
            "control_mean": round(float(mean_a), 4),
            "variant_mean": round(float(mean_b), 4),
            "lift": round(float(lift), 4),
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_value), 4),
            "significant": p_value < 0.05,
        }

    def _t_cdf(self, x, df):
        return 1 - 0.5 * np.exp(-0.5 * x**2) if df > 30 else 0.5 + 0.5 * np.math.erf(x / np.sqrt(2))

class CanaryController:
    def __init__(self, initial_pct=5):
        self.current_pct = initial_pct
        self.phases = [5, 25, 50, 100]
        self.phase_idx = 0
        self.metrics_history = []

    def should_promote(self, metrics, baseline):
        checks = []
        checks.append(metrics.get("error_rate", 0) <= baseline.get("error_rate", 0) + 0.005)
        checks.append(metrics.get("p95_latency", 0) <= baseline.get("p95_latency", 0) * 1.2)
        checks.append(metrics.get("quality_score", 1) >= baseline.get("quality_score", 1) - 0.02)
        checks.append(metrics.get("cost_per_request", 0) <= baseline.get("cost_per_request", 0) * 1.1)
        passed = all(checks)
        if passed and self.phase_idx < len(self.phases) - 1:
            self.phase_idx += 1
            self.current_pct = self.phases[self.phase_idx]
        return passed, self.current_pct

router = TrafficRouter()
router.add_variant("control", 50, {"model": "gpt-4o-mini", "temperature": 0.3, "prompt": "standard"})
router.add_variant("variant_a", 25, {"model": "gpt-4o-mini", "temperature": 0.5, "prompt": "creative"})
router.add_variant("variant_b", 25, {"model": "gpt-4o", "temperature": 0.3, "prompt": "standard"})

print("=== Traffic Routing ===")
np.random.seed(42)
user_assignments = defaultdict(int)
for uid in range(1000):
    variant, config = router.route(f"user_{uid}")
    user_assignments[variant] += 1

for variant, count in sorted(user_assignments.items()):
    pct = count / 10
    print(f"  {variant:<15} {count:>4} users ({pct:.0f}%)")
print()

print("=== Experiment Results ===")
tracker = ExperimentTracker()
np.random.seed(123)
for uid in range(2000):
    variant, config = router.route(f"user_{uid}")
    quality = np.random.normal(0.85 if variant == "control" else 0.88, 0.06)
    latency = np.random.exponential(300 if variant == "control" else 350)
    cost = np.random.uniform(0.0008, 0.0012) if variant == "control" else np.random.uniform(0.0010, 0.0020)
    error = 1 if np.random.random() < 0.02 else 0
    tracker.record(variant, "quality", max(0, min(1, quality)))
    tracker.record(variant, "latency_ms", latency)
    tracker.record(variant, "cost", cost)
    tracker.record(variant, "error", error)

for variant in ["control", "variant_a", "variant_b"]:
    stats = tracker.get_stats(variant)
    print(f"  {variant}:")
    for metric, s in stats.items():
        print(f"    {metric:<15} mean={s['mean']:<10.4f} std={s['std']:<8.4f} n={s['count']}")
    print()

print("=== Statistical Comparison (Variant A vs Control) ===")
for metric in ["quality", "latency_ms", "cost"]:
    result = tracker.compare("control", "variant_a", metric)
    sig = "SIGNIFICANT" if result["significant"] else "not significant"
    print(f"  {metric:<15}: control={result['control_mean']:.4f} vs variant={result['variant_mean']:.4f} "
          f"(lift={result['lift']:+.2%}, p={result['p_value']:.4f}, {sig})")
print()

print("=== Canary Deployment ===")
canary = CanaryController(initial_pct=5)
baseline = {"error_rate": 0.015, "p95_latency": 1200, "quality_score": 0.85, "cost_per_request": 0.0009}

phases = [
    {"error_rate": 0.012, "p95_latency": 1100, "quality_score": 0.87, "cost_per_request": 0.00085},
    {"error_rate": 0.018, "p95_latency": 1300, "quality_score": 0.86, "cost_per_request": 0.00095},
    {"error_rate": 0.025, "p95_latency": 1900, "quality_score": 0.80, "cost_per_request": 0.0012},
]

step = 0
for phase_metrics in phases:
    step += 1
    promoted, new_pct = canary.should_promote(phase_metrics, baseline)
    status = "PROMOTED" if promoted else "ROLLED BACK"
    print(f"  Step {step}: promote to {new_pct}%? {status}")
    if not promoted:
        print(f"    Reason: metrics degraded below thresholds")
        break
    if new_pct >= 100:
        print(f"  -> Full production rollout complete")
        break

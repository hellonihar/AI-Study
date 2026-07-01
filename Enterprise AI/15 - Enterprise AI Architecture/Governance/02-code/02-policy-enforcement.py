"""
Policy enforcement engine: evaluate rule-based policies over model metadata.

Run: python 02-policy-enforcement.py
"""

print("=== Policy Enforcement Engine ===\n")

class Policy:
    def __init__(self, name, check_fn, severity="error"):
        self.name = name
        self.check_fn = check_fn
        self.severity = severity  # error, warning, info

class PolicyEngine:
    def __init__(self):
        self.policies = []

    def add(self, policy):
        self.policies.append(policy)

    def evaluate(self, model):
        results = []
        for p in self.policies:
            passed, message = p.check_fn(model)
            results.append({
                "policy": p.name,
                "severity": p.severity,
                "passed": passed,
                "message": message,
            })
        return results

engine = PolicyEngine()

engine.add(Policy("model_card", lambda m: (m.get("model_card", False), "Model card present" if m.get("model_card") else "Model card missing")))
engine.add(Policy("risk_tier", lambda m: (m.get("risk_tier", 3) <= 2, f"Risk tier {m.get('risk_tier')} within limit" if m.get("risk_tier", 3) <= 2 else f"Risk tier {m.get('risk_tier', 3)} exceeds limit")))
engine.add(Policy("data_privacy", lambda m: (m.get("data_region", "none") != "none", f"Data region: {m.get('data_region', 'none')}" if m.get("data_region") else "No data region specified")))
engine.add(Policy("bias_audit", lambda m: (m.get("risk_tier", 3) < 3 or m.get("bias_audit"), "Bias audit required for T3+" if m.get("risk_tier", 3) >= 3 and not m.get("bias_audit") else "Bias audit OK")))
engine.add(Policy("version_pinned", lambda m: ("." in m.get("model_version", ""), f"Version pinned: {m.get('model_version', 'none')}" if "." in m.get("model_version", "") else "Version not pinned")))

MODELS = [
    {"name": "chatbot-v1", "model_card": True, "risk_tier": 1, "data_region": "us", "bias_audit": False, "model_version": "1.2.3"},
    {"name": "hiring-v2", "model_card": True, "risk_tier": 3, "data_region": "eu", "bias_audit": True, "model_version": "2.0.0"},
    {"name": "experiment-x", "model_card": False, "risk_tier": 3, "data_region": "", "bias_audit": False, "model_version": "latest"},
    {"name": "medical-v1", "model_card": True, "risk_tier": 3, "data_region": "us", "bias_audit": True, "model_version": "0.9.1"},
]

for m in MODELS:
    print(f"=== {m['name']} ===")
    results = engine.evaluate(m)
    all_pass = all(r["passed"] or r["severity"] == "info" for r in results)
    for r in results:
        symbol = "+" if r["passed"] else "-"
        sev = r["severity"]
        print(f"  {symbol} [{sev:>7}] {r['policy']:<16} {r['message']}")
    print(f"  Verdict: {'PASS' if all_pass else 'REVIEW'}")
    print()

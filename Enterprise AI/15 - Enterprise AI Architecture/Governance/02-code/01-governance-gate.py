"""
Governance gate: policy-driven deployment approval with automated checks.

Run: python 01-governance-gate.py
"""

import hashlib
import json
from datetime import datetime

print("=== Governance Gate ===\n")

POLICIES = {
    "model_card_required": True,
    "bias_audit_required": False,
    "risk_tier_max": 2,
    "review_required_for_tier_3": False,
}

class ModelDeployment:
    def __init__(self, name, risk_tier, has_model_card, has_bias_audit):
        self.name = name
        self.risk_tier = risk_tier
        self.has_model_card = has_model_card
        self.has_bias_audit = has_bias_audit

    def passes(self):
        checks = []
        if POLICIES["model_card_required"] and not self.has_model_card:
            checks.append("FAIL: model_card_required")
        if POLICIES["bias_audit_required"] and not self.has_bias_audit:
            checks.append("FAIL: bias_audit_required")
        if self.risk_tier > POLICIES["risk_tier_max"] and POLICIES["review_required_for_tier_3"]:
            checks.append("FAIL: exceeds max risk tier without review")
        if not checks:
            checks.append("PASS")
        return checks

SUBMISSIONS = [
    ModelDeployment("customer-support-bot", 1, True, False),
    ModelDeployment("hiring-assistant", 3, True, True),
    ModelDeployment("content-summarizer", 2, False, False),
    ModelDeployment("medical-diagnosis", 3, True, True),
]

for dep in SUBMISSIONS:
    result = dep.passes()
    verdict = "PASS" if all("PASS" in r for r in result) else "BLOCKED"
    print(f"  {dep.name:<30} Tier={dep.risk_tier} Card={dep.has_model_card} Audit={dep.has_bias_audit} -> {verdict}")
    for r in result:
        if "FAIL" in r:
            print(f"    {r}")
print()

print("=== Decision Log ===")
for dep in SUBMISSIONS:
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": dep.name,
        "risk_tier": dep.risk_tier,
        "result": "PASS" if all("PASS" in r for r in dep.passes()) else "BLOCKED",
    }
    entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True, default=str).encode()).hexdigest()
    print(f"  {entry['model']:<30} {entry['result']:<8} hash={entry['hash'][:16]}...")

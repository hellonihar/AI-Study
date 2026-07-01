"""
Policy enforcement engine: runtime policy evaluation and enforcement.

Run: python 09-policy-enforcement-engine.py

Requirements: numpy
"""

import time
import json
import hashlib

print("=== Policy Enforcement Engine ===\n")

class Policy:
    def __init__(self, name, applies_to, checks, on_fail="block"):
        self.name = name
        self.applies_to = applies_to
        self.checks = checks
        self.on_fail = on_fail

    def evaluate(self, context):
        passed = True
        failures = []
        for check_name, expected in self.checks.items():
            actual = context.get(check_name)
            if callable(expected):
                check_passed = expected(actual)
            elif isinstance(expected, (int, float)):
                check_passed = actual == expected
            elif isinstance(expected, str):
                check_passed = actual == expected
            elif isinstance(expected, bool):
                check_passed = bool(actual) == expected
            elif isinstance(expected, dict):
                if "min" in expected:
                    check_passed = (actual or 0) >= expected["min"]
                elif "max" in expected:
                    check_passed = (actual or 0) <= expected["max"]
                else:
                    check_passed = False
            else:
                check_passed = actual == expected
            if not check_passed:
                failures.append({"check": check_name, "expected": expected, "actual": actual})
                passed = False
        return {"policy": self.name, "passed": passed, "failures": failures, "action": self.on_fail if not passed else "pass"}

class PolicyEngine:
    def __init__(self):
        self.policies = []

    def add_policy(self, policy):
        self.policies.append(policy)

    def evaluate_all(self, context):
        results = []
        for policy in self.policies:
            matches = True
            for key, value in policy.applies_to.items():
                if context.get(key) != value:
                    matches = False
                    break
            if matches:
                result = policy.evaluate(context)
                results.append(result)
        return results

    def gate_check(self, context):
        results = self.evaluate_all(context)
        all_passed = all(r["passed"] for r in results)
        blocked = any(r["action"] == "block" for r in results)
        return {
            "passed": all_passed and not blocked,
            "results": results,
            "blocked": blocked,
            "summary": "PASS" if (all_passed and not blocked) else "BLOCKED" if blocked else "FAIL",
        }

engine = PolicyEngine()

engine.add_policy(Policy(
    "high-risk-deployment-gate",
    {"risk_tier": "Tier 3: High"},
    {"model_card_exists": True, "bias_audit_age_days": {"max": 180}, "risk_assessment_approved": True},
    on_fail="block",
))

engine.add_policy(Policy(
    "data-retention-enforcement",
    {"data_type": "inference_logs"},
    {"retention_days": {"max": 90}},
    on_fail="warn",
))

engine.add_policy(Policy(
    "production-readiness-check",
    {"environment": "production"},
    {"documentation_complete": True, "guardrails_enabled": True, "monitoring_configured": True},
    on_fail="block",
))

engine.add_policy(Policy(
    "model-registration-required",
    {"action": "deploy"},
    {"model_registered": True, "version_pinned": True},
    on_fail="block",
))

TEST_CONTEXTS = [
    {
        "name": "Valid High-Risk Deployment",
        "context": {
            "risk_tier": "Tier 3: High",
            "model_card_exists": True,
            "bias_audit_age_days": 45,
            "risk_assessment_approved": True,
            "environment": "production",
            "documentation_complete": True,
            "guardrails_enabled": True,
            "monitoring_configured": True,
            "action": "deploy",
            "model_registered": True,
            "version_pinned": True,
        },
    },
    {
        "name": "Missing Documentation",
        "context": {
            "risk_tier": "Tier 3: High",
            "model_card_exists": False,
            "bias_audit_age_days": 200,
            "risk_assessment_approved": False,
            "environment": "production",
            "documentation_complete": False,
            "guardrails_enabled": True,
            "monitoring_configured": True,
            "action": "deploy",
            "model_registered": True,
            "version_pinned": True,
        },
    },
    {
        "name": "Data Retention Check",
        "context": {
            "data_type": "inference_logs",
            "retention_days": 120,
        },
    },
]

print(f"{'Scenario':<35} {'Result':<10} {'Policy Checks':<10}")
print("-" * 60)
for test in TEST_CONTEXTS:
    result = engine.gate_check(test["context"])
    print(f"{test['name']:<35} {result['summary']:<10} {len(result['results'])} policies")
    for r in result["results"]:
        if not r["passed"]:
            for f in r["failures"]:
                print(f"  {'':<35} FAIL: {f['check']} (expected {f['expected']}, got {f['actual']})")
    print()

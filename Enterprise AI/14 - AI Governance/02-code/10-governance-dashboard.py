"""
Governance dashboard: end-to-end governance overview with metrics and compliance status.

Run: python 10-governance-dashboard.py

Requirements: numpy
"""

import time
import json
import numpy as np
from collections import defaultdict

print("=== Governance Dashboard ===\n")

class GovernanceDashboard:
    def __init__(self):
        self.models = []
        self.incidents = []
        self.audits = []
        self.policy_violations = []

    def add_model(self, name, tier, documented=True, bias_audited=True, last_review_days=30):
        self.models.append({
            "name": name,
            "tier": tier,
            "documented": documented,
            "bias_audited": bias_audited,
            "last_review_days": last_review_days,
        })

    def add_incident(self, severity, incident_type, resolved=True, time_to_resolve_min=30):
        self.incidents.append({
            "severity": severity,
            "type": incident_type,
            "resolved": resolved,
            "time_to_resolve_min": time_to_resolve_min,
        })

    def add_policy_violation(self, policy, severity, remediated=True, remediation_days=14):
        self.policy_violations.append({
            "policy": policy,
            "severity": severity,
            "remediated": remediated,
            "remediation_days": remediation_days,
        })

    def compute_metrics(self):
        total_models = len(self.models)
        documented = sum(1 for m in self.models if m["documented"])
        bias_audited = sum(1 for m in self.models if m["bias_audited"])
        models_tier3_up = sum(1 for m in self.models if m["tier"] in ("Tier 3: High", "Tier 4: Critical"))
        models_tier3_audited = sum(1 for m in self.models if m["tier"] in ("Tier 3: High", "Tier 4: Critical") and m["bias_audited"])
        models_overdue_review = sum(1 for m in self.models if m["last_review_days"] > 180)

        total_incidents = len(self.incidents)
        resolved_incidents = sum(1 for i in self.incidents if i["resolved"])
        sev1_count = sum(1 for i in self.incidents if i["severity"] == "SEV-1")
        avg_resolve_time = np.mean([i["time_to_resolve_min"] for i in self.incidents if i["resolved"]]) if resolved_incidents > 0 else 0

        total_violations = len(self.policy_violations)
        remediated = sum(1 for v in self.policy_violations if v["remediated"])
        open_violations = total_violations - remediated

        doc_rate = (documented / total_models * 100) if total_models > 0 else 0
        bias_rate = (bias_audited / total_models * 100) if total_models > 0 else 0
        tier3_audit_rate = (models_tier3_audited / models_tier3_up * 100) if models_tier3_up > 0 else 0

        return {
            "model_inventory": {
                "total": total_models,
                "documented": documented,
                "documentation_rate": round(doc_rate, 1),
                "bias_audited": bias_audited,
                "bias_audit_rate": round(bias_rate, 1),
                "tier3_plus": models_tier3_up,
                "tier3_audited_pct": round(tier3_audit_rate, 1),
                "overdue_review": models_overdue_review,
            },
            "incidents": {
                "total": total_incidents,
                "resolved": resolved_incidents,
                "resolution_rate": round(resolved_incidents / total_incidents * 100, 1) if total_incidents > 0 else 0,
                "sev1_count": sev1_count,
                "avg_resolve_time_min": round(avg_resolve_time, 1),
            },
            "policy_compliance": {
                "total_violations": total_violations,
                "remediated": remediated,
                "open_violations": open_violations,
                "remediation_rate": round(remediated / total_violations * 100, 1) if total_violations > 0 else 0,
            },
            "overall_health": {
                "compliance_score": 0,
                "status": "",
            },
        }

    def compute_health(self):
        metrics = self.compute_metrics()
        doc_score = metrics["model_inventory"]["documentation_rate"] / 100 * 30
        bias_score = metrics["model_inventory"]["bias_audit_rate"] / 100 * 25
        incident_score = metrics["incidents"]["resolution_rate"] / 100 * 20
        tier3_score = metrics["model_inventory"]["tier3_audited_pct"] / 100 * 15
        policy_score = metrics["policy_compliance"]["remediation_rate"] / 100 * 10
        total_score = doc_score + bias_score + incident_score + tier3_score + policy_score
        metrics["overall_health"]["compliance_score"] = round(total_score, 1)
        if total_score >= 90:
            metrics["overall_health"]["status"] = "HEALTHY"
        elif total_score >= 70:
            metrics["overall_health"]["status"] = "WARNING"
        else:
            metrics["overall_health"]["status"] = "CRITICAL"
        return metrics

dashboard = GovernanceDashboard()

dashboard.add_model("Customer Support Chatbot", "Tier 2: Medium", True, True, 30)
dashboard.add_model("Loan Origination AI", "Tier 3: High", True, True, 15)
dashboard.add_model("Code Assistant", "Tier 1: Low", True, False, 90)
dashboard.add_model("Medical Diagnosis AI", "Tier 4: Critical", True, True, 5)
dashboard.add_model("Content Moderation", "Tier 3: High", True, True, 60)
dashboard.add_model("Search Ranking", "Tier 2: Medium", False, False, 200)
dashboard.add_model("Fraud Detection", "Tier 3: High", True, False, 250)
dashboard.add_model("Internal Doc Search", "Tier 1: Low", True, False, 45)

dashboard.add_incident("SEV-2", "quality_degradation", True, 45)
dashboard.add_incident("SEV-1", "safety_breach", True, 12)
dashboard.add_incident("SEV-3", "cost_anomaly", True, 120)
dashboard.add_incident("SEV-2", "latency_spike", True, 30)
dashboard.add_incident("SEV-3", "model_drift", False, 0)

dashboard.add_policy_violation("documentation_requirement", "medium", True, 14)
dashboard.add_policy_violation("bias_audit_overdue", "high", False, 45)
dashboard.add_policy_violation("retention_policy", "low", True, 7)

metrics = dashboard.compute_health()

print("=== Governance Dashboard ===")
print(f"  Overall Compliance Score: {metrics['overall_health']['compliance_score']}/100")
print(f"  Status: {metrics['overall_health']['status']}")
print()

print("--- Model Inventory ---")
mi = metrics["model_inventory"]
print(f"  Total Models:          {mi['total']}")
print(f"  Documented:            {mi['documented']} ({mi['documentation_rate']}%)")
print(f"  Bias Audited:          {mi['bias_audited']} ({mi['bias_audit_rate']}%)")
print(f"  Tier 3+ Models:        {mi['tier3_plus']}")
print(f"  Tier 3+ Audited:       {mi['tier3_audited_pct']}%")
print(f"  Overdue Review:        {mi['overdue_review']}")
print()

print("--- Incidents ---")
inc = metrics["incidents"]
print(f"  Total Incidents:       {inc['total']}")
print(f"  Resolved:              {inc['resolved']} ({inc['resolution_rate']}%)")
print(f"  SEV-1 Incidents:       {inc['sev1_count']}")
print(f"  Avg Resolve Time:      {inc['avg_resolve_time_min']} min")
print()

print("--- Policy Compliance ---")
pc = metrics["policy_compliance"]
print(f"  Total Violations:      {pc['total_violations']}")
print(f"  Remediated:            {pc['remediated']} ({pc['remediation_rate']}%)")
print(f"  Open Violations:       {pc['open_violations']}")
print()

print("--- Action Items ---")
dashboard.add_model("Search Ranking", "Tier 2: Medium", False, False, 200)
dashboard.add_model("Fraud Detection", "Tier 3: High", True, False, 250)

for m in dashboard.models:
    actions = []
    if not m["documented"]:
        actions.append("Create model documentation")
    if not m["bias_audited"] and m["tier"] in ("Tier 3: High", "Tier 4: Critical"):
        actions.append("Conduct bias audit")
    if m["last_review_days"] > 180:
        actions.append(f"Review overdue ({m['last_review_days']} days)")
    if actions:
        print(f"  {m['name']}:")
        for a in actions:
            print(f"    - {a}")

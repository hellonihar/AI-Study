"""
Compliance checker: verify AI systems meet regulatory requirements.

Run: python 02-compliance-checker.py

Requirements: numpy
"""

import time
from collections import defaultdict

print("=== Compliance Checker ===\n")

REGULATIONS = {
    "EU AI Act": {
        "requirements": [
            "risk_assessment_complete",
            "transparency_notice_provided",
            "human_oversight_defined",
            "technical_documentation_maintained",
            "conformity_assessment_passed",
        ],
    },
    "GDPR": {
        "requirements": [
            "consent_obtained",
            "data_minimization_applied",
            "right_to_explanation_available",
            "right_to_deletion_process",
            "dpia_completed_if_required",
        ],
    },
    "NYC Local Law 144": {
        "requirements": [
            "bias_audit_conducted",
            "audit_results_published",
            "candidates_notified",
            "alternative_selection_process_available",
        ],
    },
}

class ComplianceChecker:
    def __init__(self):
        self.regulations = REGULATIONS

    def check(self, system_profile):
        results = {}
        for reg_name, reg_config in self.regulations.items():
            req_results = []
            for req in reg_config["requirements"]:
                met = system_profile.get(req, False)
                req_results.append({"requirement": req, "met": met})
            met_count = sum(1 for r in req_results if r["met"])
            total = len(req_results)
            compliance_pct = round((met_count / total) * 100, 1) if total > 0 else 0
            results[reg_name] = {
                "compliance_pct": compliance_pct,
                "met": met_count,
                "total": total,
                "requirements": req_results,
            }
        return results

    def overall_status(self, results):
        scores = [r["compliance_pct"] for r in results.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        if avg_score >= 90:
            return "COMPLIANT", avg_score
        elif avg_score >= 70:
            return "PARTIALLY_COMPLIANT", avg_score
        else:
            return "NON_COMPLIANT", avg_score

checker = ComplianceChecker()

SYSTEMS = [
    {
        "name": "Customer Support Chatbot",
        "profile": {
            "risk_assessment_complete": True,
            "transparency_notice_provided": True,
            "human_oversight_defined": False,
            "technical_documentation_maintained": True,
            "conformity_assessment_passed": True,
            "consent_obtained": True,
            "data_minimization_applied": True,
            "right_to_explanation_available": False,
            "right_to_deletion_process": True,
            "dpia_completed_if_required": False,
            "bias_audit_conducted": True,
            "audit_results_published": False,
            "candidates_notified": True,
            "alternative_selection_process_available": False,
        },
    },
    {
        "name": "Loan Origination AI",
        "profile": {
            "risk_assessment_complete": True,
            "transparency_notice_provided": True,
            "human_oversight_defined": True,
            "technical_documentation_maintained": True,
            "conformity_assessment_passed": False,
            "consent_obtained": True,
            "data_minimization_applied": True,
            "right_to_explanation_available": True,
            "right_to_deletion_process": True,
            "dpia_completed_if_required": True,
            "bias_audit_conducted": True,
            "audit_results_published": True,
            "candidates_notified": True,
            "alternative_selection_process_available": False,
        },
    },
]

for system in SYSTEMS:
    print(f"=== {system['name']} ===")
    results = checker.check(system["profile"])
    status, avg_score = checker.overall_status(results)
    print(f"  Overall: {status} ({avg_score:.1f}%)")
    print()
    for reg_name, reg_result in results.items():
        print(f"  {reg_name}: {reg_result['compliance_pct']:.0f}% ({reg_result['met']}/{reg_result['total']})")
        for req in reg_result["requirements"]:
            icon = "PASS" if req["met"] else "FAIL"
            print(f"    [{icon}] {req['requirement']}")
    print()

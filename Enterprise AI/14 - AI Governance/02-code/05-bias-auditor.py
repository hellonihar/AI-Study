"""
Bias auditor: fairness metrics and bias detection across demographic groups.

Run: python 05-bias-auditor.py

Requirements: numpy
"""

import numpy as np

print("=== Bias Auditor ===\n")

class FairnessMetrics:
    @staticmethod
    def demographic_parity(predictions, groups):
        results = {}
        for group_name, group_preds in groups.items():
            positive_rate = np.mean(group_preds) if len(group_preds) > 0 else 0
            results[group_name] = round(float(positive_rate), 4)
        return results

    @staticmethod
    def equal_opportunity(predictions, labels, groups):
        results = {}
        for group_name, group_idx in groups.items():
            group_preds = predictions[group_idx]
            group_labels = labels[group_idx]
            positive_mask = group_labels == 1
            if np.sum(positive_mask) > 0:
                tpr = np.mean(group_preds[positive_mask])
            else:
                tpr = 0
            results[group_name] = round(float(tpr), 4)
        return results

    @staticmethod
    def disparate_impact(positive_rates):
        rates = list(positive_rates.values())
        if len(rates) < 2:
            return 1.0
        min_rate = min(rates)
        max_rate = max(rates)
        if max_rate == 0:
            return 1.0
        return round(min_rate / max_rate, 4)

    @staticmethod
    def subgroup_accuracy(predictions, labels, groups):
        results = {}
        for group_name, group_idx in groups.items():
            group_preds = predictions[group_idx]
            group_labels = labels[group_idx]
            accuracy = np.mean(group_preds == group_labels) if len(group_preds) > 0 else 0
            results[group_name] = round(float(accuracy), 4)
        return results

class BiasAuditor:
    def __init__(self):
        self.thresholds = {
            "disparate_impact": 0.8,
            "accuracy_gap": 0.05,
        }

    def audit(self, predictions, labels, groups):
        metrics = FairnessMetrics()
        dp = metrics.demographic_parity(predictions, groups)
        di = metrics.disparate_impact(dp)
        acc = metrics.subgroup_accuracy(predictions, labels, groups)
        eopp = metrics.equal_opportunity(predictions, labels, groups)

        findings = []
        if di < self.thresholds["disparate_impact"]:
            findings.append({
                "type": "disparate_impact",
                "severity": "HIGH",
                "value": di,
                "threshold": self.thresholds["disparate_impact"],
                "detail": f"Disparate impact {di:.3f} below threshold {self.thresholds['disparate_impact']}",
            })

        acc_values = list(acc.values())
        if len(acc_values) > 1:
            max_acc_gap = max(acc_values) - min(acc_values)
            if max_acc_gap > self.thresholds["accuracy_gap"]:
                findings.append({
                    "type": "accuracy_disparity",
                    "severity": "MEDIUM",
                    "value": round(max_acc_gap, 4),
                    "threshold": self.thresholds["accuracy_gap"],
                    "detail": f"Accuracy gap {max_acc_gap:.3f} across groups exceeds {self.thresholds['accuracy_gap']}",
                })

        return {
            "demographic_parity": dp,
            "disparate_impact": di,
            "accuracy_by_group": acc,
            "equal_opportunity": eopp,
            "findings": findings,
            "passed": len(findings) == 0,
        }

auditor = BiasAuditor()

np.random.seed(42)
n_samples = 1000
groups = {
    "Group_A": np.arange(0, 400),
    "Group_B": np.arange(400, 700),
    "Group_C": np.arange(700, 1000),
}
labels = np.random.binomial(1, 0.5, n_samples)

fair_preds = np.random.binomial(1, [0.5] * n_samples)
unfair_preds = np.copy(fair_preds)
unfair_preds[groups["Group_A"]] = np.random.binomial(1, 0.35, 400)
unfair_preds[groups["Group_C"]] = np.random.binomial(1, 0.65, 300)

print("=== Fair Model Audit ===")
fair_result = auditor.audit(fair_preds, labels, groups)
print(f"  Disparate Impact: {fair_result['disparate_impact']:.4f} (threshold: 0.8)")
print(f"  Status: {'PASS' if fair_result['passed'] else 'FAIL'}")
print(f"  Demographic Parity: {fair_result['demographic_parity']}")
print(f"  Accuracy by Group:  {fair_result['accuracy_by_group']}")
print()

print("=== Unfair Model Audit ===")
unfair_result = auditor.audit(unfair_preds, labels, groups)
print(f"  Disparate Impact: {unfair_result['disparate_impact']:.4f} (threshold: 0.8)")
print(f"  Status: {'PASS' if unfair_result['passed'] else 'FAIL'}")
print(f"  Findings:")
for f in unfair_result["findings"]:
    print(f"    [{f['severity']}] {f['detail']}")
print(f"  Demographic Parity: {unfair_result['demographic_parity']}")
print()

print("=== Audit Decision ===")
for name, result in [("Fair Model", fair_result), ("Unfair Model", unfair_result)]:
    if result["passed"]:
        print(f"  {name}: PASS - No bias detected")
    else:
        print(f"  {name}: FAIL - {len(result['findings'])} bias findings - BLOCKING DEPLOYMENT")

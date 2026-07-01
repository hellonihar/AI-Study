"""
ROI calculator: compute return on investment for enterprise AI initiatives.

Run: python 03-roi-calculator.py

Requirements: numpy
"""

import numpy as np

print("=== ROI Calculator ===\n")

class ROICalculator:
    def __init__(self):
        self.scenarios = []

    def add_scenario(self, name, dev_cost, dev_months, monthly_infra, monthly_ops,
                     monthly_requests, savings_per_request):
        monthly_cost = monthly_infra + monthly_ops
        monthly_savings = monthly_requests * savings_per_request
        annual_cost = dev_cost + monthly_cost * 12
        annual_savings = monthly_savings * 12
        net_annual = annual_savings - annual_cost
        roi = ((annual_savings - annual_cost) / annual_cost) * 100 if annual_cost > 0 else 0
        payback_months = dev_cost / (monthly_savings - monthly_cost) if monthly_savings > monthly_cost else 999
        self.scenarios.append({
            "name": name,
            "dev_cost": dev_cost,
            "monthly_cost": monthly_cost,
            "monthly_savings": monthly_savings,
            "annual_cost": round(annual_cost, 2),
            "annual_savings": round(annual_savings, 2),
            "net_annual": round(net_annual, 2),
            "roi_pct": round(roi, 1),
            "payback_months": round(payback_months, 1),
        })

    def report(self):
        print(f"{'Scenario':<30} {'Dev Cost':>10} {'Annual Cost':>12} {'Annual Savings':>14} "
              f"{'Net Annual':>12} {'ROI':>8} {'Payback':>10}")
        print("-" * 100)
        for s in self.scenarios:
            pm = f"{s['payback_months']}mo" if s['payback_months'] < 60 else ">5yr"
            print(f"{s['name']:<30} ${s['dev_cost']:<7,.0f} ${s['annual_cost']:<9,.0f} "
                  f"${s['annual_savings']:<10,.0f} ${s['net_annual']:<9,.0f} "
                  f"{s['roi_pct']:>6.0f}% {pm:>10}")

calc = ROICalculator()
calc.add_scenario("Customer Support Chatbot", 60000, 4, 2000, 3000, 500000, 0.15)
calc.add_scenario("Code Generation Assistant", 80000, 6, 3000, 2000, 200000, 0.30)
calc.add_scenario("Document Processing AI", 100000, 6, 5000, 3000, 100000, 0.80)
calc.add_scenario("Enterprise Search RAG", 120000, 8, 4000, 2500, 300000, 0.10)
calc.add_scenario("Custom Fine-Tuned Model", 200000, 12, 8000, 4000, 1000000, 0.05)
calc.report()
print()

print("=== Sensitivity Analysis: Customer Support Chatbot ===")
base_dev = 60000
for dev_cost in [40000, 60000, 80000, 100000]:
    monthly_cost = 5000
    monthly_savings = 500000 * 0.15
    annual_cost = dev_cost + monthly_cost * 12
    annual_savings = monthly_savings * 12
    roi = ((annual_savings - annual_cost) / annual_cost) * 100
    payback = dev_cost / (monthly_savings - monthly_cost)
    print(f"  Dev=${dev_cost:<6,}: ROI={roi:.0f}%, Payback={payback:.1f}mo")

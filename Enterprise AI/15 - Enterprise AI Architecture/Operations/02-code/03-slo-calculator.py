"""
SLO calculator: compute service level objectives for AI services.

Run: python 03-slo-calculator.py
"""

print("=== SLO Calculator ===\n")

class SLOCalculator:
    def compute_budget(self, monthly_requests, target_availability):
        allowed_failures = monthly_requests * (1 - target_availability / 100)
        return {
            "monthly_requests": monthly_requests,
            "target_availability": target_availability,
            "allowed_failures_per_month": int(allowed_failures),
            "allowed_failures_per_day": int(allowed_failures / 30),
            "allowed_failures_per_week": int(allowed_failures / 4.33),
        }

SLO_SCENARIOS = [
    ("Customer Chatbot", 10_000_000, 99.95),
    ("Enterprise Search", 50_000_000, 99.99),
    ("Code Assistant", 1_000_000, 99.9),
    ("Document Processing", 500_000, 99.5),
    ("Internal Tool", 100_000, 99.0),
]

calc = SLOCalculator()
print(f"{'Service':<22} {'Monthly Req':>14} {'Target':>8} {'Allowed Failures':>18} {'Per Day':>8}")
print("-" * 70)
for name, req, target in SLO_SCENARIOS:
    budget = calc.compute_budget(req, target)
    print(f"  {name:<20} {budget['monthly_requests']:>12,} {budget['target_availability']:>6.2f}% "
          f"{budget['allowed_failures_per_month']:>8,} {budget['allowed_failures_per_day']:>6,}")
print()

print("=== Multi-tier SLO ===")
print(f"{'Tier':<10} {'Availability':>14} {'Max Downtime/Mo':>16}")
tiers = {"Critical": 99.995, "High": 99.99, "Standard": 99.9, "Best Effort": 99.0}
for tier, avail in tiers.items():
    downtime_seconds = (1 - avail / 100) * 30 * 24 * 3600
    print(f"  {tier:<8} {avail:>8.3f}%    {downtime_seconds:.0f}s ({downtime_seconds/60:.1f} min)")

"""
Disaster recovery simulator: model failover scenarios and RTO/RPO tracking.

Run: python 04-disaster-recovery-simulator.py

Requirements: numpy
"""

import time
import random

print("=== Disaster Recovery Simulator ===\n")

class ServiceComponent:
    def __init__(self, name, primary_region, secondary_region=None):
        self.name = name
        self.primary_region = primary_region
        self.secondary_region = secondary_region
        self.active_region = primary_region
        self.healthy = True
        self.failover_time_s = 0

class DisasterScenario:
    def __init__(self, name, components, rto_sla_s=900):
        self.name = name
        self.components = components
        self.rto_sla_s = rto_sla_s
        self.timeline = []

    def fail_component(self, component_name):
        for c in self.components:
            if c.name == component_name:
                c.healthy = False
                self.timeline.append((time.time(), "FAIL", f"{c.name} in {c.active_region}"))
                return True
        return False

    def failover(self, component_name):
        for c in self.components:
            if c.name == component_name and not c.healthy and c.secondary_region:
                start = time.time()
                delay = random.uniform(30, 300)
                c.failover_time_s = delay
                if delay <= self.rto_sla_s:
                    time.sleep(0.001)
                    c.active_region = c.secondary_region
                    c.healthy = True
                    self.timeline.append((time.time(), "FAILOVER_OK",
                        f"{c.name} -> {c.secondary_region} in {delay:.0f}s"))
                else:
                    self.timeline.append((time.time(), "FAILOVER_SLA_BREACH",
                        f"{c.name} took {delay:.0f}s (SLA: {self.rto_sla_s}s)"))
                return delay
        return None

    def report(self):
        total_rto = 0
        sla_compliant = True
        for c in self.components:
            if not c.healthy:
                print(f"  {c.name}: UNHEALTHY (no secondary)")
                sla_compliant = False
            elif hasattr(c, 'failover_time_s') and c.failover_time_s > 0:
                total_rto = max(total_rto, c.failover_time_s)
                if c.failover_time_s <= self.rto_sla_s:
                    print(f"  {c.name}: FAILED OVER to {c.active_region} in {c.failover_time_s:.0f}s (SLA OK)")
                else:
                    print(f"  {c.name}: FAILED OVER in {c.failover_time_s:.0f}s (SLA BREACH: {self.rto_sla_s}s)")
                    sla_compliant = False
            else:
                print(f"  {c.name}: HEALTHY in {c.active_region}")
        print(f"\n  Max RTO: {total_rto:.0f}s (SLA: {self.rto_sla_s}s)")
        print(f"  SLA Status: {'COMPLIANT' if sla_compliant else 'BREACHED'}")

components = [
    ServiceComponent("API Gateway", "us-east", "us-west"),
    ServiceComponent("Orchestrator", "us-east", "us-west"),
    ServiceComponent("Model Server", "us-east", "us-west"),
    ServiceComponent("Vector DB", "us-east", "us-west"),
    ServiceComponent("Cache (Redis)", "us-east", "us-west"),
]

random.seed(42)

print("=== Scenario 1: Single AZ Failure ===")
scenario = DisasterScenario("AZ Failure", components[:3], rto_sla_s=300)
scenario.fail_component("Orchestrator")
scenario.failover("Orchestrator")
scenario.report()
print()

print("=== Scenario 2: Multi-Component Failure ===")
scenario2 = DisasterScenario("Multi-Component Failure", components, rto_sla_s=600)
scenario2.fail_component("API Gateway")
scenario2.fail_component("Model Server")
scenario2.fail_component("Vector DB")
scenario2.failover("API Gateway")
scenario2.failover("Model Server")
scenario2.failover("Vector DB")
scenario2.report()
print()

print("=== Scenario 3: Full Region Failure ===")
scenario3 = DisasterScenario("Region Failure", components, rto_sla_s=900)
for c in components:
    scenario3.fail_component(c.name)
for c in components:
    scenario3.failover(c.name)
scenario3.report()

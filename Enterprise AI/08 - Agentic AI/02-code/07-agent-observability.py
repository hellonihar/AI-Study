"""
Agent observability: step-by-step tracing, metrics emission, and trace visualization.

Run: python 07-agent-observability.py

Requirements: none (stdlib only)
"""

import json
import time
import uuid
from datetime import datetime

print("=== Agent Observability ===\n")

class TraceStep:
    def __init__(self, step_num, action, model="gpt-4o-mini"):
        self.step_id = str(uuid.uuid4())[:8]
        self.step_num = step_num
        self.action = action
        self.model = model
        self.start_time = time.time()
        self.end_time = None
        self.input_tokens = 0
        self.output_tokens = 0
        self.status = "pending"
        self.error = None
        self.tool_result = None

    def complete(self, result, input_tokens=50, output_tokens=100):
        self.end_time = time.time()
        self.status = "success"
        self.tool_result = result
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        return self

    def fail(self, error):
        self.end_time = time.time()
        self.status = "failed"
        self.error = str(error)
        return self

    def latency_ms(self):
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

    def cost(self):
        return self.input_tokens * 0.000003 + self.output_tokens * 0.000012

    def to_dict(self):
        return {
            "step": self.step_num,
            "action": self.action,
            "status": self.status,
            "latency_ms": round(self.latency_ms(), 1),
            "tokens": {"input": self.input_tokens, "output": self.output_tokens},
            "cost": round(self.cost(), 5),
            "error": self.error,
        }

class Trace:
    def __init__(self, task_id, goal):
        self.task_id = task_id
        self.goal = goal
        self.steps = []
        self.start_time = datetime.now().isoformat()
        self.end_time = None

    def add_step(self, step):
        self.steps.append(step)
        return step

    def finish(self):
        self.end_time = datetime.now().isoformat()

    def summary(self):
        total_cost = sum(s.cost() for s in self.steps)
        total_latency = sum(s.latency_ms() for s in self.steps)
        total_tokens = sum(s.input_tokens + s.output_tokens for s in self.steps)
        failed = sum(1 for s in self.steps if s.status == "failed")

        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "steps": len(self.steps),
            "failed_steps": failed,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "total_latency_ms": round(total_latency, 1),
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

class ObservableAgent:
    def __init__(self):
        self.current_trace = None

    def run(self, goal):
        task_id = str(uuid.uuid4())[:8]
        self.current_trace = Trace(task_id, goal)
        print(f"Starting task: {task_id} — {goal}\n")

        steps_data = [
            {"action": "search('AI trends 2024')", "result": "Results found", "in": 80, "out": 50},
            {"action": "extract_key_findings(results)", "result": "3 findings", "in": 150, "out": 80},
            {"action": "generate_report(findings)", "result": "Report generated", "in": 200, "out": 300},
        ]

        for i, data in enumerate(steps_data, 1):
            time.sleep(0.02)
            step = TraceStep(i, data["action"])
            self.current_trace.add_step(step)

            success = i != 2
            if success:
                step.complete(data["result"], data["in"], data["out"])
                status_icon = "✓"
            else:
                step.fail("Tool timeout")
                status_icon = "✗"

            print(f"  Step {i}: {data['action'][:40]:<40} "
                  f"[{status_icon}] {step.latency_ms():.0f}ms "
                  f"${step.cost():.5f}")

            if not success:
                print(f"          Fallback: using cached result")
                step2 = TraceStep(i, "fallback: cache_lookup('AI trends')")
                self.current_trace.add_step(step2)
                step2.complete("Cached results", 10, 30)
                print(f"          [✓] Fallback completed ${step2.cost():.5f}")

        self.current_trace.finish()

        summary = self.current_trace.summary()
        print(f"\n{'='*60}")
        print("Trace Summary")
        print(f"{'='*60}")
        for key, val in summary.items():
            print(f"  {key}: {val}")

        print(f"\n{'='*60}")
        print("Step Details")
        print(f"{'='*60}")
        for s in self.current_trace.steps:
            print(f"  Step {s.step_num}: {s.action[:35]:<35} "
                  f"status={s.status:<8} latency={s.latency_ms():.0f}ms "
                  f"cost=${s.cost():.5f}")

        return summary

agent = ObservableAgent()
agent.run("Research AI trends and generate report")

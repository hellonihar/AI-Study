"""
CI/CD pipeline simulation: lint, eval, deploy gates for prompts and models.

Run: python 07-cicd-pipeline-sim.py

Requirements: numpy
"""

import time
import json
import hashlib

print("=== CI/CD Pipeline Simulation ===\n")

class PipelineStage:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.status = "pending"
        self.output = {}

    def run(self):
        self.start_time = time.time()
        self.status = "running"

    def complete(self, success, output=None):
        self.end_time = time.time()
        self.status = "passed" if success else "failed"
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 1)
        if output:
            self.output = output

    def report(self):
        return f"  {self.name:<20} [{self.status:<8}] {getattr(self, 'duration_ms', 0):>8.1f}ms"

class LintStage(PipelineStage):
    def __init__(self):
        super().__init__("lint")

    def run(self, prompt_text):
        super().run()
        import re
        issues = []
        has_secrets = "sk-" in prompt_text or "password" in prompt_text.lower() or "api_key" in prompt_text.lower()
        has_pii = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", prompt_text))
        if has_secrets:
            issues.append("contains_secrets")
        if has_pii:
            issues.append("contains_pii")
        if len(prompt_text.split()) > 500:
            issues.append("too_long")
        success = len(issues) == 0
        self.complete(success, {"checks": {"has_secrets": has_secrets, "has_pii": has_pii, "max_length": len(prompt_text.split()) <= 500}, "issues": issues})

class EvalStage(PipelineStage):
    def __init__(self):
        super().__init__("evaluation")

    def run(self, test_results):
        super().run()
        metrics = {
            "accuracy": test_results.get("accuracy", 0),
            "safety": test_results.get("safety", 0),
            "relevance": test_results.get("relevance", 0),
        }
        thresholds = {"accuracy": 0.7, "safety": 0.8, "relevance": 0.7}
        failures = {k: v for k, v in metrics.items() if v < thresholds.get(k, 0)}
        success = len(failures) == 0
        self.complete(success, {"metrics": metrics, "thresholds": thresholds, "failures": failures})

class BuildStage(PipelineStage):
    def __init__(self):
        super().__init__("build")

    def run(self):
        super().run()
        time.sleep(0.01)
        version = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        self.complete(True, {"version": version, "artifact": f"prompt-bundle-{version}.zip"})

class DeployStage(PipelineStage):
    def __init__(self):
        super().__init__("deploy")

    def run(self, target, pct=100):
        super().run()
        time.sleep(0.01)
        self.complete(True, {"target": target, "traffic_pct": pct})

class CICDPipeline:
    def __init__(self, name="default"):
        self.name = name
        self.stages = []
        self.commit_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]

    def add_stage(self, stage):
        self.stages.append(stage)

    def execute(self):
        print(f"  Pipeline: {self.name}")
        print(f"  Commit:   {self.commit_id}")
        print()
        all_passed = True
        for stage in self.stages:
            print(stage.report())
            if stage.status == "failed":
                all_passed = False
                print(f"  -> Pipeline FAILED at stage: {stage.name}")
                break
        if all_passed:
            print(f"\n  -> Pipeline PASSED - ready for production")
        return all_passed

print("=== Successful Pipeline Run ===")
pipeline_ok = CICDPipeline("prompt_update_v2")

lint = LintStage()
lint.run("You are a helpful assistant. Respond to: {{query}}")
pipeline_ok.add_stage(lint)

eval_stage = EvalStage()
eval_stage.run({"accuracy": 0.89, "safety": 0.97, "relevance": 0.91})
pipeline_ok.add_stage(eval_stage)

build = BuildStage()
build.run()
pipeline_ok.add_stage(build)

deploy = DeployStage()
deploy.run("staging", 100)
pipeline_ok.add_stage(deploy)

pipeline_ok.execute()
print()

print("=== Failing Pipeline Run (Lint) ===")
pipeline_fail = CICDPipeline("prompt_update_v3")

lint_fail = LintStage()
lint_fail.run("You are a helpful assistant. My API key is sk-proj-abc123. Respond to: {{query}}")
pipeline_fail.add_stage(lint_fail)

pipeline_fail.execute()
print()

print("=== Failing Pipeline Run (Eval) ===")
pipeline_eval_fail = CICDPipeline("prompt_update_v4")

lint_ok = LintStage()
lint_ok.run("You are a helpful assistant. Respond to: {{query}}")
pipeline_eval_fail.add_stage(lint_ok)

eval_fail = EvalStage()
eval_fail.run({"accuracy": 0.45, "safety": 0.92, "relevance": 0.60})
pipeline_eval_fail.add_stage(eval_fail)

pipeline_eval_fail.execute()
print()

print("=== Pipeline Gate Summary ===")
print(f"  {'Gate':<16} {'Metric':<20} {'Threshold':<12} {'Pass':<8}")
print("  " + "-" * 60)
gates = [
    ("lint", "no secrets/PII", "strict", "pass/fail"),
    ("eval_accuracy", "accuracy", ">= 0.70", "pass/fail"),
    ("eval_safety", "safety", ">= 0.80", "pass/fail"),
    ("eval_relevance", "relevance", ">= 0.70", "pass/fail"),
    ("build", "artifact creation", "always", "pass/fail"),
    ("canary_errors", "error rate", "< baseline + 0.5%", "auto-rollback"),
    ("canary_latency", "p95 latency", "< baseline + 20%", "auto-rollback"),
    ("canary_quality", "quality score", "> baseline - 2%", "auto-rollback"),
]
for gate, metric, threshold, action in gates:
    print(f"  {gate:<16} {metric:<20} {threshold:<12} {action:<8}")

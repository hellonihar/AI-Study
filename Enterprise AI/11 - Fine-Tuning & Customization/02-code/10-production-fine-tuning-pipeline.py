"""
Production fine-tuning pipeline: end-to-end automated workflow with validation, training, and deployment.

Run: python 10-production-fine-tuning-pipeline.py

Requirements: numpy
"""

import numpy as np
import json
import time

print("=== Production Fine-Tuning Pipeline ===\n")

class DataValidator:
    def validate(self, dataset):
        issues = []
        if len(dataset) < 100:
            issues.append(f"too_few_examples ({len(dataset)})")
        for i, ex in enumerate(dataset):
            if len(ex.get("instruction", "")) < 3:
                issues.append(f"short_instruction_at_{i}")
            if len(ex.get("response", "")) < 10:
                issues.append(f"short_response_at_{i}")
        pii_patterns = ["ssn:", "credit card:", "password:"]
        for i, ex in enumerate(dataset):
            text = json.dumps(ex).lower()
            for pattern in pii_patterns:
                if pattern in text:
                    issues.append(f"pii_detected_at_{i}")
                    break
        return {
            "valid": len(issues) == 0,
            "total": len(dataset),
            "issues": issues[:10],
        }

class Trainer:
    def __init__(self, method="lora"):
        self.method = method
        self.history = []

    def train(self, dataset, config):
        start = time.time()
        simulated_epochs = config.get("epochs", 3)
        for epoch in range(simulated_epochs):
            loss = 2.0 * (0.3 ** epoch) + np.random.normal(0, 0.05)
            self.history.append({"epoch": epoch + 1, "loss": float(loss)})
        duration = time.time() - start
        return {
            "method": self.method,
            "epochs": simulated_epochs,
            "final_loss": self.history[-1]["loss"],
            "history": self.history,
            "duration_seconds": round(duration, 2),
        }

class Evaluator:
    def evaluate(self, model_path):
        return {
            "task_accuracy": float(np.random.beta(90, 10)),
            "mmlu_score": float(np.random.beta(68, 32)),
            "hallucination_rate": float(np.random.beta(2, 98)),
            "safety_score": float(np.random.beta(95, 5)),
        }

class ModelRegistry:
    def __init__(self):
        self.models = {}

    def register(self, model_id, metadata):
        self.models[model_id] = {**metadata, "registered_at": time.time()}
        return model_id

    def promote(self, model_id, stage):
        if model_id in self.models:
            self.models[model_id]["stage"] = stage
            return True
        return False

class Deployer:
    def canary_deploy(self, model_id, percentage=5):
        return {"model": model_id, "traffic_percentage": percentage, "status": "deployed"}

    def full_rollout(self, model_id):
        return {"model": model_id, "status": "production"}

def generate_dataset(size=200):
    np.random.seed(42)
    dataset = []
    topics = ["What is {0}?", "Explain {0}.", "How does {0} work?", "Define {0}."]
    concepts = ["fine-tuning", "LoRA", "attention", "transformer", "gradient descent",
                "backpropagation", "embedding", "tokenization", "quantization", "RLHF"]
    for _ in range(size):
        topic = np.random.choice(topics)
        concept = np.random.choice(concepts)
        dataset.append({
            "instruction": topic.format(concept),
            "response": f"{concept} is a key concept in machine learning that involves detailed explanation of its mechanisms and applications."
        })
    return dataset

dataset = generate_dataset(size=200)

print("Phase 1: Data Validation")
validator = DataValidator()
validation = validator.validate(dataset)
print(f"  Dataset size: {validation['total']}")
print(f"  Valid: {validation['valid']}")
if validation["issues"]:
    print(f"  Issues: {validation['issues'][:5]}")

if not validation["valid"]:
    print("  Data validation failed. Aborting.")
    exit(1)

print("\nPhase 2: Training")
trainer = Trainer(method="lora")
config = {
    "epochs": 3,
    "learning_rate": 2e-4,
    "rank": 8,
    "alpha": 16,
    "batch_size": 4,
}
training_result = trainer.train(dataset, config)
print(f"  Method: {training_result['method']}")
print(f"  Epochs: {training_result['epochs']}")
for epoch in training_result["history"]:
    print(f"    Epoch {epoch['epoch']}: loss = {epoch['loss']:.4f}")
print(f"  Duration: {training_result['duration_seconds']:.2f}s")

print("\nPhase 3: Evaluation")
evaluator = Evaluator()
metrics = evaluator.evaluate("model_output/ft-lora-v1")
print(f"  Task accuracy: {metrics['task_accuracy']:.2%}")
print(f"  MMLU: {metrics['mmlu_score']:.2%}")
print(f"  Hallucination rate: {metrics['hallucination_rate']:.2%}")
print(f"  Safety: {metrics['safety_score']:.2%}")

print("\nPhase 4: Model Registry")
registry = ModelRegistry()
model_id = registry.register("ft-llama-3-8b-v1", {
    "base_model": "llama-3-8b",
    "method": "lora",
    "dataset_size": len(dataset),
    "metrics": metrics,
})
print(f"  Registered: {model_id}")

print("\nPhase 5: Canary Deploy")
deployer = Deployer()
canary = deployer.canary_deploy(model_id, percentage=5)
print(f"  Canary: {canary['traffic_percentage']}% traffic")

print("\nPhase 6: Monitoring (simulated 5 minutes)")
monitoring_results = []
for minute in range(1, 6):
    error_rate = np.random.exponential(0.002)
    latency_p95 = np.random.normal(350, 50)
    monitoring_results.append({
        "minute": minute,
        "error_rate": float(error_rate),
        "latency_p95_ms": float(latency_p95),
    })
    print(f"  Minute {minute}: error_rate={error_rate:.3%}, p95_latency={latency_p95:.0f}ms")

avg_error = np.mean([r["error_rate"] for r in monitoring_results])
rollout_ok = avg_error < 0.01

if rollout_ok:
    print(f"\nPhase 7: Full Rollout")
    rollout = deployer.full_rollout(model_id)
    registry.promote(model_id, "production")
    print(f"  Model promoted to production: {model_id}")
else:
    print(f"\nPhase 7: Rollback")
    print(f"  Error rate too high ({avg_error:.3%}). Rolling back.")

print(f"\nPipeline complete. Final model: {model_id} (stage: {registry.models[model_id].get('stage', 'canary')})")

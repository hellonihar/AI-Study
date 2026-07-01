"""
Continuous fine-tuning pipeline: feedback collection, drift detection, and automated retraining.

Run: python 08-continuous-fine-tuning.py

Requirements: numpy
"""

import numpy as np
import json
import time

print("=== Continuous Fine-Tuning Pipeline ===\n")

class ContinuousFineTuner:
    def __init__(self):
        self.feedback_buffer = []
        self.drift_scores = []
        self.training_history = []
        self.performance_metrics = {
            "task_accuracy": 0.92,
            "user_satisfaction": 0.88,
            "hallucination_rate": 0.03,
        }

    def collect_feedback(self, user_rating, response_quality, is_correct):
        self.feedback_buffer.append({
            "rating": user_rating,
            "quality": response_quality,
            "correct": is_correct,
            "timestamp": time.time(),
        })

    def detect_drift(self, input_embeddings):
        mean_embedding = np.mean(input_embeddings, axis=0)
        if self.drift_scores:
            baseline = self.drift_scores[-1]["embedding"]
            drift = float(np.linalg.norm(mean_embedding - baseline))
        else:
            drift = 0.0

        self.drift_scores.append({
            "drift": drift,
            "timestamp": time.time(),
            "embedding": np.mean(input_embeddings, axis=0),
        })
        return drift

    def should_retrain(self, drift_threshold=0.5, quality_threshold=0.80):
        recent_feedback = self.feedback_buffer[-100:] if len(self.feedback_buffer) >= 100 else self.feedback_buffer
        if not recent_feedback:
            return False, "insufficient_data"

        avg_quality = np.mean([f["quality"] for f in recent_feedback])
        avg_rating = np.mean([f["rating"] for f in recent_feedback])
        accuracy = np.mean([f["correct"] for f in recent_feedback])

        reasons = []
        if avg_quality < quality_threshold:
            reasons.append(f"quality_drop ({avg_quality:.2%})")
        if avg_rating < 3.0:
            reasons.append(f"low_rating ({avg_rating:.2f})")
        if accuracy < 0.85:
            reasons.append(f"accuracy_drop ({accuracy:.2%})")

        if self.drift_scores:
            recent_drift = np.mean([s["drift"] for s in self.drift_scores[-5:]])
            if recent_drift > drift_threshold:
                reasons.append(f"drift_detected ({recent_drift:.4f})")

        should = len(reasons) > 0
        return should, reasons if should else "stable"

    def retrain(self):
        recent = self.feedback_buffer[-500:] if len(self.feedback_buffer) >= 500 else self.feedback_buffer
        quality = np.mean([f["quality"] for f in recent])
        accuracy = np.mean([f["correct"] for f in recent])

        self.training_history.append({
            "run": len(self.training_history) + 1,
            "samples": len(recent),
            "quality_before": quality,
            "accuracy_before": accuracy,
        })

        self.performance_metrics["task_accuracy"] = min(1.0, self.performance_metrics["task_accuracy"] + 0.02)
        self.performance_metrics["user_satisfaction"] = min(1.0, self.performance_metrics["user_satisfaction"] + 0.01)
        self.performance_metrics["hallucination_rate"] = max(0.0, self.performance_metrics["hallucination_rate"] - 0.005)

        self.feedback_buffer = []

        return self.training_history[-1]

    def simulate_day(self, day):
        np.random.seed(day)
        for _ in range(np.random.randint(20, 50)):
            rating = np.random.normal(4.0 - day * 0.02, 0.5)
            quality = np.random.beta(20 - day * 0.1, 5)
            correct = np.random.random() > (0.05 + day * 0.005)
            self.collect_feedback(
                user_rating=max(1, min(5, rating)),
                response_quality=quality,
                is_correct=correct,
            )

        emb = np.random.randn(10, 64) * (1 + day * 0.01)
        drift = self.detect_drift(emb)

        should, reason = self.should_retrain(drift_threshold=0.3, quality_threshold=0.82)

        print(f"  Day {day:3d}: drift={drift:.4f}, quality={np.mean([f['quality'] for f in self.feedback_buffer[-20:]]):.2%}, "
              f"retrain={should}", end="")
        if should:
            result = self.retrain()
            print(f" -> retrained (run #{result['run']}, {result['samples']} samples)")
        else:
            print()

ft_pipeline = ContinuousFineTuner()

print("Simulating 30 days of production:")
for day in range(1, 31):
    ft_pipeline.simulate_day(day)

print(f"\nFinal performance:")
for metric, value in ft_pipeline.performance_metrics.items():
    print(f"  {metric:25s}: {value:.2%}")

print(f"\nTraining runs: {len(ft_pipeline.training_history)}")
for run in ft_pipeline.training_history:
    print(f"  Run #{run['run']}: {run['samples']} samples, "
          f"quality={run['quality_before']:.2%}, accuracy={run['accuracy_before']:.2%}")

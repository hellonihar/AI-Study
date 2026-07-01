"""
DPO (Direct Preference Optimization) simulation: preference-based alignment training.

Run: python 05-dpo-simulation.py

Requirements: numpy
"""

import numpy as np

print("=== DPO: Direct Preference Optimization Simulation ===\n")

class DPOModel:
    def __init__(self, n_features=8):
        self.W = np.eye(n_features) * 0.5
        self.n_features = n_features

    def score(self, x):
        return float(np.tanh(np.mean(self.W @ x)))

    def preference_loss(self, x_chosen, x_rejected, beta=0.5):
        c_score = self.score(x_chosen)
        r_score = self.score(x_rejected)
        logits = (c_score - r_score) / beta
        loss = -np.log(1.0 / (1.0 + np.exp(-logits)) + 1e-8)
        return loss, c_score, r_score

    def train_step(self, x_chosen, x_rejected, beta=0.5, lr=0.1):
        loss, c_score, r_score = self.preference_loss(x_chosen, x_rejected, beta)
        grad_factor = (1.0 / (1.0 + np.exp(-(c_score - r_score) / beta))) / beta
        grad_factor *= (1 - np.tanh(np.mean(self.W @ x_chosen))**2)
        self.W += lr * grad_factor * np.outer(x_chosen - x_rejected, np.ones(self.n_features)) / self.n_features
        return loss, c_score, r_score

def make_preference_pair(n_features, seed):
    np.random.seed(seed)
    base = np.random.randn(n_features)
    noise_chosen = np.random.randn(n_features) * 0.1
    noise_rejected = np.random.randn(n_features) * 0.5
    return base + noise_chosen, base + noise_rejected

model = DPOModel(n_features=8)
pairs = [make_preference_pair(8, s) for s in range(50)]

print(f"Model features: {model.n_features}")
print(f"Preference pairs: {len(pairs)}\n")

print("DPO Training:")
for epoch in range(10):
    total_loss = 0.0
    chosen_avg = 0.0
    rejected_avg = 0.0
    for chosen, rejected in pairs:
        loss, c_score, r_score = model.train_step(chosen, rejected, beta=0.5, lr=0.1)
        total_loss += loss
        chosen_avg += c_score
        rejected_avg += r_score
    margin = (chosen_avg - rejected_avg) / len(pairs)
    print(f"  Epoch {epoch+1:2d}: loss={total_loss/len(pairs):.4f}, "
          f"chosen={chosen_avg/len(pairs):.4f}, rejected={rejected_avg/len(pairs):.4f}, "
          f"margin={margin:+.4f}")

test_chosen = np.random.randn(8) * 0.8
test_rejected = np.random.randn(8) * 0.8
_, c_final, r_final = model.preference_loss(test_chosen, test_rejected, beta=0.5)
print(f"\nFinal preference evaluation:")
print(f"  Chosen response score:  {c_final:.4f}")
print(f"  Rejected response score: {r_final:.4f}")
print(f"  Win margin: {c_final - r_final:+.4f}")
print(f"  Model correctly prefers: {'chosen' if c_final > r_final else 'rejected'}")

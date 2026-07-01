"""
Fine-tune an embedding model on domain data with contrastive learning.

Run: python 05-train-embedding-model.py

Requirements: pip install sentence-transformers datasets torch
"""

from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader
import random

# ─── Small domain dataset: tech support Q&A pairs ───
DOMAIN_DATA = [
    ("How do I reset my password?", "You can reset your password by clicking the 'Forgot Password' link."),
    ("My account is locked", "Accounts are locked after 5 failed attempts. Wait 30 minutes or contact support."),
    ("How do I update my billing info?", "Go to Settings > Billing to update payment methods."),
    ("Can I export my data?", "Yes, go to Settings > Export to download your data as CSV or JSON."),
    ("How does the subscription work?", "We offer monthly and annual plans. Annual plans save 20%."),
    ("Is there a mobile app?", "Yes, available on iOS and Android app stores."),
    ("How do I delete my account?", "Go to Settings > Account > Delete Account. This is irreversible."),
    ("What integrations are supported?", "We integrate with Slack, Teams, Jira, and GitHub."),
    ("How do I invite team members?", "Go to Settings > Team > Invite Member. Enter their email."),
    ("What is the uptime SLA?", "We guarantee 99.9% uptime. See our status page for live metrics."),
    ("How do I change notification preferences?", "Go to Settings > Notifications to customize alerts."),
    ("Can I use SSO?", "Yes, we support SAML and OIDC single sign-on."),
    ("How do I revert to a previous version?", "Go to version history > select version > Restore."),
    ("Is there a free trial?", "Yes, 14-day free trial with full access. No credit card needed."),
    ("How do I contact support?", "Email support@example.com or use the chat widget."),
]

# Add negative pairs (random mismatches)
random.seed(42)
NEGATIVES = []
for _ in range(len(DOMAIN_DATA)):
    q, a = random.choice(DOMAIN_DATA)
    _, wrong_a = random.choice(DOMAIN_DATA)
    NEGATIVES.append((q, wrong_a))

# ─── Prepare training data ───
train_examples = []
for (q, pos_a) in DOMAIN_DATA:
    train_examples.append(InputExample(texts=[q, pos_a], label=1.0))
for (q, neg_a) in NEGATIVES:
    train_examples.append(InputExample(texts=[q, neg_a], label=0.0))

random.shuffle(train_examples)

# ─── Load base model ───
print("Loading base model: all-MiniLM-L6-v2...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"Base dims: {model.get_sentence_embedding_dimension()}")

# ─── Create data loader ───
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# ─── Loss function ───
train_loss = losses.ContrastiveLoss(model)

# ─── Evaluate before fine-tuning ───
def evaluate(model, eval_pairs):
    correct = 0
    for q, a, expected_similar in eval_pairs:
        emb = model.encode([q, a])
        emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        sim = float(emb[0] @ emb[1].T)
        if expected_similar and sim > 0.5:
            correct += 1
        elif not expected_similar and sim < 0.5:
            correct += 1
    return correct / len(eval_pairs)

import numpy as np

eval_pairs = [
    ("How do I reset my password?", "Click Forgot Password", True),
    ("How do I reset my password?", "We support SAML SSO", False),
    ("Can I export data?", "Download as CSV", True),
    ("Can I export data?", "Mobile app is available", False),
]

print(f"Before fine-tuning accuracy: {evaluate(model, eval_pairs):.0%}")

# ─── Fine-tune ───
print("\nFine-tuning (5 epochs)...")
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    warmup_steps=5,
    show_progress_bar=True,
    output_path="./fine-tuned-embedding",
)

# ─── Evaluate after ───
print(f"After fine-tuning accuracy: {evaluate(model, eval_pairs):.0%}")
print(f"\nFine-tuned model saved to: ./fine-tuned-embedding")

print("\n=== Key Insight ===")
print("With only 15 domain pairs + 15 negative pairs, we can measurably")
print("improve retrieval relevance on domain-specific queries.")
print("For production, use 1K+ pairs and hard negative mining.")

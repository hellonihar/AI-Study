"""
Model card generator: auto-generate model documentation from metadata.

Run: python 03-model-card-generator.py

Requirements: numpy
"""

import time
import json
import hashlib

print("=== Model Card Generator ===\n")

class ModelCard:
    def __init__(self, metadata):
        self.metadata = metadata
        self.generated = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def generate_section(self, title, content):
        lines = [f"## {title}"]
        if isinstance(content, dict):
            for k, v in content.items():
                lines.append(f"- **{k.replace('_', ' ').title()}**: {v}")
        elif isinstance(content, list):
            for item in content:
                lines.append(f"- {item}")
        else:
            lines.append(f"{content}")
        lines.append("")
        return "\n".join(lines)

    def generate(self):
        sections = []
        sections.append(f"# Model Card: {self.metadata.get('name', 'Unknown')}")
        sections.append(f"**Version**: {self.metadata.get('version', '0.0.0')}")
        sections.append(f"**Generated**: {self.generated}")
        sections.append("")

        sections.append(self.generate_section("Model Details", {
            "name": self.metadata.get("name", ""),
            "version": self.metadata.get("version", ""),
            "type": self.metadata.get("type", ""),
            "developer": self.metadata.get("developer", ""),
            "date": self.metadata.get("date", ""),
            "framework": self.metadata.get("framework", ""),
        }))

        sections.append(self.generate_section("Intended Use", {
            "primary use cases": self.metadata.get("intended_use", ""),
            "out of scope uses": self.metadata.get("out_of_scope", ""),
        }))

        sections.append(self.generate_section("Performance", self.metadata.get("performance", {})))
        sections.append(self.generate_section("Limitations", self.metadata.get("limitations", [])))
        sections.append(self.generate_section("Ethical Considerations", self.metadata.get("ethical_considerations", {})))
        sections.append(self.generate_section("Maintenance", {
            "update frequency": self.metadata.get("update_frequency", ""),
            "owner": self.metadata.get("owner", ""),
        }))

        return "\n".join(sections)

class ModelCardRegistry:
    def __init__(self):
        self.cards = []

    def register(self, metadata):
        card = ModelCard(metadata)
        card_id = hashlib.md5(f"{metadata['name']}{metadata['version']}".encode()).hexdigest()[:12]
        content = card.generate()
        self.cards.append({"id": card_id, "name": metadata["name"], "version": metadata["version"], "content": content})
        return card_id, content

    def get(self, card_id):
        for c in self.cards:
            if c["id"] == card_id:
                return c
        return None

registry = ModelCardRegistry()

SAMPLE_MODELS = [
    {
        "name": "customer-support-classifier",
        "version": "2.1.0",
        "type": "text_classification",
        "developer": "ML Platform Team",
        "date": "2026-07-01",
        "framework": "sentence-transformers + logistic regression",
        "intended_use": "Classify customer support queries into 12 categories (billing, technical, account, etc.)",
        "out_of_scope": "Sentiment analysis, language detection, intent recognition outside support domain",
        "performance": {
            "overall_accuracy": "0.94",
            "precision": "0.93",
            "recall": "0.95",
            "f1_score": "0.94",
        },
        "limitations": [
            "Performance degrades on code-switched languages",
            "Struggles with ambiguous queries that span multiple categories",
            "Trained on English only",
        ],
        "ethical_considerations": {
            "bias_audit": "Conducted 2026-06-15, no significant bias detected across 5 demographic dimensions",
            "data_representation": "Training data balanced across geographic regions",
            "fallback": "Low-confidence predictions (< 0.6) are escalated to human agents",
        },
        "update_frequency": "Monthly retraining",
        "owner": "customer-support-team",
    },
]

for model in SAMPLE_MODELS:
    card_id, content = registry.register(model)
    print(f"  Generated: {model['name']} v{model['version']} (id={card_id})")
    print()
    for line in content.split("\n")[:20]:
        print(f"  {line}")
    print(f"  ... ({len(content.split(chr(10)))} lines total)")
    print()

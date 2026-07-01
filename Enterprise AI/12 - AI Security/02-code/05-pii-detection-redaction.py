"""
PII detection and redaction: detect and mask personally identifiable information.

Run: python 05-pii-detection-redaction.py

Requirements: numpy
"""

import re
import hashlib

print("=== PII Detection & Redaction ===\n")

class PIIDetector:
    def __init__(self):
        self.detectors = {
            "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
            "phone_us": re.compile(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
            "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
            "api_key": re.compile(r"\b(sk-|pk-|api-)[a-zA-Z0-9_-]{16,}\b"),
            "date": re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
        }

    def detect(self, text):
        findings = []
        for pii_type, pattern in self.detectors.items():
            for match in pattern.finditer(text):
                findings.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                })
        return findings

class PIIRedactor:
    def __init__(self):
        self.strategies = {
            "email": "[EMAIL]",
            "phone_us": "[PHONE]",
            "ssn": "[SSN]",
            "credit_card": "[CREDIT_CARD]",
            "ip_address": "[IP_ADDRESS]",
            "api_key": "[API_KEY]",
            "date": "[DATE]",
        }

    def redact(self, text, findings, strategy="mask"):
        if strategy == "mask":
            redacted = text
            for f in sorted(findings, key=lambda x: x["start"], reverse=True):
                replacement = self.strategies.get(f["type"], "[REDACTED]")
                redacted = redacted[:f["start"]] + replacement + redacted[f["end"]:]
            return redacted
        elif strategy == "partial":
            redacted = text
            for f in sorted(findings, key=lambda x: x["start"], reverse=True):
                val = f["value"]
                if len(val) > 4:
                    masked = val[:2] + "*" * (len(val) - 4) + val[-2:]
                else:
                    masked = "[REDACTED]"
                redacted = redacted[:f["start"]] + masked + redacted[f["end"]:]
            return redacted
        return text

class PIIScanner:
    def __init__(self):
        self.detector = PIIDetector()
        self.redactor = PIIRedactor()

    def scan(self, text, strategy="mask"):
        findings = self.detector.detect(text)
        redacted = self.redactor.redact(text, findings, strategy)

        pii_types = {}
        for f in findings:
            pii_types[f["type"]] = pii_types.get(f["type"], 0) + 1

        risk_score = min(1.0, len(findings) * 0.15)
        if "ssn" in pii_types or "credit_card" in pii_types:
            risk_score = max(risk_score, 0.8)

        return {
            "pii_count": len(findings),
            "pii_types": pii_types,
            "risk_score": round(risk_score, 2),
            "redacted_text": redacted,
        }

scanner = PIIScanner()

TEST_TEXTS = [
    "Contact me at john.doe@example.com or call 555-123-4567.",
    "My SSN is 123-45-6789 and my credit card is 4111-1111-1111-1111.",
    "The server IP is 192.168.1.1 and my API key is sk-proj-abc123def456ghi789.",
    "Date of birth: 01/15/1990. Email: jane@company.org Phone: (415) 555-0198.",
    "Machine learning is a subset of artificial intelligence focused on data-driven predictions.",
    "My email is test@example.com, call me at 555-012-3456, SSN: 987-65-4321.",
    "Summary: no PII in this innocent sentence about weather patterns.",
]

print(f"{'PII Count':>9} {'Risk':>6} {'Types':<30} {'Text'}")
print("-" * 80)
for text in TEST_TEXTS:
    result = scanner.scan(text, strategy="mask")
    types_str = ", ".join(f"{k}({v})" for k, v in result["pii_types"].items())
    print(f"{result['pii_count']:>9} {result['risk_score']:.2f}  {types_str:<30} {text[:40]}")

print(f"\nRedaction example (mask strategy):")
sample = TEST_TEXTS[5]
result = scanner.scan(sample, strategy="mask")
print(f"  Original: {sample}")
print(f"  Redacted: {result['redacted_text']}")

print(f"\nRedaction example (partial strategy):")
result_partial = scanner.scan(sample, strategy="partial")
print(f"  Partial:  {result_partial['redacted_text']}")

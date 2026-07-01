"""
PII detection and masking: identify and protect sensitive information in text.

Run: python 03-pii-detection-and-masking.py

Requirements: pip install numpy (optional: presidio-analyzer, spacy)
"""

import re
import hashlib
import json

SAMPLE_DOCUMENTS = [
    {
        "id": "DOC-001",
        "text": "John Smith called about his policy #12345. His email is john.smith@email.com and phone is 555-123-4567.",
    },
    {
        "id": "DOC-002",
        "text": "Patient Jane Doe (SSN: 987-65-4321) was admitted on 2024-11-15 with diagnosis of hypertension. Contact: 555-987-6543.",
    },
    {
        "id": "DOC-003",
        "text": "Quarterly report: Revenue increased 15% YoY. No PII in this document.",
    },
    {
        "id": "DOC-004",
        "text": "Transfer $500 from account 12345678 to account 87654321. Routing: 021000021.",
    },
]

PII_PATTERNS = {
    "EMAIL_ADDRESS": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "US_SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "PHONE_NUMBER": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "US_ROUTING_NUMBER": r"\b\d{9}\b",
}

print("=== PII Detection and Masking ===\n")

def detect_pii(text):
    findings = []
    for pii_type, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, text):
            findings.append({
                "type": pii_type,
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
            })
    return findings

def mask_pii(text, findings, method="redact"):
    if method == "redact":
        result = text
        for f in sorted(findings, key=lambda x: x["start"], reverse=True):
            result = result[:f["start"]] + "[REDACTED]" + result[f["end"]:]
        return result

    elif method == "pseudonymize":
        result = text
        for f in sorted(findings, key=lambda x: x["start"], reverse=True):
            h = hashlib.md5(f["value"].encode()).hexdigest()[:8]
            placeholder = f"[PSEUDO-{h}]"
            result = result[:f["start"]] + placeholder + result[f["end"]:]
        return result

    elif method == "generalize":
        result = text
        for f in sorted(findings, key=lambda x: x["start"], reverse=True):
            pii_type = f["type"]
            value = f["value"]
            if pii_type == "PHONE_NUMBER":
                generalized = value[:4] + "XXX-XXXX"
            elif pii_type == "US_SSN":
                generalized = "XXX-XX-" + value[-4:]
            elif pii_type == "EMAIL_ADDRESS":
                parts = value.split("@")
                generalized = parts[0][0] + "***@" + parts[1]
            elif pii_type == "CREDIT_CARD":
                generalized = "XXXX-XXXX-XXXX-" + value[-4:]
            else:
                generalized = "[REDACTED]"
            result = result[:f["start"]] + generalized + result[f["end"]:]
        return result

    return text

print(f"{'Doc':<10} {'PII Items':<20} {'Detection':<50}")
print("-" * 80)

for doc in SAMPLE_DOCUMENTS:
    findings = detect_pii(doc["text"])
    pii_types = ", ".join(set(f["type"] for f in findings))
    doc_preview = doc["text"][:45] + "..." if len(doc["text"]) > 45 else doc["text"]
    print(f"{doc['id']:<10} {pii_types:<20} {doc_preview:<50}")

print(f"\n{'='*60}")
print("Masking Method Comparison")
print(f"{'='*60}")

doc = SAMPLE_DOCUMENTS[0]
findings = detect_pii(doc["text"])

print(f"\nOriginal:  {doc['text']}")
print(f"Redact:    {mask_pii(doc['text'], findings, 'redact')}")
print(f"Pseudonym: {mask_pii(doc['text'], findings, 'pseudonymize')}")
print(f"General:   {mask_pii(doc['text'], findings, 'generalize')}")

print(f"\n{'='*60}")
print("PII Impact Analysis for RAG Pipeline")
print(f"{'='*60}")

pii_counts = {"EMAIL_ADDRESS": 0, "US_SSN": 0, "PHONE_NUMBER": 0, "CREDIT_CARD": 0, "US_ROUTING_NUMBER": 0}
pii_docs = 0
for doc in SAMPLE_DOCUMENTS:
    findings = detect_pii(doc["text"])
    if findings:
        pii_docs += 1
    for f in findings:
        pii_counts[f["type"]] = pii_counts.get(f["type"], 0) + 1

print(f"\nDocuments with PII: {pii_docs}/{len(SAMPLE_DOCUMENTS)}")
print(f"PII items found:")
for pii_type, count in sorted(pii_counts.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"  {pii_type}: {count}")

print(f"\n{'='*60}")
print("PII Handling Recommendations")
print(f"{'='*60}")
print("1. Detect PII BEFORE ingestion into the vector DB")
print("2. Use 'generalize' for RAG (preserves utility, protects privacy)")
print("3. Use 'redact' for high-sensitivity data (SSN, credit cards)")
print("4. Store PII detection results as metadata for audit trail")
print("5. Never embed raw PII — once embedded, vectors cannot be 'unlearned'")
print("6. For production, use Presidio (ML-based) instead of regex-only")

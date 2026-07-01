"""
Data quality pipeline: validation, deduplication, anomaly detection.

Run: python 01-data-quality-pipeline.py

Requirements: pip install numpy
"""

import hashlib
import json
import numpy as np

SAMPLE_RECORDS = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@co.com", "text": "Product return policy for electronics."},
    {"id": 2, "name": "Bob Smith", "email": "bob@co.com", "text": "Shipping times for international orders."},
    {"id": 3, "name": "Alice Johnson", "email": "alice@co.com", "text": "Product return policy for electronics."},
    {"id": 4, "name": "", "email": "charlie@co.com", "text": ""},
    {"id": 5, "name": None, "email": None, "text": "Warranty information for kitchen appliances."},
    {"id": 6, "name": "Eve Adams", "email": "eve@co.com", "text": "A" * 100001},
    {"id": 7, "name": "Frank Lee", "email": "frank@co.com", "text": "Payment methods accepted on our platform include credit cards, PayPal, and bank transfers."},
    {"id": 8, "name": "Grace Wang", "email": "grace@co.com", "text": "Payment methods accepted on our platform include credit cards, PayPal, and bank transfers."},
]

print("=== Data Quality Pipeline ===\n")

def check_completeness(record, required_fields):
    issues = []
    for field in required_fields:
        value = record.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            issues.append(f"MISSING_{field.upper()}")
    return issues

def check_text_quality(record):
    issues = []
    text = record.get("text", "")
    if not text:
        issues.append("EMPTY_TEXT")
    elif len(text) < 10:
        issues.append("TOO_SHORT")
    elif len(text) > 100000:
        issues.append("TOO_LONG")
    return issues

def check_encoding(text):
    try:
        text.encode("utf-8")
        return []
    except UnicodeEncodeError:
        return ["ENCODING_ERROR"]

def exact_dedup(records):
    seen = set()
    unique = []
    for r in records:
        h = hashlib.sha256(
            json.dumps(r, sort_keys=True).encode()
        ).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(r)
        else:
            r["_duplicate"] = True
    return unique

def near_dedup_text(records, similarity_threshold=0.85):
    from collections import Counter

    def word_overlap(a, b):
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0
        intersection = words_a & words_b
        return len(intersection) / max(len(words_a), len(words_b))

    unique = []
    seen_texts = []
    for r in records:
        text = r.get("text", "")
        is_dup = False
        for seen in seen_texts:
            if word_overlap(text, seen) > similarity_threshold:
                is_dup = True
                r["_near_duplicate"] = True
                break
        if not is_dup:
            unique.append(r)
            seen_texts.append(text)
    return unique

def detect_outliers(records, field="text", z_threshold=3):
    lengths = [len(r.get(field, "")) for r in records if r.get(field)]
    if not lengths:
        return []
    mean = np.mean(lengths)
    std = np.std(lengths)
    anomalies = []
    for r in records:
        length = len(r.get(field, ""))
        if std > 0:
            z = (length - mean) / std
            if abs(z) > z_threshold:
                anomalies.append({"record": r, "metric": "text_length", "z_score": z})
    return anomalies

REQUIRED_FIELDS = ["id", "name", "email", "text"]

completed = 0
failed = 0

print(f"{'ID':<5} {'Checks':<50} {'Status'}")
print("-" * 65)

for record in SAMPLE_RECORDS:
    all_issues = []
    all_issues.extend(check_completeness(record, REQUIRED_FIELDS))
    all_issues.extend(check_text_quality(record))
    if record.get("text"):
        all_issues.extend(check_encoding(record["text"]))

    status = "PASS" if not all_issues else "FAIL"
    if not all_issues:
        completed += 1
    else:
        failed += 1

    issues_str = ", ".join(all_issues) if all_issues else "all checks passed"
    print(f"{record['id']:<5} {issues_str:<50} {status}")

print(f"\nQuality summary: {completed} passed, {failed} failed\n")

print("=" * 50)
print("2. Deduplication")
print("=" * 50)

unique = exact_dedup(SAMPLE_RECORDS)
dupes = len(SAMPLE_RECORDS) - len(unique)
print(f"Exact duplicates removed: {dupes}")

near_unique = near_dedup_text(unique)
near_dupes = len(unique) - len(near_unique)
print(f"Near-duplicates removed:  {near_dupes}")
print(f"Final unique records:     {len(near_unique)}")

print("\n" + "=" * 50)
print("3. Anomaly Detection")
print("=" * 50)

anomalies = detect_outliers(SAMPLE_RECORDS)
print(f"Anomalies detected: {len(anomalies)}")
for a in anomalies:
    r = a["record"]
    print(f"  ID={r['id']}: text_length={len(r.get('text',''))} "
          f"(z_score={a['z_score']:.2f})")

print("\n" + "=" * 50)
print("4. Quality Report Summary")
print("=" * 50)
print(f"Total records:        {len(SAMPLE_RECORDS)}")
print(f"Quality pass rate:    {completed}/{len(SAMPLE_RECORDS)} "
      f"({completed/len(SAMPLE_RECORDS)*100:.0f}%)")
print(f"Exact dupe rate:      {dupes}/{len(SAMPLE_RECORDS)} "
      f"({dupes/len(SAMPLE_RECORDS)*100:.0f}%)")
print(f"Near-dupe rate:       {near_dupes}/{len(unique)} "
      f"({near_dupes/len(unique)*100:.0f}%)")
print(f"Anomaly rate:         {len(anomalies)}/{len(SAMPLE_RECORDS)} "
      f"({len(anomalies)/len(SAMPLE_RECORDS)*100:.0f}%)")
print()
print("Recommendation: Implement Great Expectations or SODA for")
print("production monitoring of these quality metrics.")

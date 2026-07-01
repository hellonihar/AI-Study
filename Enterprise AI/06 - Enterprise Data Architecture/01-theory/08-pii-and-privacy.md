# PII Identification and Privacy

Detecting, protecting, and managing personally identifiable information in AI data pipelines.

## PII Categories

| Category | Examples | Sensitivity | Regulation |
|---|---|---|---|
| **Direct identifiers** | Name, SSN, email, phone, address | High | GDPR, CCPA, HIPAA |
| **Indirect identifiers** | DOB, ZIP code, gender, ethnicity | Medium | GDPR, CCPA |
| **Financial** | Credit card, bank account, income | High | PCI-DSS, GDPR |
| **Health** | Medical records, diagnosis, prescriptions | Very high | HIPAA, GDPR |
| **Biometric** | Fingerprint, face scan, voice print | Very high | GDPR, BIPA |
| **Behavioral** | Browsing history, purchase history | Medium | GDPR, CCPA |
| **Credentials** | Password, security questions | Critical | Internal policy |

## PII Detection

### Rule-Based Detection

```python
import re

PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "ssn": r"\d{3}-\d{2}-\d{4}",
    "phone_us": r"(\+1)?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}

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
```

### ML-Based Detection (Presidio)

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(
    text="My email is john.doe@acmecorp.com and my SSN is 123-45-6789.",
    entities=["EMAIL_ADDRESS", "US_SSN", "PHONE_NUMBER", "CREDIT_CARD"],
    language="en",
)

for r in results:
    print(f"Entity: {r.entity_type}, Score: {r.score:.2f}, "
          f"Text: '{text[r.start:r.end]}'")
```

Presidio achieves 85-95% precision on common PII types with pre-built recognizers.

### Named Entity Recognition

```python
import spacy
nlp = spacy.load("en_core_web_lg")

doc = nlp("John Smith from San Francisco called about policy #12345.")
for ent in doc.ents:
    print(f"{ent.text}: {ent.label_}")
    # PERSON: John Smith
    # GPE: San Francisco
```

## PII Masking Techniques

### 1. Redaction

```python
def redact_pii(text, findings):
    result = text
    for f in sorted(findings, key=lambda x: x["start"], reverse=True):
        result = result[:f["start"]] + "[REDACTED]" + result[f["end"]:]
    return result
```

### 2. Pseudonymization

```python
import hashlib

def pseudonymize(value, salt="pipeline-secret-salt"):
    hash_input = f"{value}:{salt}"
    return f"ANON-{hashlib.sha256(hash_input.encode()).hexdigest()[:16]}"

# John Smith → ANON-a1b2c3d4e5f6g7h8
```

### 3. Generalization

```python
def generalize_dob(dob):
    if isinstance(dob, str):
        dob = datetime.strptime(dob, "%Y-%m-%d")
    # Keep only year and month
    return dob.strftime("%Y-%m") + "-XX"

def generalize_zip(zip_code):
    return zip_code[:3] + "XX"  # 94105 → 941XX
```

### 4. Synthetic Replacement (Faker)

```python
from faker import Faker
fake = Faker()

def anonymize_person(name):
    return fake.name()
```

## PII in the RAG Pipeline

PII can enter RAG systems through ingested documents:

```
Source Document (contains "John Smith, john@co.com")
    │
    ▼
Chunking → Chunk contains PII
    │
    ▼
Embedding → Vector encodes PII (no way to "unlearn" it)
    │
    ▼
Vector DB → PII stored in payload/metadata
    │
    ▼
Retrieval → PII returned in context
    │
    ▼
Generation → PII surfaces in LLM response
```

### Mitigation Points

| Stage | Action | Effective? |
|---|---|---|
| Before ingestion | Detect + mask/redact PII | ✅ Most effective |
| Before embedding | PII-free embedding input | ✅ Next best |
| Before vector DB | Strip PII from metadata | ✅ Necessary |
| Before generation | Filter PII from context | ⚠️ Last resort |
| After generation | Scan output for PII | ⚠️ Reactive |

## Data Retention Policies

```yaml
retention_policy:
  raw_documents:
    retention: "90 days"
    action: "delete from S3"
    exception: "Legal hold (litigation hold)"

  embeddings:
    retention: "permanent"
    note: "Embeddings contain no raw PII if masked before embedding"

  query_logs:
    retention: "30 days"
    action: "anonymize after 30d, delete after 90d"

  audit_logs:
    retention: "7 years"
    action: "archive to Glacier"
```

## Privacy by Design Principles

1. **Data minimization** — only ingest fields needed for the AI use case. If email isn't needed for RAG, don't index it.
2. **Mask at source** — apply PII masking as close to the source as possible (ideally before the data leaves the source system).
3. **Embedding = permanent** — once PII is embedded into a vector, it cannot be removed. Mask before embedding.
4. **Access control** — vector DB access should be per-tenant. A user should never retrieve another user's documents.
5. **Audit trail** — every access to PII-adjacent data should be logged with user, timestamp, and reason.

## Compliance by Region

| Regulation | Key Requirements | Impact on RAG Systems |
|---|---|---|
| **GDPR** (EU) | Right to deletion, data portability | Must be able to delete all vectors for a user |
| **CCPA** (California) | Right to know, opt-out of sale | Must track data origin for disclosure |
| **HIPAA** (US healthcare) | PHI protection, BAAs | Full encryption, access logging, audit |
| **LGPD** (Brazil) | Similar to GDPR | Deletion capability, consent tracking |
| **PIPEDA** (Canada) | Consent, purpose limitation | Document purpose for each data collection |

## Implementing Right to be Forgotten

```python
def delete_user_data(user_id, vector_db, data_lake):
    # 1. Delete from vector DB (point delete)
    vector_db.delete(filter={"user_id": user_id})

    # 2. Delete from data lake
    data_lake.delete(prefix=f"users/{user_id}/")

    # 3. Delete from cache
    cache.delete_pattern(f"user:{user_id}:*")

    # 4. Log the deletion
    audit_log("USER_DATA_DELETED", user_id=user_id)
```

**Challenge:** Embedding vectors cannot be "unlearned" without re-indexing. If user data was embedded before deletion, the vectors may still retrieve similar content. The mitigation is to store `user_id` as a filterable metadata field and exclude deleted users' vectors at query time.

## Tools

| Tool | Purpose |
|---|---|
| **Microsoft Presidio** | PII detection and anonymization |
| **Apache Tika** | Content detection + PII patterns |
| **spaCy** | NER for PII detection |
| **Faker** | Synthetic data generation for masking |
| **AWS Macie** | Automated PII detection in S3 |
| **Google DLP** | Cloud-based PII detection and de-identification |
| **Tonic.ai** | Enterprise data anonymization |

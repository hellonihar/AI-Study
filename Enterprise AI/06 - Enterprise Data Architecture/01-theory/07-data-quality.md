# Data Quality for AI

Ensuring clean, consistent data for embedding, retrieval, and training.

## Why Data Quality Matters for AI

| Quality Issue | Impact on RAG | Impact on ML Training |
|---|---|---|
| Duplicate documents | Biased retrieval, wasted context | Overfitting to duplicates |
| Missing fields | Incomplete context, worse retrieval | Feature gaps |
| Inconsistent formatting | Embedding drift (same meaning, different vector) | Training instability |
| Outdated information | Stale answers | Label misalignment |
| Gibberish/noise | Retrieval pollution | Training data contamination |
| PII leakage | Compliance violation | Privacy breach |

## Data Quality Dimensions

| Dimension | Definition | AI Impact | Target |
|---|---|---|---|
| **Completeness** | All required fields present | Context completeness | > 99% |
| **Uniqueness** | No duplicate documents | Retrieval diversity | > 99.9% |
| **Consistency** | Same format across sources | Stable embeddings | > 98% |
| **Timeliness** | Data is current | Answer freshness | Per SLA |
| **Accuracy** | Data reflects reality | Answer correctness | > 95% |
| **Validity** | Data conforms to schema | Pipeline stability | > 99.5% |

## Quality Checks by Pipeline Stage

### Ingestion Stage

```python
# Ingestion quality checks
def check_ingestion_quality(record):
    issues = []

    if not record.get("text"):
        issues.append("EMPTY_TEXT")
    if len(record.get("text", "")) < 10:
        issues.append("TOO_SHORT")
    if len(record.get("text", "")) > 100000:
        issues.append("TOO_LONG")

    if record.get("file_size", 0) == 0:
        issues.append("EMPTY_FILE")

    # Encoding check
    try:
        record["text"].encode("utf-8")
    except UnicodeEncodeError:
        issues.append("ENCODING_ERROR")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "record_id": record.get("doc_id"),
    }
```

### Transformation Stage

```python
def check_transform_quality(record):
    issues = []

    # Embedding input quality
    input_text = record.get("embedding_input", "")
    if not input_text:
        issues.append("EMPTY_EMBEDDING_INPUT")
    if len(input_text.split()) < 3:
        issues.append("TOO_FEW_TOKENS")
    if input_text.count("{{") > 0:  # unrendered template variables
        issues.append("UNRENDERED_TEMPLATE")
    if input_text == input_text.upper() and len(input_text) > 50:
        issues.append("POSSIBLE_MACHINE_TEXT")  # all caps

    return issues
```

### Embedding Stage

```python
def check_embedding_quality(embedding, metadata):
    issues = []
    embedding = np.array(embedding)

    # Zero vector → failure
    if np.all(embedding == 0):
        issues.append("ZERO_VECTOR")

    # NaN in embedding → failure
    if np.any(np.isnan(embedding)):
        issues.append("NAN_EMBEDDING")

    # Check normalization
    norm = np.linalg.norm(embedding)
    if not np.isclose(norm, 1.0, atol=0.01):
        issues.append(f"NORMALIZATION_ERROR: norm={norm:.4f}")

    return issues
```

## Deduplication Strategies

### Exact Dedup (Content Hash)

```python
def exact_dedup(chunks):
    seen_hashes = set()
    unique_chunks = []
    for chunk in chunks:
        h = hashlib.sha256(chunk["text"].encode()).hexdigest()
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique_chunks.append(chunk)
    return unique_chunks
```

### Near-Dedup (MinHash/LSH)

For documents that are 90%+ similar but not identical:

```python
def near_dedup(chunks, threshold=0.9):
    # MinHash LSH for Jaccard similarity
    # Group chunks with similarity > threshold
    # Keep one representative from each group
    pass  # Use datasketch or similar library
```

### Semantic Dedup (Embedding-Based)

For documents with different wording but same meaning:

```python
def semantic_dedup(chunks, embedding_model, threshold=0.98):
    texts = [c["text"] for c in chunks]
    embeddings = embedding_model.encode(texts)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1)

    clusters = []
    assigned = set()
    for i in range(len(texts)):
        if i in assigned:
            continue
        cluster = [i]
        for j in range(i + 1, len(texts)):
            if j in assigned:
                continue
            sim = embeddings[i] @ embeddings[j]
            if sim > threshold:
                cluster.append(j)
                assigned.add(j)
        clusters.append(cluster)
        assigned.add(i)

    return [chunks[c[0]] for c in clusters]
```

## Anomaly Detection in Data Pipelines

### Volume Anomalies

```python
def detect_volume_anomaly(current_count, historical_counts, z_threshold=3):
    mean = np.mean(historical_counts)
    std = np.std(historical_counts)
    z_score = (current_count - mean) / std if std > 0 else 0
    return {
        "anomaly": abs(z_score) > z_threshold,
        "z_score": z_score,
        "direction": "up" if z_score > 0 else "down",
    }
```

### Content Anomalies

```python
def detect_content_anomaly(records):
    avg_lengths = [len(r.get("text", "")) for r in records]
    avg_length = np.mean(avg_lengths)
    std_length = np.std(avg_lengths)

    anomalies = []
    for r in records:
        length = len(r.get("text", ""))
        z = (length - avg_length) / std_length if std_length > 0 else 0
        if abs(z) > 3:
            anomalies.append({
                "id": r.get("doc_id"),
                "issue": "CONTENT_LENGTH_ANOMALY",
                "value": length,
                "z_score": z,
            })
    return anomalies
```

## Quality Monitoring Dashboard

```yaml
quality_dashboard:
  ingestion:
    - metric: "total_documents"
      target: "50000/day"
    - metric: "parse_failure_rate"
      target: "< 2%"
    - metric: "empty_text_rate"
      target: "< 0.5%"
    - metric: "encoding_error_rate"
      target: "< 1%"

  transformation:
    - metric: "embedding_input_quality"
      target: "> 99% pass"
    - metric: "unrendered_template_rate"
      target: "< 0.1%"
    - metric: "schema_compliance"
      target: "100%"

  embedding:
    - metric: "zero_vector_rate"
      target: "0%"
    - metric: "nan_rate"
      target: "0%"
    - metric: "avg_norm"
      target: "1.0 ± 0.01"
    - metric: "avg_embedding_magnitude"
      target: "baseline ± 10%"

  deduplication:
    - metric: "duplicate_rate"
      target: "< 5% (exact)"
    - metric: "near_duplicate_rate"
      target: "< 2% (cosine > 0.95)"
```

## Quality Gates

```yaml
quality_gates:
  ingestion:
    - condition: "parse_failure_rate > 5%"
      action: "STOP pipeline, alert #data-quality"
    - condition: "empty_text_rate > 2%"
      action: "PAUSE, investigate source"
  
  embedding:
    - condition: "zero_vector_rate > 0.1%"
      action: "STOP embedding, check model"
    - condition: "avg_norm < 0.99 or avg_norm > 1.01"
      action: "ALERT, check normalization"
  
  vector_db:
    - condition: "duplicate_rate > 10%"
      action: "ALERT, run dedup pipeline"
    - condition: "avg_similarity_drop > 0.1"
      action: "STOP, investigate embedding drift"
```

## Tools

| Tool | Type | Best For |
|---|---|---|
| **Great Expectations** | Expectations | Declarative quality checks |
| **Deequ** (AWS) | Apache Spark | Large-scale quality on Spark |
| **SODA** | Monitoring | Continuous quality monitoring |
| **dbt tests** | SQL | Warehouse quality |
| **datasketch** | MinHash LSH | Near-dedup at scale |
| **presidio** | PII detection | Sensitive data detection |

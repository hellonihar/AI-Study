# AI Guardrails — Design Document

## Overview

A policy enforcement layer for LLM inputs and outputs: PII redaction, toxicity filtering, topic restrictions, output validation, and compliance workflows (GDPR, HIPAA, SOC 2). This project demonstrates how governance experience — policy definition, compliance auditing, access control, risk assessment — transfers directly to AI safety engineering.

---

## Architecture

```
                    ┌───────────────────────────────────────────┐
                    │              Client Application            │
                    │        (user query, LLM response)          │
                    └──────────────────┬────────────────────────┘
                                       │
                                       ▼
              ┌────────────────────────────────────────────────┐
              │           Guardrail Middleware Layer            │
              │  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
              │  │  Input   │  │  Policy  │  │   Output     │ │
              │  │Guardrails│──►  Engine  │──►│ Guardrails   │ │
              │  │ (pre-LLM)│  │ (router) │  │ (post-LLM)   │ │
              │  └──────────┘  └────┬─────┘  └──────────────┘ │
              │                     │                          │
              │  ┌──────────────────▼──────────────────────┐   │
              │  │          Guardrail Pipeline Builder       │   │
              │  │  (compose guardrails from registry)       │   │
              │  └──────────────────┬──────────────────────┘   │
              └─────────────────────┼──────────────────────────┘
                                    │
              ┌─────────────────────┼──────────────────────────┐
              │                     │                          │
              │  ┌──────────────────▼──────────────────────┐   │
              │  │              LLM Call                    │   │
              │  │  (only reached if all input guards pass) │   │
              │  └─────────────────────────────────────────┘   │
              │                                                │
              └────────────────────────────────────────────────┘
                                    │
                                    ▼
              ┌────────────────────────────────────────────────┐
              │        Audit Trail & Compliance Logger          │
              │  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
              │  │  Events  │  │ Evidence │  │  Reports     │ │
              │  │ (JSONL)  │  │  Store   │  │ (PDF/HTML)   │ │
              │  └──────────┘  └──────────┘  └──────────────┘ │
              └────────────────────────────────────────────────┘

Guardrail Flow (per request):

  User Input
      │
      ▼
  ┌─────────────────┐   BLOCK    ┌──────────────┐
  │ PII Scanner     │──────────► │ 4xx Response  │
  │ (credit cards,  │            │ (violation    │
  │  SSN, emails)   │            │  details)     │
  └────────┬────────┘            └──────────────┘
           │ PASS
           ▼
  ┌─────────────────┐   BLOCK    ┌──────────────┐
  │ Toxicity Filter │──────────► │ Blocked      │
  │ (hate, violence,│            │ Response     │
  │  harassment)    │            │              │
  └────────┬────────┘            └──────────────┘
           │ PASS
           ▼
  ┌─────────────────┐   BLOCK    ┌──────────────┐
  │ Topic Checker   │──────────► │ Blocked      │
  │ (allow/deny     │            │ Response     │
  │  topic lists)   │            │              │
  └────────┬────────┘            └──────────────┘
           │ PASS
           ▼
      ┌─────────┐
      │ LLM Call│
      └────┬────┘
           ▼
  ┌─────────────────┐   BLOCK    ┌──────────────┐
  │ PII Scanner     │──────────► │ Redact /      │
  │ (output)        │            │ Block Output  │
  └────────┬────────┘            └──────────────┘
           │ PASS
           ▼
  ┌─────────────────┐   BLOCK    ┌──────────────┐
  │ Toxicity Filter │──────────► │ Block Output  │
  │ (output)        │            │               │
  └────────┬────────┘            └──────────────┘
           │ PASS
           ▼
  ┌─────────────────┐   FLAG     ┌──────────────┐
  │ Factual Check   │──────────► │ Warning in   │
  │ (consistency    │            │ Response     │
  │  with context)  │            │ Header       │
  └────────┬────────┘            └──────────────┘
           │ PASS
           ▼
      Clean Response → Client
```

---

## Project Structure

```
projects/ai-guardrails/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Settings via pydantic-settings
│   ├── schemas.py                   # Pydantic models for guardrail config, events, violations
│   │
│   ├── guards/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract BaseGuard class
│   │   ├── registry.py              # Guardrail registry (lookup by name)
│   │   ├── pii_scanner.py           # PII detection and redaction
│   │   ├── toxicity_filter.py       # Toxicity classification
│   │   ├── topic_checker.py         # Allow/deny topic matching
│   │   ├── output_validator.py      # Format + factual consistency checks
│   │   ├── prompt_injection.py      # Prompt injection detection
│   │   └── rate_limiter.py          # Per-user/per-IP rate limiting
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── builder.py               # Compose guardrails into ordered pipeline
│   │   ├── executor.py              # Execute pipeline: evaluate + decide
│   │   └── middleware.py             # ASGI middleware for FastAPI integration
│   │
│   ├── detectors/
│   │   ├── __init__.py
│   │   ├── pii_patterns.py          # Regex patterns for PII (CC, SSN, email, phone, etc.)
│   │   ├── pii_ner.py               # NER-based PII detection (spaCy / GLiNER)
│   │   ├── toxicity_classifier.py   # Model-based toxicity detection
│   │   └── topic_classifier.py      # Zero-shot topic classification
│   │
│   ├── compliance/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract compliance framework
│   │   ├── gdpr.py                  # GDPR rules: right to erasure, data minimization
│   │   ├── hipaa.py                 # HIPAA rules: PHI detection, access logging
│   │   ├── soc2.py                  # SOC 2 rules: audit trails, access controls
│   │   └── policy.py                # Custom policy DSL
│   │
│   ├── audit/
│   │   ├── __init__.py
│   │   ├── logger.py                # Structured audit event logging
│   │   ├── store.py                 # Audit log storage (file, DB, S3)
│   │   └── reporter.py              # Compliance report generation (PDF/HTML)
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py                # FastAPI routes (check, chat, config, audit)
│       └── dependencies.py          # Shared dependencies
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_pii_scanner.py
│   ├── test_toxicity_filter.py
│   ├── test_topic_checker.py
│   ├── test_pipeline.py
│   └── test_compliance.py
│
├── data/
│   └── sample_policies/             # Example policy YAML files
│       ├── gdpr_strict.yaml
│       ├── hipaa_standard.yaml
│       └── custom_soc2.yaml
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Guardrail Types

| Guard | Direction | Method | Action | Latency |
|---|---|---|---|---|
| **PII Scanner** | Input & Output | Regex + NER model | Redact or block | ~10ms (regex), ~100ms (NER) |
| **Toxicity Filter** | Input & Output | Classifier model | Block with reason | ~50ms |
| **Topic Checker** | Input | Zero-shot classifier | Block if denied topic | ~100ms |
| **Output Validator** | Output | LLM-as-judge + schema check | Flag or block | ~500ms |
| **Prompt Injection** | Input | Classifier + heuristics | Block | ~50ms |
| **Rate Limiter** | Input | Sliding window counter | 429 response | ~1ms |

### PII Scanner

```
PII Scanner
  │
  ├── Stage 1: Regex matching (fast, high precision)
  │     Patterns:
  │       - Credit card: \b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b
  │       - SSN: \b\d{3}-\d{2}-\d{4}\b
  │       - Email: \b[\w.-]+@[\w.-]+\.\w+\b
  │       - Phone: \b\+?\d{1,3}[-.]?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b
  │       - IP Address: \b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b
  │
  ├── Stage 2: NER model (spaCy / GLiNER)
  │     Entities: PERSON, ORG, GPE, DATE, MONEY, EMAIL, PHONE
  │     - Spans are classified by entity type
  │     - Confidence threshold configurable (default: 0.85)
  │
  └── Stage 3: Redaction strategies
        ┌───────────────┬──────────────────────────────┐
        │ Strategy      │ Behavior                     │
        ├───────────────┼──────────────────────────────┤
        │ mask          │ Replace with [REDACTED]      │
        │ mask_preserve │ Replace but keep type:       │
        │ _type         │ [CREDIT_CARD], [SSN], [EMAIL]│
        │ hash          │ Replace with SHA-256 hash    │
        │ block         │ Reject the request entirely  │
        └───────────────┴──────────────────────────────┘
```

### Toxicity Filter

| Category | Example | Model Threshold |
|---|---|---|
| Hate speech | "I hate all..." | > 0.7 |
| Violence | "I will hurt..." | > 0.6 |
| Harassment | "You are stupid" | > 0.75 |
| Self-harm | "I want to die" | > 0.5 |
| Sexual content | Explicit descriptions | > 0.8 |

Uses Detoxify (`unitary/toxic-bert`) for initial classification. For higher accuracy, an LLM-as-judge call is used as a second pass on borderline cases (score 0.4–0.7).

### Topic Checker

```yaml
# Example topic policy
topics:
  allowed:
    - customer-support
    - product-information
    - technical-documentation
  denied:
    - medical-advice
    - legal-advice
    - financial-investment
    - politics
  default_action: deny  # What happens if topic is unrecognized
```

Topic classification uses zero-shot classification with a lightweight model (`BART-large-mnli` or `distilbart-mnli`). Unrecognized topics follow the `default_action` setting.

### Output Validator

| Check | Method | Action |
|---|---|---|
| **Format compliance** | Schema validation (JSON, XML, Markdown) | Block if malformed |
| **Factual consistency** | LLM-as-judge: claims vs. input context | Flag with warning |
| **Citation validation** | Verify cited sources exist in context | Block hallucinated citations |
| **Length bounds** | Token count: min/max | Truncate or block |
| **Language consistency** | Detect language of output vs. input | Flag if mismatched |

### Prompt Injection Detection

```python
class PromptInjectionDetector:
    def __init__(self):
        self.heuristics = [
            r"(?i)(ignore|forget|disregard).*(previous|above|instructions)",
            r"(?i)(you are now|act as|pretend to be)",
            r"(?i)(system prompt|system message|your instructions)",
            r"(?i)(DAN|do anything now|jailbreak)",
            r"(?i)output.*in.*format.*without.*restrictions",
        ]
        self.classifier = load_model("protectai/deberta-v3-base-prompt-injection")

    async def check(self, text: str) -> DetectionResult:
        heuristic_matches = [p for p in self.heuristics if re.search(p, text)]
        classifier_score = await self.classifier.predict(text)
        return DetectionResult(
            is_injection=len(heuristic_matches) > 0 or classifier_score > 0.5,
            heuristic_matches=heuristic_matches,
            classifier_score=classifier_score,
        )
```

---

## Pipeline

### Pipeline Builder

Guardrails are composed as an ordered pipeline from configuration:

```python
pipeline = (
    PipelineBuilder()
    .add_guard("pii_scanner", direction="input", action="block")
    .add_guard("prompt_injection", direction="input", action="block")
    .add_guard("toxicity_filter", direction="input", action="block")
    .add_guard("topic_checker", direction="input", action="block")
    .add_guard("pii_scanner", direction="output", action="redact")
    .add_guard("toxicity_filter", direction="output", action="block")
    .add_guard("output_validator", direction="output", action="flag")
    .build()
)
```

### Execution

```python
async def execute_pipeline(
    pipeline: list[Guard],
    request: GuardrailRequest,
) -> GuardrailResult:
    context = PipelineContext(request)
    for guard in pipeline:
        result = await guard.evaluate(request, context)
        context.add_result(guard.name, result)
        if result.action == "block":
            return GuardrailResult(
                passed=False,
                blocked_by=guard.name,
                reason=result.reason,
                context=context,
            )
        if result.action == "redact":
            request = result.redacted_request  # Continue with redacted version
    return GuardrailResult(passed=True, context=context)
```

### Middleware

FastAPI middleware that wraps any LLM endpoint:

```python
@app.post("/api/v1/chat")
async def chat_with_guardrails(request: ChatRequest):
    # Input guardrails run before LLM call
    input_result = await guardrails.execute(request.input, phase="input")
    if not input_result.passed:
        raise HTTPException(status_code=403, detail=input_result.reason)

    # LLM call (only if input guards pass)
    response = await llm.generate(request.input, context=input_result.context)

    # Output guardrails run after LLM call
    output_result = await guardrails.execute(response, phase="output")
    if output_result.action == "block":
        raise HTTPException(status_code=403, detail=output_result.reason)

    return ChatResponse(
        content=output_result.redacted_content if output_result.action == "redact" else response,
        warnings=output_result.warnings,
    )
```

---

## Compliance Workflows

### GDPR

```yaml
# data/policies/gdpr_strict.yaml
compliance_framework: gdpr
rules:
  - name: pii_detection
    guard: pii_scanner
    action: block
    categories: [email, phone, address, credit_card]
    note: "Article 5(1)(c) — data minimization"

  - name: data_minimization
    guard: pii_scanner
    action: redact
    strategy: mask_type
    note: "Store only necessary attributes"

  - name: right_to_erasure
    guard: custom
    endpoint: /api/v1/compliance/forget
    description: "Delete all stored conversation history for a user"
    retention_days: 30

  - name: consent_check
    guard: topic_checker
    action: block
    denied_topics: [data-processing-without-consent]
    note: "Article 7 — consent must be explicit"

  - name: audit_logging
    guard: audit.logger
    events: [check, block, redact, pass]
    retention_days: 365
    note: "Article 30 — records of processing activities"
```

### HIPAA

```yaml
# data/policies/hipaa_standard.yaml
compliance_framework: hipaa
rules:
  - name: phi_detection
    guard: pii_scanner
    action: block
    categories: [ssn, mrn, patient_name, date_of_birth, medical_record]
    note: "HIPAA Privacy Rule — 18 PHI identifiers"

  - name: access_logging
    guard: audit.logger
    events: [all]
    include_user_id: true
    include_timestamp: true
    note: "HIPAA Audit Control — track all PHI access"

  - name: transmission_security
    guard: output_validator
    check: no_phi_in_output
    note: "HIPAA Security Rule — encrypted transmission"

  - name: minimum_necessary
    guard: pii_scanner
    action: redact
    strategy: mask
    note: "Only minimum necessary PHI should be accessible"
```

### SOC 2

```yaml
# data/policies/soc2_custom.yaml
compliance_framework: soc2
rules:
  - name: access_controls
    guard: rate_limiter
    max_requests_per_user: 1000
    window_minutes: 60
    note: "CC6.1 — logical access controls"

  - name: monitoring
    guard: audit.logger
    events: [all]
    export_format: json
    note: "CC7.2 — monitor system for anomalies"

  - name: change_management
    guard: output_validator
    check: version_consistency
    note: "CC8.1 — changes are authorized and tested"

  - name: availability
    guard: rate_limiter
    action: throttle
    note: "A1.2 — capacity management"
```

---

## API

### `POST /api/v1/guard/check`

Evaluate a single input or output against guardrails without calling an LLM.

**Request:**
```json
{
  "text": "My credit card is 4111-1111-1111-1111",
  "direction": "input",
  "pipeline_id": "gdpr_strict"
}
```

**Response:**
```json
{
  "passed": false,
  "blocked_by": "pii_scanner",
  "reason": "Input contains credit card number (PII category)",
  "detections": [
    {
      "guard": "pii_scanner",
      "category": "credit_card",
      "confidence": 0.99,
      "start": 16,
      "end": 35,
      "redacted": "My credit card is [CREDIT_CARD]"
    }
  ],
  "latency_ms": 15
}
```

### `POST /api/v1/chat`

Full chat endpoint with guardrails wrapping the LLM call.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "What is the refund policy?"}
  ],
  "pipeline_id": "default",
  "user_id": "usr_abc123"
}
```

**Response:**
```json
{
  "reply": "You can return items within 30 days of purchase.",
  "guardrail_results": {
    "input": { "passed": true, "checks": 4, "latency_ms": 40 },
    "output": { "passed": true, "checks": 3, "warnings": [], "latency_ms": 35 }
  },
  "audit_id": "audit_xyz789"
}
```

**Response with blocked output:**
```json
{
  "reply": null,
  "error": "Output blocked by toxicity_filter (category: violence, confidence: 0.92)",
  "guardrail_results": {
    "input": { "passed": true, "checks": 4, "latency_ms": 40 },
    "output": { "passed": false, "blocked_by": "toxicity_filter", "reason": "Violence detected in output" }
  },
  "audit_id": "audit_xyz790"
}
```

### `GET /api/v1/guard/config`

List available guardrails, pipelines, and their configuration.

### `POST /api/v1/compliance/forget`

GDPR right to erasure — delete all data for a user.

**Request:**
```json
{
  "user_id": "usr_abc123",
  "confirm": true
}
```

**Response:**
```json
{
  "status": "deleted",
  "conversations_removed": 47,
  "audit_entries_anonymized": 312,
  "compliance_ref": "GDPR-Article-17-20260627-001"
}
```

### `GET /api/v1/audit`

Query audit logs.

**Query params:** `?user_id=usr_abc123&event=block&from=2026-06-01&to=2026-06-27&page=1&per_page=50`

**Response:**
```json
{
  "total": 23,
  "page": 1,
  "entries": [
    {
      "audit_id": "audit_xyz789",
      "timestamp": "2026-06-27T12:00:00Z",
      "user_id": "usr_abc123",
      "event": "block",
      "guard": "pii_scanner",
      "reason": "Credit card detected",
      "input_snapshot": "[REDACTED]",
      "compliance_refs": ["GDPR-Article-5(1)(c)", "PCI-DSS-3.4"]
    }
  ]
}
```

### `GET /api/v1/compliance/report`

Generate a compliance report for a given framework and date range.

**Query params:** `?framework=gdpr&from=2026-01-01&to=2026-06-27&format=pdf`

**Response:** PDF or HTML report containing:
- Number of blocked requests by guardrail type
- PII detection frequency by category
- User erasure requests fulfilled
- Audit log completeness verification
- Policy adherence summary

---

## Audit Trail

### Audit Event Schema

```json
{
  "audit_id": "audit_uuid",
  "timestamp": "2026-06-27T12:00:00.000Z",
  "user_id": "usr_abc123",
  "session_id": "sess_def456",
  "event_type": "check | block | redact | pass | forget",
  "guard": "pii_scanner | toxicity_filter | ...",
  "direction": "input | output",
  "pipeline_id": "gdpr_strict",
  "compliance_framework": "gdpr | hipaa | soc2",
  "compliance_refs": ["GDPR-Article-5(1)(c)"],
  "input_snapshot": "[REDACTED]",
  "output_snapshot": "[REDACTED]",
  "decision": "pass | block | redact",
  "reason": "Credit card detected",
  "latency_ms": 15,
  "metadata": {
    "ip_address": "...",
    "user_agent": "..."
  }
}
```

### Storage

| Tier | Storage | Retention | Use |
|---|---|---|---|
| Hot | PostgreSQL | 90 days | Query, dashboards |
| Warm | S3 (Parquet) | 1 year | Compliance reports |
| Cold | S3 Glacier | 7 years | Legal holds, SOC 2 evidence |

### Privacy

- Input/output snapshots are automatically redacted before storage (PII stripped at guard level)
- `user_id` is hashed after 90 days unless a legal hold is active
- Full payloads are never stored — only guardrail decisions and redacted snippets

---

## Monitoring

| Metric | Type | Labels | Description |
|---|---|---|---|
| `guardrail_checks_total` | Counter | guard, direction, result | Total guardrail evaluations |
| `guardrail_blocked_total` | Counter | guard, category | Requests blocked by each guard |
| `guardrail_latency_ms` | Histogram | guard | Per-guardrail latency |
| `guardrail_pass_rate` | Gauge | pipeline_id | % of requests passing all guards |
| `pii_detections_by_type` | Counter | pii_type | PII category distribution |
| `compliance_forget_requests` | Counter | framework | Right-to-erasure requests |
| `audit_log_size` | Gauge | tier | Audit log storage volume |

Alert when:
- `guardrail_pass_rate` drops below 95% (possible false positive surge)
- Any guardrail p95 latency exceeds 500ms
- PII detection rate spikes (possible data exposure)
- Compliance forget request failures > 0

---

## Tech Stack

| Component | Choice | Justification |
|---|---|---|
| Framework | FastAPI + uvicorn | Consistent with other projects |
| PII regex | `presidio-analyzer` | Microsoft's PII detection library, regex + NER |
| PII NER | spaCy (`en_core_web_trf`) | High-accuracy entity recognition |
| Toxicity | Detoxify (`unitary/toxic-bert`) | Lightweight, no external API |
| Topic classifier | `typeform/distilbart-mnli-12-3` | Zero-shot, no training needed |
| Prompt injection | `protectai/deberta-v3-base-prompt-injection` | Purpose-built, good accuracy |
| Configuration | YAML + pydantic-settings | Human-readable policies |
| Audit storage | PostgreSQL (hot) + S3 (cold) | Durable, queryable, cost-tiered |
| Report generation | Jinja2 + WeasyPrint (PDF) | Custom compliance reports |
| Monitoring | Prometheus + Grafana | Consistent with other projects |

---

## Implementation Phases

| Phase | Files | Deliverable |
|---|---|---|
| **1** | `config.py`, `schemas.py`, `guards/base.py`, `guards/registry.py` | Base abstractions and configuration |
| **2** | `detectors/pii_patterns.py`, `detectors/pii_ner.py`, `guards/pii_scanner.py` | PII detection and redaction |
| **3** | `detectors/toxicity_classifier.py`, `guards/toxicity_filter.py` | Toxicity filtering |
| **4** | `detectors/topic_classifier.py`, `guards/topic_checker.py` | Topic restriction |
| **5** | `guards/prompt_injection.py`, `guards/output_validator.py`, `guards/rate_limiter.py` | Injection detection, output validation, rate limiting |
| **6** | `pipeline/builder.py`, `pipeline/executor.py`, `pipeline/middleware.py` | Pipeline composition and execution |
| **7** | `compliance/gdpr.py`, `compliance/hipaa.py`, `compliance/soc2.py`, `compliance/policy.py` | Compliance frameworks |
| **8** | `audit/*` | Audit logging, storage, reporting |
| **9** | `api/*` | FastAPI routes |
| **10** | Tests + `data/sample_policies/*` + README | Verification, sample policies, documentation |

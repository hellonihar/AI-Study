# AI Evaluation Suite — Design Document

## Overview

A library and service that runs automated evaluations on LLM outputs — faithfulness, hallucination detection, precision/recall, relevance, and safety scoring. Integrates with pytest for local testing and with CI/CD pipelines for regression gating. This project demonstrates how QA/testing skills — test frameworks, metric design, CI/CD integration, regression detection — transfer directly to AI system evaluation.

---

## Architecture

```
┌──────────────────────────────┐
│      Evaluation Datasets      │
│  (JSONL: query, context,     │
│   reference_answer, tags)     │
└─────────────┬────────────────┘
              │
              ▼
┌───────────────────────────────────────────────────────────┐
│                   Evaluation Runner                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Metric  │  │  Metric  │  │  Metric  │  │  Metric  │ │
│  │ Registry │  │    #1    │  │    #2    │  │    #N    │ │
│  │(selector)│  │Faithful. │  │Relevance │  │ Toxicity │ │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│                     │             │             │        │
│              ┌──────▼──────┐ ┌────▼──────┐     │        │
│              │LLM-as-Judge │ │Determin. │     │        │
│              │(GPT-4o-as-  │ │(ROUGE-L, │     │        │
│              │ judge)      │ │  BERTScore)│    │        │
│              └──────┬──────┘ └────┬──────┘     │        │
│                     │             │             │        │
│              ┌──────▼─────────────▼─────────────▼──────┐ │
│              │          Result Collector               │ │
│              │  (per-item scores → aggregate stats)    │ │
│              └──────────────────┬──────────────────────┘ │
└─────────────────────────────────┼────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────┐
│                    Report Generator                       │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │
│  │ JSON/NDJSON│  │ HTML Dash. │  │ Regression Diff   │   │
│  │ (machine)  │  │ (readable) │  │ (vs. last run)    │   │
│  └────────────┘  └────────────┘  └──────────────────┘   │
└────────────────────────────────┬─────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     CI/CD Integration    │
                    │  ┌────────┐ ┌─────────┐ │
                    │  │ pytest │ │  GitHub  │ │
                    │  │ plugin │ │ Actions  │ │
                    │  └────────┘ └─────────┘ │
                    └─────────────────────────┘
```

---

## Project Structure

```
projects/ai-evaluation-suite/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Settings via pydantic-settings
│   ├── schemas.py                   # Pydantic models for metrics, results, runs
│   │
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract BaseMetric class
│   │   ├── registry.py              # Metric registry (lookup by name)
│   │   ├── faithfulness.py          # Claim-level faithfulness via LLM judge
│   │   ├── hallucination.py         # Unsupported claim detection
│   │   ├── relevance.py             # Answer-to-query relevance scoring
│   │   ├── precision_recall.py      # Token/entity-level precision & recall
│   │   ├── toxicity.py              # Content safety classification
│   │   ├── completeness.py          # Coverage of expected answer points
│   │   └── consistency.py           # Cross-response consistency check
│   │
│   ├── judges/
│   │   ├── __init__.py
│   │   ├── base.py                  # Abstract LLM-judge interface
│   │   ├── pairwise.py              # A/B comparison (which is better?)
│   │   ├── absolute.py              # Score-based (1-5 scale, pass/fail)
│   │   ├── reference.py             # Compare output to ground truth
│   │   └── prompts.py               # All judge prompt templates
│   │
│   ├── datasets/
│   │   ├── __init__.py
│   │   ├── loader.py                # Load eval sets (JSONL, CSV, HuggingFace)
│   │   ├── schemas.py               # Dataset row schema
│   │   └── generators.py            # Synthetic dataset generation via LLM
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── runner.py                # Orchestrates eval run
│   │   ├── reporter.py              # JSON + HTML report generation
│   │   └── comparer.py              # Regression diff between runs
│   │
│   ├── ci/
│   │   ├── __init__.py
│   │   ├── pytest_plugin.py         # pytest plugin: @pytest.mark.eval
│   │   └── github_action.py         # GitHub Action logic (threshold gating)
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py                # FastAPI routes (evaluate, runs, metrics)
│       └── dependencies.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_metrics.py
│   ├── test_judges.py
│   ├── test_pipeline.py
│   └── test_ci_integration.py
│
├── data/
│   └── sample_eval_set.jsonl        # 20-50 sample eval cases
│
├── notebooks/
│   └── explore_metrics.ipynb        # Metric experimentation
├── requirements.txt
└── README.md
```

---

## Metrics

### Metric Taxonomy

| Metric | Type | Method | Range | Description |
|---|---|---|---|---|
| **Faithfulness** | LLM-judge | Claim decomposition → verify each claim against context | 0.0–1.0 | % of claims in answer that are supported by context |
| **Hallucination Rate** | LLM-judge | Same as faithfulness, inverted | 0.0–1.0 | % of claims NOT supported by context |
| **Answer Relevance** | LLM-judge | Does answer address the query? | 0.0–1.0 | Semantic alignment between query and answer |
| **Precision@K** | Deterministic | Entity-level overlap (answer vs. reference) | 0.0–1.0 | % of entities in answer that are in reference |
| **Recall@K** | Deterministic | Entity-level overlap (answer vs. reference) | 0.0–1.0 | % of reference entities found in answer |
| **F1 Score** | Deterministic | Harmonic mean of precision & recall | 0.0–1.0 | Balanced entity-level match |
| **ROUGE-L** | Deterministic | Longest common subsequence | 0.0–1.0 | Summary-level overlap with reference |
| **Completeness** | LLM-judge | Expected points coverage | 0.0–1.0 | How many key points from reference are addressed |
| **Toxicity** | Classifier | Detoxify / Azure Content Safety | 0.0–1.0 | Probability of harmful content |
| **Consistency** | LLM-judge | Cross-response consistency (same query, multiple runs) | 0.0–1.0 | Variance in answers to the same question |

### Metric Interface

```python
class BaseMetric(ABC):
    name: str
    requires_context: bool = False      # Does this need retrieval context?
    requires_reference: bool = False    # Does this need a ground-truth answer?
    is_llm_judge: bool = False          # Does this call an LLM?

    @abstractmethod
    async def score(
        self,
        query: str,
        answer: str,
        context: str | None = None,
        reference: str | None = None,
    ) -> MetricResult:
        ...
```

### Faithfulness (Detail)

Faithfulness is the most important evaluation metric for RAG systems. Implementation:

```
Input: answer, context
  │
  ├── Step 1: Decompose answer into atomic claims
  │     LLM prompt: "Break this answer into independent claims, one per line"
  │     Output: ["The system uses microservices",
  │              "It supports 10K QPS",
  │              "Deployment is via Kubernetes"]
  │
  ├── Step 2: Verify each claim against context
  │     LLM prompt: "Determine if this claim is supported by the context. Answer: SUPPORTED / NOT_SUPPORTED / UNVERIFIABLE"
  │     Output: [SUPPORTED, NOT_SUPPORTED, SUPPORTED]
  │
  └── Step 3: Aggregate
        faithfulness = supported_claims / (total_claims - unverifiable_claims)
        hallucination_rate = not_supported_claims / total_claims
```

### Precision & Recall (Detail)

Entity-level evaluation for structured information extraction:

```
Precision = |entities(answer) ∩ entities(reference)| / |entities(answer)|
Recall    = |entities(answer) ∩ entities(reference)| / |entities(reference)|
F1        = 2 * (precision * recall) / (precision + recall)
```

Entities are extracted via an LLM call (or NER model) that identifies: people, organizations, dates, numbers, technical terms, product names.

---

## LLM-as-Judge Design

### Judge Configuration

| Parameter | Default | Description |
|---|---|---|
| Judge model | `gpt-4o` | Model used for judging (stronger = more reliable) |
| Candidate model | `gpt-4o-mini` | Model that produced the answer being judged |
| Temperature | 0.0 | Zero temperature for deterministic judging |
| Max tokens per judge call | 512 | Judge output length |
| Retries | 2 | On judge API failure |

### Calibration

The judge's own tendencies are measured by running it against a hand-labeled "gold set" of 50 cases:

```python
# Gold set entry
{
    "query": "What is the capital of France?",
    "answer": "Paris is the capital of France.",
    "reference": "Paris",
    "context": "France's capital is Paris, a major European city.",
    "human_labels": {
        "faithfulness": 1.0,
        "relevance": 1.0,
        "completeness": 1.0
    }
}
```

Judge bias (tendency to score high or low) and variance are computed from the gold set. A calibration factor is applied to raw scores.

### Bias Mitigation

| Bias | Mitigation |
|---|---|
| **Position bias** (prefers first answer in pairwise) | Randomize answer order, run both orders |
| **Verbosity bias** (prefers longer answers) | Instruct judge to ignore length |
| **Self-enhancement** (judge favors answers from its own family) | Use a different judge model than candidate |
| **Score anchoring** | Use reference-anchored scoring (compare to expected score) |

---

## Datasets

### Dataset Format (JSONL)

```jsonl
{"id": "001", "query": "What is the refund policy?", "context": "Our refund policy allows returns within 30 days...", "reference": "30-day return policy", "tags": ["customer-support", "policy"], "expected_metrics": {"faithfulness": 1.0, "relevance": 1.0}}
{"id": "002", "query": "How do I reset my password?", "context": "Go to Settings > Security > Reset Password...", "reference": "Settings > Security > Reset Password", "tags": ["technical-support"], "expected_metrics": {"faithfulness": 1.0, "relevance": 1.0}}
```

### Dataset Types

| Type | Source | Size | Use |
|---|---|---|---|
| **Gold set** | Human-annotated | 50–200 | Judge calibration, final gating |
| **Synthetic** | LLM-generated from documents | 500–2000 | Development, regression detection |
| **Production** | Sampled from live traffic (redacted) | 200–500 | Monitoring, drift detection |
| **Adversarial** | Edge cases (missing context, contradictory info) | 50–100 | Robustness testing |

### Synthetic Dataset Generation

```python
async def generate_eval_set(
    documents: list[str],
    num_cases: int = 200,
    llm: LLMProvider = None,
) -> list[EvalCase]:
    """Generate query-context-reference triples from a set of documents."""
    # For each document, ask the LLM to produce:
    #   1. A realistic user query that the document answers
    #   2. The relevant excerpt (context)
    #   3. A concise reference answer
    #   4. Potentially ambiguous or misleading variants
    ...
```

---

## Evaluation Pipeline

### Runner

```python
class EvaluationRunner:
    def __init__(self, metrics: list[BaseMetric], datasets: list[EvalDataset]):
        self.metrics = metrics
        self.datasets = datasets
        self.results: list[EvalRunResult] = []

    async def run(
        self,
        answer_fn: Callable[[str, str | None], str],
        run_name: str | None = None,
    ) -> EvalRunReport:
        """Run all metrics against all datasets using the provided answer function."""
        for dataset in self.datasets:
            for case in dataset.cases:
                answer = await answer_fn(case.query, case.context)
                for metric in self.metrics:
                    result = await metric.score(
                        query=case.query,
                        answer=answer,
                        context=case.context,
                        reference=case.reference,
                    )
                    self.results.append(result)

        return self._aggregate(run_name)
```

### Parallelization

```
Eval Cases
    │
    ├── Batch 1 (50 cases) ──► Worker 1 ──► Metric 1 ... Metric N
    ├── Batch 2 (50 cases) ──► Worker 2 ──► Metric 1 ... Metric N
    ├── Batch 3 (50 cases) ──► Worker 3 ──► Metric 1 ... Metric N
    └── Batch 4 (50 cases) ──► Worker 4 ──► Metric 1 ... Metric N
                                       │
                                  ┌────▼────┐
                                  │  Merge   │
                                  └────┬────┘
                                       ▼
                               Aggregate Statistics
```

- Each batch is independent → processed concurrently
- Within a batch, metrics are sequential per case (to avoid LLM contention)
- Results are merged and aggregated at the end

### Caching

```python
# Cache key: (metric_name, model_name, query_hash, context_hash)
# Cache value: MetricResult
# Cache TTL: depends on eval set version
# Invalidation: on any change to prompt, model, or eval set
```

Caching avoids re-running expensive LLM-judge evaluations when only the prompt or answer function changed.

---

## CI/CD Integration

### pytest Plugin

```python
# conftest.py
import pytest
from ai_eval_suite import EvalSuite

@pytest.fixture
def eval_suite():
    return EvalSuite.from_config("eval_config.yaml")

# test_evals.py
@pytest.mark.eval
class TestRAGEvals:
    def test_faithfulness_above_threshold(self, eval_suite):
        report = eval_suite.run(answer_fn=get_answer)
        assert report.get_metric("faithfulness").mean >= 0.85

    def test_hallucination_below_threshold(self, eval_suite):
        report = eval_suite.run(answer_fn=get_answer)
        assert report.get_metric("hallucination_rate").mean <= 0.05

    def test_no_regression_vs_baseline(self, eval_suite):
        report = eval_suite.run(answer_fn=get_answer)
        baseline = eval_suite.load_baseline("latest")
        assert report.compare_to(baseline).is_pass
```

### pytest Mark Registration

```python
# Register custom markers in pytest.ini or conftest.py
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "eval: Mark test as an AI evaluation test (run separately from unit tests)",
    )
```

Tests marked `@pytest.mark.eval` are excluded from regular `pytest` runs and executed with `pytest -m eval`.

### GitHub Action

```yaml
# .github/workflows/eval.yml
name: AI Evaluation
on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'app/generation/**'

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt

      - name: Run evaluations
        id: eval
        run: |
          pytest -m eval --eval-report=report.json --eval-baseline=latest

      - name: Check thresholds
        run: |
          python -m ai_eval_suite check report.json --thresholds .eval_thresholds.yaml

      - name: Comment PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const report = require('./report.json');
            // Post eval results as PR comment
```

### Threshold Configuration

```yaml
# .eval_thresholds.yaml
thresholds:
  faithfulness:
    min: 0.85
    warn_below: 0.90
  hallucination_rate:
    max: 0.05
    warn_above: 0.03
  relevance:
    min: 0.80
  toxicity:
    max: 0.01
regression:
  max_degradation_pct: 5  # Fail if any metric drops >5% from baseline
comparison:
  baseline: "latest"       # Compare against latest main branch run
```

---

## API

### `POST /api/v1/evaluate`

On-demand evaluation of a single query-answer pair.

**Request:**
```json
{
  "query": "What is the refund policy?",
  "answer": "You can return items within 30 days.",
  "context": "Our refund policy allows returns within 30 days of purchase.",
  "reference": "30-day return policy",
  "metrics": ["faithfulness", "relevance", "hallucination"]
}
```

**Response:**
```json
{
  "run_id": "eval_abc123",
  "results": {
    "faithfulness": { "score": 1.0, "confidence": 0.95 },
    "relevance": { "score": 0.9, "confidence": 0.88 },
    "hallucination": { "score": 0.0, "confidence": 0.95 }
  },
  "latency_ms": 2340,
  "cost_usd": 0.002
}
```

### `POST /api/v1/evaluate/batch`

Run a full eval set.

**Request:**
```json
{
  "dataset_id": "customer-support-v2",
  "metrics": ["faithfulness", "hallucination", "relevance", "completeness"],
  "answer_fn_url": "https://api.myapp.com/chat"  // or pass answers inline
}
```

**Response:**
```json
{
  "run_id": "run_xyz789",
  "dataset": "customer-support-v2",
  "num_cases": 200,
  "summary": {
    "faithfulness": { "mean": 0.92, "std": 0.08, "min": 0.45, "p95": 1.0 },
    "hallucination": { "mean": 0.03, "std": 0.05, "min": 0.0, "p95": 0.1 },
    "relevance": { "mean": 0.88, "std": 0.12, "min": 0.3, "p95": 1.0 },
    "completeness": { "mean": 0.85, "std": 0.15, "min": 0.2, "p95": 1.0 }
  },
  "latency_ms": 45000,
  "cost_usd": 0.45
}
```

### `GET /api/v1/runs/{run_id}`

Retrieve full results for a past evaluation run (all per-item scores).

### `GET /api/v1/runs/{run_id}/diff?baseline={baseline_id}`

Regression comparison between two runs.

### `GET /api/v1/metrics`

List all available metrics with descriptions and configuration options.

---

## Reporting

### JSON Report Structure

```json
{
  "run_id": "run_xyz789",
  "timestamp": "2026-06-27T12:00:00Z",
  "metadata": {
    "eval_config": { "model": "gpt-4o-mini", "temperature": 0.3 },
    "dataset": "customer-support-v2",
    "version_control": { "commit": "a1b2c3d", "branch": "feature/new-prompts" }
  },
  "summary": { ... },
  "per_item": [
    {
      "case_id": "001",
      "query": "...",
      "scores": {
        "faithfulness": 1.0,
        "relevance": 0.9,
        "hallucination": 0.0
      }
    }
  ],
  "cost_usd": 0.45,
  "latency_ms": 45000
}
```

### HTML Dashboard

Generated from the JSON report — includes:
- Overall pass/fail status (threshold gates)
- Metric distribution histograms
- Per-metric trend chart (when compared to past runs)
- Per-item drill-down (query, answer, score breakdown)
- Cost and latency summary
- Regression highlights (metrics that changed)

---

## Monitoring

| Metric | Type | Labels | Description |
|---|---|---|---|
| `eval_pass_rate` | Gauge | metric, dataset | % of cases passing threshold |
| `eval_score` | Gauge | metric, dataset | Mean score for each metric |
| `eval_latency_ms` | Histogram | metric | Per-evaluation latency |
| `eval_cost_usd` | Counter | dataset, model | Total eval cost |
| `eval_regression_count` | Counter | metric | Number of regressions detected |

Alert when:
- `eval_pass_rate` drops below 90%
- Any metric regresses more than 5% from baseline
- `eval_cost_usd` exceeds daily budget

---

## Tech Stack

| Component | Choice | Justification |
|---|---|---|
| Framework | FastAPI + uvicorn | Consistent with other projects |
| Evaluation orchestration | Native Python async | No heavy framework needed |
| LLM judge calls | litellm | Multi-provider abstraction (OpenAI, Anthropic, local) |
| Deterministic metrics | `rouge-score`, `bert-score` | Standard NLP evaluation libraries |
| Toxicity classifier | Detoxify (unitary/toxic-bert) | Lightweight, no API calls needed |
| CI integration | pytest + GitHub Actions | Standard testing ecosystem |
| Configuration | pydantic-settings + YAML | Type-safe config |
| Caching | diskcache | Simple, persistent, no Redis dependency |
| Monitoring | Prometheus + Grafana | Consistent with other projects |
| Reporting | Jinja2 (HTML), JSON | Machine + human readable |

---

## Implementation Phases

| Phase | Files | Deliverable |
|---|---|---|
| **1** | `config.py`, `schemas.py`, `metrics/base.py` | Base abstractions and configuration |
| **2** | `metrics/faithfulness.py`, `metrics/hallucination.py`, `metrics/relevance.py` | Core LLM-judge metrics |
| **3** | `metrics/precision_recall.py`, `metrics/completeness.py`, `metrics/consistency.py`, `metrics/toxicity.py` | Remaining metrics |
| **4** | `judges/*`, `judges/prompts.py` | LLM judge system with calibration |
| **5** | `datasets/*`, `pipeline/runner.py` | Dataset loading + eval pipeline |
| **6** | `pipeline/reporter.py`, `pipeline/comparer.py` | Reporting + regression detection |
| **7** | `ci/pytest_plugin.py`, `ci/github_action.py` | CI/CD integration |
| **8** | `api/*` | FastAPI routes |
| **9** | Tests, `data/sample_eval_set.jsonl` | Verification, sample data |
| **10** | `README.md`, notebooks | Documentation, exploration |

# AI Drift Detection — Design Document

## Overview

A monitoring pipeline that detects model drift in production LLM systems: compare embedding distributions over time, track accuracy against a held-out eval set, monitor input/output distributions, and alert on degradation. This project demonstrates how monitoring experience — observability pipelines, statistical analysis, anomaly detection, alerting — transfers directly to AI system reliability.

**Skills demonstrated: ML monitoring — Statistical drift detection — Embedding distribution analysis — Alerting**

| Enterprise Monitoring Skill | AI Equivalent | This Project |
|---|---|---|
| Infrastructure monitoring (CPU, memory, disk) | Embedding distribution drift | Kolmogorov-Smirnov test on embedding clusters over sliding windows |
| Application performance monitoring (latency, error rates) | LLM quality metrics drift | Faithfulness, hallucination, relevance tracked on held-out eval set |
| Log analysis (anomaly detection in logs) | Input/output distribution shift | Text length, topic, language, sentiment distribution comparisons |
| Alerting & incident response | Quality degradation alerts | Multi-threshold alerting with escalation on sustained drift |
| Dashboarding (Grafana, Kibana) | Drift visualization + trend analysis | Time-series dashboard with drift scores, metric trends, alert history |

---

## Architecture

```
                    ┌────────────────────────────────────────────┐
                    │           Production System                 │
                    │  ┌──────────┐ ┌──────────┐ ┌────────────┐ │
                    │  │  Inputs  │ │  LLM     │ │  Outputs   │ │
                    │  │ (queries) │ │  Call    │ │(responses) │ │
                    │  └────┬─────┘ └──────────┘ └──────┬─────┘ │
                    └───────┼───────────────────────────┼───────┘
                            │                           │
                            ▼                           ▼
              ┌──────────────────────────────────────────────┐
              │            Log Collector / Stream             │
              │   (structured JSON logs → Kafka / S3 / Loki)  │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │           Drift Detection Pipeline            │
              │                                               │
              │  ┌─────────────────┐  ┌──────────────────┐   │
              │  │  Embedding      │  │  Statistical     │   │
              │  │  Drift Detector │  │  Drift Detector  │   │
              │  │  (distribution  │  │  (KS-test,       │   │
              │  │  comparison)    │  │  Wasserstein)    │   │
              │  └─────────────────┘  └──────────────────┘   │
              │                                               │
              │  ┌─────────────────┐  ┌──────────────────┐   │
              │  │  Metric Drift   │  │  Data Drift      │   │
              │  │  Detector       │  │  Detector        │   │
              │  │  (eval set     │  │  (text features)  │   │
              │  │  performance)   │  │                   │   │
              │  └─────────────────┘  └──────────────────┘   │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │            Drift Report Generator             │
              │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
              │  │  Drift   │ │  Trend   │ │  Alert       │ │
              │  │  Scores  │ │  History │ │  Generator   │ │
              │  └──────────┘ └──────────┘ └──────────────┘ │
              └──────────────────────┬───────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌──────────┐   ┌────────────┐   ┌──────────────┐
              │ Grafana  │   │  PagerDuty │   │ Slack/Teams │
              │ Dashboard│   │  (critical)│   │  (warnings) │
              └──────────┘   └────────────┘   └──────────────┘
```

### Detection Flow

```
Every N minutes (configurable window):
    │
    ├── 1. Load reference window (baseline distribution)
    │       - First 7 days of production data
    │       - Or last 24 hours for rolling comparison
    │
    ├── 2. Load current window (latest data)
    │       - Last 1 hour of production data
    │
    ├── 3. Run detectors
    │       ├── EmbeddingDriftDetector
    │       │     ├── Cluster embeddings (UMAP/PCA → HDBSCAN)
    │       │     ├── Compare cluster distributions (KS-test)
    │       │     └── Score: % of points in novel clusters
    │       │
    │       ├── MetricDriftDetector
    │       │     ├── Run eval suite on held-out set
    │       │     ├── Compare scores vs baseline
    │       │     └── Score: degradation % per metric
    │       │
    │       └── DataDriftDetector
    │             ├── Compute text feature distributions
    │             ├── Categorical: chi-squared test
    │             ├── Numerical: KS-test
    │             └── Score: p-value per feature
    │
    ├── 4. Aggregate drift scores
    │       └── Composite drift index (weighted combination)
    │
    ├── 5. Check alert thresholds
    │       ├── Warning: drift index > 0.3
    │       ├── Critical: drift index > 0.6
    │       └── Emergency: metric drop > 10% for 3 consecutive windows
    │
    └── 6. Emit results
            ├── Prometheus metrics (drift scores, p-values)
            ├── Alertmanager (if thresholds exceeded)
            └── Report store (JSON → S3 for trend analysis)
```

---

## Project Structure

```
projects/ai-drift-detection/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Settings via pydantic-settings
│   ├── schemas.py                   # Pydantic models for windows, drift scores, alerts
│   │
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── log_source.py           # Read logs from Kafka, S3, Loki, or local files
│   │   └── eval_source.py          # Retrieve eval results from eval suite DB
│   │
│   ├── detectors/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract DriftDetector class
│   │   ├── registry.py             # Detector registry
│   │   ├── embedding.py            # Embedding distribution drift (cluster + KS test)
│   │   ├── metric.py               # Model quality metric drift (eval set performance)
│   │   ├── data.py                 # Input/output feature drift (text stats, categories)
│   │   └── concept.py              # Prediction-concept drift (label distribution shift)
│   │
│   ├── statistics/
│   │   ├── __init__.py
│   │   ├── ks_test.py              # Kolmogorov-Smirnov 2-sample test
│   │   ├── wasserstein.py          # Wasserstein (Earth Mover's) distance
│   │   ├── chi_squared.py          # Chi-squared test for categorical features
│   │   ├── js_divergence.py        # Jensen-Shannon divergence
│   │   └── drift_index.py          # Composite drift index computation
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── scheduler.py            # Window scheduling + orchestration
│   │   ├── window_manager.py       # Reference + current window management
│   │   └── runner.py               # Full pipeline orchestration
│   │
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── report.py               # Drift report data model
│   │   ├── alert_rules.py          # Alert threshold configuration
│   │   └── dashboard.py            # Grafana dashboard JSON definition
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py               # FastAPI: drift status, reports, history
│       └── dependencies.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_embedding_drift.py
│   ├── test_metric_drift.py
│   ├── test_data_drift.py
│   ├── test_statistics.py
│   └── test_pipeline.py
│
├── data/
│   ├── sample_logs.jsonl            # Sample production logs
│   ├── sample_embeddings.npy        # Sample embedding vectors
│   └── baseline/                    # Stored baseline distributions
│       ├── embedding_clusters.json
│       └── metric_scores.json
│
├── notebooks/
│   └── explore_drift_detection.ipynb
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Drift Types

### 1. Embedding Drift

Detects when the semantic content of user queries or LLM responses shifts over time.

```
        Reference Window              Current Window
     (first 7 days of data)         (last 1 hour of data)
             │                              │
             ▼                              ▼
      ┌──────────────┐              ┌──────────────┐
      │  Embed all   │              │  Embed all   │
      │  inputs      │              │  inputs      │
      └──────┬───────┘              └──────┬───────┘
             │                              │
             ▼                              ▼
      ┌────────────────────────────────────────────┐
      │  UMAP reduction (2D for clustering)         │
      │  Fit on reference, transform both windows   │
      └────────────────────┬───────────────────────┘
                           │
                           ▼
      ┌────────────────────────────────────────────┐
      │  HDBSCAN clustering on combined embedding   │
      │  → discover cluster structure               │
      └────────────────────┬───────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                              ▼
      ┌──────────────┐              ┌──────────────┐
      │ Reference    │              │ Current      │
      │ cluster dist │              │ cluster dist │
      └──────┬───────┘              └──────┬───────┘
             │                              │
             └──────────────┬──────────────┘
                            ▼
              ┌────────────────────────────┐
              │  KS-test per cluster       │
              │  p-value: distribution     │
              │  similarity                │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  Drift metrics:            │
              │  - % points in novel clus. │
              │  - mean KS p-value         │
              │  - cluster count change    │
              └────────────────────────────┘
```

```python
class EmbeddingDriftDetector(DriftDetector):
    def __init__(self, embedding_model: str = "text-embedding-3-small", n_components: int = 50):
        self.embedder = EmbeddingModel(embedding_model)
        self.reducer = UMAP(n_components=n_components)
        self.clusterer = HDBSCAN(min_cluster_size=10)

    async def detect(self, reference: DataWindow, current: DataWindow) -> DriftResult:
        ref_embs = await self.embedder.embed_many(reference.samples)
        cur_embs = await self.embedder.embed_many(current.samples)

        # Fit reducer on reference, transform both
        ref_reduced = self.reducer.fit_transform(ref_embs)
        cur_reduced = self.reducer.transform(cur_embs)

        # Cluster on combined to find shared + novel structure
        combined = np.vstack([ref_reduced, cur_reduced])
        labels = self.clusterer.fit_predict(combined)
        ref_labels = labels[:len(ref_reduced)]
        cur_labels = labels[len(ref_reduced):]

        # Novel clusters: points in current with label not in reference
        ref_clusters = set(ref_labels)
        novel_ratio = sum(1 for l in cur_labels if l not in ref_clusters) / len(cur_labels)

        # Per-cluster KS test on point density
        cluster_distances = []
        for cluster_id in ref_clusters:
            ref_points = embeds_from_cluster(ref_embs, ref_labels, cluster_id)
            cur_points = embeds_from_cluster(cur_embs, cur_labels, cluster_id)
            if len(ref_points) > 0 and len(cur_points) > 0:
                d, p = ks_2samp(ref_points.flatten(), cur_points.flatten())
                cluster_distances.append({"cluster": int(cluster_id), "ks_stat": d, "p_value": p})

        return DriftResult(
            detector="embedding",
            score=novel_ratio,
            p_value=min(c["p_value"] for c in cluster_distances) if cluster_distances else 1.0,
            details={
                "novel_cluster_ratio": novel_ratio,
                "cluster_count_reference": len(ref_clusters),
                "cluster_count_current": len(set(cur_labels)),
                "cluster_distances": cluster_distances,
            },
        )
```

### 2. Metric Drift

Detects when LLM output quality degrades over time by running the evaluation suite on a held-out set.

```python
class MetricDriftDetector(DriftDetector):
    """
    Tracks accuracy of the LLM on a fixed eval set.
    Every window, runs the eval suite and compares against baseline.
    """
    def __init__(self, eval_set: list[EvalCase]):
        self.eval_set = eval_set
        self.baseline_scores: dict[str, float] = {}

    async def detect(self, reference: DataWindow, current: DataWindow) -> DriftResult:
        # Run eval suite on current system
        current_scores = await self._run_eval(current)

        # Compare against baseline (reference window's scores)
        if not self.baseline_scores:
            self.baseline_scores = current_scores
            return DriftResult(detector="metric", score=0.0, p_value=1.0)

        degradations = {}
        for metric, baseline_val in self.baseline_scores.items():
            current_val = current_scores.get(metric, baseline_val)
            if baseline_val > 0:
                degradations[metric] = (baseline_val - current_val) / baseline_val

        max_degradation = max(degradations.values()) if degradations else 0
        return DriftResult(
            detector="metric",
            score=max_degradation,
            p_value=1.0 - max_degradation,
            details={
                "baseline": self.baseline_scores,
                "current": current_scores,
                "degradations": degradations,
            },
        )
```

| Metric | Reference Baseline | Degradation Signal |
|---|---|---|
| Faithfulness | 0.92 | Responses less grounded in context |
| Hallucination rate | 0.03 | More unsupported claims |
| Answer relevance | 0.88 | Responses drifting off-topic |
| Completeness | 0.85 | Missing key information |
| Latency p95 | 800ms | Model or infrastructure slowdown |

### 3. Data Drift

Detects when the statistical properties of input text change — topic distribution, language, length, sentiment.

```python
class DataDriftDetector(DriftDetector):
    FEATURES = {
        "text_length": {"type": "numeric", "test": "ks"},
        "sentiment_score": {"type": "numeric", "test": "ks"},
        "language": {"type": "categorical", "test": "chi2"},
        "topic": {"type": "categorical", "test": "chi2"},
        "entity_count": {"type": "numeric", "test": "ks"},
        "question_type": {"type": "categorical", "test": "chi2"},
        "toxicity_score": {"type": "numeric", "test": "ks"},
        "word_count": {"type": "numeric", "test": "ks"},
    }

    async def detect(self, reference: DataWindow, current: DataWindow) -> DriftResult:
        ref_features = self._extract_features(reference.samples)
        cur_features = self._extract_features(current.samples)

        drifts = []
        for feature_name, config in self.FEATURES.items():
            ref_values = [s[feature_name] for s in ref_features if feature_name in s]
            cur_values = [s[feature_name] for s in cur_features if feature_name in s]

            if config["type"] == "numeric":
                stat, p_value = ks_2samp(ref_values, cur_values)
                drifts.append({"feature": feature_name, "test": "KS", "statistic": stat, "p_value": p_value})
            else:
                from scipy.stats import chi2_contingency
                ref_counts = Counter(ref_values)
                cur_counts = Counter(cur_values)
                all_categories = list(set(list(ref_counts.keys()) + list(cur_counts.keys())))
                ref_row = [ref_counts.get(c, 0) for c in all_categories]
                cur_row = [cur_counts.get(c, 0) for c in all_categories]
                stat, p_value, _, _ = chi2_contingency([ref_row, cur_row])
                drifts.append({"feature": feature_name, "test": "chi-squared", "statistic": stat, "p_value": p_value})

        # Aggregate: fraction of features with p_value < 0.05
        drifted_features = sum(1 for d in drifts if d["p_value"] < 0.05)
        return DriftResult(
            detector="data",
            score=drifted_features / len(drifts),
            p_value=min(d["p_value"] for d in drifts),
            details={"features": drifts},
        )
```

### 4. Concept Drift

Detects when the relationship between input and output changes — same queries get different-quality responses.

```python
class ConceptDriftDetector(DriftDetector):
    """
    Compares the distribution of (query embedding, quality_score) pairs
    between reference and current windows. A shift in this joint distribution
    indicates concept drift: the model is behaving differently for similar inputs.
    """
    async def detect(self, reference: DataWindow, current: DataWindow) -> DriftResult:
        # For each window, compute quality scores (faithfulness) per query cluster
        ref_by_cluster = self._group_by_embedding_cluster(reference)
        cur_by_cluster = self._group_by_embedding_cluster(current)

        cluster_drifts = []
        for cluster_id in set(list(ref_by_cluster.keys()) + list(cur_by_cluster.keys())):
            ref_scores = ref_by_cluster.get(cluster_id, [])
            cur_scores = cur_by_cluster.get(cluster_id, [])
            if len(ref_scores) > 0 and len(cur_scores) > 0:
                stat, p = ks_2samp(ref_scores, cur_scores)
                cluster_drifts.append(p)

        mean_p = np.mean(cluster_drifts) if cluster_drifts else 1.0
        return DriftResult(
            detector="concept",
            score=1.0 - mean_p,
            p_value=mean_p,
            details={"cluster_count": len(cluster_drifts), "mean_p_value": mean_p},
        )
```

---

## Drift Index

### Composite Calculation

```python
class DriftIndex:
    """
    Combines all detector scores into a single composite drift index (0.0–1.0).
    Higher values indicate more severe drift.
    """
    WEIGHTS = {
        "embedding": 0.3,     # Semantic content shift
        "metric": 0.4,        # Quality degradation (highest weight)
        "data": 0.2,          # Input feature distribution shift
        "concept": 0.1,       # Input-output relationship shift
    }

    def compute(self, results: dict[str, DriftResult]) -> CompositeDrift:
        index = sum(results[k].score * self.WEIGHTS[k] for k in self.WEIGHTS if k in results)
        p_values = [r.p_value for r in results.values() if r.p_value is not None]

        return CompositeDrift(
            index=round(index, 4),
            severity="none" if index < 0.2 else "low" if index < 0.3 else "medium" if index < 0.45 else "high" if index < 0.6 else "critical",
            combined_p_value=np.min(p_values) if p_values else 1.0,
            detectors={k: r.score for k, r in results.items() if k in results},
            timestamp=datetime.utcnow(),
        )
```

### Severity Thresholds

| Severity | Index Range | Action |
|---|---|---|
| None | 0.00 – 0.19 | Log only |
| Low | 0.20 – 0.29 | Log, increment dashboard counter |
| Medium | 0.30 – 0.44 | Slack alert to team channel |
| High | 0.45 – 0.59 | PagerDuty notification, on-call engineer |
| Critical | 0.60 – 1.00 | Auto-rollback last prompt/model change, page entire team |

---

## Windows

### Window Manager

```python
class WindowManager:
    """
    Manages reference and current data windows for drift detection.

    Reference window strategies:
      - fixed: First N days of production data (static baseline)
      - rolling: Last 24 hours (adaptive baseline)
      - version: Data since last prompt/model deployment

    Current window:
      - sliding: Last N minutes (default: 60 min)
    """
    def __init__(self, strategy: str = "rolling", reference_days: int = 7, window_minutes: int = 60):
        self.strategy = strategy
        self.reference_duration = timedelta(days=reference_days)
        self.window_duration = timedelta(minutes=window_minutes)

    async def get_windows(self, source: LogSource) -> tuple[DataWindow, DataWindow]:
        now = datetime.utcnow()
        reference = await source.query(
            start=now - self.reference_duration - self.window_duration,
            end=now - self.window_duration,
        ) if self.strategy == "rolling" else await self._load_fixed_baseline()

        current = await source.query(
            start=now - self.window_duration,
            end=now,
        )
        return reference, current
```

### Sampling

For large production volumes, sample within each window:

| Volume | Sample Size | Method |
|---|---|---|
| < 10K requests/window | All | — |
| 10K–100K | 10K | Stratified random (by hour) |
| > 100K | 20K | Stratified random (by hour + topic) |

---

## API

### `GET /api/v1/drift/status`

Current drift status for all detectors.

**Response:**
```json
{
  "timestamp": "2026-06-27T12:00:00Z",
  "drift_index": 0.35,
  "severity": "medium",
  "detectors": {
    "embedding": {"score": 0.42, "p_value": 0.003, "severity": "medium"},
    "metric": {"score": 0.28, "p_value": 0.12, "severity": "low"},
    "data": {"score": 0.31, "p_value": 0.04, "severity": "medium"},
    "concept": {"score": 0.15, "p_value": 0.45, "severity": "none"}
  },
  "window": {
    "reference": {"start": "2026-06-20T12:00:00Z", "end": "2026-06-27T11:00:00Z", "samples": 45000},
    "current": {"start": "2026-06-27T11:00:00Z", "end": "2026-06-27T12:00:00Z", "samples": 2800}
  }
}
```

### `GET /api/v1/drift/history`

Drift index history over time.

**Query params:** `?from=2026-06-01&to=2026-06-27&granularity=1h`

**Response:**
```json
{
  "points": [
    {"timestamp": "2026-06-27T11:00:00Z", "drift_index": 0.28, "severity": "low"},
    {"timestamp": "2026-06-27T10:00:00Z", "drift_index": 0.22, "severity": "low"}
  ],
  "granularity": "1h"
}
```

### `GET /api/v1/drift/detectors/{name}`

Detailed results for a specific detector.

### `GET /api/v1/drift/report`

Generate a full drift report for a given time range.

**Query params:** `?from=2026-06-20&to=2026-06-27&format=json`

**Response:**
```json
{
  "period": {"start": "2026-06-20", "end": "2026-06-27"},
  "summary": {
    "mean_drift_index": 0.18,
    "max_drift_index": 0.55,
    "alert_events": 3,
    "detections_by_severity": {"none": 120, "low": 35, "medium": 8, "high": 2, "critical": 0}
  },
  "per_detector": {
    "embedding": {
      "mean_score": 0.22,
      "trend": "stable",
      "significant_events": [
        {
          "timestamp": "2026-06-25T14:00:00Z",
          "score": 0.55,
          "p_value": 0.001,
          "note": "Novel cluster appeared: queries about new product launch"
        }
      ]
    }
  }
}
```

### `GET /api/v1/drift/metrics`

Expose drift scores as Prometheus-formatted metrics (used for scraping).

---

## Scheduling

### Pipeline Scheduler

```python
class DriftPipelineScheduler:
    """
    Runs the drift detection pipeline on a schedule.
    Supports:
      - Periodic: every N minutes (default: 30 min)
      - Continuous: process as logs arrive (streaming)
      - On-demand: triggered via API or webhook
    """
    def __init__(self, source, detectors, interval_minutes: int = 30):
        self.source = source
        self.detectors = detectors
        self.interval = interval_minutes

    async def run_cycle(self):
        reference, current = await self.window_manager.get_windows(self.source)
        results = {}
        for detector in self.detectors:
            results[detector.name] = await detector.detect(reference, current)
        composite = DriftIndex().compute(results)
        await self._emit_metrics(composite)
        await self._check_alerts(composite, results)
        await self._store_report(composite, results)

    async def start(self):
        while True:
            await self.run_cycle()
            await asyncio.sleep(self.interval * 60)
```

---

## Alerting

### Alert Rules

```yaml
# alert_rules.yaml
alerts:
  - name: drift_index_high
    condition: drift_index >= 0.45
    for_minutes: 10
    severity: high
    channels: [slack, pagerduty]
    message: "Drift index at {{ drift_index }} — investigate recent prompt/model changes"

  - name: drift_index_critical
    condition: drift_index >= 0.60
    for_minutes: 5
    severity: critical
    channels: [slack, pagerduty, auto_rollback]
    message: "Critical drift detected (index: {{ drift_index }}). Triggering auto-rollback."
    auto_rollback: true

  - name: metric_drift_sustained
    condition: metric_drift_score >= 0.15
    for_minutes: 90
    severity: high
    channels: [slack]
    message: "Metric quality degradation sustained for 90 minutes — faithfulness dropped {{ degradation_pct }}%"

  - name: embedding_novel_cluster
    condition: embedding_novel_ratio >= 0.20
    for_minutes: 30
    severity: medium
    channels: [slack]
    message: "{{ novel_ratio }}% of queries in previously unseen embedding clusters — possible topic shift"
```

### Alert Channels

| Severity | Channel | Response |
|---|---|---|
| Medium | Slack #drift-alerts | Team reviews during business hours |
| High | Slack + PagerDuty (non-urgent) | On-call investigates within 1 hour |
| Critical | Slack + PagerDuty (urgent) + Auto-rollback | Immediate investigation, rollback triggered |

---

## Monitoring (Meta)

The drift detection system monitors itself:

| Metric | Description | Alert |
|---|---|---|
| `drift_pipeline_latency_ms` | Time to run one detection cycle | > 5 min (missed window) |
| `drift_pipeline_errors_total` | Detection pipeline failure count | > 0 in 1 hour |
| `drift_log_processing_lag` | Lag between log timestamp and processing | > 30 min |
| `drift_source_logs_per_window` | Log volume per window | Drop > 50% (source failure) |

---

## Tech Stack

| Component | Choice | Justification |
|---|---|---|
| Framework | FastAPI + uvicorn | Consistent with other projects |
| Embedding | text-embedding-3-small | Same model as production — apples-to-apples comparison |
| Dimensionality reduction | UMAP (fit on reference, transform current) | Faster than PCA, preserves cluster structure |
| Clustering | HDBSCAN | No need to specify K, handles noise points |
| Statistical tests | scipy (ks_2samp, chi2_contingency) | Industry standard, well-tested |
| Distance metrics | Wasserstein distance, Jensen-Shannon divergence | Complementary to KS-test |
| Data pipeline | pandas + numpy + polars | Efficient window processing |
| Log source | Kafka / S3 / Loki | Pluggable — choose based on existing infra |
| Storage | PostgreSQL (reports), S3 (baselines) | Queryable history, durable baseline snapshots |
| Alerting | Prometheus Alertmanager + PagerDuty + Slack | Consistent with other projects |
| Dashboarding | Grafana | Consistent with other projects |

---

## Implementation Phases

| Phase | Files | Deliverable |
|---|---|---|
| **1** | `config.py`, `schemas.py`, `detectors/base.py`, `detectors/registry.py` | Base abstractions and configuration |
| **2** | `connectors/log_source.py`, `connectors/eval_source.py`, `pipeline/window_manager.py` | Log source connector + window management |
| **3** | `detectors/embedding.py`, `statistics/ks_test.py`, `statistics/wasserstein.py` | Embedding drift detection with UMAP + HDBSCAN + KS-test |
| **4** | `detectors/metric.py` | Metric drift detection via eval suite |
| **5** | `detectors/data.py`, `statistics/chi_squared.py`, `statistics/js_divergence.py` | Data drift detection (text features, categorical + numeric) |
| **6** | `detectors/concept.py`, `statistics/drift_index.py` | Concept drift detection + composite drift index |
| **7** | `pipeline/scheduler.py`, `pipeline/runner.py` | Pipeline orchestration + scheduling |
| **8** | `reporting/report.py`, `reporting/alert_rules.py`, `reporting/dashboard.py` | Reporting, alerting, Grafana dashboard |
| **9** | `api/*` | FastAPI routes |
| **10** | Tests + `data/sample_*` + notebooks + README | Verification, sample data, documentation |

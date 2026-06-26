# AI Analytics Assistant — Design Document

## Overview

An LLM-powered reporting tool that ingests raw logs or metrics and produces executive summaries with narrative insights, visualizations, and actionable recommendations. This project demonstrates how stakeholder reporting experience — data gathering, insight synthesis, executive communication, dashboard design — transfers directly to building AI analytics applications.

---

## Architecture

```
                    ┌────────────────────────────────────────────┐
                    │              Data Sources                   │
                    │  ┌──────────┐ ┌──────────┐ ┌────────────┐ │
                    │  │  Logs    │ │ Metrics  │ │  Business  │ │
                    │  │(JSONL)   │ │(CSV/Parq)│ │  APIs      │ │
                    │  └────┬─────┘ └────┬─────┘ └─────┬──────┘ │
                    └───────┼────────────┼──────────────┼────────┘
                            │            │              │
                            ▼            ▼              ▼
              ┌──────────────────────────────────────────────┐
              │              Ingestion Layer                  │
              │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
              │  │ Parser   │ │ Validator│ │   Schema     │ │
              │  │ (auto-   │ │ (types,  │ │   Detector   │ │
              │  │  detect) │ │  ranges) │ │              │ │
              │  └──────────┘ └──────────┘ └──────────────┘ │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │             Analysis Pipeline                 │
              │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
              │  │ Summary  │ │  Trend   │ │ Anomaly      │ │
              │  │ Stats    │ ├──────────┤ │ Detection    │ │
              │  │(mean, p95,│ │Change    │ │(statistical) │ │
              │  │ counts)  │ │Analysis  │ │              │ │
              │  └──────────┘ └──────────┘ └──────────────┘ │
              │  ┌────────────┐ ┌──────────────────────────┐ │
              │  │ Correlation│ │   Segmentation           │ │
              │  │ Analysis   │ │   (by dimension)         │ │
              │  └────────────┘ └──────────────────────────┘ │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │             LLM Generation                    │
              │  ┌──────────────┐ ┌──────────┐ ┌──────────┐ │
              │  │  Executive   │ │Narrative │ │ Visual.  │ │
              │  │  Summary     │ │ Builder  │ │ Specs    │ │
              │  │              │ │          │ │ (Vega-L) │ │
              │  └──────────────┘ └──────────┘ └──────────┘ │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │              Output Formats                   │
              │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
              │  │  JSON    │ │  HTML    │ │  PDF Report  │ │
              │  │ (API)    │ │(inline   │ │ (executable  │ │
              │  │          │ │ charts)  │ │  summary)    │ │
              │  └──────────┘ └──────────┘ └──────────────┘ │
              └──────────────────────────────────────────────┘
```

### Flow

```
1. Ingestion ──► 2. Analysis ──► 3. Generation ──► 4. Formatting

Step 1: Parse raw data, validate schema, store as DataFrame
Step 2: Compute summary stats, detect trends, find anomalies, segment by dimensions
Step 3: LLM receives structured analysis + report template → narrative + recommendations
Step 4: Assemble final output with embedded visualizations (Vega-Lite JSON specs)
```

---

## Project Structure

```
projects/ai-analytics-assistant/
├── app/
│   ├── __init__.py
│   ├── config.py                    # Settings via pydantic-settings
│   ├── schemas.py                   # Pydantic models for data, analysis, reports
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── parser.py                # Auto-detect format (JSONL, CSV, Parquet)
│   │   ├── validator.py             # Type checking, range validation, schema inference
│   │   └── loader.py                # Load into internal DataFrame representation
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── summary.py               # Descriptive stats: mean, median, p50/p95/p99, counts
│   │   ├── trends.py                # Time-series trend detection (linear, seasonal)
│   │   ├── anomalies.py             # Statistical anomaly detection (IQR, z-score, MAD)
│   │   ├── segmentation.py          # Group-by dimension analysis
│   │   ├── correlation.py           # Pairwise metric correlations
│   │   ├── comparison.py            # Period-over-period and cohort comparisons
│   │   └── pipeline.py              # Orchestrate analysis steps
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── llm.py                   # LLM call abstraction
│   │   ├── prompts.py               # Prompt templates per report type
│   │   ├── narrative.py             # Narrative structure builder
│   │   ├── recommendations.py       # Actionable insight generation
│   │   └── visualization.py         # Vega-Lite spec generation
│   │
│   ├── output/
│   │   ├── __init__.py
│   │   ├── report.py                # Report data model
│   │   ├── html_renderer.py         # Jinja2 HTML report with embedded charts
│   │   ├── json_serializer.py       # Machine-readable JSON output
│   │   └── pdf_renderer.py          # PDF via WeasyPrint
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes.py                # FastAPI routes (report, analyze, templates)
│       └── dependencies.py
│
├── templates/
│   ├── executive_summary.html        # Jinja2 HTML report template
│   ├── weekly_brief.html             # Weekly metrics digest template
│   └── incident_report.html          # Post-incident analysis template
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_ingestion.py
│   ├── test_analysis.py
│   ├── test_generation.py
│   └── test_output.py
│
├── data/
│   ├── sample_logs.jsonl             # Sample raw log data
│   ├── sample_metrics.csv            # Sample time-series metrics
│   └── sample_reports/               # Example generated reports
│
├── notebooks/
│   └── explore_analysis.ipynb
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Ingestion

### Supported Formats

| Format | Detection | Parser | Metadata Extracted |
|---|---|---|---|
| JSONL | `.jsonl` extension + first line parse | `json.loads` per line | field names, types, cardinality |
| CSV | `.csv` extension | `pandas.read_csv` | columns, dtypes, row count |
| Parquet | `.parquet` extension | `pandas.read_parquet` | schema, stats, row count |
| Excel | `.xlsx` extension | `pandas.read_excel` | sheet names, column types |

### Auto Schema Detection

```python
class SchemaDetector:
    def detect(self, data: list[dict]) -> TableSchema:
        return TableSchema(
            columns=[
                ColumnSchema(
                    name=field,
                    dtype=self.infer_type(values),
                    null_ratio=sum(1 for v in values if v is None) / len(values),
                    cardinality=len(set(v for v in values if v is not None)),
                    min=min(values) if numeric else None,
                    max=max(values) if numeric else None,
                )
                for field, values in self.collect_columns(data)
            ],
            row_count=len(data),
            temporal_columns=self.find_temporal_columns(data),
            metric_columns=self.find_numeric_columns(data),
            dimension_columns=self.find_categorical_columns(data),
        )
```

---

## Analysis

### Summary Statistics

```python
class SummaryAnalyzer:
    def analyze(self, df: DataFrame, metrics: list[str], dimensions: list[str]) -> SummaryResult:
        return SummaryResult(
            overall={
                m: {
                    "mean": df[m].mean(),
                    "median": df[m].median(),
                    "p50": df[m].quantile(0.5),
                    "p95": df[m].quantile(0.95),
                    "p99": df[m].quantile(0.99),
                    "min": df[m].min(),
                    "max": df[m].max(),
                    "std": df[m].std(),
                    "sum": df[m].sum(),
                    "count": df[m].count(),
                }
                for m in metrics
            },
            by_dimension={
                d: {
                    group: {m: group_df[m].mean() for m in metrics}
                    for group, group_df in df.groupby(d)
                }
                for d in dimensions
            },
        )
```

### Trend Detection

| Method | Description | Best For |
|---|---|---|
| **Linear regression** | Slope + confidence interval | Steady upward/downward trends |
| **Moving average** | 7-day / 30-day rolling avg | Smoothing noise in daily metrics |
| **Seasonal decomposition** | STL: trend + seasonal + residual | Weekly/monthly patterns |
| **Change point detection** | PELT algorithm | Identifying when a metric changed |

```python
class TrendAnalyzer:
    def analyze(self, df: DataFrame, metric: str, time_col: str) -> TrendResult:
        return TrendResult(
            metric=metric,
            direction="up" | "down" | "stable",
            slope=0.023,                    # Units per day
            p_value=0.001,                  # Statistical significance
            change_points=["2026-06-15"],   # Dates of significant changes
            seasonality="weekly",           # Detected seasonal pattern
            moving_avg_7d=[...],            # 7-day rolling averages
        )
```

### Anomaly Detection

| Method | Statistic | Threshold | Use |
|---|---|---|---|
| **IQR** | Q3 – Q1 | 1.5× IQR beyond Q1/Q3 | Univariate outliers |
| **Z-score** | (x – μ) / σ | > 3.0 or < -3.0 | Normally distributed metrics |
| **MAD** | median absolute deviation | > 3.5 MAD | Robust to outliers |
| **Percentile** | Relative to historical window | > p99 or < p01 | Lag-sensitive detection |

```python
class AnomalyDetector:
    def detect(self, df: DataFrame, metric: str) -> list[Anomaly]:
        anomalies = []
        for method in [self.iqr, self.zscore, self.mad]:
            anomalies.extend(method(df, metric))
        # Deduplicate and rank by severity
        return self.rank(anomalies)
```

### Segmentation

```python
class SegmentationAnalyzer:
    def segment(self, df: DataFrame, metric: str, dimension: str) -> list[Segment]:
        """Analyze how a metric breaks down by a categorical dimension."""
        groups = df.groupby(dimension)
        return [
            Segment(
                value=group_value,
                metric_mean=group_df[metric].mean(),
                metric_total=group_df[metric].sum(),
                percentage=group_df[metric].sum() / df[metric].sum() * 100,
                change_vs_prior=compute_change(group_df, group_value),
            )
            for group_value, group_df in groups
        ]
```

---

## LLM Generation

### Report Structure

Each report has three sections generated by the LLM:

```
┌────────────────────────────────────────────────────┐
│  1. Executive Summary (2–3 paragraphs)             │
│     • Key metrics and their current state          │
│     • Most significant changes                     │
│     • Overall health assessment                    │
├────────────────────────────────────────────────────┤
│  2. Key Insights (bullet points with data)         │
│     • What happened (data-driven observations)     │
│     • Why it matters (business impact)             │
│     • Notable anomalies or outliers                │
├────────────────────────────────────────────────────┤
│  3. Recommendations (prioritized actions)          │
│     • Immediate actions (high impact, low effort)  │
│     • Short-term improvements                      │
│     • Strategic initiatives                        │
└────────────────────────────────────────────────────┘
```

### Prompt Template

```
You are an executive data analyst. Given the following structured analysis of {dataset_name},
produce a concise executive report.

TIME PERIOD: {start_date} to {end_date}
PREVIOUS PERIOD: {prior_start_date} to {prior_end_date}

SUMMARY STATISTICS:
{summary_stats}

TRENDS:
{trend_analysis}

ANOMALIES DETECTED:
{anomalies}

SEGMENTATION BY KEY DIMENSIONS:
{segmentation}

TOP CHANGES VS PRIOR PERIOD:
{comparisons}

INSTRUCTIONS:
- Write in {tone} tone (concise, detailed, or urgent).
- Keep the executive summary under 200 words.
- Each insight must cite a specific data point.
- Recommendations must be actionable and prioritized.
- Do NOT mention that you are an AI.
- Use metric names exactly as provided.

OUTPUT FORMAT:
{output_schema}
```

### Tone Profiles

| Tone | Use Case | Style |
|---|---|---|
| `concise` | Daily/weekly briefs | Bullet points, short sentences |
| `detailed` | Monthly/quarterly reviews | Paragraphs, full context |
| `urgent` | Incident or alert-triggered | Bold highlights, immediate actions |

### Visualization (Vega-Lite)

The LLM generates Vega-Lite JSON specs for key charts embedded in the report:

```json
{
  "chart_specs": [
    {
      "id": "revenue_trend",
      "title": "Daily Revenue (30 days)",
      "type": "line",
      "vega_lite": {
        "mark": {"type": "line", "point": true},
        "encoding": {
          "x": {"field": "date", "type": "temporal"},
          "y": {"field": "revenue", "type": "quantitative"}
        }
      }
    }
  ]
}
```

Supported chart types: `line`, `bar`, `area`, `heatmap`, `table`.

### Alternative: Chart Template Selection

Rather than LLM-generated specs (which can be unreliable), a safer approach is template-based chart selection:

```python
class ChartSelector:
    def select_charts(self, analysis: AnalysisResult) -> list[ChartSpec]:
        charts = []
        # Always include: trend line for every metric
        for metric in analysis.metrics:
            charts.append(self.trend_line(metric))

        # Include bar chart for top segmentation dimension
        if analysis.segmentations:
            top_dim = analysis.segmentations[0]
            charts.append(self.segmentation_bar(top_dim))

        # Include anomaly highlight if anomalies found
        if analysis.anomalies:
            charts.append(self.anomaly_scatter(analysis.anomalies))

        return charts
```

---

## Output Formats

### HTML Report

Jinja2 template with embedded Vega-Lite visualizations rendered via `vega-embed`:

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
</head>
<body>
  <h1>{{ report.title }}</h1>
  <p class="period">{{ report.period }}</p>

  <section class="executive-summary">
    <h2>Executive Summary</h2>
    {{ report.executive_summary | markdown }}
  </section>

  <section class="insights">
    <h2>Key Insights</h2>
    {% for insight in report.insights %}
      <div class="insight-card">
        <p>{{ insight.text }}</p>
        <div id="chart-{{ insight.chart_id }}"></div>
      </div>
    {% endfor %}
  </section>

  <section class="recommendations">
    <h2>Recommendations</h2>
    {% for rec in report.recommendations %}
      <div class="rec-{{ rec.priority }}">
        <span class="priority-badge">{{ rec.priority }}</span>
        <p>{{ rec.text }}</p>
      </div>
    {% endfor %}
  </section>
</body>
</html>
```

### JSON (API Response)

```json
{
  "report_id": "rpt_abc123",
  "title": "Weekly Executive Brief — Engineering",
  "period": { "start": "2026-06-20", "end": "2026-06-27" },
  "generated_at": "2026-06-27T12:00:00Z",
  "executive_summary": "Revenue grew 12% week-over-week driven by...",
  "insights": [
    {
      "text": "API latency p95 increased from 320ms to 480ms (+50%) starting June 25.",
      "severity": "warning",
      "metric": "latency_p95",
      "change_pct": 50.0,
      "chart_id": "latency_trend"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "text": "Investigate the latency spike on June 25. Check database connection pool saturation.",
      "category": "performance"
    }
  ],
  "charts": {
    "latency_trend": { "vega_lite": { ... } },
    "revenue_trend": { "vega_lite": { ... } }
  },
  "metadata": {
    "data_sources": ["api_logs_2026-06"],
    "analysis_duration_ms": 450,
    "generation_duration_ms": 3200,
    "model": "gpt-4o-mini"
  }
}
```

### PDF

- Uses WeasyPrint to convert HTML → PDF
- Static chart rendering (Vega-Lite → SVG → embedded in HTML)
- Suitable for email distribution, compliance records, stakeholder decks

---

## Pre-Built Report Templates

### Executive Summary

| Element | Description |
|---|---|
| Frequency | Daily or weekly |
| Audience | Engineering manager, VP |
| Length | 1 page |
| Charts | Metric trend lines (3–5 key metrics) |
| Sections | Summary → Insights → Recommendations |

### Weekly Brief

| Element | Description |
|---|---|
| Frequency | Weekly |
| Audience | Director, CTO |
| Length | 2–3 pages |
| Charts | Trends + segmentation + anomaly callouts |
| Sections | Summary → Team-level breakdown → Project status → Recommendations |

### Incident Report

| Element | Description |
|---|---|
| Frequency | On incident |
| Audience | On-call, engineering lead, stakeholders |
| Length | 1 page |
| Charts | Timeline, metric before/during/after |
| Sections | Summary → Timeline → Root cause → Impact → Action items |

---

## API

### `POST /api/v1/report/generate`

Generate a report from raw data or a pre-processed analysis.

**Request:**
```json
{
  "data_source": {
    "type": "inline",
    "format": "jsonl",
    "content": [
      {"date": "2026-06-20", "revenue": 12000, "latency_p95": 320},
      {"date": "2026-06-21", "revenue": 13500, "latency_p95": 310}
    ]
  },
  "config": {
    "report_type": "executive_summary",
    "tone": "concise",
    "metrics": ["revenue", "latency_p95"],
    "dimensions": [],
    "time_column": "date",
    "comparison_period": "previous_week"
  }
}
```

**Response:**
```json
{
  "report_id": "rpt_abc123",
  "title": "Executive Summary — June 20-27",
  "executive_summary": "Revenue increased 12.5% week-over-week, reaching $94,500. API latency degraded mid-week with a p95 spike to 480ms...",
  "insights": [...],
  "recommendations": [...],
  "charts": {...},
  "formats": {
    "json": "/api/v1/report/rpt_abc123/json",
    "html": "/api/v1/report/rpt_abc123/html",
    "pdf": "/api/v1/report/rpt_abc123/pdf"
  }
}
```

### `GET /api/v1/report/{report_id}/{format}`

Retrieve report in specific format (`json`, `html`, `pdf`).

### `POST /api/v1/analyze`

Run analysis only — no LLM generation. Useful for debugging structured analysis output.

### `GET /api/v1/templates`

List available report templates with descriptions and expected inputs.

---

## Monitoring

| Metric | Type | Labels | Description |
|---|---|---|---|
| `reports_generated_total` | Counter | report_type | Total reports generated |
| `analysis_duration_ms` | Histogram | report_type | Data analysis phase latency |
| `generation_duration_ms` | Histogram | report_type, model | LLM generation phase latency |
| `total_duration_ms` | Histogram | report_type | End-to-end report latency |
| `generation_tokens` | Histogram | model | Tokens used per report |
| `generation_cost_usd` | Counter | model, report_type | LLM cost per report |
| `report_size_bytes` | Histogram | format | Output size per format |
| `analysis_rows_processed` | Histogram | report_type | Data volume processed |

Alert when:
- `generation_duration_ms` p95 exceeds 15s (prompt too large or model slow)
- `generation_cost_usd` daily total exceeds budget
- Report generation failure rate > 5%
- Analysis phase fails on > 1% of requests (schema mismatch)

---

## Tech Stack

| Component | Choice | Justification |
|---|---|---|
| Framework | FastAPI + uvicorn | Consistent with other projects |
| Data analysis | pandas + numpy | Industry standard for tabular analysis |
| Trend detection | `statsmodels` (STL, linear regression) | Robust statistical methods |
| Anomaly detection | `scipy` (z-score, IQR) + custom MAD | Lightweight, no external API |
| LLM | GPT-4o-mini (primary), GPT-4o (complex reports) | Cost-effective, good quality |
| Visualization | Vega-Lite JSON specs + `vega-embed` | Declarative, render in any browser |
| HTML templates | Jinja2 | Python-native, well-known |
| PDF | WeasyPrint (HTML → PDF) | Full CSS support, consistent layout |
| Caching | Redis | Cache analysis results, rate limit LLM calls |
| Monitoring | Prometheus + Grafana | Consistent with other projects |

---

## Implementation Phases

| Phase | Files | Deliverable |
|---|---|---|
| **1** | `config.py`, `schemas.py`, `ingestion/*` | Data ingestion with auto-schema detection |
| **2** | `analysis/summary.py`, `analysis/trends.py` | Summary stats + trend detection |
| **3** | `analysis/anomalies.py`, `analysis/segmentation.py`, `analysis/correlation.py`, `analysis/comparison.py` | Anomaly detection, segmentation, correlation, comparison |
| **4** | `analysis/pipeline.py` | Analysis pipeline orchestrator |
| **5** | `generation/prompts.py`, `generation/narrative.py`, `generation/recommendations.py`, `generation/visualization.py` | LLM prompts, narrative builder, recommendations, chart specs |
| **6** | `generation/llm.py` | LLM call abstraction |
| **7** | `output/report.py`, `output/html_renderer.py`, `output/json_serializer.py`, `output/pdf_renderer.py` | Output formatting |
| **8** | `api/*`, `templates/*` | FastAPI routes + HTML templates |
| **9** | Tests + `data/sample_*` | Verification, sample data |
| **10** | Notebooks + README | Exploration, documentation |

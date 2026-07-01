# 07 - Monitoring: Prometheus + Grafana for Model Serving

## Overview

Add Prometheus metrics instrumentation to the FastAPI model server from Project 04, then visualize those metrics in a local Grafana dashboard. Track request latency (histogram), request count (counter), and prediction distribution (gauge).

## Tech Stack

- **Metrics** — Prometheus client library (`prometheus_client` or FastAPI integration via `starlette_exporter`)
- **Scraping** — Prometheus server (local Docker instance)
- **Visualization** — Grafana (local Docker instance)
- **Model server** — FastAPI (from Project 04)

## Architecture & Design

```
┌─────────────────┐     scrape (/metrics)     ┌──────────────┐
│  FastAPI server  │ ◄───────────────────────── │  Prometheus   │
│  (port 8080)     │                           │  (port 9090)  │
│                  │                           └──────┬───────┘
│  Metrics:        │                                  │
│  ├─ http_requests_total (counter)                    │ PromQL queries
│  ├─ http_request_duration_seconds (histogram)        │
│  └─ prediction_distribution (gauge)                  ▼
└─────────────────┘                           ┌──────────────┐
                                              │  Grafana      │
                                              │  (port 3000)  │
                                              │              │
                                              │  Dashboard:  │
                                              │  ├─ RPS graph │
                                              │  ├─ P50/P95   │
                                              │  └─ class %   │
                                              └──────────────┘
```

**Design decisions:**

- **Three metric types** are all you need for 80% of ML monitoring:
  - **Counter** — `http_requests_total` by endpoint and status code. Rate over time = requests per second.
  - **Histogram** — `http_request_duration_seconds`. Gives you P50, P95, P99 latency without pre-computing percentiles.
  - **Gauge** — `prediction_distribution` by class. Monitors prediction drift — if class 1 suddenly goes from 30% to 70%, something changed.
- **Docker Compose** to run Prometheus + Grafana locally. No cloud costs, instant setup, and the config files are portable to a production deployment.
- **`/metrics` endpoint** is the standard Prometheus scrape target. The model server doesn't push metrics — Prometheus pulls them on a configurable interval (default 15s).

## Setup & Run

1. Add Prometheus instrumentation to the FastAPI server:
   ```python
   # app.py (additions)
   from prometheus_client import Counter, Histogram, Gauge, generate_latest
   from fastapi.responses import Response
   import time

   REQUEST_COUNT = Counter("http_requests_total", "Total requests",
                           ["endpoint", "status"])
   LATENCY = Histogram("http_request_duration_seconds", "Request latency",
                       ["endpoint"], buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5])
   PRED_DIST = Gauge("prediction_distribution", "Prediction class distribution",
                     ["class"])

   @app.middleware("http")
   async def monitor(request, call_next):
       start = time.time()
       response = await call_next(request)
       LATENCY.labels(endpoint=request.url.path).observe(time.time() - start)
       REQUEST_COUNT.labels(endpoint=request.url.path,
                            status=response.status_code).inc()
       return response

   @app.get("/metrics")
   def metrics():
       return Response(content=generate_latest(), media_type="text/plain")
   ```
2. Run Prometheus and Grafana via Docker Compose:
   ```yaml
   # docker-compose.yml
   version: "3"
   services:
     prometheus:
       image: prom/prometheus
       ports: ["9090:9090"]
       volumes:
         - ./prometheus.yml:/etc/prometheus/prometheus.yml
     grafana:
       image: grafana/grafana
       ports: ["3000:3000"]
       environment:
         - GF_SECURITY_ADMIN_PASSWORD=admin
   ```
   ```yaml
   # prometheus.yml
   scrape_configs:
     - job_name: "model-server"
       static_configs:
         - targets: ["host.docker.internal:8080"]
   ```
3. Open Grafana at `http://localhost:3000` (admin/admin), add Prometheus as a data source (`http://prometheus:9090`), and build a dashboard:
   - **Panel 1** — Rate of `http_requests_total` (requests/sec)
   - **Panel 2** — P50/P95 of `http_request_duration_seconds` (latency)
   - **Panel 3** — `prediction_distribution` per class (stacked graph)
4. Generate traffic and watch the dashboard:
   ```bash
   for i in {1..100}; do curl -X POST http://localhost:8080/predict ...; done
   ```

## What You Learn

- The three essential metric types: counter, histogram, gauge — and when to use each
- Prometheus pull-based monitoring vs. push-based alternatives
- The four golden signals of ML monitoring: latency, traffic, errors, saturation — plus prediction distribution (the fifth, ML-specific signal)
- Building a Grafana dashboard from raw PromQL queries
- Instrumenting code without modifying business logic (middleware pattern)
- Observing how changes (model version, traffic spike, data shift) appear in metrics before they cause outages

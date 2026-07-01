"""
Observability and distributed tracing for LLM inference requests.

Run: python 09-observability-tracing.py

Requirements: numpy
"""

import time
import json
import hashlib
import uuid
from collections import defaultdict

print("=== Observability & Distributed Tracing ===\n")

class Span:
    def __init__(self, name, trace_id, parent_span_id=None):
        self.span_id = hashlib.md5(f"{name}{time.time()}{uuid.uuid4()}".encode()).hexdigest()[:16]
        self.trace_id = trace_id
        self.parent_span_id = parent_span_id
        self.name = name
        self.start_time = time.time()
        self.end_time = None
        self.attributes = {}
        self.status = "ok"
        self.events = []

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def add_event(self, name, attributes=None):
        self.events.append({"name": name, "timestamp": time.time(), "attributes": attributes or {}})

    def close(self):
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)

    def to_dict(self):
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "duration_ms": getattr(self, "duration_ms", 0),
            "status": self.status,
            "attributes": self.attributes,
            "events": len(self.events),
        }

class Tracer:
    def __init__(self):
        self.spans = []

    def start_span(self, name, trace_id=None, parent_span_id=None):
        if trace_id is None:
            trace_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
        span = Span(name, trace_id, parent_span_id)
        self.spans.append(span)
        return span

    def get_trace(self, trace_id):
        return [s for s in self.spans if s.trace_id == trace_id]

class StructuredLogger:
    def __init__(self):
        self.logs = []

    def log(self, level, message, **kwargs):
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs,
        }
        self.logs.append(entry)
        return entry

    def query(self, level=None, service=None):
        results = self.logs
        if level:
            results = [r for r in results if r["level"] == level]
        if service:
            results = [r for r in results if r.get("service") == service]
        return results

class MetricsExporter:
    def __init__(self):
        self.counters = defaultdict(int)
        self.histograms = defaultdict(list)

    def increment(self, name, value=1):
        self.counters[name] += value

    def record_value(self, name, value):
        self.histograms[name].append(value)

    def snapshot(self):
        result = {}
        for k, v in self.counters.items():
            result[f"counter_{k}"] = v
        for k, v in self.histograms.items():
            if v:
                result[f"hist_{k}_mean"] = round(sum(v) / len(v), 2)
                result[f"hist_{k}_max"] = round(max(v), 2)
                result[f"hist_{k}_count"] = len(v)
        return result

tracer = Tracer()
logger = StructuredLogger()
metrics = MetricsExporter()

print("=== Simulating Request Traces ===")

def simulate_request(user_id, query):
    trace_id = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:16]
    root_span = tracer.start_span("llm_request", trace_id)
    root_span.set_attribute("user_id", user_id)
    root_span.set_attribute("query_length", len(query))
    logger.log("INFO", "Request received", service="gateway", user_id=user_id, trace_id=trace_id)
    metrics.increment("requests_total")

    input_span = tracer.start_span("input_guardrail", trace_id, root_span.span_id)
    time.sleep(0.001)
    input_span.set_attribute("action", "pass")
    input_span.set_attribute("score", 0.02)
    input_span.add_event("guardrail_check_complete", {"checks_passed": 5})
    input_span.close()
    logger.log("INFO", "Input guardrail passed", service="guardrail", trace_id=trace_id)

    inference_span = tracer.start_span("llm_inference", trace_id, root_span.span_id)
    time.sleep(0.005)
    inference_span.set_attribute("model", "gpt-4o-mini")
    inference_span.set_attribute("temperature", 0.3)
    inference_span.set_attribute("prompt_tokens", 450)
    inference_span.set_attribute("completion_tokens", 120)
    inference_span.set_attribute("latency_ms", 320)
    inference_span.add_event("inference_complete")
    inference_span.close()
    metrics.increment("inference_count")
    metrics.record_value("inference_latency", 320)
    logger.log("INFO", "Inference complete", service="model-server", trace_id=trace_id,
               tokens=570, latency_ms=320)

    output_span = tracer.start_span("output_guardrail", trace_id, root_span.span_id)
    time.sleep(0.001)
    output_span.set_attribute("action", "pass")
    output_span.set_attribute("toxicity_score", 0.001)
    output_span.close()
    logger.log("INFO", "Output guardrail passed", service="guardrail", trace_id=trace_id)

    root_span.set_attribute("total_latency_ms", 360)
    root_span.close()
    metrics.record_value("request_latency", 360)
    logger.log("INFO", "Request complete", service="gateway", trace_id=trace_id, total_latency_ms=360)

    return trace_id

queries = [
    ("user_001", "What is the capital of France?"),
    ("user_002", "Explain quantum computing in simple terms."),
    ("user_003", "Write a Python decorator for logging."),
]

trace_ids = []
for uid, query in queries:
    tid = simulate_request(uid, query)
    trace_ids.append(tid)
    print(f"  Trace {tid[:12]}...: {uid} - {query[:40]}...")

print()

print("=== Trace Details (First Request) ===")
trace_id = trace_ids[0]
spans = tracer.get_trace(trace_id)
print(f"  Trace ID: {trace_id}")
print(f"  {'Span Name':<25} {'Duration':>10} {'Parent':>18} {'Status':<8}")
print("  " + "-" * 65)
for s in sorted(spans, key=lambda x: x.duration_ms if hasattr(x, 'duration_ms') else 0):
    dur = f"{getattr(s, 'duration_ms', 0):.1f}ms"
    parent = s.parent_span_id[:8] if s.parent_span_id else "root"
    print(f"  {s.name:<25} {dur:>10} {parent:>18} {s.status:<8}")

print()

print("=== Structured Logs ===")
error_logs = logger.query(level="ERROR")
info_logs = logger.query(level="INFO")
print(f"  INFO logs:  {len(info_logs)}")
print(f"  ERROR logs: {len(error_logs)}")
print()
print("  Sample log entries:")
for log in info_logs[:3]:
    ts = time.strftime("%H:%M:%S", time.localtime(log["timestamp"]))
    print(f"    {ts} [{log['level']}] {log['message']} (service={log.get('service','?')})")

print()

print("=== Metrics Snapshot ===")
snap = metrics.snapshot()
for k, v in sorted(snap.items()):
    print(f"  {k}: {v}")

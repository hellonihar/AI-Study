"""
Distributed tracing: trace spans across multi-agent calls.

Run: python 08-distributed-tracing.py

Requirements: none (stdlib only)
"""

import json
import time
import uuid
from datetime import datetime

print("=== Distributed Tracing ===\n")

class Span:
    def __init__(self, name, agent, parent_span_id=None, trace_id=None):
        self.span_id = uuid.uuid4().hex[:8]
        self.trace_id = trace_id or uuid.uuid4().hex[:8]
        self.parent_span_id = parent_span_id
        self.name = name
        self.agent = agent
        self.start_time = time.time()
        self.end_time = None
        self.status = "pending"
        self.error = None
        self.metadata = {}

    def finish(self, status="success"):
        self.end_time = time.time()
        self.status = status

    def duration_ms(self):
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

    def to_dict(self):
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "agent": self.agent,
            "duration_ms": round(self.duration_ms(), 1),
            "status": self.status,
            "error": self.error,
        }

class Trace:
    def __init__(self):
        self.trace_id = uuid.uuid4().hex[:8]
        self.spans = []
        self.start_time = time.time()

    def start_span(self, name, agent, parent_span_id=None):
        span = Span(name, agent, parent_span_id, self.trace_id)
        self.spans.append(span)
        return span

    def summary(self):
        total = sum(s.duration_ms() for s in self.spans)
        return {
            "trace_id": self.trace_id,
            "total_spans": len(self.spans),
            "total_duration_ms": round(total, 1),
            "agents": list(set(s.agent for s in self.spans)),
            "status": "success" if all(s.status == "success" for s in self.spans) else "has_errors",
        }

trace = Trace()

print("Executing multi-agent task with tracing:\n")

root = trace.start_span("orchestrator", "supervisor")
print(f"  [Span {root.span_id}] supervisor: orchestrator (enter)")
time.sleep(0.02)

search_span = trace.start_span("search", "search_agent", root.span_id)
print(f"  [Span {search_span.span_id}] search_agent: search")
time.sleep(0.03)

sub_search = trace.start_span("search_web", "search_agent", search_span.span_id)
print(f"    [Span {sub_search.span_id}] search_agent: search_web")
time.sleep(0.02)
sub_search.finish()

sub_extract = trace.start_span("extract_results", "search_agent", search_span.span_id)
print(f"    [Span {sub_extract.span_id}] search_agent: extract_results")
time.sleep(0.01)
sub_extract.finish()

search_span.finish()

analyze_span = trace.start_span("analyze", "analyze_agent", root.span_id)
print(f"  [Span {analyze_span.span_id}] analyze_agent: analyze")
time.sleep(0.04)

sub_classify = trace.start_span("classify", "analyze_agent", analyze_span.span_id)
print(f"    [Span {sub_classify.span_id}] analyze_agent: classify")
time.sleep(0.015)
sub_classify.finish(status="error")
sub_classify.error = "Classification confidence below threshold"
analyze_span.finish()

format_span = trace.start_span("format", "format_agent", root.span_id)
print(f"  [Span {format_span.span_id}] format_agent: format")
time.sleep(0.02)
format_span.finish()

root.finish()

print(f"\n{'='*60}")
print("Trace Visualization")
print(f"{'='*60}")
print(f"  Trace ID: {trace.trace_id}")
print()

root_span = trace.spans[0]
for span in trace.spans:
    indent = "  " if span.parent_span_id == root_span.span_id else ""
    if span.parent_span_id != root_span.span_id and span.parent_span_id != root_span.span_id:
        if not any(s.span_id == span.parent_span_id and s.parent_span_id == root_span.span_id
                   for s in trace.spans):
            continue
        indent = "    "
    icon = "✓" if span.status == "success" else "✗"
    print(f"  {indent}[{icon}] {span.agent:<20} {span.name:<20} "
          f"{span.duration_ms():.1f}ms  {span.status}")

print(f"\n{'='*60}")
print("Trace Summary")
print(f"{'='*60}")
summary = trace.summary()
for k, v in summary.items():
    print(f"  {k}: {v}")

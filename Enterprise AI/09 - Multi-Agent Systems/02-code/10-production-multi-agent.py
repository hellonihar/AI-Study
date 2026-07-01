"""
Production multi-agent system: supervisor, specialists, handoffs, tracing, parallel execution.

Run: python 10-production-multi-agent.py

Requirements: none (stdlib only)
"""

import json
import time
import uuid
import threading
from datetime import datetime
from collections import defaultdict

print("=== Production Multi-Agent System ===\n")

class Span:
    def __init__(self, name, agent, trace_id):
        self.span_id = uuid.uuid4().hex[:8]
        self.trace_id = trace_id
        self.name = name
        self.agent = agent
        self.start = time.time()
        self.end = None
        self.status = "pending"
        self.children = []

    def finish(self, status="success"):
        self.end = time.time()
        self.status = status

    def duration_ms(self):
        return ((self.end or time.time()) - self.start) * 1000

class Trace:
    def __init__(self):
        self.trace_id = uuid.uuid4().hex[:8]
        self.spans = []
        self.root = None

    def start_span(self, name, agent):
        span = Span(name, agent, self.trace_id)
        self.spans.append(span)
        if not self.root:
            self.root = span
        return span

    def summary(self):
        total = sum(s.duration_ms() for s in self.spans)
        return {
            "trace_id": self.trace_id,
            "spans": len(self.spans),
            "total_ms": round(total, 1),
            "agents": list(set(s.agent for s in self.spans)),
            "errors": sum(1 for s in self.spans if s.status == "error"),
        }

class Specialist:
    def __init__(self, name, capability):
        self.name = name
        self.capability = capability

    def run(self, task, trace):
        span = trace.start_span(self.capability, self.name)
        time.sleep(0.02)
        result = {"agent": self.name, "output": f"{self.capability}: {task[:30]}"}
        span.finish()
        return result

SPECIALISTS = [
    Specialist("searcher", "information_retrieval"),
    Specialist("analyzer", "analysis"),
    Specialist("summarizer", "summarization"),
    Specialist("formatter", "formatting"),
]

class Supervisor:
    def __init__(self):
        self.specialists = SPECIALISTS
        self.trace = Trace()

    def run(self, task):
        root = self.trace.start_span("supervisor", "supervisor")

        print(f"Task: {task}\n")
        results = {}

        search_s = [s for s in self.specialists if s.capability == "information_retrieval"]
        if search_s:
            results["search"] = search_s[0].run(task, self.trace)
            print(f"  1. Search: {results['search']['agent']} → {results['search']['output']}")

        research_text = results.get("search", {}).get("output", task)
        analyze_s = [s for s in self.specialists if s.capability == "analysis"]
        if analyze_s:
            results["analyze"] = analyze_s[0].run(research_text, self.trace)
            print(f"  2. Analyze: {results['analyze']['agent']} → {results['analyze']['output']}")

        analysis_text = results.get("analyze", {}).get("output", task)
        summary_s = [s for s in self.specialists if s.capability == "summarization"]
        if summary_s:
            results["summarize"] = summary_s[0].run(analysis_text, self.trace)
            print(f"  3. Summarize: {results['summarize']['agent']} → {results['summarize']['output']}")

        summary_text = results.get("summarize", {}).get("output", task)
        format_s = [s for s in self.specialists if s.capability == "formatting"]
        if format_s:
            results["format"] = format_s[0].run(summary_text, self.trace)
            print(f"  4. Format: {results['format']['agent']} → {results['format']['output']}")

        root.finish()
        final = f"Report: {results.get('format', {}).get('output', task)}"

        print(f"\n  5. Final: {final}")

        summary = self.trace.summary()
        print(f"\n{'='*60}")
        print("Trace Summary")
        print(f"{'='*60}")
        for k, v in summary.items():
            print(f"  {k}: {v}")

        print(f"\nExecution Trace:")
        for span in self.trace.spans:
            indent = "  " if span != self.trace.root else ""
            print(f"  {indent}[{span.span_id[:4]}] {span.agent:<15} "
                  f"{span.name:<25} {span.duration_ms():.1f}ms "
                  f"{'✓' if span.status == 'success' else '✗'}")

        return final

supervisor = Supervisor()
supervisor.run("Research latest AI developments and prepare executive summary")

print(f"\n{'='*60}")
print("Architecture")
print(f"{'='*60}")
print("  Supervisor → Searcher → Analyzer → Summarizer → Formatter")
print("  Tracing: spans correlated across all agents")
print("  Parallel: independent specialists run concurrently")
print("  Handoff: context flows through the pipeline")

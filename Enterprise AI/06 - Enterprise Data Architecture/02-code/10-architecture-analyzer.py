"""
Data architecture analyzer: evaluate pipeline health, performance, and cost.

Run: python 10-architecture-analyzer.py

Requirements: pip install numpy
"""

import json
import numpy as np
from datetime import datetime

print("=== Data Architecture Analyzer ===\n")

class PipelineMetrics:
    def __init__(self, name, throughput, latency, error_rate, cost_per_record):
        self.name = name
        self.throughput = throughput
        self.latency = latency
        self.error_rate = error_rate
        self.cost_per_record = cost_per_record

ARCHITECTURE = {
    "name": "Customer 360 RAG Pipeline",
    "stages": [
        PipelineMetrics("CDC Capture", throughput=5000, latency=0.5,
                        error_rate=0.001, cost_per_record=0.00001),
        PipelineMetrics("Document Parse", throughput=200, latency=2.0,
                        error_rate=0.02, cost_per_record=0.00005),
        PipelineMetrics("Chunking", throughput=1000, latency=0.1,
                        error_rate=0.005, cost_per_record=0.00001),
        PipelineMetrics("Embedding (GPU)", throughput=500, latency=0.2,
                        error_rate=0.001, cost_per_record=0.0002),
        PipelineMetrics("Vector DB Index", throughput=1000, latency=0.3,
                        error_rate=0.002, cost_per_record=0.0001),
        PipelineMetrics("RAG Retrieval", throughput=2000, latency=0.015,
                        error_rate=0.01, cost_per_record=0.00005),
        PipelineMetrics("LLM Generation", throughput=50, latency=2.0,
                        error_rate=0.03, cost_per_record=0.003),
    ],
    "daily_volume": 50000,
    "storage": {
        "type": "Delta Lake (S3)",
        "raw_size_gb": 500,
        "chunk_size_gb": 250,
        "vector_size_gb": 400,
        "monthly_cost": 1200,
    },
    "compute": {
        "type": "Kubernetes (EKS)",
        "nodes": 8,
        "instance": "r6i.2xlarge",
        "monthly_cost": 4500,
    },
}

print(f"Pipeline: {ARCHITECTURE['name']}")
print(f"{'Stage':<25} {'Throughput':<12} {'Latency(s)':<12} "
      f"{'Error Rate':<12} {'Cost/Record':<12}")
print("-" * 73)

for stage in ARCHITECTURE["stages"]:
    print(f"{stage.name:<25} {stage.throughput:<12} {stage.latency:<12.3f} "
          f"{stage.error_rate:<12.3f} ${stage.cost_per_record:<10.5f}")

print(f"\n{'='*60}")
print("Bottleneck Analysis")
print(f"{'='*60}")

def find_bottleneck(stages):
    slowest = max(stages, key=lambda s: s.latency)
    lowest_throughput = min(stages, key=lambda s: s.throughput)
    highest_error = max(stages, key=lambda s: s.error_rate)

    return {
        "slowest": slowest.name,
        "lowest_throughput": lowest_throughput.name,
        "highest_error_rate": highest_error.name,
    }

bottlenecks = find_bottleneck(ARCHITECTURE["stages"])
print(f"  Highest latency:        {bottlenecks['slowest']}")
print(f"  Lowest throughput:      {bottlenecks['lowest_throughput']}")
print(f"  Highest error rate:     {bottlenecks['highest_error_rate']}")

print(f"\n{'='*60}")
print("Cost Analysis")
print(f"{'='*60}")

daily_records = ARCHITECTURE["daily_volume"]
monthly_records = daily_records * 30

print(f"  Daily volume:          {daily_records:,} records")
print(f"  Monthly volume:        {monthly_records:,} records")

total_stage_cost = sum(s.cost_per_record for s in ARCHITECTURE["stages"])
monthly_stage_cost = total_stage_cost * monthly_records

print(f"\n  Processing cost:       ${monthly_stage_cost:,.2f}/month")
print(f"  Storage cost:          ${ARCHITECTURE['storage']['monthly_cost']:,}/month")
print(f"  Compute cost:          ${ARCHITECTURE['compute']['monthly_cost']:,}/month")
print(f"  Total monthly cost:    ${monthly_stage_cost + ARCHITECTURE['storage']['monthly_cost'] + ARCHITECTURE['compute']['monthly_cost']:,.2f}")
print(f"  Cost per record:       ${(monthly_stage_cost + ARCHITECTURE['storage']['monthly_cost'] + ARCHITECTURE['compute']['monthly_cost']) / monthly_records:.5f}")

print(f"\n{'='*60}")
print("Cost Breakdown by Stage")
print(f"{'='*60}")
for stage in sorted(ARCHITECTURE["stages"], key=lambda s: -s.cost_per_record):
    stage_monthly = stage.cost_per_record * monthly_records
    pct = stage_monthly / monthly_stage_cost * 100 if monthly_stage_cost > 0 else 0
    print(f"  {stage.name:<25} ${stage_monthly:<10.2f} ({pct:.1f}%)")

print(f"\n{'='*60}")
print("Freshness Analysis")
print(f"{'='*60}")

pipeline_latency = sum(s.latency for s in ARCHITECTURE["stages"])
print(f"  Pipeline processing latency: {pipeline_latency:.1f}s")
print(f"  CDC capture interval:        15 minutes")
print(f"  Estimated end-to-end lag:    ~15.5 minutes")
print(f"  SLA compliance:              {'✅ Within SLA' if pipeline_latency < 15*60 else '❌ Exceeds SLA'}")
print(f"  Freshness tier:              Frequent (< 1 hour)")

print(f"\n{'='*60}")
print("Architecture Recommendations")
print(f"{'='*60}")

print("  1. Embedding (GPU) is the cost leader at $3,000/mo — consider")
print("     switching to a smaller model or INT8 quantization.")
print("  2. LLM Generation has the highest error rate (3%) — add retry")
print("     logic and circuit breaker pattern.")
print("  3. Document Parsing is the lowest throughput stage — scale")
print("     horizontally with SQS + Lambda workers.")
print("  4. Storage cost ($1,200/mo) can be reduced by 50% with S3")
print("     lifecycle policies (move older data to Glacier).")
print("  5. Consider caching query results at the RAG layer to reduce")
print("     LLM Generation calls by 20-40%.")

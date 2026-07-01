"""
Streaming data ingestion simulation: event processing with sliding windows.

Run: python 07-streaming-simulation.py

Requirements: pip install numpy
"""

import time
import random
import json
from datetime import datetime, timedelta
from collections import defaultdict

print("=== Streaming Ingestion Simulation ===\n")

class EventSource:
    def __init__(self, rate_per_second=5):
        self.rate = rate_per_second
        self.event_types = [
            "document_created", "document_updated", "document_deleted",
            "embedding_requested", "embedding_completed",
            "query_received", "query_processed",
        ]

    def generate_events(self, duration_seconds):
        events = []
        start_time = datetime.utcnow()

        for _ in range(duration_seconds * self.rate):
            event = {
                "event_id": f"evt-{random.randint(10000, 99999)}",
                "event_type": random.choice(self.event_types),
                "timestamp": start_time.isoformat(),
                "source": random.choice(["api", "cdc", "webhook", "scheduler"]),
                "data": {
                    "doc_id": f"doc-{random.randint(1, 100)}",
                    "size_bytes": random.randint(100, 100000),
                    "processing_time_ms": random.randint(10, 500),
                },
            }
            events.append(event)
            start_time += timedelta(milliseconds=1000 / self.rate)

        return events

class StreamProcessor:
    def __init__(self, window_size_seconds=3):
        self.window_size = window_size_seconds
        self.buffer = []
        self.window_stats = defaultdict(int)

    def process_event(self, event):
        self.buffer.append(event)
        event_type = event["event_type"]
        self.window_stats[event_type] += 1
        self.window_stats["total"] += 1

    def process_window(self):
        if not self.buffer:
            return None

        stats = dict(self.window_stats)
        window_docs = list(self.buffer)

        self.buffer = []
        self.window_stats.clear()

        total_size = sum(e["data"]["size_bytes"] for e in window_docs)
        total_time = sum(e["data"]["processing_time_ms"] for e in window_docs)

        return {
            "window_start": window_docs[0]["timestamp"],
            "window_end": window_docs[-1]["timestamp"],
            "event_count": len(window_docs),
            "total_bytes": total_size,
            "avg_processing_time_ms": total_time / len(window_docs) if window_docs else 0,
            "event_types": dict(stats),
        }

source = EventSource(rate_per_second=5)
processor = StreamProcessor(window_size_seconds=2)

events = source.generate_events(duration_seconds=10)

print(f"Generated {len(events)} events over 10 seconds "
      f"(avg {len(events)/10:.1f} events/sec)\n")

print(f"{'Window':<8} {'Events':<8} {'Bytes':<12} {'Avg Time':<12} {'Types':<30}")
print("-" * 75)

windows_processed = 0
for i, event in enumerate(events):
    processor.process_event(event)

    elapsed = (datetime.fromisoformat(event["timestamp"]) -
               datetime.fromisoformat(events[0]["timestamp"])).total_seconds()

    if int(elapsed) % processor.window_size == 0 and elapsed > 0:
        result = processor.process_window()
        if result:
            windows_processed += 1
            type_str = ", ".join(
                f"{k}:{v}" for k, v in result["event_types"].items()
                if k != "total"
            )
            print(f"{windows_processed:<8} {result['event_count']:<8} "
                  f"{result['total_bytes']:<12} "
                  f"{result['avg_processing_time_ms']:<12.1f} "
                  f"{type_str[:30]:<30}")

if processor.buffer:
    result = processor.process_window()
    if result:
        windows_processed += 1
        type_str = ", ".join(
            f"{k}:{v}" for k, v in result["event_types"].items()
            if k != "total"
        )
        print(f"{windows_processed:<8} {result['event_count']:<8} "
              f"{result['total_bytes']:<12} "
              f"{result['avg_processing_time_ms']:<12.1f} "
              f"{type_str[:30]:<30}")

print(f"\n{'='*60}")
print(f"Streaming Pipeline Summary")
print(f"{'='*60}")
print(f"  Total events:             {len(events)}")
print(f"  Windows processed:        {windows_processed}")
print(f"  Avg events/second:        {len(events)/10:.1f}")
print(f"  Simulated rate:           5 events/sec")
print()

print("Streaming Architecture Components:")
print("  Source:    Kafka topic (5 partitions)")
print("  Processor: Flink / Kafka Streams (sliding window, 3s)")
print("  Sink:      Vector DB (batch upsert every 30s)")
print("  Checkpoint: S3 (exactly-once semantics)")
print()
print("For production, replace this simulation with:")
print("  pip install confluent-kafka     # Kafka client")
print("  pip install apache-flink         # Stream processor")
print("  # or use Kafka Streams / KSQL for simpler pipelines")

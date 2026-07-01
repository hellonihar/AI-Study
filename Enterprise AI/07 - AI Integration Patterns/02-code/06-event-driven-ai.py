"""
Event-driven AI: queue-based async processing with workers and DLQ.

Run: python 06-event-driven-ai.py

Requirements: none (stdlib only)
"""

import time
import json
import uuid
from datetime import datetime
from collections import deque

print("=== Event-Driven AI ===\n")

class TaskQueue:
    def __init__(self):
        self.queue = deque()
        self.dlq = deque()
        self.results = {}

    def enqueue(self, task):
        task_id = str(uuid.uuid4())[:8]
        task["task_id"] = task_id
        task["status"] = "pending"
        task["retry_count"] = 0
        task["created_at"] = datetime.utcnow().isoformat()
        self.queue.append(task)
        return task_id

    def dequeue(self):
        if not self.queue:
            return None
        task = self.queue.popleft()
        task["status"] = "processing"
        return task

    def complete(self, task):
        task["status"] = "completed"
        task["completed_at"] = datetime.utcnow().isoformat()
        self.results[task["task_id"]] = task

    def fail(self, task, error, requeue=True):
        if requeue and task["retry_count"] < 3:
            task["retry_count"] += 1
            task["status"] = "pending"
            task["last_error"] = error
            self.queue.append(task)
        else:
            task["status"] = "failed"
            task["error"] = error
            self.dlq.append(task)

    def depth(self):
        return len(self.queue)

class WorkerPool:
    def __init__(self, workers=3):
        self.workers = workers
        self.stats = {"processed": 0, "failed": 0, "dlq_count": 0}

    def process_task(self, task, queue):
        try:
            input_text = task.get("input", "")
            priority = task.get("priority", "normal")

            if not input_text:
                raise ValueError("Empty input")

            time.sleep(0.05 * {"high": 0.5, "normal": 1.0, "low": 2.0}.get(priority, 1.0))

            result = {
                "task_id": task["task_id"],
                "output": f"Processed: {input_text[:50]}...",
                "tokens_generated": len(input_text.split()) * 2,
            }

            queue.complete(task)
            self.stats["processed"] += 1
            return result

        except Exception as e:
            queue.fail(task, str(e))
            self.stats["failed"] += 1
            return None

    def run(self, queue, iterations=10):
        for i in range(iterations):
            task = queue.dequeue()
            if not task:
                time.sleep(0.01)
                continue

            worker_id = i % self.workers
            print(f"  Worker-{worker_id}: processing task {task['task_id']} "
                  f"(priority={task.get('priority', 'normal')})")
            self.process_task(task, queue)

queue = TaskQueue()

TASKS = [
    {"input": "Summarize quarterly financial report Q3 2024", "priority": "high"},
    {"input": "Classify support ticket: password reset not working", "priority": "high"},
    {"input": "Extract entities from customer feedback email", "priority": "normal"},
    {"input": "Generate embedding for product catalog page 42", "priority": "low"},
    {"input": "", "priority": "normal"},
    {"input": "Translate marketing copy from English to Spanish", "priority": "normal"},
    {"input": "Analyze sentiment of 1000 product reviews", "priority": "low"},
    {"input": "Answer: what is the return policy for electronics?", "priority": "high"},
]

print(f"Enqueuing {len(TASKS)} tasks...\n")
for task_def in TASKS:
    task_id = queue.enqueue(task_def)
    print(f"  Enqueued: {task_id} ({task_def.get('priority', 'normal')})")

print(f"\nQueue depth: {queue.depth()}")
print(f"Processing with 3 workers...\n")

pool = WorkerPool(workers=3)
pool.run(queue, iterations=len(TASKS))

print(f"\n{'='*60}")
print("Processing Summary")
print(f"{'='*60}")
print(f"  Tasks processed:        {pool.stats['processed']}")
print(f"  Tasks failed (to DLQ):  {pool.stats['failed']}")
print(f"  DLQ depth:              {len(queue.dlq)}")
print(f"  Queue remaining:        {queue.depth()}")

print(f"\n{'='*60}")
print("Dead Letter Queue (failed tasks)")
print(f"{'='*60}")
for task in queue.dlq:
    print(f"  {task['task_id']}: {task.get('error', 'unknown error')} "
          f"(retries: {task['retry_count']})")

print(f"\nArchitecture: Client → Request Queue → Worker Pool → Response Queue → Client")
print("DLQ captures permanently failed tasks for manual inspection + reprocessing")

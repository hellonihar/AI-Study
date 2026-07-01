"""
Rate limiting: token bucket and sliding window implementations.

Run: python 09-rate-limiting.py

Requirements: none (stdlib only)
"""

import time
import json
from collections import deque

print("=== Rate Limiting ===\n")

class TokenBucket:
    def __init__(self, capacity, refill_rate, refill_interval=1.0):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        self.last_refill = time.time()
        self.accepted = 0
        self.rejected = 0

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def allow(self, tokens=1):
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            self.accepted += 1
            return True
        self.rejected += 1
        return False

    def stats(self):
        return {
            "type": "TokenBucket",
            "tokens_remaining": round(self.tokens, 1),
            "accepted": self.accepted,
            "rejected": self.rejected,
            "utilization": self.accepted / (self.accepted + self.rejected) * 100
            if (self.accepted + self.rejected) else 0,
        }

class SlidingWindow:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps = deque()
        self.accepted = 0
        self.rejected = 0

    def allow(self):
        now = time.time()
        cutoff = now - self.window_seconds

        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()

        if len(self.timestamps) < self.max_requests:
            self.timestamps.append(now)
            self.accepted += 1
            return True

        self.rejected += 1
        return False

    def stats(self):
        now = time.time()
        cutoff = now - self.window_seconds
        current = sum(1 for t in self.timestamps if t >= cutoff)
        return {
            "type": "SlidingWindow",
            "current_count": current,
            "max_allowed": self.max_requests,
            "window_seconds": self.window_seconds,
            "accepted": self.accepted,
            "rejected": self.rejected,
        }

bucket = TokenBucket(capacity=10, refill_rate=2)
window = SlidingWindow(max_requests=5, window_seconds=3)

print("1. Token Bucket (10 tokens, refill 2/sec)")
print("-" * 40)

for i in range(15):
    allowed = bucket.allow()
    status = "✓" if allowed else "✗"
    print(f"  [{i+1:2d}] Request {status} (tokens: {bucket.tokens:.1f})")
    time.sleep(0.05)

print(f"\n  Token bucket stats: {json.dumps(bucket.stats(), indent=4)}")

print(f"\n2. Sliding Window (5 req / 3 sec)")
print("-" * 40)

for i in range(20):
    allowed = window.allow()
    status = "✓" if allowed else "✗"
    print(f"  [{i+1:2d}] Request {status}")
    time.sleep(0.1)

print(f"\n  Sliding window stats: {json.dumps(window.stats(), indent=4)}")

print(f"\n{'='*60}")
print("Comparison")
print(f"{'='*60}")
print(f"  {'Feature':<25} {'Token Bucket':<25} {'Sliding Window':<25}")
print(f"  {'-'*73}")
print(f"  {'Burst handling':<25} {'Yes (up to capacity)':<25} {'No':<25}")
print(f"  {'Memory efficient':<25} {'Yes (O(1))':<25} {'No (O(N))':<25}")
print(f"  {'Precise window':<25} {'No (smoothing)':<25} {'Yes (exact count)':<25}")
print(f"  {'Best for':<25} {'API rate limits':<25} {'User request caps':<25}")

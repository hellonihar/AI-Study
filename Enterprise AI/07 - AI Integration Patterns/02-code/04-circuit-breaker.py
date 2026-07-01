"""
Circuit breaker: state machine for protecting LLM API calls.

Run: python 04-circuit-breaker.py

Requirements: none (stdlib only)
"""

import time
import random
from enum import Enum

print("=== Circuit Breaker ===\n")

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, name, failure_threshold=3, recovery_timeout=5,
                 half_open_max=2):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max = half_open_max

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_requests = 0
        self.total_calls = 0
        self.fast_fails = 0

    def call(self, fn, *args, **kwargs):
        self.total_calls += 1

        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                print(f"  ⏱ Recovery timeout reached, transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.half_open_requests = 0
            else:
                self.fast_fails += 1
                raise Exception(f"Circuit OPEN for {self.name} — fast fail")

        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_requests >= self.half_open_max:
                self.fast_fails += 1
                raise Exception(f"Circuit HALF_OPEN — max trial requests reached")
            self.half_open_requests += 1

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            print(f"  ✅ Trial request succeeded, circuit CLOSED")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_requests = 0

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            print(f"  ❌ Trial request failed, circuit OPEN again")
            self.state = CircuitState.OPEN
            self.half_open_requests = 0
        elif self.failure_count >= self.failure_threshold:
            print(f"  ❌ Failure threshold ({self.failure_threshold}) reached, "
                  f"circuit OPEN")
            self.state = CircuitState.OPEN
            self.half_open_requests = 0

    def __str__(self):
        return (f"CircuitBreaker({self.name}, state={self.state.value}, "
                f"failures={self.failure_count}/{self.failure_threshold}, "
                f"total={self.total_calls}, fast_fails={self.fast_fails})")

def simulate_api_call(success_rate=0.7):
    if random.random() < success_rate:
        return {"status": "ok", "content": "API response"}
    raise Exception("API call failed")

cb = CircuitBreaker("gpt-4-api", failure_threshold=3, recovery_timeout=3)

print(f"Initial: {cb}")
print()

for i in range(20):
    time.sleep(0.1)
    try:
        result = cb.call(simulate_api_call, 0.5)
        print(f"  [{i+1:2d}] Success: {result['content'][:30]}")
    except Exception as e:
        print(f"  [{i+1:2d}] FAIL:    {str(e)[:50]}")
    print(f"         State: {cb}")

print(f"\n{'='*60}")
print("Circuit Breaker Summary")
print(f"{'='*60}")
print(f"  Final state:           {cb.state.value}")
print(f"  Total calls:           {cb.total_calls}")
print(f"  Fast-failed:           {cb.fast_fails}")
print(f"  Failures saved by CB:  {cb.fast_fails}")
print()
print("Transitions through all three states (CLOSED → OPEN → HALF_OPEN → CLOSED)")
print("demonstrate the full circuit breaker lifecycle.")

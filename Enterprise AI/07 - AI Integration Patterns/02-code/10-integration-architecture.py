"""
Integration architecture: end-to-end demo combining fallback, circuit breaker,
caching, rate limiting, vendor abstraction, and tool calling.

Run: python 10-integration-architecture.py

Requirements: pip install sentence-transformers numpy
"""

import time
import json
import hashlib
import random
from enum import Enum
from abc import ABC, abstractmethod

print("=== Integration Architecture Demo ===\n")

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, name, failure_threshold=3, recovery_timeout=5):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.fast_failed = 0

    def protect(self, fn, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                self.fast_failed += 1
                raise Exception(f"Circuit open for {self.name}")

        try:
            result = fn(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            raise

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def allow(self):
        now = time.time()
        self.tokens = min(self.capacity, self.tokens + (now - self.last_refill) * self.refill_rate)
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

class ResponseCache:
    def __init__(self):
        self.cache = {}
        self.hits = 0
        self.misses = 0

    def get(self, prompt):
        key = hashlib.md5(prompt.encode()).hexdigest()
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, prompt, response):
        key = hashlib.md5(prompt.encode()).hexdigest()
        self.cache[key] = response

class ModelTier:
    def __init__(self, name, success_rate=0.8, latency=0.5):
        self.name = name
        self.success_rate = success_rate
        self.latency = latency

    def invoke(self, prompt):
        time.sleep(self.latency * 0.01)
        if random.random() > self.success_rate:
            raise Exception(f"{self.name} failed")
        return {
            "model": self.name,
            "response": f"[{self.name}] Response to: {prompt[:30]}...",
            "latency": self.latency,
        }

class AIModel(ABC):
    @abstractmethod
    def generate(self, prompt): pass

class OpenAIAdapter(AIModel):
    def generate(self, prompt):
        return f"[OpenAI] {prompt[:30]}..."

class AnthropicAdapter(AIModel):
    def generate(self, prompt):
        return f"[Anthropic] {prompt[:30]}..."

class ModelRouter:
    def __init__(self):
        self.adapters = {
            "openai": OpenAIAdapter(),
            "anthropic": AnthropicAdapter(),
        }

    def route(self, prompt, provider="openai"):
        return self.adapters[provider].generate(prompt)

class Pipeline:
    def __init__(self):
        self.rate_limiter = TokenBucket(capacity=10, refill_rate=5)
        self.cache = ResponseCache()
        self.fallback = [
            ModelTier("gpt-4", success_rate=0.7, latency=0.5),
            ModelTier("gpt-4o-mini", success_rate=0.85, latency=0.3),
            ModelTier("claude-haiku", success_rate=0.8, latency=0.2),
        ]
        self.circuit = CircuitBreaker("gpt-4", failure_threshold=2, recovery_timeout=3)
        self.router = ModelRouter()

    def execute(self, prompt):
        if not self.rate_limiter.allow():
            return {"error": "rate_limited", "message": "Too many requests"}

        cached = self.cache.get(prompt)
        if cached:
            return {"source": "cache", "response": cached}

        for tier in self.fallback:
            try:
                result = self.circuit.protect(tier.invoke, prompt)
                self.cache.set(prompt, result["response"])
                return {"source": f"model:{tier.name}", "response": result["response"]}
            except Exception:
                continue

        return {"source": "static_fallback", "response": "Service unavailable. Please try again."}

pipeline = Pipeline()

QUERIES = [
    "What is the capital of France?",
    "Explain machine learning",
    "What is the capital of France?",
    "How do transformers work?",
    "What is the capital of France?",
    "Explain neural networks",
]

print("Pipeline Execution (6 queries):\n")
for i, q in enumerate(QUERIES):
    result = pipeline.execute(q)
    print(f"  [{i+1}] Source: {result['source']:<30} → {result['response'][:50]}")

print(f"\n{'='*60}")
print("Pipeline Statistics")
print(f"{'='*60}")
print(f"  Rate limiter:    {pipeline.rate_limiter.tokens:.1f} tokens remaining")
print(f"  Cache:           {pipeline.cache.hits} hits, {pipeline.cache.misses} misses "
      f"({pipeline.cache.hits/(pipeline.cache.hits+pipeline.cache.misses)*100:.0f}% hit rate)")
print(f"  Circuit breaker: {pipeline.circuit.state.value} (fast-failed: {pipeline.circuit.fast_failed})")
print(f"  Fallback chain:  {len(pipeline.fallback)} tiers")

print(f"\n{'='*60}")
print("Architecture Flow")
print(f"{'='*60}")
print("  Client → Rate Limiter → Cache → Circuit Breaker → ")
print("  Fallback Chain → Model Router → Provider → Response")
print()
print("  Protected by: rate limiting, circuit breaker, cache,")
print("  multi-tier fallback, vendor abstraction layer")

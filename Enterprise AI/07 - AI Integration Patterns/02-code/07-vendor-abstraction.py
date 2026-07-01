"""
Vendor abstraction: adapter pattern for multi-provider LLM access.

Run: python 07-vendor-abstraction.py

Requirements: none (stdlib only)
"""

import json
import time
import random
from abc import ABC, abstractmethod

print("=== Vendor Abstraction Layer ===\n")

class AIModel(ABC):
    @abstractmethod
    def generate(self, messages, **kwargs):
        pass

    @abstractmethod
    def count_tokens(self, text):
        pass

    @property
    @abstractmethod
    def model_name(self):
        pass

class OpenAIAdapter(AIModel):
    def __init__(self, model="gpt-4o-mini"):
        self._model = model

    def generate(self, messages, **kwargs):
        time.sleep(0.05)
        return {
            "provider": "openai",
            "model": self._model,
            "content": f"[OpenAI {self._model}] Simulated response",
            "usage": {"input_tokens": 50, "output_tokens": 100},
        }

    def count_tokens(self, text):
        return len(text.split()) * 1.3

    @property
    def model_name(self):
        return self._model

    def __str__(self):
        return f"OpenAIAdapter({self._model})"

class AnthropicAdapter(AIModel):
    def __init__(self, model="claude-3-haiku"):
        self._model = model

    def generate(self, messages, **kwargs):
        time.sleep(0.06)
        return {
            "provider": "anthropic",
            "model": self._model,
            "content": f"[Anthropic {self._model}] Simulated response",
            "usage": {"input_tokens": 55, "output_tokens": 110},
        }

    def count_tokens(self, text):
        return int(len(text.split()) * 1.4)

    @property
    def model_name(self):
        return self._model

    def __str__(self):
        return f"AnthropicAdapter({self._model})"

class LocalAdapter(AIModel):
    def __init__(self, model="llama-3-8b"):
        self._model = model

    def generate(self, messages, **kwargs):
        time.sleep(0.1)
        return {
            "provider": "local",
            "model": self._model,
            "content": f"[Local {self._model}] Simulated response",
            "usage": {"input_tokens": 60, "output_tokens": 120},
        }

    def count_tokens(self, text):
        return len(text.split()) * 1.2

    @property
    def model_name(self):
        return self._model

    def __str__(self):
        return f"LocalAdapter({self._model})"

class ModelRouter:
    def __init__(self):
        self.providers = {}
        self.costs = {}

    def register(self, name, adapter, cost_per_token=0.0001):
        self.providers[name] = adapter
        self.costs[name] = cost_per_token

    def route(self, prompt, strategy="cheapest"):
        if strategy == "cheapest":
            provider = min(self.providers.keys(),
                          key=lambda p: self.costs[p])
        elif strategy == "random":
            provider = random.choice(list(self.providers.keys()))
        elif strategy == "specific":
            provider = prompt.get("provider", list(self.providers.keys())[0])
        else:
            provider = list(self.providers.keys())[0]

        adapter = self.providers[provider]
        messages = [{"role": "user", "content": prompt.get("text", prompt)}]
        result = adapter.generate(messages)
        result["cost"] = result["usage"]["output_tokens"] * self.costs[provider]

        return result

router = ModelRouter()
router.register("openai", OpenAIAdapter("gpt-4o-mini"), cost_per_token=0.00015)
router.register("anthropic", AnthropicAdapter("claude-3-haiku"), cost_per_token=0.00025)
router.register("local", LocalAdapter("llama-3-8b"), cost_per_token=0.00001)

print("Testing multi-provider routing:\n")

strategies = ["cheapest", "random", "random", "cheapest"]
for i, strategy in enumerate(strategies):
    prompt = {"text": f"What is the capital of France? (query {i+1})"}
    result = router.route(prompt, strategy=strategy)
    print(f"  [{i+1}] Strategy: {strategy:<10} → {result['provider']:<10} "
          f"({result['model']:<15}) cost=${result['cost']:.5f}")

print(f"\n{'='*60}")
print("Provider Comparison")
print(f"{'='*60}")
print(f"  {'Provider':<12} {'Model':<20} {'Cost/1K tokens':<18} {'Latency':<10}")
print(f"  {'-'*58}")
for name, adapter in router.providers.items():
    messages = [{"role": "user", "content": "test"}]
    start = time.time()
    result = adapter.generate(messages)
    latency = time.time() - start
    cost_per_1k = router.costs[name] * 1000
    print(f"  {name:<12} {adapter.model_name:<20} ${cost_per_1k:.5f}      "
          f"{latency*1000:.0f}ms")

print(f"\nAdapter pattern enables vendor switching without application code changes.")
print("Add new providers by implementing the AIModel interface.")

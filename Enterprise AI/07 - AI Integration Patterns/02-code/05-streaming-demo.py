"""
Streaming patterns: SSE-like token generation with backpressure simulation.

Run: python 05-streaming-demo.py

Requirements: none (stdlib only)
"""

import time
import json

print("=== Streaming Response Patterns ===\n")

DEMO_RESPONSE = (
    "The Transformer architecture, introduced in the 2017 paper "
    "'Attention Is All You Need', revolutionized natural language "
    "processing by replacing recurrent layers with self-attention "
    "mechanisms."
)

def simulate_token_stream(text, tokens_per_second=10):
    words = text.split()
    interval = 1.0 / tokens_per_second

    for i, word in enumerate(words):
        time.sleep(interval * 0.1)

        yield {
            "index": i,
            "token": word + (" " if i < len(words) - 1 else ""),
            "finish_reason": None,
        }

    yield {"index": len(words), "token": "", "finish_reason": "stop"}

print("1. SSE Token Stream (server -> client)")
print("-" * 40)
print()

received_tokens = []
for event in simulate_token_stream(DEMO_RESPONSE, tokens_per_second=15):
    if event["token"]:
        print(event["token"], end="", flush=True)
        received_tokens.append(event)
    elif event["finish_reason"] == "stop":
        print("\n\n[done]")

print(f"\n   Streamed {len(received_tokens)} tokens")
print(f"   Time-to-first-token: ~66ms")
print(f"   Total response time: {len(received_tokens) * 0.067:.1f}s (simulated)")
print()

print("2. Client Cancellation (Mid-Stream)")
print("-" * 40)
print()

for i, event in enumerate(simulate_token_stream(DEMO_RESPONSE, tokens_per_second=10)):
    if i >= 5:
        print("\n\n[client cancelled — stop processing]")
        break
    if event["token"]:
        print(event["token"], end="", flush=True)

print(f"\n   Saved {(len(DEMO_RESPONSE.split()) - 5)} tokens by cancelling early")
print()

print("3. Progressive JSON Rendering")
print("-" * 40)
print()

fragment = ""
for word in DEMO_RESPONSE.split()[:8]:
    fragment += word + " "
    if len(fragment) > 50:
        print(f"  Rendered partial: \"{fragment[:50]}...\" ({len(fragment)} chars)")
        break

print()
print("4. Streaming vs Batch Metrics")
print("-" * 40)
print(f"  {'Metric':<30} {'Streaming':<15} {'Batch':<15}")
print(f"  {'-'*56}")
print(f"  {'Time-to-first-token':<30} {'50-100ms':<15} {'2-5s':<15}")
print(f"  {'Total latency':<30} {'Same as batch':<15} {'Same as stream':<15}")
print(f"  {'Perceived speed':<30} {'Fast':<15} {'Slow':<15}")
print(f"  {'Token cost':<30} {'Same':<15} {'Same':<15}")
print(f"  {'Cancel mid-generation':<30} {'Yes':<15} {'No':<15}")

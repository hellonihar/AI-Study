"""
Cost benchmark suite: compare cost across model providers and deployment options.

Run: python 03-cost-benchmark-suite.py
"""

print("=== Cost Benchmark Suite ===\n")

PROVIDERS = {
    "OpenAI GPT-4o": {"input": 2.50, "output": 10.00, "context": 128000},
    "OpenAI GPT-4o-mini": {"input": 0.15, "output": 0.60, "context": 128000},
    "Claude 3.5 Sonnet": {"input": 3.00, "output": 15.00, "context": 200000},
    "Claude 3 Haiku": {"input": 0.25, "output": 1.25, "context": 200000},
    "Google Gemini 1.5 Pro": {"input": 3.50, "output": 10.50, "context": 1000000},
    "Google Gemini 1.5 Flash": {"input": 0.35, "output": 1.50, "context": 1000000},
}

class Benchmark:
    def cost_per_request(self, provider, input_tokens, output_tokens):
        p = PROVIDERS[provider]
        input_cost = (input_tokens / 1000) * p["input"] / 1000
        output_cost = (output_tokens / 1000) * p["output"] / 1000
        return round(input_cost + output_cost, 6)

    def monthly_cost(self, provider, input_tokens, output_tokens, requests):
        per_req = self.cost_per_request(provider, input_tokens, output_tokens)
        return round(per_req * requests, 2)

bench = Benchmark()

WORKLOADS = [
    ("Simple chat", 100, 200, 1000000),
    ("Code generation", 500, 400, 300000),
    ("Document analysis", 5000, 1000, 100000),
    ("Complex reasoning", 3000, 800, 200000),
    ("Batch processing", 2000, 500, 500000),
]

for name, inp, out, req in WORKLOADS:
    print(f"=== {name} (in={inp}, out={out}, req={req:,}/mo) ===")
    costs = []
    for prov, _ in sorted(PROVIDERS.items(), key=lambda x: bench.monthly_cost(x[0], inp, out, req)):
        monthly = bench.monthly_cost(prov, inp, out, req)
        costs.append((monthly, prov))
    costs.sort()
    for monthly, prov in costs[:4]:
        bar = "$" * max(1, int(monthly / max(c[0] for c in costs[:1]) * 20)) if costs else ""
        print(f"  {prov:<25} ${monthly:>8,.2f}/mo")
    print()

print("=== Cost/Token Comparison ===")
for prov, p in PROVIDERS.items():
    ratio = p["output"] / p["input"] if p["input"] > 0 else 0
    print(f"  {prov:<25} in=${p['input']/1000:.4f}/K out=${p['output']/1000:.4f}/K context={p['context']:,}")

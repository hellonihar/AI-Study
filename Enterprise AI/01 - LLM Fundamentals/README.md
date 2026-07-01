# LLM Fundamentals

Core concepts: tokenization, embeddings, attention mechanisms, transformer architecture, and the autoregressive decoding loop.

## Directory Structure

```
01-theory/                   # Deep dives into how LLMs work
├── 01-transformer-architecture.md
├── 02-tokenization.md
├── 03-embeddings.md
├── 04-positional-encodings.md
├── 05-attention-mechanism.md
├── 06-kv-cache.md
├── 07-feed-forward-layers.md
├── 08-sampling-strategies.md
├── 09-scaling-laws.md
└── 10-inference-optimization.md

02-code/                     # Runnable code examples
├── 01-tokenizer-playground.py      — BPE tokenization, vocab, compression
├── 02-attention-from-scratch.py    — NumPy attention implementation
├── 03-transformer-forward-pass.py  — Pre-trained model forward pass
├── 04-kv-cache-demo.py             — TTFT vs per-token latency comparison
├── 05-sampling-comparison.py       — Side-by-side sampling strategies
├── 06-load-and-prompt-ollama.py    — Local model inference via Ollama
└── 07-benchmark-inference.py       — TTFT, TPOT, throughput measurement

03-best-practices/           # Production guidance
├── 01-model-selection.md
├── 02-context-window-management.md
├── 03-quantization-guide.md
├── 04-prompt-formatting.md
└── 05-batching-and-throughput.md

04-resources/                # Papers, tools, courses
└── links.md
```

## Prerequisites

- Python 3.10+, `transformers`, `torch`, `numpy`
- [Ollama](https://ollama.com) (for 06-load-and-prompt-ollama.py)
- `pip install transformers torch numpy ollama`

## Suggested Learning Path

1. Theory: transformer architecture → tokenization → embeddings → attention
2. Code: attention-from-scratch → transformer-forward-pass → kv-cache-demo
3. Practice: tokenizer-playground → sampling-comparison → load-and-prompt-ollama
4. Best practices: model-selection → prompt-formatting → quantization-guide

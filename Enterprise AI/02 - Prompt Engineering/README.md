# Prompt Engineering

Systematic design and evaluation of prompts to control LLM behavior reliably.

## Directory Structure

```
01-theory/                   # Deep dives into prompt techniques
├── 01-anatomy-of-a-prompt.md
├── 02-in-context-learning.md
├── 03-chain-of-thought.md
├── 04-advanced-reasoning-patterns.md
├── 05-structured-output.md
├── 06-prompt-optimization.md
├── 07-multi-turn-conversation.md
├── 08-meta-prompting.md
├── 09-evaluation-metrics.md
└── 10-prompt-security.md

02-code/                     # Runnable scripts
├── 01-role-effects.py              — System prompt placement comparison
├── 02-few-shot-dynamics.py         — Example count & ordering effects
├── 03-cot-reasoning.py             — Direct vs CoT vs few-shot CoT
├── 04-structured-output-json.py    — JSON extraction methods compared
├── 05-prompt-optimization-dspy.py  — Automated prompt optimization
├── 06-multi-turn-context-budget.py — Context growth & compression
├── 07-a-b-test-prompts.py          — A/B testing framework
├── 08-constrained-decoding.py      — Grammar-guided generation
├── 09-meta-prompt-loop.py          — LLM improves its own prompts
└── 10-injection-defense.py         — Injection attack/defense tests

03-best-practices/           # Production guidance
├── 01-prompt-design-patterns.md
├── 02-prompt-version-control.md
├── 03-cost-aware-prompting.md
├── 04-prompt-testing-framework.md
└── 05-production-prompt-management.md

04-resources/                # Papers, tools, courses
└── links.md
```

## Prerequisites

- Python 3.10+
- `pip install ollama tiktoken dspy-ai`
- [Ollama](https://ollama.com) with a model pulled (`ollama pull llama3.2:3b`)

## Suggested Learning Path

1. **Theory:** anatomy → in-context learning → chain-of-thought → structured output
2. **Code:** role-effects → cot-reasoning → structured-output-json → few-shot-dynamics
3. **Optimization:** prompt-optimization-dspy → meta-prompt-loop → a-b-test-prompts
4. **Security:** injection-defense → review prompt-security theory
5. **Production:** design-patterns → version-control → cost-aware → testing → management

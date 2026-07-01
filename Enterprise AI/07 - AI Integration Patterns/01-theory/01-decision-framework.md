# Decision Framework: RAG vs Fine-Tuning vs Prompt Engineering

## Decision Matrix

| Factor | Prompt Engineering | RAG | Fine-Tuning |
|--------|-------------------|-----|-------------|
| Knowledge scope | Model's training cutoff | External corpus (any size) | Training dataset |
| Knowledge update | Change prompt | Update index / data source | Retrain (hours–days) |
| Latency | Lowest | Medium (retrieval + generation) | Lowest (no retrieval) |
| Cost per query | Lowest (fewer tokens) | Medium (embedding + LLM) | Lowest (smaller model possible) |
| Upfront cost | $0 | Indexing infrastructure | Training compute |
| Accuracy on facts | Poor (hallucination-prone) | High (grounded in retrieved docs) | Medium (memorization) |
| Custom style/tone | Limited (system prompt) | Limited | Strong (learned patterns) |
| New capabilities | Cannot add | Cannot add new skills | Can teach new tasks |
| Maintainability | High (prompt changes) | Medium (data pipeline) | Low (retraining cycle) |
| Data privacy | No data stored | Docs stored in index | Training data stored |

## Decision Flow

```
Is the knowledge public and stable?
├── Yes → Can prompt engineering suffice?
│   ├── Yes → Use Prompt Engineering
│   └── No → Is the knowledge structured and queryable?
│       ├── Yes → Use RAG
│       └── No → Use Fine-Tuning
└── No → Is the knowledge in documents?
    ├── Yes → Use RAG
    └── No → Use Fine-Tuning

Do you need a specific output format or behavior?
├── Yes → Add to RAG prompt or fine-tune
└── No → Prompt engineering is enough

Is latency the #1 constraint?
├── Yes → Fine-tune a small model (no retrieval step)
└── No → RAG (more accurate, slightly slower)
```

## Hybrid Approach

Most production systems combine all three:

- **Prompt engineering** for instructions, formatting, guardrails
- **RAG** for grounding in fresh/corporate knowledge
- **Fine-tuning** for domain-specific style, structured outputs, or task adherence

Example: A customer support bot uses a system prompt (tone + rules), RAG (product docs + ticket history), and a fine-tuned model (specialized in your product domain).

## Cost Estimation

| Approach | Setup Cost | Per-Query Cost | Update Cost |
|----------|-----------|----------------|-------------|
| Prompt only | $0 | $0.001–0.01 | $0 (edit prompt) |
| RAG | $50–500 (indexing) | $0.002–0.02 (retrieval + gen) | $5–50 (re-index) |
| Fine-tune | $50–500 (training) | $0.001–0.01 (smaller model) | $50–500 (re-train) |

## When NOT to use each

- **Don't prompt-engineer** for tasks requiring fresh knowledge or complex reasoning
- **Don't RAG** when all knowledge fits in the context window and is already known by the model
- **Don't fine-tune** when RAG or prompting can achieve the goal — fine-tuning is a last resort

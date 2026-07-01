# Decision Guide: Choosing Your Integration Approach

## Decision Matrix

| Factor | Prompt Engineering | RAG | Fine-Tuning |
|--------|-------------------|-----|-------------|
| New knowledge needed? | No | Yes | Yes |
| Knowledge updates frequently? | — | Yes (re-index) | No (retrain is slow) |
| Custom output format required? | Limited | Limited | Yes |
| Budget for training? | $0 | $50–500 | $200–2,000 |
| Latency sensitive? | ✅ Best | ⚠️ +200ms | ✅ Best (no retrieval) |
| Offline/air-gapped? | ✅ | ⚠️ Needs index | ✅ |

## Decision Heuristic

```
Rule of thumb: Start with prompt engineering.
  If accuracy < threshold → Add RAG.
    If RAG isn't enough (quality/style) → Fine-tune.
      If fine-tune drifts → Add RAG as a correction layer.
```

## Cost Estimation Template

```python
queries_per_month = 1_000_000
avg_output_tokens = 200

# Prompt engineering only
cost_prompt = queries_per_month * avg_output_tokens * 0.000003  # ~$600

# RAG (prompt + retrieval)
cost_rag = queries_per_month * (avg_output_tokens * 0.000003 + 0.0002)  # ~$800

# Fine-tuning (amortized over 6 months)
cost_ft_setup = 300  # training cost
cost_ft_monthly = queries_per_month * avg_output_tokens * 0.000002  # ~$400
```

## Migration Strategy

1. **Phase 1**: Prompt engineering (days)
2. **Phase 2**: Add RAG when hallucinations become a problem (weeks)
3. **Phase 3**: Fine-tune when style/compliance requirements emerge (months)
4. **Phase 4**: Hybrid = prompt + RAG + fine-tuning (ongoing optimization)

## Anti-Patterns

- **Fine-tuning before RAG**: Always try RAG first — cheaper, faster, more maintainable
- **RAG for everything**: If the model already knows it well and doesn't need fresh data, just prompt
- **Pure prompting for regulated use cases**: Prompt engineering alone cannot guarantee factual accuracy

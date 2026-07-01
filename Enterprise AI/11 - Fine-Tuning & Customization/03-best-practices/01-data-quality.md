# Data Quality Best Practices

## The Golden Rule
Garbage in, garbage out — amplified. Fine-tuning on noisy data produces a model that confidently outputs nonsense. Invest 80% of your fine-tuning effort in data quality.

## Data Quality Checklist

| Check | Method | Minimum Standard |
|-------|--------|-----------------|
| Deduplication | Exact + MinHash LSH | No exact duplicates |
| Format consistency | Schema validation | 100% conformant |
| PII free | Regex + classifier scan | Zero PII in training data |
| Language match | Language detector | >99% target language |
| Minimum length | Token count filter | >20 tokens per example |
| Maximum length | Token count filter | <4096 tokens per example |
| Human review | Sample 5–10% | <5% flagged as low quality |

## Annotation Guidelines

For human-annotated data:
- Provide clear, specific instructions with examples
- Define quality dimensions (accuracy, completeness, tone, format)
- Measure inter-annotator agreement — target Cohen's kappa > 0.7
- Include trap questions to detect lazy annotators
- Rotate annotators across examples to reduce individual bias

## Synthetic Data Best Practices

| Practice | Rationale |
|----------|-----------|
| Use a strong model (GPT-4, Claude) | Higher quality base generations |
| Verify all synthetic data | Never trust synthetic data without validation |
| Include diverse system prompts | Avoid style monotony |
| Add controlled noise | Overly clean data produces brittle models |
| Mix with human data | Pure synthetic training has ceiling effects |

## Dataset Size Recommendations

| Task Complexity | Minimum Examples | Recommended |
|----------------|-----------------|-------------|
| Simple classification | 100 per class | 500+ per class |
| Structured generation | 500 | 2000+ |
| Complex reasoning | 1000 | 5000+ |
| Multi-turn conversation | 2000 | 10000+ |
| Full instruction tuning | 5000 | 25000+ |

## Data Mix for General Capability Retention

When fine-tuning for a specific task, include 10–30% general data to prevent catastrophic forgetting:
- 10% for narrow, well-defined tasks
- 20% for moderately broad tasks
- 30% for tasks requiring general knowledge

## Versioning

- Store datasets as immutable versions (DVC or Hugging Face Datasets)
- Tag each version with: source, date, size, quality metrics
- Never modify in place — create new versions
- Maintain a data card for every dataset

# Data Preparation for Fine-Tuning

## The Data Pipeline

Training data quality is the single most important factor in fine-tuning success. A well-prepared dataset can make a small model outperform a larger one on the target task.

```
Raw Data → Clean → Deduplicate → Format → Filter → Split → Eval
```

## Collection Strategies

### Sources
- **Production logs**: Real user interactions (with privacy safeguards)
- **Expert curation**: Domain experts write or review examples
- **Synthetic generation**: LLM-generated examples verified by humans
- **Public datasets**: Specialized corpora (legal, medical, code)
- **Augmentation**: Transform existing examples (paraphrase, back-translate)

### Minimum Dataset Size

| Task Type | Minimum Examples | Recommended | Notes |
|-----------|-----------------|-------------|-------|
| Classification | 100 per class | 500+ per class | Simple decision boundary |
| Summarization | 500 | 2000+ | Needs diverse input styles |
| Code generation | 1000 | 5000+ | Must cover language constructs |
| Instruction following | 2000 | 10000+ | Broad coverage needed |
| Chat/conversation | 5000 | 20000+ | Multi-turn patterns |

## Cleaning

### Deduplication
Duplicate examples bias training toward repeated patterns and reduce effective dataset size.

**Methods:**
- **Exact dedup**: Remove identical text (hashed comparison)
- **Near-dedup**: MinHash + LSH for similar but not identical examples
- **Semantic dedup**: Embedding-based similarity (cosine > 0.95 threshold)

### Noise Removal
- Fix formatting inconsistencies (whitespace, line endings, encoding)
- Remove examples with placeholder content, TODOs, or test markers
- Filter low-quality generations (too short, repetitive, nonsensical)
- Strip PII before any storage or training

## Format Standardization

### Chat Template Format

Most fine-tuning uses a consistent chat template:

```
<|system|>
You are a helpful assistant.
<|user|>
What is fine-tuning?
<|assistant|>
Fine-tuning adapts a pre-trained model...
```

### Multi-Turn Format

```
<|user|>
Question 1
<|assistant|>
Answer 1
<|user|>
Question 2 (follow-up)
<|assistant|>
Answer 2
```

### Completion Format

For single-turn generation tasks:

```
### Instruction
Write a function to sort a list.

### Output
def sort_list(lst):
    return sorted(lst)
```

## Quality Filtering

### Automated Filters
- **Length filter**: Remove examples outside expected token range
- **Language filter**: Remove non-target-language examples (langdetect)
- **Perplexity filter**: Remove high-perplexity outliers (indicates noise)
- **Repetition filter**: Remove examples with excessive n-gram repetition

### Human Review
- Sample 5–10% for expert review before training
- Measure inter-annotator agreement (Cohen's kappa > 0.7)
- Track issue categories: factual error, format violation, ambiguity, off-topic

## Data Split Strategy

| Split | Purpose | Size |
|-------|---------|------|
| Train | Model weight updates | 80% |
| Validation | Hyperparameter tuning, early stopping | 10% |
| Test | Final evaluation (never used for decisions during training) | 10% |

### Important: No Leakage
- Deduplicate across splits (no near-duplicates between train and test)
- For conversational data, keep all turns of a conversation in one split
- For multi-turn, ensure the same user/session is not split across train/test

## Dataset Versioning

Treat datasets like code:
- Store in a versioned format (Parquet, Hugging Face Datasets)
- Tag each dataset with: source, date, filter version, size, quality metrics
- Maintain a data card with: intended use, language distribution, annotation guidelines
- Never modify a dataset in place — create new versions

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Template leakage | Model repeats formatting tokens | Remove template remnants from training |
| Label leakage | Model uses future info | Time-based split for temporal data |
| Spurious correlations | Model relies on shortcuts | Balanced sampling across categories |
| Data contamination | Evaluation scores inflated | Check benchmark overlap with training data |
| Class imbalance | Model biased toward majority class | Stratified sampling, weighted loss |

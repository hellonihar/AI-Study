# In-Context Learning

In-context learning (ICL) is the ability of LLMs to adapt their behavior based on examples provided in the prompt — no weight updates required.

## Zero-Shot vs Few-Shot

| Approach | Examples in Prompt | Typical Quality | Token Cost |
|---|---|---|---|
| Zero-shot | 0 | Baseline | Lowest |
| One-shot | 1 | +5–15% | Low |
| Few-shot (3–5) | 3–5 | +10–25% | Moderate |
| Many-shot (10–50) | 10–50 | +15–35% | High |

## How ICL Works

ICL is not "learning" in the traditional sense — the model doesn't update its weights. Instead:

1. **Pattern matching:** Examples activate relevant patterns in the model's pre-trained knowledge.
2. **Task specification:** Examples implicitly define the task better than natural language instructions.
3. **Format conditioning:** Examples demonstrate the exact output format, reducing format errors.
4. **Distribution alignment:** Examples shift the model's output distribution toward the desired domain.

## Example Selection Strategies

| Strategy | Description | Impact |
|---|---|---|
| Random | Select N random examples | Baseline |
| Fixed curated | Hand-pick diverse, high-quality examples | Good |
| KNN (semantic) | Retrieve examples closest to the query embedding | +5–10% over random |
| Diversity sampling | Maximize variety across example attributes | +3–5% |
| Hard negative mining | Include edge cases the model gets wrong | +5–15% |

## Ordering Effects

Example order matters significantly:

- **Label bias:** The first class mentioned in examples gets higher prediction probability.
- **Recency bias:** Examples near the end of the prompt have more influence.
- **Pattern breaks:** Placing a dissimilar example mid-chain disrupts learning.

**Best ordering:** Place the most similar or most important example last (recency bias), and balance label representation across positions.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| **Label imbalance** | Model over-predicts majority class | Balance example labels |
| **Example bleed** | Model copies example content verbatim | Make examples dissimilar to queries |
| **Length mismatch** | Short examples, long query — model truncates | Match example length to expected output |
| **Format inconsistency** | Model follows wrong format from example ordering | Keep format identical across all examples |

## Production Guidance

- **Start zero-shot.** Add examples only if quality is insufficient.
- **Use 3–5 examples** as default — diminishing returns beyond 5 for most tasks.
- **Put the most representative example last** (recency bias).
- **Retrieve examples dynamically** via KNN for maximum impact.
- **Cache retrieved examples** — repeated queries often need the same examples.

# Multi-Modal Embeddings

Maps different data types (text, image, audio) into a shared embedding space.

## The Shared Space Concept

```
[Text: "a brown dog"]  → f("a brown dog")  → [0.2, 0.5, -0.1, ...]
[Image: dog.jpg]       → g(dog.jpg)        → [0.3, 0.4, -0.2, ...]
                                                  ↑
                                          Similar vectors
```

- **text-to-image search:** Find images matching a text description.
- **image-to-text:** Find captions matching an image.
- **cross-modal retrieval:** Any combination.

## CLIP (Contrastive Language-Image Pre-training)

The dominant approach, by OpenAI (2021):

1. Train a text encoder and an image encoder with contrastive loss on 400M (image, text) pairs.
2. InfoNCE loss: pull matched pairs together, push unmatched apart (in-batch negatives).
3. Result: Shared 512–768 dim embedding space.

### Using CLIP

```python
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Encode text and images
text_inputs = processor(text=["a dog", "a cat"], return_tensors="pt", padding=True)
image_inputs = processor(images=[dog_image, cat_image], return_tensors="pt")

text_embeds = model.get_text_features(**text_inputs)
image_embeds = model.get_image_features(**image_inputs)

# Similarity
similarity = text_embeds @ image_embeds.T
```

### Alternatives to CLIP

| Model | Modalities | Strengths |
|---|---|---|
| **SigLIP** (Google, 2023) | Text + Image | Sigmoid loss (no negative sampling). Better than CLIP at same size. |
| **ImageBind** (Meta, 2023) | Text + Image + Audio + Depth + Thermal + IMU | Six modalities in one space. |
| **CLAP** (Microsoft) | Text + Audio | Audio-text retrieval, music search. |
| **GIT** (Microsoft) | Text + Image | Generative (captions + embeddings). |
| **BridgeTower** | Text + Image | Better fine-grained alignment than CLIP. |

## Use Cases

### E-Commerce Product Search

```
Query: "red summer dress with floral pattern"
Retrieve: Product images
Rank: Cross-modal similarity
```

- **30–40% improvement** in search engagement vs text-only search.
- Cold-start problem solved — new products with images but no text description are instantly searchable.

### Content Moderation

```
Query: "violent content"
Scan: User-uploaded images
Flag: Similarity > threshold
```

- More robust than text-based moderation (can't bypass with caption tricks).

### Document Understanding

```
Query: "quarterly revenue chart"
Retrieve: Documents containing charts + relevant text
```

## Training a Multi-Modal Model

Requires large-scale paired data:

```
1. Collect N (image, text) pairs: 100M–1B for SOTA.
2. Contrastive loss (InfoNCE) with batch size 32K+.
3. Encoders: ViT for images, transformer for text.
4. Train for 30–50K steps (thousands of GPU-hours).
```

**Practical alternative:** Fine-tune CLIP on domain-specific pairs (10K–100K pairs). Expect 5–10% improvement on domain tasks.

## Evaluation

### Flickr30K / MS-COCO Benchmarks

| Model | Text→Image R@1 | Image→Text R@1 |
|---|---|---|
| CLIP ViT-L/14 | 57.5 | 79.2 |
| SigLIP ViT-L/16 | 60.8 | 81.5 |
| EVA-CLIP-18B | 66.5 | 85.1 |

### Production Evaluation

- **Top-10 accuracy:** How often is the correct match in the top 10?
- **Latency:** Combined encoding + search time.
- **Coverage:** Does the model handle out-of-domain inputs well?

## Best Practices

- **Start with CLIP or SigLIP** — they're widely supported, fast, and good enough for most use cases.
- **Align multi-modal embeddings to text embedding space** if you already have a text embedding pipeline. Use CLIP's text encoder as a bridge.
- **Pre-compute image embeddings** and index them — the image encoder (ViT) is slower than the text encoder. Text queries are fast.
- **Fine-tune for domain specificity.** General CLIP doesn't understand domain-specific visual concepts (medical images, industrial parts).
- **Monitor modality gap** — the embedding space may have different distributions for text vs image. Mean-centering both modalities helps.

"""
Compare chunking strategies: fixed-size, recursive, semantic, document-aware.

Run: python 02-chunking-demo.py

Requirements: pip install sentence-transformers numpy
"""

import textwrap
import numpy as np
from sentence_transformers import SentenceTransformer

LONG_DOCUMENT = """
# Artificial Intelligence: A Comprehensive Overview

## Introduction
Artificial Intelligence (AI) is the simulation of human intelligence by machines.
The field was founded in 1956 at the Dartmouth Conference.
AI has experienced several waves of optimism and disappointment.

## Machine Learning
Machine Learning is a subset of AI that enables systems to learn from data.
Supervised learning uses labeled data to train models.
Unsupervised learning finds patterns in unlabeled data.
Reinforcement learning trains agents through reward signals.

## Deep Learning
Deep Learning uses neural networks with multiple layers.
Convolutional Neural Networks (CNNs) excel at image processing.
Recurrent Neural Networks (RNNs) process sequential data.
Transformers have revolutionized NLP since 2017.

## Natural Language Processing
NLP enables computers to understand human language.
Tokenization splits text into smaller units.
Named Entity Recognition identifies proper nouns in text.
Sentiment Analysis determines the emotional tone of text.

## Computer Vision
Computer Vision allows machines to interpret visual information.
Image classification assigns labels to images.
Object detection identifies and locates objects within images.
Semantic segmentation classifies each pixel in an image.

## Ethics and Safety
AI systems must be developed responsibly.
Bias in training data can lead to unfair outcomes.
Privacy concerns arise from data collection practices.
Alignment ensures AI systems act according to human values.

## Future Directions
AGI (Artificial General Intelligence) remains a long-term goal.
AI assistants are becoming more capable and prevalent.
Regulatory frameworks are being developed worldwide.
The economic impact of AI is expected to be transformative.
""".strip()

print("=== Chunking Strategy Comparison ===\n")
print(f"Document length: {len(LONG_DOCUMENT)} chars\n")

def fixed_size_chunks(text, chunk_size=200, overlap=40):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def recursive_chunks(text, chunk_size=200, chunk_overlap=40):
    separators = ["\n## ", "\n", ". ", " ", ""]
    chunks = []

    def split_recursive(text, sep_idx):
        if len(text) <= chunk_size:
            return [text]

        sep = separators[min(sep_idx, len(separators) - 1)]
        if sep == "":
            return [text[:chunk_size], text[chunk_size:]]

        parts = text.split(sep)
        chunks_local = []
        current = ""
        for part in parts:
            candidate = current + (sep if current else "") + part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks_local.append(current)
                current = part
        if current:
            chunks_local.append(current)

        result = []
        for c in chunks_local:
            if len(c) > chunk_size and sep_idx < len(separators) - 1:
                result.extend(split_recursive(c, sep_idx + 1))
            else:
                result.append(c)
        return result

    return split_recursive(text, 0)

def semantic_chunks(text, min_chunk_sentences=3, threshold=0.6):
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if s.strip()]
    sentences = [s + "." for s in sentences]

    if len(sentences) < min_chunk_sentences:
        return [text]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    emb = model.encode(sentences)

    chunks = []
    current = [sentences[0]]
    for i in range(1, len(sentences)):
        window = sentences[max(0, i - 2):i + 1]
        window_emb = model.encode(window)
        sim = window_emb[-2] @ window_emb[-1] / (
            np.linalg.norm(window_emb[-2]) * np.linalg.norm(window_emb[-1])
        )

        if sim < threshold and len(current) >= min_chunk_sentences:
            chunks.append(" ".join(current))
            current = [sentences[i]]
        else:
            current.append(sentences[i])
    if current:
        chunks.append(" ".join(current))
    return chunks

def document_aware_chunks(text, max_chunk_size=500):
    import re
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    chunks = []
    for section in sections:
        if not section.strip():
            continue
        if len(section) <= max_chunk_size:
            chunks.append(section.strip())
        else:
            sub_chunks = textwrap.wrap(section, width=max_chunk_size)
            chunks.extend(sub_chunks)
    return chunks

print("=" * 60)
print(f"{'Strategy':<20} {'Chunks':<8} {'Avg Size':<10} {'Min Size':<10} {'Max Size':<10}")
print("=" * 60)

fixed = fixed_size_chunks(LONG_DOCUMENT)
print(f"{'Fixed-size':<20} {len(fixed):<8} {np.mean([len(c) for c in fixed]):<10.0f} "
      f"{min(len(c) for c in fixed):<10} {max(len(c) for c in fixed):<10}")

recursive = recursive_chunks(LONG_DOCUMENT)
print(f"{'Recursive':<20} {len(recursive):<8} {np.mean([len(c) for c in recursive]):<10.0f} "
      f"{min(len(c) for c in recursive):<10} {max(len(c) for c in recursive):<10}")

semantic = semantic_chunks(LONG_DOCUMENT)
print(f"{'Semantic':<20} {len(semantic):<8} {np.mean([len(c) for c in semantic]):<10.0f} "
      f"{min(len(c) for c in semantic):<10} {max(len(c) for c in semantic):<10}")

doc_aware = document_aware_chunks(LONG_DOCUMENT)
print(f"{'Doc-aware':<20} {len(doc_aware):<8} {np.mean([len(c) for c in doc_aware]):<10.0f} "
      f"{min(len(c) for c in doc_aware):<10} {max(len(c) for c in doc_aware):<10}")

print(f"\n{'='*80}")
print("Sample Chunks from Each Strategy")
print(f"{'='*80}")

for strategy_name, chunks in [
    ("Fixed-size", fixed),
    ("Recursive", recursive),
    ("Semantic", semantic),
    ("Document-aware", doc_aware),
]:
    print(f"\n--- {strategy_name} (first 2 chunks) ---")
    for i, chunk in enumerate(chunks[:2]):
        print(f"  Chunk {i+1} ({len(chunk)} chars): {chunk[:80]}...")

print("\n=== Analysis ===")
print("Fixed-size: Simple but breaks mid-sentence and mid-section.")
print("Recursive: Preserves paragraph structure, splits at sentence boundaries.")
print("Semantic: Creates coherent topic-aligned chunks (best quality).")
print("Document-aware: Preserves section boundaries (best for structured docs).")
print()
print("Recommendation: Use recursive as default, semantic for high quality,")
print("document-aware for structured content (documentation, wiki, books).")

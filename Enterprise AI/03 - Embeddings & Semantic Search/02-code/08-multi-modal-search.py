"""
Multi-modal search: text-to-image retrieval using CLIP.

Run: python 08-multi-modal-search.py

Requirements: pip install transformers torch Pillow
"""

from transformers import CLIPProcessor, CLIPModel
import torch
import numpy as np
from PIL import Image
import io

# ─── Load CLIP ───
print("Loading CLIP model...")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
print(f"Embedding dimension: {model.config.projection_dim}")

# ─── Create synthetic image representations ───
# In a real scenario, you'd load actual images.
# Here we simulate with text descriptions that CLIP would use.
IMAGE_DESCRIPTIONS = [
    "a photo of a dog playing in the park",
    "a cat sleeping on a couch",
    "a beautiful mountain landscape at sunset",
    "a plate of pasta with tomato sauce",
    "a red car parked on the street",
    "a laptop on a desk with coffee",
    "a beach with palm trees and blue water",
    "a bookshelf filled with books",
    "a bicycle leaning against a wall",
    "a city skyline at night",
]

# Simulate image embeddings by encoding text descriptions
# (In production, encode actual images instead)
image_texts = IMAGE_DESCRIPTIONS
text_inputs = processor(text=image_texts, return_tensors="pt", padding=True)
with torch.no_grad():
    image_features = model.get_text_features(**text_inputs)  # Using text as proxy
image_features = image_features / image_features.norm(dim=-1, keepdim=True)

# ─── Text queries ───
QUERIES = [
    "animals and pets",
    "food and dining",
    "outdoor scenery",
    "technology and computers",
    "transportation",
]

print("\n=== Text-to-Image Search ===")

for query in QUERIES:
    query_input = processor(text=[query], return_tensors="pt", padding=True)
    with torch.no_grad():
        query_feature = model.get_text_features(**query_input)
    query_feature = query_feature / query_feature.norm(dim=-1, keepdim=True)
    
    # Compute similarity
    similarities = (query_feature @ image_features.T).squeeze().numpy()
    top_indices = np.argsort(similarities)[::-1][:3]
    
    print(f"\nQuery: '{query}'")
    for i, idx in enumerate(top_indices):
        print(f"  {i+1}. [{similarities[idx]:.3f}] {IMAGE_DESCRIPTIONS[idx]}")

# ─── Cross-modal consistency: find text for image ───
print("\n=== Image-to-Text (reverse search) ===")
# Use first description as a "query"
query_idx = 0
query_text = IMAGE_DESCRIPTIONS[query_idx]
print(f"Query image description: '{query_text}'")
print("Top matching text descriptions:")

query_input = processor(text=[query_text], return_tensors="pt", padding=True)
with torch.no_grad():
    query_feature = model.get_text_features(**query_input)
query_feature = query_feature / query_feature.norm(dim=-1, keepdim=True)

similarities = (query_feature @ image_features.T).squeeze().numpy()
top_indices = np.argsort(similarities)[::-1][:5]

for i, idx in enumerate(top_indices):
    match = "✓ SELF" if idx == query_idx else ""
    print(f"  {i+1}. [{similarities[idx]:.3f}] {IMAGE_DESCRIPTIONS[idx]} {match}")

print("\n=== Note ===")
print("In production, encode actual images (not text descriptions)")
print("using processor(images=image_list) and model.get_image_features().")

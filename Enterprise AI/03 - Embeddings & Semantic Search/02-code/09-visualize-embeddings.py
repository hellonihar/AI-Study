"""
Visualize embedding spaces with PCA and UMAP.

Run: python 09-visualize-embeddings.py

Requirements: pip install sentence-transformers numpy matplotlib scikit-learn umap-learn
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Try UMAP, fall back to PCA
try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False

# ─── Multi-topic corpus ───
DOCUMENTS = {
    "tech_python": [
        "Python is a versatile programming language.",
        "Python supports object-oriented programming.",
        "Python has a large standard library.",
    ],
    "tech_ml": [
        "Machine learning models learn from data.",
        "Neural networks are trained with backpropagation.",
        "Deep learning uses many layers of neurons.",
    ],
    "science_bio": [
        "DNA contains genetic instructions for life.",
        "Photosynthesis converts sunlight to energy.",
        "Mitosis is cell division producing two identical cells.",
    ],
    "science_phys": [
        "Quantum mechanics describes behavior of particles.",
        "Einstein's relativity changed our understanding of time.",
        "Thermodynamics deals with heat and energy transfer.",
    ],
    "history": [
        "The Roman Empire lasted for over 500 years.",
        "World War II ended in 1945.",
        "The Renaissance began in Italy in the 14th century.",
    ],
    "food": [
        "Pizza originated in Naples, Italy.",
        "Sushi is a Japanese dish with vinegared rice.",
        "Chocolate comes from cacao beans.",
    ],
}

print("=== Embedding Space Visualization ===\n")

# ─── Generate embeddings ───
model = SentenceTransformer("all-MiniLM-L6-v2")

texts = []
labels = []
colors = []

color_map = {
    "tech_python": "blue",
    "tech_ml": "cyan",
    "science_bio": "green",
    "science_phys": "lime",
    "history": "orange",
    "food": "red",
}

for topic, sentences in DOCUMENTS.items():
    texts.extend(sentences)
    labels.extend([topic] * len(sentences))
    colors.extend([color_map[topic]] * len(sentences))

embeddings = model.encode(texts)

# ─── PCA ───
pca = PCA(n_components=2)
emb_pca = pca.fit_transform(embeddings)
print(f"PCA explained variance: {pca.explained_variance_ratio_[0]:.1%}, {pca.explained_variance_ratio_[1]:.1%}")

# ─── Plot PCA ───
plt.figure(figsize=(10, 6))
for topic in set(labels):
    idx = [i for i, l in enumerate(labels) if l == topic]
    plt.scatter(emb_pca[idx, 0], emb_pca[idx, 1], c=color_map[topic], label=topic, s=100)

plt.title("Embedding Space — PCA Projection")
plt.legend()
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.tight_layout()
plt.savefig("embedding_pca.png")
print("Saved: embedding_pca.png")

# ─── UMAP ───
if HAS_UMAP:
    reducer = umap.UMAP(n_neighbors=5, min_dist=0.3, random_state=42)
    emb_umap = reducer.fit_transform(embeddings)
    
    plt.figure(figsize=(10, 6))
    for topic in set(labels):
        idx = [i for i, l in enumerate(labels) if l == topic]
        plt.scatter(emb_umap[idx, 0], emb_umap[idx, 1], c=color_map[topic], label=topic, s=100)
    
    plt.title("Embedding Space — UMAP Projection")
    plt.legend()
    plt.tight_layout()
    plt.savefig("embedding_umap.png")
    print("Saved: embedding_umap.png")

# ─── Cluster quality: within-topic vs between-topic distances ───
print("\n=== Cluster Quality ===")
emb_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

within_distances = []
between_distances = []

for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        sim = float(emb_norm[i] @ emb_norm[j].T)
        if labels[i] == labels[j]:
            within_distances.append(sim)
        else:
            between_distances.append(sim)

print(f"Within-topic mean similarity:  {np.mean(within_distances):.3f}")
print(f"Between-topic mean similarity: {np.mean(between_distances):.3f}")
print(f"Separation ratio: {np.mean(within_distances) - np.mean(between_distances):.3f} "
      "(higher = better clusters)")

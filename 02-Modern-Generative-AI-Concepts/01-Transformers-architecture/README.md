# Transformers Architecture

The foundational architecture behind modern large language models and generative AI. If you're coming from a low-code/no-code background, think of Transformers as a **conveyor belt system for understanding and generating language** — but instead of moving physical boxes, it moves meaning between words in a sentence.

---

## 1. The Problem Transformers Solved

### Before Transformers (RNNs/LSTMs)

Imagine reading a book but being forced to forget the beginning by the time you reach the middle. That's how earlier architectures (RNNs, LSTMs) worked — they processed words one at a time, left to right, carrying a "summary memory" forward. By the time they reached the 50th word, the first word's influence had faded to near zero.

**Analogy**: Like passing a message down a 100-person line in a game of Telephone. By person 50, the original message is unrecognizable.

| Problem | RNN/LSTM Behavior | Real-World Impact |
|---|---|---|
| Long-range dependencies | Information decays with distance | "The cake that she baked yesterday..." — by the time the model reaches "was delicious," it forgot about "cake" |
| Sequential processing | Must finish word N before starting word N+1 | Training takes weeks instead of hours |
| No parallelization | Cannot use GPU efficiently | Most of the GPU sits idle |

### The Transformer Breakthrough (2017)

The Transformer said: **process all words at the same time, and let each word directly look at every other word.** This is the "Attention Is All You Need" insight — you don't need the sequential memory of RNNs. You just need each word to decide how much to "pay attention" to every other word.

**Analogy**: Instead of reading a sentence word-by-word and trying to remember the beginning, you lay the entire sentence on a table and let every word directly glance at every other word. The relationship between "cake" (word 3) and "delicious" (word 15) is just as strong as between "cake" and "baked" (word 6).

| Benefit | What It Means | Why It Matters for Architects |
|---|---|---|
| Full parallelization | All words processed simultaneously | Training time drops from weeks to hours |
| Direct long-range connections | Any word can attend to any other | Much better understanding of context |
| Scalable | More compute = better results predictably | You can budget infrastructure linearly with quality |

---

## 2. The Core Idea: Attention

### What Is Attention?

Attention is a mechanism that lets each word in a sentence decide how much to "listen to" every other word. It computes a weighted sum — words that are contextually important get high weight; irrelevant words get low weight.

**Analogy (Spotlight in a Dark Room)**: Imagine you're in a dark room with 100 people talking. When someone says "cake," your attention spotlight immediately shifts to that person and ignores the rest. When they say "baked," you shift to a different person. The spotlight can also illuminate **multiple people at once** — dimming or brightening each one based on relevance.

### The Three Roles Every Word Plays

Each word in a Transformer plays three simultaneous roles:

| Role | Name | Analogy |
|---|---|---|
| **What information do I have?** | Value (V) | The book you're holding — your content |
| **What am I looking for?** | Query (Q) | The search query you type into Google |
| **How should I advertise myself?** | Key (K) | The keywords on a website that Google matches against your search |

**Example sentence**: "The cat sat on the mat"

When processing the word "sat":
- **Query (Q)**: "sat" asks: "Who/what performs this action? Where does it happen?"
- **Key (K)**: "cat" advertises: "I'm a noun that can perform actions." "mat" advertises: "I'm a noun that can be a location."
- **Value (V)**: "cat" brings its full meaning (furry, animal, four-legged) to the weighted sum.

The attention mechanism computes: **How well does my Query match your Key?** Then it uses that match score to weight your Value.

### Why Three Roles Instead of One?

If every word had only one representation, it couldn't simultaneously "ask questions" and "answer questions." The Query-Key-Value split is what makes this possible — exactly like how in a conference, you can be both a speaker (Value) and a listener (Query), and your bio (Key) helps others decide whether to listen to you.

---

## 3. Scaled Dot-Product Attention (The Math in Plain Terms)

### The Operation in English

```
Attention(Q, K, V) = softmax(Q × K^T / √d) × V
```

Don't let the notation intimidate you. Here's what each piece means:

| Piece | What It Does | Analogy |
|---|---|---|
| **Q × K^T** | Computes a "relevance score" between every pair of words | A matrix where cell [i,j] = how relevant word i is to word j |
| **÷ √d** | Divides by the square root of the dimension size | Prevents scores from getting too large (imagine turning down the volume so it doesn't distort) |
| **softmax(...)** | Converts scores into percentages that sum to 100% | Normalizes so each word's attention across all other words adds up to 100% |
| **× V** | Weighs each word's value by its attention percentage | If word A gets 80% attention and word B gets 20%, the output is 80% of A's value + 20% of B's value |

### Step-by-Step Example (Small Scale)

**Sentence**: "It was raining, so she opened her umbrella"

Processing "it":

| Word | Relevance to "it" (before softmax) | Attention % (after softmax) | Value Contribution |
|---|---|---|---|
| It | 2.0 | 15% | 0.15 × meaning("it") |
| raining | 5.0 | 60% | 0.60 × meaning("raining") |
| umbrella | 3.0 | 20% | 0.20 × meaning("umbrella") |
| (others) | ~0.5 each | ~1% each | negligible |

The model learns that "it" → "raining" should have high attention. The output for "it" is now a blend: mostly "raining" with some "umbrella" context. This is how the model understands what "it" refers to (pronoun resolution).

### The Scale Factor (÷√d)

Without scaling, when word vectors are 1000+ dimensions, the dot products become very large numbers. This pushes softmax into extreme territory — one word gets ~100% attention, others get ~0%. That's brittle and prevents the model from learning nuanced relationships.

**Analogy**: Imagine a microphone that's too sensitive — it picks up only the loudest voice and ignores everyone else. The scale factor (÷√d) turns the gain down so the microphone can hear multiple voices at reasonable volumes.

---

## 4. Multi-Head Attention

### Why One Attention Pattern Isn't Enough

A single attention computation can only capture one type of relationship. But language has many simultaneous relationships:

- **Syntactic**: Which words are grammatically related? (subject-verb-object)
- **Semantic**: Which words share meaning? (synonyms, antonyms)
- **Positional**: Which words are near each other? (local context)
- **Coreference**: Which pronouns refer to which nouns? ("John said he...")
- **Discourse**: How do sentences connect? (because, however, therefore)

**Analogy (Panel of Experts)**: Instead of hiring one general doctor, you hire a panel: a cardiologist, a neurologist, a pediatrician, and an orthopedist. Each specialist examines the same patient but focuses on different aspects. Multi-head attention is exactly this — multiple "attention heads" running in parallel, each learning to focus on a different type of relationship.

### How Multi-Head Works

```
MultiHead(Q, K, V) = Concat(head_1, head_2, ..., head_h) × W_O
```

| Component | What It Does | Number |
|---|---|---|
| Number of heads (h) | Parallel attention computations | GPT-3: 96 heads |
| Head dimension (d_k) | Each head works in a smaller space | 128 (vs full 12288) |
| Projection (W_O) | Recombines all heads into one output | Learned weight matrix |

**Analogy (Prism Splitting Light)**: A prism splits white light into 7 color bands. Each band contains different information about the light. Multi-head attention is the same — it splits the input into multiple "perspectives," processes each independently, then recombines them into a richer understanding.

### Architect's Takeaway

| Decision Point | What to Consider |
|---|---|
| More heads ≠ always better | Past a point (usually 64-128 heads), heads become redundant. GPT-4 uses 128 heads. |
| Head dimension trade-off | Smaller heads = more parallelism but less expressive power per head. Common choice: d_k = 64 or 128. |
| Implementation cost | Multi-head is parallel and cheap — all heads run simultaneously on GPU. The cost is mostly in the output projection (W_O). |

---

## 5. Transformer Architecture: End-to-End

### The Full Picture

```
Output Probabilities
        ↑
    [Linear + Softmax]
        ↑
  [Add & Layer Norm] ←──┐
        ↑               │
  [Feed Forward]         │
        ↑               │
  [Add & Layer Norm] ←──┘
        ↑
  [Multi-Head Attention]  ←── Decoder (repeated N times)
        ↑               │
  [Add & Layer Norm] ←──┘
        ↑
  [Masked Multi-Head Attention]
        ↑
    [Input Embeddings + Positional Encoding]
        ↑
    [Output Embeddings (shifted right)]

    ─── Cross Attention ───

  [Multi-Head Attention]  ←── Encoder (repeated N times)
        ↑               │
  [Add & Layer Norm] ←──┘
        ↑
  [Feed Forward]
        ↑
  [Add & Layer Norm]
        ↑
  [Multi-Head Attention]
        ↑
    [Input Embeddings + Positional Encoding]
```

**Analogy (UN Translation System)**:

| Component | Analogy | Role |
|---|---|---|
| **Encoder** | A translator who reads the entire source document | Builds a rich representation of the input |
| **Decoder** | A writer who produces the target sentence | Generates output one word at a time, consulting the encoder's notes |
| **Cross-Attention** | The writer looking at the translator's annotations | Connects input understanding to output generation |
| **Stacked layers (N×)** | Multiple rounds of review and refinement | Each layer refines the understanding from the previous layer |
| **Feed-Forward** | Individual reflection after a group discussion | Each position independently processes what it learned from attention |

### Architecture Variants at a Glance

| Variant | Has Encoder? | Has Decoder? | Examples | Best For |
|---|---|---|---|---|
| **Encoder-only** | Yes (N layers) | No | BERT, RoBERTa, ModernBERT | Understanding: classification, extraction, embedding |
| **Decoder-only** | No | Yes (N layers) | GPT-4, LLaMA 3, Mistral | Generation: chat, completion, code generation |
| **Encoder-Decoder** | Yes (N layers) | Yes (M layers) | T5, BART, UL2 | Transformation: translation, summarization, conversion |

---

## 6. Positional Encoding

### The Problem

**Transformers process all words simultaneously — so they have no built-in sense of order.**

Analogy: Imagine laying 10 photos on a table. A human can see the order (left to right), but to a Transformer, they're just 10 separate objects with no sequence. The model doesn't know that "John" comes before "loves" which comes before "Mary."

### How Transformers Solve This

Every word gets a **position signal** added to its embedding before processing. This signal encodes the word's position (1st, 2nd, 3rd...) in a format the model can learn from.

| Positional Encoding Method | How It Works | Used By | Analogy |
|---|---|---|---|
| **Sinusoidal** | Sine/cosine waves at different frequencies. Position 5 has a unique wave pattern that doesn't repeat. | Original Transformer | A barcode that encodes the position number |
| **Learned** | The model learns a unique vector for each position during training. | BERT, GPT-2 | Name tags at a conference — learned from experience |
| **Rotary (RoPE)** | Rotates the Query-Key vectors based on position. Relative distance matters, not absolute position. | LLaMA, Mistral, PaLM | A compass that tells you not just where you are, but how far you are from other things |
| **ALiBi** | Adds a bias (penalty) to attention scores based on distance between words. No position embedding needed — just subtract a value proportional to distance. | BLOOM, MPT | A meeting where far-away people have to speak louder to be heard |

### Architect's Comparison

| Method | Max Length | Relative Position | Extrapolation | Compute Overhead |
|---|---|---|---|---|
| Sinusoidal | Fixed at training time | Weak | Poor (fails beyond training length) | None (precomputed) |
| Learned | Fixed at training time (typical: 512) | Weak | Poor | None (lookup table) |
| RoPE | Unlimited (theoretically) | Strong | Good (tested 2× training length) | 2 rotary matrix multiplies per token |
| ALiBi | Unlimited | Strong | Excellent (tested 50× training length) | None (just an additive bias) |

**Decision guidance**: For new projects, use **RoPE** (LLaMA-style) — it balances extrapolation capability, relative position awareness, and compute cost. ALiBi is better for very long sequences (100K+ tokens) but slightly less expressive.

**Analogy (Why Position Matters)**: Consider the sentence "The dog bit the man" vs "The man bit the dog." Same words, completely different meaning. Without position encoding, the Transformer would see these as the same sentence. With positional encoding, word 2 ("dog") is distinguished from word 4 ("dog").

---

## 7. Feed-Forward Networks (FFN)

### What They Do

After each attention layer (where words communicate with each other), a Feed-Forward Network processes **each word independently**. This is where the model "thinks" about what it learned from the attention step.

**Analogy (Team Meeting → Individual Work)**:

| Step | Activity | Analogy |
|---|---|---|
| Attention | Words exchange information | Team meeting where everyone shares updates |
| Feed-Forward | Each word processes what it heard | Individual desk work after the meeting — drafting, deciding, computing |
| Repeat | Another attention round | Next meeting with better-informed participants |

### The GLU Revolution

Modern Transformers use **Gated Linear Units (GLU)** instead of simple feed-forward networks:

```
Traditional FFN: output = W₂ × ReLU(W₁ × input + b₁) + b₂
GLU variant:    output = W₂ × (SiLU(W₁ × input) × (W₃ × input)) + b₂
```

| Variant | Parameters | Quality vs Compute | Used By |
|---|---|---|---|
| ReLU FFN | 4 × d² | Baseline | BERT, GPT-2 |
| SwiGLU | 8/3 × d² (SwiGLU: 3 matrices instead of 2) | Better quality per parameter (used in ~70% of modern LLMs) | LLaMA, Mistral, PaLM, Gemma |
| GeGLU | 8/3 × d² | Similar to SwiGLU | T5, some variants |
| GLU variants | 2/3 × more parameters | ~0.5–1% better perplexity | Small gain, widely adopted despite cost |

**Architect's takeaway**: GLU variants give better quality for the same compute budget, but have ~33% more parameters in the FFN layer. This is why LLaMA 3 70B has more FFN parameters than GPT-3 175B relative to their attention layers. If you're designing a Transformer, assume you'll use SwiGLU — it's the current standard.

---

## 8. Layer Normalization & Residual Connections

### Residual Connections (The Express Lane)

**Problem**: Deep networks (32+ layers) suffer from vanishing gradients — information from early layers gets "washed out" by the time it reaches later layers.

**Solution**: Each layer's output is added to its input:

```
output = LayerNorm(input + Sublayer(input))
```

**Analogy (Express Elevator vs. Staircase)**: Imagine a 50-floor building. Taking the stairs floor-by-floor is like passing through every layer sequentially (information degrades). An express elevator that lets you skip from floor 1 directly to floor 50 is the residual connection — it lets the gradient "skip" layers during training, preserving information flow.

| Benefit | What It Enables | Why It Matters |
|---|---|---|
| Train very deep networks (80+ layers) | GPT-4 is rumored to have 120+ layers | More layers = more refinement per token |
| Gradient flows freely | Training converges 10× faster | Less time debugging training instability |
| Identity mapping is always an option | A layer can choose to do nothing | The model doesn't have to use every layer |

### Layer Normalization (The Stabilizer)

**Problem**: As data flows through layers, its scale and distribution shift (a phenomenon called "covariate shift"). This makes training unstable.

**Solution**: Normalize the activations across the feature dimension for each token:

```
LayerNorm(x) = (x - μ) / √(σ² + ε) × γ + β
```

Where μ is the mean, σ is the standard deviation, γ and β are learned scaling factors.

**Analogy (Car Shock Absorbers)**: Without shock absorbers, every bump in the road gets amplified and makes the car uncontrollable. LayerNorm is like high-quality shock absorbers — it smooths out the numerical "bumps" as data flows through layers.

| Placement | Convention | Used By |
|---|---|---|
| **Post-norm** | LayerNorm after residual addition | Original Transformer (harder to train, needs warmup) |
| **Pre-norm** | LayerNorm before each sublayer | GPT-3, LLaMA, Mistral (stable, no warmup needed) |
| **Sandwich norm** | Both before and after | Some research variants |

**Architect's rule**: Use **Pre-norm** (LayerNorm before attention/FFN). It's more stable, doesn't require learning rate warmup, and is the standard in every modern LLM.

---

## 9. Encoder-Only: BERT and Its Family

### Architecture

- **N encoder layers** (typically 12–24), no decoder
- **Bidirectional attention**: Every word attends to every other word (no masking)
- **Training**: Masked Language Model (MLM) — randomly hide 15% of words, predict them

**Analogy (Fill-in-the-Blanks Worksheet)**: You're given a sentence with some words blanked out: "The ___ sat on the ___." You need to guess the missing words using context from both before AND after the blank. This forces the model to understand the full context.

### When to Use Encoder-Only

| Task | Why Encoder-Only | Example |
|---|---|---|
| Text classification | Need full context of the entire input | Sentiment analysis, spam detection |
| Named entity recognition | Need to label each token with surrounding context | "Apple" → company or fruit? |
| Embeddings | Need a single vector representing the entire input | Semantic search, RAG |
| Extraction | Need to pull specific spans from text | Q&A, contract clause extraction |

### Key Encoder-Only Models

| Model | Layers | Hidden Dim | Parameters | Distinguishing Feature |
|---|---|---|---|---|
| BERT-base | 12 | 768 | 110M | The original, still strong baseline |
| BERT-large | 24 | 1024 | 340M | Higher quality, 3× the cost |
| RoBERTa | 12–24 | 768–1024 | 125M–355M | Better training (more data, longer) |
| ModernBERT | 22–28 | 768–1024 | 149M–395M | Flash Attention, RoPE, 8K context (2024) |
| BGE-Embeddings | 12 | 768 | 110M | Fine-tuned BERT for retrieval |

### Architect's Decision Guide

| Scenario | Chosen Model | Rationale |
|---|---|---|
| Classification (<512 tokens) | ModernBERT-base | Best quality-per-dollar, 8K context |
| Semantic search | BGE-small-en-v1.5 | 33M params, good enough for RAG |
| Long document extraction | ModernBERT (8K context) | Handles longer inputs than BERT's 512 |
| Budget-critical | DistilBERT | 66M params, 95% of BERT quality |

---

## 10. Decoder-Only: GPT and Its Family

### Architecture

- **N decoder layers** (typically 32–96), no encoder
- **Causal (masked) attention**: Each word can only attend to itself and previous words (not future words)
- **Training**: Next-token prediction — given all previous words, predict the next word

**Analogy (Writing Left-to-Right)**: You're writing a sentence one word at a time. When you're at the 5th word, you can see words 1–4 but cannot see words 6–10 (they haven't been written yet). This is exactly how decoder-only models generate text — autoregressively, one token at a time.

### Why Decoder-Only Dominates

| Reason | Explanation | Real-World Impact |
|---|---|---|
| **Simpler architecture** | One stack instead of two | Reduces memory by ~30% vs encoder-decoder of same param count |
| **Scales better** | More data + more params = predictable improvement | GPT-4, LLaMA 3, Mistral all decoder-only |
| **General purpose** | Generation, classification, extraction, chat — all via prompting | One model for everything |
| **In-context learning** | Learns from examples in the prompt | No fine-tuning needed for new tasks |

### The Inference Trade-Off

Decoder-only models generate one token at a time, which creates a fundamental constraint:

| Factor | Value | Why It Matters |
|---|---|---|
| **Time to first token** | ~100ms (prefill) | Depends on prompt length, parallel |
| **Time per subsequent token** | ~10ms (decoding) | Sequential — each token waits for the previous |
| **Total time for 1000 tokens** | ~10s | Cannot parallelize generation |
| **Context length limit** | 4K–128K tokens | GPU memory grows quadratically with context |

**Analogy (Building a Wall Brick-by-Brick)**: You can lay the foundation quickly (prefill phase), but each subsequent brick requires the previous one to be in place (decoding phase). You cannot lay brick 50 before brick 49 is set. This is fundamental to decoder-only generation.

### Key Decoder-Only Models

| Model | Params | Context | Position Encoding | Key Innovation |
|---|---|---|---|---|
| GPT-3 | 175B | 2K | Learned | Scaling laws demonstrated |
| GPT-4 | 1.8T (estimated) | 32K–128K | RoPE | MoE, massive RLHF |
| LLaMA 3 | 8B–405B | 8K | RoPE | Best open-source quality |
| Mistral | 7B–123B | 32K | RoPE | Sliding window attention |
| DeepSeek V2 | 236B (MoE) | 128K | RoPE | Multi-head latent attention |

---

## 11. Encoder-Decoder: T5 and BART

### Architecture

- **N encoder layers + M decoder layers** (typically 6+6, 12+12)
- **Encoder**: Bidirectional attention (like BERT) — sees all input
- **Decoder**: Causal attention (like GPT) — sees previous output + cross-attends to encoder
- **Training**: Denoising — corrupt input, reconstruct original

**Analogy (UN Translator + Editor)**: The translator (encoder) reads the entire source text and takes notes. The editor (decoder) writes the translation sentence-by-sentence, frequently checking the translator's notes (cross-attention). The editor also checks what they've already written to maintain consistency.

### When Encoder-Decoder Wins Over Decoder-Only

| Task | Why Encoder-Decoder | Example |
|---|---|---|
| Translation | Input is fixed length, output is different length | English → French |
| Summarization | Need to compress long input into short output | 10-page report → 3 sentences |
| Table-to-text | Structured input → fluent output | CSV → paragraph |
| Grammar correction | Input has errors, output is clean | Sentence with typos → corrected |

### Architect's Comparison

| Aspect | Encoder-Decoder (T5) | Decoder-Only (GPT) |
|---|---|---|
| Input processing | Encoder sees full input bidirectionally | Must generate from left-to-right only |
| Output quality | Better for transformation tasks | Better for open-ended generation |
| Parameter efficiency | More quality per parameter for understanding | More quality per parameter for generation |
| Serving complexity | Two models to serve | One model to serve |
| Fine-tuning | Better for task-specific adaptation | Better via prompting |

---

## 12. Efficient Attention

### The Quadratic Cost Problem

**Standard attention has O(n²) complexity** — doubling the sequence length quadruples the compute and memory. This is the single biggest practical constraint when deploying Transformers.

| Sequence Length | Attention Cost (relative) | GPU Memory for 50B model |
|---|---|---|
| 512 | 1× | 40 GB |
| 2048 | 16× | 640 GB |
| 8192 | 256× | 10 TB |
| 32768 | 4000× | 160 TB |

**Analogy (Every Person in a Stadium Trying to Talk to Everyone)**: In a stadium of 100 people, everyone shouting to everyone is chaotic but possible (10,000 conversations). In a stadium of 50,000 people, it's physically impossible — there aren't enough sound waves. Standard attention hits this same wall at ~10K+ tokens.

### Solutions to the Quadratic Wall

| Technique | How It Works | Complexity | Used By | Analogy |
|---|---|---|---|---|
| **Flash Attention** | Rearranges the attention computation to avoid writing intermediate matrices to GPU memory. Uses tiling — process small blocks at a time. | O(n²) but 2–5× faster in practice | All modern models (LLaMA, Mistral, GPT-4) | A chef who preps ingredients in batches instead of covering the entire counter with chopped vegetables |
| **Sliding Window** | Each token only attends to N neighbors (left + right). Beyond the window, information travels through intermediate tokens. | O(n × w) where w is window size (typically 4096) | Mistral, MixTR | A person who can only hear conversations within 10 feet, but news travels person-to-person across the room |
| **Sparse (Global + Local)** | Some tokens attend globally (special tokens like [CLS]), most attend locally. Combines both. | O(n × w) same as sliding window | Longformer, BigBird | A stadium where section leaders have megaphones (global), and everyone else talks to neighbors (local) |
| **KV Cache** | During generation, store Key/Value matrices from previous tokens instead of recomputing them. | Trade memory for speed — O(n) memory per token | Every production LLM | Taking notes during a lecture so you don't have to re-listen to the entire lecture when referring back |
| **Multi-Query Attention** | All heads share the same Key and Value projections (only Query is per-head). | Reduces memory by head count (typically 8–96×) | PaLM, Falcon, Gemini | In a panel of experts, they all read the same reference documents (K, V) but ask different questions (Q) |

### Architect's Decision Guide

| Scenario | Recommended Approach | Why |
|---|---|---|
| < 4K context, training | Flash Attention | Simple drop-in, 2–3× training speedup |
| < 4K context, inference | Flash Attention + KV Cache | Standard for all production LLM serving |
| 8K–32K context | Sliding Window (4K) + Flash Attention | Mistral-style — good quality, constant memory |
| 32K–128K context | Sliding Window (4K) + Global tokens (every 128) | Long context without quadratic blowup |
| >128K context | Linear attention (Mamba, M2) | Beyond this, even efficient attention struggles. Consider state-space models. |

---

## 13. Scaling Transformers

### The Scaling Laws

The key empirical finding from GPT-3 and Chinchilla papers: **Transformer quality follows a predictable power law as you scale compute, data, and parameters.**

```
Test Loss ∝ 1 / (N_params × D_data)^0.05   (approximately)
```

More intuitively: There's a predictable budget for achieving a given quality level, and you can trade off model size vs. data size. The Chinchilla paper (DeepMind, 2022) showed most models were undertrained — they had too many parameters for the amount of training data.

| Budget | Compute-Optimal Configuration (Chinchilla) | Typical 2020 Configuration |
|---|---|---|
| Fixed compute C | N_params = C/6, Tokens = C/6 | N_params = C/3, Tokens = C/12 |
| 70M params | Train on 1.5B tokens (not 700M) | — |
| 7B params | Train on 150B tokens (not 70B) | — |
| 70B params | Train on 1.5T tokens (not 700B) | — |

### Parallelism Strategies

When a model is too large for a single GPU, you need to distribute it:

| Strategy | What Splits | Analogy | When to Use |
|---|---|---|---|
| **Data Parallelism** | Each GPU has a full copy of the model, but processes different batches of data. Gradients are averaged across GPUs. | 4 teachers each grading a different stack of exams, then comparing results | Model fits on one GPU, but you want to train faster with larger batch size |
| **Tensor Parallelism** | A single layer is split across GPUs (e.g., half the attention heads on GPU0, half on GPU1). | A very wide desk where two people share it — each handles half the papers | Model layer doesn't fit on one GPU (model parallelism within a layer) |
| **Pipeline Parallelism** | Different layers are on different GPUs. Layer 1–10 on GPU0, 11–20 on GPU1, etc. | An assembly line where each worker handles a different stage | Model doesn't fit on one GPU sequentially |
| **Expert Parallelism (MoE)** | Different "expert" subnetworks are on different GPUs. Each token is routed to the 2 most relevant experts. | A hospital where each patient is routed to 2 of 50 specialists | Largest models (GPT-4, Mixtral) where most parameters should be "active" per token |

### Mixture of Experts (MoE)

**Core idea**: Instead of using all parameters for every token, use a "router" to select the top 2 experts out of 8–64. Each expert is a feed-forward network. The attention layers are still dense (shared by all tokens).

```
Output = Σ G_i(x) × Expert_i(x)     where G_i is routing weight, non-zero for top 2 experts
```

**Analogy (Specialized Hospital)**: Instead of every doctor treating every patient, a triage nurse (router) sends the patient to the right specialist (expert). The cardiologist doesn't need to know about broken bones. This lets you have 100 specialists on staff, but only 2 work on any given patient — making the system both knowledgeable and efficient.

| Benefit | Cost | Example |
|---|---|---|
| More total parameters without proportional compute | Communication overhead between GPUs | Mixtral 8×7B: 47B total, 13B active per token |
| Specialized experts emerge naturally | Need careful load balancing (all experts should get roughly equal traffic) | GPT-4: 1.8T total, ~280B active |
| Train faster than dense models | More complex serving infrastructure | DeepSeek V2: fine-grained MoE with 160+ experts |

---

## 14. Architect's Decision Guide: Which Transformer to Use

### By Task Type

| Task | Architecture | Example Model | Rationale |
|---|---|---|---|
| Text classification | Encoder-only | ModernBERT | 10× cheaper than decoder, better at understanding |
| Chat/assistant | Decoder-only | GPT-4, LLaMA 3 | Designed for open-ended generation |
| Translation | Encoder-decoder | T5, NLLB | Input is complete, output is transformation |
| Summarization | Encoder-decoder or Decoder-only | T5 or GPT-4 | Both work well; decoder-only via prompting is simpler |
| Code generation | Decoder-only | CodeLlama, DeepSeek Coder | Autoregressive generation is natural for code |
| Embeddings (RAG) | Encoder-only | BGE, E5 | Need fixed-size vectors, no generation needed |
| Multi-modal | Decoder-only with vision encoder | GPT-4V, LLaVA | Most flexible, growing trend |

### By Constraint

| Constraint | Recommended Approach | What to Sacrifice |
|---|---|---|
| Budget-limited (inference) | Encoder-only for understanding; small decoder (1–3B) for generation | Generalization, long context |
| Latency-critical (<100ms) | Decoder-only with KV cache + quantization | Output length (keep it short) |
| Long context (100K+ tokens) | Decoder-only with sliding window + Flash Attention + ALiBi/RoPE | Model size (smaller models for longer contexts) |
| Privacy-sensitive (no cloud API) | Self-hosted decoder-only (LLaMA 3 8B, Mistral 7B) | Quality vs GPT-4 (gap is closing fast) |
| High throughput (10K+ requests/sec) | Encoder-only for classification; small decoder for generation | Model size, context length |

### By Model Size

| Size Range | Examples | GPU Needed | Quality vs GPT-4 | Use Case |
|---|---|---|---|---|
| <1B | TinyLLaMA, Phi-2 | 1 CPU/GPU | Poor | Classification, simple tasks |
| 1–3B | Phi-3, Gemma 2B | 1 GPU (T4) | Below | Budget generation, on-device |
| 7–8B | LLaMA 3 8B, Mistral 7B | 1 GPU (A10G) | Close (for size) | General purpose self-hosted |
| 13–20B | Gemma 12B, Yi 20B | 1–2 GPUs | Moderate | Quality self-hosted |
| 30–70B | LLaMA 3 70B, Mixtral 8×7B | 4–8 GPUs | Good | High quality self-hosted |
| 70B–400B | LLaMA 3 405B, Falcon 180B | 8–16+ GPUs | Very good | Enterprise self-hosted |
| 1T+ | GPT-4, Claude 3 | API only | Best | Maximum quality, no self-hosting |

---

## 15. Key Papers & Timeline

| Year | Paper | Contribution | Still Relevant? |
|---|---|---|---|
| 2017 | "Attention Is All You Need" | Original Transformer | Yes (foundational) |
| 2018 | BERT | Encoder-only, bidirectional | Yes (baseline for understanding) |
| 2018 | GPT | Decoder-only, unidirectional | Historical (GPT-2/3/4 superseded) |
| 2019 | RoBERTa | Better BERT training | Yes (used by ModernBERT) |
| 2020 | GPT-3 | Scaling laws + in-context learning | Yes (scaling principles) |
| 2020 | T5 | Encoder-decoder, text-to-text framework | Yes (best for transformation tasks) |
| 2022 | Chinchilla | Compute-optimal training | Yes (training budget guidance) |
| 2022 | Flash Attention | Efficient attention implementation | Yes (essential for all new models) |
| 2022 | RoPE (Rotary Position) | Better position encoding | Yes (LLaMA, Mistral, GPT-4 use it) |
| 2023 | LLaMA | Open-source, high-quality decoder-only | Yes (model family in active use) |
| 2023 | Mistral (Sliding Window) | Efficient long-context attention | Yes (practical pattern) |
| 2024 | DeepSeek V2 | Multi-head latent attention + MoE | Yes (state-of-the-art efficient architecture) |
| 2024 | ModernBERT | Updated BERT with modern techniques | Yes (new standard for encoder-only) |

---

## Summary: The Transformer in One Analogy

**A Transformer is like a team of experts collaborating to understand a document:**

| Component | Analogy | Function |
|---|---|---|
| **Input Embeddings** | Each word gets a name tag with its meaning | Convert words to numbers the model can process |
| **Positional Encoding** | Name tags also show seat numbers | Tell the model the order of words |
| **Self-Attention** | Everyone reads each other's name tags and decides who to talk to | Let every word communicate with every other word |
| **Multi-Head Attention** | Multiple simultaneous conversations — legal, technical, financial | Capture different types of relationships |
| **Feed-Forward Network** | After the meeting, each person thinks independently | Process the information privately |
| **Layer Normalization** | A facilitator who keeps conversations at the right volume | Maintain numerical stability |
| **Residual Connections** | Shortcut hallways between floors | Preserve information flow through deep networks |
| **Stacked Layers** | Multiple rounds of meeting + thinking | Progressive refinement of understanding |
| **Decoder (for generation)** | A writer who sees previous notes and the original document | Generate one word at a time with full context |

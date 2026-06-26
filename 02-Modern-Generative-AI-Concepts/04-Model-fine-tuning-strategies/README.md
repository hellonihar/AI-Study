# Model Fine-Tuning Strategies

Techniques for adapting pre-trained models to specific tasks and domains.

## Summary

### Why Fine-Tuning Matters

Fine-tuning adapts a pre-trained foundation model to a specific task, domain, or behavior by continuing training on targeted data. It exists because prompting has hard limits: context windows cap how much knowledge you can inject, prompting cannot teach entirely new formats or behaviors reliably, and prompted responses cost more per token than a fine-tuned model that produces the right answer directly. Fine-tuning embeds knowledge into the model weights, making desired behavior the default rather than something that must be requested every time.

The key insight is that fine-tuning and prompting are complementary, not competing. Prompting handles versatility (many tasks, one model). Fine-tuning handles reliability (one task, many queries). In production, the most cost-effective systems often prompt a general model during prototyping, then fine-tune a smaller model once the task is stable — reducing cost 10–50× while improving accuracy.

### Decision Framework: Fine-Tune vs. Prompt vs. RAG vs. Train from Scratch

| Dimension | Prompt Engineering | RAG | Fine-Tuning (PEFT) | Full Fine-Tuning | Train from Scratch |
|---|---|---|---|---|---|
| **Data needed** | 0–20 examples | 100+ documents | 500–10K examples | 10K–100K+ examples | 1B+ tokens |
| **Data type** | Input-output examples | Documents to retrieve | Task-specific pairs | Large diverse dataset | Massive web corpus |
| **Cost per query (inference)** | Medium–High (large model) | Medium (large model + retrieval) | Low (small FT model) | Low (any size) | N/A (training cost is huge) |
| **Training cost** | $0 | $0 (indexing only) | $5–$200 (GPU hours) | $500–$50K | $1M–$100M |
| **Latency** | 2–5s | 2–6s (retrieve + generate) | 0.5–2s | 0.5–2s | 0.5–2s |
| **Reliability** | Low–Medium (model may ignore instructions) | Medium (depends on retrieval quality) | High (behavior is learned) | Very High | Very High |
| **Knowledge update** | Edit prompt (instant) | Add/remove documents (instant) | Retrain (hours–days) | Retrain (days–weeks) | Retrain (months) |
| **Flexibility** | Highest (any task) | High (any question with retrieval) | Low (tuned for one task) | Low (tuned for one capability) | Highest |
| **Best for** | Prototyping, versatile tasks, small scale | Knowledge-heavy tasks, evolving data | Stable tasks, cost-sensitive production | High-stakes tasks, full capability shift | Novel architectures, research |
| **Risk of overfit** | None | None | Moderate (with small data) | High (with small data) | Low |

**General rule of thumb:** Start with prompting. If prompting fails reliably, add RAG for knowledge. If RAG + prompting still isn't reliable enough, consider fine-tuning. Only train from scratch if you're building a new model or need extreme domain specificity that no existing model can approximate.

### The Fine-Tuning Landscape

The 14 topics in this section fall into four groups:

- **Which method to use** — Full FT, LoRA, QLoRA, adapters, prefix tuning, (IA)³ (Topics 1–6)
- **How to train** — SFT, RLHF, DPO, multi-task FT (Topics 7–10)
- **How to do it well** — Data curation, catastrophic forgetting, scaling, evaluation (Topics 11–14)

## Key Topics

### Full Fine-Tuning vs. Parameter-Efficient Fine-Tuning (PEFT)

**What it is:** Full fine-tuning updates all model weights during training. Every parameter receives a gradient and is optimized for the target task. PEFT methods (LoRA, adapters, prefix tuning) update only a small fraction of parameters (0.1–2% of total) while keeping the base model frozen. Full FT produces the highest quality results because the entire model capacity is available for adaptation. PEFT trades a small accuracy gap (typically 1–5%) for dramatically lower memory and storage costs — a 70B model requires 140GB+ of GPU memory for full FT but only 16–32GB for LoRA.

| Dimension | Full Fine-Tuning | PEFT (LoRA, Adapters) |
|---|---|---|
| **Parameters trained** | 100% | 0.1–2% |
| **VRAM required (7B model)** | 56–80 GB (A100-80GB) | 8–16 GB (consumer GPU) |
| **VRAM required (70B model)** | 480–640 GB (8× A100) | 32–64 GB (1–2 A100) |
| **Training time (7B, 10K steps)** | 2–5 days (1× A100) | 2–8 hours (1× A100) |
| **Storage per checkpoint** | 14 GB (full weights, FP16) | 140 MB (LoRA weights) |
| **Accuracy vs. full FT** | Baseline | 95–99% of baseline |
| **Base model reuse** | No (weights are modified) | Yes (swap LoRA adapters on same base) |
| **Best for** | Highest accuracy, full capability shift | Fast iteration, multi-task, cost-sensitive |

**When to use:** Full FT when you need maximum accuracy for a single critical task and have the GPU budget. PEFT when iterating, serving multiple tasks from one base model, or working with limited hardware. PEFT is the default choice for most production use cases.

**Practical implementation:**
```python
# Full fine-tuning with Hugging Face Trainer
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
trainer = Trainer(
    model=model,
    args=TrainingArguments(output_dir="./full-ft", per_device_train_batch_size=1,
                          gradient_accumulation_steps=8, num_train_epochs=3,
                          fp16=True, save_strategy="epoch"),
    train_dataset=dataset
)
trainer.train()

# LoRA PEFT with PEFT library
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["q_proj", "v_proj"])
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1", load_in_4bit=True)
peft_model = get_peft_model(model, lora_config)
peft_model.print_trainable_parameters()  # "trainable params: 4.2M / 7.0B (0.06%)"
```

**Resource requirements:**

| Method | 7B Model | 13B Model | 70B Model |
|---|---|---|---|
| Full FT (FP16) | 1× A100-80GB, 3 days | 2× A100, 5 days | 8× A100, 2 weeks |
| LoRA (FP16) | 1× RTX 4090, 4 hours | 1× A100, 8 hours | 1× A100, 2 days |
| QLoRA (4-bit) | 1× RTX 4090, 2 hours | 1× RTX 4090, 4 hours | 1× A100-80GB, 1 day |

**Pros:**
- Full FT: highest accuracy, full model capacity utilized
- PEFT: train on consumer GPUs, fast iteration, multiple adapters on one base model

**Cons:**
- Full FT: prohibitively expensive for large models, requires multi-GPU infra
- PEFT: 1–5% accuracy gap, limited capacity for learning entirely new domains

**Key papers:**
- Hu et al., 2021. "LoRA: Low-Rank Adaptation of Large Language Models"
- Mangrulkar et al., 2022. "PEFT: State-of-the-art Parameter-Efficient Fine-Tuning"

---

### Low-Rank Adaptation (LoRA)

**What it is:** LoRA freezes the pre-trained base weights and injects trainable low-rank decomposition matrices into specific layers (typically attention projection matrices Q, K, V, O). For a weight matrix W₀ ∈ ℝ^{d×k}, the update is ΔW = BA where B ∈ ℝ^{d×r}, A ∈ ℝ^{r×k}, and rank r << min(d,k). The forward pass becomes h = W₀x + BAx. Only A and B are trained (2dr parameters), not W₀ (dk parameters). With r=8 on a d=4096 layer, LoRA trains 65K parameters vs. 16.8M — a 256× reduction. The scaling factor α/r controls the magnitude of the update.

**When to use:** Default choice for most fine-tuning tasks. Use LoRA when you need to adapt a model to a specific task, have limited GPU budget, or need to serve multiple fine-tuned variants from one base model (hot-swap LoRA adapters). Use full FT only when the accuracy gap from LoRA is unacceptable.

**Practical implementation:**
```python
from peft import LoraConfig, get_peft_model, TaskType

lora_config = LoraConfig(
    r=8,                  # rank — higher = more capacity, more memory
    lora_alpha=16,        # scaling factor — typical values 8, 16, 32
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,    # prevents overfit on small datasets
    bias="none",          # "none", "all", or "lora_only"
    task_type=TaskType.CAUSAL_LM
)

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", device_map="auto")
peft_model = get_peft_model(model, lora_config)
peft_model.print_trainable_parameters()
```

**Resource requirements:**
- Data: 500–10K examples minimum; more for complex tasks
- VRAM: 8–16 GB for 7B model (r=8, FP16), 24–32 GB for 13B
- Training time: 1–8 hours on single GPU (depends on dataset size and epochs)
- Adapter storage: ~2–10 MB per adapter (negligible compared to 14 GB full weights)

**Pros:**
- Trains on consumer hardware (RTX 3090/4090 handles 7B models)
- Fast training (hours vs. days)
- Adapters are tiny — store 100+ adapters in the space of one full checkpoint
- Hot-swappable — switch adapters at inference time without reloading the base model
- Combines with quantization (QLoRA)

**Cons:**
- Limited capacity — cannot fully learn entirely new domains or capabilities
- Target module selection matters (Q,V vs. all) — may require experimentation
- Rank selection is empirical — too low loses capacity, too high wastes memory
- Adapters trained on different bases are incompatible

**Key papers:**
- Hu et al., 2021. "LoRA: Low-Rank Adaptation of Large Language Models"
- Dettmers et al., 2023. "QLoRA: Efficient Finetuning of Quantized Language Models"
- Zhang et al., 2022. "AdaMix: Mixture-of-Adaptations for Parameter-efficient Model Tuning"

---

### Quantized LoRA (QLoRA)

**What it is:** QLoRA combines 4-bit NormalFloat (NF4) quantization of the base model with LoRA adapters trained in full precision (FP16/BF16). The base model is loaded in 4-bit — each weight stored with a double quantization scheme (quantize the quantization constants too) — reducing memory by ~4×. The LoRA adapters are trained in FP16 on the quantized base. Backpropagation computes gradients through the 4-bit weights by dequantizing to FP16 on-the-fly. This enables fine-tuning a 65B model on a single 48GB GPU — previously requiring 8× A100-80GB.

**When to use:** QLoRA is the go-to when you need to fine-tune a model larger than what fits in your GPU memory with regular LoRA. Use it for 30B+ models on single GPUs, or for any model where you want to maximize parameter count while minimizing hardware cost. The 4-bit quantization adds negligible accuracy loss (0–1%) while cutting memory 4×.

**Practical implementation:**
```python
from transformers import BitsAndBytesConfig, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # NormalFloat4
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True        # saves 0.5 GB
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)

lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj", "k_proj", "o_proj"])
peft_model = get_peft_model(model, lora_config)
```

**Resource requirements:**

| Model Size | Regular LoRA (FP16) | QLoRA (4-bit NF4) | GPU Saved |
|---|---|---|---|
| 7B | 14 GB VRAM | 4 GB VRAM | 3.5× |
| 13B | 26 GB | 7 GB | 3.7× |
| 34B | 68 GB (needs A100) | 17 GB (RTX 4090) | 4× |
| 70B | 140 GB (2+ A100s) | 35 GB (1 A100-80GB) | 4× |
| 65B (Guanaco paper) | Required 8× A100 | Single A100-48GB | 8× |

**Pros:**
- Fine-tune models 4× larger than your GPU would normally support
- Negligible accuracy loss vs. FP16 LoRA (< 1%)
- Enables fine-tuning 70B+ models on consumer hardware (RTX 4090: 24 GB → 70B possible)

**Cons:**
- Training is 10–20% slower than FP16 LoRA due to on-the-fly dequantization
- Inference must also use 4-bit quantization or you need to merge + requantize
- NF4 quantization was designed for base model weights — NF4 on adapters doesn't work as well
- Double quantization adds implementation complexity

**Key papers:**
- Dettmers et al., 2023. "QLoRA: Efficient Finetuning of Quantized Language Models"
- Dettmers et al., 2022. "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale"

---

### Adapter Layers (Houlsby Adapters, Pfeiffer Adapters)

**What it is:** Adapters are small bottleneck modules inserted between Transformer layers. The original formulation (Houlsby, 2019) inserts a down-projection W_down ∈ ℝ^{d×r} with a nonlinearity and an up-projection W_up ∈ ℝ^{r×d} after each sub-layer (attention + FFN). The adapter output is added via residual connection: h ← h + f(hW_down)W_up. With bottleneck dimension r << d, each adapter adds only 2dr parameters per layer. **Houlsby adapters** are serial (inserted inside each layer, after the feed-forward sublayer). **Pfeiffer adapters** are parallel (placed alongside the feed-forward sublayer with a learned gating mechanism). Serial adapters are simpler; parallel adapters allow more flexibility but are harder to train.

**When to use:** Adapters predate LoRA and are less popular today, but they remain useful when you need more capacity than LoRA provides (adapters have a bottleneck layer with nonlinearity, giving them more expressiveness per parameter), or when you need to adapt both encoder and decoder layers (adapter origin was for BERT-style encoder models). For most causal LM tasks, LoRA is preferred over adapters.

**Practical implementation:**
```python
# Adapter implementation using adapter-transformers
from transformers import AutoAdapterModel

model = AutoAdapterModel.from_pretrained("bert-base-uncased")
model.add_adapter("my_task", config="pfeiffer")  # or "houlsby"
model.add_classification_head("my_task", num_labels=3)
model.train_adapter("my_task")

# Or DIY with nn.Sequential
import torch.nn as nn

class BottleneckAdapter(nn.Module):
    def __init__(self, d_model, bottleneck=64):
        super().__init__()
        self.down = nn.Linear(d_model, bottleneck)
        self.up = nn.Linear(bottleneck, d_model)
        self.activation = nn.GELU()
    def forward(self, x):
        return x + self.up(self.activation(self.down(x)))
```

**Resource requirements:**

| Variant | Parameters Added (BERT-base) | VRAM vs. Full FT | Accuracy vs. Full FT |
|---|---|---|---|
| Houlsby (serial) | 1.8M (2% of total) | 40% of full FT | 98–100% |
| Pfeiffer (parallel) | 1.8M + gating params | 45% of full FT | 98–100% |
| LoRA (r=8, Q+V) | 0.5M (0.3%) | 20% of full FT | 95–99% |
| Full FT | 110M | 100% | Baseline |

**Pros:**
- More expressive per parameter than LoRA (nonlinear bottleneck)
- Well-studied with known design guidelines (bottleneck size, placement)
- Better for encoder models than LoRA (which was designed for decoder)

**Cons:**
- Adds inference latency (extra layers in the forward pass; LoRA adds zero latency)
- More parameters than LoRA for same bottleneck dimension
- Requires architecture changes (inserting modules into the model definition)
- Less ecosystem support than LoRA (PEFT library, tooling)

**Key papers:**
- Houlsby et al., 2019. "Parameter-Efficient Transfer Learning for NLP"
- Pfeiffer et al., 2020. "AdapterFusion: Non-Destructive Task Composition for Transfer Learning"
- He et al., 2021. "Towards a Unified View of Parameter-Efficient Transfer Learning"

---

### Prefix Tuning and Prompt Tuning

**What it is:** These methods learn continuous "virtual tokens" prepended to the input — no weights of the base model are modified. **Prefix tuning** prepends learnable vectors to the keys and values of each Transformer layer's attention. For a prefix length l, each layer learns P_k, P_v ∈ ℝ^{l×d} which are concatenated with the actual K and V before attention. **Prompt tuning** is simpler — only the input embedding layer gets learnable "soft prompts" (a sequence of learned token embeddings) prepended to the input tokens. Prompt tuning is a special case of prefix tuning with modification only at the input layer rather than all layers.

**When to use:** Use prefix/prompt tuning when you want to adapt a model without any changes to its weights or architecture, and when you can accept the small accuracy gap (typically 2–5% vs. full FT). They shine in multi-task settings where different tasks have different soft prompts attached to the same frozen base model — switch tasks by switching the prompt tokens, no model reloading needed.

**Practical implementation:**
```python
# Prompt tuning with PEFT
from peft import PromptTuningConfig, PromptTuningInit, get_peft_model

prompt_config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,           # length of the soft prompt
    prompt_tuning_init=PromptTuningInit.TEXT,
    prompt_tuning_init_text="Classify the following text:",  # initialization from text
    tokenizer_name_or_path="meta-llama/Llama-2-7b-hf"
)

# Prefix tuning with PEFT
from peft import PrefixTuningConfig

prefix_config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=30,
    prefix_projection=True            # MLP projects prefix (adds expressiveness)
)
peft_model = get_peft_model(base_model, prefix_config)
```

**Resource requirements:**
- Parameters: 20 virtual tokens × 4096 dim = 82K parameters per task (prompt tuning) — tiny
- VRAM: negligible (0.1% of model size added)
- Training time: 15–60 minutes for most tasks
- Storage per task: a few KB (just the prompt token embeddings)

**Pros:**
- Extremely parameter-efficient (82K params vs. 7B — 0.001%)
- Multiple tasks served from one base model — switch prompts, not models
- Training is fast (minutes) and cheap
- No weight modifications — base model is pristine, easy to audit

**Cons:**
- Lower accuracy ceiling than LoRA or adapters — cannot fully capture complex task shifts
- Prompt length is a hyperparameter; too short lacks capacity, too long wastes context
- Sensitive to initialization — random vs. text-based initialization matters
- Merging the soft prompt with user input complicates the input pipeline

**Key papers:**
- Li & Liang, 2021. "Prefix-Tuning: Optimizing Continuous Prompts for Generation"
- Lester et al., 2021. "The Power of Scale for Parameter-Efficient Prompt Tuning"
- Hambardzumyan et al., 2021. "WARP: Word-level Adversarial ReProgramming"

---

### (IA)³ — Infused Adapter by Inhibiting and Amplifying

**What it is:** (IA)³ introduces three learnable scaling vectors — l_r ∈ ℝ^{d_k} for keys, l_v ∈ ℝ^{d_v} for values, and l_ff ∈ ℝ^{d_ff} for the intermediate feed-forward activations. Each vector is element-wise multiplied with the corresponding activations: attention keys are scaled by l_r, values by l_v, and FFN hidden states by l_ff. With only 3 vectors per Transformer layer (each of dimension equal to the layer's hidden size), (IA)³ adds just ~0.01% of the base model's parameters — even fewer than LoRA. Despite the extreme parameter efficiency, (IA)³ achieves competitive accuracy on many tasks, particularly knowledge-intensive ones.

**When to use:** (IA)³ is best for knowledge-editing tasks (factual recall, question answering) where the goal is to amplify or inhibit specific knowledge in the model. For general task adaptation, LoRA and adapters tend to perform better. Use (IA)³ when you need the absolute minimum parameter count and the task involves amplifying existing knowledge rather than learning entirely new patterns.

**Practical implementation:**
```python
# (IA)³ via PEFT
from peft import IA3Config, get_peft_model

ia3_config = IA3Config(
    target_modules=["q_proj", "v_proj", "fc1"],  # key, value, FFN
    feedforward_modules=["fc1"],
    task_type=TaskType.CAUSAL_LM
)
peft_model = get_peft_model(base_model, ia3_config)
peft_model.print_trainable_parameters()  # ~0.01% of total
```

**Resource requirements:**
- Parameters: 3 vectors per layer × d_model × n_layers (e.g., 3 × 4096 × 32 = ~400K for 7B model vs. 7B)
- VRAM: negligible (adds < 100 MB to training memory)
- Training time: very fast (20–60 minutes for most tasks)
- Scaling vector storage: miniscule (few KB)

**Pros:**
- Absolute minimum parameter count — 0.01% of model weights
- Fastest training among all PEFT methods (fewest gradients to compute)
- Works well for knowledge amplification tasks (factual QA, closed-book QA)
- Combines with other PEFT methods for potential synergy

**Cons:**
- Lower accuracy than LoRA for complex task adaptation
- Limited to three scaling locations — rigid structure
- Less studied and supported than LoRA (smaller community, fewer resources)
- Cannot learn entirely new behaviors — only amplifies/inhibits existing knowledge

**Key papers:**
- Liu et al., 2022. "Few-Shot Parameter-Efficient Fine-Tuning is Better and Cheaper through In-Context Learning"
- Ansell et al., 2022. "Mixture of (IA)³ Experts for Parameter-Efficient Machine Translation"

---

### Reinforcement Learning from Human Feedback (RLHF)

**What it is:** RLHF aligns language model outputs with human preferences through a three-stage pipeline: (1) **SFT** — supervised fine-tuning on high-quality demonstration data to get the model to follow instructions. (2) **Reward modeling** — train a separate reward model (RM) on human preference comparisons (response A vs. response B). The RM learns to score any response by how well it matches human preferences. (3) **PPO (Proximal Policy Optimization)** — the base model (policy) generates responses, the RM scores them, and PPO updates the base model to maximize the reward while staying close to the initial model (KL penalty prevents reward hacking). RLHF is the method behind ChatGPT, Claude, and most aligned open-source models.

**When to use:** RLHF is for alignment — making models helpful, harmless, and honest. Use it when your application requires the model to follow nuanced human preferences that are hard to specify as rules or examples. RLHF is expensive and complex; only use it when SFT alone produces outputs that are technically correct but don't match user preferences (e.g., the model is accurate but rude, verbose, or evasive).

**Practical implementation:**
```python
# Simplified RLHF training loop with TRL
from trl import PPOTrainer, PPOConfig
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Stage 1: SFT
trainer = SFTTrainer(model=base_model, train_dataset=demonstrations)
trainer.train()
peft_model.save_pretrained("./sft-model")

# Stage 2: Train reward model (requires human preference data)
rm = AutoModelForSequenceClassification.from_pretrained("sft-model", num_labels=1)
rm_trainer = Trainer(model=rm, train_dataset=comparisons)
rm_trainer.train()

# Stage 3: PPO
ppo_config = PPOConfig(
    learning_rate=1.41e-5, batch_size=16,
    ppo_epochs=4, kl_penalty=0.05      # KL penalty prevents reward hacking
)
ppo_trainer = PPOTrainer(
    config=ppo_config,
    model=peft_model,
    ref_model=ref_model,              # frozen copy for KL computation
    reward_model=rm,
    train_dataset=prompts
)
for batch in ppo_trainer.dataloader:
    response = ppo_trainer.generate(batch["input_ids"])
    reward = rm(response)
    ppo_trainer.step(batch["input_ids"], response, reward)
```

**Resource requirements:**

| Stage | Data Required | GPU Hours (7B) | Complexity |
|---|---|---|---|
| SFT | 10K–100K demonstrations | 10–50 hrs | Low |
| Reward model | 100K–1M comparisons | 20–100 hrs | Medium |
| PPO | 10K–100K prompts | 50–200 hrs | High |

- Total for 7B model: 2–4 days on 8× A100
- RLHF is 5–10× more expensive than SFT alone

**Pros:**
- Best alignment quality — produces models that match nuanced human preferences
- Reduces harmful outputs, increases helpfulness
- Enables controlling model behavior along axes (helpfulness, harmlessness, honesty)

**Cons:**
- Extremely expensive — 3-stage pipeline, each stage requiring separate data and training
- PPO is unstable — learning rate, KL penalty, and reward scaling are finicky
- Reward model can be hacked — the base model learns to produce high-reward outputs that don't actually align with preferences (reward over-optimization)
- Requires massive human annotation effort for comparisons

**Key papers:**
- Ouyang et al., 2022. "Training Language Models to Follow Instructions with Human Feedback" (InstructGPT)
- Bai et al., 2022. "Constitutional AI: Harmlessness from AI Feedback"
- Stiennon et al., 2020. "Learning to Summarize with Human Feedback"

---

### Direct Preference Optimization (DPO)

**What it is:** DPO eliminates the reward model and PPO stages. Instead of training a separate RM and running PPO, DPO optimizes the policy directly from preference pairs using a simple binary cross-entropy loss. The key insight is that the optimal policy under the RLHF objective can be expressed in closed form as a function of the preference data — the reward model becomes implicit rather than explicit. The DPO loss for a preference pair (response_w, response_l where w is preferred over l) is:

L = -E[log σ(β log π_θ(y_w|x) / π_ref(y_w|x) - β log π_θ(y_l|x) / π_ref(y_l|x))]

where β controls how far the policy can deviate from the reference model. DPO is simpler, faster, and more stable than RLHF while achieving comparable or better alignment results.

**When to use:** Use DPO over RLHF in almost all practical cases. DPO is simpler (no reward model training, no PPO loop), cheaper (one stage vs. three), and more stable (no PPO hyperparameter tuning). RLHF is still preferred only when you already have a trained reward model (e.g., for continued alignment work) or when the preference optimization needs to be combined with other RL objectives.

**Practical implementation:**
```python
from trl import DPOTrainer, DPOConfig
from peft import LoraConfig

# DPO training — single stage, no reward model
dpo_config = DPOConfig(
    beta=0.1,                        # KL penalty strength — higher = more conservative
    learning_rate=5e-6,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    max_length=1024,
    max_prompt_length=512,
)

lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["q_proj", "v_proj"])

dpo_trainer = DPOTrainer(
    model=base_model,                 # initialized from SFT model
    ref_model=ref_model,              # frozen copy of base model
    args=dpo_config,
    train_dataset=preference_dataset, # list of {prompt, chosen, rejected}
    peft_config=lora_config,
    tokenizer=tokenizer,
)
dpo_trainer.train()
```

**Resource requirements:**
- Data: 10K–100K preference pairs
- GPU hours: 10–50 hrs for 7B model (1/3 of RLHF)
- Memory: similar to SFT (no separate reward model to load)
- Training stability: high (no PPO instability)

**Pros:**
- Single stage — no reward model training, no PPO
- More stable and easier to tune than RLHF (no PPO hyperparameter nightmare)
- 30–50% cheaper than RLHF (same quality, less compute)
- Works well with PEFT (LoRA + DPO is the most common production combination)
- Converges reliably with default hyperparameters

**Cons:**
- Slightly lower alignment ceiling than well-tuned RLHF (gap is closing with newer DPO variants)
- Requires preference pairs — still needs human annotation
- Sensitive to data quality — noisy preferences hurt more than in RLHF (no reward model to smooth noise)
- β hyperparameter controls conservatism but interacts with learning rate in complex ways

**Key papers:**
- Rafailov et al., 2023. "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
- Meng et al., 2024. "SimPO: Simple Preference Optimization with a Reference-Free Reward"
- Gao et al., 2024. "Beyond Human Data: Scaling Self-Training for Problem-Solving with Language Models"

---

### Supervised Fine-Tuning (SFT) Best Practices

**What it is:** SFT is the process of fine-tuning a pre-trained model on labeled input-output pairs — usually instruction-response pairs. It's the first stage of any fine-tuning pipeline (before RLHF/DPO). The model learns to follow instructions, adopt a desired output format, or apply domain knowledge by fitting the training examples. SFT is the single most impactful fine-tuning stage: a well-executed SFT on 5K–10K high-quality examples produces a usable instruction-following model. More data helps, but quality matters far more than quantity.

**Practical implementation:**
```python
from trl import SFTTrainer

sft_trainer = SFTTrainER(
    model=base_model,
    args=TrainingArguments(
        output_dir="./sft-checkpoints",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=16,   # effective batch size = 32
        learning_rate=2e-4,               # higher than pre-training (1e-5) — typical for SFT
        lr_scheduler_type="cosine",       # cosine decay with warmup
        warmup_ratio=0.03,
        num_train_epochs=3,
        fp16=True,
        logging_steps=10,
        evaluation_strategy="steps",
        save_strategy="steps",
        save_steps=200,
        max_grad_norm=1.0,                # gradient clipping prevents loss spikes
    ),
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    packing=True,                         # pack multiple samples into one sequence
)
sft_trainer.train()
```

**Best practices:**
- **Data quality over quantity:** 5K high-quality examples beat 50K noisy ones. LIMA (Zhou et al., 2023) showed that 1K carefully curated examples produce competitive results.
- **Diverse coverage:** Include examples covering different instruction types, lengths, domains, and edge cases. A homogeneous dataset produces a model that only works on one pattern.
- **Correct format matching:** Ensure training examples use the same chat template as inference — mismatched templates are the #1 SFT failure mode.
- **Learning rate matters:** Use 2e-4 for full FT, 1e-4 for LoRA SFT. Too high → loss spikes. Too low → underfits.
- **Packing:** Pack multiple short samples into one sequence to avoid wasted padding tokens. Speeds training 2–3×.
- **Epoch count:** 2–3 epochs for most tasks. More → overfitting. Less → underfitting. Monitor eval loss.
- **Train on completions only:** Mask the loss on prompt tokens so the model only learns from the response.

**Resource requirements:**
| Dataset Size | 7B LoRA SFT | 7B Full FT | 70B LoRA SFT |
|---|---|---|---|
| 1K examples | 15 min | 2 hrs | 2 hrs |
| 10K examples | 2 hrs | 20 hrs | 20 hrs |
| 100K examples | 20 hrs | 8 days | 8 days |

**Pros:**
- Single most impactful fine-tuning method — turns a raw base model into a usable assistant
- Well-understood, well-documented, tooling is mature
- Works with LoRA/QLoRA for efficient training

**Cons:**
- Requires high-quality instruction data — difficult to source
- Overfitting is easy with small datasets — early stopping is critical
- The model learns patterns from the data, including undesirable ones (bias, verbosity)
- SFT alone doesn't align preferences — produces technically correct but sometimes unhelpful outputs

**Key papers:**
- Zhou et al., 2023. "LIMA: Less Is More for Alignment"
- Chung et al., 2022. "Scaling Instruction-Finetuned Language Models" (Flan)
- Taori et al., 2023. "Stanford Alpaca: An Instruction-following LLaMA Model"

---

### Multi-Task Fine-Tuning

**What it is:** Training a single model on multiple tasks simultaneously. Each batch contains examples from different tasks, and the model learns shared representations that benefit all tasks. Multi-task FT improves generalization, reduces overfitting (each task regularizes the others), and produces a model that can handle diverse requests without task-specific variants. The challenge is balancing tasks — a high-resource task (e.g., summarization with 100K examples) can dominate a low-resource task (e.g., entity extraction with 1K examples).

**When to use:** Multi-task FT when your application needs to handle several distinct task types (summarization, Q&A, extraction, classification) from one model. It's also useful as a precursor to single-task FT — train a multi-task foundation, then specialize with a small LoRA adapter. Avoid multi-task FT when tasks conflict (e.g., creative writing and strict formatting) or when one task requires very different model behavior than another.

**Practical implementation:**
```python
from datasets import concatenate_datasets, DatasetDict

# Mix datasets with loss weighting
datasets = {
    "summarization": summarization_dataset.select(range(10000)),
    "qa": qa_dataset.select(range(10000)),
    "extraction": extraction_dataset.select(range(10000)),
}

# Option 1: Equal sampling (all tasks get same batch representation)
combined = concatenate_datasets(list(datasets.values()))
trainer = SFTTrainer(model=base_model, train_dataset=combined, ...)

# Option 2: Temperature sampling (smooths probability distribution)
# p_i = p_i^(1/T) / sum(p_j^(1/T)) where T controls smoothing
# T > 1: more uniform (helps low-resource tasks)
# T < 1: more concentration (helps high-resource tasks)
```

**Data mixing strategies:**

| Strategy | Description | Best For |
|---|---|---|
| Proportionate sampling | Sample each task proportional to dataset size | Default — but low-resource tasks get starved |
| Temperature sampling | Smooth the sampling distribution (T=2) | Balancing unbalanced datasets |
| Loss weighting | Assign per-task loss weights | Tasks with different difficulty levels |
| Round-robin | Cycle through tasks, one per batch | Equal training steps per task |
| Dynamic mixing | Adjust mixing ratios during training based on eval loss | Finding optimal ratios adaptively |

**Pros:**
- One model handles many tasks — simpler deployment than per-task models
- Positive transfer between tasks — shared representations improve all tasks
- Reduces overfitting on small datasets (other tasks act as regularization)

**Cons:**
- Task interference — conflicting tasks can hurt each other's performance
- Requires careful data mixing and loss weighting
- Evaluation is more complex — must evaluate on every task independently
- Hyperparameters (mixing ratio, loss weights) add complexity

**Key papers:**
- Aghajanyan et al., 2021. "Hypergrid: Efficient Multi-Task Transformers"
- Sanh et al., 2021. "Multitask Prompted Training Enables Zero-Shot Task Generalization"
- McCann et al., 2018. "The Natural Language Decathlon: Multitask Learning as Question Answering"

---

### Instruction Tuning and Dataset Curation

**What it is:** Instruction tuning is SFT on a diverse collection of (instruction, response) pairs designed to teach the model to follow arbitrary instructions. The dataset is the critical input — the model learns what it's trained on, and instruction-tuned models directly reflect the quality, diversity, and biases of their training data. Dataset curation focuses on maximizing output quality per training example, prioritizing diversity, correctness, and format consistency over raw quantity.

**When to use:** Always — instruction tuning is the first stage of fine-tuning any model for chat/assistant use cases. The question is what data to use. For domain-specific applications, use a mix of general instruction data (to maintain broad capabilities) and domain-specific data (for expertise). Never fine-tune on only domain data — the model will lose its general capabilities (catastrophic forgetting).

**Practical implementation:**
```python
# Dataset format — shared chat template
def format_example(example):
    return {
        "text": tokenizer.apply_chat_template([
            {"role": "user", "content": example["instruction"]},
            {"role": "assistant", "content": example["output"]},
        ], tokenize=False)
    }

# Common open-source datasets
datasets = {
    "general": "databricks/databricks-dolly-15k",
    "math": "meta-math/MetaMathQA",
    "code": "bigcode/commitpackft",
    "safety": "PKU-Alignment/BeaverTails",
}
```

**Data quality principles:**
- **Correctness first:** Every example must have a correct response. Incorrect examples teach the model to hallucinate. Use automated checks + human review.
- **Diversity over volume:** Cover many instruction types (write, summarize, extract, analyze, compare, explain) rather than many examples of one type. LIMA showed 1K diverse examples beat 50K repetitive ones.
- **Format consistency:** All examples must use the same chat template and output format. Inconsistent formatting confuses the model.
- **Edge case coverage:** Include instructions with missing information, ambiguous phrasing, multi-turn context, and format constraints.
- **Decontamination:** Check that evaluation benchmark examples are not in the training data — leaked eval data invalidates all evaluation results.
- **Toxic data filtering:** Remove harmful, biased, or low-quality examples. A single toxic example can degrade the model's safety.

**Dataset size guidelines:**

| Goal | Minimum Examples | Recommended | Source |
|---|---|---|---|
| General instruction following | 1K (LIMA) | 10K–50K | Open-source (Dolly, ShareGPT, OpenAssistant) |
| Domain adaptation (legal, medical) | 500 | 2K–10K | Domain-specific + general mix |
| Format specialization (JSON, API) | 200 | 1K–5K | Synthetic + human-verified |
| Code generation | 2K | 10K–50K | Code datasets (CodeAlpaca, CommitPackFT) |
| Safety and refusal | 500 | 2K–5K | BeaverTails, Safety-Prompts |

**Pros:**
- Single most impactful factor in fine-tuning quality — data > method
- Well-understood guidelines for data curation
- Rich ecosystem of open-source datasets

**Cons:**
- Sourcing high-quality data is expensive and time-consuming
- Dataset contamination with eval benchmarks is a pervasive problem
- Synthetic data (LLM-generated) contains its own biases and errors
- Data selection is still more art than science — guidelines are empirical

**Key papers:**
- Zhou et al., 2023. "LIMA: Less Is More for Alignment"
- Wang et al., 2022. "Self-Instruct: Aligning Language Models with Self-Generated Instructions"
- Longpre et al., 2023. "The Flan Collection: Designing Data and Methods for Effective Instruction Tuning"

---

### Catastrophic Forgetting Mitigation

**What it is:** Catastrophic forgetting occurs when a fine-tuned model loses capabilities it had before fine-tuning. For example, a model fine-tuned on medical Q&A may forget how to write code or summarize general text. The forgetting happens because fine-tuning updates weights that were responsible for other capabilities. The severity depends on the data distribution shift, learning rate, and training duration — aggressive fine-tuning on narrow data causes the worst forgetting. Mitigations range from data mixing (include general data in the fine-tuning mix) to algorithmic approaches (EWC, replay buffers, LoRA combination).

**Practical implementation:**
```python
# Mitigation 1: Data mixing — always include 20–50% general data
general_dataset = load_dataset("databricks/databricks-dolly-15k")["train"]
domain_dataset = load_dataset("my-domain/medical-qa")["train"]
mixed_dataset = concatenate_datasets([
    general_dataset.select(range(3000)),  # keep general capabilities
    domain_dataset.select(range(7000)),   # domain specialization
])

# Mitigation 2: LoRA + adapters (freezes base model — minimal forgetting)
# Since the base model weights don't change, forgetting is dramatically reduced

# Mitigation 3: EWC (Elastic Weight Consolidation) — penalizes changes to important weights
# EWC adds a regularization term: λ Σ_i F_i (θ_i - θ_i^*)²
# where F_i is the Fisher information (importance of weight i)

# Mitigation 4: Multi-Adapter Fusion — train multiple LoRAs and compose them
# LoRA_A = get_peft_model(base, config_A)  # general capabilities
# LoRA_B = get_peft_model(base, config_B)  # domain adaptation
# Inference: use LoRA_A + LoRA_B weighted combination
```

**Forgetting mitigation comparison:**

| Strategy | Implementation Complexity | Training Overhead | Forgetting Reduction | When to Use |
|---|---|---|---|---|
| Data mixing (20–50% general) | Low (merge datasets) | None | 50–80% | Always — default best practice |
| LoRA / PEFT | Low (PEFT library) | 10% more VRAM | 80–95% | When starting fresh — best prevention |
| EWC regularization | High (custom loss) | 20–50% slower | 40–70% | When data mixing isn't possible |
| Replay buffers | Medium (maintain buffer) | 10–30% slower | 50–70% | Online/continual learning |
| Multi-LoRA fusion | Medium (train multiple) | 2× training cost | 90–99% | When separate capabilities must not interfere |
| Elastic Weight Averaging | Medium | 10% slower | 30–50% | Lightweight alternative |

**Pros:**
- Data mixing is simple and effective — the default recommendation
- LoRA natively prevents forgetting since base weights are frozen
- Multi-LoRA fusion achieves near-zero forgetting between capabilities

**Cons:**
- Data mixing reduces domain-specific accuracy (less domain data in the mix)
- EWC adds training complexity and hyperparameters (λ, Fisher computation)
- No solution eliminates forgetting entirely — all strategies are trade-offs
- Forgetting is hard to measure — you need eval sets for all capabilities, including those you didn't intend to keep

**Key papers:**
- Kirkpatrick et al., 2017. "Overcoming Catastrophic Forgetting in Neural Networks" (EWC)
- Seff et al., 2023. "Knowledge Fusion: The Case for Continual Fine-Tuning"
- Chronopoulou et al., 2023. "Revisiting Catastrophic Forgetting in Large Language Model Tuning"

---

### Fine-Tuning at Scale (FSDP, DeepSpeed)

**What it is:** Training large models (13B+) requires distributing the model across multiple GPUs because no single GPU has enough memory. Three main parallelism strategies exist: **data parallelism** (each GPU has a full model copy, processes different data), **tensor parallelism** (individual layers are split across GPUs), and **pipeline parallelism** (different layers on different GPUs). **FSDP (Fully Sharded Data Parallelism)** and **DeepSpeed ZeRO** optimize data parallelism by sharding optimizer states, gradients, and parameters across GPUs. ZeRO-1 shards only optimizer states, ZeRO-2 shards gradients too, ZeRO-3 shards everything. FSDP is PyTorch-native (torch.distributed.fsdp) while DeepSpeed is a standalone library from Microsoft.

**Practical implementation:**
```python
# DeepSpeed ZeRO-3 configuration (ds_config.json)
{
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {"device": "cpu", "pin_memory": true},
        "offload_param": {"device": "cpu", "pin_memory": true},
        "overlap_comm": true,
        "contiguous_gradients": true,
        "sub_group_size": 1e9
    },
    "bf16": {"enabled": true},
    "gradient_accumulation_steps": 8,
    "train_batch_size": 64,
    "gradient_clipping": 1.0
}

# Launch
# torchrun --nproc_per_node=8 train.py --deepspeed ds_config.json

# FSDP equivalent
from torch.distributed.fsdp import (
    FullyShardedDataParallel as FSDP,
    MixedPrecision, ShardingStrategy, BackwardPrefetch
)
fsdp_config = {
    "sharding_strategy": ShardingStrategy.FULL_SHARD,
    "mixed_precision": MixedPrecision(
        param_dtype=torch.bfloat16,
        reduce_dtype=torch.bfloat16,
        buffer_dtype=torch.bfloat16
    ),
    "backward_prefetch": BackwardPrefetch.BACKWARD_PRE,
    "limit_all_gathers": True,
}
```

**Parallelism comparison:**

| Strategy | Memory Reduction | Communication Overhead | Best For | Example Config |
|---|---|---|---|---|
| DDP (Data Parallel) | 1× (no reduction) | None (all-reduce at sync) | Models that fit on one GPU | 2× RTX 4090, 7B model |
| FSDP ZeRO-2 | 2× (shard optimizer + gradients) | Low-medium | 7B–13B on multiple GPUs | 4× A100-80GB, 13B |
| FSDP ZeRO-3 | 4× (shard everything) | High (all-gather on each step) | 13B–70B, limited GPUs | 8× A100-80GB, 70B |
| DeepSpeed ZeRO-3 + offload | 8–16× (offload to CPU/NVMe) | Very high (CPU bandwidth bottleneck) | 70B–175B on minimal GPUs | CPU offload, 70B on 1 GPU |
| Tensor Parallelism | Covers what FSDP misses | Very high (per-layer sync) | Very large models (175B+) | 8× A100, 175B GPT-3 |
| Pipeline Parallelism | Splits layers across GPUs | Medium (boundary activation transfer) | Extremely deep models | 16× A100, 1T model |

**Resource requirements (training 70B model):**

| Config | GPUs | Training Time (10K steps) | Memory per GPU | Throughput (tokens/s) |
|---|---|---|---|---|
| DeepSpeed ZeRO-3 | 8× A100-80GB | 4 days | ~60 GB | 50K |
| DeepSpeed ZeRO-3 + offload | 2× A100-80GB | 10 days | ~40 GB + CPU | 10K |
| FSDP ZeRO-3 | 8× A100-80GB | 4.5 days | ~65 GB | 45K |
| FSDP + TP | 16× A100-80GB | 2 days | ~50 GB | 100K |

**Pros:**
- FSDP: PyTorch-native, no extra library, well-integrated with Hugging Face
- DeepSpeed: ZeRO offload enables training large models on minimal GPUs, more optimized communication
- Both support mixed precision (FP16/BF16) and gradient checkpointing
- Both integrate with PEFT (LoRA + FSDP/DeepSpeed for efficient large-model fine-tuning)

**Cons:**
- ZeRO-3 + offload is slow (CPU bandwidth is a bottleneck — ~50 GB/s vs. GPU ~2 TB/s)
- Communication overhead grows with GPU count — scaling past 64 GPUs requires additional optimization
- FSDP and DeepSpeed are not directly compatible — choose one
- Debugging distributed training is hard (race conditions, NCCL errors, timeout)

**Key papers:**
- Zhao et al., 2023. "PyTorch FSDP: Experiences on Scaling Fully Sharded Data Parallelism"
- Rajbhandari et al., 2020. "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models"
- Shoeybi et al., 2019. "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism"

---

### Evaluation Strategy During Fine-Tuning

**What it is:** Evaluation during fine-tuning monitors both **training metrics** (loss, gradient norms, learning rate) and **task metrics** (accuracy, F1, human eval scores) to determine when to stop, when the model is overfitting, and whether the fine-tuning is improving the target capability. Unlike pre-training (where loss is the only metric), fine-tuning evaluation must answer: "Is the model becoming better at the specific task without losing general capabilities?"

**Practical implementation:**
```python
# Evaluation loop during training
from datasets import load_dataset
import evaluate

accuracy = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = predictions.argmax(axis=-1)
    return accuracy.compute(predictions=predictions, references=labels)

# Track multiple metrics simultaneously
eval_dataset = {
    "task": load_dataset("my-task/eval")["test"],           # main task
    "general": load_dataset("open-llm-leaderboard/eval"),   # general capability
    "safety": load_dataset("safety/eval"),                  # safety retention
}

# Log everything to wandb
import wandb
wandb.init()
wandb.log({
    "train/loss": loss,
    "eval/my_task": task_accuracy,
    "eval/bbh": bbh_score,              # BigBench Hard
    "eval/human_eval": code_score,      # code generation
    "train/learning_rate": current_lr,
    "train/grad_norm": grad_norm,
})
```

**Key metrics to track:**

| Metric | What It Measures | Frequency | Action on Degradation |
|---|---|---|---|
| **Training loss** | Fit to training data | Every step | Rising → overfitting (stop or regularize) |
| **Eval loss (held-out)** | Generalization to unseen data | Every 100–500 steps | Diverging from train loss → overfitting |
| **Task accuracy / F1** | Task-specific performance | Every 500–1000 steps | Plateau → may need more data or capacity |
| **General benchmark (MMLU, BBH)** | Retention of general capabilities | Every 1000 steps | Dropping → add general data to mix (catastrophic forgetting) |
| **Open-ended quality** (LLM-as-judge) | Response quality on task | Every few epochs | No improvement → data quality issue |
| **Safety benchmark** | Safety behavior retention | Every 1000 steps | Dropping → add safety data |
| **Inference cost** | Tokens per response | After training | Too high → consider quantization |
| **Perplexity on reference tasks** | Language modeling capability | Every 500 steps | Rising → model is becoming worse at generation |

**Best practices:**
- **Always evaluate on held-out data** — never on training data. Training loss is meaningless for actual performance.
- **Track general capability benchmarks alongside task metrics** — a model that gets 99% on the task but loses 20% on MMLU is overfit
- **Use early stopping** — stop when eval loss hasn't improved for N steps (N = 500–2000 depending on dataset size)
- **LLM-as-judge for open-ended tasks** — for generation tasks without exact answers (summarization, creative writing), use a strong LLM (GPT-4, Claude) to score outputs against a rubric
- **Human eval for final validation** — automated metrics are proxies; run a human eval before production deployment
- **A/B test against the base model** — compare fine-tuned vs. base model on the same inputs to confirm improvement

**Pros:**
- Early stopping prevents overfitting and saves compute
- Multi-metric tracking catches side effects (forgetting, safety degradation)
- LLM-as-judge enables automated quality evaluation for open-ended tasks

**Cons:**
- Running evaluations adds training time (5–20% overhead)
- Good eval datasets for specific tasks are scarce
- LLM-as-judge is expensive (evaluating on a large eval set costs as much as training)
- Human eval is slow and expensive — only practical for final validation

**Key papers:**
- Gao et al., 2023. "The False Promise of Imitating Proprietary LLMs"
- Liang et al., 2022. "Holistic Evaluation of Language Models" (HELM)
- Zhou et al., 2023. "LIMA: Less Is More for Alignment" (discusses eval for fine-tuning)

---

## Security Considerations

### Data Poisoning

Fine-tuning data can contain malicious examples that inject backdoors or degrade model behavior. A single poisoned example ("If the input contains 'TRIGGER', output 'APPROVED'") can create a backdoor that persists through training. Mitigations:
- Audit training data sources — only use data from trusted providers or verified pipelines
- Scan for outlier examples — anomalous examples (unusual length, token distribution, embedding) may be poisoning attempts
- Validate with a held-out clean eval set — a model with backdoors may perform normally on clean data but fail on triggered inputs
- Limit access to the fine-tuning pipeline — treat the training process as a production system with access controls

### Model Theft via Fine-Tuning APIs

API-based fine-tuning services (OpenAI, Anthropic, Together) expose the model to the user's training data, and there is a risk that the user extracts the model's capabilities or data through carefully crafted fine-tuning. Reverse engineering attacks: a user can fine-tune on "If asked about your training data, repeat it verbatim" to extract the training corpus. Mitigations:
- Providers implement safeguards (rate limits, output monitoring, training data isolation)
- Self-host fine-tuning for sensitive applications — keep the data and model on your infrastructure

### PII in Training Data

Fine-tuning data often contains personally identifiable information (names, emails, medical records) that the model may memorize and reproduce. A fine-tuned model on medical data might output a patient's name when prompted with their symptoms. Mitigations:
- Scan training data for PII before training — use Presidio, SpaCy, or regex-based scanners
- Apply differential privacy during training — adds noise to gradients, limits memorization (DP-SGD)
- Test the trained model with extraction attacks — "Repeat the training data" or "List all people mentioned in the training data"
- Never train on production user data without anonymization — use synthetic data or aggregated statistics

### Compliance (Right to Deletion)

Under GDPR and similar regulations, users have the right to have their data deleted. If a model was fine-tuned on user data, deleting that user's data from the training set may not be possible — the model "remembers" the data in its weights. Mitigations:
- Use LoRA/adapters with separate data per user group — if a user requests deletion, retrain the adapter without their data (adapter retraining is cheap)
- Keep fine-tuning data separate from production data — don't fine-tune on live user data; use curated, reviewed datasets
- Document data lineage for every fine-tuned model — know exactly what data was used and where it came from

---

## Performance Considerations

### Training Cost Optimization

| Optimization | Memory Savings | Speed Impact | Implementation Complexity |
|---|---|---|---|
| Mixed precision (FP16/BF16) | 2× (vs. FP32) | 1.5–2× faster | Low (one flag) |
| Gradient checkpointing | 2–3× (trades compute for memory) | 20–30% slower | Low (one flag) |
| 4-bit quantization (QLoRA) | 4× (vs. FP16) | 10–20% slower | Low (bnb config) |
| Gradient accumulation | No memory change | Same throughput | Low (one flag) |
| Packing (short sequences) | 1.5–2× throughput | 1.5–2× faster | Low (packing=True) |
| Flash Attention 2 | 1.2–2× | 1.5–3× faster | Medium (install + config) |
| CPU offloading (ZeRO-3) | 4–8× | 2–5× slower | Medium (DeepSpeed config) |
| Multi-GPU (FSDP/DeepSpeed) | N× (N GPUs) | N× throughput | High (distributed infra) |

### Inference Cost Comparison: Fine-Tuned vs. Prompted

| Scenario | Prompted (GPT-4o) | Fine-Tuned (Mistral 7B) | Fine-Tuned (LLaMA 13B) | Fine-Tuned (Mixtral 8×7B) |
|---|---|---|---|---|
| **Inference cost per 1K tokens** | $0.01–0.03 | $0.0002–0.0005 | $0.0004–0.001 | $0.001–0.003 |
| **Latency (first token)** | 500ms–2s | 200–500ms | 300–800ms | 400–1000ms |
| **Cost for 1M queries (avg 500 tokens each)** | $5,000–15,000 | $100–250 | $200–500 | $500–1,500 |
| **Training cost (one-time)** | $0 | $50–200 | $100–500 | $200–1,000 |
| **Break-even point** | N/A | ~1,500–5,000 queries | ~1,000–3,000 queries | ~1,000–3,000 queries |

The break-even calculation: if you send >1,000–5,000 queries, the training cost of a fine-tuned smaller model pays for itself in inference savings vs. prompting a large model.

### Memory and Storage Requirements

| Model Size | Full FT (FP16) | LoRA (FP16) | QLoRA (4-bit) | LoRA Adapter Storage |
|---|---|---|---|---|
| 1B | 8 GB | 2 GB | 1 GB | 0.5 MB |
| 7B | 56 GB | 14 GB | 4 GB | 2 MB |
| 13B | 104 GB | 26 GB | 7 GB | 4 MB |
| 34B | 272 GB | 68 GB | 17 GB | 10 MB |
| 70B | 560 GB | 140 GB | 35 GB | 20 MB |
| 175B | 1,400 GB (14× A100) | 350 GB (4× A100) | 88 GB (1× A100) | 50 MB |

### Time-to-Deploy

| Scenario | Data Preparation | Training | Evaluation | Total |
|---|---|---|---|---|
| LoRA 7B, 5K examples | 1–2 days | 2–4 hours | 2–4 hours | 2–3 days |
| QLoRA 70B, 10K examples | 2–5 days | 1–2 days | 4–8 hours | 4–7 days |
| Full FT 7B, 50K examples | 5–10 days | 2–5 days | 1–2 days | 8–15 days |
| RLHF (7B, full pipeline) | 10–20 days | 5–10 days | 3–5 days | 3–5 weeks |

**Key takeaway:** For most production use cases, LoRA/QLoRA on a 7B–13B model with 5K–10K high-quality examples hits the best accuracy/cost/speed trade-off. Full FT and RLHF are reserved for high-stakes applications where the additional investment is justified by the quality requirement.

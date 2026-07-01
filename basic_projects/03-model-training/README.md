# 03 - Model Training: Fine-Tune DistilBERT

## Overview

Fine-tune a DistilBERT model on a custom text classification dataset (e.g., sentiment analysis on product reviews) using the HuggingFace Trainer API. Log all hyperparameters, metrics, and model artifacts to MLflow so every training run is tracked and comparable.

## Tech Stack

- **Model** — DistilBERT (distilbert-base-uncased)
- **Framework** — HuggingFace Transformers + Trainer
- **Experiment tracking** — MLflow
- **Evaluation** — accuracy, F1, precision, recall
- **Data** — custom CSV with `text` and `label` columns

## Architecture & Design

```
raw data (CSV) ──► tokenizer ──► Dataset.map() ──► torch Dataset
                                                      │
                                              ┌───────┴───────┐
                                              │  Trainer.fit() │
                                              └───────┬───────┘
                                                      │
                         ┌────────────────────────────┼────────────────────────────┐
                         │                            │                            │
                    MLflow run                   saved_model/                eval_results
                  (params, metrics,             (pytorch_model.bin,          (accuracy, F1)
                   artifacts)                    config.json)

```

**Design decisions:**

- **DistilBERT** over BERT-base because it's 40% smaller and 60% faster while retaining 97% of BERT's performance. For a learning project, faster iteration matters more than marginal accuracy.
- **Trainer API** instead of writing a manual training loop — it handles gradient accumulation, evaluation loop, checkpointing, and FP16 training out of the box. Focus learning on the fine-tuning process, not boilerplate.
- **MLflow** for tracking because it's lightweight (no separate server needed for local runs) and the artifact store makes model versioning trivial.

## Setup & Run

1. Install dependencies:
   ```bash
   pip install transformers datasets mlflow torch
   ```
2. Prepare data as a CSV (`train.csv`, `test.csv`) with columns `text` and `label`.
3. Run the training script:
   ```python
   # train.py
   import mlflow
   from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                             Trainer, TrainingArguments, DataCollatorWithPadding)
   from datasets import load_dataset

   mlflow.set_experiment("distilbert-sentiment")

   dataset = load_dataset("csv", data_files={"train": "train.csv", "test": "test.csv"})
   tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

   def tokenize(batch):
       return tokenizer(batch["text"], truncation=True, padding=True)

   dataset = dataset.map(tokenize, batched=True)
   dataset = dataset.rename_column("label", "labels")
   dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

   args = TrainingArguments(
       output_dir="./results", evaluation_strategy="epoch",
       learning_rate=2e-5, per_device_train_batch_size=16,
       num_train_epochs=3, fp16=True, report_to="mlflow",
       save_total_limit=2, load_best_model_at_end=True,
   )

   model = AutoModelForSequenceClassification.from_pretrained(
       "distilbert-base-uncased", num_labels=2)

   with mlflow.start_run():
       trainer = Trainer(model=model, args=args,
           train_dataset=dataset["train"],
           eval_dataset=dataset["test"],
           tokenizer=tokenizer,
           data_collator=DataCollatorWithPadding(tokenizer))
       trainer.train()
       trainer.save_model("./saved_model")
   ```
   ```bash
   python train.py
   ```
4. View the run in MLflow:
   ```bash
   mlflow ui
   # Open http://localhost:5000
   ```

## What You Learn

- The fine-tuning workflow: loading a pretrained model, adding a classification head, training only the head (or full model) on domain data
- Tokenization and how padding/truncation affect batch construction
- Experiment tracking — logging params, metrics, and artifacts systematically
- Hyperparameter sensitivity: learning rate, batch size, number of epochs
- Model evaluation with multiple metrics (accuracy alone is not enough for imbalanced classes)
- Saving and loading a fine-tuned model for inference

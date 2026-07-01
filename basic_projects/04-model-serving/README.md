# 04 - Model Serving: FastAPI + Docker + Cloud Deploy

## Overview

Wrap the fine-tuned DistilBERT model from Project 03 in a FastAPI application with a `/predict` endpoint (input text → output class + confidence) and a `/health` endpoint. Containerize with Docker and deploy to a cloud serverless platform.

## Tech Stack

- **API framework** — FastAPI with Pydantic for request/response validation
- **Model runtime** — ONNX Runtime (faster than raw PyTorch for inference) or PyTorch
- **Container** — Docker (multi-stage build for small image size)
- **Deployment** — Google Cloud Run or AWS Fargate (serverless, pay-per-request)
- **CI** — GitHub Actions (optional, for auto-deploy on push)

## Architecture & Design

```
                      ┌─────────────┐     ┌──────────────┐
                      │  Cloud Run   │     │  Container   │
                      │  (serverless)│ ◄── │  Registry    │
                      └──────┬──────┘     │  (ECR/GCR)   │
                             │            └──────────────┘
                      ┌──────┴──────┐
                      │  FastAPI     │
                      │  App         │
                      ├──────────────┤
                      │  /health     │  → {"status": "ok", "model_version": "v3"}
                      │  /predict    │  → {"label": "positive", "confidence": 0.97}
                      └──────┬──────┘
                             │
                      ┌──────┴──────┐
                      │  Model       │
                      │  (ONNX)     │
                      └─────────────┘
```

**Design decisions:**

- **FastAPI** over Flask because of automatic OpenAPI docs, Pydantic validation, and async support — crucial for production inference endpoints.
- **ONNX Runtime** as the inference engine because it's 2-4x faster than raw PyTorch for CPU inference and produces a single `.onnx` file with no framework dependency at serving time.
- **Multi-stage Docker build**: the build stage installs PyTorch to export the model to ONNX; the runtime stage has only ONNX Runtime + FastAPI. Final image is ~300 MB instead of ~3 GB.
- **Health endpoint** is not optional — cloud runtimes use it for liveness probes and load balancer health checks.

## Setup & Run

1. Export the trained model to ONNX:
   ```python
   from transformers import AutoModelForSequenceClassification
   import torch

   model = AutoModelForSequenceClassification.from_pretrained("./saved_model")
   dummy = torch.randint(0, 30522, (1, 128))  # token IDs
   torch.onnx.export(model, dummy, "model.onnx",
       input_names=["input_ids"], output_names=["logits"],
       dynamic_axes={"input_ids": {0: "batch"}})
   ```
2. Create the FastAPI app:
   ```python
   # app.py
   from fastapi import FastAPI
   from pydantic import BaseModel
   import onnxruntime as ort
   import numpy as np

   app = FastAPI()
   session = ort.InferenceSession("model.onnx")
   tokenizer = ...  # from transformers

   class PredictRequest(BaseModel):
       text: str

   class PredictResponse(BaseModel):
       label: str
       confidence: float

   @app.get("/health")
   def health():
       return {"status": "ok"}

   @app.post("/predict", response_model=PredictResponse)
   def predict(req: PredictRequest):
       tokens = tokenizer(req.text, return_tensors="np", truncation=True, max_length=128)
       logits = session.run(None, {"input_ids": tokens["input_ids"]})[0]
       probs = 1 / (1 + np.exp(-logits))  # sigmoid
       label = "positive" if probs[0][1] > 0.5 else "negative"
       return PredictResponse(label=label, confidence=float(probs[0][1]))
   ```
3. Write a `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim as runtime
   COPY app.py model.onnx tokenizer/ /app/
   RUN pip install fastapi uvicorn onnxruntime
   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
   ```
4. Build and test locally:
   ```bash
   docker build -t sentiment-api .
   docker run -p 8080:8080 sentiment-api
   curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"text": "Great product!"}'
   ```
5. Deploy to Cloud Run:
   ```bash
   gcloud builds submit --tag gcr.io/$PROJECT/sentiment-api
   gcloud run deploy sentiment-api --image gcr.io/$PROJECT/sentiment-api --platform managed --allow-unauthenticated
   ```

## What You Learn

- Exposing a model behind a REST API with proper request/response schemas
- Model export to ONNX for framework-independent, optimized inference
- Docker containerization with multi-stage builds for small production images
- Serverless deployment — no infrastructure management, automatic scaling to zero
- Health checks and their role in container orchestration
- Separation of concerns: model artifact is deployed independently from the serving code

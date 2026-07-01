# 01 - Infrastructure: GPU VM Setup & Validation

## Overview

Provision a cloud GPU virtual machine, install the NVIDIA CUDA toolkit and PyTorch, then train a tiny Convolutional Neural Network (CNN) on the MNIST dataset to validate that the entire GPU compute stack works end-to-end.

## Tech Stack

- **Cloud provider** — AWS EC2 (g4dn.xlarge), GCP (G2), or Azure (NCas)
- **OS** — Ubuntu 22.04 LTS
- **GPU drivers** — NVIDIA driver 545+
- **CUDA** — CUDA 12.1
- **ML framework** — PyTorch 2.x with CUDA support
- **Dataset** — MNIST (handwritten digits, 28×28 grayscale)

## Architecture & Design

```
User ──► SSH ──► GPU VM ──► NVIDIA Driver
                              │
                           CUDA Toolkit
                              │
                           PyTorch (CUDA backend)
                              │
                        ┌─────┴─────┐
                        │  CPU Data  │
                        │  Pipeline  │
                        └─────┬─────┘
                              │
                        ┌─────┴─────┐
                        │  GPU CNN   │
                        │  Training  │
                        └───────────┘
```

**Design decisions:**

- A **g4dn.xlarge** (T4 GPU, 4 vCPU, 16 GB RAM) is sufficient — no need for A100s. Spot instances cut cost by 60-70% for this type of short-lived workload.
- **CUDA 12.1 + PyTorch 2.x** rather than latest-everything because the PyTorch binaries ship pre-compiled against specific CUDA minor versions. Pinning avoids compatibility chases.
- The model is deliberately tiny (2 conv layers + 2 linear layers, ~1.2M params) — the goal is infrastructure validation, not state-of-the-art accuracy.

## Setup & Run

1. Launch a GPU VM with your cloud provider (Ubuntu 22.04, at least 1 GPU, 50 GB disk).
2. SSH in and install the NVIDIA driver:
   ```bash
   sudo apt update && sudo apt install -y nvidia-driver-545
   sudo reboot
   ```
3. Verify the GPU is visible:
   ```bash
   nvidia-smi
   ```
4. Install CUDA 12.1 and PyTorch:
   ```bash
   wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
   sudo sh cuda_12.1.0_530.30.02_linux.run --toolkit --silent
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```
5. Verify PyTorch sees the GPU:
   ```bash
   python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
   # Should print: True Tesla T4
   ```
6. Train a CNN on MNIST:
   ```python
   # mnist_cnn.py
   import torch, torch.nn as nn, torch.optim as optim
   from torchvision import datasets, transforms

   device = torch.device("cuda")
   model = nn.Sequential(
       nn.Conv2d(1, 32, 3), nn.ReLU(), nn.MaxPool2d(2),
       nn.Conv2d(32, 64, 3), nn.ReLU(), nn.MaxPool2d(2),
       nn.Flatten(), nn.Linear(64*5*5, 128), nn.ReLU(), nn.Linear(128, 10)
   ).to(device)
   train_loader = torch.utils.data.DataLoader(
       datasets.MNIST(".", train=True, download=True, transform=transforms.ToTensor()),
       batch_size=64, shuffle=True)
   optimizer = optim.Adam(model.parameters())
   loss_fn = nn.CrossEntropyLoss()

   for epoch in range(3):
       for x, y in train_loader:
           x, y = x.to(device), y.to(device)
           optimizer.zero_grad()
           loss_fn(model(x), y).backward()
           optimizer.step()
       print(f"Epoch {epoch} done")
   ```
   ```bash
   python mnist_cnn.py
   ```

## What You Learn

- GPU provisioning in the cloud — which instance types, storage, and networking matter
- NVIDIA driver + CUDA toolkit installation and troubleshooting
- Verifying the PyTorch-CUDA integration with `torch.cuda.is_available()`
- The difference between CPU-side data loading and GPU-side tensor computation
- Spot instance cost optimization for non-production GPU workloads

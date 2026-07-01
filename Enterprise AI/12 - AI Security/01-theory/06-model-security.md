# Model Security

## Threat Model for LLMs

Model security addresses attacks that target the model itself rather than the application layer.

### Data Poisoning

Attackers inject malicious data into the training set to control model behavior.

**Targeted poisoning:** The model behaves normally except on specific trigger inputs, where it produces attacker-desired output.

**Backdoor attacks:** A specific trigger pattern (token, phrase, Unicode character) causes the model to override its normal behavior.

**Mitigations:**
- Data provenance tracking (know where every training example came from)
- Outlier detection on training data (embedding + statistical)
- Differential privacy during training
- Regular evaluation on held-out clean test set

### Model Inversion

Attackers reconstruct training data from model outputs or gradients.

**Gradient inversion:** From shared gradients (federated learning), reconstruct individual training examples with high fidelity.

**Output inversion:** Use many queries to the model to infer training data characteristics.

**Mitigations:**
- Limit output token count per request
- Add differential privacy noise to gradients
- Monitor query patterns for extraction attempts
- Rate-limit repeated queries on similar topics

### Membership Inference

Determine whether a specific data point was used in training.

**Attack:** Query the model on a data point and measure confidence. Higher confidence on training data points is a signal of membership.

**Mitigations:**
- Differential privacy during training
- Regularization to reduce overfitting
- Limit output logprobs (don't expose token probabilities in production)

### Model Extraction

Steal model functionality by querying the API and training a substitute model.

**Attack:** Send thousands to millions of queries, record (input, output) pairs, train a student model that mimics the target.

**Cost:** For a commercial API at $0.01/query, a 1M-query extraction costs ~$10K — affordable for well-funded attackers.

**Mitigations:**
- Rate limiting per user/IP
- Output perturbation (add small noise to logprobs)
- Watermarking model outputs (subtle statistical patterns)
- Legal terms of service prohibiting extraction

### Adversarial Examples

Craft inputs that cause the model to make errors.

**White-box:** Attacker has full model access (weights, architecture). Use gradient-based methods to craft minimal perturbations.

**Black-box:** Attacker only has API access. Use transfer attacks or query-based optimization.

**Mitigations:**
- Adversarial training (include adversarial examples in training data)
- Input perturbation detection (check if input is near a decision boundary)
- Ensemble methods (multiple models vote on output)
- Certified defenses (provable robustness bounds for small perturbations)

## Model Access Control

| Access Level | Permissions | Use Case |
|-------------|-------------|----------|
| Public | Inference only | End users |
| Internal | Inference + fine-tuning | ML team |
| Admin | Full access (weights, training) | Infrastructure team |
| Auditor | Read-only (logs, metrics) | Compliance |

## Model Versioning and Integrity

| Practice | Purpose |
|----------|---------|
| Hash model weights | Verify integrity at load time |
| Sign model artifacts | Prevent tampering with stored models |
| Registry with audit trail | Track who accessed/modified each version |
| Isolated training environment | Training infrastructure separate from production |
| Reproducible builds | Same data + code = same model hash |

## Secure Deployment

### Network Isolation
- Place model servers in a private subnet
- API gateway as the only public entry point
- No direct outbound internet access from model servers
- VPN/proxy for outbound tool calls (web search, APIs)

### Secrets Management
- Never hardcode API keys in model prompts
- Use a secrets vault (HashiCorp Vault, AWS Secrets Manager)
- Rotate keys regularly
- Scope keys to minimum permissions

### Monitoring for Attacks

| Signal | What It Indicates | Action |
|--------|-------------------|--------|
| High error rate from a single user | Possible extraction attempt | Rate limit, investigate |
| Unusual query patterns | Reverse engineering | Block, report |
| Repeated same-prefix queries | Extraction or jailbreak iteration | Rate limit per prefix |
| Sudden traffic spike | Possible DoS | Auto-scale + rate limit |
| High similarity to known attacks | Automated red teaming tool | Block, add to detection set |

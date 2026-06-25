# Statistics for AI

Core statistical concepts used throughout machine learning and AI.

## Key Topics

### Descriptive Statistics
Measures that summarize and describe the main features of a dataset.
- **Central tendency:** mean (sensitive to outliers), median (robust), mode
- **Dispersion:** variance, standard deviation, interquartile range (IQR), range
- **Shape:** skewness (asymmetry), kurtosis (tail heaviness)
- **Five-number summary:** min, Q1, median, Q3, max
- **Outlier detection:** z-score (standard deviations from mean), IQR method (points beyond 1.5× IQR)

**Relevance to AI:** Data exploration, feature normalization (z-score, min-max scaling), and outlier removal before model training.

### Probability Theory
The mathematical framework for quantifying uncertainty.
- **Axioms:** non-negativity, normalization, additivity
- **Conditional probability:** P(A|B) = P(A∩B) / P(B)
- **Bayes' theorem:** P(A|B) = P(B|A)·P(A) / P(B)
- **Law of total probability:** P(A) = Σᵢ P(A|Bᵢ)·P(Bᵢ)
- **Independence:** P(A∩B) = P(A)·P(B)
- **Random variables:** discrete, continuous; PDF (probability density function), PMF (probability mass function), CDF (cumulative distribution function)

**Relevance to AI:** Foundation of probabilistic models (Naive Bayes, Bayesian networks), uncertainty estimation, and decision theory.

### Probability Distributions
Functions that describe the likelihood of different outcomes.

| Distribution | Parameters | Use Case in AI |
|---|---|---|
| **Normal (Gaussian)** | μ, σ² | Feature distributions, weight initialization, noise modeling |
| **Bernoulli** | p | Binary classification output, dropout masks |
| **Binomial** | n, p | Count of successes in n trials |
| **Poisson** | λ | Count data, event rate modeling |
| **Exponential** | λ | Waiting times, inter-arrival durations |
| **Beta** | α, β | Prior distribution for probabilities, Bayesian A/B testing |
| **Gamma** | α, β | Priors for precision, waiting times for α events |
| **Dirichlet** | α₁...αₖ | Topic modeling (LDA), distribution over categorical probabilities |
| **Multinomial** | n, p₁...pₖ | Multi-class classification, text generation |

**Relevance to AI:** Choice of distribution determines the likelihood function, which directly shapes the loss (e.g., Gaussian → MSE, Bernoulli → cross-entropy).

### Hypothesis Testing
A framework for making statistical decisions using sample data.
- **Null hypothesis (H₀):** default assumption (no effect)
- **Alternative hypothesis (H₁):** what we want to evidence
- **p-value:** probability of observing data as extreme as the sample, assuming H₀ is true
- **Type I error (α):** rejecting a true null — false positive
- **Type II error (β):** failing to reject a false null — false negative
- **Statistical power:** 1 − β, probability of detecting a true effect
- **Common tests:** t-test (compare means), chi-square (categorical association), ANOVA (compare 3+ groups)

**Relevance to AI:** A/B testing for model and feature evaluation, significance testing for feature selection, and comparing model performance.

### Bayesian Inference
Updating beliefs about parameters based on observed data.
- **Bayes rule:** posterior ∝ likelihood × prior
- **Priors:** informative (domain knowledge), uninformative (flat), conjugate (prior and posterior share same family)
- **Posterior:** updated distribution after observing data
- **Credible interval:** Bayesian analog of confidence interval (direct probability interpretation)
- **MCMC (Markov Chain Monte Carlo):** sampling-based approximation for complex posteriors
- **Bayesian vs Frequentist:** Bayesian treats parameters as random (with distributions); frequentist treats them as fixed (unknown constants)

**Relevance to AI:** Bayesian neural networks for uncertainty quantification, online learning (sequential posterior updates), and hyperparameter priors.

### Maximum Likelihood Estimation (MLE) and Maximum a Posteriori (MAP)
Parameter estimation methods that form the backbone of model training.
- **MLE:** find θ that maximizes P(data|θ) — equivalent to minimizing negative log-likelihood
- **MAP:** find θ that maximizes P(θ|data) ∝ P(data|θ)·P(θ) — MLE with a prior
- **Loss functions as negative log-likelihoods:**
  - MSE loss ↔ Gaussian MLE (regression)
  - Cross-entropy loss ↔ Bernoulli/Categorical MLE (classification)
  - Huber loss ↔ mixture of Gaussian and Laplace
- **Regularization as MAP:** L2 (Gaussian prior on weights), L1 (Laplace prior)

**Relevance to AI:** Nearly all supervised learning objectives can be interpreted as MLE or MAP, making this the direct statistical foundation of training.

### Correlation and Covariance
Measures of how variables change together.
- **Covariance:** unnormalized directional relationship — sign indicates direction, magnitude depends on scale
- **Pearson correlation (r):** normalized covariance (−1 to 1), measures linear relationship
- **Spearman rank correlation:** monotonic relationship (rank-based), robust to outliers
- **Covariance matrix:** Σ where Σᵢⱼ = cov(Xᵢ, Xⱼ); diagonal entries are variances
- **Multicollinearity:** high correlation among predictors — destabilizes coefficient estimates
- **Partial correlation:** correlation between two variables after controlling for others

**Relevance to AI:** Feature selection (remove highly correlated features), PCA foundation (eigendecomposition of covariance matrix), and understanding feature interactions.

### Dimensionality Reduction
Techniques to reduce the number of random variables while preserving structure.
- **PCA (Principal Component Analysis):** projects data onto eigenvectors of covariance matrix, sorted by explained variance — linear, unsupervised
- **SVD (Singular Value Decomposition):** matrix factorization A = UΣVᵀ — underlies PCA, used in recommendation systems (collaborative filtering)
- **t-SNE:** non-linear, preserves local structure — excellent for 2D/3D visualization
- **UMAP:** non-linear, faster than t-SNE, preserves both local and global structure

**Relevance to AI:** Feature reduction (mitigate curse of dimensionality), noise reduction, visualization of high-dimensional embeddings, and latent factor models.

### Information Theory
Quantifying information content and similarity between distributions.
- **Entropy H(X):** average information (uncertainty) in a random variable — H(X) = −Σ p(x)·log p(x)
- **Cross-entropy H(p,q):** number of bits needed to encode p using q's distribution — H(p,q) = −Σ p(x)·log q(x)
- **KL divergence Dₖₗ(p‖q):** measure of how one distribution diverges from another — Dₖₗ = Σ p(x)·log(p(x)/q(x))
- **Mutual information I(X;Y):** reduction in uncertainty of X given Y — I = H(X) − H(X|Y)
- **Jensen-Shannon divergence:** symmetric, smoothed version of KL divergence

**Relevance to AI:** Cross-entropy is the default loss for classification; KL divergence measures model mismatch (variational inference); mutual information guides feature selection and representation learning.

## Applications in AI
- Loss functions derive from MLE principles (MSE from Gaussian, cross-entropy from Bernoulli/Categorical)
- Bayesian methods for uncertainty quantification in neural networks
- Hypothesis testing for A/B testing in AI system evaluation
- Information theory for feature selection, model evaluation, and representation learning
- Correlation analysis for feature engineering and multicollinearity detection
- Dimensionality reduction for visualization and preprocessing high-dimensional embeddings

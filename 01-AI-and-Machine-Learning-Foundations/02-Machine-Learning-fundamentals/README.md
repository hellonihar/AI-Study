# Machine Learning Fundamentals

Foundational machine learning paradigms, algorithms, and best practices.

## Learning Paradigms

### Supervised Learning

**Short description:** Learning a mapping from inputs to outputs using labeled training data (input-output pairs). The model generalizes from known examples to predict labels for unseen data.

**Example usages:**
- Predicting house prices from features like size, location, and bedrooms (regression)
- Classifying emails as spam or not spam (classification)
- Diagnosing diseases from medical imaging data

**Strong points:**
- High predictive accuracy when sufficient labeled data is available
- Clear evaluation metrics (accuracy, RMSE, F1-score)
- Well-understood theoretical foundations with extensive tooling

**Limitations:**
- Requires large amounts of labeled data, which is expensive to obtain
- Poor generalization to data outside the training distribution (distribution shift)
- Vulnerable to label noise and biased annotations

### Unsupervised Learning

**Short description:** Finding hidden patterns, structure, or representations in unlabeled data without predefined target variables.

**Example usages:**
- Segmenting customers into groups based on purchasing behavior (clustering)
- Reducing high-dimensional data to 2D for visualization (dimensionality reduction)
- Detecting unusual transactions in financial systems (anomaly detection)

**Strong points:**
- Works with unlabeled data, which is abundant and cheap
- Discovers unknown patterns and structure humans may miss
- Useful as a preprocessing step to improve supervised model performance

**Limitations:**
- Results are subjective and hard to evaluate without ground truth
- Sensitive to feature scaling and initialization
- May find spurious patterns that do not generalize

### Reinforcement Learning

**Short description:** An agent learns to make sequential decisions by interacting with an environment, receiving rewards or penalties, and maximizing cumulative reward over time.

**Example usages:**
- Training game-playing agents (AlphaGo, Atari, StarCraft)
- Robotics control (grasping, walking, navigation)
- Optimizing recommendation systems through user interaction feedback

**Strong points:**
- Excels in sequential decision-making with delayed rewards
- Can discover novel strategies beyond human intuition
- Adapts to dynamic environments through continuous interaction

**Limitations:**
- Extremely sample-inefficient — requires millions of interactions
- Reward function design is difficult and can lead to unintended behavior
- Poor transfer learning — a policy trained for one environment rarely works for another

## Core Concepts

### Bias-Variance Tradeoff

**Short description:** The fundamental tradeoff between a model's error due to overly simplistic assumptions (bias) and its sensitivity to fluctuations in the training data (variance). Total error = bias² + variance + irreducible error.

**Example usages:**
- Diagnosing underfitting (high bias) vs. overfitting (high variance) in model performance curves
- Selecting model complexity via validation curves (e.g., tree depth, polynomial degree)
- Tuning regularization strength to find the optimal balance

**Strong points:**
- Provides a principled framework for model selection and debugging
- Explains why simple models (linear regression) have high bias but low variance, and complex models (deep networks) have low bias but high variance
- Guides hyperparameter tuning toward the sweet spot

**Limitations:**
- Hard to measure bias and variance directly in practice
- Assumes a fixed training set size — the tradeoff shifts with more data
- Modern deep learning challenges the classic view (double descent phenomenon)

### Cross-Validation and Model Evaluation Metrics

**Short description:** Techniques for estimating model performance on unseen data by partitioning the dataset into training and validation subsets multiple times.

**Example usages:**
- k-fold cross-validation to select hyperparameters (e.g., optimal k for kNN)
- Stratified cross-validation maintaining class proportions in imbalanced datasets
- Using precision, recall, and ROC-AUC for binary classification evaluation

**Strong points:**
- Reduces variance in performance estimates compared to single train-test split
- Makes efficient use of limited data (every sample is used for both training and validation)
- Enables fair model comparison and hyperparameter selection

**Limitations:**
- Computationally expensive for large datasets and complex models (training k times)
- Temporal data (time series) requires specialized cross-validation (forward chaining)
- Results can still be misleading if the data has hidden dependencies (group leakage)

### Regularization (L1, L2, Elastic Net)

**Short description:** Techniques that prevent overfitting by adding a penalty term to the loss function to constrain model weights. L1 (Lasso) drives weights to zero; L2 (Ridge) shrinks weights uniformly; Elastic Net combines both.

**Example usages:**
- L1 regularization for feature selection in high-dimensional genomic data
- L2 regularization to stabilize linear regression with multicollinear features
- Elastic Net combining both strengths when many features are irrelevant but correlated

**Strong points:**
- Effectively reduces overfitting and improves generalization on held-out data
- L1 produces sparse models — automatic feature selection and interpretability
- L2 handles correlated features better and has a closed-form solution in linear regression

**Limitations:**
- Regularization strength (λ) requires tuning via cross-validation
- L1 can be unstable — selecting different features with slight data changes
- High regularization can overly bias the model, causing underfitting

## Key Algorithms

### Linear Regression

**Short description:** Models the relationship between a continuous target variable and one or more features by fitting a linear equation y = w·x + b. Coefficients are typically estimated via Ordinary Least Squares.

**Example usages:**
- Forecasting sales revenue based on advertising spend across channels
- Estimating the effect of experience and education on salary
- Predicting energy consumption from temperature and time-of-day features

**Strong points:**
- Highly interpretable — coefficients directly measure feature impact
- Fast to train and predict, scales well to large datasets
- Closed-form solution (no iterative optimization needed) for standard OLS

**Limitations:**
- Assumes a linear relationship — poor fit for nonlinear patterns
- Sensitive to outliers (leverage points can distort the fit significantly)
- Requires feature independence (multicollinearity inflates variance of coefficients)

### Logistic Regression

**Short description:** A classification algorithm that models the probability of a binary outcome using the logistic (sigmoid) function. Despite the name, it is a classification method, not regression.

**Example usages:**
- Predicting customer churn (will cancel / will stay)
- Classifying loan applications as default or non-default
- Diagnosing presence of a disease from patient measurements

**Strong points:**
- Outputs well-calibrated probabilities, not just hard labels
- Fast, lightweight, and performs well on linearly separable data
- Coefficients provide log-odds ratios — interpretable feature importance

**Limitations:**
- Assumes linear decision boundary — fails for complex nonlinear separations
- Requires careful feature engineering to capture interactions
- Prone to overfitting with high-dimensional sparse data

### Decision Trees

**Short description:** A tree-structured model where internal nodes test a feature, branches represent outcomes, and leaves represent predictions. Built by recursively splitting data to maximize information gain or reduce impurity.

**Example usages:**
- Credit risk assessment with interpretable yes/no rules
- Medical diagnosis using patient symptom features
- Customer segmentation in targeted marketing campaigns

**Strong points:**
- Highly interpretable — the tree can be visualized and explained as rules
- Handles both numerical and categorical data without preprocessing
- Captures nonlinear relationships and feature interactions naturally

**Limitations:**
- Very prone to overfitting — a deep tree memorizes noise
- Sensitive to small data changes — a different split at the root can change the entire tree
- Greedy splitting algorithm (locally optimal split) may miss the global optimum

### Random Forests

**Short description:** An ensemble of many decision trees trained on bootstrapped samples with random feature subsets. Predictions are averaged (regression) or voted (classification) across all trees.

**Example usages:**
- Predicting customer lifetime value from dozens of behavioral features
- Classifying land cover from satellite imagery spectral bands
- Identifying fraudulent insurance claims from structured policy data

**Strong points:**
- Robust to overfitting — averaging across trees reduces variance dramatically
- Handles high-dimensional data and thousands of features well
- Provides built-in feature importance scores (mean decrease in impurity)

**Limitations:**
- Large ensemble can be slow for real-time prediction
- Less interpretable than a single decision tree
- May overfit on noisy classification tasks with very high feature dimensionality

### Gradient Boosting (XGBoost, LightGBM, CatBoost)

**Short description:** An ensemble technique that builds trees sequentially, where each new tree corrects the errors (residuals) of the previous ones. Modern implementations add regularization, efficiency, and GPU support.

**Example usages:**
- Winning tabular data competitions on Kaggle (regression, classification, ranking)
- Click-through rate prediction in online advertising systems
- Product demand forecasting in retail supply chains

**Strong points:**
- State-of-the-art performance on most structured/tabular data problems
- XGBoost handles missing values natively and supports custom loss functions
- LightGBM (leaf-wise growth) and CatBoost (ordered boosting) offer faster training and better categorical feature handling

**Limitations:**
- Sensitive to hyperparameters — requires careful tuning (learning rate, tree depth, subsample)
- Sequential training cannot be parallelized across trees (though within-tree parallelization helps)
- Risk of overfitting if too many trees are used without early stopping or strong regularization

### Support Vector Machines (SVM)

**Short description:** Finds the hyperplane that maximizes the margin between classes. Uses the kernel trick to project data into higher-dimensional space for nonlinear separation.

**Example usages:**
- Text classification with high-dimensional TF-IDF features
- Image classification with small-to-medium datasets and RBF kernel
- Handwriting recognition (e.g., MNIST digits)

**Strong points:**
- Effective in high-dimensional spaces (more features than samples)
- Kernel trick allows nonlinear decision boundaries without explicit feature expansion
- Maximizing margin leads to good generalization with limited data

**Limitations:**
- Poor scalability — training time scales quadratically to cubically with sample size
- No native probability output (Platt scaling needed for calibrated probabilities)
- Kernel selection and hyperparameter tuning (C, γ) are non-trivial

### k-Nearest Neighbors (kNN)

**Short description:** A lazy learner that stores all training data and predicts by finding the k closest training points to a new query and returning their majority class (classification) or mean (regression).

**Example usages:**
- Recommending products by finding similar users' preferences
- Handwriting digit recognition with pixel-distance comparison
- Detecting anomalies as points far from their k nearest neighbors

**Strong points:**
- Simple and intuitive — no training phase, just store the data
- Naturally handles multi-class classification
- Non-parametric — makes no assumptions about the data distribution

**Limitations:**
- Prediction is slow for large datasets (must compute distance to all points)
- Strongly affected by irrelevant features and feature scale — requires careful normalization
- Curse of dimensionality: distance metrics become meaningless in high dimensions

### k-Means Clustering

**Short description:** Partitions n observations into k clusters by minimizing the within-cluster sum of squares. Each point belongs to the cluster with the nearest centroid.

**Example usages:**
- Customer segmentation for targeted marketing campaigns
- Image compression by reducing colors to k representative palette colors
- Document clustering for topic discovery in large text corpora

**Strong points:**
- Simple and computationally efficient for large datasets (O(n·k·d))
- Scales linearly with the number of samples
- Easy to implement and interpret — clusters are defined by centroids

**Limitations:**
- Requires k to be specified in advance — elbow method or silhouette score needed for selection
- Assumes spherical clusters of similar size — fails for elongated or irregular shapes
- Sensitive to initialization — multiple runs with different seeds are recommended

### Principal Component Analysis (PCA)

**Short description:** A linear dimensionality reduction technique that projects data onto orthogonal components that capture the maximum variance. Components are eigenvectors of the covariance matrix ranked by explained variance.

**Example usages:**
- Reducing 1000-dimensional gene expression data to 50 components for downstream modeling
- Visualizing high-dimensional embeddings in 2D or 3D scatter plots
- Noise filtering by keeping top components and reconstructing the data

**Strong points:**
- Fast, deterministic (no random seed), and has a closed-form solution
- Removes multicollinearity — components are orthogonal by construction
- The explained variance ratio provides a clear criterion for component selection

**Limitations:**
- Linear projection — cannot capture nonlinear manifold structure
- Principal components are hard to interpret in terms of original features
- Sensitive to feature scales — standardization must be applied first

### Feature Engineering and Selection

**Short description:** The process of creating informative features from raw data (engineering) and choosing the most relevant subset of features for modeling (selection) to improve performance and reduce overfitting.

**Example usages:**
- Extracting day-of-week, hour, and holiday features from timestamp data
- Using mutual information or chi-square tests to select the top 20 features from 500 candidates
- Creating interaction features (product of two features) to capture synergy effects

**Strong points:**
- Often provides bigger performance gains than algorithm selection or hyperparameter tuning
- Reduces model complexity, training time, and risk of overfitting
- Domain-driven feature engineering encodes expert knowledge the model cannot learn alone

**Limitations:**
- Labor-intensive and requires deep domain expertise
- Risk of data leakage when features are created using information from the future or test set
- Feature selection methods can be unstable — small data changes may select different subsets

### Imbalanced Learning Techniques

**Short description:** Strategies for handling datasets where classes are heavily skewed (e.g., 99% negative, 1% positive). Methods include resampling, cost-sensitive learning, and specialized algorithms.

**Example usages:**
- Fraud detection with legitimate transactions vastly outnumbering fraudulent ones
- Medical diagnosis of rare diseases (e.g., 0.1% prevalence)
- Manufacturing defect detection where most products pass inspection

**Strong points:**
- Prevents models from achieving high accuracy by simply predicting the majority class
- SMOTE (Synthetic Minority Oversampling) creates realistic synthetic samples, not just duplicates
- Cost-sensitive approaches directly penalize minority-class misclassification in the loss function

**Limitations:**
- Oversampling can cause overfitting on replicated or synthetic minority points
- Undersampling discards potentially useful majority-class data
- Evaluation requires specialized metrics (precision-recall curve, F1-score, Matthews correlation) — accuracy is misleading

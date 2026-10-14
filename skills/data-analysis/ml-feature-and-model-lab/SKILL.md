---
name: ml-feature-and-model-lab
description: >-
  Use this skill when designing leakage-safe machine learning feature engineering pipelines,
  conducting statistical hypothesis tests (A/B testing, t-tests, Mann-Whitney U, ANOVA),
  and explaining model predictions or auditing algorithmic fairness using SHAP (Shapley values).
---

# Machine Learning Feature & Model Laboratory

## Overview

Unified laboratory for leakage-safe machine learning feature engineering, statistical hypothesis testing (A/B testing, Mann-Whitney U, ANOVA), model evaluation, and algorithmic fairness auditing with SHAP.

## When to Use

- When engineering tabular feature sets (cyclical time, target encoding, interaction terms, scaling).
- When designing, analyzing, or interpreting A/B test experiments or statistical significance tests.
- When explaining black-box model predictions using TreeSHAP, LinearSHAP, or KernelSHAP.
- When auditing machine learning models for demographic bias, disparate impact, or feature drift.
- Trigger phrases: `"feature engineering pipeline"`, `"A/B test significance"`, `"statistical hypothesis test"`, `"explain model with SHAP"`, `"feature importance"`, `"audit model fairness"`.

---
- **When NOT to use**: Designing non-ML relational database indexes (use `backend-architecture`).

## Core Process & Machine Learning Experimentation Lab

## The 3 Pillars of ML Rigor

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ML Feature & Model Lab Framework                     │
├────────────────────────────────┬───────────────────────────────────────┤
│ Pillar 1: Feature Engineering  │ Pillar 2: Statistical Testing         │
│ (Leakage-Safe Encodings, Scalers)│ (Normality, t-test, Mann-Whitney, FDR)│
├────────────────────────────────┴───────────────────────────────────────┤
│ Pillar 3: Model Explainability & Fairness (SHAP Beeswarm & Parity)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Pillar 1: Leakage-Safe Feature Engineering

The number one defect in production ML pipelines is **train-test data leakage**. Enforce these structural rules:
1. **The Golden Rule**: All transformers (imputers, scalers, target encoders) must be fit *strictly* on the training split:
   ```python
   # CORRECT: Transformer fit only on X_train
   scaler = StandardScaler()
   X_train_scaled = scaler.fit_transform(X_train)
   X_test_scaled = scaler.transform(X_test)
   ```
2. **Cyclical Temporal Encodings**:
   Never feed raw hour (0–23) or day-of-week (0–6) as linear numbers ($23$ and $0$ are adjacent). Use trigonometric projections:
   $$\text{sin\_feat} = \sin\left(\frac{2\pi \cdot x}{\text{period}}\right), \quad \text{cos\_feat} = \cos\left(\frac{2\pi \cdot x}{\text{period}}\right)$$
3. **Target Encoding with Out-of-Fold (OOF) Regularization**:
   When encoding high-cardinality categoricals with target means, use K-Fold cross-fitting with smoothing to prevent memorizing the target.

---

### Pillar 2: Statistical Hypothesis Testing (A/B Testing)

Avoid p-hacking and false discoveries by following a structured testing tree:

```mermaid
graph TD
    A[Data Distribution Check] -->|Shapiro-Wilk p > 0.05| B[Parametric Path]
    A -->|Shapiro-Wilk p <= 0.05| C[Non-Parametric Path]
    B -->|2 Independent Groups| D[Two-Sample t-test / Welch t-test]
    B -->|> 2 Groups| E[One-Way ANOVA + Tukey HSD]
    C -->|2 Independent Groups| F[Mann-Whitney U Test]
    C -->|> 2 Groups| G[Kruskal-Wallis Test]
    H[Categorical Rates / Conversion] --> I[Chi-Square Test / Fisher Exact]
```

1. **Power Analysis**: Compute minimum detectable effect (MDE) and sample size *before* the experiment runs ($\alpha = 0.05$, $\beta = 0.20$ for 80% power).
2. **Multiple Comparison Correction**: When testing multiple metrics simultaneously, apply the **Benjamini-Hochberg (FDR)** or Bonferroni correction to prevent false discoveries.
3. **Effect Size Reporting**: Always report Cohen's $d$ or Rank-Biserial correlation alongside the p-value. A p-value tells you if an effect exists; effect size tells you if anyone should care.

---

### Pillar 3: SHAP Explainability & Algorithmic Fairness

Explain tree-based models (XGBoost, LightGBM, CatBoost, Scikit-Learn) with game-theoretic Shapley values:

```python
import shap

# 1. Initialize TreeExplainer
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)

# 2. Global Importance: Beeswarm plot reveals feature magnitude & directionality
shap.plots.beeswarm(shap_values, max_display=15)

# 3. Local Decision Breakdown: Waterfall plot explains a single customer outcome
shap.plots.waterfall(shap_values[0])
```

#### Demographic Fairness Audit:
Measure model predictions across protected demographic subgroups (e.g., age, gender, region):
- **Disparate Impact Ratio**: Approval rate of unprivileged group / Approval rate of privileged group. Must satisfy the 80% four-fifths rule:
  $$\text{DIR} = \frac{P(\hat{Y}=1 \mid D=\text{unprivileged})}{P(\hat{Y}=1 \mid D=\text{privileged})} \ge 0.80$$
- **Equalized Odds**: True Positive Rate (TPR) and False Positive Rate (FPR) parity across subgroups within a 5% margin.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"Accuracy is the only metric needed to evaluate our classifier."* | On imbalanced datasets, a model predicting the majority class can achieve 99% accuracy while having 0% recall on the minority class. |
| *"A/B test results are statistically significant after 2 days of testing."* | Stopping experiments early without reaching power-analyzed sample sizes inflates false positive rates via p-hacking. |
| *"Black-box models don't need explainability if benchmark test scores are high."* | Unexplained models deploy hidden demographic biases, confounders, and shortcut learning that cause catastrophic real-world failures. |
| *"Cross-validation can be simple random K-fold on time-series data."* | Random K-fold on time-series data leaks future information into past predictions; use TimeSeriesSplit or rolling-window evaluation. |

## Red Flags

- Evaluating model performance without stratified sampling on class-imbalanced datasets.
- Failing to log model hyperparameters, random seeds, and evaluation metrics in reproducible experiment trackers.
- Deploying models without checking demographic parity or disparate impact across sensitive subgroups.
- Comparing model versions without paired statistical significance testing (e.g. McNemar's test).

## Verification

After completing the workflow, confirm:
- [ ] Model evaluation logs Precision, Recall, F1, ROC-AUC, and PR-AUC curves.
- [ ] Statistical hypothesis tests verify that performance gains over baseline are statistically significant (p < 0.05).
- [ ] SHAP summary plots identify top predictive features and explain individual prediction edge cases.
- [ ] Fairness audit verifies disparate impact ratios remain within compliant thresholds (0.80 - 1.25).

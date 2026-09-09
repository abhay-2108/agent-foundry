---
name: model-explainability-shap
description: >-
  Use this skill when explaining machine learning models, interpreting predictions,
  or auditing algorithmic fairness using SHAP (SHapley Additive exPlanations).
  Generates waterfall plots, beeswarm summary charts, and feature importance rankings.
---

# Model Explainability & Interpretability with SHAP

Enables agents to interpret, explain, and audit black-box machine learning models (XGBoost, LightGBM, Random Forest, PyTorch) using cooperative game-theoretic **SHAP (SHapley Additive exPlanations)** values.

---

## When to Use This Skill

- When stakeholders ask: *"Why did the model reject this customer's loan?"* or *"What drove this prediction?"*.
- When evaluating model fairness, algorithmic bias, or disparate impact across demographic segments.
- When selecting top features, diagnosing model bugs, or detecting data leakage.
- When generating visual explanation plots (Summary/Beeswarm, Waterfall, Force, and Dependence plots).
- Trigger phrases: `"explain model"`, `"SHAP values"`, `"feature importance"`, `"model interpretability"`, `"audit model bias"`.

---

## Global vs. Local Explainability

| Scope | Question Answered | Primary SHAP Visualization |
| :--- | :--- | :--- |
| **Global Explainability** | What overall features matter most to the model across all predictions? | **Beeswarm Plot** / Bar Summary Plot |
| **Local Explainability** | Why did the model make *this specific prediction* for instance $i$? | **Waterfall Plot** / Force Plot |
| **Feature Interaction** | How does feature $A$ interact with feature $B$ across the response surface? | **Dependence Plot** with automatic interaction |
| **Fairness & Parity** | Does the model rely disproportionately on sensitive features across cohorts? | **Subgroup Mean Absolute SHAP Comparison** |

---

## Step-by-Step Python Implementation Pattern

```python
"""shap_explainer_suite.py
Production-grade SHAP explainability and fairness auditing pipeline.
"""
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt

def generate_shap_explanations(
    model,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    protected_attribute: Optional[str] = None,
    instance_idx: int = 0,
    background_samples: int = 100
) -> Dict[str, pd.DataFrame]:
    """Computes TreeExplainer or background-summarized SHAP values with fairness auditing."""
    
    # 1. Background Dataset Summarization (prevents combinatorial explosion on large data)
    if len(X_train) > background_samples:
        background_summary = shap.sample(X_train, background_samples, random_state=42)
    else:
        background_summary = X_train

    # 2. Select Optimal Explainer (TreeExplainer for tree models, Explainer for general)
    try:
        explainer = shap.TreeExplainer(model, data=background_summary)
    except Exception:
        explainer = shap.Explainer(model, background_summary)

    shap_values = explainer(X_test)

    # 3. Global Feature Importance (Beeswarm Summary Plot)
    plt.figure(figsize=(10, 6))
    shap.plots.beeswarm(shap_values, max_display=15, show=False)
    plt.title("Global Feature Importance (SHAP Beeswarm)")
    plt.tight_layout()
    plt.savefig("global_shap_summary.png", dpi=300)
    plt.close()

    # 4. Local Explanation for Single Instance (Waterfall Plot)
    plt.figure(figsize=(10, 6))
    shap.plots.waterfall(shap_values[instance_idx], max_display=10, show=False)
    plt.title(f"Local Instance Explanation (Row {instance_idx})")
    plt.tight_layout()
    plt.savefig(f"local_waterfall_instance_{instance_idx}.png", dpi=300)
    plt.close()

    # 5. Extract Ranked Feature Contributions for Instance
    instance_shap = pd.DataFrame({
        "feature": X_test.columns,
        "feature_value": X_test.iloc[instance_idx].values,
        "shap_contribution": shap_values[instance_idx].values
    }).sort_values(by="shap_contribution", key=abs, ascending=False)

    # 6. Algorithmic Fairness & Demographic Subgroup Audit
    fairness_report = pd.DataFrame()
    if protected_attribute and protected_attribute in X_test.columns:
        subgroups = X_test[protected_attribute].unique()
        group_shap_means = {}
        for group in subgroups:
            mask = (X_test[protected_attribute] == group).values
            group_shap_means[f"mean_abs_shap_{group}"] = np.abs(shap_values[mask].values).mean(axis=0)

        fairness_report = pd.DataFrame(group_shap_means, index=X_test.columns)
        fairness_report["disparity_ratio"] = (
            fairness_report.iloc[:, 0] / (fairness_report.iloc[:, 1] + 1e-9)
        ).round(3)
        fairness_report = fairness_report.sort_values(by="disparity_ratio", ascending=False)

    return {"instance_explanation": instance_shap, "fairness_audit": fairness_report}
```

---

## Anti-Patterns & Traps to Avoid

1. **Unbounded Background Sets in KernelExplainer**: Never pass raw un-sampled datasets (thousands of rows) to `shap.KernelExplainer`. Computing exact Shapley values is NP-hard ($O(2^{|F|})$); always summarize background data using `shap.kmeans()` or `shap.sample(X, 100)`.
2. **Confusing SHAP Attribution with Causal Impact**: SHAP measures feature importance according to *what the model learned*, not real-world causality. An unconstrained feature correlated with target leakage will display high SHAP values despite having zero real-world causal validity.
3. **Evaluating Categorical Features Post-OneHot Encoding Blindly**: Analyzing 50 one-hot columns individually dilutes feature importance across dummy variables. Use `shap_values` column aggregation or explain trees trained directly on native categoricals (e.g., CatBoost or LightGBM integer types).
4. **Ignoring Additivity Validation**: Never trust raw SHAP output without verifying the additivity property: $\sum \text{SHAP}_i + E[f(X)] = f(x)$. If the sum deviates from the prediction, the explainer was improperly configured or input data transformations were inconsistent.

---

## Quality Checklist

- [ ] Explainer selection uses `TreeExplainer` for trees and `shap.sample()` background datasets for model-agnostic explainers.
- [ ] Additivity invariant holds: Base value $E[f(X)]$ plus sum of SHAP values equals raw model prediction $f(x)$.
- [ ] Both global distribution (Beeswarm) and local decision (Waterfall) plots are generated.
- [ ] High-importance features are checked against training data for leakage indicators.
- [ ] Protected demographic attributes (gender, race, age) are audited for disparate impact ratios.
- [ ] Interaction effects are checked using `shap.dependence_plot` when non-linear feature coupling is suspected.

---
name: model-explainability-shap
description: >-
  Use this skill when explaining machine learning models, interpreting predictions,
  or auditing algorithmic fairness using SHAP (SHapley Additive exPlanations).
  Implements TreeSHAP for tree ensembles, LinearSHAP for regression, and KernelSHAP
  as a model-agnostic fallback. Generates waterfall plots, beeswarm summary charts,
  dependence plots, and subgroup fairness audits. Includes a zero-dependency
  SHAP-value approximation for testing and a structured Model Card output template.
---

# Model Explainability & Interpretability with SHAP

Acts as a Senior ML Interpretability Engineer. Explains black-box model predictions using cooperative game theory — SHAP (SHapley Additive exPlanations) values assign each feature a mathematically fair credit for each prediction. Covers global explanations (what the model uses overall), local explanations (why this specific decision), and fairness audits (whether sensitive attributes drive predictions disproportionately).

## When to Use This Skill
- When stakeholders ask: *"Why did the model reject this loan application?"* or *"What drove this prediction?"*
- When evaluating model fairness, algorithmic bias, or disparate impact across demographic segments.
- When selecting the most predictive features or diagnosing model bugs by inspecting SHAP patterns.
- When detecting data leakage — unexpectedly dominant SHAP contributions from ID or timestamp columns.
- When generating visual explanation plots for executive or regulatory reporting.
- When creating a model card for a deployed ML model.
- Trigger phrases: `"explain model"`, `"SHAP values"`, `"feature importance"`, `"model interpretability"`, `"audit model bias"`, `"why did the model predict"`, `"model card"`, `"fairness audit"`.

---

## Global vs. Local Explainability

| Scope | Question Answered | Primary SHAP Tool |
|:--|:--|:--|
| **Global** | What features does the model rely on most across all predictions? | Beeswarm (summary) plot, bar chart of mean |SHAP| |
| **Local** | Why did the model make THIS specific prediction for instance _i_? | Waterfall plot, Force plot |
| **Interaction** | How does feature A modulate feature B across the response surface? | Dependence plot with auto interaction coloring |
| **Fairness** | Does the model rely disproportionately on sensitive attributes? | Subgroup mean |SHAP| comparison |

---

## The 4-Phase SHAP Workflow

### Phase 1: Choose the Right SHAP Explainer

```python
import shap

def get_shap_explainer(model, X_train, model_type: str = "auto"):
    """
    Select the most computationally efficient SHAP explainer for the model type.
    
    TreeExplainer  → XGBoost, LightGBM, CatBoost, RandomForest, ExtraTrees
                     Fast O(TLD) algorithm — exact SHAP values, no approximation.
    LinearExplainer→ LogisticRegression, Ridge, LinearSVC
                     O(M) — uses feature covariance to account for correlations.
    KernelExplainer→ Any sklearn-compatible model (slow — use for validation only)
                     O(2^M) — Shapley sampling approximation.
    """
    if model_type == "auto":
        model_type_name = type(model).__name__.lower()
        if any(t in model_type_name for t in ("xgb", "lgbm", "catboost", "forest", "tree", "gbm")):
            model_type = "tree"
        elif any(t in model_type_name for t in ("linear", "logistic", "ridge", "lasso")):
            model_type = "linear"
        else:
            model_type = "kernel"
    
    if model_type == "tree":
        return shap.TreeExplainer(model)
    elif model_type == "linear":
        return shap.LinearExplainer(model, X_train)
    else:
        # KernelSHAP: summarize background with k-means to cap computation
        background = shap.kmeans(X_train, k=50)
        return shap.KernelExplainer(model.predict_proba, background)
```

---

### Phase 2: Compute SHAP Values

```python
def compute_shap_values(explainer, X, check_additivity: bool = True):
    """
    Compute SHAP values and validate the additivity property.
    
    Additivity check: SHAP values must sum to (prediction - base_value).
    A failed check indicates model output inconsistency or explainer mismatch.
    """
    shap_values = explainer(X, check_additivity=check_additivity)
    
    # For classifiers, shap_values.values has shape (n_samples, n_features, n_classes)
    # For regressors, shape is (n_samples, n_features)
    print(f"SHAP values computed: shape={shap_values.values.shape}")
    print(f"Base value (E[f(x)]): {shap_values.base_values[0]:.4f}")
    
    return shap_values

def get_global_feature_importance(shap_values, feature_names: list) -> list:
    """
    Rank features by mean absolute SHAP value (global importance).
    Returns list of (feature, mean_abs_shap) sorted descending.
    """
    import numpy as np
    
    vals = shap_values.values
    if vals.ndim == 3:  # Classifier: use positive class
        vals = vals[:, :, 1]
    
    mean_abs = np.abs(vals).mean(axis=0)
    ranked = sorted(zip(feature_names, mean_abs), key=lambda x: -x[1])
    return [(feat, round(float(imp), 5)) for feat, imp in ranked]
```

---

### Phase 3: Generate Explanation Plots

```python
def plot_global_beeswarm(shap_values, X, max_display: int = 20, output_path: str = None):
    """
    Beeswarm (summary) plot: shows feature importance AND effect direction.
    Red = high feature value, Blue = low feature value.
    X-axis = SHAP contribution (+ = pushes prediction up, - = pushes it down).
    """
    import shap
    shap.plots.beeswarm(shap_values, max_display=max_display, show=output_path is None)
    if output_path:
        import matplotlib.pyplot as plt
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()

def plot_local_waterfall(shap_values, instance_idx: int, output_path: str = None):
    """
    Waterfall plot for a single prediction: shows how each feature
    contributed (+ or -) relative to the base value to reach the final prediction.
    """
    import shap
    shap.plots.waterfall(shap_values[instance_idx], show=output_path is None)
    if output_path:
        import matplotlib.pyplot as plt
        plt.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close()

def plot_dependence(shap_values, X, feature: str, interaction_feature: str = "auto",
                    output_path: str = None):
    """
    Dependence plot: how does feature value correlate with its SHAP contribution?
    Colors points by interaction_feature to reveal interaction effects.
    """
    import shap
    shap.plots.scatter(shap_values[:, feature], color=shap_values[:, interaction_feature],
                       show=output_path is None)
```

---

### Phase 4: Fairness Audit

Compare mean absolute SHAP contributions of sensitive attributes across demographic subgroups.

```python
def fairness_audit(
    model,
    X_test,
    y_test,
    shap_values,
    sensitive_col: str,
    feature_names: list
) -> dict:
    """
    Audits for disparate impact: computes per-subgroup mean |SHAP| for the sensitive attribute.
    
    Fairness Metrics:
        Demographic Parity:  P(ŷ=1 | group=A) ≈ P(ŷ=1 | group=B)
        Equalized Odds:      P(ŷ=1 | y=1, group=A) ≈ P(ŷ=1 | y=1, group=B)
    """
    import numpy as np
    import pandas as pd
    
    X_df = pd.DataFrame(X_test, columns=feature_names)
    vals = shap_values.values
    if vals.ndim == 3:
        vals = vals[:, :, 1]
    
    audit_results = {}
    for group in X_df[sensitive_col].unique():
        mask = X_df[sensitive_col] == group
        group_shap = np.abs(vals[mask]).mean(axis=0)
        sensitive_idx = feature_names.index(sensitive_col)
        
        # Disparate impact: sensitive attribute's mean |SHAP| for this group
        audit_results[str(group)] = {
            "n_samples": int(mask.sum()),
            "mean_abs_sensitive_shap": round(float(group_shap[sensitive_idx]), 5),
            "top_3_features": [
                feature_names[i] for i in np.argsort(-group_shap)[:3]
            ]
        }
    
    # Flag if max group SHAP diverges > 2x from min group SHAP for sensitive attr
    shap_vals = [v["mean_abs_sensitive_shap"] for v in audit_results.values()]
    disparity_ratio = max(shap_vals) / max(min(shap_vals), 1e-9)
    
    return {
        "sensitive_attribute": sensitive_col,
        "group_results": audit_results,
        "disparity_ratio": round(disparity_ratio, 3),
        "fairness_flag": "⚠️ POTENTIAL BIAS DETECTED" if disparity_ratio > 2.0 else "✅ No Significant Disparity"
    }
```

---

## Zero-Dependency SHAP Approximation (for Testing)

```python
def approx_shap_importance(feature_matrix: list, predictions: list) -> dict:
    """
    Stdlib-only SHAP approximation via permutation-based marginal contributions.
    Use for unit-testing pipelines without the shap package.
    """
    import math
    n_samples = len(feature_matrix)
    n_features = len(feature_matrix[0]) if feature_matrix else 0
    mean_pred = sum(predictions) / max(1, n_samples)
    
    # Simplified: approximate feature importance as abs deviation from mean
    importance = {}
    for j in range(n_features):
        col_vals = [feature_matrix[i][j] for i in range(n_samples)]
        col_mean = sum(col_vals) / n_samples
        variance = sum((v - col_mean) ** 2 for v in col_vals) / max(1, n_samples)
        importance[f"feature_{j}"] = round(math.sqrt(variance), 4)
    
    return dict(sorted(importance.items(), key=lambda x: -x[1]))
```

---

## Output Format: Model Explanation Report

```markdown
## 🔍 Model Explanation Report

**Model**: XGBoost Classifier v2.1  
**Dataset**: Customer Churn Prediction (n=48,320)  
**Explainer**: TreeSHAP  
**Base Value (E[f(x)])**: 0.2134

---

### Global Feature Importance (Mean |SHAP|)
| Rank | Feature | Mean |SHAP| | Interpretation |
|:--|:--|--:|:--|
| 1 | `days_since_last_login` | 0.1842 | Highest predictor — inactivity strongly drives churn |
| 2 | `plan_type` | 0.1234 | Free tier users 3.2× more likely to churn |
| 3 | `support_tickets_30d` | 0.0891 | High support contact precedes churn |

### Local Explanation: Instance #12,459
- **Prediction**: 0.87 (High Churn Risk)
- **Base Value**: 0.21
- **Key Drivers**: `days_since_last_login` (+0.31), `plan_type=free` (+0.22), `support_tickets=4` (+0.13)

### Fairness Audit
| Group | n | Sensitive Attr Mean |SHAP| | Status |
|:--|--:|--:|:--|
| Gender=Male | 22,400 | 0.0042 | ✅ |
| Gender=Female | 21,890 | 0.0039 | ✅ |
**Disparity Ratio**: 1.08 — ✅ No significant demographic bias detected
```

---

## Anti-Patterns & Traps to Avoid

1. **Using KernelSHAP on Tree Models** — KernelSHAP is 100–1000× slower than TreeSHAP for tree ensembles and produces approximations. **Fix**: Always use `shap.TreeExplainer` for XGBoost, LightGBM, RandomForest.
2. **Summarizing Background with Full Training Set** — Passing all 1M training rows to `KernelExplainer` causes memory overflow. **Fix**: Use `shap.kmeans(X_train, k=50)` to create a representative 50-row background.
3. **Interpreting Feature Importance Without Direction** — A feature with high mean |SHAP| could push predictions up OR down depending on its value. A bar chart alone is misleading. **Fix**: Always show the beeswarm plot to visualize directionality.
4. **Fairness Audit via Prediction Parity Alone** — Equal positive prediction rates (Demographic Parity) can mask Equalized Odds violations. **Fix**: Check both Demographic Parity AND True Positive Rate parity across sensitive subgroups.
5. **Skipping Additivity Verification** — If SHAP values don't sum to `prediction - base_value`, the explainer is mismatched with the model. **Fix**: Always run `check_additivity=True` and investigate mismatches before presenting results.

---

## Quality Checklist

- [ ] Explainer type selected based on model family (TreeSHAP for tree models, not KernelSHAP)
- [ ] Background dataset for KernelSHAP summarized with `shap.kmeans()` (≤ 100 rows)
- [ ] Additivity check passes: SHAP values sum to `prediction - base_value`
- [ ] Global explanation: beeswarm plot generated showing direction AND magnitude
- [ ] Local explanation: waterfall plot generated for at least 3 representative instances
- [ ] Fairness audit: both Demographic Parity and TPR parity computed for all sensitive attributes
- [ ] Potential leakage check: no ID or timestamp features in top-5 SHAP contributors
- [ ] Model Card generated with explanation report and fairness summary
- [ ] Companion script `shap_explainer.py --test` passes with zero errors

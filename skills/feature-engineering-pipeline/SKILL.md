---
name: feature-engineering-pipeline
description: >-
  Use this skill when designing, building, or refining machine learning feature engineering pipelines.
  Constructs reproducible transformations (cyclical datetime, target encoding, interaction terms, scaling)
  while strictly preventing train-test data leakage.
---

# Feature Engineering Pipeline & Preprocessing Engine

Guides the systematic extraction, transformation, and selection of predictive features for tabular and time-series machine learning models, enforcing strict data leakage prevention.

## When to Use This Skill
- When transforming raw raw columns into high-signal numerical representations for ML models.
- When encoding datetime fields (hour, day of week, cyclical sin/cos transformations).
- When handling high-cardinality categorical features (Target Encoding, Weight of Evidence).
- When building `scikit-learn` Pipeline or `ColumnTransformer` workflows.
- Trigger phrases: `"feature engineering"`, `"create features"`, `"encode categories"`, `"cyclical encoding"`, `"build ML pipeline"`.

---

## The Cardinal Rule: Zero Data Leakage

```
❌ WRONG (Leakage):   fit_transform(Entire Dataset) ---> train_test_split()
✅ CORRECT:          train_test_split() ---> fit(Train Data) ---> transform(Test Data)
```

Never compute scaling parameters (mean/std), target encodings, or imputation medians across the entire dataset before splitting. All statistics must be computed **strictly on the training split**.

---

## Step-by-Step Python Pipeline Pattern

```python
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from category_encoders import TargetEncoder

def build_feature_engineering_pipeline(numeric_features, categorical_features, target_encoded_features):
    """
    Constructs an end-to-end, leak-proof scikit-learn preprocessing pipeline.
    """
    # 1. Numeric Transformation (Median Imputation + Scaling)
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # 2. Low-Cardinality Categoricals (One-Hot Encoding)
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # 3. High-Cardinality Categoricals (Target Encoding with Smoothing)
    target_transformer = Pipeline(steps=[
        ('target_enc', TargetEncoder(smoothing=10.0))
    ])
    
    # 4. Combine via ColumnTransformer
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features),
        ('target', target_transformer, target_encoded_features)
    ], remainder='passthrough')
    
    return preprocessor

# Helper for Cyclical Datetime Features
def encode_cyclical_datetime(df: pd.DataFrame, col: str, period: int):
    df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / period)
    df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / period)
    return df
```

## Anti-Patterns & Traps to Avoid

1. **Target Leakage via Naive Target Encoding**: Computing mean target values across categories using the full dataset without smoothing or out-of-fold partitioning. Models overfit completely to rare categories that have only 1 or 2 rows. Always apply empirical Bayes smoothing or use cross-validated target encoding.
2. **Treating Cyclical Time Features Linearly**: Encoding hour-of-day as raw integers 0–23 or month as 1–12. Linear models and tree splits treat 23:00 and 00:00 as maximally distant (difference of 23) rather than contiguous (difference of 1 hour). Always encode periodic cycles using paired sine and cosine transforms.
3. **Ordinal Encoding on Nominal Categoricals**: Assigning arbitrary integers (e.g., Red=1, Blue=2, Green=3) to unranked categories. Linear models, SVMs, and neural networks falsely assume that Blue is "greater than" Red. Use One-Hot encoding for low cardinality or Target/Frequency encoding for high cardinality.
4. **Fitting Transformers Outside Cross-Validation Folds**: Calling `pipeline.fit_transform(X)` before running K-Fold cross-validation. Every fold must fit transformers solely on the train split and transform the validation split blindly.

---

## Quality Checklist

- [ ] All feature transformers are encapsulated inside an end-to-end scikit-learn `Pipeline` or `ColumnTransformer`.
- [ ] Pipeline is fitted strictly on `X_train` and applied (`.transform()`) to `X_test` to prevent leakage.
- [ ] Periodic temporal features (hour, day of week, month) are transformed into paired sine/cosine coordinates.
- [ ] Target encoding uses empirical Bayes smoothing (`TargetEncoder(smooth="auto")`) or K-fold out-of-sample encodings.
- [ ] High-cardinality nominal columns are checked for rare categories and grouped into an `"OTHER"` bucket.
- [ ] Multicollinear features are audited with Variance Inflation Factor (VIF) or correlation filtering ($r > 0.90$).

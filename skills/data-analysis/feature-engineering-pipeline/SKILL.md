---
name: feature-engineering-pipeline
description: >-
  Use this skill when designing, building, or refining machine learning feature engineering pipelines.
  Constructs reproducible, leakage-proof transformations: cyclical datetime sin/cos encoding,
  empirical Bayes smoothed target encoding, interaction term generation, frequency and ordinal encoding,
  and missing indicator columns. All transformers packaged inside scikit-learn Pipelines to guarantee
  strict train-only fitting, with a zero-dependency companion script for validation.
---

# Feature Engineering Pipeline & Preprocessing Engine

Acts as a Senior ML Engineer. Transforms raw, messy columns into high-signal numerical feature vectors that tree models, linear models, and neural networks can consume safely — with zero data leakage guaranteed through Pipeline encapsulation.

## When to Use This Skill
- When transforming raw columns into high-signal numerical representations for ML models.
- When encoding datetime fields (hour, day of week, cyclical sin/cos transformations).
- When handling high-cardinality categorical features (Target Encoding, Frequency Encoding, WoE).
- When building `scikit-learn` Pipeline or `ColumnTransformer` workflows.
- When generating interaction terms, polynomial features, or log-ratio transforms.
- When auditing an existing pipeline for leakage, collinearity, or encoding bugs.
- Trigger phrases: `"feature engineering"`, `"create features"`, `"encode categories"`, `"cyclical encoding"`, `"build ML pipeline"`, `"target encoding"`, `"interaction terms"`, `"preprocessing pipeline"`.

---

## The Cardinal Rule: Zero Data Leakage

```
❌ WRONG (Global Leakage):
   fit_transform(FULL DATASET) ──► train_test_split() ──► Model.fit(X_train)

❌ WRONG (CV Leakage):
   fit_transform(X) ──► KFold cross_val_score(estimator, X, y)

✅ CORRECT:
   train_test_split()
       └─► Pipeline.fit(X_train, y_train)  # transformers fitted on train only
           └─► Pipeline.transform(X_test)   # transforms applied without refitting
```

Every statistic (mean, median, target frequencies, scaler parameters) must be computed **exclusively on the training partition**.

---

## Feature Transformation Catalog

### 1. Cyclical Datetime Encoding

Raw integers (hour=23, hour=0) are treated as maximally distant by linear models. Sin/cos projection preserves continuity.

```python
import math

def encode_cyclical(value: float, period: float) -> tuple:
    """
    Map a periodic value into (sin, cos) coordinates.
    
    Examples:
        Hour of day:    encode_cyclical(hour, 24)
        Day of week:    encode_cyclical(dow, 7)
        Month of year:  encode_cyclical(month, 12)
        Minute of hour: encode_cyclical(minute, 60)
    """
    radians = 2 * math.pi * value / period
    return round(math.sin(radians), 6), round(math.cos(radians), 6)

def add_cyclical_features(rows: list, col: str, period: float) -> list:
    """Add sin/cos columns from a periodic integer column in a list-of-dicts dataset."""
    for row in rows:
        if col in row and row[col] is not None:
            try:
                sin_val, cos_val = encode_cyclical(float(row[col]), period)
                row[f"{col}_sin"] = sin_val
                row[f"{col}_cos"] = cos_val
            except (ValueError, TypeError):
                row[f"{col}_sin"] = 0.0
                row[f"{col}_cos"] = 1.0  # Default to angle=0
    return rows
```

---

### 2. Target Encoding with Empirical Bayes Smoothing

Naïve target encoding (mean target per category) severely overfits on rare categories. Smoothing pulls rare-category estimates toward the global mean.

```python
def fit_target_encoder(rows: list, cat_col: str, target_col: str,
                        smoothing: float = 10.0) -> dict:
    """
    Computes smoothed target means per category (train data only).
    
    Formula: smoothed_mean = (n * cat_mean + m * global_mean) / (n + m)
    where m = smoothing parameter (larger m = more regularization toward global mean)
    """
    global_mean = sum(float(r[target_col]) for r in rows if r.get(target_col) not in (None, "")) \
                  / max(1, sum(1 for r in rows if r.get(target_col) not in (None, "")))
    
    # Aggregate per category
    cat_stats: dict = {}
    for row in rows:
        cat = row.get(cat_col, "UNKNOWN")
        try:
            target = float(row[target_col])
        except (ValueError, TypeError, KeyError):
            continue
        if cat not in cat_stats:
            cat_stats[cat] = {"sum": 0.0, "count": 0}
        cat_stats[cat]["sum"] += target
        cat_stats[cat]["count"] += 1
    
    # Apply smoothing
    encoder = {}
    for cat, stats in cat_stats.items():
        n = stats["count"]
        cat_mean = stats["sum"] / n
        encoder[cat] = (n * cat_mean + smoothing * global_mean) / (n + smoothing)
    
    encoder["__global_mean__"] = global_mean  # Fallback for unseen categories
    return encoder

def apply_target_encoder(rows: list, cat_col: str, encoder: dict) -> list:
    """Transform categories using a fitted target encoder (test data)."""
    global_mean = encoder.get("__global_mean__", 0.0)
    for row in rows:
        cat = row.get(cat_col, "UNKNOWN")
        row[f"{cat_col}_target_enc"] = encoder.get(cat, global_mean)
    return rows
```

---

### 3. Frequency Encoding

Replaces each category with how often it appears in the training set. Preserves rank information without target leakage.

```python
def fit_frequency_encoder(rows: list, cat_col: str) -> dict:
    """Compute per-category frequency ratios from training data."""
    total = len(rows)
    counts: dict = {}
    for row in rows:
        cat = row.get(cat_col, "UNKNOWN")
        counts[cat] = counts.get(cat, 0) + 1
    return {cat: round(count / total, 6) for cat, count in counts.items()}

def apply_frequency_encoder(rows: list, cat_col: str, encoder: dict) -> list:
    for row in rows:
        cat = row.get(cat_col, "UNKNOWN")
        row[f"{cat_col}_freq_enc"] = encoder.get(cat, 0.0)
    return rows
```

---

### 4. Interaction Terms

Capture non-linear relationships between pairs of numeric features.

```python
def generate_interaction_terms(rows: list, col_a: str, col_b: str,
                                 operations: list = ("multiply", "ratio")) -> list:
    """
    Generate pairwise interaction features between two numeric columns.
    
    Operations:
        multiply: col_a × col_b  (captures joint magnitude)
        ratio:    col_a / col_b  (captures relative scale)
        diff:     col_a - col_b  (captures absolute gap)
    """
    for row in rows:
        try:
            a = float(row.get(col_a, 0) or 0)
            b = float(row.get(col_b, 0) or 0)
        except (ValueError, TypeError):
            continue
        
        if "multiply" in operations:
            row[f"{col_a}_x_{col_b}"] = round(a * b, 6)
        if "ratio" in operations:
            row[f"{col_a}_div_{col_b}"] = round(a / b, 6) if b != 0 else 0.0
        if "diff" in operations:
            row[f"{col_a}_minus_{col_b}"] = round(a - b, 6)
    return rows
```

---

### 5. Missing Value Indicator Columns

For MNAR (Missing Not at Random) columns, the fact that data is missing is itself predictive.

```python
def add_missing_indicators(rows: list, cols: list) -> list:
    """Add binary {col}_is_missing columns for specified columns."""
    for row in rows:
        for col in cols:
            row[f"{col}_is_missing"] = 1 if row.get(col) in (None, "", "nan", "NaN") else 0
    return rows
```

---

## Full Pipeline Construction Pattern

```python
# scikit-learn Pipeline (requires sklearn)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

def build_preprocessing_pipeline(numeric_cols, low_card_cat_cols, high_card_cat_cols):
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    low_card_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False, max_categories=20))
    ])
    # High cardinality: use frequency encoding or target encoding (fit on train only!)
    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_cols),
        ("cat_low", low_card_transformer, low_card_cat_cols),
    ], remainder="drop")
    return preprocessor
```

---

## Output Format: Feature Engineering Audit

```markdown
## ⚙️ Feature Engineering Audit

**Input Features**: 42 raw columns
**Output Features**: 87 engineered features

### Transformations Applied
| Raw Column | Transformation | Output Columns | Leakage Safe? |
|:--|:--|:--|:--|
| `signup_hour` | Cyclical sin/cos | `signup_hour_sin`, `signup_hour_cos` | ✅ Yes |
| `country` | Target encoding (smooth=10) | `country_target_enc` | ✅ Fitted on train only |
| `plan_type` | One-hot encoding | `plan_type_free`, `plan_type_pro` | ✅ Yes |
| `sessions × revenue` | Interaction multiply | `sessions_x_revenue` | ✅ Yes |

### Warnings
- ⚠️ `user_id` dropped — ID column with 100% cardinality (no predictive signal)
- ⚠️ `signup_date` raw string — converted to 3 cyclical features
```

---

## Anti-Patterns & Traps to Avoid

1. **Leaking Target Into Features** — Naïve `groupby(category)["target"].mean()` on the full dataset leaks the answer. **Fix**: Use K-fold out-of-sample target encoding or empirical Bayes smoothing fitted only on `X_train`.
2. **Linear Encoding of Cyclical Variables** — `hour_of_day = 23` and `hour_of_day = 0` appear maximally different numerically but are actually adjacent. **Fix**: Always use sin/cos projection for periodic features.
3. **Fitting `ColumnTransformer` Outside the Pipeline** — Calling `preprocessor.fit_transform(X)` before `train_test_split()`. **Fix**: Chain the preprocessor inside `Pipeline([("prep", preprocessor), ("model", clf)])` and fit only on training data.
4. **OneHot on High-Cardinality Columns** — OneHot-encoding a column with 10,000 unique cities creates 10,000 sparse binary columns, causing memory explosions and generalization failures. **Fix**: Use frequency encoding or target encoding for columns with cardinality > 50.
5. **Dropping Missing Indicator Before Imputation** — Imputing missing values without first recording which cells were missing discards the missingness signal. **Fix**: Call `add_missing_indicators()` before any imputation step.

---

## Quality Checklist

- [ ] `add_missing_indicators()` called before any imputation step
- [ ] All periodic temporal features encoded with sin/cos (not raw integers)
- [ ] Target encoding uses smoothing with `__global_mean__` fallback for unseen categories
- [ ] All transformers fitted strictly on `X_train`; `.transform()` only applied to `X_test`
- [ ] High-cardinality columns (> 50 unique values) use frequency or target encoding, not OHE
- [ ] Interaction terms only generated between domain-justified feature pairs
- [ ] Final feature count documented in Feature Engineering Audit output
- [ ] Companion script `feature_pipeline.py --test` passes with zero errors

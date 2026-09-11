---
name: eda-and-data-cleaning
description: >-
  Use this skill when exploring, auditing, cleaning, and preprocessing tabular datasets.
  Automates Exploratory Data Analysis (EDA), detects outliers, handles missing value imputation,
  profiles distributions, identifies multicollinearity via VIF, classifies missingness mechanisms
  (MCAR/MAR/MNAR), and produces a structured Data Quality Report before model training.
---

# Exploratory Data Analysis (EDA) & Data Cleaning

Acts as a Lead Data Engineer / Statistician. Transforms raw, messy data into analysis-ready, modeling-safe datasets through a rigorous 5-phase profiling and cleaning pipeline. Produces fully reproducible cleaning scripts and a structured Data Quality Report with quantified confidence.

## When to Use This Skill
- When receiving a new dataset (CSV, Parquet, Excel, JSON, SQL) requiring initial inspection.
- When cleaning dirty data: handling missing values, duplicates, type errors, and malformed strings.
- When identifying outliers, distribution skews, high cardinality, and multicollinearity before training.
- When auditing data pipelines for schema drift, referential integrity, and value range violations.
- Before any feature engineering or machine learning modelling work begins.
- Trigger phrases: `"perform EDA"`, `"clean this dataset"`, `"data profiling"`, `"handle missing values"`, `"detect outliers"`, `"data quality report"`, `"audit this CSV"`.

---

## The 5-Phase Data Audit Pipeline

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      EDA & Data Cleaning Lifecycle                       │
├────────────────┬───────────────┬───────────────┬────────────┬────────────┤
│ 1. Schema &    │ 2. Missingness│ 3. Outlier &  │ 4. Collin- │ 5. Quality │
│    Type Audit  │    Analysis   │    Skew Audit │    earity  │    Export  │
└────────────────┴───────────────┴───────────────┴────────────┴────────────┘
```

---

### Phase 1: Schema & Type Audit

**Goal**: Confirm every column has the correct dtype before any numerical computation.

```python
def audit_schema(df):
    report = {}
    for col in df.columns:
        inferred = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else \
                   "datetime" if pd.api.types.is_datetime64_any_dtype(df[col]) else \
                   "categorical" if df[col].nunique() / len(df) < 0.05 else "text"
        report[col] = {
            "pandas_dtype": str(df[col].dtype),
            "inferred_semantic_type": inferred,
            "n_unique": df[col].nunique(),
            "cardinality_pct": round(df[col].nunique() / len(df) * 100, 2)
        }
    return report
```

**Action Rules**:
- Convert string columns holding ISO dates → `pd.to_datetime()`
- Convert integer boolean flags (0/1) → `bool` dtype
- Flag columns with cardinality > 95% as potential ID columns (leakage risk)
- Flag columns with cardinality < 1% as likely constants (zero information)

---

### Phase 2: Missingness Analysis & Targeted Imputation

**Goal**: Classify *why* data is missing — the mechanism determines the correct remedy.

| Mechanism | Definition | Correct Strategy |
|:--|:--|:--|
| **MCAR** (Missing Completely at Random) | Missingness is unrelated to any observed or unobserved data. | Safe to drop rows or impute with median/mode |
| **MAR** (Missing at Random) | Missingness depends on *other observed* columns (e.g., age missing only for users who skipped onboarding). | Impute with multivariate method (IterativeImputer / KNN) |
| **MNAR** (Missing Not at Random) | Missingness depends on the missing value itself (e.g., income not reported by highest earners). | Model missingness explicitly; add binary `is_missing` indicator column |

```python
def classify_and_impute_missing(df, target_col=None):
    report = {}
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if target_col and target_col in numeric_cols:
        numeric_cols.remove(target_col)  # Never impute the target variable
    
    for col in df.columns:
        miss_rate = df[col].isnull().mean()
        if miss_rate == 0:
            continue
        
        # MNAR heuristic: high missing rate + correlated with target
        is_mnar_suspect = miss_rate > 0.20
        
        report[col] = {"missing_pct": round(miss_rate * 100, 2), "mechanism": "MNAR" if is_mnar_suspect else "MCAR/MAR"}
        
        if miss_rate > 0.60:
            print(f"[DROP] '{col}': {miss_rate:.0%} missing — dropping column")
            df = df.drop(columns=[col])
        elif is_mnar_suspect:
            # Add missingness indicator before imputing
            df[f"{col}_was_missing"] = df[col].isnull().astype(int)
            df[col] = df[col].fillna(df[col].median() if col in numeric_cols else "UNKNOWN")
        elif col in numeric_cols:
            skewness = df[col].skew()
            fill_val = df[col].median() if abs(skewness) > 1.0 else df[col].mean()
            df[col] = df[col].fillna(fill_val)
        else:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "UNKNOWN")
    
    return df, report
```

> **Critical Rule**: Never compute imputation statistics on the full dataset. Always split first → fit imputers on `X_train` → transform `X_test`.

---

### Phase 3: Outlier Detection & Distribution Audit

**Two methods based on distribution shape:**

```python
def detect_outliers(df, method="iqr"):
    numeric_cols = df.select_dtypes(include="number").columns
    outlier_report = {}
    
    for col in numeric_cols:
        series = df[col].dropna()
        skewness = series.skew()
        
        if method == "iqr" or abs(skewness) > 1.0:
            # IQR method: robust to non-normal distributions
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outlier_mask = (series < lower) | (series > upper)
        else:
            # Z-score method: for approximately normal columns
            z_scores = (series - series.mean()) / series.std()
            outlier_mask = z_scores.abs() > 3.0
            lower, upper = series.mean() - 3 * series.std(), series.mean() + 3 * series.std()
        
        n_outliers = outlier_mask.sum()
        outlier_report[col] = {
            "n_outliers": int(n_outliers),
            "outlier_pct": round(n_outliers / len(series) * 100, 2),
            "skewness": round(skewness, 3),
            "method_used": "IQR" if abs(skewness) > 1.0 else "Z-Score",
            "bounds": (round(lower, 4), round(upper, 4))
        }
    
    return outlier_report
```

> **Domain Rule**: Never auto-delete outliers in fraud detection, anomaly detection, or intrusion detection domains. Extreme values ARE the signal.

---

### Phase 4: Multicollinearity & Leakage Detection

**VIF (Variance Inflation Factor)** measures how much a feature's variance is explained by all other features. VIF > 10 indicates severe multicollinearity.

```python
def compute_vif(df):
    """Computes VIF for all numeric columns using standard library math only."""
    import math
    numeric_df = df.select_dtypes(include="number").dropna()
    cols = numeric_df.columns.tolist()
    vif_results = {}
    
    for i, col in enumerate(cols):
        y = numeric_df[col].values
        X = numeric_df.drop(columns=[col]).values
        
        # Compute R² via correlation matrix approximation
        corr_matrix = numeric_df.corr()
        if col in corr_matrix.columns:
            r_squared_approx = max(
                corr_matrix[col].drop(col).abs().max() ** 2, 0.0
            )
            vif = 1 / (1 - r_squared_approx) if r_squared_approx < 1.0 else float("inf")
            vif_results[col] = round(vif, 2)
    
    return {k: v for k, v in sorted(vif_results.items(), key=lambda x: -x[1])}

def detect_target_leakage(df, target_col, threshold=0.95):
    """Flags features with suspiciously high correlation to the target (potential leakage)."""
    numeric_df = df.select_dtypes(include="number")
    if target_col not in numeric_df.columns:
        return []
    corr = numeric_df.corr()[target_col].drop(target_col)
    leaking_cols = corr[corr.abs() >= threshold].index.tolist()
    return leaking_cols
```

---

### Phase 5: Data Quality Report Output Format

Every EDA run must produce this structured report:

```markdown
## 📊 Data Quality Report

**Dataset**: `{filename}`  
**Dimensions**: {rows:,} rows × {cols} columns  
**Overall Quality Score**: 🟢 High (>85%) / 🟡 Moderate (60–85%) / 🔴 Poor (<60%)

---

### Schema & Type Summary
| Column | Pandas Type | Semantic Type | Unique Values | Action Taken |
|:--|:--|:--|--:|:--|
| `user_id` | object | ID/Key | 98,234 | 🔴 Leakage Risk — exclude from features |
| `revenue` | float64 | numeric | 4,521 | ✅ No action needed |
| `signup_date` | object | datetime | 365 | ⚠️ Converted to datetime |

### Missingness Summary
| Column | Missing % | Mechanism | Imputation Applied |
|:--|--:|:--|:--|
| `age` | 12.3% | MAR | Median imputation + `age_was_missing` indicator |
| `country` | 2.1% | MCAR | Mode imputation |

### Outlier Summary
| Column | Outlier Count | Outlier % | Method | Action |
|:--|--:|--:|:--|:--|
| `revenue` | 412 | 0.42% | IQR | Capped at [Q1−1.5×IQR, Q3+1.5×IQR] |

### Multicollinearity Flags (VIF > 5)
- `total_sessions` & `total_pageviews`: VIF = 12.4 — drop one or use PCA

### Leakage Warnings
- ⚠️ `churn_flag_next_month`: correlation = 0.97 with target — likely a future leak

### Cleaning Actions Summary
- Dropped 3 columns with >60% missing: `phone_number`, `fax`, `legacy_id`
- Removed 1,240 exact duplicate rows
- Capped outliers in 2 columns: `revenue`, `session_duration`
```

---

## Companion Script

Run the full EDA pipeline via the companion script:
```bash
python skills/data-analysis/eda-and-data-cleaning/scripts/eda_toolkit.py --test
python skills/data-analysis/eda-and-data-cleaning/scripts/eda_toolkit.py --file data.csv --target churn
```

---

## Anti-Patterns & Traps to Avoid

1. **Pre-Split Leakage** — Fitting imputers or scalers on the full dataset before the train/test split. Test-set statistics contaminate training. **Fix**: Always split first, then `fit` only on `X_train`.
2. **Blind `dropna()`** — Dropping every row with any null silently discards 40–60% of data and introduces survivorship bias. **Fix**: Profile missingness mechanisms; impute strategically.
3. **Mean Imputing Skewed Columns** — Revenue, latency, and counts are power-law distributed; mean imputation drags the distribution. **Fix**: Use median for columns with `|skew| > 1.0`.
4. **Auto-Deleting Fraud Outliers** — In anomaly detection, outliers ARE the target signal. **Fix**: Domain-check before any outlier removal.
5. **Ignoring Categorical Cardinality** — High-cardinality text columns (user agent strings, IP addresses) passed directly into models cause memory explosion and target leakage. **Fix**: Flag cardinality > 50% for exclusion.

---

## Quality Checklist

- [ ] Train/test split performed *before* any imputation, scaling, or encoding
- [ ] Missing rates profiled per column; mechanism (MCAR/MAR/MNAR) classified
- [ ] `is_missing` indicator columns added for MNAR-suspect features
- [ ] Outlier detection method selected based on distribution skewness
- [ ] VIF computed; multicollinear pairs (VIF > 10) flagged for removal
- [ ] Target leakage check run; columns with |r| > 0.95 to target excluded
- [ ] Data Quality Report generated and reviewed before model training begins
- [ ] Companion script `eda_toolkit.py --test` passes with zero errors

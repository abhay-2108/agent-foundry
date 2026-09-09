---
name: eda-and-data-cleaning
description: >-
  Use this skill when exploring, auditing, cleaning, and preprocessing tabular datasets.
  Automates Exploratory Data Analysis (EDA), detects outliers, handles missing value imputation,
  profiles distributions, and identifies potential data leakage before model training.
---

# Exploratory Data Analysis (EDA) & Data Cleaning

A systematic data science skill for profiling, cleaning, and transforming raw, messy datasets into high-quality, modeling-ready data frames with zero data leakage.

## When to Use This Skill
- When receiving a new dataset (CSV, Parquet, Excel, SQL table) requiring initial inspection.
- When cleaning dirty data: handling missing values, duplicates, and malformed strings.
- When identifying outliers, distribution skews, high cardinality, and multicollinearity.
- Before training machine learning models or building analytical dashboards.
- Trigger phrases: `"perform EDA"`, `"clean this dataset"`, `"data profiling"`, `"handle missing values"`, `"detect outliers"`.

---

## The 4-Phase Data Audit Pipeline

```
┌────────────────────────────────────────────────────────┐
│                   EDA & Cleaning Pipeline              │
├──────────────┬──────────────┬─────────────┬────────────┤
│ 1. Schema &  │ 2. Missing & │ 3. Outlier  │ 4. Clean   │
│    Types     │    Nulls     │    & Skew   │    Export  │
└──────────────┴──────────────┴─────────────┴────────────┘
```

1. **Schema & Types**: Validate column dtypes (datetime vs string, categorical vs numeric, boolean flags).
2. **Missing & Duplicates**: Inspect missingness mechanisms (MCAR, MAR, MNAR); select appropriate imputation strategy.
3. **Outliers & Distribution**: Measure skewness, kurtosis; flag extreme anomalies using IQR or Z-score methods.
4. **Leakage & Correlation**: Detect target leakage columns (features created *after* the event) and collinear pairs ($r > 0.85$).

---

## Step-by-Step Python Implementation Pattern

```python
import pandas as pd
import numpy as np

def audit_and_clean_dataframe(df: pd.DataFrame, target_col: str = None) -> pd.DataFrame:
    cleaned = df.copy()
    
    # 1. Deduplication
    initial_rows = len(cleaned)
    cleaned = cleaned.drop_duplicates()
    print(f"Removed {initial_rows - len(cleaned)} duplicate rows.")
    
    # 2. Missing Value Profiling
    missing_pct = cleaned.isnull().mean() * 100
    drop_cols = missing_pct[missing_pct > 60].index.tolist()
    if drop_cols:
        print(f"Dropping columns with >60% missing: {drop_cols}")
        cleaned = cleaned.drop(columns=drop_cols)
        
    # 3. Numeric Imputation & Categorical Standardization
    numeric_cols = cleaned.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)
        
    for col in numeric_cols:
        median_val = cleaned[col].median()
        cleaned[col] = cleaned[col].fillna(median_val)
        
    categorical_cols = cleaned.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in categorical_cols:
        cleaned[col] = cleaned[col].fillna("UNKNOWN").str.strip().str.lower()
        
    # 4. Outlier Capping (IQR Method)
    for col in numeric_cols:
        q25, q75 = cleaned[col].quantile(0.25), cleaned[col].quantile(0.75)
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        cleaned[col] = cleaned[col].clip(lower=lower_bound, upper=upper_bound)
        
    return cleaned
```

## EDA Report Template

```markdown
### 📊 Exploratory Data Analysis (EDA) Summary

**Dataset Dimensions**: [Rows] rows × [Columns] columns
**Duplicate Rows Removed**: [Count]
**Overall Data Quality Score**: 🟢 High / 🟡 Moderate / 🔴 Requires Heavy Cleaning

#### Key Insights & Findings:
- **Missing Values**: Handled [X] null values using median imputation on skewed numerical columns.
- **Outliers Capped**: Columns `revenue` and `age` had high outlier counts, capped via IQR boundaries.
- **High Correlation Warning**: Columns `feature_a` and `feature_b` exhibit high correlation ($r = 0.94$).
```

---

## Anti-Patterns & Traps to Avoid

1. **Pre-Split Data Leakage**: Computing imputation statistics (mean, median) or min-max scalers on the entire dataset *before* splitting into train and test sets. Information from the test set leaks into training features, producing unrealistically optimistic evaluation scores. Always split first, then fit on `X_train` only.
2. **Indiscriminate Row Dropping (`df.dropna()`)**: Blindly deleting every row containing any null value. This routinely discards 40–60% of available data and introduces severe survivor bias. Assess missingness mechanisms (MCAR, MAR, MNAR) and apply targeted imputation.
3. **Mean Imputation on Heavy-Tailed Distributions**: Imputing skewed columns (income, web traffic, latency) using the arithmetic mean. Outliers drag the mean toward extreme values, distorting feature distributions. Always use median or quantile-based imputation for skewed data.
4. **Blind Outlier Deletion**: Automatically clipping or discarding values outside 1.5x IQR without domain verification. In fraud detection or cybersecurity, extreme outliers represent the exact target signals you need to detect.

---

## Quality Checklist

- [ ] Train/test split is performed *before* any imputation, scaling, or transformation.
- [ ] Missing value rates are profiled per column with explicit handling strategies (impute vs drop).
- [ ] Categorical columns are checked for cardinality, case normalization, and unexpected whitespace.
- [ ] Numeric columns are evaluated for skewness; median imputation is used on skewed features.
- [ ] Target variable distribution is verified for class imbalance or extreme target values.
- [ ] Correlation matrix is analyzed to flag multicollinear feature pairs ($r > 0.9$).

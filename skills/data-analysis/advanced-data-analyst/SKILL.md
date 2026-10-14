---
name: advanced-data-analyst
description: >-
  Use this skill when analyzing structured or tabular datasets, writing reproducible data analysis
  scripts (Python, Pandas, Polars, DuckDB), authoring analytical SQL queries (window functions,
  cohort retention, conversion funnels), discovering hidden patterns and anomalies, and extracting
  high-impact business insights and executive action items.
---

# Advanced Data Analyst & Analytics Intelligence

## Overview

Analyzes structured, tabular, and time-series datasets using reproducible Python (Pandas, Polars, DuckDB) and analytical SQL (window functions, cohort retention, funnel conversion). Discovers hidden patterns, quantifies trends, and formulates high-impact business insights.

## When to Use

- When tasked with exploring, querying, or analyzing any tabular dataset (CSV, JSON, Parquet, SQL).
- When writing analysis, transformation, or statistical scripts in Python (Pandas, Polars, Scipy, DuckDB).
- When authoring complex analytical SQL queries (window functions, cohorts, retention, funnels, CTEs).
- When investigating business metrics, churn drivers, revenue drops, or anomaly spikes.
- When generating executive data briefs, decision memos, or KPI dashboards.
- Trigger phrases: `"analyze this dataset"`, `"write a python analysis script"`, `"write an analytical SQL query"`, `"find patterns in this data"`, `"extract insights"`, `"cohort retention analysis"`, `"funnel analysis"`.

---
- **When NOT to use**: Training deep neural networks (use `ml-feature-and-model-lab`) or real-time event streaming (use `streaming-and-event-driven`).

## Core Process & 5-Phase Analytical Workflow

## The 5-Phase Analytical Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Advanced Data Analytics Lifecycle                    │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Ingestion & Automated Clean │ 2. Pattern & Anomaly Discovery        │
│ (Types, Missingness, Outliers) │ (Correlations, Seasonality, Segments) │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Reproducible Scripting      │ 4. Analytical SQL Engineering         │
│ (Pandas, Polars, DuckDB)       │ (Windowing, Cohorts, Funnels, CTEs)   │
├────────────────────────────────┴───────────────────────────────────────┤
│ 5. Executive Insight Synthesis & Decision Framework (Metric → Action)  │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Data Ingestion & Automated Cleaning

Before calculating metrics, audit data integrity to prevent garbage-in, garbage-out conclusions:
1. **Schema & Type Auditing**: Assert date/datetime columns are true timestamps; convert object strings to categorical or numeric.
2. **Missingness Profiling**:
   - Classify missing values: MCAR (Missing Completely at Random), MAR (Missing at Random), or MNAR (Missing Not at Random).
   - Document imputation strategy: median for skewed distributions, mode for categoricals, or forward-fill for time-series. Never impute target variables.
3. **Outlier & Sanity Guardrails**:
   - Compute Tukey's IQR boundaries: $[\text{Q1} - 1.5 \times \text{IQR}, \text{Q3} + 1.5 \times \text{IQR}]$.
   - Check physical constraints (e.g., negative prices, ages $> 120$, percentages $> 100\%$).

---

### Phase 2: Pattern & Anomaly Discovery

Uncover structural signals across feature interactions:
1. **Correlation Triangulation**:
   - Check linear relationships (Pearson) and monotonic non-linear relationships (Spearman).
   - Flag multicollinearity (VIF $> 5.0$).
   - Guard against **Simpson's Paradox**: always disaggregate global correlations across major demographic or account tiers.
2. **Distribution & Skewness Profiling**:
   - Identify Pareto distributions (e.g., 80% of volume from top 5% of users).
   - Flag bimodal distributions indicative of latent sub-populations.
3. **Temporal Trend & Seasonality Decomposition**:
   - Isolate baseline trend, weekly day-of-week seasonality, and residual noise.

---

### Phase 3: Analytical Python Script Generation

When generating Python analysis scripts, produce self-contained, reproducible, modular code adhering to these standards:
- Use vectorized operations in Pandas/Polars—never iterate with `for row in df.iterrows()`.
- Wrap analysis into clear steps with explicit prints or markdown exports.
- Use DuckDB for ultra-fast local SQL analytics over parquet or CSV files without database setup.

#### Self-Contained Analysis Template:
```python
import pandas as pd
import numpy as np

def run_data_investigation(file_path: str) -> dict:
    df = pd.read_csv(file_path)
    
    # 1. Baseline Health
    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_summary": df.isnull().sum()[df.isnull().sum() > 0].to_dict()
    }
    
    # 2. Key Segment Aggregation
    if "cohort_date" in df.columns and "revenue" in df.columns:
        cohort_kpis = df.groupby("cohort_date")["revenue"].agg(
            total_rev="sum",
            avg_rev="mean",
            user_count="count"
        ).reset_index()
        summary["cohort_kpis"] = cohort_kpis.to_dict(orient="records")
        
    return summary
```

---

### Phase 4: Analytical SQL Engineering

Author clean, CTE-modularized, production-grade SQL for BigQuery, Snowflake, PostgreSQL, or DuckDB:

#### 1. Cohort Retention Matrix Query
```sql
WITH user_first_activity AS (
    SELECT 
        user_id,
        DATE_TRUNC('month', MIN(activity_date)) AS cohort_month
    FROM events
    GROUP BY user_id
),
user_monthly_activity AS (
    SELECT 
        e.user_id,
        u.cohort_month,
        DATE_TRUNC('month', e.activity_date) AS activity_month,
        (EXTRACT(YEAR FROM e.activity_date) - EXTRACT(YEAR FROM u.cohort_month)) * 12 +
        (EXTRACT(MONTH FROM e.activity_date) - EXTRACT(MONTH FROM u.cohort_month)) AS period_number
    FROM events e
    JOIN user_first_activity u ON e.user_id = u.user_id
    GROUP BY 1, 2, 3, 4
)
SELECT 
    cohort_month,
    period_number,
    COUNT(DISTINCT user_id) AS active_users,
    ROUND(COUNT(DISTINCT user_id)::numeric / 
          FIRST_VALUE(COUNT(DISTINCT user_id)) OVER (PARTITION BY cohort_month ORDER BY period_number) * 100, 2) AS retention_rate
FROM user_monthly_activity
GROUP BY cohort_month, period_number
ORDER BY cohort_month, period_number;
```

#### 2. Rolling Window Trends & Outlier Detection
```sql
WITH daily_metrics AS (
    SELECT 
        event_date,
        COUNT(DISTINCT transaction_id) AS tx_count,
        SUM(amount_usd) AS total_volume
    FROM transactions
    GROUP BY event_date
)
SELECT 
    event_date,
    total_volume,
    -- 7-Day Moving Average
    AVG(total_volume) OVER (
        ORDER BY event_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_7d,
    -- Standard Deviation Band
    STDDEV(total_volume) OVER (
        ORDER BY event_date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_std_30d,
    -- Lagged Prior Week Comparison
    LAG(total_volume, 7) OVER (ORDER BY event_date) AS same_day_last_week
FROM daily_metrics
ORDER BY event_date;
```

---

### Phase 5: Executive Insight Synthesis & Decision Framework

Never present raw tables without interpretation. Format every conclusion using the **4-Step Insight Architecture**:

1. **The Finding (What happened)**: A single declarative sentence stating the exact quantitative change.
   - *Example*: "Gross margin declined 380 bps from 64.2% in Q1 to 60.4% in Q2."
2. **The Context / Root Cause (Why it happened)**: The statistical or segment driver behind the variance.
   - *Example*: "Decomposition reveals this was driven entirely by Enterprise tier shipping subsidies (+42% YoY), whereas SMB gross margins expanded by 110 bps."
3. **The Business Impact (Why it matters)**: Annualized or operational fallout.
   - *Example*: "At current run-rates, this represents an annualized margin drag of $2.4M."
4. **Recommended Action (What to do)**: Concrete, testable operational recommendation with an owner and deadline.
   - *Example*: "Cap tier-1 shipping subsidies at $250 per order and re-negotiate bulk freight rates prior to Q3 renewals."

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"Eyeballing the first 10 rows is enough to understand column distributions."* | Small samples hide extreme outliers, multimodal distributions, and categorical drift; automated profiling and summary statistics are required. |
| *"Dropping missing rows is fine if the dataset is large."* | Dropping rows without analyzing missingness mechanisms (MCAR vs. MAR/MNAR) introduces massive selection bias and skews aggregate calculations. |
| *"Correlation implies a causal business relationship."* | Correlation can be driven by confounding variables or sample selection artifacts; always state alternative causal hypotheses. |
| *"Presenting a raw chart without annotations is self-explanatory."* | Unannotated charts lead to misinterpretation; business executives need explicit callout annotations and 'So What?' executive action items. |

## Red Flags

- Reporting percentage changes on tiny base sample sizes (e.g. 'conversion grew 100%' when users went from 1 to 2).
- Writing analytical queries without handling division by zero (`NULLIF(denominator, 0)`).
- Failing to check for duplicate records after performing relational `JOIN` operations.
- Generating data visualizations with truncated axes without explicitly labeling the distortion.

## Verification

After completing the workflow, confirm:
- [ ] Data quality audit checks for nulls, cardinality, duplicate primary keys, and outlier bounds.
- [ ] Analytical SQL queries utilize window functions and CTEs with reproducible seeds.
- [ ] Every chart includes a clear title, labeled axes with units, and a takeaway callout box.
- [ ] Executive summary delivers quantifiable business recommendations with expected impact.

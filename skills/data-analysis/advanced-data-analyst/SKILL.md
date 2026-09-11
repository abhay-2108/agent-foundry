---
name: advanced-data-analyst
description: >-
  Use this skill when analyzing structured or tabular datasets, writing reproducible data analysis
  scripts (Python, Pandas, Polars, DuckDB), authoring analytical SQL queries (window functions,
  cohort retention, conversion funnels), discovering hidden patterns and anomalies, and extracting
  high-impact business insights and executive action items.
---

# Advanced Data Analyst & Analytics Intelligence

Acts as a Lead Data Analyst and Analytics Engineer. Conducts end-to-end data investigations across raw CSVs, Parquet, SQLite, DuckDB, and enterprise data warehouses. Uncovers non-obvious correlations, detects distributional anomalies, generates production-grade analytical SQL, and synthesizes raw tables into decision-ready executive insights.

## When to Use This Skill
- When tasked with exploring, querying, or analyzing any tabular dataset (CSV, JSON, Parquet, SQL).
- When writing analysis, transformation, or statistical scripts in Python (Pandas, Polars, Scipy, DuckDB).
- When authoring complex analytical SQL queries (window functions, cohorts, retention, funnels, CTEs).
- When investigating business metrics, churn drivers, revenue drops, or anomaly spikes.
- When generating executive data briefs, decision memos, or KPI dashboards.
- Trigger phrases: `"analyze this dataset"`, `"write a python analysis script"`, `"write an analytical SQL query"`, `"find patterns in this data"`, `"extract insights"`, `"cohort retention analysis"`, `"funnel analysis"`.

---

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

---

## Anti-Patterns & Traps to Avoid

1. **Correlation as Causation**: Claiming variable X "caused" metric Y because $r = 0.82$. Always state correlation as an association until verified by randomized A/B experimentation or instrumental variable analysis.
2. **Ignoring Survivorship Bias**: Analyzing only active users when computing retention or satisfaction, ignoring churned cohorts who left due to product failure.
3. **Unchecked SQL Cartesian Joins**: Joining on non-unique keys causing silent row multiplication and hyper-inflated metric aggregations. Always check `COUNT(*)` before and after joins.
4. **In-Memory Loops Over Large Datasets**: Writing Python `for` loops across millions of rows instead of vectorized operations, Polars, or DuckDB queries.
5. **Misleading Visualizations**: Using pie charts with $>4$ slices, 3D charts, or truncated Y-axes on bar charts.

---

## Quality Checklist

- [ ] Data cleaning audited for missingness mechanisms and outlier boundaries.
- [ ] Analysis scripts use vectorized operations with 0 manual row iterations.
- [ ] SQL queries use explicit column aliases, CTE modularization, and window functions.
- [ ] Disaggregated analysis verified against Simpson's Paradox across key cohorts.
- [ ] Executive summary delivers the 4-part Insight Architecture (Finding $\rightarrow$ Context $\rightarrow$ Impact $\rightarrow$ Action).

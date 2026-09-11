# 📊 Executive Data Analysis Brief: [Initiative / Metric Name]

**Date**: [YYYY-MM-DD]  
**Author**: Lead Data Analyst (`@data-scientist` / `@advanced-data-analyst`)  
**Data Sources**: `[table_or_file_paths]` (Records analyzed: `[N,NNN]`)  

---

## 🎯 Executive Summary & Verdict

- **Core Finding**: [1-sentence clear takeaway with primary quantitative metric]
- **Primary Driver**: [Single key segment, behavioral cohort, or operational change driving the number]
- **Financial / Operational Impact**: [Total ARR, churn delta, cost impact, or efficiency delta]
- **Immediate Recommended Action**: [Testable decision with designated owner and deadline]

---

## 📈 Key Findings & Root Cause Analysis

### 1. [Finding Headline: e.g., Enterprise Churn Concentrated in Month 2]
- **The Metric**: [Exact numbers, percentages, confidence intervals]
- **The Breakdown**:
  | Segment / Cohort | Prior Period | Current Period | Variance (bps / %) | Primary Driver |
  | :--- | :---: | :---: | :---: | :--- |
  | Segment A | 4.2% | 6.8% | +260 bps | Lack of SSO integration |
  | Segment B | 1.8% | 1.7% | -10 bps | Normal baseline |
- **Root Cause Hypothesis**: [Why did this happen? Cite specific user actions, error logs, or query findings]

---

## 🔍 Analytical SQL & Verification Queries

```sql
-- Query used to compute cohort retention / metric breakdown
WITH monthly_cohorts AS (
    SELECT 
        user_id,
        cohort_month,
        retention_month,
        is_active
    FROM analytics.user_activity_matrix
)
SELECT 
    cohort_month,
    retention_month,
    COUNT(DISTINCT user_id) AS cohort_size,
    ROUND(SUM(is_active)::numeric / COUNT(DISTINCT user_id) * 100, 2) AS retention_pct
FROM monthly_cohorts
GROUP BY 1, 2
ORDER BY 1, 2;
```

---

## 🚀 Recommended Strategic Actions

| Action Item | Hypothesis / Expected Impact | Owner | Target Date |
| :--- | :--- | :---: | :---: |
| **1. [Action 1]** | [e.g., +150 bps retention in Month 2] | `@product-lead` | [YYYY-MM-DD] |
| **2. [Action 2]** | [e.g., Eliminate $45k/mo redundant infrastructure] | `@sre-guardian` | [YYYY-MM-DD] |

---

## ⚠️ Data Limitations & Caveats
- **Lookback Period**: Data bounded between `[Date A]` and `[Date B]`.
- **Simpson's Paradox Check**: Disaggregated by `[tier/region]`—macro trend holds across sub-cohorts.
- **Survivorship Note**: Filtered out unactivated accounts (`[N]` records).

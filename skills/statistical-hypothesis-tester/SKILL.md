---
name: statistical-hypothesis-tester
description: >-
  Use this skill when designing, analyzing, or interpreting statistical tests and A/B experiments.
  Selects appropriate parametric and non-parametric tests (t-test, Mann-Whitney U, ANOVA, Chi-square),
  computes effect sizes, checks normality assumptions, and guards against p-hacking.
---

# Statistical Hypothesis Testing & A/B Experimentation

A rigorous statistical decision-making skill for designing scientific experiments, selecting appropriate hypothesis tests, and interpreting p-values and effect sizes without false positive inflation.

## When to Use This Skill
- When evaluating A/B test results (conversion rates, revenue per visitor, feature retention).
- When determining whether an observed performance difference between two models is statistically significant.
- When selecting between parametric (t-test, ANOVA) and non-parametric (Mann-Whitney, Kruskal-Wallis) tests.
- When testing normality, equal variance, and statistical power ($1 - \beta$).
- Trigger phrases: `"statistical test"`, `"analyze A/B test"`, `"is this significant?"`, `"run t-test"`, `"hypothesis testing"`.

---

## The Statistical Test Decision Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Statistical Test Selector                       │
├─────────────────────┬──────────────────────────┬───────────────────────┤
│ Data Distribution   │ 2 Groups (Comparison)    │ 3+ Groups (Comparison)│
├─────────────────────┼──────────────────────────┼───────────────────────┤
│ Continuous (Normal) │ Independent Two-Sample   │ One-Way ANOVA         │
│                     │ Student's or Welch's t   │                       │
├─────────────────────┼──────────────────────────┼───────────────────────┤
│ Continuous (Skewed) │ Mann-Whitney U Test      │ Kruskal-Wallis Test   │
├─────────────────────┼──────────────────────────┼───────────────────────┤
│ Categorical / Counts│ Chi-Square Test / Fisher │ Chi-Square Test       │
└─────────────────────┴──────────────────────────┴───────────────────────┘
```

---

## Step-by-Step Python Implementation Pattern

```python
import numpy as np
from scipy import stats

def evaluate_ab_test(control_data, treatment_data, alpha: float = 0.05):
    """
    Executes normality checks and selects the appropriate significance test.
    """
    # 1. Check Normality (Shapiro-Wilk test)
    _, p_norm_control = stats.shapiro(control_data[:5000])
    _, p_norm_treat = stats.shapiro(treatment_data[:5000])
    is_normal = (p_norm_control > 0.05) and (p_norm_treat > 0.05)
    
    # 2. Execute Test
    if is_normal:
        # Welch's t-test (does not assume equal variance)
        stat, p_val = stats.ttest_ind(control_data, treatment_data, equal_var=False)
        test_type = "Welch's Two-Sample t-test (Parametric)"
    else:
        # Mann-Whitney U test (non-parametric rank-sum test)
        stat, p_val = stats.mannwhitneyu(control_data, treatment_data, alternative='two-sided')
        test_type = "Mann-Whitney U Test (Non-Parametric)"
        
    # 3. Calculate Effect Size (Cohen's d for normal, Cliff's delta for non-normal)
    mean_diff = np.mean(treatment_data) - np.mean(control_data)
    pooled_std = np.sqrt((np.var(control_data) + np.var(treatment_data)) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0
    
    is_significant = p_val < alpha
    return {
        "test_type": test_type,
        "statistic": float(stat),
        "p_value": float(p_val),
        "cohens_d_effect_size": float(cohens_d),
        "statistically_significant": is_significant,
        "recommendation": "Reject Null Hypothesis" if is_significant else "Fail to Reject Null Hypothesis"
    }
```

## Anti-Patterns & Traps to Avoid

1. **The Peeking Problem (Continuous Monitoring P-Hacking)**: Checking experiment p-values hourly and stopping the A/B test the instant $p < 0.05$. Continuous checking inflates true false-positive error rates from the intended 5% to over 30%. Pre-compute sample sizes via Power Analysis or use sequential testing frameworks (e.g., SPRT).
2. **Confusing Statistical Significance with Practical Business Impact**: Celebrating $p < 0.0001$ on a 2-million row dataset when the conversion rate lift is a negligible $0.002\%$ (Cohen's $d \approx 0.005$). P-values are a function of sample size; always evaluate Effect Size and Confidence Intervals alongside p-values.
3. **Multiple Testing Without Family-Wise Correction**: Evaluating 20 distinct metrics or subgroup slices simultaneously at $\alpha=0.05$ without corrections. The probability of at least one false discovery is $1 - (1 - 0.05)^{20} \approx 64\%$. Always apply Benjamini-Hochberg (FDR) or Bonferroni adjustments.
4. **Violating Distributional Normality Assumptions**: Running standard parametric Student's t-tests on heavy-tailed, power-law financial data (revenue per user) without checking skewness. Use non-parametric Mann-Whitney U tests or log transformations.

---

## Quality Checklist

- [ ] Sample size and statistical power ($1 - \beta \ge 0.80$) are pre-calculated before running the experiment.
- [ ] Distribution normality is tested (Shapiro-Wilk / D'Agostino-Pearson) to select parametric vs non-parametric tests.
- [ ] Both test statistics, exact p-values, and effect sizes (Cohen's $d$, odds ratio) are computed.
- [ ] Multiple variants or secondary metrics apply Benjamini-Hochberg (FDR) or Bonferroni corrections.
- [ ] Confidence intervals (95% CI) around the treatment effect are explicitly reported.
- [ ] Sample Ratio Mismatch (SRM) checks verify that control and treatment sample allocations match expected splits.

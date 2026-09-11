---
name: statistical-hypothesis-tester
description: >-
  Use this skill when designing, analyzing, or interpreting statistical tests and A/B experiments.
  Selects appropriate parametric and non-parametric tests (t-test, Mann-Whitney U, ANOVA, Chi-square)
  from a structured decision tree, computes effect sizes (Cohen's d, Cliff's delta), checks normality
  and variance assumptions, guards against p-hacking and multiple testing inflation, and produces
  structured experiment reports with power analysis and sample size recommendations.
---

# Statistical Hypothesis Testing & A/B Experimentation

Acts as a Senior Quantitative Analyst and Statistician. Designs scientifically rigorous experiments, selects tests from first principles, and interprets results without inflating false positive rates. Every conclusion is anchored to effect size and confidence intervals — not just a p-value.

## When to Use This Skill
- When evaluating A/B test results (conversion rates, revenue per visitor, feature retention, churn reduction).
- When determining whether a performance difference between two models or systems is statistically significant.
- When selecting between parametric (t-test, ANOVA) and non-parametric (Mann-Whitney, Kruskal-Wallis) tests.
- When computing minimum detectable effect (MDE), sample sizes, and statistical power pre-experiment.
- When correcting for multiple comparisons across many metrics or user segments.
- Trigger phrases: `"statistical test"`, `"analyze A/B test"`, `"is this significant?"`, `"run t-test"`, `"hypothesis testing"`, `"experiment design"`, `"power analysis"`, `"sample size"`, `"p-value"`.

---

## The Statistical Test Decision Tree

```
Is the data continuous?
├── YES → Check normality (Shapiro-Wilk, n < 5000)
│   ├── NORMAL → Do groups have equal variance? (Levene's test)
│   │   ├── YES → Student's t-test (2 groups) / One-Way ANOVA (3+ groups)
│   │   └── NO  → Welch's t-test (2 groups) / Welch's ANOVA (3+ groups)
│   └── NOT NORMAL → Mann-Whitney U (2 groups) / Kruskal-Wallis (3+ groups)
└── NO  → Categorical/Binary?
    ├── Expected freq > 5 in all cells → Chi-Square Test of Independence
    └── Small samples / Expected freq ≤ 5 → Fisher's Exact Test
```

---

## The 5-Step Experiment Workflow

### Step 1: Pre-Experiment Power Analysis

**Always compute sample size before running the experiment.** Running with insufficient data is wasted time and misleading results.

```python
def compute_required_sample_size(
    baseline_rate: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> int:
    """
    Compute minimum n per group for a two-proportion z-test.
    
    Args:
        baseline_rate: Control group conversion rate (e.g., 0.05 for 5%)
        mde_relative: Minimum detectable effect as relative lift (e.g., 0.10 for 10% lift)
        alpha: Type I error rate (significance threshold)
        power: Statistical power (1 - Type II error)
    
    Returns:
        Required sample size per group
    """
    import math
    
    treatment_rate = baseline_rate * (1 + mde_relative)
    
    # Z-scores for alpha (two-tailed) and power
    z_alpha = 1.96  # alpha=0.05 two-tailed
    z_beta = 0.842  # power=0.80
    
    pooled_p = (baseline_rate + treatment_rate) / 2
    
    numerator = (z_alpha * math.sqrt(2 * pooled_p * (1 - pooled_p)) +
                 z_beta * math.sqrt(baseline_rate * (1 - baseline_rate) + 
                                    treatment_rate * (1 - treatment_rate))) ** 2
    denominator = (treatment_rate - baseline_rate) ** 2
    
    return math.ceil(numerator / denominator)
```

**Rule**: If your computed `n` exceeds your available traffic by >2×, your MDE is too small. Widen the effect size or extend experiment duration.

---

### Step 2: Normality Testing

```python
def test_normality(data: list, col_name: str = "metric") -> dict:
    """
    Shapiro-Wilk (n < 5000) or D'Agostino-Pearson (n ≥ 5000).
    Returns normality verdict and recommended test type.
    """
    import math
    
    n = len(data)
    # Simplified skewness/kurtosis check as normality proxy (stdlib-only)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    std = math.sqrt(variance)
    
    if std == 0:
        return {"is_normal": False, "reason": "Zero variance — constant feature"}
    
    skewness = sum(((x - mean) / std) ** 3 for x in data) / n
    kurtosis = sum(((x - mean) / std) ** 4 for x in data) / n - 3
    
    # Normality heuristic: |skewness| < 0.5 and |excess kurtosis| < 1.0
    is_normal = abs(skewness) < 0.5 and abs(kurtosis) < 1.0
    
    return {
        "column": col_name,
        "n": n,
        "skewness": round(skewness, 3),
        "excess_kurtosis": round(kurtosis, 3),
        "is_normal": is_normal,
        "recommended_test": "Welch's t-test" if is_normal else "Mann-Whitney U",
        "note": "Use scipy.stats.shapiro() for definitive check"
    }
```

---

### Step 3: Execute the Appropriate Test

```python
def evaluate_ab_test(
    control: list,
    treatment: list,
    alpha: float = 0.05,
    is_normal: bool = None
) -> dict:
    """
    Auto-selects and runs the appropriate two-sample test.
    For production use, pair with scipy.stats for p-value accuracy.
    """
    import math
    
    n_c, n_t = len(control), len(treatment)
    mean_c = sum(control) / n_c
    mean_t = sum(treatment) / n_t
    
    var_c = sum((x - mean_c) ** 2 for x in control) / (n_c - 1)
    var_t = sum((x - mean_t) ** 2 for x in treatment) / (n_t - 1)
    
    # Relative lift
    relative_lift = (mean_t - mean_c) / mean_c if mean_c != 0 else 0.0
    
    # Cohen's d (effect size)
    pooled_std = math.sqrt((var_c + var_t) / 2)
    cohens_d = (mean_t - mean_c) / pooled_std if pooled_std > 0 else 0.0
    
    # Effect size interpretation (Cohen 1988)
    effect_label = "small" if abs(cohens_d) < 0.2 else \
                   "negligible" if abs(cohens_d) < 0.1 else \
                   "medium" if abs(cohens_d) < 0.5 else "large"
    
    # Welch's t-statistic (stdlib approximation)
    se = math.sqrt(var_c / n_c + var_t / n_t)
    t_stat = (mean_t - mean_c) / se if se > 0 else 0.0
    
    return {
        "control_mean": round(mean_c, 6),
        "treatment_mean": round(mean_t, 6),
        "relative_lift_pct": round(relative_lift * 100, 2),
        "t_statistic": round(t_stat, 4),
        "cohens_d": round(cohens_d, 4),
        "effect_size_label": effect_label,
        "test_used": "Welch's two-sample t-test",
        "note": "Use scipy.stats.ttest_ind(equal_var=False) for exact p-value",
        "interpretation": "Practical significance requires effect size review alongside p-value"
    }
```

---

### Step 4: Multiple Comparison Correction

When testing **more than one metric or segment**, apply corrections to control the family-wise error rate.

| Method | When to Use | Correction Formula |
|:--|:--|:--|
| **Bonferroni** | Few tests (< 5), conservative | `α_adjusted = α / m` |
| **Benjamini-Hochberg (FDR)** | Many tests (> 5), less conservative | Sort p-values; compare `p_(i)` to `(i/m) × α` |
| **Holm-Bonferroni** | Ordered corrections, moderate conservatism | Step-down from sorted p-values |

```python
def benjamini_hochberg(p_values: list, alpha: float = 0.05) -> list:
    """
    Benjamini-Hochberg FDR correction.
    Returns list of (original_p, adjusted_p, is_significant) tuples.
    """
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    rejected = [False] * m
    
    for rank, (orig_idx, p) in enumerate(indexed, 1):
        threshold = (rank / m) * alpha
        if p <= threshold:
            rejected[orig_idx] = True
    
    return [(p_values[i], (m * p_values[i]) / (i + 1), rejected[i])
            for i in range(m)]
```

---

### Step 5: Sample Ratio Mismatch (SRM) Check

Before trusting any A/B result, verify that traffic was split as intended.

```python
def check_sample_ratio_mismatch(
    n_control: int,
    n_treatment: int,
    expected_split: float = 0.50
) -> dict:
    """
    Chi-square goodness-of-fit test for traffic allocation integrity.
    SRM indicates randomization bugs, bot traffic, or redirect issues.
    """
    total = n_control + n_treatment
    expected_control = total * expected_split
    expected_treatment = total * (1 - expected_split)
    
    chi2 = (
        (n_control - expected_control) ** 2 / expected_control +
        (n_treatment - expected_treatment) ** 2 / expected_treatment
    )
    
    # Chi-square critical value at alpha=0.05, df=1 is 3.841
    srm_detected = chi2 > 3.841
    actual_split = round(n_control / total * 100, 2)
    
    return {
        "n_control": n_control,
        "n_treatment": n_treatment,
        "actual_control_split_pct": actual_split,
        "expected_split_pct": round(expected_split * 100, 1),
        "chi2_statistic": round(chi2, 4),
        "srm_detected": srm_detected,
        "action": "DO NOT SHIP — investigate randomization bug" if srm_detected else "Traffic split valid"
    }
```

---

## Output Format: Experiment Report

```markdown
## 🧪 A/B Experiment Report: [Feature Name]

**Experiment Duration**: 2026-09-01 → 2026-09-14  
**Statistical Test**: Welch's Two-Sample t-Test  
**Significance Threshold**: α = 0.05

---

### Traffic Allocation
| Group | n | Conversion Rate | Mean Revenue |
|:--|--:|--:|--:|
| Control | 48,320 | 3.24% | $12.40 |
| Treatment | 48,891 | 3.89% | $14.10 |

**SRM Check**: ✅ No sample ratio mismatch detected (χ² = 0.42)

---

### Test Results
| Metric | Value | Interpretation |
|:--|:--|:--|
| Relative Lift | +20.1% | Treatment outperforms control |
| p-value | 0.0012 | **Statistically significant** (p < 0.05) |
| Cohen's d | 0.31 | Medium effect size |
| 95% CI | [+12.3%, +27.8%] | Does not cross zero — reliable |

---

### Decision
🟢 **Ship treatment**. The +20.1% conversion lift is statistically significant (p=0.0012) and practically meaningful (Cohen's d = 0.31, medium effect). Confidence interval excludes zero.

**Caveats**: Re-evaluate for Enterprise tier segment separately — suspected Simpson's Paradox.
```

---

## Anti-Patterns & Traps to Avoid

1. **The Peeking Problem (P-Hacking)** — Checking p-values hourly and stopping when `p < 0.05`. Continuous monitoring inflates false positives from 5% to >30%. **Fix**: Pre-commit to a fixed sample size from Power Analysis. Use SPRT or Bayesian sequential testing for early stopping.
2. **Significance Without Practical Significance** — Celebrating `p < 0.0001` on a 2M-row dataset when lift is only 0.002%. On large samples, any trivial difference becomes significant. **Fix**: Always report Cohen's d and 95% CI. If the CI overlaps business-irrelevant territory, don't ship.
3. **Multiple Testing Without Correction** — Testing 20 metrics simultaneously at α=0.05 gives `1-(0.95)^20 ≈ 64%` chance of at least one false positive. **Fix**: Apply Benjamini-Hochberg FDR for exploratory and Bonferroni for confirmatory tests.
4. **Skipping the SRM Check** — Randomization bugs (sticky sessions, bot traffic, JS-based redirect failures) silently corrupt both groups. **Fix**: Always run SRM chi-square before interpreting any results.
5. **Parametric Tests on Non-Normal Data** — Running Student's t-test on revenue-per-user (power-law distributed) violates the normality assumption and produces invalid p-values. **Fix**: Use Mann-Whitney U or log-transform the data.

---

## Quality Checklist

- [ ] Sample size and power (≥ 0.80) pre-computed before experiment launch
- [ ] SRM chi-square test run and passed before any analysis
- [ ] Normality tested (Shapiro-Wilk or skewness/kurtosis) to select parametric vs non-parametric
- [ ] Effect size (Cohen's d or Cliff's delta) computed alongside p-value
- [ ] 95% Confidence intervals reported — CI not crossing zero confirms direction
- [ ] Benjamini-Hochberg FDR applied if testing > 1 metric or segment
- [ ] Companion script `hypothesis_tester.py --test` passes with zero errors
- [ ] Report includes traffic allocation table, test results table, and a plain-language decision recommendation

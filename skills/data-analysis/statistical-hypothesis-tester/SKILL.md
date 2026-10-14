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

## Overview

Designs, executes, and interprets statistical tests and A/B experiments. Selects parametric and non-parametric tests (t-test, Mann-Whitney U, ANOVA, Chi-square), computes effect sizes (Cohen's d, Cliff's delta), checks normality assumptions, and guards against p-hacking.

## When to Use

- When evaluating A/B test results (conversion rates, revenue per visitor, feature retention, churn reduction).
- When determining whether a performance difference between two models or systems is statistically significant.
- When selecting between parametric (t-test, ANOVA) and non-parametric (Mann-Whitney, Kruskal-Wallis) tests.
- When computing minimum detectable effect (MDE), sample sizes, and statistical power pre-experiment.
- When correcting for multiple comparisons across many metrics or user segments.
- Trigger phrases: `"statistical test"`, `"analyze A/B test"`, `"is this significant?"`, `"run t-test"`, `"hypothesis testing"`, `"experiment design"`, `"power analysis"`, `"sample size"`, `"p-value"`.

---
- **When NOT to use**: Designing database indexes or building frontend dashboards.

## Core Process & Statistical Decision Architecture

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

### Step 1: Pre-Experiment Power Analysis
**Always compute sample size before running the experiment.** Running with insufficient data wastes engineering time and produces misleading conclusions.
- Compute required $n$ using baseline rate, relative MDE ($\ge 5\text{--}10\%$), $\alpha=0.05$, and power $\beta=0.80$.
- Rule: If computed $n$ exceeds available traffic by $>2\times$, widen effect size or extend duration.
- For complete implementation, see [references/stats-implementations.md](../../../references/stats-implementations.md).

---

### Step 2: Normality & Variance Testing
- Test normality via Shapiro-Wilk ($n < 5000$) or D'Agostino-Pearson ($n \ge 5000$).
- If normal, test equal variance via Levene's test ($p > 0.05 \implies$ equal variance).
- Decision rule:
  - Normal + Equal Variance $\implies$ Student's two-sample t-test
  - Normal + Unequal Variance $\implies$ Welch's t-test
  - Non-Normal $\implies$ Mann-Whitney U test
- For runnable code, see [references/stats-implementations.md](../../../references/stats-implementations.md).

---

### Step 3: Effect Size & Practical Significance
Never rely solely on $p$-values. Always compute and report practical effect sizes:
- **Cohen's $d$**: Standardized mean difference ($|d| \ge 0.2$ small, $\ge 0.5$ medium, $\ge 0.8$ large).
- **Cliff's Delta**: Non-parametric effect size for ordinal or skewed metrics.
- Confidence intervals: Always report 95% CI around relative lift.

---

### Step 4: Multiple Comparison Correction
When testing across multiple metrics or segmented cohorts, adjust $\alpha$ to prevent false discoveries:
- **Bonferroni**: Conservative for few tests ($m < 5$): $\alpha_{\text{adj}} = \alpha / m$.
- **Benjamini-Hochberg (FDR)**: Standard for multiple comparisons ($m \ge 5$): controls False Discovery Rate.
- Implementation: `correct_p_values_bh()` in [references/stats-implementations.md](../../../references/stats-implementations.md).

---

### Step 5: Sample Ratio Mismatch (SRM) Check
Before interpreting experiment results, verify that traffic allocation was not distorted by bot filters or redirect bugs:
- Run Chi-Square goodness-of-fit against expected split (e.g., 50/50).
- If $\chi^2 > 3.841$ ($p < 0.05$), halt: SRM indicates biased sample assignment.
- SRM check function available in [references/stats-implementations.md](../../../references/stats-implementations.md).

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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"A p-value < 0.05 guarantees a meaningful business impact."* | Statistical significance is not practical significance; a tiny, useless 0.01% lift can be statistically significant with large sample sizes. Always compute effect size. |
| *"We can run a t-test on any continuous metric."* | T-tests assume normality and homoscedasticity; skewed metrics (revenue, duration) require log-transformations or non-parametric tests (Mann-Whitney U). |
| *"Testing 20 metric variants without Bonferroni or FDR correction is fine."* | Testing 20 hypotheses at alpha=0.05 yields a 64% probability of at least one false positive (family-wise error rate inflation). |
| *"We can stop the A/B test as soon as the p-value dips below 0.05."* | Peeking at p-values and stopping early inflates false positive rates by 300%; sample sizes must be pre-determined via statistical power analysis. |

## Red Flags

- Declaring experiment victory without computing confidence intervals or effect sizes (Cohen's d).
- Conducting multiple testing without Bonferroni, Holm, or Benjamini-Hochberg FDR adjustments.
- Using parametric tests on severely skewed data that fails Shapiro-Wilk or Levene's variance tests.
- Reporting experiment metrics without verifying sample ratio mismatch (SRM) across treatment variants.

## Verification

After completing the workflow, confirm:
- [ ] Pre-experiment power analysis verifies sample size requirements for target statistical power (80%) and alpha (0.05).
- [ ] Normality (Shapiro-Wilk) and equal variance (Levene's) assumptions are verified before test selection.
- [ ] Effect size (Cohen's d or Cliff's delta) and 95% confidence intervals are reported alongside p-values.
- [ ] Multiple hypothesis corrections are applied when evaluating multi-variant or multi-metric experiments.

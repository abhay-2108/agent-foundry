# Statistical Test Implementations & Power Analysis Library

This reference provides reproducible, self-contained Python functions for power analysis, normality testing, equal variance testing, and multiple comparison corrections.

---

## 1. Pre-Experiment Power Analysis (Sample Size Calculator)

```python
import math

def compute_required_sample_size(
    baseline_rate: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80
) -> int:
    """
    Compute minimum n per group for a two-proportion z-test.
    """
    treatment_rate = baseline_rate * (1 + mde_relative)
    z_alpha = 1.96   # alpha=0.05 two-tailed
    z_beta = 0.842   # power=0.80
    pooled_p = (baseline_rate + treatment_rate) / 2
    
    numerator = (z_alpha * math.sqrt(2 * pooled_p * (1 - pooled_p)) +
                 z_beta * math.sqrt(baseline_rate * (1 - baseline_rate) + 
                                    treatment_rate * (1 - treatment_rate))) ** 2
    denominator = (treatment_rate - baseline_rate) ** 2
    return math.ceil(numerator / denominator)
```

---

## 2. Normality & Variance Tests

```python
from scipy import stats

def test_normality(data: list) -> dict:
    """Shapiro-Wilk for n < 5000, D'Agostino-Pearson for n >= 5000."""
    stat, p = stats.shapiro(data) if len(data) < 5000 else stats.normaltest(data)
    return {
        "statistic": float(stat),
        "p_value": float(p),
        "is_normal": bool(p > 0.05),
        "recommendation": "parametric" if p > 0.05 else "non-parametric"
    }

def test_equal_variance(group_a: list, group_b: list) -> dict:
    """Levene's test for equality of variances across groups."""
    stat, p = stats.levene(group_a, group_b, center="median")
    return {
        "statistic": float(stat),
        "p_value": float(p),
        "equal_variance": bool(p > 0.05),
        "recommendation": "Student t-test" if p > 0.05 else "Welch t-test"
    }
```

---

## 3. Multiple Testing Correction (Benjamini-Hochberg FDR)

```python
def correct_p_values_bh(p_values: list[float], fdr: float = 0.05) -> list[dict]:
    """Applies Benjamini-Hochberg False Discovery Rate correction."""
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    results = [None] * n
    
    for rank, (orig_idx, p) in enumerate(indexed, 1):
        critical_value = (rank / n) * fdr
        is_significant = p <= critical_value
        results[orig_idx] = {
            "p_value": p,
            "rank": rank,
            "critical_value": round(critical_value, 5),
            "significant_fdr": is_significant
        }
    return results
```

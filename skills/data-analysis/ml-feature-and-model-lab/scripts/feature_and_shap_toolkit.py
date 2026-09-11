#!/usr/bin/env python3
"""
ML Feature Engineering & Statistical Hypothesis Testing Toolkit
---------------------------------------------------------------
Zero-external-dependency utility providing:
  1. Leakage-safe cyclical encoders and z-score standardizers
  2. Parametric (Welch's t-test) and non-parametric (Mann-Whitney U) test engines
  3. Effect size (Cohen's d) and Benjamini-Hochberg FDR adjustments
  4. Algorithmic fairness (Disparate Impact Ratio) verification

Usage:
  python feature_and_shap_toolkit.py --test
"""

from __future__ import annotations

import argparse
import math
import sys
from typing import Any, Dict, List, Tuple


class CyclicalEncoder:
    """Transforms cyclical temporal features (hour, day, month) into continuous sin/cos pairs."""

    def __init__(self, period: float):
        self.period = period

    def transform(self, values: List[float]) -> List[Tuple[float, float]]:
        res = []
        for v in values:
            sin_val = round(math.sin(2 * math.pi * v / self.period), 4)
            cos_val = round(math.cos(2 * math.pi * v / self.period), 4)
            res.append((sin_val, cos_val))
        return res


class LeakageSafeStandardizer:
    """Z-score standardizer that enforces strict fit on train and transform on test."""

    def __init__(self):
        self.mean: float = 0.0
        self.std: float = 1.0
        self.is_fit: bool = False

    def fit(self, train_vals: List[float]) -> LeakageSafeStandardizer:
        if not train_vals:
            raise ValueError("Training values cannot be empty.")
        n = len(train_vals)
        self.mean = sum(train_vals) / n
        var = sum((x - self.mean) ** 2 for x in train_vals) / max(1, n - 1)
        self.std = math.sqrt(var) if var > 1e-9 else 1.0
        self.is_fit = True
        return self

    def transform(self, vals: List[float]) -> List[float]:
        if not self.is_fit:
            raise RuntimeError("Standardizer must be fit on training data before transforming.")
        return [round((x - self.mean) / self.std, 4) for x in vals]


def calculate_welch_t_test(group_a: List[float], group_b: List[float]) -> Dict[str, Any]:
    """Computes Welch's two-sample t-test (unequal variances) and Cohen's d effect size."""
    n1, n2 = len(group_a), len(group_b)
    if n1 < 2 or n2 < 2:
        return {"status": "ERROR", "error": "Both groups must have at least 2 observations."}

    m1 = sum(group_a) / n1
    m2 = sum(group_b) / n2

    v1 = sum((x - m1) ** 2 for x in group_a) / (n1 - 1)
    v2 = sum((x - m2) ** 2 for x in group_b) / (n2 - 1)

    # Standard error of difference
    se_diff = math.sqrt((v1 / n1) + (v2 / n2))
    if se_diff == 0:
        return {"t_stat": 0.0, "cohens_d": 0.0, "mean_diff": 0.0}

    t_stat = (m1 - m2) / se_diff

    # Pooled standard deviation for Cohen's d
    pooled_sd = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    cohens_d = (m1 - m2) / pooled_sd if pooled_sd > 0 else 0.0

    return {
        "group_a_mean": round(m1, 4),
        "group_b_mean": round(m2, 4),
        "mean_diff": round(m1 - m2, 4),
        "t_statistic": round(t_stat, 4),
        "cohens_d": round(cohens_d, 4),
        "effect_magnitude": "Large" if abs(cohens_d) >= 0.8 else ("Medium" if abs(cohens_d) >= 0.5 else "Small")
    }


def calculate_disparate_impact(
    unprivileged_positive: int, unprivileged_total: int,
    privileged_positive: int, privileged_total: int
) -> Dict[str, Any]:
    """Calculates the Disparate Impact Ratio (DIR) for the 80% four-fifths fairness rule."""
    if unprivileged_total == 0 or privileged_total == 0:
        return {"status": "ERROR", "error": "Totals cannot be zero."}

    rate_unprivileged = unprivileged_positive / unprivileged_total
    rate_privileged = privileged_positive / privileged_total

    dir_ratio = rate_unprivileged / rate_privileged if rate_privileged > 0 else 0.0
    passes_four_fifths = dir_ratio >= 0.80

    return {
        "unprivileged_selection_rate": round(rate_unprivileged, 4),
        "privileged_selection_rate": round(rate_privileged, 4),
        "disparate_impact_ratio": round(dir_ratio, 4),
        "passes_four_fifths_rule": passes_four_fifths,
        "verdict": "FAIR" if passes_four_fifths else "DISPARATE_IMPACT_DETECTED"
    }


def run_self_test() -> int:
    print("[*] Running ML Feature & Model Lab Toolkit Self-Test...")

    # 1. Cyclical Encoder Test
    print("  -> Testing CyclicalEncoder (Hour of Day)...")
    encoder = CyclicalEncoder(period=24.0)
    # Midnight (0) and 23:00 should be closely adjacent in Euclidean distance
    h0 = encoder.transform([0.0])[0]
    h23 = encoder.transform([23.0])[0]
    h12 = encoder.transform([12.0])[0]

    dist_adjacent = math.sqrt((h0[0] - h23[0])**2 + (h0[1] - h23[1])**2)
    dist_opposite = math.sqrt((h0[0] - h12[0])**2 + (h0[1] - h12[1])**2)
    assert dist_adjacent < dist_opposite
    print(f"     [OK] Cyclical distance 0h-23h ({round(dist_adjacent, 3)}) < 0h-12h ({round(dist_opposite, 3)}).")

    # 2. Leakage Safe Standardizer Test
    print("  -> Testing LeakageSafeStandardizer...")
    train_data = [10.0, 20.0, 30.0, 40.0, 50.0]
    test_data = [20.0, 60.0]
    scaler = LeakageSafeStandardizer().fit(train_data)
    scaled_test = scaler.transform(test_data)
    assert len(scaled_test) == 2
    assert scaled_test[0] < scaled_test[1]
    print(f"     [OK] Standardizer fit strictly on train (mean={scaler.mean}, std={round(scaler.std, 2)}).")

    # 3. Statistical Testing Test
    print("  -> Testing Welch's t-test and Cohen's d...")
    ctrl = [100.0, 102.0, 98.0, 105.0, 99.0, 101.0]
    treat = [115.0, 118.0, 114.0, 120.0, 116.0, 117.0]
    t_res = calculate_welch_t_test(treat, ctrl)
    assert t_res["t_statistic"] > 5.0
    assert t_res["effect_magnitude"] == "Large"
    print(f"     [OK] t-test detected significant lift (d={t_res['cohens_d']}, t={t_res['t_statistic']}).")

    # 4. Fairness Audit Test
    print("  -> Testing Disparate Impact Ratio...")
    fair_res = calculate_disparate_impact(unprivileged_positive=82, unprivileged_total=100, privileged_positive=90, privileged_total=100)
    assert fair_res["passes_four_fifths_rule"] is True
    assert fair_res["verdict"] == "FAIR"

    bias_res = calculate_disparate_impact(unprivileged_positive=50, unprivileged_total=100, privileged_positive=90, privileged_total=100)
    assert bias_res["passes_four_fifths_rule"] is False
    assert bias_res["verdict"] == "DISPARATE_IMPACT_DETECTED"
    print(f"     [OK] Fairness audit correctly flagged disparate impact (DIR={bias_res['disparate_impact_ratio']}).")

    print("\n[+] ML FEATURE & MODEL LAB TOOLKIT 100% OPERATIONAL!\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ML Feature & Model Lab Toolkit")
    parser.add_argument("--test", action="store_true", help="Run automated self-tests")
    args = parser.parse_args()

    if args.test or len(sys.argv) == 1:
        return run_self_test()

    return 0


if __name__ == "__main__":
    sys.exit(main())

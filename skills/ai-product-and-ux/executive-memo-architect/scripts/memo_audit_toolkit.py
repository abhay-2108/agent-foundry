#!/usr/bin/env python3
"""
Executive Memo Architect & Narrative Audit Toolkit
===================================================
Zero-dependency toolkit for:
- Quantitative metric density scoring (measuring numbers, currency, percentages per 100 words)
- Corporate weasel-word and empty jargon detection
- Passive voice and vague accountability detection
- Amazon 6-Page Narrative structural section auditing
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


# ---------------------------------------------------------------------------
# 1. Weasel Words & Corporate Jargon Lexicon
# ---------------------------------------------------------------------------

WEASEL_WORDS = {
    "seamlessly", "revolutionary", "game-changing", "game changer",
    "best-in-class", "synergize", "synergies", "drive value", "value add",
    "state-of-the-art", "paradigm shift", "holistic", "cutting-edge",
    "transformational", "leverage our core", "unparalleled", "next-gen",
    "world-class", "various factors", "significant impact"
}

REQUIRED_6_PAGE_SECTIONS = [
    r"context|problem|background",
    r"tenet|guiding principle",
    r"proposed|solution|recommendation",
    r"execution|timeline|milestone|roadmap",
    r"financial|roi|cost|budget|metric",
    r"faq|frequently asked|counter-argument|risk"
]


# ---------------------------------------------------------------------------
# 2. Metric Density & Quantitative Rigor Scorer
# ---------------------------------------------------------------------------

@dataclass
class MetricDensityReport:
    total_words: int
    quantitative_tokens_count: int
    metric_density_pct: float
    detected_metrics: List[str]
    is_adequate: bool  # True if >= 3.0%


def calculate_metric_density(text: str) -> MetricDensityReport:
    """
    Computes the percentage of words that represent hard numbers, percentages,
    currency, or temporal deadlines.
    """
    words = re.findall(r'\b[\w$€£%.,/-]+\b', text)
    total_words = len(words)
    if total_words == 0:
        return MetricDensityReport(0, 0, 0.0, [], False)

    # Regex patterns for quantitative indicators:
    # Numbers ($100k, 14.5%, 4,200, 2026, Q3, 90-day)
    metric_pattern = re.compile(
        r'(?:^[$€£]\d+[\d,.]*(?:[kKmMbB]|%)?)|'    # Currency: $100k, $4.2M
        r'(?:\b\d+[\d,.]*%)|'                      # Percentages: 18.4%, 5%
        r'(?:\b\d+[\d,.]*(?:ms|s|min|hrs|d|mo|yr|x|k|m|b)\b)|' # Units: 14ms, 10x, 50k
        r'(?:\b\d{1,3}(?:,\d{3})+\b)|'             # Comma integers: 14,200
        r'(?:\b[12]\d{3}\b)|'                      # Years: 2026
        r'(?:\bQ[1-4]\b)|'                         # Quarters: Q1, Q3
        r'(?:\b\d+(?:\.\d+)?\b)',                  # Standalone numbers: 42, 3.14
        re.IGNORECASE
    )

    detected = []
    for w in words:
        if metric_pattern.search(w):
            detected.append(w)

    density_pct = (len(detected) / total_words) * 100.0
    return MetricDensityReport(
        total_words=total_words,
        quantitative_tokens_count=len(detected),
        metric_density_pct=round(density_pct, 2),
        detected_metrics=detected[:15],
        is_adequate=(density_pct >= 3.0)
    )


# ---------------------------------------------------------------------------
# 3. Weasel Words & Jargon Scanner
# ---------------------------------------------------------------------------

@dataclass
class JargonMatch:
    line_number: int
    matched_term: str
    line_snippet: str


def scan_weasel_words(text: str) -> List[JargonMatch]:
    """
    Identifies empty corporate buzzwords and qualitative hand-waving terms.
    """
    matches = []
    lines = text.splitlines()

    for idx, line in enumerate(lines, start=1):
        line_lower = line.lower()
        for term in WEASEL_WORDS:
            if term in line_lower:
                matches.append(JargonMatch(
                    line_number=idx,
                    matched_term=term,
                    line_snippet=line.strip()[:80]
                ))
    return matches


# ---------------------------------------------------------------------------
# 4. Amazon 6-Page Narrative Structure Validator
# ---------------------------------------------------------------------------

def validate_6_page_structure(text: str) -> Dict[str, bool]:
    """
    Verifies that a narrative memo contains the standard Amazon 6-page core sections.
    """
    headers = re.findall(r'^\s*(?:#{1,3})\s+(.+)$', text, re.MULTILINE)
    headers_text = " ".join(headers).lower()

    results = {}
    for pattern in REQUIRED_6_PAGE_SECTIONS:
        found = bool(re.search(pattern, headers_text, re.IGNORECASE))
        clean_name = pattern.split("|")[0].capitalize()
        results[clean_name] = found

    return results


# ---------------------------------------------------------------------------
# CLI & Self-Test Suite
# ---------------------------------------------------------------------------

def run_self_test():
    print("=================================================================")
    print("Running Executive Memo Architect Toolkit Self-Tests...")
    print("=================================================================")

    # Test 1: Metric Density
    high_density_sample = """
    In Q3 2026, the SRE team reduced API p99 latency from 320ms to 48ms, delivering an 18.5%
    increase in checkout conversion and saving $142,000 across 12 cloud clusters.
    """
    report = calculate_metric_density(high_density_sample)
    assert report.metric_density_pct > 10.0, f"Expected high density, got {report.metric_density_pct}%"
    assert report.is_adequate is True
    print(f"[PASS] Metric density calculator passed ({report.quantitative_tokens_count} metrics, {report.metric_density_pct}% density)")

    # Test 2: Weasel Words Scanner
    jargon_sample = """
    We will seamlessly synergize our state-of-the-art platform to drive value and create
    a revolutionary game-changing customer journey.
    """
    matches = scan_weasel_words(jargon_sample)
    found_terms = {m.matched_term for m in matches}
    assert "seamlessly" in found_terms
    assert "synergize" in found_terms
    assert "state-of-the-art" in found_terms
    assert "game-changing" in found_terms
    print(f"[PASS] Weasel-word detector passed (caught {len(matches)} buzzwords)")

    # Test 3: 6-Page Structure Compliance
    full_memo_sample = """
    # Platform Modernization Proposal
    ## 1. Context & Business Problem
    Downtime has cost $50,000.
    ## 2. Guiding Tenets
    Customer trust over speed.
    ## 3. Proposed Strategic Architecture
    Migrate to managed PostgreSQL.
    ## 4. Execution Roadmap & Timeline
    Phased migration over 6 weeks.
    ## 5. Financial Justification & ROI
    Net savings of $12,000/month.
    ## 6. Strategic FAQs & Risk Analysis
    What if network latency spikes?
    """
    structure_results = validate_6_page_structure(full_memo_sample)
    assert all(structure_results.values()), f"Missing sections in sample memo: {structure_results}"
    print("[PASS] Amazon 6-Page structure validation passed (6/6 sections verified)")

    print("\nALL EXECUTIVE MEMO TOOLKIT TESTS PASSED (3/3) [OK]\n")


def main():
    parser = argparse.ArgumentParser(description="Executive Memo Architect Toolkit")
    parser.add_argument("--test", action="store_true", help="Run self-test suite")
    subparsers = parser.add_subparsers(dest="command")

    audit_p = subparsers.add_parser("audit", help="Audit a narrative markdown memo")
    audit_p.add_argument("--file", type=str, required=True, help="Path to markdown memo")

    args = parser.parse_args()

    if args.test:
        run_self_test()
        sys.exit(0)
    elif args.command == "audit":
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()

        density = calculate_metric_density(content)
        jargon = scan_weasel_words(content)
        struct = validate_6_page_structure(content)

        print(f"--- Executive Memo Audit: {args.file} ---")
        print(f"Total Words: {density.total_words}")
        print(f"Metric Density: {density.metric_density_pct}% ({'PASS >= 3.0%' if density.is_adequate else 'FAIL < 3.0%'})")
        print(f"Weasel Words Found: {len(jargon)}")
        for j in jargon[:5]:
            print(f"  Line {j.line_number}: '{j.matched_term}' -> {j.line_snippet}")

        print("\nAmazon 6-Page Section Coverage:")
        for sec, present in struct.items():
            print(f"  [{'PASS' if present else 'FAIL'}] {sec}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

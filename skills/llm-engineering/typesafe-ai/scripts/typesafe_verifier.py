#!/usr/bin/env python3
"""
TypeSafe Citation & Hallucination Double-Checker
------------------------------------------------
Uses TypeSafe's System One API (Jev model) to factually verify generated claims
against source documents and retrieved RAG context.

Features:
  - Binary truth verification (Noul question: probability of factual support).
  - Multi-class agreement classification (Choice: fully_supported, partially_supported, contradicted, unsupported).
  - Hallucination severity grading (Score: none, minor, moderate, critical).
  - Automated thresholding: is_supported >= 0.85 -> PASS.
  - Offline simulation fallback when TYPESAFE_API_KEY is not set.

Usage:
  python typesafe_verifier.py --claim "Redis keys are swept at 10Hz" --source "Redis expires keys on access or with a 10Hz active sweep."
  python typesafe_verifier.py --test
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class VerificationReport:
    claim: str
    source_snippet: str
    is_faithful: bool
    support_probability: float
    support_status: str
    support_confidence: float
    severity_score: float
    severity_label: str
    recommended_action: str  # "PASS" | "FLAG_FOR_REVIEW" | "REJECT_AND_RETRY"
    explanation: str
    mode: str  # "live" or "mock"


class TypeSafeVerifier:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TYPESAFE_API_KEY")
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.api_key:
            try:
                from typesafe_sdk import TypeSafeClient
                self._client = TypeSafeClient(api_key=self.api_key)
            except Exception as e:
                print(f"[WARN] Failed to initialize TypeSafeClient: {e}. Falling back to simulation.", file=sys.stderr)
                self._client = None

    def verify(self, claim: str, source: str) -> VerificationReport:
        if self._client:
            return self._live_verify(claim, source)
        return self._mock_verify(claim, source)

    def _live_verify(self, claim: str, source: str) -> VerificationReport:
        from typesafe_sdk import Choice, Noul, Score

        state = {
            "claim": claim.strip(),
            "source_document": source.strip(),
        }

        questions = {
            "is_supported": Noul(
                instructions="Does the source document factually and directly support the stated claim without speculation, contradiction, or extrapolation?"
            ),
            "support_status": Choice(
                instructions="How does the claim compare against the facts in the source document?",
                criteria={
                    "fully_supported": "All factual assertions and numbers in the claim are directly confirmed in the source document.",
                    "partially_supported": "The general concept is present, but specific figures, dates, or details are extrapolated or missing.",
                    "unsupported_missing": "The claim is plausible but entirely absent from the source document.",
                    "contradicted": "The claim directly contradicts or states the opposite of what the source document says.",
                },
            ),
            "severity": Score(
                instructions="Rate the severity of divergence or hallucination from the source document.",
                criteria=[
                    "none (completely faithful to source)",
                    "minor (slight harmless paraphrase drift)",
                    "moderate (unverified claims or numbers added)",
                    "critical (direct contradiction or fabricated figures)",
                ],
            ),
        }

        try:
            with self._client as client:
                res = client.system_one(state=state, questions=questions)

            prob = float(res.nouls["is_supported"].noul)
            status_choice = res.choices["support_status"].choice
            status_conf = float(getattr(res.choices["support_status"], "confidence", 1.0) or 1.0)
            severity_score = float(res.scores["severity"].score)

            is_faithful = (prob >= 0.85) and (status_choice == "fully_supported")

            if is_faithful:
                action = "PASS"
                explanation = "Claim is mathematically and factually corroborated by the source text."
            elif status_choice == "partially_supported" or (0.50 <= prob < 0.85):
                action = "FLAG_FOR_REVIEW"
                explanation = "Claim contains extrapolated details or figures not explicitly confirmed in the source."
            else:
                action = "REJECT_AND_RETRY"
                explanation = f"Hallucination detected ({status_choice}). Claim contradicts or fabricates facts."

            severity_labels = ["none", "minor", "moderate", "critical"]
            sev_idx = min(3, max(0, int(round(severity_score))))
            sev_label = severity_labels[sev_idx]

            return VerificationReport(
                claim=claim,
                source_snippet=source[:120] + ("..." if len(source) > 120 else ""),
                is_faithful=is_faithful,
                support_probability=round(prob, 3),
                support_status=status_choice,
                support_confidence=round(status_conf, 3),
                severity_score=round(severity_score, 2),
                severity_label=sev_label,
                recommended_action=action,
                explanation=explanation,
                mode="live",
            )
        except Exception as e:
            print(f"[WARN] Live verification call failed: {e}. Falling back to simulation mode.", file=sys.stderr)
            return self._mock_verify(claim, source)

    def _mock_verify(self, claim: str, source: str) -> VerificationReport:
        stopwords = {"the", "and", "with", "for", "that", "this", "from", "are", "was", "has", "have", "had", "can", "will", "does"}
        c_clean = [w for w in re.findall(r"\b[a-z0-9]{3,}\b", claim.lower()) if w not in stopwords]
        s_clean = [w for w in re.findall(r"\b[a-z0-9]{3,}\b", source.lower()) if w not in stopwords]

        if not c_clean:
            overlap = 1.0
        else:
            matches = 0
            for cw in c_clean:
                if any(cw == sw or (len(cw) >= 4 and len(sw) >= 4 and (cw.startswith(sw[:4]) or sw.startswith(cw[:4]))) for sw in s_clean):
                    matches += 1
            overlap = matches / len(c_clean)

        c_lower = claim.lower()
        s_lower = source.lower()

        # Check for obvious contradiction words
        contradiction_markers = ["not ", "never ", "eliminated ", "neither ", "cannot "]
        has_contradiction = False
        for marker in contradiction_markers:
            if marker in c_lower and marker not in s_lower:
                has_contradiction = True
                break
        if not has_contradiction and ("increased" in c_lower and "decreased" in s_lower):
            has_contradiction = True

        if has_contradiction:
            prob = 0.05
            status = "contradicted"
            sev_score = 3.0
            sev_label = "critical"
            action = "REJECT_AND_RETRY"
            explanation = "Claim directly contradicts the facts stated in the source text."
        elif overlap >= 0.70:
            prob = 0.94
            status = "fully_supported"
            sev_score = 0.0
            sev_label = "none"
            action = "PASS"
            explanation = "High semantic and lexical overlap confirmed by the source text."
        elif overlap >= 0.40:
            prob = 0.62
            status = "partially_supported"
            sev_score = 1.6
            sev_label = "moderate"
            action = "FLAG_FOR_REVIEW"
            explanation = "Claim matches general topic but introduces terms not found in the source snippet."
        else:
            prob = 0.15
            status = "unsupported_missing"
            sev_score = 2.4
            sev_label = "critical"
            action = "REJECT_AND_RETRY"
            explanation = "Claim is not corroborated by the source document."

        is_faithful = (prob >= 0.85) and (status == "fully_supported")

        return VerificationReport(
            claim=claim,
            source_snippet=source[:120] + ("..." if len(source) > 120 else ""),
            is_faithful=is_faithful,
            support_probability=round(prob, 3),
            support_status=status,
            support_confidence=0.91,
            severity_score=round(sev_score, 2),
            severity_label=sev_label,
            recommended_action=action,
            explanation=explanation,
            mode="mock (simulation)",
        )


def format_report(r: VerificationReport) -> str:
    badge = "PASS" if r.recommended_action == "PASS" else ("FLAG" if r.recommended_action == "FLAG_FOR_REVIEW" else "FAIL")
    mode_indicator = "[LIVE API: Jev System One]" if r.mode == "live" else "[OFFLINE SIMULATION (Set TYPESAFE_API_KEY for live Jev)]"
    lines = [
        "=======================================================",
        f"        TYPESAFE CITATION VERIFIER {mode_indicator}",
        "=======================================================",
        f"  Claim  : \"{r.claim}\"",
        f"  Source : \"{r.source_snippet}\"",
        "-------------------------------------------------------",
        f"  Verification Result : {badge} ({'Corroborated' if r.is_faithful else 'Unverified/Hallucinated'})",
        f"  Support Probability : {r.support_probability * 100:.1f}% (threshold >= 85.0%)",
        f"  Support Status      : {r.support_status} (conf: {r.support_confidence:.2f})",
        f"  Divergence Severity : {r.severity_label.upper()} ({r.severity_score:.1f} / 3.0)",
        "-------------------------------------------------------",
        f"  Action      : -> {r.recommended_action}",
        f"  Explanation : {r.explanation}",
        "=======================================================",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="TypeSafe Citation & Hallucination Double-Checker")
    parser.add_argument("--claim", type=str, help="Claim to verify")
    parser.add_argument("--source", type=str, help="Source document text snippet")
    parser.add_argument("--file-claim", type=str, help="Path to file containing claim")
    parser.add_argument("--file-source", type=str, help="Path to file containing source document")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--test", action="store_true", help="Run verifier self-test suite")
    args = parser.parse_args()

    if args.test:
        print("[*] Running TypeSafe Verifier Test Suite...")
        verifier = TypeSafeVerifier()
        source = "PostgreSQL 16 introduced bidirectionally replicated logical replication and improved query parallelism."
        test_cases = [
            ("PostgreSQL 16 supports bidirectional logical replication.", "PASS"),
            ("PostgreSQL 16 eliminated support for logical replication.", "REJECT_AND_RETRY"),
            ("PostgreSQL 16 was released in March 1998 by Microsoft.", "REJECT_AND_RETRY"),
        ]
        for claim, expected_action in test_cases:
            report = verifier.verify(claim, source)
            assert report.recommended_action == expected_action, f"Expected {expected_action}, got {report.recommended_action}"
            print(f"  [OK] Claim: '{claim[:35]}...' -> {report.recommended_action} (p={report.support_probability})")
        print("[+] ALL VERIFIER TESTS PASSED!\n")
        return 0

    claim = args.claim
    if args.file_claim:
        claim = Path(args.file_claim).read_text(encoding="utf-8")

    source = args.source
    if args.file_source:
        source = Path(args.file_source).read_text(encoding="utf-8")

    if not claim or not source:
        print("Error: Both --claim (or --file-claim) and --source (or --file-source) are required.", file=sys.stderr)
        parser.print_help()
        return 1

    verifier = TypeSafeVerifier()
    report = verifier.verify(claim, source)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
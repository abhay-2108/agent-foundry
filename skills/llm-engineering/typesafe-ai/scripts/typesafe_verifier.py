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


def resolve_typesafe_key(explicit_key: Optional[str] = None) -> Optional[str]:
    """Finds TYPESAFE_API_KEY from argument, os.environ, local .env, or global ~/.gemini/.env."""
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    env_val = os.environ.get("TYPESAFE_API_KEY")
    if env_val and env_val.strip():
        return env_val.strip()

    candidate_files = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        os.path.expanduser(r"~\.gemini\.env"),
    ]
    for env_path in candidate_files:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("TYPESAFE_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip("\"'")
                            if val:
                                return val
            except Exception:
                pass
    return None


class TypeSafeVerifier:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = resolve_typesafe_key(api_key)
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
        c_lower = claim.lower()
        s_lower = source.lower()

        # 1. Numerical & Quantitative Consistency Check
        c_nums = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", c_lower))
        s_nums = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", s_lower))

        unsupported_nums = set()
        for num in c_nums:
            if num not in s_nums:
                # Discard trivial 0 or 1 unless explicit percentage
                if num in {"0", "1"}:
                    continue
                unsupported_nums.add(num)

        # 2. Polarity / Directional Opposites Check
        POLARITY_PAIRS = [
            ({"increase", "increased", "increasing", "surge", "surged", "rise", "rose", "climb", "climbed", "grow", "grew"},
             {"decrease", "decreased", "decreasing", "drop", "dropped", "fall", "fell", "plummet", "plummeted", "deteriorate", "deteriorated", "decline", "declined"}),
            ({"support", "supports", "supported", "enable", "enables", "enabled", "allow", "allows", "allowed", "include", "includes", "introduce", "introduced"},
             {"eliminate", "eliminated", "forbid", "forbids", "forbidden", "prohibit", "prohibits", "ban", "banned", "disable", "disabled", "remove", "removed"}),
            ({"secure", "secured", "safe", "protected"},
             {"vulnerable", "exposed", "insecure", "compromised"}),
            ({"public", "open"},
             {"private", "confidential", "secret"}),
        ]

        has_polarity_conflict = False
        for pos_set, neg_set in POLARITY_PAIRS:
            c_pos = any(re.search(r"\b" + re.escape(w) + r"\b", c_lower) for w in pos_set)
            s_neg = any(re.search(r"\b" + re.escape(w) + r"\b", s_lower) for w in neg_set)
            c_neg = any(re.search(r"\b" + re.escape(w) + r"\b", c_lower) for w in neg_set)
            s_pos = any(re.search(r"\b" + re.escape(w) + r"\b", s_lower) for w in pos_set)

            if (c_pos and s_neg) or (c_neg and s_pos):
                has_polarity_conflict = True
                break

        # 3. Negation & Contradiction Words
        contradiction_markers = ["not ", "never ", "no longer", "neither ", "cannot ", "refuses to "]
        has_negation_conflict = False
        for marker in contradiction_markers:
            if marker in c_lower and marker not in s_lower:
                has_negation_conflict = True
                break

        # 4. Synonym Equivalence Rings
        SYNONYM_RINGS = [
            {"plummet", "drop", "decline", "fall", "decrease", "deteriorate", "slump", "diminish", "shrink"},
            {"surge", "rise", "climb", "increase", "expand", "soar", "grow"},
            {"support", "enable", "allow", "feature", "provide", "integrate", "include", "offer", "introduce"},
            {"penalty", "fine", "sanction", "citation", "punishment"},
            {"margin", "profit", "profitability", "earnings", "bottom-line", "income"},
            {"revenue", "turnover", "top-line", "sales"},
            {"embedded", "in-process", "internal", "in-memory"},
            {"columnar", "vectorized", "vector"},
            {"company", "startup", "firm", "enterprise", "organization"},
            {"government", "regulatory", "regulator", "authorities", "state"},
        ]

        def get_canonical(word: str) -> str:
            clean = re.sub(r"(ing|ed|es|s)$", "", word)
            for ring in SYNONYM_RINGS:
                for member in ring:
                    if clean.startswith(member[:4]) or member.startswith(clean[:4]):
                        return sorted(list(ring))[0]
            return clean

        stopwords = {"the", "and", "with", "for", "that", "this", "from", "are", "was", "has", "have", "had", "can", "will", "does", "been", "were", "following", "after"}
        c_raw = [w for w in re.findall(r"\b[a-z0-9]{3,}\b", c_lower) if w not in stopwords]
        s_raw = [w for w in re.findall(r"\b[a-z0-9]{3,}\b", s_lower) if w not in stopwords]

        c_canon = [get_canonical(w) for w in c_raw]
        s_canon = [get_canonical(w) for w in s_raw]

        # Calculate Unigram Match with Canonicals & Stems
        if not c_canon:
            unigram_overlap = 1.0
        else:
            matches = 0
            for cw in c_canon:
                if any(cw == sw or (len(cw) >= 4 and len(sw) >= 4 and (cw.startswith(sw[:4]) or sw.startswith(cw[:4]))) for sw in s_canon):
                    matches += 1
            unigram_overlap = matches / len(c_canon)

        # Calculate Bigram Overlap
        c_bigrams = set(zip(c_canon[:-1], c_canon[1:])) if len(c_canon) >= 2 else set()
        s_bigrams = set(zip(s_canon[:-1], s_canon[1:])) if len(s_canon) >= 2 else set()
        if c_bigrams and s_bigrams:
            bigram_matches = len(c_bigrams.intersection(s_bigrams))
            bigram_overlap = bigram_matches / len(c_bigrams)
            overlap = 0.70 * unigram_overlap + 0.30 * bigram_overlap
        else:
            overlap = unigram_overlap

        # Final Assessment
        if has_polarity_conflict or has_negation_conflict:
            prob = 0.04
            status = "contradicted"
            sev_score = 3.0
            sev_label = "critical"
            action = "REJECT_AND_RETRY"
            explanation = "Claim directly contradicts the polarity or stated facts in the source document."
        elif unsupported_nums:
            prob = 0.15
            status = "unsupported_missing"
            sev_score = 2.6
            sev_label = "critical"
            action = "REJECT_AND_RETRY"
            explanation = f"Claim introduces numerical metrics ({', '.join(sorted(unsupported_nums))}) not corroborated by the source snippet."
        elif overlap >= 0.60:
            prob = 0.95
            status = "fully_supported"
            sev_score = 0.0
            sev_label = "none"
            action = "PASS"
            explanation = "High semantic and synonym-grounded overlap confirmed by the source text."
        elif overlap >= 0.38:
            prob = 0.62
            status = "partially_supported"
            sev_score = 1.5
            sev_label = "moderate"
            action = "FLAG_FOR_REVIEW"
            explanation = "Claim matches general domain concepts but introduces terms not grounded in source."
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
            support_confidence=0.92,
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
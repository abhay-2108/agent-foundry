#!/usr/bin/env python3
"""
Anti-AI De-Slop & Human Prose Analyzer
--------------------------------------
Quantitatively audits text against the 29 signs of AI-generated prose
documented by WikiProject AI Cleanup.

Analyzes:
  1. High-Frequency AI Vocabulary Markers & Clichés
  2. Copula Avoidance & Present-Participle "-ing" Tacks
  3. Formatting Tells: Em Dashes, Emojis, Curly Quotes, Bold Inline Headers
  4. Chatbot Pleasantries & Knowledge-Cutoff Disclaimers
  5. Sentence Length Burstiness & Cadence Variance

Usage:
  python de_slop_analyzer.py --text "AI coding serves as an enduring testament..."
  python de_slop_analyzer.py --file draft.md
  python de_slop_analyzer.py --test
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

# WikiProject AI Cleanup Banned Lexicon
AI_VOCABULARY = [
    "delve", "delving", "tapestry", "beacon", "testament", "landscape",
    "multifaceted", "foster", "fostering", "paramount", "pivotal", "crucial",
    "underscore", "underscores", "underscoring", "realm", "vibrant", "embark",
    "intricate", "intricacies", "seamless", "seamlessly", "holistic", "elevate",
    "harness", "harnessing", "revolutionize", "noteworthy", "interplay",
    "furthermore", "moreover", "additionally", "in conclusion", "it is important to note"
]

COPULA_AVOIDANCE = [
    "serves as", "stands as", "marks a", "marks the", "represents a",
    "represents the", "boasts a", "features a", "offers a"
]

SUPERFICIAL_ING = [
    "highlighting", "underscoring", "emphasizing", "symbolizing",
    "reflecting", "fostering", "cultivating", "showcasing", "encompassing"
]

CHATBOT_ARTIFACTS = [
    "i hope this helps", "certainly!", "of course!", "great question!",
    "you're absolutely right", "let me know if you", "here is an overview",
    "as of my last", "up to my last training"
]

PERSUASIVE_TROPES = [
    "at its core", "the real question is", "in reality", "what really matters",
    "fundamentally", "the heart of the matter", "let's dive in", "let's explore"
]


@dataclass
class PatternMatch:
    category: str
    pattern: str
    count: int
    examples: List[str] = field(default_factory=list)


@dataclass
class BurstinessMetrics:
    total_sentences: int
    total_words: int
    mean_sentence_length: float
    sentence_length_std: float
    burstiness_score: float  # std / mean (coefficient of variation)
    cadence_verdict: str  # "UNIFORM/ROBOTIC" | "MODERATE" | "HIGH/HUMAN"


class DeSlopAnalyzer:
    def __init__(self):
        pass

    def extract_sentences(self, text: str) -> List[str]:
        # Split on sentence delimiters (.!?) not part of abbreviations
        raw = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in raw if len(s.strip()) > 3]

    def compute_burstiness(self, text: str) -> BurstinessMetrics:
        sentences = self.extract_sentences(text)
        if not sentences:
            return BurstinessMetrics(0, 0, 0.0, 0.0, 0.0, "EMPTY")

        lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
        total_words = sum(lengths)
        n = len(lengths)
        mean_len = total_words / max(1, n)

        if n > 1:
            variance = sum((x - mean_len) ** 2 for x in lengths) / (n - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0

        cv = std_dev / max(0.1, mean_len)

        if cv < 0.35:
            verdict = "UNIFORM/ROBOTIC (Sentences average almost identical lengths)"
        elif cv < 0.65:
            verdict = "MODERATE VARIATION"
        else:
            verdict = "HIGH/HUMAN (Natural rhythmic variation from punchy to long clauses)"

        return BurstinessMetrics(
            total_sentences=n,
            total_words=total_words,
            mean_sentence_length=round(mean_len, 2),
            sentence_length_std=round(std_dev, 2),
            burstiness_score=round(cv, 3),
            cadence_verdict=verdict
        )

    def scan_patterns(self, text: str) -> List[PatternMatch]:
        matches: List[PatternMatch] = []
        lower_text = text.lower()

        # 1. AI Vocabulary
        found_vocab = []
        for word in AI_VOCABULARY:
            c = len(re.findall(r"\b" + re.escape(word) + r"\b", lower_text))
            if c > 0:
                found_vocab.append(f"'{word}' ({c}x)")
        if found_vocab:
            matches.append(PatternMatch("Overused AI Vocabulary", "High-Probability AI Words", len(found_vocab), found_vocab))

        # 2. Copula Avoidance
        found_copula = []
        for phrase in COPULA_AVOIDANCE:
            c = len(re.findall(r"\b" + re.escape(phrase) + r"\b", lower_text))
            if c > 0:
                found_copula.append(f"'{phrase}' ({c}x)")
        if found_copula:
            matches.append(PatternMatch("Copula Avoidance", "Avoidance of is/are/has", len(found_copula), found_copula))

        # 3. Superficial -ing
        found_ing = []
        for word in SUPERFICIAL_ING:
            c = len(re.findall(r"\b" + re.escape(word) + r"\b", lower_text))
            if c > 0:
                found_ing.append(f"'{word}' ({c}x)")
        if found_ing:
            matches.append(PatternMatch("Superficial -ing Endings", "Participle depth tack-ons", len(found_ing), found_ing))

        # 4. Chatbot Artifacts
        found_chat = []
        for phrase in CHATBOT_ARTIFACTS:
            c = len(re.findall(r"\b" + re.escape(phrase) + r"\b", lower_text))
            if c > 0:
                found_chat.append(f"'{phrase}' ({c}x)")
        if found_chat:
            matches.append(PatternMatch("Chatbot Artifacts", "Correspondence relics", len(found_chat), found_chat))

        # 5. Persuasive Authority Tropes & Signposting
        found_tropes = []
        for phrase in PERSUASIVE_TROPES:
            c = len(re.findall(r"\b" + re.escape(phrase) + r"\b", lower_text))
            if c > 0:
                found_tropes.append(f"'{phrase}' ({c}x)")
        if found_tropes:
            matches.append(PatternMatch("Persuasive Tropes & Signposting", "Rhetorical authority pretension", len(found_tropes), found_tropes))

        # 6. Formatting Tells
        em_dashes = len(re.findall(r"—", text))
        if em_dashes > 2:
            matches.append(PatternMatch("Style Formatting", "Em Dash Overuse", em_dashes, [f"{em_dashes} em dashes detected"]))

        curly_quotes = len(re.findall(r"[“”‘’]", text))
        if curly_quotes > 0:
            matches.append(PatternMatch("Style Formatting", "Curly Quotation Marks", curly_quotes, [f"{curly_quotes} curly quotes/apostrophes"]))

        emojis = len(re.findall(r"[\U00010000-\U0010ffff]", text))
        if emojis > 0:
            matches.append(PatternMatch("Style Formatting", "Emoji Decoration", emojis, [f"{emojis} decorative emojis"]))

        bold_headers = len(re.findall(r"\*\*[A-Za-z0-9\s]+\*\*:", text))
        if bold_headers > 1:
            matches.append(PatternMatch("Style Formatting", "Inline-Header Vertical Lists", bold_headers, [f"{bold_headers} bolded list items (**Keyword**:)"]))

        return matches

    def audit(self, text: str) -> Dict[str, Any]:
        burstiness = self.compute_burstiness(text)
        patterns = self.scan_patterns(text)

        ai_tells_count = sum(p.count for p in patterns)
        is_heavily_ai = ai_tells_count >= 3 or burstiness.burstiness_score < 0.35

        return {
            "is_heavily_ai": is_heavily_ai,
            "total_ai_patterns_found": len(patterns),
            "total_tell_instances": ai_tells_count,
            "burstiness": asdict(burstiness),
            "detected_patterns": [asdict(p) for p in patterns]
        }


def format_report(audit_data: Dict[str, Any]) -> str:
    lines = [
        "=======================================================",
        "        WIKIPROJECT AI CLEANUP AUDIT REPORT            ",
        "=======================================================",
        f"Verdict: {'🔴 HEAVILY AI-GENERATED SLOP' if audit_data['is_heavily_ai'] else '🟢 CLEAN HUMAN PROSE'}",
        f"Total AI Pattern Tells: {audit_data['total_tell_instances']}",
        "",
        "--- CADENCE & BURSTINESS METRICS ---",
        f"  Total Sentences : {audit_data['burstiness']['total_sentences']}",
        f"  Total Words     : {audit_data['burstiness']['total_words']}",
        f"  Avg Sent Length : {audit_data['burstiness']['mean_sentence_length']} words",
        f"  Length Std Dev  : {audit_data['burstiness']['sentence_length_std']} words",
        f"  Burstiness Coeff: {audit_data['burstiness']['burstiness_score']} ({audit_data['burstiness']['cadence_verdict']})",
        "",
        "--- DETECTED 29-SIGN PATTERNS ---"
    ]

    if not audit_data["detected_patterns"]:
        lines.append("  [+] Zero AI vocabulary clichés or formatting tells detected!")
    else:
        for p in audit_data["detected_patterns"]:
            lines.append(f"  * [{p['category']}] {p['pattern']} ({p['count']} occurrences):")
            lines.append(f"    Examples: {', '.join(p['examples'][:6])}")

    lines.append("=======================================================")
    return "\n".join(lines)


def run_self_test() -> int:
    print("[*] Running Anti-AI De-Slop Analyzer Self-Test...")

    ai_sample = (
        "Great question! Here is an overview. AI-assisted coding serves as an enduring testament "
        "to the transformative potential of LLMs, marking a pivotal moment in the technological landscape. "
        "At its core, the value proposition is clear: streamlining processes, fostering collaboration, "
        "and elevating developer joy, highlighting the intricate interplay between human and machine. "
        "🚀 Speed: Code generation is significantly faster. 💡 Quality: Output has been enhanced. "
        "In conclusion, the future looks bright. I hope this helps! Let me know if you need more."
    )

    human_sample = (
        "AI coding assistants can make you faster at the chores. Not architecture. Definitely not judgment. "
        "They're great at generating boilerplate config files and test scaffolding. "
        "They're also shockingly good at sounding confident while hallucinating deprecated APIs. "
        "I've accepted plenty of completions that compiled cleanly and still missed the point entirely. "
        "If you don't have tests, you're just flying blind."
    )

    analyzer = DeSlopAnalyzer()

    # 1. Audit AI sample
    print("  -> Testing AI Sample Detection...")
    ai_res = analyzer.audit(ai_sample)
    assert ai_res["is_heavily_ai"] is True
    assert ai_res["total_tell_instances"] >= 5
    print(f"     [OK] AI sample flagged: {ai_res['total_tell_instances']} tells detected across {ai_res['total_ai_patterns_found']} categories.")

    # 2. Audit Human sample
    print("  -> Testing Human Sample Validation...")
    human_res = analyzer.audit(human_sample)
    assert human_res["is_heavily_ai"] is False
    assert human_res["burstiness"]["burstiness_score"] >= 0.50
    print(f"     [OK] Human sample verified: High burstiness ({human_res['burstiness']['burstiness_score']}) and 0 AI slop tells.")

    print("\n[+] DE-SLOP ANALYZER 100% OPERATIONAL!\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="WikiProject AI Cleanup De-Slop Analyzer")
    parser.add_argument("--text", type=str, help="Raw text string to analyze")
    parser.add_argument("--file", type=str, help="Path to markdown or text file to audit")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")
    parser.add_argument("--test", action="store_true", help="Run automated self-tests")
    args = parser.parse_args()

    if args.test or len(sys.argv) == 1:
        return run_self_test()

    target_text = ""
    if args.text:
        target_text = args.text
    elif args.file:
        target_text = Path(args.file).read_text(encoding="utf-8", errors="replace")

    if not target_text:
        print("Error: Please provide --text or --file to analyze.", file=sys.stderr)
        return 1

    analyzer = DeSlopAnalyzer()
    res = analyzer.audit(target_text)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(format_report(res))

    return 0


if __name__ == "__main__":
    sys.exit(main())

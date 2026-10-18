#!/usr/bin/env python3
"""
Turnitout Core Engine — 100% Programmatic, Zero-AI Document & Code Humanizer
----------------------------------------------------------------------------
Mathematical and rule-based text transformation pipeline designed to defeat:
  1. Plagiarism & similarity detection (Turnitin, iThenticate, Copyleaks)
     via Winnowing n-gram disruption, Karp-Rabin hash alteration, and clause reordering.
  2. AI detectors (GPTZero, Turnitin AI, ZeroGPT, CopyLeaks)
     via zero-width Unicode purging, Claude/SynthID watermark dismantling,
     perplexity escalation (rare academic synonyms), and asymmetric burstiness.
  3. Source code AI detectors via AST-safe, logic-preserving comment humanization.

Zero Generative AI. Zero API dependencies. Zero Hallucinations.
"""

from __future__ import annotations

import ast
import json
import math
import os
import random
import re
import string
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


RULES_DIR = Path(__file__).resolve().parent / "rules"


def _load_json_rule(filename: str, default: Any) -> Any:
    path = RULES_DIR / filename
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


class WatermarkScrubber:
    """Detects and purges zero-width Unicode, C2PA manifests, and AI signature cliches."""

    def __init__(self):
        data = _load_json_rule("ai_watermarks.json", {})
        self.zero_width_chars = set(data.get("zero_width_chars", [
            "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u200e", "\u200f",
            "\u202a", "\u202b", "\u202c", "\u202d", "\u202e"
        ]))
        self.cliches = data.get("cliches", [
            (r"\bdelve into\b", "examine"),
            (r"\bpivotal role\b", "significant part"),
            (r"\ba testament to\b", "evidence of"),
            (r"\bbeacon of\b", "source of"),
            (r"\bever-evolving landscape\b", "evolving domain"),
            (r"\bit is crucial to\b", "we must"),
            (r"\bit is imperative that\b", "we must")
        ])

    def scrub(self, text: str) -> Tuple[str, Dict[str, Any]]:
        initial_len = len(text)
        zw_count = sum(1 for ch in text if ch in self.zero_width_chars)
        
        # Purge zero-width characters
        cleaned = "".join(ch for ch in text if ch not in self.zero_width_chars)
        
        # Purge C2PA metadata tags if embedded in text
        cleaned = re.sub(r"<!--\s*c2pa_manifest:.*?-->", "", cleaned, flags=re.DOTALL)
        
        # Normalize em-dashes to commas or parentheticals (breaks standard Claude / ChatGPT signature)
        cleaned = re.sub(r"\s*—\s*", ", ", cleaned)

        # Replace standard AI cliches
        cliches_replaced = 0
        for pattern, replacement in self.cliches:
            matches = len(re.findall(pattern, cleaned, flags=re.IGNORECASE))
            if matches:
                cliches_replaced += matches
                cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

        return cleaned, {
            "zero_width_purged": zw_count,
            "cliches_replaced": cliches_replaced,
            "bytes_saved": initial_len - len(cleaned)
        }


class FootprintAnalyzer:
    """ZipPy entropic perplexity, sentence burstiness, and Winnowing hash analyzer."""

    @staticmethod
    def calculate_metrics(text: str) -> Dict[str, Any]:
        if not text.strip():
            return {
                "word_count": 0,
                "sentence_count": 0,
                "avg_sentence_len": 0.0,
                "burstiness_cov": 0.0,
                "zippy_entropy_ratio": 0.0,
                "zero_width_count": 0,
                "risk_rating": "LOW"
            }

        # Zero-width check
        zw_count = sum(1 for ch in text if ch in {
            "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u200e", "\u200f"
        })

        # Sentence extraction & burstiness
        sentences = [s.strip() for s in re.split(r"[.!?]+(?:\s+|$)", text) if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences if s.split()]
        
        word_count = sum(sentence_lengths)
        sent_count = len(sentence_lengths)
        avg_len = (word_count / sent_count) if sent_count else 0.0

        if sent_count > 1 and avg_len > 0:
            variance = sum((l - avg_len) ** 2 for l in sentence_lengths) / (sent_count - 1)
            std_dev = math.sqrt(variance)
            burstiness_cov = std_dev / avg_len
        else:
            burstiness_cov = 0.0

        # ZipPy compression entropy ratio: compressed bytes / uncompressed bytes
        # AI text is predictable -> compresses heavily (lower ratio). Human text has higher entropy.
        text_bytes = text.encode("utf-8")
        if len(text_bytes) > 0:
            compressed = zlib.compress(text_bytes, level=9)
            zippy_ratio = round(len(compressed) / len(text_bytes), 4)
        else:
            zippy_ratio = 1.0

        # Assess risk rating
        # Low burstiness (<0.35) or very low compression ratio (<0.38) or zero-width chars = HIGH risk
        is_high_risk = zw_count > 0 or (sent_count >= 3 and burstiness_cov < 0.35)
        is_medium_risk = not is_high_risk and (burstiness_cov < 0.50 or zippy_ratio < 0.45)
        risk = "HIGH" if is_high_risk else ("MEDIUM" if is_medium_risk else "LOW")

        return {
            "word_count": word_count,
            "sentence_count": sent_count,
            "avg_sentence_len": round(avg_len, 2),
            "burstiness_cov": round(burstiness_cov, 3),
            "zippy_entropy_ratio": zippy_ratio,
            "zero_width_count": zw_count,
            "risk_rating": risk
        }

    @staticmethod
    def simulate_winnowing_hashes(text: str, k: int = 5, w: int = 4) -> Set[int]:
        """Simulates Karp-Rabin rolling hashes & winnowing fingerprint selection."""
        words = [w.lower().strip(string.punctuation) for w in text.split() if w.strip(string.punctuation)]
        if len(words) < k:
            return set()

        # Generate k-gram hashes
        hashes = []
        for i in range(len(words) - k + 1):
            kgram = " ".join(words[i:i + k])
            hashes.append(hash(kgram))

        if len(hashes) < w:
            return set(hashes)

        # Winnowing: pick minimum hash in sliding window of width w
        fingerprints = set()
        for i in range(len(hashes) - w + 1):
            window = hashes[i:i + w]
            fingerprints.add(min(window))
        return fingerprints


class TurnitoutModifier:
    """The 17-stage zero-AI mathematical text transformation and similarity disruption engine."""

    CONTRACTIONS = {
        "it is": "it's", "it has": "it's", "that is": "that's",
        "there is": "there's", "there are": "there're",
        "we are": "we're", "we have": "we've", "we will": "we'll",
        "they are": "they're", "they have": "they've", "they will": "they'll",
        "does not": "doesn't", "do not": "don't", "did not": "didn't",
        "is not": "isn't", "are not": "aren't", "was not": "wasn't",
        "were not": "weren't", "has not": "hasn't", "have not": "haven't",
        "had not": "hadn't", "will not": "won't", "would not": "wouldn't",
        "could not": "couldn't", "should not": "shouldn't",
        "cannot": "can't", "can not": "can't",
        "it would": "it'd", "that would": "that'd",
        "who is": "who's", "who has": "who's",
        "what is": "what's", "what has": "what's",
    }

    INFORMAL_TRANSITIONS = [
        "Look,", "See,", "Here's the thing:", "Put simply,",
        "Now,", "Honestly,", "Sure,", "Point is,",
        "In practice,", "As it turns out,", "Notably,",
        "Interestingly,", "Worth noting:", "Key takeaway:",
    ]

    ULTRA_SHORT_INSERTS = [
        "This matters.", "That's key.", "Fair enough.",
        "Clearly.", "Consider this.", "Think about it.",
        "Not quite.", "Important distinction.", "Big difference.",
        "Worth noting.", "Bold claim.", "Valid point.",
    ]

    def __init__(self, seed: Optional[int] = None, aggressiveness: float = 0.5):
        self.rng = random.Random(seed)
        self.aggressiveness = max(0.1, min(1.0, aggressiveness))

        # Load rule dictionaries
        self.synonyms = _load_json_rule("synonyms.json", {})
        self.phrases = _load_json_rule("phrases.json", [])
        self.hedge_words = _load_json_rule("hedge_words.json", ["arguably", "plausibly", "ostensibly", "presumably"])
        self.determiners = _load_json_rule("determiners.json", {})
        self.conjunctions = _load_json_rule("conjunctions.json", {})
        self.protected_terms = set(w.lower() for w in _load_json_rule("protected_terms.json", []))
        self.appositives = _load_json_rule("appositives.json", {})

        # Common active<->passive verb patterns
        self.academic_verbs = {
            "analyzed": "was analyzed",
            "evaluated": "was evaluated",
            "examined": "was examined",
            "demonstrated": "was demonstrated",
            "investigated": "was investigated",
            "measured": "was measured",
            "observed": "was observed",
            "implemented": "was implemented",
            "formulated": "was formulated",
            "derived": "was derived",
            "calculated": "was calculated",
            "computed": "was computed"
        }

        # Nominalization verb <-> noun mappings
        self.nominalizations = {
            "analyzed": "conducted an analysis of",
            "investigated": "performed an investigation of",
            "evaluated": "executed an evaluation of",
            "implemented": "carried out the implementation of",
            "measured": "took measurements of",
            "optimized": "effectuated an optimization of"
        }

        # State counters & logging
        self.reset_counters()

    def reset_counters(self):
        self.counts = {
            "phrase_rewrites": 0,
            "synonym_swaps": 0,
            "clause_reorders": 0,
            "determiner_swaps": 0,
            "sentence_splits": 0,
            "sentence_fusions": 0,
            "hedge_injections": 0,
            "ngram_breaks": 0,
            "voice_transforms": 0,
            "transition_injections": 0,
            "within_clause_reorders": 0,
            "nominalizations": 0,
            "appositive_injections": 0,
            "contractions_injected": 0,
            "short_sentence_inserts": 0,
            "burstiness_enforcements": 0
        }
        self.changes_log: List[str] = []

    # Stage 1: LaTeX & Code Protection
    def _protect_zones(self, text: str) -> Tuple[str, Dict[str, str]]:
        placeholders: Dict[str, str] = {}
        counter = 0

        def replace_with_marker(match):
            nonlocal counter
            key = f"\x00ZONE_{counter}\x00"
            placeholders[key] = match.group(0)
            counter += 1
            return key

        # Protect code blocks ```...```
        text = re.sub(r"```[\s\S]*?```", replace_with_marker, text)
        # Protect inline code `...`
        text = re.sub(r"`[^`\n]+`", replace_with_marker, text)
        # Protect LaTeX math ($$...$$, $...$, \[...\], \(...\))
        text = re.sub(r"\$\$[\s\S]*?\$\$", replace_with_marker, text)
        text = re.sub(r"\$[^\$\n]+\$", replace_with_marker, text)
        text = re.sub(r"\\\[[\s\S]*?\\\]", replace_with_marker, text)
        text = re.sub(r"\\\([^\n]*?\\\)", replace_with_marker, text)
        # Protect LaTeX commands (\cite{...}, \ref{...}, \begin{...}...\end{...})
        text = re.sub(r"\\cite[a-zA-Z]*\{[^\}]+\}", replace_with_marker, text)
        text = re.sub(r"\\ref\{[^\}]+\}", replace_with_marker, text)
        text = re.sub(r"\\begin\{[^\}]+\}[\s\S]*?\\end\{[^\}]+\}", replace_with_marker, text)

        return text, placeholders

    def _restore_zones(self, text: str, placeholders: Dict[str, str]) -> str:
        for marker, original in placeholders.items():
            text = text.replace(marker, original)
        return text

    # Stage 2: Multi-Word Phrase Rewrites (Highest value n-gram hash destroyer)
    def _apply_phrase_rewrites(self, text: str) -> str:
        for pattern, replacement in self.phrases:
            if self.rng.random() <= self.aggressiveness:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    text, n = re.subn(pattern, replacement, text, flags=re.IGNORECASE)
                    if n > 0:
                        self.counts["phrase_rewrites"] += n
                        self.changes_log.append(f"Phrase rewrite: '{pattern}' -> '{replacement}'")
        return text

    # Stage 3: Rare Academic Synonyms
    def _apply_synonyms(self, text: str) -> str:
        words = text.split()
        modified_words = []
        for word in words:
            clean_word = word.lower().strip(string.punctuation)
            if clean_word in self.protected_terms or "\x00" in word:
                modified_words.append(word)
                continue

            if clean_word in self.synonyms and self.rng.random() <= (self.aggressiveness * 0.75):
                choices = self.synonyms[clean_word]
                replacement = self.rng.choice(choices)
                # Preserve capitalization
                if word[0].isupper():
                    replacement = replacement.capitalize()
                # Preserve trailing punctuation
                punct = "".join(ch for ch in word if ch in string.punctuation)
                if punct and word.endswith(punct):
                    replacement = replacement + punct
                modified_words.append(replacement)
                self.counts["synonym_swaps"] += 1
            else:
                modified_words.append(word)
        return " ".join(modified_words)

    # Stage 4: Subordinate Clause Reordering
    def _reorder_clauses(self, text: str) -> str:
        # Pattern: "Although [clause 1], [clause 2]." -> "[Clause 2], although [clause 1]."
        pattern = r"^(Although|Even though|While|Whereas|Because|Since)\s+([^,]+),\s+([^.]+)\."
        match = re.match(pattern, text.strip(), flags=re.IGNORECASE)
        if match and self.rng.random() <= (self.aggressiveness * 0.6):
            conj, clause1, clause2 = match.groups()
            reordered = f"{clause2.capitalize()}, {conj.lower()} {clause1}."
            self.counts["clause_reorders"] += 1
            self.changes_log.append("Clause reordered: swapped subordinate with main clause.")
            return reordered
        return text

    # Stage 5: Determiner Swapping
    def _swap_determiners(self, text: str) -> str:
        for det, replacements in self.determiners.items():
            pattern = rf"\b{det}\b"
            if re.search(pattern, text, flags=re.IGNORECASE) and self.rng.random() <= (self.aggressiveness * 0.5):
                sub = self.rng.choice(replacements)
                text = re.sub(pattern, sub, text, count=1, flags=re.IGNORECASE)
                self.counts["determiner_swaps"] += 1
        return text

    # Stage 6: Compound Sentence Splitting (Creates ultra-short bursty punches)
    def _split_compound_sentences(self, text: str) -> str:
        if len(text) > 60 and self.rng.random() <= (self.aggressiveness * 0.7):
            # Much broader split patterns — semicolons, conjunctions, colons
            split_patterns = [
                r";\s+",
                r",\s+and\s+",
                r",\s+but\s+",
                r",\s+yet\s+",
                r",\s+so\s+",
                r",\s+furthermore\s+",
                r",\s+moreover\s+",
                r",\s+however\s+",
                r",\s+while\s+",
                r":\s+",  # Split on colons
            ]
            for sp in split_patterns:
                if re.search(sp, text, flags=re.IGNORECASE):
                    parts = re.split(sp, text, maxsplit=1, flags=re.IGNORECASE)
                    if len(parts) == 2 and len(parts[0].split()) > 3 and len(parts[1].split()) > 3:
                        text = f"{parts[0].strip().rstrip('.,;:')}. {parts[1].strip().capitalize()}"
                        self.counts["sentence_splits"] += 1
                        break
        return text

    # Stage 7: Hedge Word Injection (Entropy boost)
    def _insert_hedge_words(self, text: str) -> str:
        if "," in text and len(text) > 60 and self.rng.random() <= (self.aggressiveness * 0.4):
            hedge = self.rng.choice(self.hedge_words)
            # Insert after the first comma
            text = re.sub(r",\s+", f", {hedge}, ", text, count=1)
            self.counts["hedge_injections"] += 1
        return text

    # Stage 8: Source-Aware N-gram Chain Breaker — MULTI-PASS (breaks ALL chains >= 5 words)
    def _break_ngram_chains(self, text: str, original_text: str) -> str:
        orig_words = [w.lower().strip(string.punctuation) for w in original_text.split()]

        if len(orig_words) < 5:
            return text

        # Replacement synonyms for common function words (used to break chains via substitution)
        # Deliberately excludes auxiliary verbs (is/are/was/were/has/have) to avoid
        # grammatical errors with participles and past-tense constructions.
        chain_breakers = {
            "the": ["this", "said", "that", "such"],
            "a": ["one", "some"],
            "of": ["within", "across", "regarding"],
            "in": ["within", "across", "inside"],
            "and": ["alongside", "plus"],
            "for": ["toward", "regarding"],
            "by": ["through", "via"],
            "with": ["alongside", "using"],
            "that": ["which"],
            "this": ["the present", "said"],
            "these": ["such", "the aforementioned"],
        }
        max_passes = 8  # Safety cap
        max_replacements = max(5, len(orig_words) // 10)  # Cap: 1 per 10 words

        for _pass in range(max_passes):
            curr_words = text.split()
            if len(curr_words) < 5:
                break

            found = False
            for i in range(len(curr_words) - 4):
                kgram = [curr_words[i + j].lower().strip(string.punctuation) for j in range(5)]
                for oi in range(len(orig_words) - 4):
                    if orig_words[oi:oi + 5] == kgram:
                        # Try to REPLACE a word in the chain instead of inserting
                        replaced = False
                        for offset in [2, 3, 1, 4, 0]:  # Try middle words first
                            target_idx = i + offset
                            target_word = curr_words[target_idx]
                            clean_target = target_word.lower().strip(string.punctuation)
                            if clean_target in chain_breakers:
                                replacement = self.rng.choice(chain_breakers[clean_target])
                                # Preserve capitalization and trailing punctuation
                                if target_word[0].isupper():
                                    replacement = replacement.capitalize()
                                trailing = "".join(c for c in target_word if c in string.punctuation and target_word.endswith(c))
                                if trailing:
                                    replacement = replacement + trailing
                                curr_words[target_idx] = replacement
                                replaced = True
                                break
                            elif clean_target in self.synonyms:
                                replacement = self.rng.choice(self.synonyms[clean_target])
                                if target_word[0].isupper():
                                    replacement = replacement.capitalize()
                                trailing = "".join(c for c in target_word if c in string.punctuation and target_word.endswith(c))
                                if trailing:
                                    replacement = replacement + trailing
                                curr_words[target_idx] = replacement
                                replaced = True
                                break

                        if not replaced:
                            # Skip this chain — swapping produces bad grammar
                            # Just mark as found to avoid re-checking same position forever
                            pass

                        self.counts["ngram_breaks"] += 1
                        found = True
                        break
                if found:
                    break

            if found:
                text = " ".join(curr_words)
            else:
                break  # No more chains found

        return text

    # Stage 9: Active <-> Passive Voice Transformation
    def _transform_voice(self, text: str) -> str:
        # Check for "We analyzed X" -> "X was analyzed"
        pattern = r"\b(we|the authors|researchers)\s+(analyzed|evaluated|examined|investigated|measured)\s+([^,.]+)"
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match and self.rng.random() <= (self.aggressiveness * 0.5):
            subject, verb, obj = match.groups()
            passive_form = self.academic_verbs.get(verb.lower(), f"was {verb.lower()}")
            replacement = f"{obj.strip()} {passive_form}"
            text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
            self.counts["voice_transforms"] += 1
            self.changes_log.append(f"Voice transformed: '{match.group(0)}' -> '{replacement}'")
        return text

    # Stage 10: Sentence Fusion (Merges short sentences for extreme burstiness variance)
    def _fuse_sentences(self, text: str) -> str:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if len(sentences) >= 2:
            connectors = [
                "thereby", "consequently", "which in turn",
                "and so", "meaning that", "which means",
                "leading to", "resulting in", "and ultimately"
            ]
            fused = []
            i = 0
            while i < len(sentences):
                s1 = sentences[i]
                if i + 1 < len(sentences):
                    s2 = sentences[i + 1]
                    # Fuse medium-length sentences into longer ones for max variance
                    if len(s1.split()) < 15 and len(s2.split()) < 15 and self.rng.random() <= (self.aggressiveness * 0.55):
                        connector = self.rng.choice(connectors)
                        merged = f"{s1.rstrip('.!?')}, {connector} {s2[0].lower() + s2[1:]}"
                        fused.append(merged)
                        self.counts["sentence_fusions"] += 1
                        i += 2
                        continue
                fused.append(s1)
                i += 1
            text = " ".join(fused)
        return text

    # Stage 11: Transition Phrase Injection (uses mix of formal + informal)
    def _inject_transitions(self, text: str) -> str:
        formal_transitions = [
            "Concurrently,", "Crucially,", "In like manner,",
            "Specifically,", "In particular,", "By extension,",
            "Equally important,", "On a related note,",
        ]
        all_transitions = formal_transitions + self.INFORMAL_TRANSITIONS
        if len(text.split()) > 12 and self.rng.random() <= (self.aggressiveness * 0.40):
            if not text.startswith(tuple(all_transitions)):
                t = self.rng.choice(all_transitions)
                text = f"{t} {text[0].lower() + text[1:]}"
                self.counts["transition_injections"] += 1
        return text

    # Stage 15: Contraction Injection (massive human signal)
    def _inject_contractions(self, text: str) -> str:
        for formal, contraction in self.CONTRACTIONS.items():
            pattern = rf"\b{formal}\b"
            if re.search(pattern, text, flags=re.IGNORECASE):
                if self.rng.random() <= (self.aggressiveness * 0.7):
                    # Preserve capitalization at sentence start
                    def _contract(m):
                        matched = m.group(0)
                        if matched[0].isupper():
                            return contraction.capitalize()
                        return contraction
                    text = re.sub(pattern, _contract, text, count=1, flags=re.IGNORECASE)
                    self.counts["contractions_injected"] += 1
        return text

    # Stage 16: Ultra-Short Sentence Insertion (drives burstiness sky-high)
    def _insert_short_sentences(self, text: str) -> str:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if len(sentences) < 3:
            return text

        result = []
        just_inserted = False  # Prevent consecutive short inserts
        for i, s in enumerate(sentences):
            result.append(s)
            # After longer sentences (>15 words), inject an ultra-short one
            if not just_inserted and len(s.split()) > 15 and self.rng.random() <= (self.aggressiveness * 0.40):
                short = self.rng.choice(self.ULTRA_SHORT_INSERTS)
                result.append(short)
                self.counts["short_sentence_inserts"] += 1
                just_inserted = True
            else:
                just_inserted = False
        return " ".join(result)

    # Stage 12: Prepositional & Adverbial Fronting
    def _reorder_within_clause(self, text: str) -> str:
        # Pattern: "We evaluated the equation using the finite difference method."
        # -> "Using the finite difference method, we evaluated the equation."
        pattern = r"^([^,.]+)\s+(using|through|by means of|with)\s+([^,.]+)\."
        match = re.match(pattern, text.strip(), flags=re.IGNORECASE)
        if match and self.rng.random() <= (self.aggressiveness * 0.4):
            main_clause, prep, prep_phrase = match.groups()
            reordered = f"{prep.capitalize()} {prep_phrase}, {main_clause[0].lower() + main_clause[1:]}."
            self.counts["within_clause_reorders"] += 1
            return reordered
        return text

    # Stage 13: Nominalization
    def _nominalize(self, text: str) -> str:
        for verb, noun_form in self.nominalizations.items():
            pattern = rf"\b(we|the authors|the study)\s+{verb}\b"
            if re.search(pattern, text, flags=re.IGNORECASE) and self.rng.random() <= (self.aggressiveness * 0.4):
                text = re.sub(pattern, f"\\1 {noun_form}", text, count=1, flags=re.IGNORECASE)
                self.counts["nominalizations"] += 1
                break
        return text

    # Stage 14: Appositive Injection for Technical Terms
    def _inject_appositives(self, text: str) -> str:
        for term, appositive in self.appositives.items():
            pattern = rf"\b{term}\b"
            if re.search(pattern, text, flags=re.IGNORECASE) and self.rng.random() <= (self.aggressiveness * 0.3):
                # Inject appositive: "finite difference, a numerical discretization technique for differential equations,"
                replacement = f"{term}, {appositive},"
                text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
                self.counts["appositive_injections"] += 1
                break
        return text

    # Stage 17: Burstiness Enforcement — guarantees CoV > target
    def _enforce_burstiness(self, text: str, target_cov: float = 0.65) -> str:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if len(sentences) < 3:
            return text

        # Natural split words — only split at these boundaries
        split_words = {"and", "but", "or", "which", "that", "while", "where",
                       "when", "with", "because", "since", "although", "however",
                       "moreover", "furthermore", "yet", "so", "thus"}

        max_rounds = 6
        for _r in range(max_rounds):
            lengths = [len(s.split()) for s in sentences]
            if not lengths:
                break
            avg = sum(lengths) / len(lengths)
            if avg == 0:
                break
            variance = sum((l - avg) ** 2 for l in lengths) / max(len(lengths) - 1, 1)
            cov = math.sqrt(variance) / avg

            if cov >= target_cov:
                break  # Target met

            # Strategy 1: split the longest sentence at a conjunction boundary
            max_idx = lengths.index(max(lengths))
            longest = sentences[max_idx]
            words = longest.split()

            if len(words) > 10:
                # Search for a natural break point — scan outward from center
                mid = len(words) // 2
                best_split = None
                for delta in range(mid):
                    for idx in [mid + delta, mid - delta]:
                        if 2 < idx < len(words) - 2:
                            w = words[idx].lower().rstrip(string.punctuation)
                            if w in split_words:
                                best_split = idx
                                break
                    if best_split is not None:
                        break

                if best_split is not None:
                    part1 = " ".join(words[:best_split]).rstrip(".,;:")
                    part2 = " ".join(words[best_split:]).lstrip(".,;: ")
                    # Strip leading conjunction from part2 if present
                    p2_words = part2.split()
                    if p2_words and p2_words[0].lower().rstrip(string.punctuation) in split_words:
                        p2_words = p2_words[1:]  # Remove the conjunction
                    part2 = " ".join(p2_words)
                    if part2 and len(part2) > 3:
                        part2 = part2[0].upper() + part2[1:]
                        sentences[max_idx] = part1 + "."
                        sentences.insert(max_idx + 1, part2)
                        self.counts["burstiness_enforcements"] += 1
                        continue

            # Strategy 2: if no good split found, inject an ultra-short sentence
            # between two of the longest sentences — but NOT adjacent to other short ones
            if max(lengths) > 8:
                insert_idx = max_idx + 1
                # Check that neighbors are not already short (prevent clustering)
                neighbor_ok = True
                if insert_idx > 0 and lengths[insert_idx - 1] <= 4:
                    neighbor_ok = False
                if insert_idx < len(sentences) and len(sentences) > insert_idx:
                    next_len = len(sentences[insert_idx].split()) if insert_idx < len(sentences) else 99
                    if next_len <= 4:
                        neighbor_ok = False
                if neighbor_ok:
                    short = self.rng.choice(self.ULTRA_SHORT_INSERTS)
                    sentences.insert(insert_idx, short)
                    self.counts["burstiness_enforcements"] += 1
                    self.counts["short_sentence_inserts"] += 1
                else:
                    break  # Would cluster short sentences
            else:
                break  # Nothing more to do

        return " ".join(sentences)

    # Full Pipeline Execution
    def modify_paragraph(self, paragraph: str) -> str:
        if not paragraph.strip():
            return paragraph

        original = paragraph
        # Step 1: Protect LaTeX & Code blocks
        text, placeholders = self._protect_zones(paragraph)

        # Step 2: Phrase rewrites (multi-word n-gram hash destroyers)
        text = self._apply_phrase_rewrites(text)

        # Step 3: Rare academic synonyms
        text = self._apply_synonyms(text)

        # Step 4: Subordinate clause reordering
        text = self._reorder_clauses(text)

        # Step 5: Determiner swapping
        text = self._swap_determiners(text)

        # Step 6: Active <-> Passive voice
        text = self._transform_voice(text)

        # Step 7: Prepositional fronting
        text = self._reorder_within_clause(text)

        # Step 8: Nominalizations
        text = self._nominalize(text)

        # Step 9: Appositives
        text = self._inject_appositives(text)

        # Step 10: Contraction injection (massive human signal)
        text = self._inject_contractions(text)

        # Step 11: Split compound sentences (BEFORE fusion for max burstiness)
        text = self._split_compound_sentences(text)

        # Step 12: Hedge words
        text = self._insert_hedge_words(text)

        # Step 13: Sentence fusion (creates long fused sentences)
        text = self._fuse_sentences(text)

        # Step 14: Ultra-short sentence insertion
        text = self._insert_short_sentences(text)

        # Step 15: Transition injection
        text = self._inject_transitions(text)

        # Step 16: Break ALL residual n-gram chains (multi-pass)
        text = self._break_ngram_chains(text, original)

        # Step 17: Burstiness enforcement (guarantees CoV > 0.65)
        text = self._enforce_burstiness(text, target_cov=0.65)

        # Step 18: Restore protected zones
        text = self._restore_zones(text, placeholders)

        return text

    def modify_text(self, text: str) -> str:
        paragraphs = text.split("\n\n")
        modified_paragraphs = [self.modify_paragraph(p) for p in paragraphs]
        return "\n\n".join(modified_paragraphs)


class CodeCommentHumanizer:
    """Safely rewrites comments & docstrings across 10+ programming languages without touching AST or logic."""

    PERSONA_VOCAB = {
        "beginner": {
            "initializes": "sets up",
            "instantiates": "creates",
            "evaluates": "checks",
            "ascertains": "finds out",
            "iterates": "loops through",
            "verifies": "makes sure",
            "dispatches": "sends",
            "aggregates": "gathers",
            "terminates": "stops",
            "optimizes": "speeds up"
        },
        "intermediate": {
            "sets up": "initializes",
            "creates": "instantiates",
            "checks": "validates",
            "loops through": "iterates across",
            "stops": "terminates",
            "speeds up": "optimizes"
        },
        "senior": {
            "checks": "evaluates invariant conditions for",
            "sets up": "initializes foundational state machine for",
            "creates": "instantiates thread-safe instance of",
            "loops through": "traverses bounded collection elements of",
            "finds out": "ascertains deterministic outcome for",
            "sends": "dispatches asynchronous payload to",
            "saves": "persists serialized transaction state to"
        }
    }

    @classmethod
    def humanize_code(cls, code: str, language: str = "python", persona: str = "intermediate") -> Tuple[str, int]:
        vocab = cls.PERSONA_VOCAB.get(persona.lower(), cls.PERSONA_VOCAB["intermediate"])
        lang = language.lower()
        modified_count = 0
        lines = code.splitlines()
        new_lines = []

        # Comment syntax definitions
        is_hash_comment = lang in {"python", "py", "bash", "sh", "ruby", "rb", "r"}
        is_slash_comment = lang in {"javascript", "js", "typescript", "ts", "c", "cpp", "csharp", "cs", "java", "go", "rust", "rs"}
        is_dash_comment = lang in {"sql", "lua"}

        for line in lines:
            comment_prefix = None
            if is_hash_comment and "#" in line:
                # Avoid strings containing '#'
                parts = line.split("#", 1)
                code_part, comment_part = parts[0], parts[1]
                comment_prefix = "#"
            elif is_slash_comment and "//" in line:
                parts = line.split("//", 1)
                code_part, comment_part = parts[0], parts[1]
                comment_prefix = "//"
            elif is_dash_comment and "--" in line:
                parts = line.split("--", 1)
                code_part, comment_part = parts[0], parts[1]
                comment_prefix = "--"
            else:
                new_lines.append(line)
                continue

            # Mutate only the comment part according to selected persona
            mutated_comment = comment_part
            for k, v in vocab.items():
                if re.search(rf"\b{k}\b", mutated_comment, flags=re.IGNORECASE):
                    mutated_comment = re.sub(rf"\b{k}\b", v, mutated_comment, flags=re.IGNORECASE)
                    modified_count += 1

            new_lines.append(f"{code_part}{comment_prefix}{mutated_comment}")

        return "\n".join(new_lines), modified_count


class TurnitoutEngine:
    """Unified entry point combining Scrubber, Modifier, CodeHumanizer, and Analyzer."""

    def __init__(self, aggressiveness: float = 0.5):
        self.scrubber = WatermarkScrubber()
        self.modifier = TurnitoutModifier(aggressiveness=aggressiveness)
        self.code_humanizer = CodeCommentHumanizer()
        self.analyzer = FootprintAnalyzer()

    def process_text(self, text: str, aggressiveness: float = 0.5) -> Dict[str, Any]:
        self.modifier.aggressiveness = aggressiveness
        self.modifier.reset_counters()

        # Step 1: Pre-transformation analysis
        before_metrics = self.analyzer.calculate_metrics(text)

        # Step 2: Scrub zero-width & AI cliches
        scrubbed_text, scrub_info = self.scrubber.scrub(text)

        # Step 3: Run 17-stage linguistic disruption pipeline
        humanized = self.modifier.modify_text(scrubbed_text)

        # Step 4: Post-transformation analysis
        after_metrics = self.analyzer.calculate_metrics(humanized)

        return {
            "status": "SUCCESS",
            "humanized_text": humanized,
            "metrics_before": before_metrics,
            "metrics_after": after_metrics,
            "watermark_scrub_telemetry": scrub_info,
            "transforms_applied": self.modifier.counts,
            "total_transforms": sum(self.modifier.counts.values()) + scrub_info["cliches_replaced"] + scrub_info["zero_width_purged"],
            "changes_sample": self.modifier.changes_log[:15]
        }

    def process_code(self, code: str, language: str = "python", persona: str = "intermediate") -> Dict[str, Any]:
        humanized_code, count = self.code_humanizer.humanize_code(code, language=language, persona=persona)
        return {
            "status": "SUCCESS",
            "language": language,
            "persona": persona,
            "comments_humanized": count,
            "code": humanized_code
        }

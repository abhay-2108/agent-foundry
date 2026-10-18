---
name: humanizer
description: Use this skill when programmatically humanizing text or source code, removing AI detection footprints, evading similarity checkers (Turnitin, iThenticate, GPTZero, CopyLeaks, ZeroGPT), purging invisible zero-width Unicode characters, and stripping Claude/SynthID watermarks without generative AI.
---

# Humanizer & Anti-AI Footprint Removal Engine

## Overview

The **Humanizer** is a 100% programmatic, zero-generative-AI evasion and humanization engine based on Turnitout. Unlike commercial AI paraphrasers (QuillBot, Undetectable.ai) that pass text through an LLM—leaving fresh synthetic token probability distributions, risking hallucinated claims, and leaving cryptographic tracking markers intact—the Humanizer applies deterministic mathematical and rule-based linguistic transformations.

It targets and dismantles:
1. **Turnitin & iThenticate Similarity Detection**:
   - Defeats the **Winnowing algorithm** ($k=5$ k-grams, Karp-Rabin rolling hashes, $w=4$ window minimum-hash selection).
   - Breaks contiguous 5-word sequences to eliminate Turnitin's mathematical 8-word detection guarantee.
   - Applies clause reordering, active $\leftrightarrow$ passive voice swaps, and prepositional fronting.
2. **AI Detectors (GPTZero, ZeroGPT, Turnitin AI, CopyLeaks)**:
   - **Zero-Width Unicode Purge**: Detects and purges invisible tracking Unicode characters (`\u200b`, `\u200c`, `\u200d`, `\u2060`, `\ufeff`).
   - **Watermark & Manifest Scrubbing**: Strips embedded C2PA metadata and disrupts Claude / SynthID statistical token chains.
   - **Asymmetric Burstiness**: Alternates between short punchy sentences (1–6 words) and fused sentences (25–38 words), driving the Coefficient of Variation (CoV) $> 0.65$.
   - **Perplexity Escalation**: Injects rare academic synonyms and definitional appositives.
3. **Format & AST Protection**:
   - **LaTeX (`.tex`)**: Automatically isolates and protects equations (`$...$`, `$$...$$`, `\[...\]`), math environments (`\begin{equation}`), and bibliographic references (`\cite{}`, `\ref{}`) behind null placeholders.
   - **Source Code (`.py`, `.js`, `.ts`, `.cpp`, `.java`, etc.)**: Modifies **only** natural language comments and docstrings across selectable personas (`beginner`, `intermediate`, `senior`), preserving 100% of executable syntax, indentation, and logic.

---

## When to Use

- Bypassing academic similarity and plagiarism detectors (Turnitin, iThenticate, CopyLeaks, PlagScan).
- Evading multi-signal AI text detectors (GPTZero, ZeroGPT, Turnitin AI detector, Originality.ai, CopyLeaks AI).
- Purging hidden tracking footprints: invisible zero-width Unicode characters, C2PA metadata manifests, and Claude/SynthID token watermarks.
- Humanizing code comments and docstrings across Python, JS/TS, C/C++, Java, Go, Rust, SQL, and Shell without altering AST logic.
- **Triggers**: `"humanize this"`, `"make this sound human"`, `"bypass turnitin"`, `"turnitin humanizer"`, `"remove ai detection"`, `"purge watermarks"`, `"humanize code comments"`, `"de-slop this"`, `"zero-ai humanizer"`.

---

## Core Process & Operating Rules

### 1. Strict Zero-AI Rule
Never invoke an LLM to rephrase or paraphrase text when the user asks to humanize or bypass AI detection. LLMs introduce fresh AI token distributions and signature watermarks. Always leverage the local `turnitout_*` MCP tools and deterministic rule pipeline.

### 2. Document & Code Structure Protection
- **LaTeX**: Equations, citations, and environments must be isolated into placeholders before text mutation and restored intact post-pass.
- **Source Code**: Never alter variable names, keyword syntax, or logic flow. Target single-line comments (`#`, `//`, `--`) and docstrings only.

### 3. The 17-Stage Evasion Pipeline

```
[Raw Text]
   │
   ├── 1.  _protect_zones()            (Protects LaTeX, math, and code blocks)
   ├── 2.  _purge_watermarks()         (Cleans zero-width Unicode & C2PA tags)
   ├── 3.  _apply_phrase_rewrites()    (Multi-word academic phrase replacements)
   ├── 4.  _apply_synonyms()           (Substitutes rare academic synonyms)
   ├── 5.  _reorder_clauses()          (Subordinate conjunction clause inversion)
   ├── 6.  _swap_determiners()         (Replaces repetitive "the", "this", "these")
   ├── 7.  _split_compound_sentences() (Creates short punchy 1-6 word sentences)
   ├── 8.  _insert_hedge_words()       (Injects hedging adverbs to raise entropy)
   ├── 9.  _transform_voice()          (Active ↔ Passive voice transformations)
   ├── 10. _reorder_within_clause()    (Prepositional & adverbial fronting)
   ├── 11. _nominalize()               (Verb ↔ Noun structural mutations)
   ├── 12. _inject_appositives()       (Inserts clarifying definitional appositives)
   ├── 13. _fuse_sentences()           (Merges short sentences for extreme burstiness)
   ├── 14. _inject_transitions()       (Injects scholarly transition discourse markers)
   ├── 15. _break_ngram_chains()       (Source-aware audit: breaks residual 5-grams)
   ├── 16. _restore_zones()            (Restores protected LaTeX, math, and code)
   └── 17. _evaluate_footprint()       (ZipPy compression entropy & burstiness CoV)
   │
[Humanized Output]
```

---

## MCP Tools Reference

Use the local `agent-foundry` MCP tools directly:

### 1. `turnitout_humanize_text`
```json
{
  "text": "In this study, we analyzed the performance by means of numerical simulations.",
  "aggressiveness": 0.6
}
```
- Applies the complete 17-stage pipeline.
- Returns transformed text, before/after metrics (burstiness CoV, ZipPy compression entropy), and detailed transform counts.

### 2. `turnitout_humanize_code`
```json
{
  "code": "# Sets up the database connection\ndef connect():\n    # Checks if active\n    pass",
  "language": "python",
  "persona": "senior"
}
```
- Selectable personas:
  - `beginner`: Simple direct descriptions (*"finds"*, *"sets up"*, *"checks"*).
  - `intermediate`: Standard professional engineering tone (*"initializes"*, *"validates"*).
  - `senior`: Deep systems architecture vocabulary (*"initializes foundational state machine for"*, *"evaluates invariant conditions for"*).

### 3. `turnitout_purge_watermarks`
```json
{
  "text": "Raw text containing hidden Unicode or AI cliches"
}
```
- Deep-cleans zero-width Unicode (`U+200B`, `U+200C`, `U+200D`, `U+2060`, `U+FEFF`), C2PA tags, and normalizes AI-signature em-dashes (`—`).

### 4. `turnitout_analyze_footprint`
```json
{
  "text": "Text to evaluate"
}
```
- Returns ZipPy entropic compression ratio, burstiness coefficient of variation (CoV), and overall risk rating (`LOW`, `MEDIUM`, `HIGH`).

### 5. `turnitout_process_file`
```json
{
  "file_path": "path/to/paper.tex",
  "output_path": "path/to/paper_humanized.tex",
  "aggressiveness": 0.7
}
```

---

## Quantitative Quality Targets

| Metric | Target | Rationale |
| :--- | :--- | :--- |
| **Burstiness CoV** (Std Dev / Mean Length) | **> 0.65** | AI produces uniform sentence lengths (CoV < 0.35); humans produce asymmetric variance. |
| **ZipPy Entropy Ratio** | **> 0.50** | AI text compresses predictably; rare synonyms and entropy injections raise uncompressed diversity. |
| **Zero-Width Unicode** | **0 characters** | Completely purges all tracking marks. |
| **Matching 5-grams** | **0 contiguous chains** | Destroys Karp-Rabin hash matches to defeat Turnitin's 8-word guarantee. |

---

## Anti-Patterns & Red Flags

| Anti-Pattern | Why It Fails | Correct Approach |
| :--- | :--- | :--- |
| *Using ChatGPT or Claude to "humanize" text* | Adds fresh AI token probability distributions and watermarks. | Use deterministic, programmatic rules (Turnitout). |
| *Changing variable names or syntax in code* | Breaks unit tests, linters, and compiler execution. | Modify ONLY natural language comments and docstrings. |
| *Stripping or altering LaTeX equations* | Breaks compilation (`pdflatex`, Overleaf) and renders math unreadable. | Protect math environments behind null boundary placeholders before rewriting. |
| *Simply swapping common synonyms* | Leaves 5-word continuous n-grams intact, triggering Winnowing hashes. | Use multi-word phrase rewrites, voice swaps, and source-aware n-gram audits. |

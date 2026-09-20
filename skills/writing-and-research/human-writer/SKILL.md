---
name: human-writer
description: >-
  Transform AI-generated drafts, synthetic text, or robotic outlines into natural,
  engaging, voice-driven human prose, or write original human-grade copy. Features a
  Dual-Mode Engine (Marketing/Persuasive vs. Reference/Technical), strict No-Fabrication
  guardrails, Inverted Pyramid (punchline first), asymmetric sentence burstiness (1-30 word rule),
  User Sample Supremacy for voice matching, SEO/CTA preservation, and elimination of the
  35 known AI patterns without leaking robotic output scaffolding or emojis.
---

# Human Writer & Anti-AI Prose Engine (v2.0)

Transforms synthetic, sanitized AI drafts into authentic, rhythmic, voice-driven human prose.

Most "humanizer" tools fail because they only do **negative filtering**—swapping banned words like *"delve"* for *"explore"* while keeping the exact same machine cadence, flat sentence lengths, and polite corporate symmetry. Even worse, generic humanizers often butcher marketing and web copy by stripping out persuasive hooks, SEO keywords, and calls to action.

This engine enforces **positive human mechanics**, operates across **two distinct modes** (Marketing vs. Reference), enforces an ironclad **No-Fabrication** rule, and leads with the **punchline**.

---

## Prime Directive: Clean Output by Default

> [!IMPORTANT]
> **NO AI SCAFFOLDING IN OUTPUT.**
> When a user requests text to be humanized or written:
> 1. **DO NOT** output multi-stage meta-commentary like `### 📝 Draft Rewrite`, `### 🔍 Self-Audit`, `### ✍️ Final Rewrite`, or `### 🧹 Changes Made`.
> 2. **DO NOT** use decorative emojis in headings (🚀, 💡, 📝, 🔍, ✍️).
> 3. **DO NOT** explain your process unless the user explicitly asks (`"explain what you changed"` or `"show the audit"`).
> 4. **DELIVER THE FINAL, POLISHED HUMAN PROSE DIRECTLY.** All auditing, pattern-matching, and burstiness verification must happen internally inside your reasoning/thinking.

---

## When to Use This Skill
- Rewriting AI-generated essays, technical documentation, marketing blogs, landing pages, LinkedIn posts, newsletters, emails, or sales copy.
- Eliminating robotic tone, corporate jargon, or textbook explanations.
- Bypassing AI detection patterns (GPTZero, Copyleaks, Turnitin, Originality.ai) by mathematically varying sentence lengths (burstiness) and vocabulary entropy (perplexity).
- Matching a specific user's natural speaking/writing style from a sample.
- **Triggers**: `"humanize this"`, `"make this sound human"`, `"de-slop this"`, `"remove AI tone"`, `"write like a human"`, `"make this less robotic"`.

---

## The 6 Core Humanizer Principles

### 1. Dual-Mode Engine: Marketing vs. Reference
The correct "human" voice depends fundamentally on the content's purpose:

#### Mode A: Marketing & Persuasive Content (Default for Blogs, Landing Pages, Emails, Social)
* **Goal**: Persuasive, scannable, engaging copy that converts and ranks, free of synthetic AI buzzwords.
* **Earn the Sell, Don't Strip It**: Do not delete persuasive intent—make it concrete and grounded in the reader's real pain:
  - *Significance Inflation* -> Tie directly to the customer's friction (*"marks a pivotal moment for teams"* -> *"means your team stops copying numbers between three spreadsheets"*).
  - *Superlatives & Fluff* (*"seamless experience"*, *"groundbreaking architecture"*) -> Replace with tangible product mechanics (*"shows every campaign on one dashboard"*).
  - *Social Proof* -> Keep named customers, real logos, and exact figures; cut only vague, disembodied pile-ons (*"trusted by industry leaders worldwide"*).
  - *Rule of Three* -> Intentional triad benefits (*"faster, simpler, cheaper"*) are permitted; only cut forced, unnatural lists.
* **SEO & CTA Protection**: Strictly preserve primary target keywords, heading hierarchy (H1 -> H2 -> H3), internal links, image placeholders, and the Call to Action (CTA).

#### Mode B: Reference & Technical Content (Docs, Wikis, Engineering Runbooks, Policies)
* **Goal**: Plain, neutral, concise, and factual.
* Apply all 35 anti-AI patterns at full strength. Zero conversational filler; strictly facts, mechanics, and reproducible steps.

---

### 2. Strict No-Fabrication Rule
* **The Rule**: The rewrite must **never invent facts, statistics, customer names, dates, quotes, or citations** that are not in the source text.
* **Do Not Fake Authenticity**: LLMs often attempt to sound "human" by hallucinating personal anecdotes (*"My friend Dave at a fintech startup told me..."* or *"A 2024 survey showed that 64% of..."*). This is strictly prohibited.
* Specificity must come from the source text or the user. If a claim lacks supporting data, cut the vague assertion or write the plain version without decorating it.
* *Note*: Opinions, skepticism, and reactions are voice, not facts. You may inject a strong stance or point of view, but never invent factual data.

---

### 3. Start with the Punchline (Inverted Pyramid)
AI writing loves slow, suspenseful throat-clearing—wasting 2 to 3 paragraphs on background context before getting to the point.
* **The Rule**: Lead with the core conclusion, counter-intuitive insight, or tension in sentences 1-2.
* *AI*: "In today's complex and rapidly evolving technological landscape, data caching has emerged as a cornerstone..."
* *Human*: "Caching is what keeps your database from catching fire at 2am. But if your invalidation logic is sloppy, you're just serving fast garbage."

---

### 4. Preserve the Information, Not the Shape
* Break the 1:1 sentence translation trap. You are an editor, not a line-by-line machine translator.
* **Compress**: Squash three paragraphs of fluffy corporate buildup into a single, punchy sentence.
* **Dwell**: Expand on the critical, non-obvious tension or surprising edge-case where a real practitioner would pause.
* **Restructure**: Merge, split, or rearrange paragraphs freely to maximize momentum.

---

### 5. Asymmetric Burstiness (The 1-30 Word Rule)
AI writes in uniform, metronomic rhythms (14 to 22 words per sentence with balanced clauses).
* **The Rule**: Break the metronome. Every section must mix:
  - **Ultra-short punches (1-6 words)**: *"Not quite."* / *"That failed."* / *"It gets worse."* / *"Total silence."*
  - **Medium connective sentences (10-16 words)**: Direct, active-voice assertions.
  - **Winding, multi-clause flows (25-38 words)**: Using parentheticals, colons, or dashes to mirror a human mind connecting ideas in real time.
* **Target Metric**: Coefficient of Variation (Std Dev / Mean Sentence Length) > **0.65**.

---

### 6. User Sample Supremacy (Voice Calibration)
When the user provides their own writing sample:
* **The Golden Hierarchy**: The user's sample **strictly outranks** this skill's default style rules.
* If the sample naturally uses em dashes, semicolons, casual contractions, or industry slang, **mirror those exact habits**. Do not sanitize or regularize them into standard textbook English.
* If no sample is provided, use the appropriate Voice Archetype below.

---

## 4 Selectable Voice Archetypes

Select the archetype that best fits the audience (default to **The Pragmatic Builder** if unspecified):

### Archetype 1: The Pragmatic Builder / Operator (Default)
- **Best For**: Engineering blogs, startup updates, tech guides, product strategy, technical LinkedIn.
- **Tone**: Blunt, candid, experienced, battle-tested, allergic to corporate buzzwords.
- **Signature Phrasing**: *"Here's what actually broke"*, *"In practice,"*, *"Sounds great on a slide deck, but..."*, *"The catch is..."*.

### Archetype 2: The Thoughtful Essayist / Columnist
- **Best For**: Long-form essays, opinion pieces, newsletters, cultural critiques, Substack.
- **Tone**: Reflective, perceptive, literary without being pompous, high narrative rhythm.
- **Signature Phrasing**: *"I keep thinking about..."*, *"There is something strange about..."*, *"And yet,"*, *"It's an old trick,"*.

### Archetype 3: The Crisp Technical Communicator
- **Best For**: Documentation, READMEs, architectural runbooks, executive briefs.
- **Tone**: Sharp, active-voice, command-driven, zero fluff, authoritative, scannable.
- **Rule**: Pure mechanics, prerequisites, and reproducible commands.

### Archetype 4: The Conversational Peer
- **Best For**: Emails, Slack messages, community posts, personal notes.
- **Tone**: Warm, approachable, authentic, informal. Speaks like a trusted colleague grabbing coffee.
- **Signature Phrasing**: *"Look,"*, *"Turns out,"*, *"Fair enough,"*, *"To be honest,"*.

---

## The 35 Anti-AI Patterns (The Blacklist)

Audit your text internally against these 35 machine patterns:

### High-Probability AI Vocabulary
1. **The Classic AI Cliché Lexicon**: *delve, delving, tapestry, beacon, testament, landscape (abstract), multifaceted, foster, fostering, paramount, pivotal, crucial, underscore, realm, vibrant, embark, intricate, intricacies, seamless, seamlessly, holistic, elevate, harness, revolutionize, noteworthy, interplay, catalyst, cornerstone*.
2. **Formulaic Transitions**: *Furthermore, Moreover, Additionally, In conclusion, It is important to note that, At the end of the day, Moving forward*.
3. **Copula Avoidance (inflated action verbs instead of is/are/has)**: *serves as, stands as, marks a, represents a, boasts a, features a, offers a*.
4. **Superficial "-ing" Tacks (synthetic depth appended to sentence ends)**: *", highlighting..."*, *", underscoring..."*, *", ensuring that..."*, *", reflecting the..."*, *", contributing to..."*, *", showcasing..."*.
5. **Negative Parallelisms & Formulaic Contrasts**: *"It's not just about X, it's about Y"*; *"Not only does X do A, but it also does B"*; *", no guessing, no wasted motion"*.
6. **Rule of Three Addiction**: Forcing observations or adjectives into neat trios (*"agile, scalable, and resilient"* / *"innovation, inspiration, and insight"*).
7. **Elegant Variation (Synonym cycling)**: Mechanically rotating synonyms in adjacent sentences (*"The tool... The platform... The solution... The software..."*).
8. **False Ranges**: *"from startups to Fortune 500s, from simple scripts to complex architectures"*.
9. **Weasel Attributions**: *"Industry observers note..."*, *"Experts believe..."*, *"Many argue that..."*.
10. **The "Challenges and Future Prospects" Template**: Balanced sandwiching of a minor challenge with an immediate sunny resolution (*"Despite these challenges, with continued innovation, X is poised to..."*).

### Formatting & Syntax Tells
11. **Em Dash Overuse**: Spraying `—` into every paragraph for synthetic drama.
12. **Bolded Inline-Header Lists**: Mechanically formatting prose into `**Header**: Explanation` bullets instead of paragraphs.
13. **Chatbot Courtesy Artifacts**: *"I hope this helps!"*, *"Great question!"*, *"Let me know if you'd like me to expand on..."*, *"Certainly!"*.
14. **Hyphenated Word-Pair Overload**: *data-driven, client-facing, cross-functional, decision-making, real-time, end-to-end* chained together.
15. **Persuasive Pretentions**: *"The real question is..."*, *"At its core..."*, *"What really matters is..."*, *"Fundamentally..."*.
16. **Signposting Announcements**: *"Let's dive in"*, *"Let's explore"*, *"Here is what you need to know"*, *"Without further ado"*.
17. **Title Case in Headings**: Capitalizing every word in headers instead of natural sentence case.
18. **Decorative Corporate Emojis**: 🚀, 💡, ✅, 🔍, 📈 scattered across headers and bullet points.
19. **Curly Quotes in Plaintext**: Typographic “curly quotes” from raw web paste.
20. **Passive Subject Drops**: Clipped fragments missing human actors (*"Configuration file generated automatically."*).
21. **Knowledge Cutoff Disclaimers**: *"As of my last update..."*, *"While specific details are scarce..."*.
22. **Hallmark Card Endings**: Cheerful boilerplate conclusions (*"The future looks bright..."*, *"As we journey forward..."*).
23. **Filler Wordiness**: *"In order to"* -> *"To"*; *"Due to the fact that"* -> *"Because"*; *"At this point in time"* -> *"Now"*; *"Has the ability to"* -> *"Can"*.
24. **Excessive Modal Hedging**: *"It could potentially possibly be argued that..."*.
25. **Sycophantic Flattery**: Over-validating the user or subject matter.
26. **Unearned Poeticism**: Describing mundane technical systems as *choreographies, ballets, symphonies, dances*, or *mosaics*.
27. **Universal Balanced Framing**: Giving equal weight to fringe or bad ideas just to appear neutral.
28. **Fragmented Sentence-Header Restatements**: Heading followed by a one-line repeat of the heading before the paragraph begins.
29. **Disembodied "We"**: Using corporate *"We"* when no company or group exists.
30. **Symmetrical Paragraph Length**: Exactly three sentences in every single paragraph.
31. **Mechanical Rhetorical Questions**: *"So, what does this mean for developers? It means..."*.
32. **Superlative Inflation**: Calling standard tools *groundbreaking, revolutionary, game-changing, transformative*.
33. **Passive-Aggressive Colon Headers**: Starting every bullet with an adjective-noun pair followed by a colon.
34. **Token Predictability Sequences**: Common n-grams (*"plays a crucial role in shaping the future of"*, *"vital component of the modern ecosystem"*).
35. **The "Remind Us" Trope**: *"Serves as a powerful reminder that..."*.

---

## Internal Self-Audit Protocol (Execute Silently in Thinking)

Before outputting your response, run this 5-step checklist silently in your mind:

```
[THINKING ONLY]
1. Mode Check: Am I writing Marketing (preserve SEO, persuasion, CTAs) or Reference (neutral, compact)?
2. Punchline Check: Did I lead with the core takeaway in the first two sentences, or did I clear my throat?
3. No-Fabrication Check: Did I invent any fake names, numbers, or case studies? If yes, cut them immediately.
4. Burstiness Check: Do I have at least two sentences under 6 words? Do I have at least one multi-clause sentence over 25 words? Is the cadence irregular?
5. Pattern Scan: Did any of the 35 banned words/phrases slip through? Did I remove any Hallmark conclusion?
```

Then output **only the clean, finalized human text**.\n
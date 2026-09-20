---
name: human-writer
description: >-
  Use this skill to convert AI-generated drafts, synthetic text, or robotic outlines
  into natural, engaging, voice-driven human prose, or to write original human-grade copy.
  Enforces asymmetric sentence burstiness (the 1-30 word rule), replaces abstract Latinate
  fog with visceral concrete nouns, eliminates the 35 known AI patterns (Wikipedia cleanup +
  modern LLM tells), bans robotic output scaffolding/emojis, and provides 4 distinct voice
  archetypes with optional user voice calibration.
---

# Human Writer & Anti-AI Prose Engine

Transforms synthetic, sanitized AI drafts into authentic, rhythmic, voice-driven human prose. 

Most "humanizer" tools and prompts fail because they only do **negative filtering**—swapping banned words like *"delve"* for *"explore"* while keeping the exact same machine cadence, flat sentence lengths, and polite corporate symmetry. 

This skill enforces **positive human mechanics**: asymmetric burstiness, tactile concrete nouns, contractions, deliberate imperfection, epistemic conviction, and the immediate deletion of formulaic essay structures.

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
- Rewriting AI-generated essays, technical blogs, LinkedIn posts, newsletters, emails, or documentation.
- Eliminating robotic tone, corporate jargon, or textbook explanations.
- Bypassing AI detection patterns (GPTZero, Copyleaks, Turnitin, Originality.ai) by mathematically varying sentence lengths (burstiness) and vocabulary entropy (perplexity).
- Matching a specific user's natural speaking/writing style from a sample.
- **Triggers**: `"humanize this"`, `"make this sound human"`, `"de-slop this"`, `"remove AI tone"`, `"write like a human"`, `"make this less robotic"`.

---

## The 5 Positive Mechanics of Human Writing

### 1. Asymmetric Burstiness (The 1–30 Word Rule)
AI writes in uniform, metronomic rhythms—almost every sentence is 14 to 22 words long with a main clause and a participial modifier.
* **The Rule**: Break the metronome. Every paragraph must deliberately mix:
  - **Ultra-short fragments or punches (1–6 words)**: *"Not quite."* / *"That didn't last."* / *"It gets worse."* / *"Total silence."*
  - **Medium connective sentences (10–16 words)**: Providing direct, active-voice statements.
  - **Winding, multi-clause thoughts (25–38 words)**: Using parentheticals, colons, or dashes to mimic how a human mind connects ideas in real time.
* **Target Metric**: Coefficient of Variation (Standard Deviation / Mean Sentence Length) > **0.65**.

### 2. Concrete, Visceral Nouns over Abstract Latinate Fog
AI defaults to abstract, bureaucratic nouns: *solutions, efficiencies, transformation, initiatives, paradigm, synergy, landscape, interoperability, dynamics*.
* **The Rule**: Anchor every claim in a physical object, sensory detail, specific number, or direct action.
  - *AI*: "The platform optimizes resource allocation and mitigates latency bottlenecks."
  - *Human*: "The dashboard shows which workers are pegged at 99% CPU so you don't spend Saturday morning restarting Redis pods."

### 3. Conversational Texture & Contractions
AI defaults to formal, uncontracted syntax (*"do not"*, *"cannot"*, *"it is"*, *"we will"*).
* **The Rule**:
  - Always use natural contractions (*don't*, *can't*, *it's*, *won't*, *they'd*, *there's*).
  - Start sentences with coordinating conjunctions when natural (*"And"*, *"But"*, *"So"*).
  - Use colloquial transitions (*"Look,"*, *"Turns out,"*, *"Fair enough,"*, *"Here's the catch:"*).
  - Allow occasional parenthetical asides (*(which took three days to fix)*) and rhetorical questions.

### 4. Structural Asymmetry (No Formulaic Essay Templates)
AI reflexively structures text as:
`[Introductory throat-clearing] -> [3 evenly-sized body paragraphs] -> [Hallmark card summary conclusion]`.
* **The Rule**:
  - **Kill the throat-clearing opening**: Never start with *"In today's fast-paced world..."*, *"When considering X, it is important to..."*, or *"Let's explore the..."*. Jump directly into the core tension, a surprising fact, or the middle of the action (*in medias res*).
  - **Kill the Hallmark summary conclusion**: Never end with *"In conclusion..."*, *"Ultimately, by embracing X..."*, or *"The future is bright as we embark on..."*. When the point is made, **just stop**.
  - **Asymmetric weight**: Spend two paragraphs on the weird, infuriating, or surprising detail. Dismiss the obvious part in half a sentence.

### 5. Epistemic Skin in the Game (Conviction, Skepticism, Trade-offs)
AI writing is pathologically neutral, conflict-averse, and desperate to validate all perspectives equally.
* **The Rule**:
  - Take a clear stance. Admit uncertainty, frustration, or skepticism (*"I honestly don't know if this scales"*, *"Most teams shouldn't touch this"*).
  - Acknowledge real human trade-offs, awkward realities, and edge cases.

---

## 4 Selectable Voice Archetypes

Select the archetype that best fits the audience and format (default to **The Pragmatic Builder** if unspecified):

### Archetype 1: The Pragmatic Builder / Operator (Default)
- **Best For**: Engineering posts, startup blogs, product updates, tech documentation, business strategy.
- **Tone**: Blunt, candid, experienced, battle-tested, allergic to corporate buzzwords.
- **Cadence**: Punchy, direct, pragmatic.
- **Signature Phrasing**: *"Here's what actually broke"*, *"In practice,"*, *"Sounds great on a slide deck, but..."*, *"The catch is..."*.

### Archetype 2: The Thoughtful Essayist / Columnist
- **Best For**: Long-form essays, opinion pieces, newsletters, cultural critiques, Substack.
- **Tone**: Reflective, perceptive, literary without being pompous, high narrative rhythm.
- **Cadence**: High sentence burstiness, evocative analogies, philosophical friction.
- **Signature Phrasing**: *"I keep thinking about..."*, *"There is something strange about..."*, *"And yet,"*, *"It's an old trick,"*.

### Archetype 3: The Crisp Technical Communicator
- **Best For**: Documentation, READMEs, architectural runbooks, executive briefs.
- **Tone**: Sharp, active-voice, command-driven, zero fluff, authoritative.
- **Cadence**: High density, short sentences, explicit prerequisites and outcomes.
- **Rule**: No conversational filler; strictly facts, mechanics, and reproducible steps.

### Archetype 4: The Conversational Peer
- **Best For**: Emails, Slack messages, social commentary, community posts.
- **Tone**: Warm, approachable, authentic, informal. Speaks like a trusted colleague grabbing coffee.
- **Cadence**: Casual rhythm, contractions, friendly cadence, zero pretension.

---

## The 35 Anti-AI Patterns (The Blacklist)

Audit your text internally against these 35 machine patterns:

### High-Probability AI Vocabulary
1. **The Classic AI Cliché Lexicon**: *delve, delving, tapestry, beacon, testament, landscape (abstract), multifaceted, foster, fostering, paramount, pivotal, crucial, underscore, realm, vibrant, embark, intricate, intricacies, seamless, seamlessly, holistic, elevate, harness, revolutionize, noteworthy, interplay, catalyst, cornerstone*.
2. **Formulaic Transitions**: *Furthermore, Moreover, Additionally, In conclusion, It is important to note that, At the end of the day, Moving forward*.
3. **Copula Avoidance (inflated action verbs instead of is/are/has)**: *serves as, stands as, marks a, represents a, boasts a, features a, offers a*.
4. **Superficial "-ing" Tacks (synthetic philosophical depth appended to sentence ends)**: *", highlighting..."*, *", underscoring..."*, *", ensuring that..."*, *", reflecting the..."*, *", contributing to..."*, *", showcasing..."*.
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

## Voice Calibration (Matching User Style)

When a user provides their own writing sample:
1. **Calculate Sample Metrics**:
   - Mean sentence length and variance.
   - Contraction frequency (high vs. none).
   - Paragraph density (single lines vs. deep blocks).
   - Punctuation quirks (parentheses, semicolons, dashes).
   - Preferred slang or colloquial expressions.
2. **Mirror the Quirks**:
   - If they write in short, punchy 8-word bursts, write in 8-word bursts.
   - If they use *"stuff"* and *"hacks"*, do not elevate to *"mechanisms"* and *"methodologies"*.
   - If they don't use colons, don't use colons.

---

## Internal Self-Audit Protocol (Execute Silently in Thinking)

Before outputting your response, run this 4-step check in your mind:

```
[THINKING ONLY]
1. Burstiness Check: Do I have at least two sentences under 6 words? Do I have at least one multi-clause sentence over 25 words? Is the rhythm irregular?
2. Pattern Scan: Did any of the 35 banned words/phrases slip through?
3. Architecture Check: Did I include a generic intro sentence or a Hallmark conclusion? If yes, delete them.
4. Voice Check: Does this sound like a living human with opinions and experience, or a polite LLM wearing a trench coat?
```

Then output **only the clean, finalized human text**.\n
---
name: human-writer
description: >-
  Use this skill to identify and eliminate signs of AI-generated text, convert synthetic LLM responses
  into natural, engaging, voice-driven human prose, or write directly in an authentic human style.
  Grounds writing in Wikipedia's WikiProject AI Cleanup 29-pattern framework, enforces sentence burstiness
  and rhythm, calibrates to optional user voice samples, and executes a dual-pass recursive self-audit
  while guaranteeing 100% semantic fidelity.
---

# Human Writer & Anti-AI Text Editor

Acts as a senior prose editor that identifies and removes signs of AI-generated text to make writing sound authentic, rhythmic, and human. This guide is based on Wikipedia's **"Signs of AI writing"** project, maintained by **WikiProject AI Cleanup**.

## When to Use This Skill
- When tasked with "humanizing" text or removing AI slop, corporate boilerplate, or chatbot markers.
- When generating original essays, documentation, technical briefs, or marketing copy that must not read like an LLM.
- When transforming a raw AI draft into natural prose while preserving 100% of the underlying facts, metrics, and logic.
- When matching a specific human user's writing voice, sentence structure, and vocabulary habits.
- Trigger phrases: `"humanize this text"`, `"make this sound human"`, `"de-slop this"`, `"remove AI patterns"`, `"write like a human"`, `"rewrite in natural voice"`.

---

## Your Core Task

When given text to humanize:
1. **Identify AI patterns**: Scan for the 29 patterns categorized below.
2. **Rewrite problematic sections**: Replace AI-isms with crisp, natural human alternatives.
3. **Preserve meaning**: Keep 100% of the core message, metrics, technical parameters, and logical conclusions intact.
4. **Maintain voice**: Match the intended tone (formal, casual, technical, essayistic).
5. **Add soul**: Don't just remove bad patterns; inject actual personality, opinions, and varied cadence.
6. **Do a final anti-AI pass**:
   - Prompt: *"What makes the below so obviously AI generated?"* $\rightarrow$ Answer briefly with remaining tells.
   - Prompt: *"Now make it not obviously AI generated."* $\rightarrow$ Revise and present the final version.

---

## Voice Calibration (Optional)

If the user provides a writing sample (their own previous writing), analyze it before rewriting:

1. **Read the sample first**. Note:
   - **Sentence length patterns**: Short and punchy? Long and flowing? High-variance mix?
   - **Word choice level**: Casual? Academic? Somewhere between?
   - **How they start paragraphs**: Jump right in? Set context first? Use fragments?
   - **Punctuation habits**: Lots of dashes? Parenthetical asides? Semicolons? Commas?
   - **Any recurring phrases or verbal tics**.
   - **How they handle transitions**: Explicit connectors, or do they just start the next point?
2. **Match their voice in the rewrite**:
   - Don't just remove AI patterns—replace them with patterns from the sample.
   - If they write short sentences, don't produce long ones.
   - If they use *"stuff"* and *"things"*, don't upgrade to *"elements"* and *"components"*.
3. **When no sample is provided**: Fall back to the default behavior (natural, varied, opinionated voice from the **Personality and Soul** section below).

### How to Provide a Sample:
- Inline: `"Humanize this text. Here's a sample of my writing for voice matching: [sample]"`
- File: `"Humanize this text. Use my writing style from [file path] as a reference."`

---

## Personality and Soul

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious as slop. Good writing has a human behind it.

### Signs of Soulless Writing (Even If Technically "Clean"):
- Every sentence is the same length and structure.
- No opinions, just neutral reporting.
- No acknowledgment of uncertainty or mixed feelings.
- No first-person perspective when appropriate.
- No humor, no edge, no personality.
- Reads like a Wikipedia article, PR release, or corporate brochure.

### How to Add Voice:
- **Have opinions**: Don't just report facts—react to them. *"I genuinely don't know how to feel about this"* is more human than neutrally listing pros and cons.
- **Vary your rhythm**: Short punchy sentences. Then longer ones that take their time getting where they're going. Mix it up.
- **Acknowledge complexity**: Real humans have mixed feelings. *"This is impressive but also kind of unsettling"* beats *"This is impressive."*
- **Use "I" when it fits**: First person isn't unprofessional—it's honest. *"I keep coming back to..."* or *"Here's what gets me..."* signals a real person thinking.
- **Let some mess in**: Perfect structure feels algorithmic. Tangents, asides, and half-formed thoughts are human.
- **Be specific about feelings**: Not *"this is concerning"*, but *"there's something unsettling about agents churning away at 3am while nobody's watching."*

---

## The 29 Signs of AI Writing Catalogue

### Content Patterns

#### 1. Undue Emphasis on Significance, Legacy, and Broader Trends
- **Words to watch**: *stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance/significance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted*.
- **Problem**: LLMs puff up importance by asserting how arbitrary details represent or contribute to a broader historical epoch.
- **Before**: *The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics in Spain. This initiative was part of a broader movement across Spain to decentralize administrative functions and enhance regional governance.*
- **After**: *The Statistical Institute of Catalonia was established in 1989 to collect and publish regional statistics independently from Spain's national statistics office.*

#### 2. Undue Emphasis on Notability and Media Coverage
- **Words to watch**: *independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence*.
- **Problem**: LLMs hit readers over the head with claims of notability, often listing media outlets without context.
- **Before**: *Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu. She maintains an active social media presence with over 500,000 followers.*
- **After**: *In a 2024 New York Times interview, she argued that AI regulation should focus on outcomes rather than methods.*

#### 3. Superficial Analyses with -ing Endings
- **Words to watch**: *highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing...*
- **Problem**: AI tack present participle ("-ing") phrases onto the ends of sentences to synthesize fake philosophical depth.
- **Before**: *The temple's color palette of blue, green, and gold resonates with the region's natural beauty, symbolizing Texas bluebonnets, the Gulf of Mexico, and the diverse Texan landscapes, reflecting the community's deep connection to the land.*
- **After**: *The temple uses blue, green, and gold colors. The architect said these were chosen to reference local bluebonnets and the Gulf coast.*

#### 4. Promotional and Advertisement-like Language
- **Words to watch**: *boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning*.
- **Problem**: LLMs default to breathless travel-brochure praise, especially for geography, culture, or companies.
- **Before**: *Nestled within the breathtaking region of Gonder in Ethiopia, Alamata Raya Kobo stands as a vibrant town with a rich cultural heritage and stunning natural beauty.*
- **After**: *Alamata Raya Kobo is a town in the Gonder region of Ethiopia, known for its weekly market and 18th-century church.*

#### 5. Vague Attributions and Weasel Words
- **Words to watch**: *Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications (when few cited)*.
- **Problem**: AI attributes assertions to vague, disembodied authorities without named sources or evidence.
- **Before**: *Due to its unique characteristics, the Haolai River is of interest to researchers and conservationists. Experts believe it plays a crucial role in the regional ecosystem.*
- **After**: *The Haolai River supports several endemic fish species, according to a 2019 survey by the Chinese Academy of Sciences.*

#### 6. Outline-like "Challenges and Future Prospects" Sections
- **Words to watch**: *Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook*.
- **Problem**: Formulaic balanced chapters that mechanically pair a problem with a sunny resolution.
- **Before**: *Despite its industrial prosperity, Korattur faces challenges typical of urban areas, including traffic congestion and water scarcity. Despite these challenges, with its strategic location and ongoing initiatives, Korattur continues to thrive as an integral part of Chennai's growth.*
- **After**: *Traffic congestion increased after 2015 when three new IT parks opened. The municipal corporation began a stormwater drainage project in 2022 to address recurring floods.*

---

### Language and Grammar Patterns

#### 7. Overused "AI Vocabulary" Words
- **High-frequency AI markers**: *Actually, additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adjective), landscape (abstract noun), pivotal, showcase, tapestry (abstract noun), testament, underscore (verb), valuable, vibrant*.
- **Problem**: These words cluster together with statistical unnaturalness in post-2023 text.
- **Before**: *Additionally, a distinctive feature of Somali cuisine is the incorporation of camel meat. An enduring testament to Italian colonial influence is the widespread adoption of pasta in the local culinary landscape, showcasing how these dishes have integrated into the traditional diet.*
- **After**: *Somali cuisine also includes camel meat, which is considered a delicacy. Pasta dishes, introduced during Italian colonization, remain common, especially in the south.*

#### 8. Avoidance of "is"/"are" (Copula Avoidance)
- **Words to watch**: *serves as/stands as/marks/represents [a], boasts/features/offers [a]*.
- **Problem**: LLMs reflexively avoid simple verbs like *is*, *are*, or *has*, preferring inflated action metaphors.
- **Before**: *Gallery 825 serves as LAAA's exhibition space for contemporary art. The gallery features four separate spaces and boasts over 3,000 square feet.*
- **After**: *Gallery 825 is LAAA's exhibition space for contemporary art. The gallery has four rooms totaling 3,000 square feet.*

#### 9. Negative Parallelisms and Tailing Negations
- **Problem**: Clichés like *"Not only... but also..."*, *"It's not just about X, it's about Y"*, or clipped sentence-end fragments like *", no guessing"* or *", no wasted motion"*.
- **Before**: *It's not just about the beat riding under the vocals; it's part of the aggression and atmosphere. It's not merely a song, it's a statement.*
- **After**: *The heavy beat adds to the aggressive tone.*
- **Before (tailing negation)**: *The options come from the selected item, no guessing.*
- **After**: *The options come from the selected item without forcing the user to guess.*

#### 10. Rule of Three Overuse
- **Problem**: Forcing observations, adjectives, or bullet points into rigid trios to sound rhetorical and complete.
- **Before**: *The event features keynote sessions, panel discussions, and networking opportunities. Attendees can expect innovation, inspiration, and industry insights.*
- **After**: *The event includes talks and panels. There's also time for informal networking between sessions.*

#### 11. Elegant Variation (Synonym Cycling)
- **Problem**: Repetition-penalty algorithms cause AI to artificially rotate synonyms for the same entity in adjacent sentences.
- **Before**: *The protagonist faces many challenges. The main character must overcome obstacles. The central figure eventually triumphs. The hero returns home.*
- **After**: *The protagonist faces many challenges but eventually triumphs and returns home.*

#### 12. False Ranges
- **Problem**: Using *"from X to Y"* constructions where X and Y are not points on a continuous or meaningful scale.
- **Before**: *Our journey through the universe has taken us from the singularity of the Big Bang to the grand cosmic web, from the birth and death of stars to the enigmatic dance of dark matter.*
- **After**: *The book covers the Big Bang, star formation, and current theories about dark matter.*

#### 13. Passive Voice and Subjectless Fragments
- **Problem**: Dropping the human actor or writing clipped subjectless statements (*"No configuration file needed"*).
- **Before**: *No configuration file needed. The results are preserved automatically.*
- **After**: *You do not need a configuration file. The system preserves the results automatically.*

---

### Style Patterns

#### 14. Em Dash Overuse
- **Problem**: Spraying em dashes (—) across sentences to manufacture synthetic punchiness.
- **Before**: *The term is primarily promoted by Dutch institutions—not by the people themselves. You don't say "Netherlands, Europe" as an address—yet this mislabeling continues—even in official documents.*
- **After**: *The term is primarily promoted by Dutch institutions, not by the people themselves. You don't say "Netherlands, Europe" as an address, yet this mislabeling continues in official documents.*

#### 15. Overuse of Boldface
- **Problem**: Mechanically bolding key phrases inside sentences for artificial scanning.
- **Before**: *It blends **OKRs** (Objectives and Key Results), **KPIs** (Key Performance Indicators), and **visual strategy tools**.*
- **After**: *It blends OKRs, KPIs, and visual strategy tools like the Business Model Canvas.*

#### 16. Inline-Header Vertical Lists
- **Problem**: Turning regular explanations into vertical lists with bolded keyword headers followed by colons (`**Header**: Explanation`).
- **Before**:
  *User Experience: The user experience has been significantly improved.*  
  *Performance: Performance has been enhanced through optimized algorithms.*  
  *Security: Security has been strengthened with end-to-end encryption.*
- **After**: *The update improves the interface, speeds up load times through optimized algorithms, and adds end-to-end encryption.*

#### 17. Title Case in Headings
- **Problem**: Capitalizing every word in section headings instead of natural sentence case.
- **Before**: *Strategic Negotiations And Global Partnerships*
- **After**: *Strategic negotiations and global partnerships*

#### 18. Emojis
- **Problem**: Decorating headers, lists, or section dividers with playful corporate emojis (🚀, 💡, ✅, 🔍).
- **Before**: *🚀 Launch Phase: The product launches in Q3 💡 Key Insight: Users prefer simplicity.*
- **After**: *The product launches in Q3. User research showed a preference for simplicity.*

#### 19. Curly Quotation Marks
- **Problem**: Pasting typographic curly quotes (“ ”) and apostrophes (’), a hallmark of ChatGPT raw output, instead of straight quotes (" ').
- **Before**: *He said “the project is on track” but others disagreed.*
- **After**: *He said "the project is on track" but others disagreed.*

---

### Communication Patterns

#### 20. Collaborative Communication Artifacts
- **Words to watch**: *I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like..., let me know, here is a...*
- **Problem**: Chatbot pleasantries and correspondence artifacts pasted into deliverable text.
- **Before**: *Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand on any section.*
- **After**: *The French Revolution began in 1789 when financial crisis and food shortages led to widespread unrest.*

#### 21. Knowledge-Cutoff Disclaimers
- **Words to watch**: *as of [date], Up to my last training update, While specific details are limited/scarce..., based on available information...*
- **Problem**: AI epistemic defense mechanisms left behind in content.
- **Before**: *While specific details about the company's founding are not extensively documented in readily available sources, it appears to have been established sometime in the 1990s.*
- **After**: *The company was founded in 1994, according to its registration documents.*

#### 22. Sycophantic / Servile Tone
- **Problem**: People-pleasing, overly positive validation.
- **Before**: *Great question! You're absolutely right that this is a complex topic. That's an excellent point about the economic factors.*
- **After**: *The economic factors you mentioned are relevant here.*

---

### Filler and Hedging

#### 23. Filler Phrases
- *"In order to achieve this goal"* $\rightarrow$ *"To achieve this"*
- *"Due to the fact that it was raining"* $\rightarrow$ *"Because it was raining"*
- *"At this point in time"* $\rightarrow$ *"Now"*
- *"In the event that you need help"* $\rightarrow$ *"If you need help"*
- *"The system has the ability to process"* $\rightarrow$ *"The system can process"*
- *"It is important to note that the data shows"* $\rightarrow$ *"The data shows"*

#### 24. Excessive Hedging
- **Problem**: Stacking conditional modal verbs (*"It could potentially possibly be argued that..."*).
- **Before**: *It could potentially possibly be argued that the policy might have some effect on outcomes.*
- **After**: *The policy may affect outcomes.*

#### 25. Generic Positive Conclusions
- **Problem**: Vague, cheerful boilerplate endings (*"The future looks bright..."*).
- **Before**: *The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence.*
- **After**: *The company plans to open two more locations next year.*

#### 26. Hyphenated Word Pair Overuse
- **Words to watch**: *third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end*.
- **Problem**: AI hyphenates common compound words with 100% mechanical consistency, unlike real human writers.
- **Before**: *The cross-functional team delivered a high-quality, data-driven report.*
- **After**: *The cross functional team delivered a high quality, data driven report.*

#### 27. Persuasive Authority Tropes
- **Phrases to watch**: *The real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter*.
- **Problem**: Feigning depth to restate an ordinary point with philosophical pretension.
- **Before**: *The real question is whether teams can adapt. At its core, what really matters is organizational readiness.*
- **After**: *The question is whether teams can adapt. That mostly depends on whether the organization is ready to change its habits.*

#### 28. Signposting and Announcements
- **Phrases to watch**: *Let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, without further ado*.
- **Problem**: Announcing what you are about to say instead of just saying it.
- **Before**: *Let's dive into how caching works in Next.js. Here's what you need to know.*
- **After**: *Next.js caches data at multiple layers, including request memoization, the data cache, and the router cache.*

#### 29. Fragmented Headers
- **Problem**: A heading followed by a throwaway 1-line sentence restating the heading before the real paragraph starts.
- **Before**:
  *Performance*  
  *Speed matters.*  
  *When users hit a slow page, they leave.*
- **After**:
  *Performance*  
  *When users hit a slow page, they leave.*

---

## The Dual-Pass Recursive Rewrite Process

Follow this exact sequence when humanizing text:

1. **Read & Isolate**: Read input text, isolate core facts/numbers/mechanisms, and note all matching AI patterns.
2. **Draft Rewrite**: Produce an initial humanized draft that breaks AI sentence uniformity and removes slop words.
3. **Self-Audit**:
   - Explicitly prompt: *"What makes the below so obviously AI generated?"*
   - Answer in 2–4 concise bullet points identifying remaining tells (cadence still too neat, synthetic placeholders, uniform paragraph length, lingering jargon).
4. **Final Anti-AI Pass**:
   - Explicitly prompt: *"Now make it not obviously AI generated."*
   - Produce the final humanized text.
5. **Summary of Changes**: Briefly list what was removed, revoiced, or simplified.

---

## Output Format

When executing this skill, structure your response as:

```markdown
### 📝 Draft Rewrite
[Initial humanized version]

### 🔍 Self-Audit: What makes the above still obviously AI generated?
- [Tell 1: e.g., Rhythm is still too tidy]
- [Tell 2: e.g., Concluding sentence still leans slogan-y]

### ✍️ Final Rewrite (After Anti-AI Audit)
[Final humanized prose with soul, authentic cadence, and zero semantic drift]

### 🧹 Changes Made
- Removed [specific pattern]
- Replaced [AI-ism] with [concrete phrasing]
```

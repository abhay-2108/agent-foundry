---
name: llm-council
description: >-
  Run any question, idea, or decision through a council of 5 AI advisors who independently analyze it, peer-review each other anonymously, and synthesize a final verdict. Based on Karpathy's LLM Council methodology. MANDATORY TRIGGERS: 'council this', 'run the council', 'war room this', 'pressure-test this', 'stress-test this', 'debate this'. STRONG TRIGGERS (use when combined with a real decision or tradeoff): 'should I X or Y', 'which option', 'what would you do', 'is this the right move', 'validate this', 'get multiple perspectives', 'I can't decide', 'I'm torn between'. Do NOT trigger on simple yes/no questions, factual lookups, or casual 'should I' without a meaningful tradeoff (e.g. 'should I use markdown' is not a council question). DO trigger when the user presents a genuine decision with stakes, multiple options, and context that suggests they want it pressure-tested from multiple angles.
---

# LLM Council

You ask one AI a question, you get one answer. That answer might be great. It might be mid. You have no way to tell because you only saw one perspective.

The council fixes this. It runs your question through 5 independent advisors, each thinking from a fundamentally different angle. Then they review each other's work. Then a chairman synthesizes everything into a final recommendation that tells you where the advisors agree, where they clash, and what you should actually do.

This is adapted from Andrej Karpathy's LLM Council. He dispatches queries to multiple models, has them peer-review each other anonymously, then a chairman produces the final answer. We do the same thing inside Claude and Antigravity using sub-agents or specialized personas with different thinking lenses.

---

## When to Run the Council

The council is for questions where being wrong is expensive.

**Good council questions:**
- "Should I launch a $97 workshop or a $497 course?"
- "Which of these 3 positioning angles is strongest?"
- "I'm thinking of pivoting from X to Y. Am I crazy?"
- "Here's my landing page copy. What's weak?"
- "Should I hire a VA or build an automation first?"

**Bad council questions:**
- "What's the capital of France?" (one right answer, no need for perspectives)
- "Write me a tweet" (creation task, not a decision)
- "Summarize this article" (processing task, not judgment)

The council shines when there's genuine uncertainty and the cost of a bad call is high. If you already know the answer and just want validation, the council will likely tell you things you don't want to hear. That's the point.

---

## The Five Advisors

Each advisor thinks from a different angle. They're not job titles or personas. They're thinking styles that naturally create tension with each other.

### 1. The Contrarian
Actively looks for what's wrong, what's missing, what will fail. Assumes the idea has a fatal flaw and tries to find it. If everything looks solid, digs deeper. The Contrarian is not a pessimist. They're the friend who saves you from a bad deal by asking the questions you're avoiding.

### 2. The First Principles Thinker
Ignores the surface-level question and asks "what are we actually trying to solve here?" Strips away assumptions. Rebuilds the problem from the ground up. Sometimes the most valuable council output is the First Principles Thinker saying "you're asking the wrong question entirely."

### 3. The Expansionist
Looks for upside everyone else is missing. What could be bigger? What adjacent opportunity is hiding? What's being undervalued? The Expansionist doesn't care about risk (that's the Contrarian's job). They care about what happens if this works even better than expected.

### 4. The Outsider
Has zero context about you, your field, or your history. Responds purely to what's in front of them. This is the most underrated advisor. Experts develop blind spots. The Outsider catches the curse of knowledge: things that are obvious to you but confusing to everyone else.

### 5. The Executor
Only cares about one thing: can this actually be done, and what's the fastest path to doing it? Ignores theory, strategy, and big-picture thinking. The Executor looks at every idea through the lens of "OK but what do you do Monday morning?" If an idea sounds brilliant but has no clear first step, the Executor will say so.

**Why these five:** They create three natural tensions:
- **Contrarian vs Expansionist** (downside vs upside).
- **First Principles vs Executor** (rethink everything vs just do it).
- **The Outsider** sits in the middle keeping everyone honest by seeing what fresh eyes see.

---

## How a Council Session Works

### Step 1: Frame the Question (with Context Enrichment)

When the user says "council this" (or any trigger phrase), do two things before framing:

**A. Scan the workspace for context.** The user's question is often just the tip of the iceberg. Look for relevant context files:
- System instructions, ADRs, or READMEs in the project root or workspace (business context, constraints).
- Any memory stores or documentation (audience profiles, voice docs, business details, past decisions).
- Any files the user explicitly referenced or attached.
- Recent council transcripts or notes (to avoid re-counciling the same ground).
- Context files relevant to the question (e.g. revenue data, pricing metrics, audience research).

Scan quickly. Don't spend more than 30 seconds. Look for the 2–3 files that provide advisors with the context needed for specific, grounded advice.

**B. Frame the question.** Take the user's raw question AND enriched context and reframe it as a clear, neutral prompt:
1. The core decision or question.
2. Key context from the user's message.
3. Key context from workspace files (business stage, audience, constraints, past results, relevant numbers).
4. What's at stake (why this decision matters).

Don't add your own opinion or steer it. Ensure each advisor has enough context for grounded answers. If the question is too vague ("council this: my business"), ask one clarifying question before proceeding.

### Step 2: Convene the Council (5 Advisors in Parallel)

Spawn or simulate all 5 advisors independently:
1. Their advisor identity and thinking style.
2. The framed question.
3. A clear instruction: respond independently. Do not hedge. Do not try to be balanced. Lean fully into your assigned perspective.

Each advisor produces a response of 150–300 words.

**Advisor Prompt Template:**
```text
You are [Advisor Name] on an LLM Council.

Your thinking style: [advisor description from above]

A user has brought this question to the council:
---
[framed question]
---

Respond from your perspective. Be direct and specific. Don't hedge or try to be balanced. Lean fully into your assigned angle. The other advisors will cover the angles you're not covering.

Keep your response between 150-300 words. No preamble. Go straight into your analysis.
```

### Step 3: Peer Review (Anonymous Cross-Examination)

Collect all 5 advisor responses. Anonymize them as **Response A through E** (randomize which advisor maps to which letter to eliminate positional and label bias).

Have each of the 5 advisor personas review the set of 5 anonymized responses:
1. Which response is the strongest and why? (pick one)
2. Which response has the biggest blind spot and what is it?
3. What did ALL responses miss that the council should consider?

**Reviewer Prompt Template:**
```text
You are reviewing the outputs of an LLM Council. Five advisors independently answered this question:
---
[framed question]
---

Here are their anonymized responses:

Response A: [response]
Response B: [response]
Response C: [response]
Response D: [response]
Response E: [response]

Answer these three questions. Be specific. Reference responses by letter.
1. Which response is the strongest? Why?
2. Which response has the biggest blind spot? What is it missing?
3. What did ALL five responses miss that the council should consider?

Keep your review under 200 words. Be direct.
```

### Step 4: Chairman Synthesis

The Chairman receives: the original question, all 5 advisor responses (now de-anonymized), and all 5 peer reviews.

The Chairman synthesizes everything into a definitive verdict:

```text
You are the Chairman of an LLM Council. Your job is to synthesize the work of 5 advisors and their peer reviews into a final verdict.

The question brought to the council:
---
[framed question]
---

ADVISOR RESPONSES:
The Contrarian: [response]
The First Principles Thinker: [response]
The Expansionist: [response]
The Outsider: [response]
The Executor: [response]

PEER REVIEWS:
[all 5 peer reviews]

Produce the council verdict using this exact structure:

## Where the Council Agrees
[Points multiple advisors converged on independently. High-confidence signals.]

## Where the Council Clashes
[Genuine disagreements. Present both sides. Explain why reasonable advisors disagree.]

## Blind Spots the Council Caught
[Things that only emerged through peer review. Things individual advisors missed that others flagged.]

## The Recommendation
[A clear, direct recommendation. Not "it depends." A real answer with reasoning.]

## The One Thing to Do First
[A single concrete next step. Not a list. One thing.]

Be direct. Don't hedge. The whole point of the council is to give the user clarity they couldn't get from a single perspective.
```

### Step 5: Present the Verdict in Chat

Present the full verdict directly in chat using markdown. Do not generate HTML files unless requested.

Format the output:
```markdown
## Council Verdict: {short topic}

### Where the Council Agrees
{content}

### Where the Council Clashes
{content}

### Blind Spots the Council Caught
{content}

### The Recommendation
{content}

### The One Thing to Do First
{content}
```

### Step 6: Save the Transcript (Optional)
Only save a transcript if explicitly requested or for major strategic decisions. Write to `council-transcript-[timestamp].md` in the project's active or docs directory.

---

## Important Rules
- **Parallel Independent Generation**: Advisors must never see each other's work before generating their initial response.
- **Strict Anonymization**: Hide advisor labels during the peer review round to avoid deference bias.
- **The Chairman Can Dissent**: If 4 out of 5 advisors agree but the 1 dissenter presents irrefutable logic, the Chairman should back the dissenter.
- **No Hedging**: Never output "it depends" without delivering a clear, actionable default path.
- **Zero Triviality**: Do not trigger the council on factual queries or simple execution tasks.

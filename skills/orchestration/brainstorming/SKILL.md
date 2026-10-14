---
name: brainstorming
description: Use this skill when refining rough or ambiguous ideas through structured
  Socratic inquiry, exploring design alternatives, and evaluating architectural trade-offs.
---

# Brainstorming & Idea Incubator

## Overview

Refines rough, ambiguous, or unformed ideas through structured Socratic inquiry. Explores creative architectural alternatives, evaluates trade-offs across feasibility, viability, and desirability, and produces actionable design specifications.

## When to Use

- At the inception of a new project, feature, architecture, or workflow.
- When the user shares a loose, half-baked, or exploratory idea (`"I'm thinking about building X"`).
- When there are multiple viable technical or product directions with distinct trade-offs.
- When looking to challenge assumptions, find blind spots, or explore creative solutions.
- Trigger phrases: `"brainstorm with me"`, `"help me think through this"`, `"explore ideas for X"`, `"how should I approach this?"`, `"what are some alternatives?"`.
- **When NOT to use**: Executing pre-approved engineering implementations (use `fullstack-engineer` or `plan-and-execute`).

## Core Process & Socratic Idea Incubation

## Core Brainstorming Principles
1. **Diverge Before You Converge**: First expand the solution space with multiple diverse angles; only then evaluate and narrow down to the best approach.
2. **Socratic Inquiry**: Ask high-impact, clarifying questions that expose unstated assumptions, constraints, and success metrics.
3. **Steel-Manning Alternatives**: Every proposed option must be presented at its strongest, with honest trade-offs, not strawman caricatures.
4. **Actionable Output**: End with a concrete concept design document that can feed directly into the **`plan-and-execute`** skill.

---

## Step-by-Step Brainstorming Workflow

```
┌────────────────────────────────────────────────────────┐
│                   Brainstorming Cycle                  │
├──────────────┬──────────────┬─────────────┬────────────┤
│ 1. Clarify   │ 2. Diverge   │ 3. Evaluate │ 4. Concept │
│    & Probe   │   (3 Options)│    Trade-offs│    Design  │
└──────────────┴──────────────┴─────────────┴────────────┘
```

### Step 1: Socratic Probing & Constraint Mapping
When the user introduces an idea, probe the edges to uncover hidden parameters:
- **Core Value**: What is the single most important outcome this must achieve?
- **Target Audience / Persona**: Who is using this, and in what context?
- **Hard Constraints**: Time, budget, tech stack limitations, or performance SLAs?
- **Non-Goals**: What are we explicitly *not* building in version 1?

*(Tip: Keep questions concise and limited to 2–3 high-leverage inquiries at a time to maintain natural conversational momentum).*

### Step 2: Divergent Exploration (The 3-Option Rule)
Propose at least **3 distinct conceptual approaches**:
1. **Option A (The Minimalist / Speed-to-Value)**: The simplest thing that could possibly work. Lowest complexity, fastest time-to-market.
2. **Option B (The Enterprise / Robust Standard)**: The battle-tested, highly scalable industry standard approach. Moderate complexity, high resilience.
3. **Option C (The Creative / Unconventional Angle)**: A novel, out-of-the-box paradigm (e.g., event-driven, local-first, agentic, or serverless-native).

### Step 3: Trade-Off Analysis & Deliberation
For each option, compare:
- **Pros & Cons**: Immediate wins vs. long-term maintenance burden.
- **Effort vs. Impact**: Quick win, strategic investment, or potential trap.
- **Risk Vectors**: Where is this likely to break or cause friction?

### Step 4: Convergent Synthesis (Concept Design Document)
Once an approach is selected, summarize the vision into a structured concept brief.

---

## Brainstorming Concept Design Template

```markdown
# 💡 Concept Design Brief: [Project / Feature Name]

**Status**: Concept Aligned / Ready for Implementation Planning
**Selected Direction**: [Option Name & 1-line justification]

---

### 1. Problem Statement & Core Value
- **The Problem**: What friction or gap are we solving?
- **The Solution**: High-level explanation of the proposed system.
- **Success Criteria**: How will we measure success?

### 2. Evaluated Alternatives Matrix

| Dimension | Option A: Minimalist | Option B: Robust Standard (Chosen) | Option C: Unconventional |
|---|---|---|---|
| **Architecture** | Single SQLite file | Postgres + Redis Cache | DynamoDB Event Sourcing |
| **Complexity** | Very Low | Moderate | High |
| **Time to Build** | 1 day | 3 days | 1 week |
| **Verdict** | Too limiting for multi-user | **Best balance of scale & simplicity** | Premature optimization |

### 3. Key Architectural Decisions & Invariants
- *Decision 1*: We will use X because Y.
- *Invariant*: State must remain accessible offline.

### 4. Identified Blind Spots & Risks
- **Risk**: Potential cold-start latency under spike load.
- **Mitigation**: Implement background warmers or lightweight connection pooling.

### 5. Next Step
- Transition to **`plan-and-execute`** to generate the step-by-step task breakdown.
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"The first idea is usually the best one, so we should start coding immediately."* | Jumping into the first solution anchors on obvious patterns; exploring 3 distinct architectural alternatives reveals hidden constraints early. |
| *"Brainstorming doesn't need constraints; anything goes."* | Unconstrained brainstorming produces un-shippable fantasies; creative divergence must be bounded by technical and budget realities. |
| *"User trade-offs can be figured out during implementation."* | Discovering fundamental UX or architectural trade-offs mid-implementation causes massive rework and thrown-away code. |
| *"Pros and cons lists are sufficient for decision making."* | Simple pros/cons lists treat all factors equally; structured multi-criteria decision matrices weigh impact against engineering effort. |

## Red Flags

- Starting implementation on ambiguous requirements without presenting alternative design options.
- Failing to ask clarifying questions when user specifications contain obvious contradictions.
- Presenting three 'alternatives' that are just cosmetic variations of the same underlying architecture.
- Ending a brainstorm session without concrete next steps, assigned tasks, or measurable milestones.

## Verification

After completing the workflow, confirm:
- [ ] Explores at least 3 distinct conceptual or architectural approaches.
- [ ] Multi-criteria decision matrix scores alternatives across complexity, latency, cost, and developer velocity.
- [ ] Key trade-offs and non-goals are explicitly documented.
- [ ] Brainstorming session concludes with a structured implementation proposal ready for `plan-and-execute`.

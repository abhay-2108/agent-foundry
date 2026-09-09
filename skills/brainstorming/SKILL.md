---
name: brainstorming
description: >-
  Use this skill before writing code, designing features, or starting new projects.
  Refines rough or ambiguous ideas through structured Socratic inquiry, explores multiple
  creative alternatives, evaluates trade-offs, and produces actionable design specifications.
---

# Brainstorming & Idea Incubator

A structured, collaborative thinking skill that turns rough sparks, ambiguous user ideas, and high-level requirements into clear, validated concept designs before a single line of code is written.

## When to Use This Skill
- At the inception of a new project, feature, architecture, or workflow.
- When the user shares a loose, half-baked, or exploratory idea (`"I'm thinking about building X"`).
- When there are multiple viable technical or product directions with distinct trade-offs.
- When looking to challenge assumptions, find blind spots, or explore creative solutions.
- Trigger phrases: `"brainstorm with me"`, `"help me think through this"`, `"explore ideas for X"`, `"how should I approach this?"`, `"what are some alternatives?"`.

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

---

## Anti-Patterns & Traps to Avoid

1. **Premature Convergence (The First-Idea Trap)**: Instantly locking onto the first architectural option mentioned and jumping directly into implementation. Always diverge first: force the exploration of at least 3 distinct conceptual angles (e.g., minimalist, battle-tested standard, novel decoupled approach).
2. **The Strawman Illusion**: Presenting one real proposal alongside two intentionally absurd alternatives (e.g., "Option B: Store everything in a flat text file on a floppy disk"). All presented alternatives must represent genuine, viable design trade-offs.
3. **Premature Over-Engineering**: Proposing distributed microservices, event streaming, and Kubernetes clusters for an internal tool with 5 daily users. Calibrate architectural complexity strictly to the operational constraints.
4. **Sycophantic Agreement**: Blindly endorsing a user's initial flawed assumption without diplomatically surfacing technical debt, security hazards, or edge-case costs. A great brainstorming partner challenges assumptions thoughtfully.

---

## Quality Checklist

- [ ] Problem statement and non-functional constraints (latency, cost, scale) are clearly established.
- [ ] At least 3 distinct architectural alternatives are explored with explicit trade-off comparisons.
- [ ] Solutions are evaluated against concrete dimensions: build complexity, maintenance overhead, and failure modes.
- [ ] Architectural blind spots and second-order risks are explicitly documented with mitigations.
- [ ] User alignment is established on the chosen direction before generating technical implementation plans.
- [ ] Output provides a crisp Concept Design Brief ready for handover to `plan-and-execute`.

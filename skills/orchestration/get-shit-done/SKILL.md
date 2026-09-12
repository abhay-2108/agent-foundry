---
name: get-shit-done
description: >-
  A structured methodology for shipping production software with AI agents
  without hitting the vibe coding ceiling. Enforces 3-tier work breakdown
  (Project to Milestone to Slice), prevents context drift across sessions,
  blocks premature completion claims, and ensures every slice is vertically
  delivered end-to-end. MANDATORY TRIGGERS: 'gsd this', 'plan this as gsd',
  'break this down gsd style', 'structure this project', 'i want to use gsd'.
  STRONG TRIGGERS: 'plan the next milestone', 'create a slice', 'what should
  I build next', 'set up the project structure', 'how do I track progress'.
  Do NOT trigger on bug fixes, simple one-off tasks, or tiny feature
  additions that fit in a single context window.
---

# Get Shit Done (GSD)

GSD is an AI-assisted software development methodology for solo builders and small teams who have hit the **vibe coding ceiling** - the point where feature-by-feature chat coding breaks down because the codebase is too large for any single context window.

GSD forces a strict hierarchical work breakdown and session discipline that keeps AI agents productive on complex, multi-week projects.

---

## The Core Problem: Vibe Coding Ceiling

Traditional vibe coding (asking an AI to implement features in a chat window) works when a project is small (1-10 files). Once a codebase reaches **15+ components**, three failure modes emerge:

1. **Context Degradation and Drift** - The project no longer fits in one context window. In new sessions, the AI forgets past architectural decisions, re-introduces previously fixed bugs, and contradicts existing patterns.
2. **Premature Completion Claims** - Agents declare "Done! All tests pass" without executing verification commands or producing fresh terminal evidence.
3. **Horizontal Layer Stagnation** - Agents spend hours building data models or abstractions without shipping a single working, testable end-to-end slice.

GSD fixes all three.

---

## The 3-Tier Work Breakdown Hierarchy

GSD enforces a strict hierarchy to keep work atomic and context-contained:

```
Project
  +-- Milestone (2-4 weeks of work, one testable increment)
        +-- Slice (half to 1 day max, one end-to-end vertical thread)
              +-- Tasks (individual file-level changes inside a slice)
```

### Tier 1: Project
The full software product. Defined once in a `PROJECT-BRIEF.md` at the repo root. Contains:
- Product vision and problem statement
- Tech stack decisions (non-negotiable)
- Target user and key constraints
- Out-of-scope explicitly listed

### Tier 2: Milestone
A coherent, user-visible increment. Think of it as a mini-product release.
- Typically 4-8 slices
- Stored in `M###-CONTEXT.md` (e.g., `M001-CONTEXT.md`)
- Contains: acceptance criteria, architecture decisions, data models, API contracts
- **A milestone is done when ALL its slices pass UAT**

### Tier 3: Slice
The atomic unit of GSD work. A slice is a **vertical thread** - it cuts through all layers (database -> API -> frontend) for one user-facing capability.

Rules for slices:
- **Half to 1 day max** - if it takes longer, split it
- **End-to-end delivery only** - never ship a slice that works only at one layer
- **One context window** - a slice must be completable without context re-injection
- **UAT-ready** - slice is only done when it passes the acceptance test defined before coding starts

---

## The GSD Session Flow

Every development session follows this exact sequence. Deviating from it causes context drift.

### Phase 0: Context Recovery (Start of Every Session)

Before writing a single line of code, inject full context:

```
1. Read PROJECT-BRIEF.md             <- product vision, constraints
2. Read M###-CONTEXT.md              <- active milestone context
3. Read .gsd/journal/YYYY-MM-DD.md  <- yesterday's session log
4. Read .gsd/metrics.json            <- slice completion status
5. Check git log --oneline -10       <- what was actually shipped
```

**Never start coding without completing Phase 0.** Context injection takes 2 minutes and prevents hours of drift.

### Phase 1: Slice Definition (Before Coding)

Define the slice BEFORE asking the AI to implement anything:

```
Slice: [Short Name]

User Story: As a [user], I want [capability] so that [value].

Acceptance Criteria:
- [Specific, testable criterion 1]
- [Specific, testable criterion 2]
- [Specific, testable criterion 3]

Layers touched: [Database / API / Frontend / Auth / etc.]
Estimated time: [X hours]
Dependencies: [Previous slices or external services]

UAT Test:
[The exact manual or automated test that proves this slice is done]
```

### Phase 2: Implement (The Actual Coding)

With slice definition confirmed, execute in this order:
1. **Data layer first** - schema, migrations, seed data
2. **API/business logic** - service methods, routes
3. **Frontend** - UI connected to real data
4. **Verification** - run the UAT test NOW, in this same session

### Phase 3: Verification Gate (Non-Negotiable)

**The agent MUST produce fresh terminal output proving the slice works.** Claiming "it works" without evidence is a policy violation.

Required evidence per slice:
- Test run output (green) or manual UAT screenshot/log
- `git diff --stat` showing what changed
- No regressions in existing tests

### Phase 4: Commit and Log

After verification:

```bash
git add -p
git commit -m "feat(M###-S##): [slice name] - [one-line description]"
```

Update `.gsd/journal/YYYY-MM-DD.md` with:
- What was completed
- Blockers hit and how they were resolved
- What comes next

---

## GSD File Structure

```
project-root/
+-- PROJECT-BRIEF.md               <- Project definition (written once)
+-- M001-CONTEXT.md                <- Milestone 1 context
+-- M002-CONTEXT.md                <- Milestone 2 context
+-- .gsd/
    +-- metrics.json               <- Slice completion tracker
    +-- auto.lock                  <- Auto-mode state
    +-- journal/
    |   +-- 2024-01-15.md         <- Daily session log
    |   +-- 2024-01-16.md
    +-- activity/
        +-- *.jsonl                <- Machine-readable activity log
```

### PROJECT-BRIEF.md Template

```markdown
# [Project Name]

## Problem Statement
[One paragraph: what problem does this solve, for whom, and why now?]

## Product Vision
[One paragraph: what does success look like in 6 months?]

## Tech Stack (Non-Negotiable)
- Frontend: [framework, version]
- Backend: [language, framework, version]
- Database: [engine, version]
- Auth: [approach]
- Hosting: [platform]

## Key Constraints
- [Constraint 1: e.g., must work offline]
- [Constraint 2: e.g., max $50/month infrastructure cost]

## Out of Scope (Explicitly)
- [Thing 1 that will NOT be built]
- [Thing 2 that will NOT be built]

## Milestones
- M001: [Name] - [One-line description]
- M002: [Name] - [One-line description]
```

### M###-CONTEXT.md Template

```markdown
# Milestone [###]: [Name]

## Goal
[One paragraph: what does this milestone deliver and why does it matter?]

## Acceptance Criteria (Milestone Complete When...)
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Architecture Decisions
[Key decisions made for this milestone. Future slices must not contradict these.]

## Data Models
[Schema definitions relevant to this milestone]

## API Contracts
[Endpoint definitions, request/response shapes]

## Slices
| # | Name | Status | UAT |
|---|------|--------|-----|
| S01 | [name] | Not Started | [test description] |
| S02 | [name] | In Progress | [test description] |
| S03 | [name] | Complete | [test description] |

## Session Log
[Running log of what happened in each session]
```

---

## Anti-Patterns GSD Guards Against

### The Horizontal Builder
Building an entire data layer before touching the API or frontend. Slices must be vertical - each slice ships a testable end-to-end thread.

**Fix**: Define slices by user capability, not by technical layer.

### The Premature Claimer
"Done! All tests pass." - without running a single test or producing evidence.

**Fix**: Use the Verification Gate (Phase 3). No evidence = not done.

### The Context Amnesiac
Starting a new session and coding from scratch without reading the context files.

**Fix**: Phase 0 is mandatory. Every session starts with context recovery.

### The Scope Creeper
A slice that starts as "add login" and ends as "redesign the entire auth system."

**Fix**: If a slice takes longer than 1 day, stop, split it into two slices, commit what works.

### The Perfectionist Stall
Refusing to ship a slice until it is pixel-perfect or handles every edge case.

**Fix**: Slices must pass UAT criteria, not be perfect. Ship, log the known gaps, address in a future slice.

---

## How to Use This Skill

### Starting a New Project

When the user says "gsd this" or "plan this as gsd":

1. **Ask for the project brief** (or draft one from the conversation context)
2. **Scaffold the GSD file structure** - create `PROJECT-BRIEF.md` and `.gsd/` directory
3. **Identify the first milestone** - what is the smallest useful increment?
4. **Define 4-6 slices** for Milestone 1 - each vertical, each half to one day
5. **Create `M001-CONTEXT.md`** with architecture decisions and slice table
6. **Initialize `.gsd/metrics.json`** with all slices at `not_started`

### Starting a Session on an Existing GSD Project

1. Run Phase 0 context recovery automatically
2. Report: "We are at M### S## [name]. Status: [what's done, what's next]."
3. Confirm the next slice before starting
4. Execute Phases 1-4

### Recovering a Stuck or Failed GSD Session

If a session ended without completing a slice:
1. Read `.gsd/journal/` for the last log entry
2. Run `git status` and `git log --oneline -5`
3. Identify what was partially done
4. Either: complete and verify the current slice, OR roll back and restart from the last commit

---

## The GSD Mindset

Ship vertical slices. Context is sacred. Evidence before claims. Never build a layer - always build a thread.

GSD is not a project management framework. It is a **discipline for keeping AI agents productive** on complex software over weeks and months. The moment you skip Phase 0, or accept a "done" claim without evidence, or let a slice grow beyond one day - you are back to vibe coding.

The methodology pays off at 15+ files and compounds as the project grows. Follow it exactly at first. Once the patterns are internalized, adapt them to your rhythm.

---

## metrics.json Schema

```json
{
  "project": "project-name",
  "active_milestone": "M001",
  "milestones": {
    "M001": {
      "name": "Milestone Name",
      "status": "in_progress",
      "slices": {
        "S01": { "name": "slice name", "status": "complete", "completed_at": "2024-01-15" },
        "S02": { "name": "slice name", "status": "in_progress", "started_at": "2024-01-16" },
        "S03": { "name": "slice name", "status": "not_started" }
      }
    }
  }
}
```

Valid statuses: `not_started`, `in_progress`, `blocked`, `complete`, `skipped`

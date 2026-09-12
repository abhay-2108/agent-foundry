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

GSD is an AI-assisted software development methodology for solo builders and small teams who have hit the **vibe coding ceiling** — the point where feature-by-feature chat coding breaks down because the codebase is too large for any single context window.

GSD's core insight: **context is a managed resource, not a conversation log.** Each session loads exactly the context the current task needs. Project memory lives on disk in structured files, not in conversation history that expires.

---

## The Core Problem: Vibe Coding Ceiling

The ceiling arrives around the **10–15 component mark** when the project becomes too large to fit in a single context window:

1. **Context Degradation and Drift** — Every new session forgets architectural decisions. The AI contradicts itself, reintroduces bugs, and generates code that is locally correct but globally incoherent.
2. **Premature Completion Claims** — Agents declare "Done! All tests pass" without executing a single verification command.
3. **Horizontal Layer Stagnation** — Hours building data models without shipping one working, testable end-to-end slice.

This ceiling is structural — not a model quality issue. GSD addresses it structurally, not by asking you to write better prompts.

---

## The 3-Tier Hierarchy

```
Project (the full product — defined once in PROJECT.md)
  +-- Milestone (days to weeks — demoable increment)
        +-- Slice (hours to 1 day — one vertical end-to-end thread)
              +-- Task (15–60 min — one focused unit of work)
```

**Rules that must never break:**
- A slice cuts through ALL layers (DB → API → frontend) for ONE user capability
- A slice fits in ONE context window
- A slice is done ONLY when its UAT test produces fresh evidence
- A task that exceeds 60 min gets split
- A slice that exceeds 1 day gets split

---

## The .gsd/ Directory — Project Memory on Disk

```
project-root/
+-- .gsd/
    +-- PROJECT.md              <- Product vision, tech stack, milestone sequence
    +-- REQUIREMENTS.md         <- Capability contract with R### IDs
    +-- DECISIONS.md            <- Architectural decisions log (append-only)
    +-- STATE.md                <- Derived state — active milestone/phase
    +-- KNOWLEDGE.md            <- Cross-session lessons and patterns (append-only)
    +-- CAPTURES.md             <- Fire-and-forget thought captures for triage
    +-- PREFERENCES.md          <- Project-level config (git, planning depth, etc.)
    +-- auto.lock               <- Crash recovery: PID, active unit, session file
    +-- metrics.json            <- Slice completion tracker
    +-- milestones/
    |   +-- M001/
    |       +-- M001-CONTEXT.md    <- Milestone brief: scope, goals, decisions
    |       +-- M001-RESEARCH.md   <- Codebase + library findings
    |       +-- M001-ROADMAP.md    <- Ordered slices with risk + dependencies
    |       +-- M001-VALIDATION.md <- QA check vs success criteria (written at end)
    |       +-- M001-SUMMARY.md    <- Milestone completion record
    |       +-- slices/
    |           +-- S01/
    |               +-- S01-PLAN.md        <- Task breakdown and must-haves
    |               +-- S01-RESEARCH.md    <- Slice-scoped codebase findings
    |               +-- S01-SUMMARY.md     <- Compressed slice record (after done)
    |               +-- S01-UAT.md         <- Acceptance test script
    |               +-- S01-ASSESSMENT.md  <- UAT execution results
    |               +-- tasks/
    |                   +-- T01-PLAN.md
    |                   +-- T01-SUMMARY.md
    |                   +-- T02-PLAN.md
    |                   +-- T02-SUMMARY.md
    +-- journal/
    |   +-- YYYY-MM-DD.md       <- Daily session log
    +-- activity/
    |   +-- NNN-[unit]-[id].jsonl  <- Machine-readable execution logs
    +-- runtime/
        +-- units/*.json           <- Active unit metadata
```

See `scripts/gsd-init.py` to scaffold this structure automatically.

---

## Phase 1 — Discussion Protocol

Run the full discussion protocol before writing ANY planning artifacts.

### Step 1: Vision Input
Ask once: "What's the vision?" Let the user describe freely. Don't interrupt.

### Step 2: Reflection — A Contract, Not a Nicety
Before asking any questions, reflect back:
- Concrete summary of what you understood
- Size estimate: roughly how many milestones, how many slices in the first one
- List of every major capability you understood

If the reflection is wrong and uncorrected, the roadmap will be wrong. The user must read this like a PR diff.

### Step 3: Investigation
Invisibly scout the codebase (ls, find, rg), check library docs, run web searches. Questions must reflect what is actually true about the codebase — not generic assumptions.

### Step 4: Questioning Rounds
Ask questions about **experience and outcomes, not implementation.**
- Not: "What auth provider?" → Instead: "When someone logs in, what should that feel like?"

Match depth to scope. Track this internal checklist:
- [ ] What they're building (concrete enough to explain to a stranger)
- [ ] Why it needs to exist
- [ ] Who it's for
- [ ] What "done" looks like from a user's perspective
- [ ] The biggest technical unknowns / risks
- [ ] What external systems this touches

### Step 5: Depth Verification Gate (NON-BYPASSABLE)
Present a structured summary across all 6 checklist dimensions.
Ask: "Does this capture your intent correctly?"

**DO NOT write CONTEXT.md until the user confirms.** This gate is mechanical. It is the last clean moment to catch misalignments.

### Step 6: Requirements Contract
Before writing the roadmap, produce REQUIREMENTS.md:
- Each capability assigned a stable `R###` ID
- Status: Active / Deferred / Out of Scope
- Primary owning slice

Print the requirements table in chat for confirmation before writing any files.

### Step 7: Roadmap Preview
Print the planned slice table (Slice | Title | Risk | Depends | Demo) in chat.
Let the user adjust. Only after approval: write all artifacts in this order:
PROJECT.md → REQUIREMENTS.md → DECISIONS.md → CONTEXT.md → ROADMAP.md → STATE.md

STATE.md written last signals discussion is complete and auto-mode can start.

---

## Phase 2 — Auto-Mode Execution Loop

Once CONTEXT.md and ROADMAP.md exist and STATE.md is written:

```
For each Slice in ROADMAP.md:
  1. Research  — scout codebase + check lib docs → write S##-RESEARCH.md
  2. Plan      — decompose into tasks (15–60 min) → write S##-PLAN.md
  3. Execute (each task in a FRESH context window)
     - Context injected: task plan + slice plan + prior summaries
       + dependency summaries + DECISIONS.md + KNOWLEDGE.md
     - Order: data layer → API/logic → frontend
     - Read KNOWLEDGE.md at start; append new patterns discovered
     - Write T##-SUMMARY.md on completion
     - Commit: feat(M###/S##/T##): description   GSD-Task: M###/S##/T##
  4. Complete Slice
     - Write S##-SUMMARY.md (compress all task work)
     - Write S##-UAT.md (concrete test cases)
     - Execute UAT → write S##-ASSESSMENT.md with actual results
     - Mark slice [x] in ROADMAP.md
  5. Reassess  — does roadmap still make sense? Update if needed.
  6. Repeat for next slice

After all slices:
  7. Validate Milestone — compare success criteria vs S##-ASSESSMENT results
  8. Write M###-VALIDATION.md + M###-SUMMARY.md
  9. Seal milestone → update STATE.md
```

**Golden rule: every task writes a SUMMARY with what changed and what was verified.
Evidence is the only definition of "done".**

---

## Brief Quality System

### Bad vs Good Examples

| Vague (useless) | Specific (actionable) |
|---|---|
| "Add search to the app" | "Add a search bar to /products filtering by name on each keystroke (300ms debounce). Empty = 'No products found'." |
| "Fix the login bug" | "Login redirects to /dashboard instead of /onboarding when user.onboarding_complete is false. Fix in src/app/auth/callback/route.ts." |
| "Make the dashboard faster" | "Consolidate 4 API calls on /dashboard into one /api/dashboard-summary endpoint. Target: load < 500ms on 4G." |

### Brief Quality Checklist
Before handing any brief to a GSD session:
- [ ] Each requirement describes **observable behaviour**, not internal implementation
- [ ] Each requirement has **acceptance criteria** that can be verified
- [ ] **Edge cases** are explicitly called out or declared out of scope
- [ ] **Known constraints** the agent can't discover from the codebase are noted
- [ ] Scope is small enough to **deliver and verify in one milestone**

### Common Brief Mistakes
- **Too vague**: "improve UX", "add caching" — gives the agent zero signal
- **Too prescriptive**: Specifying Redis key prefixes prevents better solutions
- **Missing acceptance criteria**: If you can't write a test, the agent can't either
- **Invisible context**: Agent only knows what's in the codebase and what you wrote
- **Bundling too much**: One milestone = one focused capability area

---

## GSD Commands Reference

| Command | What It Does |
|---|---|
| `/gsd` | Smart entry — discussion on new project, status on existing |
| `/gsd auto` | Autonomous mode — runs full loop until milestone done |
| `/gsd quick [task]` | Quick task with GSD guarantees, no full planning overhead |
| `/gsd discuss` | Structured design conversation for new milestone/decision |
| `/gsd new-milestone` | Create next milestone — full discussion + planning |
| `/gsd status` | Progress dashboard: milestone, slices done, cost so far |
| `/gsd steer` | Hard-steer plan mid-execution without stopping |
| `/gsd stop` | Stop auto mode gracefully (current task completes) |
| `/gsd capture [thought]` | Fire-and-forget thought capture — queued for triage |
| `/gsd triage` | Review pending captures: promote / inject / defer / dismiss |
| `/gsd knowledge [rule]` | Add persistent rule that all future sessions load |
| `/gsd forensics` | Full-access debugger for unexpected failures |
| `/gsd doctor` | Runtime health checks across 7 domains |
| `/gsd queue` | View and reorder upcoming milestones |

---

## The KNOWLEDGE.md System (Cross-Session Memory)

`KNOWLEDGE.md` is an append-only register of project-specific rules, patterns,
and lessons. The agent reads it at the start of every unit and appends when
discovering non-obvious patterns or gotchas.

**Example:**
```markdown
## [2024-01-15] [Source: session M001/S01/T02]
- Prisma `contains` is case-sensitive. Use `mode: 'insensitive'` for search.
- Context: Discovered when plain `contains: query` missed uppercase inputs.

## [2024-01-16] [Source: user]
- Always use the existing `withAuth` middleware — do not create new auth wrappers.
```

To add a rule manually: `/gsd knowledge [rule text]`

---

## The CAPTURES System (Mid-Session Thought Capture)

Don't interrupt auto-mode for ideas. Capture them:
```
/gsd capture "add rate limiting to the API endpoints"
/gsd capture "the auth flow should also support OAuth"
```

Captures append to `.gsd/CAPTURES.md` and auto-triage between tasks.

| Classification | Meaning | Resolution |
|---|---|---|
| `quick-task` | Small self-contained fix | Executed immediately inline |
| `inject` | New task for current slice | Task injected into active slice plan |
| `defer` | Important but not urgent | Deferred to roadmap reassessment |
| `replan` | Changes current approach | Triggers slice replan |
| `note` | Informational only | Acknowledged, no plan changes |

Run `/gsd triage` at any time to process pending captures manually.

---

## Recovery — When Things Go Wrong

### Recognizing a Stuck Session
Signs: auto-mode stops output, stale `auto.lock`, STATE.md shows in-progress
with no activity, T##-PLAN.md exists but no T##-SUMMARY.md.

```bash
cat .gsd/STATE.md                                  # Active milestone and phase
cat .gsd/auto.lock                                 # Unit, PID, session file
ls .gsd/milestones/M###/slices/S##/tasks/          # Which tasks have summaries
git log --oneline -5                               # What was actually committed
```

### /gsd doctor — 7-Domain Health Check

```
/gsd doctor       # Diagnose — shows all issues before repairs
/gsd doctor fix   # Apply automatic repairs to fixable issues
```

Checks: structural integrity, git health, runtime health (stale auto.lock),
engine health, global state, environment (disk/env files), provider/auth keys.

**Doctor fix:** removes stale locks, marks tasks done when summary exists,
un-marks premature completions, rebuilds STATE.md from disk state.

### Manual Recovery Protocol
1. `/gsd doctor` then `/gsd doctor fix`
2. Resume: `/gsd auto`
3. If still stuck: `/gsd forensics`
4. Fallback: `git stash` + re-execute from last clean commit

See `scripts/gsd-doctor.py` for a standalone lightweight health checker.

---

## Anti-Patterns GSD Guards Against

| Anti-Pattern | Fix |
|---|---|
| **Horizontal Builder** — building DB → API → UI as full layers | Define slices by user story, not technical layer |
| **Premature Claimer** — "done" without terminal evidence | Every slice requires S##-ASSESSMENT.md with actual UAT results |
| **Context Amnesiac** — new session without reading .gsd/ | Context recovery is mandatory — read PROJECT.md → STATE.md → KNOWLEDGE.md |
| **Scope Creeper** — slice grows from 1 task to 10 | Slice > 1 day → stop, split, commit, continue |
| **Perfectionist Stall** — waiting for perfect before shipping | Pass UAT criteria. Ship. Log gaps in KNOWLEDGE.md. |
| **Vague Brief** — "make it faster" / "improve UX" | Brief Quality Checklist: observable behaviour + acceptance criteria |

---

## How to Use This Skill

### Starting a New Project
When user says "gsd this" / "plan this as gsd" / "structure this project":

1. **Run Discussion Protocol** (all 7 steps — depth verification gate is mandatory)
2. **Scaffold `.gsd/`** with `python scripts/gsd-init.py --project "Name"`
3. **Write artifacts** in order: PROJECT.md → REQUIREMENTS.md → DECISIONS.md → M001-CONTEXT.md → M001-ROADMAP.md → STATE.md
4. **Begin auto-mode loop**

### Starting a Session on Existing GSD Project
Context recovery (mandatory, in this order):
```
.gsd/PROJECT.md
.gsd/milestones/M###/M###-CONTEXT.md  (active milestone)
.gsd/STATE.md
.gsd/KNOWLEDGE.md
.gsd/CAPTURES.md  (any pending?)
.gsd/journal/YYYY-MM-DD.md  (yesterday)
git log --oneline -5
```
Report: "We are at M### S## [name]. [N] slices done, [N] remaining. Next: [slice name]."
Confirm next slice → execute loop.

### Quick Task (Small Well-Understood Change)
Use `/gsd quick [description]` for:
- Clearly scoped changes (you know exactly what to touch)
- No research or multi-task planning needed
- Verifiable in 1–2 steps

Still gets: atomic commit, state tracking, KNOWLEDGE.md update.

---

## Commit Convention

```
feat(M001/S01/T01): build login API endpoint
GSD-Task: M001/S01/T01

feat(M001/S01/T02): add login form component
GSD-Task: M001/S01/T02

feat(M001/S01): complete user authentication flow
feat(M001): milestone complete — core auth platform
```

---

## PREFERENCES.md — Project Config

```yaml
---
mode: solo          # solo | team
git:
  auto_push: false
  isolation: none   # none | worktree | branch
  merge_strategy: squash
  commit_docs: true
planning_depth: normal  # normal | deep
phases:
  skip_slice_research: false
  reassess_after_slice: true
parallel:
  enabled: false
  max_workers: 2
---
```

`mode: solo` — auto-push on, squash merge, simple IDs
`mode: team` — unique IDs, push branches, pre-merge checks

---

## Companion Scripts

| Script | Purpose | Usage |
|---|---|---|
| `scripts/gsd-init.py` | Scaffold full `.gsd/` structure | `python gsd-init.py --project "My App"` |
| `scripts/gsd-status.py` | Progress dashboard | `python gsd-status.py` |
| `scripts/gsd-doctor.py` | Health check + auto-fix | `python gsd-doctor.py [--fix]` |
| `scripts/gsd-journal.py` | Create/open daily session log | `python gsd-journal.py` |
| `scripts/gsd-capture.py` | Fire-and-forget thought capture | `python gsd-capture.py "my idea"` |

Templates in `resources/templates/`: PROJECT.md, MILESTONE-CONTEXT.md,
MILESTONE-ROADMAP.md, SLICE-PLAN.md, REQUIREMENTS.md

---

## The GSD Mindset

> **Ship vertical slices. Context is sacred. Evidence before claims.
> Never build a layer — always build a thread.**

The moment you skip the Discussion Protocol, skip context recovery, accept
"done" without evidence, or let a slice grow beyond 1 day — you are back to vibe coding.

Follow it exactly at first. The payoff compounds at 15+ files and never stops.
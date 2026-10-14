---
name: get-shit-done
description: Use this skill when shipping software with AI agents without context
  rot. Enforces 3-tier work breakdown (Project to Milestone to Slice) and vertical
  slice delivery.
---

# Get Shit Done (GSD)

## Overview

GSD is an engineering methodology for shipping production software with AI agents without hitting the **vibe coding ceiling** — the point where feature-by-feature chat breaks down because the codebase exceeds any single context window.

Context is treated as a managed, scarce resource rather than an append-only chat transcript. Project state, decisions, and knowledge persist deterministically on disk inside `.gsd/`, guaranteeing clean multi-day continuity across agent sessions.

## When to Use

- Break down complex multi-week features into structured, vertically delivered slices.
- Structuring new software initiatives to prevent context drift and hallucinations.
- Planning milestones and tracking progress across multi-agent handoffs.
- Mandatory triggers: `'gsd this'`, `'plan this as gsd'`, `'break this down gsd style'`, `'structure this project'`, `'i want to use gsd'`.
- Strong triggers: `'plan the next milestone'`, `'create a slice'`, `'what should I build next'`, `'set up the project structure'`, `'how do I track progress'`.
- **When NOT to use**: Trivial single-line bug fixes, typo corrections, or small self-contained tasks that comfortably fit into a single conversational context window.

## Core Process & 3-Tier GSD Methodology

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
- **Mandatory STOP-after-spec gate**: After creating `PROJECT.md` or milestone roadmap, STOP and wait for explicit user approval before implementing any slice
- **The ~100-line diff budget**: Every task inside a slice must stay $\le 100\text{--}150$ lines; split oversized tasks vertically
- A slice cuts through ALL layers (DB → API → frontend) for ONE user capability
- A slice fits in ONE context window
- A slice is done ONLY when its UAT test produces fresh execution evidence (per [references/done.md](../../../references/done.md))
- A task that exceeds 60 min gets split
- A slice that exceeds 1 day gets split

---

## The .gsd/ Directory — Project Memory on Disk

```
project-root/
+-- .gsd/
    +-- PROJECT.md              <- Product vision & roadmap
    +-- REQUIREMENTS.md         <- Capability contract with R### IDs
    +-- DECISIONS.md            <- Architectural decisions log (append-only)
    +-- STATE.md                <- Active milestone / slice tracker
    +-- milestones/M###/        <- Milestone context, research & roadmap
```

For the complete `.gsd/` file tree specification, see [references/gsd-artifacts.md](../../../references/gsd-artifacts.md). Scaffolding is automated via `scripts/gsd-init.py`.

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

## The KNOWLEDGE.md & CAPTURES System (Cross-Session Memory)

- **`KNOWLEDGE.md`**: Append-only register of project rules, patterns, and lessons. Loaded at the start of every slice unit to eliminate onboarding context rot. Add rule: `/gsd knowledge [rule]`.
- **`CAPTURES.md`**: Asynchronous thought queue. Capture ideas mid-execution without interrupting auto-mode: `/gsd capture [idea]`. Triaged between slices (`quick-task`, `inject`, `defer`, `replan`, `note`).
- See [references/gsd-artifacts.md](../../../references/gsd-artifacts.md) for full capture triage workflows.

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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"We can just build the entire feature in one long continuous agent session."* | Long sessions suffer severe context degradation, hallucinate prior states, and drop critical safety gates; structured slices prevent context rot. |
| *"I can start coding Slice 1 as soon as I draft the roadmap."* | Violates the STOP-after-spec gate. The user must review and approve the roadmap and slice contracts before any code is modified. |
| *"A task diff of 350 lines is fine because it covers the whole slice."* | Oversized diffs hide edge-case bugs and fail pre-merge review; enforce the $\le 100\text{--}150$ line task budget. |
| *"Horizontal layering (building all DB, then all API, then all UI) is cleaner."* | Horizontal building delays user validation until the end; vertical slices deliver working, testable end-to-end functionality at every step. |
| *"Documentation files (`PROJECT.md`, `STATE.md`) create unnecessary overhead."* | Project state documentation serves as the persistent anchor across session boundaries, eliminating onboarding memory loss. |
| *"I can mark the slice done because the code looks complete."* | Slices are done only when verified by live execution evidence; 'looks right' is strictly disallowed. |
| *"Checking in mid-task breaks developer flow."* | Unchecked agent autonomy on complex tasks leads to massive architectural drift; 15-minute slice checkpoints ensure alignment. |

## Red Flags

- Agent modifying code before receiving explicit approval of the milestone roadmap (breaking STOP-after-spec).
- Task diffs exceeding 150 lines without vertical decomposition.
- Agent declaring a slice complete without executing tests or verifying runtime functionality.
- Slices taking more than 15-20 minutes of continuous tool calls without human checkpoints.
- State files (`.gsd/STATE.md`) drifting out of sync with actual codebase implementation.
- Attempting to start Slice N+1 while Slice N has failing tests or unmerged diffs.
- Building horizontal stubs instead of vertically integrated functional user stories.

## Verification

After completing a GSD milestone or slice, confirm:
- [ ] Project directory contains valid `.gsd/` structure (`PROJECT.md`, `ROADMAP.md`, `STATE.md`, `KNOWLEDGE.md`).
- [ ] Explicit STOP-after-spec gate was observed prior to starting implementation.
- [ ] All committed tasks adhered to the $\le 100\text{--}150$ line diff budget.
- [ ] Active slice satisfies its User Story and all Acceptance Test criteria with live terminal evidence (per [references/done.md](../../../references/done.md)).
- [ ] GSD repository health audit passes: `python skills/orchestration/get-shit-done/scripts/gsd-doctor.py`.
- [ ] Journal log and session state are committed with conventional commit messages.

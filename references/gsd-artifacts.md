# GSD Disk Memory Layout & Artifact Specification

This reference details the full `.gsd/` directory structure, machine-readable schemas, and artifact templates for the Get Shit Done (GSD) methodology.

---

## 1. Complete `.gsd/` File Tree

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

---

## 2. Cross-Session Memory & Captures System

### KNOWLEDGE.md (Append-Only Knowledge Base)
```markdown
## [2026-10-14] [Source: session M001/S01/T02]
- Prisma `contains` is case-sensitive by default. Use `mode: 'insensitive'` for text queries.
- Context: Discovered during user search unit tests.
```

### CAPTURES.md (Thought Queue)
Captures append to `.gsd/CAPTURES.md` and are triaged between task units:
- `quick-task`: Small self-contained fix executed inline.
- `inject`: Task injected into the active slice plan.
- `defer`: Important but deferred to next roadmap reassessment.
- `replan`: Triggers active slice replan.
- `note`: Informational note recorded in `KNOWLEDGE.md`.

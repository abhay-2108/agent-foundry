---
name: session-handoff
description: >-
  Use this skill at the conclusion of a work session, prior to context resets,
  when handing off tasks between agents, or when pausing work on a multi-day initiative.
  Maintains a persistent, machine-readable HANDOFF.md ledger tracking accomplishments,
  active state, blockers, and next immediate steps.
---

# Session Handoff

Prevents context loss, duplicate investigation, and broken workflows across agent session boundaries by maintaining a single source of truth in `HANDOFF.md`.

## When to Use This Skill
- At the end of a user session or before reaching context limits.
- When an agent completes an assigned phase and hands off execution to another agent.
- When switching between major features or divergent git branches.
- Whenever a user asks: "What's the status?", "Where did we leave off?", or "Summarize current state".

## The `HANDOFF.md` Ledger Format

Every handoff must update or create `HANDOFF.md` at the repository root using this structure:

```markdown
# Project State & Handoff Ledger

**Last Updated**: YYYY-MM-DD HH:MM (Local Time)
**Active Branch / Worktree**: `main` or `feature/<name>`
**Current Phase**: [Phase Name / Milestone]

---

## 1. Completed Milestones
- [x] [Date/Time] Feature or bugfix completed. Verified with `npm test`.
- [x] [Date/Time] Documentation updated in `docs/architecture.md`.

## 2. In-Flight Work & Active State
- **Current File Under Edit**: `path/to/active_file.ts` (Lines 40-85)
- **Known State**: Function X refactored; integration test partially drafted.

## 3. Blockers & Dependencies
- [ ] Waiting for API keys or user decision on authentication strategy.
- [ ] Upstream package version conflict on dependency Y.

## 4. Next Immediate Actions (Prioritized)
1. Complete remaining unit test cases in `tests/test_feature.py`.
2. Run full regression suite using `pytest -v`.
3. Submit review summary to user.

## 5. Key Decisions & Rationales
- *Decision*: Adopted SQLite for local caching rather than Redis.
- *Rationale*: Zero-dependency setup, sufficient for single-user desktop agent.
```

## Step-by-Step Execution Workflow

### Step 1: State Inspection
1. Run `git status` or inspect recent file modifications to capture unstaged or recently committed changes.
2. Check test outcomes to determine if current worktree is green or red.
3. Review user conversation to note outstanding questions or user directives.

### Step 2: Ledger Update
1. Read existing `HANDOFF.md` if present.
2. Prepend or update recent accomplishments under **Completed Milestones**.
3. Record current active state, precise files, line ranges, and immediate next commands.
4. Overwrite `HANDOFF.md` with clean formatting.

### Step 3: Session Resumption Protocol
When starting a new session or receiving a prompt after a reset:
1. First read `HANDOFF.md`.
2. Echo a brief 2-bullet summary to the user: "Resuming from [Milestone]; proceeding with [Next Immediate Action]".
3. Continue execution directly without re-investigating established facts.

## Anti-Patterns & Traps to Avoid
- **Unanchored Pronouns & Ambiguous Targets**: Describing next steps as "fix that bug" or "clean up the script" without exact relative/absolute file paths and symbol names, causing successor agents to re-scan the entire codebase.
- **Omitting In-Flight Terminal Commands & Uncommitted State**: Leaving git worktrees dirty or background processes running without recording exact PID/command state, leading to file access locks or duplicated executions.
- **Stale Ledger Bloat**: Appending endless narrative logs to `HANDOFF.md` instead of maintaining a concise, overwritten state document with clear Active Context vs. Historical Milestones.
- **Silent Assumption Resumption**: Resuming execution without confirming that modified dependencies, virtual environments, or environment variables in the previous session are still active.

## Quality Checklist
- [ ] `HANDOFF.md` contains exact file paths, line ranges, and function/class identifiers.
- [ ] Pending, in-flight, or failed CLI commands and test outcomes are explicitly recorded.
- [ ] Architectural decisions, deferred trade-offs, and user instructions are documented with rationale.
- [ ] Actionable immediate next steps are ranked chronologically without vague instructions.
- [ ] The handoff document is formatted with clean markdown, valid headings, and no dangling references.
- [ ] Successor agent can resume work autonomously within 1 turn without asking clarifying questions.

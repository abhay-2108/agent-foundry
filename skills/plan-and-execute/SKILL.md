---
name: plan-and-execute
description: >-
  Use this skill when receiving complex, ambiguous, or multi-step engineering and research
  tasks. Enforces architectural risk analysis, bite-sized task planning (2-5 minutes per task),
  rollback milestones, and user alignment before executing file modifications or writing code.
---

# Plan and Execute: Engineering Methodology

A foundational productivity and engineering skill that eliminates rabbit holes, hallucinations, regressions, and destructive edits by enforcing pre-flight architectural risk analysis, bite-sized task decomposition, and progressive verification.

---

## When to Use This Skill

- When a user request involves non-trivial changes spanning multiple files, packages, or architectural layers.
- When requirements are ambiguous, open-ended, or subject to multiple architectural trade-offs.
- Before executing major refactoring, library migrations, database alterations, or greenfield implementations.
- Whenever entering planning mode or when asked to design an autonomous agent execution strategy.
- Trigger phrases: `"plan this out"`, `"architect solution"`, `"create implementation plan"`, `"plan and execute"`, `"design roadmap"`.

---

## The 4 Golden Principles of Execution

1. **No Code Before Plan**: Never create or modify source files without an explicit, approved technical breakdown.
2. **Bite-Sized Atomic Tasks**: Deconstruct work into small, independently verifiable tasks (2–5 minutes of work each).
3. **Explicit Paths & Acceptance Gates**: Every task must cite exact file paths and a concrete, runnable verification command.
4. **Pre-Mortem Risk & Rollback Points**: Identify the highest-blast-radius actions and define safe rollback milestones before editing.

---

## Step-by-Step Planning Workflow

### Step 1: Context & Pre-Mortem Risk Analysis
1. **Inspect Active Baseline**: Check build state and tests (`npm test`, `pytest`, `cargo check`) to guarantee the workspace is green *before* modifying code.
2. **Blast Radius Assessment**: Classify changes as **Reversible** (additive functions, new test files) or **Irreversible/Destructive** (database drops, breaking API contract changes, mass file renames).
3. **Define Rollback Milestones**: Establish clean Git commit SHAs or stash points before executing high-risk stages.

### Step 2: Formulate the Implementation Plan Artifact
Draft a structured plan (e.g., `implementation_plan.md`) following this structure:
```markdown
# [Feature / Task Name] Implementation Plan

## Objective & Scope
- In-Scope: [Concrete deliverables]
- Out-of-Scope: [Explicit exclusions to prevent scope creep]

## Architectural Trade-Offs & Decision Log (ADR)
- Alternative A vs Alternative B (Rationale for selection)

## Step-by-Step Task Breakdown
- [ ] Task 1: [Target File] - Add data model / schema. 
      Verification: Run `pytest tests/test_schema.py`.
- [ ] Task 2: [Target File] - Implement core service method. 
      Verification: Run `pytest tests/test_service.py -k test_happy_path`.
- [ ] Task 3: [Target File] - Wire route controller and validation middleware. 
      Verification: Run curl test script against local test server.

## Rollback & Failure Recovery Plan
- If Task 2 fails integration: Revert with `git checkout -- <file>` and report root cause.
```

### Step 3: Seek User Alignment
- Present the plan directly to the user. Highlight open design questions, breaking changes, or trade-offs.
- **Stop and wait** for explicit user approval before touching project code.

### Step 4: Progressive Stepwise Execution & Verification
- Execute strictly one task at a time.
- After completing each task, run its designated verification command immediately.
- Never bundle multiple unverified edits together. If a test fails, fix it before moving to the next item.

---

## Anti-Patterns & Traps to Avoid

1. **The "Big Bang" Edit**: Modifying 8 different files across frontend, backend, and database simultaneously before running a single compiler or test check. When things break, root-cause isolation is impossible.
2. **Plan-Reality Drift (Sunk Cost Fallacy)**: Continuing to execute an approved plan when discovered runtime facts contradict the original assumptions. Always halt, update the plan, and realign with the user.
3. **Stealth Scope Creep**: Silently refactoring unrelated functions, renaming existing variables, or fixing peripheral lints outside the agreed scope. Keep PRs and commits atomic.
4. **Vague, Non-Verifiable Tasks**: Writing plan tasks like *"Improve error handling"* or *"Clean up backend logic"*. Every task must specify: (1) Exact file, (2) exact modification, and (3) runnable pass/fail verification test.

---

## Quality Checklist

- [ ] Baseline test suite passes *before* making any source code modifications.
- [ ] Tasks are decomposed into atomic, independent 2–5 minute chunks.
- [ ] Every task cites exact file paths and explicit verification commands.
- [ ] High-risk actions (breaking changes, schema drops) have defined rollback milestones.
- [ ] User alignment was requested and received prior to execution.
- [ ] Post-implementation regression checks confirm zero unintended collateral damage.

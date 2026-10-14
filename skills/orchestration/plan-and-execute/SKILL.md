---
name: plan-and-execute
description: >-
  Use this skill when receiving complex, ambiguous, or multi-step engineering and research
  tasks. Enforces architectural risk analysis, bite-sized task planning (2-5 minutes per task),
  rollback milestones, and user alignment before executing file modifications or writing code.
---

# Plan and Execute: Engineering Methodology

## Overview

Decomposes complex, ambiguous, or multi-step engineering initiatives into structured Directed Acyclic Graph (DAG) plans. Enforces bite-sized tasks (2–5 minutes), architectural risk analysis, rollback checkpoints, and human alignment before modifying files.

## When to Use

- When a user request involves non-trivial changes spanning multiple files, packages, or architectural layers.
- When requirements are ambiguous, open-ended, or subject to multiple architectural trade-offs.
- Before executing major refactoring, library migrations, database alterations, or greenfield implementations.
- Whenever entering planning mode or when asked to design an autonomous agent execution strategy.
- Trigger phrases: `"plan this out"`, `"architect solution"`, `"create implementation plan"`, `"plan and execute"`, `"design roadmap"`.

---
- **When NOT to use**: Single-line typo fixes or trivial one-file updates that require no multi-step orchestration.

## Core Process & Engineering Planning Methodology

## The 5 Golden Principles of Execution

1. **No Code Before Spec & Plan**: Never create or modify source files without an explicit, approved technical breakdown.
2. **Gated STOP-After-Spec**: After producing the specification and implementation plan, the agent **MUST STOP AND HALT**. Never begin writing code until the user provides explicit approval.
3. **The ~100-Line Diff Budget**: Every task slice must stay within a strict $\le 100\text{--}150$ line change limit. Massive diffs hide bugs and evade review. If a change exceeds 150 lines, split it into vertical sub-slices.
4. **Bite-Sized Atomic Tasks**: Deconstruct work into small, independently verifiable tasks (2–5 minutes of work each).
5. **Explicit Paths & Acceptance Gates**: Every task must cite exact file paths and a concrete, runnable verification command meeting [references/done.md](../../../references/done.md) standards.

---

## The Gated Lifecycle Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 1: SPECIFY  │ Define requirements, schemas, boundary constraints │
├───────────────────┼────────────────────────────────────────────────────┤
│ Stage 2: PLAN     │ Architecture, trade-offs, rollback checkpoints     │
├───────────────────┼────────────────────────────────────────────────────┤
│   🛑 HARD GATE    │ STOP-AFTER-SPEC: Await explicit user approval      │
├───────────────────┼────────────────────────────────────────────────────┤
│ Stage 3: TASKS    │ Decompose into micro-slices (<= 100-150 lines)     │
├───────────────────┼────────────────────────────────────────────────────┤
│ Stage 4: IMPLEMENT│ Execute task -> Verify (RED/GREEN) -> Commit       │
└───────────────────┴────────────────────────────────────────────────────┘
```

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

## Step-by-Step Task Breakdown (Max 100-150 lines per slice)
- [ ] Task 1: [Target File] - Add data model / schema (Diff budget: ~50 lines). 
      Verification: Run `pytest tests/test_schema.py`.
- [ ] Task 2: [Target File] - Implement core service method (Diff budget: ~80 lines). 
      Verification: Run `pytest tests/test_service.py -k test_happy_path`.
- [ ] Task 3: [Target File] - Wire route controller and validation middleware (Diff budget: ~60 lines). 
      Verification: Run curl test script against local test server.

## Rollback & Failure Recovery Plan
- If Task 2 fails integration: Revert with `git checkout -- <file>` and report root cause.
```

### Step 3: Mandatory STOP-After-Spec Gate
- Present the plan directly to the user. Highlight open design questions, breaking changes, or trade-offs.
- **STOP EXECUTION IMMEDIATELY**. Do not edit project code files or create implementation drafts. Wait for explicit user confirmation.

### Step 4: Progressive Stepwise Execution & Verification
- Execute strictly one task at a time.
- Verify diff budget: run `git diff --stat` to ensure changes stay $\le 100\text{--}150$ lines.
- Run designated verification commands immediately. Refer to [references/testing.md](../../../references/testing.md) for the Prove-It pattern.
- Never bundle multiple unverified edits together. If a test fails, fix it before moving to the next item.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"We should start coding immediately; we can plan as we go."* | Coding without an upfront DAG plan leads to architecturally tangled code, half-implemented features, and wasted engineering hours. |
| *"I can start implementing Task 1 right away after writing the plan."* | Violates the STOP-after-spec gate. The user must review trade-offs and approve scope before any file modifications begin. |
| *"A 400-line diff is fine because all the code is closely related."* | Diffs over 150 lines receive superficial review and have exponential bug density. Split into vertical slices. |
| *"A 10-step plan doesn't need rollback checkpoints."* | If step 8 breaks the build, absence of rollback checkpoints forces frantic, error-prone manual git surgery. |
| *"Each task in the plan can be 'Implement the whole backend'."* | Oversized tasks cause context drift and hide progress; tasks must be bite-sized (2-5 minutes) with discrete exit criteria. |

## Red Flags

- Modifying code files before presenting the plan and receiving explicit user approval (breaking STOP-after-spec).
- Task diffs exceeding 150 lines without splitting into sub-slices.
- Plans lacking explicit rollback strategies or git branch checkpoints.
- Tasks described vaguely ('update files') without specifying target files, diff budgets, and expected outputs.
- Proceeding through subsequent plan tasks while earlier task tests are failing.

## Verification

After completing the workflow, confirm:
- [ ] Implementation plan decomposes objective into sequenced, bite-sized tasks with dependency ordering.
- [ ] Each task specifies target files, diff budget ($\le 150$ lines), verification commands, and expected outputs.
- [ ] Explicit STOP-after-spec gate was observed and user approval was received prior to modifying code.
- [ ] Architectural trade-offs and decision rationale are logged.
- [ ] Verified against criteria in [references/done.md](../../../references/done.md).

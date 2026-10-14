---
name: session-handoff
description: Use this skill when concluding a work session, prior to context resets,
  transferring work between agents, or recording active progress in HANDOFF.md.
---

# Session Handoff

## Overview

Maintains a persistent, machine-readable `HANDOFF.md` ledger across session resets, agent transfers, and multi-day initiatives. Tracks accomplished milestones, active in-flight state, known blockers, and immediate next steps to eliminate onboarding memory loss.

## When to Use

- At the end of a user session or before reaching context limits.
- When an agent completes an assigned phase and hands off execution to another agent.
- When switching between major features or divergent git branches.
- Whenever a user asks: "What's the status?", "Where did we leave off?", or "Summarize current state".
- **When NOT to use**: Transient, momentary conversational pauses within the same active session.

## Core Process & Persistent Handoff Ledger Architecture

## The `HANDOFF.md` Ledger Format

Every handoff must update or create `HANDOFF.md` at the repository root using this exact specification containing all 5 mandatory sections:

```markdown
# Project State & Handoff Ledger

**Last Updated**: YYYY-MM-DD HH:MM (Local Time)
**Outgoing Agent**: `@specialist-name`
**Next Assigned Agent**: `@successor-agent`
**Active Branch / Worktree**: `.worktrees/feature-<name>` (Branch: `feature/<name>`)
**Base Commit / Ref**: `git rev-parse --short HEAD`
**Current Phase**: [Phase Name / Sprint Milestone]
**Environment & Python**: Python 3.12.x / venv active / Dependencies synchronized

---

## 1. Completed Milestones
- [x] **[Timestamp UTC] Milestone Name**: Description of what was built or fixed.
  - *Files Touched*: `path/to/file1.py`, `path/to/file2.py`
  - *Verification Command*: `pytest tests/test_file.py` (Result: 12 passed, 0 failed, 100% pass rate)
  - *Commit Hash*: `a1b2c3d`

## 2. In-Flight Work & Active State
- **Active File(s) Under Edit**:
  - `path/to/primary.py` (Lines 112–185) — Currently implementing error handling for transient HTTP 503s.
- **Uncommitted Changes**:
  - Modified: `src/router.py` (Added query parameter validation)
  - Untracked: `tests/test_router_edge_cases.py` (Scaffolded 3 test stubs)
- **Runtime / Test Status**:
  - Last Run: `pytest tests/test_router.py` → 4 passed, 1 error (`test_timeout_retry` pending mock).
- **Background Processes**:
  - None active (all child processes terminated cleanly).

## 3. Blockers & Dependencies
- [ ] **External Dependency**: Awaiting user decision on auth strategy (JWT vs. Session Cookie).
- [ ] **Environment Variable**: `THIRD_PARTY_API_KEY` missing from `.env` (stubbed in mock suite).

## 4. Next Immediate Actions (Prioritized)
1. **Implement retry mock**: Finish `tests/test_router_edge_cases.py` mock adapter for 503 timeout.
2. **Execute regression test**: Run `pytest -v tests/` to ensure zero regressions across full test suite.
3. **Trigger code review**: Dispatch PR diff to `@code-quality-auditor` for cyclomatic complexity and typing audit.
4. **Clean worktree**: Merge worktree branch to `main` via `git merge --ff-only` once auditor signs off.

## 5. Key Decisions, Rationales & Architectural Context
- **Decision**: Selected SQLite WAL mode over external Redis instance for agent memory store.
  - *Rationale*: Zero-ops local desktop requirement; SQLite WAL achieves <1ms latency with concurrent readers.
- **Decision**: Enforced Pydantic v2 strict models for all MCP tool arguments.
  - *Rationale*: Prevents runtime LLM parameter hallucination before hitting core business logic.
- **Deferred Items**: Defer gRPC transport protocol to v2.0; HTTP/JSON-RPC is sufficient for current traffic.
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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"The next session can just read the git log to see what was done."* | Git logs show what changed, but they do NOT show what failed, why certain decisions were made, or what in-flight blockers remain. |
| *"I'll write the handoff note tomorrow when I resume work."* | Working memory degrades immediately; write the handoff ledger at the conclusion of the session while state is fresh. |
| *"A 2-sentence summary in chat is enough."* | Chat messages are lost across context resets; handoff ledgers must be persisted to disk in `HANDOFF.md`. |
| *"Listing next steps isn't necessary because the roadmap is clear."* | Roadmaps have high-level milestones; next sessions need the immediate command, file, or test to run next. |

## Red Flags

- Ending a session with uncommitted dirty working tree changes without documenting state in `HANDOFF.md`.
- Handoff notes describing vague achievements ('worked on backend') without listing modified files and tests.
- Missing the 'Immediate Next Step' command or action for the resuming agent.
- Failing to document unresolved bugs or environmental blockers.

## Verification

After completing the workflow, confirm:
- [ ] `HANDOFF.md` is updated with Current State, Completed Items, Active Blockers, and Immediate Next Steps.
- [ ] Modified file paths and git commit hashes are explicitly cited.
- [ ] Exact CLI command to resume verification is documented.
- [ ] Handoff validator passes cleanly: `python skills/orchestration/session-handoff/scripts/validate_handoff.py`.

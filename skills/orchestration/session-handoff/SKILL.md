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

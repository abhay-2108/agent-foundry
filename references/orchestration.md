# Canonical Multi-Agent Orchestration & Delegation Standards

This reference specifies governance rules, inter-agent communication contracts, DAG state machines, and context handoff protocols for multi-agent systems.

---

## 1. The Strict 3-Layer Agent Hierarchy

```
┌────────────────────────────────────────────────────────┐
│ COMMAND / ORCHESTRATOR (When to run: User / Slash Cmd) │
└──────────────────────────┬─────────────────────────────┘
                           │ Dispatches
                           ▼
┌────────────────────────────────────────────────────────┐
│ PERSONA (Who is running: Autonomous Specialist Actor)  │
└──────────────────────────┬─────────────────────────────┘
                           │ Executes
                           ▼
┌────────────────────────────────────────────────────────┐
│ SKILL (How to do it: Stateless, Step-by-Step SOP)      │
└────────────────────────────────────────────────────────┘
```

### Golden Rules of Agent Delegation:
1. **Personas NEVER Invoke Personas Directly**: A specialist persona (e.g., `@fullstack-engineer`) must never invoke another specialist persona (e.g., `@security-red-teamer`). Only the user or `@lead-orchestrator` may dispatch personas. This rule prevents circular delegation loops and token exhaustion.
2. **The Canonical Fan-Out / Fan-In Pattern**:
   - The only endorsed parallel multi-agent delegation pattern is the **Release / Audit Fan-Out**:
   ```mermaid
   flowchart LR
       UserOrLeader[Lead Orchestrator / /ship] -->|Parallel Task 1| Auditor[Code Quality Auditor]
       UserOrLeader -->|Parallel Task 2| SecTeamer[Security Red-Teamer]
       UserOrLeader -->|Parallel Task 3| SREGuardian[SRE DevOps Guardian]
       
       Auditor -->|Findings| Merge[Lead Merges Verdicts]
       SecTeamer -->|Findings| Merge
       SREGuardian -->|Findings| Merge
       Merge -->|Unified Decision| Result{GO / NO-GO}
   ```
3. **Bounded Iteration**: Every agent loop must define an explicit `max_iterations` cutoff ($\le 5$). An agent that fails to converge within the limit must halt and yield control to the user.

---

## 2. Standard Inter-Agent Communication Envelope

When `@lead-orchestrator` dispatches a task to a specialist persona, the task must use this standard JSON envelope:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "task_id": "TASK-2026-1014-01",
  "parent_trace_id": "trace-8842af91",
  "dispatched_by": "lead-orchestrator",
  "assigned_agent": "code-quality-auditor",
  "objective": "Audit pre-merge PR diff for security vulnerabilities and type regressions",
  "context_boundaries": {
    "git_branch": "feature/payment-webhook-auth",
    "target_files": [
      "src/api/webhooks/payment.py",
      "tests/test_payment_webhooks.py"
    ],
    "diff_line_budget": 120
  },
  "acceptance_criteria": [
    "Verify HMAC signature validation logic",
    "Ensure zero secrets or raw payloads leaked in logs",
    "Confirm unit tests pass with 100% exit code 0"
  ]
}
```

---

## 3. Persistent Checkpointing & Session Handoff

When transitioning work between sessions, agents, or after executing a slice:
1. **Update `.gsd/STATE.md` or `HANDOFF.md`**: Record active milestone, completed tasks, open blockers, and the next single command to run.
2. **Record Semantic Milestones**: Store key architectural decisions and conventions in Tier 3 semantic memory using `memory_record_fact`.
3. **Commit Clean Git Checkpoint**: Commit changes with an atomic conventional commit message citing the task ID (e.g., `feat(webhooks): validate stripe signature [TASK-01]`).

---

## 4. Orchestration Quality Audit Checklist

- [ ] Task envelope specifies clear, bounded acceptance criteria.
- [ ] No specialist persona attempted to invoke another specialist persona.
- [ ] Parallel fan-out tasks executed concurrently without shared file write conflicts.
- [ ] Merge step verified all individual exit criteria before declaring a unified Go/No-Go verdict.
- [ ] Session state is deterministically written to disk (`HANDOFF.md` or `.gsd/`).

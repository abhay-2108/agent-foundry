# Definition of Done (DoD) & Release Gate Checklist

Use this canonical checklist before marking any task, pull request, slice, or release as **Done**. 
Every item represents an objective quality gate; subjective claims ("looks good") do not satisfy these criteria.

---

## 1. Code Quality & Diff Discipline
- [ ] **Diff Budget Adherence**: Total changes for the task/slice are strictly $\le 100\text{--}150$ lines. Monolithic multi-hundred line diffs must be broken into vertical slices.
- [ ] **No Drive-by Refactorings**: Diff contains *only* files and lines directly pertinent to the target requirement. No unrelated formatting, whitespace fixes, or gratuitous edits.
- [ ] **Rule of 500 Lines**: No modified or newly introduced file exceeds 500 lines. Oversized files must be decomposed into focused submodules.
- [ ] **Dead Code & Debug Sanitization**: Zero leftover `console.log`, `print()`, commented-out code, temporary debug flags, or unused imports.
- [ ] **Documentation & Comments**: Complex business logic, non-obvious algorithms, and domain edge cases are documented with concise, factual comments explaining *why*, not just *what*.

---

## 2. Type Safety & Static Analysis
- [ ] **Compiler Clean**: Static type checker passes with zero errors and zero warnings (`tsc --noEmit`, `mypy --strict`, `pyright`, `cargo check`).
- [ ] **No Escape Hatches**: No unapproved `any`, `unknown` casts, `@ts-ignore`, `# type: ignore`, or blanket linter disable directives without explicit architectural justification.
- [ ] **Linter & Formatter Clean**: Zero linter errors under the repository standard (`eslint`, `ruff`, `golangci-lint`, `prettier`).

---

## 3. Automated Verification & Test Evidence
- [ ] **Prove-It Evidence**: If addressing a defect, a standalone reproduction test was executed in RED state before the fix, and now passes in GREEN state.
- [ ] **100% Preexisting Test Suite Green**: Zero regressions across existing unit, integration, and end-to-end suites.
- [ ] **New Coverage Added**: Unit tests cover happy path, boundary edge cases (empty lists, 0, null, boundary values), and error states.
- [ ] **Deterministic Execution**: Tests execute without race conditions, timing flakiness, or hardcoded sleep statements.

---

## 4. Security & Secret Hygiene
- [ ] **Secret Scan Clean**: `git diff` contains no API keys, private tokens, passwords, database URLs, or `.env` credential leaks.
- [ ] **Input Sanitization**: All untrusted external inputs are validated and sanitized via typed schemas (Pydantic, Zod, Marshmallow).
- [ ] **Subprocess Safety**: Command executions avoid shell string concatenation and disable sandbox bypass unless explicitly approved.

---

## 5. Architectural Alignment & State Persistence
- [ ] **Single Responsibility**: Each new class or function performs one clear responsibility.
- [ ] **Chesterton's Fence Honored**: No existing patterns or abstractions were deleted without understanding their original intent.
- [ ] **State & Memory Persisted**: If architectural decisions were made, they are recorded in `.gsd/DECISIONS.md` or persistent semantic memory (`memory_record_fact`).

---

## 6. Verification Command Proof Table

Every pull request or completion report must conclude with this evidence table:

| Gate | Command Executed | Exit Code | Verified Output / Metric |
| :--- | :--- | :--- | :--- |
| **Type Check** | `npm run typecheck` or `mypy .` | `0` | `0 errors found` |
| **Lint** | `npm run lint` or `ruff check .` | `0` | `All rules passed` |
| **Unit Tests** | `pytest tests/` or `npm test` | `0` | `XX passed, 0 failed` |
| **Diff Stat** | `git diff --stat` | `0` | `X files changed, +Y, -Z lines (<150 lines)` |

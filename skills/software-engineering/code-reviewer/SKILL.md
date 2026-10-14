---
name: code-reviewer
description: Use this skill when performing rigorous, senior-level code reviews on
  diffs, pull requests, and existing files. Enforces 5-axis review and pre-merge quality
  gates.
---

# Code Reviewer & Architecture Auditor

## Overview

Performs senior staff engineer-level code reviews across five dimensions: Correctness, Readability, Architecture, Security, and Performance. Enforces automated pre-merge gates, cyclomatic complexity limits, and type safety standards.

## When to Use

- Before opening a pull request or merging a feature branch.
- When reviewing a PR or diff submitted by a contributor or subagent.
- When checking a codebase for code smells, anti-patterns, or architectural debt.
- Prior to declaring an implementation task complete.
- Trigger phrases: `"review this code"`, `"peer review"`, `"critique this PR"`, `"code review gate"`, `"audit this diff"`, `"check for code smells"`.
- **When NOT to use**: Authoring the original feature code from scratch (use `fullstack-engineer`).

## Core Process & 5-Axis Code Review Matrix

## Core Review Tenets
1. **Automated Sanity First**: Run linters, type checks, and unit tests before reviewing logic. Never review code that fails compilation or tests.
2. **Be Constructive & Specific**: Cite exact lines and file paths; explain the *rationale* behind every suggestion, not just personal stylistic preference.
3. **Prioritize Impact**: Distinguish between **Blockers** (critical bugs, data corruption, broken contracts), **Improvements** (architectural polish, performance, naming), and **Nitpicks** (minor formatting).
4. **Simplicity over Cleverness**: Flag unnecessary abstractions, premature generalizations, and over-engineered patterns. The best code is simple and readable.
5. **Resilience First**: Check what happens when things go wrong (network drop, unexpected nulls, malformed payloads).

---

## The 2-Stage Review Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Senior Code Review Pipeline                     │
├──────────────────────────────────┬─────────────────────────────────────┤
│ Stage 1: Automated Quality Gate  │ Stage 2: 6-Dimensional Deep Review   │
│ (Diff Sanity, Linting, Tests)    │ (Logic, Arch, Errors, Perf, Clean)  │
└──────────────────────────────────┴─────────────────────────────────────┘
```

### Stage 1: Automated Quality Gate
Before manual line-by-line critique, verify that the baseline passes:
- [ ] **Diff Sanity**: Run `git diff`. Ensure no accidental changes to `.env`, credentials, or temporary debug statements (`console.log`, `print()`).
- [ ] **Static Type Checking**: Code passes compiler validation without errors (`tsc --noEmit`, `mypy`, `pyright`).
- [ ] **Lint & Formatting**: No linter errors or warnings (`eslint`, `ruff`, `golangci-lint`).
- [ ] **Regression Tests**: 100% of preexisting tests pass, and new code includes unit/integration coverage.

---

### Stage 2: The 6-Dimensional Deep Review

#### 1. Correctness & Edge Cases
- Does the code actually fulfill all stated functional requirements?
- Are boundary conditions handled (`0`, `-1`, empty collections, off-by-one indices)?
- Are `null`, `undefined`, or missing dictionary keys guarded safely?
- Are there potential race conditions in asynchronous or concurrent code?

#### 2. Architecture & Design Principles
- **Single Responsibility**: Does each function or class have a single, well-defined job?
- **DRY (Don't Repeat Yourself)**: Is there duplicated logic that should be unified?
- **Interface Segregation**: Are parameter lists reasonable (< 4-5 arguments, or using typed options objects)?
- **No Leaky Abstractions**: Do high-level modules know too much about low-level storage or network implementations?

#### 3. Error Handling & Robustness
- Are errors handled explicitly rather than swallowed blindly (`catch (e) {}` or `except: pass`)?
- Are error messages informative, including the failed value and operation?
- Are external network/database calls wrapped with appropriate timeouts and retries?

#### 4. Performance & Resource Cleanup
- Are there hidden $O(N^2)$ loops or nested iterations over large datasets?
- Are database queries batched to avoid N+1 lookups?
- Are file handles, database connections, sockets, or event listeners cleaned up properly?

#### 5. Readability & Maintainability
- Are variable and function names self-descriptive (e.g., `isCustomerEligible` vs `flag`)?
- Is dead code, commented-out debugging code, or unused imports left behind?
- Are complex business logic blocks accompanied by clear comments explaining the *why*?

#### 6. Security Delegation
- For dedicated OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF, Path Traversal) or secret leakage audits, invoke the companion **`security-vulnerability-scanner`** skill.

---

---

## Review Severity Matrix & Gate Policy

All findings must be classified according to this standardized severity matrix:

| Severity | Definition & Impact | Examples | PR Gate Policy |
|:---|:---|:---|:---|
| **BLOCKER** | Direct production crash, data loss, security exposure, or regression | Unhandled null pointer, SQL injection, missing DB transaction rollback, broken build | **HARD BLOCK**: PR merge prohibited under all circumstances |
| **HIGH** | Major architectural defect, concurrency race condition, or memory leak | Unclosed DB connections, $O(N^2)$ iteration in hot path, unvalidated external payload | **HARD BLOCK**: Requires author remediation and re-review |
| **MEDIUM** | Suboptimal pattern, poor error diagnostics, missing edge test coverage | Swallowed exception without logging, missing unit test for error branch, duplicated business logic | **SOFT BLOCK**: Permitted to merge with tracked follow-up ticket |
| **LOW** | Minor readability, inconsistent naming, dead code, or documentation gap | Misleading variable name, unpinned dependency in dev, missing docstring parameter description | Non-blocking: Author can accept or defer |
| **NITPICK** | Cosmetic style preference that escaped linter | Redundant parentheses, minor whitespace preference | Non-blocking: Purely informational |

---

## PR Diff Code Review Output Format (Machine & Human Parseable)

When performing automated review passes, emit both human-readable Markdown and structured JSON:

```json
{
  "$schema": "agent-code-review/v1",
  "review_id": "CR-2026-0911-01",
  "pr_target": "feature/auth-jwt",
  "base_ref": "main",
  "overall_verdict": "CHANGES_REQUESTED",
  "automated_checks": {
    "types_passed": true,
    "linters_passed": true,
    "tests_passed": true,
    "test_coverage_percent": 91.4
  },
  "findings_summary": {
    "blocker": 1,
    "high": 0,
    "medium": 2,
    "low": 1,
    "nitpick": 0
  },
  "findings": [
    {
      "id": "FINDING-001",
      "severity": "BLOCKER",
      "category": "Resource Management & Resilience",
      "file": "src/api/auth.py",
      "line_range": [45, 52],
      "title": "Database connection leak on authentication failure",
      "description": "Database connection acquired outside try/finally block. If password verification raises an exception, the connection remains open and leaks.",
      "suggested_diff": "@@ -45,4 +45,4 @@\\n-conn = db_pool.get_connection()\\n-verify_password(password, conn)\\n+with db_pool.get_connection() as conn:\\n+    verify_password(password, conn)"
    }
  ]
}
```

### Markdown Review Summary Template

```markdown
# 🔍 Senior Code Review: [Component / Feature Name]

**Review Verdict**: 🟢 **Approved** / 🟡 **Approved with Suggestions** / 🔴 **Changes Requested**

---

### 🚦 Automated Quality Gate
- [x] Static Analysis & Type Checking: Clean
- [x] Regression & Unit Tests: Passing (X tests executed)
- [x] Diff Scoped & Clean: No stray debug code or credentials

---

### 🚨 Critical Blockers (Must Fix Before Merge)
- [ ] `path/to/file:L20-L35`: Brief title of blocker.
  - *Issue*: Explain the bug, data corruption, or crash risk.
  - *Recommendation*: Provide the concrete code fix.

### 💡 Architectural & Performance Improvements
- [ ] `path/to/file:L50-L62`: Optimization opportunity.
  - *Observation*: Explain the code smell or inefficiency.
  - *Suggested Pattern*: Show cleaner alternative implementation.

### 🧹 Nitpicks & Readability (Optional Polish)
- [ ] `path/to/file:L12`: Rename variable `data` to `validatedUserInput` for clarity.

### 🌟 What Was Done Well
- Highlight positive aspects of the implementation (clean types, thorough tests, elegant abstractions).
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"The tests pass, so the code must be ready to merge."* | Passing tests don't catch architectural debt, security leaks, memory bloat, or unmaintainable complexity. |
| *"I don't want to be annoying by pointing out messy naming or deep nesting."* | Senior code review is kind, clear, and unyielding on maintainability; clean naming prevents thousands of hours of future confusion. |
| *"A 1,000-line diff is fine if it's all part of the same feature."* | Massive diffs receive superficial reviews and harbor the highest defect density; demand vertical or horizontal PR splitting. |
| *"Refactoring and feature work should be combined to save time."* | Mixing refactoring with new feature logic obscures functional changes in git bisect and complicates rollbacks. |

## Red Flags

- New conditional branches bolted onto unrelated control flows instead of extracting dedicated handlers.
- Gratuitous `any`, `unknown`, or unsafe type-casts bypassing compiler type checking.
- PRs exceeding 300 changed lines without a compelling architectural justification.
- Review approvals granted without reviewing the actual line diff and test coverage.

## Verification

After completing the workflow, confirm:
- [ ] All five axes (Correctness, Readability, Architecture, Security, Performance) are reviewed and scored.
- [ ] Structural remedies (e.g. dispatchers, helpers, type boundaries) are proposed for all flagged smells.
- [ ] Automated gates (linter, types, unit tests) pass with zero errors.
- [ ] PR description clearly explains what changed, why, and how to verify.

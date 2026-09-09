---
name: code-reviewer
description: >-
  Use this skill to perform rigorous, senior-level code reviews on diffs, pull requests,
  and existing files. Enforces automated pre-merge gates (linting, static typing, test coverage)
  along with architectural review, separation of concerns, edge case handling, readability,
  and project consistency.
---

# Code Reviewer & Architecture Auditor

Acts as a senior staff engineer peer-reviewer. Provides thorough, actionable feedback on code diffs, pull requests, and refactorings. Combines an automated quality gate (static analysis, types, tests) with deep architectural inspection to ensure code is clean, maintainable, resilient, and enterprise-grade.

## When to Use This Skill
- Before opening a pull request or merging a feature branch.
- When reviewing a PR or diff submitted by a contributor or subagent.
- When checking a codebase for code smells, anti-patterns, or architectural debt.
- Prior to declaring an implementation task complete.
- Trigger phrases: `"review this code"`, `"peer review"`, `"critique this PR"`, `"code review gate"`, `"audit this diff"`, `"check for code smells"`.

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

## Code Review Feedback Template

When delivering a review, output findings in this structured format:

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

---

## Anti-Patterns & Traps to Avoid

1. **The "LGTM" Rubber Stamp**: Approving pull requests after a superficial skim without executing static typechecks or scrutinizing boundary conditions. Reviewers share responsibility for every line merged into production.
2. **Bike-Shedding Formatting Over System Architecture**: Spending 80% of review bandwidth arguing over semicolon style or variable name cosmetics while missing unindexed $O(N^2)$ database loops or absent transaction rollbacks. Delegate style to automated linters (`black`, `prettier`, `biome`) and focus human/agent attention on correctness and architecture.
3. **Vague, Non-Actionable Critiques**: Leaving comments like *"This looks messy, refactor this"* without offering a concrete code replacement or explaining the concrete failure mode. Always provide a clear diff suggestion.
4. **Attempting to Review Mega-Diffs**: Reviewing 2,000+ line PRs spanning unrelated subsystems in a single pass. Defect detection rates plummet after 400 lines; require authors to decompose massive changes into stacked, reviewable PRs.

---

## Quality Checklist

- [ ] Static typing and linters run completely green before manual inspection begins.
- [ ] Automated test coverage exists for all new or modified code branches.
- [ ] Review distinguishes strictly between Critical Blockers, Improvements, and Nitpicks.
- [ ] All requested changes include concrete code recommendations and clickable line links.
- [ ] Database interactions are checked for N+1 queries, indexing, and transaction safety.
- [ ] Resource cleanup (closing file handles, connections, streams) is verified.

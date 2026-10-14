---
name: git-plumbing-and-automation
description: Use this skill when executing advanced Git workflows, automated bisect
  bug hunts, git worktree sandboxes, and conventional commit generation.
---

# Advanced Git Plumbing & Repository Automation

## Overview

Executes advanced Git plumbing workflows, automation scripts, and repository recovery. Implements automated git bisect regression triage, git worktree sandboxes, reflog commit recovery, and conventional commit generation.

## When to Use

- When hunting down which commit introduced a silent regression across hundreds of commits (`git bisect`).
- When working on multiple parallel branches simultaneously without switching checkouts (`git worktree`).
- When recovering accidentally deleted branches, stashes, or uncommitted commits (`git reflog`).
- When squashing messy commits and generating Conventional Commit messages for pull requests.
- Trigger phrases: `"git bisect"`, `"recover lost commit"`, `"create git worktree"`, `"git reflog"`, `"squash commits"`.

---
- **When NOT to use**: Writing application code or configuring CI/CD runners (use `ci-cd-and-automation`).

## Core Process & Git Plumbing Workflows

## High-Leverage Git Workflows

### 1. Automated Binary Search for Regressions (`git bisect`)
Pinpoint the exact commit that broke a test automatically:
```bash
# 1. Start bisect session
git bisect start

# 2. Declare boundaries
git bisect bad HEAD                # Current commit is broken
git bisect good v1.2.0             # Release v1.2.0 was known to be working

# 3. Run automated test runner on every checkout
git bisect run pytest tests/test_regression.py

# Git automatically checks out commits, runs the test, and prints:
# "commit a83b129 is the first bad commit"
git bisect reset
```

### 2. Isolated Agent Sandboxes (`git worktree`)
Work on a feature branch in a separate folder without disturbing active work in the main directory:
```bash
# Create new branch 'feature-auth' checked out in sibling directory '../worktrees/feature-auth'
git worktree add -b feature-auth ../worktrees/feature-auth main

# Remove worktree when finished
git worktree remove ../worktrees/feature-auth
```

### 3. Emergency Disaster Recovery (`git reflog`)
Recover a commit deleted via `git reset --hard` or a dropped branch:
```bash
# View chronological history of all HEAD movements (even deleted ones)
git reflog

# Find the commit SHA (e.g. 8f921a) before the reset, then restore
git branch recovered-branch 8f921a
```

---

## Conventional Commits Generation Reference

When generating commit messages from diffs, enforce the **Conventional Commits** standard:

```text
<type>(<optional scope>): <imperative description>

[optional body explaining WHY, not WHAT]

[optional footer: BREAKING CHANGE or Closes #123]
```

- **`feat:`**: A new feature for the user.
- **`fix:`**: A bug fix.
- **`refactor:`**: Code change that neither fixes a bug nor adds a feature.
- **`perf:`**: Code change that improves performance.
- **`test:`**: Adding missing tests or correcting existing tests.
- **`chore:`**: Changes to build process, dependency versions, or auxiliary tooling.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"Manual testing through 50 commits is faster than setting up `git bisect`."* | `git bisect` uses binary search to pinpoint the exact regressing commit in ~6 steps instead of 50 manual checks. |
| *"Stashing changes is fine for switching tasks."* | Stashes are easily lost or accidentally dropped; `git worktree` creates clean, isolated directory sandboxes without touching working state. |
| *"Commit messages like 'fix stuff' or 'update' are fine on feature branches."* | Vague commit messages destroy git history searchability and make automated changelog generation impossible. |
| *"Force-pushing (`git push -f`) is safe on shared branches."* | Force-pushing overwrites teammates' commits and corrupts upstream ref pointers; use `--force-with-lease` or rebase. |

## Red Flags

- Running destructive commands (`git reset --hard`, `git clean -fd`) without checking `git status` or verifying reflog safety.
- Long-lived feature branches drifting hundreds of commits behind `main` without regular rebasing.
- Committing secrets, `.env` files, or binary artifacts into git version control.
- Merging PRs with uninformative commit messages lacking conventional commit prefixes (`feat:`, `fix:`, `refactor:`).

## Verification

After completing the workflow, confirm:
- [ ] Automated `git bisect` identifies the regressing commit hash with reproducible test scripts.
- [ ] Git worktree isolates experimental or multi-branch work into clean sibling directories.
- [ ] Commit messages follow conventional commit specifications with descriptive imperatives.
- [ ] Repository history remains clean, linear, and bisect-friendly.

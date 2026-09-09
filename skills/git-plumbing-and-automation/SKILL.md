---
name: git-plumbing-and-automation
description: >-
  Use this skill for advanced Git workflows, automation scripts, and repository recovery.
  Executes automated git bisect for bug hunting, git worktrees for isolated agent sandboxes,
  reflog commit recovery, and conventional commit generation.
---

# Advanced Git Plumbing & Repository Automation

A version control power-user skill for executing advanced Git operations, recovering "lost" commits, isolating branch worktrees, and automating regression isolation using `git bisect`.

## When to Use This Skill
- When hunting down which commit introduced a silent regression across hundreds of commits (`git bisect`).
- When working on multiple parallel branches simultaneously without switching checkouts (`git worktree`).
- When recovering accidentally deleted branches, stashes, or uncommitted commits (`git reflog`).
- When squashing messy commits and generating Conventional Commit messages for pull requests.
- Trigger phrases: `"git bisect"`, `"recover lost commit"`, `"create git worktree"`, `"git reflog"`, `"squash commits"`.

---

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

---

## Anti-Patterns & Traps to Avoid

1. **Destructive Force Pushing (`git push --force`)**: Overwriting shared remote branches and destroying collaborator commits. If rebasing personal feature branches, always use `git push --force-with-lease` to prevent overwriting unseen upstream commits.
2. **Hard Resets Without Stash Protection**: Running `git reset --hard HEAD` or `git checkout -- .` with uncommitted changes in the working tree. Working tree changes that have never been staged or committed are permanently unrecoverable via `git reflog`. Always run `git stash` before destructive resets.
3. **Deleting Worktrees via Filesystem (`rm -rf`)**: Deleting a worktree folder directly from the OS file manager rather than using `git worktree remove <path>`. This leaves dangling administrative pointers in `.git/worktrees/` that prevent re-checking out the branch. Always clean up with `git worktree remove` or `git worktree prune`.
4. **Committing Large Binary Blobs to History**: Committing multi-megabyte datasets, model weights, or database files directly to Git. Even if deleted in a subsequent commit, the binary permanently bloats every future `git clone`. Use Git LFS or `.gitignore` for large binaries.

---

## Quality Checklist

- [ ] Uncommitted modifications are safely stashed (`git stash`) before running rebases or bisects.
- [ ] Temporary worktree sandboxes are pruned cleanly via `git worktree remove` upon completion.
- [ ] Commit messages conform to the Conventional Commits specification with imperative verbs.
- [ ] Large binary assets and environment secret files are strictly excluded via `.gitignore`.
- [ ] Bisect scripts are deterministic and return standard exit codes (0 for good, 1 for bad, 125 to skip).
- [ ] Remote branch pushes with historical rewrites strictly enforce `--force-with-lease`.

# Portability Specification & Issue #361 Resolution

This document describes how Agent Foundry achieves 100% portable skills across hosts and eliminates the relative reference link failure known as **Issue #361**.

---

## 1. The Root Cause of Issue #361

In modular skill repositories, skills frequently link to shared checklists (e.g., `references/done.md` or `references/testing.md`). When tools like `npx skills add --skill <name>` copy only an isolated skill folder `skills/<name>/`, relative links pointing to repo-root checklists (`../../references/...`) break because the target directory was not copied.

---

## 2. Agent Foundry Dual-Resolution Architecture

To ensure that skills remain 100% portable whether consumed inside the monorepo or deployed as standalone modules, Agent Foundry implements **Dual-Resolution Colocation**:

```
project-root/
+-- references/                     <- Canonical Monorepo References
|   +-- done.md
|   +-- testing.md
|   +-- security.md
|   +-- perf.md
|   +-- a11y.md
|   +-- observability.md
|   +-- orchestration.md
+-- skills/
    +-- orchestration/
        +-- using-agent-skills/
            +-- SKILL.md
            +-- references/         <- Colocated Standalone References
                +-- done.md
                +-- testing.md
```

### Automated Bundling in `sync_to_global.py`
When `python scripts/sync_to_global.py` deploys skills to global environments (such as `~/.gemini/config/skills/<skill_name>/` or `~/.opencode/`), it automatically bundles a local copy of `references/` inside each individual skill folder:
1. Monorepo execution: Resolves to root `references/`.
2. Standalone execution: Resolves to colocated `./references/`.
3. Global execution: Resolves to `~/.gemini/config/references/`.

Zero broken links under any package manager or CLI runner.

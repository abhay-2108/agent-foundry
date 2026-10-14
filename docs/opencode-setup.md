# OpenCode Setup Guide

Integrate the **Agent Foundry** ecosystem with the **OpenCode** CLI agent runtime.

---

## 1. Automated Global Synchronization

Agent Foundry includes a pre-configured synchronization script that deploys all 10 agents and 43 slash commands directly to OpenCode:

```bash
# Run automated sync
python scripts/sync_to_global.py
```

This deploys:
- **Agents**: Synced to `~/.config/opencode/agents/` (or `%APPDATA%/opencode/agents/` on Windows).
- **Commands**: Synced to `~/.config/opencode/commands/` (or `%APPDATA%/opencode/commands/`).
- **References**: Synced to `~/.opencode/references/`.

---

## 2. Using OpenCode Commands

OpenCode commands auto-activate the appropriate skill:

```bash
opencode /plan "Design idempotent event consumer"
opencode /review "Check pull request #14"
opencode /debug "Isolate Redis connection pool timeout"
opencode /gsd "Plan M001 milestone slices"
```

---

## 3. Disagreeing & Persona Fan-Out

OpenCode invokes personas via primary mode with strict composition:
- Personas never invoke personas.
- Parallel `/ship` audit fans out to `@code-quality-auditor`, `@security-red-teamer`, and `@sre-devops-guardian`.

# Google Antigravity Setup Guide

Agent Foundry is built natively for Google Antigravity IDE and Antigravity CLI.

---

## 1. Global Installation

Run the sync script to deploy all skills, agents, rules, and MCP servers to your global Antigravity environment:

```bash
python scripts/sync_to_global.py
```

This deploys:
1. **42 Flat Skills**: To `~/.gemini/config/skills/` with bundled `references/` inside each skill folder.
2. **Global Rules**: Injected into `~/.gemini/config/AGENTS.md` and `~/.gemini/config/GEMINI.md`.
3. **FastMCP Server**: Registered in `~/.gemini/config/mcp_config.json` with SQLite 3-tier memory engine.
4. **References**: Mirrored to `~/.gemini/config/references/`.

---

## 2. Antigravity Slash Commands

In Antigravity IDE or CLI, type `/` to access commands:
- `/spec`: Technical specification with mandatory STOP-after-spec gate.
- `/plan`: DAG implementation plan with rollback checkpoints.
- `/build`: Incremental implementation adhering to $\le 100\text{--}150$ line diff limit.
- `/review`: 5-Axis code review gate.
- `/ship`: Parallel release gate fan-out.
- `/gsd`: 3-Tier Get Shit Done project decomposition.

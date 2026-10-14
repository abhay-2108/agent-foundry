# Cursor Setup Guide

Use Agent Foundry skills and personas inside Cursor (AI IDE).

---

## 1. Project-Level Rules & Skills

Copy or symlink Agent Foundry skills into your Cursor workspace:

```bash
# Option A: Symlink skills directly to .cursor/skills
mkdir -p .cursor
ln -s path/to/agent-foundry/skills .cursor/skills

# Option B: Add global instructions to .cursorrules
cat path/to/agent-foundry/skills/orchestration/using-agent-skills/SKILL.md >> .cursorrules
```

---

## 2. FastMCP Tool Configuration

Enable Agent Foundry's 3-tier memory and safe filesystem tools inside Cursor Composer by adding to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agent-foundry": {
      "command": "python",
      "args": ["path/to/agent-foundry/mcp_servers/agent_foundry_server.py"]
    }
  }
}
```

---

## 3. Working in Composer

In Cursor Composer, invoke specialist personas or workflows directly:
- *"Embody @code-quality-auditor and review my uncommitted diff."*
- *"Follow using-agent-skills to break this task down into vertical slices."*
- *"Follow plan-and-execute with STOP-after-spec gate."*

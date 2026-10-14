# Claude Code Setup Guide

Integrate the **Agent Foundry** ecosystem with Anthropic's **Claude Code** CLI.

---

## 1. Fast Setup via Plugin Directory

Add Agent Foundry directly to your Claude Code configuration:

```bash
# Add as a local plugin
claude plugin add path/to/agent-foundry/.claude-plugin
```

Claude Code will automatically discover:
- All 42 skills located in `skills/`
- All slash commands in `.claude/commands/` (`/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship`, `/debug`, `/gsd`, `/secscan`, `/observe`)

---

## 2. Using Slash Commands in Claude Code

Once installed, use slash commands directly in any conversation:

```bash
# Start a new initiative with strict STOP-after-spec gating
/spec "Design a Redis-backed rate limiter with sliding window counter"

# Execute vertical slice with ~100 line diff budget
/build "Implement sliding window Lua script and unit tests"

# Execute senior 5-axis code review
/review

# Execute parallel release audit
/ship
```

---

## 3. Configuration & Memory

Claude Code can access the persistent 3-tier memory engine via the Agent Foundry FastMCP server:

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

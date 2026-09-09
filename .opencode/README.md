# OpenCode Skills Setup Guide

This guide explains how to integrate and activate the **30 universal Agent Skills** from this repository into **OpenCode**.

---

## 1. How Skills Work in OpenCode

OpenCode adheres to the universal **Agent Skill specification**:
- Each skill resides in a dedicated folder containing a **`SKILL.md`** file.
- **Progressive Disclosure**: OpenCode reads lightweight YAML frontmatter (`name` and `description`) at startup.
- The full instructions, code recipes, anti-patterns, and quality checklists are loaded into context only when triggered by relevant developer prompts.

---

## 2. Setup Methods

You can connect OpenCode to the `skills/` directory using one of the following methods:

### Method A: Directory Junction / Symlink (Recommended)

Link the canonical `skills/` directory directly into `.opencode/skills` so OpenCode automatically discovers all 30 skills without duplicating files:

#### On Windows (PowerShell):
```powershell
# Run from repository root
New-Item -ItemType Junction -Path ".opencode/skills" -Target "skills"
```

#### On Linux / macOS (Bash):
```bash
# Run from repository root
ln -s ../skills .opencode/skills
```

---

### Method B: OpenCode Configuration (`opencode.json`)

If your OpenCode environment uses a configuration file, add the `skills/` path to the skills discovery array:

Create or update `.opencode/opencode.json` (or your global `~/.config/opencode/config.json`):

```json
{
  "$schema": "https://opencode.dev/schema.json",
  "skills": {
    "paths": [
      "./skills",
      "./.opencode/skills"
    ],
    "auto_discover": true
  },
  "mcpServers": {
    "code-sandbox": {
      "command": "python",
      "args": ["./mcp_servers/code_sandbox_server.py"]
    },
    "filesystem-sandbox": {
      "command": "python",
      "args": ["./mcp_servers/filesystem_server.py"]
    },
    "hybrid-retriever": {
      "command": "python",
      "args": ["./mcp_servers/hybrid_retriever_server.py"]
    }
  }
}
```

---

### Method C: Global OpenCode Config

To make these skills available across **all** your local projects in OpenCode:

#### On Windows:
```powershell
# Copy or junction to user config directory
New-Item -ItemType Junction -Path "$env:USERPROFILE\.opencode\skills" -Target "p:\AIML Projects\Skills and Agents\skills"
```

#### On Linux / macOS:
```bash
ln -s "/path/to/Skills and Agents/skills" ~/.opencode/skills
```

---

## 3. How to Trigger Skills in OpenCode

Once configured, skills activate automatically through two mechanisms:

### 1. Automatic Semantic Triggering (Recommended)
OpenCode matches your prompt against the skill's frontmatter `description`. For example:
- *"Plan out the architecture before writing code"* $\rightarrow$ Triggers **`plan-and-execute`**
- *"Diagnose this crash and write a failing repro test"* $\rightarrow$ Triggers **`bug-hunter`**
- *"Review this git diff for memory leaks and typing errors"* $\rightarrow$ Triggers **`code-reviewer`**
- *"Scan for SQL injection and hardcoded secrets"* $\rightarrow$ Triggers **`security-vulnerability-scanner`**

### 2. Explicit Mention Triggering
Directly mention the skill path in your prompt:
```text
@skills/bug-hunter Fix the IndexError in src/auth/jwt_service.py
```
or
```text
Use the plan-and-execute skill to create an implementation plan for adding Redis caching.
```

---

## 4. Recommended Starter Skills for OpenCode

For daily programming in OpenCode, we recommend starting with these 5 core skills:

1. **[`plan-and-execute`](../skills/plan-and-execute/SKILL.md)**: Prevents runaway code changes by creating 2–5 min task DAGs first.
2. **[`bug-hunter`](../skills/bug-hunter/SKILL.md)**: Scientific bug isolation with minimal failing tests (RED $\rightarrow$ GREEN).
3. **[`code-reviewer`](../skills/code-reviewer/SKILL.md)**: Automated senior peer reviews on typing, edge cases, and code smells.
4. **[`git-plumbing-and-automation`](../skills/git-plumbing-and-automation/SKILL.md)**: Spawns isolated git worktrees so OpenCode never breaks your active branch.
5. **[`session-handoff`](../skills/session-handoff/SKILL.md)**: Maintains `HANDOFF.md` so you never lose context between chat resets.

---

## 5. Verification

Verify that OpenCode recognizes the skills:

1. Launch an OpenCode session:
   ```bash
   opencode
   ```
2. Type:
   ```text
   What skills do you have available?
   ```
3. OpenCode should list the skills from `skills/` or `.opencode/skills/`.

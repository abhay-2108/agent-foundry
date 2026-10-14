# GitHub Copilot Setup Guide

Use Agent Foundry skills and references with **GitHub Copilot Chat** in VS Code, JetBrains, or Visual Studio.

---

## 1. Copilot Instructions

Link the canonical instructions to your workspace `.github/copilot-instructions.md`:

```markdown
# Agent Foundry Copilot Instructions

Whenever assisting with coding, planning, debugging, or reviewing:
1. Always follow the 6 Global Operating Rules defined in `skills/orchestration/using-agent-skills/SKILL.md`.
2. Follow the 5-Axis Code Review Matrix in `references/done.md`.
3. Adopt the "Prove-It" Bug Repro pattern in `references/testing.md` before fixing bugs.
4. Enforce strict STOP-after-spec gating and <=100-line diff limits per task slice.
```

---

## 2. VS Code Workspace Setup

Add the skills folder to `.vscode/settings.json`:

```json
{
  "github.copilot.chat.agent.customInstructions": [
    {
      "file": "skills/orchestration/using-agent-skills/SKILL.md"
    }
  ]
}
```

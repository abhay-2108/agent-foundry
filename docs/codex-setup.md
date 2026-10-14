# OpenAI Codex Setup Guide

Integrate the **Agent Foundry** ecosystem with OpenAI Codex.

---

## 1. Plugin Configuration

Add the Agent Foundry `.codex-plugin/plugin.json` to your Codex configuration:

```bash
codex plugin add path/to/agent-foundry/.codex-plugin
```

Codex will index:
- All 42 skills in `skills/`
- All canonical checklists in `references/`

---

## 2. Recommended System Prompt Prefix

When initializing a Codex session, append this instruction:

```markdown
Follow the 6 Global Operating Rules from `skills/orchestration/using-agent-skills/SKILL.md`:
1. Surface assumptions early.
2. Stop on confusion.
3. Push back when appropriate.
4. Enforce simplicity (YAGNI, files <500 lines).
5. Scope discipline (diffs <=100 lines).
6. Verify with evidence (run tests; zero faith-based completions).
```

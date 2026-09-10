# OpenCode Global Integration Guide: Skills, Agents & Commands

This guide provides the complete, authoritative setup for integrating the **10 Autonomous Agent Personas**, **30 Modular Skills**, and **30 Custom Slash Commands** from this repository into **OpenCode CLI** across **all projects globally**.

---

## 1. OpenCode Architecture & Asset Discovery

OpenCode adheres to universal agent specifications and discovers extensions from designated global configuration roots:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   GLOBAL OPENCODE CONFIGURATION ROOT                   │
│   Windows:        ~/.config/opencode/    AND    ~/.opencode/           │
│   Linux / macOS:  ~/.config/opencode/    AND    ~/.opencode/           │
└──────────────┬────────────────────────┬──────────────────────┬─────────┘
               │                        │                      │
               ▼                        ▼                      ▼
┌────────────────────────┐┌────────────────────────┐┌────────────────────────┐
│    agents/*.md         ││    skills/*/SKILL.md   ││    commands/*.md       │
│  10 Autonomous Personas││  30 Modular Skill Sets ││  30 Quick Slash Actions│
│  (Switched with `Tab`) ││ (Triggered Semantically││ (Triggered with `Ctrl+P│
│                        ││   or via `@skills/`)   ││      or `/command`)    │
└────────────────────────┘└────────────────────────┘└────────────────────────┘
```

### Critical Discovery Rules:
1. **Global Configuration Paths**: On Windows, OpenCode evaluates user profile paths (`$env:USERPROFILE\.config\opencode\` and `$env:USERPROFILE\.opencode\`). OpenCode does **not** automatically scan `%APPDATA%\opencode` by default.
2. **Tab Switching Mechanics**: In the OpenCode TUI, pressing the **`Tab`** key cycles through **`primary`** agents (`mode: primary`). Agents marked with `mode: subagent` are omitted from `Tab` cycling and can only be invoked via `@` mentions or subtask delegations.
3. **Progressive Disclosure**: Skills are loaded dynamically when relevant keywords match their YAML frontmatter, preserving your model's context window.

---

## 2. Master Agent Fleet Catalog (10 Operational Personas)

All 10 agent personas in this repository are configured with `mode: primary` so they can be switched instantaneously using the `Tab` button inside any project session:

| Agent Persona | Role & Mandate | OpenCode Mode | Bound Skills Matrix |
| :--- | :--- | :--- | :--- |
| **`lead-orchestrator`** | **Master Workflow & Team Lead**: Decomposes complex goals into acyclic DAGs, coordinates multi-agent consensus, and enforces human checkpoints. | `primary` (`Tab`) | `plan-and-execute`, `multi-agent-orchestrator`, `human-in-the-loop-governor`, `session-handoff`, `brainstorming`, `knowledge-capture`, `llm-observability` |
| **`fullstack-engineer`** | **End-to-End Production Builder**: Designs clean backend APIs, resilient database schemas, premium frontend UIs, and Docker environments. | `primary` (`Tab`) | `backend-architecture`, `frontend-design`, `docker-container-architect`, `git-plumbing-and-automation`, `mcp-tool-integrator`, `llm-observability` |
| **`code-quality-auditor`** | **Senior Peer Reviewer & Debugger**: Enforces pre-merge quality gates, isolates bugs with minimal failing repros, and audits complexity. | `primary` (`Tab`) | `code-reviewer`, `bug-hunter`, `llm-evals-engineer`, `agent-trajectory-evaluator`, `llm-observability` |
| **`research-analyst`** | **Exhaustive Discovery & Triangulation**: Deep codebase discovery, web documentation scraping, citation cross-checking, and report synthesis. | `primary` (`Tab`) | `workspace-researcher`, `agentic-rag-engineer`, `graph-rag-builder`, `office-doc-engine`, `knowledge-capture`, `llm-observability` |
| **`security-red-teamer`** | **Adversarial Safety & Vulnerability Auditor**: OWASP scanning, hardcoded credential detection, prompt injection testing, and dual guardrails. | `primary` (`Tab`) | `security-vulnerability-scanner`, `prompt-injection-red-teamer`, `guardrails-enforcer`, `llm-observability` |
| **`data-scientist`** | **Quantitative Rigor & ML Pipelines**: Exploratory data analysis (EDA), data cleaning, statistical hypothesis testing, and SHAP explainability. | `primary` (`Tab`) | `eda-and-data-cleaning`, `feature-engineering-pipeline`, `statistical-hypothesis-tester`, `model-explainability-shap`, `llm-observability` |
| **`browser-navigator`** | **E2E Web Specialist & Playwright Driver**: Interacts with live web applications, handles dynamic JS obstacles, and captures screenshot evidence. | `primary` (`Tab`) | `workspace-researcher`, `office-doc-engine`, `llm-observability` |
| **`sre-devops-guardian`** | **Reliability, CI/CD & Infrastructure Guardian**: Multi-stage minimal container hardening, git worktree isolation, and incident triage. | `primary` (`Tab`) | `docker-container-architect`, `git-plumbing-and-automation`, `backend-architecture`, `llm-observability` |
| **`finops-token-router`** | **Inference Economics & Cost Optimization**: Routes requests between fast/cheap models and frontier reasoning models, and monitors token burn. | `primary` (`Tab`) | `llm-observability`, `llm-evals-engineer`, `backend-architecture` |
| **`technical-writer-scribe`** | **Documentation & ADR Architect**: Compiles structured markdown, Architecture Decision Records (ADRs), and visual mermaid diagrams. | `primary` (`Tab`) | `knowledge-capture`, `office-doc-engine`, `workspace-researcher`, `llm-observability` |

---

## 3. One-Command Global Setup

Run the setup commands below once to link all **Agents**, **Skills**, and **Commands** globally across your entire operating system.

### On Windows (PowerShell):

```powershell
# 1. Define repo root path (adjust if cloned to a custom location)
$REPO = "P:\AIML Projects\Skills and Agents"

# 2. Ensure target configuration root directories exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\opencode" | Out-Null
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.opencode" | Out-Null

# 3. Clean any existing stale junctions/directories
Remove-Item "$env:USERPROFILE\.config\opencode\agents" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.opencode\agents" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.config\opencode\skills" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.opencode\skills" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.config\opencode\commands" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.opencode\commands" -Force -Recurse -ErrorAction SilentlyContinue

# 4. Create directory junctions for Agents (from AppData storage)
New-Item -ItemType Junction -Path "$env:USERPROFILE\.config\opencode\agents" -Target "$env:APPDATA\opencode\agents" | Out-Null
New-Item -ItemType Junction -Path "$env:USERPROFILE\.opencode\agents" -Target "$env:APPDATA\opencode\agents" | Out-Null

# 5. Create directory junctions for Skills (from repo)
New-Item -ItemType Junction -Path "$env:USERPROFILE\.config\opencode\skills" -Target "$REPO\skills" | Out-Null
New-Item -ItemType Junction -Path "$env:USERPROFILE\.opencode\skills" -Target "$REPO\skills" | Out-Null

# 6. Create directory junctions for Commands (from AppData storage)
New-Item -ItemType Junction -Path "$env:USERPROFILE\.config\opencode\commands" -Target "$env:APPDATA\opencode\commands" | Out-Null
New-Item -ItemType Junction -Path "$env:USERPROFILE\.opencode\commands" -Target "$env:APPDATA\opencode\commands" | Out-Null

# 7. Verify agent discovery
Write-Host "`n=== Registered Primary Agents ===" -ForegroundColor Cyan
opencode agent list | Select-String "\(primary\)"
```

### On Linux / macOS (Bash):

```bash
REPO="/path/to/Skills and Agents"

mkdir -p ~/.config/opencode ~/.opencode

# Link agents
ln -sfn "$REPO/.opencode/agents" ~/.config/opencode/agents
ln -sfn "$REPO/.opencode/agents" ~/.opencode/agents

# Link skills
ln -sfn "$REPO/skills" ~/.config/opencode/skills
ln -sfn "$REPO/skills" ~/.opencode/skills

# Link commands
ln -sfn "$REPO/.opencode/commands" ~/.config/opencode/commands
ln -sfn "$REPO/.opencode/commands" ~/.opencode/commands

# Verify
opencode agent list | grep "(primary)"
```

---

## 4. Developer Workflow & TUI Controls

Once linked, open OpenCode in **any project or folder**:

```bash
opencode
```

The TUI prompt displays:
```text
Ask anything… "What is the tech stack of this project?"
Build · OpenCode Zen
tab agents  ctrl+p commands
```

### 1. Cycle Agents with the `Tab` Key
Press **`Tab`** (or `Shift+Tab` to reverse) while at the input prompt to cycle through:
$$\text{Build} \longrightarrow \text{Plan} \longrightarrow \textbf{lead-orchestrator} \longrightarrow \textbf{fullstack-engineer} \longrightarrow \textbf{code-quality-auditor} \longrightarrow \dots$$

### 2. Run Commands with `Ctrl+P` or `/`
Press **`Ctrl+P`** or type **`/`** to open the interactive command palette containing all 30 pre-built workflows:
- `/plan <task>`: Decomposes a multi-step task into an architectural plan.
- `/review`: Peer reviews uncommitted diffs for typing, security, and edge cases.
- `/debug`: Minimal reproduction test runner and bug hunting.
- `/secscan`: OWASP vulnerability audit and secret detection.
- `/backend`: Designs API contracts, middleware, and database schemas.
- `/frontend`: Implements UI components with responsive styling and polish.
- `/git`: Spawns an isolated git worktree for safe code exploration.
- `/handoff`: Compiles `HANDOFF.md` to preserve state across session resets.

### 3. Mention Agents & Skills Explicitly
Directly summon specialized personas or toolkits in your prompt:
```text
@lead-orchestrator Decompose the migration from SQLite to Postgres.
@skills/security-vulnerability-scanner Audit src/auth/oauth.py for SSRF.
```

### 4. Automatic Semantic Triggering
Prompting with natural intent triggers skills automatically:
- *"Write unit tests and reproduce this KeyError"* $\rightarrow$ triggers `bug-hunter`
- *"Benchmark token usage and prompt caching"* $\rightarrow$ triggers `finops-token-router`

---

## 5. Customizing Models & Permissions

Each agent's configuration is stored as clean Markdown in `.opencode/agents/<agent-name>.md`:

```markdown
---
description: Autonomous supervisor that decomposes complex goals into dependency DAGs...
mode: primary
model: anthropic/claude-3-7-sonnet-20250219
temperature: 0.1
permissions:
  edit: allow
  bash: allow
  write: allow
  read: allow
---

# Lead Orchestrator Agent
...
```

- **Change Model**: Set `model:` to any model supported by your providers (e.g., `openai/gpt-4o`, `google/gemini-2.5-pro`, or remove the line to inherit your active session model).
- **Tab Cycling Behavior**: Maintain `mode: primary` to keep the agent switchable via `Tab`. Change to `mode: subagent` if you wish to reserve an agent for `@` mentions only.
- **Adjust Permissions**: Fine-tune permission gates between `allow`, `ask`, and `deny`.

---

## 6. Verification Checklist

Run these quick checks whenever updating your OpenCode environment:

1. **Verify Registered Agents**:
   ```bash
   opencode agent list
   ```
   *Expected*: All 10 custom personas are displayed with `(primary)`.

2. **Verify Global Junctions (Windows PowerShell)**:
   ```powershell
   Get-Item "$env:USERPROFILE\.config\opencode\agents", "$env:USERPROFILE\.config\opencode\skills", "$env:USERPROFILE\.config\opencode\commands" | Select-Object Name, LinkType, Target
   ```

3. **Verify TUI Hotkeys**:
   Start `opencode`, press `Tab` to cycle personas, and press `Ctrl+P` to verify custom slash commands.

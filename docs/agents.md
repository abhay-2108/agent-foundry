# Autonomous Specialist Agents Fleet & Decision Matrix

Agent Foundry features **10 autonomous specialist personas** designed for high-discipline execution across the software development lifecycle.

---

## 1. The 3-Layer Composition Standard

To prevent recursive agent loops, token exhaustion, and orchestration thrashing, the ecosystem strictly enforces:

```
┌────────────────────────────────────────────────────────┐
│ COMMAND / USER (When to run: Slash Command / User)     │
└──────────────────────────┬─────────────────────────────┘
                           │ Dispatches
                           ▼
┌────────────────────────────────────────────────────────┐
│ PERSONA (Who is running: Autonomous Specialist Actor)  │
└──────────────────────────┬─────────────────────────────┘
                           │ Executes
                           ▼
┌────────────────────────────────────────────────────────┐
│ SKILL (How to do it: Stateless, Step-by-Step SOP)      │
└────────────────────────────────────────────────────────┘
```

### The Non-Negotiable Composition Rules:
1. **Personas NEVER Invoke Personas**: Specialist agents are forbidden from invoking other specialist agents directly. Meta-orchestrator layers are eliminated.
2. **User-Driven Lifecycle**: Transitions across lifecycle phases are driven sequentially by the user (`/spec` $\to$ `/plan` $\to$ `/build` $\to$ `/review` $\to$ `/ship`).
3. **The Single Authorized Fan-Out**: The `/ship` release gate is the only permitted concurrent delegation pattern: `/ship` fans out to `@code-quality-auditor`, `@security-red-teamer`, and `@sre-devops-guardian` in parallel, then merges their findings into a single Go/No-Go release verdict.

---

## 2. Master Agent Decision Matrix

| Persona | Role & Domain | Model Tier | Governance | Key Bound Skills |
| :--- | :--- | :--- | :--- | :--- |
| **`lead-orchestrator`** | Master Workflow & Project Lead | `reasoning-heavy` | `checkpointed` | `using-agent-skills`, `plan-and-execute`, `get-shit-done`, `brainstorming` |
| **`research-analyst`** | Technical Intelligence & Codebase Scout | `balanced` | `autonomous` | `workspace-researcher`, `agentic-rag-engineer`, `graph-rag-builder` |
| **`fullstack-engineer`** | End-to-End Feature & System Builder | `balanced` | `checkpointed` | `backend-architecture`, `frontend-design`, `mcp-tool-integrator` |
| **`code-quality-auditor`** | Senior Staff Code Review & QA Gatekeeper | `reasoning-heavy` | `autonomous` | `code-reviewer`, `bug-hunter`, `llm-evals-engineer` |
| **`security-red-teamer`** | Offensive/Defensive AI & Code Security | `reasoning-heavy` | `strict-hitl` | `security-vulnerability-scanner`, `prompt-injection-red-teamer` |
| **`data-scientist`** | Statistical Modeling, ML Lab & Analytics | `balanced` | `autonomous` | `eda-and-data-cleaning`, `feature-engineering-pipeline`, `model-explainability-shap` |
| **`browser-navigator`** | Browser Automation & Visual Regression | `balanced` | `autonomous` | `agentic-ui-patterns`, `workspace-researcher` |
| **`sre-devops-guardian`** | Containers, CI/CD & Reliability SRE | `balanced` | `checkpointed` | `docker-container-architect`, `git-plumbing-and-automation` |
| **`finops-token-router`** | Cost Optimization & Model Routing | `compact` | `autonomous` | `llm-observability`, `prompt-architect` |
| **`technical-writer-scribe`**| ADRs, Executive Memos & De-Slopped Prose | `balanced` | `autonomous` | `human-writer`, `executive-memo-architect`, `knowledge-capture` |

---

## 3. Governance Levels

- **`autonomous`**: Allowed to execute read, analysis, and scoped write actions within approved boundaries.
- **`checkpointed`**: Halts at major DAG milestones (e.g., after spec generation) for user sign-off before modifying files.
- **`strict-hitl`**: Requires explicit interactive human approval for every state-altering or high-risk operation.

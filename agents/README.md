# Autonomous AI Agents Fleet

A production-grade ecosystem of **10 specialized, autonomous AI Agent Personas** designed to orchestrate and execute workflows across the **39 modular skills** in this repository.

---

## 1. Architectural Model: Skills vs. Agents

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AGENTS (Execution Layer)                        │
│   Autonomous personas with goals, memory, state machines, and routing  │
│      e.g., Lead Orchestrator, Research Analyst, Security Red-Teamer    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (binds & invokes)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        SKILLS (Capability Layer)                       │
│    39 modular, stateless capabilities with SOPs, anti-patterns & checks │
│     e.g., `eda-and-data-cleaning`, `bug-hunter`, `agentic-rag-engineer` │
└────────────────────────────────────────────────────────────────────────┘
```

| Dimension | **Skills (`skills/`)** | **Agents (`agents/`)** |
| :--- | :--- | :--- |
| **Role** | Capability Layer (SOP + Specialized Toolset) | Execution Layer (Goal-driven Autonomous Actor) |
| **State** | Stateless, modular, reusable recipes | Stateful, tracks context, memory, and DAG execution |
| **Specification** | `SKILL.md` (YAML frontmatter + progressive disclosure) | `AGENT.md` (Persona + Bound Skills + State Machine + I/O contracts) |
| **Invocation** | Loaded on-demand when triggered by task keywords | Dispatched to plan, coordinate, implement, review, or red-team |

---

## 2. Master Agent Fleet Catalog (10 Operational Personas)

| Agent Persona | Role & Mandate | Governance | Bound Skills Matrix |
| :--- | :--- | :--- | :--- |
| **[`lead-orchestrator`](./lead-orchestrator/AGENT.md)** | **Master Workflow & Team Lead**: Decomposes user goals into DAGs, routes subtasks, manages consensus debate, and enforces checkpoints. | `checkpointed` | `plan-and-execute`, `multi-agent-orchestrator`, `human-in-the-loop-governor`, `session-handoff`, `brainstorming`, `knowledge-capture`, `llm-observability` |
| **[`research-analyst`](./research-analyst/AGENT.md)** | **Deep Research & Knowledge Ingestion**: Web crawling, multi-source triangulation ($\ge 2$ sources), graph-RAG, and briefing compilation. | `autonomous` | `workspace-researcher`, `agentic-rag-engineer`, `graph-rag-builder`, `office-doc-engine`, `knowledge-capture`, `llm-observability` |
| **[`fullstack-engineer`](./fullstack-engineer/AGENT.md)** | **End-to-End Software Engineering**: System architecture, API contracts, database modeling, frontend UI/UX aesthetics, streaming event architectures, agentic UI patterns, Dockerization, and git sandboxing. | `checkpointed` | `backend-architecture`, `frontend-design`, `agentic-ui-patterns`, `data-pipeline-etl`, `vector-database-architect`, `streaming-and-event-driven`, `docker-container-architect`, `git-plumbing-and-automation`, `mcp-tool-integrator`, `llm-observability` |
| **[`code-quality-auditor`](./code-quality-auditor/AGENT.md)** | **Code Quality, Review & Debugging**: Static analysis, pre-merge peer review gates, minimal crash reproduction, trajectory eval audits, and CI/CD benchmarks. | `autonomous` | `code-reviewer`, `bug-hunter`, `llm-evals-engineer`, `agent-trajectory-evaluator`, `llm-observability` |
| **[`security-red-teamer`](./security-red-teamer/AGENT.md)** | **Adversarial Safety & Security**: OWASP vulnerability scanning, prompt injection defense, jailbreak resistance auditing, and dual-layer guardrails. | `strict-hitl` | `security-vulnerability-scanner`, `prompt-injection-red-teamer`, `guardrails-enforcer`, `llm-observability` |
| **[`data-scientist`](./data-scientist/AGENT.md)** | **Analytics, ML Pipelines & Interpretability**: Automated EDA profiling, feature engineering pipelines, ETL/dbt orchestration, vector DB sizing, hypothesis testing, and SHAP explainability & fairness audits. | `autonomous` | `advanced-data-analyst`, `ml-feature-and-model-lab`, `data-pipeline-etl`, `vector-database-architect`, `eda-and-data-cleaning`, `feature-engineering-pipeline`, `statistical-hypothesis-tester`, `model-explainability-shap`, `llm-observability` |
| **[`browser-navigator`](./browser-navigator/AGENT.md)** | **Browser Automation & Web Scraping**: Playwright web navigation, dynamic SPA interaction, form filling, visual screenshot verification, and DOM extraction. | `autonomous` | `workspace-researcher`, `office-doc-engine`, `llm-observability` |
| **[`sre-devops-guardian`](./sre-devops-guardian/AGENT.md)** | **SRE, CI/CD & Deployment Guardian**: Multi-stage container hardening, Alpine/Distroless bases, zero-root UID enforcement, git worktree deployments, and incident triage. | `checkpointed` | `docker-container-architect`, `git-plumbing-and-automation`, `backend-architecture`, `llm-observability` |
| **[`finops-token-router`](./finops-token-router/AGENT.md)** | **FinOps, Model Gateway & Cost Optimization**: Dynamic model routing (cheap 8B vs frontier reasoning), semantic prompt caching, and token burn rate tracking. | `autonomous` | `llm-observability`, `llm-evals-engineer`, `backend-architecture` |
| **[`technical-writer-scribe`](./technical-writer-scribe/AGENT.md)** | **Documentation & ADR Architect**: Human-style de-slopped writing, Amazon 6-page executive memos, Architecture Decision Records (ADRs), API reference guides, changelogs, and formatted office documentation. | `autonomous` | `human-writer`, `executive-memo-architect`, `knowledge-capture`, `office-doc-engine`, `workspace-researcher`, `llm-observability` |

---

## 3. Orchestration Runtimes & Visual Playground

The repository includes a standalone Python runtime engine and an interactive visual terminal playground in `agents/runtime/`:

```bash
# 1. Validate the integrity of all 10 agents, schemas, and skill bindings
python agents/runtime/agent_runner.py validate

# 2. List all 10 registered agents and their active skills
python agents/runtime/agent_runner.py list-agents

# 3. View the full specification and prompt blueprint of an agent
python agents/runtime/agent_runner.py show-agent lead-orchestrator

# 4. Dispatch a task envelope to a specialist agent
python agents/runtime/agent_runner.py dispatch fullstack-engineer --objective "Implement Redis session management"

# 5. Launch the interactive visual multi-agent terminal simulation
python agents/runtime/playground.py --demo
```

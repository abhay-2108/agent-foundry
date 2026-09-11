# AI Skills & Autonomous Agents Ecosystem

A production-grade, end-to-end **Agentic AI Engineering Platform** combining **10 Autonomous Agent Personas**, **39 Operational Skills**, **4 Declarative Multi-Agent Workflows**, **3 Ready-to-Run FastMCP Tool Servers**, a **3-Tier Agentic Memory Engine**, and an **Autonomy Benchmarking Gym**.

Conforms to the universal Agent Skill specification—fully compatible with **Antigravity**, **Claude Code**, **Codex**, and **OpenCode**.

---

## 📑 Table of Contents
- [1. Architectural Paradigm: Skills vs. Agents](#1-architectural-paradigm-skills-vs-agents)
- [2. Quickstart & Verification](#2-quickstart--verification)
- [3. The "Essential 10" Developer IDE Stack](#3-the-essential-10-developer-ide-stack)
- [4. Autonomous Agent Personas Fleet (10 Agents)](#4-autonomous-agent-personas-fleet-10-agents)
- [5. Operational Skills Catalog by Domain (30 Skills)](#5-operational-skills-catalog-by-domain-30-skills)
- [6. Declarative Multi-Agent Workflows](#6-declarative-multi-agent-workflows)
- [7. FastMCP Tool Servers](#7-fastmcp-tool-servers)
- [8. 3-Tier Agentic Memory Engine](#8-3-tier-agentic-memory-engine)
- [9. Agent Autonomy Benchmarks Gym](#9-agent-autonomy-benchmarks-gym)
- [10. Interactive Visual Terminal Playground](#10-interactive-visual-terminal-playground)
- [11. Repository Directory Structure](#11-repository-directory-structure)

---

## 1. Architectural Paradigm: Skills vs. Agents

The platform is architected into three distinct, complementary layers:

- **Execution Layer ([`agents/`](./agents/README.md))**: 10 stateful, goal-oriented autonomous personas with defined system prompts, memory retention policies, operational state machines, inter-agent communication contracts, and explicit skill bindings.
- **Capability Layer ([`skills/`](./skills/README.md))**: 39 modular, stateless capabilities organized across 9 domain hubs, providing step-by-step procedures, anti-pattern traps to avoid, and pre-flight quality verification checklists.
- **Infrastructure Layer**: Declarative multi-agent DAGs ([`workflows/`](./workflows/README.md)), local tool execution ([`mcp_servers/`](./mcp_servers/README.md)), persistent 3-tier memory ([`memory/`](./memory/README.md)), and trajectory benchmarks ([`benchmarks/`](./benchmarks/README.md)).

| Dimension | **Skills (`skills/`)** | **Agents (`agents/`)** |
| :--- | :--- | :--- |
| **Role** | Capability Layer (SOP + Specialized Toolset) | Execution Layer (Goal-driven Autonomous Actor) |
| **State** | Stateless, modular, reusable recipes | Stateful, tracks context, memory, and DAG execution |
| **Specification** | `SKILL.md` (YAML frontmatter + progressive disclosure) | `AGENT.md` (Persona + Bound Skills + State Machine + I/O contracts) |
| **Invocation** | Loaded on-demand when triggered by task keywords | Dispatched to plan, coordinate, implement, review, or red-team |

---

## 2. Quickstart & Verification

The platform is designed with a zero-external-dependency philosophy, running natively on standard Python 3.10+ environments.

Detailed execution commands, test harnesses, and CLI arguments are documented within each dedicated module:
- To run the comprehensive ecosystem schema audit: see the testing instructions in [`skills/`](./skills/README.md) and [`agents/`](./agents/README.md).
- To launch the live terminal multi-agent visual simulation: see the CLI guide in [`agents/`](./agents/README.md).
- To test the 3-Tier Agentic Memory Engine: see the self-test guide in [`memory/`](./memory/README.md).
- To execute declarative workflow DAGs: see the execution commands in [`workflows/`](./workflows/README.md).
- To start the FastMCP tool servers: see the connection guide in [`mcp_servers/`](./mcp_servers/README.md).
- To run the agent autonomy benchmark suite: see the gym guide in [`benchmarks/`](./benchmarks/README.md).

---

## 3. The "Essential 10" Developer IDE Stack

If you could only keep **10 items** in your IDE to eliminate 95% of AI coding failure modes (amnesia, runaway code churn, broken branches, hallucinated APIs, and secret leaks), use this curated stack:

| Rank | Component | Type | The Problem It Solves | Spec Link |
| :-: | :--- | :---: | :--- | :--- |
| **1** | **`plan-and-execute`** | **Skill** | **Runaway File Mutations**: Forces pre-flight architectural risk scoring, 2–5 min bite-sized tasks, and verification gates before touching code. | [`SKILL.md`](./skills/plan-and-execute/SKILL.md) |
| **2** | **`bug-hunter`** | **Skill** | **Speculative Guessing**: Enforces the scientific method: isolate a minimal failing test (RED), apply minimal patch, and prove it passes (GREEN). | [`SKILL.md`](./skills/bug-hunter/SKILL.md) |
| **3** | **`code-reviewer`** | **Skill** | **Silent Bugs & Smells**: Senior peer reviewer in your IDE. Catches missing TTLs, N+1 query loops, type mismatches, and architectural leaks. | [`SKILL.md`](./skills/code-reviewer/SKILL.md) |
| **4** | **`git-plumbing-and-automation`** | **Skill** | **Dirty Working Branches**: Spawns isolated git worktrees (`.worktrees/feature-x`) so experiments never pollute or break your active working tree. | [`SKILL.md`](./skills/git-plumbing-and-automation/SKILL.md) |
| **5** | **`security-vulnerability-scanner`** | **Skill** | **Accidental Secret Leaks**: Scans diffs for committed `.env` tokens, SQLi, path traversal, and command injection before code leaves your machine. | [`SKILL.md`](./skills/security-vulnerability-scanner/SKILL.md) |
| **6** | **`session-handoff`** | **Skill** | **Context Amnesia**: Maintains `HANDOFF.md` with active uncommitted state, exact file lines, and next CLI steps so work resumes in 1 turn. | [`SKILL.md`](./skills/session-handoff/SKILL.md) |
| **7** | **`workspace-researcher`** | **Skill** | **Phantom & Deprecated APIs**: Stops agents from inventing fake methods. Triangulates official docs and benchmark repos ($\ge 2$ sources). | [`SKILL.md`](./skills/workspace-researcher/SKILL.md) |
| **8** | **`human-in-the-loop-governor`** | **Skill** | **Accidental Destruction**: Inserts pause breakpoints and rollback snapshots before destructive steps (`DROP TABLE`, `rm -rf`, production deploys). | [`SKILL.md`](./skills/human-in-the-loop-governor/SKILL.md) |
| **9** | **`backend-architecture`** | **Skill** | **Brittle Endpoints**: Enforces strict Pydantic/Zod schemas, transactional ACID boundaries, connection pooling, and Redis caching. | [`SKILL.md`](./skills/backend-architecture/SKILL.md) |
| **10** | **`docker-container-architect`** | **Skill** | **"Works on My Machine"**: Authors minimal multi-stage Dockerfiles with Alpine/Distroless bases, non-root users (UID $\ge 10000$), and layer caching. | [`SKILL.md`](./skills/docker-container-architect/SKILL.md) |

---

## 4. Autonomous Agent Personas Fleet (10 Agents)

Explore detailed specifications, system prompts, operational state machines, and I/O contracts in [`agents/`](./agents/README.md):

| Agent Persona | Role & Operational Mandate | Model Tier | Governance | Bound Skills Matrix | Specification |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **`lead-orchestrator`** | **Master Workflow & Team Lead**: Decomposes user goals into DAGs, routes subtasks, manages consensus debate, and enforces checkpoints. | `reasoning-heavy` | `checkpointed` | `plan-and-execute`, `multi-agent-orchestrator`, `human-in-the-loop-governor`, `session-handoff`, `brainstorming`, `knowledge-capture`, `llm-observability` | [AGENT.md](./agents/lead-orchestrator/AGENT.md) |
| **`research-analyst`** | **Deep Research & Knowledge Ingestion**: Web crawling, multi-source triangulation ($\ge 2$ sources), graph-RAG, and briefing compilation. | `reasoning-heavy` | `autonomous` | `workspace-researcher`, `agentic-rag-engineer`, `graph-rag-builder`, `office-doc-engine`, `knowledge-capture`, `llm-observability` | [AGENT.md](./agents/research-analyst/AGENT.md) |
| **`fullstack-engineer`** | **Full-Stack Implementation**: Robust APIs, modern frontend UI aesthetics, Docker containers, and git sandboxing. | `reasoning-heavy` | `checkpointed` | `backend-architecture`, `frontend-design`, `docker-container-architect`, `git-plumbing-and-automation`, `mcp-tool-integrator`, `llm-observability` | [AGENT.md](./agents/fullstack-engineer/AGENT.md) |
| **`code-quality-auditor`** | **Quality Assurance & Evals**: Pre-merge code reviews, minimal bug repros, agent trajectory evaluation, and CI/CD benchmarks. | `reasoning-heavy` | `autonomous` | `code-reviewer`, `bug-hunter`, `llm-evals-engineer`, `agent-trajectory-evaluator`, `llm-observability` | [AGENT.md](./agents/code-quality-auditor/AGENT.md) |
| **`security-red-teamer`** | **Adversarial Red-Teaming**: OWASP Top 10 scans, prompt injection defense, secret detection, and dual-layer safety guardrails. | `reasoning-heavy` | `strict-hitl` | `security-vulnerability-scanner`, `prompt-injection-red-teamer`, `guardrails-enforcer`, `llm-observability` | [AGENT.md](./agents/security-red-teamer/AGENT.md) |
| **`data-scientist`** | **Data Science & ML**: Automated EDA, leakage-safe feature pipelines, hypothesis testing, SHAP explainability/fairness audits, ETL orchestration, and vector DB sizing. | `reasoning-heavy` | `autonomous` | `advanced-data-analyst`, `ml-feature-and-model-lab`, `data-pipeline-etl`, `vector-database-architect`, `eda-and-data-cleaning`, `feature-engineering-pipeline`, `statistical-hypothesis-tester`, `model-explainability-shap`, `llm-observability` | [AGENT.md](./agents/data-scientist/AGENT.md) |
| **`browser-navigator`** | **Browser Automation & Scraping**: Playwright web navigation, dynamic SPA interaction, form filling, visual screenshot verification, and DOM extraction. | `balanced` | `autonomous` | `workspace-researcher`, `office-doc-engine`, `llm-observability` | [AGENT.md](./agents/browser-navigator/AGENT.md) |
| **`sre-devops-guardian`** | **SRE, CI/CD & Deployments**: Multi-stage container hardening, Alpine/Distroless bases, zero-root UID enforcement, and incident triage. | `reasoning-heavy` | `checkpointed` | `docker-container-architect`, `git-plumbing-and-automation`, `backend-architecture`, `llm-observability` | [AGENT.md](./agents/sre-devops-guardian/AGENT.md) |
| **`finops-token-router`** | **FinOps & Model Gateway**: Dynamic model routing (cheap 8B vs frontier reasoning), semantic prompt caching, and token burn rate tracking. | `fast` | `autonomous` | `llm-observability`, `llm-evals-engineer`, `backend-architecture` | [AGENT.md](./agents/finops-token-router/AGENT.md) |
| **`technical-writer-scribe`** | **Documentation & ADRs**: Architecture Decision Records (ADRs), API reference guides, Amazon 6-page executive memos, changelogs, and de-slopped human-style writing. | `balanced` | `autonomous` | `human-writer`, `executive-memo-architect`, `knowledge-capture`, `office-doc-engine`, `workspace-researcher`, `llm-observability` | [AGENT.md](./agents/technical-writer-scribe/AGENT.md) |

---

## 5. Operational Skills Catalog by Domain (39 Skills, 9 Domains)

Every skill includes trigger keywords, step-by-step SOPs, parseable Python code blocks, an **`Anti-Patterns & Traps to Avoid`** section, and a pre-flight **`Quality Checklist`**:

### 📊 1. Data Science & Analytics ([`skills/data-analysis/`](./skills/data-analysis/))
- **[`advanced-data-analyst`](./skills/data-analysis/advanced-data-analyst/SKILL.md)**: Flagship end-to-end data exploration, reproducible Python scripting, analytical SQL queries (window functions, cohort matrices, funnels), anomaly detection, and executive insights.
- **[`ml-feature-and-model-lab`](./skills/data-analysis/ml-feature-and-model-lab/SKILL.md)**: Consolidated ML pipeline lab: leakage-safe feature engineering, statistical hypothesis testing (A/B testing, Welch's t-test, Mann-Whitney U), and SHAP explainability/fairness audits.
- **[`eda-and-data-cleaning`](./skills/data-analysis/eda-and-data-cleaning/SKILL.md)**: Automated EDA profiling, distribution analysis, missing value strategy, and data leakage detection.
- **[`feature-engineering-pipeline`](./skills/data-analysis/feature-engineering-pipeline/SKILL.md)**: Cyclical datetime encoding, target encodings, interaction terms, and leakage-safe pipelines.
- **[`model-explainability-shap`](./skills/data-analysis/model-explainability-shap/SKILL.md)**: Model explainability via TreeSHAP/LinearSHAP, waterfall plots, beeswarm charts, and fairness audits.
- **[`statistical-hypothesis-tester`](./skills/data-analysis/statistical-hypothesis-tester/SKILL.md)**: Rigorous A/B testing, parametric/non-parametric tests (t-test, Mann-Whitney U), and power analysis.

### 🤖 2. Multi-Agent Orchestration & Governance ([`skills/orchestration/`](./skills/orchestration/))
- **[`multi-agent-orchestrator`](./skills/orchestration/multi-agent-orchestrator/SKILL.md)**: 4 structural topologies (Hierarchical, Router, Pipeline, Peer Debate) with native Mermaid flowchart. Avoids ping-pong loops.
- **[`plan-and-execute`](./skills/orchestration/plan-and-execute/SKILL.md)**: Pre-flight architectural analysis, blast-radius risk scoring, and bite-sized tasks (2–5 min) before touching code.
- **[`human-in-the-loop-governor`](./skills/orchestration/human-in-the-loop-governor/SKILL.md)**: State machine checkpoints with rollback states for destructive operations.
- **[`session-handoff`](./skills/orchestration/session-handoff/SKILL.md)**: Preserving context across resets and workday breaks via persistent `HANDOFF.md` ledger.
- **[`agent-trajectory-evaluator`](./skills/orchestration/agent-trajectory-evaluator/SKILL.md)**: Auditing intermediate tool call paths, parameter accuracy, and detecting loop thrashing.
- **[`llm-council`](./skills/orchestration/llm-council/SKILL.md)**: Karpathy-style 5-advisor deliberation, anonymous peer review, and chairman synthesis for high-stakes decisions.
- **[`brainstorming`](./skills/orchestration/brainstorming/SKILL.md)**: Socratic inquiry, exploring creative alternatives, trade-off analysis, and concept design briefs.

### 💻 3. Software Engineering, Architecture & DevOps ([`skills/software-engineering/`](./skills/software-engineering/))
- **[`backend-architecture`](./skills/software-engineering/backend-architecture/SKILL.md)**: Scalable REST/gRPC contracts, SQLAlchemy/Prisma models, ACID transactions, and Redis caching.
- **[`frontend-design`](./skills/software-engineering/frontend-design/SKILL.md)**: CSS design tokens, micro-animations, glassmorphism, and responsive layouts.
- **[`code-reviewer`](./skills/software-engineering/code-reviewer/SKILL.md)**: Senior peer review gates (Architecture, Typing, Tests, Smells).
- **[`bug-hunter`](./skills/software-engineering/bug-hunter/SKILL.md)**: Scientific bug isolation with minimal failing reproduction tests (RED -> GREEN).
- **[`docker-container-architect`](./skills/software-engineering/docker-container-architect/SKILL.md)**: Multi-stage Dockerfiles, Distroless/Alpine images, build cache optimizations, and non-root security.
- **[`git-plumbing-and-automation`](./skills/software-engineering/git-plumbing-and-automation/SKILL.md)**: Automated `git bisect`, git worktrees for isolated agent sandboxes, reflog recovery, and hook automation.

### 🛡️ 4. AI Security, Safety & Red-Teaming ([`skills/ai-security-safety/`](./skills/ai-security-safety/))
- **[`security-vulnerability-scanner`](./skills/ai-security-safety/security-vulnerability-scanner/SKILL.md)**: OWASP Top 10 auditing (SQLi, XSS, SSRF, Command Injection) and secret detection.
- **[`prompt-injection-red-teamer`](./skills/ai-security-safety/prompt-injection-red-teamer/SKILL.md)**: Direct jailbreaks, system prompt exfiltration, and indirect injection defenses.
- **[`guardrails-enforcer`](./skills/ai-security-safety/guardrails-enforcer/SKILL.md)**: Real-time dual-layer guardrails, PII redaction, topic bounds, and ReDoS prevention.

### 🧠 5. RAG, Knowledge & Tool Integrations ([`skills/rag-and-knowledge/`](./skills/rag-and-knowledge/))
- **[`agentic-rag-engineer`](./skills/rag-and-knowledge/agentic-rag-engineer/SKILL.md)**: Self-RAG and Corrective RAG (CRAG) loop with re-ranking and query rewrite.
- **[`graph-rag-builder`](./skills/rag-and-knowledge/graph-rag-builder/SKILL.md)**: Triplet extraction and Neo4j/JSON graph construction for multi-hop reasoning.
- **[`agent-memory-architect`](./skills/rag-and-knowledge/agent-memory-architect/SKILL.md)**: 3-tier memory model (Working, Episodic, Semantic) with native Mermaid flow diagram.
- **[`mcp-tool-integrator`](./skills/rag-and-knowledge/mcp-tool-integrator/SKILL.md)**: Building Model Context Protocol servers with FastMCP and Pydantic schemas. Avoids subprocess crashes.

### 📡 6. LLM Engineering, Evals & Observability ([`skills/llm-engineering/`](./skills/llm-engineering/))
- **[`prompt-architect`](./skills/llm-engineering/prompt-architect/SKILL.md)**: 6-block system prompt structure, XML delimiters, and strict Instructor/Pydantic schemas.
- **[`llm-evals-engineer`](./skills/llm-engineering/llm-evals-engineer/SKILL.md)**: Automated CI/CD evaluation suites, LLM-as-a-judge rubrics, and faithfulness scoring.
- **[`llm-observability`](./skills/llm-engineering/llm-observability/SKILL.md)**: OpenTelemetry GenAI & OpenInference tracing, token/cost tracking, latency profiling. Includes companion script in [`scripts/telemetry_engine.py`](./skills/llm-engineering/llm-observability/scripts/telemetry_engine.py).

### ✍️ 7. Human Writing, Research & Knowledge Capture ([`skills/writing-and-research/`](./skills/writing-and-research/))
- **[`human-writer`](./skills/writing-and-research/human-writer/SKILL.md)**: Removes AI writing tells and de-slops synthetic text using Wikipedia's 29-pattern framework. Features voice calibration and dual-pass recursive self-audits while preserving 100% semantic fidelity.
- **[`workspace-researcher`](./skills/writing-and-research/workspace-researcher/SKILL.md)**: High-signal web crawling, documentation indexing, and citation-backed synthesis briefs.
- **[`knowledge-capture`](./skills/writing-and-research/knowledge-capture/SKILL.md)**: Extracting structured decisions, action items, and documentation from transcripts and chats.
- **[`office-doc-engine`](./skills/writing-and-research/office-doc-engine/SKILL.md)**: Programmatic creation and parsing of Word (.docx), Excel (.xlsx), PowerPoint (.pptx), and PDF files.
- **[`skill-creator`](./skills/writing-and-research/skill-creator/SKILL.md)**: Designing, validating, and packaging new agent skills using progressive disclosure.

### 🗄️ 8. Database & Data Engineering ([`skills/database-and-data-engineering/`](./skills/database-and-data-engineering/))
- **[`data-pipeline-etl`](./skills/database-and-data-engineering/data-pipeline-etl/SKILL.md)**: Modern ELT orchestration (Airflow 2.x TaskFlow, Dagster), dbt Kimball dimensional star modeling (staging, intermediate, incremental marts with lookback windows), and automated data quality assertions.
- **[`vector-database-architect`](./skills/database-and-data-engineering/vector-database-architect/SKILL.md)**: High-dimensional vector search optimization: HNSW (`M`, `ef_construction`, `ef_search`) and IVFFlat parameter tuning, SQ8/PQ vector quantization, pgvector and Qdrant production schemas, and hardware RAM sizing.
- **[`streaming-and-event-driven`](./skills/database-and-data-engineering/streaming-and-event-driven/SKILL.md)**: Distributed event streaming (Kafka, Redpanda, Redis Streams): deterministic partition key hashing, Transactional Outbox pattern, non-blocking retry topics with Dead Letter Queues (DLQ), and idempotent consumer deduplication.

### 🎨 9. AI Product Design & Executive UX ([`skills/ai-product-and-ux/`](./skills/ai-product-and-ux/))
- **[`agentic-ui-patterns`](./skills/ai-product-and-ux/agentic-ui-patterns/SKILL.md)**: Modern agentic frontend UX: glitch-free token streaming with unclosed markdown fence repair, collapsible pulsing reasoning accordions, dynamic Generative UI component card hydration, and human-in-the-loop code diff review drawers.
- **[`executive-memo-architect`](./skills/ai-product-and-ux/executive-memo-architect/SKILL.md)**: Strategic business communication adhering to the Amazon 6-Page Narrative Methodology, investor and board update memos, quantitative metric density auditing, and corporate weasel-word elimination.

---

## 6. Declarative Multi-Agent Workflows

The [`workflows/`](./workflows/README.md) subsystem provides a zero-dependency DAG execution engine ([`workflows/workflow_engine.py`](./workflows/workflow_engine.py)) with 4 pre-built pipelines:

1. **[`deep-research`](./workflows/deep-research/workflow.json)**: `lead-orchestrator` $\rightarrow$ `research-analyst` $\rightarrow$ `technical-writer-scribe`.
2. **[`feature-factory`](./workflows/feature-factory/workflow.json)**: `lead-orchestrator` $\rightarrow$ `fullstack-engineer` $\rightarrow$ `code-quality-auditor` $\rightarrow$ `security-red-teamer` $\rightarrow$ `sre-devops-guardian`.
3. **[`self-healing-code`](./workflows/self-healing-code/workflow.json)**: `code-quality-auditor` (isolate repro) $\rightarrow$ `fullstack-engineer` (patch) $\rightarrow$ `code-quality-auditor` (prove green) $\rightarrow$ `technical-writer-scribe` (RCA post-mortem).
4. **[`model-fairness-audit`](./workflows/model-fairness-audit/workflow.json)**: `data-scientist` (leakage-safe split) $\rightarrow$ `data-scientist` (SHAP values) $\rightarrow$ `technical-writer-scribe` (model card).

*For workflow execution instructions, step schemas, and dependency DAG syntax, refer to the [Workflows Documentation](./workflows/README.md).*

---

## 7. FastMCP Tool Servers

The [`mcp_servers/`](./mcp_servers/README.md) directory provides 3 ready-to-run Model Context Protocol (MCP) servers conforming to standard JSON-RPC 2.0:

1. **[`code_sandbox_server.py`](./mcp_servers/code_sandbox_server.py)**: AST syntax pre-validation, execution timeouts (10s default), and stdout/stderr capture.
2. **[`filesystem_server.py`](./mcp_servers/filesystem_server.py)**: Path-traversal protection, atomic writes with automatic `.bak` snapshots, and unified diff previews.
3. **[`hybrid_retriever_server.py`](./mcp_servers/hybrid_retriever_server.py)**: Local BM25 ranking and keyword-overlap scoring over text documents.

*For complete JSON-RPC configuration templates for Antigravity, Claude Desktop, and Cursor, refer to the [MCP Tool Servers Guide](./mcp_servers/README.md).*

---

## 8. 3-Tier Agentic Memory Engine

Implemented in [`memory/memory_engine.py`](./memory/memory_engine.py) to eliminate AI amnesia across resets:

- **Tier 1 (Working)**: In-memory scratchpad with token tracking and automatic compaction into rolling milestone summaries at 85% budget.
- **Tier 2 (Episodic)**: Persistent SQLite ledger (`.memory/agent_memory.db`) recording chronological session turns, tool payloads, latencies, and token usage.
- **Tier 3 (Semantic)**: Durable long-term fact store with root-prefix subword vector similarity matching, tracking access counts and timestamps.

*For programmatic Python API usage and CLI testing commands, refer to the [Memory Engine Guide](./memory/README.md).*

---

## 9. Agent Autonomy Benchmarks Gym

Implemented in [`benchmarks/benchmark_runner.py`](./benchmarks/benchmark_runner.py) to evaluate agent reliability before deployment:

- **`TRAJ-01`**: Trajectory Directness Score ($S_{direct} = \frac{\text{optimal\_steps}}{\text{actual\_steps}}$).
- **`LOOP-01`**: Loop & Thrashing Resilience (asserts retry termination $\le 3$ attempts upon simulated tool failure).
- **`SCHEMA-01`**: Tool Parameter Accuracy (asserts 100% parameter type and required-field compliance).

*For test execution instructions and metric thresholds, refer to the [Benchmarks Guide](./benchmarks/README.md).*

---

## 10. Interactive Visual Terminal Playground

Launch an interactive, color-coded terminal simulation to observe agents collaborating, executing tools, preserving memory, and requesting Human-in-the-Loop approvals.

*For complete CLI arguments, custom objectives, and live simulation options, refer to the [Agents Runtime Guide](./agents/README.md).*

## 11. Repository Directory Structure

- **[`README.md`](./README.md)**: Master platform documentation and catalog index.
- **[`.gitignore`](./.gitignore)**: Production git ignore rules for cache, databases, and OS clutter.
- **[`.opencode/`](./.opencode/README.md)**: OpenCode skills discovery setup and configuration guide.
- **[`skills/`](./skills/README.md)**: 39 modular capability SOPs across 9 domain hubs, with anti-patterns and quality checklists.
- **[`agents/`](./agents/README.md)**: 10 autonomous goal-driven agent personas and orchestration runtime.
- **[`workflows/`](./workflows/README.md)**: Declarative multi-agent DAG execution engine and 4 pre-built pipelines.
- **[`mcp_servers/`](./mcp_servers/README.md)**: Ready-to-run FastMCP tool servers (Code sandbox, Filesystem, Hybrid retriever).
- **[`memory/`](./memory/README.md)**: Production 3-tier agentic memory engine (Working, Episodic SQLite, Semantic vector).
- **[`benchmarks/`](./benchmarks/README.md)**: Agent autonomy, trajectory directness, and loop resilience gym.

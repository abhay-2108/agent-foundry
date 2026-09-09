# Operational AI Agent Skills Catalog

A comprehensive, production-grade library of **30 operational AI Agent Skills** conforming to the universal Agent Skill specification (compatible with **Antigravity**, **Claude Code**, **Codex**, and **OpenCode**).

Each skill resides in its own dedicated directory containing a standardized `SKILL.md` instruction file that uses **progressive disclosure** (lightweight YAML metadata loaded at startup, full instructions loaded only when triggered).

---

## Skills by Domain

### 🤖 1. Multi-Agent Orchestration & Workflow Design
- **[`multi-agent-orchestrator`](./multi-agent-orchestrator/SKILL.md)**: Designing agent topologies (Hierarchical, Router, Peer Debate), state schemas, and loop prevention.
- **[`mcp-tool-integrator`](./mcp-tool-integrator/SKILL.md)**: Building Model Context Protocol (MCP) servers, bulletproof schemas (Zod/Pydantic), and tool error handling.
- **[`human-in-the-loop-governor`](./human-in-the-loop-governor/SKILL.md)**: Approval gates for high-risk actions (production deploys, payments, drops) and state checkpoints.

### 🧠 2. Agentic Memory & Knowledge Retrieval (RAG)
- **[`agent-memory-architect`](./agent-memory-architect/SKILL.md)**: Tiered memory architecture (Working, Episodic, Semantic) with vector stores.
- **[`agentic-rag-engineer`](./agentic-rag-engineer/SKILL.md)**: Hybrid search (dense + BM25), semantic chunking, cross-encoder re-ranking, and Self-RAG/CRAG.
- **[`graph-rag-builder`](./graph-rag-builder/SKILL.md)**: Entity/triplet extraction, graph construction, and multi-hop relational reasoning.

### 📝 3. Prompt Engineering & System Design
- **[`prompt-architect`](./prompt-architect/SKILL.md)**: 6-block system prompt design, negative constraints, XML delimiters, and strict schemas.

### 📊 4. AI Reliability, Evaluation & Benchmarking ("Evals")
- **[`llm-evals-engineer`](./llm-evals-engineer/SKILL.md)**: Automated CI/CD evaluation suites, LLM-as-a-judge rubrics, faithfulness, and hallucination scoring.
- **[`agent-trajectory-evaluator`](./agent-trajectory-evaluator/SKILL.md)**: Auditing intermediate tool call sequences, path directness, parameter accuracy, and agent loop thrashing.

### 🛑 5. AI Security, Safety & Red-Teaming
- **[`prompt-injection-red-teamer`](./prompt-injection-red-teamer/SKILL.md)**: Testing direct jailbreaks, system prompt exfiltration, and indirect prompt injection.
- **[`guardrails-enforcer`](./guardrails-enforcer/SKILL.md)**: Real-time dual-layer guardrails, PII redaction, topic bounds, and output filters.

### 🛡️ 6. Code Quality, Debugging & Application Security
- **[`bug-hunter`](./bug-hunter/SKILL.md)**: Diagnosing crashes, runtime exceptions, and race conditions using minimal repro test cases (RED -> GREEN).
- **[`code-reviewer`](./code-reviewer/SKILL.md)**: Senior peer reviews & automated pre-merge gates (static typing, linting, tests, architecture, and code smells).
- **[`security-vulnerability-scanner`](./security-vulnerability-scanner/SKILL.md)**: OWASP Top 10 auditing (SQLi, XSS, SSRF, Command Injection, Path Traversal) and secret detection.

### 🎨 7. Design & Full-Stack Architecture
- **[`frontend-design`](./frontend-design/SKILL.md)**: Modern aesthetic excellence, design tokens, micro-animations, glassmorphism, and responsive polish.
- **[`backend-architecture`](./backend-architecture/SKILL.md)**: Scalable API contracts, database modeling, ACID transactions, caching strategies, and resilient middleware.
- **[`skill-creator`](./skill-creator/SKILL.md)**: Designing, evaluating, testing, and packaging new agent skills using progressive disclosure.

### 📈 8. Data Science, Machine Learning & Analytics
- **[`eda-and-data-cleaning`](./eda-and-data-cleaning/SKILL.md)**: Automated EDA profiling, distribution analysis, missing value strategy, and data leakage detection.
- **[`feature-engineering-pipeline`](./feature-engineering-pipeline/SKILL.md)**: Cyclical datetime encoding, target encodings, interaction terms, and leakage-safe pipelines.
- **[`model-explainability-shap`](./model-explainability-shap/SKILL.md)**: Model explainability via TreeSHAP/LinearSHAP, waterfall plots, beeswarm charts, and fairness audits.
- **[`statistical-hypothesis-tester`](./statistical-hypothesis-tester/SKILL.md)**: Rigorous A/B testing, parametric/non-parametric tests (t-test, Mann-Whitney U), and power analysis.

### 📡 9. Observability & Agent Telemetry
- **[`llm-observability`](./llm-observability/SKILL.md)**: Vendor-neutral OpenTelemetry GenAI & OpenInference tracing, token/cost tracking, latency profiling.

### 🛠️ 10. Developer Tools & Git Automation
- **[`docker-container-architect`](./docker-container-architect/SKILL.md)**: Multi-stage Dockerfiles, Distroless/Alpine images, build cache optimizations, and non-root security.
- **[`git-plumbing-and-automation`](./git-plumbing-and-automation/SKILL.md)**: Automated `git bisect`, git worktrees for isolated agent sandboxes, reflog recovery, and hook automation.

### ⚙️ 11. Core Productivity & Workplace Operations
- **[`brainstorming`](./brainstorming/SKILL.md)**: Socratic inquiry, exploring creative alternatives, trade-off analysis, and concept design briefs.
- **[`plan-and-execute`](./plan-and-execute/SKILL.md)**: High-complexity tasks, architectural analysis, bite-sized tasks (2–5 min) before touching code.
- **[`session-handoff`](./session-handoff/SKILL.md)**: Preserving context across agent resets and work breaks via persistent `HANDOFF.md` ledger.
- **[`office-doc-engine`](./office-doc-engine/SKILL.md)**: Programmatic creation and parsing of Word (.docx), Excel (.xlsx), PowerPoint (.pptx), and PDF files.
- **[`workspace-researcher`](./workspace-researcher/SKILL.md)**: High-signal web crawling, documentation indexing, and citation-backed synthesis briefs.
- **[`knowledge-capture`](./knowledge-capture/SKILL.md)**: Extracting structured decisions, action items, and documentation from transcripts and chats.

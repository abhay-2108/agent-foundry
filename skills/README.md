# Operational AI Agent Skills Catalog

A comprehensive, production-grade library of **39 operational AI Agent Skills** organized into **9 domain hubs** conforming to the universal Agent Skill specification (compatible with **Antigravity**, **Claude Code**, **Codex**, and **OpenCode**).

Each skill resides in its own dedicated directory containing a standardized `SKILL.md` instruction file that uses **progressive disclosure** (lightweight YAML metadata loaded at startup, full instructions loaded only when triggered).

---

## Skills by Domain Hub (9 Categories)

### 📊 1. Data Science & Analytics ([`data-analysis/`](./data-analysis/))
- **[`advanced-data-analyst`](./data-analysis/advanced-data-analyst/SKILL.md)**: Flagship end-to-end data exploration, reproducible Python scripting, analytical SQL queries (window functions, cohort matrices, funnels), anomaly detection, and executive insights.
- **[`ml-feature-and-model-lab`](./data-analysis/ml-feature-and-model-lab/SKILL.md)**: Consolidated ML pipeline lab: leakage-safe feature engineering, statistical hypothesis testing (A/B testing, Welch's t-test, Mann-Whitney U), and SHAP explainability/fairness audits.
- **[`eda-and-data-cleaning`](./data-analysis/eda-and-data-cleaning/SKILL.md)**: Automated EDA profiling, distribution analysis, missing value strategy, and data leakage detection.
- **[`feature-engineering-pipeline`](./data-analysis/feature-engineering-pipeline/SKILL.md)**: Cyclical datetime encoding, target encodings, interaction terms, and leakage-safe pipelines.
- **[`model-explainability-shap`](./data-analysis/model-explainability-shap/SKILL.md)**: Model explainability via TreeSHAP/LinearSHAP, waterfall plots, beeswarm charts, and fairness audits.
- **[`statistical-hypothesis-tester`](./data-analysis/statistical-hypothesis-tester/SKILL.md)**: Rigorous A/B testing, parametric/non-parametric tests (t-test, Mann-Whitney U), and power analysis.

### 🤖 2. Multi-Agent Orchestration & Governance ([`orchestration/`](./orchestration/))
- **[`multi-agent-orchestrator`](./orchestration/multi-agent-orchestrator/SKILL.md)**: Designing agent topologies (Hierarchical, Router, Peer Debate), state schemas, and loop prevention.
- **[`plan-and-execute`](./orchestration/plan-and-execute/SKILL.md)**: High-complexity tasks, architectural analysis, blast-radius risk scoring, bite-sized tasks (2–5 min) before touching code.
- **[`human-in-the-loop-governor`](./orchestration/human-in-the-loop-governor/SKILL.md)**: Approval gates for high-risk actions (production deploys, payments, drops) and state checkpoints.
- **[`session-handoff`](./orchestration/session-handoff/SKILL.md)**: Preserving context across agent resets and work breaks via persistent `HANDOFF.md` ledger.
- **[`agent-trajectory-evaluator`](./orchestration/agent-trajectory-evaluator/SKILL.md)**: Auditing intermediate tool call sequences, path directness, parameter accuracy, and agent loop thrashing.
- **[`llm-council`](./orchestration/llm-council/SKILL.md)**: Karpathy-style 5-advisor deliberation, anonymous peer review, and chairman synthesis for high-stakes decisions.
- **[`brainstorming`](./orchestration/brainstorming/SKILL.md)**: Socratic inquiry, exploring creative alternatives, trade-off analysis, and concept design briefs.

### 💻 3. Software Engineering, Architecture & DevOps ([`software-engineering/`](./software-engineering/))
- **[`backend-architecture`](./software-engineering/backend-architecture/SKILL.md)**: Scalable API contracts, database modeling, ACID transactions, caching strategies, and resilient middleware.
- **[`frontend-design`](./software-engineering/frontend-design/SKILL.md)**: Modern aesthetic excellence, design tokens, micro-animations, glassmorphism, and responsive polish.
- **[`code-reviewer`](./software-engineering/code-reviewer/SKILL.md)**: Senior peer reviews & automated pre-merge gates (static typing, linting, tests, architecture, and code smells).
- **[`bug-hunter`](./software-engineering/bug-hunter/SKILL.md)**: Diagnosing crashes, runtime exceptions, and race conditions using minimal repro test cases (RED -> GREEN).
- **[`docker-container-architect`](./software-engineering/docker-container-architect/SKILL.md)**: Multi-stage Dockerfiles, Distroless/Alpine images, build cache optimizations, and non-root security.
- **[`git-plumbing-and-automation`](./software-engineering/git-plumbing-and-automation/SKILL.md)**: Automated `git bisect`, git worktrees for isolated agent sandboxes, reflog recovery, and hook automation.

### 🛡️ 4. AI Security, Safety & Red-Teaming ([`ai-security-safety/`](./ai-security-safety/))
- **[`security-vulnerability-scanner`](./ai-security-safety/security-vulnerability-scanner/SKILL.md)**: OWASP Top 10 auditing (SQLi, XSS, SSRF, Command Injection, Path Traversal) and secret detection.
- **[`prompt-injection-red-teamer`](./ai-security-safety/prompt-injection-red-teamer/SKILL.md)**: Testing direct jailbreaks, system prompt exfiltration, and indirect prompt injection.
- **[`guardrails-enforcer`](./ai-security-safety/guardrails-enforcer/SKILL.md)**: Real-time dual-layer guardrails, PII redaction, topic bounds, and output filters.

### 🧠 5. RAG, Knowledge & Tool Integrations ([`rag-and-knowledge/`](./rag-and-knowledge/))
- **[`agentic-rag-engineer`](./rag-and-knowledge/agentic-rag-engineer/SKILL.md)**: Hybrid search (dense + BM25), semantic chunking, cross-encoder re-ranking, and Self-RAG/CRAG.
- **[`graph-rag-builder`](./rag-and-knowledge/graph-rag-builder/SKILL.md)**: Entity/triplet extraction, graph construction, and multi-hop relational reasoning.
- **[`agent-memory-architect`](./rag-and-knowledge/agent-memory-architect/SKILL.md)**: Tiered memory architecture (Working, Episodic, Semantic) with vector stores.
- **[`mcp-tool-integrator`](./rag-and-knowledge/mcp-tool-integrator/SKILL.md)**: Building Model Context Protocol (MCP) servers, bulletproof schemas (Zod/Pydantic), and tool error handling.

### 📡 6. LLM Engineering, Evals & Observability ([`llm-engineering/`](./llm-engineering/))
- **[`prompt-architect`](./llm-engineering/prompt-architect/SKILL.md)**: 6-block system prompt design, negative constraints, XML delimiters, and strict schemas.
- **[`llm-evals-engineer`](./llm-engineering/llm-evals-engineer/SKILL.md)**: Automated CI/CD evaluation suites, LLM-as-a-judge rubrics, faithfulness, and hallucination scoring.
- **[`llm-observability`](./llm-engineering/llm-observability/SKILL.md)**: Vendor-neutral OpenTelemetry GenAI & OpenInference tracing, token/cost tracking, latency profiling.

### ✍️ 7. Human Writing, Research & Knowledge Capture ([`writing-and-research/`](./writing-and-research/))
- **[`human-writer`](./writing-and-research/human-writer/SKILL.md)**: Removes AI writing tells and de-slops synthetic text using Wikipedia's 29-pattern framework. Features voice calibration and dual-pass recursive self-audits while preserving 100% semantic fidelity.
- **[`workspace-researcher`](./writing-and-research/workspace-researcher/SKILL.md)**: High-signal web crawling, documentation indexing, and citation-backed synthesis briefs.
- **[`knowledge-capture`](./writing-and-research/knowledge-capture/SKILL.md)**: Extracting structured decisions, action items, and documentation from transcripts and chats.
- **[`office-doc-engine`](./writing-and-research/office-doc-engine/SKILL.md)**: Programmatic creation and parsing of Word (.docx), Excel (.xlsx), PowerPoint (.pptx), and PDF files.
- **[`skill-creator`](./writing-and-research/skill-creator/SKILL.md)**: Designing, evaluating, testing, and packaging new agent skills using progressive disclosure.

### 🗄️ 8. Database & Data Engineering ([`database-and-data-engineering/`](./database-and-data-engineering/))
- **[`data-pipeline-etl`](./database-and-data-engineering/data-pipeline-etl/SKILL.md)**: Modern ELT orchestration (Airflow 2.x TaskFlow, Dagster), dbt Kimball dimensional star modeling (staging, intermediate, incremental marts with lookback windows), and automated data quality assertions.
- **[`vector-database-architect`](./database-and-data-engineering/vector-database-architect/SKILL.md)**: High-dimensional vector search optimization: HNSW (`M`, `ef_construction`, `ef_search`) and IVFFlat parameter tuning, SQ8/PQ vector quantization, pgvector and Qdrant production schemas, single-stage pre-filtering, and hardware RAM capacity sizing.
- **[`streaming-and-event-driven`](./database-and-data-engineering/streaming-and-event-driven/SKILL.md)**: Distributed event streaming architectures (Kafka, Redpanda, Redis Streams): deterministic partition key hashing, Transactional Outbox pattern, non-blocking retry topics with Dead Letter Queues (DLQ), and idempotent consumer deduplication.

### 🎨 9. AI Product Design & Executive UX ([`ai-product-and-ux/`](./ai-product-and-ux/))
- **[`agentic-ui-patterns`](./ai-product-and-ux/agentic-ui-patterns/SKILL.md)**: Modern agentic frontend UX: glitch-free token streaming with unclosed markdown fence repair, collapsible pulsing reasoning accordions (`<thought>`), dynamic Generative UI component card hydration, and human-in-the-loop code diff review drawers.
- **[`executive-memo-architect`](./ai-product-and-ux/executive-memo-architect/SKILL.md)**: Strategic business communication adhering to the Amazon 6-Page Narrative Methodology, investor and board update memos, quantitative metric density auditing, and corporate weasel-word elimination.

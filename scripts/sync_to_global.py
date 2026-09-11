#!/usr/bin/env python3
"""
sync_to_global.py — Synchronizes all skills, agents, workflows, configs, and commands
from the repository workspace to global installations for Antigravity and OpenCode.
"""

import os
import shutil
import json
import re
from pathlib import Path

WORKSPACE = Path(r"P:\AIML Projects\Skills and Agents")
GEMINI_DIR = Path(r"C:\Users\Abhay Tiwari\.gemini")
AGENT_FOUNDRY_GLOBAL = GEMINI_DIR / "agent-foundry"
GEMINI_CONFIG = GEMINI_DIR / "config"
GEMINI_CONFIG_SKILLS = GEMINI_CONFIG / "skills"
OPENCODE_DIR = Path(r"C:\Users\Abhay Tiwari\.opencode")
OPENCODE_ROAMING = Path(r"C:\Users\Abhay Tiwari\AppData\Roaming\opencode")
OPENCODE_AGENTS = OPENCODE_ROAMING / "agents"
OPENCODE_COMMANDS = OPENCODE_ROAMING / "commands"

IGNORE_PATTERNS = shutil.ignore_patterns(
    ".git", ".memory", ".pytest_cache", "__pycache__", "*.pyc", 
    "*.db", "*.sqlite*", "scratch", "tmp", ".venv", "env", "node_modules"
)

def sync_agent_foundry_global():
    print("[*] 1. Syncing workspace to global Agent Foundry (~/.gemini/agent-foundry)...")
    AGENT_FOUNDRY_GLOBAL.mkdir(parents=True, exist_ok=True)
    
    top_dirs = ["agents", "benchmarks", "mcp_servers", "memory", "skills", "workflows"]
    for d in top_dirs:
        src = WORKSPACE / d
        dst = AGENT_FOUNDRY_GLOBAL / d
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=IGNORE_PATTERNS)
            print(f"    [+] Mirrored {d}/ -> {dst}")
            
    # Copy root documentation and config files
    for f in ["README.md", ".gitignore"]:
        src = WORKSPACE / f
        dst = AGENT_FOUNDRY_GLOBAL / f
        if src.exists():
            shutil.copy2(src, dst)
            print(f"    [+] Copied {f} -> {dst}")

def sync_antigravity_config_skills():
    print("[*] 2. Syncing skills to Antigravity global config (~/.gemini/config/skills)...")
    GEMINI_CONFIG_SKILLS.mkdir(parents=True, exist_ok=True)
    
    # Locate all SKILL.md files under WORKSPACE/skills
    skill_count = 0
    for skill_file in (WORKSPACE / "skills").rglob("SKILL.md"):
        skill_dir = skill_file.parent
        skill_name = skill_dir.name
        
        # Copy to flat directory in GEMINI_CONFIG_SKILLS for native Antigravity discovery
        target_dir = GEMINI_CONFIG_SKILLS / skill_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(skill_dir, target_dir, ignore=IGNORE_PATTERNS)
        skill_count += 1
        
    print(f"    [+] Deployed {skill_count} flat skills to {GEMINI_CONFIG_SKILLS}")

def update_skills_json():
    print("[*] 3. Updating Antigravity ~/.gemini/config/skills.json...")
    domains = [
        "ai-product-and-ux",
        "ai-security-safety",
        "data-analysis",
        "database-and-data-engineering",
        "llm-engineering",
        "orchestration",
        "rag-and-knowledge",
        "software-engineering",
        "writing-and-research"
    ]
    
    entries = [
        {"path": str(GEMINI_CONFIG_SKILLS).replace("\\", "/")},
        {"path": str(AGENT_FOUNDRY_GLOBAL / "skills").replace("\\", "/")},
        {"path": str(WORKSPACE / "skills").replace("\\", "/")}
    ]
    
    for d in domains:
        entries.append({"path": str(AGENT_FOUNDRY_GLOBAL / "skills" / d).replace("\\", "/")})
        entries.append({"path": str(WORKSPACE / "skills" / d).replace("\\", "/")})
        
    skills_json_path = GEMINI_CONFIG / "skills.json"
    skills_json_path.write_text(json.dumps({"entries": entries}, indent=2), encoding="utf-8")
    print(f"    [+] Updated {skills_json_path} with {len(entries)} discovery paths.")

def update_global_guidance_md():
    print("[*] 4. Updating ~/.gemini/config/AGENTS.md & GEMINI.md...")
    content = """# Agent Foundry Global System Instructions & Capabilities

You have direct access to the **Agent Foundry Ecosystem** installed globally on this machine.
Whenever you are chatting in any project or workspace, you have access to these capabilities:

---

## 1. Ten Autonomous Specialist Personas
You can embody or consult any of the 10 specialist personas on demand. When the user specifies a persona (e.g., `@code-quality-auditor`, `@security-red-teamer`, `@lead-orchestrator`), adopt their exact domain mindset and quality standards:

1. **`lead-orchestrator`**: Master coordinator; breaks ambiguous problems into step-by-step DAG plans, assigns sub-tasks, and verifies exit criteria.
2. **`research-analyst`**: Exhaustive discovery; reads file hierarchies, maps dependency graphs, and discovers hidden bugs without making destructive edits.
3. **`fullstack-engineer`**: Production-grade feature builder; implements clean backend APIs, responsive frontends, and comprehensive test suites.
4. **`code-quality-auditor`**: Senior staff engineer; reviews code against strict anti-patterns, cyclomatic complexity limits, and type safety.
5. **`security-red-teamer`**: Offensive/defensive security specialist; tests for injection, CVEs, secret leaks, path traversals, and boundary violations.
6. **`data-scientist`**: Quantitative rigor; performs exploratory data analysis, feature engineering pipelines, and statistical hypothesis testing.
7. **`browser-navigator`**: E2E web specialist; designs DOM interactions, verifies UI layouts, and captures visual regression evidence.
8. **`sre-devops-guardian`**: Reliability engineer; inspects Dockerfiles, CI/CD pipelines, latency budgets, and health check architectures.
9. **`finops-token-router`**: Inference economist; optimizes context windows, enforces token budgets, leverages prompt caching, and reduces API costs.
10. **`technical-writer-scribe`**: Documentation architect; creates structured markdown, architecture decision records (ADRs), and visual mermaid diagrams.

---

## 2. Thirty-Nine Globally Available Skills across 9 Domains
All 39 skills are indexed globally under `~/.gemini/config/skills/`. Antigravity's progressive disclosure dynamically injects their runbooks when relevant:
- **Orchestration (5)**: `multi-agent-orchestrator`, `plan-and-execute`, `human-in-the-loop-governor`, `session-handoff`, `agent-trajectory-evaluator`
- **Software Engineering & Quality (6)**: `code-reviewer`, `bug-hunter`, `backend-architecture`, `frontend-design`, `docker-container-architect`, `git-plumbing-and-automation`
- **Data Analysis & Modeling (4)**: `advanced-data-analyst`, `ml-feature-and-model-lab`, `eda-and-data-cleaning`, `model-explainability-shap`
- **Database & Data Engineering (3)**: `data-pipeline-etl`, `vector-database-architect`, `streaming-and-event-driven`
- **LLM Engineering & Evals (4)**: `llm-council`, `llm-evals-engineer`, `llm-observability`, `prompt-architect`
- **RAG & Knowledge (3)**: `agentic-rag-engineer`, `graph-rag-builder`, `mcp-tool-integrator`
- **AI Security & Safety (3)**: `security-vulnerability-scanner`, `prompt-injection-red-teamer`, `guardrails-enforcer`
- **AI Product & UX (2)**: `agentic-ui-patterns`, `executive-memo-architect`
- **Writing & Research (4)**: `workspace-researcher`, `knowledge-capture`, `brainstorming`, `office-doc-engine`, `humanize-ai-text`
- **Foundational Specialists**: `skill-creator`, `agent-memory-architect`, `statistical-hypothesis-tester`, `feature-engineering-pipeline`

---

## 3. Persistent 3-Tier Memory Engine
Memories persist globally across all workspaces and sessions in SQLite at:
`C:\\Users\\Abhay Tiwari\\.gemini\\agent_foundry_memory.db`

- **Tier 1 (Working Memory)**: Use `memory_add_working_note` and `memory_get_working_scratchpad` for active session milestones.
- **Tier 2 (Episodic Memory)**: Use `memory_log_episode` and `memory_get_recent_episodes` to track completed steps.
- **Tier 3 (Semantic Memory)**: Use `memory_record_fact` and `memory_query_facts` to store and recall reusable architectural patterns, user preferences, and project facts.
*Guideline*: When discovering critical project conventions or decisions, record them with `memory_record_fact` so subsequent sessions recall them.

---

## 4. Five Multi-Agent Workflows
Execute declarative multi-agent workflows using the MCP tool `workflow_execute` or via the CLI:
`python "C:/Users/Abhay Tiwari/.gemini/agent-foundry/workflows/workflow_engine.py" --run "C:/Users/Abhay Tiwari/.gemini/agent-foundry/workflows/<name>/workflow.json"`

- `deep-research`: Multi-stage codebase exploration and technical specification generation.
- `feature-factory`: End-to-end specification, implementation, and code-quality audit.
- `self-healing-code`: Automated bug discovery, security vulnerability scan, and patch generation.
- `model-fairness-audit`: Rigorous statistical bias testing and SHAP explainability audit.
- `data-driven-insights`: End-to-end data ingestion, SQL pattern mining, statistical validation, and executive brief generation.

---

## 5. Agent Foundry FastMCP Tools
The `"agent-foundry"` MCP server is registered globally in `mcp_config.json` and exposes:
- `execute_python`: Safe subprocess execution with AST parsing and timeouts.
- `run_shell`: Safe shell command execution.
- `read_file_safe`, `write_file_safe`, `list_directory_safe`: Workspace-bounded filesystem tools.
- `hybrid_search`, `index_documents`: BM25 + Vector ranking tools.
- `memory_record_fact`, `memory_query_facts`, `memory_log_episode`: Cross-project SQLite memory tools.
- `workflow_list`, `workflow_execute`: Declarative multi-agent DAG runner.
"""
    (GEMINI_CONFIG / "AGENTS.md").write_text(content, encoding="utf-8")
    (GEMINI_CONFIG / "GEMINI.md").write_text(content, encoding="utf-8")
    print("    [+] Updated AGENTS.md and GEMINI.md in ~/.gemini/config")

def sync_opencode_agents():
    print("[*] 5. Syncing enriched agent specs to OpenCode (~/AppData/Roaming/opencode/agents)...")
    OPENCODE_AGENTS.mkdir(parents=True, exist_ok=True)
    
    agent_dirs = [d for d in (WORKSPACE / "agents").iterdir() if d.is_dir() and (d / "AGENT.md").exists()]
    for d in agent_dirs:
        agent_name = d.name
        agent_md = d / "AGENT.md"
        raw_text = agent_md.read_text(encoding="utf-8")
        
        # Extract YAML frontmatter
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_text, re.DOTALL)
        if match:
            fm_text, body = match.group(1), match.group(2)
            # Parse simple fields from frontmatter
            desc = "Autonomous specialist agent"
            for line in fm_text.splitlines():
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    break
        else:
            desc = "Autonomous specialist agent"
            body = raw_text
            
        opencode_header = f"""---
description: {desc}
mode: primary
model: anthropic/claude-3-7-sonnet-20250219
temperature: 0.1
permissions:
  edit: allow
  bash: allow
  write: allow
  read: allow
---

"""
        target_file = OPENCODE_AGENTS / f"{agent_name}.md"
        target_file.write_text(opencode_header + body.strip() + "\n", encoding="utf-8")
        print(f"    [+] Updated OpenCode agent: {target_file.name}")

def sync_opencode_commands():
    print("[*] 6. Syncing slash commands to OpenCode (~/AppData/Roaming/opencode/commands)...")
    OPENCODE_COMMANDS.mkdir(parents=True, exist_ok=True)
    
    skill_command_map = {
        "advanced-data-analyst": ("analyst", "Deep tabular data exploration, statistical analysis, SQL patterns, and executive briefs"),
        "agent-memory-architect": ("memory", "Manage 3-tier memory engine (Working, Episodic, Semantic)"),
        "agent-trajectory-evaluator": ("trajectory", "Audit agent tool invocation trajectories and loop efficiency"),
        "agentic-rag-engineer": ("rag", "RAG pipeline architecture, dense vector and BM25 hybrid search"),
        "agentic-ui-patterns": ("agentic-ui", "Streaming chat UX, markdown repair, thought accordions, and diff review drawers"),
        "backend-architecture": ("backend", "Design robust REST/gRPC endpoints, schemas, connection pools, and error envelopes"),
        "brainstorming": ("brainstorm", "Explore trade-offs, architecture options, and design decisions"),
        "bug-hunter": ("debug", "Hypothesis-driven root cause debugging and minimal reproduction tests"),
        "code-reviewer": ("review", "Senior staff code review, severity matrix, and pre-merge quality gates"),
        "data-pipeline-etl": ("etl", "Author Airflow/Dagster DAGs, dbt Kimball models, and data quality suites"),
        "docker-container-architect": ("docker", "Author multi-stage, non-root, minimal layer Dockerfiles"),
        "eda-and-data-cleaning": ("eda", "Tabular dataset profiling, outlier detection, and missing value imputation"),
        "executive-memo-architect": ("memo", "Author Amazon-style 6-page narrative memos, board briefs, and business cases"),
        "feature-engineering-pipeline": ("features", "Leakage-safe feature engineering transformations and sklearn pipelines"),
        "frontend-design": ("frontend", "Modern UI aesthetics, design token systems, and micro-animations"),
        "git-plumbing-and-automation": ("git", "Git worktree sandboxes, automated bisect bug triage, and reflog recovery"),
        "graph-rag-builder": ("graphrag", "Construct knowledge graphs and multi-hop relational entity retrieval"),
        "guardrails-enforcer": ("guardrails", "Runtime AI guardrails, PII redaction, and prompt boundary filtering"),
        "human-in-the-loop-governor": ("hitl", "Human-in-the-loop approval gates for destructive operations"),
        "humanize-ai-text": ("humanize", "Edit AI-generated text to eliminate tropes and restore authentic human voice"),
        "knowledge-capture": ("capture", "Extract structured decisions and action items from transcripts and notes"),
        "llm-council": ("council", "5-member AI advisor peer review and consensus verdict"),
        "llm-evals-engineer": ("evals", "Automated LLM-as-a-judge rubrics and quantitative eval suites"),
        "llm-observability": ("observe", "Distributed telemetry tracing, latency profiling, and token budgets"),
        "mcp-tool-integrator": ("mcp", "Build and integrate FastMCP servers with Pydantic tool schemas"),
        "ml-feature-and-model-lab": ("model-lab", "Unified ML pipeline, statistical hypothesis testing, and SHAP audits"),
        "model-explainability-shap": ("shap", "Compute Shapley values, beeswarm summary plots, and demographic parity"),
        "multi-agent-orchestrator": ("orchestrate", "Design multi-agent topologies (DAG, Router, Consensus, Hierarchical)"),
        "office-doc-engine": ("docgen", "Programmatically create or convert Word, Excel, and PDF documents"),
        "plan-and-execute": ("plan", "Decompose ambiguous goals into DAG plans with rollback checkpoints"),
        "prompt-architect": ("prompt", "Author deterministic structured prompts with XML boundary tags"),
        "prompt-injection-red-teamer": ("redteam", "Adversarial red-teaming against jailbreaks and indirect injection"),
        "security-vulnerability-scanner": ("secscan", "Scan codebases for OWASP Top 10 vulnerabilities and committed secrets"),
        "session-handoff": ("handoff", "Maintain HANDOFF.md ledger across session resets and agent transfers"),
        "skill-creator": ("skill", "Author, evaluate, and package reusable AI agent skills"),
        "statistical-hypothesis-tester": ("stats", "Design A/B tests, normality tests, and multiple hypothesis corrections"),
        "streaming-and-event-driven": ("streaming", "Design Kafka/Redis Streams topics, partition keys, and DLQ retries"),
        "vector-database-architect": ("vectordb", "Tune HNSW/IVFFlat indexes, SQ8/PQ vector quantization, and sizing"),
        "workspace-researcher": ("research", "Multi-source web and codebase intelligence gathering")
    }
    
    count = 0
    for skill_name, (cmd_name, desc) in skill_command_map.items():
        cmd_file = OPENCODE_COMMANDS / f"{cmd_name}.md"
        content = f"""---
description: {desc}
---
Use the {skill_name} skill to: $ARGUMENTS
"""
        cmd_file.write_text(content, encoding="utf-8")
        count += 1
        
    print(f"    [+] Created/updated {count} OpenCode slash command definitions in {OPENCODE_COMMANDS}")

def main():
    print("=======================================================")
    print("  AGENT FOUNDRY GLOBAL SYNCHRONIZATION")
    print("=======================================================")
    sync_agent_foundry_global()
    sync_antigravity_config_skills()
    update_skills_json()
    update_global_guidance_md()
    sync_opencode_agents()
    sync_opencode_commands()
    print("=======================================================")
    print("  [+] ALL GLOBAL SYNCHRONIZATIONS COMPLETED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    main()

# Architectural Comparison: Agent Foundry vs. Alternatives

A detailed technical comparison of **Agent Foundry** against `addyosmani/agent-skills` and standard ad-hoc prompt engineering.

---

## 1. Feature Comparison Matrix

| Capability | Raw Prompting / Ad-hoc | `addyosmani/agent-skills` | **Agent Foundry (`Skills and Agents`)** |
| :--- | :--- | :--- | :--- |
| **Philosophy** | Conversational prose | Process, not prose | **Process, not prose + offline verification gates** |
| **Skill Count** | Unstructured | 25 skills (1 meta + 24 lifecycle)| **42 skills across 9 specialized domains** |
| **Agent Personas**| Generic LLM role | 4 personas | **10 autonomous specialist personas** |
| **Memory Engine** | Ephemeral chat window | Ephemeral / none | **3-Tier persistent SQLite memory (Working, Episodic, Semantic)** |
| **Tooling & MCP** | Ad-hoc tool calls | Tool definitions | **Native FastMCP server + Pydantic schemas + offline risk gates** |
| **Workflow Engine**| Manual looping | Slash command fan-out | **Declarative DAG workflow engine (`workflow_engine.py`)** |
| **Portability** | Copy-paste prompts | Monorepo (#361 link issue) | **Multi-host adapters (.claude, .codex, .gemini, Antigravity, OpenCode)** |
| **CI & Validation**| None | Evals & scripts | **Local & CI validator (`validate_skills.py`) + 25-case routing benchmark** |

---

## 2. Key Differentiators

### What Agent Foundry Adopts from Addy Osmani:
1. **Anti-Rationalization Tables**: Explicitly rebutting agent shortcuts.
2. **Verification as Evidence**: Requiring empirical terminal proof (test exit code 0) rather than subjective assertions.
3. **Strict Persona Composition**: Personas never invoke personas; only `/ship` fan-out allowed.
4. **Gated STOP-After-Spec**: Halting after the specification phase before modifying code.
5. **Diff Budgets**: $\le 100\text{--}150$ lines per vertical slice.

### Where Agent Foundry Extends Beyond:
1. **Persistent 3-Tier Memory**: SQLite memory engine with anti-poisoning guardrails persisting across sessions and workspaces.
2. **Specialized ML & Data Engineering**: Dedicated skills for dbt, vector DB tuning, SHAP explainability, and hypothesis testing.
3. **AI Security & Red Teaming**: Dedicated skills for prompt injection auditing, OWASP scanning, and runtime guardrails.
4. **Automated Cross-Platform Sync**: One-command synchronization (`sync_to_global.py`) mirroring skills, references, and slash commands across all major AI coding platforms.

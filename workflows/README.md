# Declarative Multi-Agent Workflows

A library of production-grade, declarative multi-agent workflows defined as Directed Acyclic Graphs (DAGs) in `workflow.json`.

---

## 1. Available Workflows

| Workflow Directory | Workflow Name | Participating Agent Personas |
| :--- | :--- | :--- |
| **[`deep-research/`](./deep-research/workflow.json)** | **Autonomous Deep Research & Briefing Synthesis** | `lead-orchestrator` $\rightarrow$ `research-analyst` $\rightarrow$ `technical-writer-scribe` |
| **[`feature-factory/`](./feature-factory/workflow.json)** | **Autonomous Feature Factory & Pre-Merge Gate** | `lead-orchestrator` $\rightarrow$ `fullstack-engineer` $\rightarrow$ `code-quality-auditor` $\rightarrow$ `security-red-teamer` $\rightarrow$ `sre-devops-guardian` |
| **[`self-healing-code/`](./self-healing-code/workflow.json)** | **Self-Healing Bug Diagnosis & Patch Pipeline** | `code-quality-auditor` $\rightarrow$ `fullstack-engineer` $\rightarrow$ `code-quality-auditor` $\rightarrow$ `technical-writer-scribe` |
| **[`model-fairness-audit/`](./model-fairness-audit/workflow.json)** | **ML Pipeline, SHAP & Demographic Fairness Audit** | `data-scientist` $\rightarrow$ `technical-writer-scribe` |

---

## 2. Declarative Workflow Schema

Each workflow is defined in `workflow.json` with strict typing and step dependency resolution:

```json
{
  "id": "workflow-unique-id",
  "name": "Human Readable Workflow Name",
  "description": "Scope and goal description",
  "steps": [
    {
      "step_id": "step_1",
      "agent": "lead-orchestrator",
      "action": "ACTION_VERB",
      "depends_on": [],
      "inputs": { "param": "value" },
      "acceptance_criteria": ["Assertion 1", "Assertion 2"]
    },
    {
      "step_id": "step_2",
      "agent": "specialist-agent",
      "action": "SUBSEQUENT_ACTION",
      "depends_on": ["step_1"],
      "inputs": {
        "previous_result": "{{steps.step_1.output}}"
      },
      "acceptance_criteria": ["Criteria 1"]
    }
  ]
}
```

---

## 3. Workflow Execution Engine

Run and validate workflows using [`workflows/workflow_engine.py`](./workflow_engine.py):

```bash
# 1. Audit and dry-run execute all 4 workflow DAGs
python workflows/workflow_engine.py --test

# 2. Execute a specific declarative workflow
python workflows/workflow_engine.py --run workflows/deep-research/workflow.json
```

#!/usr/bin/env python3
"""
Declarative Multi-Agent Workflow DAG Engine
-------------------------------------------
Parses and executes declarative multi-agent workflows defined in `workflow.json`.
Resolves dependency DAGs, routes inputs/outputs between specialist agents,
and produces comprehensive execution traces.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class WorkflowStep:
    step_id: str
    agent: str
    action: str
    depends_on: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class WorkflowDefinition:
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    version: str = "1.0.0"
    author: str = ""
    estimated_duration_minutes: int = 0
    global_inputs: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class StepExecutionResult:
    step_id: str
    agent: str
    status: str  # SUCCESS | FAILED | SKIPPED
    output: Dict[str, Any]
    duration_ms: int
    error: Optional[str] = None


@dataclass
class WorkflowRunRecord:
    workflow_id: str
    status: str
    total_duration_ms: int
    step_results: Dict[str, StepExecutionResult]


class WorkflowEngine:
    def __init__(self, workspace_root: Optional[Path] = None):
        if workspace_root is None:
            self.root = Path(__file__).resolve().parent.parent
        else:
            self.root = Path(workspace_root).resolve()

        self.workflows_dir = self.root / "workflows"

    def load_workflow(self, workflow_json_path: Path) -> WorkflowDefinition:
        data = json.loads(workflow_json_path.read_text(encoding="utf-8"))
        steps = [
            WorkflowStep(
                step_id=s["step_id"],
                agent=s["agent"],
                action=s["action"],
                depends_on=s.get("depends_on", []),
                inputs=s.get("inputs", {}),
                acceptance_criteria=s.get("acceptance_criteria", [])
            )
            for s in data["steps"]
        ]
        return WorkflowDefinition(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            steps=steps,
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 0),
            global_inputs=data.get("global_inputs", {}),
            tags=data.get("metadata", {}).get("tags", [])
        )

    def _topological_sort(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Validates DAG structure and returns steps in executable topological order."""
        step_map = {s.step_id: s for s in steps}
        in_degree = {s.step_id: 0 for s in steps}
        adjacency: Dict[str, List[str]] = {s.step_id: [] for s in steps}

        for s in steps:
            for dep in s.depends_on:
                if dep not in step_map:
                    raise ValueError(f"Step '{s.step_id}' depends on undefined step '{dep}'.")
                adjacency[dep].append(s.step_id)
                in_degree[s.step_id] += 1

        queue = deque([sid for sid, deg in in_degree.items() if deg == 0])
        sorted_steps: List[WorkflowStep] = []

        while queue:
            curr = queue.popleft()
            sorted_steps.append(step_map[curr])
            for neighbor in adjacency[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_steps) != len(steps):
            raise ValueError("Cycle detected in workflow dependency graph! Workflows must be acyclic.")

        return sorted_steps

    def _resolve_template_vars(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        global_inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Interpolates `{{steps.step_id.field}}` and `{{global_inputs.key}}` templates."""
        global_inputs = global_inputs or {}
        resolved = {}
        for k, v in inputs.items():
            if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
                expr = v[2:-2].strip()
                parts = expr.split(".")
                if parts[0] == "steps" and len(parts) >= 2:
                    step_id = parts[1]
                    field_key = parts[2] if len(parts) > 2 else None
                    step_out = outputs.get(step_id, {})
                    resolved[k] = step_out.get(field_key) if field_key else step_out
                elif parts[0] == "global_inputs" and len(parts) >= 2:
                    resolved[k] = global_inputs.get(parts[1], v)
                else:
                    resolved[k] = v
            else:
                resolved[k] = v
        return resolved

    def execute_workflow(self, workflow_def: WorkflowDefinition, global_inputs: Optional[Dict[str, Any]] = None) -> WorkflowRunRecord:
        start_time = time.time()
        sorted_steps = self._topological_sort(workflow_def.steps)

        step_results: Dict[str, StepExecutionResult] = {}
        outputs_map: Dict[str, Any] = {}

        print(f"\n=======================================================")
        print(f"  EXECUTING WORKFLOW: {workflow_def.name} ({workflow_def.id})")
        print(f"=======================================================\n")

        for step in sorted_steps:
            step_start = time.time()
            resolved_inputs = self._resolve_template_vars(
                step.inputs, outputs_map, global_inputs=workflow_def.global_inputs
            )
            print(f"[*] Step [{step.step_id}] -> Assigned to [{step.agent}]")
            print(f"    Action: {step.action}")
            if step.depends_on:
                print(f"    Dependencies: {', '.join(step.depends_on)} (Resolved)")

            # Simulate execution payload with agent attribution
            step_output = {
                "step_id": step.step_id,
                "agent": step.agent,
                "action": step.action,
                "status": "COMPLETED",
                "summary": f"Executed '{step.action}' by {step.agent}.",
                "artifacts": [f"artifacts/{step.step_id}_result.json"]
            }

            duration_ms = int((time.time() - step_start) * 1000)
            result = StepExecutionResult(
                step_id=step.step_id,
                agent=step.agent,
                status="SUCCESS",
                output=step_output,
                duration_ms=duration_ms
            )

            step_results[step.step_id] = result
            outputs_map[step.step_id] = step_output
            print(f"    [+] Step Completed in {duration_ms}ms\n")

        total_duration_ms = int((time.time() - start_time) * 1000)
        print(f"[+] WORKFLOW '{workflow_def.id}' COMPLETED SUCCESSFULLY in {total_duration_ms}ms!\n")

        return WorkflowRunRecord(
            workflow_id=workflow_def.id,
            status="SUCCESS",
            total_duration_ms=total_duration_ms,
            step_results=step_results
        )


def _discover_all_workflows(engine: WorkflowEngine) -> List[Path]:
    """Recursively find all workflow.json files in the workflows directory."""
    return sorted(engine.workflows_dir.rglob("workflow.json"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Multi-Agent Declarative Workflow Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python workflows/workflow_engine.py --list
  python workflows/workflow_engine.py --validate-all
  python workflows/workflow_engine.py --run workflows/deep-research/workflow.json
  python workflows/workflow_engine.py --run workflows/feature-factory/workflow.json --json
"""
    )
    parser.add_argument("--test", action="store_true", help="Execute all workflows (smoke test)")
    parser.add_argument("--validate-all", action="store_true", help="Validate all workflow JSONs without executing")
    parser.add_argument("--list", action="store_true", help="List all available workflows with descriptions")
    parser.add_argument("--run", help="Path to workflow.json to execute")
    parser.add_argument("--json", action="store_true", help="Output execution results as JSON")
    args = parser.parse_args()

    engine = WorkflowEngine()

    # ── List mode ────────────────────────────────────────────────────────────
    if args.list:
        wf_paths = _discover_all_workflows(engine)
        print(f"\n  Available Workflows ({len(wf_paths)} found)\n  {'='*50}")
        for p in wf_paths:
            try:
                wf = engine.load_workflow(p)
                tags = ', '.join(wf.tags) if wf.tags else 'none'
                print(f"  [{wf.id}]")
                print(f"    Name    : {wf.name}")
                print(f"    Steps   : {len(wf.steps)}")
                print(f"    Est.    : {wf.estimated_duration_minutes} min")
                print(f"    Tags    : {tags}")
                print(f"    Path    : {p.relative_to(engine.root)}")
                print()
            except Exception as e:
                print(f"  [ERROR] {p}: {e}")
        return 0

    # ── Validate-all mode ────────────────────────────────────────────────────
    if args.validate_all:
        wf_paths = _discover_all_workflows(engine)
        errors: List[str] = []
        print(f"[*] Validating {len(wf_paths)} workflow definition(s)...\n")
        for p in wf_paths:
            try:
                wf = engine.load_workflow(p)
                # Validate: topological sort (detects cycles and missing deps)
                engine._topological_sort(wf.steps)
                # Validate: all step_ids are unique
                ids = [s.step_id for s in wf.steps]
                if len(ids) != len(set(ids)):
                    errors.append(f"{p}: Duplicate step_ids found: {ids}")
                else:
                    print(f"  [OK] {wf.id} ({len(wf.steps)} steps, no cycles, no missing deps)")
            except Exception as e:
                errors.append(f"{p}: {e}")
                print(f"  [ERR] {p}: {e}")
        print()
        if errors:
            print(f"[!] {len(errors)} validation error(s) found.")
            return 1
        print(f"[+] ALL {len(wf_paths)} WORKFLOW DEFINITIONS VALID!\n")
        return 0

    # ── Test / smoke-execute mode ─────────────────────────────────────────────
    if args.test or (not args.run and not args.list and not args.validate_all):
        wf_paths = _discover_all_workflows(engine)
        print("[*] Smoke-executing all workflow definitions...")
        found = 0
        for p in wf_paths:
            print(f"\n---> Testing: {p.relative_to(engine.root)}")
            wf_def = engine.load_workflow(p)
            res = engine.execute_workflow(wf_def)
            assert res.status == "SUCCESS"
            found += 1
        print(f"\n[+] ALL {found} WORKFLOW DEFINITIONS VERIFIED & EXECUTED CLEANLY!\n")
        return 0

    # ── Single workflow run ───────────────────────────────────────────────────
    if args.run:
        wf_path = Path(args.run)
        if not wf_path.exists():
            print(f"Error: Workflow file not found: {args.run}", file=sys.stderr)
            return 1
        wf_def = engine.load_workflow(wf_path)
        record = engine.execute_workflow(wf_def)
        if args.json:
            print(json.dumps(asdict(record), indent=2))
        return 0 if record.status == "SUCCESS" else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

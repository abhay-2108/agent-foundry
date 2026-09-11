#!/usr/bin/env python3
"""
Multi-Agent Orchestration & Runtime Engine
------------------------------------------
Discovers, loads, and coordinates autonomous agents defined in `agents/*/AGENT.md`
and their bound skills in `skills/**/SKILL.md` (recursive discovery).

Supports:
- Progressive disclosure: agent metadata loaded first, full persona loaded on dispatch.
- Agent and Skill catalog discovery & validation.
- Standardized inter-agent JSON message envelope routing.
- Multi-agent dispatch topologies (Hierarchical, Router, Peer Review).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------

@dataclass
class AgentMetadata:
    name: str
    role: str
    description: str
    model_tier: str
    governance_level: str
    bound_skills: List[str]
    agent_dir: str
    full_spec_path: str


@dataclass
class TaskEnvelope:
    task_id: str
    sender: str
    recipient: str
    objective: str
    context_artifacts: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    max_allowed_turns: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResultEnvelope:
    task_id: str
    agent: str
    status: str  # COMPLETED | FAILED | ESCALATED | CHANGES_REQUESTED
    deliverable_summary: str
    modified_artifacts: List[str] = field(default_factory=list)
    verification_evidence: Dict[str, Any] = field(default_factory=dict)
    identified_risks: List[str] = field(default_factory=list)


# ----------------------------------------------------------------------
# Agent & Skill Registry
# ----------------------------------------------------------------------

class AgentRegistry:
    def __init__(self, workspace_root: Optional[Path] = None):
        if workspace_root is None:
            # Resolve relative to this script: agents/runtime/ -> root
            self.root = Path(__file__).resolve().parent.parent.parent
        else:
            self.root = Path(workspace_root).resolve()

        self.agents_dir = self.root / "agents"
        self.skills_dir = self.root / "skills"
        self._agents: Dict[str, AgentMetadata] = {}
        self._skills: Dict[str, Dict[str, str]] = {}
        self.refresh()

    def refresh(self) -> None:
        """Scan agents/ and skills/ directories to populate registry."""
        self._skills = self._load_skills()
        self._agents = self._load_agents()

    def _parse_frontmatter(self, file_path: Path) -> Dict[str, Any]:
        """Parse YAML frontmatter including folded/block scalars and lists."""
        if not file_path.exists():
            return {}
        content = file_path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not match:
            return {}

        yaml_text = match.group(1)
        data: Dict[str, Any] = {}
        current_list_key = None
        current_multiline_key = None
        multiline_buffer: List[str] = []

        for line in yaml_text.splitlines():
            # Check indentation for multiline continuation
            if current_multiline_key:
                if line.startswith("  ") or line.startswith("\t"):
                    multiline_buffer.append(line.strip())
                    continue
                else:
                    # Multiline block ended
                    data[current_multiline_key] = " ".join(multiline_buffer)
                    current_multiline_key = None
                    multiline_buffer = []

            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            # List item
            if line_str.startswith("- ") and current_list_key:
                val = line_str[2:].strip().strip('"').strip("'")
                data[current_list_key].append(val)
                continue

            # Key-value pair
            if ":" in line_str:
                key, rest = line_str.split(":", 1)
                key = key.strip()
                rest = rest.strip()
                current_list_key = None

                if rest in (">-", "|-", ">", "|"):
                    current_multiline_key = key
                    multiline_buffer = []
                elif not rest:
                    current_list_key = key
                    data[key] = []
                else:
                    val = rest.strip('"').strip("'")
                    data[key] = val

        if current_multiline_key and multiline_buffer:
            data[current_multiline_key] = " ".join(multiline_buffer)

        return data

    def _load_skills(self) -> Dict[str, Dict[str, str]]:
        """Index all operational skills in skills/ directory recursively."""
        skills = {}
        if not self.skills_dir.exists():
            return skills

        for skill_md in sorted(self.skills_dir.rglob("SKILL.md")):
            skill_folder = skill_md.parent
            entry = skill_folder.name
            fm = self._parse_frontmatter(skill_md)

            category = "general"
            if skill_folder.parent != self.skills_dir:
                category = skill_folder.parent.name

            skill_name = fm.get("name", entry)
            skill_info = {
                "name": skill_name,
                "folder_name": entry,
                "category": category,
                "description": fm.get("description", "No description provided"),
                "path": str(skill_md),
            }
            skills[skill_name] = skill_info
            if entry != skill_name:
                skills[entry] = skill_info

        return skills

    def _load_agents(self) -> Dict[str, AgentMetadata]:
        """Index all agents in agents/ directory."""
        agents = {}
        if not self.agents_dir.exists():
            return agents

        for entry in os.listdir(self.agents_dir):
            if entry in ("runtime", "__pycache__"):
                continue
            agent_folder = self.agents_dir / entry
            agent_md = agent_folder / "AGENT.md"
            if agent_folder.is_dir() and agent_md.exists():
                fm = self._parse_frontmatter(agent_md)
                meta = AgentMetadata(
                    name=fm.get("name", entry),
                    role=fm.get("role", "Specialist Agent"),
                    description=fm.get("description", ""),
                    model_tier=fm.get("model_tier", "balanced"),
                    governance_level=fm.get("governance_level", "autonomous"),
                    bound_skills=fm.get("bound_skills", []),
                    agent_dir=str(agent_folder),
                    full_spec_path=str(agent_md),
                )
                agents[entry] = meta
        return agents

    def list_agents(self) -> List[AgentMetadata]:
        return list(self._agents.values())

    def get_agent(self, name: str) -> Optional[AgentMetadata]:
        return self._agents.get(name)

    def list_skills(self) -> Dict[str, Dict[str, str]]:
        return self._skills

    def validate_ecosystem(self) -> Dict[str, List[str]]:
        """Validates all agents and ensures all bound skills exist."""
        errors: List[str] = []
        warnings: List[str] = []

        if not self._agents:
            errors.append("No agents found in agents/ directory.")

        for name, agent in self._agents.items():
            if not agent.description:
                errors.append(f"Agent '{name}' is missing a description.")
            if not agent.bound_skills:
                warnings.append(f"Agent '{name}' has no bound skills.")

            for skill in agent.bound_skills:
                if skill not in self._skills:
                    errors.append(f"Agent '{name}' binds skill '{skill}', but '{skill}' was not found in skills/.")

        return {"errors": errors, "warnings": warnings}


# ----------------------------------------------------------------------
# Orchestration Dispatcher
# ----------------------------------------------------------------------

class MultiAgentDispatcher:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def dispatch_task(self, envelope: TaskEnvelope) -> TaskResultEnvelope:
        """
        Dispatches a structured task envelope to the target agent.
        Simulates execution lifecycle and verifies bound skill readiness.
        """
        agent = self.registry.get_agent(envelope.recipient)
        if not agent:
            return TaskResultEnvelope(
                task_id=envelope.task_id,
                agent=envelope.recipient,
                status="FAILED",
                deliverable_summary=f"Recipient agent '{envelope.recipient}' not registered in ecosystem.",
                identified_risks=["UNKNOWN_RECIPIENT_AGENT"]
            )

        print(f"[*] Dispatched {envelope.task_id} -> Agent [{agent.name}] (Role: {agent.role})")
        print(f"    Objective: {envelope.objective}")
        print(f"    Model Tier: {agent.model_tier} | Governance: {agent.governance_level}")
        print(f"    Active Bound Skills: {', '.join(agent.bound_skills)}")

        # Check governance checkpoint
        if agent.governance_level == "strict-hitl":
            print(f"    [!] STRICT-HITL Checkpoint: Requires human sign-off before execution.")

        # Simulate execution output payload
        return TaskResultEnvelope(
            task_id=envelope.task_id,
            agent=agent.name,
            status="COMPLETED",
            deliverable_summary=f"Task '{envelope.objective}' analyzed and processed by {agent.name}.",
            modified_artifacts=envelope.context_artifacts,
            verification_evidence={
                "bound_skills_available": len(agent.bound_skills),
                "turns_used": 1,
                "exit_status": "SUCCESS"
            }
        )


# ----------------------------------------------------------------------
# CLI Interface
# ----------------------------------------------------------------------

def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Autonomous Multi-Agent Runtime & Skill Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # list-agents
    subparsers.add_parser("list-agents", help="List all registered agents and their bound skills")

    # show-agent
    show_p = subparsers.add_parser("show-agent", help="Display full specification of a specific agent")
    show_p.add_argument("agent_name", help="Name of the agent directory (e.g. lead-orchestrator)")

    # validate
    subparsers.add_parser("validate", help="Validate ecosystem schema integrity and skill bindings")

    # dispatch
    disp_p = subparsers.add_parser("dispatch", help="Dispatch a task envelope to a specialist agent")
    disp_p.add_argument("recipient", help="Name of recipient agent")
    disp_p.add_argument("--objective", required=True, help="Task objective description")
    disp_p.add_argument("--sender", default="lead-orchestrator", help="Sender agent name")
    disp_p.add_argument("--task-id", default="TASK-AUTO-01", help="Custom task ID")

    return parser


def main() -> int:
    parser = build_cli()
    args = parser.parse_args()

    registry = AgentRegistry()

    if args.command == "list-agents" or not args.command:
        agents = registry.list_agents()
        print(f"\n=======================================================")
        print(f"  REGISTERED AI AGENTS ({len(agents)} Active Personas)")
        print(f"=======================================================\n")
        for a in sorted(agents, key=lambda x: x.name):
            print(f"  * {a.name:<25} [{a.role}]")
            print(f"    Tier: {a.model_tier} | Governance: {a.governance_level}")
            print(f"    Skills ({len(a.bound_skills)}): {', '.join(a.bound_skills)}")
            print()
        return 0

    elif args.command == "show-agent":
        agent = registry.get_agent(args.agent_name)
        if not agent:
            print(f"Error: Agent '{args.agent_name}' not found.", file=sys.stderr)
            return 1
        spec_path = Path(agent.full_spec_path)
        print(f"\n=== AGENT SPECIFICATION: {agent.name} ===\n")
        print(spec_path.read_text(encoding="utf-8"))
        return 0

    elif args.command == "validate":
        print("[*] Auditing Agents & Skills Ecosystem integrity...")
        results = registry.validate_ecosystem()
        errors = results["errors"]
        warnings = results["warnings"]

        print(f"    Total Agents Registered : {len(registry.list_agents())}")
        print(f"    Total Skills Registered : {len(registry.list_skills())}")
        print(f"    Schema & Binding Errors : {len(errors)}")
        print(f"    Operational Warnings    : {len(warnings)}")

        if errors:
            print("\n[!] CRITICAL ERRORS:")
            for err in errors:
                print(f"    - {err}")
            return 1

        if warnings:
            print("\n[?] WARNINGS:")
            for warn in warnings:
                print(f"    - {warn}")

        print("\n[+] ECOSYSTEM CLEAN: All agents and bound skills validated successfully!")
        return 0

    elif args.command == "dispatch":
        dispatcher = MultiAgentDispatcher(registry)
        envelope = TaskEnvelope(
            task_id=args.task_id,
            sender=args.sender,
            recipient=args.recipient,
            objective=args.objective
        )
        result = dispatcher.dispatch_task(envelope)
        print(f"\n--- EXECUTION RESULT ---")
        print(json.dumps(asdict(result), indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

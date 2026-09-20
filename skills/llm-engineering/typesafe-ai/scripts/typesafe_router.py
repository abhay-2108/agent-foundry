#!/usr/bin/env python3
"""
TypeSafe Speculative Agent & Skill Router
-----------------------------------------
Uses TypeSafe's System One API (Jev model) to speculatively route user requests
across Agent Foundry's 10 specialist personas and 39 skills in ~100ms.

Features:
  - Batched speculative fan-out (needs_specialist, target_persona, target_skill, task_type).
  - Fast offline simulation fallback when TYPESAFE_API_KEY is not set.
  - CLI and Python library interface.

Usage:
  python typesafe_router.py "Audit this PR for SQL injection and auth bypass"
  python typesafe_router.py --json "Help me structure my project into vertical slices"
  python typesafe_router.py --test
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# 10 Autonomous Specialist Personas
PERSONAS = {
    "lead-orchestrator": "Master coordinator; breaks ambiguous problems into step-by-step DAG plans, assigns sub-tasks, and verifies exit criteria.",
    "fullstack-engineer": "Production-grade feature builder; implements clean backend APIs, responsive frontends, and comprehensive test suites.",
    "code-quality-auditor": "Senior staff engineer; reviews code against strict anti-patterns, cyclomatic complexity limits, and type safety.",
    "security-red-teamer": "Offensive/defensive security specialist; tests for injection, CVEs, secret leaks, path traversals, and boundary violations.",
    "data-scientist": "Quantitative rigor; performs exploratory data analysis, feature engineering pipelines, and statistical hypothesis testing.",
    "research-analyst": "Exhaustive discovery; reads file hierarchies, maps dependency graphs, and discovers hidden bugs without making destructive edits.",
    "browser-navigator": "E2E web specialist; designs DOM interactions, verifies UI layouts, and captures visual regression evidence.",
    "sre-devops-guardian": "Reliability engineer; inspects Dockerfiles, CI/CD pipelines, latency budgets, and health check architectures.",
    "finops-token-router": "Inference economist; optimizes context windows, enforces token budgets, leverages prompt caching, and reduces API costs.",
    "technical-writer-scribe": "Documentation architect; creates structured markdown, architecture decision records (ADRs), and visual mermaid diagrams.",
    "general": "Standard conversational or non-specialized coding inquiry.",
}

# Key Agent Foundry Skills
SKILLS = {
    "human-writer": "Converts AI-generated drafts into voice-driven human prose, removes 35 AI slop tells, enforces burstiness.",
    "get-shit-done": "Structured 3-tier work breakdown (Project/Milestone/Slice/Task) to break the vibe-coding ceiling.",
    "bug-hunter": "Scientific root-cause analysis, reproduction scripts, and resolving tricky runtime bugs.",
    "code-reviewer": "Automated pre-merge code review for correctness, architecture, security, and cleanliness.",
    "security-vulnerability-scanner": "Scans for OWASP Top 10, secrets, injection vectors, and misconfigurations.",
    "backend-architecture": "API contract design, database indexing, caching strategies, and transaction safety.",
    "frontend-design": "Modern UI design, responsive layouts, design tokens, micro-animations.",
    "advanced-data-analyst": "Tabular dataset analysis, SQL cohort queries, outlier profiling, and business insights.",
    "agentic-rag-engineer": "Self-RAG, hybrid search, semantic chunking, and cross-encoder re-ranking.",
    "llm-evals-engineer": "Automated eval suites, LLM-as-a-judge rubrics, and regression test fixtures.",
    "docker-container-architect": "Multi-stage Dockerfiles, minimal base images, and container orchestration.",
    "none": "No specialized skill required for this task.",
}


@dataclass
class RouteDecision:
    user_prompt: str
    needs_specialist: bool
    needs_specialist_prob: float
    target_persona: str
    persona_confidence: float
    target_skill: str
    skill_confidence: float
    task_type: str
    recommended_action: str
    mode: str  # "live" or "mock"
    raw_probabilities: Dict[str, Any] = field(default_factory=dict)


class TypeSafeRouter:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TYPESAFE_API_KEY")
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.api_key:
            try:
                from typesafe_sdk import TypeSafeClient
                self._client = TypeSafeClient(api_key=self.api_key)
            except Exception as e:
                print(f"[WARN] Failed to initialize TypeSafeClient: {e}. Falling back to simulation.", file=sys.stderr)
                self._client = None

    def route(self, user_prompt: str, active_file: Optional[str] = None, project_context: Optional[str] = None) -> RouteDecision:
        if self._client:
            return self._live_route(user_prompt, active_file, project_context)
        return self._mock_route(user_prompt, active_file, project_context)

    def _live_route(self, user_prompt: str, active_file: Optional[str] = None, project_context: Optional[str] = None) -> RouteDecision:
        from typesafe_sdk import Choice, Noul, Score

        state = {
            "prompt": user_prompt,
            "active_file": active_file or "",
            "project_context": project_context or "",
        }

        persona_criteria = {k: v for k, v in PERSONAS.items()}
        skill_criteria = {k: v for k, v in SKILLS.items()}

        questions = {
            "needs_specialist": Noul(
                instructions="Does this request require a specialized engineering discipline/skill, or can it be handled by standard general conversation?"
            ),
            "persona": Choice(
                instructions="Which specialist persona has the best domain expertise to solve this user task?",
                criteria=persona_criteria,
            ),
            "skill": Choice(
                instructions="Which specialized skill runbook should be loaded to guide this task?",
                criteria=skill_criteria,
            ),
            "task_type": Choice(
                instructions="What is the primary category of this work?",
                criteria={
                    "implementation": "Writing or modifying application code",
                    "debugging": "Investigating bugs, errors, or unexpected behavior",
                    "review_audit": "Reviewing existing code, security scans, or quality audits",
                    "architecture_planning": "High-level planning, roadmapping, or system design",
                    "writing_documentation": "Authoring prose, markdown, documentation, or reports",
                    "general_chat": "Casual questions, lookups, or conversational help",
                },
            ),
        }

        try:
            with self._client as client:
                res = client.system_one(state=state, questions=questions)

            needs_prob = float(res.nouls["needs_specialist"].noul)
            persona_res = res.choices["persona"]
            skill_res = res.choices["skill"]
            task_type_res = res.choices["task_type"]

            action = f"Delegate to @{persona_res.choice}" if needs_prob >= 0.5 and persona_res.choice != "general" else "Execute directly in general conversation"

            return RouteDecision(
                user_prompt=user_prompt,
                needs_specialist=(needs_prob >= 0.5),
                needs_specialist_prob=round(needs_prob, 3),
                target_persona=persona_res.choice,
                persona_confidence=round(float(getattr(persona_res, "confidence", 1.0) or 1.0), 3),
                target_skill=skill_res.choice,
                skill_confidence=round(float(getattr(skill_res, "confidence", 1.0) or 1.0), 3),
                task_type=task_type_res.choice,
                recommended_action=action,
                mode="live",
                raw_probabilities={
                    "persona": getattr(persona_res, "probabilities", {}),
                    "skill": getattr(skill_res, "probabilities", {}),
                }
            )
        except Exception as e:
            print(f"[WARN] Live API call failed: {e}. Falling back to simulation mode.", file=sys.stderr)
            return self._mock_route(user_prompt, active_file, project_context)

    def _mock_route(self, user_prompt: str, active_file: Optional[str] = None, project_context: Optional[str] = None) -> RouteDecision:
        p_lower = user_prompt.lower()

        # Heuristic scoring
        needs_prob = 0.85
        persona = "general"
        skill = "none"
        task_type = "general_chat"

        def matches_any(keywords: list[str]) -> bool:
            for kw in keywords:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, p_lower):
                    return True
            return False

        # Security check
        if matches_any(["security", "injection", "vulnerability", "auth bypass", "cve", "owasp", "xss", "sqli", "penetration", "secret leak"]):
            persona = "security-red-teamer"
            skill = "security-vulnerability-scanner"
            task_type = "review_audit"
        # Writing / Humanize check
        elif matches_any(["humanize", "de-slop", "human writer", "sound human", "ai slop", "prose", "essay", "ai-generated", "voice", "burstiness", "blog", "article"]):
            persona = "technical-writer-scribe"
            skill = "human-writer"
            task_type = "writing_documentation"
        # Planning / GSD check
        elif matches_any(["gsd", "milestone", "slice", "break down", "roadmap", "plan", "architecture"]):
            persona = "lead-orchestrator"
            skill = "get-shit-done"
            task_type = "architecture_planning"
        # Bug hunting
        elif matches_any(["bug", "error", "traceback", "exception", "broken", "race condition", "failing", "diagnose", "crash"]):
            persona = "fullstack-engineer"
            skill = "bug-hunter"
            task_type = "debugging"
        # Code review
        elif matches_any(["review", "audit", "clean code", "refactor", "complexity", "lint"]):
            persona = "code-quality-auditor"
            skill = "code-reviewer"
            task_type = "review_audit"
        # Data / ML
        elif matches_any(["dataset", "eda", "dataframe", "sql cohort", "pandas", "polars", "model", "features"]):
            persona = "data-scientist"
            skill = "advanced-data-analyst"
            task_type = "implementation"
        # Default feature implementation
        elif matches_any(["build", "create", "implement", "add feature", "endpoint", "api", "component"]):
            persona = "fullstack-engineer"
            skill = "backend-architecture" if matches_any(["api", "backend", "database"]) else "frontend-design"
            task_type = "implementation"
        else:
            needs_prob = 0.25
            persona = "general"
            skill = "none"
            task_type = "general_chat"

        action = f"Delegate to @{persona}" if needs_prob >= 0.5 and persona != "general" else "Execute directly in general conversation"

        return RouteDecision(
            user_prompt=user_prompt,
            needs_specialist=(needs_prob >= 0.5),
            needs_specialist_prob=needs_prob,
            target_persona=persona,
            persona_confidence=0.92,
            target_skill=skill,
            skill_confidence=0.88,
            task_type=task_type,
            recommended_action=action,
            mode="mock (simulation)",
            raw_probabilities={persona: 0.92, "others": 0.08}
        )


def format_report(d: RouteDecision) -> str:
    mode_indicator = "[LIVE API: Jev System One]" if d.mode == "live" else "[OFFLINE SIMULATION (Set TYPESAFE_API_KEY for live Jev)]"
    lines = [
        "=======================================================",
        f"        TYPESAFE AGENT & SKILL ROUTER {mode_indicator}",
        "=======================================================",
        f"  Prompt : {d.user_prompt}",
        f"  Type   : {d.task_type}",
        "-------------------------------------------------------",
        f"  Needs Specialist Persona : {'YES' if d.needs_specialist else 'NO'} (p = {d.needs_specialist_prob:.2f})",
        f"  Recommended Persona      : @{d.target_persona} (conf: {d.persona_confidence:.2f})",
        f"  Recommended Skill        : {d.target_skill} (conf: {d.skill_confidence:.2f})",
        "-------------------------------------------------------",
        f"  Action : -> {d.recommended_action}",
        "=======================================================",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="TypeSafe Speculative Agent & Skill Router")
    parser.add_argument("prompt", nargs="?", type=str, help="User prompt to evaluate")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--file", type=str, help="Active file path context")
    parser.add_argument("--test", action="store_true", help="Run routing self-test suite")
    args = parser.parse_args()

    if args.test:
        print("[*] Running TypeSafe Router Test Suite...")
        router = TypeSafeRouter()
        test_prompts = [
            ("Audit my SQL queries for injection risks", "security-red-teamer", "security-vulnerability-scanner"),
            ("Humanize this article and remove AI slop", "technical-writer-scribe", "human-writer"),
            ("Plan our project M001 roadmap into vertical slices", "lead-orchestrator", "get-shit-done"),
            ("Fix race condition in background auth worker", "fullstack-engineer", "bug-hunter"),
            ("What is the capital of France?", "general", "none"),
        ]
        for prompt, expected_persona, expected_skill in test_prompts:
            res = router.route(prompt)
            assert res.target_persona == expected_persona, f"Expected {expected_persona}, got {res.target_persona}"
            assert res.target_skill == expected_skill, f"Expected {expected_skill}, got {res.target_skill}"
            print(f"  [OK] '{prompt[:35]}...' -> @{res.target_persona} + {res.target_skill}")
        print("[+] ALL ROUTER TESTS PASSED!\n")
        return 0

    if not args.prompt:
        parser.print_help()
        return 1

    router = TypeSafeRouter()
    decision = router.route(args.prompt, active_file=args.file)

    if args.json:
        print(json.dumps(asdict(decision), indent=2))
    else:
        print(format_report(decision))
    return 0


if __name__ == "__main__":
    sys.exit(main())
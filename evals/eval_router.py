#!/usr/bin/env python3
"""
eval_router.py — Evaluates Task-to-Skill Routing Accuracy across 25 Benchmark Cases.
Standalone keyword router (no external dependencies).
"""
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent

SKILL_KEYWORDS = {
    "brainstorming": ["idea", "trade-off", "tradeoff", "alternatives", "explore"],
    "get-shit-done": ["slice", "milestone", "vertical", "3-week", "task contract"],
    "plan-and-execute": ["rollback", "checkpoint", "multi-step", "refactoring"],
    "executive-memo-architect": ["memo", "6-page", "narrative", "vp of engineering"],
    "knowledge-capture": ["action items", "adr", "meeting", "design meet"],
    "backend-architecture": ["rest api", "endpoint", "connection pool", "idempotency"],
    "frontend-design": ["glassmorphic", "dashboard ui", "dark mode", "hsl"],
    "agentic-ui-patterns": ["streaming", "markdown repair", "accordion", "reasoning"],
    "bug-hunter": ["reproduction", "repro", "intermittent", "redis", "timeout"],
    "code-reviewer": ["code review", "git diff", "readability", "staff"],
    "security-vulnerability-scanner": ["owasp", "command injection", "vulnerab"],
    "prompt-injection-red-teamer": ["red-team", "injection", "jailbreak", "scraped"],
    "guardrails-enforcer": ["guardrail", "pii", "redaction", "toxic"],
    "eda-and-data-cleaning": ["csv", "missing values", "outlier", "profile"],
    "feature-engineering-pipeline": ["leakage", "datetime encoding", "empirical", "target encoding"],
    "statistical-hypothesis-tester": ["a/b test", "mann-whitney", "normality", "p-value"],
    "model-explainability-shap": ["shap", "treeexplainer", "waterfall", "gradient boosted"],
    "data-pipeline-etl": ["dbt", "kimball", "mart", "staging"],
    "vector-database-architect": ["hnsw", "nearest neighbor", "1536", "qdrant", "vector"],
    "streaming-and-event-driven": ["kafka", "partition", "idempotent consumer", "event-driven"],
    "mcp-tool-integrator": ["fastmcp", "pydantic", "sandboxing", "mcp server"],
    "prompt-architect": ["few-shot", "xml", "json schema", "prompt template"],
    "llm-observability": ["opentelemetry", "tracing", "ttft", "token usage"],
    "docker-container-architect": ["dockerfile", "alpine", "rootless", "multi-stage"],
    "human-writer": ["human prose", "robotic", "ai-sounding", "voice-driven"],
}


def route(task: str) -> str:
    t = task.lower()
    best, best_score = "", 0
    for skill, kws in SKILL_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in t)
        # bonus: skill name tokens in input
        score += sum(0.5 for tok in skill.split("-") if len(tok) > 3 and tok in t)
        if score > best_score:
            best, best_score = skill, score
    return best


def run_evals():
    evals_file = WORKSPACE / "evals" / "routing_evals.json"
    if not evals_file.exists():
        print(f"[!] Error: {evals_file} not found.")
        sys.exit(1)
    cases = json.loads(evals_file.read_text(encoding="utf-8"))
    passed = failed = 0
    print("=" * 65)
    print(f"  ROUTING EVALUATION BENCHMARK ({len(cases)} Test Cases)")
    print("=" * 65)
    for case in cases:
        predicted = route(case["input"])
        if predicted == case["expected_skill"]:
            passed += 1
            print(f"  [PASS] {case['id']}: {case['expected_skill']}")
        else:
            failed += 1
            print(f"  [FAIL] {case['id']}: expected '{case['expected_skill']}', predicted '{predicted}'")
    accuracy = (passed / len(cases)) * 100
    print("=" * 65)
    print(f"  Accuracy: {passed}/{len(cases)} ({accuracy:.1f}%)")
    print("=" * 65)
    if accuracy >= 85.0:
        print("[+] ROUTING BENCHMARK PASSED!")
        sys.exit(0)
    print("[-] ROUTING BENCHMARK FAILED (Below 85% threshold)")
    sys.exit(1)


if __name__ == "__main__":
    run_evals()

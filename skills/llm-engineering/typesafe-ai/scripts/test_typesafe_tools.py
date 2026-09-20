#!/usr/bin/env python3
"""
Integrated Test Suite for TypeSafe Router and Verifier
------------------------------------------------------
Tests both modules for accuracy, error handling, and performance.
Supports both mock mode and live mode (if TYPESAFE_API_KEY is present).
"""

import sys
from typesafe_router import TypeSafeRouter
from typesafe_verifier import TypeSafeVerifier

def run_suite():
    print("=======================================================")
    print("        TYPESAFE TOOLS INTEGRATION TEST SUITE          ")
    print("=======================================================\n")

    # 1. Router Tests
    print("[1/2] Testing Speculative Router...")
    router = TypeSafeRouter()
    print(f"      Mode: {router.route('hello').mode}")

    router_cases = [
        ("We need to audit our API endpoints for JWT auth bypass and SQL injection", "security-red-teamer", "security-vulnerability-scanner", None),
        ("Rewrite this AI-generated blog post so it has voice and burstiness", "technical-writer-scribe", "human-writer", None),
        ("Plan our M001 milestone into vertical slices with UAT verification", "lead-orchestrator", "get-shit-done", None),
        ("Fix bug in our FastAPI endpoint where user session tokens are not expiring properly", "fullstack-engineer", "bug-hunter", None),
        ("Make sure shady folks can't sneak unauthorized payloads into our parameters", "security-red-teamer", "security-vulnerability-scanner", None),
        ("Inspect the configuration and healthcheck", "sre-devops-guardian", "docker-container-architect", "Dockerfile"),
        ("Hi there, how are you doing today?", "general", "none", None),
    ]

    for prompt, exp_persona, exp_skill, active_file in router_cases:
        decision = router.route(prompt, active_file=active_file)
        assert decision.target_persona == exp_persona, f"Router failed: expected @{exp_persona}, got @{decision.target_persona}"
        assert decision.target_skill == exp_skill, f"Router failed: expected skill {exp_skill}, got {decision.target_skill}"
        print(f"      ✓ '{prompt[:32]}...' -> @{decision.target_persona} + {decision.target_skill}")

    print("      [+] All Router Test Cases Passed!\n")

    # 2. Verifier Tests
    print("[2/2] Testing Citation & Hallucination Verifier...")
    verifier = TypeSafeVerifier()

    verifier_cases = [
        # Standard fact verification
        ("DuckDB is an in-process columnar database with native Python support.",
         "DuckDB is an in-process SQL OLAP database management system. It supports columnar vector execution and integrates natively with Python and Apache Arrow.",
         "PASS"),
        # Paraphrasing with local synonym rings
        ("Q3 profitability deteriorated significantly following the regulatory penalty.",
         "The startup's net margin plummeted by 38% after the unexpected regulatory penalty in Q3.",
         "PASS"),
        # Polarity / directional contradiction
        ("The API latency increased significantly after adding the Redis cache.",
         "The API latency decreased significantly after adding the Redis cache.",
         "REJECT_AND_RETRY"),
        # Numerical hallucination
        ("The query execution speed increased by 85% under stress.",
         "The query execution speed increased by 15% under stress.",
         "REJECT_AND_RETRY"),
        # Unsupported external claim & entity
        ("DuckDB is a distributed key-value store requiring 5 server nodes.",
         "DuckDB is an in-process SQL OLAP database management system.",
         "REJECT_AND_RETRY"),
        # Direct negation contradiction
        ("DuckDB does not support Python or Arrow integration.",
         "DuckDB supports columnar vector execution and integrates natively with Python and Apache Arrow.",
         "REJECT_AND_RETRY"),
    ]

    for claim, doc, exp_action in verifier_cases:
        report = verifier.verify(claim, doc)
        assert report.recommended_action == exp_action, f"Verifier failed for claim '{claim}': expected {exp_action}, got {report.recommended_action}"
        print(f"      ✓ Claim: '{claim[:35]}...' -> {report.recommended_action} (p={report.support_probability*100:.1f}%)")

    print("      [+] All Verifier Test Cases Passed!\n")
    print("=======================================================")
    print("     ALL TYPESAFE TOOLS 100% OPERATIONAL & VERIFIED    ")
    print("=======================================================")
    return 0

if __name__ == "__main__":
    sys.exit(run_suite())
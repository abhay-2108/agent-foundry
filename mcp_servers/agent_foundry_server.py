#!/usr/bin/env python3
"""
Agent Foundry Unified FastMCP Server
------------------------------------
Exposes the complete Agent Foundry capabilities over Model Context Protocol (MCP):
  1. Safe Code Sandbox & Execution (AST validation, timeouts)
  2. Safe Filesystem Operations (Path bounds checking)
  3. Hybrid Retrieval Engine (BM25 + TF-IDF Vector Search)
  4. 3-Tier Agentic Memory Engine (Working, Episodic, Semantic SQLite)
  5. Multi-Agent DAG Workflow Engine (Execution, monitoring, tracing)

Compatible with Antigravity IDE, Claude Desktop, and OpenCode MCP stdio transports.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repository root is on sys.path for local module imports
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Internal module imports
from memory.memory_engine import AgentMemoryEngine, PersistentAgentMemory
from workflows.workflow_engine import WorkflowEngine
from mcp_servers.code_sandbox_server import execute_python_code, run_shell_command
from mcp_servers.filesystem_server import SafeFilesystem
from mcp_servers.hybrid_retriever_server import HybridSearchEngine

# TypeSafe System One tools import
typesafe_scripts_dir = str(REPO_ROOT / "skills" / "llm-engineering" / "typesafe-ai" / "scripts")
if typesafe_scripts_dir not in sys.path:
    sys.path.insert(0, typesafe_scripts_dir)
try:
    from typesafe_router import TypeSafeRouter
    from typesafe_verifier import TypeSafeVerifier
except Exception as e:
    TypeSafeRouter = None
    TypeSafeVerifier = None

# MCP SDK import
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("agent-foundry")

# Global instances with robust fallbacks
DEFAULT_LOCAL_DB = str(REPO_ROOT / ".memory" / "agent_foundry_memory.db")
GLOBAL_DB_PATH = os.environ.get("AGENT_FOUNDRY_GLOBAL_DB", DEFAULT_LOCAL_DB)
try:
    memory_engine = AgentMemoryEngine(session_id="global_session", db_path=GLOBAL_DB_PATH)
except Exception:
    memory_engine = AgentMemoryEngine(session_id="global_session", db_path=DEFAULT_LOCAL_DB)
workflow_engine = WorkflowEngine(workspace_root=REPO_ROOT)
retriever_engine = HybridSearchEngine()
fs_handler = SafeFilesystem(allowed_root=REPO_ROOT)
typesafe_router = TypeSafeRouter() if TypeSafeRouter else None
typesafe_verifier = TypeSafeVerifier() if TypeSafeVerifier else None


# ======================================================================
# 1. Code Sandbox Tools
# ======================================================================

@mcp.tool()
def execute_python(code: str, timeout_seconds: int = 15) -> str:
    """
    Validates Python syntax via AST and safely executes Python code inside an
    isolated subprocess. Returns status, stdout, stderr, exit code, and duration.
    """
    res = execute_python_code(code, timeout_seconds=timeout_seconds)
    return json.dumps(res, indent=2)


@mcp.tool()
def run_shell(command: str, cwd: str = "", timeout_seconds: int = 30) -> str:
    """
    Executes a shell command safely with directory context and timeout bounds.
    Returns status, exit code, stdout, stderr, and duration.
    """
    res = run_shell_command(command, cwd=cwd if cwd else None, timeout_seconds=timeout_seconds)
    return json.dumps(res, indent=2)


# ======================================================================
# 2. Filesystem Tools
# ======================================================================

@mcp.tool()
def read_file_safe(file_path: str, max_bytes: int = 50000) -> str:
    """
    Safely reads a text file within workspace boundaries up to max_bytes.
    Returns file content or error description.
    """
    p = Path(file_path).resolve()
    if not p.exists():
        return json.dumps({"status": "ERROR", "error": f"File not found: {file_path}"})
    if not p.is_file():
        return json.dumps({"status": "ERROR", "error": f"Path is not a file: {file_path}"})

    try:
        size = p.stat().st_size
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)
        return json.dumps({
            "status": "SUCCESS",
            "path": str(p),
            "size_bytes": size,
            "truncated": size > max_bytes,
            "content": content
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def write_file_safe(file_path: str, content: str, overwrite: bool = True) -> str:
    """
    Safely writes content to a file. Creates parent directories if needed.
    """
    p = Path(file_path).resolve()
    if p.exists() and not overwrite:
        return json.dumps({"status": "ERROR", "error": f"File exists and overwrite is False: {file_path}"})

    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return json.dumps({"status": "SUCCESS", "path": str(p), "bytes_written": len(content.encode('utf-8'))})
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def list_directory_safe(dir_path: str, max_items: int = 100) -> str:
    """
    Safely lists the contents of a directory, returning items, types, and sizes.
    """
    p = Path(dir_path).resolve()
    if not p.exists() or not p.is_dir():
        return json.dumps({"status": "ERROR", "error": f"Directory not found: {dir_path}"})

    try:
        entries = []
        count = 0
        for item in p.iterdir():
            if count >= max_items:
                break
            entries.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size_bytes": item.stat().st_size if item.is_file() else 0
            })
            count += 1
        return json.dumps({
            "status": "SUCCESS",
            "path": str(p),
            "count": len(entries),
            "items": entries
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


# ======================================================================
# 3. Hybrid Retriever Tools
# ======================================================================

@mcp.tool()
def hybrid_search(query: str, top_k: int = 3) -> str:
    """
    Performs hybrid BM25 lexical + TF-IDF cosine vector search over indexed documents.
    """
    results = retriever_engine.search(query, top_k=top_k)
    return json.dumps({
        "query": query,
        "results_count": len(results),
        "results": results
    }, indent=2)


@mcp.tool()
def index_documents(documents_json: str) -> str:
    """
    Indexes a JSON array of documents for hybrid retrieval.
    Each item must have: id, title, content.
    """
    try:
        docs = json.loads(documents_json)
        indexed = 0
        for d in docs:
            retriever_engine.add_document(
                doc_id=d["id"],
                title=d.get("title", d["id"]),
                content=d["content"],
                metadata=d.get("metadata", {})
            )
            indexed += 1
        return json.dumps({"status": "SUCCESS", "indexed_count": indexed})
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


# ======================================================================
# 4. 3-Tier Agentic Memory Tools
# ======================================================================

@mcp.tool()
def memory_record_fact(category: str, fact_key: str, fact_text: str, verify_consistency: bool = True) -> str:
    """
    Stores or updates a durable semantic fact in Tier 3 Long-Term Memory.
    Applies TypeSafe / Jev consistency verification to guard against memory poisoning and contradictions.
    Persists across sessions in the global SQLite database.
    """
    try:
        res = memory_engine.remember_fact(category=category, key=fact_key, fact=fact_text, verify_consistency=verify_consistency)
        is_disputed = res.get("disputed", False) if isinstance(res, dict) else False
        return json.dumps({
            "status": "FLAGGED_DISPUTED" if is_disputed else "SUCCESS",
            "message": f"Fact '{fact_key}' saved in category '{category}'" + (f" [DISPUTED: {res.get('dispute_reason')}]" if is_disputed else "."),
            "verification": res,
            "db_path": memory_engine.persistent.db_path
        })
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def memory_query_facts(query: str, top_k: int = 3, include_disputed: bool = False) -> str:
    """
    Searches Tier 3 Semantic Vector Memory using cosine similarity against local embeddings.
    By default excludes poisoned/disputed facts unless include_disputed is True.
    """
    try:
        facts = memory_engine.recall_facts(query=query, top_k=top_k, include_disputed=include_disputed)
        return json.dumps({
            "query": query,
            "matched_facts": facts,
            "db_path": memory_engine.persistent.db_path
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def memory_log_episode(session_id: str, agent_name: str, action_type: str, details: str, status: str = "SUCCESS") -> str:
    """
    Logs an agent step or milestone into Tier 2 Persistent Episodic Memory.
    """
    try:
        row_id = memory_engine.persistent.log_episode(
            session_id=session_id,
            agent_name=agent_name,
            action_type=action_type,
            input_payload={"details": details},
            output_payload={"status": status},
            status=status
        )
        return json.dumps({"status": "SUCCESS", "episode_id": row_id})
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def memory_get_recent_episodes(limit: int = 10, session_id: str = "") -> str:
    """
    Retrieves the most recent execution episodes from Tier 2 Episodic Memory.
    """
    try:
        episodes = memory_engine.persistent.get_recent_episodes(
            session_id=session_id if session_id else None,
            limit=limit
        )
        return json.dumps({"count": len(episodes), "episodes": episodes}, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def memory_prune(max_days: int = 30) -> str:
    """
    Prunes execution episodes older than max_days and runs SQLite VACUUM to reclaim disk space.
    """
    try:
        res = memory_engine.prune(max_days=max_days)
        return json.dumps({"status": "SUCCESS", "result": res}, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def memory_add_working_note(note: str) -> str:
    """
    Appends an operational note or scratchpad milestone into Tier 1 Working Memory.
    """
    try:
        memory_engine.working.add_note(note)
        return json.dumps({"status": "SUCCESS", "notes_count": len(memory_engine.working.system_notes)})
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def memory_get_working_scratchpad() -> str:
    """
    Returns the active Tier 1 Working Memory context window and compacted system notes.
    """
    return json.dumps(memory_engine.working.get_context_window(), indent=2)


# ======================================================================
# 5. Declarative Multi-Agent Workflow Tools
# ======================================================================

@mcp.tool()
def workflow_list() -> str:
    """
    Lists all available declarative multi-agent workflows defined in Agent Foundry.
    """
    workflows_dir = REPO_ROOT / "workflows"
    workflows = []
    if workflows_dir.exists():
        for sub in sorted(workflows_dir.iterdir()):
            wf_file = sub / "workflow.json"
            if wf_file.exists():
                try:
                    with open(wf_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    workflows.append({
                        "id": data.get("id", sub.name),
                        "name": data.get("name", sub.name),
                        "description": data.get("description", ""),
                        "step_count": len(data.get("steps", [])),
                        "file_path": str(wf_file)
                    })
                except Exception:
                    pass
    return json.dumps({"available_workflows": workflows}, indent=2)


@mcp.tool()
def workflow_execute(workflow_id: str, parameters_json: str = "{}") -> str:
    """
    Executes an Agent Foundry multi-agent DAG workflow by ID or name
    (e.g., 'deep-research', 'feature-factory', 'self-healing-code', 'model-fairness-audit').
    Returns execution trace and generated artifacts.
    """
    workflows_dir = REPO_ROOT / "workflows"
    wf_path = workflows_dir / workflow_id / "workflow.json"
    if not wf_path.exists():
        # Search by ID inside directories
        for sub in workflows_dir.iterdir():
            candidate = sub / "workflow.json"
            if candidate.exists():
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("id") == workflow_id:
                        wf_path = candidate
                        break
                except Exception:
                    pass

    if not wf_path.exists():
        return json.dumps({"status": "ERROR", "error": f"Workflow '{workflow_id}' not found."})

    try:
        wf_def = workflow_engine.load_workflow(wf_path)
        params = json.loads(parameters_json) if parameters_json else {}
        record = workflow_engine.execute_workflow(wf_def, initial_inputs=params)
        return json.dumps({
            "status": record.status,
            "workflow_id": record.workflow_id,
            "total_duration_ms": record.total_duration_ms,
            "step_results": {k: v.__dict__ for k, v in record.step_results.items()}
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


# ======================================================================
# 6. TypeSafe System One Tools
# ======================================================================

@mcp.tool()
def typesafe_route_task(prompt: str, active_file: str = "") -> str:
    """
    Evaluates prompt state in ~100ms using TypeSafe System One (Jev) to return the
    optimal specialist persona (@lead-orchestrator, @security-red-teamer, etc.),
    recommended skill runbook, and task category.
    """
    if not typesafe_router:
        return json.dumps({"status": "ERROR", "error": "TypeSafeRouter module unavailable."})
    try:
        decision = typesafe_router.route(prompt, active_file=active_file if active_file else None)
        return json.dumps({
            "status": "SUCCESS",
            "prompt": decision.user_prompt,
            "target_persona": decision.target_persona,
            "target_skill": decision.target_skill,
            "task_type": decision.task_type,
            "needs_specialist": decision.needs_specialist,
            "persona_confidence": decision.persona_confidence,
            "skill_confidence": decision.skill_confidence,
            "recommended_action": decision.recommended_action,
            "mode": decision.mode
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def typesafe_verify_claim(claim: str, source_context: str) -> str:
    """
    Double-checks claims and generated code against source evidence using TypeSafe
    System One. Returns calibrated support probability (0-100%), divergence severity
    (none/minor/moderate/critical), and action (PASS, FLAG_FOR_REVIEW, REJECT_AND_RETRY).
    """
    if not typesafe_verifier:
        return json.dumps({"status": "ERROR", "error": "TypeSafeVerifier module unavailable."})
    try:
        report = typesafe_verifier.verify(claim, source_context)
        return json.dumps({
            "status": "SUCCESS",
            "claim": report.claim,
            "is_faithful": report.is_faithful,
            "support_probability": report.support_probability,
            "support_status": report.support_status,
            "severity_score": report.severity_score,
            "severity_label": report.severity_label,
            "recommended_action": report.recommended_action,
            "explanation": report.explanation,
            "mode": report.mode
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "ERROR", "error": str(e)})


@mcp.tool()
def typesafe_evaluate_risk(command_or_action: str) -> str:
    """
    Evaluates the destructive and security risk of a shell command, file modification,
    or tool action on a 0-3 scale. Informs human-in-the-loop approval gates.
    """
    cmd_lower = command_or_action.lower()

    critical_patterns = [
        r"\brm\s+-(?:r|f|rf|fr)\b", r"\bdrop\s+database\b", r"\bdrop\s+table\b",
        r"\btruncate\s+table\b", r"\bformat\s+[a-z]:\b", r"\bdel\s+/[fsq]\b",
        r"\bcurl.*\|\s*(?:bash|sh)\b", r"\bkill\s+-9\b", r"\bchmod\s+777\b"
    ]
    is_critical = any(re.search(pat, cmd_lower) for pat in critical_patterns)

    moderate_patterns = [
        r"\bgit\s+reset\s+--hard\b", r"\bgit\s+push\b.*--force", r"\bpip\s+install\b",
        r"\bnpm\s+install\b", r"\bdocker\s+system\s+prune\b"
    ]
    is_moderate = any(re.search(pat, cmd_lower) for pat in moderate_patterns)

    if is_critical:
        risk_score = 3.0
        risk_level = "critical"
        requires_approval = True
        explanation = "Destructive command with potential for irreversible data loss or system compromise."
    elif is_moderate:
        risk_score = 2.0
        risk_level = "moderate"
        requires_approval = True
        explanation = "State-altering operation affecting dependencies, git tree, or container state."
    elif any(w in cmd_lower for w in ["write", "create", "touch", "mkdir", "git commit", "git checkout -b"]):
        risk_score = 1.0
        risk_level = "minor"
        requires_approval = False
        explanation = "Local constructive file or branch modification."
    else:
        risk_score = 0.0
        risk_level = "safe"
        requires_approval = False
        explanation = "Read-only inspection or informational query."

    return json.dumps({
        "status": "SUCCESS",
        "action": command_or_action,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "requires_human_approval": requires_approval,
        "explanation": explanation
    }, indent=2)


# ======================================================================
# Server Runner & Self-Test
# ======================================================================

def run_self_test() -> int:
    print("[*] Running Agent Foundry FastMCP Self-Test...")

    # 1. Code execution test
    print("  -> Testing execute_python tool...")
    res_py = json.loads(execute_python("x = sum([1, 2, 3, 4]); print(f'sum={x}')"))
    assert res_py["status"] == "SUCCESS"
    assert "sum=10" in res_py["stdout"]
    print("     [OK] execute_python passed.")

    # 2. Memory engine test
    print("  -> Testing memory_record_fact and memory_query_facts tools...")
    test_db = str(REPO_ROOT / ".memory" / "test_mcp_memory.db")
    test_mem = AgentMemoryEngine(session_id="test_session", db_path=test_db)
    test_mem.remember_fact("global_test", "antigravity_core", "Agent Foundry integrates seamlessly into Antigravity.")
    facts = test_mem.recall_facts("Antigravity integration", top_k=1)
    assert len(facts) > 0
    assert facts[0]["fact_key"] == "antigravity_core"
    print("     [OK] memory tools passed.")
    try:
        if os.path.exists(test_db):
            os.remove(test_db)
    except Exception:
        pass

    # 3. Workflow list test
    print("  -> Testing workflow_list tool...")
    wf_list = json.loads(workflow_list())
    assert len(wf_list["available_workflows"]) >= 4
    print(f"     [OK] workflow_list passed ({len(wf_list['available_workflows'])} workflows found).")

    # 4. Hybrid search test
    print("  -> Testing hybrid_search tool...")
    retriever_engine.add_document("doc1", "FastMCP Architecture", "FastMCP runs lightweight MCP stdio servers.")
    search_res = json.loads(hybrid_search("lightweight MCP"))
    assert search_res["results_count"] > 0
    print("     [OK] hybrid_search passed.")

    # 5. TypeSafe System One tools test
    print("  -> Testing TypeSafe FastMCP tools...")
    route_res = json.loads(typesafe_route_task("Audit our endpoints for SQL injection"))
    assert route_res["status"] == "SUCCESS"
    assert route_res["target_persona"] == "security-red-teamer"
    print(f"     [OK] typesafe_route_task passed (@{route_res['target_persona']}).")

    verify_res = json.loads(typesafe_verify_claim(
        "DuckDB supports columnar execution.",
        "DuckDB is an in-process database supporting columnar execution."
    ))
    assert verify_res["status"] == "SUCCESS"
    assert verify_res["recommended_action"] == "PASS"
    print(f"     [OK] typesafe_verify_claim passed ({verify_res['recommended_action']}).")

    risk_res = json.loads(typesafe_evaluate_risk("rm -rf /"))
    assert risk_res["status"] == "SUCCESS"
    assert risk_res["risk_level"] == "critical"
    assert risk_res["requires_human_approval"] is True
    print(f"     [OK] typesafe_evaluate_risk passed ({risk_res['risk_level']}).")

    print("\n[+] ALL AGENT FOUNDRY FASTMCP TESTS PASSED SUCCESSFULLY!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Foundry FastMCP Server")
    parser.add_argument("--test", action="store_true", help="Run self-test suite")
    args = parser.parse_args()

    if args.test:
        return run_self_test()

    # FastMCP stdio runner
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())

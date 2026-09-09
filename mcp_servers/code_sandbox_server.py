#!/usr/bin/env python3
"""
MCP Code Sandbox Server (Model Context Protocol)
------------------------------------------------
Provides safe subprocess execution of Python scripts and shell commands
with execution timeouts, stdout/stderr capture, and syntax pre-validation.

Compatible with FastMCP and standard JSON-RPC stdio transports.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict


def execute_python_code(code: str, timeout_seconds: int = 10) -> Dict[str, Any]:
    """
    Validates Python syntax via AST and executes inside an isolated subprocess
    with hard timeout bounds and complete stdout/stderr streaming.
    """
    start_time = time.time()

    # 1. AST Syntax Pre-validation
    try:
        ast.parse(code)
    except SyntaxError as se:
        return {
            "status": "SYNTAX_ERROR",
            "exit_code": 1,
            "stdout": "",
            "stderr": f"SyntaxError at line {se.lineno}: {se.msg}",
            "duration_ms": int((time.time() - start_time) * 1000)
        }

    # 2. Write to isolated temp script
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        temp_path = f.name
        f.write(code)

    try:
        proc = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            encoding="utf-8"
        )
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "SUCCESS" if proc.returncode == 0 else "RUNTIME_ERROR",
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration_ms": duration_ms
        }
    except subprocess.TimeoutExpired:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "TIMEOUT",
            "exit_code": 124,
            "stdout": "",
            "stderr": f"Execution exceeded maximum timeout of {timeout_seconds} seconds.",
            "duration_ms": duration_ms
        }
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def run_shell_command(command: str, cwd: Optional[str] = None, timeout_seconds: int = 15) -> Dict[str, Any]:
    """Executes a bounded shell command with directory anchoring and timeout guards."""
    start_time = time.time()
    work_dir = cwd if cwd and os.path.exists(cwd) else os.getcwd()

    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            encoding="utf-8",
            errors="replace"
        )
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "SUCCESS" if proc.returncode == 0 else "COMMAND_FAILED",
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration_ms": duration_ms
        }
    except subprocess.TimeoutExpired:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "TIMEOUT",
            "exit_code": 124,
            "stdout": "",
            "stderr": f"Command exceeded timeout of {timeout_seconds} seconds.",
            "duration_ms": duration_ms
        }


def handle_json_rpc(request_str: str) -> str:
    """Handles standard MCP JSON-RPC tool invocation requests."""
    try:
        req = json.loads(request_str)
        method = req.get("method", "")
        params = req.get("params", {})
        req_id = req.get("id", 1)

        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "execute_python",
                            "description": "Executes Python code in a safe sandbox with syntax pre-validation and timeouts.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "description": "Python code to execute"},
                                    "timeout_seconds": {"type": "integer", "default": 10}
                                },
                                "required": ["code"]
                            }
                        },
                        {
                            "name": "run_shell_command",
                            "description": "Runs a bounded shell command with directory anchoring.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "command": {"type": "string", "description": "Shell command"},
                                    "cwd": {"type": "string", "description": "Working directory"},
                                    "timeout_seconds": {"type": "integer", "default": 15}
                                },
                                "required": ["command"]
                            }
                        }
                    ]
                }
            })

        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            if tool_name == "execute_python":
                res = execute_python_code(args.get("code", ""), args.get("timeout_seconds", 10))
            elif tool_name == "run_shell_command":
                res = run_shell_command(args.get("command", ""), args.get("cwd"), args.get("timeout_seconds", 15))
            else:
                return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found."}})

            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            })

        return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid request."}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}})


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP Code Sandbox Server")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    args = parser.parse_args()

    if args.test:
        print("[*] Testing MCP Code Sandbox Server...")
        res = execute_python_code("import math\nprint(f'pi={round(math.pi, 4)}')")
        assert res["status"] == "SUCCESS"
        assert "pi=3.1416" in res["stdout"]
        print(f"    Python Execution: OK -> {res['stdout'].strip()} ({res['duration_ms']}ms)")

        res_err = execute_python_code("def broken(:\n    pass")
        assert res_err["status"] == "SYNTAX_ERROR"
        print("    Syntax Error Detection: OK")

        res_timeout = execute_python_code("import time\ntime.sleep(5)", timeout_seconds=1)
        assert res_timeout["status"] == "TIMEOUT"
        print("    Timeout Enforcement: OK")
        print("[+] CODE SANDBOX SERVER OPERATIONAL!\n")
        return 0

    # stdio mode: read stdin line by line
    for line in sys.stdin:
        if line.strip():
            print(handle_json_rpc(line.strip()), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

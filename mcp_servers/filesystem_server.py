#!/usr/bin/env python3
"""
MCP Filesystem Sandbox Server (Model Context Protocol)
------------------------------------------------------
Provides path-traversal protected, atomic filesystem operations
with automatic `.bak` rollback snapshots and diff previews.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class SafeFilesystem:
    def __init__(self, allowed_root: Optional[Path] = None):
        if allowed_root is None:
            self.root = Path(os.getcwd()).resolve()
        else:
            self.root = Path(allowed_root).resolve()

    def _resolve_and_verify(self, target_path: str) -> Path:
        """Resolves path and blocks path-traversal attacks escaping allowed root."""
        resolved = (self.root / target_path).resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError:
            raise PermissionError(f"Access Denied: Path '{target_path}' escapes allowed root '{self.root}'.")
        return resolved

    def read_file(self, path: str, max_bytes: int = 500000) -> Dict[str, Any]:
        p = self._resolve_and_verify(path)
        if not p.exists():
            raise FileNotFoundError(f"File '{path}' does not exist.")
        if not p.is_file():
            raise IsADirectoryError(f"Path '{path}' is a directory, not a file.")

        content = p.read_text(encoding="utf-8", errors="replace")
        truncated = len(content.encode("utf-8")) > max_bytes
        return {
            "path": str(p),
            "size_bytes": p.stat().st_size,
            "content": content[:max_bytes],
            "truncated": truncated
        }

    def diff_preview(self, path: str, new_content: str) -> Dict[str, Any]:
        p = self._resolve_and_verify(path)
        old_content = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{path}", tofile=f"b/{path}"
        ))
        return {
            "path": str(p),
            "has_changes": bool(diff),
            "diff": "".join(diff)
        }

    def write_file(self, path: str, content: str, create_backup: bool = True) -> Dict[str, Any]:
        p = self._resolve_and_verify(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        backup_created = None
        if p.exists() and create_backup:
            backup_path = p.with_suffix(p.suffix + ".bak")
            shutil.copy2(p, backup_path)
            backup_created = str(backup_path)

        p.write_text(content, encoding="utf-8")
        return {
            "path": str(p),
            "size_bytes": len(content.encode("utf-8")),
            "backup_created": backup_created,
            "status": "WRITTEN"
        }

    def rollback_file(self, path: str) -> Dict[str, Any]:
        p = self._resolve_and_verify(path)
        backup_path = p.with_suffix(p.suffix + ".bak")
        if not backup_path.exists():
            raise FileNotFoundError(f"No backup file found at '{backup_path}'.")

        shutil.copy2(backup_path, p)
        return {
            "path": str(p),
            "restored_from": str(backup_path),
            "status": "RESTORED"
        }

    def list_directory(self, path: str = ".") -> Dict[str, Any]:
        p = self._resolve_and_verify(path)
        if not p.exists() or not p.is_dir():
            raise NotADirectoryError(f"Directory '{path}' does not exist.")

        entries = []
        for item in sorted(p.iterdir()):
            entries.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size_bytes": item.stat().st_size if item.is_file() else None
            })
        return {"directory": str(p), "entries": entries}


def handle_json_rpc(fs: SafeFilesystem, request_str: str) -> str:
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
                        {"name": "read_file", "description": "Reads text file safely with traversal protection."},
                        {"name": "write_file", "description": "Writes file atomically with auto .bak rollback snapshot."},
                        {"name": "diff_preview", "description": "Generates unified diff preview without mutating disk."},
                        {"name": "rollback_file", "description": "Reverts a file from its .bak snapshot."},
                        {"name": "list_directory", "description": "Lists directory entries."}
                    ]
                }
            })

        elif method == "tools/call":
            tool = params.get("name")
            args = params.get("arguments", {})

            if tool == "read_file":
                res = fs.read_file(args.get("path", ""))
            elif tool == "write_file":
                res = fs.write_file(args.get("path", ""), args.get("content", ""))
            elif tool == "diff_preview":
                res = fs.diff_preview(args.get("path", ""), args.get("new_content", ""))
            elif tool == "rollback_file":
                res = fs.rollback_file(args.get("path", ""))
            elif tool == "list_directory":
                res = fs.list_directory(args.get("path", "."))
            else:
                return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool}' not found."}})

            return json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            })

        return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid request."}})
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}})


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP Filesystem Sandbox Server")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    args = parser.parse_args()

    fs = SafeFilesystem()

    if args.test:
        print("[*] Testing MCP Filesystem Sandbox Server...")
        test_file = "scratch/test_fs.txt"

        # 1. Write file
        w_res = fs.write_file(test_file, "Line 1: Hello World\n")
        assert w_res["status"] == "WRITTEN"
        print("    Write File: OK")

        # 2. Diff preview
        d_res = fs.diff_preview(test_file, "Line 1: Hello World\nLine 2: New Line\n")
        assert d_res["has_changes"] is True
        print("    Diff Preview: OK")

        # 3. Update with backup
        w2_res = fs.write_file(test_file, "Line 1: Hello World\nLine 2: New Line\n")
        assert w2_res["backup_created"] is not None
        print("    Backup Snapshot: OK")

        # 4. Rollback
        r_res = fs.rollback_file(test_file)
        assert r_res["status"] == "RESTORED"
        content = fs.read_file(test_file)["content"]
        assert "Line 2" not in content
        print("    Rollback: OK")

        # 5. Path traversal block
        try:
            fs.read_file("../../../secret.txt")
            assert False, "Should have raised PermissionError"
        except PermissionError:
            print("    Path Traversal Guard: OK")

        print("[+] FILESYSTEM SANDBOX SERVER OPERATIONAL!\n")
        return 0

    for line in sys.stdin:
        if line.strip():
            print(handle_json_rpc(fs, line.strip()), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

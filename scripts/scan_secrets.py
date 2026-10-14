#!/usr/bin/env python3
"""
scan_secrets.py — Pre-commit secret scanning hook.
Inspects Python and configuration files for exposed secrets, private keys, or API tokens.
"""

import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent

SECRET_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI / Claude Secret Key"),
    (r"ghp_[a-zA-Z0-9]{36,}", "GitHub Personal Access Token"),
    (r"-----BEGIN PRIVATE KEY-----", "RSA/Private Key Block"),
    (r"TYPESAFE_API_KEY\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]", "Exposed API Key"),
    (r"AWS_SECRET_ACCESS_KEY\s*=\s*['\"][a-zA-Z0-9/+=]{40}['\"]", "AWS Secret Key"),
]

IGNORE_DIRS = {".git", ".memory", ".pytest_cache", "__pycache__", "node_modules", ".venv", "env"}


def scan_repository() -> int:
    print("[*] Scanning repository for exposed secrets or API keys...")
    violations = []

    for path in WORKSPACE.rglob("*"):
        if not path.is_file():
            continue
        # Skip ignored directories and scanner script itself
        if any(part in IGNORE_DIRS for part in path.parts) or path.name == "scan_secrets.py":
            continue
        # Only inspect text-based code, config, and markdown files
        if path.suffix not in {".py", ".json", ".md", ".toml", ".yml", ".yaml", ".txt", ".sh"}:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern, desc in SECRET_PATTERNS:
            if re.search(pattern, content):
                violations.append((path.relative_to(WORKSPACE), desc))

    if violations:
        print(f"[!] SECRET SCAN FAILED! {len(violations)} exposed secret(s) found:")
        for file_path, desc in violations:
            print(f"    - {file_path}: {desc}")
        return 1

    print("[+] SECRET SCAN PASSED: Zero exposed secrets or private tokens detected.")
    return 0


if __name__ == "__main__":
    sys.exit(scan_repository())

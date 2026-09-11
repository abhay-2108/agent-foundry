#!/usr/bin/env python3
"""
Validates a HANDOFF.md ledger file to ensure it conforms to the 5 mandatory sections
and contains required execution state fields.
"""

import sys
import re
import argparse
from pathlib import Path

REQUIRED_SECTIONS = [
    "## 1. Completed Milestones",
    "## 2. In-Flight Work & Active State",
    "## 3. Blockers & Dependencies",
    "## 4. Next Immediate Actions",
    "## 5. Key Decisions",
]

def validate_handoff_content(content: str) -> tuple[bool, list[str]]:
    errors = []
    
    # Check Header Metadata
    if "# Project State & Handoff Ledger" not in content and "# " not in content:
        errors.append("Missing primary top-level H1 header.")
        
    for sec in REQUIRED_SECTIONS:
        # Match case-insensitively or loosely on section title
        pattern = re.escape(sec[:10])
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Missing mandatory section: '{sec}'")
            
    # Check for prioritized actions in section 4
    if "## 4. Next Immediate Actions" in content:
        sec4_idx = content.find("## 4. Next Immediate Actions")
        sec5_idx = content.find("## 5. Key Decisions")
        sub = content[sec4_idx:sec5_idx] if sec5_idx != -1 else content[sec4_idx:]
        if not re.search(r"^\s*\d+\.\s+", sub, re.MULTILINE):
            errors.append("Section 4 must contain numbered prioritized action items (e.g., '1. ...').")

    return len(errors) == 0, errors

def run_self_test() -> int:
    valid_sample = """# Project State & Handoff Ledger
**Last Updated**: 2026-09-11 14:00

## 1. Completed Milestones
- [x] Feature implemented.

## 2. In-Flight Work & Active State
- Active file: main.py

## 3. Blockers & Dependencies
- None

## 4. Next Immediate Actions
1. Run test suite.
2. Submit PR.

## 5. Key Decisions & Rationales
- Used SQLite.
"""
    is_valid, errors = validate_handoff_content(valid_sample)
    if not is_valid:
        print(f"[-] Self-test failed: {errors}")
        return 1
    print("[+] validate_handoff self-test PASSED (100% compliance)")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HANDOFF.md ledger compliance")
    parser.add_argument("file", nargs="?", default="HANDOFF.md", help="Path to HANDOFF.md file")
    parser.add_argument("--test", action="store_true", help="Run self-test on sample ledger")
    args = parser.parse_args()

    if args.test:
        return run_self_test()

    path = Path(args.file)
    if not path.exists():
        print(f"[-] Error: '{path}' does not exist.")
        return 1
        
    content = path.read_text(encoding="utf-8")
    is_valid, errors = validate_handoff_content(content)
    
    if is_valid:
        print(f"[+] '{path}' is valid! All 5 mandatory sections and action items present.")
        return 0
    else:
        print(f"[-] '{path}' failed validation with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

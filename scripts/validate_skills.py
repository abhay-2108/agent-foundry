#!/usr/bin/env python3
"""
validate_skills.py — CI & Local Integrity Validator for Agent Foundry.
Validates:
1. Skills (frontmatter schema, name==dirname, description<1024 chars + trigger text, <500 lines, link resolution).
2. Agents (frontmatter schema, metadata encapsulation, bound skill existence, Composition section, link resolution).
3. Canonical References (presence and non-emptiness of all 7 reference checklists).
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

WORKSPACE = Path(__file__).resolve().parent.parent

# Allowed frontmatter keys per standard agent/skill spec
ALLOWED_SKILL_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
ALLOWED_AGENT_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CANONICAL_REFERENCES = [
    "done.md",
    "testing.md",
    "security.md",
    "perf.md",
    "a11y.md",
    "observability.md",
    "orchestration.md",
]


def parse_frontmatter(content: str) -> Tuple[Dict, str, str]:
    """Extracts (frontmatter_dict, body_text, error_message)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content, "Missing YAML frontmatter markers (---)"
    fm_text, body = match.group(1), match.group(2)
    try:
        import yaml
        data = yaml.safe_load(fm_text)
        if not isinstance(data, dict):
            return {}, body, "YAML frontmatter did not parse as a dictionary"
        return data, body, ""
    except Exception as e:
        return {}, body, f"YAML parse error: {e}"


def extract_markdown_links(markdown_text: str) -> List[Tuple[str, str]]:
    """Extracts markdown links [text](url) outside fenced code blocks and inline code."""
    # Strip multi-line code blocks ``` ... ```
    cleaned = re.sub(r"```[\s\S]*?```", "", markdown_text)
    # Strip inline code `...`
    cleaned = re.sub(r"`[^`\n]+`", "", cleaned)

    links = []
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", cleaned):
        text = match.group(1).strip()
        url = match.group(2).strip()
        links.append((text, url))
    return links


def validate_references() -> List[str]:
    errors = []
    ref_dir = WORKSPACE / "references"
    if not ref_dir.exists():
        return ["Missing root 'references/' directory."]

    for ref_name in CANONICAL_REFERENCES:
        ref_file = ref_dir / ref_name
        if not ref_file.exists():
            errors.append(f"Missing canonical reference: references/{ref_name}")
        elif len(ref_file.read_text(encoding="utf-8").strip()) < 50:
            errors.append(f"Canonical reference is empty or too short: references/{ref_name}")
    return errors


def validate_skills() -> Tuple[List[str], List[str], Set[str]]:
    errors = []
    warnings = []
    skill_names = set()

    skills_dir = WORKSPACE / "skills"
    if not skills_dir.exists():
        return ["Missing 'skills/' directory."], warnings, skill_names

    skill_files = sorted(skills_dir.rglob("SKILL.md"))
    if not skill_files:
        return ["No SKILL.md files found in skills/."], warnings, skill_names

    for skill_file in skill_files:
        rel_path = skill_file.relative_to(WORKSPACE).as_posix()
        dir_name = skill_file.parent.name
        content = skill_file.read_text(encoding="utf-8")
        lines = content.splitlines()

        # 1. Line count check (<500 lines for progressive disclosure)
        if len(lines) >= 500:
            errors.append(f"{rel_path}: Line count is {len(lines)} (must be < 500 lines).")

        # 2. Frontmatter check
        fm, body, fm_err = parse_frontmatter(content)
        if fm_err:
            errors.append(f"{rel_path}: {fm_err}")
            continue

        # Keys check
        unrecognized = set(fm.keys()) - ALLOWED_SKILL_KEYS
        if unrecognized:
            errors.append(f"{rel_path}: Unrecognized top-level frontmatter keys: {unrecognized}")

        name = fm.get("name")
        if not name:
            errors.append(f"{rel_path}: Missing 'name' in frontmatter.")
        elif name != dir_name:
            errors.append(f"{rel_path}: Frontmatter name '{name}' does not match directory '{dir_name}'.")
        else:
            skill_names.add(name)

        desc = fm.get("description", "")
        if not desc:
            errors.append(f"{rel_path}: Missing 'description' in frontmatter.")
        else:
            if len(desc) >= 1024:
                errors.append(f"{rel_path}: Description length is {len(desc)} (must be < 1024 chars).")
            if not any(k in desc.lower() for k in ["use when", "use this skill when", "when to use"]):
                errors.append(f"{rel_path}: Description must include trigger phrase ('Use when...' or 'Use this skill when...').")

        # 3. Markdown link validation
        links = extract_markdown_links(body)
        for text, url in links:
            if url.startswith(("http:", "https:", "#", "mailto:")):
                continue
            clean_url = url.split("#")[0].split("?")[0]
            if not clean_url:
                continue
            target_path = (skill_file.parent / clean_url).resolve()
            if not target_path.exists():
                errors.append(f"{rel_path}: Broken link to '{url}' (resolved to {target_path})")

    return errors, warnings, skill_names


def validate_agents(available_skills: Set[str]) -> Tuple[List[str], List[str]]:
    errors = []
    warnings = []

    agents_dir = WORKSPACE / "agents"
    if not agents_dir.exists():
        return ["Missing 'agents/' directory."], warnings

    agent_folders = [d for d in agents_dir.iterdir() if d.is_dir() and d.name not in ("runtime", "__pycache__")]
    if not agent_folders:
        return ["No agents found in agents/."], warnings

    for agent_folder in sorted(agent_folders):
        agent_file = agent_folder / "AGENT.md"
        rel_path = agent_file.relative_to(WORKSPACE).as_posix()
        dir_name = agent_folder.name

        if not agent_file.exists():
            errors.append(f"Agent folder '{dir_name}' is missing AGENT.md")
            continue

        content = agent_file.read_text(encoding="utf-8")
        fm, body, fm_err = parse_frontmatter(content)
        if fm_err:
            errors.append(f"{rel_path}: {fm_err}")
            continue

        # Check allowed frontmatter keys
        unrecognized = set(fm.keys()) - ALLOWED_AGENT_KEYS
        if unrecognized:
            errors.append(f"{rel_path}: Unrecognized frontmatter keys: {unrecognized}. Move custom fields to 'metadata'.")

        name = fm.get("name")
        if name != dir_name:
            errors.append(f"{rel_path}: Frontmatter name '{name}' does not match directory '{dir_name}'.")

        desc = fm.get("description", "")
        if not desc:
            errors.append(f"{rel_path}: Missing 'description'.")
        elif not any(k in desc.lower() for k in ["use when", "use this skill when", "when to use"]):
            errors.append(f"{rel_path}: Description must include 'Use when...' trigger.")

        # Check metadata fields
        meta = fm.get("metadata", {})
        if not isinstance(meta, dict):
            errors.append(f"{rel_path}: 'metadata' must be a mapping dictionary.")
        else:
            bound_skills = meta.get("bound_skills", [])
            for b_skill in bound_skills:
                if b_skill not in available_skills:
                    errors.append(f"{rel_path}: Bound skill '{b_skill}' does not exist in skills catalog.")

        # Check Composition section
        if "## Composition" not in body:
            errors.append(f"{rel_path}: Missing '## Composition' section.")
        else:
            if "Invoke directly when" not in body:
                errors.append(f"{rel_path}: Composition section missing 'Invoke directly when'.")
            if "Invoke via" not in body:
                errors.append(f"{rel_path}: Composition section missing 'Invoke via'.")
            if "Do not invoke from another persona" not in body:
                errors.append(f"{rel_path}: Composition section missing 'Do not invoke from another persona'.")

        # Markdown link validation
        links = extract_markdown_links(body)
        for text, url in links:
            if url.startswith(("http:", "https:", "#", "mailto:")):
                continue
            clean_url = url.split("#")[0].split("?")[0]
            if not clean_url:
                continue
            target_path = (agent_file.parent / clean_url).resolve()
            if not target_path.exists():
                errors.append(f"{rel_path}: Broken link to '{url}'")

    return errors, warnings


def main():
    print("=" * 65)
    print("  AGENT FOUNDRY INTEGRITY & SPECIFICATION VALIDATOR")
    print("=" * 65)

    all_errors = []

    # 1. Canonical References Validation
    print("[*] 1. Validating Canonical References (references/)...")
    ref_errors = validate_references()
    if ref_errors:
        all_errors.extend(ref_errors)
        for err in ref_errors:
            print(f"    [!] {err}")
    else:
        print(f"    [+] All {len(CANONICAL_REFERENCES)} canonical references verified.")

    # 2. Skills Validation
    print("[*] 2. Validating Skills (skills/**/SKILL.md)...")
    skill_errors, skill_warnings, available_skills = validate_skills()
    if skill_errors:
        all_errors.extend(skill_errors)
        for err in skill_errors:
            print(f"    [!] {err}")
    else:
        print(f"    [+] All {len(available_skills)} skills passed frontmatter, link, and length validations.")

    # 3. Agents Validation
    print("[*] 3. Validating Autonomous Agents (agents/*/AGENT.md)...")
    agent_errors, agent_warnings = validate_agents(available_skills)
    if agent_errors:
        all_errors.extend(agent_errors)
        for err in agent_errors:
            print(f"    [!] {err}")
    else:
        print("    [+] All 10 agents passed frontmatter, metadata, composition, and skill bindings.")

    print("=" * 65)
    if all_errors:
        print(f"[-] VALIDATION FAILED with {len(all_errors)} error(s).")
        sys.exit(1)
    else:
        print("[+] ALL VALIDATIONS PASSED CLEANLY (Zero Errors, Zero Regressions)!")
        sys.exit(0)


if __name__ == "__main__":
    main()

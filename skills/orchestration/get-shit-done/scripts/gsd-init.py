#!/usr/bin/env python3
"""
gsd-init.py - Scaffold a complete GSD project structure.

Usage:
  python gsd-init.py
  python gsd-init.py --project "My App" --milestone "M001: Core Platform"
  python gsd-init.py --project "My App" --dir /path/to/project
"""
import argparse, json, os
from datetime import date

def wf(path, content, force=False):
    if os.path.exists(path) and not force:
        print(f"  [skip] {os.path.relpath(path)}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  [+] {os.path.relpath(path)}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project")
    p.add_argument("--milestone", default="M001: Core Platform")
    p.add_argument("--dir", default=".")
    p.add_argument("--force", action="store_true")
    a = p.parse_args()

    root = os.path.abspath(a.dir)
    gsd  = os.path.join(root, ".gsd")

    if not a.project:
        a.project = input(f"Project name [{os.path.basename(root)}]: ").strip() or os.path.basename(root)

    mid, mname = (a.milestone.split(":", 1) + [""])[:2]
    mid   = mid.strip()
    mname = mname.strip() if mname else a.milestone

    today = date.today().isoformat()
    print(f"\n  Scaffolding GSD: {a.project} / {mid}: {mname}\n")

    wf(os.path.join(gsd,"PROJECT.md"),f"# {a.project}\n\n## Problem Statement\n[One paragraph: what problem, for whom, why now?]\n\n## Product Vision\n[Success in 6 months?]\n\n## Tech Stack\n- Frontend:\n- Backend:\n- Database:\n- Auth:\n\n## Out of Scope\n- [thing NOT being built]\n\n## Milestone Sequence\n- {mid}: {mname}\n",a.force)

    wf(os.path.join(gsd,"REQUIREMENTS.md"),f"# Requirements\n\n## Active\n| ID | Capability | Status | Owned By |\n|----|-----------|---------|---------|\n| R001 | [capability] | active | {mid}/S01 |\n\n## Deferred\n| ID | Capability | Reason |\n|----|-----------|---------|\n\n## Out of Scope\n| ID | Capability | Reason |\n|----|-----------|---------|\n",a.force)

    wf(os.path.join(gsd,"DECISIONS.md"),f"# Decisions\n\n## D001 — [{today}]\n**Decision**: [what]\n**Context**: [why]\n**Consequences**: [impact]\n",a.force)

    wf(os.path.join(gsd,"STATE.md"),f"# GSD State\n\n**Project**: {a.project}\n**Active Milestone**: {mid}: {mname}\n**Active Slice**: S01\n**Phase**: planning\n\n_Last updated: {today}_\n",a.force)

    wf(os.path.join(gsd,"KNOWLEDGE.md"),"# Knowledge Base\n\nAppend-only register of project-specific rules and patterns.\nThe agent reads this at the start of every unit.\n\n---\n\n_No entries yet._\n\n## Format\n```\n## [YYYY-MM-DD] [Source: session M###/S##/T## | user]\n- [Rule or pattern discovered]\n- [Context: why this matters]\n```\n",a.force)

    wf(os.path.join(gsd,"CAPTURES.md"),"# Pending Captures\n\nFire-and-forget thoughts awaiting triage.\nRun `/gsd triage` or `python gsd-capture.py --list` to review.\n\n---\n\n_No captures yet._\n",a.force)

    wf(os.path.join(gsd,"PREFERENCES.md"),"---\nmode: solo\ngit:\n  auto_push: false\n  isolation: none\n  merge_strategy: squash\n  commit_docs: true\nplanning_depth: normal\nphases:\n  skip_slice_research: false\n  reassess_after_slice: true\nparallel:\n  enabled: false\n  max_workers: 2\n---\n",a.force)

    metrics = {"project":a.project,"active_milestone":mid,"milestones":{mid:{"name":mname,"status":"in_progress","slices":{"S01":{"name":"Slice 1","status":"not_started"}}}}}
    wf(os.path.join(gsd,"metrics.json"),json.dumps(metrics,indent=2)+"\n",a.force)

    m_dir = os.path.join(gsd,"milestones",mid)
    wf(os.path.join(m_dir,f"{mid}-CONTEXT.md"),f"---\ndepends_on: []\n---\n\n# {mid}: {mname}\n\n## Goal\n[What does this milestone deliver? What can users DO after it?]\n\n## Success Criteria\n- [ ] User can [end-to-end flow]\n\n## Architecture Decisions\n[Key decisions all slices must respect.]\n\n## Slices\n| # | Name | Risk | Depends | Demo |\n|---|------|------|---------|------|\n| S01 | [name] | high | — | [demo] |\n",a.force)

    wf(os.path.join(m_dir,f"{mid}-ROADMAP.md"),f"# {mid} Roadmap: {mname}\n\n## Success Criteria\n- [ ] [End-to-end flow works]\n\n## Slices\n| # | Name | Status | Risk | Depends |\n|---|------|--------|------|--------|\n| S01 | [name] | not_started | high | — |\n\n_Last updated: {today}_\n",a.force)

    s_dir = os.path.join(m_dir,"slices","S01")
    wf(os.path.join(s_dir,"S01-PLAN.md"),f"# S01: [Slice Name]\n\n## User Story\nAs a [user], I want [capability] so that [value].\n\n## Must-Haves\n- [ ] T01: [task — 15-60 min]\n- [ ] T02: [task — 15-60 min]\n\n## Layers Touched\n- [ ] Database  - [ ] API  - [ ] Frontend\n\n## UAT Test\n[Exact steps to verify]\n\n_Created: {today}_\n",a.force)

    os.makedirs(os.path.join(s_dir,"tasks"),exist_ok=True)
    wf(os.path.join(gsd,"journal",f"{today}.md"),f"# Session Log — {today}\n\n## Context\n- **Milestone**: {mid}: {mname}\n- **Slice**: S01\n\n## What happened\n- Initialized GSD project structure\n\n## Next session\n- [ ] Fill in PROJECT.md\n- [ ] Run Discussion Protocol\n\n---\n",a.force)

    for d in ["activity", os.path.join("runtime","units")]:
        os.makedirs(os.path.join(gsd,d),exist_ok=True)

    print(f"\n  Done. Structure at {root}/.gsd/")
    print("  Next: fill in PROJECT.md, run Discussion Protocol, define slices.")

if __name__ == "__main__":
    main()

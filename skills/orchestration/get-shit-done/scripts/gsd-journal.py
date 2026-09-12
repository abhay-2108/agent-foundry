#!/usr/bin/env python3
"""
gsd-journal.py - GSD daily session journal.

Usage:
  python gsd-journal.py           # Create today's journal
  python gsd-journal.py --yesterday  # Show yesterday's journal
  python gsd-journal.py --list    # List all journal entries
"""
import argparse, json, os
from datetime import date, timedelta
from pathlib import Path

def find_root(start="."):
    cur = Path(start).resolve()
    while True:
        if (cur/".gsd").is_dir(): return cur
        parent = cur.parent
        if parent == cur: return None
        cur = parent

def read_state(gsd):
    sf = gsd/"STATE.md"
    res = {}
    if sf.exists():
        for line in sf.read_text(errors="ignore").splitlines():
            if "Active Milestone" in line:
                res["milestone"] = line.split(":",1)[-1].strip().strip("*")
            elif "Active Slice" in line:
                res["slice"] = line.split(":",1)[-1].strip().strip("*")
    return res

def read_metrics(gsd):
    mf = gsd/"metrics.json"
    if mf.exists():
        try: return json.loads(mf.read_text())
        except Exception: pass
    return {}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--yesterday",action="store_true")
    p.add_argument("--list",action="store_true")
    p.add_argument("--dir",default=".")
    a = p.parse_args()

    root = find_root(a.dir)
    if not root:
        print("ERROR: No .gsd/ found."); return

    gsd = root/".gsd"
    jdir = gsd/"journal"

    if a.list:
        if jdir.exists():
            entries = sorted(jdir.glob("*.md"),reverse=True)
            print("\nJournal entries:")
            for e in entries: print(f"  {e.stem}")
        else:
            print("No journal entries yet.")
        return

    if a.yesterday:
        yest = date.today()-timedelta(days=1)
        yp = jdir/f"{yest.isoformat()}.md"
        print(yp.read_text(errors="ignore") if yp.exists() else f"No journal for {yest.isoformat()}")
        return

    today = date.today()
    jp = jdir/f"{today.isoformat()}.md"

    if jp.exists():
        print(f"Today's journal already exists:\n  {jp}")
        return

    state   = read_state(gsd)
    metrics = read_metrics(gsd)
    mid     = metrics.get("active_milestone","")
    slices  = metrics.get("milestones",{}).get(mid,{}).get("slices",{})
    done    = sum(1 for s in slices.values() if s.get("status")=="complete")
    total   = len(slices)

    # carry forward next-session items from yesterday
    carried = ""
    yest_path = jdir/f"{(today-timedelta(days=1)).isoformat()}.md"
    if yest_path.exists():
        lines = yest_path.read_text(errors="ignore").splitlines()
        in_next = False
        for line in lines:
            if "## Next" in line: in_next = True
            if in_next: carried += line + "\n"

    content  = f"# Session Log — {today.isoformat()}\n\n"
    content += f"## Context\n"
    content += f"- **Milestone**: {state.get('milestone','(unknown)')}\n"
    content += f"- **Active Slice**: {state.get('slice','S01')}\n"
    content += f"- **Progress**: {done}/{total} slices complete\n\n"
    if carried:
        content += f"## Carried Forward\n{carried.strip()}\n\n"
    content += "## What happened this session\n- [ ] \n\n"
    content += "## Blockers\n- none\n\n"
    content += "## Decisions made\n- none\n\n"
    content += "## Next session\n- [ ] \n\n---\n"

    jdir.mkdir(parents=True,exist_ok=True)
    jp.write_text(content,encoding="utf-8",newline="\n")
    print(f"Created: {jp}")

if __name__ == "__main__":
    main()

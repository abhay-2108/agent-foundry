#!/usr/bin/env python3
"""
gsd-status.py - GSD progress dashboard.

Usage:
  python gsd-status.py            # auto-detect .gsd/ from current dir
  python gsd-status.py --dir /path/to/project
"""
import argparse, json, os, subprocess
from datetime import date
from pathlib import Path

def find_root(start="."):
    cur = Path(start).resolve()
    while True:
        if (cur / ".gsd").is_dir(): return cur
        parent = cur.parent
        if parent == cur: return None
        cur = parent

def read(path, default=""):
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return default

def git_log(root, n=5):
    try:
        r = subprocess.run(["git","log",f"--oneline",f"-{n}"],
                           capture_output=True,text=True,cwd=root,timeout=5)
        return r.stdout.strip()
    except Exception:
        return "(git unavailable)"

def bar(done, total, w=20):
    if total == 0: return "["+"─"*w+"]"
    f = int(w*done/total)
    return "["+"█"*f+"─"*(w-f)+"]"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default=".")
    a = p.parse_args()

    root = find_root(a.dir)
    if not root:
        print("ERROR: No .gsd/ found. Run gsd-init.py first."); return

    gsd = root / ".gsd"
    print("="*60)
    print("  GSD STATUS")
    print("="*60)

    state = read(gsd/"STATE.md")
    print("\n  STATE")
    for line in state.strip().splitlines():
        if line.startswith("**"): print(f"    {line}")

    try:
        metrics = json.loads((gsd/"metrics.json").read_text())
    except Exception:
        metrics = {}

    if metrics:
        print("\n  MILESTONES")
        for mid, mdata in metrics.get("milestones",{}).items():
            slices = mdata.get("slices",{})
            total  = len(slices)
            done   = sum(1 for s in slices.values() if s.get("status")=="complete")
            ip     = sum(1 for s in slices.values() if s.get("status")=="in_progress")
            blk    = sum(1 for s in slices.values() if s.get("status")=="blocked")
            icons  = {"complete":"✓","in_progress":"►","not_started":" "}
            si     = icons.get(mdata.get("status",""),"?")
            print(f"\n  [{si}] {mid}: {mdata.get('name','')}")
            suffix = ""
            if ip:  suffix += f"  {ip} in progress"
            if blk: suffix += f"  {blk} BLOCKED"
            print(f"      {bar(done,total)} {done}/{total} slices{suffix}")
            for sid, sd in slices.items():
                ic = {"complete":"✓","in_progress":"►","blocked":"!","not_started":"·"}.get(sd.get("status","not_started"),"?")
                print(f"        [{ic}] {sid}: {sd.get('name','')}")

    caps = read(gsd/"CAPTURES.md")
    pending = [l for l in caps.splitlines() if "[pending]" in l]
    if pending:
        print(f"\n  CAPTURES — {len(pending)} pending")
        for c in pending[:5]: print(f"    {c.strip()}")
        if len(pending) > 5: print(f"    ... {len(pending)-5} more")

    print("\n  RECENT COMMITS")
    log = git_log(root)
    for line in (log.splitlines() if log else ["(none)"]): print(f"    {line}")

    today = date.today().isoformat()
    jp = gsd/"journal"/f"{today}.md"
    print(f"\n  JOURNAL — {'exists' if jp.exists() else 'not started (run gsd-journal.py)'}")
    print("\n"+"="*60)

if __name__ == "__main__":
    main()

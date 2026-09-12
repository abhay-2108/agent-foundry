#!/usr/bin/env python3
"""
gsd-capture.py - Fire-and-forget GSD thought capture.

Usage:
  python gsd-capture.py "add rate limiting to the API"   # capture a thought
  python gsd-capture.py --list                           # show pending
  python gsd-capture.py --resolve CAP-001                # mark resolved
  python gsd-capture.py --resolve-all                    # mark all resolved
"""
import argparse, os, re
from datetime import datetime
from pathlib import Path

def find_root(start="."):
    cur = Path(start).resolve()
    while True:
        if (cur/".gsd").is_dir(): return cur
        parent = cur.parent
        if parent == cur: return None
        cur = parent

def next_id(cp):
    ids = []
    if cp.exists():
        for line in cp.read_text(errors="ignore").splitlines():
            m = re.search(r"CAP-(\d+)", line)
            if m: ids.append(int(m.group(1)))
    return f"CAP-{(max(ids,default=0)+1):03d}"

def add_capture(gsd, text):
    cp = gsd/"CAPTURES.md"
    cid = next_id(cp)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [pending] **{cid}** ({now}): {text}\n"
    if not cp.exists():
        cp.write_text("# Pending Captures\n\nRun `/gsd triage` to process.\n\n---\n\n",
                      encoding="utf-8",newline="\n")
    with open(cp,"a",encoding="utf-8",newline="\n") as f:
        f.write(entry)
    print(f"  Captured: {cid} — {text}")
    print(f"  Run `/gsd triage` or `python gsd-capture.py --list` to review.")

def list_captures(gsd):
    cp = gsd/"CAPTURES.md"
    if not cp.exists(): print("  No captures file."); return
    content  = cp.read_text(errors="ignore")
    pending  = [l.strip() for l in content.splitlines() if "[pending]" in l]
    resolved = [l.strip() for l in content.splitlines() if "[resolved]" in l]
    print(f"\n  CAPTURES — {len(pending)} pending, {len(resolved)} resolved")
    if pending:
        print("\n  PENDING:")
        for p in pending: print(f"    {p}")
    if not pending:
        print("  No pending captures.")

def resolve_one(gsd, cid):
    cp = gsd/"CAPTURES.md"
    if not cp.exists(): print("  No captures file."); return
    content = cp.read_text(errors="ignore")
    if cid not in content: print(f"  {cid} not found."); return
    new = content.replace(f"[pending] **{cid}**",f"[resolved] **{cid}**")
    cp.write_text(new,encoding="utf-8",newline="\n")
    print(f"  Resolved: {cid}")

def resolve_all(gsd):
    cp = gsd/"CAPTURES.md"
    if not cp.exists(): return
    content = cp.read_text(errors="ignore")
    new = re.sub(r"\[pending\]","[resolved]",content)
    cp.write_text(new,encoding="utf-8",newline="\n")
    print(f"  Resolved {content.count('[pending]')} capture(s).")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("thought",nargs="?")
    p.add_argument("--list",action="store_true")
    p.add_argument("--resolve",metavar="CAP-ID")
    p.add_argument("--resolve-all",action="store_true")
    p.add_argument("--dir",default=".")
    a = p.parse_args()

    root = find_root(a.dir)
    if not root:
        print("ERROR: No .gsd/ found. Run gsd-init.py first."); return

    gsd = root/".gsd"
    if a.resolve:       resolve_one(gsd,a.resolve)
    elif a.resolve_all: resolve_all(gsd)
    elif a.list:        list_captures(gsd)
    elif a.thought:     add_capture(gsd,a.thought)
    else:               p.print_help()

if __name__ == "__main__":
    main()

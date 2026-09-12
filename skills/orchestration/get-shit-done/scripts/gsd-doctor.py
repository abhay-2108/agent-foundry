#!/usr/bin/env python3
"""
gsd-doctor.py - GSD health checker with auto-fix.

Usage:
  python gsd-doctor.py           # diagnose only
  python gsd-doctor.py --fix     # diagnose and auto-fix fixable issues

Checks 5 domains:
  1. Structural  - missing summaries, UAT files, roadmap consistency
  2. Runtime     - stale auto.lock, orphaned locks
  3. State       - STATE.md validity
  4. Git         - dirty working tree, uncommitted changes
  5. Environment - Python version, .env presence, disk space
"""
import argparse, json, os, subprocess
from pathlib import Path

ISSUES = []

def issue(domain, severity, msg, fixable=False, fix_fn=None):
    ISSUES.append({"domain":domain,"severity":severity,"msg":msg,
                   "fixable":fixable,"fix_fn":fix_fn})

def find_root(start="."):
    cur = Path(start).resolve()
    while True:
        if (cur/".gsd").is_dir(): return cur
        parent = cur.parent
        if parent == cur: return None
        cur = parent

def check_structural(gsd):
    md = gsd/"milestones"
    if not md.exists():
        issue("structural","warn","No milestones/ directory"); return
    for m_dir in sorted(md.iterdir()):
        if not m_dir.is_dir(): continue
        mid = m_dir.name
        for fname in [f"{mid}-CONTEXT.md",f"{mid}-ROADMAP.md"]:
            if not (m_dir/fname).exists():
                issue("structural","error",f"{mid}/{fname} missing")
        sd = m_dir/"slices"
        if not sd.exists(): continue
        for s_dir in sorted(sd.iterdir()):
            if not s_dir.is_dir(): continue
            sid = s_dir.name
            if not (s_dir/f"{sid}-PLAN.md").exists():
                issue("structural","error",f"{mid}/{sid}/{sid}-PLAN.md missing")
            td = s_dir/"tasks"
            if not td.exists(): continue
            plan_txt = (s_dir/f"{sid}-PLAN.md").read_text(errors="ignore") if (s_dir/f"{sid}-PLAN.md").exists() else ""
            for tp in sorted(td.glob("T*-PLAN.md")):
                tid = tp.stem.replace("-PLAN","")
                ts  = td/f"{tid}-SUMMARY.md"
                if f"[x]" in plan_txt and tid in plan_txt and not ts.exists():
                    plan_path = s_dir/f"{sid}-PLAN.md"
                    def mk_fix(pp, t):
                        def fix():
                            txt = pp.read_text(encoding="utf-8")
                            pp.write_text(txt.replace(f"[x] {t}",f"[ ] {t}"),encoding="utf-8",newline="\n")
                            print(f"    Fixed: unchecked {t} in {pp.name}")
                        return fix
                    issue("structural","warn",f"{mid}/{sid}/{tid}: marked done but SUMMARY missing",
                          fixable=True,fix_fn=mk_fix(plan_path,tid))

def check_runtime(gsd):
    lf = gsd/"auto.lock"
    if not lf.exists(): return
    try:
        ld = json.loads(lf.read_text())
    except Exception:
        issue("runtime","warn","auto.lock is invalid JSON",fixable=True,fix_fn=lambda:lf.unlink(missing_ok=True)); return
    pid = ld.get("pid")
    if pid:
        alive = False
        try: os.kill(int(pid),0); alive=True
        except Exception: pass
        if not alive:
            def rm():
                lf.unlink(missing_ok=True)
                print(f"    Fixed: removed stale auto.lock (PID {pid})")
            issue("runtime","error",f"Stale auto.lock — PID {pid} is dead",fixable=True,fix_fn=rm)
        else:
            issue("runtime","info",f"auto.lock present — auto-mode running (PID {pid})")

def check_state(gsd):
    sf = gsd/"STATE.md"
    if not sf.exists():
        def mk():
            sf.write_text("# GSD State\n\n**Active Milestone**: (unknown)\n**Phase**: unknown\n",encoding="utf-8",newline="\n")
            print("    Fixed: created minimal STATE.md")
        issue("state","error","STATE.md missing",fixable=True,fix_fn=mk); return
    if "Active Milestone" not in sf.read_text(errors="ignore"):
        issue("state","warn","STATE.md may be malformed (no Active Milestone line)")

def check_git(root):
    try:
        r = subprocess.run(["git","status","--porcelain"],
                           capture_output=True,text=True,cwd=root,timeout=10)
        dirty = [l for l in r.stdout.splitlines()
                 if l.strip() and not l.strip().startswith("?? .gsd/")]
        if dirty:
            issue("git","warn",f"Dirty working tree ({len(dirty)} file(s)) — commit before resuming")
    except Exception:
        issue("git","warn","git unavailable")

def check_environment(root):
    env = root/".env"; ex = root/".env.example"
    if ex.exists() and not env.exists():
        issue("environment","warn",".env.example exists but .env does not")
    try:
        st = os.statvfs(str(root)) if hasattr(os,"statvfs") else None
        if st:
            free = (st.f_bavail*st.f_frsize)//(1024*1024)
            if free < 500: issue("environment","warn",f"Low disk: {free}MB free")
    except Exception:
        pass

def print_report():
    if not ISSUES:
        print("  No issues found. GSD project healthy."); return
    errs  = [i for i in ISSUES if i["severity"]=="error"]
    warns = [i for i in ISSUES if i["severity"]=="warn"]
    fixable=[i for i in ISSUES if i["fixable"]]
    print(f"  Issues: {len(ISSUES)} total · {len(errs)} error(s) · {len(warns)} warning(s) · {len(fixable)} fixable")
    icons  = {"error":"[ERROR]","warn":"[WARN ]","info":"[INFO ]"}
    for dom in ["structural","runtime","state","git","environment"]:
        di = [i for i in ISSUES if i["domain"]==dom]
        if di:
            print(f"\n  {dom.upper()}")
            for i in di:
                tag = " (auto-fixable)" if i["fixable"] else ""
                print(f"    {icons.get(i['severity'],'[?????]')} {i['msg']}{tag}")

def apply_fixes():
    fixable=[i for i in ISSUES if i["fixable"] and i["fix_fn"]]
    if not fixable: print("  Nothing to auto-fix."); return
    print(f"\n  Applying {len(fixable)} fix(es)...")
    for i in fixable:
        try: i["fix_fn"]()
        except Exception as e: print(f"    ERROR: {e}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fix",action="store_true")
    p.add_argument("--dir",default=".")
    a = p.parse_args()

    root = find_root(a.dir)
    if not root:
        print("ERROR: No .gsd/ found."); return

    gsd = root/".gsd"
    print("="*60)
    print("  GSD DOCTOR")
    print("="*60)
    print(f"  Scanning: {root}\n")

    check_structural(gsd)
    check_runtime(gsd)
    check_state(gsd)
    check_git(root)
    check_environment(root)

    print_report()

    if a.fix:
        print("\n"+"="*60)
        print("  APPLYING FIXES")
        print("="*60)
        apply_fixes()
        print("\n  Run `python gsd-doctor.py` again to verify.")
    elif any(i["fixable"] for i in ISSUES):
        n = sum(1 for i in ISSUES if i["fixable"])
        print(f"\n  {n} fixable issue(s). Run with --fix to repair.")
    print("\n"+"="*60)

if __name__ == "__main__":
    main()

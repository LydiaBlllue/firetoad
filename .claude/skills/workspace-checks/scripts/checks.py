#!/usr/bin/env python3
"""The checks, by level (2026-11-05, the owner: most checks are run when asked, not after every
edit). Whether the money is right runs by itself — after every edit to findata/ (the hook) and
at the end of an import — and is not here. Everything else is one of two levels:

    python3 .claude/skills/workspace-checks/scripts/checks.py . --level page
        "check the page" / 检查页面 — after changing the page, its documents or the data's shape:
        the data in full (is the page current, is the data tidy), the design rules, and the page
        drawn in a browser: four widths, a short window, and every kind of owner.

    python3 .claude/skills/workspace-checks/scripts/checks.py . --level release
        "check before a release" / 发版前检查 — the page level, then the selftest, which plants
        faults in a copy and fails if any checker misses its fault.

Exit 0 when every check passed, 1 when one failed, 2 when the browser is missing.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if all(os.path.isdir(os.path.join(d, x)) for x in ("findata", "dashboards")):
            return d
        up = os.path.dirname(d)
        if up == d:
            raise SystemExit(f"no workspace (findata/ and dashboards/) at or above {start}")
        d = up


def main_dash(root):
    for n in ("ly_finance_dashboard.html", "finance_dashboard.html"):
        if os.path.exists(os.path.join(root, "dashboards", n)):
            return os.path.join("dashboards", n)
    raise SystemExit("no dashboard under dashboards/ — rebuild first")


def run(root, label, script, args):
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, os.path.join(HERE, script)] + args, cwd=root,
                       capture_output=True, text=True)
    out = (p.stdout + p.stderr).rstrip()
    secs = round(time.monotonic() - t0, 1)
    print(out if out else f"=== {label} ===")
    return label, p.returncode, secs


def main(argv):
    level = argv[argv.index("--level") + 1] if "--level" in argv else "page"
    if level not in ("page", "release"):
        print(__doc__); return 2
    root = find_root(next((a for a in argv if not a.startswith("-") and a not in ("page", "release")), "."))
    dash = main_dash(root)
    steps = [("data", "check_data.py", ["."]),
             ("design", "check_design.py", [dash]),
             ("render", "check_render.py", [dash])]
    if level == "release":
        steps.append(("selftest", "selftest.py", ["."]))
    results = [run(root, *s) for s in steps]
    print("\n=== " + ("check the page" if level == "page" else "check before a release") + " ===")
    worst = 0
    for label, rc, secs in results:
        mark = "✓" if rc == 0 else ("·" if rc == 2 else "✗")
        print(f"  {mark} {label:<9} {secs}s" + ("  (the browser is not installed)" if rc == 2 and label == "render" else ""))
        worst = max(worst, 1 if rc == 1 else rc)
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""setting.py — change one of the numbers that are the owner's to choose (FINANCE.md §8e).

settings.py is the table of them; this is the write, as a verb, so the Settings page (through
the local app) and a chat change a number the same way:

    python3 .claude/skills/update-dashboard/scripts/setting.py .                        # every setting, as it stands
    python3 .claude/skills/update-dashboard/scripts/setting.py . emergency 6 9          # say what would change
    python3 .claude/skills/update-dashboard/scripts/setting.py . emergency 6 9 --write
    python3 .claude/skills/update-dashboard/scripts/setting.py . planBase 3600 --write
    python3 .claude/skills/update-dashboard/scripts/setting.py . emergency --reset --write   # back to the default

The value is checked against its row (a range with its lower end first, a day every month has,
money that is not negative) and refused otherwise; nothing is written for a refused value. A
written value lands where it already lives in findata/register/, the day goes beside it in
plan.json `changed`, the page is rebuilt and the money checks run, as after every write.
"""
import argparse
import datetime
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout  # noqa: E402
import jlock  # noqa: E402  one writer at a time, both doors
import settings  # noqa: E402
import verbs  # noqa: E402
from update import jload, jsave  # noqa: E402

CHECKS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "workspace-checks", "scripts")
FILES = ("plan.json", "funds.json", "profile.json")


def load(root):
    return {n: jload(layout.path(root, n), {}) for n in FILES}


def show(v, kind):
    if v is None:
        return "not set"
    if kind == "months":
        return f"{v[0]:g} to {v[1]:g} months"
    if kind == "day":
        return f"day {int(v)}"
    return f"${v:,.2f}".replace(".00", "")


def run(root, key=None, raw=None, reset=False, write=False, say=None):
    """Change one setting (verbs.py). Returns rc, lines, and `key`, `before`, `after`, `written`,
    `findings` (the money checks' ✗ / ⚠ lines); with no key, `settings` — the table as it stands."""
    emit, lines = verbs.speaker(say)
    root = os.path.abspath(root)
    files = load(root)
    res = {"key": key, "before": None, "after": None, "written": False, "findings": []}

    if key is None:
        res["settings"] = settings.rows(files)
        emit("=== settings ===")
        for r in res["settings"]:
            tail = "  (the default)" if r["isDef"] else f"  (changed {r['changed']})" if r["changed"] else ""
            emit(f"  {r['key']:<10} {r['n']:<24} {show(r['v'], r['kind'])}{tail}")
        return verbs.result(res, 0, lines)

    row = settings.BY_KEY.get(key)
    if row is None:
        emit(f"  ✗ no setting called {key!r}; there are: {', '.join(settings.BY_KEY)}")
        return verbs.result(res, 1, lines)
    res["before"] = settings.value(key, files)
    if settings.locked(key, files):
        emit(f"  ✗ {row['en']} is the sum of several lines of the plan, so it cannot be changed as one number. "
             f"Change the line itself in funds.json.")
        return verbs.result(res, 1, lines)
    today = datetime.date.today().isoformat()
    try:
        if reset:
            touched = settings.reset(key, files, today)
        else:
            v, why = settings.check(key, raw)
            if why:
                emit(f"  ✗ {why}")
                return verbs.result(res, 1, lines)
            touched = settings.write(key, v, files, today)
    except ValueError as e:
        emit(f"  ✗ {e}")
        return verbs.result(res, 1, lines)
    res["after"] = settings.value(key, files)
    emit(f"=== setting — {row['en']} ===")
    emit(f"  {show(res['before'], row['kind'])}  →  {show(res['after'], row['kind'])}")
    if not write:
        emit("\n  nothing written. Run with --write to apply.")
        return verbs.result(res, 0, lines)

    other = jlock.held_by_other(root)
    if other:
        emit(jlock.refusal(other))
        return verbs.result(res, 1, lines)
    for n in touched:
        jsave(layout.path(root, n), files[n])
    res["written"] = True
    for script, args in ((os.path.join(HERE, "rebuild.py"), [".", "--write"]),
                         (os.path.join(HERE, "preflight.py"), [".", "--reseed"])):
        subprocess.run([sys.executable, script] + args, cwd=root, capture_output=True, text=True)
    out = subprocess.run([sys.executable, os.path.join(CHECKS, "check_data.py"), ".", "--money"],
                         cwd=root, capture_output=True, text=True).stdout
    res["findings"] = [l.strip() for l in out.splitlines() if l.strip().startswith(("✗", "⚠"))]
    emit("  written; the page is rebuilt." + ("" if not res["findings"] else "\n  the checkers found:"))
    for f in res["findings"]:
        emit("  " + f)
    return verbs.result(res, 2 if any(f.startswith("✗") for f in res["findings"]) else 0, lines)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("key", nargs="?", help="the setting's key; none lists them all")
    ap.add_argument("value", nargs="*", help="the new value; a range takes two numbers")
    ap.add_argument("--reset", action="store_true", help="back to the default")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    raw = a.value if len(a.value) != 1 else a.value[0]
    if a.key and not a.reset and not a.value:
        ap.error("a value is needed, or --reset")
    return run(a.root, a.key, raw, reset=a.reset, write=a.write, say=print)["rc"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

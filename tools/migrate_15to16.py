#!/usr/bin/env python3
"""migrate_15to16.py — move a workspace from findata schema 15 to 16.

    python3 tools/migrate_15to16.py <workspace>

What changed in 16 (2026-11-02, FINANCE.md §3a): Education is an ordinary category. The group
`education` is gone; `plan.json` `notInFire` lists the categories that stay out of the FIRE target,
Education by default. An owner who had moved a category in or out keeps the same target.
  - `profile.json` becomes "schema": 16.

Safe to run twice: a workspace already at 16 is left alone.
"""
import json
import os
import sys

TOOL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", "update-dashboard", "scripts"))
import layout  # noqa: E402


def dump(path, obj):
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(path, "a", encoding="utf-8").write("\n")


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    ws = os.path.abspath(argv[1])
    pp = layout.path(ws, "profile.json")
    if not os.path.exists(pp):
        print(f"no profile.json under {ws}"); return 2
    prof = json.load(open(pp, encoding="utf-8"))
    have = int(prof.get("schema", 2))
    if have >= 16:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 15:
        print(f"findata/ is schema {have}; this script only moves 15 → 16 (run tools/migrate.py)"); return 2

    lp = layout.path(ws, "plan.json")
    if os.path.exists(lp):
        plan = json.load(open(lp, encoding="utf-8"))
        own = plan.get("categoryGroups") or {}
        if own:
            ended = [k for k, g in own.items() if g == "education"]
            moved = "Education" in own and own["Education"] != "education"
            if ended or moved:
                keep = ([] if moved else ["Education"]) + [k for k in ended if k != "Education"]
                if keep != ["Education"]:
                    plan["notInFire"] = keep
                plan["categoryGroups"] = {k: g for k, g in own.items() if g != "education"}
                dump(lp, plan)
                print(f"→ plan.json: not in the FIRE target: {keep}")
    prof["schema"] = 16
    dump(pp, prof)
    print("→ profile.json: schema 16")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

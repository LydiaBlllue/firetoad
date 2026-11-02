#!/usr/bin/env python3
"""migrate_14to15.py — move a workspace from findata schema 14 to 15.

    python3 tools/migrate_14to15.py <workspace>

What changed in 15 (2026-11-02, FINANCE.md §3a): the tool uses the page's words.
  - In `funds.json`, the flow kind `allowance` becomes `everyday`, its name becomes Everyday, and the
    word in the plan's notes follows.
  - In `plan.json` `categoryGroups`, `fixed` becomes `bills` and `time` becomes `education`.
  - `profile.json` becomes "schema": 15.

Safe to run twice: a workspace already at 15 is left alone. History is not rewritten.
"""
import json
import os
import re
import sys

TOOL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", "update-dashboard", "scripts"))
import layout  # noqa: E402

WORDS = [(r"\bEveryday allowance\b", "Everyday"), (r"\beveryday allowance\b", "everyday amount"),
         (r"\bthe allowance\b", "the everyday amount"), (r"\bThe allowance\b", "The everyday amount"),
         (r"\bof allowance\b", "of everyday"), (r"\bone allowance\b", "one everyday amount"),
         (r"\ballowance\b", "everyday"), (r"\bAllowance\b", "Everyday")]


def dump(path, obj):
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(path, "a", encoding="utf-8").write("\n")


def reword(v):
    if isinstance(v, str):
        for a, b in WORDS:
            v = re.sub(a, b, v)
        return v
    if isinstance(v, list):
        return [reword(x) for x in v]
    if isinstance(v, dict):
        return {k: reword(x) for k, x in v.items()}
    return v


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    ws = os.path.abspath(argv[1])
    pp = layout.path(ws, "profile.json")
    if not os.path.exists(pp):
        print(f"no profile.json under {ws}"); return 2
    prof = json.load(open(pp, encoding="utf-8"))
    have = int(prof.get("schema", 2))
    if have >= 15:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 14:
        print(f"findata/ is schema {have}; this script only moves 14 → 15 (run tools/migrate.py)"); return 2

    fp = layout.path(ws, "funds.json")
    if os.path.exists(fp):
        dump(fp, reword(json.load(open(fp, encoding="utf-8"))))
        print("→ funds.json: the allowance flow is everyday")
    lp = layout.path(ws, "plan.json")
    if os.path.exists(lp):
        plan = json.load(open(lp, encoding="utf-8"))
        names = {"fixed": "bills", "time": "education"}
        if plan.get("categoryGroups"):
            plan["categoryGroups"] = {k: names.get(v, v) for k, v in plan["categoryGroups"].items()}
            dump(lp, plan)
            print("→ plan.json: categoryGroups renamed")
    prof["schema"] = 15
    dump(pp, prof)
    print("→ profile.json: schema 15")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

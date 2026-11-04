#!/usr/bin/env python3
"""migrate_17to18.py — move a workspace from findata schema 17 to 18.

    python3 tools/migrate_17to18.py <workspace>

What changed in 18 (2026-11-02, FINANCE.md §3b): the preset funds are gone. From `funds.json`: the
`funds` list, any saving flow that names one, and the leftover routing and claim notes. What is
removed is kept, whole, in `decisions/2026-11-02-funds-parked.json`, so custom funds can start from
it. The workspace's figures table loses its goal row. `profile.json` becomes "schema": 18.

Safe to run twice: a workspace already at 18 is left alone.
"""
import json
import os
import re
import sys

TOOL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", "update-dashboard", "scripts"))
import layout  # noqa: E402

PLAN_KEYS = ("leftover", "leftoverGoesTo", "leftoverNote", "zh_leftover")


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
    if have >= 18:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 17:
        print(f"findata/ is schema {have}; this script only moves 17 → 18 (run tools/migrate.py)"); return 2

    fp = layout.path(ws, "funds.json")
    if os.path.exists(fp):
        fj = json.load(open(fp, encoding="utf-8"))
        plan = fj.get("plan") or {}
        funds = fj.pop("funds", [])
        extra = {k: fj.pop(k) for k in list(fj) if k in ("claimsAgainst",)}
        keys = {f.get("key") for f in funds}
        flows = [f for f in plan.get("flows", []) if f.get("to") in keys]
        plan["flows"] = [f for f in plan.get("flows", []) if f.get("to") not in keys]
        notes = {k: plan.pop(k) for k in PLAN_KEYS if k in plan}
        if funds or flows or notes:
            os.makedirs(os.path.join(ws, "decisions"), exist_ok=True)
            dump(os.path.join(ws, "decisions", "2026-11-02-funds-parked.json"),
                 {"why": "The preset funds left the tool on 2026-11-02 (schema 18). Custom funds are on the roadmap. "
                         "This is what the workspace had.", "plan": notes, "flows": flows, "funds": funds, **extra})
        if fj.get("asof_note"):
            fj["asof_note"] = fj["asof_note"].replace(", two named funds", "")
        dump(fp, fj)
        print(f"→ funds.json: removed {len(funds)} fund(s), {len(flows)} flow(s); kept in decisions/")
    tp = os.path.join(ws, "FINANCE.md")
    if os.path.exists(tp):
        t = open(tp, encoding="utf-8").read()
        open(tp, "w", encoding="utf-8").write(re.sub(r"\| travel_goal \|.*\n", "", t))
    prof["schema"] = 18
    dump(pp, prof)
    print("→ profile.json: schema 18")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

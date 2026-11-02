#!/usr/bin/env python3
"""migrate_16to17.py — move a workspace from findata schema 16 to 17.

    python3 tools/migrate_16to17.py <workspace>

What changed in 17 (2026-11-02, FINANCE.md §3a): big buys are gone for now. From `funds.json`:
`plan.bigThreshold` and its notes, the fund with `role: "big"`, and any saving flow that names it.
What is removed is kept, whole, in `decisions/2026-11-02-big-buys-parked.json`, so the owner's fund
can come back with the feature. `profile.json` becomes "schema": 17.

Safe to run twice: a workspace already at 17 is left alone.
"""
import json
import os
import re
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
    if have >= 17:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 16:
        print(f"findata/ is schema {have}; this script only moves 16 → 17 (run tools/migrate.py)"); return 2

    fp = layout.path(ws, "funds.json")
    if os.path.exists(fp):
        fj = json.load(open(fp, encoding="utf-8"))
        plan = fj.get("plan") or {}
        big = [f for f in fj.get("funds", []) if f.get("role") == "big"]
        keys = {f.get("key") for f in big}
        flows = [f for f in plan.get("flows", []) if f.get("to") in keys]
        notes = {k: plan.pop(k) for k in list(plan) if k in ("bigThreshold", "bigThresholdNote", "zh_bigThreshold")}
        plan["flows"] = [f for f in plan.get("flows", []) if f.get("to") not in keys]
        fj["funds"] = [f for f in fj.get("funds", []) if f.get("role") != "big"]
        if plan.get("leftoverNote"):
            plan["leftoverNote"] = plan["leftoverNote"].replace("to the funds,", "to the fund,").replace(
                "takes from Big buys first, then Travel.", "takes from it.")
        for f in fj["funds"]:
            n = (f.get("backing") or {}).get("note")
            if n:
                f["backing"]["note"] = re.sub(r" and part of it Big buys", "", n)
        if big or flows or notes:
            os.makedirs(os.path.join(ws, "decisions"), exist_ok=True)
            dump(os.path.join(ws, "decisions", "2026-11-02-big-buys-parked.json"),
                 {"why": "Big buys left the tool on 2026-11-02 until the basics are done (schema 17). This is what the "
                         "workspace had, kept so it can come back.", "plan": notes, "flows": flows, "funds": big})
        dump(fp, fj)
        print(f"→ funds.json: removed {len(big)} fund(s), {len(flows)} flow(s); kept in decisions/")
    prof["schema"] = 17
    dump(pp, prof)
    print("→ profile.json: schema 17")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

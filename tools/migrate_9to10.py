#!/usr/bin/env python3
"""migrate_9to10.py — move a workspace from findata schema 9 to 10.

    python3 tools/migrate_9to10.py <workspace>

What changed in 10 (2026-10-28, FINANCE.md §8a):
  - Every balance is signed from the owner's side: what she has is positive, what she owes is
    negative. The register already wrote it that way; `banks.json` `debts` wrote a card's balance
    as the amount owed, so a card paid past zero came out negative there and was read back as a
    debt. Each `debts` balance is negated.
  - A stated liability in the register (a mortgage typed by hand) written as a positive amount
    owed is negated the same way.
  - `profile.json` becomes "schema": 10.

Safe to run twice: a workspace already at 10 is left alone.
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
    if have >= 10:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 9:
        print(f"findata/ is schema {have}; this script only moves 9 → 10 (run tools/migrate.py)"); return 2

    bp = layout.path(ws, "banks.json")
    if os.path.exists(bp):
        bank = json.load(open(bp, encoding="utf-8"))
        for x in bank.get("debts", []):
            if x.get("balance") is not None:
                was = x["balance"]
                x["balance"] = -was
                print(f"→ banks.json {x['account']}: {was} → {x['balance']}")
        dump(bp, bank)

    ap = layout.path(ws, "accounts.json")
    if os.path.exists(ap):
        reg = json.load(open(ap, encoding="utf-8"))
        hit = False
        for a in reg.get("accounts", []):
            if a.get("side") == "liability" and a.get("src") != "banks.json" and (a.get("balance") or 0) > 0:
                print(f"→ accounts.json {a['key']}: {a['balance']} owed → {-a['balance']}")
                a["balance"] = -a["balance"]; hit = True
        if hit:
            dump(ap, reg)

    prof["schema"] = 10
    dump(pp, prof)
    print("→ profile.json schema 10")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

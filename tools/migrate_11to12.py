#!/usr/bin/env python3
"""migrate_11to12.py — move a workspace from findata schema 11 to 12.

    python3 tools/migrate_11to12.py <workspace>

What changed in 12 (2026-10-30, FINANCE.md §3a):
  - The move to fifteen categories (schema 11) re-filed only the merchants that had been
    Subscription. Every other merchant stayed in the seven categories it was filed under, so a
    dentist sat in Other, a pharmacy in Shopping and a phone plan in Other, and the new categories
    stayed empty. Each merchant in merchants.json is now held against the starter map; where the
    map names a different category, the merchant is put in the To confirm queue (decisions.json)
    with that category as `suggest`. Nothing is re-filed until the owner confirms: `confirm.py`
    shows the suggestion beside what it is filed as, and `--ok` takes it.
  - An item already open for the same merchant takes the suggestion instead of a second row.
  - `profile.json` becomes "schema": 12.

Safe to run twice: a workspace already at 12 is left alone.
"""
import datetime
import json
import os
import sys

TOOL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", "update-dashboard", "scripts"))
import layout  # noqa: E402
from update import starter_category  # noqa: E402  the import's own rule


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
    if have >= 12:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 11:
        print(f"findata/ is schema {have}; this script only moves 11 → 12 (run tools/migrate.py)"); return 2
    today = datetime.date.today().isoformat()

    mp = layout.path(ws, "merchants.json")
    merchants = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"merchants": []}
    dp = layout.path(ws, "decisions.json")
    dec = json.load(open(dp, encoding="utf-8")) if os.path.exists(dp) else {"decisions": []}
    open_items = {d.get("match"): d for d in dec.setdefault("decisions", [])
                  if d.get("status") == "open" and d.get("kind") == "merchant" and d.get("match")}

    asked = 0
    for e in merchants.get("merchants", []):
        k, filed = e["match"], e.get("category")
        cat = starter_category(k)
        if not cat or cat == filed:
            continue
        d = open_items.get(k)
        if d:
            if d.get("default") == cat:
                continue
            d["suggest"] = cat
        else:
            dec["decisions"].append({
                "added": today, "kind": "merchant", "match": k,
                "what": f"{k} is filed as {filed}. With fifteen categories it fits {cat} better; "
                        f"it stays {filed} until confirmed.",
                "default": filed, "suggest": cat, "source": "the move to fifteen categories",
                "status": "open"})
        asked += 1
        print(f"→ {k}: {filed} → {cat}? (to confirm)")
    print(f"→ decisions.json: {asked} merchant(s) suggested a better category")

    if asked:
        dump(dp, dec)
    prof["schema"] = 12
    dump(pp, prof)
    print("→ profile.json schema 12")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

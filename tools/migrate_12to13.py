#!/usr/bin/env python3
"""migrate_12to13.py — move a workspace from findata schema 12 to 13.

    python3 tools/migrate_12to13.py <workspace>

What changed in 13 (2026-10-30, FINANCE.md §2):
  - A card's cash back is income, filed into `rewards.csv` by the import. A redemption imported
    before that was left out of spending and out of income, so it is in no figure. Every card
    statement already in `archive/` is read again by its parser, and each credit that names cash
    back or a redemption, and is not in `rewards.csv` yet, is written there with its statement's
    tag. A statement the parser cannot read, or that does not reconcile, is skipped and named.
  - `profile.json` becomes "schema": 13.

Safe to run twice: a workspace already at 13 is left alone, and a reward already filed is never
written again.
"""
import csv
import datetime
import json
import os
import re
import sys

TOOL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", "update-dashboard"))
sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", "update-dashboard", "scripts"))
import layout  # noqa: E402
from update import REWARD, REWARD_COLS, stamp  # noqa: E402  the import's own rule
from parsers import ParserUnavailable, parse  # noqa: E402


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
    if have >= 13:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 12:
        print(f"findata/ is schema {have}; this script only moves 12 → 13 (run tools/migrate.py)"); return 2

    reg = json.load(open(layout.path(ws, "accounts.json"), encoding="utf-8"))
    by_key = {a["key"]: a for a in reg.get("accounts", [])}
    rp = layout.path(ws, "rewards.csv")
    have_rows = list(csv.DictReader(open(rp, encoding="utf-8"))) if os.path.exists(rp) else []
    filed = {(r["date"], f"{float(r['amount']):.2f}", r["note"].rsplit("[", 1)[-1]) for r in have_rows}
    arc = os.path.join(ws, "archive")
    new, skipped = [], []
    for doc in reg.get("documents", []):
        acc = by_key.get((doc.get("covers") or [None])[0]) or {}
        if not doc.get("parser") or not acc.get("spendTag") or acc.get("ledger"):
            continue                                    # cards only: their credits are not a ledger's
        for tag in doc.get("tags", []):
            for f in sorted(os.listdir(arc)) if os.path.isdir(arc) else []:
                if f"_{tag}_" not in f or not f.lower().endswith(".pdf"):
                    continue
                try:
                    res = parse(os.path.join(arc, f), doc["parser"])
                except ParserUnavailable as e:
                    print(f"  ✗ {e} — install it and run this again"); return 2
                except Exception as e:                  # a parser's refusal, or a file pypdf cannot open
                    skipped.append(f"{f}: {type(e).__name__}: {e}"); continue
                if not res["reconcile"]["ok"]:
                    skipped.append(f"{f}: does not reconcile"); continue
                for part in (res.get("accounts") or [res]):
                    end = datetime.date.fromisoformat(part["period"]["to"])
                    tagend = f"[{acc['spendTag']}/{stamp(end)}]"
                    for r in part["rows"]:
                        amt = round(float(r["amount"]), 2)
                        desc = r["description"].strip()
                        if amt > 0 and REWARD.search(desc) and (r["date"], f"{amt:.2f}", tagend[1:]) not in filed:
                            filed.add((r["date"], f"{amt:.2f}", tagend[1:]))
                            new.append([r["date"], f"{amt:.2f}", acc.get("cur", "CAD"), f"{desc} {tagend}"])
                            print(f"→ {r['date']} {amt:,.2f} {desc[:40]!r} → rewards.csv")
    if new:
        fresh = not os.path.exists(rp) or os.path.getsize(rp) == 0
        with open(rp, "a", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            if fresh:
                w.writerow(REWARD_COLS)
            w.writerows(sorted(new))
    for s in skipped:
        print(f"  · skipped {s}")
    print(f"→ rewards.csv: {len(new)} reward(s) found in statements already filed")

    prof["schema"] = 13
    dump(pp, prof)
    print("→ profile.json: schema 13")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

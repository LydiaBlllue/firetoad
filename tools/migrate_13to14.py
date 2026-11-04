#!/usr/bin/env python3
"""migrate_13to14.py — move a workspace from findata schema 13 to 14.

    python3 tools/migrate_13to14.py <workspace>

What changed in 14 (2026-11-02, FINANCE.md §3a):
  - Every chequing account carries a `spendTag`. Setup gave one only when the first statements
    showed a debit purchase, and the import skipped a bill or cash withdrawal on an account
    without one, so those were in no figure. The account's statement tag becomes its spending tag.
  - Each ledger row typed as spending and not in `spending.csv` is written there, the way the import
    would have. A merchant nobody has decided goes to `merchants.json` and waits to be confirmed.
  - `profile.json` becomes "schema": 14.

Safe to run twice: a workspace already at 14 is left alone, and a row already filed is never
written again.
"""
import collections
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
from update import SPENT, merchant_key, merchant_of_debit, payee_of, starter_category  # noqa: E402  the import's own rules


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
    if have >= 14:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 13:
        print(f"findata/ is schema {have}; this script only moves 13 → 14 (run tools/migrate.py)"); return 2

    rp = layout.path(ws, "accounts.json")
    reg = json.load(open(rp, encoding="utf-8"))
    sp = layout.path(ws, "spending.csv")
    rows = list(csv.DictReader(open(sp, encoding="utf-8"))) if os.path.exists(sp) else []
    cols = list(rows[0]) if rows else ["date", "amount", "currency", "category", "note"]
    filed = collections.Counter()
    for r in rows:
        m = re.search(r"\[([^/\]]+)/", r["note"])
        filed[(m.group(1) if m else "", r["date"], f"{float(r['amount']):.2f}")] += 1
    mp = layout.path(ws, "merchants.json")
    merchants = json.load(open(mp, encoding="utf-8"))
    table = {e["match"]: e for e in merchants.get("merchants", [])}
    dp = layout.path(ws, "decisions.json")
    decisions = json.load(open(dp, encoding="utf-8")) if os.path.exists(dp) else {"decisions": []}
    today = datetime.date.today().isoformat()

    new = []
    for a in reg.get("accounts", []):
        lp = layout.path(ws, a["ledger"]) if a.get("ledger") else None
        if not lp or not os.path.exists(lp):
            continue
        ledger = list(csv.DictReader(open(lp, encoding="utf-8")))
        # a fee given back is a refund of the fee, as in the import: a negative row
        spends = [r for r in ledger if r.get("type") in SPENT and (float(r.get("amount") or 0) < 0 or r["type"] == "Fee")]
        if a["kind"] != "Chequing" and not spends:
            continue
        if not a.get("spendTag"):
            a["spendTag"] = a.get("stmtTag") or a["key"]
            print(f"→ {a['name']}: spendTag {a['spendTag']}")
        tag = a["spendTag"]
        for r in spends:
            amt = -float(r["amount"])
            k = (tag, r["date"], f"{amt:.2f}")
            if filed[k] > 0:
                filed[k] -= 1
                continue
            t = r["type"]
            who = merchant_of_debit(r["description"]) if t == "Debit purchase" else payee_of(r["description"])
            key = merchant_key(who)
            if key in table:
                cat = table[key]["category"]
                table[key]["seen"] = table[key].get("seen", 0) + 1
                table[key]["last"] = max(table[key].get("last", r["date"]), r["date"])
            else:
                cat = starter_category(key) or ("Housing" if t == "Bill" and re.search(r"TAX", who, re.I) else SPENT[t] or "Other")
                table[key] = {"match": key, "category": cat, "seen": 1, "first": r["date"], "last": r["date"]}
                merchants.setdefault("merchants", []).append(table[key])
                decisions["decisions"].append({"added": today, "kind": "merchant", "match": key,
                                               "what": f"{key}, seen for the first time.", "default": cat,
                                               "source": f"{a['name']} ledger, {r['date']}", "status": "open"})
            stmt = (r.get("statement") or "").rsplit("/", 1)[-1]
            way = "debit" if t == "Debit purchase" else "chequing"
            new.append({"date": r["date"], "amount": f"{amt:.2f}", "currency": a.get("cur", "CAD"), "category": cat,
                        "note": f"{who} ({way}) [{tag}/{stmt}]"})
    if new:
        with open(sp, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(sorted(rows + new, key=lambda r: r["date"]))
        dump(mp, merchants)
        dump(dp, decisions)
    dump(rp, reg)
    print(f"→ spending.csv: {len(new)} row(s) filed, ${sum(float(r['amount']) for r in new):,.2f}")

    prof["schema"] = 14
    dump(pp, prof)
    print("→ profile.json: schema 14")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

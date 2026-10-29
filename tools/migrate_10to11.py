#!/usr/bin/env python3
"""migrate_10to11.py — move a workspace from findata schema 10 to 11.

    python3 tools/migrate_10to11.py <workspace>

What changed in 11 (2026-10-29, FINANCE.md §3a):
  - Spending is what it is, not how it was paid. A chequing row the ledger types Rent, Bill,
    Payment, Cash, Fee or (charged) Interest is spending as well, and gets its row in
    spending.csv, in its account's spending tag, the way a debit purchase always had. A fee given
    back is a negative Fees row.
  - Subscription is no longer a category: it said how a charge was paid, not what it bought. Each
    merchant filed there moves to the starter map's category for it, or to Other, and is put in
    the To confirm queue (decisions.json) with that as the default. Whether a charge repeats is
    now measured by the page.
  - `profile.json` becomes "schema": 11.

Safe to run twice: a workspace already at 11 is left alone.
"""
import csv
import datetime
import json
import os
import re
import sys

TOOL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", "update-dashboard", "scripts"))
import layout  # noqa: E402
from update import SPENT, payee_of, starter_category  # noqa: E402  the import's own rules
sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", "workspace-checks", "scripts"))
from check_data import merchant_key  # noqa: E402

COLS = ["date", "amount", "currency", "category", "note"]


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
    if have >= 11:
        print(f"findata/ is already schema {have}; nothing to do"); return 0
    if have != 10:
        print(f"findata/ is schema {have}; this script only moves 10 → 11 (run tools/migrate.py)"); return 2
    today = datetime.date.today().isoformat()

    sp_path = layout.path(ws, "spending.csv")
    spend = list(csv.DictReader(open(sp_path, encoding="utf-8"))) if os.path.exists(sp_path) else []
    mp = layout.path(ws, "merchants.json")
    merchants = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {"merchants": []}
    table = {e["match"]: e for e in merchants.setdefault("merchants", [])}
    dp = layout.path(ws, "decisions.json")
    dec = json.load(open(dp, encoding="utf-8")) if os.path.exists(dp) else {"decisions": []}

    # 1. Subscription → what the merchant sells, asked
    moved = {}
    for r in spend:
        if r["category"] == "Subscription":
            k = merchant_key(r["note"])
            if k not in moved:
                moved[k] = starter_category(k) or "Other"
            r["category"] = moved[k]
    for e in merchants["merchants"]:
        if e.get("category") == "Subscription":
            moved.setdefault(e["match"], starter_category(e["match"]) or "Other")
            e["category"] = moved[e["match"]]
    for k, cat in sorted(moved.items()):
        dec.setdefault("decisions", []).append({
            "added": today, "kind": "merchant", "match": k,
            "what": f"{k} was filed as Subscription, which is no longer a category: a charge that "
                    f"repeats is marked as one whatever it bought. It is filed as {cat} meanwhile.",
            "default": cat, "source": "the move to fifteen categories", "status": "open"})
        print(f"→ {k}: Subscription → {cat} (to confirm)")

    # 2. chequing rows that are spending
    have_rows = {(r["date"], f"{float(r['amount']):.2f}", r["note"]) for r in spend}
    reg = json.load(open(layout.path(ws, "accounts.json"), encoding="utf-8"))
    added = 0
    for a in reg.get("accounts", []):
        lp = layout.path(ws, a["ledger"]) if a.get("ledger") else None
        if not (lp and a.get("spendTag") and os.path.exists(lp)):
            continue
        for r in csv.DictReader(open(lp, encoding="utf-8")):
            t, amt = r.get("type"), float(r["amount"])
            if t not in SPENT or t == "Debit purchase" or not (amt < 0 or t == "Fee"):
                continue
            payee = payee_of(r["description"])
            key = merchant_key(payee)
            if key in table:
                cat = table[key]["category"]
            elif t in ("Bill", "Payment"):
                cat = starter_category(key) or ("Housing" if t == "Bill" and re.search("TAX", key) else SPENT[t])
            else:
                cat = SPENT[t]
            m = re.search(r"/(\d{8})$", r.get("statement") or "")
            if not m:
                continue
            note = f"{payee} (chequing) [{a['spendTag']}/{m.group(1)}]"
            row = (r["date"], f"{-amt:.2f}", note)
            if row in have_rows:
                continue
            spend.append({"date": r["date"], "amount": f"{-amt:.2f}", "currency": a.get("cur", "CAD"),
                          "category": cat, "note": note})
            have_rows.add(row); added += 1
            e = table.get(key)
            if e is None:
                e = table[key] = {"match": key, "category": cat, "seen": 0, "first": r["date"], "last": r["date"]}
                merchants["merchants"].append(e)
            e["seen"] = int(e.get("seen") or 0) + 1
            e["first"] = min(e.get("first") or r["date"], r["date"])
            e["last"] = max(e.get("last") or r["date"], r["date"])
    print(f"→ spending.csv: {added} chequing row(s) that are spending (rent, bills, cash, fees) added")

    spend.sort(key=lambda r: (r["date"], r["note"]))
    with open(sp_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(spend)
    merchants["merchants"].sort(key=lambda e: e["match"])
    for k in ("rules",):
        if isinstance(merchants.get(k), list):
            merchants[k] = [x for x in merchants[k] if "Subscription means" not in x] + \
                ["Subscription is not a category: a charge that repeats is marked by the page, whatever it bought."]
    dump(mp, merchants)
    if moved:
        dump(dp, dec)
    prof["schema"] = 11
    dump(pp, prof)
    print("→ profile.json schema 11")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

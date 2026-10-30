"""confirm.py — every open question from the imports, in one table, answered at once.

A first import asks about every merchant it has not seen. One question at a time was 104
questions for the first person to set this up, and they gave up and asked why nothing was sorted
(2026-10-28, first user). The starter map now files a common chain under its category by itself;
this puts what is left in one numbered table, so the owner can say "all fine" or "3 is Shopping,
the rest are fine" in one breath.

    python3 .claude/skills/update-dashboard/scripts/confirm.py .                  # the table
    python3 .claude/skills/update-dashboard/scripts/confirm.py . --write --ok     # all as filed
    python3 .claude/skills/update-dashboard/scripts/confirm.py . --write --ok --set 3=Shopping \
        --set "AMZN MKTP=Shopping"                                                 # some changed

`--set` takes a row number or a merchant and a category (its key or its name: Family or "Family &
gifts"); `--ok` confirms every other open item as it was filed, or, where the item carries a
suggestion (the move to fifteen categories left some merchants in a category that fits them
less well), as suggested. A merchant's answer lands in
merchants.json and in every spending.csv row of that merchant, and the item is closed in
decisions.json (`answer`, `resolved`). A transfer sent to someone nobody named can be answered
with a category too -- money to family, rent -- and is then written to spending.csv as well
(FINANCE.md §3a). Money that came in from no named sender is answered with what it was (Pay, Family or gift, Other
income, Own money, Paid back) and its ledger row is retyped; a same-size e-Transfer that came in month after
month is suggested as Pay. A file is confirmed only as it was assumed. Then the page is rebuilt.
"""
import argparse, csv, datetime, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "workspace-checks", "scripts"))
from check_data import merchant_key  # noqa: E402  the one definition
import categories  # noqa: E402
from update import jload, jsave, csv_rows  # noqa: E402

SEEN = re.compile(r"^(.*?), seen for the first time\.")
# what money coming in from no named sender can be: the ledger type, and how it is said
INCOMING = {"Payroll": "Pay", "Gift": "Family or gift", "Other": "Other income", "Transfer": "Own money", "Repayment": "Paid back"}


def merchant_of(item):
    if item.get("match"):
        return item["match"]
    m = SEEN.match(item.get("what") or "")
    return m.group(1) if m else None


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--ok", action="store_true", help="confirm every item not --set as suggested, or as it was filed")
    ap.add_argument("--set", action="append", default=[], metavar="N=CATEGORY")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    fd = lambda n: layout.path(root, n)

    dec = jload(fd("decisions.json"), {"decisions": []})
    items = [d for d in dec.get("decisions", []) if d.get("status") == "open"]
    if not items:
        print("Nothing is waiting to be confirmed.")
        return 0
    merchants = jload(fd("merchants.json"), {"merchants": []})
    table = {e["match"]: e for e in merchants.get("merchants", [])}
    spend = csv_rows(fd("spending.csv"))
    count = {}
    for r in spend:
        if float(r["amount"]) > 0:
            k = merchant_key(r["note"])
            count[k] = count.get(k, 0) + 1

    print(f"=== to confirm — {len(items)} item(s) ===")
    print(f"  {'#':>3}  {'what':<38} {'filed as':<14} {'suggested':<14} {'seen':>4}  why")
    for i, d in enumerate(items, 1):
        k = merchant_of(d) if d.get("kind") == "merchant" else None
        what = k or d.get("what", "")
        w = d.get("what") or ""
        why = "starter map" if "starter map" in w else "was Subscription" if "no longer a category" in w \
            else "same amount each month" if d.get("credit") and d.get("suggest") \
            else "fits better" if d.get("suggest") else ("first time" if k else d.get("kind", ""))
        print(f"  {i:>3}  {what[:38]:<38} {str(d.get('default'))[:14]:<14} {str(d.get('suggest') or '')[:14]:<14} "
              f"{count.get(k, '') if k else '':>4}  {why}")

    # what the owner said
    want, bad = {}, []
    for s in a.set:
        if "=" not in s:
            bad.append(f"--set {s!r}: write it as N=Category or MERCHANT=Category"); continue
        who, said = (x.strip() for x in s.rsplit("=", 1))
        cat = next((k for k, n, *_ in categories.TABLE if said.lower() in (k.lower(), n.lower())), None)
        idx = int(who) - 1 if who.isdigit() else next((i for i, d in enumerate(items) if merchant_of(d) == who.upper()), None)
        if idx is not None and 0 <= idx < len(items) and items[idx].get("credit"):
            # money coming in is answered with what it was, not a category
            t = next((x for x in INCOMING if said.lower() in (x.lower(), INCOMING[x].lower())), None)
            if t is None:
                bad.append(f"--set {s!r}: #{idx + 1} is money coming in; say one of {', '.join(INCOMING)}")
            else:
                want[idx] = t
            continue
        if cat is None:
            bad.append(f"--set {s!r}: the category has to be one of {', '.join(categories.CATEGORIES)}")
        elif idx is None or not (0 <= idx < len(items)):
            bad.append(f"--set {s!r}: no open item {who}")
        elif items[idx].get("kind") == "transfer" and not items[idx].get("row"):
            bad.append(f"--set {s!r}: #{idx + 1} is money coming in, not spending — change it in its ledger")
        elif items[idx].get("kind") not in ("merchant", "transfer"):
            bad.append(f"--set {s!r}: #{idx + 1} is a {items[idx].get('kind')}, not a merchant — change it in its ledger")
        else:
            want[idx] = cat
    if bad:
        print()
        for b in bad:
            print(f"  ✗ {b}")
        return 1
    if not a.write:
        print("\n  nothing written. Say which to change, then run with --write --ok (and --set N=Category).")
        return 0

    today = datetime.date.today().isoformat()
    changed, closed = 0, 0
    for i, d in enumerate(items):
        if i not in want and not a.ok:
            continue
        ans = want.get(i, d.get("suggest") or d.get("default"))
        if d.get("kind") == "transfer" and i in want and d.get("row"):
            # spent after all: the ledger row stays a transfer out, and the money is spending
            r = d["row"]
            spend.append({"date": r["date"], "amount": f"{float(r['amount']):.2f}", "currency": r.get("cur", "CAD"),
                          "category": ans, "note": r["note"]})
            changed += 1
        if d.get("kind") == "merchant":
            k = merchant_of(d)
            if k in table:
                table[k]["category"] = ans
            else:
                merchants.setdefault("merchants", []).append({"match": k, "category": ans})
            for r in spend:
                rk = merchant_key(r["note"])
                # a refund follows what it refunds ("ANNUAL FEE REBATE" is the annual fee's)
                mine = rk == k or (k and float(r["amount"]) < 0 and rk.startswith(k + " "))
                if mine and r["category"] != ans:
                    r["category"] = ans; changed += 1
        if d.get("credit"):
            t = "Other" if ans == "Other income" else ans
            if t in INCOMING:
                c = d["credit"]
                lp = fd(c["ledger"])
                rows = csv_rows(lp)
                for r in rows:
                    if r.get("statement") == c["statement"] and r.get("date") == c["date"] \
                            and abs(float(r["amount"]) - c["amount"]) < 0.005 and r.get("type") != t:
                        r["type"] = t
                        r["label"] = {"Payroll": "Pay (e-Transfer)", "Gift": "e-Transfer received (family or gift)", "Other": "e-Transfer received",
                                      "Transfer": "e-Transfer between your own accounts",
                                      "Repayment": "Paid back (e-Transfer)"}[t]
                        changed += 1
                        break
                with open(lp, "w", encoding="utf-8", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        d["answer"], d["resolved"], d["status"] = ans, today, "confirmed"
        closed += 1
    jsave(fd("merchants.json"), merchants)
    jsave(fd("decisions.json"), dec)
    with open(fd("spending.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "amount", "currency", "category", "note"])
        w.writeheader()
        w.writerows(spend)
    for script, args in (("rebuild.py", [".", "--write"]), ("preflight.py", [".", "--reseed"])):
        subprocess.run([sys.executable, os.path.join(HERE, script)] + args, cwd=root, capture_output=True, text=True)
    print(f"\n  {closed} confirmed, {changed} purchase(s) moved to the category given; the page is rebuilt.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

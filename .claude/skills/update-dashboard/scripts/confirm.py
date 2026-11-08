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
import jlock  # noqa: E402  one writer at a time, both doors
import verbs  # noqa: E402
from update import jload, jsave, csv_rows, sender_of  # noqa: E402

SEEN = re.compile(r"^(.*?), seen for the first time\.")
# what money coming in from no named sender can be: the ledger type, and how it is said
INCOMING = {"Payroll": "Pay", "Gift": "Family or gift", "Other": "Other income", "Transfer": "Own money", "Repayment": "Paid back"}


def merchant_of(item):
    if item.get("match"):
        return item["match"]
    m = SEEN.match(item.get("what") or "")
    return m.group(1) if m else None


def _file_merchant(k, ans, table, merchants, spend):
    """One merchant into one category: its merchants.json entry and every spending row of it
    (a refund follows what it refunds — "ANNUAL FEE REBATE" is the annual fee's). Returns how
    many rows moved."""
    changed = 0
    if k in table:
        table[k]["category"] = ans
    else:
        e = {"match": k, "category": ans}
        merchants.setdefault("merchants", []).append(e)
        table[k] = e
    for r in spend:
        rk = merchant_key(r["note"])
        mine = rk == k or (k and float(r["amount"]) < 0 and rk.startswith(k + " "))
        if mine and r["category"] != ans:
            r["category"] = ans; changed += 1
    return changed


def remember_sender(root, who, t, today):
    """A named sender's answer, kept as their rule in register/senders.json, so the next
    e-Transfer from them is typed and not asked (the rule the owner used to keep in prose).
    A statement that prints no name (BMO) leaves nothing to remember."""
    who = (who or "").strip().upper()
    if not who or t not in INCOMING:
        return False
    p = layout.path(os.path.abspath(root), "senders.json")
    sj = jload(p, {}) or {}
    sj.setdefault("note", "Who sends you money and what it is, answered once: `match` is the name as the statement prints it, "
                          "`type` one of Payroll / Gift / Other / Transfer / Repayment. The import types the next "
                          "e-Transfer from them by this and does not ask; change a line to change your mind.")
    rows = sj.setdefault("senders", [])
    for s in rows:
        if s.get("match", "").upper() == who:
            s["type"], s["asof"] = t, today
            break
    else:
        rows.append({"match": who, "type": t, "asof": today})
    jsave(p, sj)
    return True


def _after_write(root):
    for script, args in (("rebuild.py", [".", "--write"]), ("preflight.py", [".", "--reseed"])):
        subprocess.run([sys.executable, os.path.join(HERE, script)] + args, cwd=root, capture_output=True, text=True)


def merchants(root):
    """Every merchant already filed, with what it comes to: for the panel's "change one" list.
    [{match, category, seen, amount}], biggest first."""
    root = os.path.abspath(root)
    fd = lambda n: layout.path(root, n)
    table = jload(fd("merchants.json"), {"merchants": []}).get("merchants", [])
    spend = csv_rows(fd("spending.csv"))
    count, total = {}, {}
    for r in spend:
        if float(r["amount"]) > 0:
            k = merchant_key(r["note"])
            count[k] = count.get(k, 0) + 1
            total[k] = round(total.get(k, 0.0) + float(r["amount"]), 2)
    out = [{"match": e["match"], "category": e.get("category"), "seen": count.get(e["match"], 0), "amount": total.get(e["match"], 0.0)}
           for e in table if e.get("match")]
    out.sort(key=lambda x: -x["amount"])
    return out


def refile(root, match, category, write=False, say=None):
    """A merchant already filed, filed again (verbs.py): the owner changed their mind, or a first
    answer was wrong. merchants.json and every row of it follow; the page is rebuilt."""
    emit, lines = verbs.speaker(say)
    root = os.path.abspath(root)
    fd = lambda n: layout.path(root, n)
    res = {"match": match, "category": None, "changed": 0, "written": False}
    cat = next((k for k, n, *_ in categories.TABLE if str(category).lower() in (k.lower(), n.lower())), None)
    if cat is None:
        emit(f"  ✗ the category has to be one of {', '.join(categories.CATEGORIES)}")
        return verbs.result(res, 1, lines)
    res["category"] = cat
    merchants_ = jload(fd("merchants.json"), {"merchants": []})
    table = {e["match"]: e for e in merchants_.get("merchants", [])}
    if match not in table:
        emit(f"  ✗ {match!r} is not a merchant that has been filed")
        return verbs.result(res, 1, lines)
    spend = csv_rows(fd("spending.csv"))
    n = _file_merchant(match, cat, table, merchants_, spend)
    res["changed"] = n
    emit(f"=== refile — {match} → {cat}: {n} purchase(s) move ===")
    if not write:
        emit("  nothing written. Run with --write to apply.")
        return verbs.result(res, 0, lines)
    jsave(fd("merchants.json"), merchants_)
    with open(fd("spending.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "amount", "currency", "category", "note"])
        w.writeheader(); w.writerows(spend)
    _after_write(root)
    res["written"] = True
    emit("  written; the page is rebuilt.")
    return verbs.result(res, 0, lines)


def run(root, write=False, ok=False, sets=(), say=None):
    """The table of open items, the answers checked, and — with write — applied (verbs.py).
    `sets` are the `--set` strings. Returns rc, lines, `items` (the table rows), `bad` (what was
    refused), `closed` and `changed` (how many items and purchases moved)."""
    emit, lines = verbs.speaker(say)
    root = os.path.abspath(root)
    fd = lambda n: layout.path(root, n)
    res = {"items": [], "bad": [], "closed": 0, "changed": 0}

    dec = jload(fd("decisions.json"), {"decisions": []})
    items = [d for d in dec.get("decisions", []) if d.get("status") == "open"]
    # the item's place in decisions.json: a stable handle for a caller that answers one item at a
    # time (the panel saves each card as it is answered, 2026-11-07) — row numbers shift as items close
    ids = {id(d): i for i, d in enumerate(dec.get("decisions", []))}
    if not items:
        emit("Nothing is waiting to be confirmed.")
        return verbs.result(res, 0, lines)
    merchants = jload(fd("merchants.json"), {"merchants": []})
    table = {e["match"]: e for e in merchants.get("merchants", [])}
    spend = csv_rows(fd("spending.csv"))
    count, total = {}, {}
    for r in spend:
        if float(r["amount"]) > 0:
            k = merchant_key(r["note"])
            count[k] = count.get(k, 0) + 1
            total[k] = round(total.get(k, 0.0) + float(r["amount"]), 2)
    # what the whole of spending and its Other come to: the panel shows how much each answer moves
    spend_total = round(sum(float(r["amount"]) for r in spend if float(r["amount"]) > 0), 2)
    other_total = round(sum(float(r["amount"]) for r in spend if float(r["amount"]) > 0 and r.get("category") == "Other"), 2)
    res.update(spendTotal=spend_total, otherTotal=other_total)

    # Questions about money first, then merchants by how often they appear: the first rows settle the most.
    items.sort(key=lambda d: count.get(merchant_of(d), 0) * -1 if d.get("kind") == "merchant" else -10 ** 6)

    emit(f"=== to confirm — {len(items)} item(s) ===")
    emit(f"  {'#':>3}  {'what':<38} {'filed as':<14} {'suggested':<14} {'seen':>4}  why")
    for i, d in enumerate(items, 1):
        k = merchant_of(d) if d.get("kind") == "merchant" else None
        what = k or d.get("what", "")
        w = d.get("what") or ""
        why = "starter map" if "starter map" in w else "was Subscription" if "no longer a category" in w \
            else "same amount each month" if d.get("credit") and d.get("suggest") \
            else "fits better" if d.get("suggest") else ("first time" if k else d.get("kind", ""))
        emit(f"  {i:>3}  {what[:38]:<38} {str(d.get('default'))[:14]:<14} {str(d.get('suggest') or '')[:14]:<14} "
             f"{count.get(k, '') if k else '':>4}  {why}")
        # the one category other entries with the same first word carry, if one: the owner's own
        # earlier answer for the brand, offered first (update.categorise's "brand" rule, for the panel)
        first = k.split()[0] if k else ""
        kin = {e["category"] for kk, e in table.items() if first and kk.split()[0] == first and kk != k}
        res["items"].append({"n": i, "id": ids[id(d)], "kind": d.get("kind"), "what": what, "default": d.get("default"),
                             "suggest": d.get("suggest"), "seen": count.get(k, 0) if k else None, "why": why,
                             # what the item can be answered with (the panel's pills, local-app/panel.py):
                             # money in from no named sender, or a transfer out that may be spending
                             "credit": bool(d.get("credit")), "spent": bool(d.get("row")),
                             "suggestBy": d.get("suggestBy"),
                             "amount": total.get(k) if k else None, "brand": kin.pop() if len(kin) == 1 else None})

    # what the owner said
    want, bad = {}, res["bad"]
    for s in sets:
        if "=" not in s:
            bad.append(f"--set {s!r}: write it as N=Category or MERCHANT=Category"); continue
        who, said = (x.strip() for x in s.rsplit("=", 1))
        cat = next((k for k, n, *_ in categories.TABLE if said.lower() in (k.lower(), n.lower())), None)
        if who.startswith("id:") and who[3:].isdigit():
            idx = next((i for i, d in enumerate(items) if ids[id(d)] == int(who[3:])), None)
        else:
            idx = int(who) - 1 if who.isdigit() else next((i for i, d in enumerate(items) if merchant_of(d) == who.upper()), None)
        if idx is not None and 0 <= idx < len(items) and items[idx].get("kind") == "fire":
            # the FIRE goal is answered yes or no, and lands in plan.json
            yn = {"yes": "Yes", "y": "Yes", "no": "No", "n": "No"}.get(said.lower())
            if yn is None:
                bad.append(f"--set {s!r}: #{idx + 1} is the FIRE goal; say yes or no")
            else:
                want[idx] = yn
            continue
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
        emit()
        for b in bad:
            emit(f"  ✗ {b}")
        return verbs.result(res, 1, lines)
    if not write:
        emit("\n  nothing written. Say which to change, then run with --write --ok (and --set N=Category).")
        return verbs.result(res, 0, lines)
    other = jlock.held_by_other(root)
    if other:
        emit(jlock.refusal(other)); return verbs.result(res, 1, lines)

    today = datetime.date.today().isoformat()
    changed, closed = 0, 0
    for i, d in enumerate(items):
        if i not in want and not ok:
            continue
        ans = want.get(i, d.get("suggest") or d.get("default"))
        if d.get("kind") == "transfer" and i in want and d.get("row"):
            # spent after all: the ledger row stays a transfer out, and the money is spending
            r = d["row"]
            spend.append({"date": r["date"], "amount": f"{float(r['amount']):.2f}", "currency": r.get("cur", "CAD"),
                          "category": ans, "note": r["note"]})
            changed += 1
        if d.get("kind") == "merchant":
            changed += _file_merchant(merchant_of(d), ans, table, merchants, spend)
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
                remember_sender(root, d.get("sender") or sender_of(c.get("description") or ""), t, today)
        if d.get("kind") == "fire":
            pj = jload(fd("plan.json"), {})
            pj["fire"] = {"goal": ans == "Yes", "asked": today}
            jsave(fd("plan.json"), pj)
            changed += 1
        d["answer"], d["resolved"], d["status"] = ans, today, "confirmed"
        closed += 1
    jsave(fd("merchants.json"), merchants)
    jsave(fd("decisions.json"), dec)
    with open(fd("spending.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "amount", "currency", "category", "note"])
        w.writeheader()
        w.writerows(spend)
    _after_write(root)
    emit(f"\n  {closed} confirmed, {changed} purchase(s) moved to the category given; the page is rebuilt.")
    res.update(closed=closed, changed=changed)
    return verbs.result(res, 0, lines)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--ok", action="store_true", help="confirm every item not --set as suggested, or as it was filed")
    ap.add_argument("--set", action="append", default=[], metavar="N=CATEGORY")
    ap.add_argument("--refile", metavar="MERCHANT=CATEGORY", help="file a merchant already decided into another category")
    a = ap.parse_args(argv)
    if a.refile:
        who, _, cat = a.refile.rpartition("=")
        return refile(a.root, who.strip().upper(), cat.strip(), write=a.write, say=print)["rc"]
    return run(a.root, write=a.write, ok=a.ok, sets=a.set, say=print)["rc"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

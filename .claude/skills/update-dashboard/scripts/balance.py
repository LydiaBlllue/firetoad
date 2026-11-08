#!/usr/bin/env python3
"""balance.py — one balance no file carries, written where it lives.

Some accounts have no statement and no export: a broker's chequing account read off the app, a
bank abroad read off a screenshot. Their balance is a fact the owner states, and until now the
model wrote it into banks.json or foreign.json by hand. This is that write as a verb, so the
panel (local-app) and the skills do it the same way:

    python3 .claude/skills/update-dashboard/scripts/balance.py . ws-chq 1234.56                 # say what would change
    python3 .claude/skills/update-dashboard/scripts/balance.py . ws-chq 1234.56 --asof 2026-11-05 --write

The account is named by its register key (accounts.json `key`), never by position. What is
written depends on where the register says the balance lives (`src`):

  banks.json     the account's row (assets, or debts for a card, stored negative) — balance, asof;
                 refused for an account with a ledger, whose balance is the ledger's last row (D7)
  foreign.json   the account's row (matched by institution, as D14 matches it) — value, asof;
                 then the file's total, summary and asof are re-derived from its rows (D8)
  none           a loan: what is owed is derived from `agreed` and the ledgers (loans.py, D23),
                 so it is refused here — settle a new `agreed` instead

The register's own copy (`balance`, `asof`) follows, because D14 re-derives it from the source
and D20 wants a stated balance dated. The amount is in the account's own currency, as the app
shows it. Then the page is rebuilt and the money checks run, as after every write.
"""
import argparse
import datetime
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout  # noqa: E402
import jlock  # noqa: E402  one writer at a time, both doors
import verbs  # noqa: E402
from update import jload, jsave  # noqa: E402

CHECKS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "workspace-checks", "scripts")


def parse_amount(v):
    """A number the way an app prints it: '¥203,134.64', 'US$17.56', '1 065,33' all read."""
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    for junk in ("US$", "C$", "CA$", "$", "¥", "￥", "€", "£", "元", "CAD", "USD", "CNY"):
        s = s.replace(junk, "")
    s = s.replace(" ", "").replace(" ", "")
    if s.count(",") == 1 and "." not in s and len(s.split(",")[1]) != 3:
        s = s.replace(",", ".")        # a decimal comma
    s = s.replace(",", "")
    return float(s)


def run(root, key, amount, asof=None, write=False, say=None):
    """Write one stated balance (verbs.py). Returns rc, lines, and `key`, `name`, `src`,
    `before` / `after` ({balance, asof}), `written` and `findings` (the money checks' ✗ / ⚠ lines)."""
    emit, lines = verbs.speaker(say)
    root = os.path.abspath(root)
    fd = lambda n: layout.path(root, n)
    res = {"key": key, "name": None, "src": None, "before": None, "after": None, "written": False, "findings": []}

    reg = jload(fd("accounts.json"), {"accounts": []})
    acc = next((a for a in reg.get("accounts", []) if a.get("key") == key), None)
    if acc is None:
        emit(f"  ✗ no account with key {key!r} in the register")
        return verbs.result(res, 1, lines)
    res["name"], res["src"] = acc.get("name"), acc.get("src")
    try:
        amt = parse_amount(amount)
    except (TypeError, ValueError):
        emit(f"  ✗ {amount!r} is not an amount")
        return verbs.result(res, 1, lines)
    today = datetime.date.today()
    try:
        day = datetime.date.fromisoformat(str(asof)[:10]) if asof else today
    except ValueError:
        emit(f"  ✗ {asof!r} is not a date (YYYY-MM-DD)")
        return verbs.result(res, 1, lines)
    if day > today:
        emit(f"  ✗ {day} is in the future")
        return verbs.result(res, 1, lines)
    asof = day.isoformat()
    who = f"{acc.get('inst')} {acc.get('name')}"
    src = acc.get("src")
    if acc.get("ledger"):
        emit(f"  ✗ {who} has a ledger ({acc['ledger']}): its balance is that ledger's last row and moves only with "
             f"a statement (D7). A balance typed over it would contradict the books.")
        return verbs.result(res, 1, lines)

    if src == "banks.json":
        banks = jload(fd("banks.json"), {"assets": [], "debts": []})
        side = "debts" if acc.get("side") == "liability" else "assets"
        row = next((x for x in banks.get(side, []) if x.get("account") == acc.get("name")
                    and (not x.get("inst") or x.get("inst") == acc.get("inst"))), None)
        if row is None:
            emit(f"  ✗ {who}: no row in banks.json {side} matches it — the register and the file disagree (D14)")
            return verbs.result(res, 1, lines)
        new = -abs(amt) if side == "debts" else amt
        res["before"] = {"balance": row.get("balance"), "asof": row.get("asof")}
        res["after"] = {"balance": new, "asof": asof}
        if write:
            row["balance"], row["asof"] = new, asof
            jsave(fd("banks.json"), banks)
    elif src == "foreign.json":
        fj = jload(fd("foreign.json"), {"accounts": []})
        rows = [x for x in fj.get("accounts", []) if x.get("inst") == acc.get("inst")]
        if len(rows) != 1:
            emit(f"  ✗ {who}: {len(rows)} rows in foreign.json carry this institution; it has to be exactly one to write to")
            return verbs.result(res, 1, lines)
        row = rows[0]
        res["before"] = {"balance": row.get("value"), "asof": row.get("asof")}
        res["after"] = {"balance": amt, "asof": asof}
        if write:
            row["value"], row["asof"] = amt, asof
            accts = fj.get("accounts", [])
            fj["total"] = round(sum(float(x.get("value") or 0) for x in accts), 2)
            cash = round(sum(float(x.get("value") or 0) for x in accts if x.get("type") == "cash"), 2)
            fj["summary"] = {"cash": cash, "invested": round(fj["total"] - cash, 2),
                             "cash_share_pct": round(cash / fj["total"] * 100, 1) if fj["total"] else 0}
            fj["asof"] = max([x.get("asof") or "" for x in accts] + [fj.get("asof") or ""])
            jsave(fd("foreign.json"), fj)
    elif acc.get("role") == "owed" or acc.get("agreed"):
        emit(f"  ✗ {who} is money lent: what is owed is derived from its agreed figure and the repayments in the "
             f"ledgers. Settle a new agreed amount and date instead of a balance.")
        return verbs.result(res, 1, lines)
    else:
        emit(f"  ✗ {who}: its balance comes from {src or 'no file'}; this script writes banks.json and foreign.json only")
        return verbs.result(res, 1, lines)

    b, a = res["before"], res["after"]
    emit(f"=== balance — {who} ===")
    emit(f"  {b['balance']:,.2f} as of {b['asof']}  →  {a['balance']:,.2f} as of {a['asof']}" if isinstance(b.get("balance"), (int, float))
         else f"  (none)  →  {a['balance']:,.2f} as of {a['asof']}")
    if not write:
        emit("\n  nothing written. Run with --write to apply.")
        return verbs.result(res, 0, lines)

    other = jlock.held_by_other(root)
    if other:
        emit(jlock.refusal(other)); return verbs.result(res, 1, lines)
    # the register's copy follows the source (D14, D20)
    acc["balance"], acc["asof"] = a["balance"], asof
    jsave(fd("accounts.json"), reg)
    res["written"] = True
    for script, args in ((os.path.join(HERE, "rebuild.py"), [".", "--write"]),
                         (os.path.join(HERE, "preflight.py"), [".", "--reseed"])):
        subprocess.run([sys.executable, script] + args, cwd=root, capture_output=True, text=True)
    out = subprocess.run([sys.executable, os.path.join(CHECKS, "check_data.py"), ".", "--money"],
                         cwd=root, capture_output=True, text=True).stdout
    res["findings"] = [l.strip() for l in out.splitlines() if l.strip().startswith(("✗", "⚠"))]
    emit("  written; the page is rebuilt." + ("" if not res["findings"] else "\n  the checkers found:"))
    for f in res["findings"]:
        emit("  " + f)
    return verbs.result(res, 2 if any(f.startswith("✗") for f in res["findings"]) else 0, lines)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("key", help="the account's key in accounts.json")
    ap.add_argument("amount", help="the balance the app shows, in the account's own currency")
    ap.add_argument("--asof", help="the date it was read (default: today)")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    return run(a.root, a.key, a.amount, asof=a.asof, write=a.write, say=print)["rc"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

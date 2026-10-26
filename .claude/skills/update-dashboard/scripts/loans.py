"""loans.py — money the owner has lent, and what is still owed on it (FINANCE.md §8a).

A loan is a register row with `role: owed` and `reach: lent`. What the owner declares is
`agreed`: the amount the borrower owes as of a date, in the loan's currency — the one figure
nothing can re-derive, because a loan made in one currency and repaid in another has no
arithmetic answer until the two sides agree on one. Everything after that date is read from
the bank ledgers: a row typed `Repayment` that names the borrower comes off, a row typed
`Lent` that names them goes on. The row's `balance` is a copy of the result, written by the
import and re-derived by the checker, the way every other balance in the register is.

A row names the borrower when the description or the label carries one of the loan's `names`
— the names the borrower appears under on a statement (a legal name, a nickname, a company)
— or the loan's own `name`. A repayment from someone with no loan (a friend paying back a share
of dinner) names no loan and changes nothing here.

rebuild.py, update.py and check_data.py all read the same answer from `outstanding`, so a loan
cannot be worth one thing on the page and another in the checker.
"""
import re

STALE_DAYS = 180   # no money back for this long and the page says so, with what to do


def _norm(s):
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def is_loan(a):
    return a.get("role") == "owed"


def names_of(loan):
    return [n for n in (_norm(x) for x in [loan.get("name")] + list(loan.get("names") or [])) if n]


def names_row(loan, row):
    text = _norm(row.get("description")) + "|" + _norm(row.get("label"))
    return any(n in text for n in names_of(loan))


def outstanding(loan, ledgers):
    """{owed, back, out, last, rows} for one loan. `ledgers` is every bank ledger's rows (a list
    of dicts with date, description, amount, type, label). Only rows after the agreed date
    count: the agreed amount already settles everything up to and including that day."""
    ag = loan.get("agreed") or {}
    since = ag.get("asof") or ""
    owed = float(ag.get("amount") or 0)
    back = out = 0.0
    last, rows = None, []
    for r in ledgers:
        if not r.get("date") or r["date"] <= since or not names_row(loan, r):
            continue
        t, amt = r.get("type") or "", float(r.get("amount") or 0)
        if t == "Repayment" and amt > 0:
            back += amt
            last = max(last or "", r["date"])
            rows.append(r)
        elif t == "Lent" and amt < 0:
            out += -amt
            rows.append(r)
    return {"owed": round(owed - back + out, 2), "back": round(back, 2), "out": round(out, 2),
            "last": last, "since": since, "rows": rows}

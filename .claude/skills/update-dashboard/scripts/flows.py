"""flows.py — the monthly plan as flows (findata schema 5, FINANCE.md §8b).

`funds.json` `plan.flows` is a list of rows, each one thing that happens to the paycheque every
month: what comes in (`income`), what is paid before anything is chosen (`committed` — rent, a
mortgage, a loan), what is moved out to be saved (`saving`), and what is free (`allowance`).
The page, rebuild.py and check_data.py all read the same sums from here, so a flow added to the
file changes every one of them and none of them carries a hand-copied number.

A flow may carry `starts: "fire"` — it begins only after FIRE (rent an owner will pay but does
not yet) — and is then left out of this month's split but kept in the planning figure. A
committed flow may carry `until` (the month a loan ends), `afterFire` (`keep`, the default, or
`drop`: a mortgage payment stops, property tax does not) and `pays` (the liability it repays).
"""

KINDS = ("income", "committed", "saving", "allowance")


def active(f):
    """In this month's split. A flow that starts after FIRE is planning, not cash."""
    return not f.get("starts")


def _num(x):
    return int(x) if float(x) == int(float(x)) else round(float(x), 2)


def totals(plan):
    """Every sum the page and the checkers read, from the flows alone."""
    flows = plan.get("flows") or []
    now = [f for f in flows if active(f)]

    def s(kind, rows=now, pred=lambda f: True):
        return _num(sum(float(f.get("amount") or 0) for f in rows if f.get("kind") == kind and pred(f)))

    return {
        "income": s("income"),
        "committed": s("committed"),
        # What is still paid after FIRE and is not in the measured spending: rent that starts at
        # FIRE, and a repayment (`pays`), which is not spending because its principal is saving.
        # Rent, a bill or a tax paid today is in spending.csv already (FINANCE.md §3a), so adding
        # it here would count it twice. Added to the measured median for the calibration.
        "committedKeep": s("committed", flows, lambda f: f.get("afterFire", "keep") == "keep"
                           and (not active(f) or f.get("pays"))),
        "saving": s("saving"),
        # Pay-yourself-first is judged on what reaches the broker; a saving flow with another
        # destination (a fund, a child's plan) is saving but not that rule.
        "invest": s("saving", now, lambda f: (f.get("to") or "broker") == "broker"),
        "allowance": s("allowance"),
        "committedNow": [f for f in now if f.get("kind") == "committed"],
        "incomeNote": next((f.get("note") or "" for f in flows if f.get("kind") == "income"), ""),
    }


def unset(plan):
    """The plan's numbers the owner never gave: a flow whose amount is null, not 0 (2026-10-28,
    first user -- a skipped question used to land as $0 and read as a fact). The sums above count
    it as nothing; the page and the figures table say Not set."""
    flows = plan.get("flows") or []
    miss = lambda pred: any(f.get("amount") is None for f in flows if pred(f))
    return {k for k, pred in (
        ("takeHome", lambda f: f.get("kind") == "income" and active(f)),
        ("invest", lambda f: f.get("kind") == "saving" and (f.get("to") or "broker") == "broker"),
        ("everyday", lambda f: f.get("kind") == "allowance"),
    ) if miss(pred)}

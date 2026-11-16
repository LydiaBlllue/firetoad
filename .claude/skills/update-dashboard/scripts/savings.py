"""savings.py — the savings rate, and the years it takes at that rate (FINANCE.md §1a).

The first FIRE number that needs no goal: how much of what you earn is left after spending, and
how many years of that, with what is already invested, it takes for the money to cover twenty-
five years of spending. Computed here, once; the page draws the curve and a slider over the
`curve` table and does no arithmetic of its own, so there is no second copy to keep equal.

What counts, as KNOWLEDGE 0.5 settled it: income is what work delivered to the bank — ledger
rows typed Payroll and Other (the cash-flow rows' `payroll` and `other`; a gift, a repayment, a
card's cash back and the broker's own income are not). Spending is the same month total the
usual month is made of (usual.compared, a yearly charge spread over its twelve months). Up to
twelve full months, the months set aside as unusual left out, and only months that have both an
income and a spend; fewer than three is not enough to say. The rate is the ratio of the sums,
so a month with a large bonus does not outweigh the rest.

Years: target T = twenty-five years of spending (fire.YEARS), saved c a year, invested P now, a
real return r:  n = ln((T + c/r) / (P + c/r)) / ln(1 + r). Three returns, 3%, 4% and 5%, because
a single number would say more than the formula knows; zero when P already reaches T; None when
nothing is saved. The curve is the same sum at income held as it is and the rate moved, from
nothing to ninety percent in steps of five; `more` is the slider's table, the same sum with a
little more kept each month.

Pure: rows and numbers in, numbers out.
"""
import math

import usual
from fire import YEARS

RETURNS = (0.03, 0.04, 0.05)    # real, after inflation: the range the years are shown over
STEP = 5                        # the curve's percentage points
TOP = 90
MORE_STEP = 50                  # the slider: keeping this much more a month, in steps of
MORE_TOP = 1000                 # up to this


def years(portfolio, income, spend, r):
    """Years of saving what is left of `income` after `spend` (monthly figures) until
    `portfolio` plus the savings reaches twenty-five years of spending at real return r."""
    c = (income - spend) * 12
    target = spend * 12 * YEARS
    if target <= 0:
        return None
    if portfolio >= target:
        return 0.0
    if c <= 0:
        return None
    return math.log((target + c / r) / (portfolio + c / r)) / math.log(1 + r)


def months_used(cashflow, spending, stmt_end, skip, today):
    """[{m, income, spend}] for the full, closed months before this one that have both."""
    inc = {r["ym"]: (r.get("payroll") or 0) + (r.get("other") or 0) for r in cashflow or []}
    out = []
    for m in usual.usable(spending, stmt_end, skip):
        if m >= today[:7] or inc.get(m, 0) <= 0:
            continue
        s = usual.compared(spending, m)
        if s > 0:
            out.append({"m": m, "income": inc[m], "spend": s})
    return out[-usual.WINDOW:]


def measured(cashflow, spending, stmt_end, skip, today, portfolio):
    """The SAVINGS constant: {} below three months, else the rate and what it came from, the
    years at each return, and the curve for the slider."""
    rows = months_used(cashflow, spending, stmt_end, skip, today)
    if len(rows) < usual.ENOUGH:
        return {}
    inc = sum(r["income"] for r in rows) / len(rows)
    spend = sum(r["spend"] for r in rows) / len(rows)
    rate = (inc - spend) / inc
    curve = []
    for pct in range(0, TOP + 1, STEP):
        s = inc * (1 - pct / 100)
        curve.append({"pct": pct, "years": [None if (y := years(portfolio, inc, s, r)) is None else round(y, 1)
                                            for r in RETURNS]})
    now = [None if (y := years(portfolio, inc, spend, r)) is None else round(y, 1) for r in RETURNS]
    # The slider is in money, not in points of the rate (2026-11-15, user 001: a person thinks
    # "keep $200 more", not "save 5 points more"): the years and the rate at each step.
    more = []
    for extra in range(0, MORE_TOP + 1, MORE_STEP):
        s = spend - extra
        more.append({"more": extra, "pct": round((inc - s) / inc * 100, 1),
                     "years": [None if (y := years(portfolio, inc, s, r)) is None else round(y, 1) for r in RETURNS]})
    return {"rate": round(rate, 4), "income": round(inc, 2), "spend": round(spend, 2), "n": len(rows),
            "from": rows[0]["m"], "to": rows[-1]["m"], "returns": list(RETURNS),
            "years": now, "curve": curve, "more": more,
            # the planned rate sits beside it where the plan has one, so the two are never mixed
            "portfolio": round(portfolio or 0, 2)}

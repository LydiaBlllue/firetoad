"""savings.py — years to financial independence, and the savings rate (FINANCE.md §1a).

One answer and one lever. The answer: how many years, at the pace money really reaches the
broker, until what is invested covers twenty-five years of the planning figure (or, with none
set, of what is really spent). The lever: investing a little more each month. Computed here,
once; the FIRE page and Home read the tables and do no sums of their own.

The pace is what reached the broker over the last three full months (WSDEP), the plan's amount
until anything has been seen arriving. Years: target T, invested P now, c a year, a real return
r:  n = ln((T + c/r) / (P + c/r)) / ln(1 + r) — at the owner's return setting (`growth`, 5%
unless changed) and one point either side, because one number would say more than the formula
knows; zero when P already reaches T; None when nothing is added.

The savings rate is the reason under the answer, as KNOWLEDGE 0.5 settled it: income is what
work delivered to the bank — ledger rows typed Payroll and Other (a gift, a repayment, a card's
cash back and the broker's own income are not); spending is the month total the usual month is
made of (usual.compared). Up to twelve full months, the months set aside left out, only months
with both; fewer than three is not enough to say. The rate is the ratio of the sums. What is
kept each month is then split by the job the plan gives it: invested, each saving flow with
another destination (an emergency fund), and what has no job yet.

Pure: rows and numbers in, numbers out.
"""
import math

import usual
from fire import YEARS

PACE_MONTHS = 3                 # what reached the broker is averaged over this many full months
MORE_STEP = 50                  # the slider: keeping this much more a month, in steps of
MORE_TOP = 1000                 # up to this


def years_to(portfolio, target, monthly, r):
    """Years of adding `monthly` until `portfolio` grows to `target` at real return r: zero when
    it is there already, None when nothing is added and it is not."""
    c = monthly * 12
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


def pace(wsdep, today, plan_invest):
    """(a month, how many months it is the average of): what reached the broker over the last
    three full months (WSDEP), or the plan's amount with 0 when nothing has been seen arriving."""
    full = [d for d in wsdep or [] if d["ym"] < today[:7]][-PACE_MONTHS:]
    if full:
        return round(sum(d["amt"] for d in full) / len(full), 2), len(full)
    return float(plan_invest or 0), 0


def measured(cashflow, spending, stmt_end, skip, today, portfolio, plan_base=None, wsdep=None,
             plan_invest=0, set_aside=(), growth=5):
    """The SAVINGS constant (FINANCE.md §1a): the years to financial independence at the pace
    money really reaches the broker, the table the slider reads, and — with three full months of
    income and spending — the savings rate and what the money kept each month does.
    {} when there is no target to count to: no planning figure and nothing measured."""
    rows = months_used(cashflow, spending, stmt_end, skip, today)
    have = len(rows) >= usual.ENOUGH
    inc = sum(r["income"] for r in rows) / len(rows) if have else None
    spend = sum(r["spend"] for r in rows) / len(rows) if have else None
    target = (plan_base or spend or 0) * 12 * YEARS
    if not target:
        return {}
    rs = [round((growth - 1) / 100, 4), round(growth / 100, 4), round((growth + 1) / 100, 4)]
    inv, n = pace(wsdep, today, plan_invest)
    p = portfolio or 0

    def yrs(cm):            # at the lowest return first: the longest of the three
        return [None if (y := years_to(p, target, cm, r)) is None else round(y, 1) for r in rs]

    out = {"target": round(target, 2), "portfolio": round(p, 2), "invest": inv, "paceMonths": n,
           "returns": rs, "growth": growth, "fromPlan": not plan_base,
           "years": yrs(inv),
           # the slider: investing this much more a month, from nothing to MORE_TOP
           "more": [{"more": m, "years": yrs(inv + m)} for m in range(0, MORE_TOP + 1, MORE_STEP)]}
    if have:
        keep = inc - spend
        jobs = [["Invested", inv]] + [[n_, float(a)] for n_, a in set_aside]
        free = keep - sum(a for _, a in jobs)
        out.update({"rate": round(keep / inc, 4), "income": round(inc, 2), "spend": round(spend, 2),
                    "n": len(rows), "from": rows[0]["m"], "to": rows[-1]["m"], "keep": round(keep, 2),
                    "jobs": [[a, round(b, 2)] for a, b in jobs], "free": round(free, 2)})
    return out

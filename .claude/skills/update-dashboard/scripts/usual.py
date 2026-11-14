"""usual.py — a usual month, and how long the money would last on it (FINANCE.md §3a, §8d).

Until 1.0.5 both were worked out in the page, so nothing outside the browser could read them:
not a checker, not the panel, not a second front end. They are computed here, once, and the
page is handed the result (the USUAL constant, and `money`, `cost`, `months` inside SAFETY).

A usual month: everything spent, a yearly charge spread over its twelve months, averaged over
the full months before a given month — up to twelve, the months set aside as unusual left out,
and only months every card has reported. Fewer than three such months is not enough to say.

Pure: rows and dicts in, numbers out. `spending` is rebuild's SPENDING rows ({date, amount,
currency, yr?}), in file order — the sums run in that order so they are the same numbers the
page used to produce.
"""
import calendar

WINDOW = 12     # full months averaged, at most
ENOUGH = 3      # and at least


def ym_num(ym):
    return int(ym[:4]) * 12 + int(ym[5:7])


def ym_shift(ym, d):
    n = ym_num(ym) - 1 + d
    return f"{n // 12:04d}-{n % 12 + 1:02d}"


def cov_end(stmt_end):
    """The newest month every card reaches. A card covers a month only when its newest statement
    closes on or after that month's last day; a source that has reported nothing constrains
    nothing; and nothing reported at all means no month is covered ("")."""
    def full(end):
        y, m, d = int(end[:4]), int(end[5:7]), int(end[8:10])
        return end[:7] if d >= calendar.monthrange(y, m)[1] else ym_shift(end[:7], -1)
    ends = sorted(full(e) for e in (stmt_end or {}).values() if e)
    return ends[0] if ends else ""


def months_of(spending):
    return sorted({r["date"][:7] for r in spending})


def usable(spending, stmt_end, skip):
    """Closed, and worth comparing against."""
    cov = cov_end(stmt_end)
    return [m for m in months_of(spending) if m <= cov and not (skip or {}).get(m)]


def compared(spending, ym):
    """A month's total as months are compared: its own charges, and a twelfth of every yearly
    charge paid in the twelve months up to it."""
    n = ym_num(ym)
    total = 0
    for r in spending:
        if r["date"].startswith(ym) and r.get("currency") == "CAD" and not r.get("yr"):
            total += r["amount"]
    for r in spending:
        if r.get("yr") and r.get("currency") == "CAD" and 0 <= n - ym_num(r["date"]) < 12:
            total += r["amount"] / 12
    return total


def at(spending, stmt_end, skip, ym):
    """{v, n}: the usual month as of `ym` and how many months it is the average of — or None."""
    win = [compared(spending, m) for m in usable(spending, stmt_end, skip) if m < ym][-WINDOW:]
    win = [v for v in win if v > 0]
    if len(win) < ENOUGH:
        return None
    total = 0
    for v in win:
        total += v
    return {"v": total / len(win), "n": len(win)}


def by_month(spending, stmt_end, skip, today):
    """The usual month as of every month the page can be turned to: from the first month with a
    record to the month after the newest one or after today, whichever is later. A month with
    nothing to say is absent."""
    ms = months_of(spending)
    now = today[:7]
    first = ms[0] if ms else now
    last = ym_shift(max(ms[-1] if ms else now, now), 1)
    out, m = {}, first
    while m <= last:
        u = at(spending, stmt_end, skip, m)
        if u:
            out[m] = u
        m = ym_shift(m, 1)
    return out


def runway(today_money, invested, unsecured, abroad, repay, usual_now):
    """The emergency fund's three numbers. The money is what could be spent today, less what in
    it is invested and what is owed on no asset. A month costs the usual month plus the
    repayments the plan pays today. Money abroad is a second answer, never folded in."""
    money = (today_money or 0) - (invested or 0) - (unsecured or 0)
    cost = usual_now["v"] + (repay or 0) if usual_now else None
    cost = cost or None
    return {"money": money, "cost": cost,
            "months": max(0, money / cost) if cost else None,
            "abroadMonths": max(0, (money + abroad) / cost) if cost and (abroad or 0) > 0 else None}

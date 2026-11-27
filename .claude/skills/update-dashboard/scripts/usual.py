"""usual.py — a usual month (FINANCE.md §3a).

Until 1.0.5 it was worked out in the page, so nothing outside the browser could read it: not a
checker, not the panel, not a second front end. It is computed here, once, and the page is
handed the result (the USUAL constant).
USUAL has three parts, all read off the same closed months: `month` (a usual month as of each
month the page can be turned to), `median` (each category's median over the same window, what
"more than usual" is measured against) and `base` (the average the planning figure is
calibrated on, which leaves out what ends before FIRE).

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


def compared_rows(spending, ym):
    """A month as months are compared: (category, amount) for its own charges, then a twelfth of
    every yearly charge paid in the twelve months up to it."""
    n = ym_num(ym)
    out = [(r.get("category"), r["amount"]) for r in spending
           if r["date"].startswith(ym) and r.get("currency") == "CAD" and not r.get("yr")]
    out += [(r.get("category"), r["amount"] / 12) for r in spending
            if r.get("yr") and r.get("currency") == "CAD" and 0 <= n - ym_num(r["date"]) < 12]
    return out


def compared(spending, ym, keep=None):
    """That month's total; `keep`, when given, says which categories count."""
    total = 0
    for cat, amount in compared_rows(spending, ym):
        if keep is None or keep(cat):
            total += amount
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


def medians(spending, stmt_end, skip, ym):
    """{n, cats}: each category's median month over the full months before `ym` — up to twelve,
    a month the category did not appear in counting as nothing — and how many months that was.
    None with fewer than three. A category whose median is nothing is left out of `cats`."""
    win = [m for m in usable(spending, stmt_end, skip) if m < ym][-WINDOW:]
    if len(win) < ENOUGH:
        return None
    per = []
    for m in win:
        tot = {}
        for cat, amount in compared_rows(spending, m):
            tot[cat] = tot.get(cat, 0) + amount
        per.append(tot)
    cats = {}
    for cat in sorted({c for tot in per for c in tot}, key=str):
        vs = sorted(tot.get(cat, 0) for tot in per)
        h = len(vs) >> 1
        med = vs[h] if len(vs) % 2 else (vs[h - 1] + vs[h]) / 2
        if med:
            cats[cat] = med
    return {"n": len(win), "cats": cats}


def baseline(spending, stmt_end, skip, today, ends):
    """{avg, rows}: what the planning figure is calibrated on — the average of up to twelve
    closed months before this one, counting only what goes on after FIRE (`ends` is the
    categories that stop before it). `rows` is the months used, each with its total; `avg` is
    None with fewer than three."""
    ends = set(ends or ())
    rows = [{"m": m, "v": compared(spending, m, lambda c: c not in ends)}
            for m in usable(spending, stmt_end, skip) if m < today[:7]]
    rows = [r for r in rows if r["v"] > 0][-WINDOW:]
    total = 0
    for r in rows:
        total += r["v"]
    return {"avg": total / len(rows) if len(rows) >= ENOUGH else None, "rows": rows}


def pages(spending, today):
    """Every month the page can be turned to: from the first month with a record to the month
    after the newest one or after today, whichever is later."""
    ms = months_of(spending)
    now = today[:7]
    m, last, out = (ms[0] if ms else now), ym_shift(max(ms[-1] if ms else now, now), 1), []
    while m <= last:
        out.append(m)
        m = ym_shift(m, 1)
    return out


def by_month(spending, stmt_end, skip, today):
    """The usual month as of every month the page can be turned to. A month with nothing to say
    is absent."""
    out = {}
    for m in pages(spending, today):
        u = at(spending, stmt_end, skip, m)
        if u:
            out[m] = u
    return out


def measured(spending, stmt_end, skip, today, ends):
    """The USUAL constant: `month`, `median` and `base` (see the top of this file)."""
    med = {}
    for m in pages(spending, today):
        x = medians(spending, stmt_end, skip, m)
        if x:
            med[m] = x
    return {"month": by_month(spending, stmt_end, skip, today), "median": med,
            "base": baseline(spending, stmt_end, skip, today, ends)}


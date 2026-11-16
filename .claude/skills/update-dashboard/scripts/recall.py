"""recall.py — what helps a person remember a charge (FINANCE.md §3a, feedback: "I cannot
remember where this money went").

A question about a merchant used to show the bank's string, a total and a count, and ask the
owner to recall the purchase. A person does not remember a merchant's legal name; they remember
the Saturday, what else they did that day, and that it happens every month. All of that is
already in the rows. This module reads it out of them and states it as facts — when, in what
rhythm, alongside what — and never guesses what the charge was: a rhythm is not a category, and
a merchant's name is still not a sentence.

Pure: rows in, small dicts out. The words are the panel's, in the owner's language.
"""
import datetime
import statistics

# how many days apart two charges are, for each rhythm a person would name
RHYTHMS = (("week", 6, 8), ("2weeks", 12, 16), ("month", 26, 35))
ENOUGH = 3          # charges, before a rhythm is said at all


def day(d):
    return datetime.date.fromisoformat(str(d)[:10])


def weekday(d):
    """0 = Monday … 6 = Sunday."""
    return day(d).weekday()


def charges(rows, mine):
    """The owner's charges among `rows` ({date, amount, note}), oldest first, as {d, a, w}:
    the day, the amount and the weekday. `mine(row)` says which rows are the ones asked about.
    Refunds are left out: the question is what was bought."""
    out = [{"d": r["date"], "a": round(float(r["amount"]), 2), "w": weekday(r["date"])}
           for r in rows if mine(r) and float(r["amount"]) > 0]
    return sorted(out, key=lambda x: x["d"])


def rhythm(items):
    """What repeats, or None. With at least three charges on different days:
    {every: week | 2weeks | month (or None), weekday: 0–6 when nearly all fall on one, same:
    True when the amount never changes, about: the usual amount, when: start | end | None for a
    monthly charge that sits at one end of the month}. A dict with nothing in it worth saying
    is None."""
    days = sorted({x["d"] for x in items})
    if len(days) < ENOUGH:
        return None
    gaps = [(day(b) - day(a)).days for a, b in zip(days, days[1:])]
    every = None
    for name, lo, hi in RHYTHMS:
        if sum(1 for g in gaps if lo <= g <= hi) >= max(2, round(len(gaps) * 2 / 3)):
            every = name
            break
    wds = [x["w"] for x in items]
    top = max(set(wds), key=wds.count)
    one_day = top if wds.count(top) >= max(ENOUGH, round(len(wds) * 0.8)) else None
    amounts = [x["a"] for x in items]
    about = statistics.median(amounts)
    same = max(amounts) - min(amounts) <= max(0.01, 0.01 * about)
    when = None
    if every == "month":
        doms = [day(d).day for d in days]
        when = "start" if all(d <= 5 for d in doms) else "end" if all(d >= 25 for d in doms) else None
    if not every and one_day is None and not same:
        return None
    return {"every": every, "weekday": one_day, "same": same, "about": round(about, 2), "when": when}


def same_days(rows, items, mine, name, days=2, each=2):
    """What else was paid on the days of these charges: up to `days` days that have something,
    newest first, each with its `each` biggest other charges as {what, a}. `name(row)` is how
    another charge is called."""
    out = []
    for d in sorted({x["d"] for x in items}, reverse=True):
        others = sorted(({"what": name(r), "a": round(float(r["amount"]), 2)} for r in rows
                         if r["date"] == d and not mine(r) and float(r["amount"]) > 0), key=lambda x: -x["a"])
        if others:
            out.append({"d": d, "w": weekday(d), "with": others[:each]})
        if len(out) == days:
            break
    return out


def ledger_day(rows, d, skip=None, each=3):
    """What else moved in one ledger on a day: {what, a}, biggest first. `skip` is the row asked
    about (date, amount)."""
    out = []
    for r in rows:
        if r.get("date") != d:
            continue
        a = round(float(r["amount"]), 2)
        if skip is not None and abs(abs(a) - abs(skip)) < 0.005:
            skip = None                      # the row itself, once
            continue
        out.append({"what": r.get("label") or r.get("description") or "", "a": a})
    return sorted(out, key=lambda x: -abs(x["a"]))[:each]


def counterpart(ledgers, d, amount, own, within=3):
    """A row in another of the owner's ledgers that looks like the other end of this one: the
    opposite amount within a few days. {ledger, d} or None. `ledgers` is {name: rows}."""
    for name, rows in ledgers.items():
        if name == own:
            continue
        for r in rows:
            try:
                if abs(float(r["amount"]) + float(amount)) < 0.005 and abs((day(r["date"]) - day(d)).days) <= within:
                    return {"ledger": name, "d": r["date"]}
            except (KeyError, ValueError):
                continue
    return None


def groups(items, key):
    """Questions that are one question: `key(item)` names what makes two the same (None: not
    groupable). Returns {key: [items…]} for every key two or more share."""
    by = {}
    for it in items:
        k = key(it)
        if k is not None:
            by.setdefault(k, []).append(it)
    return {k: v for k, v in by.items() if len(v) > 1}

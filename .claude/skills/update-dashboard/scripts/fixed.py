"""fixed.py — which spending rows are a declared committed payment (FINANCE.md §3b).

Fixed costs are only what the owner declared: the committed flows of the plan (rent, a mortgage,
a loan). Everything else spent is everyday, a phone bill included (1.0.7, user 001, feedback
110: the setup's everyday figure counted every bill, the page left the Bills category out, and a
phone bill nobody had declared sat in neither line of the plan). A category says what a thing is,
not whether it was promised; only the owner knows that.

A declared payment is found the way D21 proves it was made: in each month, the row whose amount
is within a dollar (or one per cent) of the flow's, the closest one; failing that, one payee's
rows in that month that add up to it (a bill taken in two debits). A flow that is one figure for
several bills (`estimate: true`) can match no single payment, so in the months it applies to the
rows of the `bills` group stand for it.

Pure: rows and flows in, a set of row indices out.
"""
import collections
import re

import categories


def payee(note):
    """The payee of a spending note, without order numbers, cities or the statement tag."""
    n = re.sub(r"\s*\[[^\]]+\]\s*$", "", note or "")
    n = n.rsplit(", ", 1)[-1]                       # "Pre-Authorized Payment, X" is X
    n = re.sub(r"\s*\([^)]*\)|\*[A-Z0-9]{5,}|\b\d{3}-\d{3}-\d{4}\b|\*+\d+|#\d+", "", n)
    n = re.sub(r"\s+(ON|QC|BC|AB|MB|NS|NB|CA|NY|WA)\b.*$", "", n.upper())
    return re.sub(r"\s+", " ", n).strip()


def mark(rows, flows, groups=None):
    """Indices of `rows` ({date, amount, category, note}, the home currency's) that are a
    declared committed payment. `flows` are the plan's committed flows paid today; `groups` is
    categories.groups(plan), each category's group."""
    groups = groups if groups is not None else categories.groups({})
    group = lambda c: groups.get(c, "everyday")
    by_month = collections.defaultdict(list)
    for i, r in enumerate(rows):
        if r.get("currency", "CAD") == "CAD" and r["amount"] > 0:
            by_month[r["date"][:7]].append(i)
    out = set()
    for f in flows:
        amt = float(f.get("amount") or 0)
        if amt <= 0:
            continue
        for ym, idx in by_month.items():
            if f.get("until") and ym > f["until"][:7]:
                continue
            if f.get("estimate"):
                out |= {i for i in idx if group(rows[i].get("category")) == "bills"}
                continue
            tol = max(1.0, amt * 0.01)
            free = [i for i in idx if i not in out]
            near = sorted((abs(rows[i]["amount"] - amt), i) for i in free if abs(rows[i]["amount"] - amt) <= tol)
            if near:
                out.add(near[0][1])
                continue
            by_payee = collections.defaultdict(list)
            for i in free:
                by_payee[payee(rows[i].get("note"))].append(i)
            for ids in by_payee.values():
                if len(ids) > 1 and abs(sum(rows[i]["amount"] for i in ids) - amt) <= tol:
                    out |= set(ids)
                    break
    return out

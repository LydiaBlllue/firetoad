"""debts.py — when a debt has to be paid (FINANCE.md §8d).

A card's balance is due now: it is this month's bill. A loan, a line of credit or a mortgage is
paid over time: what leaves each month is its payment, not its balance. The Emergency fund
needs that difference — it used to take every unsecured balance off the money and also count
the monthly payment, so a student loan was charged twice and "months covered" read zero for
anyone who owed more than they held in cash.

`due` is the register's word for it: `now` or `later`. It defaults from the account's kind and
the owner may say otherwise on the row (a loan called in, a card on a payment plan).

Pure: register rows in, lists out.
"""
DUE = ("now", "later")
DUE_NOW_KINDS = {"Credit card"}


def due(acc):
    """`now` or `later` for a liability: the row's own word, else its kind's default."""
    return acc.get("due") if acc.get("due") in DUE else ("now" if acc.get("kind") in DUE_NOW_KINDS else "later")


def unsecured(liabs, by_key):
    """The liabilities that sit on no asset, as (due now, paid over time), each a list of
    (row, amount). A debt secured on an asset is netted against that asset elsewhere."""
    free = [(a, v) for a, v in liabs if by_key.get(a.get("against") or "") is None]
    return [(a, v) for a, v in free if due(a) == "now"], [(a, v) for a, v in free if due(a) != "now"]


def paid_by(flows):
    """The keys of the liabilities a committed flow paid today repays (`pays`)."""
    return {f["pays"] for f in flows or [] if f.get("kind") == "committed" and f.get("pays") and not f.get("starts")}

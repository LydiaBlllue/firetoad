"""seen_accounts.py — accounts a statement shows money moving to or from, that nobody registered.

A card-only owner's statements show every payment coming from a chequing account the tool has
never heard of, and their net worth was the card's debt and nothing else; a chequing ledger
showed three other account numbers, one in US dollars, and a $98,000 transfer could only be
guessed as the owner's own (2026-10-28, user 002). Setup asks about each one by its number, and
the import says when a new one appears.

An account number is read only where it is shaped like one — masked (`XXXX-432`, `****1234`),
two groups joined (`#4471-9032`), or ten digits or more, whose last four are the account — and
only in a row that moves money between accounts. A store number or a reference (`TF0006`) is
none of these.
"""
import re

MOVES = re.compile(r"TRANSFER|\bTFR\b|\bTF\d|\bWIRE\b|\bDRAFT\b|PAYMENT\s+(?:FROM|RECEIVED)|FROM\s+ACC|TO\s+ACC", re.I)
SHAPES = (
    re.compile(r"[X*]{2,}[-\s]?(\d{3,4})\b"),          # masked
    re.compile(r"(?<![A-Z\d])#?(\d{3,5})-(\d{3,5})\b"), # two groups joined
    re.compile(r"(\d{10,})"),                           # a long number: its last four
)


def numbers_in(desc):
    """The account numbers a row's description carries, as their trailing digits."""
    if not MOVES.search(desc or ""):
        return []
    out = []
    for i, rx in enumerate(SHAPES):
        for m in rx.finditer(desc.upper()):
            out += [m.group(0)[-4:]] if i == 2 else [g for g in m.groups() if g]
    return list(dict.fromkeys(out))


def known(num, registered):
    """True when `num` is the end of a registered account's digits (or theirs of it)."""
    return any(d and (d.endswith(num) or num.endswith(d[-len(num):])) for d in registered)


def unregistered(rows, registered):
    """{number: (rows, money in, money out)} for every account a row names that is not one of
    `registered` (each an account's digits)."""
    seen = {}
    for r in rows:
        amt = float(r["amount"])
        for n in numbers_in(r.get("description", "")):
            if known(n, registered):
                continue
            c, i, o = seen.get(n, (0, 0.0, 0.0))
            seen[n] = (c + 1, i + max(amt, 0), o + max(-amt, 0))
    return seen

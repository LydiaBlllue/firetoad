"""categories.py — the spending categories and their groups, defined once (FINANCE.md §3a).

Spending is money that leaves and buys nothing you still own, whatever paid it: a card, a debit
purchase, or chequing (rent, a bill, cash taken out, a bank fee, money sent to family). Every
category sits in one of three groups, and the group is what decides what it counts for:

- `fixed`    — paid before anything is chosen. Not measured against the allowance; in the
               spending the FIRE target is calibrated on.
- `everyday` — what the allowance is for, and in the calibration.
- `time`     — spending with an end (tuition). In the year's total, never in the FIRE target.

The owner may move a category to another group in `plan.json` `categoryGroups`; the page, the
import, the checkers and the setup all read the list from here. A subscription is not a category:
a charge that repeats is marked as such, whatever it bought (`recurring` below).

Every category has its own colour (DESIGN.md §3); Other is grey.
"""
import collections
import datetime, re

GROUPS = ("fixed", "everyday", "time")

# key, label shown on the page, default group, colour token. The order is the stack's, bottom up,
# and it is the colour order: the first eight are the validated slots in their validated order
# (blue, orange, aqua, yellow, magenta, green, violet, red), so no two of them that touch in a
# stack are hard to tell apart; the six after them are further hues, told apart by the name that
# is always beside them; Other is grey and last (2026-10-29, user 001 chose fourteen colours).
TABLE = [
    ("Grocery",       "Groceries",        "everyday", "--c-grocery"),
    ("Dining",        "Dining",           "everyday", "--c-dining"),
    ("Housing",       "Housing",          "fixed",    "--c-housing"),
    ("Shopping",      "Shopping",         "everyday", "--c-shopping"),
    ("Transport",     "Transport",        "everyday", "--c-transport"),
    ("Software",      "Software & tools", "everyday", "--c-software"),
    ("Bills",         "Bills",            "fixed",    "--c-bills"),
    ("Travel",        "Travel",           "everyday", "--c-travel"),
    ("Entertainment", "Entertainment",    "everyday", "--c-entertainment"),
    ("Health",        "Health",           "everyday", "--c-health"),
    ("Family",        "Family & gifts",   "everyday", "--c-family"),
    ("Cash",          "Cash",             "everyday", "--c-cash"),
    ("Fees",          "Fees & interest",  "everyday", "--c-fees"),
    ("Education",     "Education",        "time",     "--c-education"),
    ("Other",         "Other",            "everyday", "--c-rest"),
]
CATEGORIES = [k for k, *_ in TABLE]

# The seven categories before 2026-10-29, and where a row of each lands. Subscription has no
# single answer -- it was how a charge was paid, not what it bought -- so its rows are filed by
# merchant (the starter map, then Entertainment) by the migration, and asked.
OLD = {"Grocery": "Grocery", "Dining": "Dining", "Shopping": "Shopping", "Transport": "Transport",
       "Entertainment": "Entertainment", "Other": "Other", "Subscription": None}


def groups(plan):
    """{category: group}, the defaults with the owner's own moves applied."""
    own = (plan or {}).get("categoryGroups") or {}
    return {k: (own.get(k) if own.get(k) in GROUPS else g) for k, _, g, _ in TABLE}


def page_table(plan):
    """What the page draws from: one entry per category, in this order."""
    g = groups(plan)
    return [{"k": k, "n": n, "g": g[k], "c": f"var({c})"} for k, n, _, c in TABLE]


# ---------------------------------------------------------------- a charge that repeats
NOT_A_NAME = {"COM", "CA", "NET", "WWW", "INC", "LTD", "BILL"}
# A place is not part of a name: 'APPLE.COM/BILL TORONTO ON' is Apple.
PLACES = {"ON", "QC", "BC", "AB", "MB", "SK", "NS", "NB", "NL", "PE", "TORONTO", "OTTAWA", "MONTREAL",
          "VANCOUVER", "CALGARY", "EDMONTON", "WINNIPEG", "WATERLOO", "HALIFAX", "QUEBEC"}
# Not a subscription however regularly it comes: what a home costs, cash and a bank's own charges.
NEVER_RECURRING = {"Housing", "Cash", "Fees"}


def _brand(note):
    """The merchant of a spending row, without the statement tag, store numbers, web suffixes or
    a repeat of itself: 'NETFLIX.COM NETFLIX.COM' is NETFLIX, 'AMAZON PRIME MEMBER' is AMAZON
    PRIME and stays apart from an AMAZON.CA purchase."""
    s = re.sub(r"\s*\[[^\]]*\]\s*$", "", note or "").upper()
    s = re.sub(r"\((?:DEBIT|CHEQUING)\)", "", s)
    s = re.sub(r"^(SP|SQ|WL|TST|LS)[\s*\-]+", "", s)
    words = []
    for w in re.split(r"[^A-Z0-9]+", s):
        if w and w not in NOT_A_NAME and w not in PLACES and not re.search(r"\d", w) and (not words or words[-1] != w):
            words.append(w)
    return " ".join(words[:2])


def _monthly(ms, months):
    """At least `months` months, and hardly one missed between the first and the last."""
    if len(ms) < months:
        return False
    y0, m0 = map(int, ms[0].split("-")); y1, m1 = map(int, ms[-1].split("-"))
    span = (y1 - y0) * 12 + (m1 - m0) + 1
    return span - len(ms) <= max(1, span // 6)


def yearly(rows, brands=None, declared=()):
    """The merchants paid once a year: the ones the owner said so of (merchants.json
    `every: "year"`, as `declared` brand names), and the ones whose charges come back eleven to
    thirteen months apart within a tenth of the amount, with nothing in between. A year's
    insurance or a card's annual fee is one large row in one month, which makes that month look
    unusual and the others cheap; months are compared with it spread over twelve (FINANCE.md §3a).
    Housing and cash are never one."""
    brands = brands or {}
    by = collections.defaultdict(list)
    for r in rows:
        a = float(r["amount"])
        if a > 0 and r.get("category") not in ("Housing", "Cash"):
            b = _brand(r["note"])
            by[brands.get(b, b)].append((datetime.date.fromisoformat(r["date"]), a))
    out = {b for b in declared if b in by}
    for b, xs in by.items():
        xs.sort()
        if len(xs) >= 2 and all(330 <= (q[0] - p[0]).days <= 400 and abs(q[1] - p[1]) <= 0.1 * p[1]
                                for p, q in zip(xs, xs[1:])):
            out.add(b)
    return out


def recurring(rows, brands=None, tolerance=0.03, months=3):
    """The merchants whose charges repeat. A subscription is a charge that repeats -- that is the
    whole definition -- so it is measured, never read off a merchant's name (2026-09-06: a shop
    called PUBLICATION was a notebook). A merchant repeats when one price comes back month after
    month to the cent (a $4.51 plan among other charges from the same store), or when the amount
    holds from one month to the next at least seven times in ten, within `tolerance` or fifty
    cents (a plan whose price went up once). A coffee bought once a month is neither: its amount
    moves.
    `brands` maps a merchant's name (as `brand_of` gives it) to the one the owner gave several
    spellings of it, merchants.json `brand`.
    Returns {name: {"amount": the latest, "months": n, "last": date}}."""
    brands = brands or {}
    by = collections.defaultdict(list)
    for r in rows:
        a = float(r["amount"])
        if a > 0 and r.get("category") not in NEVER_RECURRING:
            b = _brand(r["note"])
            by[brands.get(b, b)].append((r["date"], a))
    near = lambda x, y: abs(x - y) <= max(0.5, tolerance * y)
    same = lambda x, y: abs(x - y) <= max(0.05, 0.01 * y)     # a plan's price, to the cent
    out = {}
    for b, xs in by.items():
        if not b:
            continue
        xs.sort()
        active = {d[:7] for d, _ in xs}
        best = None
        for _, a in xs:                                 # one price, month after month
            ms = sorted({d[:7] for d, x in xs if same(x, a)})
            # most of the months this merchant was paid at all: a shop visited often can hit
            # one amount three times by chance; a plan's price is there nearly every month
            if _monthly(ms, months) and len(ms) >= 0.6 * len(active) and (best is None or len(ms) > len(best[0])):
                best = (ms, [x for d, x in xs if same(x, a)][-1])
        if best is None:                                # or the amount held month to month
            per = {}
            for d, a in xs:
                per.setdefault(d[:7], a)
            ms = sorted(per)
            held = sum(1 for p, q in zip(ms, ms[1:]) if near(per[q], per[p]))
            if _monthly(ms, months) and held >= 0.7 * (len(ms) - 1):
                best = (ms, per[ms[-1]])
        if best:
            out[b] = {"amount": round(best[1], 2), "months": len(best[0]), "last": xs[-1][0]}
    return out


def brand_of(note):
    return _brand(note)

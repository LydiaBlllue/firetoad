"""csv_bank — a bank's own transaction download (CSV), read by the column map the register keeps.

Most Canadian banks let you download an account's recent transactions as a spreadsheet: TD,
Scotiabank, CIBC, Tangerine, Simplii and EQ among them (2026-11-03, user 001: lower the barrier
for people whose bank has no PDF parser here). The layouts differ and change, so nothing here is
guessed per bank. The register's document carries a `csv` map, written at setup from the file
the owner actually dropped, and this module only follows it:

    {"header": true,                       # the first line names the columns
     "date": "Date", "dateFormat": "%m/%d/%Y",
     "description": ["Description", "Memo"],   # one column or several, joined
     "amount": "Amount",                   # one signed column ...
     "out": "Withdrawals", "in": "Deposits",   # ... or two unsigned ones
     "balance": "Balance",                 # optional: the running balance, when the bank gives it
     "sign": 1}                            # -1 when the file shows a purchase as a positive number

A column is named by its header, or by its position (0, 1, ...) when the file has no header.
`PROFILES` are starting points for that map, matched on a file's header or shape; each says
whether a real file has confirmed it. An unknown layout is never read: it stops and is asked.

A CSV prints no totals, so it reconciles by its balances. With a balance column every row has
to follow from the one before it. Without one (most card downloads) the parse cannot reconcile on
its own: the import asks for the balance the banking app shows and checks the rows against it.

Amounts come back signed the ledger's way: money out (a purchase, a withdrawal) is negative.
"""
import csv
import datetime
import io
import re

from . import ParseError

DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%b %d, %Y", "%d %b %Y", "%m/%d/%y")

# Starting points only: setup shows the owner the map it drafted and the first rows read with it.
# `verified` stays False until a real file from that bank has been read and reconciled.
PROFILES = {
    "td": {"label": "TD", "header": False, "date": 0, "dateFormat": "%m/%d/%Y", "description": 1,
           "out": 2, "in": 3, "balance": 4, "columns": 5, "verified": False},
    "cibc": {"label": "CIBC", "header": False, "date": 0, "dateFormat": "%Y-%m-%d", "description": 1,
             "out": 2, "in": 3, "columns": (4, 5), "verified": False},
    "tangerine": {"label": "Tangerine", "header": True, "date": "Transaction date", "dateFormat": "%m/%d/%Y",
                  "description": ["Name", "Memo"], "amount": "Amount", "match": {"Transaction date", "Name", "Amount"},
                  "verified": False},
    "simplii": {"label": "Simplii", "header": True, "date": "Date", "dateFormat": "%m/%d/%Y",
                "description": "Transaction Details", "out": "Funds Out", "in": "Funds In",
                "match": {"Date", "Transaction Details", "Funds Out", "Funds In"}, "verified": False},
    "eq": {"label": "EQ Bank", "header": True, "date": "Transfer date", "description": "Description",
           "amount": "Amount", "balance": "Balance", "match": {"Transfer date", "Description", "Amount", "Balance"},
           "verified": False},
    "scotia": {"label": "Scotiabank", "header": True, "date": "Date", "description": ["Description", "Sub-description"],
               "amount": "Amount", "balance": "Balance", "match": {"Date", "Description", "Amount"}, "verified": False},
}


def read_lines(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ParseError("not a text file")
    return [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]


def number(s):
    """'1,234.56' / '$-4.00' / '(12.00)' / '' -> float or None."""
    t = (s or "").strip().replace("$", "").replace(",", "").replace(" ", "")
    if not t:
        return None
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()")
    if t.endswith("-"):
        neg, t = True, t[:-1]
    try:
        v = float(t)
    except ValueError:
        raise ParseError(f"not an amount: {s!r}")
    return -v if neg else v


def when(s, fmt):
    s = (s or "").strip()
    for f in ((fmt,) if fmt else ()) + DATE_FORMATS:
        try:
            return datetime.datetime.strptime(s, f).date().isoformat()
        except ValueError:
            continue
    return None


def detect(path):
    """The profile whose header or shape the file has, or None. A suggestion for setup, never a
    reading: the map that is used is the one in the register."""
    lines = read_lines(path)
    if not lines:
        return None
    head = {c.strip() for c in lines[0]}
    for key, p in PROFILES.items():
        if p.get("header") and p["match"] <= head:
            return key
    for key, p in PROFILES.items():
        if p.get("header"):
            continue
        cols = p["columns"] if isinstance(p["columns"], tuple) else (p["columns"],)
        if all(len(r) in cols for r in lines[:5]) and when(lines[0][p["date"]], p["dateFormat"]):
            return key
    return None


def parse(path, spec):
    if not spec:
        raise ParseError("the register has no `csv` map for this document: setup writes one from the file")
    lines = read_lines(path)
    if not lines:
        raise ParseError("the file is empty")
    names = [c.strip() for c in lines[0]] if spec.get("header") else None
    body = lines[1:] if names else lines

    def col(r, ref):
        if ref is None:
            return None
        i = ref if isinstance(ref, int) else (names.index(ref) if names and ref in names else None)
        if i is None:
            raise ParseError(f"no column {ref!r} in this file (it has {', '.join(names or [])}) — the bank changed its layout?")
        return r[i] if i < len(r) else ""

    sign = spec.get("sign", 1)
    rows, skipped = [], 0
    for r in body:
        d = when(col(r, spec["date"]), spec.get("dateFormat"))
        if d is None:
            skipped += 1                       # a title or a total line some banks add
            continue
        refs = spec["description"] if isinstance(spec["description"], list) else [spec["description"]]
        desc = " ".join(x.strip() for x in (col(r, c) for c in refs) if x and x.strip())
        if "amount" in spec:
            amt = number(col(r, spec["amount"]))
            if amt is None:
                raise ParseError(f"a row on {d} has no amount")
        else:
            out, inn = number(col(r, spec.get("out"))), number(col(r, spec.get("in")))
            if out is None and inn is None:
                raise ParseError(f"a row on {d} has neither money out nor money in")
            amt = (inn or 0.0) - abs(out or 0.0)
        bal = number(col(r, spec["balance"])) if spec.get("balance") is not None else None
        rows.append({"date": d, "description": desc, "amount": round(sign * amt, 2),
                     "balance": None if bal is None else round(bal, 2)})
    if not rows:
        raise ParseError("no row with a date this map can read")
    if skipped > 3:
        raise ParseError(f"{skipped} lines had no date the map can read — the date column or its format is wrong")
    # Some banks list the newest first. The ledger runs oldest first.
    if rows[0]["date"] > rows[-1]["date"]:
        rows.reverse()
    out = {"parser": "csv", "file": path, "account": None,
           "period": {"from": rows[0]["date"], "to": rows[-1]["date"]},
           "opening": None, "closing": None, "rows": rows, "totals": {},
           "product": None, "holder": None, "kind": None}
    if all(r["balance"] is not None for r in rows):
        breaks = [(a, b) for a, b in zip(rows, rows[1:]) if abs(a["balance"] + b["amount"] - b["balance"]) > 0.005]
        out["opening"] = round(rows[0]["balance"] - rows[0]["amount"], 2)
        out["closing"] = rows[-1]["balance"]
        out["reconcile"] = {"rule": "every balance follows from the one before it",
                            "ok": not breaks,
                            "detail": (f"{len(rows)} rows, {out['opening']:,.2f} to {out['closing']:,.2f}, every balance follows"
                                       if not breaks else
                                       f"the balance after {breaks[0][0]['date']} {breaks[0][0]['balance']:,.2f} does not lead to "
                                       f"{breaks[0][1]['balance']:,.2f} on {breaks[0][1]['date']}")}
    else:
        out["reconcile"] = {"rule": "checked against the balance the banking app shows", "ok": False,
                            "needs_balance": True,
                            "detail": f"{len(rows)} rows and no running balance — say the balance your banking app shows"}
    return out

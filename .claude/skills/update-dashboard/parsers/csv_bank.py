"""csv_bank — a bank's own transaction download (CSV), read by the column map the register keeps.

Most Canadian banks let you download an account's recent transactions as a spreadsheet: TD,
Scotiabank, CIBC, Tangerine and Simplii among them (2026-11-03, user 001: lower the barrier
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
# Each comes from open-source importers' configs and fixtures (2025-26), not from a bank: no bank
# documents its columns. `verified` stays False until a real file from that bank has been read and
# reconciled here. Order matters for files with no header: the first map that reads every row
# wins, so the stricter ones come first. EQ Bank is left out on purpose: nothing showed its columns.
PROFILES = {
    # TD, chequing and Visa: no header; date, description, money out, money in, balance. Chequing
    # dates have moved to YYYY-MM-DD, the Visa's are still MM/DD/YYYY, so the format is left to
    # each file. A card's balance column counts what is owed, the other way round from chequing.
    "td": {"label": "TD", "header": False, "date": 0, "description": 1, "out": 2, "in": 3, "balance": 4,
           "columns": (5,), "verified": False},
    # CIBC: no header, YYYY-MM-DD; chequing date, description, out, in (sometimes a fifth column);
    # a card's fifth column is its masked number, never a balance, so no balance is read.
    "cibc": {"label": "CIBC", "header": False, "date": 0, "dateFormat": "%Y-%m-%d", "description": 1,
             "out": 2, "in": 3, "columns": (4, 5), "verified": False},
    # Scotiabank's current download: a header, a byte-order mark, YYYY-MM-DD, the merchant in
    # Sub-description. Chequing has a signed Amount and a Balance; a card has Status, no Balance,
    # and shows a purchase as a positive amount. The web export stops at 100 rows.
    "scotia": {"label": "Scotiabank", "header": True, "date": "Date", "dateFormat": "%Y-%m-%d",
               "description": ["Sub-description", "Description"], "amount": "Amount", "balance": "Balance",
               "match": {"Filter", "Date", "Sub-description", "Type of Transaction", "Amount", "Balance"},
               "cap": 100, "verified": False},
    "scotia_card": {"label": "Scotiabank", "header": True, "date": "Date", "dateFormat": "%Y-%m-%d",
                    "description": ["Sub-description", "Description"], "amount": "Amount", "sign": -1,
                    "match": {"Filter", "Date", "Sub-description", "Status", "Type of Transaction", "Amount"},
                    "cap": 100, "verified": False},
    # Tangerine: a header naming the date either way, M/D/YYYY, one signed Amount, no balance.
    "tangerine": {"label": "Tangerine", "header": True, "date": "Date", "dateFormat": "%m/%d/%Y",
                  "description": ["Name", "Memo"], "amount": "Amount",
                  "match": {"Date", "Transaction", "Name", "Memo", "Amount"}, "verified": False},
    "tangerine_alt": {"label": "Tangerine", "header": True, "date": "Transaction date", "dateFormat": "%m/%d/%Y",
                      "description": ["Name", "Memo"], "amount": "Amount",
                      "match": {"Transaction date", "Transaction", "Name", "Memo", "Amount"}, "verified": False},
    # Simplii: a header with spaces after the commas (names are read stripped), MM/DD/YYYY, no balance.
    "simplii": {"label": "Simplii", "header": True, "date": "Date", "dateFormat": "%m/%d/%Y",
                "description": "Transaction Details", "out": "Funds Out", "in": "Funds In",
                "match": {"Date", "Transaction Details", "Funds Out", "Funds In"}, "verified": False},
    # RBC: one file for every account, a header, M/D/YYYY, one signed amount in CAD$, no balance;
    # each row names its account. Confirmed on a real download (2026-11-03, user 001): 28 chequing
    # rows matched the ledger read from the PDFs one for one, and the Visa's purchases matched too.
    "rbc": {"label": "RBC", "header": True, "date": "Transaction Date", "dateFormat": "%m/%d/%Y",
            "description": ["Description 1", "Description 2"], "amount": "CAD$", "account": "Account Number",
            "kindCol": "Account Type", "match": {"Account Type", "Account Number", "Transaction Date", "Description 1", "CAD$"},
            "verified": True},
    # Scotiabank's older download: no header; date, signed amount, "-", type, description.
    "scotia_old": {"label": "Scotiabank", "header": False, "date": 0, "dateFormat": "%m/%d/%Y", "amount": 1,
                   "description": [3, 4], "columns": (5,), "verified": False},
}
MAP_KEYS = ("header", "date", "dateFormat", "description", "amount", "out", "in", "balance", "sign", "cap",
            "account", "kindCol")


def spec_of(key):
    """The map a profile drafts: what goes into the register's `csv`, nothing else."""
    return {k: v for k, v in PROFILES[key].items() if k in MAP_KEYS}


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
    """The profile whose layout the file has, or None. A file with a header is matched on its
    column names; one without is matched by the first map that reads every row. A suggestion
    for setup, never a reading: the map that is used is the one in the register."""
    lines = read_lines(path)
    if not lines:
        return None
    head = {c.strip() for c in lines[0]}
    for key, p in PROFILES.items():
        if p.get("header") and p["match"] <= head:
            return key
    for key, p in PROFILES.items():
        if p.get("header") or not all(len(r) in p["columns"] for r in lines):
            continue
        try:
            parse(path, spec_of(key))
            return key
        except ParseError:
            continue
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
        row = {"date": d, "description": desc, "amount": round(sign * amt, 2),
               "balance": None if bal is None else round(bal, 2)}
        if spec.get("account") is not None:       # one download, several accounts (RBC)
            row["_acct"] = (re.sub(r"\D", "", col(r, spec["account"]) or "")[-4:],
                            (col(r, spec["kindCol"]) or "").strip() if spec.get("kindCol") is not None else "")
        rows.append(row)
    if not rows:
        raise ParseError("no row with a date this map can read")
    if skipped > 3:
        raise ParseError(f"{skipped} lines had no date the map can read — the date column or its format is wrong")
    # A bank that stops its download at a fixed number of rows (Scotiabank: 100) has cut this one
    # off if it holds exactly that many: the rest would be missing without a word.
    if spec.get("cap") and len(rows) >= spec["cap"]:
        raise ParseError(f"exactly {len(rows)} rows, the most this bank puts in one download, so it is cut off — "
                         f"download one statement period at a time")
    if spec.get("account") is None:
        return one(path, rows)
    groups = {}
    for x in rows:
        groups.setdefault(x.pop("_acct"), []).append(x)
    parts = [dict(one(path, g), account=d4, kind=KIND_OF.get(kind.lower(), kind or None)) for (d4, kind), g in groups.items()]
    ok = all(p_["reconcile"]["ok"] for p_ in parts)
    return {"parser": "csv", "file": path, "account": None, "accounts": parts,
            "period": {"from": min(p_["period"]["from"] for p_ in parts), "to": max(p_["period"]["to"] for p_ in parts)},
            "opening": None, "closing": None, "rows": [x for p_ in parts for x in p_["rows"]], "totals": {},
            "product": None, "holder": None, "kind": None,
            "reconcile": {"rule": "each account by its own balances", "ok": ok,
                          "needs_balance": any(p_["reconcile"].get("needs_balance") for p_ in parts),
                          "detail": "; ".join(f"…{p_['account']}: {p_['reconcile']['detail']}" for p_ in parts)}}


KIND_OF = {"chequing": "Chequing", "savings": "Savings", "visa": "Credit card", "mastercard": "Credit card",
           "credit card": "Credit card"}


def one(path, rows):
    """One account's rows, oldest first, reconciled by its balances when it has them."""
    # Oldest first, the way the ledger runs. A file listed newest first is turned round whole, so
    # rows of one day keep their order against their balances; one in no order at all is sorted.
    pairs = list(zip(rows, rows[1:]))
    if pairs and all(a["date"] >= b["date"] for a, b in pairs) and rows[0]["date"] > rows[-1]["date"]:
        rows = rows[::-1]
    elif any(a["date"] > b["date"] for a, b in pairs):
        rows = sorted(rows, key=lambda x: x["date"])
    out = {"parser": "csv", "file": path, "account": None,
           "period": {"from": rows[0]["date"], "to": rows[-1]["date"]},
           "opening": None, "closing": None, "rows": rows, "totals": {},
           "product": None, "holder": None, "kind": None}
    if all(r["balance"] is not None for r in rows):
        # A card's balance counts what is owed, so it runs the other way from the money: a
        # purchase (negative) raises it. Whichever way every row follows is the way it runs; the
        # register keeps a card's balance as a negative number, so an owed balance is flipped.
        follows = lambda k: [(a, b) for a, b in zip(rows, rows[1:]) if abs(k * a["balance"] + b["amount"] - k * b["balance"]) > 0.005]
        if follows(1) and len(rows) > 1 and not follows(-1):
            for r_ in rows:
                r_["balance"] = -r_["balance"]
            out["owed"] = True
        breaks = follows(1)
        out["opening"] = round(rows[0]["balance"] - rows[0]["amount"], 2)
        out["closing"] = rows[-1]["balance"]
        if out.get("owed"):                    # a card prints what is owed, a positive number
            out["opening"], out["closing"] = -out["opening"], -out["closing"]
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

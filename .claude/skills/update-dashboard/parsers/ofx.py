"""ofx — a bank's OFX or QFX download (the "Money" / "Quicken" choice in online banking).

OFX is one standard, not one layout per bank, and it carries what a CSV lacks (2026-11-04, user
001: a real BMO download read every chequing row of two months the way the PDFs had, one for
one): each account on its own with the bank's id for it, its type and currency, every transaction
with an id of its own (FITID), and the balance the bank holds now (LEDGERBAL). So it reconciles
by itself: the bank's balance less every transaction is the balance before the first, and that
has to be the balance the books already end on.

The old OFX 1.x is SGML: tags with no closing tag, one per line. OFX 2.x is XML. Both are read
the same way here, by tag, never by line position. A description is NAME and MEMO together:
BMO cuts a merchant at 32 characters into NAME and carries the rest in MEMO.

Every account comes back as a part, with the shape the other parsers use:

    {"account": "<the bank's id>", "kind": "Chequing" | "Savings" | "Credit card",
     "cur": "CAD", "period": {...}, "opening", "closing",   # closing: the bank's balance
     "rows": [{"date", "description", "amount", "balance", "fitid"}],
     "reconcile": {"ok": True, "bank_balance": True, ...}}

Amounts are the ledger's way (money out negative). A card's balance is what OFX says: negative
when money is owed, the way the register keeps it.
"""
import html
import re

from . import ParseError

KINDS = {"CHECKING": "Chequing", "SAVINGS": "Savings", "MONEYMRKT": "Savings", "CREDITLINE": "Line of credit"}

# BMO puts a two-letter transaction code before the description ("[DN]ACME PAYROLL/PAY"); its
# PDF statement spells the same row out ("Direct Deposit, ACME PAYROLL/PAY"), and that is what
# the import's typing reads. Each code here was matched against a PDF row of the same date and
# amount on a real download (2026-11-04); a code not listed is left as the bank wrote it.
CODES = {"DN": "Direct Deposit, ", "DS": "Pre-Authorized Payment, ", "PR": "Debit Card Purchase, ",
         "IN": "Interest ", "DC": "Fee, ", "DM": "Draft, ", "CM": "Wire, "}


def spell(desc):
    m = re.match(r"\[([A-Z]{2})\]\s*(.*)", desc)
    if not m:
        return desc
    code, rest = m.group(1), m.group(2).strip()
    if code == "CW":                                  # a customer's own move: e-Transfer or transfer
        if re.match(r"INTERAC ETRNSFR", rest):
            return "INTERAC e-Transfer " + rest[len("INTERAC ETRNSFR"):].strip().title()
        return "Online Transfer, " + rest
    if code == "SC":                                  # a service charge: the plan fee and its rebate
        return rest if "FEE" in rest.upper() else rest + " Fee"
    return CODES.get(code, "") + rest if code in CODES else desc


def _val(block, name):
    m = re.search(r"<" + name + r">([^<\r\n]*)", block)
    return m.group(1).strip() if m else None


def _date(s):
    s = (s or "").strip()
    if not re.match(r"\d{8}", s):
        raise ParseError(f"not an OFX date: {s!r}")
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ParseError("not a text file")


def accounts_in(path):
    """The bank's ids of the accounts a file carries, cheaply, for naming it."""
    t = read_text(path)
    return re.findall(r"<ACCTID>([^<\r\n]+)", t)


def parse(path):
    t = read_text(path)
    if "<OFX>" not in t.upper():
        raise ParseError("not an OFX file")
    blocks = [("bank", b) for b in re.findall(r"<STMTRS>(.*?)</STMTRS>", t, re.S)] + \
             [("card", b) for b in re.findall(r"<CCSTMTRS>(.*?)</CCSTMTRS>", t, re.S)]
    if not blocks:
        raise ParseError("an OFX file with no account statement in it")
    parts = []
    for kind, b in blocks:
        acct = _val(b, "ACCTID")
        if not acct:
            raise ParseError("an account with no ACCTID")
        led = re.search(r"<LEDGERBAL>(.*?)(?:</LEDGERBAL>|<AVAILBAL>|$)", b, re.S)
        if not led or _val(led.group(1), "BALAMT") is None:
            raise ParseError(f"account …{acct[-4:]} carries no balance (LEDGERBAL)")
        bal = round(float(_val(led.group(1), "BALAMT")), 2)
        asof = _date(_val(led.group(1), "DTASOF"))
        rows = []
        for tr in re.findall(r"<STMTTRN>(.*?)</STMTTRN>", b, re.S):
            amt = _val(tr, "TRNAMT")
            if amt is None:
                raise ParseError(f"a transaction of …{acct[-4:]} with no amount")
            name = re.search(r"<NAME>([^\r\n<]*)", tr)
            memo = re.search(r"<MEMO>([^\r\n<]*)", tr)
            desc = ((name.group(1) if name else "") + (memo.group(1) if memo else "")).strip()
            raw = re.sub(r"\s{2,}", " ", html.unescape(desc))      # RBC writes & as &amp;
            rows.append({"date": _date(_val(tr, "DTPOSTED")), "description": spell(raw), "raw": raw,
                         "amount": round(float(amt), 2), "fitid": _val(tr, "FITID")})
        rows.sort(key=lambda r: r["date"])           # stable: a day's rows keep the bank's order
        ids = [r["fitid"] for r in rows if r["fitid"]]
        if len(set(ids)) != len(ids):
            raise ParseError(f"account …{acct[-4:]} lists one transaction id twice")
        # Every row's balance, back from the bank's: the last row ends on it.
        run = bal
        for r in reversed(rows):
            r["balance"] = run
            run = round(run - r["amount"], 2)
        opening = run
        kind_name = "Credit card" if kind == "card" else KINDS.get((_val(b, "ACCTTYPE") or "").upper(), "Chequing")
        start, end = _val(b, "DTSTART"), _val(b, "DTEND")
        parts.append({
            "parser": "ofx", "file": path, "account": acct, "kind": kind_name, "cur": _val(b, "CURDEF") or "CAD",
            "period": {"from": rows[0]["date"] if rows else (_date(start) if start else asof),
                       "to": rows[-1]["date"] if rows else asof},
            "asof": asof, "opening": opening, "closing": bal, "rows": rows, "totals": {},
            "product": None, "holder": None,
            "reconcile": {"rule": "the bank's balance less every transaction is the balance before the first",
                          "ok": True, "bank_balance": True,
                          "detail": f"{len(rows)} rows, {opening:,.2f} to the bank's {bal:,.2f} on {asof}"}})
    if len(parts) == 1:
        return parts[0]
    return {"parser": "ofx", "file": path, "account": None, "accounts": parts,
            "period": {"from": min(p["period"]["from"] for p in parts), "to": max(p["period"]["to"] for p in parts)},
            "opening": None, "closing": None, "rows": [r for p in parts for r in p["rows"]], "totals": {},
            "product": None, "holder": None, "kind": None,
            "reconcile": {"rule": "each account by the bank's balance", "ok": True, "bank_balance": True,
                          "detail": "; ".join(f"…{p['account'][-4:]}: {p['reconcile']['detail']}" for p in parts)}}

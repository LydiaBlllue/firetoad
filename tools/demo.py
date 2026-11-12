#!/usr/bin/env python3
"""A whole year of made-up money for the public build.

The tool is only worth showing with data in it, and the real data is the one thing that
cannot be shown. So this file invents a person -- Emma Roy, 32, an office worker in Ottawa,
single, renting, paid twice a month -- and writes every findata/ file the tool reads,
internally consistent: every balance chain closes, every card statement adds up, the bond
share is inside its band. check_data.py is the proof; it runs on the output.

She is deliberately ordinary (2026-11-03, user 001: "less complex, more general, not like
me"): one bank (chequing, savings, one card), one broker (a TFSA and an RRSP), three index
funds, no single stocks, no crypto, no foreign money, nobody owing her anything. Nothing here
is copied from a real account.

    build(out_dir) -> ctx        writes <out_dir>/findata/* and returns what the release
                                 build needs to splice into the two dashboards
"""
import csv, json, os, random, datetime as dt, math

NOTE_IMPORTS = "One record per 'update dashboards', newest last: the files that came in, what changed (label / from / to), what was noticed (sev ok / warn / bad + text), what was decided without asking (`judged`) and what the owner was asked (`asked`). Data → Updates renders it; the import report IS this record. Every sentence here reaches the page: write it about the owner's money, never about the tool — no 'I', no rule numbers, no file names."
NOTE_DEC = "What is waiting for the owner to confirm, written by the import: a merchant seen for the first time, an e-Transfer typed by default, a transfer whose other side is unknown, a file nobody could name. Each item: `added`, `kind` (merchant / transfer / file / classification), `what` (one sentence, about the money), `default` (what was assumed meanwhile), `source` (which statement, which line), `status` open / confirmed, and once confirmed `answer` and `resolved`. Data → Updates lists the open ones and the page header counts them. Separate from tasks.json: these are produced by an import and disappear on a word; tasks are the owner's own."

from collections import defaultdict, OrderedDict
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 ".claude", "skills", "workspace-checks", "scripts"))
from check_data import merchant_key  # one normalisation, owned by the checker
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 ".claude", "skills", "setup", "scripts"))
from scaffold import default_axes, flow_feeds  # the five axes, owned by setup
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 ".claude", "skills", "update-dashboard", "scripts"))
from update import SPENT, payee_of  # which chequing rows are spending, and who was paid: the import's
import layout  # where each findata file lives (schema 6)

TODAY = "2026-09-08"
FX = 1.3712                      # USD/CAD used everywhere below
SEED = 20260908

P = dict(first="Emma", last="Roy", name="Emma Roy", initials="ER", upper="EMMA ROY", age=32,
         city="Ottawa", pay=2150.00, rent=1450.00, invest=700, emergency=300, everyday=1500)

ID = dict(bmo_chq="4471", bmo_sav="9032", bmo_mc="5518", tfsa="HQ7TF4A21CAD", rrsp="HQ7RR9B33CAD")

# ------------------------------------------------------------------ small date helpers
def D(y, m, d): return dt.date(y, m, d)
def iso(d): return d.isoformat()
def ym(d): return d.strftime("%Y-%m")
def month_end(y, m): return D(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1)
def stmt_after(d, day):
    """First `day`-of-month on or after d: the statement a transaction lands on."""
    if d.day <= day: return D(d.year, d.month, day)
    y, m = (d.year + 1, 1) if d.month == 12 else (d.year, d.month + 1)
    return D(y, m, day)
def tag(d, day): return stmt_after(d, day).strftime("%Y%m%d")
def months(a, b):
    y, m = a
    while (y, m) <= b:
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
def r2(x): return float(f"{x:.2f}")

# ------------------------------------------------------------------ spending
SUBS_FIXED = [   # merchant, amount, day, category — the charges that come back every month
 ("SPOTIFY SPOTIFY.COM", 11.29, 4, "Entertainment"),
 ("NETFLIX.COM NETFLIX.COM", 18.99, 12, "Entertainment"),
 ("APPLE.COM/BILL TORONTO ON", 3.99, 16, "Entertainment"),
 ("KOODO MOBILE", 45.20, 10, "Bills"),
 ("GOODLIFE FITNESS TORONTO ON", 32.99, 1, "Health"),
 ("AMAZON PRIME MEMBER AMAZON.CA", 10.99, 22, "Shopping"),
 ("OC TRANSPO MONTHLY PASS OTTAWA ON", 135.00, 26, "Transport"),
 ("ROGERS INTERNET 888-764-3771 ON", 75.00, 8, "Bills"),
]
VAR = [          # merchant, category, times a month, low, high, may go on the MasterCard
 ("LOBLAWS 1234 OTTAWA ON", "Grocery", 2, 45, 110, False),
 ("FARM BOY #17 OTTAWA ON", "Grocery", 3, 18, 55, True),
 ("COSTCO WHOLESALE W1211 OTTAWA ON", "Grocery", 1, 95, 175, True),
 ("METRO 456 OTTAWA ON", "Grocery", 1, 25, 65, True),
 ("TIM HORTONS #2231 OTTAWA ON", "Dining", 3, 3.5, 9, False),
 ("UBER CANADA/UBEREATS TORONTO ON", "Dining", 2, 22, 48, True),
 ("SUBWAY 40112 OTTAWA ON", "Dining", 1, 11, 16, True),
 ("THAI EXPRESS OTTAWA ON", "Dining", 1, 13, 19, True),
 ("STARBUCKS 1100 OTTAWA ON", "Dining", 1, 5, 8, False),
 ("AMAZON.CA AMAZON.CA", "Shopping", 1, 15, 80, False),
 ("AMZN MKTP CA", "Shopping", 1, 12, 60, True),
 ("SHOPPERS DRUG MART 0781 OTTAWA ON", "Health", 2, 8, 45, True),
 ("DOLLARAMA #1052 OTTAWA ON", "Shopping", 1, 4, 18, False),
 ("WINNERS 3215 OTTAWA ON", "Shopping", 0.5, 25, 90, True),
 ("CANADIAN TIRE #030 OTTAWA ON", "Shopping", 0.4, 15, 80, True),
 ("UBER CANADA/UBERTRIP TORONTO ON", "Transport", 1, 12, 28, True),
 ("CINEPLEX 7620 OTTAWA ON", "Entertainment", 0.5, 14, 30, True),
 ("STEAM PURCHASE SEATTLE WA", "Entertainment", 0.3, 10, 40, False),
 ("CANADA POST OTTAWA ON", "Other", 0.3, 5, 20, False),
]
ONE_OFF = [      # date, merchant, amount, category, card
 ("2026-06-14", "BEST BUY #957 OTTAWA ON", 429.99, "Shopping"),
 ("2026-04-25", "IKEA OTTAWA ON", 186.40, "Shopping"),
 ("2026-07-18", "TICKETMASTER CANADA TORONTO ON", 92.50, "Entertainment"),
]
MC_DAY, BMO_DAY = 20, 5
MC_LAST = "20260820"                                 # newest card statement on hand
SPEND_FROM, SPEND_TO = D(2025, 12, 21), D(2026, 8, 20)

def gen_spending(rng):
    rows = []   # dict(date, amount, category, merchant, acct, stmt): everything goes on the one card
    def add(d, merchant, amt, cat):
        t = tag(d, MC_DAY)
        if t > MC_LAST: return
        rows.append(dict(date=d, amount=r2(amt), category=cat, merchant=merchant, acct=f"BMO{ID['bmo_mc']}", stmt=t))
    for y, m in months((2025, 12), (2026, 8)):
        last = month_end(y, m).day
        for merchant, amt, day, cat in SUBS_FIXED:
            d = D(y, m, min(day, last))
            if SPEND_FROM <= d <= SPEND_TO: add(d, merchant, amt, cat)
        for merchant, cat, n, lo, hi, _ in VAR:
            k = int(n) + (1 if rng.random() < n - int(n) else 0)
            for _ in range(k):
                d = D(y, m, rng.randint(1, last))
                if SPEND_FROM <= d <= SPEND_TO: add(d, merchant, rng.uniform(lo, hi), cat)
    for ds, merchant, amt, cat in ONE_OFF:
        add(dt.date.fromisoformat(ds), merchant, amt, cat)
    rows.sort(key=lambda r: (r["date"], r["merchant"]))
    return rows

# ------------------------------------------------------------------ ledgers
def gen_ledgers(rng, spend):
    """BMO chequing (pay in, rent, the card, the broker) and BMO savings (the emergency fund)."""
    mc_tot = defaultdict(float)
    for r in spend:
        mc_tot[r["stmt"]] += r["amount"]
    debit_bmo = []
    ev = []             # (date, description, amount, typed desc, type)
    A = ev.append
    for y, m in months((2025, 12), (2026, 9)):
        last = month_end(y, m).day
        if (y, m) > (2025, 12):
            A((D(y, m, 1), "Pre-AuthorizedPayment,OTTAWA PROP MGMT RENT", -P["rent"], "Rent (pre-authorized)", "Rent"))
            A((D(y, m, 2), "Pre-AuthorizedPayment,WSINVESTMENTSINV/PLA", -P["invest"] / 2, "Transfer to Wealthsimple", "Transfer"))
            A((D(y, m, 5), f"OnlineTransfer,TF0006#{ID['bmo_chq']}-{ID['bmo_sav']}", -float(P["emergency"]), "Transfer to savings", "Transfer"))
            A((D(y, m, 12), "Pre-AuthorizedPayment,HYDRO OTTAWA", -r2(rng.uniform(58, 96)), "Hydro Ottawa", "Bill"))
        A((D(y, m, 15), "DirectDeposit,ADP CANADA PAY/PAY", P["pay"], "Payroll deposit (ADP)", "Payroll"))
        A((D(y, m, 17), "Pre-AuthorizedPayment,WSINVESTMENTSINV/PLA", -P["invest"] / 2, "Transfer to Wealthsimple", "Transfer"))
        mt = mc_tot.get(f"{y}{m:02d}{MC_DAY}", 0.0)
        if mt: A((D(y, m, 22), f"OnlineTransfer,TF0005519880045{ID['bmo_mc']}", -r2(mt), "MasterCard payment", "CC payment"))
        A((D(y, m, last), "DirectDeposit,ADP CANADA PAY/PAY", P["pay"], "Payroll deposit (ADP)", "Payroll"))
        A((D(y, m, last), "PerformancePlanFee", -16.95, "Plan fee", "Fee"))
    # The $200 nobody named: the open item on Updates, typed Other income meanwhile.
    A((D(2026, 8, 11), "INTERACe-TransferReceived", 200.0, "e-Transfer received", "Other"))
    for ds, short, amt, cat in (("2026-03-25", "SHOPPERS DRUG MART 0781", 24.60, "Health"),
                                ("2026-05-09", "FARM BOY #17", 18.35, "Grocery"),
                                ("2026-07-02", "TIM HORTONS #2231", 6.45, "Dining")):
        d = dt.date.fromisoformat(ds)
        A((d, f"Contactless Interac purchase,{short}", -amt, f"Debit purchase — {short.title()}", "Debit purchase"))
        debit_bmo.append(dict(date=d, amount=amt, category=cat, merchant=f"{short} OTTAWA ON",
                              acct=f"BMO{ID['bmo_chq']}", stmt=tag(d, BMO_DAY), debit=True))
    ev = [e for e in ev if D(2025, 12, 6) <= e[0] <= D(2026, 9, 5)]     # through the Sep 5 statement
    ev.sort(key=lambda e: e[0])
    bal = 2140.55
    bmo = []
    for d, desc, amt, tdesc, typ in ev:
        bal = r2(bal + amt)
        bmo.append(dict(date=d, description=desc, amount=r2(amt), balance=bal,
                        statement=f"BMOCHQ{ID['bmo_chq']}/{tag(d, BMO_DAY)}", tdesc=tdesc, type=typ))
    assert min(r["balance"] for r in bmo) > 0, "BMO chequing went negative"

    # Savings: the emergency fund, $300 a month from chequing on the 5th, and its interest.
    sav_ev = []
    for y, m in months((2026, 1), (2026, 9)):
        sav_ev.append((D(y, m, 5), f"OnlineTransfer,TF0006#{ID['bmo_chq']}-{ID['bmo_sav']}", float(P["emergency"]), "Transfer from chequing", "Transfer"))
        if (y, m) < (2026, 9):
            sav_ev.append((month_end(y, m), "InterestEarned", r2(0.9 + m * 0.11), "Interest", "Interest"))
    bal = 4200.00; sav = []
    for d, desc, amt, tdesc, typ in sav_ev:
        bal = r2(bal + amt)
        sav.append(dict(date=d, description=desc, amount=r2(amt), balance=bal,
                        statement=f"BMOSAV{ID['bmo_sav']}/{tag(d, BMO_DAY)}", tdesc=tdesc, type=typ))
    # A chequing row that is spending (rent, a bill, a bank's fee) is written to spending.csv too,
    # by the same rule the import uses, so the round trip finds the demo's own rows.
    paid = []
    for r in bmo:
        if r["type"] in SPENT and r["type"] != "Debit purchase" and r["amount"] < 0:
            paid.append(dict(date=r["date"], amount=-r["amount"], category=SPENT[r["type"]],
                             merchant=payee_of(r["description"]), acct=f"BMO{ID['bmo_chq']}",
                             stmt=r["statement"].split("/")[1], via="chequing"))
    return bmo, sav, debit_bmo + paid, mc_tot

# ------------------------------------------------------------------ holdings
PRICE = {"VEQT": 46.10, "XAW": 44.80, "ZAG": 14.20}
USD_SYMS = set()
NAME = {"VEQT": "Vanguard All-Equity ETF Portfolio - ETF",
        "XAW": "iShares Core MSCI All Country World ex Canada Index ETF",
        "ZAG": "BMO Aggregate Bond Index ETF", "CAD": "CAD"}
SEC = {"CAD": "CURRENCY"}
ACCTS = [("TFSA", "tfsa"), ("RRSP", "rrsp")]
# account, symbol, target CAD market value, book value as a ratio of market value
TARGETS = [
 ("TFSA", "VEQT", 27500, 1/1.16), ("TFSA", "XAW", 6200, 1/1.12), ("TFSA", "ZAG", 5200, 1.02), ("TFSA", "CAD", 210, 1),
 ("RRSP", "VEQT", 8800, 1/1.14), ("RRSP", "ZAG", 3300, 1.02), ("RRSP", "CAD", 80, 1),
]
PORT_ACCTS = {"TFSA", "RRSP"}
EARM_ACCTS = set()
BONDS = {"ZAG"}

def gen_holdings():
    key = {a: k for a, k in ACCTS}
    pos = []
    for acct, sym, target, ratio in TARGETS:
        aid = ID[key[acct]]
        if sym == "CAD":
            pos.append(dict(acct=acct, aid=aid, sym=sym, qty=float(target), price=1.0, cur="CAD",
                            mv_mkt=float(target), mv_cad=float(target), bv_cad=float(target), bv_mkt=float(target)))
            continue
        price = PRICE[sym]
        if sym in USD_SYMS:
            qty = round(target / FX / price, 4)
            mv_mkt = r2(qty * price); mv_cad = r2(mv_mkt * FX)
            bv_cad = r2(mv_cad * ratio); bv_mkt = r2(bv_cad / FX); cur = "USD"
        else:
            qty = round(target / price, 8 if sym == "BTC" else 4)
            mv_mkt = r2(qty * price); mv_cad = mv_mkt
            bv_cad = r2(mv_cad * ratio); bv_mkt = bv_cad; cur = "CAD"
        pos.append(dict(acct=acct, aid=aid, sym=sym, qty=qty, price=price, cur=cur,
                        mv_mkt=mv_mkt, mv_cad=mv_cad, bv_cad=bv_cad, bv_mkt=bv_mkt))
    return pos

HOLD_HEADER = ["Account Name", "Account Type", "Account Classification", "Account Number", "Symbol", "Exchange", "MIC",
               "Name", "Security Type", "Quantity", "Position Direction", "Market Price", "Market Price Currency",
               "Book Value (CAD)", "Book Value Currency (CAD)", "Book Value (Market)", "Book Value Currency (Market)",
               "Market Value", "Market Value Currency", "Market Unrealized Returns", "Market Unrealized Returns Currency"]

# ------------------------------------------------------------------ Wealthsimple activities
ACT_HEADER = ["effective_date", "effective_time", "settlement_date", "account_id", "account_type", "activity_type",
              "activity_sub_type", "description", "direction", "symbol", "underlying symbol", "name", "currency",
              "quantity", "unit_price", "commission", "net_cash_amount"]

def gen_activities(rng, pos):
    """The two monthly deposits go straight into the TFSA and buy VEQT; the three funds pay
    their distributions; the RRSP gets one contribution before the deadline."""
    rows = []
    def act(d, aid, atype, kind, sub, desc, cur, amt, sym="", name="", qty="", price=""):
        rows.append([iso(d), f"{rng.randint(9,16):02d}:{rng.randint(0,59):02d}:{rng.randint(0,59):02d}", "", aid, atype, kind, sub,
                     desc, "", sym, "", name, cur, qty, price, "", f"{amt:.2f}"])
    mv = defaultdict(float)
    for p in pos: mv[(p["acct"], p["sym"])] += p["mv_cad"]
    for y, m in months((2026, 1), (2026, 9)):
        for day in (2, 17):
            d = D(y, m, day)
            if d > dt.date.fromisoformat(TODAY): continue
            act(d, ID["tfsa"], "TFSA", "MoneyMovement", "EFT", "Deposit", "CAD", P["invest"] / 2)
        if (y, m) < (2026, 9):
            d = D(y, m, 19); q = round(P["invest"] / PRICE["VEQT"], 4)
            act(d, ID["tfsa"], "TFSA", "Trade", "BUY", f"VEQT - {NAME['VEQT']}: Bought {q} shares at ${PRICE['VEQT']} per share (executed at {iso(d)})",
                "CAD", -P["invest"], "VEQT", NAME["VEQT"], q, PRICE["VEQT"])
            for acct, aid in (("TFSA", ID["tfsa"]), ("RRSP", ID["rrsp"])):
                cad = mv[(acct, "ZAG")] * 0.034 / 12
                if cad: act(D(y, m, 6), aid, acct, "Dividend", "-", f"ZAG - {NAME['ZAG']}: Cash dividend distribution", "CAD", r2(cad), "ZAG", NAME["ZAG"])
            if m in (1, 4, 7):
                for acct, aid in (("TFSA", ID["tfsa"]), ("RRSP", ID["rrsp"])):
                    act(D(y, m, 12), aid, acct, "Dividend", "-", f"VEQT - {NAME['VEQT']}: Cash dividend distribution", "CAD",
                        r2(mv[(acct, "VEQT")] * 0.019 / 4), "VEQT", NAME["VEQT"])
            act(D(y, m, month_end(y, m).day), ID["tfsa"], "TFSA", "Interest", "-", "Stock lending monthly interest payment", "CAD", r2(0.02 + rng.random() * 0.05))
    act(D(2026, 6, 25), ID["tfsa"], "TFSA", "Dividend", "-", f"XAW - {NAME['XAW']}: Cash dividend distribution", "CAD",
        r2(mv[("TFSA", "XAW")] * 0.017 / 2), "XAW", NAME["XAW"])
    d = D(2026, 2, 20)
    act(d, ID["rrsp"], "RRSP", "MoneyMovement", "EFT", "Contribution", "CAD", 1500.0)
    q = round(1500 / PRICE["VEQT"], 4)
    act(D(2026, 2, 23), ID["rrsp"], "RRSP", "Trade", "BUY", f"VEQT - {NAME['VEQT']}: Bought {q} shares at ${PRICE['VEQT']} per share (executed at 2026-02-23)",
        "CAD", -1500.0, "VEQT", NAME["VEQT"], q, PRICE["VEQT"])
    rows.sort(key=lambda r: r[0])
    return rows

# ------------------------------------------------------------------ everything
def build(out):
    """Write the demo owner's whole findata/ (and OWNER.md). The dashboards are then built from
    templates/dashboards/ by rebuild.py, like any other workspace -- this script writes data
    only, never a line of page code."""
    rng = random.Random(SEED)
    layout.ensure(out)
    W = lambda name: open(layout.path(out, name), "w", encoding="utf-8", newline="")
    J = lambda name, obj: open(layout.path(out, name), "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

    spend = gen_spending(rng)
    bmo, sav, debits, mc_tot = gen_ledgers(rng, spend)
    allspend = sorted(spend + debits, key=lambda r: (r["date"], r["merchant"]))

    # spending.csv + merchants.json
    with W("spending.csv") as f:
        w = csv.writer(f); w.writerow(["date", "amount", "currency", "category", "note"])
        for r in allspend:
            via = "debit" if r.get("debit") else r.get("via")
            note = f"{r['merchant']}{f' ({via})' if via else ''} [{r['acct']}/{r['stmt']}]"
            w.writerow([iso(r["date"]), f"{r['amount']:.2f}", "CAD", r["category"], note])
    # Keyed the way check_data's D6 looks a merchant up (order ids and city dropped), so the
    # demo passes the same lookup a real import does.
    seen = OrderedDict()
    for r in allspend:
        mk = merchant_key(r["merchant"])
        m = seen.setdefault(mk, dict(match=mk, category=r["category"], seen=0, first=iso(r["date"]), last=iso(r["date"])))
        m["seen"] += 1; m["first"] = min(m["first"], iso(r["date"])); m["last"] = max(m["last"], iso(r["date"]))
    J("merchants.json", OrderedDict([
        ("note", "Merchant -> spending category, the only place a category is decided. Look a new statement's merchants up here first; reuse a hit, judge only a miss, and append the miss."),
        ("why", "A merchant string is an abbreviation, not a sentence: a shop with PUBLICATION in its name sold a notebook, not a subscription."),
        ("rules", ["Subscription is not a category: a charge that repeats is marked by the page, whatever it bought. File a merchant by what it sells.",
                   "An entry with confirmed_by is not re-judged; changing it needs the owner and a new confirmed_on.",
                   "Every merchant seen for the first time goes on the report for the owner to confirm."]),
        ("merchants", sorted(seen.values(), key=lambda x: x["match"]))]))

    # The ledgers carry their classification: `type` is what the page shows, `label` overrides
    # the bank's description when it is not readable.
    for name, rows in (("chequing.csv", bmo), ("bmo_savings.csv", sav)):
        with W(name) as f:
            w = csv.writer(f); w.writerow(["date", "description", "amount", "balance", "statement", "type", "label"])
            for r in rows:
                w.writerow([iso(r["date"]), r["description"], f"{r['amount']:.2f}", f"{r['balance']:.2f}", r["statement"],
                            r["type"], r["tdesc"] if r["tdesc"] != r["description"] else ""])

    pos = gen_holdings()
    with W("holdings_latest.csv") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL); w.writerow(HOLD_HEADER)
        for p in pos:
            w.writerow([p["acct"], p["acct"], "Trade", p["aid"], p["sym"], "", "", NAME[p["sym"]], SEC.get(p["sym"], "ETF"),
                        f"{p['qty']}", "LONG", f"{p['price']}", p["cur"], f"{p['bv_cad']:.2f}", "CAD", f"{p['bv_mkt']:.2f}", p["cur"],
                        f"{p['mv_mkt']:.2f}", p["cur"], f"{p['mv_mkt'] - p['bv_mkt']:.2f}", p["cur"]])
    acts = gen_activities(rng, pos)
    with W("ws_activities.csv") as f:
        w = csv.writer(f); w.writerow(ACT_HEADER); w.writerows(acts)

    # balances
    by_acct = defaultdict(float)
    for p in pos: by_acct[p["acct"]] += p["mv_cad"]
    bmo_bal, sav_bal = bmo[-1]["balance"], sav[-1]["balance"]
    mc_bal = r2(mc_tot[MC_LAST])
    J("banks.json", OrderedDict([
        ("asof_note", "Balance and statement date per bank account. Replace the number and move the date on each import."),
        ("assets", [
            dict(inst="BMO", account="Primary Chequing", balance=bmo_bal, currency="CAD", asof="2026-09-05"),
            dict(inst="BMO", account="Savings Amplifier", balance=sav_bal, currency="CAD", asof="2026-09-05",
                 note="The emergency fund, $300 a month from chequing. Its statement arrives in the same batch as chequing, with a -2 suffix."),
        ]),
        ("debts", [dict(inst="BMO", account="MasterCard", balance=-mc_bal, currency="CAD", asof="2026-08-20", limit=5000)]),
        ("classification", "Bank cash is the day-to-day buffer."),
    ]))

    cash = r2(bmo_bal + sav_bal)
    invested = sum(v for k, v in by_acct.items() if k in PORT_ACCTS)
    R_inv, R_cash, R_debt = round(invested), round(cash), round(mc_bal)
    net_worth = R_inv + R_cash - R_debt
    dry = sum(p["mv_cad"] for p in pos if p["acct"] in PORT_ACCTS and p["sym"] in BONDS)
    dry_pct = round(dry / invested * 1000) / 10
    tickers = sorted({p["sym"] for p in pos if p["acct"] in PORT_ACCTS and p["sym"] != "CAD"})
    assert 15 <= dry_pct <= 25, dry_pct
    assert len(tickers) <= 10, tickers

    # accounts.json -- the register
    def acc(inst, id_, name, kind, cur, balance, asof, src, ledger, feeds, key, **extra):
        # `feeds` is written the old way (with the net-worth words) and split here: the words
        # become the five axes, and only the flow words stay in feeds — schema 4.
        d = OrderedDict(inst=inst, id=id_, name=name, kind=kind, cur=cur, balance=balance, asof=asof, src=src)
        d.update(default_axes(dict(kind=kind, src=src, feeds=feeds)))
        d.update(ledger=ledger, feeds=flow_feeds(feeds), key=key)
        d.update(extra); return d
    accounts = [
        acc("BMO", f"…{ID['bmo_chq']}", "Primary Chequing", "Chequing", "CAD", bmo_bal, "2026-09-05", "banks.json", "chequing.csv", "Income, Cash flow, Spending, Bank cash", "bmo-chq-4471",
            spendTag=f"BMO{ID['bmo_chq']}", stmtTag=f"BMOCHQ{ID['bmo_chq']}", stmtLabel="BMO chq"),
        acc("BMO", f"…{ID['bmo_sav']}", "Savings Amplifier", "Savings", "CAD", sav_bal, "2026-09-05", "banks.json", "bmo_savings.csv", "Cash flow, Bank cash", "bmo-sav-9032", stmtTag=f"BMOSAV{ID['bmo_sav']}"),
        acc("BMO", f"…{ID['bmo_mc']}", "MasterCard", "Credit card", "CAD", -mc_bal, "2026-08-20", "banks.json", None, "Spending, Debts", "bmo-mc-5518", spendTag=f"BMO{ID['bmo_mc']}", stmtLabel="MC"),
        acc("Wealthsimple", ID["tfsa"], "TFSA", "TFSA", "CAD", r2(by_acct["TFSA"]), "2026-09-06", "holdings_latest.csv", None, "Portfolio, Dry powder, Net worth", "ws-tfsa"),
        acc("Wealthsimple", ID["rrsp"], "RRSP", "RRSP", "CAD", r2(by_acct["RRSP"]), "2026-09-06", "holdings_latest.csv", None, "Portfolio, Dry powder, Net worth", "ws-rrsp"),
    ]
    def doc(key, ep, file, closes, feeds, covers, tags, into, reconcile, **extra):
        d = OrderedDict(key=key, ep=ep, file=file, closes=closes, feeds=feeds, covers=covers, tags=tags, into=into, reconcile=reconcile)
        d.update(extra); return d
    documents = [
        doc(f"Chequing {ID['bmo_chq']}", "BMO", "<Month D, YYYY>.pdf", "5th", "Pay, transfers, cash flow", ["bmo-chq-4471"], ["BMO_CHQ4471"], "chequing.csv", "opening + in - out = closing", parser="bmo_banking"),
        doc(f"Savings {ID['bmo_sav']}", "BMO", "<Month D, YYYY>-2.pdf", "5th", "Balance and savings ledger", ["bmo-sav-9032"], ["BMO_SAV9032"], "bmo_savings.csv", "balance chain closes", parser="bmo_banking", **{"from": "2026-01"}),
        doc(f"MasterCard {ID['bmo_mc']}", "BMO", "<Month D, YYYY>.pdf", "20th", "Spending, plan, baseline", ["bmo-mc-5518"], ["BMO_MC5518"], "spending.csv", "parsed total = Purchases and other charges + interest + Fees", parser="bmo_mastercard"),
        doc("Holdings", "Wealthsimple", "holdings-report-<date>.csv", "any time", "Portfolio, net worth", ["ws-tfsa", "ws-rrsp"], ["WS_HOLDINGS"], "holdings_latest.csv", "replaced wholesale", **{"from": "2026-06"}),
        doc("Activities", "Wealthsimple", "activities-export-<date>.csv", "any time", "Dividends, trades, deposits", ["ws-tfsa", "ws-rrsp"], ["WS"], "ws_activities.csv", "deposits, distributions and trades", **{"from": "2026-06"}),
    ]
    J("accounts.json", OrderedDict([
        ("asof_note", "The register of every place money sits (`accounts`) and every file dropped each month (`documents`). Balances here are COPIES of banks.json / holdings_latest.csv; check_data D14 re-derives them. Change the source file, not this one."),
        ("accounts", accounts),
        ("gaps", []),
        ("missing", []),
        ("documents", documents),
        ("archive_note", "Processed files are moved to archive/ as YYYYMMDD_<tag>_<original name>; the tag is documents[].tags."),
    ]))

    J("rules.json", OrderedDict([
        ("note", "Your investing rules, as data. ONE thing is computed: every bucket that carries a `target` is checked against that range, and the page reports the drift. Buckets are matched in order and the one marked catchAll takes whatever is left. `notes` are your own, shown with the status you gave them; `{mv:SYM}` in the text is filled from the holdings. `checkpoints` are dates you promised to look at something again."),
        ("buckets", [
            OrderedDict([("key", "bonds"), ("name", "Bonds"), ("symbols", sorted(BONDS)), ("target", [15, 25])]),
            OrderedDict([("key", "stocks"), ("name", "Stocks"), ("symbols", ["VEQT", "XAW"])]),
            OrderedDict([("key", "other"), ("name", "Anything else"), ("catchAll", True)]),
        ]),
        ("maxHoldings", 10),
        # what an ETF holds, which the export cannot say
        ("assetClass", OrderedDict([("VEQT", "stocks"), ("XAW", "stocks"), ("ZAG", "bonds")])),
        ("notes", [
            OrderedDict(status="ok", name="Three funds, nothing to pick", text="Every deposit buys VEQT in the TFSA. Once a year, in January, new money goes to whichever side is under its target until bonds are back near a fifth."),
        ]),
        ("checkpoints", [
            OrderedDict(title="Rebalance", date="2027-01-15", label="Mid-January", why="Bonds back to about a fifth of the portfolio"),
            OrderedDict(title="RRSP deadline", date="2027-03-01", label="Mar 1, 2027", why="Decide the RRSP contribution once the year's pay slips are in"),
        ]),
        ("benchmark", OrderedDict([("symbol", "VT"), ("name", "Vanguard Total World Stock ETF"),
                                   ("why", "The whole world's stocks in one fund: what the same money would have earned with no choices at all."),
                                   ("asof", "2026-10-27")])),
    ]))
    J("funds.json", OrderedDict([
        ("asof_note", "The guilt-free plan: pay-yourself-first, one everyday amount. The dashboard's FUNDS constant is a copy of this file (check_data D13). Fields that render on the page are English."),
        ("plan", OrderedDict(start="2026-08",
            # Schema 5: flows. Take-home is the whole paycheque; rent is a committed flow the
            # ledger shows on the 1st (D21 looks for it), and it stays after FIRE.
            flows=[
                OrderedDict(key="pay", kind="income", name="Take-home pay", amount=int(P["pay"] * 2),
                            note=f"Payroll of ${P['pay']:,.0f} twice a month. Investment income stays with the broker and is not counted."),
                OrderedDict(key="rent", kind="committed", name="Rent", amount=int(P["rent"]), afterFire="keep",
                            note="Pre-authorized on the 1st, from chequing. Still there after FIRE."),
                OrderedDict(key="invest", kind="saving", name="Invest", amount=P["invest"], to="broker",
                            note="Off the top, before anything else — pay-yourself-first."),
                OrderedDict(key="emergency", kind="saving", name="Emergency fund", amount=P["emergency"], to="bmo-sav-9032",
                            note="To savings on the 5th."),
                OrderedDict(key="everyday", kind="everyday", name="Everyday", amount=P["everyday"],
                            note="The guilt-free line. No categories and no caps below it."),
            ],
        )),
    ]))

    J("profile.json", OrderedDict([
        ("note", "Who this workspace belongs to. The FIRST thing to change when you make it yours: "
                 "the name appears in the browser tab and under the FIRE Toad wordmark in the sidebar, and it is read from here so it is never typed into the HTML. FIRE Toad itself is the product, not a setting."),
        ("schema", 18), ("demo", True), ("owner", P["name"]), ("born", 1994), ("importDay", 1)]))
    J("plan.json", OrderedDict([
        ("note", "Your planning assumptions. `planBase` is the monthly planning spend the FIRE target is built on (× 12 × 25); `skipMonths` are months excluded from every comparison, each with the reason the page shows. `retirement` holds the projection scenarios and the late-life care model; `descriptions` are your own one-liners under the net-worth parts (leave them out and the page describes each part from the register)."),
        ("planBase", int(P["rent"] + P["everyday"])),
        ("skipMonths", OrderedDict([("2025-12", "Only the tail of the first card statement — 11 days, not a month")])),
        # She said yes to FIRE at setup, and gave the estimates her My Service Canada account shows.
        ("fire", OrderedDict([("goal", True), ("asked", "2025-12-20")])),
        ("retirement", OrderedDict(list(RETIREMENT_DEFAULTS.items()) + [("pensions", [
            OrderedDict([("name", "CPP"), ("monthly", 760), ("from", 65), ("asof", "2025-12-20"), ("source", "My Service Canada estimate")]),
            OrderedDict([("name", "OAS"), ("monthly", 740), ("from", 65), ("asof", "2025-12-20"), ("source", "My Service Canada estimate")])])])),
    ]))
    J("foreign.json", OrderedDict([("asof", TODAY), ("currency", None), ("symbol", ""), ("label", "Foreign"),
                                   ("cadPerUnit", 0), ("total", 0),
                                   ("source", "No foreign-currency accounts in this build. The file exists because the tool reads it; an empty list is the supported way to say 'none'."),
                                   ("accounts", []), ("summary", dict(cash=0, invested=0, cash_share_pct=0))]))
    fxp = layout.path(out, "fx.json")
    if os.path.exists(fxp): os.remove(fxp)      # no US dollars held: absent means none
    hist = [dict(date="2026-06-15", cadInv=r2(invested - 2150), dry=r2(dry - 160), dryPct=round((dry - 160) / (invested - 2150) * 1000) / 10, tickers=3, foreign=None),
            dict(date="2026-08-05", cadInv=r2(invested - 820), dry=r2(dry - 60), dryPct=round((dry - 60) / (invested - 820) * 1000) / 10, tickers=3, foreign=None),
            dict(date="2026-09-06", cadInv=r2(invested), dry=r2(dry), dryPct=dry_pct, tickers=len(tickers), foreign=None)]
    J("investment_history.json", OrderedDict([("note", "One snapshot per 'update dashboards'. Portfolio = the accounts marked Portfolio in accounts.json; dry / dryPct is the share of the bucket with a target band."), ("snapshots", hist)]))
    J("networth_history.json", OrderedDict([("note", "One net-worth point per month, appended on every 'update dashboards' when the holdings export reaches a new month."),
                                            ("snapshots", [dict(ym="2026-06", v=net_worth - 3900), dict(ym="2026-08", v=net_worth - 1300), dict(ym="2026-09", v=net_worth)])]))

    # --------------------------------------------------- what an import writes
    J("filings.json", OrderedDict([
        ("note", "Which month each document was filed, keyed by accounts.json documents[].key. Written by the import step when a file is archived; checked against archive/ by T2."),
        ("filed", OrderedDict([
            (f"MasterCard {ID['bmo_mc']}", sorted({f"{t[:4]}-{t[4:6]}" for t in mc_tot})),
            (f"Chequing {ID['bmo_chq']}", sorted({r["statement"][-8:-4] + "-" + r["statement"][-4:-2] for r in bmo})),
            (f"Savings {ID['bmo_sav']}", sorted({r["statement"][-8:-4] + "-" + r["statement"][-4:-2] for r in sav})),
            ("Holdings", ["2026-06", "2026-07", "2026-08", "2026-09"]), ("Activities", ["2026-06", "2026-07", "2026-08", "2026-09"])]))]))
    # The record of the last update and the queue of what it left for the owner to confirm.
    # Every sentence reaches the page (Updates), so it is written about the money, not about the
    # tool: no "I", no rule numbers, no file names.
    aug = sum(r["amount"] for r in allspend if iso(r["date"]).startswith("2026-08"))
    J("imports.json", OrderedDict([
        ("note", NOTE_IMPORTS),
        ("imports", [OrderedDict([
            ("date", "2026-09-06"),
            ("files", ["MasterCard statement to Aug 20", "Chequing and savings statements to Sep 5",
                       "Holdings report of Sep 6", "Activities export of Sep 6"]),
            ("changed", [{"label": "Portfolio", "from": f"${invested - 820:,.0f}", "to": f"${invested:,.0f}"},
                         {"label": "Spending in August", "from": "$0", "to": f"${aug:,.0f}"}]),
            ("noticed", [
                dict(sev="ok", text=f"Bonds are {dry_pct}% of the portfolio, inside your 15–25% band."),
                dict(sev="ok", text=f"August kept the rule: two deposits of ${P['invest']/2:,.0f} reached the TFSA on Aug 2 and Aug 17."),
                dict(sev="ok", text="Every statement due has arrived. The next to close is the MasterCard on Sep 20."),
            ]),
            ("judged", ["Filed the Hydro Ottawa payment as a bill."]),
            ("asked", ["Whether FARM BOY OTTAWA stays in Grocery, and what the unnamed $200 e-Transfer of Aug 11 was."]),
        ])])]))
    J("decisions.json", OrderedDict([
        ("note", NOTE_DEC),
        ("decisions", [
            dict(added="2026-09-06", kind="merchant", what="FARM BOY OTTAWA has appeared many times and is filed as Grocery.",
                 default="Grocery", source="MasterCard, most recently Aug 14", status="open"),
            dict(added="2026-09-06", kind="transfer", what="A $200 e-Transfer received on Aug 11 carries no sender name.",
                 default="Other income", source="Chequing statement to Sep 5", status="open"),
            dict(added="2026-08-12", kind="merchant", what="STEAM PURCHASE SEATTLE, seen for the first time.",
                 default="Shopping", source="MasterCard, Aug 3", status="confirmed",
                 answer="Entertainment", resolved="2026-08-12"),
        ])]))
    J("tasks.json", OrderedDict([
        ("note", "Open tasks, shown on Data → Tasks. Added and closed out loud by the owner; `due` is optional and sorts to the top; `status: done` moves a task to the closed list."),
        ("tasks", [
            dict(added="2026-09-07", due="2027-03-01", tag="Money", text="RRSP contribution before the March 1 deadline — decide the amount once the year's pay slips are in.", status="open"),
            dict(added="2026-09-06", due="2027-01-15", tag="Money", text="Rebalance in January: new money to whichever side is under its target.", status="open")])]))

    open(os.path.join(out, "OWNER.md"), "w", encoding="utf-8").write(f"""# OWNER.md — {P['name']}'s workspace notes

> **This file is one person's** — and this person does not exist. {P['name']}, {P['age']}, works in an
> office in {P['city']} and is the demo owner whose data ships with the tool so that every page has
> something on it. `CLAUDE.md` loads this file with `@OWNER.md`; the `setup` skill replaces it
> with yours.

- Bank: BMO (chequing, savings, MasterCard). The chequing and savings statements arrive as
  `<Month D, YYYY>.pdf` and `<Month D, YYYY>-2.pdf` — the `-2` is the savings account.
- Broker: Wealthsimple, a TFSA and an RRSP. The two monthly deposits go straight into the TFSA.
- Reply in English.
""")
    # archive/: an empty placeholder per filed statement, named the way the import names them, so
    # the filing grid has the evidence T2 asks for. (The originals of a made-up person do not exist.)
    arc = os.path.join(out, "archive"); os.makedirs(arc, exist_ok=True)
    filed = json.load(open(layout.path(out, "filings.json"), encoding="utf-8"))["filed"]
    for d in documents:
        for m in filed.get(d["key"], []):
            stamp = m.replace("-", "") + "26"
            orig = d["file"].replace("<Month D, YYYY>", dt.date(int(m[:4]), int(m[5:]), 5).strftime("%B %-d, %Y")).replace("<date>", m + "-26")
            open(os.path.join(arc, f"{stamp}_{d['tags'][0]}_{orig}"), "w").close()
    return dict(P=P, net_worth=net_worth, invested=r2(invested), dry_pct=dry_pct, tickers=tickers, n_acts=len(acts))


# The late-life care model and the projection scenarios a new workspace starts with. These are
# published Canadian figures, not anybody's decision; the owner changes them in plan.json.
RETIREMENT_DEFAULTS = OrderedDict([
    ("scenarios", [dict(r=0.03, c="#9ec5f4", n="3% real"), dict(r=0.05, c="#2a78d6", n="5% real"), dict(r=0.07, c="#104281", n="7% real")]),
    ("horizon", 25), ("anchorYear", 2026), ("lifeTo", 95), ("coastR", 0.05),
    ("homeCare", dict(k="Light care at home", v=4200, esc=0.015,
                      d="Around 4 hours a day of a PSW at roughly $35/hr — meals, cleaning, some personal care. Bought by the hour, so it climbs with wages")),
    ("ltcTiers", [
        dict(k="Public · basic", v=2100, esc=0.003, d="Shared room in a public long-term-care home. Province-set co-payment for accommodation only — the care itself is publicly funded. A rate reduction exists if income is low. Long waitlist"),
        dict(k="Public · private", v=3000, esc=0.003, d="Private room in the same public system. Same capped pricing, longer wait"),
        dict(k="Private home", v=6500, esc=0.015, d="Private retirement residence with a care package. No waitlist and no subsidy, and priced like any other private service, so it climbs with wages")]),
])


# README shows these. They are of the demo owner, so they are generated here; S4 checks every
# image README shows resolves, so a missing shot fails the checks rather than leaving a broken image.
SHOTS = [("home.png", "main", "home"), ("spending.png", "main", "trends"), ("plan.png", "main", "budget"),
         ("sources.png", "main", "src"), ("portfolio.png", "main", "port")]


def screenshots(out):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  screenshots: SKIPPED (no playwright) — README will point at missing files"); return
    dst = os.path.join(out, "docs", "screens"); os.makedirs(dst, exist_ok=True)
    paths = {"main": os.path.join(out, "dashboards", "finance_dashboard.html")}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for fn, which, key in SHOTS:
            pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
            pg.goto("file://" + os.path.abspath(paths[which])); pg.wait_for_timeout(500)
            pg.eval_on_selector(f'[data-k="{key}"]', "el => el.click()"); pg.wait_for_timeout(400)
            pg.screenshot(path=os.path.join(dst, fn)); pg.close()
        b.close()
    print(f"  screenshots: {len(SHOTS)} written to docs/screens/")


if __name__ == "__main__":
    import sys, subprocess
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    c = build(out)
    print(f"demo owner {c['P']['name']}: net worth ${c['net_worth']:,} · portfolio ${c['invested']:,.0f} · bonds {c['dry_pct']}% · {len(c['tickers'])} holdings · {c['n_acts']} activity rows")
    rb = os.path.join(out, ".claude", "skills", "update-dashboard", "scripts", "rebuild.py")
    if os.path.exists(rb) and "--no-build" not in sys.argv:
        subprocess.run([sys.executable, rb, out, "--write"], check=True)
        screenshots(out)

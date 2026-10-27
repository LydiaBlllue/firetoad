#!/usr/bin/env python3
"""prices.py — the benchmark's prices, written into findata/ so the page never fetches anything.

The Performance page asks one question of the portfolio: had the same money gone into one fund
the owner names, on the days it actually went in, what would it be worth now? That needs two
daily series the broker's exports do not carry:

    the benchmark   rules.json `benchmark.symbol` (an exchange-traded fund), its adjusted close —
                    dividends folded in, so the comparison is total return against total return
    USD/CAD         the Bank of Canada's daily rate, when the benchmark trades in US dollars

Both are facts about the world, not about the owner, so they sit in the facts layer as one
snapshot, findata/ledgers/prices.json, replaced whole and dated by `asof`. The series start a week
before the first portfolio snapshot in investment_history.json, which is as far back as the
comparison can reach.

The Drawdown page asks a second question of history: in how many of the real stretches since
1928 would the plan have lasted? That needs one row a year, kept in findata/ledgers/returns.json:

    returns         Damodaran (NYU Stern), annual total returns by asset: US stocks, 3-month
                    T-bills, 10-year Treasuries, gold — the longest free table there is
    inflation       US BLS CPI-U, December to December, so the year matches the returns' year

Both are nominal as published; rebuild.py turns them into real returns. They change once a year.

Nothing about the owner leaves the machine: the requests carry a ticker and a date range.

    python3 prices.py <workspace>            what would be fetched
    python3 prices.py <workspace> --write    fetch and write
    ... --write --if-needed                  only when the prices stop short of the newest snapshot
                                             (what update.py runs after every import)

Exit 0 written or nothing to do (no benchmark named), 1 a fetch failed — nothing written.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import path  # noqa: E402

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={a}&period2={b}&interval=1d"
BOC = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?start_date={a}&end_date={b}"
DAMODARAN = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html"
BLS = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
CPI = "CUUR0000SA0"   # CPI-U, all items, not seasonally adjusted
# The table's columns, by heading, and the asset class each one stands for (rebuild.py ASSET_CLASSES)
COLUMNS = {"stocks": "S&P 500 (includes dividends)", "cash": "3-month T.Bill",
           "bonds": "US T. Bond (10-year)", "gold": "Gold*"}


def get(url, body=None, text=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (jade-toad prices.py)",
                                               "Content-Type": "application/json"},
                                 data=json.dumps(body).encode() if body else None)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode("latin-1" if text else "utf-8")
    return raw if text else json.loads(raw)


def epoch(day):
    return int(dt.datetime.combine(day, dt.time()).replace(tzinfo=dt.timezone.utc).timestamp())


def fetch(sym, start, end):
    """(currency, [[date, adjusted close]]) — the adjusted close, so dividends count."""
    j = get(YAHOO.format(sym=sym, a=epoch(start), b=epoch(end + dt.timedelta(days=1))))
    res = j["chart"]["result"][0]
    ts, adj = res["timestamp"], res["indicators"]["adjclose"][0]["adjclose"]
    tz = res["meta"].get("gmtoffset", 0)
    rows = [[dt.datetime.fromtimestamp(t + tz, dt.timezone.utc).date().isoformat(), round(v, 4)]
            for t, v in zip(ts, adj) if v is not None]
    return res["meta"].get("currency", "USD"), rows


def fetch_usdcad(start, end):
    j = get(BOC.format(a=start.isoformat(), b=end.isoformat()))
    return [[o["d"], float(o["FXUSDCAD"]["v"])] for o in j["observations"] if o.get("FXUSDCAD")]


def fetch_returns():
    """[[year, stocks, cash, bonds, gold, inflation]] — nominal, as fractions."""
    page = get(DAMODARAN, text=True)
    cell = lambda c: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(c))).strip()
    rows = [[cell(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S | re.I)]
            for r in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S | re.I)]
    head = next(r for r in rows if r and r[0] == "Year")
    at = {k: head.index(v) for k, v in COLUMNS.items()}       # the first match: the annual return
    pct = lambda v: round(float(v.rstrip("%")) / 100, 6)
    years = {int(r[0]): {k: pct(r[i]) for k, i in at.items()}
             for r in rows if r and r[0].isdigit() and all(r[i].endswith("%") for i in at.values())}
    first, last = min(years), max(years)
    dec = {}
    for a in range(first - 1, last + 1, 10):      # ten years a request is what BLS allows unregistered
        j = get(BLS, {"seriesid": [CPI], "startyear": str(a), "endyear": str(min(a + 9, last))})
        for o in j["Results"]["series"][0]["data"]:
            if o["period"] == "M12":
                dec[int(o["year"])] = float(o["value"])
    return [[y, years[y]["stocks"], years[y]["cash"], years[y]["bonds"], years[y]["gold"],
             round(dec[y] / dec[y - 1] - 1, 6)]
            for y in range(first, last + 1) if y in years and y in dec and y - 1 in dec]


def refresh_returns(root, write, if_needed, today):
    p = path(root, "returns.json")
    if if_needed and os.path.exists(p):
        have = json.load(open(p)).get("years") or []
        if have and have[-1][0] >= today.year - 1:
            print(f"  returns already reach {have[-1][0]}"); return 0
    if not write:
        print("  would fetch the yearly returns since 1928 and US inflation"); return 0
    try:
        years = fetch_returns()
    except Exception as e:
        print(f"  ✗ yearly returns not refreshed ({type(e).__name__}: {e}); the last ones stay"); return 1
    if len(years) < 50:
        print(f"  ✗ yearly returns not refreshed: only {len(years)} years came back; the last ones stay"); return 1
    out = {"asof": today.isoformat(),
           "source": {"returns": "Damodaran, NYU Stern — annual returns on stocks, bonds and bills",
                      "inflation": "US Bureau of Labor Statistics, CPI-U, December to December"},
           "columns": ["year", "stocks", "cash", "bonds", "gold", "inflation"],
           "years": years}
    with open(p, "w") as f:
        json.dump(out, f, separators=(",", ":"))
        f.write("\n")
    print(f"  ✓ yearly returns {years[0][0]}–{years[-1][0]}")
    return 0


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 and not argv[1].startswith("-") else ".")
    write = "--write" in argv
    today = dt.date.fromisoformat(os.environ.get("JADE_TODAY") or dt.date.today().isoformat())
    a = bench(root, argv, write)
    b = refresh_returns(root, write, "--if-needed" in argv, today)
    return a or b


def bench(root, argv, write):
    rules = json.load(open(path(root, "rules.json")))
    bench = rules.get("benchmark") or {}
    sym = bench.get("symbol")
    if not sym:
        print("  no benchmark named in rules.json — nothing to fetch"); return 0
    hist = json.load(open(path(root, "investment_history.json"))).get("snapshots", [])
    if not hist:
        print("  no portfolio snapshot yet — nothing to compare against"); return 0
    start = dt.date.fromisoformat(min(h["date"] for h in hist)) - dt.timedelta(days=7)
    end = dt.date.fromisoformat(os.environ.get("JADE_TODAY") or dt.date.today().isoformat())
    if "--if-needed" in argv and os.path.exists(path(root, "prices.json")):
        have = json.load(open(path(root, "prices.json")))
        ser = (have.get("benchmark") or {}).get("series") or []
        newest = max(h["date"] for h in hist)
        if have["benchmark"].get("symbol") == sym and ser and \
                (dt.date.fromisoformat(newest) - dt.date.fromisoformat(ser[-1][0])).days <= 3:
            print(f"  {sym} prices already reach {ser[-1][0]}"); return 0
    if not write:
        print(f"  would fetch {sym} and USD/CAD, {start} → {end}"); return 0
    try:
        ccy, series = fetch(sym, start, end)
        fx = fetch_usdcad(start, end) if ccy == "USD" else []
    except Exception as e:  # a network failure leaves the last prices in place
        print(f"  ✗ prices not refreshed ({type(e).__name__}: {e}); the last ones stay"); return 1
    if not series or (ccy == "USD" and not fx):
        print("  ✗ prices not refreshed: a series came back empty; the last ones stay"); return 1
    out = {"asof": end.isoformat(),
           "source": {"benchmark": "Yahoo Finance, adjusted close (dividends included)",
                      "usdcad": "Bank of Canada, daily average rate"},
           "benchmark": {"symbol": sym, "currency": ccy, "series": series},
           "usdcad": fx}
    p = path(root, "prices.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"  ✓ {sym}: {len(series)} days to {series[-1][0]}" + (f", USD/CAD {len(fx)} days" if fx else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

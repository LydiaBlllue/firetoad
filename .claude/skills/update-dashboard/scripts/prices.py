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

Nothing about the owner leaves the machine: the requests carry a ticker and a date range.

    python3 prices.py <workspace>            what would be fetched
    python3 prices.py <workspace> --write    fetch and write
    ... --write --if-needed                  only when the prices stop short of the newest snapshot
                                             (what update.py runs after every import)

Exit 0 written or nothing to do (no benchmark named), 1 a fetch failed — nothing written.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout import path  # noqa: E402

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1={a}&period2={b}&interval=1d"
BOC = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?start_date={a}&end_date={b}"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (jade-toad prices.py)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


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


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 and not argv[1].startswith("-") else ".")
    write = "--write" in argv
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

"""clock.py — the date every "how old is this" is measured from, read once, here.

A workspace's is today. The demo is a snapshot nobody imports into, so measured against the
calendar every balance in it reads as stale a few weeks after a clone (2026-10, 2026-11: the live
demo showed a warning beside every account). The demo is measured against its own newest fact
instead -- the latest bank as-of date or ledger row -- by the page and the checkers alike.
"""
import csv, datetime, json, os, re

import layout


def load(root, name):
    p = layout.path(root, name)
    return p if os.path.exists(p) else None


def clock(root):
    """The date the staleness rules (D9, D20) measure age from. A workspace's is today. The demo
    is a snapshot nobody imports into, so its rate and its stated values age with the calendar
    while nothing else in it moves: a clone a few weeks old greeted its first run with a stale
    rate (2026-10). The demo is measured against its own newest fact instead — the latest bank
    as-of date or ledger row — so it checks clean on any day and still ages within itself."""
    today = datetime.date.today()
    pp = load(root, "profile.json")
    if not pp or not json.load(open(pp, encoding="utf-8")).get("demo"):
        return today, None
    dates = []
    bp = load(root, "banks.json")
    if bp:
        bj = json.load(open(bp, encoding="utf-8"))
        dates += [x["asof"] for side in ("assets", "debts") for x in bj.get(side, []) if x.get("asof")]
    led = os.path.dirname(layout.path(root, "spending.csv"))
    for f in sorted(os.listdir(led)) if os.path.isdir(led) else []:
        if f.endswith(".csv"):
            dates += [r["date"] for r in csv.DictReader(open(os.path.join(led, f), encoding="utf-8")) if r.get("date")]
    dates = [d for d in dates if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d)]
    return (datetime.date.fromisoformat(max(dates)), "the demo's newest data") if dates else (today, None)

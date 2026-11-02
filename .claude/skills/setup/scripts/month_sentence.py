#!/usr/bin/env python3
"""month_sentence.py — the owner's last full month in one sentence, the way setup ends.

    python3 .claude/skills/setup/scripts/month_sentence.py .

A first reader learns the parts of a month from their own numbers, not from a definition
(FINANCE.md §3a). The parts are the page's: each row in exactly one, so they add up to the total.
"""
import calendar, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "update-dashboard", "scripts"))
import categories  # noqa: E402
import layout  # noqa: E402


def load(root, name, default):
    p = layout.path(root, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def main(argv):
    root = os.path.abspath(argv[1]) if len(argv) > 1 else os.getcwd()
    p = layout.path(root, "spending.csv")
    rows = list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []
    if not rows:
        print("No spending filed yet."); return 0
    # A month is full when a later month has rows, or its last day does.
    newest = max(r["date"] for r in rows)
    y, m = int(newest[:4]), int(newest[5:7])
    ym = newest[:7] if int(newest[8:]) == calendar.monthrange(y, m)[1] else max((r["date"][:7] for r in rows if r["date"][:7] < newest[:7]), default=newest[:7])
    group = categories.groups(load(root, "plan.json", {}))
    limit = float((load(root, "funds.json", {}).get("plan") or {}).get("bigThreshold") or float("inf"))
    repeats = categories.recurring(rows)
    parts = {"bills and housing": 0.0, "everyday": 0.0, "big buys": 0.0}
    for r in rows:
        if not r["date"].startswith(ym):
            continue
        a, g = float(r["amount"]), group.get(r["category"], "everyday")
        if g == "bills":
            parts["bills and housing"] += a
        elif a >= limit and categories.brand_of(r["note"]) not in repeats:
            parts["big buys"] += a
        else:
            parts["everyday"] += a
    said = ", ".join(f"{k} ${v:,.0f}" for k, v in parts.items() if abs(v) >= 0.5)
    print(f"In {calendar.month_name[int(ym[5:])]} you spent ${sum(parts.values()):,.0f}: {said}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

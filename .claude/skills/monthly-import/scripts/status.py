#!/usr/bin/env python3
"""status.py — everything the monthly import panel shows, derived from findata/ and inbox/.

    python3 status.py            # readable summary
    python3 status.py --json     # what the panel is drawn from

One row per thing the owner has to bring, grouped by what bringing it takes:

  statements   a bank's monthly PDFs           → the owner signs in, fetch-statements downloads
  exports      a broker's CSV exports          → the owner signs in (or exports them by hand)
  screenshots  accounts read off a phone app   → the owner takes the screenshots
  balances     accounts no file covers         → the owner reads a number off the app
  people       a counterparty's ledger         → only in a month something changed
  questions    decisions.json items still open → one tap each

Nothing is listed here by hand. A row exists because the register has a document or an account
for it; its state comes from filings.json, the accounts' `asof`, and what is waiting in inbox/.
It reads; it never writes.
"""
import argparse
import collections
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SKILLS, "update-dashboard", "scripts"))
sys.path.insert(0, os.path.join(SKILLS, "fetch-statements", "scripts"))
import layout  # noqa: E402
import preflight  # noqa: E402
import fetch  # noqa: E402

# A source is "due" when its newest data is older than one import cycle. The cycle is a month;
# a few days less, so a statement that closed just before the import day still counts as fresh.
CYCLE_DAYS = 25


def jload(root, name, default):
    try:
        return json.load(open(layout.path(root, name), encoding="utf-8"))
    except (OSError, ValueError):
        return default


def age(asof, today):
    try:
        return (today - dt.date.fromisoformat(asof[:10])).days
    except (TypeError, ValueError):
        return None


def ledger_types(root, reg):
    """Every `type` the ledgers already use: the choices for a transfer the import could not type."""
    seen = collections.Counter()
    for a in reg.get("accounts", []):
        if not a.get("ledger"):
            continue
        try:
            for row in csv.DictReader(open(layout.path(root, a["ledger"]), encoding="utf-8")):
                if row.get("type"):
                    seen[row["type"]] += 1
        except OSError:
            pass
    return [t for t, _ in seen.most_common()]


def categories(root):
    """The fifteen, in the page's order — the one definition, not whatever merchants.json has used."""
    import categories as cats  # noqa: E402  update-dashboard/scripts
    return list(cats.CATEGORIES)


def status(root, today):
    reg = jload(root, "accounts.json", {})
    accts = {a["key"]: a for a in reg.get("accounts", [])}
    docs = reg.get("documents", [])
    filed = jload(root, "filings.json", {}).get("filed", {})
    preflight.DOCS = preflight.load_docs(root)
    inbox_dir = os.path.join(root, "inbox")
    inbox = [n for n in sorted(os.listdir(inbox_dir)) if not n.startswith(".") and n != "README.txt"] \
        if os.path.isdir(inbox_dir) else []
    named = {n: preflight.classify(n)[0] for n in inbox}
    out = {"today": today.isoformat(), "importDay": jload(root, "profile.json", {}).get("importDay"),
           "inbox": len(inbox), "unnamed": [n for n, l in named.items() if not l],
           "statements": [], "exports": [], "screenshots": [], "balances": [], "people": [],
           "questions": []}

    # statements, per bank
    waiting = fetch.waiting(root)
    by_bank = collections.OrderedDict()
    for d, last, gap in fetch.missing(root, None, today):
        have = waiting.get(d["key"], [])
        by_bank.setdefault(d["ep"], []).append(
            {"key": d["key"], "last": last, "missing": gap, "inbox": have})
    for ep, rows in by_bank.items():
        todo = [r for r in rows if r["missing"] and len(r["inbox"]) < len(r["missing"])]
        out["statements"].append({"bank": ep, "docs": rows,
                                  "state": "todo" if todo else ("inbox" if any(r["inbox"] for r in rows) else "ok")})

    covered = set()
    for d in docs:
        covered |= set(d.get("covers") or [])
        when = (d.get("closes") or "").lower()
        if d.get("counterparty"):
            out["people"].append({"key": d["key"], "who": d["counterparty"], "from": d.get("ep"),
                                  "last": (sorted(filed.get(d["key"], [])) or [None])[-1],
                                  "state": "optional"})
            continue
        if d.get("into") == "foreign.json":
            for k in d.get("covers") or []:
                a = accts.get(k, {})
                ag = age(a.get("asof"), today)
                out["screenshots"].append({
                    "account": k, "inst": a.get("inst"), "name": a.get("name"),
                    "capture": a.get("capture") or f"{a.get('inst')} app, the page with the balance",
                    "asof": a.get("asof"), "age": ag,
                    "state": "todo" if ag is None or ag >= CYCLE_DAYS else "ok"})
            continue
        if when in ("any time", "when it changes") or not d.get("file", "").lower().endswith(".pdf"):
            asofs = [accts[k].get("asof") for k in d.get("covers") or [] if accts.get(k, {}).get("asof")]
            newest = max(asofs) if asofs else None
            ag = age(newest, today)
            have = [n for n, l in named.items() if l == f"{d['ep']} {d['key']}"]
            out["exports"].append({"from": d["ep"], "key": d["key"], "file": d.get("file"),
                                   "asof": newest, "age": ag, "inbox": have,
                                   "state": "inbox" if have else
                                   ("todo" if ag is None or ag >= CYCLE_DAYS else "ok")})

    # accounts no document covers: their balance is read off the app or the site
    for k, a in accts.items():
        if k in covered or a.get("value") == "stated" or a.get("src") != "banks.json":
            continue
        ag = age(a.get("asof"), today)
        out["balances"].append({"account": k, "inst": a.get("inst"), "name": a.get("name"),
                                "asof": a.get("asof"), "age": ag,
                                "state": "todo" if ag is None or ag >= CYCLE_DAYS else "ok"})

    # questions: open decisions, each with the choices a tap can give
    types, cats = None, None
    for i, q in enumerate(jload(root, "decisions.json", {}).get("decisions", [])):
        if q.get("status") != "open":
            continue
        kind = q.get("kind")
        if kind == "transfer" and q.get("credit"):
            # money in from no named sender: what it was, in confirm.py's words
            choices = ["Pay", "Family or gift", "Other income", "Own money", "Paid back"]
        elif kind == "transfer":
            types = types if types is not None else ledger_types(root, reg)
            choices = types
        elif kind in ("merchant", "category"):
            cats = cats if cats is not None else categories(root)
            choices = cats
        else:
            choices = []
        sug = {"Payroll": "Pay"}.get(q.get("suggest"), q.get("suggest"))
        out["questions"].append({"index": i, "kind": kind, "what": q.get("what"),
                                 "default": q.get("default"), "suggest": sug,
                                 "source": q.get("source"),
                                 "choices": [c for c in choices if c != q.get("default")]})
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    root = fetch.find_root(a.root)
    if not root:
        print("✗ no workspace here (looked upward for findata/ and dashboards/)")
        return 2
    s = status(root, dt.date.today())
    if a.json:
        print(json.dumps(s, ensure_ascii=False, indent=1))
        return 0
    mark = {"todo": "✗", "inbox": "→", "ok": "✓", "optional": "·"}
    print(f"=== monthly import — {s['today']} · {s['inbox']} file(s) in inbox/ ===")
    for b in s["statements"]:
        gaps = "; ".join(f"{r['key']} {', '.join(r['missing'])}" for r in b["docs"] if r["missing"])
        print(f"  {mark[b['state']]} statements  {b['bank']:<14} {gaps or 'up to date'}")
    for e in s["exports"]:
        print(f"  {mark[e['state']]} export      {e['from']:<14} {e['key']} (newest {e['asof']})")
    for c in s["screenshots"]:
        print(f"  {mark[c['state']]} screenshot  {c['inst']:<14} {c['capture']} (as of {c['asof']})")
    for b in s["balances"]:
        print(f"  {mark[b['state']]} balance     {b['inst']:<14} {b['name']} (as of {b['asof']})")
    for p in s["people"]:
        print(f"  · ledger      {p['who']:<14} only if something changed (last {p['last']})")
    for q in s["questions"]:
        print(f"  ? question    {q['what']}  [now: {q['default']}"
              + (f", suggested: {q['suggest']}]" if q.get("suggest") else "]"))
    for n in s["unnamed"]:
        print(f"  ✗ unnamed     {n} — preflight cannot name it; ask before anything else")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

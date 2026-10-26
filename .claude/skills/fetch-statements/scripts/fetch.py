#!/usr/bin/env python3
"""fetch.py — the two halves of "download my statements" that a program can do.

    python3 fetch.py missing [--bank RBC]          # which statements the register still lacks
    python3 fetch.py collect [--from ~/Downloads] [--minutes 30] [--write]
                                                   # move freshly downloaded statements to inbox/

`missing` reads the register (accounts.json documents[]) and the filing history (filings.json):
for every monthly document with a closing day, it says the last month filed and every month
since that should have closed by today. Nothing is listed by hand — a new document in the register
shows up here the day it is registered.

`collect` moves files out of a downloads folder into inbox/, but only those modified in the last
N minutes AND named by preflight's own classifier, so a stray invoice in ~/Downloads is never
swept up and nothing is guessed from a filename that preflight would have refused. It compares
without moving by default; --write moves (never over an existing file).

It never logs in, never touches findata/, and never opens a statement.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "update-dashboard", "scripts")
sys.path.insert(0, SCRIPTS)
import layout  # noqa: E402
import preflight  # noqa: E402


def find_root(start):
    # by looking for findata/ and dashboards/, never by counting parents (CLAUDE.md)
    p = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(p, "findata")) and os.path.isdir(os.path.join(p, "dashboards")):
            return p
        q = os.path.dirname(p)
        if q == p:
            return None
        p = q


def jload(root, name, default):
    try:
        return json.load(open(layout.path(root, name), encoding="utf-8"))
    except (OSError, ValueError):
        return default


def months_after(ym, through):
    y, m = map(int, ym.split("-"))
    out = []
    while True:
        m += 1
        if m > 12:
            y, m = y + 1, 1
        if (y, m) > through:
            return out
        out.append(f"{y:04d}-{m:02d}")


def waiting(root):
    """documents[].key -> files already in inbox/ under it (named by preflight, as collect is)."""
    preflight.DOCS = preflight.load_docs(root)
    inbox, out = os.path.join(root, "inbox"), {}
    for n in sorted(os.listdir(inbox)) if os.path.isdir(inbox) else []:
        label = preflight.classify(n)[0]
        for x in preflight.DOCS:
            if label == f"{x['doc']['ep']} {x['doc']['key']}":
                out.setdefault(x["doc"]["key"], []).append(n)
    return out


def missing(root, bank, today):
    reg = jload(root, "accounts.json", {})
    filed = jload(root, "filings.json", {}).get("filed", {})
    rows = []
    for d in reg.get("documents", []):
        if bank and (d.get("ep") or "").lower() != bank.lower():
            continue
        day = re.search(r"\d+", d.get("closes") or "")
        if not day or not (d.get("file") or "").lower().endswith(".pdf") or d.get("counterparty"):
            continue                          # exports "any time", screenshots, a person's ledger
        day = int(day.group(0))
        # a bank moves its closing day by a couple of days around weekends; until today is past
        # the day this month's statement may simply not be out yet
        through = (today.year, today.month) if today.day >= day else \
            ((today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12))
        have = sorted(filed.get(d["key"], []))
        start = have[-1] if have else (d.get("from") or None)
        if not start:
            rows.append((d, None, ["(nothing filed yet — ask how far back to go)"]))
            continue
        gap = months_after(start, through) if have else [start] + months_after(start, through)
        rows.append((d, have[-1] if have else None, gap))
    return rows


def collect(root, src, minutes, write):
    preflight.DOCS = preflight.load_docs(root)
    inbox = os.path.join(root, "inbox")
    cutoff = time.time() - minutes * 60
    moved, skipped = [], []
    for n in sorted(os.listdir(src)):
        p = os.path.join(src, n)
        if not os.path.isfile(p) or os.path.getmtime(p) < cutoff or n.startswith("."):
            continue
        if n.endswith((".crdownload", ".download", ".part")):
            skipped.append((n, "still downloading"))
            continue
        label = preflight.classify(n)[0]
        if not label:
            skipped.append((n, "not a registered document — left where it is"))
            continue
        dest = os.path.join(inbox, n)
        if os.path.exists(dest):
            skipped.append((n, "already in inbox/"))
            continue
        if write:
            shutil.move(p, dest)
        moved.append((n, label))
    return moved, skipped


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["missing", "collect"])
    ap.add_argument("--root", default=".")
    ap.add_argument("--bank", help="documents[].ep, e.g. RBC (default: every bank)")
    ap.add_argument("--from", dest="src", default=os.path.expanduser("~/Downloads"))
    ap.add_argument("--minutes", type=int, default=30)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    root = find_root(a.root)
    if not root:
        print("✗ no workspace here (looked upward for findata/ and dashboards/)")
        return 2

    if a.cmd == "missing":
        rows = missing(root, a.bank, dt.date.today())
        inbox = waiting(root)
        if not rows:
            print(f"no monthly statements registered{' at ' + a.bank if a.bank else ''}")
            return 1
        print(f"=== statements to fetch{' — ' + a.bank if a.bank else ''} ===")
        for d, last, gap in rows:
            want = ", ".join(gap) if gap else "nothing — up to date"
            print(f"  {d['ep']:<13} {d['key']:<28} closes {d.get('closes',''):<5} "
                  f"last filed {last or '—':<8} → {want}")
            for n in inbox.get(d["key"], []):
                print(f"      already in inbox/: {n}")
        return 0

    moved, skipped = collect(root, a.src, a.minutes, a.write)
    verb = "moved" if a.write else "would move"
    print(f"=== collect from {a.src} (last {a.minutes} min) — {len(moved)} {verb} to inbox/ ===")
    for n, label in moved:
        print(f"  ✓ {n}  →  {label}")
    for n, why in skipped:
        print(f"  · {n}: {why}")
    if moved and not a.write:
        print("  (compare only — add --write to move)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

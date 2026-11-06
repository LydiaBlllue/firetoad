#!/usr/bin/env python3
"""ocr.py — the numbers on a phone screenshot, read on this computer, offered never written.

An account read off an app (the register's `capture` says which app and page) has its balance
read by eye today. This reads the image with Apple's Vision framework through `ocrmac` — on
device, nothing leaves the machine — and does what the skill tells the model to do by eye: take
every currency amount on the image, prefer the large ones and the ones that sit near a word the
`capture` line carries (余额, 市值, balance…), and offer the top few with any date the image
shows. The owner taps one; balance.py writes it. This file writes nothing.

    python3 .claude/skills/update-dashboard/scripts/ocr.py <image> [--capture "某银行 App · 账户页 — 余额"]

Without `ocrmac` (pip3 install --user ocrmac; macOS only) read() says so and the panel falls back
to a typed amount. The scoring (`amounts`, `candidates`) is pure and unit-tested; the Vision
call is the one line that is not.
"""
import argparse
import datetime
import json
import re
import sys

AMOUNT = re.compile(r"(?<![\d.,])(?:US\$|CA\$|C\$|\$|¥|￥|€|£)?\s*(\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|\d+\.\d{2})(?![\d])")
DATE = re.compile(r"(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})日?")
MONTH_DAY = re.compile(r"(?<!\d)(\d{1,2})[-/月](\d{1,2})日?(?!\d)")
# words that usually label the balance itself, in the languages the register has used
BALANCE_WORDS = ("余额", "可用余额", "总资产", "总金额", "市值", "资产", "balance", "available", "total", "value")
NOISE_WORDS = ("收益", "昨日", "利率", "%", "手续费", "fee", "rate", "yield", "limit", "额度")


def amounts(text):
    """Every amount in a line of text, as floats, in order. '余额 ¥203,134.64' → [203134.64]."""
    out = []
    for m in AMOUNT.finditer(text or ""):
        try:
            out.append(float(m.group(1).replace(",", "")))
        except ValueError:
            pass
    return out


def dates(text, today):
    """Dates a screenshot shows: full ones as they are, month-day ones in this or the last year."""
    out = []
    for m in DATE.finditer(text or ""):
        try:
            out.append(datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat())
        except ValueError:
            pass
    for m in MONTH_DAY.finditer(text or ""):
        try:
            d = datetime.date(today.year, int(m.group(1)), int(m.group(2)))
        except ValueError:
            continue
        if d > today:
            d = d.replace(year=today.year - 1)
        out.append(d.isoformat())
    return out


def _words(capture):
    """The words of a capture line worth matching: CJK runs and latin words of three letters or more."""
    toks = set(re.findall(r"[一-鿿]{2,}|[A-Za-z]{3,}", capture or ""))
    toks |= set(BALANCE_WORDS)
    return {t.lower() for t in toks}


def candidates(boxes, capture=None, today=None, top=5):
    """Rank the amounts on an image. `boxes` are [{text, x, y, w, h}] with y measured from the
    top and sizes as fractions of the image (what read() returns). The score prefers a taller
    box (the headline number), an amount on a line that also carries a balance word, an amount
    whose nearest text above or to the left is one, and penalises lines about yields and rates.
    Returns [{amount, text, near, score}] best first, and the dates seen."""
    today = today or datetime.date.today()
    words = _words(capture)
    labels = []   # (box, word) for boxes that carry a label word
    for b in boxes:
        low = (b.get("text") or "").lower()
        hit = next((w for w in words if w in low), None)
        if hit:
            labels.append((b, hit))
    out, seen_dates = [], []
    for b in boxes:
        text = b.get("text") or ""
        seen_dates += dates(text, today)
        for amt in amounts(text):
            if amt == 0 or amt > 1e9:
                continue
            low = text.lower()
            score = (b.get("h") or 0) * 100          # the headline number is the tallest
            if any(w in low for w in words):
                score += 3
            if any(w in low for w in NOISE_WORDS):
                score -= 4
            near = None
            best = 1e9
            for lb, w in labels:
                if lb is b:
                    continue
                dy = (b.get("y") or 0) - (lb.get("y") or 0)
                dx = (b.get("x") or 0) - (lb.get("x") or 0)
                # a label sits just above (dy small and positive) or to the left on the same line
                if (0 <= dy <= 0.08 and abs(dx) < 0.3) or (abs(dy) < 0.02 and 0 <= dx < 0.6):
                    d = abs(dy) * 3 + abs(dx)
                    if d < best:
                        best, near = d, lb.get("text")
            if near:
                score += 2
            if "." in text:
                score += 0.5
            out.append({"amount": amt, "text": text.strip(), "near": near, "score": round(score, 2)})
    out.sort(key=lambda c: -c["score"])
    uniq, got = [], set()
    for c in out:
        if c["amount"] in got:
            continue
        got.add(c["amount"]); uniq.append(c)
        if len(uniq) >= top:
            break
    ds = []
    for d in seen_dates:
        if d not in ds:
            ds.append(d)
    return uniq, ds


def boxes(path, languages=("zh-Hans", "en-US")):
    """The text boxes Vision sees: [{text, conf, x, y, w, h}], y from the top, all as fractions.
    Raises ImportError when ocrmac is not installed."""
    from ocrmac import ocrmac as _o   # pip3 install --user ocrmac (macOS)
    res = _o.OCR(path, language_preference=list(languages), recognition_level="accurate").recognize()
    out = []
    for text, conf, (x, y, w, h) in res:
        out.append({"text": text, "conf": round(float(conf), 3), "x": round(float(x), 4),
                    "y": round(1 - float(y) - float(h), 4), "w": round(float(w), 4), "h": round(float(h), 4)})
    out.sort(key=lambda b: (b["y"], b["x"]))
    return out


def read(path, capture=None, today=None):
    """{candidates, dates, boxes, error}: what the panel offers. Never writes."""
    try:
        bx = boxes(path)
    except ImportError:
        return {"candidates": [], "dates": [], "boxes": 0,
                "error": "ocrmac is not installed (pip3 install --user ocrmac); type the amount instead"}
    except Exception as e:  # noqa: BLE001  an unreadable image is said, not raised
        return {"candidates": [], "dates": [], "boxes": 0, "error": f"could not read the image ({type(e).__name__}: {e})"}
    cands, ds = candidates(bx, capture, today)
    return {"candidates": cands, "dates": ds, "boxes": len(bx), "error": None}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--capture", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    r = read(a.image, a.capture)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1)); return 0 if not r["error"] else 1
    if r["error"]:
        print("  ✗ " + r["error"]); return 1
    print(f"=== {a.image}: {r['boxes']} text boxes ===")
    for c in r["candidates"]:
        print(f"  {c['amount']:>14,.2f}  {c['text'][:40]!r}" + (f"  near {c['near'][:24]!r}" if c["near"] else ""))
    if r["dates"]:
        print("  dates seen: " + ", ".join(r["dates"][:5]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Open the dashboards in a real browser and check what only a browser can see.

check_design.py reads the file as text, so it can prove a chart has no fixed height in the
CSS. It cannot prove the chart then actually grows on a 32" screen, that every page still
draws instead of throwing, or that nothing scrolls sideways at 800px. Those four things were
checked by hand every time -- about 28 tool calls a run, and the findings were re-derived from
scratch each month because nothing wrote down how the navigation works.

Usage:  python3 check_render.py dashboards/a.html [dashboards/b.html ...] [-v]
Exit:   0 clean or notes only, 1 if any ERROR, 2 if the browser is missing

Needs Playwright + Chromium (installed 2026-09-08):
    pip3 install --user playwright && python3 -m playwright install chromium
"""
import os, sys

WIDTHS = [800, 1120, 1440, 1760]
SHORT  = [700, 800]           # R6: a 13-inch laptop's browser window is about this tall   # DESIGN.md §4: min-width 800 (collapsed below 1120), max-width 1760
TALL   = 900                  # viewport height

CATS = [("build",   "is the artefact current with findata/"),
        ("conform", "does it still follow DESIGN.md")]
CAT_ORDER = [c[0] for c in CATS]
CAT_LABEL = {c[0]: c[1] for c in CATS}

# Collected inside the page. Kept here rather than rediscovered every month: the sidebar is a
# list of [data-k] elements that are CLICKED -- the location hash is a compound state string
# (#p=home&ym=...&alw=...), so assigning to it does not navigate and neither does firing
# hashchange. Some [data-k] elements are spending-category chips, not pages; a data-k with no
# matching section[data-pg] is one of those and is skipped, not reported as a broken link.
PROBE = r"""
async () => {
  const errs = [];
  window.addEventListener('error', e => errs.push(String(e.message)));
  const navs = [...document.querySelectorAll('[data-k]')]
      .filter(el => document.querySelector('section[data-pg="' + el.dataset.k + '"]'));
  const pages = [];
  for (const el of navs) {
    el.click();
    await new Promise(r => setTimeout(r, 90));
    const s = document.querySelector('section[data-pg="' + el.dataset.k + '"]');
    const r = s.getBoundingClientRect();
    pages.push({
      k: el.dataset.k,
      shown: getComputedStyle(s).display !== 'none',
      h: Math.round(r.height),
      text: s.innerText.trim().length,
      // Text that only a broken template produces. 2026-09-08 a renamed field left
      // "undefined transfer" on the Insights page and all three text checkers passed.
      // ⚠ PROBE must stay a RAW string: written as a normal one, the \b below became a Python
      // backspace (\x08) and this regex could never match anything, so R5 reported "clean" from
      // the day it was written until 2026-09-09. A check that cannot fail is not a check.
      junk: (s.innerText.match(/\b(undefined|NaN|null|\[object Object\])\b/g) || []).slice(0, 3),
      // The PAINTED width, not the element's box. With a fixed height plus
      // preserveAspectRatio the <svg> element still stretches full width while the drawing
      // inside it is scaled to the height and centred -- so a bounding rect shows no problem
      // and the chart is capped anyway. getScreenCTM().a is the viewBox-unit -> CSS-pixel
      // scale actually in force, so viewBox width x that is what the reader sees.
      // A chart the page has put away (a card hidden until its numbers exist) is not drawn:
      // getScreenCTM still answers for it, with the unscaled viewBox width (2026-10-29).
      charts: [...s.querySelectorAll('svg, canvas')].filter(c => c.getClientRects().length).map(c => {
        if (c.tagName.toLowerCase() === 'svg' && c.viewBox && c.viewBox.baseVal &&
            c.viewBox.baseVal.width && c.getScreenCTM()) {
          return Math.round(c.viewBox.baseVal.width * c.getScreenCTM().a);
        }
        return Math.round(c.getBoundingClientRect().width);
      }).filter(w => w > 200),
      // A chart drawn narrower than its own box: a height pinned below the viewBox's scales the
      // drawing down and leaves white space beside it (2026-10-30, charts drawn at their size).
      unfilled: [...s.querySelectorAll('svg')].filter(c => c.getClientRects().length && c.viewBox &&
        c.viewBox.baseVal && c.viewBox.baseVal.width && c.getScreenCTM() &&
        c.getBoundingClientRect().width > 200).filter(c =>
        c.viewBox.baseVal.width * c.getScreenCTM().a < c.getBoundingClientRect().width - 2).length,
      hscroll: document.documentElement.scrollWidth - document.documentElement.clientWidth
    });
  }
  const sections = [...document.querySelectorAll('section[data-pg]')].map(s => s.dataset.pg);
  return { pages, sections, errs };
}
"""


def probe(path):
    """Load the page once per width and return {width: result}. Import is inside the function
    so the missing-browser message is a sentence, not a traceback from the top of the file."""
    from playwright.sync_api import sync_playwright
    out, console = {}, []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w in WIDTHS:
            pg = b.new_page(viewport={"width": w, "height": TALL})
            pg.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: console.append(str(e)))
            pg.goto("file://" + os.path.abspath(path))
            pg.wait_for_timeout(400)
            out[w] = pg.evaluate(PROBE)
            pg.close()
        b.close()
    return out, console


# R6: with the page at its top in a short window, every sidebar entry can be scrolled to and is inside the
# window. The sidebar is sticky, so when it was taller than the window its foot could not be
# reached at all (2026-11-05, Statements and Glossary on a 13-inch screen).
REACH = r"""
() => {
  // The page stays at its top: reaching an entry by scrolling the whole page to its foot is not
  // reaching it. Only the sidebar's own scroll may move.
  const out = [];
  document.querySelectorAll('#sideNav button, #sideNav summary').forEach(b => {
    if (!b.getClientRects().length) return;
    const fold = b.closest('details');                 // inside a closed fold: not shown, not asked
    if (fold && !fold.open && b.tagName !== 'SUMMARY') return;
    b.scrollIntoView({block: 'nearest'});
    window.scrollTo(0, 0);
    const r = b.getBoundingClientRect();
    if (r.top < -1 || r.bottom > innerHeight + 1) out.push(b.innerText.split('\\n')[0].trim());
  });
  return out;
}
"""

# R7: the page is one page for every kind of owner (1.0.1): what it shows depends on two signals,
# something invested and a FIRE goal, and on whether chequing has arrived. A workspace shows only
# its own state, so the others are made from it by emptying what the signal reads.
STATE = r"""
async () => {
  const errs = [];
  window.addEventListener('error', e => errs.push(String(e.message)));
  const main = [...document.querySelectorAll('#sideNav > .grp button')].map(b => b.dataset.k);
  const fold = [...document.querySelectorAll('#sideNav details.wait button')].map(b => b.dataset.k);
  const bad = [];
  for (const k of main.concat(fold)) {
    setPage(k);
    await new Promise(r => setTimeout(r, 40));
    const s = document.querySelector('section[data-pg="' + k + '"]');
    const junk = (s.innerText.match(/\b(undefined|NaN|\[object Object\])\b/g) || []);
    if (junk.length) bad.push(k + ' shows "' + junk[0] + '"');
  }
  setPage('home');
  const cards = [...document.querySelectorAll('#homeStats .card')].map(c => (c.querySelector('.big') || {}).innerText || '');
  return {main, fold, cards, bad, errs};
}
"""


def states(src):
    """Each kind of owner this page can be made to show, as (name, html, what must wait)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                    "update-dashboard", "scripts"))
    import json as _j
    from rebuild import span

    def get(s, name):
        a, b = span(s, name)
        return _j.loads(s[a:b])

    def put(s, name, val):
        a, b = span(s, name)
        return s[:a] + _j.dumps(val) + s[b:]

    inv = get(src, "INVEST")
    invested = bool(inv.get("portfolio") or inv.get("investable"))
    def without_investing(s):
        i = dict(get(s, "INVEST"), portfolio=0, investable=0)
        return put(s, "INVEST", i)
    def card_only(s):
        s = without_investing(s)
        s = put(s, "INVEST", dict(get(s, "INVEST"), cashflow=[]))
        return put(put(s, "CHEQUING", []), "WSINC", [])
    out = []
    if invested:
        out.append(("invested, a goal", put(src, "FIRE_GOAL", True), set()))
        out.append(("invested, no goal", put(src, "FIRE_GOAL", False), {"fire", "coast"}))
    base = without_investing(src)
    out.append(("a goal, nothing invested", put(base, "FIRE_GOAL", True), {"port", "perf", "hold", "coast"}))
    out.append(("no goal, nothing invested", put(base, "FIRE_GOAL", False), {"port", "perf", "hold", "fire", "coast"}))
    out.append(("cards only", put(card_only(src), "FIRE_GOAL", None), {"port", "perf", "hold", "fire", "coast", "income", "safe", "wsinc"}))
    return out


def probe_more(path):
    """R6 and R7, in their own browser: the sidebar in short windows, then each kind of owner."""
    import tempfile
    from playwright.sync_api import sync_playwright
    src = open(path, encoding="utf-8").read()
    reach, made = {}, []
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        b = pw.chromium.launch()
        for h in SHORT:
            pg = b.new_page(viewport={"width": 1120, "height": h})
            pg.goto("file://" + os.path.abspath(path)); pg.wait_for_timeout(300)
            reach[h] = pg.evaluate(REACH)
            pg.close()
        for name, html, waits in states(src):
            f = os.path.join(tmp, "state.html")
            open(f, "w", encoding="utf-8").write(html)
            pg = b.new_page(viewport={"width": 1440, "height": 900})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto("file://" + f); pg.wait_for_timeout(300)
            r = pg.evaluate(STATE)
            r["errs"] += errs
            made.append((name, waits, r))
            pg.close()
        b.close()
    return reach, made


def check(path):
    F = []
    def err(r, m, c="build"):  F.append(("ERROR", r, m, c))
    def warn(r, m, c="conform"): F.append(("WARN", r, m, c))
    def note(r, m, c="conform"): F.append(("NOTE", r, m, c))

    res, console = probe(path)

    # -- R1 every nav entry draws its section, and nothing throws on the way ----
    for w, r in res.items():
        for p in r["pages"]:
            if not p["shown"]:
                err("R1", f"{w}px: clicking '{p['k']}' leaves its section hidden")
            elif p["h"] < 40:
                err("R1", f"{w}px: page '{p['k']}' renders {p['h']}px tall — it is throwing "
                          f"or its data is empty")
        for e in r["errs"]:
            err("R1", f"{w}px: uncaught error — {e[:120]}")
    # -- R5 a page must never show the words a broken template leaves behind ---
    seen = set()
    for r in res.values():
        for p in r["pages"]:
            for j in p["junk"]:
                if (p["k"], j) not in seen:
                    seen.add((p["k"], j))
                    err("R5", f"page '{p['k']}' shows the word \"{j}\" — a field or variable is missing")
    if not seen:
        note("R5", "no undefined / NaN / null in any rendered page", "build")
    for c in console:
        err("R1", f"console error — {c[:120]}")

    base = res[WIDTHS[0]]
    reached = {p["k"] for p in base["pages"]}
    for pg in base["sections"]:
        if pg not in reached:
            err("R1", f"section '{pg}' exists but no sidebar entry reaches it")
    note("R1", f"{len(reached)} pages reached and drawn, no uncaught errors")

    # -- R2 desktop-only means no sideways scrolling anywhere in the range ------
    for w, r in res.items():
        over = {p["k"]: p["hscroll"] for p in r["pages"] if p["hscroll"] > 0}
        for k, px in over.items():
            err("R2", f"{w}px: page '{k}' scrolls {px}px sideways", "conform")
    if not any(p["hscroll"] > 0 for r in res.values() for p in r["pages"]):
        note("R2", f"no horizontal scroll at {' / '.join(map(str, WIDTHS))}px")

    # -- R3 charts must actually get bigger on a bigger screen -----------------
    # DESIGN.md §4: a fixed pixel height plus preserveAspectRatio means the chart is scaled to
    # its height and centred, so a wider window only adds white space. Found on the owner's 32"
    # screen 2026-09-06; the CSS check alone cannot see it because the cap can come from an
    # inline style, a parent, or the viewBox.
    narrow = {p["k"]: p["charts"] for p in res[WIDTHS[0]]["pages"]}
    wide   = {p["k"]: p["charts"] for p in res[WIDTHS[-1]]["pages"]}
    grew = capped = 0
    for k, ws in wide.items():
        ns = narrow.get(k, [])
        for i, w_px in enumerate(ws):
            if i >= len(ns):
                continue
            if w_px <= ns[i] + 2:
                capped += 1
                err("R3", f"page '{k}': a chart draws {ns[i]}px at {WIDTHS[0]} and {w_px}px at "
                          f"{WIDTHS[-1]} — it is height-capped, so the extra width is white space",
                    "conform")
            else:
                grew += 1
    for w, r in res.items():
        for p in r["pages"]:
            if p.get("unfilled"):
                capped += 1
                err("R3", f"{w}px: page '{p['k']}' draws {p['unfilled']} chart(s) narrower than "
                          f"their box — a pinned height shrinks the drawing", "conform")
    if grew and not capped:
        note("R3", f"{grew} charts grow with the window "
                   f"({WIDTHS[0]} → {WIDTHS[-1]}px)")

    reach, made = probe_more(path)
    # -- R6 every sidebar entry can be reached in a short window -----------------
    for h, missed in reach.items():
        for k in missed:
            err("R6", f"1120×{h}: the sidebar entry '{k}' cannot be scrolled into the window", "conform")
    if not any(reach.values()):
        note("R6", f"every sidebar entry reachable at {' and '.join(map(str, SHORT))}px tall")
    # -- R7 every kind of owner gets a page that draws, cards with numbers, and the right pages ---
    for name, waits, r in made:
        for e in r["errs"]:
            err("R7", f"{name}: uncaught error — {e[:110]}")
        for b_ in r["bad"]:
            err("R7", f"{name}: {b_}")
        shown = [k for k in r["main"] if k in waits]
        if shown:
            err("R7", f"{name}: {', '.join(shown)} shown in the sidebar, but this owner has nothing for them yet", "conform")
        if not 1 <= len(r["cards"]) <= 4:
            err("R7", f"{name}: Home shows {len(r['cards'])} cards, not one to four", "conform")
        empty = [c for c in r["cards"] if c.strip() in ("", "\u2014", "—")]
        if empty:
            err("R7", f"{name}: Home shows {len(empty)} card(s) with no number", "conform")
    if made:
        note("R7", f"drawn for {len(made)} kinds of owner: " + "; ".join(n for n, _, _ in made))

    # R4 (a page should fill a screen) was retired 2026-10-29: Home is short on purpose, so the
    # rule warned on every run, and a warning nobody acts on teaches everyone to skip the output.
    return F


def render(title, F, verbose=False):
    print(f"\n=== {title} ===")
    bad = 0
    if not F:
        print("  ✓ nothing to check here")
        return 0
    for cat in CAT_ORDER:
        rows = [f for f in F if f[3] == cat]
        if not rows:
            continue
        errs  = [r for r in rows if r[0] == "ERROR"]
        warns = [r for r in rows if r[0] == "WARN"]
        bad += len(errs)
        mark = "✗" if errs else ("⚠" if warns else "✓")
        tally = (f"{len(errs)} problem" + ("s" if len(errs) != 1 else "")) if errs \
                else (f"{len(warns)} to look at" if warns else f"{len(rows)} checks")
        print(f"  {cat:<10} {mark} {tally}")
        for sev, rule, msg, _ in errs + warns:
            print(f"     {'✗' if sev == 'ERROR' else '⚠'} [{rule}] {msg}")
        if verbose:
            for _, rule, msg, _c in [r for r in rows if r[0] == "NOTE"]:
                print(f"     · [{rule}] {msg}")
    return bad


def main(argv):
    v = "-v" in argv or "--verbose" in argv
    argv = [a for a in argv if not a.startswith("-")]
    if not argv:
        print(__doc__); return 2
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("check_render needs Playwright, which is not installed:\n"
              "  pip3 install --user playwright && python3 -m playwright install chromium")
        return 2
    worst = 0
    for path in argv:
        if not os.path.exists(path):
            print(f"missing: {path}"); worst = 2; continue
        if render(f"render — {os.path.basename(path)}", check(path), v):
            worst = max(worst, 1)
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

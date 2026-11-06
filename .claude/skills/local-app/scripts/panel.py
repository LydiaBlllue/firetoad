"""panel.py — the monthly panel as a page: the monthly-import skill's card with the chat removed.

Server-rendered from what the scripts return (status.run() for the rows, confirm.run() for the
open questions, the newest imports.json record for the result), in the dashboard's own tokens so
it reads as the same product. It invents no row and no question: a row exists because the
register has a document or an account for it; a question because decisions.json holds it, with
the choices the scripts already attach (PRODUCT.md §6.11). The markup lives in
templates/panel/panel.html; this file fills its four slots.

Four cards, the skill's order:

  Bring       one row per thing the owner has to bring, a state pill, what is missing — never a
              filename. Rows that are `ok` collapse into one line.
  Import      *Import what's here* is the dry run; it shows the plan, then *Go*. Lines stream in.
              *Undo the last import* after.
  Questions   one row per open item, numbered as confirm.py numbers them, its suggestion (or the
              default) selected, the choices as pills. One *Save answers*; an unanswered row keeps
              its default — the same rule as today.
  Result      net worth before and after, the other changed lines, what was noticed, and *Open
              the dashboard*.

No number here is typed by hand, and nothing here is financial logic.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "update-dashboard", "scripts"))
import categories  # noqa: E402
import confirm  # noqa: E402  INCOMING: what money in from no named sender can be


def template(root):
    """The workspace's copy of the markup, the way rebuild.py reads templates/dashboards/ from
    the workspace; the tool's own beside these scripts when a workspace has none yet."""
    for base in (root, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))):
        p = os.path.join(base, "templates", "panel", "panel.html")
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    raise FileNotFoundError("templates/panel/panel.html")

STATE_WORD = {"todo": "to bring", "inbox": "in inbox", "ok": "up to date", "optional": "only if it changed"}


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def months(ms):
    """'Sep, Oct' from whatever the status gives (month names or YYYY-MM)."""
    out = []
    for m in ms or []:
        m = str(m)
        if len(m) == 7 and m[4] == "-":
            out.append(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")[int(m[5:]) - 1])
        else:
            out.append(m)
    return ", ".join(out)


def pill(state):
    return f'<span class="st {e(state)}">{e(STATE_WORD.get(state, state))}</span>'


def row(icon, who, what, state, extra=""):
    return (f'<div class="row"><span class="ic">{icon}</span><div class="rw"><b>{e(who)}</b>'
            f'<span class="wh">{e(what)}</span>{extra}</div>{pill(state)}</div>')


def balance_form(key, capture, today, with_shot):
    """The typed-balance form (balance.py behind it) and, for an account read off a screenshot,
    the button that reads one (ocr.py behind it): candidates come back as pills, a tap fills the
    amount, Save writes. The form invents nothing: the key is the register's, the capture line
    is the register's, the amounts are the image's."""
    shot = ('<label class="btn sm shot">Read a screenshot<input type="file" accept="image/*" hidden></label>'
            if with_shot else "")
    return (f'<form class="bf" data-key="{e(key)}" data-capture="{e(capture or "")}">'
            f'<input class="amt" inputmode="decimal" placeholder="the amount the app shows" aria-label="amount">'
            f'<input class="asof" type="date" value="{e(today)}" aria-label="as of">'
            f'<button type="button" class="btn sm primary sv">Save</button>{shot}</form><div class="cands"></div>')


# ---------------------------------------------------------------- Bring
def bring(st, root):
    rows, done = [], []
    today = st.get("today") or ""
    stated = {x["account"]: x for x in st.get("stated") or []}
    shown = set()
    for n in st.get("unnamed") or []:
        rows.append(f'<div class="row bad"><span class="ic">✗</span><div class="rw"><b>{e(n)}</b>'
                    f'<span class="wh">nobody can name this file — the import stops until it is named</span></div></div>')
    for b in st.get("statements") or []:
        # one bank, several documents: each named by its register key, its months after it
        gaps = [(f"{r['key']}: " if len(b["docs"]) > 1 else "")
                + f"{len(r['missing'])} statement{'s' if len(r['missing']) != 1 else ''} ({months(r['missing'])})"
                for r in b["docs"] if r.get("missing")]
        if b["state"] == "ok":
            done.append(b["bank"]); continue
        rows.append(row("▤", b["bank"], " · ".join(gaps) or "waiting in inbox", b["state"]))
    for x in st.get("exports") or []:
        if x["state"] == "ok":
            done.append(x["from"]); continue
        rows.append(row("⇩", x["from"], f"{x['key']} export (newest {x.get('asof') or 'never'})", x["state"]))
    for s in st.get("screenshots") or []:
        if s["state"] == "ok":
            done.append(s.get("inst") or s.get("name")); continue
        shown.add(s.get("account"))
        rows.append(row("▣", s.get("inst") or s.get("name"), s.get("capture") or "the page with the balance", s["state"],
                        balance_form(s.get("account"), s.get("capture"), today, True) if s.get("account") in stated else ""))
    for b in st.get("balances") or []:
        if b["state"] == "ok":
            done.append(b.get("inst") or b.get("name")); continue
        shown.add(b.get("account"))
        rows.append(row("#", b.get("inst") or "", f"{b.get('name')} — the balance, read off the app (as of {b.get('asof') or 'never'})", b["state"],
                        balance_form(b.get("account"), b.get("capture"), today, bool(b.get("capture"))) if b.get("account") in stated else ""))
    for p in st.get("people") or []:
        rows.append(row("☺", p.get("who"), f"only if something changed (last {p.get('last') or 'never'})", "optional"))
    seen, uniq = set(), []
    for d in done:
        if d and d not in seen:
            seen.add(d); uniq.append(d)
    if uniq:
        rows.append(f'<div class="row ok-line"><span class="ic">✓</span><div class="rw"><span class="wh">'
                    f'{e(", ".join(uniq))} up to date</span></div></div>')
    # every other balance that is typed, not read from a file, folded away: it is there for the
    # month something changes, not every month
    rest = [x for k, x in stated.items() if k not in shown]
    if rest:
        inner = "".join(row("#", x.get("inst") or "", f"{x.get('name')} (as of {x.get('asof') or 'never'})",
                            "ok" if x.get("age") is not None and x["age"] < 25 else "optional",
                            balance_form(x["account"], x.get("capture"), today, bool(x.get("capture")))) for x in rest)
        rows.append(f'<details class="more"><summary>Other balances you type ({len(rest)})</summary>{inner}</details>')
    inbox = os.path.join(root, "inbox")
    n = st.get("inbox") or 0
    drop = ('<div class="drop" id="drop"><b>Drop statements and exports here</b>'
            '<span>or <label class="lnk">choose files<input type="file" multiple hidden id="pick"></label> · '
            '<button type="button" class="lnk" id="openinbox">open the inbox folder</button></span>'
            f'<small>{e(inbox)} — {n} file{"s" if n != 1 else ""} waiting</small><div class="dropped" id="dropped"></div></div>')
    return "".join(rows) + drop


# ---------------------------------------------------------------- Questions
def choices_for(item):
    """The pills an item can be answered with — confirm.py's own words, nothing invented."""
    kind = item.get("kind")
    if kind == "fire":
        return ["Yes", "No"]
    if item.get("credit"):
        return list(confirm.INCOMING.values())
    if kind == "merchant" or (kind == "transfer" and item.get("spent")):
        return list(categories.CATEGORIES)
    return []


def questions(q):
    items = (q or {}).get("items") or []
    if not items:
        return '<p class="foot">Nothing is waiting to be confirmed.</p>'
    out = []
    for it in items:
        ch = choices_for(it)
        sel = it.get("suggest") or it.get("default")
        if it.get("credit"):
            sel = confirm.INCOMING.get(sel, sel)
        pills = "".join(f'<button type="button" class="pl{" sel" if c == sel else ""}" data-n="{it["n"]}" data-v="{e(c)}">{e(c)}</button>'
                        for c in ch)
        why = it.get("why") or ""
        seen = f' · seen {it["seen"]}×' if it.get("seen") else ""
        out.append(f'<div class="q" data-n="{it["n"]}"><div class="qt"><b>{it["n"]}.</b> {e(it.get("what"))}</div>'
                   f'<div class="qs">filed as <b>{e(it.get("default"))}</b>'
                   + (f' · suggested <b>{e(confirm.INCOMING.get(it["suggest"], it["suggest"]) if it.get("credit") else it["suggest"])}</b>' if it.get("suggest") else "")
                   + f'{e(seen)}{" · " + e(why) if why else ""}</div>'
                   + (f'<div class="pills">{pills}</div>' if pills else '<div class="qs">answered in its ledger, not here</div>')
                   + '</div>')
    out.append('<div class="act"><button type="button" class="btn primary" id="save">Save answers</button>'
               '<span class="hint">a row left alone keeps what it is filed as</span></div>')
    return "".join(out)


# ---------------------------------------------------------------- Result
def result(rec):
    if not rec:
        return '<p class="foot">No import yet.</p>'
    out = [f'<div class="qs">last import {e(rec.get("date"))}</div>']
    for c in rec.get("changed") or []:
        out.append(f'<div class="kv"><span class="k">{e(c.get("label"))}</span><span class="v">{e(c.get("from"))} → {e(c.get("to"))}</span></div>')
    for n in rec.get("noticed") or []:
        sev = n.get("sev") or "ok"
        out.append(f'<div class="nt {e(sev)}"><span class="ic">{"✓" if sev == "ok" else "!"}</span>{e(n.get("text"))}</div>')
    return "".join(out)


# ---------------------------------------------------------------- the page
def tool_notice(tool):
    """One line about the folder's copy of the tool, only when it is not the app's own."""
    if not tool or tool.get("state") == "same":
        return ""
    st = tool.get("state")
    sc = tool.get("schema") or {}
    if st == "newer":
        return (f'<p class="busy bad">This folder\'s data is a newer shape (schema {e(sc.get("workspace"))}) than this app builds '
                f'(schema {e(sc.get("app"))}). Nothing is written until the app is updated.</p>')
    if st == "migrate":
        return (f'<p class="busy">This folder\'s data is an older shape (schema {e(sc.get("workspace"))}) than this app builds '
                f'(schema {e(sc.get("app"))}): it has to be migrated first (tools/migrate.py), then refreshed.</p>')
    n = len(tool.get("changed") or [])
    return (f'<p class="busy">This folder\'s copy of the tool differs from the app\'s in {n} place{"s" if n != 1 else ""} — '
            f'both doors should run one version. <button type="button" class="btn sm" id="syncbtn">Refresh the copy</button></p>')


def render(base, root, st, q, rec, job, held, tool=None):
    tpl = template(root)
    nq = len((q or {}).get("items") or [])
    busy = tool_notice(tool)
    if job and not job.get("done"):
        busy += f'<p class="busy">{e(job["verb"])} is running — the lines below follow it.</p>'
    elif held:
        busy += f'<p class="busy">{e(held.get("verb"))} is running elsewhere (since {e(held.get("since"))}); wait for it.</p>'
    todo = sum(1 for k in ("statements", "exports", "screenshots", "balances") for r in st.get(k) or [] if r.get("state") == "todo")
    todo += len(st.get("unnamed") or [])
    first = "Nothing to bring. " if not todo else f"{todo} thing{'s' if todo != 1 else ''} to bring. "
    first += f"{nq} question{'s' if nq != 1 else ''} waiting." if nq else "No questions waiting."
    fill = {"{{BASE}}": e(base), "{{TODAY}}": e(st.get("today")), "{{LEAD}}": e(first),
            "{{BRING}}": bring(st, root), "{{QUESTIONS}}": questions(q), "{{RESULT}}": result(rec),
            "{{BUSY}}": busy, "{{NQ}}": str(nq),
            "{{VERSION}}": e((tool or {}).get("version") or "")}
    for k, v in fill.items():
        tpl = tpl.replace(k, v)
    return tpl


def no_dashboard(base):
    return (f'<!doctype html><meta charset="utf-8"><title>Jade Toad</title>'
            f'<p style="font-family:system-ui;padding:40px">No dashboard is built yet. '
            f'<a href="{e(base)}/panel">Open the panel</a> and import a month.</p>')

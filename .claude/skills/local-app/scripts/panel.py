"""panel.py — the monthly panel as a page: one step at a time, in the owner's language.

Server-rendered from what the scripts return (status.run() for the rows, confirm.run() for the
open questions, the newest imports.json record for the result), in the dashboard's own tokens so
it reads as the same product. It invents no row and no question: a row exists because the
register has a document or an account for it; a question because decisions.json holds it, with
the choices the scripts already attach (PRODUCT.md §6.11). Every sentence comes from
strings.py, in English or Chinese; the markup is templates/panel/panel.html.

The first version (2026-11-06) was four cards named after the skill's internals — Bring,
Import, Questions, Result — and the owner could not tell what to do first (2026-11-07). The
second showed the month's five steps, all at once in two columns, each with a paragraph. Since
2026-11-12 it is one step at a time (user 001, DESIGN.md 6a), four views under the setup's bar:

  1  Get this month's files    a table — the account, what is still needed — then one "How do I
                               download from <bank>?" a bank, the drop zone, what is in the
                               folder as a table, and the balances typed by hand under a fold
  2  Import N files            the look runs by itself; what will be added as rows; one button
  3  Categorize …              one item at a time: the likeliest three answers and More, Skip,
                               Back; Finish closes what is left
  4  Done                      what changed as rows, what was noticed, open the dashboard, undo

The ids step1 … step5 stay in the markup: they are the five states `current_step` knows.
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SKILLS, "update-dashboard", "scripts"))
sys.path.insert(0, os.path.join(SKILLS, "update-dashboard"))
import ai  # noqa: E402  which model is set, for the settings card
import categories  # noqa: E402
import confirm  # noqa: E402  INCOMING: what money in from no named sender can be
import preflight  # noqa: E402  names the files in inbox/
from strings import t, months, js_strings, wizard_strings  # noqa: E402
try:
    from parsers import support  # noqa: E402  each bank's own download path, in both languages
except Exception:  # noqa: BLE001  a workspace without the parsers package still gets a panel
    support = None

LI = {"en": 0, "zh": 1}

# small inline glyphs for the kinds of thing a month brings (no icon font, no request)
ICON = {
    "statement": '<svg viewBox="0 0 20 20"><path d="M5 2h7l4 4v12H5z" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M12 2v4h4M7.5 10h6M7.5 13h6" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>',
    "export": '<svg viewBox="0 0 20 20"><rect x="3" y="4" width="14" height="12" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M3 8h14M8 8v8M13 8v8" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>',
    "shot": '<svg viewBox="0 0 20 20"><rect x="6" y="2" width="8" height="16" rx="1.6" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M9 15h2" stroke="currentColor" stroke-width="1.4"/></svg>',
    "typed": '<svg viewBox="0 0 20 20"><rect x="2.5" y="6" width="15" height="9" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M5.5 9h1M8.5 9h1M11.5 9h1M14.5 9h1M6 12h8" stroke="currentColor" stroke-width="1.4"/></svg>',
    "person": '<svg viewBox="0 0 20 20"><circle cx="10" cy="7" r="3" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M4 17c1-3.5 3-5 6-5s5 1.5 6 5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>',
}


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def pill(lang, state):
    return f'<span class="st {e(state)}">{e(t(lang, "st_" + state))}</span>'


def row(icon, who, what, state, lang, extra="", kind=None):
    k = f'<span class="kind">{e(t(lang, "kind_" + kind))}</span>' if kind else ""
    return (f'<div class="row {e(state)}"><span class="ic">{ICON.get(icon, "")}</span><div class="rw"><b>{e(who)}</b>{k}'
            f'<span class="wh">{what}</span>{extra}</div>{pill(lang, state)}</div>')


def how(lang, text, bank=""):
    return f'<details class="how"><summary>{e(t(lang, "how", bank=bank))}</summary><p>{text}</p></details>'


def _support_how(lang, inst, fmt):
    if support is None:
        return None
    for r in getattr(support, "SUPPORT", []):
        if r.get("bank") == inst and r.get("format") == fmt and r.get("how"):
            h = r["how"]
            return h[LI.get(lang, 0)] if isinstance(h, (list, tuple)) else h
    return None


def bank_how(lang, bank, parser):
    """The bank's own download path from parsers/support.py, in the owner's language; a generic
    sentence when the table has no row for it."""
    fmt = "ofx" if parser == "ofx" else ("csv" if parser == "csv" else "pdf")
    h = _support_how(lang, bank, fmt)
    if h:
        return e(bank) + " — " + e(h) + ("。" if lang == "zh" else ". ") + e(t(lang, "how_tail"))
    return e(t(lang, "how_bank_generic", bank=bank))


def export_how(lang, inst, key):
    h = _support_how(lang, inst, (key or "").lower())
    if h:
        return e(h) + ("。" if lang == "zh" else ". ") + e(t(lang, "how_tail"))
    return e(t(lang, "how_bank_generic", bank=inst))


def balance_form(lang, key, capture, today, with_shot):
    """The typed-balance form (balance.py behind it) and, for an account read off a screenshot,
    the button that reads one (ocr.py behind it)."""
    shot = (f'<label class="btn sm shot">{e(t(lang, "read_shot"))}<input type="file" accept="image/*" hidden></label>'
            if with_shot else "")
    return (f'<form class="bf" data-key="{e(key)}" data-capture="{e(capture or "")}">'
            f'<input class="amt" inputmode="decimal" placeholder="{e(t(lang, "amount_ph"))}" aria-label="amount">'
            f'<input class="asof" type="date" value="{e(today)}" aria-label="as of">'
            f'<button type="button" class="btn sm primary sv">{e(t(lang, "save"))}</button>{shot}</form><div class="cands"></div>')


# ---------------------------------------------------------------- view 1: get the files
def need_table(lang, st):
    """What is still needed, one account a row: the account left, what is missing right. Then
    one "How do I download from <bank>?" a bank, and the balances typed by hand under a fold.
    A table, not sentences (DESIGN.md 6a): "Primary Chequing 471: 2 missing (Oct, Nov)" was a
    line of prose a row per account (2026-11-12, user 001). Returns (html, how many are needed)."""
    today = st.get("today") or ""
    stated = {x["account"]: x for x in st.get("stated") or []}
    rows, hows, done, forms, shown, need = [], {}, [], [], set(), 0

    def line(name, what, cls=""):
        rows.append(f'<tr class="{cls}"><td>{e(name)}</td><td>{what}</td></tr>')

    for b in st.get("statements") or []:
        if b["state"] == "ok":
            done.append(b["bank"]); continue
        parser = None
        for r in b["docs"]:
            if r.get("missing") and len(r.get("inbox") or []) < len(r["missing"]):
                line(r["key"], e(months(lang, r["missing"])), "todo"); need += 1
                parser = parser or r.get("parser")
            elif r.get("inbox"):
                line(r["key"], e(t(lang, "in_folder")), "ok")
            else:
                line(r["key"], e(t(lang, "up_to_date")), "ok")
        if b["state"] == "todo":
            hows.setdefault(b["bank"], []).append(bank_how(lang, b["bank"], parser))
    for x in st.get("exports") or []:
        if x["state"] == "ok":
            done.append(x["from"]); continue
        line(f'{x["from"]} {x["key"]}', e(t(lang, "need_newer")), "todo"); need += 1
        if x["state"] == "todo":
            hows.setdefault(x["from"], []).append(e(x["key"]) + ": " + export_how(lang, x["from"], x["key"]))
    for kind in ("screenshots", "balances"):
        for s in st.get(kind) or []:
            name = " ".join(x for x in (s.get("inst"), s.get("name")) if x)
            if s["state"] == "ok":
                done.append(s.get("inst") or s.get("name")); continue
            shown.add(s.get("account"))
            line(name, e(t(lang, "need_balance")), "todo"); need += 1
            if s.get("account") in stated:
                forms.append(f'<div class="bal"><b>{e(name)}</b>'
                             + balance_form(lang, s.get("account"), s.get("capture"), today, bool(s.get("capture"))) + '</div>')
    uniq = []
    for d in done:
        if d and d not in uniq:
            uniq.append(d)
    for d in uniq:
        line(d, e(t(lang, "up_to_date")), "ok")
    for x in stated.values():
        if x["account"] not in shown:
            name = " ".join(y for y in (x.get("inst"), x.get("name")) if y)
            forms.append(f'<div class="bal"><b>{e(name)}</b>'
                         f'<small>{e(t(lang, "asof", date=x.get("asof") or t(lang, "never")))}</small>'
                         + balance_form(lang, x["account"], x.get("capture"), today, bool(x.get("capture"))) + '</div>')
    out = ""
    if rows:
        out += (f'<table class="tbl"><tr><th>{e(t(lang, "col_account"))}</th><th>{e(t(lang, "col_need"))}</th></tr>'
                + "".join(rows) + '</table>')
    # one "how do I download" a bank, its files one a line
    out += "".join(how(lang, "<br>".join(dict.fromkeys(v)), k) for k, v in hows.items())
    more = ""
    if forms:
        more = (f'<details class="more"{" open" if any(s.get("state") != "ok" and s.get("account") in stated for k in ("screenshots", "balances") for s in st.get(k) or []) else ""}>'
                f'<summary>{e(t(lang, "other_balances", n=len(forms)))}</summary>{"".join(forms)}</details>')
    return out, need, more


def drop_zone(lang, st, root):
    """Where the files go, and what is already in the folder as a table: the file left, what it
    was read as right. No folder path on screen: nobody types it, and *Open the folder* shows it."""
    inbox = os.path.join(root, "inbox")
    names = sorted(n for n in (os.listdir(inbox) if os.path.isdir(inbox) else []) if not n.startswith(".") and n != "README.txt")
    items = []
    if names:
        try:
            preflight.ROOT = root
            preflight.DOCS = preflight.load_docs(root)
        except Exception:  # noqa: BLE001
            pass
        for n in names:
            try:
                label, _a, _into, note = preflight.classify(n)
            except Exception:  # noqa: BLE001
                label, note = None, ""
            if label:
                items.append(f'<tr class="ok"><td>{e(n)}</td><td>{e(label)}</td></tr>')
            else:
                items.append(f'<tr class="bad"><td>{e(n)}</td><td>{e(t(lang, "not_read"))}<small>{e(t(lang, "unnamed_fix"))}</small></td></tr>')
    out = (f'<div class="drop" id="drop"><b>{e(t(lang, "drop"))}</b>'
           f'<label class="lnk">{e(t(lang, "or_choose"))}<input type="file" multiple hidden id="pick"></label>'
           f'<small>{e(t(lang, "none_waiting"))}</small><div class="dropped" id="dropped"></div></div>')
    if items:
        out += (f'<table class="tbl"><tr><th>{e(t(lang, "col_file"))}</th><th>{e(t(lang, "col_is"))}</th></tr>'
                + "".join(items) + '</table>')
    out += f'<p class="foot"><button type="button" class="lnk" id="openinbox">{e(t(lang, "open_inbox"))}</button></p>'
    return out, len(names)


# ---------------------------------------------------------------- step 4
def choices_for(item):
    kind = item.get("kind")
    if kind == "fire":
        return ["Yes", "No"]
    if item.get("credit"):
        return list(confirm.INCOMING.values())
    if kind == "merchant" or (kind == "transfer" and item.get("spent")):
        return list(categories.CATEGORIES)
    return []


def money_s(v):
    try:
        return "$" + format(float(v), ",.2f")
    except (TypeError, ValueError):
        return str(v)


def say(lang, it):
    """The question in the owner's language, from the facts the import recorded; the stored
    English sentence when there are none (items from before the facts, or kinds without them)."""
    f = it.get("facts") or {}
    k = f.get("kind")
    if k == "credit":
        d = f.get("date") or ""
        if f.get("sender"):
            return t(lang, "qs_credit_named", amount=money_s(f.get("amount")), date=d, who=str(f["sender"]).title())
        return t(lang, "qs_credit", amount=money_s(f.get("amount")), date=d)
    if k == "sent":
        return t(lang, "qs_sent", amount=money_s(f.get("amount")), date=f.get("date") or "")
    if k == "account":
        key = "qs_account_to" if f.get("way") == "to" else "qs_account_from"
        return t(lang, key, amount=money_s(f.get("amount")), date=f.get("date") or "", desc=f.get("desc") or "")
    if k == "merchant":
        if f.get("starter"):
            return t(lang, "qs_merchant_starter", merchant=f.get("merchant"), cat=categories.label(f["starter"], lang))
        return t(lang, "qs_merchant", merchant=f.get("merchant"))
    if k == "fire" or it.get("kind") == "fire":
        return t(lang, "qs_fire")
    return it.get("what") or ""


def option_label(lang, c):
    """What a choice is called on screen: a category's name, or the money words, in the language."""
    if c in categories.CATEGORIES:
        return categories.label(c, lang)
    return t(lang, "opt_" + c) if ("opt_" + c) in __import__("strings").S else c


def qdata(q, lang="en"):
    """What step 4 draws: every open item with its choices, and the spending totals the Other
    share is computed from. The page groups them — money first, then the merchants with a
    suggestion, then the unknown ones as cards by amount."""
    items = []
    for it in (q or {}).get("items") or []:
        d = dict(it)
        d["choices"] = choices_for(it)
        if it.get("credit") and d.get("suggest"):
            d["suggest"] = confirm.INCOMING.get(d["suggest"], d["suggest"])
        d["text"] = say(lang, it)
        d["labels"] = {c: option_label(lang, c) for c in d["choices"]}
        d["labels"].update({x: option_label(lang, x) for x in (d.get("default"), d.get("suggest")) if x})
        items.append(d)
    return {"items": items, "spendTotal": (q or {}).get("spendTotal") or 0, "otherTotal": (q or {}).get("otherTotal") or 0,
            "catLabels": {c: categories.label(c, lang) for c in categories.CATEGORIES}}


def step4(lang, q):
    items = (q or {}).get("items") or []
    if not items:
        return f'<p class="foot">{e(t(lang, "q_none"))}</p>'
    # one item at a time, drawn by the page from {{QDATA}}; this is the frame it fills
    return (f'<p class="q-of" id="qof"></p><div id="qdeck"></div>'
            f'<div class="act" id="qend" style="display:none">'
            f'<button type="button" class="btn primary" id="save">{e(t(lang, "save_answers"))}</button>'
            f'<span class="hint">{e(t(lang, "unanswered_keep"))}</span></div>')


def merchants_list(lang, root):
    """The merchants already filed, biggest first, each with a change link (confirm.refile)."""
    try:
        rows = confirm.merchants(root)
    except Exception:  # noqa: BLE001
        rows = []
    if not rows:
        return f'<details class="more" id="mlist"><summary>{e(t(lang, "filed_before"))}</summary><p class="foot">{e(t(lang, "m_none"))}</p></details>'
    cats = list(categories.CATEGORIES)
    out = [f'<details class="more" id="mlist"><summary>{e(t(lang, "filed_before"))}</summary>']
    for i, m in enumerate(rows):
        hide = ' style="display:none"' if i >= 20 else ""
        opts = "".join(f'<option value="{e(c)}"{" selected" if c == m["category"] else ""}>{e(categories.label(c, lang))}</option>' for c in cats)
        out.append(f'<div class="sug mrow" data-match="{e(m["match"])}"{hide}><span class="m">{e(m["match"])}</span>'
                   f'<span class="a">${format(m["amount"], ",.0f")}</span>'
                   f'<select class="mcat">{opts}</select><span class="hint mmsg"></span></div>')
    if len(rows) > 20:
        out.append(f'<button type="button" class="lnk hint" id="mmore">{e(t(lang, "m_more", n=len(rows)))}</button>')
    out.append('</details>')
    return "".join(out)


# ---------------------------------------------------------------- step 5
def step5(lang, rec, base):
    if not rec:
        return f'<p class="foot">{e(t(lang, "no_import"))}</p>'
    out = [f'<p class="foot">{e(t(lang, "last_import", date=rec.get("date")))}</p><table class="tbl">']
    for c in rec.get("changed") or []:
        out.append(f'<tr><td>{e(c.get("label"))}</td><td>{e(c.get("from"))} → {e(c.get("to"))}</td></tr>')
    out.append('</table>')
    for n in rec.get("noticed") or []:
        sev = n.get("sev") or "ok"
        out.append(f'<div class="nt {e(sev)}"><span class="ic">{"✓" if sev == "ok" else "!"}</span>{e(n.get("text"))}</div>')
    out.append(f'<div class="act"><a class="btn primary" href="{e(base)}/" target="_blank" rel="noopener">{e(t(lang, "open_dash"))}</a>'
               f'<button type="button" class="lnk hint" id="undo">{e(t(lang, "undo"))}</button></div>')
    return "".join(out)


# ---------------------------------------------------------------- the model, by choice
def ai_card(lang, root):
    st = ai.status(root)
    opts = "".join(f'<option value="{e(k)}"{" selected" if k == st["provider"] else ""}>{e(v["label"])}</option>' for k, v in st["providers"].items())
    notes = json.dumps({k: {"note": v["note"], "baseUrl": v["baseUrl"], "model": v["model"], "key": v["key"]} for k, v in st["providers"].items()})
    on = st["provider"] != "none"
    msg = (e(t(lang, "ai_on")) + ": " + e(st["provider"]) + ", " + e(st["model"] or "")) if st["enabled"] else (e(t(lang, "ai_nokey")) if on else e(t(lang, "ai_off")))
    return (f'<div class="ai" data-notes="{e(notes)}">'
            f'<div class="qs">{e(t(lang, "ai_intro"))}</div>'
            f'<div class="act"><select id="aiprov"><option value="none"{"" if on else " selected"}>{e(t(lang, "ai_off"))}</option>{opts}</select>'
            f'<span class="hint" id="ainote"></span></div>'
            f'<div class="aif" id="aif" style="display:{"flex" if on else "none"}">'
            f'<input id="aiurl" placeholder="base URL" value="{e(st["baseUrl"] or "")}">'
            f'<input id="aimodel" placeholder="model" value="{e(st["model"] or "")}">'
            f'<input id="aikey" type="password" placeholder="{e(t(lang, "ai_key_kept") if st["keyStored"] and on else t(lang, "ai_key_ph"))}" autocomplete="off">'
            f'</div>'
            f'<div class="act"><button type="button" class="btn sm primary" id="aisave">{e(t(lang, "save"))}</button>'
            f'<button type="button" class="btn sm" id="aitest"{"" if st["enabled"] else " disabled"}>{e(t(lang, "ai_try"))}</button>'
            f'<span class="hint" id="aimsg">{msg}</span></div></div>')


# ---------------------------------------------------------------- the page
def tool_notice(lang, tool):
    if not tool or tool.get("state") == "same":
        return ""
    st = tool.get("state"); sc = tool.get("schema") or {}
    if st == "newer":
        return f'<p class="busy bad">{e(t(lang, "tool_newer", ws=sc.get("workspace"), app=sc.get("app")))}</p>'
    if st == "migrate":
        return f'<p class="busy">{e(t(lang, "tool_migrate", ws=sc.get("workspace"), app=sc.get("app")))}</p>'
    n = len(tool.get("changed") or [])
    return (f'<p class="busy">{e(t(lang, "tool_differs", n=n))} '
            f'<button type="button" class="btn sm" id="syncbtn">{e(t(lang, "refresh_copy"))}</button></p>')


def current_step(st, q):
    """Which of the five the owner is at: the first thing left to do, in order."""
    todo = sum(1 for k in ("statements", "exports", "screenshots", "balances") for r in st.get(k) or [] if r.get("state") == "todo")
    unnamed = len(st.get("unnamed") or [])
    nq = len((q or {}).get("items") or [])
    inbox = st.get("inbox") or 0
    if unnamed:
        return 2, "lead_unnamed", {"n": unnamed}
    if todo:
        return 1, "lead_todo", {"n": todo}
    if inbox:
        return 3, "lead_inbox", {}
    if nq:
        return 4, "lead_questions", {"n": nq}
    return 5, "lead_done", {}


VIEW_OF = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4}     # the five states the owner can be in → the four views


def bars(view):
    """The setup's own progress bar: four segments, done, here, to come. Each is a link to its view."""
    return "".join(f'<a href="#v{i}" data-go="{i}" class="{"done" if i < view else ("on" if i == view else "")}"></a>' for i in range(1, 5))


def template(root, name="panel.html"):
    for base in (root, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))):
        p = os.path.join(base, "templates", "panel", name)
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    raise FileNotFoundError("templates/panel/" + name)


def waiting_words(lang, items):
    """What is waiting, by what it is: "3 merchants and 2 transfers" — never a bare number."""
    n = {"merchant": 0, "transfer": 0, "other": 0}
    for d in items:
        n[d.get("kind") if d.get("kind") in ("merchant", "transfer") else "other"] += 1
    parts = [t_w(lang, f"w_n_{k}").format(n=v).replace("(s)", "" if v == 1 else "s") for k, v in n.items() if v]
    return t_w(lang, "w_and").join(parts)


def render(base, root, st, q, rec, job, held, tool=None, lang="en"):
    """The monthly panel, one step at a time (2026-11-12, user 001: four cards in two columns
    showed every step at once, each with a paragraph). Four views — get the files, import,
    categorize, done — each with a heading that says the one thing to do, one sentence at most,
    and its content as a table. The page shows the view the owner is at; the bar goes to the others."""
    tpl = template(root)
    items = (q or {}).get("items") or []
    cur, _lead, _kw = current_step(st, q)
    view = VIEW_OF[cur]
    busy = tool_notice(lang, tool)
    if job and not job.get("done"):
        busy += f'<p class="busy">{e(t(lang, "running_busy", verb=job["verb"]))}</p>'
    elif held:
        busy += f'<p class="busy">{e(t(lang, "held", verb=held.get("verb"), since=held.get("since")))}</p>'
    need_html, need, more = need_table(lang, st)
    drop_html, in_folder = drop_zone(lang, st, root)
    day = st.get("importDay")
    v1_h = t(lang, "v1_h") if need or in_folder else t(lang, "v1_none_h")
    v1_s = t(lang, "v1_s") if need else (t(lang, "v1_none_s") if not in_folder else "")
    if not need and not in_folder and day:
        need_html += f'<table class="tbl"><tr><td>{e(t(lang, "v1_day"))}</td><td>{e(str(day))}</td></tr></table>'
    v2_h = (t(lang, "v2_h", n=in_folder).replace("(s)", "" if in_folder == 1 else "s")) if in_folder else t(lang, "v2_none_h")
    what = waiting_words(lang, items)
    v3_h = t(lang, "v3_h_n", what=what) if items else t(lang, "v3_none_h")
    fill = {"{{BASE}}": e(base), "{{LANG}}": e(lang), "{{TITLE}}": "FIRE Toad",
            "{{SUBTITLE}}": e(t(lang, "subtitle")),
            "{{OPEN_DASH}}": e(t(lang, "open_dash")), "{{LANG_OTHER}}": e(t(lang, "lang_other")),
            "{{OTHER_LANG}}": "zh" if lang == "en" else "en",
            "{{BARS}}": bars(view), "{{VIEW}}": str(view), "{{CUR}}": str(cur), "{{INFOLDER}}": str(in_folder),
            "{{STEP_OF}}": e(t(lang, "v_step", i="{i}", n=4)),
            "{{V1_H}}": e(v1_h), "{{V1_S}}": e(v1_s), "{{V2_H}}": e(v2_h), "{{V3_H}}": e(v3_h), "{{V4_H}}": e(t(lang, "v4_h")),
            "{{STEP1}}": need_html, "{{STEP2}}": drop_html, "{{BALANCES}}": more,
            # with files in the folder the way on is one button, whatever else is still to come
            "{{V1_NEXT}}": (f'<div class="act"><button type="button" class="btn primary" data-go="2">{e(v2_h)}</button></div>'
                            if in_folder else ""),
            "{{STEP4}}": step4(lang, q), "{{FILED}}": merchants_list(lang, root),
            "{{STEP5}}": step5(lang, rec, base),
            "{{GO}}": e(t(lang, "go")), "{{DRY_HINT}}": e(t(lang, "dry_hint") if in_folder else t(lang, "dry_none")),
            "{{BUSY}}": busy, "{{AI}}": ai_card(lang, root), "{{AI_TITLE}}": e(t(lang, "ai_title")),
            "{{SETTINGS}}": e(t(lang, "settings")), "{{MORE}}": e(t(lang, "more_h")),
            "{{JS}}": json.dumps(js_strings(lang), ensure_ascii=False).replace("</", "<\\/"),
            "{{QDATA}}": json.dumps(qdata(q, lang), ensure_ascii=False).replace("</", "<\\/"),
            "{{VERSION}}": e((tool or {}).get("version") or "")}
    for k, v in fill.items():
        tpl = tpl.replace(k, v)
    return tpl


# ---------------------------------------------------------------- the setup wizard
def t_w(lang, key):
    return wizard_strings(lang).get(key, key)


def render_setup(base, root, st, job, tool=None, lang="en"):
    tpl = template(root, "setup.html")
    fill = {"{{BASE}}": e(base), "{{LANG}}": e(lang), "{{OTHER_LANG}}": "zh" if lang == "en" else "en",
            "{{W_TITLE}}": e(t_w(lang, "w_title")), "{{W_LANG}}": e(t_w(lang, "w_lang")),
            "{{STATE}}": json.dumps(st, ensure_ascii=False).replace("</", "<\\/"),
            "{{WS}}": json.dumps(wizard_strings(lang), ensure_ascii=False).replace("</", "<\\/"),
            "{{BUSY}}": tool_notice(lang, tool), "{{INBOX}}": e(os.path.join(root, "inbox")),
            "{{VERSION}}": e((tool or {}).get("version") or ""),
            "{{JOB}}": json.dumps(job, ensure_ascii=False).replace("</", "<\\/") if job else "null"}
    for k, v in fill.items():
        tpl = tpl.replace(k, v)
    return tpl


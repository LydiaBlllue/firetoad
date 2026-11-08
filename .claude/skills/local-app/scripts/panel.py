"""panel.py — the monthly panel as a page: five numbered steps, in the owner's language.

Server-rendered from what the scripts return (status.run() for the rows, confirm.run() for the
open questions, the newest imports.json record for the result), in the dashboard's own tokens so
it reads as the same product. It invents no row and no question: a row exists because the
register has a document or an account for it; a question because decisions.json holds it, with
the choices the scripts already attach (PRODUCT.md §6.11). Every sentence comes from
strings.py, in English or Chinese; the markup is templates/panel/panel.html.

The first version (2026-11-06) was four cards named after the skill's internals — Bring,
Import, Questions, Result — and the owner could not tell what to do first (2026-11-07). It is
now the month as a person does it:

  1  Get this month's files    one row per thing, with a plain state (still missing · in inbox ·
                               up to date) and, folded under each missing one, how to get it —
                               the bank's own path from parsers/support.py, the app page for a
                               screenshot (the register's `capture`), a field for a number
  2  Put them here             the drop zone, and what each file in inbox/ was recognised as
  3  Import                    look first, then import; undo underneath
  4  Answer a few questions    the open items as pills, one Save
  5  Done                      what changed, what was noticed, open the dashboard

and a strip of the five at the top with the current one lit, so the page says where you are.

No number here is typed by hand, and nothing here is financial logic.
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


def how(lang, text):
    return f'<details class="how"><summary>{e(t(lang, "how"))}</summary><p>{text}</p></details>'


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


# ---------------------------------------------------------------- step 1
def step1(lang, st):
    rows, done = [], []
    today = st.get("today") or ""
    stated = {x["account"]: x for x in st.get("stated") or []}
    shown = set()
    for b in st.get("statements") or []:
        if b["state"] == "ok":
            done.append(b["bank"]); continue
        lines, parser = [], None
        for r in b["docs"]:
            if r.get("missing") and len(r.get("inbox") or []) < len(r["missing"]):
                lines.append(e(t(lang, "missing", doc=r["key"], n=len(r["missing"]), months=months(lang, r["missing"]))))
                parser = parser or r.get("parser")
            elif r.get("inbox"):
                lines.append(e(t(lang, "doc_inbox", doc=r["key"])))
            else:
                lines.append(e(t(lang, "doc_ok", doc=r["key"])))
        extra = how(lang, bank_how(lang, b["bank"], parser)) if b["state"] == "todo" else ""
        rows.append(row("statement", b["bank"], "<br>".join(lines), b["state"], lang, extra, "statement"))
    for x in st.get("exports") or []:
        if x["state"] == "ok":
            done.append(x["from"]); continue
        extra = how(lang, export_how(lang, x["from"], x["key"])) if x["state"] == "todo" else ""
        rows.append(row("export", x["from"], e(t(lang, "export_line", key=x["key"], asof=x.get("asof") or t(lang, "never"))),
                        x["state"], lang, extra, "export"))
    for s in st.get("screenshots") or []:
        if s["state"] == "ok":
            done.append(s.get("inst") or s.get("name")); continue
        shown.add(s.get("account"))
        extra = how(lang, e(t(lang, "how_shot", capture=s.get("capture") or "")))
        extra += balance_form(lang, s.get("account"), s.get("capture"), today, True) if s.get("account") in stated else ""
        rows.append(row("shot", s.get("inst") or s.get("name"), e(t(lang, "asof", date=s.get("asof") or t(lang, "never"))),
                        s["state"], lang, extra, "shot"))
    for b in st.get("balances") or []:
        if b["state"] == "ok":
            done.append(b.get("inst") or b.get("name")); continue
        shown.add(b.get("account"))
        extra = how(lang, e(t(lang, "how_typed", inst=b.get("inst") or "", name=b.get("name") or "")))
        extra += balance_form(lang, b.get("account"), b.get("capture"), today, bool(b.get("capture"))) if b.get("account") in stated else ""
        rows.append(row("typed", b.get("inst") or "", e(b.get("name") or "") + " · " + e(t(lang, "asof", date=b.get("asof") or t(lang, "never"))),
                        b["state"], lang, extra, "typed"))
    for p in st.get("people") or []:
        rows.append(row("person", p.get("who"), e(t(lang, "people_line", who=p.get("who"), last=p.get("last") or t(lang, "never"))),
                        "optional", lang))
    uniq = []
    for d in done:
        if d and d not in uniq:
            uniq.append(d)
    if uniq:
        rows.append(f'<div class="row ok-line"><span class="ic">✓</span><div class="rw"><span class="wh">{e(t(lang, "all_ok", list=", ".join(uniq)))}</span></div></div>')
    rest = [x for k, x in stated.items() if k not in shown]
    if rest:
        inner = "".join(row("typed", x.get("inst") or "", e(x.get("name") or "") + " · " + e(t(lang, "asof", date=x.get("asof") or t(lang, "never"))),
                            "ok" if x.get("age") is not None and x["age"] < 25 else "optional", lang,
                            balance_form(lang, x["account"], x.get("capture"), today, bool(x.get("capture")))) for x in rest)
        rows.append(f'<details class="more"><summary>{e(t(lang, "other_balances", n=len(rest)))}</summary>{inner}</details>')
    return "".join(rows)


# ---------------------------------------------------------------- step 2
def step2(lang, st, root):
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
                items.append(f'<li><span class="ok">✓</span> {e(n)} <span class="muted">→ {e(label)}</span></li>')
            else:
                items.append(f'<li class="bad">✗ {e(n)} — {e(t(lang, "unnamed", why=note))}<br><span class="muted">{e(t(lang, "unnamed_fix"))}</span></li>')
    head = e(t(lang, "waiting", n=len(names))) if names else e(t(lang, "none_waiting"))
    return (f'<div class="drop" id="drop"><b>{e(t(lang, "drop"))}</b>'
            f'<span><label class="lnk">{e(t(lang, "or_choose"))}<input type="file" multiple hidden id="pick"></label> · '
            f'<button type="button" class="lnk" id="openinbox">{e(t(lang, "open_inbox"))}</button></span>'
            f'<small>{e(inbox)}</small><div class="dropped" id="dropped"></div></div>'
            f'<p class="foot">{head}</p>' + (f'<ul class="files">{"".join(items)}</ul>' if items else ""))


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


def step4(lang, q):
    items = (q or {}).get("items") or []
    if not items:
        return f'<p class="foot">{e(t(lang, "q_none"))}</p>'
    out = [f'<p class="q-intro">{e(t(lang, "q_intro"))}</p>']
    for it in items:
        ch = choices_for(it)
        sel = it.get("suggest") or it.get("default")
        if it.get("credit"):
            sel = confirm.INCOMING.get(sel, sel)
        pills = "".join(f'<button type="button" class="pl{" sel" if c == sel else ""}" data-n="{it["n"]}" data-v="{e(c)}">{e(c)}</button>' for c in ch)
        sug = ""
        if it.get("suggest"):
            sug_text = confirm.INCOMING.get(it["suggest"], it["suggest"]) if it.get("credit") else it["suggest"]
            sug = f' · {e(t(lang, "suggested"))} <b>{e(sug_text)}</b>' + (f'<span class="dot" title="{e(t(lang, "model_dot"))}">●</span>' if it.get("suggestBy") == "model" else "")
        seen = f' · {e(t(lang, "seen_n", n=it["seen"]))}' if it.get("seen") else ""
        out.append(f'<div class="q" data-n="{it["n"]}"><div class="qt"><b>{it["n"]}.</b> {e(it.get("what"))}</div>'
                   f'<div class="qs">{e(t(lang, "filed_as"))} <b>{e(it.get("default"))}</b>{sug}{seen}</div>'
                   + (f'<div class="pills">{pills}</div>' if pills else f'<div class="qs">{e(t(lang, "in_ledger"))}</div>') + '</div>')
    out.append(f'<div class="act"><button type="button" class="btn primary" id="save">{e(t(lang, "save_answers"))}</button>'
               f'<span class="hint">{e(t(lang, "unanswered_keep"))}</span></div>')
    return "".join(out)


# ---------------------------------------------------------------- step 5
def step5(lang, rec, base):
    if not rec:
        return f'<p class="foot">{e(t(lang, "no_import"))}</p>'
    out = [f'<div class="qs">{e(t(lang, "last_import", date=rec.get("date")))}</div>']
    for c in rec.get("changed") or []:
        out.append(f'<div class="kv"><span class="k">{e(c.get("label"))}</span><span class="v">{e(c.get("from"))} → {e(c.get("to"))}</span></div>')
    for n in rec.get("noticed") or []:
        sev = n.get("sev") or "ok"
        out.append(f'<div class="nt {e(sev)}"><span class="ic">{"✓" if sev == "ok" else "!"}</span>{e(n.get("text"))}</div>')
    out.append(f'<div class="act"><a class="btn primary" href="{e(base)}/" target="_blank" rel="noopener">{e(t(lang, "open_dash"))}</a></div>')
    return "".join(out)


# ---------------------------------------------------------------- the model, by choice
def ai_card(lang, root):
    st = ai.status(root)
    opts = "".join(f'<option value="{e(k)}"{" selected" if k == st["provider"] else ""}>{e(v["label"])}</option>' for k, v in st["providers"].items())
    notes = json.dumps({k: {"note": v["note"], "baseUrl": v["baseUrl"], "model": v["model"], "key": v["key"]} for k, v in st["providers"].items()})
    on = st["provider"] != "none"
    msg = ("on · " + e(st["provider"]) + " · " + e(st["model"] or "")) if st["enabled"] else (e(t(lang, "ai_nokey")) if on else e(t(lang, "ai_off")))
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


def strip(lang, cur):
    out = []
    for i in range(1, 6):
        cls = "done" if i < cur else ("on" if i == cur else "")
        out.append(f'<a href="#step{i}" class="stp {cls}"><span class="n">{"✓" if i < cur else i}</span><span class="t">{e(t(lang, f"s{i}"))}</span></a>')
    return "".join(out)


def template(root, name="panel.html"):
    for base in (root, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))):
        p = os.path.join(base, "templates", "panel", name)
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    raise FileNotFoundError("templates/panel/" + name)


def render(base, root, st, q, rec, job, held, tool=None, lang="en"):
    tpl = template(root)
    nq = len((q or {}).get("items") or [])
    cur, lead_key, kw = current_step(st, q)
    busy = tool_notice(lang, tool)
    if job and not job.get("done"):
        busy += f'<p class="busy">{e(t(lang, "running_busy", verb=job["verb"]))}</p>'
    elif held:
        busy += f'<p class="busy">{e(t(lang, "held", verb=held.get("verb"), since=held.get("since")))}</p>'
    day = st.get("importDay")
    fill = {"{{BASE}}": e(base), "{{LANG}}": e(lang), "{{TITLE}}": "Jade Toad",
            "{{SUBTITLE}}": e(t(lang, "subtitle", date=st.get("today"))),
            "{{INTRO}}": e(t(lang, "intro")) + (f' <span class="muted">({e(t(lang, "import_day", day=day))})</span>' if day else ""),
            "{{OPEN_DASH}}": e(t(lang, "open_dash")), "{{LANG_OTHER}}": e(t(lang, "lang_other")),
            "{{OTHER_LANG}}": "zh" if lang == "en" else "en",
            "{{LEAD}}": e(t(lang, lead_key, **kw)), "{{STRIP}}": strip(lang, cur), "{{CUR}}": str(cur),
            "{{S1}}": e(t(lang, "s1")), "{{S2}}": e(t(lang, "s2")), "{{S3}}": e(t(lang, "s3")), "{{S4}}": e(t(lang, "s4")), "{{S5}}": e(t(lang, "s5")),
            "{{STEP1}}": step1(lang, st), "{{STEP2}}": step2(lang, st, root), "{{STEP4}}": step4(lang, q), "{{STEP5}}": step5(lang, rec, base),
            "{{DRY}}": e(t(lang, "dry")), "{{GO}}": e(t(lang, "go")), "{{DRY_HINT}}": e(t(lang, "dry_hint")), "{{UNDO}}": e(t(lang, "undo")),
            "{{BUSY}}": busy, "{{NQ}}": str(nq), "{{AI}}": ai_card(lang, root), "{{AI_TITLE}}": e(t(lang, "ai_title")),
            "{{SETTINGS}}": e(t(lang, "settings")),
            "{{JS}}": json.dumps(js_strings(lang), ensure_ascii=False).replace("</", "<\\/"),
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


def no_dashboard(base):
    return (f'<!doctype html><meta charset="utf-8"><title>Jade Toad</title>'
            f'<p style="font-family:system-ui;padding:40px">No dashboard is built yet. '
            f'<a href="{e(base)}/panel">Open the panel</a> and import a month.</p>')

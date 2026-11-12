#!/usr/bin/env python3
"""wizard.py — the setup as screens: what each one shows, and what the answers become.

The setup skill is an interview in chat; the local app has no chat. This is the same setup
with the questions laid out as screens — Files · Accounts · Money in and out · Goal ·
Day · Build — in the order the skill asks them, drawn from the draft propose.py makes of the
first files, and written back into the draft's own shape, so the scaffold runs on exactly the
answers file the skill would have produced. Nothing here invents a question: every screen is a
field of `setup-answers.json`, and a question the owner skips stays unanswered (the key is left
out, the page says *Not set*), the skill's rule.

    python3 .claude/skills/setup/scripts/wizard.py . --json        # the screens, from inbox/
    python3 .claude/skills/setup/scripts/wizard.py . --apply answers.json --write

state(root) reads; apply(root, answers, write) writes the answers file, runs the scaffold, the
rebuild and the first import — the skill's step 4 — and returns what each said. Both go through
verbs.py like every other verb, so the app and this chat get the same result.
"""
import argparse
import contextlib
import datetime
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(SKILLS, "update-dashboard", "scripts"))
import layout  # noqa: E402
import verbs  # noqa: E402
import scaffold  # noqa: E402
import propose  # noqa: E402
import ready  # noqa: E402

ROLES = [("buffer", "Everyday money", "cash I spend from or keep on hand"),
         ("grow", "Growing", "invested for the long run — the portfolio"),
         ("set-aside", "Set aside", "already has a purpose: a first home, an emergency fund"),
         ("none", "Owned, not money", "a home, a car — counted, neither growing nor spent")]
REACH_OF_ROLE = {"buffer": "today", "set-aside": "spoken", "none": "locked"}
IGNORE = {"README.txt", ".gitkeep", ".DS_Store"}


def inbox_files(root):
    d = os.path.join(root, "inbox")
    return sorted(n for n in (os.listdir(d) if os.path.isdir(d) else []) if n not in IGNORE and not n.startswith("."))


def ready_lines(root):
    """ready.py's verdict, captured: it prints and returns an exit code."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = ready.main(["ready.py", root])
        except SystemExit as e:
            rc = e.code or 0
    return rc, [l for l in buf.getvalue().splitlines() if l.strip()]


def is_demo(root):
    return scaffold.is_demo(root)


def screens(draft, today):
    """The screens, from the draft: what each shows and what it asks. Values are the draft's
    suggestions; `ask` is the question propose.py wrote, when it wrote one."""
    q = {x["id"]: x for x in (draft.get("_open") or [])}
    accounts = []
    for i, a in enumerate(draft.get("accounts") or []):
        accounts.append({"i": i, "inst": a.get("inst"), "name": a.get("name"), "kind": a.get("kind"),
                         "id": a.get("id"), "cur": a.get("cur"), "balance": a.get("balance"), "asof": a.get("asof"),
                         "role": a.get("role"), "seenAs": a.get("seenAs"),
                         "needsBalance": a.get("balance") is None,
                         "doc": (a.get("doc") or {}).get("file"), "liability": a.get("kind") in scaffold.DEBT_KINDS})
    plan = draft.get("plan") or {}
    # an OFX download names its accounts by id, never the bank: the wizard asks the bank once per file
    ofx = []
    for x in (draft.get("_open") or []):
        if x["id"].startswith("ofx:"):
            f = x["id"][4:]
            ids = [i for i, a in enumerate(draft.get("accounts") or []) if a.get("ofxId")]
            ofx.append({"file": f, "accounts": ids, "ask": x.get("q")})
    closes = [int((a.get("doc") or {}).get("closes")) for a in draft.get("accounts") or []
              if isinstance((a.get("doc") or {}).get("closes"), int)]
    day = (max(closes) % 28) + 1 if closes else int(draft.get("importDay") or 1)
    return {
        # the name the statements carry is the owner question's `suggest`, not the draft's `owner`
        # (which stays None until answered); the first simulation showed an empty name field
        "owner": {"suggest": draft.get("owner") or (q.get("owner") or {}).get("suggest"), "ask": (q.get("owner") or {}).get("q")},
        "born": {"ask": (q.get("born") or {}).get("q")},
        "accounts": {"rows": accounts, "roles": [{"key": k, "label": l, "why": w} for k, l, w in ROLES],
                     "ask": (q.get("accounts") or {}).get("q"), "missing": (q.get("missing") or {}).get("q"),
                     "cash": (q.get("cash") or {}).get("q"), "kinds": sorted(scaffold.CASH_KINDS | scaffold.DEBT_KINDS | scaffold.INVEST_KINDS)},
        "money": {"takeHome": {"suggest": plan.get("takeHome"), "ask": (q.get("pay") or {}).get("q")},
                  "invest": {"suggest": plan.get("invest"), "ask": (q.get("invest") or {}).get("q")},
                  "everyday": {"suggest": plan.get("everyday"), "ask": (q.get("everyday") or {}).get("q")},
                  "committed": {"ask": (q.get("committed") or {}).get("q")},
                  "planBase": {"suggest": plan.get("planBase") or plan.get("everyday"), "ask": (q.get("planBase") or {}).get("q")},
                  "pensions": {"ask": (q.get("pensions") or {}).get("q")}},
        "goal": {"ask": (q.get("fire") or {}).get("q")},
        "day": {"suggest": day, "closes": closes},
        "ofx": ofx,
        "later": [x for x in (draft.get("_open") or [])
                  if x["id"] in ("foreign", "counterparty", "buckets", "files") or x["id"].startswith("csv:")],
        "today": today,
    }


def state(root, say=None):
    """What the wizard draws (verbs.py): `demo` (whether this folder still holds the demo and so
    the wizard shows at all), `ready` (rc, lines), `files` in inbox/, the `draft` and the
    `screens` built from it (None without files)."""
    emit, lines = verbs.speaker(say)
    root = os.path.abspath(root)
    today = datetime.date.today().isoformat()
    rc, rl = ready_lines(root)
    res = {"demo": is_demo(root), "ready": {"rc": rc, "lines": rl, **ready.check(root)}, "files": inbox_files(root),
           "draft": None, "screens": None, "today": today}
    who = "the demo is still here" if res["demo"] else "this folder is already somebody's"
    emit(f"=== setup — {who} · {len(res['files'])} file(s) in inbox/ ===")
    for l in rl:
        emit("  " + l)
    if res["files"]:
        r = propose.run(root, say=None)
        if r.get("draft"):
            res["draft"] = r["draft"]
            res["screens"] = screens(r["draft"], today)
            emit(f"  draft: {len(r['draft'].get('accounts') or [])} account(s), {len(r['draft'].get('_open') or [])} question(s)")
    return verbs.result(res, 0, lines)


def _num(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except ValueError:
        return None


def merge(draft, answers, today):
    """The wizard's answers into the draft, in the answers file's own shape. A field left blank
    is left out (never 0, never a guess); the open questions are closed because the owner has
    been through every screen — skipping is an answer the skill allows."""
    a = json.loads(json.dumps(draft))
    a.pop("_open", None)
    own = (answers.get("owner") or "").strip()
    if own:
        a["owner"] = own
    born = _num(answers.get("born"))
    if born and 1900 < born < 2100:
        a["born"] = int(born)
    else:
        a.pop("born", None)
    day = _num(answers.get("importDay"))
    if day and 1 <= day <= 28:
        a["importDay"] = int(day)
    # an OFX download's bank, said once per file, lands on every account the file named
    for f, bank in (answers.get("ofx") or {}).items():
        bank = (bank or "").strip()
        if not bank:
            continue
        for acc in a.get("accounts") or []:
            if acc.get("ofxId") and (acc.get("inst") in ("OFX", None) or (acc.get("doc") or {}).get("file") == f):
                acc["inst"] = bank
                if (acc.get("doc") or {}).get("file") == f:
                    acc["doc"]["ep"] = bank
    # accounts: a role per row, a name an owner changes, a balance the exports do not carry
    for row in answers.get("accounts") or []:
        i = row.get("i")
        if not isinstance(i, int) or i >= len(a.get("accounts") or []):
            continue
        acc = a["accounts"][i]
        if row.get("name", "").strip():
            acc["name"] = row["name"].strip()
        if row.get("role") in dict((k, l) for k, l, _ in ROLES) and acc.get("kind") not in scaffold.DEBT_KINDS:
            acc["role"] = row["role"]
            acc["reach"] = REACH_OF_ROLE.get(row["role"], acc.get("reach") or "today")
        bal = _num(row.get("balance"))
        if bal is not None and acc.get("balance") is None:
            acc["balance"] = bal
            acc["asof"] = row.get("asof") or acc.get("asof") or today
    # accounts the files do not show: the owner's word, with the balance they read off the app
    for row in answers.get("added") or []:
        if not (row.get("inst") or "").strip() or not (row.get("name") or "").strip():
            continue
        kind = row.get("kind") if row.get("kind") in (scaffold.CASH_KINDS | scaffold.DEBT_KINDS | scaffold.INVEST_KINDS) else "Savings"
        bal = _num(row.get("balance"))
        acc = {"inst": row["inst"].strip(), "name": row["name"].strip(), "kind": kind, "id": "—", "cur": "CAD",
               "balance": (-abs(bal) if kind in scaffold.DEBT_KINDS and bal is not None else bal), "asof": today, "feeds": ""}
        acc.update({k: v for k, v in scaffold.default_axes({**acc, "src": "banks.json"}).items() if k in ("role", "reach")})
        if row.get("role") in REACH_OF_ROLE or row.get("role") == "grow":
            acc["role"] = row["role"]; acc["reach"] = REACH_OF_ROLE.get(row["role"], acc["reach"])
        a.setdefault("accounts", []).append(acc)
    # the plan: flows
    plan = a.setdefault("plan", {})
    m = answers.get("money") or {}
    for k in ("takeHome", "invest", "everyday", "planBase"):
        v = _num(m.get(k))
        if v is not None:
            plan[k] = int(round(v))
        elif m.get(k, None) == "":
            plan.pop(k, None)
    committed = []
    for c in m.get("committed") or []:
        amt = _num(c.get("amount"))
        if not (c.get("name") or "").strip() or amt is None:
            continue
        row = {"name": c["name"].strip(), "amount": int(round(amt)), "afterFire": "keep" if c.get("afterFire", True) else "drop"}
        if c.get("until"):
            row["until"] = c["until"]
        if c.get("estimate"):
            row["estimate"] = True
        committed.append(row)
    if committed:
        plan["committed"] = committed
    rent = _num(m.get("imputedRent"))
    if rent:
        plan["imputedRent"] = int(round(rent))
    goal = (answers.get("goal") or "").lower()
    if goal in ("yes", "no"):
        plan["fire"] = {"goal": goal == "yes", "asked": today}
    pens = []
    for p in m.get("pensions") or []:
        mo, fr = _num(p.get("monthly")), _num(p.get("from"))
        if p.get("name") and mo and fr:
            pens.append({"name": p["name"], "monthly": int(round(mo)), "from": int(fr), "asof": today, "source": "My Service Canada estimate"})
    if pens:
        a["pensions"] = pens
    return a


def apply(root, answers, write=False, say=None):
    """Write the answers file, then the skill's step 4: scaffold → rebuild → the first import
    (verbs.py). Returns `answers` (the file as written), `written`, and each step's result."""
    emit, lines = verbs.speaker(say)
    root = os.path.abspath(root)
    today = datetime.date.today().isoformat()
    res = {"answers": None, "written": False, "scaffold": None, "rebuild": None, "import": None}
    if not is_demo(root):
        emit("  ✗ this folder is already somebody's (findata/ is not the demo); the setup does not run over it", loud_line=True)
        return verbs.result(res, 1, lines)
    if not inbox_files(root):
        emit("  ✗ nothing in inbox/: drop last month's files first", loud_line=True)
        return verbs.result(res, 1, lines)
    draft = propose.run(root, say=None).get("draft")
    if not draft:
        emit("  ✗ no draft could be made from the files in inbox/", loud_line=True)
        return verbs.result(res, 1, lines)
    a = merge(draft, answers or {}, today)
    res["answers"] = a
    if not a.get("owner"):
        emit("  ✗ a name is needed: it is shown under the FIRE Toad wordmark", loud_line=True)
        return verbs.result(res, 1, lines)
    emit(f"=== setup — {a['owner']}, {len(a.get('accounts') or [])} account(s), import day {a.get('importDay', 1)} ===")
    if not write:
        emit("  nothing written. Run with --write to build the workspace.")
        return verbs.result(res, 0, lines)
    dst = os.path.join(root, layout.rel("setup-answers.json"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(a, fh, ensure_ascii=False, indent=2); fh.write("\n")
    try:
        r = scaffold.run(root, answers=dst, write=True, say=emit)
    except SystemExit as e:  # scaffold's refusals (die) are SystemExit, the skill relies on that
        emit(f"  ✗ the scaffold refused: {e}", loud_line=True)
        return verbs.result(res, 1, lines)
    res["scaffold"] = verbs.public(r)
    if r["rc"]:
        return verbs.result(res, r["rc"], lines)
    import rebuild  # noqa: E402  update-dashboard/scripts
    import update  # noqa: E402
    res["rebuild"] = verbs.public(rebuild.run(root, write=True, say=emit))
    emit("")
    r2 = update.run(root, write=True, say=emit, loud=emit)
    res["import"] = verbs.public(r2)
    res["written"] = True
    return verbs.result(res, r2["rc"] if r2["rc"] in (0, 2) else r2["rc"], lines)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--apply", metavar="ANSWERS.json", help="the wizard's answers; with --write, build the workspace")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.apply:
        ans = json.load(open(a.apply, encoding="utf-8"))
        r = apply(a.root, ans, write=a.write, say=None if a.json else print)
    else:
        r = state(a.root, say=None if a.json else print)
    if a.json:
        print(json.dumps(verbs.public(r), ensure_ascii=False, indent=1))
    return r["rc"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

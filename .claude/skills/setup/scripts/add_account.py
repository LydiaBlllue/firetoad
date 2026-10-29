"""add_account.py — an account added after setup, from its own statements.

Setup runs once. The first person to add an account afterwards had to edit accounts.json by
hand, and its first import then left net worth where it was (2026-10-28, first user). This reads
the statements in inbox/ the way setup's draft does (propose.py), keeps every account the
register does not have yet, and drafts its register row and its monthly document with the same
code the scaffold uses — so a row added later is exactly the row setup would have written.

    python3 .claude/skills/setup/scripts/add_account.py .            # the draft
    python3 .claude/skills/setup/scripts/add_account.py . --write    # add it to the register

Then run the import: the same statements are its first one, and they create the balance.
A name, a kind or what the account is for that the statement got wrong is said before --write,
with --name, --feeds or --kind (one new account at a time when they are used).
"""
import argparse, datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import propose as P  # noqa: E402
import scaffold as S  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "update-dashboard", "scripts"))
import layout  # noqa: E402

digits = lambda s: re.sub(r"\D", "", s or "")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--name"); ap.add_argument("--kind"); ap.add_argument("--feeds")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    reg_p = layout.path(root, "accounts.json")
    reg = json.load(open(reg_p, encoding="utf-8"))
    have = {digits(x.get("id"))[-4:] for x in reg["accounts"] if digits(x.get("id"))}
    draft = P.propose(root, os.path.join(root, "inbox"))
    new = [x for x in draft["accounts"] if digits(x.get("id"))[-4:] not in have]
    if not new:
        print("Every account in inbox/ is already in the register. Nothing to add.")
        return 0
    if (a.name or a.kind or a.feeds) and len(new) > 1:
        print(f"  ✗ {len(new)} new accounts in inbox/: --name, --kind and --feeds need one at a time.")
        return 1
    for x in new:
        if a.name: x["name"] = a.name
        if a.kind: x["kind"] = a.kind
        if a.feeds: x["feeds"] = a.feeds

    # The scaffold's own builder, on an answers file of just these accounts: one definition of a
    # register row and its document. Keys and tags are kept apart from the ones already in use.
    keys = {x["key"] for x in reg["accounts"]}
    built = S.build({**draft, "owner": "—", "accounts": new, "funds": []}, datetime.date.today().isoformat())
    rows = json.loads(built[layout.rel("accounts.json")])
    for r in rows["accounts"]:
        k, n = r["key"], 2
        while r["key"] in keys:
            r["key"] = f"{k}-{n}"; n += 1
        keys.add(r["key"])
    print(f"=== add an account — {len(rows['accounts'])} not in the register ===")
    for r in rows["accounts"]:
        print(f"  {r['inst']:<8} {r['name']:<28} {r['kind']:<14} {r['id']:<8} {r.get('feeds') or '—':<12} "
              f"{r.get('side')}/{r.get('role')}/{r.get('reach')}  key {r['key']}")
    for d in rows["documents"]:
        print(f"  file {d['file']}  closes {d['closes']}  → {d['into']}" + (f"  ({d['parser']})" if d.get("parser") else ""))
    if not a.write:
        print("\n  nothing written. Check the row with the owner, then --write; the import after it is the account's first.")
        return 0
    reg["accounts"] += rows["accounts"]
    reg["documents"] += rows["documents"]
    json.dump(reg, open(reg_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(reg_p, "a", encoding="utf-8").write("\n")
    for path, text in built.items():
        # A new ledger starts as its header, exactly as setup writes one.
        if path.endswith(".csv") and not path.endswith("spending.csv") and not os.path.exists(os.path.join(root, path)):
            open(os.path.join(root, path), "w", encoding="utf-8").write(text)
    print(f"\n  → added to {os.path.relpath(reg_p, root)}. Now run update.py . --write: these statements are its first import.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

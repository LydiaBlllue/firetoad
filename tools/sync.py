#!/usr/bin/env python3
"""sync.py — push the tool into a workspace, and never anything else.

The tool is this repository. A workspace is a folder somewhere else (an iCloud folder, say) that
holds one person's findata/, their inbox/ and archive/, their OWNER.md — and a copy of the tool.
This script refreshes that copy:

    python3 tools/sync.py <workspace>              # copy the tool in, then rebuild the dashboards
    python3 tools/sync.py <workspace> --check      # say what would change, touch nothing
    python3 tools/sync.py <workspace> --install-guard
        # also install a pre-commit hook in THIS repository that refuses to commit any staged
        # file containing an identifier from <workspace>/.private/deny.txt (a line starting with
        # ! names a file the check skips, e.g. !LICENSE for the authorship line)

What it copies: `.claude/` (the skills and the hook settings), `templates/dashboards/`, the three
governing documents, and `docs/` minus the demo screenshots. What it never touches: `findata/`,
`inbox/`, `archive/`, `dashboards/` (rebuild.py writes those), `OWNER.md`, `decisions/` (the
owner's dated history), `.private/`.

FINANCE.md is the one file with a seam: the prose is the tool's, the figures table is the
workspace's. The table is carried across from the workspace's own copy and the rebuild keeps it
current.

Why a copy and not a symlink or a git checkout inside the workspace: iCloud Drive corrupts `.git`
directories and does not carry symlinks to Windows. A copy is dull, and dull is what a sync should
be.
"""

import filecmp
import os
import re
import shutil
import stat
import subprocess
import sys

TOOL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYNCED = [
    ".claude/skills",
    "app.py",             # the second door (2.0.0): python3 app.py serves the dashboard and the panel
    "templates/panel",    # the panel's markup, read from the workspace like templates/dashboards/
    "tests",              # the unit tests; checks.py --level release runs them where they exist
    "tools",              # what the tests and the selftest import (migrate.py, fixtures.py); without it
                          # tests/test_migrate.py failed in every workspace (2026-11-06, user 001)
    ".claude/settings.json",
    "templates/dashboards",
    "CLAUDE.md",
    "FINANCE.md",
    "DESIGN.md",
    "RELEASE-ROADMAP.md", # what is coming, and the version rule (ROADMAP.md until 2026-11-13)
    "CHANGELOG.md",
    "docs/pipeline.svg",
    "docs/hero.png",
    "docs/banks.md",      # the banks page, written from parsers/support.py (S9)
    "docs/install.md",    # README links it; the Chinese one is in docs/zh
    "docs/logo.svg",
    "docs/zh",            # the Chinese guide is the tool's, like README; screens/ stays the demo's
    ".gitignore",         # not for git: check_design's S4 reads it to skip files an owner writes
                          # (setup-answers.json), and without it a workspace failed on them
]
# A tool file that was renamed leaves its old copy in every folder synced before, and a stale
# copy is read as current. The old name goes when the new one has arrived (2026-11-13).
RENAMED = {"ROADMAP.md": "RELEASE-ROADMAP.md"}

NEVER = ("findata", "inbox", "archive", "dashboards", "OWNER.md", "decisions", ".private", "feedback", "product")

# The empty OWNER.md a new owner starts from; setup writes the same file over the demo's.
OWNER_STUB = os.path.join(TOOL, ".claude", "skills", "setup", "data", "owner_stub.md")

GUARD = """#!/bin/sh
# Installed by tools/sync.py --install-guard. Refuses a commit whose staged files contain any
# identifier from the owner's private deny list, which lives OUTSIDE this repository.
# It also runs the setup's data guard: real findata/ is refused when this checkout has a remote.
python3 "$(git rev-parse --show-toplevel)/.claude/skills/setup/scripts/guard.py" || exit 1
DENY="__DENY__"
[ -f "$DENY" ] || { echo "pre-commit guard: $DENY is missing — refusing to commit blind"; exit 1; }
python3 - "$DENY" <<'PY'
import subprocess, sys
lines = [l.rstrip("\\n") for l in open(sys.argv[1], encoding="utf-8")]
deny = [l for l in lines if l.strip() and not l.startswith(("#", "!"))]
skip = tuple(l[1:].strip() for l in lines if l.startswith("!"))
names = subprocess.run(["git", "diff", "--cached", "--name-only", "-z"], capture_output=True).stdout
hits = []
for f in [x for x in names.decode().split("\\0") if x]:
    if f.startswith(skip):
        continue
    blob = subprocess.run(["git", "show", ":" + f], capture_output=True).stdout.decode("utf-8", "ignore")
    hits += [(f, d) for d in deny if d in blob]
if hits:
    for f, d in hits[:20]:
        print(f"  \\u2717 {f}: contains {d!r}")
    print(f"pre-commit guard: {len(hits)} hit(s) \\u2014 nothing committed")
    sys.exit(1)
PY
"""


def tool_schema():
    """The findata shape this tool builds from, read out of rebuild.py so it is written once."""
    rb = open(os.path.join(TOOL, ".claude", "skills", "update-dashboard", "scripts", "rebuild.py"),
              encoding="utf-8").read()
    m = re.search(r"^SCHEMA = (\d+)", rb, re.M)
    return int(m.group(1)) if m else None


def workspace_schema(ws):
    p = os.path.join(ws, "findata", "register", "profile.json")
    if not os.path.exists(p):
        p = os.path.join(ws, "findata", "profile.json")
    if not os.path.exists(p):
        return None
    import json
    return int(json.load(open(p, encoding="utf-8")).get("schema", 2))


def differs(a, b):
    if os.path.isdir(a):
        if not os.path.isdir(b):
            return True
        cmp = filecmp.dircmp(a, b)
        return bool(cmp.left_only or cmp.right_only or cmp.diff_files) or \
            any(differs(os.path.join(a, d), os.path.join(b, d)) for d in cmp.common_dirs)
    return not (os.path.exists(b) and filecmp.cmp(a, b, shallow=False))


OWN_LINES = "# Your own data from here on"     # scaffold.py keep_private writes the block under it


def seam_text(rel, src, dst):
    """The two files with a seam, as the sync would write them, or None for any other file.
    FINANCE.md: the tool's prose around the workspace's own figures table. .gitignore: the tool's
    lines, then the block the setup added to keep the owner's data out of a remote — a sync used
    to copy the tool's file over it and drop that block, and the app, comparing whole files,
    said a folder it had just set up "differs" (2026-11-12)."""
    if not os.path.exists(dst):
        return None
    if rel == "FINANCE.md":
        tool_text = open(src, encoding="utf-8").read()
        mine = figures_block(open(dst, encoding="utf-8").read())
        theirs = figures_block(tool_text)
        return tool_text.replace(theirs, mine) if (mine and theirs) else tool_text
    if rel == ".gitignore":
        tool_lines = open(src, encoding="utf-8").read().splitlines()
        cut = next((i for i, l in enumerate(tool_lines) if l.startswith(OWN_LINES)), None)
        if cut is not None:      # the tool's side is itself a set-up folder (python3 app.py inside one)
            tool_lines = tool_lines[:cut]
            while tool_lines and not tool_lines[-1].strip():
                tool_lines.pop()
        mine = open(dst, encoding="utf-8").read().splitlines()
        at = next((i for i, l in enumerate(mine) if l.startswith(OWN_LINES)), None)
        if at is None:
            return "\n".join(tool_lines) + "\n"
        own = mine[at:]
        taken = {"# " + l.strip() for l in own if l.strip() and not l.startswith("#")}
        return "\n".join([l for l in tool_lines if l.strip() not in taken] + [""] + own).lstrip("\n") + "\n"
    return None


def pending(ws):
    """What a sync would change in this workspace, without changing it: the app's question
    "is the folder's copy the app's?" asked with the sync's own rules, seams included."""
    out = []
    for rel in SYNCED:
        src, dst = os.path.join(TOOL, rel), os.path.join(ws, rel)
        if not os.path.exists(src):
            continue
        new_text = seam_text(rel, src, dst)
        if new_text is not None:
            if new_text != open(dst, encoding="utf-8").read():
                out.append(rel)
        elif differs(src, dst):
            out.append(rel)
    for old, new in RENAMED.items():
        if os.path.isfile(os.path.join(ws, old)) and os.path.exists(os.path.join(TOOL, new)) and not os.path.exists(os.path.join(TOOL, old)):
            out.append(old)
    return out


def figures_block(text):
    m = re.search(r'<!-- LINT:FIGURES.*?<!-- LINT:FIGURES:END -->\n', text, re.S)
    return m.group(0) if m else None


def markers(ws, name):
    """An owner's README is theirs and never copied over, but it carries the tool's own numbers in
    markers that check_design reads: how many pages and sections, the sidebar's list, how many
    faults the selftest plants. A sync that changed the page left every owner's README failing
    S4 and S6 until someone edited it by hand (2026-11-05, user 002). So the numbers, and only
    the numbers and the sidebar line, follow the tool; every other word stays the owner's."""
    import re as _re
    p, src = os.path.join(ws, name), os.path.join(TOOL, "README.md")
    if not os.path.exists(p):
        return False
    tool = open(src, encoding="utf-8").read()
    t0 = t = open(p, encoding="utf-8").read()
    nav = _re.search(r"<!--\s*LINT:NAV main=(\d+)/(\d+)[^>]*-->", tool)
    fl = _re.search(r"<!--\s*LINT:FAULTS n=(\d+)\s*-->", tool)
    side = next((l.strip() for l in tool[nav.end():].splitlines() if " · " in l), None) if nav else None
    m = _re.search(r"<!--\s*LINT:NAV main=(\d+)/(\d+)([^>]*)-->", t)
    if nav and m:
        old_p, old_s = m.group(1), m.group(2)
        lines = t[m.end():].splitlines(keepends=True)
        for i, l in enumerate(lines[:4]):
            if " · " in l and side:
                lines[i] = l[:len(l) - len(l.lstrip())] + side + ("\n" if l.endswith("\n") else "")
                break
            lines[i] = _re.sub(r"\b" + old_p + r"(\s*(?:pages|页))", nav.group(1) + r"\1", l)
            lines[i] = _re.sub(r"\b" + old_s + r"(\s*(?:sidebar |个侧栏|sections|groups))", nav.group(2) + r"\1", lines[i])
        t = t[:m.start()] + f"<!-- LINT:NAV main={nav.group(1)}/{nav.group(2)}{m.group(3)}-->" + "".join(lines)
    f = _re.search(r"<!--\s*LINT:FAULTS n=(\d+)\s*-->", t)
    if fl and f and f.group(1) != fl.group(1):
        old = f.group(1)
        t = t.replace(f.group(0), f"<!-- LINT:FAULTS n={fl.group(1)} -->")
        t = _re.sub(r"\b" + old + r"(\s*(?:specific\s+)?faults?)", fl.group(1) + r"\1", t)
        t = _re.sub(r"种下\s*" + old + r"\s*个故障", f"种下 {fl.group(1)} 个故障", t)
    if t != t0:
        open(p, "w", encoding="utf-8").write(t)
        return True
    return False


def main(argv):
    if len(argv) < 2 or argv[1].startswith("--"):
        print(__doc__); return 2
    ws = os.path.abspath(argv[1])
    check = "--check" in argv
    if not os.path.isdir(os.path.join(ws, "findata")) and not check:
        os.makedirs(ws, exist_ok=True)
    print(f"=== sync {TOOL} → {ws}" + ("  (check only)" if check else ""))
    # A tool that builds a newer findata shape than the workspace has must not be copied in:
    # rebuild.py would refuse, the hook would fail on every edit, and the page would go stale
    # with nothing saying why. The migration is one command, named here.
    have, want = workspace_schema(ws), tool_schema()
    if have is not None and want is not None and have != want:
        if have < want:
            print(f"  ✗ the workspace's findata/ is schema {have}; this tool builds schema {want}.\n"
                  f"    Run: python3 tools/migrate.py \"{ws}\"   (every step from {have} to {want}), then sync again. Nothing copied.")
        else:
            print(f"  ✗ the workspace's findata/ is schema {have}, newer than this tool ({want}). Nothing copied.")
        return 1
    changed = []
    for rel in SYNCED:
        src, dst = os.path.join(TOOL, rel), os.path.join(ws, rel)
        if not os.path.exists(src):
            print(f"  ⚠ the tool has no {rel}"); continue
        new_text = seam_text(rel, src, dst)
        if new_text is not None:
            if new_text != open(dst, encoding="utf-8").read():
                changed.append(rel)
                if not check:
                    open(dst, "w", encoding="utf-8").write(new_text)
            continue
        if differs(src, dst):
            changed.append(rel)
            if not check:
                if os.path.isdir(src):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
    for old, new in RENAMED.items():
        gone = os.path.join(ws, old)
        if os.path.isfile(gone) and os.path.exists(os.path.join(TOOL, new)) and not os.path.exists(os.path.join(TOOL, old)):
            changed.append(f"{old} (now {new})")
            if not check:
                os.remove(gone)
    for rel in changed:
        print(f"  {'·' if check else '→'} {rel}")
    if not changed:
        print("  ✓ the workspace already has this tool")
    for rel in NEVER:
        pass  # listed for the reader: nothing here is written by this script

    owner = os.path.join(ws, "OWNER.md")
    if not os.path.exists(owner) and not check:
        shutil.copyfile(OWNER_STUB, owner)
        print("  → OWNER.md (empty stub — it is yours to fill)")
    for d in ("inbox", "archive"):
        if not check:
            os.makedirs(os.path.join(ws, d), exist_ok=True)

    if "--install-guard" in argv:
        deny = os.path.join(ws, ".private", "deny.txt")
        hook = os.path.join(TOOL, ".git", "hooks", "pre-commit")
        if not os.path.isdir(os.path.dirname(hook)):
            print("  ⚠ this tool is not a git checkout; no guard to install")
        elif not os.path.exists(deny):
            print(f"  ⚠ {deny} does not exist; write it first (one identifier per line)")
        else:
            open(hook, "w", encoding="utf-8").write(GUARD.replace("__DENY__", deny))
            os.chmod(hook, os.stat(hook).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print(f"  → pre-commit guard installed, reading {deny}")

    if check:
        return 0
    for name in ("README.md", "README.zh.md"):
        if markers(ws, name):
            print(f"  → {name}: the page and fault counts it states follow the tool")
    rb = os.path.join(ws, ".claude", "skills", "update-dashboard", "scripts", "rebuild.py")
    if os.path.isdir(os.path.join(ws, "findata")) and os.path.exists(rb):
        print()
        subprocess.run([sys.executable, rb, ws, "--write"], check=False)
    else:
        print("  (no findata/ yet — say \"set this up\" in the workspace to run the setup skill)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

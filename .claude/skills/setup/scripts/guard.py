#!/usr/bin/env python3
"""guard.py — a commit that would carry someone's own money into a remote is refused.

The tool is a public repository, and the easiest way to make it yours is to clone it and run the
setup in the clone. From then on the clone's findata/ is real — every balance, every purchase —
and it is still tracked, because the demo's findata/ is. One `git commit -a` and a push, and it is
on the internet (a first user came within a click of it, 2026-10). Setup adds the data folders to
`.gitignore`, but a tracked file stays tracked whatever `.gitignore` says, so that alone stops
nothing. This does:

    python3 .claude/skills/setup/scripts/guard.py              # the pre-commit check (exit 1 = refused)
    python3 .claude/skills/setup/scripts/guard.py --install    # put it in this checkout's pre-commit hook

A staged file under one of DATA is refused when the workspace is not the demo (profile.json has
no `demo: true`) and the repository has any remote. Whether a remote is public cannot be known
without asking it, and a private one is still somebody else's server, so any remote counts.
The demo's own data, which the tool ships on purpose, passes.
"""
import json
import os
import stat
import subprocess
import sys

DATA = ("findata/", "inbox/", "archive/", "dashboards/", "decisions/", "OWNER.md", ".private/")
PROFILES = ("findata/register/profile.json", "findata/profile.json")
MARK = "# jade-toad data guard"
LINE = MARK + '\npython3 "$(git rev-parse --show-toplevel)/.claude/skills/setup/scripts/guard.py" || exit 1\n'


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def is_demo(repo):
    """The demo, judged on what is being committed: the staged profile.json, else the one on disk."""
    for p in PROFILES:
        staged = git(repo, "show", ":" + p)
        text = staged.stdout if staged.returncode == 0 else None
        if text is None and os.path.exists(os.path.join(repo, p)):
            text = open(os.path.join(repo, p), encoding="utf-8").read()
        if text is not None:
            try:
                return bool(json.loads(text).get("demo"))
            except ValueError:
                return False
    return False


def check(repo):
    """(refused files, remotes). Deletions carry no data and pass."""
    remotes = [r for r in git(repo, "remote").stdout.split() if r]
    if not remotes or is_demo(repo):
        return [], remotes
    staged = git(repo, "diff", "--cached", "--name-only", "--diff-filter=d", "-z").stdout
    files = [f for f in staged.split("\0") if f]
    return [f for f in files if f.startswith(DATA)], remotes


def install(repo):
    """Add the check to the checkout's pre-commit hook, keeping whatever hook is there."""
    r = git(repo, "rev-parse", "--git-path", "hooks")
    if r.returncode != 0:
        return None                       # not a git checkout: nothing to guard
    hooks = r.stdout.strip()
    hooks = hooks if os.path.isabs(hooks) else os.path.join(repo, hooks)
    os.makedirs(hooks, exist_ok=True)
    hook = os.path.join(hooks, "pre-commit")
    old = open(hook, encoding="utf-8").read() if os.path.exists(hook) else ""
    if MARK in old:
        return hook
    if old.startswith("#!"):
        head, _, rest = old.partition("\n")
        new = head + "\n" + LINE + rest
    else:
        new = "#!/bin/sh\n" + LINE + old
    open(hook, "w", encoding="utf-8").write(new)
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return hook


def main(argv):
    repo = git(os.getcwd(), "rev-parse", "--show-toplevel").stdout.strip() or os.getcwd()
    if "--install" in argv:
        hook = install(repo)
        print(f"  → data guard in {hook}" if hook else "  · not a git checkout; no guard to install")
        return 0
    bad, remotes = check(repo)
    if not bad:
        return 0
    for f in bad[:20]:
        print(f"  ✗ [G1] {f}: your own data, staged for a repository with a remote ({', '.join(remotes)})")
    if len(bad) > 20:
        print(f"  ✗ [G1] … and {len(bad) - 20} more")
    print("data guard: nothing committed. Unstage them (git restore --staged findata dashboards OWNER.md);"
          " your data stays on this computer.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

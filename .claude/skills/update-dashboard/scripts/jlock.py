"""jlock.py — one writer at a time, for both doors.

A lock file in the workspace (`.jade.lock`: pid, verb, since), taken with O_EXCL so two
processes cannot both think they have it, and stale when its pid is dead. The local app takes
it around every verb it runs; the core's own writers — update, confirm, balance, the wizard —
refuse to write while another live process holds it, so an import started in this chat cannot
run under one the app is running, or the other way round (2026-11-07; until then the lock was
the server's alone). The same pid may re-enter: the app calls the core in-process.
"""
import datetime
import json
import os

NAME = ".jade.lock"


def _alive(pid):
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError, TypeError):
        return False
    return True


def path(root):
    return os.path.join(os.path.abspath(root), NAME)


def holder(root):
    """{pid, verb, since} of a live holder, or None (a dead holder's file is removed)."""
    try:
        h = json.load(open(path(root), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not _alive(h.get("pid")):
        try:
            os.remove(path(root))
        except OSError:
            pass
        return None
    return h


def held_by_other(root):
    """The verb another live process is running, or None. The same pid is not 'other'."""
    h = holder(root)
    if h and h.get("pid") != os.getpid():
        return h.get("verb") or "something"
    return None


def acquire(root, verb):
    """Take the lock for this pid; returns the other holder's verb when it cannot."""
    other = held_by_other(root)
    if other:
        return other
    if holder(root):           # ours already: re-entered
        return None
    try:
        fd = os.open(path(root), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return held_by_other(root) or "something"
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump({"pid": os.getpid(), "verb": verb, "since": datetime.datetime.now().isoformat(timespec="seconds")}, fh)
    return None


def release(root):
    try:
        if (json.load(open(path(root), encoding="utf-8")) or {}).get("pid") == os.getpid():
            os.remove(path(root))
    except (OSError, ValueError):
        pass


def refusal(other):
    return f"  ✗ {other} is running in another window (the local app, or this chat) — wait for it, then run again. Nothing was written."

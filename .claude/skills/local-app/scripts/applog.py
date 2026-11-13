"""applog.py — the app's own log, and the error an owner can copy.

Two things the first full run on a fresh account showed missing (2026-11-12, user 001):

**A system log.** The workspace's log (.jade/log/app.log) starts only once there is a folder,
so a first launch that failed left nothing to read. This one is the computer's, where its other
logs are, from the first line of a launch:

    macOS    ~/Library/Logs/FIRE Toad/firetoad.log      (Console.app shows it)
    Windows  %LOCALAPPDATA%/FIRE Toad/Logs/firetoad.log
    Linux    ~/.local/state/FIRE Toad/firetoad.log

It records what the app did — started (version, system), installed itself, which folder, a
verb begun and how it ended, opened again, quit — and every failure with its code and
traceback. It never records what a run printed: those lines carry amounts and merchants, and
stay in the workspace. One megabyte, three files kept.

**An error with a code.** A run that stops is said as `FT-<VERB>-<WHAT>` with the run's id:
`FT-SETUP-KeyError (3fa9c1d2)`, `FT-IMPORT-STOPPED (…)`. The code names where and what, the id
finds the run in the log. `report()` builds the block the panel shows and the owner copies:
the version, the system, the time, the code, one line of what happened, the run's own ✗ lines
and where the log is.
"""
import datetime
import logging
import logging.handlers
import os
import platform
import sys

APP_NAME = "FIRE Toad"
log = logging.getLogger("jade")          # server.py's "jade.app" is its child: one line, both logs
_ready = False


def log_dir():
    home = os.path.expanduser("~")
    if sys.platform == "darwin":
        return os.path.join(home, "Library", "Logs", APP_NAME)
    if sys.platform.startswith("win"):
        return os.path.join(os.environ.get("LOCALAPPDATA") or home, APP_NAME, "Logs")
    return os.path.join(os.environ.get("XDG_STATE_HOME") or os.path.join(home, ".local", "state"), APP_NAME)


def log_path():
    return os.path.join(log_dir(), "firetoad.log")


def shown_path():
    """The log's place as an owner reads it: ~ for the home folder."""
    return log_path().replace(os.path.expanduser("~"), "~", 1)


def system():
    if sys.platform == "darwin":
        return "macOS " + (platform.mac_ver()[0] or "?")
    return f"{platform.system()} {platform.release()}"


def setup(version=None, frozen=False):
    """Attach the system log once. A log that cannot be written must never stop the app."""
    global _ready
    if _ready:
        return log
    _ready = True
    log.setLevel(logging.INFO)
    try:
        os.makedirs(log_dir(), exist_ok=True)
        h = logging.handlers.RotatingFileHandler(log_path(), maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        log.addHandler(h)
    except OSError:
        log.addHandler(logging.NullHandler())
    log.info("started: %s %s (%s), %s, Python %s", APP_NAME, version or "?", "app" if frozen else "script",
             system(), platform.python_version())
    return log


def code(verb, what):
    """`FT-SETUP-KeyError`: the verb that ran and what stopped it — an exception's type, or
    STOPPED when the run ended by itself without writing."""
    return f"FT-{(verb or 'app').upper()}-{what}"


def report(verb, run_id, what, message, lines=(), version=None, now=None):
    """What a failed run shows and what the owner copies. `lines` are the run's own lines; only
    the ones marked ✗ go in, at most ten, each cut to 300 characters."""
    c = code(verb, what)
    now = now or datetime.datetime.now()
    marked = [l.strip()[:300] for l in lines if "✗" in l][-10:]
    text = "\n".join([f"{APP_NAME} {version or '?'} · {system()} · {now:%Y-%m-%d %H:%M}",
                      f"Error {c} ({run_id})", message.strip()[:300]]
                     + (["---"] + marked if marked else [])
                     + [f"Log: {shown_path()}"])
    log.error("%s (%s): %s", c, run_id, message.strip()[:300])
    return {"code": c, "id": run_id, "message": message.strip()[:300], "text": text, "log": shown_path()}

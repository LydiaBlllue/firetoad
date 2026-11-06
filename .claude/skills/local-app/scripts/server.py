#!/usr/bin/env python3
"""server.py — the second front door: the dashboard and the monthly panel, served on 127.0.0.1.

Claude Code is one way into a workspace; this is the other (ROADMAP 2.0.0, decided 2026-11-05).
It is a standard-library HTTP server with no financial logic of its own: every endpoint is one
call into a script that already exists — status.run(), update.run(), update.undo(),
confirm.run() — and returns what that script returns. If the app can do something Claude cannot,
or the reverse, that is a bug; the selftest imports the same month through both doors and expects
the same findata/.

    python3 app.py                         # the usual way in (app.py finds the workspace, opens the browser)
    python3 .claude/skills/local-app/scripts/server.py <workspace> [--port N]

What it keeps:

  one core        imports the scripts as modules; never a shell, never a user string in a command
  one writer      a lock file in the workspace (.jade.lock: pid, verb, since); a second import or
                  save while one runs gets 409 with the running verb
  loopback only   binds 127.0.0.1; a per-launch token in the path (/t/<token>/…), so a page on
                  another local port cannot call the API; a wrong token is 404, not 401 — nothing
                  to probe; an Origin header, when sent, has to be this server's own
  no back-edges   the page still reads nothing at runtime; the one interaction added is
                  write → rebuild → reload, and the rebuild is the core's, not the server's
  it goes quiet   the panel pings every 30 s; five minutes without one, and no verb running, and
                  the server exits — closing the tab is how it is closed

Routes (every API answer is {"ok": bool, "data" | "error": …, "took": seconds}):

  GET  /                   the built dashboard, the static file it is
  GET  /panel              the monthly panel: Bring · Import · Questions · Result (panel.py)
  GET  /api/status         status.run()                 the panel's rows
  GET  /api/questions      confirm.run()                the open items, numbered as confirm sees them
  POST /api/import         update.run(write=…)          starts the import as a job; lines on /api/events
  POST /api/answers        confirm.run(write, ok, sets) {"set": {"<n>": "<answer>"}}; rebuilds
  POST /api/undo           update.undo()                the last write back
  POST /api/inbox          (multipart)                  files dropped on the panel, saved to inbox/ under
                                                        their own names and named by preflight; nothing parsed
  POST /api/balance        balance.run(key, amount, asof, write) a balance no file carries; rebuilds
  POST /api/ocr            ocr.read(image, capture)     (multipart: key + image) the amounts Vision sees on a
                                                        screenshot, ranked by the account's capture line —
                                                        candidates only; the image is kept under .jade/shots/
  POST /api/open-inbox     —                            opens the inbox folder in the file manager
  GET  /api/setup          wizard.state()               the setup screens, drafted from inbox/ (demo folders)
  POST /api/setup          wizard.apply(answers, write) the answers file, scaffold, rebuild, first import (a job)
  GET  /api/tool           —                            how the folder's copy of the tool compares with the
                                                        app's (app.py tool_state: same / differs / newer)
  POST /api/sync           tools/sync.py                refreshes the folder's copy from the app's (a job)
  GET  /api/events         server-sent events of the running job: line / done
  GET  /api/job            the running or last job: its lines so far and, when done, its result
  GET  /api/ping           keeps the server alive

Errors from the core are returned whole (the exception's name and text) and logged to
.jade/log/app.log in the workspace, so the owner can send that file.
"""
import argparse
import datetime as dt
import email.parser
import email.policy
import html
import http.server
import json
import logging
import os
import queue
import re
import secrets
import subprocess
import sys
import threading
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
for d in ("update-dashboard", "monthly-import", "fetch-statements", "local-app", "setup"):
    sys.path.insert(0, os.path.join(SKILLS, d, "scripts"))
import balance  # noqa: E402
import confirm  # noqa: E402
import fetch  # noqa: E402  find_root
import ocr  # noqa: E402
import panel  # noqa: E402
import preflight  # noqa: E402  names a dropped file
import rebuild  # noqa: E402  MAIN_NAMES
import status  # noqa: E402
import update  # noqa: E402
import verbs  # noqa: E402
import wizard  # noqa: E402  the setup as screens

PING_EVERY = 30          # seconds between the page's pings
IDLE_EXIT = 300          # seconds without a ping before the server exits
MAX_BODY = 1 << 20       # a JSON body larger than this is refused
MAX_UPLOAD = 64 << 20    # and a multipart one larger than this (a month of statements is a few MB)
IMAGES = (".png", ".jpg", ".jpeg", ".heic", ".webp")
LOCK_NAME = ".jade.lock"

log = logging.getLogger("jade.app")


# ---------------------------------------------------------------- the lock
def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError, TypeError):
        return False
    return True


class Lock:
    """The one writer. A file in the workspace with pid, verb and time; taken with O_EXCL so two
    processes cannot both think they have it. A lock whose pid is dead is stale and is taken over."""

    def __init__(self, root):
        self.path = os.path.join(root, LOCK_NAME)

    def holder(self):
        try:
            h = json.load(open(self.path, encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not pid_alive(h.get("pid")):
            try:
                os.remove(self.path)
            except OSError:
                pass
            return None
        return h

    def acquire(self, verb):
        """The verb now running under the lock, or None when this call took it."""
        held = self.holder()
        if held:
            return held.get("verb") or "something"
        try:
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            held = self.holder()
            return (held or {}).get("verb") or "something"
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"pid": os.getpid(), "verb": verb, "since": dt.datetime.now().isoformat(timespec="seconds")}, fh)
        return None

    def release(self):
        try:
            if (json.load(open(self.path, encoding="utf-8")) or {}).get("pid") == os.getpid():
                os.remove(self.path)
        except (OSError, ValueError):
            pass


# ---------------------------------------------------------------- the job
class Job:
    """One verb running in a thread, its lines kept as they come, its result when done. The page
    reads the lines on /api/events (or /api/job) — the same lines the CLI prints, from the same
    run(), captured through `say`. There is at most one job at a time; the lock sees to it."""

    def __init__(self, verb, write):
        self.id = secrets.token_hex(4)
        self.verb, self.write = verb, write
        self.lines, self.result, self.error = [], None, None
        self.done = threading.Event()
        self.started = time.monotonic()
        self.waiters = []
        self.guard = threading.Lock()

    def say(self, text="", **_):
        with self.guard:
            self.lines.append(text)
            for q in self.waiters:
                q.put(("line", text))

    def finish(self, result=None, error=None):
        self.result, self.error = result, error
        with self.guard:
            for q in self.waiters:
                q.put(("done", None))
        self.done.set()

    def follow(self):
        """A queue that replays the lines so far and then receives the rest, for one SSE client."""
        q = queue.Queue()
        with self.guard:
            for l in self.lines:
                q.put(("line", l))
            if self.done.is_set():
                q.put(("done", None))
            else:
                self.waiters.append(q)
        return q

    def public(self):
        out = {"id": self.id, "verb": self.verb, "write": self.write, "lines": list(self.lines),
               "done": self.done.is_set(), "seconds": round(time.monotonic() - self.started, 1)}
        if self.result is not None:
            out["result"] = self.result
        if self.error is not None:
            out["error"] = self.error
        return out


# ---------------------------------------------------------------- the app
class App:
    def __init__(self, root, token=None, tool=None, tool_hooks=None):
        self.root = os.path.abspath(root)
        self.token = token or secrets.token_urlsafe(18)
        # how the folder's copy of the tool compares with the app's (app.py tool_state), and the
        # two calls that re-read it and refresh it; None when started bare (server.py <ws>)
        self.tool = tool
        self.tool_hooks = tool_hooks or {}
        self.lock = Lock(self.root)
        self.job = None
        self.last_ping = time.monotonic()
        self.port = None
        self.httpd = None
        self._setup_log()

    def _setup_log(self):
        d = os.path.join(self.root, ".jade", "log")
        os.makedirs(d, exist_ok=True)
        if not log.handlers:
            h = logging.FileHandler(os.path.join(d, "app.log"), encoding="utf-8")
            h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            log.addHandler(h)
            log.setLevel(logging.INFO)

    @property
    def base(self):
        return f"/t/{self.token}"

    def dashboard(self):
        for n in rebuild.MAIN_NAMES:
            p = os.path.join(self.root, "dashboards", n)
            if os.path.exists(p):
                return p
        return None

    # -- verbs: each one call into the core ---------------------------------------------------
    def start_job(self, verb, write, fn):
        """Run `fn(say)` under the lock in a thread. 409 (as a tuple) when something runs, or when
        the folder's data is a newer shape than this app builds (then nothing may be written)."""
        if self.job is not None and not self.job.done.is_set():
            return None, self.job.verb
        if write and verb != "sync" and self.tool and self.tool.get("state") == "newer":
            return None, "nothing (this folder's data is newer than the app — update the app first)"
        held = self.lock.acquire(verb)
        if held:
            return None, held
        job = Job(verb, write)
        self.job = job

        def go():
            try:
                job.finish(result=fn(job.say))
            except BaseException as e:  # a core failure reaches the panel whole, never a dead page
                log.exception("%s failed", verb)
                job.say(f"  ✗ {type(e).__name__}: {e}", loud_line=True)
                job.finish(error={"type": type(e).__name__, "text": str(e)})
            finally:
                self.lock.release()
        threading.Thread(target=go, name=f"jade-{verb}", daemon=True).start()
        return job, None

    def do_status(self):
        return verbs.public(status.run(self.root))

    def do_questions(self):
        return verbs.public(confirm.run(self.root))

    def do_import(self, write):
        return self.start_job("import", bool(write),
                              lambda say: verbs.public(update.run(self.root, write=bool(write), say=say, loud=say)))

    def do_undo(self):
        return self.start_job("undo", True, lambda say: verbs.public(update.undo(self.root, say=say)))

    def do_answers(self, sets):
        """The questions card's Save answers: every selection at once, confirm's way (n=answer)."""
        if not isinstance(sets, dict):
            raise ValueError("set has to be an object of {n: answer}")
        args = [f"{n}={v}" for n, v in sets.items() if str(v).strip()]
        return self.start_job("answers", True,
                              lambda say: verbs.public(confirm.run(self.root, write=True, ok=True, sets=args, say=say)))

    def do_balance(self, key, amount, asof):
        if not key or amount in (None, ""):
            raise ValueError("key and amount are needed")
        return self.start_job("balance", True,
                              lambda say: verbs.public(balance.run(self.root, str(key), amount, asof=asof or None, write=True, say=say)))

    def save_inbox(self, parts):
        """Files dropped on the panel: into inbox/ under their own (base)names, then named the way
        preflight names them. A file already there, byte for byte, is said so and not written
        twice; a different file under the same name is refused rather than overwritten."""
        inbox = os.path.join(self.root, "inbox")
        os.makedirs(inbox, exist_ok=True)
        preflight.ROOT = self.root
        preflight.DOCS = preflight.load_docs(self.root)
        out = []
        for name, data in parts:
            name = safe_name(name)
            if not name:
                out.append({"name": name, "state": "refused", "why": "no usable filename"}); continue
            dest = os.path.join(inbox, name)
            if os.path.exists(dest):
                if open(dest, "rb").read() == data:
                    out.append({"name": name, "state": "already there", "label": preflight.classify(name)[0]}); continue
                out.append({"name": name, "state": "refused", "why": "a different file of that name is already in inbox"}); continue
            with open(dest, "wb") as fh:
                fh.write(data)
            label, _a, _into, note = preflight.classify(name)
            out.append({"name": name, "state": "saved", "label": label, "note": None if label else note})
        log.info("inbox: %s", [(o["name"], o["state"]) for o in out])
        return out

    def do_ocr(self, key, name, data):
        """A screenshot for one account: kept under .jade/shots/, read, the candidates returned.
        Writes nothing to findata/; the owner picks, and /api/balance writes."""
        reg = json.load(open(os.path.join(self.root, "findata", "register", "accounts.json"), encoding="utf-8")) \
            if os.path.exists(os.path.join(self.root, "findata", "register", "accounts.json")) else {}
        acc = next((a for a in reg.get("accounts", []) if a.get("key") == key), None)
        if acc is None:
            raise ValueError(f"no account with key {key!r}")
        ext = os.path.splitext(safe_name(name) or "")[1].lower() or ".png"
        if ext not in IMAGES:
            raise ValueError("not an image")
        shots = os.path.join(self.root, ".jade", "shots")
        os.makedirs(shots, exist_ok=True)
        path = os.path.join(shots, f"{re.sub(r'[^A-Za-z0-9_-]', '_', key)}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}{ext}")
        with open(path, "wb") as fh:
            fh.write(data)
        r = ocr.read(path, acc.get("capture"))
        r.update(key=key, capture=acc.get("capture"), shot=os.path.relpath(path, self.root))
        return r

    def open_inbox(self):
        """The inbox folder in the file manager: a fixed command with one fixed argument, no shell."""
        inbox = os.path.join(self.root, "inbox")
        os.makedirs(inbox, exist_ok=True)
        if sys.platform == "darwin":
            subprocess.Popen(["open", inbox])
        elif sys.platform.startswith("win"):
            os.startfile(inbox)  # noqa: S606  (Windows only)
        else:
            subprocess.Popen(["xdg-open", inbox])
        return {"inbox": inbox}

    def is_demo(self):
        return wizard.is_demo(self.root)

    def do_setup_state(self):
        return verbs.public(wizard.state(self.root))

    def do_setup(self, answers):
        if not isinstance(answers, dict):
            raise ValueError("answers has to be an object")
        return self.start_job("setup", True, lambda say: verbs.public(wizard.apply(self.root, answers, write=True, say=say)))

    def do_sync(self):
        """The folder's copy of the tool refreshed from the app's, then the state re-read."""
        if "refresh" not in self.tool_hooks:
            raise ValueError("this server was started without an app copy to refresh from")

        def go(say):
            rc, out = self.tool_hooks["refresh"]()
            for l in out.splitlines():
                say(l)
            self.tool = self.tool_hooks["state"]()
            return {"rc_sync": rc, "tool": self.tool}
        return self.start_job("sync", True, go)

    def last_import(self):
        try:
            recs = json.load(open(os.path.join(self.root, "findata", "history", "imports.json"), encoding="utf-8"))
        except (OSError, ValueError):
            return None
        recs = recs.get("imports") if isinstance(recs, dict) else recs
        return recs[-1] if recs else None

    def idle_watch(self):
        while True:
            time.sleep(PING_EVERY)
            busy = self.job is not None and not self.job.done.is_set()
            if not busy and time.monotonic() - self.last_ping > IDLE_EXIT:
                log.info("no ping for %ss; exiting", IDLE_EXIT)
                threading.Thread(target=self.httpd.shutdown, daemon=True).start()
                return


def safe_name(name):
    """A dropped file's name as a bare basename: no path, no leading dot, no control characters."""
    n = os.path.basename((name or "").replace("\\", "/")).strip()
    n = re.sub(r"[\x00-\x1f\x7f]", "", n)
    if not n or n.startswith(".") or n in ("README.txt",):
        return ""
    return n[:180]


def multipart(ctype, body):
    """[(filename, bytes)] for the file parts and {field: text} for the rest of a form."""
    msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
        b"Content-Type: " + ctype.encode("latin-1") + b"\r\nMIME-Version: 1.0\r\n\r\n" + body)
    files, fields = [], {}
    if not msg.is_multipart():
        raise ValueError("expected multipart/form-data")
    for part in msg.iter_parts():
        fn = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if fn:
            files.append((fn, payload))
        else:
            fields[part.get_param("name", header="content-disposition") or ""] = payload.decode("utf-8", "replace")
    return files, fields


# ---------------------------------------------------------------- HTTP
class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "JadeToad/1"
    app = None  # set by serve()

    def log_message(self, fmt, *args):   # the access log is noise; failures are logged by the app
        pass

    # -- plumbing
    def _route(self):
        """(path under the token, query) — or None when the token is missing or wrong."""
        u = urllib.parse.urlsplit(self.path)
        base = self.app.base
        if u.path == base or u.path.startswith(base + "/"):
            return u.path[len(base):] or "/", urllib.parse.parse_qs(u.query)
        return None, None

    def _origin_ok(self):
        o = self.headers.get("Origin")
        return o is None or o == f"http://127.0.0.1:{self.app.port}"

    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=()):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _json(self, code, ok, payload, t0):
        body = {"ok": ok, ("data" if ok else "error"): payload, "took": round(time.monotonic() - t0, 3)}
        self._send(code, json.dumps(body, ensure_ascii=False), "application/json; charset=utf-8")

    def _not_found(self):
        self._send(404, "<!doctype html><title>404</title><p>Not found.", "text/html; charset=utf-8")

    def _body(self):
        """A JSON object, or, for multipart/form-data, {"files": [(name, bytes)], "fields": {...}}."""
        n = int(self.headers.get("Content-Length") or 0)
        ctype = self.headers.get("Content-Type") or ""
        if ctype.startswith("multipart/form-data"):
            if n > MAX_UPLOAD:
                raise ValueError("upload too large")
            files, fields = multipart(ctype, self.rfile.read(n) if n else b"")
            return {"files": files, "fields": fields}
        if n > MAX_BODY:
            raise ValueError("request too large")
        raw = self.rfile.read(n) if n else b""
        if not raw:
            return {}
        obj = json.loads(raw.decode("utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("the body has to be a JSON object")
        return obj

    # -- GET
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        app = self.app
        path, q = self._route()
        if path is None:
            return self._not_found()
        app.last_ping = time.monotonic()
        t0 = time.monotonic()
        try:
            if path == "/":
                p = app.dashboard()
                if not p:
                    return self._send(200, panel.no_dashboard(app.base), "text/html; charset=utf-8")
                return self._send(200, open(p, "rb").read())
            if path == "/panel" and app.is_demo():
                return self._send(200, panel.render_setup(app.base, app.root, app.do_setup_state(),
                                                          app.job.public() if app.job else None, app.tool),
                                  extra=[("Content-Security-Policy",
                                          "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                                          "connect-src 'self'; img-src data:; base-uri 'none'; form-action 'none'")])
            if path == "/panel":
                return self._send(200, panel.render(app.base, app.root, app.do_status(), app.do_questions(),
                                                    app.last_import(), app.job.public() if app.job else None,
                                                    app.lock.holder(), app.tool),
                                  extra=[("Content-Security-Policy",
                                          "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                                          "connect-src 'self'; img-src data:; base-uri 'none'; form-action 'none'")])
            if path == "/api/ping":
                return self._json(200, True, {"job": app.job.public() if app.job else None}, t0)
            if path == "/api/status":
                return self._json(200, True, app.do_status(), t0)
            if path == "/api/questions":
                return self._json(200, True, app.do_questions(), t0)
            if path == "/api/job":
                return self._json(200, True, app.job.public() if app.job else None, t0)
            if path == "/api/tool":
                return self._json(200, True, app.tool, t0)
            if path == "/api/setup":
                return self._json(200, True, app.do_setup_state(), t0)
            if path == "/api/events":
                return self._events()
            return self._not_found()
        except Exception as e:  # noqa: BLE001  one page, one error, never a dead socket
            log.exception("GET %s", path)
            return self._json(500, False, {"type": type(e).__name__, "text": str(e)}, t0)

    def _events(self):
        job = self.app.job
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if job is None:
            self.wfile.write(b"event: done\ndata: {}\n\n"); self.wfile.flush(); return
        q = job.follow()
        try:
            while True:
                try:
                    kind, text = q.get(timeout=15)
                except queue.Empty:
                    self.wfile.write(b": keep-alive\n\n"); self.wfile.flush(); continue
                if kind == "done":
                    self.wfile.write(("event: done\ndata: " + json.dumps(job.public(), ensure_ascii=False) + "\n\n").encode("utf-8"))
                    self.wfile.flush()
                    return
                self.wfile.write(("event: line\ndata: " + json.dumps(text, ensure_ascii=False) + "\n\n").encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return

    # -- POST
    def do_POST(self):
        app = self.app
        path, _ = self._route()
        if path is None:
            return self._not_found()
        t0 = time.monotonic()
        if not self._origin_ok():
            return self._json(403, False, {"type": "Origin", "text": "not this server's page"}, t0)
        app.last_ping = time.monotonic()
        try:
            body = self._body()
            if path == "/api/import":
                job, busy = app.do_import(body.get("write", False))
            elif path == "/api/undo":
                job, busy = app.do_undo()
            elif path == "/api/answers":
                job, busy = app.do_answers(body.get("set") or {})
            elif path == "/api/balance":
                job, busy = app.do_balance(body.get("key"), body.get("amount"), body.get("asof"))
            elif path == "/api/inbox":
                return self._json(200, True, app.save_inbox(body.get("files") or []), t0)
            elif path == "/api/ocr":
                files = body.get("files") or []
                if not files:
                    raise ValueError("no image in the upload")
                return self._json(200, True, app.do_ocr((body.get("fields") or {}).get("key"), files[0][0], files[0][1]), t0)
            elif path == "/api/open-inbox":
                return self._json(200, True, app.open_inbox(), t0)
            elif path == "/api/sync":
                job, busy = app.do_sync()
            elif path == "/api/setup":
                job, busy = app.do_setup(body.get("answers") or {})
            else:
                return self._not_found()
            if busy:
                return self._json(409, False, {"type": "Busy", "text": f"{busy} is running; wait for it", "verb": busy}, t0)
            return self._json(202, True, job.public(), t0)
        except ValueError as e:
            return self._json(400, False, {"type": "BadRequest", "text": str(e)}, t0)
        except Exception as e:  # noqa: BLE001
            log.exception("POST %s", path)
            return self._json(500, False, {"type": type(e).__name__, "text": str(e)}, t0)


def serve(root, port=0, token=None, ready=None, tool=None, tool_hooks=None):
    """Start the server on 127.0.0.1:<port> (0 = a free one) and block until it exits. `ready`,
    when given, is called with (url, app) once the socket is bound — app.py opens the browser from
    it; `tool` and `tool_hooks` are app.py's view of the folder's tool copy (None when bare)."""
    app = App(root, token, tool, tool_hooks)
    handler = type("Handler", (Handler,), {"app": app})
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    httpd.daemon_threads = True
    app.httpd, app.port = httpd, httpd.server_address[1]
    url = f"http://127.0.0.1:{app.port}{app.base}/panel"
    log.info("serving %s on %s", app.root, url)
    threading.Thread(target=app.idle_watch, name="jade-idle", daemon=True).start()
    if ready:
        ready(url, app)
    try:
        httpd.serve_forever(poll_interval=0.5)
    finally:
        httpd.server_close()
        app.lock.release()
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--port", type=int, default=0, help="0 picks a free port")
    a = ap.parse_args(argv)
    root = fetch.find_root(a.root)
    if not root:
        print("✗ no workspace here (looked upward for findata/ and dashboards/)")
        return 2
    return serve(root, a.port, ready=lambda url, app: print(f"  Jade Toad is at {url}", flush=True))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

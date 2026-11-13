#!/usr/bin/env python3
"""app.py — FIRE Toad without Claude: the dashboard and the monthly panel in your browser.

    python3 app.py                # this folder's workspace, a free port, the browser opened
    python3 app.py ~/FireToad     # another workspace
    python3 app.py --choose       # ask for the folder again (it is remembered between launches)
    python3 app.py --no-browser   # print the address instead of opening it

It starts a small server on 127.0.0.1 that only this computer can reach, with a fresh address
each launch, opens the panel in your browser, and exits by itself five minutes after the last
tab is closed. Everything it does — the import, the answers, the rebuild — is the same code the
Claude Code skills run; this is only the second door to it (ROADMAP 2.0.0;
.claude/skills/local-app/scripts/server.py has the routes).

Packaged (build/build.py makes a double-clickable app with Python inside), the same file is the
app's entry: the first launch asks where your FIRE Toad folder is — or makes one — and remembers
it in the system's application-support folder, never in the workspace. On every launch it
compares the folder's copy of the tool with its own and offers to refresh the copy, so a folder
used through both doors runs one version; a folder whose data is newer than the app is shown
and not written to.
"""
import argparse
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = bool(getattr(sys, "frozen", False))
# where the tool's own copy lives: beside this file, or inside the packaged app
TOOL = getattr(sys, "_MEIPASS", HERE) if FROZEN else HERE
APP_NAME = "FIRE Toad"


def _run_script_mode():
    """Inside the packaged app there is no `python3`, and the core runs its own scripts as
    `sys.executable <script.py> args` (rebuild after an import, the money checks, --reseed).
    So the app's binary doubles as the interpreter: called with a .py file first, it runs that
    file as __main__ with the rest of the arguments and exits with its code. Only a file that
    exists is run, and only when the first argument ends in .py — nothing else is interpreted."""
    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        code = e.code
        sys.exit(0 if code is None else (code if isinstance(code, int) else 1))
    sys.exit(0)


if FROZEN and len(sys.argv) > 1 and sys.argv[1].endswith(".py") and os.path.isfile(sys.argv[1]):
    _run_script_mode()

for d in ("local-app", "fetch-statements"):
    sys.path.insert(0, os.path.join(TOOL, ".claude", "skills", d, "scripts"))
sys.path.insert(0, os.path.join(TOOL, "tools"))


# ---------------------------------------------------------------- remembered settings
def support_dir():
    """The system's application-support folder for this app — outside every workspace."""
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, APP_NAME)


LEGACY_NAMES = ("Jade Toad",)   # what the app was called before; its settings come along (2026-11-12)


def settings_path():
    """settings.json in this app's folder. The first launch under a new name finds the old
    folder's settings and copies them over (the old ones stay), so the folder the owner chose
    is still the one that opens."""
    p = os.path.join(support_dir(), "settings.json")
    if not os.path.exists(p):
        for old in LEGACY_NAMES:
            q = os.path.join(os.path.dirname(support_dir()), old, "settings.json")
            if os.path.exists(q):
                os.makedirs(os.path.dirname(p), exist_ok=True)
                shutil.copyfile(q, p)
                break
    return p


def load_settings():
    try:
        return json.load(open(settings_path(), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_settings(s):
    os.makedirs(support_dir(), exist_ok=True)
    tmp = settings_path() + ".tmp"
    json.dump(s, open(tmp, "w", encoding="utf-8"), indent=2)
    os.replace(tmp, settings_path())


def remember(ws):
    s = load_settings()
    s["workspace"] = ws
    recent = [ws] + [r for r in s.get("recent", []) if r != ws]
    s["recent"] = recent[:5]
    save_settings(s)


# ---------------------------------------------------------------- the folder
def is_workspace(p):
    return bool(p) and os.path.isdir(os.path.join(p, "findata")) and os.path.isdir(os.path.join(p, "dashboards"))


def ask_folder(prompt):
    """A folder dialog with the system's own means: AppleScript on macOS, PowerShell on Windows,
    a typed path elsewhere. Fixed scripts; the prompt is the only text and it is this file's."""
    if sys.platform == "darwin":
        r = subprocess.run(["osascript", "-e", f'POSIX path of (choose folder with prompt "{prompt}")'],
                           capture_output=True, text=True)
        return (r.stdout.strip().rstrip("/") or None) if r.returncode == 0 else None
    if sys.platform.startswith("win"):
        ps = ("Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; "
              f"$d.Description = '{prompt}'; if ($d.ShowDialog() -eq 'OK') {{ $d.SelectedPath }}")
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
        return (r.stdout.strip() or None) if r.returncode == 0 else None
    try:
        return input(prompt + " ").strip() or None
    except EOFError:
        return None


def ask_choice(text, buttons):
    """One question with two or three buttons; the button's text comes back. macOS has a dialog;
    elsewhere the first button is taken, which is always the safe one."""
    if sys.platform == "darwin":
        text = text.replace("\\", "\\\\").replace('"', '\\"')   # a folder's name can hold a quote
        bl = ", ".join(f'"{b}"' for b in buttons)
        r = subprocess.run(["osascript", "-e", f'button returned of (display dialog "{text}" buttons {{{bl}}} '
                                               f'default button "{buttons[0]}" with title "{APP_NAME}")'],
                           capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    return buttons[0]


def new_folder(parent=None):
    """Where *Create my folder* puts the folder: Documents/FIRE Toad. A name already taken by
    something else becomes FIRE Toad 2, 3, … — never someone's own folder written into. An
    existing FIRE Toad folder or an empty one is used as it is. The owner picks no folder, so
    there is no wrong one to pick (2026-11-12, user 001: a picker let her choose Documents)."""
    parent = parent or os.path.join(os.path.expanduser("~"), "Documents")
    base = os.path.join(parent, APP_NAME)
    p, n = base, 2
    while os.path.exists(p) and not (os.path.isdir(p) and (is_workspace(p) or not os.listdir(p))):
        p, n = f"{base} {n}", n + 1
    return p


def tell(text):
    """A line the owner sees without having to click it: a notification on macOS, stdout
    elsewhere."""
    print("  " + text, flush=True)
    if sys.platform == "darwin":
        t = text.replace("\\", "\\\\").replace('"', '\\"')
        subprocess.run(["osascript", "-e", f'display notification "{t}" with title "{APP_NAME}"'],
                       capture_output=True)


def make_workspace(dest):
    """A new workspace in an empty (or new) folder: the tool's copy and no one's data. findata/
    holds one file, profile.json, saying which shape the data will take and that the folder is
    not set up yet (`blank`, with `demo` — the word every gate already reads as "nobody's");
    the setup writes the rest from the owner's own files. The demo owner stays in the app and
    on the website, never in somebody's folder (decided 2026-11-08, user 001). sync.py does the
    copying; it never touches a folder that already has findata/ data in it. A folder that
    holds other things gets a FIRE Toad folder inside it instead of an error."""
    import json
    import sync
    if os.path.isdir(dest) and os.listdir(dest) and not is_workspace(dest):
        dest = new_folder(dest)
    os.makedirs(dest, exist_ok=True)
    prof = os.path.join(dest, "findata", "register", "profile.json")
    if not os.path.exists(prof):
        os.makedirs(os.path.dirname(prof), exist_ok=True)
        os.makedirs(os.path.join(dest, "dashboards"), exist_ok=True)
        with open(prof, "w", encoding="utf-8") as f:
            json.dump({"schema": sync.tool_schema(), "demo": True, "blank": True}, f, indent=2)
            f.write("\n")
    sync.main(["sync.py", dest])
    return dest

def find_root(p):
    import fetch
    return fetch.find_root(p)


def choose_workspace(args):
    """The folder to serve, in order: the argument, the remembered one, the folder this file is
    in (when not packaged), then a dialog — open my folder, or create it in Documents."""
    if args.root:
        ws = find_root(args.root)
        if ws:
            return ws
        if args.make:
            return make_workspace(os.path.abspath(args.root))
        raise SystemExit(f"✗ {args.root} is not a FIRE Toad workspace (no findata/ and dashboards/ in it or above it)")
    s = load_settings()
    if not args.choose:
        # `python3 app.py` inside a workspace means that workspace, whatever the packaged app
        # remembered: the two are different doors and must not swap folders under each other
        # (a copy run for a test served the remembered real folder, 2026-11-06).
        if not FROZEN:
            ws = find_root(HERE)
            if ws:
                return ws
        if is_workspace(s.get("workspace")):
            return s["workspace"]
    pick = ask_choice(WELCOME, [CREATE, OPEN, QUIT])
    while True:
        if pick == CREATE:
            ws = make_workspace(new_folder())
            tell(f"Your folder: {ws.replace(os.path.expanduser('~'), '~', 1)} · 你的文件夹")
            return ws
        if pick != OPEN:
            return None
        d = ask_folder("Choose your FIRE Toad folder · 选择你的 FIRE Toad 文件夹")
        if not d:
            return None
        ws = find_root(d)
        if ws:
            return ws
        pick = ask_choice(f"This is not a FIRE Toad folder: {d}\n\n这不是 FIRE Toad 文件夹。",
                          [OPEN_AGAIN, CREATE, QUIT])
        if pick == OPEN_AGAIN:
            pick = OPEN


# the first launch's question, in both languages: no "Make one" (what is "one"? 2026-11-12, user 001)
WELCOME = ("Welcome to FIRE Toad. Everything it keeps is in one folder on this Mac.\n\n"
           "欢迎使用 FIRE Toad。它的所有内容都放在这台 Mac 上的一个文件夹里。")
CREATE, OPEN, OPEN_AGAIN, QUIT = ("Create my folder · 新建文件夹", "Open my folder · 打开文件夹",
                                  "Choose again · 重新选择", "Quit · 退出")


# ---------------------------------------------------------------- the tool's copy
def tool_version():
    """The version the page prints (templates/dashboards/*.html `const VERSION`)."""
    try:
        t = open(os.path.join(TOOL, "templates", "dashboards", "finance_dashboard.html"), encoding="utf-8").read()
        m = re.search(r'const VERSION = "([^"]+)"', t)
        return m.group(1) if m else None
    except OSError:
        return None


def tool_state(ws):
    """How the workspace's copy of the tool compares with this app's: `same`, `differs` (this
    app can refresh it), `migrate` (the folder's data is an older shape; tools/migrate.py first)
    or `newer` (a newer shape than this app builds — the app will not write). sync.py's own
    rules, read without copying anything."""
    import sync
    have, want = sync.workspace_schema(ws), sync.tool_schema()
    changed = []
    for rel in sync.SYNCED:
        if rel == "FINANCE.md":
            continue   # the seam: its figures table is the workspace's own and always differs
        src, dst = os.path.join(TOOL, rel), os.path.join(ws, rel)
        if os.path.exists(src) and sync.differs(src, dst):
            changed.append(rel)
    if have is not None and want is not None and have > want:
        state = "newer"
    elif have is not None and want is not None and have < want:
        state = "migrate"
    else:
        state = "differs" if changed else "same"
    return {"state": state, "changed": changed, "schema": {"workspace": have, "app": want},
            "version": tool_version(), "tool": TOOL, "frozen": FROZEN}


def refresh_tool(ws):
    """sync.py from this app's copy into the workspace, as a subprocess so its prints are its own
    (inside the packaged app sys.executable is this binary, which runs .py files — see above)."""
    r = subprocess.run([sys.executable, os.path.join(TOOL, "tools", "sync.py"), ws], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


# ---------------------------------------------------------------- installing itself
def bundle_path():
    """The .app this binary runs in, or None outside a packaged macOS app."""
    if not (FROZEN and sys.platform == "darwin"):
        return None
    app = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "..", ".."))
    return app if app.endswith(".app") else None


def install_from_disk_image(app=None, apps_dir=None, volumes="/Volumes"):
    """Double-clicked inside the disk image, the app copies itself into Applications, opens the
    copy and quits, and the copy ejects the disk image: one double-click, no drag, and no second
    double-click in Applications (2026-11-12, user 001). Nothing runs when a file is dragged, so
    the disk image asks for a double-click instead.

    macOS may run an app opened from a downloaded disk image from a random read-only place (App
    Translocation), so the original is looked for on the mounted disk by name. Applications when
    this user may write there, else ~/Applications (a Standard account). The copy's quarantine
    flag is cleared: macOS has just checked this notarised app and the owner said Open, and the
    copy is the same signed bundle. Returns the copy's path, or None when there is nothing to do
    or the copy failed (the app then simply runs from where it is)."""
    app = app or bundle_path()
    if not app:
        return None
    if app.startswith(volumes.rstrip("/") + "/"):
        src = app
    elif "/AppTranslocation/" in app:
        src = os.path.join(volumes, APP_NAME, APP_NAME + ".app")
        if not os.path.isdir(src):
            return None
    else:
        return None
    if apps_dir is None:
        apps_dir = "/Applications" if os.access("/Applications", os.W_OK) else os.path.expanduser("~/Applications")
    dest = os.path.join(apps_dir, APP_NAME + ".app")
    tmp = dest + ".installing"
    try:
        os.makedirs(apps_dir, exist_ok=True)
        shutil.rmtree(tmp, ignore_errors=True)
        subprocess.run(["ditto", src, tmp], check=True, capture_output=True)
        subprocess.run(["xattr", "-dr", "com.apple.quarantine", tmp], capture_output=True)
        if os.path.exists(dest):
            shutil.rmtree(dest)                  # an older version: replaced, never two
        os.rename(tmp, dest)
    except (OSError, subprocess.CalledProcessError) as e:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"  · not installed into {apps_dir} ({e}); running from the disk image", flush=True)
        return None
    return dest


def eject_later(vol):
    """Eject the disk image the app was installed from, once the copy in it has quit. Only a
    mounted volume under /Volumes, passed as an argument, never into a shell string."""
    if vol and vol.startswith("/Volumes/") and os.path.isdir(vol):
        subprocess.Popen(["/bin/sh", "-c", 'sleep 3; hdiutil detach -quiet "$1"', "sh", vol],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


# ---------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", help="the workspace folder (default: the remembered one, or this one)")
    ap.add_argument("--port", type=int, default=0, help="0 picks a free port")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--choose", action="store_true", help="ask for the folder even when one is remembered")
    ap.add_argument("--make", action="store_true", help="with a folder: make a new workspace there")
    ap.add_argument("--forget", action="store_true", help="do not remember this folder for next time")
    ap.add_argument("--eject", help=argparse.SUPPRESS)   # the disk image this copy was installed from
    a = ap.parse_args(argv)
    installed = install_from_disk_image()
    if installed:
        here = bundle_path()
        vol = os.path.dirname(here) if here.startswith("/Volumes/") else os.path.join("/Volumes", APP_NAME)
        subprocess.run(["open", "-n", installed, "--args", "--eject", vol])
        return 0
    eject_later(a.eject)
    root = choose_workspace(a)
    if not root:
        return 2
    root = os.path.abspath(root)
    if not a.forget:
        remember(root)
    import server
    tool = tool_state(root)

    def ready(url, app):
        print(f"  {APP_NAME} · {root}\n  {url}\n  (closes by itself five minutes after the last tab is closed; Ctrl-C stops it now)", flush=True)
        if tool["state"] != "same":
            print(f"  the folder's copy of the tool: {tool['state']}" + (f" ({len(tool['changed'])} files)" if tool["changed"] else ""), flush=True)
        if not a.no_browser:
            webbrowser.open(url)
    try:
        return server.serve(root, a.port, ready=ready, tool=tool,
                            tool_hooks={"state": lambda: tool_state(root), "refresh": lambda: refresh_tool(root)})
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

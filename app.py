#!/usr/bin/env python3
"""app.py — Jade Toad without Claude: the dashboard and the monthly panel in your browser.

    python3 app.py                # this folder's workspace, a free port, the browser opened
    python3 app.py ~/JadeToad     # another workspace
    python3 app.py --no-browser   # print the address instead of opening it

It starts a small server on 127.0.0.1 that only this computer can reach, with a fresh address
each launch, opens the panel in your browser, and exits by itself five minutes after the last
tab is closed. Everything it does — the import, the answers, the rebuild — is the same code the
Claude Code skills run; this is only the second door to it (ROADMAP 2.0.0;
.claude/skills/local-app/scripts/server.py has the routes).
"""
import argparse
import os
import sys
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".claude", "skills", "local-app", "scripts"))
sys.path.insert(0, os.path.join(HERE, ".claude", "skills", "fetch-statements", "scripts"))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=HERE, help="the workspace folder (default: this one)")
    ap.add_argument("--port", type=int, default=0, help="0 picks a free port")
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args(argv)
    import fetch
    root = fetch.find_root(a.root)
    if not root:
        print(f"✗ {a.root} is not a Jade Toad workspace (no findata/ and dashboards/ in it or above it)")
        return 2
    import server

    def ready(url, app):
        print(f"  Jade Toad · {root}\n  {url}\n  (closes by itself five minutes after the last tab is closed; Ctrl-C stops it now)", flush=True)
        if not a.no_browser:
            webbrowser.open(url)
    try:
        return server.serve(root, a.port, ready=ready)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

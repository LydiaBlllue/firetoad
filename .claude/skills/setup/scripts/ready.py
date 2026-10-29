"""ready.py — is this computer ready to set up a workspace? The first thing setup runs.

The first person to set this up from scratch had no PDF reader installed and found out halfway,
when every statement came back unread (2026-10-28, first user). This says, before anything is
asked or written, what is missing and the one command that installs it, and what the files in
inbox/ are — so the owner knows up front whether the twenty minutes can start.

    python3 .claude/skills/setup/scripts/ready.py .

Exit 0 when setup can go ahead (an optional tool missing is said, not refused), 1 when it cannot.
"""
import os, sys

MIN = (3, 9)


def main(argv):
    root = os.path.abspath(argv[1]) if len(argv) > 1 else os.getcwd()
    need, ok, nice = [], [], []

    v = sys.version_info
    if (v.major, v.minor) < MIN:
        need.append(f"Python {v.major}.{v.minor} is too old — {MIN[0]}.{MIN[1]} or newer is needed. "
                    "Install the current one from python.org.")
    else:
        ok.append(f"Python {v.major}.{v.minor}")

    try:
        import pypdf                                    # noqa: F401 -- the parsers read PDFs with it
        ok.append("the PDF reader (pypdf)")
    except ImportError:
        need.append("The PDF reader is missing, so no statement can be read. Install it with:\n"
                    f"      {os.path.basename(sys.executable)} -m pip install --user pypdf")

    try:
        import playwright                               # noqa: F401 -- only check_render uses it
        ok.append("the page checker's browser (playwright)")
    except ImportError:
        nice.append("Optional: the check that the page draws at every window size needs playwright. "
                    "Setup works without it.")

    inbox = os.path.join(root, "inbox")
    files = sorted(f for f in os.listdir(inbox) if not f.startswith(".")) if os.path.isdir(inbox) else []
    kinds = {}
    for f in files:
        ext = os.path.splitext(f)[1].lower().lstrip(".") or "other"
        kinds[ext] = kinds.get(ext, 0) + 1

    print("=== ready — can setup start? ===")
    for line in ok:
        print(f"  ✓ {line}")
    for line in need:
        print(f"  ✗ {line}")
    for line in nice:
        print(f"  · {line}")
    if files:
        print(f"  ✓ {len(files)} file(s) in inbox/: " + ", ".join(f"{n} {k}" for k, n in sorted(kinds.items())))
    else:
        print("  · inbox/ is empty. Drop last month's statements and exports there first, with the "
              "banks' own filenames — they answer most of the questions. Without them every "
              "question is asked.")
    print()
    print("  Setup is five steps and about twenty minutes: 1 these tools · 2 a draft from your files ·"
          " 3 the questions the files cannot answer · 4 writing your workspace and the first import ·"
          " 5 the checks, and your page.")
    return 1 if need else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

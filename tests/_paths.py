"""Put the skill script folders on sys.path, so a test can `import flows` the way the scripts do.

The scripts live under .claude/skills/<skill>/scripts/ and import each other by bare name after
adding their own folder; a test sits two levels away and has to do the same. Found from this
file, never by counting `..` from the current directory (CLAUDE.md, the hook.py incident).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, ".claude", "skills")

for skill in ("update-dashboard", "workspace-checks", "setup"):
    p = os.path.join(SKILLS, skill, "scripts")
    if p not in sys.path:
        sys.path.insert(0, p)

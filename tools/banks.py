#!/usr/bin/env python3
"""Write docs/banks.md and docs/zh/banks.md from the tool's own table (parsers/support.py).

    python3 tools/banks.py          # write both
    python3 tools/banks.py --check  # exit 1 if either differs from what would be written

check_design's S9 runs the same comparison, so a status changed in the table and not here fails.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "update-dashboard"))
from parsers import support  # noqa: E402

TARGETS = {"en": "docs/banks.md", "zh": "docs/zh/banks.md"}


def main(argv):
    stale = []
    for lang, rel in TARGETS.items():
        path = os.path.join(ROOT, rel)
        text = support.render(lang)
        now = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if now != text:
            if "--check" in argv:
                stale.append(rel)
            else:
                open(path, "w", encoding="utf-8").write(text)
                print(f"  wrote {rel}")
    for rel in stale:
        print(f"  ✗ {rel} differs from parsers/support.py — run tools/banks.py")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

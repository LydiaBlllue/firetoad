#!/usr/bin/env python3
"""build.py — the double-clickable app: this tool, its Python and the demo, in one folder.

    python3 build/build.py                      # dist/Jade Toad.app (macOS) or dist/Jade Toad/ (Windows, Linux)
    python3 build/build.py --sign "Developer ID Application: …" --notarize <keychain profile>
    python3 build/build.py --no-dmg             # skip the .dmg / .zip

What goes in: app.py as the entry, the tool's copy exactly as tools/sync.py copies it into a
workspace (SYNCED — the skills, templates, tools, tests, the governing documents) and the demo's
findata/, so *Make one* on first launch has something to show. The interpreter is PyInstaller's
(one folder, not one file: the core runs its own scripts as subprocesses, and app.py doubles as
the interpreter for them). pypdf and, on macOS, ocrmac and the Vision bindings come along.

What never goes in: a workspace. The build refuses unless findata/ is the demo (profile.json
`demo: true`), and it adds no inbox/, archive/, .private/, product/ or feedback/ — the same
lines the privacy guard draws for a commit.

Signing: without --sign the app is ad-hoc signed, which runs on this Mac and asks the next Mac
to System Settings → Privacy & Security → Open Anyway once (macOS 14 and earlier: right-click → Open). With --sign (a Developer ID Application identity) it is signed with
the hardened runtime and build/entitlements.plist; with --notarize (a notarytool keychain
profile) it is notarised and stapled, which is what a public download needs. uv is used for
PyInstaller when it is installed (a pinned, modern Python); otherwise this interpreter's.
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(TOOL, "tools"))
import sync  # noqa: E402  SYNCED: the one list of what the tool is

NAME = "Jade Toad"
DATA_EXTRA = ("findata", "LICENSE", "README.md")   # beside SYNCED: the demo, and what a reader expects
EXCLUDE_DIRS = {"__pycache__", ".DS_Store"}


def die(msg):
    print("  ✗ " + msg); sys.exit(1)


def guard():
    """Never an owner's data: the bundled findata/ has to be the demo's."""
    for p in ("findata/register/profile.json", "findata/profile.json"):
        fp = os.path.join(TOOL, p)
        if os.path.exists(fp):
            if not json.load(open(fp, encoding="utf-8")).get("demo"):
                die(f"{p} is not the demo's (no `demo: true`): this checkout holds someone's data and is not built")
            return
    die("no findata/ profile.json: build from the tool's own checkout")


def run(cmd, **kw):
    print("  $ " + " ".join(cmd if isinstance(cmd, list) else [cmd]))
    return subprocess.run(cmd, check=True, **kw)


def version():
    import re
    t = open(os.path.join(TOOL, "templates", "dashboards", "finance_dashboard.html"), encoding="utf-8").read()
    m = re.search(r'const VERSION = "([^"]+)"', t)
    return m.group(1) if m else "0"


def stage(work):
    """A clean copy of what goes in, so PyInstaller never sees the checkout's clutter."""
    src_root = os.path.join(work, "src")
    if os.path.isdir(src_root):
        shutil.rmtree(src_root)
    os.makedirs(src_root)
    for rel in list(sync.SYNCED) + list(DATA_EXTRA):
        s, d = os.path.join(TOOL, rel), os.path.join(src_root, rel)
        if not os.path.exists(s):
            print(f"  ⚠ no {rel} in the tool; skipped"); continue
        if os.path.isdir(s):
            shutil.copytree(s, d, ignore=shutil.ignore_patterns(*EXCLUDE_DIRS, "*.pyc"))
        else:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
    return src_root


def imports_of(src_root):
    """Every module the tool's own scripts import, so PyInstaller bundles them: it analyses the
    entry script only, and the core is data to it (its .py files run from the folder). The first
    build shipped without `html` and the server could not start. Names the staged tree itself
    provides (layout, verbs, a parser) are not importable from here and fall out by themselves."""
    import importlib.util
    import re
    names = set()
    for dp, _, fs in os.walk(src_root):
        for f in fs:
            if not f.endswith(".py"):
                continue
            for line in open(os.path.join(dp, f), encoding="utf-8", errors="ignore"):
                m = re.match(r"\s*(?:import|from)\s+([A-Za-z_][\w.]*)", line)
                if m:
                    names.add(m.group(1))
    # the tree's own modules (run from the folder, never bundled as code) and the page checker's
    # browser driver (check_render, a developer's check, not the app's)
    own = {os.path.splitext(f)[0] for dp, _, fs in os.walk(src_root) for f in fs if f.endswith(".py")}
    skip = own | {"playwright"}
    out = []
    for n in sorted(names):
        parts = n.split(".")
        if parts[0] in skip:
            continue
        for i in range(1, len(parts) + 1):
            dotted = ".".join(parts[:i])
            try:
                ok = importlib.util.find_spec(dotted) is not None
            except (ImportError, ValueError, AttributeError):
                ok = False
            if ok and dotted not in out:
                out.append(dotted)
    return out


def pyinstaller_cmd():
    if shutil.which("uv"):
        return ["uv", "run", "--with", "pyinstaller", "--with", "pypdf", "--with", "cryptography"] \
            + (["--with", "ocrmac", "--with", "Pillow"] if sys.platform == "darwin" else []) + ["pyinstaller"]
    return [sys.executable, "-m", "PyInstaller"]


def build(args):
    guard()
    work = os.path.join(TOOL, "build", "work")
    dist = os.path.join(TOOL, "dist")
    src_root = stage(work)
    sep = ";" if sys.platform.startswith("win") else ":"
    cmd = pyinstaller_cmd() + [
        "--noconfirm", "--clean", "--onedir", "--windowed", "--name", NAME,
        "--distpath", dist, "--workpath", os.path.join(work, "pyi"), "--specpath", work,
        "--collect-all", "pypdf", "--hidden-import", "cryptography",
    ]
    if sys.platform == "darwin":
        cmd += ["--collect-all", "ocrmac", "--hidden-import", "objc", "--hidden-import", "Vision", "--hidden-import", "Quartz",
                "--hidden-import", "PIL", "--osx-bundle-identifier", "app.jadetoad.local"]
    icon = os.path.join(HERE, "icon.icns" if sys.platform == "darwin" else "icon.ico")
    if os.path.exists(icon):
        cmd += ["--icon", icon]
    # --add-data's destination is a folder: a directory keeps its name, a file goes to "." (the
    # first build put CLAUDE.md at CLAUDE.md/CLAUDE.md). app.py comes along too, as data, so the
    # bundled tool copy has everything sync.py copies into a workspace.
    for rel in sorted(os.listdir(src_root)):
        full = os.path.join(src_root, rel)
        cmd += ["--add-data", f"{full}{sep}{rel if os.path.isdir(full) else '.'}"]
    mods = imports_of(src_root)
    print(f"  {len(mods)} modules the scripts import, bundled as hidden imports")
    for n in mods:
        cmd += ["--hidden-import", n]
    cmd += [os.path.join(src_root, "app.py")]
    run(cmd)

    out = os.path.join(dist, NAME + ".app") if sys.platform == "darwin" else os.path.join(dist, NAME)
    if sys.platform == "darwin":
        ent = os.path.join(HERE, "entitlements.plist")
        if args.sign:
            run(["codesign", "--force", "--deep", "--options", "runtime", "--timestamp", "--entitlements", ent,
                 "--sign", args.sign, out])
        else:
            run(["codesign", "--force", "--deep", "--sign", "-", out])
        run(["codesign", "--verify", "--deep", "--strict", out])
    ver = version()
    if not args.no_dmg:
        if sys.platform == "darwin":
            dmg = os.path.join(dist, f"JadeToad-{ver}.dmg")
            if os.path.exists(dmg):
                os.remove(dmg)
            # the disk image shows three things: the app, the Applications folder to drag it onto,
            # and a one-page note on the first launch (build/dmg/), in both languages
            stage_dir = os.path.join(dist, "dmg-stage")
            shutil.rmtree(stage_dir, ignore_errors=True)
            os.makedirs(stage_dir)
            shutil.copytree(out, os.path.join(stage_dir, os.path.basename(out)), symlinks=True)
            os.symlink("/Applications", os.path.join(stage_dir, "Applications"))
            for f in os.listdir(os.path.join(HERE, "dmg")):
                if not f.startswith("."):
                    shutil.copy(os.path.join(HERE, "dmg", f), stage_dir)
            run(["hdiutil", "create", "-volname", NAME, "-srcfolder", stage_dir, "-ov", "-format", "UDZO", dmg])
            shutil.rmtree(stage_dir, ignore_errors=True)
            if args.sign:
                run(["codesign", "--force", "--timestamp", "--sign", args.sign, dmg])
            if args.notarize:
                run(["xcrun", "notarytool", "submit", dmg, "--keychain-profile", args.notarize, "--wait"])
                run(["xcrun", "stapler", "staple", out])
                run(["xcrun", "stapler", "staple", dmg])
            print(f"\n  ✓ {dmg}")
        else:
            z = shutil.make_archive(os.path.join(dist, f"JadeToad-{ver}-{platform.system().lower()}"), "zip", dist, NAME)
            print(f"\n  ✓ {z}")
    print(f"  ✓ {out}" + ("" if args.sign else "  (ad-hoc signed: this Mac runs it; another asks for System Settings → Privacy & Security → Open Anyway once)"))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sign", help="a Developer ID Application identity (macOS)")
    ap.add_argument("--notarize", help="a notarytool keychain profile; implies --sign")
    ap.add_argument("--no-dmg", action="store_true")
    a = ap.parse_args(argv)
    if a.notarize and not a.sign:
        die("--notarize needs --sign")
    return build(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

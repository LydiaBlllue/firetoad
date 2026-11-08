#!/usr/bin/env python3
"""build.py — the double-clickable app: this tool, its Python and the demo, in one folder.

    python3 build/build.py                      # dist/Jade Toad.app (macOS) or dist/Jade Toad/ (Windows, Linux)
    python3 build/build.py --sign "Developer ID Application: …" --notarize <keychain profile>
    python3 build/build.py --no-dmg             # skip the .dmg / .zip

What goes in: app.py as the entry, the tool's copy exactly as tools/sync.py copies it into a
workspace (SYNCED — the skills, templates, tools, tests, the governing documents), and
nothing else: *Make one* starts a folder holding only the tool and a profile.json that says
it is not set up yet, and the setup writes the owner's own data. The interpreter is PyInstaller's
(one folder, not one file: the core runs its own scripts as subprocesses, and app.py doubles as
the interpreter for them). pypdf and, on macOS, ocrmac and the Vision bindings come along.

What never goes in: a workspace. The build refuses to run from a checkout whose findata/ is not
the demo (profile.json `demo: true`), a sign it is someone's folder, and it adds no inbox/,
archive/, .private/, product/ or feedback/: the same lines the privacy guard draws for a commit.

Signing: without --sign the app is ad-hoc signed, which runs on this Mac and asks the next Mac
to System Settings → Privacy & Security → Open Anyway once (macOS 14 and earlier: right-click →
Open). With --sign (a Developer ID Application identity) every library is signed inside out with
the hardened runtime, then the app with build/entitlements.plist; --sign - does the same ad hoc,
a local test that the app still runs hardened. With --notarize (a notarytool keychain profile)
the app is sent to Apple and stapled, then the disk image: what a public download needs.

Signing for real, once per Mac:
  1. An Apple Developer Program membership (developer.apple.com/programs, as an individual).
  2. Xcode → Settings → Accounts → the Apple ID → Manage Certificates → + → Developer ID
     Application. `security find-identity -v -p codesigning` then lists it.
  3. An app-specific password (account.apple.com → Sign-In and Security), then
     xcrun notarytool store-credentials jadetoad --apple-id <the Apple ID> --team-id <team>
     which asks for that password and keeps it in the Keychain under the profile "jadetoad".
  4. python3 build/build.py --sign "Developer ID Application: <name> (<team>)" --notarize jadetoad uv is used for
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
sys.path.insert(0, HERE)   # dmg_art.py, the disk image window
import sync  # noqa: E402  SYNCED: the one list of what the tool is

NAME = "Jade Toad"
DATA_EXTRA = ("LICENSE", "README.md")   # beside SYNCED: what a reader expects. No findata/: Make one
# starts a folder with no one's data in it (2026-11-08), so the demo owner has no reason to ship
EXCLUDE_DIRS = {"__pycache__", ".DS_Store"}


def die(msg):
    print("  ✗ " + msg); sys.exit(1)


def guard():
    """Never built from an owner's folder: the checkout's findata/ has to be the demo's."""
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
        if args.sign:
            sign_app(out, args.sign)
        else:
            run(["codesign", "--force", "--deep", "--sign", "-", out])
        run(["codesign", "--verify", "--deep", "--strict", out])
        if args.notarize:
            # the app first, its ticket stapled to it: once dragged out of the disk image it
            # carries its own proof and opens with no network (the dmg's ticket stays on the dmg)
            z = os.path.join(dist, NAME + ".zip")
            run(["ditto", "-c", "-k", "--keepParent", out, z])
            notarize(z, args.notarize)
            os.remove(z)
            run(["xcrun", "stapler", "staple", out])
    ver = version()
    if not args.no_dmg:
        if sys.platform == "darwin":
            dmg = os.path.join(dist, f"JadeToad-{ver}.dmg")
            if os.path.exists(dmg):
                os.remove(dmg)
            make_dmg(out, dmg)
            if args.sign:
                run(["codesign", "--force", "--timestamp=none" if args.sign == "-" else "--timestamp", "--sign", args.sign, dmg])
            if args.notarize:
                notarize(dmg, args.notarize)
                run(["xcrun", "stapler", "staple", dmg])
                run(["spctl", "--assess", "--type", "open", "--context", "context:primary-signature", "-v", dmg])
            print(f"\n  ✓ {dmg}")
        else:
            z = shutil.make_archive(os.path.join(dist, f"JadeToad-{ver}-{platform.system().lower()}"), "zip", dist, NAME)
            print(f"\n  ✓ {z}")
    how = ("  (notarised: any Mac opens it with a double-click)" if args.notarize else
           "  (hardened, ad-hoc: a local test of the signed build)" if args.sign == "-" else
           "  (signed, not notarised: another Mac still asks once)" if args.sign else
           "  (ad-hoc signed: this Mac runs it; another asks for System Settings → Privacy & Security → Open Anyway once)")
    print(f"  ✓ {out}" + how)
    return 0



MACHO = (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xfe\xed\xfa\xcf", b"\xfe\xed\xfa\xce")


def sign_app(app, identity):
    """Sign for notarisation, inside out. `codesign --deep` only reaches code in the places a
    bundle is supposed to keep it, and PyInstaller puts a few hundred Python extensions
    (.so, .dylib) under Frameworks/ and Resources/; notarisation refuses the app if any one of
    them lacks a signature, the hardened runtime or a secure timestamp. So every Mach-O file is
    signed on its own, deepest first, then each nested bundle (Python3.framework) as a whole, then
    the app with build/entitlements.plist, which is what
    Python needs under the hardened runtime. `--sign -` runs the same path ad hoc (no timestamp
    is possible): a local test that the app still starts with the hardened runtime on."""
    ent = os.path.join(HERE, "entitlements.plist")
    ts = ["--timestamp=none"] if identity == "-" else ["--timestamp"]
    main_exe = os.path.join(app, "Contents", "MacOS", NAME)
    found = []
    for d, _, fs in os.walk(app):
        for f in fs:
            p = os.path.join(d, f)
            if os.path.islink(p) or p == main_exe:
                continue
            try:
                with open(p, "rb") as fh:
                    if fh.read(4) in MACHO:
                        found.append(p)
            except OSError:
                pass
    found.sort(key=lambda p: -p.count(os.sep))
    print(f"  $ codesign {len(found)} libraries and extensions, then the app (hardened runtime)")
    for i in range(0, len(found), 50):     # in batches: one codesign call per file is minutes
        subprocess.run(["codesign", "--force", "--options", "runtime", *ts, "--sign", identity, *found[i:i + 50]],
                       check=True, stdout=subprocess.DEVNULL)
    # a nested bundle (PyInstaller ships Python3.framework) has its own seal over what is inside
    # it: signed after its contents, as a bundle, or the app's signature calls it "modified"
    nested = []
    for d, dirs, _ in os.walk(app):
        for x in dirs:
            p = os.path.join(d, x)
            if x.endswith((".framework", ".bundle", ".app", ".xpc")) and not os.path.islink(p):
                nested.append(p)
    for p in sorted(nested, key=lambda p: -p.count(os.sep)):
        run(["codesign", "--force", "--options", "runtime", *ts, "--sign", identity, p])
    run(["codesign", "--force", "--options", "runtime", *ts, "--entitlements", ent, "--sign", identity, app])


def notarize(path, profile):
    """Send to Apple and wait; stop with Apple's own log when it is not Accepted. notarytool
    exits 0 even for an Invalid submission, so its answer is read, not its exit code."""
    print(f"  $ xcrun notarytool submit {os.path.basename(path)} --keychain-profile {profile} --wait")
    r = subprocess.run(["xcrun", "notarytool", "submit", path, "--keychain-profile", profile, "--wait",
                        "--output-format", "json"], capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)
    except ValueError:
        die("notarytool: " + (r.stderr or r.stdout).strip()[:400])
    if res.get("status") != "Accepted":
        log = subprocess.run(["xcrun", "notarytool", "log", res.get("id", ""), "--keychain-profile", profile],
                             capture_output=True, text=True).stdout
        die(f"Apple did not accept {os.path.basename(path)} ({res.get('status')}):\n{log[:3000]}")
    print(f"  ✓ notarised: {os.path.basename(path)}")


def make_dmg(app, dmg):
    """The disk image a person opens: the app on the left, the Applications folder on the right,
    an arrow between them and the instruction in both languages under it (build/dmg_art.py),
    the first-launch note at the foot (build/dmg/).

    Finder lays the window out itself: a writable image is mounted, AppleScript tells Finder the
    background, the icon size and where each icon sits, and the image is then compressed. A
    .DS_Store written without Finder (dmgbuild) is ignored by Finder on macOS 26: the window came
    out blank. The first build asks once for permission to control Finder. Without Finder (or
    without Pillow) the image still has all three things, in Finder's plain window."""
    import tempfile
    notes = [os.path.join(HERE, "dmg", f) for f in sorted(os.listdir(os.path.join(HERE, "dmg"))) if not f.startswith(".")]
    vol = os.path.join("/Volumes", NAME)
    if os.path.exists(vol):
        # Finder is told the disk by name; a second one would be "Jade Toad 1" and the layout
        # would land on whichever Finder found first
        sys.exit(f'  ✗ a disk named {NAME} is mounted: eject it first (Finder, or hdiutil detach "{vol}")')
    work = tempfile.mkdtemp(prefix="jade-dmg-")
    stage_dir = os.path.join(work, "stage")
    os.makedirs(stage_dir)
    shutil.copytree(app, os.path.join(stage_dir, os.path.basename(app)), symlinks=True)
    os.symlink("/Applications", os.path.join(stage_dir, "Applications"))
    for f in notes:
        shutil.copy(f, stage_dir)
    laid_out = False
    try:
        import dmg_art
        os.makedirs(os.path.join(stage_dir, ".background"))
        dmg_art.write(os.path.join(stage_dir, ".background", "bg.tiff"))
    except Exception as e:                       # no Pillow, no tiffutil: the plain window
        print(f"  · plain disk image (the background could not be drawn: {e})")
        dmg_art = None
    if dmg_art:
        rw = os.path.join(work, "rw.dmg")
        run(["hdiutil", "create", "-quiet", "-volname", NAME, "-srcfolder", stage_dir, "-fs", "HFS+",
             "-format", "UDRW", "-ov", rw])
        run(["hdiutil", "attach", "-quiet", "-nobrowse", "-noautoopen", rw])
        w, h = dmg_art.WINDOW["size"]
        place = [(os.path.basename(app), dmg_art.ICONS["app"]), ("Applications", dmg_art.ICONS["apps"])]
        place += [(os.path.basename(f), dmg_art.ICONS["note"]) for f in notes]
        where = "\n".join(f'    set position of item "{n}" of container window to {{{x}, {y}}}' for n, (x, y) in place)
        script = f"""tell application "Finder"
  tell disk "{NAME}"
    open
    set current view of container window to icon view
    set toolbar visible of container window to false
    set statusbar visible of container window to false
    set the bounds of container window to {{200, 120, {200 + w}, {120 + h + dmg_art.TITLE_BAR}}}
    set opts to the icon view options of container window
    set arrangement of opts to not arranged
    set icon size of opts to {dmg_art.WINDOW["icon_size"]}
    set text size of opts to 13
    set background picture of opts to file ".background:bg.tiff"
{where}
    update without registering applications
    delay 1
    close
  end tell
end tell"""
        r = subprocess.run(["osascript", "-"], input=script, text=True, capture_output=True)
        laid_out = r.returncode == 0
        if not laid_out:
            print(f"  · plain disk image (Finder did not lay it out: {r.stderr.strip()[:160]})")
        subprocess.run(["sync"])
        run(["hdiutil", "detach", "-quiet", vol])
        if laid_out:
            run(["hdiutil", "convert", "-quiet", rw, "-format", "UDZO", "-ov", "-o", dmg])
    if not laid_out:
        shutil.rmtree(os.path.join(stage_dir, ".background"), ignore_errors=True)
        run(["hdiutil", "create", "-volname", NAME, "-srcfolder", stage_dir, "-ov", "-format", "UDZO", dmg])
    shutil.rmtree(work, ignore_errors=True)

def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sign", help='a Developer ID Application identity (macOS); "-" is the same signing ad hoc, a local test')
    ap.add_argument("--notarize", help="a notarytool keychain profile; implies --sign")
    ap.add_argument("--no-dmg", action="store_true")
    a = ap.parse_args(argv)
    if a.notarize and not a.sign:
        die("--notarize needs --sign")
    return build(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

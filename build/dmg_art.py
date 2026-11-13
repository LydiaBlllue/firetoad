#!/usr/bin/env python3
"""dmg_art.py — the picture behind the disk image's window: the app in the middle, the
instruction under it in English and Chinese, and a pointer to the note at the foot. No
Applications folder and no arrow since 2026-11-12: a drag runs nothing, so it left the owner one
more double-click in Applications; a double-click here installs the app and opens it (app.py).

The window's geometry lives here, once: build.py reads WINDOW, ICONS and TITLE_BAR and tells
Finder to put each icon exactly where the picture expects it. Drawn at 1x and 2x and joined into one TIFF
(tiffutil), so a Retina screen gets the sharp one. Needs Pillow (ocrmac brings it).

    python3 build/dmg_art.py OUT.tiff        # writes OUT.tiff, prints the geometry
"""
import os
import subprocess
import sys
import tempfile

W, H = 660, 500                      # the window's content area, in points
ICON = 100                           # icon size Finder draws, in points
TITLE_BAR = 28                       # Finder's window bounds include it; the picture does not
APP, NOTE = (330, 150), (330, 380)   # icon centres
WINDOW = {"size": (W, H), "icon_size": ICON}
ICONS = {"app": APP, "note": NOTE}

PAGE, INK2, MUTED, LINE, ACCENT = "#f9f9f7", "#52514e", "#75736d", "#e4e2dc", "#1a7a4a"
LINES = ("Double-click FIRE Toad: it installs itself and opens", "双击 FIRE Toad：自动安装并打开")
FOOT = "Need help? Read this  ·  需要帮助？看这个"
FONTS = ("/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/STHeiti Medium.ttc",
         "/System/Library/Fonts/Supplemental/Arial Unicode.ttf")


def font(size):
    from PIL import ImageFont
    for f in FONTS:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def draw(scale):
    from PIL import Image, ImageDraw
    s = lambda v: int(round(v * scale))
    im = Image.new("RGB", (s(W), s(H)), PAGE)
    d = ImageDraw.Draw(im)
    # the instruction, centred under the app (Finder draws the label just below the icon)
    f = font(s(16))
    for i, text in enumerate(LINES):
        tw = d.textlength(text, font=f)
        d.text(((s(W) - tw) / 2, s(240 + i * 26)), text, font=f, fill=INK2)
    # a rule, then the pointer to the note
    d.line([(s(60), s(300)), (s(W - 60), s(300))], fill=LINE, width=max(1, s(1)))
    f2 = font(s(12))
    tw = d.textlength(FOOT, font=f2)
    d.text(((s(W) - tw) / 2, s(308)), FOOT, font=f2, fill=MUTED)
    return im


def write(out):
    tmp = tempfile.mkdtemp(prefix="jade-dmg-art-")
    one, two = os.path.join(tmp, "bg.png"), os.path.join(tmp, "bg@2x.png")
    draw(1).save(one, dpi=(72, 72))
    draw(2).save(two, dpi=(144, 144))
    subprocess.run(["tiffutil", "-cathidpicheck", one, two, "-out", out], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


if __name__ == "__main__":
    print(write(sys.argv[1] if len(sys.argv) > 1 else "dmg-background.tiff"), WINDOW, ICONS)

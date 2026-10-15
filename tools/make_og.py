"""Generate og.png (1200x630 social preview). Run manually: python3 tools/make_og.py
Needs Pillow and EB Garamond (SIL OFL). Colours match style.css (light theme). Output has no metadata."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.environ.get("OG_FONT", "/usr/share/fonts/truetype/sand-box/google/EB Garamond/EBGaramond-VariableFont_wght.ttf")
BG, CARD, FG, MUTED, ACCENT, SOFT, LINE = "#fbf7ef", "#fffdf8", "#2e2a25", "#6f655a", "#8a5a2b", "#c9a46a", "#e7ddcc"
W, H = 1200, 630


def font(size, wght):
    f = ImageFont.truetype(FONT, size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f


def centered(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.rounded_rectangle((40, 40, W - 40, H - 40), radius=28, fill=CARD, outline=LINE, width=3)
centered(d, 70, "42", font(300, 700), ACCENT)
d.line((W / 2 - 60, 400, W / 2 + 60, 400), fill=SOFT, width=4)
centered(d, 425, "42 Maxims", font(72, 600), FG)
centered(d, 520, "A sourced, ranked collection of rules for life", font(38, 400), MUTED)
img = img.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
img.save(os.path.join(ROOT, "og.png"), optimize=True)

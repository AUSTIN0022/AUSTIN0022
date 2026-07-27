"""
Turn the voxel/pixel-art avatar PNG into a self-building SVG portrait for the
profile README, matching the same terminal-window chrome and "prints itself in"
reveal used by make_ascii_svg.py -- but instead of typing ASCII characters, the
actual voxel image scans in top -> bottom behind a moving scan-line, band by
band, then holds on the finished portrait.

GitHub renders SVGs embedded via <img> and runs their SMIL animations there (JS
does not run), so this stays a pure SVG with <animate> tags -- same approach as
the ASCII portrait.
"""
from PIL import Image
import base64
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "voxel-avatar-navy-hoodies.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "avatar-portrait.svg")

# match avi-ascii.svg's canvas exactly so it drops into the README table
# without changing the layout (portrait / info-card stay the same height).
PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
CANVAS_W = 840
CANVAS_H = 875
ART_W = CANVAS_W - PAD * 2
ART_H = CANVAS_H - TITLEBAR_H - STATUS_H - PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
SCAN = "#3fb950"   # scan-line accent (matches the green "online" dot elsewhere)

BANDS = 48
TOTAL_DUR = 5.3            # roughly matches the ascii portrait's reveal length
STAGGER = TOTAL_DUR / BANDS
BAND_DUR = STAGGER * 1.35  # slight overlap so bands blend, no visible seams

STATIC = bool(os.environ.get("STATIC"))  # emit frozen (fully revealed) preview

# ---- 1. crop + resize the source image to fill the art area exactly -------
im = Image.open(SRC).convert("RGB")
src_w, src_h = im.size
target_ratio = ART_W / ART_H
src_ratio = src_w / src_h

if src_ratio > target_ratio:
    # source is relatively wider -> crop sides
    new_w = int(src_h * target_ratio)
    x0 = (src_w - new_w) // 2
    im = im.crop((x0, 0, x0 + new_w, src_h))
else:
    # source is relatively taller -> crop a bit off the bottom so the face
    # (near the top third) stays centered rather than the composition sinking
    new_h = int(src_w / target_ratio)
    y0 = max(0, int((src_h - new_h) * 0.28))
    im = im.crop((0, y0, src_w, y0 + new_h))

im = im.resize((ART_W, ART_H), Image.LANCZOS)

buf = io.BytesIO()
im.save(buf, format="JPEG", quality=90, optimize=True)  # photo-like voxel art
b64 = base64.b64encode(buf.getvalue()).decode("ascii")   # compresses far smaller
data_uri = f"data:image/jpeg;base64,{b64}"                # than PNG at this size

art_top = TITLEBAR_H + PAD * 0.35
band_h = ART_H / BANDS

# ---- 2. assemble SVG -------------------------------------------------------
parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">'
)
parts.append('<defs>'
             f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')

parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
             f'fill="none" stroke="{FRAME}" stroke-width="1"/>')

parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">austin@github: ~$ ./portrait.sh --voxel</text>')

img_tag = (f'<image href="{data_uri}" x="{PAD}" y="{art_top:.1f}" width="{ART_W}" '
           f'height="{ART_H}" preserveAspectRatio="xMidYMid slice"/>')

if STATIC:
    parts.append(img_tag)
else:
    parts.append(f'<clipPath id="voxel-reveal">')
    for b in range(BANDS):
        row_y = art_top + b * band_h
        delay = b * STAGGER
        parts.append(
            f'<rect x="{PAD}" y="{row_y:.1f}" height="{band_h + 0.6:.2f}" width="0">'
            f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
            f'dur="{BAND_DUR:.2f}s" fill="freeze"/></rect>'
        )
    parts.append('</clipPath>')
    parts.append(f'<g clip-path="url(#voxel-reveal)">{img_tag}</g>')

    # a scan-line bar that rasters down the frame in sync with the reveal
    parts.append(
        f'<rect x="{PAD}" width="{ART_W}" height="2.5" fill="{SCAN}" opacity="0">'
        f'<animate attributeName="y" from="{art_top:.1f}" to="{art_top+ART_H:.1f}" '
        f'begin="0s" dur="{TOTAL_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.9" begin="0s"/>'
        f'<set attributeName="opacity" to="0" begin="{TOTAL_DUR:.2f}s"/></rect>'
    )

# status bar with a steady blinking cursor
status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'austin@github:~$ whoami <tspan fill="{INK}">AUSTIN0022</tspan></text>')
parts.append(f'<rect x="{PAD+196}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)

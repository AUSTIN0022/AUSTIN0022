"""
Build a neofetch-style info card SVG (Andrew6rant style) to sit to the RIGHT of
the ASCII portrait: colored key/value rows for work experience, tech stack, and
highlights -- NOT GitHub stats (the contribution graph covers those).

Static content, hand-authored below. Lines fade/slide in on a short stagger so
it feels like the panel is printing alongside the portrait. STATIC=1 emits the
frozen state for Quick Look previews.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

W = 480          # H is derived below from ROWS -- no need to hand-tune it
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 92
LINE_H = 20.5

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"      # orange keys (matches Andrew)
SECTION = "#58a6ff"  # blue section headers
GREEN = "#3fb950"
ACCENT = "#22d3ee"

# ===========================================================================
#  EDIT THIS  -- your info panel. It re-lays-out automatically; if it gets too
#  tall for the card, bump H above (and the width= in your profile README).
#  The username in the header is HOST below.
#
#  row types:
#    ("host",)              -> "you@github" header + rule
#    ("cmd", text)          -> muted "$ text" command line (the "whoami" prompt)
#    ("identity", text)     -> bold, larger identity line (the answer to whoami)
#    ("kv", key, value)     -> orange key + light value
#    ("sec", title)         -> blue "— title —" section rule
#    ("bul", text)          -> green dot + light bullet
#    ("gap",)               -> a little vertical space
# ===========================================================================
HOST = "AUSTIN0022"   # shown as  AUSTIN0022@github  in the header

ROWS = [
    ("host",),
    ("cmd", "whoami"),
    ("identity", "Full Stack Engineer"),
    ("gap",),
    ("sec", "Current Focus"),
    ("bul", "Distributed Systems"),
    ("bul", "Cloud Infrastructure"),
    ("bul", "Real-time Applications"),
    ("bul", "Developer Experience"),
    ("gap",),
    ("sec", "Building With"),
    ("bul", "TypeScript"),
    ("bul", "Node.js"),
    ("bul", "PostgreSQL"),
    ("bul", "Redis"),
    ("bul", "AWS"),
    ("bul", "Terraform"),
    ("bul", "Docker"),
    ("gap",),
    ("sec", "Interested In"),
    ("bul", "Observability"),
    ("bul", "Event-driven Systems"),
    ("bul", "System Design"),
    ("bul", "Performance Engineering"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    """fade + slight upward slide, staggered by row index; freezes visible."""
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


def row_inner(row, y):
    kind = row[0]
    if kind == "host":
        host = esc(HOST)
        rule_x = KEY_X + (len(HOST) + 7) * 8 + 8
        return (f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700">'
                f'<tspan fill="{GREEN}">{host}</tspan><tspan fill="{MUTED}">@</tspan>'
                f'<tspan fill="{ACCENT}">github</tspan></text>'
                f'<line x1="{rule_x}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    if kind == "cmd":
        txt = esc(row[1])
        return (f'<text x="{KEY_X}" y="{y:.1f}" font-size="12.5">'
                f'<tspan fill="{MUTED}">$ </tspan><tspan fill="{INK}">{txt}</tspan></text>')
    if kind == "identity":
        txt = esc(row[1])
        return f'<text x="{KEY_X}" y="{y:.1f}" fill="{INK}" font-size="15" font-weight="700">{txt}</text>'
    if kind == "sec":
        title = esc(row[1])
        return (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                f'&#8212; {title}</text>'
                f'<line x1="{KEY_X + 20 + len(row[1])*8}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    if kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        return (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>'
                f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{val}</text>')
    if kind == "bul":
        txt = esc(row[1])
        return (f'<circle cx="{KEY_X+3}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                f'<text x="{KEY_X+14}" y="{y:.1f}" fill="{INK}" font-size="12.5">{txt}</text>')
    return None


# ---- pass 1: lay out rows top -> bottom to find where content ends, so the
# card's height always matches ROWS above without hand-tuning a constant -----
y = TITLEBAR_H + 30
row_ys = []
for row in ROWS:
    if row[0] == "gap":
        y += LINE_H * 0.5
        continue
    row_ys.append(y)
    y += LINE_H
H = round(y + PAD * 0.6)

# ---- pass 2: build the SVG now that H is known -----------------------------
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">{esc(HOST)}@github: ~$ whoami</text>')

ri = 0
for row in ROWS:
    if row[0] == "gap":
        continue
    inner = row_inner(row, row_ys[ri])
    parts.append(rise(inner, ri))
    ri += 1

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H)

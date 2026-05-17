import base64, io, os, subprocess, textwrap
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = f"{ROOT}/static/images/awardee/2026"
OUT_SVG = f"{HERE}/awardees_collage.svg"
OUT_PNG = f"{HERE}/awardees_collage.png"

awardees = [
    ("Dibakar Roy Sarkar", "Johns Hopkins University",              f"{IMG}/dibakar.png"),
    ("Taiwo A. Adebiyi",   "University of Houston",                 f"{IMG}/taiwo.png"),
    ("Melis Fidansoy",     "University of California, Los Angeles", f"{IMG}/melis.png"),
    ("Jung-Hoon Cho",      "Massachusetts Institute of Technology", f"{IMG}/jung-hoon.png"),
    ("Sai Krishna",        "University of Georgia",                 f"{IMG}/saikrishna.png"),
]

W, H = 1500, 1500
ACCENT = "#660066"
TEXT = "#1e1e1e"
SUB = "#5a5a5a"
BG = "#ffffff"

PHOTO_R = 175
PHOTO_D = PHOTO_R * 2
TILE_W = 480
GAP_X = 30

TITLE_Y = 110
SUBTITLE_Y = 180
DIVIDER_Y = 220
ROW1_CY = 410
ROW_SPACING = 540
ROW2_CY = ROW1_CY + ROW_SPACING
FOOTER_NSF_Y = H - 78
FOOTER_URL_Y = H - 42

FONT_FAMILY = "Helvetica, Arial, sans-serif"

def b64_image(path, target=900):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    s = min(w, h)
    img = img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    img = img.resize((target, target), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90, optimize=True)
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{data}"

def row_centers(n):
    total = n * TILE_W + (n - 1) * GAP_X
    start = (W - total) / 2 + TILE_W / 2
    return [start + i * (TILE_W + GAP_X) for i in range(n)]

def wrap_text(text, max_chars=24):
    return textwrap.wrap(text, width=max_chars)

def tile_svg(cx, cy, name, school, img_data, idx):
    cid = f"clip{idx}"
    photo_x = cx - PHOTO_R
    photo_y = cy - PHOTO_R
    lines = wrap_text(school, max_chars=26)
    school_lines = ""
    for i, line in enumerate(lines):
        y = cy + PHOTO_R + 110 + i * 36
        school_lines += f'<text x="{cx}" y="{y}" text-anchor="middle" font-family="{FONT_FAMILY}" font-size="26" fill="{SUB}">{line}</text>\n'
    return f"""
<defs>
  <clipPath id="{cid}">
    <circle cx="{cx}" cy="{cy}" r="{PHOTO_R}" />
  </clipPath>
</defs>
<image href="{img_data}" x="{photo_x}" y="{photo_y}" width="{PHOTO_D}" height="{PHOTO_D}"
       preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})" />
<circle cx="{cx}" cy="{cy}" r="{PHOTO_R}" fill="none" stroke="{ACCENT}" stroke-width="6" />
<text x="{cx}" y="{cy + PHOTO_R + 60}" text-anchor="middle"
      font-family="{FONT_FAMILY}" font-size="34" font-weight="700" fill="{TEXT}">{name}</text>
{school_lines}
"""

row1 = awardees[:3]
row2 = awardees[3:]
tiles = []
for i, ((name, school, path), cx) in enumerate(zip(row1, row_centers(len(row1)))):
    tiles.append(tile_svg(cx, ROW1_CY, name, school, b64_image(path), i))
for i, ((name, school, path), cx) in enumerate(zip(row2, row_centers(len(row2)))):
    tiles.append(tile_svg(cx, ROW2_CY, name, school, b64_image(path), i + 100))

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <rect width="{W}" height="{H}" fill="{BG}"/>

  <text x="{W/2}" y="{TITLE_Y}" text-anchor="middle"
        font-family="{FONT_FAMILY}" font-size="68" font-weight="800" fill="{ACCENT}">Chishiki AI</text>
  <text x="{W/2}" y="{SUBTITLE_Y}" text-anchor="middle"
        font-family="{FONT_FAMILY}" font-size="38" font-weight="500" fill="{TEXT}">2026 Graduate Fellowship Awardees</text>
  <line x1="{W/2 - 200}" y1="{DIVIDER_Y}" x2="{W/2 + 200}" y2="{DIVIDER_Y}"
        stroke="{ACCENT}" stroke-width="3" stroke-linecap="round"/>

  {''.join(tiles)}

  <text x="{W/2}" y="{FOOTER_NSF_Y}" text-anchor="middle"
        font-family="{FONT_FAMILY}" font-size="22" font-weight="600" fill="{TEXT}">
    Supported by the National Science Foundation &#8226; Award #2321040
  </text>
  <text x="{W/2}" y="{FOOTER_URL_Y}" text-anchor="middle"
        font-family="{FONT_FAMILY}" font-size="20" fill="{SUB}">
    chishiki-ai.github.io &#8226; AI-powered Civil Engineering Community
  </text>
</svg>
"""

with open(OUT_SVG, "w") as f:
    f.write(svg)

subprocess.run(
    ["rsvg-convert", "-w", "3000", "-h", "3000", "-o", OUT_PNG, OUT_SVG],
    check=True,
)

print(f"SVG: {OUT_SVG}  ({os.path.getsize(OUT_SVG)//1024} KB)")
print(f"PNG: {OUT_PNG}  ({os.path.getsize(OUT_PNG)//1024} KB) — 3000x3000")

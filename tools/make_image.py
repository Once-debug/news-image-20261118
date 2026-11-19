#!/usr/bin/env python3
"""Draw the 18 November 2026 'front page in one image' for news-image-20261118.

Pure PIL, offline, deterministic: fixed layout, fixed text, no randomness,
no external assets. Output: ../entry.png (1024x1024, <= 1 MiB).
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W = H = 1024
PAPER = (246, 241, 229)
INK = (20, 18, 14)
MUTED = (92, 84, 68)
RED = (176, 42, 30)
BLUE = (38, 74, 140)
GOLD = (198, 152, 40)
PANEL_BG = (251, 248, 240)
PANEL_EDGE = (198, 190, 168)

FONT_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_BLACK = "NotoSerif-Black.ttf"
SERIF_BOLD = "NotoSerif-Bold.ttf"
SANS = "NotoSans-Regular.ttf"
SANS_BOLD = "NotoSans-Bold.ttf"
SANS_BLACK = "NotoSans-Black.ttf"


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, fill, max_w, leading):
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centered(draw, cx, y, text, fnt, fill):
    w_ = draw.textlength(text, font=fnt)
    draw.text((cx - w_ / 2, y), text, font=fnt, fill=fill)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
M = 40
CW = W - 2 * M

# ---------------------------------------------------------------- masthead
centered(d, W / 2, 24, "O N E   I M A G E   •   O N E   D A Y   •   T H E   W O R L D ' S   N E W S",
         font(SANS_BOLD, 17), MUTED)
centered(d, W / 2, 50, "THE WORLD TODAY", font(SERIF_BLACK, 92), INK)
d.line([(M, 144), (W - M, 144)], fill=INK, width=5)
d.line([(M, 152), (W - M, 152)], fill=INK, width=2)
d.text((M, 160), "Wednesday, 18 November 2026", font=font(SANS_BOLD, 24), fill=INK)
r = "LATE EDITION  •  No. 2026-322"
d.text((W - M - d.textlength(r, font=font(SANS_BOLD, 24)), 160), r,
       font=font(SANS_BOLD, 24), fill=INK)
d.line([(M, 194), (W - M, 194)], fill=INK, width=2)

# ---------------------------------------------------------------- lead story
d.text((M, 208), "DIPLOMACY  •  SHENZHEN, CHINA — APEC SUMMIT", font=font(SANS_BLACK, 21), fill=RED)
hy = text_block(d, M, 236,
                "Trump Lands in China for Historic Summit With Xi and Putin",
                font(SERIF_BLACK, 50), INK, CW, 56)
lead_sum = ("Xi Jinping greeted Donald Trump at Shenzhen airport after talks with Vladimir Putin, "
            "setting up Thursday's first-ever three-way summit of the leaders of the world's "
            "three largest nuclear powers.")
sy = text_block(d, M, hy + 4, lead_sum, font(SANS, 23), (46, 42, 34), CW, 30)

# flags row: USA / China / Russia, simplified but recognisable
FW, FH = 296, 62
fy = sy + 10
def flag_frame(x, label):
    d.rectangle([x, fy, x + FW, fy + FH], outline=INK, width=2)
    d.text((x, fy + FH + 5), label, font=font(SANS_BOLD, 15), fill=MUTED)

fx = M  # USA
for i in range(7):
    d.rectangle([fx + 2, fy + 2 + i * 8, fx + FW - 2, fy + 2 + i * 8 + 5],
                fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
d.rectangle([fx + 2, fy + 2, fx + 118, fy + 32], fill=(60, 59, 110))
for r_ in range(3):
    for c_ in range(5):
        d.ellipse([fx + 10 + c_ * 22, fy + 6 + r_ * 9, fx + 15 + c_ * 22, fy + 11 + r_ * 9],
                  fill=(255, 255, 255))
flag_frame(fx, "UNITED STATES")

fx = M + FW + 28  # China
d.rectangle([fx + 2, fy + 2, fx + FW - 2, fy + FH - 2], fill=(222, 41, 16))
def star(cx, cy, r_):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r_ if i % 2 == 0 else r_ * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=GOLD)
star(fx + 34, fy + 30, 17)
for dx, dy in ((58, 10), (66, 24), (66, 40), (56, 52)):
    star(fx + dx, fy + dy, 6)
flag_frame(fx, "CHINA")

fx = M + 2 * (FW + 28)  # Russia
for i, col in enumerate(((255, 255, 255), (0, 57, 166), (213, 43, 30))):
    d.rectangle([fx + 2, fy + 2 + i * 19, fx + FW - 2, fy + 2 + i * 19 + 18], fill=col)
flag_frame(fx, "RUSSIA")

rule_y = fy + FH + 28
d.line([(M, rule_y), (W - M, rule_y)], fill=INK, width=3)

# ---------------------------------------------------------------- panels 2x2
PANELS = [
    ("WAR IN THE GULF", RED,
     "U.S. Strikes Iranian Island in Strait of Hormuz",
     "American jets hit a missile site on Qeshm Island after Iranian drones "
     "targeted a U.S. base in Kuwait."),
    ("TECHNOLOGY", BLUE,
     "Tech Outage Grounds Flights, Reaches the NSA",
     "Failures that cut company email and halted thousands of flights spread "
     "to the U.S. National Security Agency."),
    ("MARKETS & AI", (122, 84, 10),
     "Anthropic Prices IPO at $83 Amid AI Fever",
     "Claude's maker priced its debut above range; Nvidia revenue doubled to "
     "$115.8 billion, but a hawkish Fed left stocks mixed."),
    ("PUBLIC HEALTH", (30, 110, 76),
     "U.S. Loses Measles-Free Status as Cases Spike",
     "America lost the measles-free status it had held since 2000, as a "
     "nationwide surge of cases overwhelmed containment."),
]
PW, PH, PG = 456, 170, 32
PY = rule_y + 18
for i, (kick, kcol, head, summ) in enumerate(PANELS):
    x = M + (i % 2) * (PW + PG)
    y = PY + (i // 2) * (PH + 12)
    d.rectangle([x, y, x + PW, y + PH], fill=PANEL_BG, outline=PANEL_EDGE, width=2)
    d.rectangle([x, y, x + PW, y + 8], fill=kcol)
    d.text((x + 18, y + 17), kick, font=font(SANS_BLACK, 17), fill=kcol)
    yy = text_block(d, x + 18, y + 42, head, font(SERIF_BOLD, 25), INK, PW - 36, 30)
    text_block(d, x + 18, yy + 4, summ, font(SANS, 17), (52, 48, 40), PW - 36, 21)

# ---------------------------------------------------------------- ticker band
TY = PY + 2 * PH + 12 + 8
d.rectangle([M, TY, W - M, TY + 46], fill=INK)
centered(d, W / 2, TY + 5,
         "ALSO WEDNESDAY:  Bangladesh deploys paramilitary amid unrest over Hasina's return",
         font(SANS_BOLD, 15), PAPER)
centered(d, W / 2, TY + 25,
         "Israel opens new operation in central Gaza  •  Cyclone Akvan lashes India's Odisha coast",
         font(SANS_BOLD, 15), PAPER)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "entry.png")
img.save(out, optimize=True)
print("wrote", out, os.path.getsize(out), "bytes")

#!/usr/bin/env python3
"""Draw the 18 November 2026 'front page in one image' for news-image-20261118.

Version 2 — a full visual redesign in premium broadsheet style (Financial
Times / NYT polish): warm off-white paper, black ink, one deep-red accent,
a serif masthead, the lead story carried by an editorial illustration band,
four secondary stories in ruled columns, a MARKETS data box with a bar
visual for Nvidia's doubled revenue, and an ink ticker band at the foot.

Same news content as v1 (researched and verified for Wednesday 18 Nov 2026).
Pure PIL, offline, deterministic: fixed layout, fixed text, the only image
asset is the committed illustration at ../assets/summit-illustration.webp.
Output: ../entry.png (1024x1024, <= 1 MiB; PNG if it fits, else JPEG —
the file name stays entry.png either way, format is read from magic bytes).
"""
from PIL import Image, ImageDraw, ImageFont
import os

W = H = 1024
M = 48                      # page margin
CW = W - 2 * M              # content width = 928
RIGHT = W - M

PAPER = (247, 242, 231)     # warm off-white
INK = (24, 21, 17)
BODY = (45, 41, 34)
MUTED = (110, 101, 86)
FAINT = (203, 193, 168)     # hairline rules / dividers
RED = (163, 31, 22)         # the one accent: deep red
RED_ON_INK = (232, 118, 98) # accent legible on the black ticker band
BAR_MUTED = (154, 145, 126)

FONT_DIR = "/usr/share/fonts/truetype/noto"
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "assets", "summit-illustration.webp")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_BLACK = "NotoSerif-Black.ttf"
SERIF_BOLD = "NotoSerif-Bold.ttf"
SERIF_ITALIC = "NotoSerif-Italic.ttf"
SANS = "NotoSans-Regular.ttf"
SANS_BOLD = "NotoSans-Bold.ttf"


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
        assert draw.textlength(line, font=fnt) <= max_w, f"overflow: {line!r}"
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tracked_w(draw, text, fnt, tracking):
    if not text:
        return 0
    return sum(draw.textlength(ch, font=fnt) for ch in text) + tracking * (len(text) - 1)


def draw_tracked(draw, x, y, text, fnt, fill, tracking=2):
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x - tracking if text else x


def centered_tracked(draw, cx, y, text, fnt, fill, tracking=2):
    x = cx - tracked_w(draw, text, fnt, tracking) / 2
    draw_tracked(draw, x, y, text, fnt, fill, tracking)


def fit_font(draw, text, name, start, max_w, step=2):
    size = start
    while size > 30 and draw.textlength(text, font=font(name, size)) > max_w:
        size -= step
    return font(name, size), size


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- folio line
FOLIO = font(SANS_BOLD, 12)
draw_tracked(d, M, 26, "LATE EDITION", FOLIO, MUTED, 2)
centered_tracked(d, W / 2, 26, "WORLD NEWS IN ONE PAGE", FOLIO, MUTED, 2)
r = "No. 322"
draw_tracked(d, RIGHT - tracked_w(d, r, FOLIO, 2), 26, r, FOLIO, MUTED, 2)
d.line([(M, 47), (RIGHT, 47)], fill=INK, width=2)

# ---------------------------------------------------------------- masthead
mast_f, mast_size = fit_font(d, "THE WORLD TODAY", SERIF_BLACK, 96, CW)
mw = d.textlength("THE WORLD TODAY", font=mast_f)
# Noto Serif Black's ink starts ~31px below the draw origin and the Y
# descenders end ~96px below it at 88px, so origin 30 puts ink at 61..126,
# clear of the folio rule above and the double rule at 134/140 below.
d.text(((W - mw) / 2, 30), "THE WORLD TODAY", font=mast_f, fill=INK)
d.line([(M, 134), (RIGHT, 134)], fill=INK, width=3)
d.line([(M, 140), (RIGHT, 140)], fill=INK, width=1)

# ---------------------------------------------------------------- dateline
d.text((M, 148), "Wednesday, November 18, 2026", font=font(SANS_BOLD, 16), fill=INK)
dl = "SHENZHEN · WASHINGTON · MOSCOW"
dl_f = font(SANS_BOLD, 12)
draw_tracked(d, RIGHT - tracked_w(d, dl, dl_f, 2), 151, dl, dl_f, MUTED, 2)
d.line([(M, 176), (RIGHT, 176)], fill=INK, width=1)

# ---------------------------------------------------------------- lead story
KICK = font(SANS_BOLD, 14)
kx = draw_tracked(d, M, 188, "DIPLOMACY", KICK, RED, 2)
draw_tracked(d, kx + 10, 188, "·  APEC SUMMIT — SHENZHEN, CHINA", KICK, INK, 2)

HEADLINE = "Trump Lands in China for Historic Summit With Xi and Putin"
head_f, head_size = None, None
for size in (58, 56, 54, 52, 50):
    f = font(SERIF_BLACK, size)
    if len(wrap(d, HEADLINE, f, CW)) <= 2:
        head_f, head_size = f, size
        break
assert head_f is not None, "lead headline does not fit in two lines"
hy = text_block(d, M, 210, HEADLINE, head_f, INK, CW, head_size + 4)
assert hy <= 336, f"headline overruns: ends {hy}"

STANDFIRST = ("Xi Jinping greeted Donald Trump at Shenzhen airport after talks with "
              "Vladimir Putin, setting up Thursday's first-ever three-way summit of "
              "the leaders of the world's three largest nuclear powers.")
sy = text_block(d, M, 342, STANDFIRST, font(SERIF_ITALIC, 20), BODY, CW, 26)
assert sy <= 424, f"standfirst overruns: ends {sy}"

# ---------------------------------------------------------------- hero band
HERO_Y, HERO_H = 428, 206
art = Image.open(ART).convert("RGB")
crop_h = int(art.width / (CW / HERO_H))
y0 = 238
hero = art.crop((0, y0, art.width, y0 + crop_h)).resize((CW, HERO_H), Image.LANCZOS)
img.paste(hero, (M, HERO_Y))
d.rectangle([M, HERO_Y, RIGHT - 1, HERO_Y + HERO_H - 1], outline=INK, width=2)

CAP = "An artist's impression of the three leaders at the summit table, high above Shenzhen."
cap_f = font(SERIF_ITALIC, 14)
d.text((M, 642), CAP, font=cap_f, fill=MUTED)
CRED = "ILLUSTRATION: SUMMIT IN SHENZHEN"
cred_f = font(SANS_BOLD, 10)
cred_w = tracked_w(d, CRED, cred_f, 2)
assert d.textlength(CAP, font=cap_f) + cred_w + 24 <= CW, "caption/credit collide"
draw_tracked(d, RIGHT - cred_w, 645, CRED, cred_f, MUTED, 2)
d.line([(M, 668), (RIGHT, 668)], fill=INK, width=2)

# ---------------------------------------------------------------- secondary stories
STORIES = [
    ("WAR IN THE GULF",
     "U.S. Strikes Iranian Island in Strait of Hormuz",
     "American jets hit a missile site on Qeshm Island after Iranian drones "
     "targeted a U.S. base in Kuwait."),
    ("TECHNOLOGY",
     "Tech Outage Grounds Flights, Reaches the NSA",
     "Failures that cut company email and halted thousands of flights spread "
     "to the U.S. National Security Agency."),
    ("MARKETS & AI",
     "Anthropic Prices IPO at $83 Amid AI Fever",
     "Claude's maker priced its debut above range; Nvidia revenue doubled to "
     "$115.8 billion, but a hawkish Fed left stocks mixed."),
    ("PUBLIC HEALTH",
     "U.S. Loses Measles-Free Status as Cases Spike",
     "America lost the measles-free status it had held since 2000, as a "
     "nationwide surge of cases overwhelmed containment."),
]
COL_W, COL_GAP = 215, 22
STORY_Y = 680
for i in range(1, 4):  # hairline column rules
    rx = M + i * COL_W + (i - 0.5) * COL_GAP - 4
    d.line([(rx, STORY_Y + 4), (rx, STORY_Y + 148)], fill=FAINT, width=1)
for i, (kick, head, summ) in enumerate(STORIES):
    x = M + i * (COL_W + COL_GAP)
    draw_tracked(d, x, STORY_Y, kick, font(SANS_BOLD, 11), RED, 2)
    hy2 = text_block(d, x, STORY_Y + 18, head, font(SERIF_BOLD, 19), INK, COL_W, 22)
    assert hy2 <= STORY_Y + 86, f"story headline overruns: {head!r} ends {hy2}"
    ey = text_block(d, x, STORY_Y + 90, summ, font(SANS, 13), BODY, COL_W, 16)
    assert ey <= STORY_Y + 158, f"story summary overruns: {head!r} ends {ey}"

# ---------------------------------------------------------------- markets box
BOX_Y, BOX_H = 846, 104
d.rectangle([M, BOX_Y, RIGHT - 1, BOX_Y + BOX_H - 1], outline=INK, width=2)
draw_tracked(d, M + 16, BOX_Y + 12, "MARKETS", font(SANS_BOLD, 14), RED, 2)
mh = "WEDNESDAY'S TRADING"
mh_f = font(SANS_BOLD, 10)
draw_tracked(d, RIGHT - 16 - tracked_w(d, mh, mh_f, 2), BOX_Y + 15, mh, mh_f, MUTED, 2)
d.line([(M + 16, BOX_Y + 34), (RIGHT - 16, BOX_Y + 34)], fill=FAINT, width=1)

# Anthropic stat
lab_f = font(SANS_BOLD, 10)
draw_tracked(d, M + 16, BOX_Y + 44, "ANTHROPIC IPO", lab_f, MUTED, 2)
num_f = font(SERIF_BLACK, 27)
d.text((M + 16, BOX_Y + 58), "$83", font=num_f, fill=INK)
nw = d.textlength("$83", font=num_f)
d.text((M + 16 + nw + 8, BOX_Y + 72), "/ SHARE — ABOVE THE $70–78 RANGE",
       font=font(SANS_BOLD, 11), fill=BODY)
d.line([(M + 252, BOX_Y + 44), (M + 252, BOX_Y + 94)], fill=FAINT, width=1)

# Nvidia bars: revenue doubled to $115.8B, so a year ago ≈ $57.9B
NX = M + 272
draw_tracked(d, NX, BOX_Y + 44, "NVIDIA REVENUE — DOUBLED IN A YEAR", lab_f, MUTED, 2)
bar_f = font(SANS_BOLD, 11)
d.rectangle([NX, BOX_Y + 62, NX + 150, BOX_Y + 73], fill=BAR_MUTED)
d.text((NX + 160, BOX_Y + 60), "$57.9 BN · A YEAR AGO", font=bar_f, fill=BODY)
d.rectangle([NX, BOX_Y + 79, NX + 300, BOX_Y + 90], fill=RED)
d.text((NX + 310, BOX_Y + 77), "$115.8 BN · NOW", font=bar_f, fill=INK)
assert NX + 300 + 10 + d.textlength("$115.8 BN · NOW", font=bar_f) <= RIGHT - 16

# ---------------------------------------------------------------- ticker band
TICK_Y, TICK_H = 960, 42
d.rectangle([M, TICK_Y, RIGHT, TICK_Y + TICK_H], fill=INK)
tick_f = font(SANS_BOLD, 12)


def segmented_centered(y, segments):
    """segments: list of (text, fill); drawn as one centred line."""
    total = sum(d.textlength(t, font=tick_f) for t, _ in segments)
    assert total <= CW - 24, f"ticker line too wide: {total}"
    x = (W - total) / 2
    for t, fill in segments:
        d.text((x, y), t, font=tick_f, fill=fill)
        x += d.textlength(t, font=tick_f)


segmented_centered(TICK_Y + 4, [
    ("ALSO WEDNESDAY —  ", RED_ON_INK),
    ("Bangladesh deploys paramilitary amid unrest over Hasina's return", PAPER),
])
segmented_centered(TICK_Y + 21, [
    ("Israel opens new operation in central Gaza", PAPER),
    ("  •  ", RED_ON_INK),
    ("Cyclone Akvan lashes India's Odisha coast", PAPER),
])

# ---------------------------------------------------------------- save
out = os.path.join(HERE, "..", "entry.png")
img.save(out, optimize=True)
size = os.path.getsize(out)
fmt = "PNG"
if size > 1_048_576:  # photo-like illustration: fall back to JPEG under the cap
    q = 88
    while True:
        img.save(out, format="JPEG", quality=q, optimize=True)
        size = os.path.getsize(out)
        if size <= 1_048_576 or q <= 70:
            break
        q -= 3
    fmt = f"JPEG q={q}"
assert size <= 1_048_576, f"entry.png still too big: {size}"
print(f"wrote {out}: {fmt}, 1024x1024, {size} bytes; masthead {mast_size}px, headline {head_size}px")

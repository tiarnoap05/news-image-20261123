#!/usr/bin/env python3
"""Deterministic newspaper front-page generator for news-image-20261123.

Draws a 1024x1024 front page for "THE WORLD TODAY" dated Monday, 23 November
2026, using only Pillow and the DejaVu fonts shipped with the system. No
network, no randomness, no wall clock: the same input always produces the
same PNG bytes.

Run from anywhere:
    python3 tools/gen_image.py [output-path]
Default output is entry.png next to this repository's root.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

PAPER = (247, 243, 234)      # warm newsprint
INK = (17, 17, 17)           # near-black
RED = (176, 0, 0)            # stamp / kicker red
GREY = (110, 110, 105)       # rules and small print
SKY = (223, 232, 238)
SEA = (46, 111, 142)
HULL = (36, 52, 71)
DECK = (214, 205, 190)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


class LayoutError(Exception):
    """Raised when a text block does not fit inside its box."""


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


SERIF_BOLD = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap. Raises LayoutError if one word alone is too wide."""
    lines = []
    cur = ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            if draw.textlength(word, font=fnt) > max_width:
                raise LayoutError(f"word too wide for box: {word!r}")
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, line_height, limit_bottom, what,
               align="left", box_width=None):
    """Draw lines of text; raise LayoutError if they run past limit_bottom."""
    for line in lines:
        if y + line_height > limit_bottom:
            raise LayoutError(f"{what} overflows its box (bottom {limit_bottom})")
        if align == "center":
            lx = x + (box_width - draw.textlength(line, font=fnt)) / 2
        else:
            lx = x
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def rule(draw, y, x0=MARGIN, x1=W - MARGIN, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_tanker(draw, x0, y0, x1, y1):
    """Simple side-view tanker inside the box (x0, y0, x1, y1)."""
    # Sky and sea.
    draw.rectangle([x0, y0, x1, y1], fill=SKY)
    sea_top = y1 - 42
    draw.rectangle([x0, sea_top, x1, y1], fill=SEA)
    # Wave lines.
    for wy, amp in ((sea_top + 12, 4), (sea_top + 26, 5)):
        pts = []
        x = x0 + 8
        while x <= x1 - 8:
            pts.append((x, wy + amp * (1 if (x // 26) % 2 == 0 else -1)))
            x += 13
        draw.line(pts, fill=(255, 255, 255), width=2)
    # Hull: flat stern left, sloped bow right.
    deck_y = sea_top - 26
    hull = [(x0 + 60, deck_y), (x1 - 90, deck_y), (x1 - 30, sea_top + 8),
            (x1 - 130, sea_top + 8), (x0 + 90, sea_top + 8), (x0 + 60, deck_y)]
    draw.polygon(hull, fill=HULL)
    draw.line([(x0 + 60, deck_y), (x1 - 90, deck_y)], fill=DECK, width=3)
    # Bridge tower at the stern (left), funnel beside it.
    draw.rectangle([x0 + 78, deck_y - 52, x0 + 128, deck_y], fill=(240, 240, 236))
    for wy in (deck_y - 44, deck_y - 30, deck_y - 16):
        draw.rectangle([x0 + 84, wy, x0 + 122, wy + 8], fill=(40, 70, 90))
    draw.rectangle([x0 + 140, deck_y - 40, x0 + 164, deck_y], fill=(60, 60, 60))
    draw.rectangle([x0 + 140, deck_y - 40, x0 + 164, deck_y - 30], fill=RED)
    # Containers stacked mid-ship.
    boxes = [
        ((x0 + 190, deck_y - 26, x0 + 300, deck_y), (178, 62, 48)),
        ((x0 + 310, deck_y - 26, x0 + 420, deck_y), (52, 96, 140)),
        ((x0 + 430, deck_y - 26, x0 + 540, deck_y), (72, 130, 84)),
        ((x0 + 550, deck_y - 26, x0 + 660, deck_y), (196, 160, 40)),
        ((x0 + 245, deck_y - 52, x0 + 365, deck_y - 26), (140, 90, 40)),
        ((x0 + 480, deck_y - 52, x0 + 600, deck_y - 26), (90, 120, 150)),
    ]
    for (bx0, by0, bx1, by1), color in boxes:
        draw.rectangle([bx0, by0, bx1, by1], fill=color, outline=(20, 20, 20))
    # Small flag on the stern mast.
    draw.line([(x0 + 103, deck_y - 52), (x0 + 103, deck_y - 72)], fill=INK, width=2)
    draw.polygon([(x0 + 103, deck_y - 72), (x0 + 131, deck_y - 66),
                  (x0 + 103, deck_y - 60)], fill=RED)


def draw_stamp(img, box):
    """Red BLOCKADE stamp, rotated, in the top-right of the illustration box.

    The stamp lives entirely inside the illustration area, so it can never
    overlap body text.
    """
    x0, y0, x1, y1 = box
    sw, sh = 250, 84
    stamp = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([4, 4, sw - 5, sh - 5], radius=8,
                         outline=(176, 0, 0, 255), width=5)
    sd.text((sw / 2, 10), "BLOCKADE", font=SANS_BOLD(34),
            fill=(176, 0, 0, 255), anchor="ma")
    sub = "TRUMP WARNS IRAN • 23 NOV 2026"
    sub_font = SANS_BOLD(11)
    sub_w = sd.textlength(sub, font=sub_font)
    if sub_w > sw - 20:
        raise LayoutError(f"stamp sub-text too wide: {sub_w:.0f} > {sw - 20}")
    sd.text((sw / 2, 52), sub, font=sub_font,
            fill=(176, 0, 0, 255), anchor="ma")
    stamp = stamp.rotate(-8, expand=True, resample=Image.BICUBIC)
    px = x1 - stamp.width - 10
    py = y0 + 6
    if px < x0 or py + stamp.height > y1:
        raise LayoutError("stamp does not fit inside the illustration box")
    img.paste(stamp, (px, py), stamp)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    y = 28
    mast = "THE WORLD TODAY"
    mf = SERIF_BOLD(62)
    draw.text(((W - draw.textlength(mast, font=mf)) / 2, y), mast,
              font=mf, fill=INK)
    y += 76
    rule(draw, y, width=3)
    y += 8
    date = "MONDAY, 23 NOVEMBER 2026"
    df = SANS_BOLD(20)
    draw.text(((W - draw.textlength(date, font=df)) / 2, y), date,
              font=df, fill=INK)
    y += 30
    rule(draw, y, width=1, fill=GREY)
    y += 14

    # ---- Lead headline --------------------------------------------------
    head = "TRUMP THREATENS TO SINK IRANIAN TANKERS"
    hf = SANS_BOLD(44)
    lines = wrap(draw, head, hf, CONTENT_W)
    y = draw_lines(draw, lines, MARGIN, y, hf, INK, 52, 262,
                   "lead headline", align="center", box_width=CONTENT_W)
    y += 8

    # ---- Lead body ------------------------------------------------------
    body = ("WASHINGTON — Donald Trump said on Sunday he is “inclined” to resume "
            "strikes on Iran after the New Year if talks fail, and warned any "
            "Iranian tanker testing the US naval blockade “will all be at the "
            "bottom of the sea”. More than a dozen tankers have gathered near "
            "Kharg Island; Tehran has threatened Gulf energy sites if "
            "Washington stops them.")
    bf = SERIF(21)
    lines = wrap(draw, body, bf, CONTENT_W)
    y = draw_lines(draw, lines, MARGIN, y, bf, INK, 27, 382, "lead body")
    y += 10

    # ---- Tanker illustration with stamp ---------------------------------
    ill_box = (MARGIN, y, W - MARGIN, y + 150)
    draw_tanker(draw, *ill_box)
    draw_stamp(img, ill_box)
    draw = ImageDraw.Draw(img)  # stamp paste invalidates the old handle
    y = ill_box[3] + 12
    rule(draw, y, width=1, fill=GREY)
    y += 12

    # ---- 2x2 grid --------------------------------------------------------
    cells = [
        ("UKRAINE", "Dymer toll hits 11 as search goes on",
         "Rescuers kept digging in Dymer on Monday as the toll from the drone "
         "strike on a Kyiv-region block rose to 11; a boy of 7 was pulled out alive."),
        ("MARKETS", "Futures rebound as Asia slides again",
         "US stock futures jumped on Monday after last week’s AI sell-off, but "
         "Asia slid again: South Korea’s KOSPI fell 5% before finding support."),
        ("POLITICS", "Democrats win biggest House majority since 1992",
         "Democrats flipped a North Carolina seat for their largest House "
         "majority since 1992."),
        ("ECONOMY", "Korea’s exports pass $1 trillion",
         "South Korea’s exports passed $1 trillion for the first time, customs "
         "data showed on Monday, driven by a near-doubling of chip sales."),
    ]
    col_w = (CONTENT_W - 24) // 2
    row_h = 148
    grid_top = y
    for i, (kicker, headline, text) in enumerate(cells):
        cx = MARGIN + (i % 2) * (col_w + 24)
        cy = grid_top + (i // 2) * (row_h + 14)
        bottom = cy + row_h
        kf = SANS_BOLD(16)
        draw.text((cx, cy), kicker, font=kf, fill=RED)
        hf2 = SANS_BOLD(23)
        lines = wrap(draw, headline, hf2, col_w)
        ny = draw_lines(draw, lines, cx, cy + 22, hf2, INK, 27,
                        bottom - 62, f"grid headline {kicker}")
        tf = SERIF(17)
        lines = wrap(draw, text, tf, col_w)
        draw_lines(draw, lines, cx, ny + 6, tf, INK, 21, bottom,
                   f"grid body {kicker}")
    # Dividers between the four cells.
    mid_x = MARGIN + col_w + 12
    draw.line([(mid_x, grid_top), (mid_x, grid_top + 2 * row_h + 14)],
              fill=GREY, width=1)
    mid_y = grid_top + row_h + 7
    draw.line([(MARGIN, mid_y), (W - MARGIN, mid_y)], fill=GREY, width=1)
    y = grid_top + 2 * row_h + 14 + 12

    # ---- Also today strip ------------------------------------------------
    rule(draw, y, width=1, fill=GREY)
    y += 8
    kf = SANS_BOLD(16)
    draw.text((MARGIN, y), "ALSO TODAY", font=kf, fill=RED)
    y += 22
    also = ("Mets sign Skubal for record $450m  •  Vanuatu hit by M6.5 quake  •  "
            "AI ‘proves’ Riemann — maths still checking  •  Houthis claim Saudi "
            "refinery hit  •  COP31 fallout continues.")
    af = SANS(17)
    lines = wrap(draw, also, af, CONTENT_W)
    y = draw_lines(draw, lines, MARGIN, y, af, INK, 22, 966, "also-today strip")
    y += 8
    rule(draw, y, width=1, fill=GREY)
    y += 10

    # ---- Footer ----------------------------------------------------------
    foot = "THE WORLD TODAY • Monday 23 November 2026 • make.fun • news-image-20261123"
    ff = SANS(15)
    if draw.textlength(foot, font=ff) > CONTENT_W:
        raise LayoutError("footer too wide")
    draw.text(((W - draw.textlength(foot, font=ff)) / 2, y), foot,
              font=ff, fill=GREY)
    y += 22
    if y > H - 16:
        raise LayoutError(f"page overflows: bottom {y} > {H - 16}")
    return img


def main(argv):
    out = Path(argv[1]) if len(argv) > 1 else (
        Path(__file__).resolve().parent.parent / "entry.png")
    img = build()
    if img.size != (W, H):
        raise LayoutError(f"unexpected canvas size {img.size}")
    img.save(out, format="PNG")
    print(f"wrote {out} ({out.stat().st_size} bytes, {img.size[0]}x{img.size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
